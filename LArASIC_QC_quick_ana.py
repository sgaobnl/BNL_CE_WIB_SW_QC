import time
import os
import sys
import numpy as np
import pickle
import copy
import time, datetime, random, statistics    
from spymemory_decode import wib_dec
import statsmodels.api as sm
#from spymemory_decode import avg_aligned_by_ts

fsubdir = "/FE_001000000_001000001_001000202_001000003_001000004_001000005_001000006_001000007"
froot = "D:/Github/BNL_CE_WIB_SW_QC_main/tmp_data/"
fdir = froot + fsubdir + "/"

def linear_fit(x, y):
    error_fit = False 
    try:
        results = sm.OLS(y,sm.add_constant(x)).fit()
    except ValueError:
        error_fit = True 
    if ( error_fit == False ):
        error_gain = False 
        try:
            slope = results.params[1]
        except IndexError:
            slope = 0
            error_gain = True
        try:
            constant = results.params[0]
        except IndexError:
            constant = 0
    else:
        slope = 0
        constant = 0
        error_gain = True

    y_fit = np.array(x)*slope + constant
    delta_y = abs(y - y_fit)
    inl = delta_y / (max(y)-min(y))
    peakinl = max(inl)
    return slope, constant, peakinl, error_gain


def plt_log(plt,logsd):
    fig.suptitle("Test Result", weight ="bold", fontsize = 12)
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

    ax6.scatter(fe, cddas, color='b', marker = 'o', label='VDDA')
    ax6.scatter(fe, cddps, color='r', marker = 'o', label='VDDP')
    ax6.scatter(fe, cddos, color='g', marker = 'o', label='VDDO')
    ax6.set_title("Current Measurement", fontsize=8)
    ax6.set_ylabel("Current / mA", fontsize=8)
    ax6.set_ylim((-10,50))
    ax6.set_xlabel("FE no", fontsize=8)
    ax6.grid()



def data_ana(fembs, rawdata, rms_flg=False):
    wibdata = wib_dec(rawdata,fembs, spy_num=1)
    datd = [wibdata[0], wibdata[1],wibdata[2],wibdata[3]][fembs[0]]

    chns =[]
    rmss = []
    peds = []
    pkps = []
    pkns = []
    wfs = []

    ppos=0
    npos=0
    for achn in range(len(datd)):
        chndata = datd[achn]
        amax = np.max(chndata[300:-150])
        amin = np.min(chndata[300:-150])
        if achn==0:
            ppos = np.where(chndata[300:]==amax)[0][0] + 300
            npos = np.where(chndata[300:]==amin)[0][0] + 300

        if rms_flg:
            arms = np.std(chndata)
            aped = int(np.mean(chndata))
        else:
            arms = np.std(chndata[ppos-150:ppos-50])
            aped = int(np.mean(chndata[ppos-150:ppos-50]))
        chns.append(achn)
        rmss.append(arms)
        peds.append(aped)
        pkps.append(amax)
        pkns.append(amin)
        wfs.append(chndata[ppos-50:ppos+150])
    return chns, rmss, peds, pkps, pkns, wfs


def plt_subplot(plt, fembs, rawdata):
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

cs_no =  True
if cs_no:
#if True:
    fp = fdir + "QC_INIT_CHK" + ".bin"
    with open(fp, 'rb') as fn:
        data = pickle.load( fn)
    
    dkeys = list(data.keys())
    
    logsd = data["logs"]
    dkeys.remove("logs")
    
    for onekey in dkeys:
        if ("DIRECT_PLS_CHK" in onekey) or ("ASICDAC_CALI_CHK" in onekey):
            print (onekey)
            import matplotlib.pyplot as plt
            fig = plt.figure(figsize=(9,6))
            plt.rcParams.update({'font.size': 8})
            cfgdata = data[onekey]
            fembs = cfgdata[0]
            rawdata = cfgdata[1]
            cfg_info = cfgdata[2]
            plt_log(plt,logsd)
            plt_subplot(plt, fembs, rawdata)
            plt.tight_layout( rect=[0.05, 0.05, 0.95, 0.95])
            plt.plot()
            plt.show()


if cs_no:
#if True:
    fp = fdir + "QC_PWR" + ".bin"
    with open(fp, 'rb') as fn:
        data = pickle.load( fn)
    
    dkeys = list(data.keys())
    
    logsd = data["logs"]
    dkeys.remove("logs")
    
    for onekey in dkeys:
        print (onekey)
        import matplotlib.pyplot as plt
        fig = plt.figure(figsize=(9,6))
        plt.rcParams.update({'font.size': 8})
        cfgdata = data[onekey]
        fembs = cfgdata[0]
        rawdata = cfgdata[1]
        cfg_info = cfgdata[2]
        pwr_meas = cfgdata[3]
        plt_log(plt,logsd)
        plt_fepwr(plt, pwr_meas)
        plt_subplot(plt, fembs, rawdata)
        plt.tight_layout( rect=[0.05, 0.05, 0.95, 0.95])
        plt.plot()
        plt.show()


if cs_no:
#if True:
    fp = fdir + "QC_PWR_CYCLE" + ".bin"
    if os.path.isfile(fp):
        with open(fp, 'rb') as fn:
            data = pickle.load( fn)
    
        dkeys = list(data.keys())
        
        logsd = data["logs"]
        dkeys.remove("logs")
        
        for onekey in dkeys:
            print (onekey)
            import matplotlib.pyplot as plt
            fig = plt.figure(figsize=(9,6))
            plt.rcParams.update({'font.size': 8})
            cfgdata = data[onekey]
            fembs = cfgdata[0]
            rawdata = cfgdata[1]
            cfg_info = cfgdata[2]
            pwr_meas = cfgdata[3]
            plt_log(plt,logsd)
            plt_fepwr(plt, pwr_meas)
            plt_subplot(plt, fembs, rawdata)
            plt.tight_layout( rect=[0.05, 0.05, 0.95, 0.95])
            plt.plot()
            plt.show()
   
if cs_no:
#if True:
    fp = fdir + "QC_CHKRES" + ".bin"
    with open(fp, 'rb') as fn:
        data = pickle.load( fn)
    
    dkeys = list(data.keys())
    
    logsd = data["logs"]
    dkeys.remove("logs")
    
    for onekey in dkeys:
        print (onekey)
        import matplotlib.pyplot as plt
        fig = plt.figure(figsize=(9,6))
        plt.rcParams.update({'font.size': 8})
        cfgdata = data[onekey]
        fembs = cfgdata[0]
        rawdata = cfgdata[1]
        cfg_info = cfgdata[2]
        plt_log(plt,logsd)
        plt_subplot(plt, fembs, rawdata)
        plt.tight_layout( rect=[0.05, 0.05, 0.95, 0.95])
        plt.plot()
        plt.show()

if cs_no:
#if True:
    fp = fdir + "QC_MON" + ".bin"
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

if cs_no:
#if True:
    fp = fdir + "QC_CALI_ASICDAC" + ".bin"
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

if cs_no:
    fp = fdir + "QC_CALI_DATDAC" + ".bin"
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

if cs_no:
#if True:
    fp = fdir + "QC_CALI_DIRECT" + ".bin"
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

if cs_no:
    fp = fdir + "QC_RMS" + ".bin"
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

if cs_no:
#if True:
    fp = fdir + "QC_Cap_Meas" + ".bin"
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
        
                wibdata = wib_dec(rawdata, fembs, spy_num=1)
                #chns = np.arange(fembs[0]*128 + fembchn, fembs[0]*128 + fembchn + 128, 16)
                chns = np.arange( fembchn, fembchn + 128, 16)
                pps = []

                #for chn in chns:
                #    avgdata = avg_aligned_by_ts(wibdata, chn, period)
                #    pps.append (np.max(avgdata[0]))
                for femb in fembs:
                    for chn in chns:
                        #print (np.max(wibdata[femb][chn]), np.mean(wibdata[femb][chn]))
                        pps.append (np.max(wibdata[femb][chn]))
                #exit()
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
            




    
