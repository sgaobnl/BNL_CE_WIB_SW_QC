"""
RTS_ROBOT_TEST.py - robot moves + AI socket inspection only, same flow as RTS_DAT_rev0.py.

No QC: no LN2/init check, no user GUI, no emails, no OCR tray scan, no DAT power (ssh),
no DAT_QC, no cryo, no bad tray, no data copy. MAKE SURE THE DAT BOARD IS POWERED OFF.

As in RTS_DAT_rev0.py:
  duts = chip indices on the tray (0..89, trayc = chipi%15+1, trayr = chipi//15+1)
  while duts left:
    MovetoSoket : next chips tray -> sockets skts=[0..7] (sktn = skt+1), one by one,
                  each followed by the AI socket check:
                    good -> continue
                    bad  -> pick the chip up from the socket only (no tray), rotate +0.5 deg, insert
                    good -> continue
                    bad  -> pick up, rotate -1.0 deg (now -0.5 deg from the first insertion), insert
                    good -> continue
                    bad  -> compare the z_max of the 3 inspections, pick up and insert at the
                            rotation with the smallest z_max (not moved if that is the current
                            one); this last insertion is inspected for the log only
                  (--reseat-du = angles from the first insertion, default 0.5,-0.5; the robot step
                  is the difference; robot command ReseatChipInSocket)
    MovetoTray  : all chips in the sockets -> back to their original tray position
  the last round uses only as many sockets as there are chips left.

Usage (on the RTS PC, from the BNL_CE_WIB_SW_QC folder):
  python RTS_ROBOT_TEST.py --chips 0-20            # rounds: 0-7, 8-15, 16-20
  python RTS_ROBOT_TEST.py --chips 0-7 --cycles 3  # same 8 chips 3 times
  python RTS_ROBOT_TEST.py --chips 0,3,5 --no-ai   # robot moves only
  python RTS_ROBOT_TEST.py --reseat-du 0.5,-1     # inspected angles 0, +0.5, -1 deg
Needs the ReseatChipInSocket command in the Epson project (RTS_server.prg / RTS_tools.prg).
Results: <rootdir>/images/ (pictures from the robot), robot_test_log.csv, robot_test_log.bin
"""

import argparse
import csv
import datetime
import os
import pickle
import sys
import time

from RTS_CFG import RTS_CFG
from set_rootpath import rootdir_cs
import socket_ai_client
from socket_ai_client import socket_ai_rotate_reseat

DUTTYPE = "FE"   # the socket AI model is trained on LArASIC only
CSV_FIELDS = ["round", "chipi", "trayc", "trayr", "sktn", "ts_first_insert", "ts_final",
              "n_inspections", "n_reseats", "reseat_dU", "results", "scores", "z_maxes", "worst_sides",
              "final_dU", "final_result", "t2s_s", "s2t_s"]


def parse_list(spec):
    """'0-20' -> [0..20];  '0-3,7,9-10' -> [0, 1, 2, 3, 7, 9, 10]"""
    out = []
    for part in spec.split(","):
        part = part.strip()
        if "-" in part:
            a, b = part.split("-")
            out.extend(range(int(a), int(b) + 1))
        elif part:
            out.append(int(part))
    return out


def tray_pos(chipi):
    """Chip index (0..89) -> (trayc 1..15, trayr 1..6), as in RTS_DAT_rev0.py."""
    return (chipi % 15) + 1, (chipi // 15) + 1


def RTS_debug(info):
    """Robot error, as RTS_DAT_rev0.RTS_debug but without email: 444 -> shutdown, 6 -> fixed."""
    print("\033[91mPlease check the error information on EPSON RC\033[0m")
    print(info)
    while True:
        print("444-> Shutdown RTS and exit anyway")
        print("6->fixed,")
        userinput = input("Please contact tech coordinator : ")
        if len(userinput) > 0:
            if "444" in userinput:
                rts.MotorOn()
                rts.JumpToCamera()
                rts.rts_shutdown()
                print("Exit anyway")
                sys.exit(1)
            elif "6" in userinput[0]:
                input("Make sure the chip back to orginal position and click anykey")
                rts.MotorOn()
                break


def MovetoSoket(sinkno, duts, skts, use_ai, reseat_du, records):
    """Fill the sockets `skts` with the first chips of `duts`; returns (duts left, dut_skt {ts: (chipi, skt)})."""
    dut_skt = {}
    rts.MotorOn()
    rts.PumpOn()
    time.sleep(5)
    rts.PumpOff()

    tmpi = 0
    while tmpi < len(skts) and len(duts) > 0:
        skt = skts[tmpi]
        chipi = duts[0]
        trayc, trayr = tray_pos(chipi)
        sktn = skt + 1
        t0 = time.time()
        status = rts.MoveChipFromTrayToSocket(trayno, trayc, trayr, sinkno, sktn, DUTTYPE)
        ai_log = []
        first_ts = rts.msg
        if (status >= 0) and use_ai:  # AI socket inspection on wcgpu1, rotated reseats in the socket if bad
            status = socket_ai_rotate_reseat(rts, rootdir, sinkno, sktn, DUTTYPE, reseat_du, ai_log)
            if status < 0:
                RTS_debug("Reseat in socket failed: chip may be in Sinkno={}, Skt={} or on the stinger. "
                          "Put it back to TrayNo={}, Col(1-15)={}, Row(1-6)={}"
                          .format(sinkno, sktn, trayno, trayc, trayr))
                continue  # same chip, same socket again
        if status < 0:
            RTS_debug("T2S: chip on original TrayNo={}, Col(1-15)={}, Row(1-6)={} -> Sinkno={}, Skt={}"
                      .format(trayno, trayc, trayr, sinkno, sktn))
            continue  # same chip, same socket again
        duts = duts[1:]
        dut_skt[rts.msg] = (chipi, skt)
        records[rts.msg] = {"chipi": chipi, "trayc": trayc, "trayr": trayr, "sktn": sktn,
                            "ts_first_insert": first_ts, "ts_final": rts.msg, "ai": ai_log,
                            "t2s_s": round(time.time() - t0, 1)}
        tmpi = tmpi + 1
    rts.rts_idle()
    return duts, dut_skt


def MovetoTray(sinkno, dut_skt, records):
    """Move every chip in `dut_skt` from its socket back to its original tray position."""
    rts.MotorOn()
    rts.PumpOn()
    time.sleep(5)
    rts.PumpOff()

    for ts in sorted(dut_skt, key=lambda k: dut_skt[k][1]):  # socket order
        chipi, skt = dut_skt[ts]
        trayc, trayr = tray_pos(chipi)
        sktn = skt + 1
        while True:
            t0 = time.time()
            status = rts.MoveChipFromSocketToTray(sinkno, sktn, trayno, trayc, trayr, DUTTYPE)
            if status >= 0:
                records[ts]["s2t_s"] = round(time.time() - t0, 1)
                break
            RTS_debug("S2T: chip on original Sinkno={}, Skt={} -> TrayNo={}, Col(1-15)={}, Row(1-6)={}"
                      .format(sinkno, sktn, trayno, trayc, trayr))
    rts.rts_idle()


def csv_row(rnd, rec):
    ai = rec["ai"]
    return {"round": rnd, "chipi": rec["chipi"], "trayc": rec["trayc"], "trayr": rec["trayr"],
            "sktn": rec["sktn"], "ts_first_insert": rec["ts_first_insert"], "ts_final": rec["ts_final"],
            "n_inspections": len(ai), "n_reseats": max(0, len(ai) - 1),
            "reseat_dU": "|".join(f"{a['dU_total']:+g}" for a in ai[1:]),
            "results": "|".join(a["result"] for a in ai),
            "scores": "|".join(str(a.get("score", "")) for a in ai),
            "z_maxes": "|".join(str(a.get("z_max", "")) for a in ai),
            "final_dU": f"{ai[-1]['dU_total']:+g}" if ai else "",
            "worst_sides": "|".join(str(a.get("worst_side", "")) for a in ai),
            "final_result": ai[-1]["result"] if ai else "no_ai",
            "t2s_s": rec.get("t2s_s", ""), "s2t_s": rec.get("s2t_s", "")}


def save_logs(rows, logs):
    with open(os.path.join(rootdir, "robot_test_log.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        w.writeheader()
        w.writerows(rows)
    with open(os.path.join(rootdir, "robot_test_log.bin"), "wb") as f:
        pickle.dump(logs, f)


def print_summary(rows):
    print("\n================ ROBOT TEST SUMMARY ================")
    print(f"chips moved              : {len(rows)}")
    print(f"good at first inspection : {sum(r['results'].startswith('good') for r in rows)}")
    print(f"good after reseat        : {sum(r['final_result'] == 'good' and r['n_reseats'] > 0 for r in rows)}")
    print(f"still bad after reseats  : {sum(r['final_result'] == 'bad' for r in rows)}")
    print(f"  ... of which returned to the lowest-z_max rotation: "
          f"{sum(r['final_result'] == 'bad' and r['n_inspections'] > 3 for r in rows)}")
    print(f"AI server errors         : {sum(r['final_result'] == 'error' for r in rows)}")
    print(f"total reseats            : {sum(r['n_reseats'] for r in rows)}")
    print("====================================================")


def server_health():
    """The server's /health reply (model, threshold), or None if it cannot be reached."""
    try:
        r = socket_ai_client.requests.get(socket_ai_client.SERVER_URL + "/health", timeout=5)
        return r.json() if r.ok else None
    except Exception:
        return None


############################################################
p = argparse.ArgumentParser(description="Robot move + AI socket inspection test (no QC)")
p.add_argument("--chips", default="0-7", help="chip indices on the tray, 0..89, e.g. 0-20 (default 0-7)")
p.add_argument("--skts", default="0-7", help="sockets to fill each round, 0..7 (default 0-7)")
p.add_argument("--trayno", type=int, default=2, help="tray with the chips (default 2)")
p.add_argument("--sinkno", type=int, default=2, help="DAT board (default 2)")
p.add_argument("--cycles", type=int, default=1, help="repeat the whole chip list N times")
p.add_argument("--no-ai", action="store_true", help="skip the socket AI check (robot moves only)")
p.add_argument("--reseat-du", default="0.5,-0.5",
               help="angles (deg, offset from the first insertion) for the in-socket reseats "
                    "while the AI says bad (default 0.5,-0.5 = rotate +0.5, then -1.0); still bad after "
                    "the last one -> reinserted at the angle with the smallest z_max")
p.add_argument("--rootdir", default=None, help="output folder (default <FE rootdir>/ROBOT_TEST_<time>/)")
args = p.parse_args()

trayno = args.trayno
sinkno = args.sinkno
skts = parse_list(args.skts)
use_ai = not args.no_ai
reseat_du = [float(x) for x in args.reseat_du.split(",") if x.strip()]
rootdir = args.rootdir or rootdir_cs(DUTTYPE) + "ROBOT_TEST_" + datetime.datetime.now().strftime("%Y%m%d%H%M%S") + "/"
os.makedirs(os.path.join(rootdir, "images"), exist_ok=True)

print(f"Robot test: tray {trayno} chips {args.chips} -> DAT {sinkno} sockets {[s + 1 for s in skts]}, "
      f"{args.cycles} cycle(s), socket AI {'ON (' + socket_ai_client.SERVER_URL + ')' if use_ai else 'OFF'}"
      + (f", reseat rotations {reseat_du} deg" if use_ai else ""))
print(f"Output: {rootdir}")
if use_ai:
    health = server_health()
    print("Socket AI server:", health if health else
          "\033[93mNOT reachable - inspections will return 'error' (test continues)\033[0m")
input("\033[93mMake sure the DAT board is POWERED OFF and the tray is in place. Press Enter to start...\033[0m")

rts = RTS_CFG()
rts.msg = "10000000000"
rts.rts_init(port=2001, host_ip='192.168.0.2')
rts.RootDirSet(rootdir=rootdir)
rts.MotorOn()
rts.JumpToCamera()

logs = {"args": vars(args), "rounds": []}
rows = []
rnd = 0
for cycle in range(args.cycles):
    duts = parse_list(args.chips)
    while len(duts) > 0:
        rnd += 1
        records = {}
        print(f"\n***** round {rnd}: chips {duts[:len(skts)]} -> sockets *****")
        duts, dut_skt = MovetoSoket(sinkno, duts, skts, use_ai, reseat_du, records)
        MovetoTray(sinkno, dut_skt, records)
        logs["rounds"].append({"round": rnd, "cycle": cycle + 1, "dut_skt": dut_skt, "records": records})
        rows.extend(csv_row(rnd, records[ts]) for ts in dut_skt)
        save_logs(rows, logs)
        print("Remain chips on tray: ", duts)

rts.JumpToCamera()
rts.rts_shutdown()
save_logs(rows, logs)
print_summary(rows)
print(f"Log: {os.path.join(rootdir, 'robot_test_log.csv')}")
