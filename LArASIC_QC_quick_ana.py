import time
import sys
import numpy as np
import pickle
import copy
import time, datetime, random, statistics    
from spymemory_decode import wib_dec

fdir = "./tmp_data/FE_00000000_00000001_00000002_00000003_00000004_00000005_00000006_00000007/"

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
        y = 0.93
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



def plt_subplot(plt, fembs, rawdata):
    ax1 = plt.subplot2grid((2, 3), (0, 1), colspan=1, rowspan=1)
    ax2 = plt.subplot2grid((2, 3), (0, 2), colspan=1, rowspan=1)
    ax3 = plt.subplot2grid((2, 3), (1, 1), colspan=1, rowspan=1)
    ax4 = plt.subplot2grid((2, 3), (1, 2), colspan=1, rowspan=1)

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
        amax = np.max(chndata[300:])
        amin = np.min(chndata[300:])
        if achn==0:
            ppos = np.where(chndata==amax)[0][0]
            npos = np.where(chndata==amin)[0][0]
        aped = int(np.mean(chndata[ppos-150:ppos-50]))

        arms = np.std(chndata[ppos-150:ppos-50])
        chns.append(achn)
        rmss.append(arms)
        peds.append(aped)
        pkps.append(amax)
        pkns.append(amin)
        wfs.append(chndata[ppos-50:ppos+150])
        ax1.plot(chndata[ppos-20:ppos+20])
        ax2.plot(chndata[npos-20:npos+20])
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


if False:
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
    
if False:
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

if True:
    fp = fdir + "QC_MON" + ".bin"
    with open(fp, 'rb') as fn:
        data = pickle.load( fn)
    
    AD_LSB = 2564/4096 
    dkeys = list(data.keys())
    
    logsd = data["logs"]
    dkeys.remove("logs")
    print (dkeys)

    vbts = ('VBGR', 'MON_VBGR', 'MON_Temper')
    vbgrs   = np.array(data[vbts[0]][1])
    print (vbgrs)
    vmbgrs  = np.array(data[vbts[1]][1])
    print (vmbgrs)
    vmtemps = np.array(data[vbts[2]][1])
    print (vmtemps)
    vblsk = ('MON_200BL', 'MON_900BL')
    vbls200   = np.array(data[vblsk[0]][1])*AD_LSB
    vbls900   = np.array(data[vblsk[1]][1])*AD_LSB
    print (vbls200)
    print (vbls900)
    exit()

    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(9,6))
    plt.rcParams.update({'font.size': 8})
    ax1 = plt.subplot2grid((2, 3), (0, 0), colspan=1, rowspan=1)
    ax2 = plt.subplot2grid((2, 3), (0, 1), colspan=1, rowspan=1)
    ax3 = plt.subplot2grid((2, 3), (0, 2), colspan=1, rowspan=1)
    ax4 = plt.subplot2grid((2, 3), (1, 0), colspan=1, rowspan=1)
    ax5 = plt.subplot2grid((2, 3), (1, 1), colspan=1, rowspan=1)
    ax6 = plt.subplot2grid((2, 3), (1, 2), colspan=1, rowspan=1)
  

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
            




    
