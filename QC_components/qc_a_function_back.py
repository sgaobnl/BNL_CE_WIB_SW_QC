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
def monitor_power_rail_analysis(interface, datadir, fembNo, label = 'test'):
    log.tmp_log.clear()
    log.check_log.clear()
    log.chkflag.clear()
    log.badlist.clear()

    # parameter
    gnd_ref = 150;    gnd_err = 150
    adc_p_ref = 2245;    adc_p_err = 100
    CDVDDA_ref = 1187;    CDVDDA_err = 100
    CDVDDIO_ref = 2236;    CDVDDIO_err = 100
    ACCVDD1P2_ref = 1097;    ACCVDD1P2_err = 100
    FE_ref = 1797;    FE_err = 200

    fsub = "MON_PWR_" + interface + "_200mVBL_14_0mVfC_2_0us_0x00.bin"
    fpwr = datadir + fsub
    with open(fpwr, 'rb') as fn:
        monvols = pickle.load(fn)
        vfembs = monvols[1]
        vold = monvols[0]
    vkeys = list(vold.keys())
    # LSB = 2.5 / 16384
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

        #   print value into table and also highlight the issue value while check them out
        mvvold = {}
        check = True
        check_list = []
        for key in vkeys:
            if "GND" in key:
                voltage_temp = abs(int(mvold[key][0] * LSB * 1000))
                if abs(voltage_temp - gnd_ref) < gnd_err:
                    mvvold[key] = "{}".format(voltage_temp)
                else:
                    mvvold[key] = "<span style = 'color:red;'> {} </span>".format(abs(int(mvold[key][0] * LSB * 1000)))
                    check = False
                    check_list.append("Monitor Path {} = {}, issue".format(key, voltage_temp))
            elif "HALF" in key:
                voltage_temp = abs(int((mvold[key][0] - mvold["GND"][0]) * LSB * 2 * 1000))
                if abs(voltage_temp - adc_p_ref) < adc_p_err:
                    mvvold[key.replace("_HALF", "")] = "{}".format(voltage_temp)
                else:
                    mvvold[key.replace("_HALF", "")] = "<span style = 'color:red;'> {} </span>".format(voltage_temp)
                    check = False
                    check_list.append("Monitor Path {} = {}, issue".format(key.replace("_HALF", ""), voltage_temp))
            elif "CDVDDA" in key:
                voltage_temp = abs(int((mvold[key][0] - mvold["GND"][0]) * LSB * 1000))
                if abs(voltage_temp - CDVDDA_ref) < CDVDDA_err:
                    mvvold[key] = "{}".format(voltage_temp)
                else:
                    mvvold[key] = "<span style = 'color:red;'> {} </span>".format(voltage_temp)
                    check = False
                    check_list.append("Monitor Path {} = {}, issue".format(key, voltage_temp))
            elif "CDVDDIO" in key:
                voltage_temp = abs(int((mvold[key][0] - mvold["GND"][0]) * LSB * 1000))
                if abs(voltage_temp - CDVDDIO_ref) < CDVDDIO_err:
                    mvvold[key] = "{}".format(voltage_temp)
                else:
                    mvvold[key] = "<span style = 'color:red;'> {} </span>".format(voltage_temp)
                    check = False
                    check_list.append("Monitor Path {} = {}, issue".format(key, voltage_temp))
            elif "VDDD1P2" in key:
                voltage_temp = abs(int((mvold[key][0] - mvold["GND"][0]) * LSB * 1000))
                if abs(voltage_temp - ACCVDD1P2_ref) < ACCVDD1P2_err:
                    mvvold[key] = "{}".format(voltage_temp)
                else:
                    mvvold[key] = "<span style = 'color:red;'> {} </span>".format(voltage_temp)
                    check = False
                    check_list.append("Monitor Path {} = {}, issue".format(key, voltage_temp))
            else:
                voltage_temp = abs(int((mvold[key][0] - mvold["GND"][0]) * LSB * 1000))
                if abs(voltage_temp - FE_ref) < FE_err:
                    mvvold[key] = "{}".format(voltage_temp)
                else:
                    mvvold[key] = "<span style = 'color:red;'> {} </span>".format(voltage_temp)
                    check = False
                    check_list.append("Monitor Path {} = {}, issue".format(key, voltage_temp))
        log.tmp_log[femb_id] = mvvold
        log.check_log[femb_id]["Result"] = check
        log.check_log[femb_id]["Issue List"] = check_list
        log.check_log[femb_id]["Label"] = label


# item 1_1
# def power_ana(fembs, fembNo, pwr_meas, env):
#     log.tmp_log.clear()
#     log.chkflag.clear()
#     log.badlist.clear()
#
#     for ifemb in range(len(fembs)):
#         femb_id = "FEMB ID {}".format(fembNo['femb%d' % fembs[ifemb]])
#         tmp = QC_check.CHKPWR(pwr_meas, fembs[ifemb], env)
#         log.chkflag[femb_id]["PWR"] = tmp[0]
#         log.badlist[femb_id]["PWR"] = tmp[1]
#
#         bias_v = round(pwr_meas['FEMB%d_BIAS_V'%fembs[ifemb]],3)
#         LArASIC_v = round(pwr_meas['FEMB{}_DC2DC{}_V'.format(fembs[ifemb],0)],3)
#         COLDATA_v = round(pwr_meas['FEMB{}_DC2DC{}_V'.format(fembs[ifemb],1)],3)
#         ColdADC_v = round(pwr_meas['FEMB{}_DC2DC{}_V'.format(fembs[ifemb],2)],3)
#
#         bias_i = round(pwr_meas['FEMB%d_BIAS_I'%fembs[ifemb]],3)
#         LArASIC_i = round(pwr_meas['FEMB{}_DC2DC{}_I'.format(fembs[ifemb], 0)], 3)
#         COLDATA_i = round(pwr_meas['FEMB{}_DC2DC{}_I'.format(fembs[ifemb], 1)], 3)
#         ColdADC_i = round(pwr_meas['FEMB{}_DC2DC{}_I'.format(fembs[ifemb], 2)], 3)
#
#         bias_p = round(bias_v * bias_i, 3)
#         LArASIC_p = round(LArASIC_v * LArASIC_i, 3)
#         COLDATA_p = round(COLDATA_v * COLDATA_i, 3)
#         ColdADC_p = round(ColdADC_v * ColdADC_i, 3)
#
#         # the | is used in Markdown table
#         log.tmp_log[femb_id]["name"] = "BIAS | LArASIC | ColdDATA | ColdADC"
#         log.tmp_log[femb_id]["V_set/V"] = " 5 | 3 | 3 | 3.5 "
#         log.tmp_log[femb_id]["V_meas/V"] = "{} | {} | {} | {}".format(bias_v, LArASIC_v, COLDATA_v, ColdADC_v)
#         log.tmp_log[femb_id]["I_meas/V"] = "{} | {} | {} | {}".format(abs(bias_i), LArASIC_i, COLDATA_i, ColdADC_i)
#         log.tmp_log[femb_id]["P_meas/V"] = "{} | {} | {} | {}".format(bias_p, LArASIC_p, COLDATA_p, ColdADC_p)
#
#         # log.report_log05[femb_id]["Power check status"] = tmp[0]
#         log.tmp_log[femb_id]["Power"] = "{} | - |Total P | {}".format(tmp[1], round(LArASIC_p + COLDATA_p + ColdADC_p, 3))
#     return log.tmp_log











def power_ana(fembs, ifemb, femb_id, pwr_meas, env, label = 'test'):
    log.tmp_log.clear()
    log.check_log.clear()

    check = True
    check_issue = []
    # parameter
    bias_v_ref = 5; bias_v_err = 0.6;    bias_i_ref = 0; bias_i_err = 0.1
    LArASIC_v_ref = 3; LArASIC_v_err = 0.2;    LArASIC_i_ref1 = 0.43; LArASIC_i_ref2 = 0.693; LArASIC_i_err = 0.1
    COLDATA_v_ref = 3; COLDATA_v_err = 0.2;    COLDATA_i_ref1 = 0.174; COLDATA_i_ref2 = 0.229; COLDATA_i_err = 0.1
    ColdADC_v_ref = 3.5; ColdADC_v_err = 0.2;  ColdADC_i_ref1 = 1.648;  ColdADC_i_ref2 = 1.709; ColdADC_i_err = 0.1
    # bias_v i p
    temp_v = round(pwr_meas['FEMB%d_BIAS_V'%fembs[ifemb]],3)
    if abs(temp_v - bias_v_ref) < bias_v_err:
        bias_v = "{}".format(temp_v)
    else:
        check = False
        check_issue.append("BIAS_V = {} out of [{} +- {}]\n".format(temp_v, bias_v_ref, bias_v_err))
        bias_v = "<span style = 'color:red;'> {} </span>".format(temp_v)
    temp_i = round(pwr_meas['FEMB%d_BIAS_I' % fembs[ifemb]], 3)
    if abs(temp_i - bias_i_ref) < bias_i_err:
        bias_i = "{}".format(abs(temp_i))
    else:
        check = False
        check_issue.append("bias_i = {} out of [{} +- {}]\n".format(temp_i, bias_i_ref, bias_i_err))
        bias_i = "<span style = 'color:red;'> {} </span>".format(temp_i)
    bias_p = abs(round(temp_v * temp_i, 3))

    # LArASIC_v i p
    temp_v = round(pwr_meas['FEMB{}_DC2DC{}_V'.format(fembs[ifemb],0)],3)
    if abs(temp_v - LArASIC_v_ref) < LArASIC_v_err:
        LArASIC_v = "{}".format(temp_v)
    else:
        check = False
        check_issue.append("LArASIC_v = {} out of [{} +- {}]\n".format(temp_v, LArASIC_v_ref, LArASIC_v_err))
        LArASIC_v = "<span style = 'color:red;'> {} </span>".format(temp_v)
    temp_i = round(pwr_meas['FEMB{}_DC2DC{}_I'.format(fembs[ifemb], 0)], 3)
    if abs(temp_i - LArASIC_i_ref1) < LArASIC_i_err:
        LArASIC_i = "{}".format(temp_i)
    elif(abs(temp_i - LArASIC_i_ref2) < LArASIC_i_err):
        LArASIC_i = "{}".format(temp_i)
    else:
        check = False
        check_issue.append("LArASIC_i = {} out of [{}/{} +- {}]\n".format(temp_i, LArASIC_i_ref1, LArASIC_i_ref2, LArASIC_i_err))
        LArASIC_i = "<span style = 'color:red;'> {} </span>".format(temp_i)
    LArASIC_p = round(temp_v * temp_i, 3)

    # COLDATA_v i p
    temp_v = round(pwr_meas['FEMB{}_DC2DC{}_V'.format(fembs[ifemb],1)],3)
    if abs(temp_v - COLDATA_v_ref) < COLDATA_v_err:
        COLDATA_v = "{}".format(temp_v)
    else:
        check = False
        check_issue.append("COLDATA_v = {} out of [{} +- {}]\n".format(temp_v, COLDATA_v_ref, COLDATA_v_err))
        COLDATA_v = "<span style = 'color:red;'> {} </span>".format(temp_v)
    temp_i = round(pwr_meas['FEMB{}_DC2DC{}_I'.format(fembs[ifemb], 1)], 3)
    if abs(temp_i - COLDATA_i_ref1) < COLDATA_i_err:
        COLDATA_i = "{}".format(temp_i)
    elif(abs(temp_i - COLDATA_i_ref2) < COLDATA_i_err):
        COLDATA_i = "{}".format(temp_i)
    else:
        check = False
        check_issue.append("COLDATA_i = {} out of [{}/{} +- {}]\n".format(temp_i, COLDATA_i_ref1, COLDATA_i_ref2, COLDATA_i_err))
        COLDATA_i = "<span style = 'color:red;'> {} </span>".format(temp_i)
    COLDATA_p = round(temp_v * temp_i, 3)

    # ColdADC_v i p
    temp_v = round(pwr_meas['FEMB{}_DC2DC{}_V'.format(fembs[ifemb],2)],3)
    if abs(temp_v - ColdADC_v_ref) < ColdADC_v_err:
        ColdADC_v = "{}".format(temp_v)
    else:
        check = False
        check_issue.append("ColdADC_v = {} out of [{} +- {}]\n".format(temp_v, ColdADC_v_ref, ColdADC_v_err))
        ColdADC_v = "<span style = 'color:red;'> {} </span>".format(temp_v)
    temp_i = round(pwr_meas['FEMB{}_DC2DC{}_I'.format(fembs[ifemb], 2)], 3)
    if abs(temp_i - ColdADC_i_ref1) < ColdADC_i_err:
        ColdADC_i = "{}".format(temp_i)
    elif(abs(temp_i - ColdADC_i_ref2) < ColdADC_i_err):
        ColdADC_i = "{}".format(temp_i)
    else:
        check = False
        check_issue.append("ColdADC_i = {} out of [{}/{} +- {}]\n".format(temp_i, ColdADC_i_ref1, ColdADC_i_ref2, ColdADC_i_err))
        ColdADC_i = "<span style = 'color:red;'> {} </span>".format(temp_i)
    ColdADC_p = round(temp_v * temp_i, 3)

    total_p = bias_p + LArASIC_p + COLDATA_p + ColdADC_p

    # the | is used in Markdown table
    log.tmp_log[femb_id]["Measure Items"] = "BIAS | LArASIC | ColdADC | COLDATA "
    log.tmp_log[femb_id]["V_set / V"] = " 5 | 3 | 3.5 | 3 "
    log.tmp_log[femb_id]["V_meas / V"] = "{} | {} | {} | {}".format(bias_v, LArASIC_v, ColdADC_v, COLDATA_v)
    log.tmp_log[femb_id]["I_meas / A"] = "{} | {} | {} | {}".format(bias_i, LArASIC_i, ColdADC_i, COLDATA_i)
    log.tmp_log[femb_id]["P_meas / V"] = "{} | {} | {} | {}".format(bias_p, LArASIC_p, ColdADC_p, COLDATA_p)
    log.tmp_log[femb_id]["Total Power"] = " {} |  | | ".format(round(total_p, 2))

    log.check_log[femb_id]["Result"] = check
    log.check_log[femb_id]["Issue List"] = check_issue
    log.check_log[femb_id]["Label"] = label



def pulse_ana(pls_rawdata, fembs, fembNo, ReportDir, fname, doc = "PWR_Meas/", label = 'test'):
    log.tmp_log.clear()
    log.check_log.clear()
    log.chkflag.clear()
    log.badlist.clear()

    for ifemb in range(len(fembs)):
        femb_id = "FEMB ID {}".format(fembNo['femb%d' % fembs[ifemb]])
        check = True
        check_issue = []

        report_addr = ReportDir[fembs[ifemb]] + doc
        print(report_addr)
        ppk, npk, bl = qc_tools.GetPeaks(pls_rawdata, fembs[ifemb], report_addr, fname, funcfit=False)

        ppk_mean = int(np.mean(ppk))
        ppk_err = int(abs(np.max(ppk) - np.min(ppk)))

        npk_mean = int(np.mean(npk))
        npk_err = int(abs(np.max(npk) - np.min(npk)))
        # bbl_mean = np.mean(bl)

        log.tmp_log[femb_id]["{}_ppk_mean0".format(fname)] = int(ppk_mean)
        log.tmp_log[femb_id]["{}_ppk_err0".format(fname)] = int(ppk_err)
        log.tmp_log[femb_id]["{}_npk_mean0".format(fname)] = abs(int(npk_mean))
        log.tmp_log[femb_id]["{}_npk_err0".format(fname)] = int(npk_err)

        tmp = QC_check.CHKPulse(ppk, 800)
        print(tmp[0])
        if tmp[0] == False:
            log.tmp_log[femb_id]["{}_ppk_mean".format(fname)] = '<span style="color: red;">' + str(ppk_mean) + '</span>'
            log.tmp_log[femb_id]["{}_ppk_err".format(fname)] = '<span style="color: red;">' + str(ppk_err) + '</span>'
        else:
            log.tmp_log[femb_id]["{}_ppk_mean".format(fname)] = str(ppk_mean)
            log.tmp_log[femb_id]["{}_ppk_err".format(fname)] = str(ppk_err)
        check = check and tmp[0]
        check_issue.append("Pulse_PPK_issue: {}\n".format(tmp[1]))
        # log.badlist[femb_id]["Pulse_SE_PPK"]=tmp[1]

        tmp = QC_check.CHKPulse(npk, 800)
        print(tmp[0])
        if tmp[0] == False:
            log.tmp_log[femb_id]["{}_npk_mean".format(fname)] = '<span style="color: red;">' + str(npk_mean) + '</span>'
            log.tmp_log[femb_id]["{}_npk_err".format(fname)] = '<span style="color: red;">' + str(npk_err) + '</span>'
        else:
            log.tmp_log[femb_id]["{}_npk_mean".format(fname)] = str(npk_mean)
            log.tmp_log[femb_id]["{}_npk_err".format(fname)] = str(npk_err)
        check = check and tmp[0]
        check_issue.append("Pulse_NPK_issue: {}\n".format(tmp[1]))
        # log.badlist[femb_id]["Pulse_SE_NPK"]=(tmp[1])

        tmp = QC_check.CHKPulse(bl, 800)
        print(tmp[0])
        check = check and tmp[0]
        check_issue.append("Pulse_BBL_issue: {}\n".format(tmp[1]))
        log.check_log[femb_id]["Result"] = check
        log.check_log[femb_id]["Issue List"] = check_issue
        log.check_log[femb_id]["Label"] = label


