import time
import os
import sys
import numpy as np
import pickle, struct
import copy
import time, datetime
from spymemory_decode import wib_dec
#from dunedaq_decode import wib_dec #based CPP
#from spymemory_decode import avg_aligned_by_ts
import colorama
from colorama import Fore, Back
colorama.init(autoreset=True)

# Automatically adds a Style.RESET_ALL after each print statement
#print(Fore.RED + 'Red foreground text')
#print(Back.RED + 'Red background text')

#fsubdir = "ADC_000100001_000100002_000100003_000100004_000100005_000100006_000100007_000100008"
#fsubdir = "ADC_100100001_100100002_100100003_100100004_100100005_100100006_100100007_100100008"
#fsubdir = "FE_003000001_003000002_003000003_003000004_003000005_003000006_003000007_003000008"
fsubdir = "RT_CD_060592417_060542417"
froot = os.getcwd() + "\\tmp_data\\"

fdir = froot + fsubdir + "\\"
# fdir = os.path.join(froot,fsubdir) #platform-agnostic

evl = input ("Analyze all test items? (Y/N) : " )
if ("Y" in evl) or ("y" in evl):
    tms = [0,1,2,3,4,5,6,7,8,9,10]
    pass
else:
    print ("\033[93m  QC task list   \033[0m")
    print ("\033[96m 0: Initilization checkout (not selectable for itemized test item) \033[0m")
    print ("\033[96m 1: COLDATA basic functionality checkout  \033[0m")
    print ("\033[96m 2: COLDATA primary/secondary swap check  \033[0m")
    print ("\033[96m 3: COLDATA power consumption measurement  \033[0m")
    print ("\033[96m 4: COLDATA PLL lock range measurement  \033[0m")
    print ("\033[96m 5: COLDATA fast command verification  \033[0m")
    print ("\033[96m 6: COLDATA output link verification \033[0m")
    print ("\033[96m 7: COLDATA EFUSE burn-in \033[0m")

    while True:
        testnostr = input ("Please input a number (0, 1, 2, 3, 4, 5, 6, 7) for one test item: " )
        try:
            testno = int(testnostr)
            tms = [testno]
            break
        except ValueError:
            print ("Wrong value, please re-enter...")
def data_ana(fembs, rawdata, rms_flg=False):
    wibdata = wib_dec(rawdata,fembs, spy_num=1, cd0cd1sync=False)[0]
    datd = [wibdata[0], wibdata[1],wibdata[2],wibdata[3]][fembs[0]]

    chns =[]
    rmss = []
    peds = []
    pkps = []
    pkns = []
    wfs = []
    wfsf = []

    ppos0=0
    npos0=0
    ppos64=0
    npos64=0
    for achn in range(len(datd)):
        chndata = datd[achn]
        amax = np.max(chndata[300:-150])
        amin = np.min(chndata[300:-150])
        if achn==0:
            ppos0 = np.where(chndata[300:-150]==amax)[0][0] + 300
            npos0 = np.where(chndata[300:-150]==amin)[0][0] + 300
        if achn==64:
            ppos64 = np.where(chndata[300:-150]==amax)[0][0] + 300
            npos64 = np.where(chndata[300:-150]==amin)[0][0] + 300

        if rms_flg:
            arms = np.std(chndata)
            aped = int(np.mean(chndata))
        else:
            if achn <64:
                arms = np.std(chndata[ppos0-150:ppos0-50])
                aped = int(np.mean(chndata[ppos0-150:ppos0-50]))
                wfs.append(chndata[ppos0-50:ppos0+150])
                wfsf.append(chndata)
            else:
                arms = np.std(chndata[ppos64-150:ppos64-50])
                aped = int(np.mean(chndata[ppos64-150:ppos64-50]))
                wfs.append(chndata[ppos64-50:ppos64+150])
                wfsf.append(chndata)
        chns.append(achn)
        rmss.append(arms)
        peds.append(aped)
        pkps.append(amax)
        pkns.append(amin)
    return chns, rmss, peds, pkps, pkns, wfs,wfsf
    
def ana_res(fembs, rawdata, par=[7000,10000], rmsr=[5,25], pedr=[500,3000],rms_flg=False ):
    chns, rmss, peds, pkps, pkns, wfs, wfsf = data_ana(fembs, rawdata, rms_flg)
    show_flg=True
    amps = np.array(pkps) - np.array(peds)
    if all(item > par[0] for item in amps) and all(item < par[1] for item in amps) :
        if all(item > rmsr[0] for item in rmss) and all(item < rmsr[1] for item in rmss) :
            if all(item > pedr[0] for item in peds) and all(item < pedr[1] for item in peds) :
                show_flg = False
    return show_flg

#Todo change default V & C ranges
def ana_cdpwr(pwr_meas, vddfe = [1.7, 1.9], v1p1 = [1.0, 1.2], vddio = [2.15, 2.35], cdda = [8.5, 9.5], cddfe = [0, 0.1], cddcore = [9, 11], cddd = [21, 23], cddio = [66, 69]): #v2p5 = [2.4, 2.6], v1p2 = [1.1, 1.3], ca2p5=[15,25], cd1p2=[0,5], cio=[20,35], cd2p5 = [20,35]):
    kpwrs = list(pwr_meas.keys())

    
    vddas = []
    fe_vddas = []
    vddcores = []
    vddds = []
    vddios = []

    cddas = []
    fe_cddas = []
    cddcores = []
    cddds = []
    cddios = []
    
    for i in range(len(kpwrs)):      
        if "CD_VDDA" in kpwrs[i]:
            vddas.append(pwr_meas[kpwrs[i]][0])
            cddas.append(pwr_meas[kpwrs[i]][1])
        if "FE_VDDA" in kpwrs[i]:
            fe_vddas.append(pwr_meas[kpwrs[i]][0])
            fe_cddas.append(pwr_meas[kpwrs[i]][1]) 
        if "VDDCORE" in kpwrs[i]:
            vddcores.append(pwr_meas[kpwrs[i]][0])
            cddcores.append(pwr_meas[kpwrs[i]][1])
        if "VDDD" in kpwrs[i]:
            vddds.append(pwr_meas[kpwrs[i]][0])
            cddds.append(pwr_meas[kpwrs[i]][1])        
        if "VDDIO" in kpwrs[i]:
            vddios.append(pwr_meas[kpwrs[i]][0])
            cddios.append(pwr_meas[kpwrs[i]][1])
  
    show_flg=True
    if all(v1p1[0] <= item <= v1p1[1] for item in vddas) and all(cdda[0] <= item <= cdda[1] for item in cddas) :
        if all(vddfe[0] <= item <= vddfe[1] for item in fe_vddas) and all(cddfe[0] <= item <= cddfe[1] for item in fe_cddas) :
            if all(v1p1[0] <= item <= v1p1[1] for item in vddcores) and all(cddcore[0] <= item <= cddcore[1] for item in cddcores) :
                if all(v1p1[0] <= item <= v1p1[1] for item in vddds) and all(cddd[0] <= item <= cddd[1] for item in cddds) :
                    if all(vddio[0] <= item <= vddio[1] for item in vddios) and all(cddio[0] <= item <= cddio[1] for item in cddios) : 
                        show_flg = False
    return show_flg
    
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

def plt_cdpwr(plt, pwr_meas):
    kpwrs = list(pwr_meas.keys())
    ax5 = plt.subplot2grid((2, 1), (0, 0), colspan=1, rowspan=1)
    ax6 = plt.subplot2grid((2, 1), (1, 0), colspan=1, rowspan=1)

    vddas = []
    fe_vddas = []
    vddcores = []
    vddds = []
    vddios = []

    cddas = []
    fe_cddas = []
    cddcores = []
    cddds = []
    cddios = []
    
    for i in range(len(kpwrs)):      
        if "CD_VDDA" in kpwrs[i]:
            vddas.append(pwr_meas[kpwrs[i]][0])
            cddas.append(pwr_meas[kpwrs[i]][1])
        if "FE_VDDA" in kpwrs[i]:
            fe_vddas.append(pwr_meas[kpwrs[i]][0])
            fe_cddas.append(pwr_meas[kpwrs[i]][1]) 
        if "VDDCORE" in kpwrs[i]:
            vddcores.append(pwr_meas[kpwrs[i]][0])
            cddcores.append(pwr_meas[kpwrs[i]][1])
        if "VDDD" in kpwrs[i]:
            vddds.append(pwr_meas[kpwrs[i]][0])
            cddds.append(pwr_meas[kpwrs[i]][1])        
        if "VDDIO" in kpwrs[i]:
            vddios.append(pwr_meas[kpwrs[i]][0])
            cddios.append(pwr_meas[kpwrs[i]][1]) 

    # adc=[0,1,2,3,4,5,6,7]
    cd=[0,1]
    import matplotlib.ticker as ticker
    
    ax5.scatter(cd, vddas, color='b', marker = 'o', label="CD_VDDA")
    ax5.scatter(cd, fe_vddas, color='r', marker = 'o', label="FE_VDDA")
    ax5.scatter(cd, vddcores, color='g', marker = 'o', label="VDDCORE")
    ax5.scatter(cd, vddds, color='c', marker = 'o', label="VDDD")
    ax5.scatter(cd, vddios, color='m', marker = 'o', label="VDDIO")
    ax5.set_title("Voltage Measurement", fontsize=8)
    ax5.get_xaxis().set_major_locator(ticker.MultipleLocator(1))
    ax5.set_ylabel("Voltage (V)", fontsize=8)
    ax5.set_xlim((-0.5,1.5))
    ax5.set_ylim((0,3))
    ax5.set_xlabel("CD no", fontsize=8)
    ax5.grid()
    ax5.legend()

    ax6.scatter(cd, cddas, color='b', marker = 'o', label='CD_VDDA')
    ax6.scatter(cd, fe_cddas, color='r', marker = 'o', label='FE_VDDA')
    ax6.scatter(cd, cddcores, color='g', marker = 'o', label='VDDCORE')
    ax6.scatter(cd, cddds, color='c', marker = 'o', label='VDDD')
    ax6.scatter(cd, cddios, color='m', marker = 'o', label='VDDIO') 
    ax6.get_xaxis().set_major_locator(ticker.MultipleLocator(1))
    ax6.set_title("Current Measurement", fontsize=8)
    ax6.set_ylabel("Current (mA)", fontsize=8)
    ax6.set_xlim((-0.5,1.5))
    ax6.set_ylim((-10,200))
    ax6.set_xlabel("CD no", fontsize=8)
    ax6.legend()
    ax6.grid()
    
def plt_subplot(plt, fembs, rawdata ):
    ax1 = plt.subplot2grid((2, 2), (0, 0), colspan=1, rowspan=1)
    ax2 = plt.subplot2grid((2, 2), (0, 1), colspan=1, rowspan=1)
    ax3 = plt.subplot2grid((2, 2), (1, 0), colspan=1, rowspan=1)
    ax4 = plt.subplot2grid((2, 2), (1, 1), colspan=1, rowspan=1)

    chns, rmss, peds, pkps, pkns, wfs, wfsf = data_ana(fembs, rawdata)



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
        ax2.plot(wfsf[chn], color="C%d"%(chn//64+1))
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
    ax3.set_ylabel("Amplitude", fontsize=8)
    ax3.set_xlabel("CH number", fontsize=8)

    ax4.plot(chns,rmss, color='r', marker='.')
    ax4.set_title("Noise", fontsize=8)
    ax4.set_ylabel("ADC / bit", fontsize=8)
    ax4.set_xlabel("CH number", fontsize=8)
    ax1.grid()
    ax2.grid()

def plt_compare_wfs(plt, fembs, rawdata1, rawdata2):
    ax1 = plt.subplot2grid((1, 2), (0, 0), colspan=1, rowspan=1)
    ax2 = plt.subplot2grid((1, 2), (0, 1), colspan=1, rowspan=1)
    
    chns, rmss, peds, pkps, pkns, wfs, wfsf = data_ana(fembs, rawdata1)
    for chn in chns:
        ax1.plot(wfsf[chn], color="C%d"%(chn//64+1))
    chns, rmss, peds, pkps, pkns, wfs, wfsf = data_ana(fembs, rawdata2)    
    for chn in chns:
        ax2.plot(wfsf[chn], color="C%d"%(chn//64+1))
    ax1.set_title("Overlap waveforms", fontsize=8)
    ax1.set_ylabel("Amplitude", fontsize=8)
    ax1.set_xlabel("Time", fontsize=8)
    ax2.set_title("Overlap waveforms", fontsize=8)
    ax2.set_ylabel("Amplitude", fontsize=8)
    ax2.set_xlabel("Time", fontsize=8)    

def largest_true_range(arr): #written by chatgpt
    max_length = 0
    current_length = 0
    start_index = -1
    best_start_index = -1

    for i, value in enumerate(arr):
        if value:
            if current_length == 0:
                start_index = i
            current_length += 1
        else:
            if current_length > max_length:
                max_length = current_length
                best_start_index = start_index
            current_length = 0

    # Check the last range
    if current_length > max_length:
        max_length = current_length
        best_start_index = start_index

    if max_length > 0:
        return (best_start_index, best_start_index + max_length - 1)
    else:
        return None
    
if 0 in tms:
    print ("-------------------------------------------------------------------------")
    print ("0: Initilization checkout")
    #fp = fdir + "QC_INIT_CHK" + ".bin"
    fp = os.path.join(fdir,"QC_INIT_CHK"+".bin")
    
    with open(fp, 'rb') as fn:
        data = pickle.load( fn)
        
    dkeys = list(data.keys())
    
    logsd = data["logs"]
    dkeys.remove("logs")
    
    
    for onekey in dkeys:
        if ("DIRECT_PLS_CHK" in onekey) or ("ASICDAC_CALI_CHK" in onekey) :
            cfgdata = data[onekey]
            fembs = cfgdata[0]
            rawdata = cfgdata[1]
            cfg_info = cfgdata[2]

            show_flg=True
            if ("DIRECT_PLS_CHK" in onekey) :
                show_flg = ana_res(fembs, rawdata, par=[9000,16000], rmsr=[5,25], pedr=[300,3000] )
            if ("ASICDAC_CALI_CHK" in onekey):
                show_flg = ana_res(fembs, rawdata, par=[7000,10000], rmsr=[5,25], pedr=[300,3000] )
            #show_flg=True#
            if show_flg:
                print (onekey + "  : Fail")
                print ("command on WIB terminal to retake data for this test item is as below :")
                print ("When it is done, replace {} on the local PC".format(fp) )

                import matplotlib.pyplot as plt
                fig = plt.figure(figsize=(8,6))
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
    print ("-------------------------------------------------------------------------")
    print ("1: COLDATA basic functionality checkout  ")
    print ("command on WIB terminal to retake data for this test item is as bellow :")
    fp = fdir + "QC_BASIC_FUNC" + ".bin"
    print ("When it is done, replace {} on the local PC".format(fp) )
    if os.path.isfile(fp):
        with open(fp, 'rb') as fn:
            data = pickle.load( fn)
    
        dkeys = list(data.keys())
        
        logsd = data["logs"]
        dkeys.remove("logs")
    else:
        print(Fore.RED + fp + " not found.")
        exit()
        
    #print(dkeys)
    for onekey in dkeys:
        if "Reset" in onekey:
            rstdata = data[onekey]
            hasError = rstdata[1]
            if hasError:
                print(Fore.RED + onekey + " check Fail")
                print("Power info:")
                print(rstdata[2])
                
            else:
                print(onekey + " check PASS")
        elif "GPIO" in onekey:
            gpiodata = data[onekey]
            
            print(onekey + ": ",end="")
            if "PASS" not in gpiodata[1]:
                print(Fore.RED + gpiodata[1])
                cd = gpiodata[2]
                for pair in cd:
                    print("Wrote "+hex(pair[0])+", read "+hex(pair[1]))
            else:
                print(gpiodata[1])
        elif "SPI_config" in onekey:
            spi_pass = data[onekey]
            if spi_pass:
                print(onekey+" completed. PASS")
            else:
                print(Fore.RED+onekey+" Failed")
    print ("#########################################################################")    
    
if 2 in tms:
    print ("-------------------------------------------------------------------------")
    print ("2: COLDATA primary/secondary swap check  ")
    print ("command on WIB terminal to retake data for this test item is as bellow :")
    fp = fdir + "QC_SWAP" + ".bin"
    print ("When it is done, replace {} on the local PC".format(fp) )
    if os.path.isfile(fp):
        with open(fp, 'rb') as fn:
            data = pickle.load( fn)
    
        dkeys = list(data.keys())
        
        logsd = data["logs"]
        dkeys.remove("logs")
    else:
        print(Fore.RED + fp + " not found.")
        exit()
        
    #print(dkeys)    
    for onekey in dkeys:
        if "LVDS" in onekey or "CMOS" in onekey:
            i2cerror = data[onekey]
            if i2cerror:
                print(Fore.RED + onekey + " path config Fail")
            else:
                print(onekey + " path config PASS")
        elif "ADCs" in onekey:
            i2cerror = data[onekey]
            if i2cerror:
                print(Fore.RED + onekey + " path config Fail")            
            else:
                print(onekey + " path config PASS")
        elif "Data" in onekey:
            cfgdata = data[onekey]
            fembs = cfgdata[0]
            rawdata = cfgdata[1]

            show_flg=True
            if show_flg:
                print (onekey + "  : Fail")
                print ("command on WIB terminal to retake data for this test item is as below :")
                print ("When it is done, replace {} on the local PC".format(fp) )

                import matplotlib.pyplot as plt
                fig = plt.figure(figsize=(8,6))
                plt.rcParams.update({'font.size': 8})
                plt_log(plt,logsd, onekey)
                plt_subplot(plt, fembs, rawdata)
                plt.tight_layout( rect=[0.05, 0.05, 0.95, 0.95])
                plt.plot()
                plt.show()
                plt.close()
            else:
                print (onekey + "  : PASS")

#            rawdata = data[onekey][1]
#            fembs = data[onekey][0]
#            wibdata = wib_dec(rawdata,fembs, spy_num=1, cd0cd1sync=False)[0]
#            
#            pattern_ok = True
#            for ch, chdata in enumerate(wibdata[fembs[0]]):
#                if ch % 16 < 8:
#                    expected = 0x2af3
#                else:
#                    expected = 0x48d
#                
#                for snum, samp in enumerate(chdata):
#                    if samp != expected:
#                        print("Ch",ch,"sample",snum,"is",hex(samp),"- expected",hex(expected))
#                        pattern_ok = False
#            if pattern_ok:
#                print(onekey,"pattern data okay, PASS")
#            else:
#                print(Fore.RED+onekey+" pattern data incorrect. Fail")
    print ("#########################################################################")   
    
if 3 in tms:
    print ("-------------------------------------------------------------------------")
    print ("3: COLDATA power consumption measurement  ")
    print ("command on WIB terminal to retake data for this test item is as bellow :")
    fp = fdir + "QC_PWR_CYCLE" + ".bin"
    print ("When it is done, replace {} on the local PC".format(fp) )
    if os.path.isfile(fp):
        with open(fp, 'rb') as fn:
            data = pickle.load( fn)
    
        dkeys = list(data.keys())
        
        logsd = data["logs"]
        dkeys.remove("logs")
    else:
        print(Fore.RED + fp + " not found.")
        exit()
        
    # print(dkeys)
    
    for onekey in dkeys:
        cfgdata = data[onekey]
        fembs = cfgdata[0]
        # rawdata = cfgdata[1]
        cfg_info = cfgdata[1]
        # pwr_meas = cfgdata[3]
        pwr_meas = cfgdata[2] 
        if "BAND" in onekey: 
            if "0x20" in onekey:
                show_flag = ana_cdpwr(pwr_meas, vddfe = [1.7, 1.9], v1p1 = [1.0, 1.2], vddio = [2.15, 2.35], cdda = [8.5, 9.5], cddfe = [0, 0.1], cddcore = [9, 11], cddd = [21, 23], cddio = [66, 69])
            elif "0x25" in onekey:
                show_flag = ana_cdpwr(pwr_meas, vddfe = [1.7, 1.9], v1p1 = [1.0, 1.2], vddio = [2.15, 2.35], cdda = [8.5, 9.5], cddfe = [0, 0.1], cddcore = [9, 11], cddd = [21, 23], cddio = [66, 69])
            elif "0x26" in onekey:
                show_flag = ana_cdpwr(pwr_meas, vddfe = [1.7, 1.9], v1p1 = [1.0, 1.2], vddio = [2.15, 2.35], cdda = [8.5, 9.5], cddfe = [0, 0.1], cddcore = [9, 11], cddd = [21, 23], cddio = [66, 69])
        if "LVDS_CUR" in onekey: 
            if "0x0" in onekey:
                show_flag = ana_cdpwr(pwr_meas, vddfe = [1.7, 1.9], v1p1 = [1.0, 1.2], vddio = [2.15, 2.35], cdda = [8.5, 9.5], cddfe = [0, 0.1], cddcore = [9, 11], cddd = [21, 23], cddio = [66, 69])
            elif "0x2" in onekey:
                show_flag = ana_cdpwr(pwr_meas, vddfe = [1.7, 1.9], v1p1 = [1.0, 1.2], vddio = [2.15, 2.35], cdda = [8.5, 9.5], cddfe = [0, 0.1], cddcore = [9, 11], cddd = [21, 23], cddio = [66, 69])
            elif "0x7" in onekey:
                show_flag = ana_cdpwr(pwr_meas, vddfe = [1.7, 1.9], v1p1 = [1.0, 1.2], vddio = [2.15, 2.35], cdda = [8.5, 9.5], cddfe = [0, 0.1], cddcore = [9, 11], cddd = [21, 23], cddio = [66, 69])       
        if show_flag:
            print (onekey)
            import matplotlib.pyplot as plt
            fig = plt.figure(figsize=(6,6))
            plt.rcParams.update({'font.size': 8})
            cfgdata = data[onekey]
            fembs = cfgdata[0]
            # rawdata = cfgdata[1]
            cfg_info = cfgdata[1]
            pwr_meas = cfgdata[2]
            plt_log(plt,logsd, onekey)
            plt_cdpwr(plt, pwr_meas)
            # plt_subplot(plt, fembs, rawdata)
            plt.tight_layout( rect=[0.05, 0.05, 0.95, 0.95])
            plt.plot()
            plt.show()
    print ("#########################################################################")   
    
if 4 in tms:
    print ("-------------------------------------------------------------------------")
    print ("4: COLDATA PLL lock range measurement  ")
    print ("command on WIB terminal to retake data for this test item is as bellow :")
    fp = fdir + "QC_LOCK" + ".bin"
    print ("When it is done, replace {} on the local PC".format(fp) )
    if os.path.isfile(fp):
        with open(fp, 'rb') as fn:
            data = pickle.load( fn)
    
        dkeys = list(data.keys())
        
        logsd = data["logs"]
        dkeys.remove("logs")
    else:
        print(Fore.RED + fp + " not found.")
        exit()
        
    #print(dkeys)
    
    lowers = []
    highers = [] 
    outliers = []
    
    ts_outliers = []
    for onekey in dkeys:
        if "locked" in onekey:
            cd_locked = data[onekey]
            
            cd_outliers = []                              
            lower_rng, higher_rng = largest_true_range(cd_locked)
            lower_rng = lower_rng + 0x1a
            higher_rng = higher_rng + 0x1a
            print(onekey,": from",hex(lower_rng),"to",hex(higher_rng))
            lowers.append(lower_rng)
            highers.append(higher_rng)
            
            for i, lock in enumerate(cd_locked):
                if lock and (((i+0x1a) < lower_rng) or ((i+0x1a) > higher_rng)):
                    cd_outliers.append(i + 0x1a)
            outliers.append(cd_outliers)
            if len(cd_outliers) > 0:
                print("outliers: ",[hex(out) for out in cd_outliers])
                print('')
        if "data" in onekey:
            cds_data = data[onekey]
            
            cd_outliers = []
            ts_lower_rng, ts_higher_rng = largest_true_range(cds_data) #Contains data if synced, False if not synced
            ts_lower_rng = ts_lower_rng + 0x1a
            ts_higher_rng = ts_higher_rng + 0x1a
            print(onekey,": synced from",hex(ts_lower_rng),"to",hex(ts_higher_rng))
            
            for i, synced in enumerate(cds_data):
                if synced and (((i+0x1a) < ts_lower_rng) or ((i+0x1a) > ts_higher_rng)):
                    ts_outliers.append(i + 0x1a)
            if len(ts_outliers) > 0:
                print("outliers: ",[hex(out) for out in ts_outliers])
                print('')            
            
    if True:
        import matplotlib.pyplot as plt
        import matplotlib.ticker as ticker
        def to_hex(x, pos):
            return '0x%x' % int(x)

        fmt = ticker.FuncFormatter(to_hex)
        cds = [0,1]
        range_sizes = [h - l for h,l in zip(highers,lowers)]
        axes = plt.gca()
        rect = plt.bar(cds, range_sizes, bottom=lowers, width=0.25, color='blue')
        rect2 = axes.bar(0.5, ts_higher_rng-ts_lower_rng, bottom=ts_lower_rng, width=0.25, color='green', label='Data synchronization between CDs')        
        for cd in cds:
            if len(outliers[cd]) > 0:
                for outlier in outliers[cd]:
                    axes.scatter(cd,outlier,color='blue')
                    axes.annotate(hex(outlier),(cd,outlier))
        if len(ts_outliers) > 0:
            for outlier in ts_outliers:
                axes.scatter(0.5,outlier,color='green')
                axes.annotate(hex(outlier),(0.5,outlier))            
        axes.set_xlim([-0.5,1.5])
        axes.set_ylim([0x1a,0x3f])
        axes.get_xaxis().set_major_locator(ticker.MultipleLocator(1))
        axes.get_yaxis().set_major_formatter(fmt)
        plt.xlabel('COLDATA #')
        plt.ylabel('CONFIG_PLL_BAND (0x41) register value')
        plt.legend()
        plt.title('COLDATA PLL locking range')
        # height = rect.get_height()
        # plt.text(rect.get_x() + rect.get_width() / 2.0, height, f'{height:.0f}', ha='center', va='bottom')

        # rect.bar_label(ax.containers[0])
        plt.show()
        
        
        ##TODO determine acceptable locking range
    print ("#########################################################################")       
    
if 5 in tms:
    print ("-------------------------------------------------------------------------")
    print ("5: COLDATA fast command verification  ")
    print ("command on WIB terminal to retake data for this test item is as bellow :")
    fp = fdir + "QC_FASTCMD" + ".bin"
    print ("When it is done, replace {} on the local PC".format(fp) )
    if os.path.isfile(fp):
        with open(fp, 'rb') as fn:
            data = pickle.load( fn)
    
        dkeys = list(data.keys())
        
        logsd = data["logs"]
        dkeys.remove("logs")
    else:
        print(Fore.RED + fp + " not found.")
        exit()

    for onekey in dkeys:
        #if ("ASICDAC_CALI_CHK_Pre" in onekey) or ("ASICDAC_CALI_CHK_Post" in onekey)  :

        if ("ASICDAC_CALI" in onekey)  :
            cfgdata = data[onekey]
            fembs = cfgdata[0]
            rawdata = cfgdata[1]

            #show_flg = ana_res(fembs, rawdata, par=[9000,16000], rmsr=[5,25], pedr=[300,3000] )
            show_flg=True
            if show_flg:
                print (onekey + "  : Fail")
                print ("command on WIB terminal to retake data for this test item is as below :")
                print ("When it is done, replace {} on the local PC".format(fp) )

                import matplotlib.pyplot as plt
                fig = plt.figure(figsize=(8,6))
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

    exit()
        
    #print(dkeys)
    for onekey in dkeys:
        if "idle" in onekey:
            datad = data[onekey]
        if "edge_sync" in onekey:
            datad = data[onekey]
            if not datad['rawdata_after_dataalign']:
                print(Fore.RED + onekey + ': Data Failed to sync.')          
            elif datad['rawdata_before_dataalign']:
                print(Fore.RED + onekey + ': Data already synced before running data_align. Result inconclusive. Fail') #change?
            else:
                print(onekey+": PASS")
        if "edge_act" in onekey:
            hasERROR, adcbads = data[onekey]
            if hasERROR:
                print(Fore.RED + onekey + ': ADCs ' + str(adcbads)+ ' have non-default register values') 
            else:
                print(onekey+": PASS")
        if 'ACT_idle' in onekey:
            datad = data[onekey]
        # if "ACT_larasic_pls" in onekey: #checked already with ASICDAC_CALI_CHK
        if "ACT_save_timestamp" in onekey:
            datad = data[onekey]
            for key in ["0x2_timestamp", "0x3_timestamp"]:
                print(key+": "+str(datad[key]))
            cfgdata = datad['rawdata']
            fembs = cfgdata[0]
            rawdata = cfgdata[1]
            wibdata = wib_dec(rawdata,fembs, spy_num=1)
            cd_tmts =  wibdata[0][6]   
            print("Spy buffer timestamps:", cd_tmts)#,hex(cd_tmts))
            #Spybuf_trig seems to take too long to run to compare cd_tmts with saved timestamps
        if "ACT_save_status" in onekey:
            datad = data[onekey]
            
            reg23_0x2 = datad["0x2_regs"][0] #reg 24 (larasic status bits) already checked by dat_asic_chk
            reg23_0x3 = datad["0x3_regs"][0]
            
            #status_Heartbeat (bit 0) – Should always be a zero if the FastCommand Serial Interface is working properly.
            if reg23_0x3 & 0x1 != 0:
                print(Fore.RED + onekey + ": status_Heartbeat register bit is not 0 for CD address 0x3. Fail")
            # elif reg23_0x3 & 0x2 != 0:  
                # print(Fore.RED + onekey + ": status_Heartbeat_perpetual register bit is not 0 for CD address 0x3.") #acceptable?
            else:
                print(onekey,"0x3 heartbeat pass")
                
            if reg23_0x2 & 0x1 != 0:
                print(Fore.RED + onekey + ": status_Heartbeat register bit is not 0 for CD address 0x2. Fail")
            # elif reg23_0x2 & 0x2 != 0:  
                # print(Fore.RED + onekey + ": status_Heartbeat_perpetual register bit is not 0 for CD address 0x2.") #acceptable?        
            else:
                print(onekey,"0x2 heartbeat pass")            
            
            #status_Heartbeat_perpetual (bit 1) – if Status_Heartbeat was ever a 1, status_Heartbeat_perpetual will remain a 1 until (reset or clear)
            print("Status_heartbeat_perpetual 0x3:",hex((reg23_0x3 & 0x2)>>1))
            print("Status_heartbeat_perpetual 0x2:",hex((reg23_0x2 & 0x2)>>1))
            
            #Check Interface_LOCK (bit 6)
            cd0_locked, cd1_locked, cd_sel = datad["CD_LOCK"]
            #If cd_sel = 0, CD0 has 0x3 addr
            if cd_sel == 0:
                cd0_lock_reg = (reg23_0x3 >> 6) & 0x1
                cd1_lock_reg = (reg23_0x2 >> 6) & 0x1               
            else:
                cd0_lock_reg = (reg23_0x2 >> 6) & 0x1
                cd1_lock_reg = (reg23_0x3 >> 6) & 0x1                
            if cd0_lock_reg != cd0_locked:
                print(Fore.RED + onekey + ": CD1 INTERFACE_LOCK register bit does not match CD0_LOCK pad. Fail")
            else:
                print(onekey+" CD1 lock: PASS")
            if cd1_lock_reg != cd1_locked:
                print(Fore.RED + onekey + ": CD2 INTERFACE_LOCK register bit does not match CD1_LOCK pad. Fail")        
            else:
                print(onekey+" CD2 lock: PASS")
                
            #Check CORE_RUN bit 7
            core_run_0x3 = (reg23_0x3 >> 7) & 0x1
            core_run_0x2 = (reg23_0x2 >> 7) & 0x1
            print("CORE_RUN:", hex(core_run_0x3), hex(core_run_0x2)) #acceptable?
        if "ACT_clr_saves" in onekey:
            datad = data[onekey]
            datadkeys = list(datad.keys())
            for regkey in datadkeys:
                regs = datad[regkey]
                if not all(reg == 0x0 for reg in regs):
                    print(Fore.RED + onekey + ": " + regkey + ": registers not successfully cleared. Fail")
                else:
                    print(onekey,regkey,"PASS")
        if "ACT_rst_adcs" in onekey:
            hasERROR, adcbads = data[onekey]
            if hasERROR:
                print(Fore.RED + onekey + ': ADCs ' + str(adcbads)+ ' have non-default register values. Fail')      
            else:
                print(onekey+": PASS")
        if "ACT_rst_larasic" in onekey: #ACT_rst_larasics & ACT_rst_larasic_spi 
            datad = data[onekey]
            vbgrs_before = datad["VBGR_before"] 
            vbgrs_after = datad["VBGR_after"]             
            vbgr_avgs_bf = []
            vbgr_avgs_af = []
            for fe in range(8):
                mon_paras = vbgrs_before[fe]
                #print(mon_paras)
                femb_id = mon_paras[8][0]
                samples = mon_paras[6]
                adcss = mon_paras[7]
                fe_vbgrs = []
                for samp in range(samples):
                    fe_vbgrs.append(adcss[samp][femb_id])
                vbgr_avgs_bf.append(sum(fe_vbgrs) / samples)
                
                mon_paras = vbgrs_after[fe]
                #print(mon_paras)
                femb_id = mon_paras[8][0]
                samples = mon_paras[6]
                adcss = mon_paras[7]
                fe_vbgrs = []
                for samp in range(samples):
                    fe_vbgrs.append(adcss[samp][femb_id])
                vbgr_avgs_af.append(sum(fe_vbgrs) / samples)                
            print(onekey,": LArASIC avg VBGR readings before reset:",vbgr_avgs_bf)
            print(onekey,": LArASIC avg VBGR readings after reset:",vbgr_avgs_af)
            #Add determination that VBGR no longer within range
            
            rawdata_before = datad["rawdata_before"]
            rawdata_after = datad["rawdata_after"]
            #Add pulse detection?
            if True:
                import matplotlib.pyplot as plt
                fig = plt.figure(figsize=(9,6))
                plt.rcParams.update({'font.size': 8})      
                plt_compare_wfs(plt, fembs, rawdata_before, rawdata_after)
                plt.suptitle("LArASIC output waveforms before and after "+onekey+" reset")
                plt.show()
        if "ACT_prm_larasics" in onekey:
            program_success = data[onekey]           
            if not program_success:  
                print(Fore.RED + onekey + ": LArASIC programming unsuccessful. Fail")
            else:
                print(onekey+": PASS")
    print ("#########################################################################")           

if 6 in tms:
    print ("-------------------------------------------------------------------------")
    print ("6: COLDATA output link verification  ")
    print ("command on WIB terminal to retake data for this test item is as bellow :")
    fp = fdir + "QC_LVDS_Curs" + ".bin"
    print ("When it is done, replace {} on the local PC".format(fp) )
    if os.path.isfile(fp):
        with open(fp, 'rb') as fn:
            data = pickle.load( fn)
    
        dkeys = list(data.keys())
        
        logsd = data["logs"]
        dkeys.remove("logs")
    else:
        print(Fore.RED + fp + " not found.")
        exit()


    for onekey in dkeys:
        #if ("ASICDAC_CALI_CHK_Pre" in onekey) or ("ASICDAC_CALI_CHK_Post" in onekey)  :
        if ("LVDS" in onekey)  :
            print (onekey)
            cfgdata = data[onekey]
            fembs = cfgdata[0]
            rawdata = cfgdata[1]

            #show_flg = ana_res(fembs, rawdata, par=[9000,16000], rmsr=[5,25], pedr=[300,3000] )
            show_flg=True
            if show_flg:
                print (onekey + "  : Fail")
                print ("command on WIB terminal to retake data for this test item is as below :")
                print ("When it is done, replace {} on the local PC".format(fp) )

                import matplotlib.pyplot as plt
                fig = plt.figure(figsize=(8,6))
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

if 6 in tms:
    print ("-------------------------------------------------------------------------")
    print ("6: COLDATA output link verification  ")
    print ("command on WIB terminal to retake data for this test item is as bellow :")
    fp = fdir + "QC_OUTPUT" + ".bin"
    print ("When it is done, replace {} on the local PC".format(fp) )
    if os.path.isfile(fp):
        with open(fp, 'rb') as fn:
            data = pickle.load( fn)
    
        dkeys = list(data.keys())
        
        logsd = data["logs"]
        dkeys.remove("logs")
    else:
        print(Fore.RED + fp + " not found.")
        exit()
        
    #print(dkeys)
    for onekey in dkeys:
        if 'LArASIC_pulse' in onekey:  
                for current in range(0x8):
                
                    cfgdata = data[onekey][current]
                    fembs = cfgdata[0]
                    rawdata = cfgdata[1]
                    cfg_info = cfgdata[2]       
                    #only presence of pulses matters, not noise                    
                    #show_flg = ana_res(fembs, rawdata, par=[7000,10000], rmsr=[5,25], pedr=[300,3000] )
                    show_flg = ana_res(fembs, rawdata, par=[7000,10000], rmsr=[0,100], pedr=[300,3000] ) 
                    #show_flg=True#
                    if show_flg:
                        print (Fore.RED + onekey + " LVDS current " + hex(current) + "  : Fail")
                        # print ("command on WIB terminal to retake data for this test item is as below :")
                        # print ("When it is done, replace {} on the local PC".format(fp) )

                        import matplotlib.pyplot as plt
                        fig = plt.figure(figsize=(9,6))
                        plt.rcParams.update({'font.size': 8})
                        plt_log(plt,logsd, onekey + " LVDS current " + hex(current))
                        plt_subplot(plt, fembs, rawdata)
                        plt.tight_layout( rect=[0.05, 0.05, 0.95, 0.95])
                        plt.plot()
                        plt.show()
                        plt.close()
                    else:
                        print (onekey + " LVDS current " + hex(current) + ": PASS")
        elif 'ADC_pattern' in onekey:
            for current in range(0x8):
                rawdata = data[onekey][current][1]
                fembs = data[onekey][current][0]
                wibdata = wib_dec(rawdata,fembs, spy_num=1, cd0cd1sync=False)[0]
                
                pattern_ok = True
                for ch, chdata in enumerate(wibdata[fembs[0]]):
                    if ch % 16 < 8:
                        expected = 0x2af3
                    else:
                        expected = 0x48d
                    
                    for snum, samp in enumerate(chdata):
                        if samp != expected:
                            print("Ch",ch,"sample",snum,"is",hex(samp),"- expected",hex(expected))
                            pattern_ok = False
                if pattern_ok:
                    print(onekey,"LVDS current",hex(current),"pattern data okay: PASS")
                else:
                    print(Fore.RED+onekey+" LVDS pattern data: Fail")
    print ("#########################################################################")         
            
if 7 in tms:
    print ("-------------------------------------------------------------------------")
    print ("7: COLDATA EFUSE burn-in  ")
    print ("command on WIB terminal to retake data for this test item is as bellow :")
    fp = fdir + "QC_EFUSE" + ".bin"
    print ("When it is done, replace {} on the local PC".format(fp) )
    if os.path.isfile(fp):
        with open(fp, 'rb') as fn:
            data = pickle.load( fn)
    
        dkeys = list(data.keys())
        
        logsd = data["logs"]
        dkeys.remove("logs")
    else:
        print(Fore.RED + fp + " not found.")
        exit()
        
    #print(dkeys)
    for onekey in dkeys:
        if "CD" in onekey:
            efusedata = data[onekey]
            val = efusedata[0]
            readout = efusedata[1]
            print(onekey,"programmed with",hex(val),", reads out",hex(readout))
            if (readout & 0x7fffffff) == val: 
                print(onekey+": PASS")
            else:
                print(Fore.RED + onekey+": Fail")
    print ("#########################################################################")     
    
