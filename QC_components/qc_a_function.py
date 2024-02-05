import os
import sys
from QC_tools import ana_tools
import pickle
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
from collections import defaultdict
# import components.assembly_log as log
import QC_components.qc_log as log
import QC_check

qc_tools = ana_tools()
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


def power_ana(fembs, fembNo, pwr_meas, env):
    log.tmp_log.clear()
    log.chkflag.clear()
    log.badlist.clear()

    for ifemb in range(len(fembs)):
        femb_id = "FEMB ID {}".format(fembNo['femb%d' % fembs[ifemb]])
        tmp = QC_check.CHKPWR(pwr_meas, fembs[ifemb], env)
        log.chkflag[femb_id]["PWR"] = tmp[0]
        log.badlist[femb_id]["PWR"] = tmp[1]

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

        # the | is used in Markdown table
        log.tmp_log[femb_id]["name"] = "BIAS | LArASIC | ColdDATA | ColdADC"
        log.tmp_log[femb_id]["V_set/V"] = " 5 | 3 | 3 | 3.5 "
        log.tmp_log[femb_id]["V_meas/V"] = "{} | {} | {} | {}".format(bias_v, LArASIC_v, COLDATA_v, ColdADC_v)
        log.tmp_log[femb_id]["I_meas/V"] = "{} | {} | {} | {}".format(abs(bias_i), LArASIC_i, COLDATA_i, ColdADC_i)
        log.tmp_log[femb_id]["P_meas/V"] = "{} | {} | {} | {}".format(bias_p, LArASIC_p, COLDATA_p, ColdADC_p)

        # log.report_log05[femb_id]["Power check status"] = tmp[0]
        log.tmp_log[femb_id]["Power"] = "{} | - |Total P | {}".format(tmp[1], round(LArASIC_p + COLDATA_p + ColdADC_p, 3))
    return log.tmp_log







def pulse_ana(pls_rawdata, fembs, fembNo, ReportDir, fname, doc = "PWR_Meas/"):
    log.tmp_log.clear()
    log.chkflag.clear()
    log.badlist.clear()
    for ifemb in range(len(fembs)):
        femb_id = "FEMB ID {}".format(fembNo['femb%d' % fembs[ifemb]])
        report_addr = ReportDir[fembs[ifemb]] + doc
        print(report_addr)
        ppk, npk, bl = qc_tools.GetPeaks(pls_rawdata, fembs[ifemb], report_addr, fname, funcfit=False)

        tmp = QC_check.CHKPulse(ppk)
        ppk_mean = np.mean(ppk)
        npk_mean = np.mean(npk)
        bbl_mean = np.mean(bl)

        log.tmp_log[femb_id]["npk_mean"] = np.round(npk_mean, 2)
        log.tmp_log[femb_id]["bbl_mean"] = np.round(bbl_mean, 2)
        log.tmp_log[femb_id]["ppk_mean"] = np.round(ppk_mean, 2)

        log.chkflag[femb_id]["Pulse_SE_PPK"]=tmp[0]
        log.badlist[femb_id]["Pulse_SE_PPK"]=tmp[1]

        tmp = QC_check.CHKPulse(npk)
        log.chkflag[femb_id]["Pulse_SE_NPK"]=(tmp[0])
        log.badlist[femb_id]["Pulse_SE_NPK"]=(tmp[1])

        tmp = QC_check.CHKPulse(bl)
        log.chkflag[femb_id]["Pulse_SE_BL"]=(tmp[0])
        log.badlist[femb_id]["Pulse_SE_BL"]=(tmp[1])
        if (log.chkflag[femb_id]["Pulse_SE_PPK"] == False) and log.chkflag[femb_id]["Pulse_SE_NPK"] == False and (log.chkflag[femb_id]["Pulse_SE_BL"] == False):
            log.tmp_log[femb_id]["Result"] = True
        else:
            log.tmp_log[femb_id]["Pulse_SE PPK err_status"] = log.badlist["Pulse_SE_PPK"]
            log.tmp_log[femb_id]["Pulse_SE NPK err_status"] = log.badlist["Pulse_SE_NPK"]
            log.tmp_log[femb_id]["Pulse_SE BL err_status"] = log.badlist["Pulse_SE_BL"]
            log.tmp_log[femb_id]["Result"] = False

    return log.tmp_log
