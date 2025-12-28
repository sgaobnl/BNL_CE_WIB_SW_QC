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
def monitor_power_rail_analysis(interface,  fembs, monvols, fembNo, label = 'test', NewWIB = True):
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

    vfembs = monvols[1]
    vold = monvols[0]
    vkeys = list(vold.keys())
    if NewWIB:
        LSB = 1 / (2 ** 14) * 2.500  # NEW WIB IS 2500
    else:
        LSB = 1 / (2 ** 14) * 2.048  # NEW WIB IS 2500

    for ifemb in range(len(fembs)):
        femb_id = "FEMB ID {}".format(fembNo['femb%d' % fembs[ifemb]])
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

def power_ana(fembs, ifemb, femb_id, pwr_meas, env, label = 'test'):
    log.tmp_log.clear()
    log.check_log.clear()

    check = True
    check_issue = []
    # parameter
    #           BIAS    LArASIC ColdADC COLDATA
    ref_v       = [5,     3,      3.5,    3]
    err_v       = [1,     0.2,    0.2,    0.2]
    ref_i_RT    = [0,  0.43,   1.648,  0.174]
    ref_i_LN    = [0,  0.693,  1.709,  0.229]
    err_i       = [0.2,     0.2,    0.2,    0.2]
    #   the above will use to improve the structure
    bias_v_ref = 5; bias_v_err = 0.6;    bias_i_ref = 0; bias_i_err = 0.1
    LArASIC_v_ref = 3; LArASIC_v_err = 0.2;    LArASIC_i_ref1 = 0.43; LArASIC_i_ref2 = 0.693; LArASIC_i_err = 0.2
    COLDATA_v_ref = 3; COLDATA_v_err = 0.2;    COLDATA_i_ref1 = 0.174; COLDATA_i_ref2 = 0.229; COLDATA_i_err = 0.1
    ColdADC_v_ref = 3.5; ColdADC_v_err = 0.2;  ColdADC_i_ref1 = 1.648;  ColdADC_i_ref2 = 1.709; ColdADC_i_err = 0.2
    # bias_v i p
    temp_v = round(pwr_meas['FEMB%d_BIAS_V'%fembs[ifemb]],3)
    log.check_log[femb_id]["BIAS_V"] = temp_v
    if abs(temp_v - bias_v_ref) < bias_v_err:
        bias_v = "{}".format(temp_v)
    else:
        check = False
        check_issue.append("BIAS_V = {} out of [{} +- {}]\n".format(temp_v, bias_v_ref, bias_v_err))
        bias_v = "<span style = 'color:red;'> {} </span>".format(temp_v)
    temp_i = round(pwr_meas['FEMB%d_BIAS_I' % fembs[ifemb]], 3)
    log.check_log[femb_id]["BIAS_I"] = temp_i
    if abs(temp_i - bias_i_ref) < bias_i_err:
        bias_i = "{}".format(abs(temp_i))
    else:
        check = False
        check_issue.append("bias_i = {} out of [{} +- {}]\n".format(temp_i, bias_i_ref, bias_i_err))
        bias_i = "<span style = 'color:red;'> {} </span>".format(temp_i)
    bias_p = abs(round(temp_v * temp_i, 3))
    log.check_log[femb_id]["bias_p"] = bias_p

    # LArASIC_v i p
    temp_v = round(pwr_meas['FEMB{}_DC2DC{}_V'.format(fembs[ifemb],0)],3)
    log.check_log[femb_id]["LArASIC_V"] = temp_v
    if abs(temp_v - LArASIC_v_ref) < LArASIC_v_err:
        LArASIC_v = "{}".format(temp_v)
    else:
        check = False
        check_issue.append("LArASIC_v = {} out of [{} +- {}]\n".format(temp_v, LArASIC_v_ref, LArASIC_v_err))
        LArASIC_v = "<span style = 'color:red;'> {} </span>".format(temp_v)
    temp_i = round(pwr_meas['FEMB{}_DC2DC{}_I'.format(fembs[ifemb], 0)], 3)
    log.check_log[femb_id]["LArASIC_I"] = temp_i
    if abs(temp_i - LArASIC_i_ref1) < LArASIC_i_err:
        LArASIC_i = "{}".format(temp_i)
    elif(abs(temp_i - LArASIC_i_ref2) < LArASIC_i_err):
        LArASIC_i = "{}".format(temp_i)
    else:
        check = False
        check_issue.append("LArASIC_i = {} out of [{}/{} +- {}]\n".format(temp_i, LArASIC_i_ref1, LArASIC_i_ref2, LArASIC_i_err))
        LArASIC_i = "<span style = 'color:red;'> {} </span>".format(temp_i)
    LArASIC_p = round(temp_v * temp_i, 3)
    log.check_log[femb_id]["LArASIC_p"] = LArASIC_p

    # COLDATA_v i p
    temp_v = round(pwr_meas['FEMB{}_DC2DC{}_V'.format(fembs[ifemb],1)],3)
    log.check_log[femb_id]["COLDATA_V"] = temp_v
    if abs(temp_v - COLDATA_v_ref) < COLDATA_v_err:
        COLDATA_v = "{}".format(temp_v)
    else:
        check = False
        check_issue.append("COLDATA_v = {} out of [{} +- {}]\n".format(temp_v, COLDATA_v_ref, COLDATA_v_err))
        COLDATA_v = "<span style = 'color:red;'> {} </span>".format(temp_v)
    temp_i = round(pwr_meas['FEMB{}_DC2DC{}_I'.format(fembs[ifemb], 1)], 3)
    log.check_log[femb_id]["COLDATA_I"] = temp_i
    if abs(temp_i - COLDATA_i_ref1) < COLDATA_i_err:
        COLDATA_i = "{}".format(temp_i)
    elif(abs(temp_i - COLDATA_i_ref2) < COLDATA_i_err):
        COLDATA_i = "{}".format(temp_i)
    else:
        check = False
        check_issue.append("COLDATA_i = {} out of [{}/{} +- {}]\n".format(temp_i, COLDATA_i_ref1, COLDATA_i_ref2, COLDATA_i_err))
        COLDATA_i = "<span style = 'color:red;'> {} </span>".format(temp_i)
    COLDATA_p = round(temp_v * temp_i, 3)
    log.check_log[femb_id]["COLDATA_p"] = COLDATA_p
    # ColdADC_v i p
    temp_v = round(pwr_meas['FEMB{}_DC2DC{}_V'.format(fembs[ifemb],2)],3)
    log.check_log[femb_id]["ColdADC_V"] = temp_v
    if abs(temp_v - ColdADC_v_ref) < ColdADC_v_err:
        ColdADC_v = "{}".format(temp_v)
    else:
        check = False
        check_issue.append("ColdADC_v = {} out of [{} +- {}]\n".format(temp_v, ColdADC_v_ref, ColdADC_v_err))
        ColdADC_v = "<span style = 'color:red;'> {} </span>".format(temp_v)
    temp_i = round(pwr_meas['FEMB{}_DC2DC{}_I'.format(fembs[ifemb], 2)], 3)
    log.check_log[femb_id]["ColdADC_I"] = temp_i
    if abs(temp_i - ColdADC_i_ref1) < ColdADC_i_err:
        ColdADC_i = "{}".format(temp_i)
    elif(abs(temp_i - ColdADC_i_ref2) < ColdADC_i_err):
        ColdADC_i = "{}".format(temp_i)
    else:
        check = False
        check_issue.append("ColdADC_i = {} out of [{}/{} +- {}]\n".format(temp_i, ColdADC_i_ref1, ColdADC_i_ref2, ColdADC_i_err))
        ColdADC_i = "<span style = 'color:red;'> {} </span>".format(temp_i)
    ColdADC_p = round(temp_v * temp_i, 3)
    log.check_log[femb_id]["ColdADC_p"] = ColdADC_p

    total_p = bias_p + LArASIC_p + COLDATA_p + ColdADC_p
    log.check_log[femb_id]["TPower"] = np.round(total_p,2)

    # the | is used in Markdown table
    log.tmp_log[femb_id]["Measure Items"] = "BIAS | LArASIC | ColdADC | COLDATA "
    log.tmp_log[femb_id]["V_set / V"] = " 5 | 3 | 3.5 | 3 "
    log.tmp_log[femb_id]["V_meas / V"] = "{} | {} | {} | {}".format(bias_v, LArASIC_v, ColdADC_v, COLDATA_v)
    log.tmp_log[femb_id]["I_meas / A"] = "{} | {} | {} | {}".format(bias_i, LArASIC_i, ColdADC_i, COLDATA_i)
    log.tmp_log[femb_id]["P_meas / W"] = "{} | {} | {} | {}".format(bias_p, LArASIC_p, ColdADC_p, COLDATA_p)
    log.tmp_log[femb_id]["Total Power / W"] = " {} |  | | ".format(round(total_p, 2))

    log.check_log[femb_id]["Result"] = check
    log.check_log[femb_id]["Issue List"] = check_issue
    log.check_log[femb_id]["Label"] = label
    log.check_log[femb_id]["Power"] = " {}".format(round(total_p, 2))



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
        ppk, npk, bl = qc_tools.GetPeaks(pls_rawdata, fembs[ifemb], report_addr, fname, funcfit=False)
        ppk_csv = [int(a-b) for a, b in zip(ppk,bl)]
        ppk_max = int(np.max(ppk))
        ppk_min = int(np.min(ppk))
        ppk_mean = int(np.mean(ppk))
        ppk_err = int(np.std(ppk))

        zero = [int(a - b) for a, b in zip(bl, bl)]
        bbl_csv = [int(a - b) for a, b in zip(bl, zero)]
        bbl = bl
        bbl_mean = int(np.mean(bl))
        bbl_err = int(np.std(bl))
        bbl_max = int(np.min(bl))
        bbl_min = int(np.min(bl))
        npk_csv = [int(a - b) for a, b in zip(bl, npk)]
        npk_mean = int(np.mean(npk))
        npk_err = int(np.std(npk))
        npk_max = int(np.min(npk))
        npk_min = int(np.min(npk))

        if '5nA' in label:
            pulse_range = 5000
        else:
            pulse_range = 3000


        rpk = [a-b for a, b in zip(ppk, bl)]
        tmp = QC_check.CHKPulse(rpk, pulse_range, type = 'pedestal')
        if tmp[0] == False:
            log.tmp_log[femb_id]["ppk_mean"] = '<span style="color: red;">' + str(ppk_mean) + '</span>'
            log.tmp_log[femb_id]["ppk_std"] = '<span style="color: red;">' + str(ppk_err) + '</span>'
        else:
            log.tmp_log[femb_id]["ppk_mean"] = str(ppk_mean)
            log.tmp_log[femb_id]["ppk_std"] = str(ppk_err)
        check = check and tmp[0]
        check_issue.append("Pulse_PPK_issue: {}\n".format(tmp[1]))
        tmp = QC_check.CHKPulse(bl, pulse_range, type = 'pedestal')
        if tmp[0] == False:
            log.tmp_log[femb_id]["bbl_mean"] = '<span style="color: red;">' + str(bbl_mean) + '</span>'
            log.tmp_log[femb_id]["bbl_std"] = '<span style="color: red;">' + str(bbl_err) + '</span>'
            log.tmp_log[femb_id]["issue_ch"] = '<span style="color: red;">' + str(tmp[1]) + '</span>'
        else:
            log.tmp_log[femb_id]["bbl_mean"] = str(bbl_mean)
            log.tmp_log[femb_id]["bbl_std"] = str(bbl_err)
        check = check and tmp[0]
        check_issue.append("Pulse_NPK_issue: {}\n".format(tmp[1]))
        tmp = QC_check.CHKPulse(npk, pulse_range, type = 'pedestal')
        if tmp[0] == False:
            log.tmp_log[femb_id]["npk_mean"] = '<span style="color: red;">' + str(npk_mean) + '</span>'
            log.tmp_log[femb_id]["npk_std"] = '<span style="color: red;">' + str(npk_err) + '</span>'
            log.tmp_log[femb_id]["issue_ch"] = '<span style="color: red;">' + str(tmp[1]) + '</span>'
        else:
            log.tmp_log[femb_id]["npk_mean"] = str(npk_mean)
            log.tmp_log[femb_id]["npk_std"] = str(npk_err)
        check = check and tmp[0]
        check_issue.append("Pulse_NPK_issue: {}\n".format(tmp[1]))

        check_issue.append("Pulse_BBL_issue: {}\n".format(tmp[1]))
        log.check_log[femb_id]["Result"] = check
        log.check_log[femb_id]["Issue List"] = check_issue
        log.check_log[femb_id]["Label"] = label
        log.check_log[femb_id]["ppk_mean"] = ppk_mean
        log.check_log[femb_id]["ppk_std"] = ppk_err
        log.check_log[femb_id]["ppk_max"] = ppk_max
        log.check_log[femb_id]["ppk_min"] = ppk_min
        log.check_log[femb_id]["ppk"] = ppk
        log.check_log[femb_id]["bbl_mean"] = bbl_mean
        log.check_log[femb_id]["bbl_std"] = bbl_err
        log.check_log[femb_id]["bbl_max"] = bbl_max
        log.check_log[femb_id]["bbl_min"] = bbl_min
        log.check_log[femb_id]["bbl"] = bbl
        log.check_log[femb_id]["npk_mean"] = npk_mean
        log.check_log[femb_id]["npk_std"] = npk_err
        log.check_log[femb_id]["npk"] = npk
        log.check_log[femb_id]["npk_max"] = npk_max
        log.check_log[femb_id]["npk_min"] = npk_min


