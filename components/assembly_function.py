import os
import sys
from wib_cfgs import WIB_CFGS
import pickle
from QC_tools import ana_tools
import numpy as np
import time

chk = WIB_CFGS()
qc_tools = ana_tools()

def Create_data_folders(fembNo, env, toytpc):

    datadir = "./CHK/"
    for key,femb_no in fembNo.items():
        datadir = datadir + "femb{}_".format(femb_no)

    datadir = datadir+"{}_{}".format(env,toytpc)
    n=1
    while (os.path.exists(datadir)):
        if n==1:
            datadir = datadir + "_R{:03d}".format(n)
        else:
            datadir = datadir[:-3] + "{:03d}".format(n)
        n=n+1
        if n>20:
            raise Exception("There are more than 20 folders...")

    try:
        os.makedirs(datadir)
    except OSError:
        print ("Error to create folder %s"%datadir)
        sys.exit()

    datadir = datadir+"/"

    return datadir

def Create_report_folders(fembs, fembNo, env, toytpc, datadir):

    reportdir = datadir + "report/"

    PLOTDIR = {}

    for ifemb in fembs:
        femb_no = fembNo['femb%d'%ifemb]
        plotdir = reportdir + "FEMB{}_{}_{}".format(femb_no, env, toytpc)

        if os.path.exists(plotdir):
            pass
        else:
            try:
                os.makedirs(plotdir)
            except OSError:
                print ("Error to create folder %s"%plotdir)
                sys.exit()

        plotdir = plotdir+"/"


        PLOTDIR[ifemb] = plotdir

    return PLOTDIR

def register_check(en, fembs, fembNo, outfile):
    if en:
        print("Check FEMB registers")
        #   reset 3-ASIC
        for ifemb in fembs:
            errflag = chk.femb_cd_chkreg(ifemb)
            if errflag:
                print("FEMB ID {} faild COLDATA register check 1, continue testing".format(fembNo['femb%d' % ifemb]))
                outfile.write("FEMB ID {} faild COLDATA register 1 check\n".format(fembNo['femb%d' % ifemb]))
                # fembs.remove(ifemb)
                # fembNo.pop('femb%d'%ifemb)
                continue

            errflag = chk.femb_adc_chkreg(ifemb)
            if errflag:
                print("FEMB ID {} faild COLDADC register check 1, continue testing".format(fembNo['femb%d' % ifemb]))
                outfile.write("FEMB ID {} faild COLDADC register 1 check\n".format(fembNo['femb%d' % ifemb]))
                # fembs.remove(ifemb)
                # fembNo.pop('femb%d'%ifemb)
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
                print(key, vold[key][0][fembid], (vold[key][0][fembid] - vgnd) * LSB * 2,
                      "voltage offset caused by power cable is substracted")
            else:
                print(key, vold[key][0][fembid], (vold[key][0][fembid] - vgnd) * LSB,
                      "voltage offset caused by power cable is substracted")
    if save:
        fp = datadir + "MON_PWR_"+ interface +"_{}_{}_{}_0x{:02x}.bin".format("200mVBL", "14_0mVfC", "2_0us", 0x00)
        with open(fp, 'wb') as fn:
            pickle.dump([vold, fembs], fn)
    return vold

def monitor_power_rail_analysis(interface, datadir, reportdir):
    fsub = "MON_PWR_" + interface + "_200mVBL_14_0mVfC_2_0us_0x00.bin"
    fpwr = datadir + fsub
    with open(fpwr, 'rb') as fn:
        monvols = pickle.load(fn)
        vfembs = monvols[1]
        vold = monvols[0]
    vkeys = list(vold.keys())
    LSB = 2.048 / 16384
    for ifemb in range(len(vfembs)):
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
                mvvold[key] = [int(mvold[key][0] * LSB * 1000)]
            elif "HALF" in key:
                mvvold[key.replace("_HALF", "")] = [int((mvold[key][0] - mvold["GND"][0]) * LSB * 2 * 1000)]
            else:
                mvvold[key] = [int((mvold[key][0] - mvold["GND"][0]) * LSB * 1000)]

    qc_tools.PrintVolMON(vfembs, mvvold, reportdir, fsub)

def monitoring_path(fembs, snc, sg0, sg1, datadir, save):
    sps = 1
    print("monitor bandgap reference")
    nchips = range(8)
    mon_refs = {}
    for i in nchips:  # 8 chips per femb
        adcrst = chk.wib_fe_mon(femb_ids=fembs, mon_type=2, mon_chip=i, snc=snc, sg0=sg0, sg1=sg1, sps=sps)
        mon_refs[f"chip{i}"] = adcrst[7]

    print("monitor temperature")
    mon_temps = {}
    for i in nchips:
        adcrst = chk.wib_fe_mon(femb_ids=fembs, mon_type=1, mon_chip=i, snc=snc, sg0=sg0, sg1=sg1, sps=sps)
        mon_temps[f"chip{i}"] = adcrst[7]

    print("monitor ColdADCs")
    mon_adcs = {}
    for i in nchips:
        mon_adc = chk.wib_adc_mon_chip(femb_ids=fembs, mon_chip=i, sps=sps)
        mon_adcs[f"chip{i}"] = mon_adc

    if save:
        fp = datadir + "Mon_{}_{}.bin".format("200mVBL", "14_0mVfC")

        with open(fp, 'wb') as fn:
            pickle.dump([mon_refs, mon_temps, mon_adcs, fembs], fn)

    return mon_refs, mon_temps, mon_adcs




################ reset COLDATA, COLDADC and LArASIC ##############
def chip_reset(fembs):
    print("Reset FEMBs")
    chk.femb_cd_rst()
    chk.femb_cd_rst()
    time.sleep(0.1)
    for ifemb in fembs:
        chk.femb_cd_fc_act(ifemb, act_cmd="rst_adcs")
        time.sleep(0.01)
        chk.femb_cd_fc_act(ifemb, act_cmd="rst_adcs")
        time.sleep(0.01)
        chk.femb_cd_fc_act(ifemb, act_cmd="rst_larasics")
        chk.femb_cd_fc_act(ifemb, act_cmd="rst_larasics")
        time.sleep(0.01)
        chk.femb_cd_fc_act(ifemb, act_cmd="rst_larasic_spi")
        chk.femb_cd_fc_act(ifemb, act_cmd="rst_larasic_spi")

    time.sleep(0.1)

# def generate_report(fembs, snc, sg0, sg1, datadir, save):
