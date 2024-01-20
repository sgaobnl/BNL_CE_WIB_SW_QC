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
        print(Decision)
        if errflag:
            print("FEMB ID {} faild COLDATA register check 1, continue testing".format(fembNo['femb%d' % ifemb]))
            log.report_log03[femb_id]["COLDATA_REG_{}".format(times)] =("FEMB ID {} faild COLDATA register 1 check".format(fembNo['femb%d' % ifemb]))

            if Decision:
                log.report_log03[femb_id]["Result"] = False
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
            log.report_log03[femb_id]["COLDATA_REG_{}".format(times)] = ("Pass")

        errflag = chk.femb_adc_chkreg(ifemb)
        if errflag:
            print("FEMB ID {} faild COLDADC register check 1, continue testing".format(fembNo['femb%d' % ifemb]))
            log.report_log03[femb_id]["ColdADC_REG_CHK_{}".format(times)] = ("FEMB ID {} faild ColdADC register 1 check".format(fembNo['femb%d' % ifemb]))
            if Decision:
                log.report_log03[femb_id]["Result"] = False
                fembs.remove(ifemb)
                fembNo.pop('femb%d' % ifemb)
                strcs = input("skip this femb? (Y/N)")
                if "Y" in strcs or "y" in strcs:
                    pass
                else:
                    print("Exit anyway...")
                    exit()

        else:
            log.report_log03[femb_id]["ColdADC_REG_{}".format(times)] = ("Pass")
            if Decision:
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
                mvvold[key] = "{}".format(abs(int(mvold[key][0] * LSB * 1000)))
            elif "HALF" in key:
                mvvold[key.replace("_HALF", "")] = "{}".format(abs(int((mvold[key][0] - mvold["GND"][0]) * LSB * 2 * 1000)))
            else:
                mvvold[key] = "{}".format(abs(int((mvold[key][0] - mvold["GND"][0]) * LSB * 1000)))
        log.power_rail_report_log[femb_id] = mvvold
        print(log.power_rail_report_log[femb_id])
        log.power_rail_report_log[femb_id]["Result"] = True

    #qc_tools.PrintVolMON(vfembs, mvvold, reportdir, fsub)

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
        log.chkflag["BL"]=(tmp[0])
        log.badlist["BL"]=(tmp[1])
        ped_err_flag = tmp[0]
        baseline_err_status = tmp[1]
        log.report_log04[femb_id]["PED 128-CH std"] = tmp[2]

        tmp = QC_check.CHKPulse(rms, 5)
        log.chkflag["RMS"]=(tmp[0])
        log.badlist["RMS"]=(tmp[1])
        rms_err_flag = tmp[0]
        rms_err_status = tmp[1]
        log.report_log04[femb_id]["RMS 128-CH std"] = tmp[2]
        if (ped_err_flag == False) and (rms_err_flag == False):
            log.report_log04[femb_id]["Result"] = True
        else:
            log.report_log04[femb_id]["baseline err_status"] = baseline_err_status
            log.report_log04[femb_id]["RMS err_status"] = rms_err_status
            log.report_log04[femb_id]["Result"] = False


#   item05  Power analysis
def power_ana(fembs, ifemb, femb_id, pwr_meas, env, result = False):
    log.tmp_log.clear()
    log.chkflag.clear()
    log.badlist.clear()

    tmp = QC_check.CHKPWR(pwr_meas, fembs[ifemb], env)
    log.chkflag["PWR"]=(tmp[0])
    log.badlist["PWR"]=(tmp[1])

    bias_v = round(pwr_meas['FEMB%d_BIAS_V'%fembs[ifemb]],3)
    LArASIC_v = round(pwr_meas['FEMB{}_DC2DC{}_V'.format(fembs[ifemb],0)],3)
    COLDATA_v = round(pwr_meas['FEMB{}_DC2DC{}_V'.format(fembs[ifemb],1)],3)
    ColdADC_v = round(pwr_meas['FEMB{}_DC2DC{}_V'.format(fembs[ifemb],2)],3)

    bias_i = round(pwr_meas['FEMB%d_BIAS_I'%fembs[ifemb]],3)
    LArASIC_i = round(pwr_meas['FEMB{}_DC2DC{}_I'.format(fembs[ifemb], 0)], 3)
    COLDATA_i = round(pwr_meas['FEMB{}_DC2DC{}_I'.format(fembs[ifemb], 1)], 3)
    ColdADC_i = round(pwr_meas['FEMB{}_DC2DC{}_I'.format(fembs[ifemb], 2)], 3)

    bias_p = abs(round(bias_v * bias_i, 3))
    LArASIC_p = round(LArASIC_v * LArASIC_i, 3)
    COLDATA_p = round(COLDATA_v * COLDATA_i, 3)
    ColdADC_p = round(ColdADC_v * ColdADC_i, 3)
    total_p = bias_p + LArASIC_p + COLDATA_p + ColdADC_p

    # the | is used in Markdown table
    log.tmp_log[femb_id]["Result"] = result
    log.tmp_log[femb_id]["Measure Object"] = "BIAS | LArASIC | ColdDATA | ColdADC"
    log.tmp_log[femb_id]["V_set/V"] = " 5 | 3 | 3 | 3.5 "
    log.tmp_log[femb_id]["V_meas/V"] = "{} | {} | {} | {}".format(bias_v, LArASIC_v, COLDATA_v, ColdADC_v)
    log.tmp_log[femb_id]["I_meas/V"] = "{} | {} | {} | {}".format(abs(bias_i), LArASIC_i, COLDATA_i, ColdADC_i)
    log.tmp_log[femb_id]["P_meas/V"] = "{} | {} | {} | {}".format(bias_p, LArASIC_p, COLDATA_p, ColdADC_p)

    # log.report_log05[femb_id]["Power check status"] = tmp[0]
    log.tmp_log[femb_id]["Power ERROR status"] = "{} | | 'Total Power' | {} ".format(log.badlist["PWR"], total_p)

    return log.tmp_log

def power_ana_diff(fembs, fembNo, datareport, pwr_meas, env):
    for ifemb in range(len(fembs)):
        femb_id = "FEMB ID {}".format(fembNo['femb%d' % fembs[ifemb]])
        fp_pwr = datareport[fembs[ifemb]] + "pwr_meas"
        #qc_tools.PrintPWR(pwr_meas, fembs[ifemb], fp_pwr)
        tmp = QC_check.CHKPWR(pwr_meas, fembs[ifemb], env)
        log.chkflag["PWR"]=(tmp[0])
        log.badlist["PWR"].append(tmp[1])

        bias_v = round(pwr_meas['FEMB%d_BIAS_V'%fembs[ifemb]],3)
        LArASIC_v = round(pwr_meas['FEMB{}_DC2DC{}_V'.format(fembs[ifemb],0)],3)
        COLDATA_v = round(pwr_meas['FEMB{}_DC2DC{}_V'.format(fembs[ifemb],1)],3)
        ColdADC_v = round(pwr_meas['FEMB{}_DC2DC{}_V'.format(fembs[ifemb],2)],3)

        bias_i = round(pwr_meas['FEMB%d_BIAS_I'%fembs[ifemb]],3)
        LArASIC_i = round(pwr_meas['FEMB{}_DC2DC{}_I'.format(fembs[ifemb], 0)], 3)
        COLDATA_i = round(pwr_meas['FEMB{}_DC2DC{}_I'.format(fembs[ifemb], 1)], 3)
        ColdADC_i = round(pwr_meas['FEMB{}_DC2DC{}_I'.format(fembs[ifemb], 2)], 3)

        bias_p = round(bias_v * bias_i, 3)
        LArASIC_p = round(LArASIC_v * LArASIC_i, 3)
        COLDATA_p = round(COLDATA_v * COLDATA_i, 3)
        ColdADC_p = round(ColdADC_v * ColdADC_i, 3)
        total_p = bias_p + LArASIC_p + COLDATA_p + ColdADC_p

        # the | is used in Markdown table
        log.report_log09[femb_id]["name"] = "BIAS | LArASIC | ColdDATA | ColdADC"
        log.report_log09[femb_id]["V_set/V"] = " 5 | 3 | 3 | 3.5 "
        log.report_log09[femb_id]["V_meas/V"] = "{} | {} | {} | {}".format(bias_v, LArASIC_v, COLDATA_v, ColdADC_v)
        log.report_log09[femb_id]["I_meas/V"] = "{} | {} | {} | {}".format(abs(bias_i), LArASIC_i, COLDATA_i, ColdADC_i)
        log.report_log09[femb_id]["P_meas/V"] = "{} | {} | {} | {}".format(bias_p, LArASIC_p, COLDATA_p, ColdADC_p)

        # log.report_log05[femb_id]["Power check status"] = tmp[0]
        log.report_log09[femb_id]["Power ERROR status"] = "{} | | 'Total Power' | {} ".format(log.badlist["PWR"], total_p)

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
        td = 1
        print(123)
        print(tmp[0])
        print(456)
        print(tmp[1])
        log.chkflag["Pulse_SE"]["PPK"]=(tmp[0])
        print(789)
        print(log.chkflag["Pulse_SE"]["PPK"])
        log.badlist["Pulse_SE"]["PPK"]=(tmp[1])

        td = 2
        tmp = QC_check.CHKPulse(npk)
        log.chkflag["Pulse_SE"]["NPK"]=(tmp[0])
        log.badlist["Pulse_SE"]["NPK"]=(tmp[1])

        td = 3
        tmp = QC_check.CHKPulse(bl)
        log.chkflag["Pulse_SE"]["BL"]=(tmp[0])
        log.badlist["Pulse_SE"]["BL"]=(tmp[1])


        if (log.chkflag["Pulse_SE"]["PPK"] == False) and (log.chkflag["Pulse_SE"]["NPK"] == False) and (log.chkflag["Pulse_SE"]["BL"] == False):
            log.report_log07[femb_id]["Result"] = True
        else:
            log.report_log07[femb_id]["Pulse_SE PPK err_status"] = log.badlist["Pulse_SE"]["PPK"]
            log.report_log07[femb_id]["Pulse_SE NPK err_status"] = log.badlist["Pulse_SE"]["NPK"]
            log.report_log07[femb_id]["Pulse_SE BL err_status"] = log.badlist["Pulse_SE"]["BL"]
            log.report_log07[femb_id]["Result"] = False

#   item08  DIFF pulse data
def DIFF_pulse_data(pls_rawdata, fembs, fembNo,datareport, fname):
    pldata = qc_tools.data_decode(pls_rawdata, fembs)
    for ifemb in range(len(fembs)):
        femb_id = "FEMB ID {}".format(fembNo['femb%d' % fembs[ifemb]])
        ppk, npk, bl = qc_tools.GetPeaks(pldata, fembs[ifemb], datareport[fembs[ifemb]], fname)

        tmp = QC_check.CHKPulse(ppk)
        log.chkflag["Pulse_DIFF"]["PPK"]=(tmp[0])
        log.badlist["Pulse_DIFF"]["PPK"]=(tmp[1])

        tmp = QC_check.CHKPulse(npk)
        log.chkflag["Pulse_DIFF"]["NPK"]=(tmp[0])
        log.badlist["Pulse_DIFF"]["NPK"]=(tmp[1])

        tmp = QC_check.CHKPulse(bl)
        log.chkflag["Pulse_DIFF"]["BL"]=(tmp[0])
        log.badlist["Pulse_DIFF"]["BL"]=(tmp[1])

        if (log.chkflag["Pulse_DIFF"]["PPK"] == False) and (log.chkflag["Pulse_DIFF"]["NPK"] == False) and (log.chkflag["Pulse_DIFF"]["BL"] == False):
            log.report_log08[femb_id]["Result"] = True
        else:
            log.report_log08[femb_id]["Pulse_SE PPK err_status"] = log.badlist["Pulse_SE"]["PPK"]
            log.report_log08[femb_id]["Pulse_SE NPK err_status"] = log.badlist["Pulse_SE"]["NPK"]
            log.report_log08[femb_id]["Pulse_SE BL err_status"] = log.badlist["Pulse_SE"]["BL"]
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
    #qc_tools.PrintMON(fembs, nchips, mon_refs, mon_temps, mon_adcs, datareport, makeplot=True)
    log.report_log11["ITEM"] = "5 Monitoring Path"
    fadc = 1/(2**14)*2048
    fe_t = [None] * 8;    fe_bgp = [None] * 8;    vcmi = [None] * 8;    vcmo = [None] * 8
    vrefp = [None] * 8;    vrefn = [None] * 8;    vssa = [None] * 8
    for ifemb in fembs:
        femb_id = "FEMB ID {}".format(fembNo['femb%d' % ifemb])
        for i in nchips:  # 8 chips per board
            fe_t[i] = round(mon_temps[f'chip{i}'][0][ifemb] * fadc, 1)
            fe_bgp[i] = round(mon_refs[f'chip{i}'][0][ifemb] * fadc, 1)
            vcmi[i] = round(mon_adcs[f'chip{i}']["VCMI"][1][0][ifemb] * fadc, 1)
            vcmo[i] = round(mon_adcs[f'chip{i}']["VCMO"][1][0][ifemb] * fadc, 1)
            vrefp[i] = round(mon_adcs[f'chip{i}']["VREFP"][1][0][ifemb] * fadc, 1)
            vrefn[i] = round(mon_adcs[f'chip{i}']["VREFN"][1][0][ifemb] * fadc, 1)
            vssa[i] = round(mon_adcs[f'chip{i}']["VSSA"][1][0][ifemb] * fadc, 1)
        log.report_log11["Result"] = True
    # for ifemb in range(len(fembs)):
        log.report_log11[femb_id]["ASIC #"] = " 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 "
        log.report_log11[femb_id]["FE T"] = " {} | {} | {} | {} | {} | {} | {} | {} ".format(fe_t[0], fe_t[1], fe_t[2], fe_t[3], fe_t[4], fe_t[5], fe_t[6], fe_t[7])
        log.report_log11[femb_id]["FE BGP"] = " {} | {} | {} | {} | {} | {} | {} | {} ".format(fe_bgp[0], fe_bgp[1], fe_bgp[2], fe_bgp[3], fe_bgp[4], fe_bgp[5], fe_bgp[6], fe_bgp[7])
        log.report_log11[femb_id]["VCMI"] = " {} | {} | {} | {} | {} | {} | {} | {} ".format(vcmi[0], vcmi[1], vcmi[2], vcmi[3], vcmi[4], vcmi[5], vcmi[6], vcmi[7])
        log.report_log11[femb_id]["VCMO"] = " {} | {} | {} | {} | {} | {} | {} | {} ".format(vcmo[0], vcmo[1], vcmo[2], vcmo[3], vcmo[4], vcmo[5], vcmo[6], vcmo[7])
        log.report_log11[femb_id]["VREFP"] = " {} | {} | {} | {} | {} | {} | {} | {} ".format(vrefp[0], vrefp[1], vrefp[2], vrefp[3], vrefp[4], vrefp[5], vrefp[6], vrefp[7])
        log.report_log11[femb_id]["VREFN"] = " {} | {} | {} | {} | {} | {} | {} | {} ".format(vrefn[0], vrefn[1], vrefn[2], vrefn[3], vrefn[4], vrefn[5], vrefn[6], vrefn[7])
        log.report_log11[femb_id]["VSSA"] = " {} | {} | {} | {} | {} | {} | {} | {} ".format(vssa[0], vssa[1], vssa[2], vssa[3], vssa[4], vssa[5], vssa[6], vssa[7])
    for ifemb in range(len(fembs)):
        tmp = QC_check.CHKFET(mon_temps, fembs[ifemb], nchips, env)
        log.chkflag["MON_T"]=(tmp[0])
        log.badlist["MON_T"]=(tmp[1])

        tmp = QC_check.CHKFEBGP(mon_refs, fembs[ifemb], nchips, env)
        log.chkflag["MON_BGP"]=(tmp[0])
        log.badlist["MON_BGP"]=(tmp[1])

        tmp = QC_check.CHKADC(mon_adcs, fembs[ifemb], nchips, "VCMI", 985, 40, 935, 40, env)
        log.chkflag["MON_ADC"]["VCMI"]=(tmp[0])
        log.badlist["MON_ADC"]["VCMI"]=(tmp[1])

        tmp = QC_check.CHKADC(mon_adcs, fembs[ifemb], nchips, "VCMO", 1272, 40, 1232, 40, env)
        log.chkflag["MON_ADC"]["VCMO"]=(tmp[0])
        log.badlist["MON_ADC"]["VCMO"]=(tmp[1])

        tmp = QC_check.CHKADC(mon_adcs, fembs[ifemb], nchips, "VREFP", 1988, 40, 1980, 40, env)
        log.chkflag["MON_ADC"]["VREFP"]=(tmp[0])
        log.badlist["MON_ADC"]["VREFP"]=(tmp[1])

        tmp = QC_check.CHKADC(mon_adcs, fembs[ifemb], nchips, "VREFN", 550, 40, 482, 40, env)
        log.chkflag["MON_ADC"]["VREFN"]=(tmp[0])
        log.badlist["MON_ADC"]["VREFN"]=(tmp[1])

        tmp = QC_check.CHKADC(mon_adcs, fembs[ifemb], nchips, "VSSA", 105, 40, 35, 20, env)
        log.chkflag["MON_ADC"]["VSSA"]=(tmp[0])
        log.badlist["MON_ADC"]["VSSA"]=(tmp[1])







