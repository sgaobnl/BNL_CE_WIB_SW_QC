import pickle
import numpy as np
import QC_components.qc_log as log
from wib_cfgs import WIB_CFGS

chk = WIB_CFGS()

def monitor_power_rail_analysis(interface, datadir, fembNo):
    log.tmp_log.clear()
    log.chkflag.clear()
    log.badlist.clear()
    fsub = "MON_PWR_" + interface + "_200mVBL_14_0mVfC_2_0us_0x00.bin"
    fpwr = datadir + fsub
    with open(fpwr, 'rb') as fn:
        monvols = pickle.load(fn)
        vfembs = monvols[1]
        vold = monvols[0]
    vkeys = list(vold.keys())
    LSB = 2.048 / 16384
    for ifemb in range(len(vfembs)):
        femb_id = "FEMB ID {}".format(fembNo['femb%d' % vfembs[ifemb]])
        mvold = {}
        for key in vkeys:
            f0, f1, f2, f3 = zip(*vold[key])
            vfs = [f0, f1, f2, f3]
            vf = list(vfs[vfembs[ifemb]])
            vf.remove(np.max(vf))
            vf.remove(np.min(vf))
            vfm = np.mean(vf)
            vfstd = np.std(vf)
            mvold[key] = [vfm, vfstd]

        mvvold = {}
        for key in vkeys:
            if "GND" in key:
                mvvold[key] = [abs(int(mvold[key][0] * LSB * 1000))]
            elif "HALF" in key:
                mvvold[key.replace("_HALF", "")] = [abs(int((mvold[key][0] - mvold["GND"][0]) * LSB * 2 * 1000))]
            else:
                mvvold[key] = [abs(int((mvold[key][0] - mvold["GND"][0]) * LSB * 1000))]
        print(mvvold)
        log.tmp_log[femb_id] = mvvold
        log.tmp_log[femb_id]["Result"] = True
    return log.tmp_log







def monitor_power_rail(interface, fembs, datadir, save = False):
    sps = 10
    vold = chk.wib_vol_mon(femb_ids=fembs, sps=sps)
    dkeys = list(vold.keys())
    LSB = 2.048 / 16384
    for fembid in fembs:
        vgnd = vold["GND"][0][fembid]
        for key in dkeys:
            if "GND" in key:
                print(key, vold[key][0][fembid], vold[key][0][fembid] * LSB)
            elif "HALF" in key:
                print(key, vold[key][0][fembid], (vold[key][0][fembid] - vgnd) * LSB * 2, "voltage offset caused by power cable is substracted")
            else:
                print(key, vold[key][0][fembid], (vold[key][0][fembid] - vgnd) * LSB, "voltage offset caused by power cable is substracted")
    if save:
        fp = datadir + "MON_PWR_"+ interface +"_{}_{}_{}_0x{:02x}.bin".format("200mVBL", "14_0mVfC", "2_0us", 0x00)
        with open(fp, 'wb') as fn:
            pickle.dump([vold, fembs], fn)
    return vold