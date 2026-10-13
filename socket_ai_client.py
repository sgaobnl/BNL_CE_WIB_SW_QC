"""
Test-stand side of the LArASIC socket inspection (runs on the RTS PC).

Master copy: elec_AI/socket_inspection/socket_ai_client.py on wcgpu1.
A copy lives in BNL_CE_WIB_SW_QC/ (see sync_client_to_qc_repo.sh) - edit the master.

Flow per chip, after the robot's MoveChipFromTrayToSocket:
  1. read <rootdir>/images/<ts>_socket.bmp  (2560x1920, saved by the robot)
  2. crop region1 (512x512), as in the training data
  3. POST the crop as lossless PNG (~100 KB instead of the 4.8 MB BMP) to wcgpu1
  4. server answers "good" / "bad"
  5. on "bad" (socket_ai_rotate_reseat, used by RTS_DAT_rev0.py and RTS_ROBOT_TEST.py):
     pick the chip up from the socket, rotate +0.5 deg, insert, re-inspect; still "bad": pick up,
     rotate -1.0 deg (-0.5 deg from the first insertion), insert, re-inspect; still "bad": pick up
     and insert at the angle whose inspection had the smallest z_max, then continue
     (robot command ReseatChipInSocket; angles RESEAT_DU).
     socket_ai_reseat is the older variant: socket -> tray -> socket, at most MAX_RESEAT times.

Server lifetime (since 2026-10-07): the model is on the GPU only while chips are moved into the
sockets. socket_ai_start() asks the launcher on wcgpu1 (LAUNCHER_URL, socket_ai_launcher.py) to
start the inference server and waits until it is ready (~8 s); socket_ai_stop() releases it.
RTS_DAT_rev0.py calls them at the beginning and end of MovetoSoket. Both never raise; without
the launcher the chain just runs without the check (and the server exits by itself after its
idle timeout if a stop never arrives).

Only needs PIL and requests (both already used by the OCR code).
"""

import atexit
import io
import json
import os
import time

import requests
from PIL import Image

SERVER_URL = "http://wcgpu1.phy.bnl.gov:11435"
LAUNCHER_URL = "http://wcgpu1.phy.bnl.gov:11436"   # socket_ai_launcher.py: starts/stops the server on request
START_TIMEOUT_S = 150  # socket_ai_start(): max wait for the model to load (launcher kills the server after 120 s)
ENABLE = True          # False -> socket_ai_start/stop() and socket_ai_rotate_reseat() / socket_ai_reseat() do nothing
RESEAT_DU = [0.5, -0.5]  # socket_ai_rotate_reseat: angles (deg) from the first insertion, tried while "bad"
MAX_RESEAT = 3         # socket_ai_reseat (socket -> tray -> socket) only
TIMEOUT_S = 20
RETRIES = 3

# Same geometry as crop_config_LarASIC.json (used to build the training set).
CROP_CONFIG = {
    "image_size": [2560, 1920],
    "region1": {"x0": 1026, "y0": 691, "x1": 1538, "y1": 1203},
    "region2": {"x0": 1152, "y0": 827, "x1": 1402, "y1": 1077},
}


def load_crop_config(path=None):
    """Return the crop geometry, from a JSON file (select_regions.py format) or the default."""
    if path is None:
        return CROP_CONFIG
    with open(path) as f:
        return json.load(f)


def crop_socket_image(image, crop_cfg=CROP_CONFIG):
    """Crop region1. A 512x512 input is taken as already cropped."""
    r1 = crop_cfg["region1"]
    w, h = r1["x1"] - r1["x0"], r1["y1"] - r1["y0"]
    image = image.convert("L")
    if image.size == tuple(crop_cfg["image_size"]):
        image = image.crop((r1["x0"], r1["y0"], r1["x1"], r1["y1"]))
    elif image.size != (w, h):
        raise ValueError(f"unexpected image size {image.size}, expected "
                         f"{tuple(crop_cfg['image_size'])} or {(w, h)}")
    return image


def encode_png(image):
    """Lossless PNG bytes (the model is sensitive to compression artefacts, so no JPEG)."""
    buf = io.BytesIO()
    image.save(buf, format="PNG", optimize=True)
    return buf.getvalue()


def socket_image_path(rootdir, ts):
    """Path of the in-socket picture the robot saves in MoveChipFromTrayToSocket."""
    return os.path.join(rootdir, "images", f"{ts}_socket.bmp")


def wait_for_file(path, timeout_s=10.0):
    """The robot writes the BMP just before replying; allow for a slow file share."""
    t0 = time.time()
    while time.time() - t0 < timeout_s:
        if os.path.isfile(path) and os.path.getsize(path) > 0:
            return True
        time.sleep(0.5)
    return False


def inspect_socket_image(image_path, chip_id="unknown", socket=0, attempt=0,
                         server_url=SERVER_URL, timeout_s=TIMEOUT_S, retries=RETRIES):
    """
    Send one socket picture to the inference server.
    Returns a dict with "result" = "good" | "bad" | "error" (plus score details on success).
    Never raises: an unreachable server must not stop the test chain.
    """
    try:
        if not wait_for_file(image_path):
            return {"result": "error", "error": f"picture not found: {image_path}"}
        with Image.open(image_path) as im:
            png = encode_png(crop_socket_image(im))
    except Exception as e:
        return {"result": "error", "error": f"cannot prepare picture: {e}"}

    url = f"{server_url}/api/socket_check"
    params = {"id": chip_id, "socket": socket, "attempt": attempt}
    last_err = ""
    for _ in range(retries):
        try:
            r = requests.post(url, params=params, data=png, timeout=timeout_s,
                              headers={"Content-Type": "image/png"})
            if r.status_code == 200:
                return r.json()
            last_err = f"HTTP {r.status_code}: {r.text[:200]}"
        except requests.RequestException as e:
            last_err = str(e)
        time.sleep(1)
    return {"result": "error", "error": last_err}


_stop_registered = False


def socket_ai_start(launcher_url=LAUNCHER_URL, timeout_s=START_TIMEOUT_S, log=None):
    """
    Start the inference server on wcgpu1 (model loaded onto the GPU) and wait until it is ready.
    Call before the first MoveChipFromTrayToSocket of a round; pair with socket_ai_stop().

    Returns the launcher's reply: {"status": "running", "started": bool, "load_s": ..., "health": {...}}
    or {"status": "error", "error": ...}. Never raises; on error the chain continues and every
    inspection answers "error" until the server is up. The first successful start registers
    socket_ai_stop() with atexit, so an aborted run releases the GPU too.
    `log` (a list) receives one dict per call.
    """
    global _stop_registered
    if not ENABLE:
        return {"status": "disabled"}
    t0 = time.time()
    try:
        r = requests.post(f"{launcher_url}/start", timeout=timeout_s)
        info = r.json() if r.headers.get("Content-Type", "").startswith("application/json") else {}
        if r.status_code != 200:
            info = {"status": "error", "error": info.get("detail") or f"HTTP {r.status_code}: {r.text[:200]}"}
    except (requests.RequestException, ValueError) as e:
        info = {"status": "error", "error": str(e)}
    info.update(action="start", time=time.strftime("%Y-%m-%d %H:%M:%S"), wait_s=round(time.time() - t0, 1))
    if log is not None:
        log.append(info)
    if info["status"] == "running":
        h = info.get("health") or {}
        what = f"loaded in {info.get('load_s')} s" if info.get("started") else "was already running"
        print(f"Socket AI server {what}: model {h.get('model')}, threshold {h.get('threshold')}")
        if not _stop_registered:
            atexit.register(socket_ai_stop, launcher_url)
            _stop_registered = True
    else:
        print(f"\033[93mSocket AI server could not be started ({info.get('error')}); "
              f"inspections will return 'error' and the chain continues\033[0m")
    return info


def socket_ai_stop(launcher_url=LAUNCHER_URL, timeout_s=45, log=None):
    """
    Stop the inference server on wcgpu1 (process exits, GPU memory released). Call after the
    last chip of the round is in its socket. Never raises; idempotent.
    Returns the launcher's reply {"status": "stopped" | "running", "was_running": bool} or {"status": "error", ...}.
    """
    if not ENABLE:
        return {"status": "disabled"}
    try:
        r = requests.post(f"{launcher_url}/stop", timeout=timeout_s)
        info = r.json() if r.headers.get("Content-Type", "").startswith("application/json") else {}
        if r.status_code != 200:
            info = {"status": "error", "error": info.get("detail") or f"HTTP {r.status_code}: {r.text[:200]}"}
    except (requests.RequestException, ValueError) as e:
        info = {"status": "error", "error": str(e)}
    info.update(action="stop", time=time.strftime("%Y-%m-%d %H:%M:%S"))
    if log is not None:
        log.append(info)
    if info["status"] == "stopped" and info.get("was_running"):
        print(f"Socket AI server stopped after {info.get('uptime_s')} s; GPU released")
    elif info["status"] == "error":
        print(f"\033[93mSocket AI server stop failed ({info.get('error')}); "
              f"it exits by itself after its idle timeout\033[0m")
    return info


def socket_ai_reseat(rts, rootdir, trayno, trayc, trayr, sinkno, sktn, duttype="FE",
                     max_reseat=MAX_RESEAT, log=None):
    """
    Call right after a successful rts.MoveChipFromTrayToSocket (rts.msg = its ts).

    Inspects the socket picture; while the answer is "bad", moves the chip back to its
    tray slot and inserts it again (new picture, new ts), at most `max_reseat` times.

    Returns the robot status to use from here on:
      >= 0  chip is in the socket, rts.msg holds the ts of the last insertion
      <  0  a reseat move failed; the caller handles it like a failed tray->socket move
    `log` (a list) receives one dict per inspection.
    A server error or a still-"bad" chip after max_reseat does not block the chain.
    """
    status = int(rts.msg)
    if not ENABLE:
        return status

    for attempt in range(max_reseat + 1):
        ts = rts.msg
        info = inspect_socket_image(socket_image_path(rootdir, ts), chip_id=ts,
                                    socket=sktn, attempt=attempt)
        info.update({"ts": ts, "attempt": attempt, "tray": (trayno, trayc, trayr),
                     "socket": (sinkno, sktn)})
        if log is not None:
            log.append(info)
        print(f"Socket AI: ts={ts} socket={sktn} attempt={attempt} -> {info['result']} "
              f"(score={info.get('score')}, worst side={info.get('worst_side')})")

        if info["result"] != "bad":
            if info["result"] == "error":
                print(f"\033[93mSocket AI unavailable ({info.get('error')}); continue without it\033[0m")
            return status
        if attempt == max_reseat:
            print(f"\033[91mSocket AI: still bad after {max_reseat} reseats; continue\033[0m")
            return status

        print(f"Socket AI: reseat {attempt + 1}/{max_reseat}: socket -> tray -> socket")
        status = rts.MoveChipFromSocketToTray(sinkno, sktn, trayno, trayc, trayr, duttype)
        if status < 0:
            return status
        status = rts.MoveChipFromTrayToSocket(trayno, trayc, trayr, sinkno, sktn, duttype)
        if status < 0:
            return status
    return status


def _z_of(info):
    """z_max of an inspection reply (the decision score if z_max is missing), None if unusable."""
    z = info.get("z_max", info.get("score"))
    try:
        return float(z)
    except (TypeError, ValueError):
        return None


def socket_ai_rotate_reseat(rts, rootdir, sinkno, sktn, duttype="FE", reseat_du=None, log=None):
    """
    Call right after a successful rts.MoveChipFromTrayToSocket (rts.msg = its ts).

    Inspects the socket picture; while the answer is "bad", picks the chip up from the socket,
    rotates it to the next angle of `reseat_du` (default RESEAT_DU) and inserts it into the same
    socket again (new picture, new ts). The angles are offsets from the first insertion, e.g.
    [+0.5, -0.5]: the robot turns by the difference to the current offset (+0.5, then -1.0).
    If the chip is still "bad" at the last angle, it is picked up once more and inserted at the
    angle whose inspection had the smallest z_max (no move if that is the current angle); that
    insertion is inspected again for the log, and the chain continues whatever the answer.

    Returns the robot status to use from here on:
      >= 0  chip is in the socket, rts.msg holds the ts of the last insertion
      <  0  a ReseatChipInSocket move failed: the chip may be in the socket or on the stinger
    `log` (a list) receives one dict per inspection (dU_total = angle of that inspection).
    A server error does not block the chain.
    """
    status = int(rts.msg)
    if not ENABLE:
        return status
    reseat_du = list(RESEAT_DU if reseat_du is None else reseat_du)
    log = [] if log is None else log
    first = len(log)               # the caller's list may already hold other chips
    angles = [0.0] + reseat_du     # angle of each inspection, from the first insertion
    du_total = 0.0
    for attempt in range(len(angles) + 1):
        ts = rts.msg
        info = inspect_socket_image(socket_image_path(rootdir, ts), chip_id=ts,
                                    socket=sktn, attempt=attempt)
        info.update({"ts": ts, "attempt": attempt, "socket": (sinkno, sktn),
                     "dU_total": du_total, "return_to_best": attempt == len(angles)})
        log.append(info)
        print(f"Socket AI: ts={ts} socket={sktn} attempt={attempt} rotation={du_total:+.2f} deg "
              f"-> {info['result']} (z_max={info.get('z_max')}, worst side={info.get('worst_side')})")

        if info["return_to_best"]:   # inspection at the best angle, for the log only
            return status
        if info["result"] != "bad":
            if info["result"] == "error":
                print(f"\033[93mSocket AI unavailable ({info.get('error')}); continue without it\033[0m")
            return status

        if attempt < len(reseat_du):
            target = reseat_du[attempt]
            print(f"Socket AI: reseat {attempt + 1}/{len(reseat_du)}: pick up from socket, "
                  f"rotate {target - du_total:+.2f} deg (to {target:+.2f} deg), insert")
        else:
            mine = log[first:]
            zs = [_z_of(l) for l in mine]
            best = min((i for i in range(len(zs)) if zs[i] is not None), key=lambda i: zs[i], default=None)
            if best is None:
                print("\033[91mSocket AI: still bad, no z_max to compare; continue\033[0m")
                return status
            target = mine[best]["dU_total"]
            print(f"\033[91mSocket AI: still bad after {len(reseat_du)} rotated reseats; z_max "
                  + ", ".join(f"{l['dU_total']:+.2f} deg: {z}" for l, z in zip(mine, zs))
                  + f" -> smallest at {target:+.2f} deg\033[0m")
            if target == du_total:
                print("Socket AI: already at that rotation; continue")
                return status
            print(f"Socket AI: pick up from socket, rotate {target - du_total:+.2f} deg "
                  f"(back to {target:+.2f} deg), insert; continue")
        status = rts.ReseatChipInSocket(sinkno, sktn, target - du_total, duttype)
        if status < 0:
            return status
        du_total = target
    return status


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("usage: python socket_ai_client.py <socket.bmp> [server_url]")
        sys.exit(1)
    import datetime

    # unique id, so repeated manual tests do not overwrite each other's saved files
    manual_id = "manual_" + datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    print(inspect_socket_image(sys.argv[1], chip_id=manual_id,
                               server_url=sys.argv[2] if len(sys.argv) > 2 else SERVER_URL))
