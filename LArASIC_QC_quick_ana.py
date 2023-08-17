import time
import os
import sys
import numpy as np
import pickle
import copy
import time, datetime
from spymemory_decode import wib_dec
#from spymemory_decode import avg_aligned_by_ts
import colorama
from colorama import Fore, Back
colorama.init(autoreset=True)

# Automatically adds a Style.RESET_ALL after each print statement
#print(Fore.RED + 'Red foreground text')
#print(Back.RED + 'Red background text')

fsubdir = "FE_012000001_012000002_012000203_012000004_012000005_012000006_012000007_012000008"
froot = "D:/Github/BNL_CE_WIB_SW_QC_main/tmp_data/"
fdir = froot + fsubdir + "/"


evl = input ("Analyze all test items? (Y/N) : " )
if ("Y" in evl) or ("y" in evl):
    tms = [0, 1, 2,3,4,5,61, 62, 63,7,8]
    pass
else:
    print ("\033[93m  QC task list   \033[0m")
    print ("\033[96m 0: Initilization checkout  \033[0m")
    print ("\033[96m 1: FE power consumption measurement  \033[0m")
    print ("\033[96m 2: FE response measurement checkout  \033[0m")
    print ("\033[96m 3: FE monitoring measurement  \033[0m")
    print ("\033[96m 4: FE power cycling measurement  \033[0m")
    print ("\033[96m 5: FE noise measurement  \033[0m")
    print ("\033[96m 61: FE calibration measurement (ASIC-DAC)  \033[0m")
    print ("\033[96m 62: FE calibration measurement (DAT-DAC) \033[0m")
    print ("\033[96m 63: FE calibration measurement (Direct-Input) \033[0m")
    print ("\033[96m 7: FE delay run  \033[0m")
    print ("\033[96m 8: FE cali-cap measurement \033[0m")

    while True:
        testnostr = input ("Please input a number (0, 1, 2, 3, 4, 5, 61, 62, 63, 8) for one test item: " )
        try:
            testno = int(testnostr)
            tms = [testno]
            break
        except ValueError:
            print ("Wrong value, please re-enter...")

#import statsmodels.api as sm
#def linear_fit(x, y):
#    error_fit = False 
#    try:
#        results = sm.OLS(y,sm.add_constant(x)).fit()
#    except ValueError:
#        error_fit = True 
#    if ( error_fit == False ):
#        error_gain = False 
#        try:
#            slope = results.params[1]
#        except IndexError:
#            slope = 0
#            error_gain = True
#        try:
#            constant = results.params[0]
#        except IndexError:
#            constant = 0
#    else:
#        slope = 0
#        constant = 0
#        error_gain = True
#
#    y_fit = np.array(x)*slope + constant
#    delta_y = abs(y - y_fit)
#    inl = delta_y / (max(y)-min(y))
#    peakinl = max(inl)
#    return slope, constant, peakinl, error_gain


def plt_log(plt,logsd, onekey):
    fig.suptitle("Test Result of " + onekey, weight ="bold", fontsize = 12)
    lkeys = list(logsd)
    for i in range(len(lkeys)):
        loginfo = "{} : {}".format(lkeys[i], data["logs"][lkeys[i]])
        #if i%2:
        #    x = 0.5
        #else:
        #    x = 0.1
        #y = 0.90-(i//2)*0.02
        x = 0.05 + 0.15*i
        #y = 0.90-i*0.02
        y = 0.92
        fig.text(x, y, loginfo, fontsize=8)

def ana_fepwr(pwr_meas, vin=[1.7,1.9], cdda=[15,25], cddp=[20,35], cddo=[0,5]):
    kpwrs = list(pwr_meas.keys())

    vddas = []
    vddos = []
    vddps = []
    cddas = []
    cddos = []
    cddps = []

    for i in range(len(kpwrs)):
        if "VDDA" in kpwrs[i]:
            vddas.append(pwr_meas[kpwrs[i]][0])
            cddas.append(pwr_meas[kpwrs[i]][1])
        if "VDDO" in kpwrs[i]:
            vddos.append(pwr_meas[kpwrs[i]][0])
            cddos.append(pwr_meas[kpwrs[i]][1])
        if "VPPP" in kpwrs[i]:
            vddps.append(pwr_meas[kpwrs[i]][0])
            cddps.append(pwr_meas[kpwrs[i]][1])
    
    show_flg=True
    if all(item >= vin[0] for item in vddas) and all(item <= vin[1] for item in vddas) :
        if all(item >= vin[0] for item in vddos) and all(item <= vin[1] for item in vddos) :
            if all(item >= vin[0] for item in vddps) and all(item <= vin[1] for item in vddps) :
                if all(item >= cdda[0] for item in cddas) and all(item <= cdda[1] for item in cddas) :
                    if all(item >= cddp[0] for item in cddps) and all(item <= cddp[1] for item in cddps) :
                        if all(item >= cddo[0] for item in cddos) and all(item <= cddo[1] for item in cddos) :
                            show_flg = False
    return show_flg




def plt_fepwr(plt, pwr_meas):
    kpwrs = list(pwr_meas.keys())
    ax5 = plt.subplot2grid((2, 3), (0, 0), colspan=1, rowspan=1)
    ax6 = plt.subplot2grid((2, 3), (1, 0), colspan=1, rowspan=1)

    vddas = []
    vddos = []
    vddps = []
    cddas = []
    cddos = []
    cddps = []

    for i in range(len(kpwrs)):
        if "VDDA" in kpwrs[i]:
            vddas.append(pwr_meas[kpwrs[i]][0])
            cddas.append(pwr_meas[kpwrs[i]][1])
        if "VDDO" in kpwrs[i]:
            vddos.append(pwr_meas[kpwrs[i]][0])
            cddos.append(pwr_meas[kpwrs[i]][1])
        if "VPPP" in kpwrs[i]:
            vddps.append(pwr_meas[kpwrs[i]][0])
            cddps.append(pwr_meas[kpwrs[i]][1])

    fe=[0,1,2,3,4,5,6,7]
    ax5.plot(fe, vddas, color='b', marker = 'o', label='VDDA')
    ax5.plot(fe, vddps, color='r', marker = 'o', label='VDDP')
    ax5.plot(fe, vddos, color='g', marker = 'o', label='VDDO')
    ax5.set_title("Voltage Measurement", fontsize=8)
    ax5.set_ylabel("Voltage / V", fontsize=8)
    ax5.set_ylim((0,2))
    ax5.set_xlabel("FE no", fontsize=8)
    ax5.grid()
    ax5.legend()

    ax6.scatter(fe, cddas, color='b', marker = 'o', label='VDDA')
    ax6.scatter(fe, cddps, color='r', marker = 'o', label='VDDP')
    ax6.scatter(fe, cddos, color='g', marker = 'o', label='VDDO')
    ax6.set_title("Current Measurement", fontsize=8)
    ax6.set_ylabel("Current / mA", fontsize=8)
    ax6.set_ylim((-10,50))
    ax6.set_xlabel("FE no", fontsize=8)
    ax6.legend()
    ax6.grid()



def data_ana(fembs, rawdata, rms_flg=False):
    wibdata = wib_dec(rawdata,fembs, spy_num=1)[0]
    datd = [wibdata[0], wibdata[1],wibdata[2],wibdata[3]][fembs[0]]

    chns =[]
    rmss = []
    peds = []
    pkps = []
    pkns = []
    wfs = []

    ppos0=0
    npos0=0
    ppos64=0
    npos64=0
    for achn in range(len(datd)):
        chndata = datd[achn]
        amax = np.max(chndata[300:-150])
        amin = np.min(chndata[300:-150])
        if achn==0:
            ppos0 = np.where(chndata[300:]==amax)[0][0] + 300
            npos0 = np.where(chndata[300:]==amin)[0][0] + 300
        if achn==64:
            ppos64 = np.where(chndata[300:]==amax)[0][0] + 300
            npos64 = np.where(chndata[300:]==amin)[0][0] + 300

        if rms_flg:
            arms = np.std(chndata)
            aped = int(np.mean(chndata))
        else:
            if achn <64:
                arms = np.std(chndata[ppos0-150:ppos0-50])
                aped = int(np.mean(chndata[ppos0-150:ppos0-50]))
                wfs.append(chndata[ppos0-50:ppos0+150])
            else:
                arms = np.std(chndata[ppos64-150:ppos64-50])
                aped = int(np.mean(chndata[ppos64-150:ppos64-50]))
                wfs.append(chndata[ppos64-50:ppos64+150])
        chns.append(achn)
        rmss.append(arms)
        peds.append(aped)
        pkps.append(amax)
        pkns.append(amin)
    return chns, rmss, peds, pkps, pkns, wfs

def ana_res(fembs, rawdata, par=[7000,10000], rmsr=[5,25], pedr=[500,3000] ):
    chns, rmss, peds, pkps, pkns, wfs = data_ana(fembs, rawdata)
    show_flg=True
    amps = np.array(pkps) - np.array(peds)
    if all(item > par[0] for item in amps) and all(item < par[1] for item in amps) :
        if all(item > rmsr[0] for item in rmss) and all(item < rmsr[1] for item in rmss) :
            if all(item > pedr[0] for item in peds) and all(item < pedr[1] for item in peds) :
                show_flg = False
    return show_flg


def plt_subplot(plt, fembs, rawdata ):
    ax1 = plt.subplot2grid((2, 3), (0, 1), colspan=1, rowspan=1)
    ax2 = plt.subplot2grid((2, 3), (0, 2), colspan=1, rowspan=1)
    ax3 = plt.subplot2grid((2, 3), (1, 1), colspan=1, rowspan=1)
    ax4 = plt.subplot2grid((2, 3), (1, 2), colspan=1, rowspan=1)

    chns, rmss, peds, pkps, pkns, wfs = data_ana(fembs, rawdata)



#    wibdata = wib_dec(rawdata,fembs, spy_num=1)
#    datd = [wibdata[0], wibdata[1],wibdata[2],wibdata[3]][fembs[0]]
#
#    chns =[]
#    rmss = []
#    peds = []
#    pkps = []
#    pkns = []
#    wfs = []
#
#    ppos=0
#    npos=0
#    for achn in range(len(datd)):
#        chndata = datd[achn]
#        amax = np.max(chndata[300:])
#        amin = np.min(chndata[300:])
#        if achn==0:
#            ppos = np.where(chndata==amax)[0][0]
#            npos = np.where(chndata==amin)[0][0]
#        aped = int(np.mean(chndata[ppos-150:ppos-50]))
#
#        arms = np.std(chndata[ppos-150:ppos-50])
#        chns.append(achn)
#        rmss.append(arms)
#        peds.append(aped)
#        pkps.append(amax)
#        pkns.append(amin)
#        wfs.append(chndata[ppos-50:ppos+150])
#        ax1.plot(chndata[ppos-20:ppos+20])
#        ax2.plot(chndata[npos-20:npos+20])

    for chn in chns:
        ax1.plot(wfs[chn][30:70], marker='.')
        ax2.plot(wfs[chn], marker='.')
    ax1.set_title("Overlap waveforms", fontsize=8)
    ax1.set_ylabel("Amplitude", fontsize=8)
    ax1.set_xlabel("Time", fontsize=8)
    ax2.set_title("Overlap waveforms", fontsize=8)
    ax2.set_ylabel("Amplitude", fontsize=8)
    ax2.set_xlabel("Time", fontsize=8)

    for i in range(0,128,16):
        ax3.vlines(i-0.5, 0, 17000, color='y')
        ax4.vlines(i-0.5, 0, 50, color='y')

    ax3.plot(chns, pkps, color='r', marker='.')
    ax3.plot(chns, peds, color='b', marker='.')
    ax3.plot(chns, pkns, color='m', marker='.')
    ax3.set_title("Pulse Response Distribution", fontsize=8)
    ax3.set_xlabel("Amplitude", fontsize=8)
    ax3.set_ylabel("CH number", fontsize=8)

    ax4.plot(chns,rmss, color='r', marker='.')
    ax4.set_title("Noise", fontsize=8)
    ax4.set_xlabel("ADC / bit", fontsize=8)
    ax4.set_ylabel("CH number", fontsize=8)
    ax1.grid()
    ax2.grid()


def dacana(data,dacdkey ):
    dacs, dacv = zip(*data[dacdkey])
    fedacs = [[], [], [], [], [], [], [], []]
    fes = []
    for fe in range(8):
        for dac in range(len(dacs)):
            fedacs[fe].append([dacs[dac],dacv[dac][fe]])
    
        x, y = zip(*fedacs[fe])
        y = np.array(y)*AD_LSB
        if ("SGP1" in dacdkey) or ("SG0_1_SG1_1" in dacdkey):
            slope, constant, peakinl, error_gain = linear_fit(x[:-3], y[:-3])
        else:
            slope, constant, peakinl, error_gain = linear_fit(x, y)
        fes.append([dacdkey, fe,x,y,slope, constant, peakinl])
    return fes

if 0 in tms:
#if True:
    print ("-------------------------------------------------------------------------")
    print ("0: Initilization checkout")
    fp = fdir + "QC_INIT_CHK" + ".bin"

    with open(fp, 'rb') as fn:
        data = pickle.load( fn)
    
    dkeys = list(data.keys())
    
    logsd = data["logs"]
    dkeys.remove("logs")
    
    for onekey in dkeys:
        if ("DIRECT_PLS_CHK" in onekey) or ("ASICDAC_CALI_CHK" in onekey):
            cfgdata = data[onekey]
            fembs = cfgdata[0]
            rawdata = cfgdata[1]
            cfg_info = cfgdata[2]

            show_flg=True
            if ("DIRECT_PLS_CHK" in onekey) :
                show_flg = ana_res(fembs, rawdata, par=[9000,13000], rmsr=[5,25], pedr=[300,3000] )
            if ("ASICDAC_CALI_CHK" in onekey):
                show_flg = ana_res(fembs, rawdata, par=[7000,10000], rmsr=[5,25], pedr=[300,3000] )

            if show_flg:
                print (onekey + "  : Fail")
                print ("command on WIB terminal to retake data for this test item is as bellow :")
                print ("python3 LArASIC_QC_top.py -t 0")
                print ("When it is done, replace {} on the local PC".format(fp) )

                import matplotlib.pyplot as plt
                fig = plt.figure(figsize=(9,6))
                plt.rcParams.update({'font.size': 8})
                plt_log(plt,logsd, onekey)
                plt_subplot(plt, fembs, rawdata)
                plt.tight_layout( rect=[0.05, 0.05, 0.95, 0.95])
                plt.plot()
                plt.show()
                plt.close()
            else:
                print (onekey + "  : PASS")
    print ("#########################################################################")

if 1 in tms:
#if True:
    print ("-------------------------------------------------------------------------")
    print ("1: FE power consumption measurement")

    fp = fdir + "QC_PWR" + ".bin"
    with open(fp, 'rb') as fn:
        data = pickle.load( fn)
    
    dkeys = list(data.keys())
    
    logsd = data["logs"]
    dkeys.remove("logs")
    
    for onekey in dkeys:
        cfgdata = data[onekey]
        fembs = cfgdata[0]
        rawdata = cfgdata[1]
        cfg_info = cfgdata[2]
        pwr_meas = cfgdata[3]

        show_flg=True
        if ("PWR_SDD0_SDF0_SNC0" in onekey) :
            show_flg = ana_fepwr(pwr_meas, vin=[1.7,1.9], cdda=[15,25], cddp=[20,35], cddo=[0,5])
            if not show_flg:
                show_flg = ana_res(fembs, rawdata, par=[3000,6000], rmsr=[5,30], pedr=[8000,10000] )
        if ("PWR_SDD0_SDF1_SNC0" in onekey) :
            show_flg = ana_fepwr(pwr_meas, vin=[1.7,1.9], cdda=[35,50], cddp=[25,35], cddo=[0,10])
            if not show_flg:
                show_flg = ana_res(fembs, rawdata, par=[3000,6000], rmsr=[5,30], pedr=[8000,10000] )
        if ("PWR_SDD1_SDF0_SNC0" in onekey) :
            show_flg = ana_fepwr(pwr_meas, vin=[1.60,1.9], cdda=[40,50], cddp=[25,35], cddo=[5,15])
            if not show_flg:
                show_flg = ana_res(fembs, rawdata, par=[3000,6000], rmsr=[5,30], pedr=[8000,10000] )
        if ("PWR_SDD0_SDF0_SNC1" in onekey) :
            show_flg = ana_fepwr(pwr_meas, vin=[1.7,1.9], cdda=[15,25], cddp=[20,35], cddo=[0,5])
            if not show_flg:
                show_flg = ana_res(fembs, rawdata, par=[3000,6000], rmsr=[5,30], pedr=[500,2000] )
        if ("PWR_SDD0_SDF1_SNC1" in onekey) :
            show_flg = ana_fepwr(pwr_meas, vin=[1.7,1.9], cdda=[35,50], cddp=[25,35], cddo=[0,10])
            if not show_flg:
                show_flg = ana_res(fembs, rawdata, par=[3000,6000], rmsr=[5,30], pedr=[500,2000] )
        if ("PWR_SDD1_SDF0_SNC1" in onekey) :
            show_flg = ana_fepwr(pwr_meas, vin=[1.60,1.9], cdda=[40,50], cddp=[25,35], cddo=[5,15])
            if not show_flg:
                show_flg = ana_res(fembs, rawdata, par=[3000,6000], rmsr=[5,30], pedr=[300,2000] )

        if show_flg:
            print (onekey + "  : Fail")
            print ("command on WIB terminal to retake data for this test item is as bellow :")
            print ("python3 LArASIC_QC_top.py -t 1")
            print ("When it is done, replace {} on the local PC".format(fp) )

            import matplotlib.pyplot as plt
            fig = plt.figure(figsize=(9,6))
            plt.rcParams.update({'font.size': 8})
            plt_log(plt,logsd, onekey)
            plt_fepwr(plt, pwr_meas)
            plt_subplot(plt, fembs, rawdata)
            plt.tight_layout( rect=[0.05, 0.05, 0.95, 0.95])
            plt.plot()
            plt.show()
        else:
            print (onekey + "  : PASS")
    print ("#########################################################################")
   
if 2 in tms:
    print ("-------------------------------------------------------------------------")
    print ("2: FE response measurement checkout")

    fp = fdir + "QC_CHKRES" + ".bin"
    with open(fp, 'rb') as fn:
        data = pickle.load( fn)
    
    dkeys = list(data.keys())
    
    logsd = data["logs"]
    dkeys.remove("logs")
    #dkeys = ["CHK_OUTPUT_SDD0_SDF0_SLK00_SLK10_SNC0_ST01_ST11_SG00_SG10"]
    
    for onekey in dkeys:
        print (onekey)
        show_flg = True
        cfgdata = data[onekey]
        fembs = cfgdata[0]
        rawdata = cfgdata[1]
        cfg_info = cfgdata[2]

        if ("CHK_GAINs_SDD0_SDF0_SLK00_SLK10_SNC0_ST01_ST11_SG00_SG10" in onekey) :
            show_flg = ana_res(fembs, rawdata, par=[3000,6000], rmsr=[5,30], pedr=[8000,10000] )
        if ("CHK_GAINs_SDD0_SDF0_SLK00_SLK10_SNC0_ST01_ST11_SG00_SG11" in onekey) :
            show_flg = ana_res(fembs, rawdata, par=[3000,6000], rmsr=[3,15], pedr=[8000,10000] )
        if ("CHK_GAINs_SDD0_SDF0_SLK00_SLK10_SNC0_ST01_ST11_SG01_SG10" in onekey) :
            show_flg = ana_res(fembs, rawdata, par=[3000,6000], rmsr=[10,40], pedr=[8000,10000] )
        if ("CHK_GAINs_SDD0_SDF0_SLK00_SLK10_SNC0_ST01_ST11_SG01_SG11" in onekey) :
            show_flg = ana_res(fembs, rawdata, par=[2500,5000], rmsr=[2,10], pedr=[8000,10000] )
        if ("CHK_OUTPUT_SDD0_SDF0_SLK00_SLK10_SNC0_ST01_ST11_SG00_SG10" in onekey) :
            show_flg = ana_res(fembs, rawdata, par=[3000,6000], rmsr=[5,30], pedr=[8000,10000] )
        if ("CHK_OUTPUT_SDD0_SDF1_SLK00_SLK10_SNC0_ST01_ST11_SG00_SG10" in onekey) :
            show_flg = ana_res(fembs, rawdata, par=[3000,6000], rmsr=[5,30], pedr=[8000,10000] )
        if ("CHK_OUTPUT_SDD1_SDF0_SLK00_SLK10_SNC0_ST01_ST11_SG00_SG10" in onekey) :
            show_flg = ana_res(fembs, rawdata, par=[3000,6000], rmsr=[5,30], pedr=[8000,10000] )
        if ("CHK_BL_SDD0_SDF0_SLK00_SLK10_SNC0_ST01_ST11_SG00_SG10" in onekey) :
            show_flg = ana_res(fembs, rawdata, par=[3000,6000], rmsr=[5,30], pedr=[8000,10000] )
        if ("CHK_BL_SDD0_SDF0_SLK00_SLK10_SNC1_ST01_ST11_SG00_SG10" in onekey) :
            show_flg = ana_res(fembs, rawdata, par=[3000,6000], rmsr=[5,30], pedr=[500,2000] )
        if ("CHK_SLKS_SDD0_SDF0_SLK00_SLK10_SNC0_ST01_ST11_SG00_SG10" in onekey) :
            show_flg = ana_res(fembs, rawdata, par=[3000,6000], rmsr=[5,30], pedr=[8000,10000] )
        if ("CHK_SLKS_SDD0_SDF0_SLK00_SLK11_SNC0_ST01_ST11_SG00_SG10" in onekey) :
            show_flg = ana_res(fembs, rawdata, par=[3000,6000], rmsr=[5,30], pedr=[10000,12000] )
        if ("CHK_SLKS_SDD0_SDF0_SLK01_SLK10_SNC0_ST01_ST11_SG00_SG10" in onekey) :
            show_flg = ana_res(fembs, rawdata, par=[3000,6000], rmsr=[5,30], pedr=[8000,10000] )
        if ("CHK_SLKS_SDD0_SDF0_SLK01_SLK11_SNC0_ST01_ST11_SG00_SG10" in onekey) :
            show_flg = ana_res(fembs, rawdata, par=[3000,6000], rmsr=[5,30], pedr=[8000,10000] )
        if ("CHK_TP_SDD0_SDF0_SLK00_SLK10_SNC0_ST00_ST10_SG00_SG10" in onekey) :
            show_flg = ana_res(fembs, rawdata, par=[3000,6000], rmsr=[5,30], pedr=[8000,10000] )
        if ("CHK_TP_SDD0_SDF0_SLK00_SLK10_SNC0_ST00_ST11_SG00_SG10" in onekey) :
            show_flg = ana_res(fembs, rawdata, par=[3000,6000], rmsr=[5,30], pedr=[8000,10000] )
        if ("CHK_TP_SDD0_SDF0_SLK00_SLK10_SNC0_ST01_ST10_SG00_SG10" in onekey) :
            show_flg = ana_res(fembs, rawdata, par=[3000,6000], rmsr=[5,30], pedr=[8000,10000] )
        if ("CHK_TP_SDD0_SDF0_SLK00_SLK10_SNC0_ST01_ST11_SG00_SG10" in onekey) :
            show_flg = ana_res(fembs, rawdata, par=[3000,6000], rmsr=[5,30], pedr=[8000,10000] )

        if show_flg:
            print (onekey + "  : Fail")
            print ("command on WIB terminal to retake data for this test item is as bellow :")
            print ("python3 LArASIC_QC_top.py -t 2")
            print ("When it is done, replace {} on the local PC".format(fp) )

            import matplotlib.pyplot as plt
            fig = plt.figure(figsize=(9,6))
            plt.rcParams.update({'font.size': 8})
            plt_log(plt,logsd, onekey)
            plt_subplot(plt, fembs, rawdata)
            plt.tight_layout( rect=[0.05, 0.05, 0.95, 0.95])
            plt.plot()
            plt.show()
        else:
            print (onekey + "  : PASS")
    print ("#########################################################################")

if 3 in tms:
    print ("-------------------------------------------------------------------------")
    print ("3: FE monitoring measurement ")
    print ("command on WIB terminal to retake data for this test item is as bellow :")
    print ("python3 LArASIC_QC_top.py -t 3")
    fp = fdir + "QC_MON" + ".bin"
    print ("When it is done, replace {} on the local PC".format(fp) )

    with open(fp, 'rb') as fn:
        data = pickle.load( fn)
    
    AD_LSB = 2564/4096 
    dkeys = list(data.keys())
    
    logsd = data["logs"]
    dkeys.remove("logs")

    #####################VBGR and temperature analysis#####################################
    vbts = ('VBGR', 'MON_VBGR', 'MON_Temper')
    vbgrs   = np.array(data[vbts[0]][1])
    vmbgrs  = np.array(data[vbts[1]][1])
    vmtemps = np.array(data[vbts[2]][1])
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(9,6))
    plt.plot(vbgrs, label=vbts[0], marker='o')
    plt.plot(vmbgrs, label=vbts[1], marker='*')
    plt.plot(vmtemps, label=vbts[2], marker='s')
    plt.title("VBGR and Vtemperature Measurement")
    plt.ylabel("Voltage / mV")
    plt.ylim((0,2000))
    plt.xlabel("FE no")
    plt.legend()
    plt.grid()
    plt.plot()
    plt.show()
    plt.close()

    #####################BL analysis#####################################
    vblsk = ('MON_200BL', 'MON_900BL')
    vbls200   = data[vblsk[0]]
    vbls900   = data[vblsk[1]]

    fes_200 = []
    fes_900 = []
    for chn in range(16):
        for fe in range(8):
            fes_200.append(vbls200[chn][1][fe]*AD_LSB)
            fes_900.append(vbls900[chn][1][fe]*AD_LSB)
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(9,6))
    plt.plot(fes_200, label="BL 200mV", marker='o')
    plt.plot(fes_900, label="BL 900mV", marker='*')
    for i in range(0,128,16):
        plt.vlines(i-0.5, 0, 2000, color='y')

    plt.title("Baseline Measurement")
    plt.ylabel("Voltage / mV")
    plt.ylim((0,2000))
    plt.xlabel("FE chns")
    plt.legend()
    plt.plot()
    plt.show()
    plt.close()

    #####################ASIC-DAC analysis#####################################
    dacdkeys = ["MON_DAC_SGP1", "MON_DAC_SG0_0_SG1_0", "MON_DAC_SG0_1_SG1_0", "MON_DAC_SG0_0_SG1_1", "MON_DAC_SG0_1_SG1_1" ]

    fig = plt.figure(figsize=(12,10))
    plt.rcParams.update({'font.size': 6})
    ax1 = plt.subplot2grid((4, 2), (0, 0), colspan=1, rowspan=1)
    ax2 = plt.subplot2grid((4, 2), (1, 0), colspan=1, rowspan=1)
    ax3 = plt.subplot2grid((4, 2), (2, 0), colspan=1, rowspan=1)
    ax4 = plt.subplot2grid((4, 2), (3, 0), colspan=1, rowspan=1)
    ax5 = plt.subplot2grid((4, 2), (0, 1), colspan=1, rowspan=1)
    ax6 = plt.subplot2grid((4, 2), (1, 1), colspan=1, rowspan=1)
    ax7 = plt.subplot2grid((4, 2), (2, 1), colspan=1, rowspan=1)
    ax8 = plt.subplot2grid((4, 2), (3, 1), colspan=1, rowspan=1)
    axs = [ax1, ax2, ax3, ax4, ax5, ax6, ax7, ax8]

    for dacdkey in dacdkeys:
        fes = dacana(data,dacdkey )
        for fei in range(8):
            dacinfo = fes[fei]
            axs[fei].scatter(dacinfo[2], dacinfo[3], marker='.', label= "FE%02d-"%dacinfo[1] + dacinfo[0] + " %.2f mV/bit "%dacinfo[4] + "%.2f%%"%(dacinfo[6]*100))
    for fei in range(8):
        axs[fei].set_title("DAC Measurement", fontsize=8)
        axs[fei].set_ylabel("Voltage / mV", fontsize=8)
        axs[fei].set_ylim((0,1500))
        axs[fei].set_xlabel("DAC / bit", fontsize=8)
        axs[fei].grid()
        axs[fei].legend()

    plt.tight_layout( rect=[0.05, 0.05, 0.95, 0.95])
    plt.show()
    plt.close()
    print ("#########################################################################")

if 4 in tms:
    print ("-------------------------------------------------------------------------")
    print ("4: FE power cycling measurement  ")
    print ("command on WIB terminal to retake data for this test item is as bellow :")
    print ("python3 LArASIC_QC_top.py -t 4")
    fp = fdir + "QC_PWR_CYCLE" + ".bin"
    print ("When it is done, replace {} on the local PC".format(fp) )
    if os.path.isfile(fp):
        with open(fp, 'rb') as fn:
            data = pickle.load( fn)
    
        dkeys = list(data.keys())
        
        logsd = data["logs"]
        dkeys.remove("logs")
        
    for onekey in dkeys:
        cfgdata = data[onekey]
        fembs = cfgdata[0]
        rawdata = cfgdata[1]
        cfg_info = cfgdata[2]
        pwr_meas = cfgdata[3]

        show_flg=True
        if ("PwrCycle_0" in onekey) :
            show_flg = ana_fepwr(pwr_meas, vin=[1.7,1.9], cdda=[15,25], cddp=[20,35], cddo=[0,5])
            if not show_flg:
                show_flg = ana_res(fembs, rawdata, par=[3000,6000], rmsr=[5,30], pedr=[8000,10000] )
        if ("PwrCycle_1" in onekey) :
            show_flg = ana_fepwr(pwr_meas, vin=[1.7,1.9], cdda=[15,30], cddp=[25,40], cddo=[0,10])
            if not show_flg:
                show_flg = ana_res(fembs, rawdata, par=[3000,6000], rmsr=[5,30], pedr=[8000,10000] )
        if ("PwrCycle_2" in onekey) :
            show_flg = ana_fepwr(pwr_meas, vin=[1.70,1.9], cdda=[15,30], cddp=[30,40], cddo=[0,10])
            if not show_flg:
                show_flg = ana_res(fembs, rawdata, par=[3000,6000], rmsr=[5,30], pedr=[8000,10000] )
        if ("PwrCycle_3" in onekey) :
            show_flg = ana_fepwr(pwr_meas, vin=[1.70,1.9], cdda=[15,30], cddp=[30,40], cddo=[0,10])
            if not show_flg:
                show_flg = ana_res(fembs, rawdata, par=[3000,6000], rmsr=[5,30], pedr=[10000,12000] )
        if ("PwrCycle_4" in onekey) :
            show_flg = ana_fepwr(pwr_meas, vin=[1.70,1.9], cdda=[15,30], cddp=[30,40], cddo=[0,10])
            if not show_flg:
                show_flg = ana_res(fembs, rawdata, par=[10000,13000], rmsr=[5,30], pedr=[500,2000] )
        if ("PwrCycle_5" in onekey) :
            show_flg = ana_fepwr(pwr_meas, vin=[1.65,1.9], cdda=[40,50], cddp=[20,35], cddo=[5,15])
            if not show_flg:
                show_flg = ana_res(fembs, rawdata, par=[10000,13000], rmsr=[5,30], pedr=[500,2000] )
        if ("PwrCycle_6" in onekey) :
            show_flg = ana_fepwr(pwr_meas, vin=[1.65,1.9], cdda=[40,50], cddp=[20,35], cddo=[0,10])
            if not show_flg:
                show_flg = ana_res(fembs, rawdata, par=[10000,13000], rmsr=[5,30], pedr=[500,2000] )
        if ("PwrCycle_7" in onekey) :
            show_flg = ana_fepwr(pwr_meas, vin=[1.7,1.9], cdda=[15,30], cddp=[30,40], cddo=[0,10])
            if not show_flg:
                show_flg = ana_res(fembs, rawdata, par=[10000,13000], rmsr=[5,30], pedr=[500,2000] )

        if show_flg:
            print (onekey)
            import matplotlib.pyplot as plt
            fig = plt.figure(figsize=(9,6))
            plt.rcParams.update({'font.size': 8})
            cfgdata = data[onekey]
            fembs = cfgdata[0]
            rawdata = cfgdata[1]
            cfg_info = cfgdata[2]
            pwr_meas = cfgdata[3]
            plt_log(plt,logsd, onekey)
            plt_fepwr(plt, pwr_meas)
            plt_subplot(plt, fembs, rawdata)
            plt.tight_layout( rect=[0.05, 0.05, 0.95, 0.95])
            plt.plot()
            plt.show()
    print ("#########################################################################")

if 5 in tms:
    print ("-------------------------------------------------------------------------")
    print ("5: FE noise measurement ")
    print ("command on WIB terminal to retake data for this test item is as bellow :")
    print ("python3 LArASIC_QC_top.py -t 5")
    fp = fdir + "QC_RMS" + ".bin"
    print ("When it is done, replace {} on the local PC".format(fp) )
    with open(fp, 'rb') as fn:
        data = pickle.load( fn)
    
    dkeys = list(data.keys())
    
    logsd = data["logs"]
    dkeys.remove("logs")

    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(8,6))
    plt.rcParams.update({'font.size': 8})
    ax1 = plt.subplot2grid((2, 1), (0, 0), colspan=1, rowspan=1)
    ax2 = plt.subplot2grid((2, 1), (1, 0), colspan=1, rowspan=1)
  
    for st0 in [0, 1]:
        for st1 in [0, 1]:
            for onekey in dkeys:
                if "RMS_SDD0_SDF0_SLK00_SLK10_SNC0_ST0%d_ST1%d_SG00_SG10"%(st0, st1) in onekey:
                    print (onekey)
                    cfgdata = data[onekey]
                    fembs = cfgdata[0]
                    rawdata = cfgdata[1]
                    cfg_info = cfgdata[2]
                    chns, rmss, peds, pkps, pkns, wfs = data_ana(fembs, rawdata, rms_flg=True)

                    ax1.plot(np.array(peds), marker='.', label="ST0%d_ST1%d"%(st0, st1))
                    ax2.plot(np.array(rmss), marker='.', label="ST0%d_ST1%d"%(st0, st1))

    ax1.set_xlim((-10,130))
    ax1.legend()
    ax2.set_xlim((-10,130))
    ax2.legend()

    plt.tight_layout( rect=[0.05, 0.05, 0.95, 0.95])
    plt.plot()
    plt.show()
    plt.close()

    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(8,6))
    plt.rcParams.update({'font.size': 8})
    ax1 = plt.subplot2grid((2, 1), (0, 0), colspan=1, rowspan=1)
    ax2 = plt.subplot2grid((2, 1), (1, 0), colspan=1, rowspan=1)
  
    for slk0 in [0, 1]:
        for slk1 in [0, 1]:
            for onekey in dkeys:
                if "RMS_SLK_SDD0_SDF0_SLK0%d_SLK1%d_SNC0_ST01_ST11_SG00_SG10"%(slk0, slk1) in onekey:
                    print (onekey)
                    cfgdata = data[onekey]
                    fembs = cfgdata[0]
                    rawdata = cfgdata[1]
                    cfg_info = cfgdata[2]
                    chns, rmss, peds, pkps, pkns, wfs = data_ana(fembs, rawdata, rms_flg=True)

                    ax1.plot(np.array(peds), marker='.', label="ST0%d_ST1%d"%(slk0, slk1))
                    ax2.plot(np.array(rmss), marker='.', label="ST0%d_ST1%d"%(slk0, slk1))

    ax1.set_xlim((-10,130))
    ax1.legend()
    ax2.set_xlim((-10,130))
    ax2.legend()

    plt.tight_layout( rect=[0.05, 0.05, 0.95, 0.95])
    plt.plot()
    plt.show()
    plt.close()
    print ("#########################################################################")

if 61 in tms:
    print ("-------------------------------------------------------------------------")
    print (" 61: FE calibration measurement (ASIC-DAC)")
    print ("command on WIB terminal to retake data for this test item is as bellow :")
    print ("python3 LArASIC_QC_top.py -t 61")
    fp = fdir + "QC_CALI_ASICDAC" + ".bin"
    print ("When it is done, replace {} on the local PC".format(fp) )
    with open(fp, 'rb') as fn:
        data = pickle.load( fn)
    
    dkeys = list(data.keys())
    
    logsd = data["logs"]
    dkeys.remove("logs")

    for snc in [0, 1]:
        import matplotlib.pyplot as plt
        fig = plt.figure(figsize=(8,6))
        plt.rcParams.update({'font.size': 8})
        ax1 = plt.subplot2grid((2, 1), (0, 0), colspan=1, rowspan=1)
        ax2 = plt.subplot2grid((2, 1), (1, 0), colspan=1, rowspan=1)
  
        for onekey in dkeys:
            if "SNC%d"%snc in onekey:
                print (onekey)
                cfgdata = data[onekey]
                fembs = cfgdata[0]
                rawdata = cfgdata[1]
                cfg_info = cfgdata[2]
                chns, rmss, peds, pkps, pkns, wfs = data_ana(fembs, rawdata)
                ax1.plot(pkps, marker='.', label=onekey)
                ax2.plot(pkns, marker='.', label=onekey)
        ax1.set_xlim((-10,200))
        ax1.legend()
        ax2.set_xlim((-10,200))
        ax2.legend()

        plt.tight_layout( rect=[0.05, 0.05, 0.95, 0.95])
        plt.plot()
        plt.show()
        plt.close()
    print ("#########################################################################")
    
if 62 in tms:
    print ("-------------------------------------------------------------------------")
    print ("62: FE calibration measurement (DAT-DAC) ")
    print ("command on WIB terminal to retake data for this test item is as bellow :")
    print ("python3 LArASIC_QC_top.py -t 62")
    fp = fdir + "QC_CALI_DATDAC" + ".bin"
    print ("When it is done, replace {} on the local PC".format(fp) )
    with open(fp, 'rb') as fn:
        data = pickle.load( fn)
    
    dkeys = list(data.keys())
    
    logsd = data["logs"]
    dkeys.remove("logs")

    for snc in [ 1]:
        for buf in [0,1,2]:
            sdd = buf//2
            sdf = buf%2
            import matplotlib.pyplot as plt
            fig = plt.figure(figsize=(8,6))
            plt.rcParams.update({'font.size': 8})
            ax1 = plt.subplot2grid((2, 1), (0, 0), colspan=1, rowspan=1)
            ax2 = plt.subplot2grid((2, 1), (1, 0), colspan=1, rowspan=1)
  
            for onekey in dkeys:
                if "SDD%d_SDF%d_SNC%d"%( sdd, sdf, snc) in onekey:
                    print (onekey)
                    cfgdata = data[onekey]
                    fembs = cfgdata[0]
                    rawdata = cfgdata[1]
                    cfg_info = cfgdata[2]
                    chns, rmss, peds, pkps, pkns, wfs = data_ana(fembs, rawdata)
                    ax1.plot(np.array(pkps)-np.array(peds), marker='.', label=onekey)
                    ax2.plot(np.array(pkns)-np.array(peds), marker='.', label=onekey)
            ax1.set_xlim((-10,200))
            ax1.legend()
            ax2.set_xlim((-10,200))
            ax2.legend()

            plt.tight_layout( rect=[0.05, 0.05, 0.95, 0.95])
            plt.plot()
            plt.show()
            plt.close()
    print ("#########################################################################")

if 63 in tms:
    print ("-------------------------------------------------------------------------")
    print (" 63: FE calibration measurement (Direct-Input) ")
    print ("command on WIB terminal to retake data for this test item is as bellow :")
    print ("python3 LArASIC_QC_top.py -t 63")
    fp = fdir + "QC_CALI_DIRECT" + ".bin"
    print ("When it is done, replace {} on the local PC".format(fp) )
    with open(fp, 'rb') as fn:
        data = pickle.load( fn)
    
    dkeys = list(data.keys())
    
    logsd = data["logs"]
    dkeys.remove("logs")

    for snc in [ 1]:
        import matplotlib.pyplot as plt
        fig = plt.figure(figsize=(8,6))
        plt.rcParams.update({'font.size': 8})
        ax1 = plt.subplot2grid((2, 1), (0, 0), colspan=1, rowspan=1)
        ax2 = plt.subplot2grid((2, 1), (1, 0), colspan=1, rowspan=1)
  
        for onekey in dkeys:
            if "SNC%d"%snc in onekey:
                print (onekey)
                cfgdata = data[onekey]
                fembs = cfgdata[0]
                rawdata = cfgdata[1]
                cfg_info = cfgdata[2]
                chns, rmss, peds, pkps, pkns, wfs = data_ana(fembs, rawdata)
#                ax1.plot(pkps, marker='.', label=onekey)
#                ax2.plot(pkns, marker='.', label=onekey)
                ax1.plot(np.array(pkps)-np.array(peds), marker='.', label=onekey)
                ax2.plot(np.array(pkns)-np.array(peds), marker='.', label=onekey)

        ax1.set_xlim((-10,200))
        ax1.legend()
        ax2.set_xlim((-10,200))
        ax2.legend()

        plt.tight_layout( rect=[0.05, 0.05, 0.95, 0.95])
        plt.plot()
        plt.show()
        plt.close()
    print ("#########################################################################")

if 7 in tms:
    print ("-------------------------------------------------------------------------")
    print ("7: FE delay run ")
    print ("command on WIB terminal to retake data for this test item is as bellow :")
    print ("python3 LArASIC_QC_top.py -t 7")
    fp = fdir + "QC_DLY_RUN" + ".bin"
    print ("When it is done, replace {} on the local PC".format(fp) )

    with open(fp, 'rb') as fn:
        data = pickle.load( fn)
    
    dkeys = list(data.keys())
    
    logsd = data["logs"]
    dkeys.remove("logs")
    
    for onekey in dkeys:
        show_flg = True
        cfgdata = data[onekey]
        fembs = cfgdata[0]
        rawdata = cfgdata[1]
        cfg_info = cfgdata[2]

        show_flg = ana_res(fembs, rawdata, par=[3000,6000], rmsr=[5,45], pedr=[8000,10000] )
        if show_flg:
            print (onekey + "  : Fail")
            print ("command on WIB terminal to retake data for this test item is as bellow :")
            print ("python3 LArASIC_QC_top.py -t 7")
            print ("When it is done, replace {} on the local PC".format(fp) )

            import matplotlib.pyplot as plt
            fig = plt.figure(figsize=(9,6))
            plt.rcParams.update({'font.size': 8})
            plt_log(plt,logsd, onekey)
            plt_subplot(plt, fembs, rawdata)
            plt.tight_layout( rect=[0.05, 0.05, 0.95, 0.95])
            plt.plot()
            plt.show()
        else:
            print (onekey + "  : PASS")
    print ("#########################################################################")

if 8 in tms:
    print ("-------------------------------------------------------------------------")
    print ("8: FE cali-cap measurement ")
    print ("command on WIB terminal to retake data for this test item is as bellow :")
    print ("python3 LArASIC_QC_top.py -t 8")
    fp = fdir + "QC_Cap_Meas" + ".bin"
    print ("When it is done, replace {} on the local PC".format(fp) )
    with open(fp, 'rb') as fn:
        data = pickle.load( fn)
    
    dkeys = list(data.keys())
    
    logsd = data["logs"]
    dkeys.remove("logs")

    chncs = 0
    pps4s = []
    for chncs in range(16):
        pps4 = []
        vals = []
        for onekey in dkeys:
            if "FECHN%02d"%chncs in onekey:
                print (onekey)
                cfgdata = data[onekey]
                fembs = cfgdata[0]
                rawdata = cfgdata[1]
                fembchn = cfgdata[2]
                val =     cfgdata[3]
                period =  cfgdata[4]
                width =   cfgdata[5]
                fe_info = cfgdata[6]
                cfg_info = cfgdata[7]
                vals.append(val)
        
                wibdata = wib_dec(rawdata, fembs, spy_num=1)[0]
                #chns = np.arange(fembs[0]*128 + fembchn, fembs[0]*128 + fembchn + 128, 16)
                chns = np.arange( fembchn, fembchn + 128, 16)
                pps = []

                for femb in fembs:
                #    import matplotlib.pyplot as plt
                #    fig = plt.figure(figsize=(8,6))

                    for chn in chns:
                        #print (np.max(wibdata[femb][chn]), np.mean(wibdata[femb][chn]))
                        pps.append (np.max(wibdata[femb][chn]))
                #        plt.plot(wibdata[femb][chn], label="%d"%chn)
                #    plt.legend()
                #    plt.show()
                #    plt.close()


                pps4.append(pps)
        pps4s.append(pps4)

    ratios = []
    for ch in range(128):
        fe=ch//16
        fechn=ch%16
        ratios.append((pps4s[fechn][0][fe] - pps4s[fechn][1][fe])/(pps4s[fechn][2][fe] - pps4s[fechn][3][fe]))

    del1 = vals[3]-vals[2]
    del2 = vals[1] - vals[0]
    caps = np.array(ratios)*del1/del2/0.185
    print (caps)

    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(8,6))
    plt.plot(caps)
    plt.title("1pF Cap Measurement")
    plt.ylabel("Capacitance / pC")
    plt.ylim((0,1.5))
    plt.xlabel("FE no")
    for i in range(0,128,16):
        plt.vlines(i-0.5, 0, 1.5, color='y')
    plt.plot()
    plt.show()
    plt.close()
    print ("#########################################################################")





#if True:
#    fp = fdir + "QC_CALI_DIRECT" + ".bin"
#    with open(fp, 'rb') as fn:
#        data = pickle.load( fn)
#    
#    dkeys = list(data.keys())
#    
#    logsd = data["logs"]
#    dkeys.remove("logs")
#    
#    for onekey in dkeys:
#        print (onekey)
#        import matplotlib.pyplot as plt
#        fig = plt.figure(figsize=(6,8))
#        plt.rcParams.update({'font.size': 8})
#        cfgdata = data[onekey]
#        fembs = cfgdata[0]
#        rawdata = cfgdata[1]
#        cfg_info = cfgdata[2]
#        plt_log(plt,logsd)
#        plt_subplot(plt, fembs, rawdata)
#        plt.tight_layout( rect=[0.05, 0.05, 0.95, 0.95])
#        plt.plot()
#        plt.show()
   
#
#
#
#
#
#
#
#
#
#
#
#fp = fdir + "QC_CHKRES" + ".bin"
#with open(fp, 'rb') as fn:
#    data = pickle.load( fn)
#
#dkeys = list(data.keys())
#if "logs" in dkeys:
#    dkeys.remove("logs")
#
#for onekey in dkeys:
#    print (onekey)
#    cfgdata = data[onekey]
#    fembs = cfgdata[0]
#    rawdata = cfgdata[1]
#    #fembs = cfgdata[1]
#    #rawdata = cfgdata[0]
#
#    wibdata = wib_dec(rawdata,fembs, spy_num=1)
#    #wibdata = wib_dec(rawdata,fembs, spy_num=1)
#
#    datd = [wibdata[0], wibdata[1],wibdata[2],wibdata[3]][0]
#
#    import matplotlib.pyplot as plt
#    for fe in range(8):
#        for fe_chn in range(16):
#            fechndata = datd[fe*16+fe_chn]
#            if np.max(fechndata) - np.mean(fechndata) > 8000:
#                pass
#            else:
#                print (fe*16+fe_chn,fe, fe_chn) 
#            plt.plot(fechndata)
#    plt.show()
#    plt.close()
#            #    pp = np.max(fechndata[500:1500])
#            #    pp_pos = np.where(fechndata[500:1500] == pp)[0][0]
#            #    x = np.arange(300)
#            #    plt.plot(x,fechndata[500+pp_pos-100:500+pp_pos+200])
#            #    ped = np.mean(fechndata[pp_pos-200:pp_pos-150])
#            #    npmin = np.min(fechndata)
#            #    print (fe, fe_chn, pp, ped, npmin)
#            #    plt.show()
#            #    plt.close()
#
## ... (rest of your code)
# 
##    print (pwr)
            




    
