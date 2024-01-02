import os
import sys
from wib_cfgs import WIB_CFGS
import pickle
from QC_tools import ana_tools
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
from collections import defaultdict
import components.assembly_log as log
import QC_check

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

#   03  check registers
def register_check(fembs, fembNo, times = 1, Decision = False):
    print("Check FEMB registers")
    report_log = defaultdict(dict)
    #   reset 3-ASIC
    for ifemb in fembs:
        femb_id = "FEMB ID {}".format(fembNo['femb%d' % ifemb])
        errflag = chk.femb_cd_chkreg(ifemb)
        if errflag:
            print("FEMB ID {} faild COLDATA register check 1, continue testing".format(fembNo['femb%d' % ifemb]))
            log.report_log03[femb_id]["COLDATA_REG_CHK_{}".format(times)] =("FEMB ID {} faild COLDATA register 1 check".format(fembNo['femb%d' % ifemb]))
            log.report_log03[femb_id]["Result"] = False
            if Decision:

                fembs.remove(ifemb)
                fembNo.pop('femb%d' % ifemb)
                strcs = input("skip this femb? (Y/N)")
                if "Y" in strcs or "y" in strcs:
                    pass
                else:
                    print("Exit anyway...")
                    exit()

            continue
        else:
            log.report_log03[femb_id]["COLDATA_REG_CHK_{}".format(times)] = ("FEMB ID {} SUCCESS".format(fembNo['femb%d' % ifemb]))
            log.report_log03[femb_id]["Result"] = True
        errflag = chk.femb_adc_chkreg(ifemb)
        if errflag:
            print("FEMB ID {} faild COLDADC register check 1, continue testing".format(fembNo['femb%d' % ifemb]))
            log.report_log03[femb_id]["ColdADC_REG_CHK_{}".format(times)] = ("FEMB ID {} faild ColdADC register 1 check".format(fembNo['femb%d' % ifemb]))
            log.report_log03[femb_id]["Result"] = False
            if Decision:

                fembs.remove(ifemb)
                fembNo.pop('femb%d' % ifemb)
                strcs = input("skip this femb? (Y/N)")
                if "Y" in strcs or "y" in strcs:
                    pass
                else:
                    print("Exit anyway...")
                    exit()

        else:
            log.report_log03[femb_id]["ColdADC_REG_CHK_{}".format(times)] = ("FEMB ID {} SUCCESS".format(fembNo['femb%d' % ifemb]))
            log.report_log03[femb_id]["Result"] = True


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

def monitor_power_rail_analysis(interface, datadir, reportdir, fembNo):
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
        log.power_rail_report_log[femb_id] = mvvold
        print(log.power_rail_report_log[femb_id])
        log.power_rail_report_log[femb_id]["Result"] = True

    qc_tools.PrintVolMON(vfembs, mvvold, reportdir, fsub)

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

def merge_pngs(png_paths, output_path):
    images = [plt.imread(png_path) for png_path in png_paths]

    # Determine the maximum height among images
    max_height = max(image.shape[0] for image in images)

    # Pad images to have the same height
    padded_images = [np.pad(image, ((0, max_height - image.shape[0]), (0, 0), (0, 0)), mode='constant') for image in images]

    # Concatenate images horizontally
    merged_image = np.concatenate(padded_images, axis=1)

    # Display the merged image
    plt.imshow(merged_image)
    plt.axis('off')

    # Save the figure as a new PNG file
    plt.savefig(output_path, bbox_inches='tight', pad_inches=0)
    plt.close()



#   item04 RMS_PED PULSE
def rms_ped_ana(rms_rawdata, fembs, fembNo, datareport, fname):
    pldata = qc_tools.data_decode(rms_rawdata, fembs)
    for ifemb in range(len(fembs)):
        femb_id = "FEMB ID {}".format(fembNo['femb%d' % fembs[ifemb]])
        ped, rms = qc_tools.GetRMS(pldata, fembs[ifemb], datareport[fembs[ifemb]], fname)
        tmp = QC_check.CHKPulse(ped, 5)
        log.chkflag["BL"].append(tmp[0])
        log.badlist["BL"].append(tmp[1])
        log.report_log04[femb_id]["baseline chk_status"] = tmp[0]
        log.report_log04[femb_id]["baseline err_status"] = tmp[1]

        tmp = QC_check.CHKPulse(rms, 5)
        log.chkflag["RMS"].append(tmp[0])
        log.badlist["RMS"].append(tmp[1])
        log.report_log04[femb_id]["RMS chk_status"] = tmp[0]
        log.report_log04[femb_id]["RMS err_status"] = tmp[1]

        if (log.report_log04[femb_id]["baseline chk_status"] == False) and (log.report_log04[femb_id]["RMS chk_status"] == False):
            log.report_log04[femb_id]["Result"] = True
        else:
            log.report_log04[femb_id]["Result"] = False


#   item05  Power analysis
def power_ana(fembs, fembNo, datareport, pwr_meas, env):
    for ifemb in range(len(fembs)):
        femb_id = "FEMB ID {}".format(fembNo['femb%d' % fembs[ifemb]])
        fp_pwr = datareport[fembs[ifemb]] + "pwr_meas"
        qc_tools.PrintPWR(pwr_meas, fembs[ifemb], fp_pwr)
        tmp = QC_check.CHKPWR(pwr_meas, fembs[ifemb], env)
        log.chkflag["PWR"].append(tmp[0])
        log.badlist["PWR"].append(tmp[1])
        log.report_log05[femb_id]["Power check status"] = tmp[0]
        log.report_log05[femb_id]["Power ERROR status"] = tmp[1]



#   item07  Single-ended pulse data
def se_pulse_ana(pls_rawdata, fembs, fembNo, datareport, fname):
    pldata = qc_tools.data_decode(pls_rawdata, fembs)

    for ifemb in range(len(fembs)):
        femb_id = "FEMB ID {}".format(fembNo['femb%d' % fembs[ifemb]])
        ppk, npk, bl = qc_tools.GetPeaks(pldata, fembs[ifemb], datareport[fembs[ifemb]], fname, funcfit=False)
        # outfp = datareport[fembs[ifemb]] + "pulse_{}.bin".format(fname)
        # with open(outfp, 'wb') as fn:
        #      pickle.dump([ppk,npk,bl], fn)

        tmp = QC_check.CHKPulse(ppk)
        log.chkflag["Pulse_SE"]["PPK"].append(tmp[0])
        log.badlist["Pulse_SE"]["PPK"].append(tmp[1])
        log.report_log07[femb_id]["Pulse_SE PPK chk_status"] = tmp[0]
        log.report_log07[femb_id]["Pulse_SE PPK err_status"] = tmp[1]

        tmp = QC_check.CHKPulse(npk)
        log.chkflag["Pulse_SE"]["NPK"].append(tmp[0])
        log.badlist["Pulse_SE"]["NPK"].append(tmp[1])
        log.report_log07[femb_id]["Pulse_SE NPK chk_status"] = tmp[0]
        log.report_log07[femb_id]["Pulse_SE NPK err_status"] = tmp[1]

        tmp = QC_check.CHKPulse(bl)
        log.chkflag["Pulse_SE"]["BL"].append(tmp[0])
        log.badlist["Pulse_SE"]["BL"].append(tmp[1])
        log.report_log07[femb_id]["Pulse_SE BL chk_status"] = tmp[0]
        log.report_log07[femb_id]["Pulse_SE BL err_status"] = tmp[1]

        if (log.report_log07[femb_id]["Pulse_SE PPK chk_status"] == False) and (
                log.report_log07[femb_id]["Pulse_SE NPK chk_status"] == False) and (
                log.report_log07[femb_id]["Pulse_SE BL chk_status"] == False):
            log.report_log07[femb_id]["Result"] = True
        else:
            log.report_log07[femb_id]["Result"] = False

#   item08  DIFF pulse data
def DIFF_pulse_data(pls_rawdata, fembs, fembNo,datareport, fname):
    pldata = qc_tools.data_decode(pls_rawdata, fembs)
    for ifemb in range(len(fembs)):
        femb_id = "FEMB ID {}".format(fembNo['femb%d' % fembs[ifemb]])
        ppk, npk, bl = qc_tools.GetPeaks(pldata, fembs[ifemb], datareport[fembs[ifemb]], fname)

        tmp = QC_check.CHKPulse(ppk)
        log.chkflag["Pulse_DIFF"]["PPK"].append(tmp[0])
        log.badlist["Pulse_DIFF"]["PPK"].append(tmp[1])
        log.report_log08[femb_id]["Pulse_DIFF PPK err_status"] = tmp[1]
        log.report_log08[femb_id]["Pulse_DIFF PPK chk_status"] = tmp[0]

        tmp = QC_check.CHKPulse(npk)
        log.chkflag["Pulse_DIFF"]["NPK"].append(tmp[0])
        log.badlist["Pulse_DIFF"]["NPK"].append(tmp[1])
        log.report_log08[femb_id]["Pulse_DIFF npk err_status"] = tmp[1]
        log.report_log08[femb_id]["Pulse_DIFF npk chk_status"] = tmp[0]

        tmp = QC_check.CHKPulse(bl)
        log.chkflag["Pulse_DIFF"]["BL"].append(tmp[0])
        log.badlist["Pulse_DIFF"]["BL"].append(tmp[1])
        log.report_log08[femb_id]["Pulse_DIFF bl err_status"] = tmp[1]
        log.report_log08[femb_id]["Pulse_DIFF bl chk_status"] = tmp[0]

        if (log.report_log08[femb_id]["Pulse_DIFF PPK chk_status"] == False) and (
                log.report_log08[femb_id]["Pulse_DIFF PPK chk_status"] == False) and (
                log.report_log08[femb_id]["Pulse_DIFF bl chk_status"] == False):
            log.report_log08[femb_id]["Result"] = True
        else:
            log.report_log08[femb_id]["Result"] = False


#   item10  monitor path
#   Data Acquire
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

#   Data Analysis
def mon_path_ana(fembs, mon_refs, mon_temps, mon_adcs, datareport, fembNo, env):
    nchips = range(8)
    qc_tools.PrintMON(fembs, nchips, mon_refs, mon_temps, mon_adcs, datareport, makeplot=True)
    log.report_log10["ITEM"] = "10 FEMB monitoring Path"
    for ifemb in range(len(fembs)):
        femb_id = "FEMB ID {}".format(fembNo['femb%d' % fembs[ifemb]])
        log.report_log10[femb_id]["Result"] = False
        tmp = QC_check.CHKFET(mon_temps, fembs[ifemb], nchips, env)
        log.chkflag["MON_T"].append(tmp[0])
        log.badlist["MON_T"].append(tmp[1])

        tmp = QC_check.CHKFEBGP(mon_refs, fembs[ifemb], nchips, env)
        log.chkflag["MON_BGP"].append(tmp[0])
        log.badlist["MON_BGP"].append(tmp[1])

        tmp = QC_check.CHKADC(mon_adcs, fembs[ifemb], nchips, "VCMI", 985, 40, 935, 40, env)
        log.chkflag["MON_ADC"]["VCMI"].append(tmp[0])
        log.badlist["MON_ADC"]["VCMI"].append(tmp[1])

        tmp = QC_check.CHKADC(mon_adcs, fembs[ifemb], nchips, "VCMO", 1272, 40, 1232, 40, env)
        log.chkflag["MON_ADC"]["VCMO"].append(tmp[0])
        log.badlist["MON_ADC"]["VCMO"].append(tmp[1])

        tmp = QC_check.CHKADC(mon_adcs, fembs[ifemb], nchips, "VREFP", 1988, 40, 1980, 40, env)
        log.chkflag["MON_ADC"]["VREFP"].append(tmp[0])
        log.badlist["MON_ADC"]["VREFP"].append(tmp[1])

        tmp = QC_check.CHKADC(mon_adcs, fembs[ifemb], nchips, "VREFN", 550, 40, 482, 40, env)
        log.chkflag["MON_ADC"]["VREFN"].append(tmp[0])
        log.badlist["MON_ADC"]["VREFN"].append(tmp[1])

        tmp = QC_check.CHKADC(mon_adcs, fembs[ifemb], nchips, "VSSA", 105, 40, 35, 20, env)
        log.chkflag["MON_ADC"]["VSSA"].append(tmp[0])
        log.badlist["MON_ADC"]["VSSA"].append(tmp[1])







