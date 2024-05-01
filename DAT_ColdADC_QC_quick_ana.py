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

fsubdir = "ADC_000000001_000000002_000000003_000000004_000000005_000000006_000000007_000000008"
#fsubdir = "FE_003000001_003000002_003000003_003000004_003000005_003000006_003000007_003000008"
froot = os.getcwd() + "\\tmp_data\\"

fdir = froot + fsubdir + "\\"
# fdir = os.path.join(froot,fsubdir) #platform-agnostic

evl = input ("Analyze all test items? (Y/N) : " )
if ("Y" in evl) or ("y" in evl):
    tms = [0,1,2,3,4,5,6,7,8,9,10]
    pass
else:
    print ("\033[93m  QC task list   \033[0m")
    print ("\033[96m 0: Initilization checkout  \033[0m")
    print ("\033[96m 1: ADC power cycling measurement  \033[0m")
    print ("\033[96m 2: ADC I2C communication checkout  \033[0m")
    print ("\033[96m 3: ADC reference voltage measurement  \033[0m")
    print ("\033[96m 4: ADC autocalibration check  \033[0m")
    print ("\033[96m 5: ADC noise measurement  \033[0m")
    print ("\033[96m 6: ADC DNL/INL measurement  \033[0m")
    print ("\033[96m 7: ADC overflow check  \033[0m")
    print ("\033[96m 8: ADC ENOB measurement \033[0m")
    print ("\033[96m 9: ADC ring oscillator frequency readout \033[0m")

    while True:
        testnostr = input ("Please input a number (0, 1, 2, 3, 4, 5, 6, 7, 8, 9) for one test item: " )
        try:
            testno = int(testnostr)
            tms = [testno]
            break
        except ValueError:
            print ("Wrong value, please re-enter...")
            
#functions

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
        
#Todo replace default V & C ranges:    
def ana_adcpwr(pwr_meas, v2p5 = [2.4, 2.6], v1p2 = [1.1, 1.3], ca2p5=[15,25], cd1p2=[0,5], cio=[20,35], cd2p5 = [20,35]):
    kpwrs = list(pwr_meas.keys())

    vdda2p5s = []
    vddd1p2s = []
    vddios = []
    vddd2p5s = []
    
    cdda2p5s = []
    cddd1p2s = []
    cddios = []
    cddd2p5s = []

    for i in range(len(kpwrs)):
        if "VDDA2P5" in kpwrs[i]:
            vdda2p5s.append(pwr_meas[kpwrs[i]][0])
            cdda2p5s.append(pwr_meas[kpwrs[i]][1])
        if "VDDD1P2" in kpwrs[i]:
            vddd1p2s.append(pwr_meas[kpwrs[i]][0])
            cddd1p2s.append(pwr_meas[kpwrs[i]][1])
        if "VDDIO" in kpwrs[i]:
            vddios.append(pwr_meas[kpwrs[i]][0])
            cddios.append(pwr_meas[kpwrs[i]][1])
        if "VDDD2P5" in kpwrs[i]:
            vddd2p5s.append(pwr_meas[kpwrs[i]][0])
            cddd2p5s.append(pwr_meas[kpwrs[i]][1])        
    
    show_flg=True
    if all(v2p5[0] <= item <= v2p5[1] for item in vdda2p5s) and all(ca2p5[0] <= item <= ca2p5[1] for item in cdda2p5s) :
        if all(v1p2[0] <= item <= v1p2[1] for item in vddd1p2s) and all(cd1p2[0] <= item <= cd1p2[1] for item in cddd1p2s) :
            if all(v2p5[0] <= item >= v2p5[1] for item in vddios) and all(cio[0] <= item <= cio[1] for item in cddios) :
                if all(v2p5[0] <= item <= v2p5[1] for item in vddd2p5s) and all(cd2p5[0] <= item <= cd2p5[1] for item in cddd2p5s) :
                    # if all(item >= cddp[0] for item in cddps) and all(item <= cddp[1] for item in cddps) :
                        # if all(item >= cddo[0] for item in cddos) and all(item <= cddo[1] for item in cddos) :
                    show_flg = False
    return show_flg

def plt_adcpwr(plt, pwr_meas):
    kpwrs = list(pwr_meas.keys())
    ax5 = plt.subplot2grid((2, 3), (0, 0), colspan=1, rowspan=1)
    ax6 = plt.subplot2grid((2, 3), (1, 0), colspan=1, rowspan=1)

    vdda2p5s = []
    vddd1p2s = []
    vddios = []
    vddd2p5s = []
    
    cdda2p5s = []
    cddd1p2s = []
    cddios = []
    cddd2p5s = []

    for i in range(len(kpwrs)):
        if "VDDA2P5" in kpwrs[i]:
            vdda2p5s.append(pwr_meas[kpwrs[i]][0])
            cdda2p5s.append(pwr_meas[kpwrs[i]][1])
        if "VDDD1P2" in kpwrs[i]:
            vddd1p2s.append(pwr_meas[kpwrs[i]][0])
            cddd1p2s.append(pwr_meas[kpwrs[i]][1])
        if "VDDIO" in kpwrs[i]:
            vddios.append(pwr_meas[kpwrs[i]][0])
            cddios.append(pwr_meas[kpwrs[i]][1])
        if "VDDD2P5" in kpwrs[i]:
            vddd2p5s.append(pwr_meas[kpwrs[i]][0])
            cddd2p5s.append(pwr_meas[kpwrs[i]][1]) 

    adc=[0,1,2,3,4,5,6,7]
    ax5.plot(adc, vdda2p5s, color='b', marker = 'o', label="VDDA2P5")
    ax5.plot(adc, vddd1p2s, color='r', marker = 'o', label="VDDD1P2")
    ax5.plot(adc, vddios, color='g', marker = 'o', label="VDDIO")
    ax5.plot(adc, vddd2p5s, color='c', marker = 'o', label="VDDD2P5")
    ax5.set_title("Voltage Measurement", fontsize=8)
    ax5.set_ylabel("Voltage / V", fontsize=8)
    ax5.set_ylim((0,3))
    ax5.set_xlabel("ADC no", fontsize=8)
    ax5.grid()
    ax5.legend()

    ax6.scatter(adc, cdda2p5s, color='b', marker = 'o', label='VDDA2P5')
    ax6.scatter(adc, cddd1p2s, color='r', marker = 'o', label='VDDD1P2')
    ax6.scatter(adc, cddios, color='g', marker = 'o', label='VDDIO')
    ax6.scatter(adc, cddd2p5s, color='c', marker = 'o', label='VDDD2P5')
    
    ax6.set_title("Current Measurement", fontsize=8)
    ax6.set_ylabel("Current / mA", fontsize=8)
    ax6.set_ylim((-10,200))
    ax6.set_xlabel("ADC no", fontsize=8)
    ax6.legend()
    ax6.grid()
    
def plt_subplot(plt, fembs, rawdata ):
    ax1 = plt.subplot2grid((2, 3), (0, 1), colspan=1, rowspan=1)
    ax2 = plt.subplot2grid((2, 3), (0, 2), colspan=1, rowspan=1)
    ax3 = plt.subplot2grid((2, 3), (1, 1), colspan=1, rowspan=1)
    ax4 = plt.subplot2grid((2, 3), (1, 2), colspan=1, rowspan=1)

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
    ax3.set_xlabel("Amplitude", fontsize=8)
    ax3.set_ylabel("CH number", fontsize=8)

    ax4.plot(chns,rmss, color='r', marker='.')
    ax4.set_title("Noise", fontsize=8)
    ax4.set_xlabel("ADC / bit", fontsize=8)
    ax4.set_ylabel("CH number", fontsize=8)
    ax1.grid()
    ax2.grid()
    
def adc_refv_chk(datad):
    dkeys = list(datad.keys())
    err_high = 1.15
    err_low = 0.85
    
    vrefp_nom = 1950 #mV
    vrefn_nom = 450 
    vcmi_nom = 900 
    vcmo_nom = 1200
    
    warn_flg = False
    for onekey in dkeys:
        if "MON_VREFP" in onekey:
            vnom = vrefp_nom
        elif "MON_VREFN" in onekey:
            vnom = vrefn_nom
        elif "MON_VCMI" in onekey:
            vnom = vcmi_nom
        elif "MON_VCMO" in onekey:
            vnom = vcmo_nom            
        if all(vnom*err_low < data < vnom*err_high for data in datad[onekey][1]): 
            pass
        else:
            print ("Warning: {} is out of range of {} mV: {}".format(onekey, vnom, datad[onekey][1]))
            warn_flg = True
    return warn_flg

def ana_adc_imon(data_imons):
    dkeys = list(data_imons.keys())
    err_high = 1.15
    err_low = 0.85    
    
    icmos_ref_nom = 200 #mA
    isha0_nom = 80
    iadc0_nom = 60
    isha1_nom = 50
    iadc1_nom = 50
    ibuff_cmos_nom = 30
    iref_nom = 400
    iref_buffer0_nom = 300
    
    warn_flg = False
    for onekey in dkeys:
        if 'ICMOS_REF' in onekey:
            inom = icmos_ref_nom
        elif 'ISHA0' in onekey:
            inom = isha0_nom
        elif 'IADC0' in onekey:
            inom = iadc0_nom
        elif 'ISHA1' in onekey:
            inom = isha1_nom
        elif 'IADC1' in onekey:
            inom = iadc1_nom
        elif 'IBUFF(CMOS)' in onekey:
            inom = ibuff_cmos_nom
        elif 'IREF' in onekey:
            inom = iref_nom
        elif 'IREFBUFFER0' in onekey:
            inom = iref_buffer0_nom
        if all(inom*err_low < data < inom*err_high for data in data_imons[onekey][2]): 
            pass
        else:
            print ("Warning: {} is out of range of {} mA: {}".format(onekey, inom, data_imons[onekey][2]))
            warn_flg = True
    return warn_flg    

def ana_adc_weightchk(weights):
    default_weights = [[0xc000, 0x4000], [0xe000, 0x2000], [0xf000, 0x1000], [0xf800, 0x0800],
                        [0xfc00, 0x0400], [0xfe00, 0x0200], [0xff00, 0x0100], [0xff80, 0x0080],
                        [0xffc0, 0x0040], [0xffe0, 0x0020], [0xfff0, 0x0010], [0xfff8, 0x0008],
                        [0xfffc, 0x0004], [0xfffe, 0x0002], [0xffff, 0x0001], [0x0000, 0x0000]] #last pair are gain and offset
    err_high = 1.15
    err_low = 0.85 
    
    warn_flg = False
    for adc in range(2): #ADC0 or ADC1
        for wt in range(2): #W0 or W2
            for stage_num in range(16):   
                default_weight = default_weights[stage_num][wt] 
                if all (err_low*default_weight < weights[chip][adc][wt][stage_num] < err_high*default_weight for chip in range(8)):
                    pass
                else: 
                    print ("Warning: ADC%d stage %d W%d is out of range of 0x%x:"%(adc, stage_num, wt*2, default_weight), [hex(weights[chip][adc][wt][stage_num]) for chip in range(8)])
                    warn_flg = True
    return warn_flg 

def onpick(event): #For enob wf visibility toggling
    legend = event.artist
    isVisible = legend.get_visible()

    graphs[legend].set_visible(not isVisible)
    legend.set_visible(not isVisible)

    fig.canvas.draw()    


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
        #Add confirmation of power pass?
        if ("MON_VREFP" in onekey) or ("MON_VREFN" in onekey) or ("MON_VCMI" in onekey) or ("MON_VCMO" in onekey):            
            print(onekey + " : " + data[onekey][2])
        if ("DIRECT_PLS_CHK" in onekey) or ("ASICDAC_CALI_CHK" in onekey):
            cfgdata = data[onekey]
            fembs = cfgdata[0]
            rawdata = cfgdata[1]
            cfg_info = cfgdata[2]

            show_flg=True
            if ("DIRECT_PLS_CHK" in onekey) :
                show_flg = ana_res(fembs, rawdata, par=[9000,16000], rmsr=[5,25], pedr=[300,3000] )
            if ("ASICDAC_CALI_CHK" in onekey):
                show_flg = ana_res(fembs, rawdata, par=[7000,10000], rmsr=[5,25], pedr=[300,3000] )
            show_flg=True#
            if show_flg:
                print (onekey + "  : Fail")
                print ("command on WIB terminal to retake data for this test item is as below :")
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
    print ("-------------------------------------------------------------------------")
    print ("1: ADC power cycling measurement  ")
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
        rawdata = cfgdata[1]
        cfg_info = cfgdata[2]
        #pwr_meas = cfgdata[3]
        pwr_meas = cfgdata[4] #ADC

        show_flg=True
        #Todo replace V & C ranges: 
        if ("PwrCycle_0" in onekey) :
            show_flg = ana_adcpwr(pwr_meas, v2p5 = [2.4, 2.6], v1p2 = [1.1, 1.3], ca2p5=[15,25], cd1p2=[0,5], cio=[20,35], cd2p5 = [20,35])
            if not show_flg:
            # if True:
                show_flg = ana_res(fembs, rawdata, par=[3000,6000], rmsr=[5,30], pedr=[8000,10000] )
        if ("PwrCycle_1" in onekey) :
            show_flg = ana_adcpwr(pwr_meas, v2p5 = [2.4, 2.6], v1p2 = [1.1, 1.3], ca2p5=[15,25], cd1p2=[0,5], cio=[20,35], cd2p5 = [20,35])
            if not show_flg:
            # if True:
                show_flg = ana_res(fembs, rawdata, par=[3000,6000], rmsr=[5,30], pedr=[8000,10000] )
        if ("PwrCycle_2" in onekey) :
            show_flg = ana_adcpwr(pwr_meas, v2p5 = [2.4, 2.6], v1p2 = [1.1, 1.3], ca2p5=[15,25], cd1p2=[0,5], cio=[20,35], cd2p5 = [20,35])
            if not show_flg:
            # if True:
                show_flg = ana_res(fembs, rawdata, par=[3000,6000], rmsr=[5,30], pedr=[8000,10000] )
        if ("PwrCycle_3" in onekey) :
            show_flg = ana_adcpwr(pwr_meas, v2p5 = [2.4, 2.6], v1p2 = [1.1, 1.3], ca2p5=[15,25], cd1p2=[0,5], cio=[20,35], cd2p5 = [20,35])
            if not show_flg:
            # if True:
                show_flg = ana_res(fembs, rawdata, par=[3000,6000], rmsr=[5,30], pedr=[10000,12000] )
        if ("PwrCycle_4" in onekey) :
            show_flg = ana_adcpwr(pwr_meas, v2p5 = [2.4, 2.6], v1p2 = [1.1, 1.3], ca2p5=[15,25], cd1p2=[0,5], cio=[20,35], cd2p5 = [20,35])
            if not show_flg:
            # if True:
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
            pwr_meas = cfgdata[4]
            plt_log(plt,logsd, onekey)
            plt_adcpwr(plt, pwr_meas)
            plt_subplot(plt, fembs, rawdata)
            plt.tight_layout( rect=[0.05, 0.05, 0.95, 0.95])
            plt.plot()
            plt.show()
    #debugging:    
    #current_diffs = {}
    #pkeys = list(data['PwrCycle_0'][4].keys())
    #for onekey in pkeys:
    #    current_diffs[onekey+'PwrCycle_2_minus_PwrCycle_0'] = data['PwrCycle_2'][4][onekey][1] - data['PwrCycle_0'][4][onekey][1]
    #    current_diffs[onekey+'PwrCycle_3_minus_PwrCycle_0'] = data['PwrCycle_3'][4][onekey][1] - data['PwrCycle_0'][4][onekey][1]
    #print(current_diffs)    
    print ("#########################################################################")    
    
if 2 in tms:
    print ("-------------------------------------------------------------------------")
    #print ("2: ADC I2C communication checkout  ")
    #print ("command on WIB terminal to retake data for this test item is as bellow :")
    #fp = fdir + "QC_I2C_COMM" + ".bin"
    #print ("When it is done, replace {} on the local PC".format(fp) )
    #if os.path.isfile(fp):
    #    with open(fp, 'rb') as fn:
    #        data = pickle.load( fn)
    #
    #    dkeys = list(data.keys())
    #    
    #    logsd = data["logs"]
    #    dkeys.remove("logs")
    #else:
    #    print(Fore.RED + fp + " not found.")
    #    exit()
    #    
    #
    ## print(dkeys)
    #for onekey in dkeys:
    #    if "POR_CHKREG_FAIL" in dkeys:
    #        if data[onekey] is None: #pass
    #            print("\033[92mPOR register checkout passed.   \033[0m")
    #        else:
    #            print("\033[91mPOR register checkout failed.   \033[0m")
    #            print("Register printout:")
    #            reg_addr1=range(0x80,0xB3)
    #            reg_addr2=range(1,5)                     
    #            for adc_no in range(8):
    #                print("ADC 0")
    #                for i, reg_addr in enumerate(list(reg_addr1)):
    #                    print("Register 0x%x: 0x%x"%(reg_addr, data[onekey][adc_no][0][i]))
    #                for i, reg_addr in enumerate(list(reg_addr2)):
    #                    print("Register 0x%x: 0x%x"%(reg_addr, data[onekey][adc_no][1][i]))                   
                
if 3 in tms:
    print ("-------------------------------------------------------------------------")
    print ("3: ADC reference voltage measurement  ")
    print ("command on WIB terminal to retake data for this test item is as bellow :")
    fp = fdir + "QC_REFV" + ".bin"
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
        
    print(dkeys)    
    for onekey in dkeys:
        if ("MON_VREFP" in onekey) or ("MON_VREFN" in onekey) or ("MON_VCMI" in onekey) or ("MON_VCMO" in onekey):  
            if adc_refv_chk({onekey:data[onekey]}): #warn_flag == True
                print(Fore.RED+onekey+": FAIL")#,list(data[onekey][1]))
                # datad_mons[onekey].append("FAIL")
                # passf = False
            else:
                pass
                # datad_mons[onekey].append("PASS")
                print(onekey+": PASS")
        elif 'refv_dacs' in onekey:
            # dacs = [0, 0b1, 0b10, 0b11, 0b100, 0b111, 0b1000, 0b1111, 0b10000, 0b11111, 0b100000, 0b111111, 0b1000000, 0b1111111, 0b10000000, 0b11111111]
            dacs = [0, 0b1, 0b10, 0b11, 0b100, 0b111, 0b1000, 0b1111, 0b10000, 0b11111, 0b100000, 0b110000, 0b111111, 
                0b1000000, 0b1010000, 0b1100000, 0b1110000, 0b1111111, 
                0b10000000, 0b10010000, 0b10100000, 0b10110000, 0b11000000, 0b11010000, 0b11100000, 0b11110000, 0b11111111]            
            one_hots = [0b1, 0b10, 0b100, 0b1000, 0b10000, 0b100000, 0b1000000, 0b10000000]      
            vrefp_dacs = [[data['refv_dacs'][dac]['MON_VREFP'][1][adc] for dac in range(len(dacs))] for adc in range(8)]
            vrefn_dacs = [[data['refv_dacs'][dac]['MON_VREFN'][1][adc] for dac in range(len(dacs))] for adc in range(8)]
            vcmi_dacs = [[data['refv_dacs'][dac]['MON_VCMI'][1][adc] for dac in range(len(dacs))] for adc in range(8)]
            vcmo_dacs = [[data['refv_dacs'][dac]['MON_VCMO'][1][adc] for dac in range(len(dacs))] for adc in range(8)]
            
            #Formula from https://www.sjsu.edu/people/Tan.v.nguyen/L2_F17_Intro_Data%20Conversion.pptx
            #DNL(m) = (Vout(m) - Vout(m-1) - 1 LSB)/(1 LSB)
            #1 LSB = Vout(max) / 2^n = Voutmax / 256            
            adc_vrefp_dnls = []
            adc_vrefn_dnls = []
            adc_vcmi_dnls = []
            adc_vcmo_dnls = [] 

            adc_vrefp_inls = []
            adc_vrefn_inls = []
            adc_vcmi_inls = []
            adc_vcmo_inls = []             

            for adc in range(8):
                vrefp_dnls = []
                vrefn_dnls = []
                vcmi_dnls = []
                vcmo_dnls = []
                
                one_lsb_vrefp = (vrefp_dacs[adc][-1] - vrefp_dacs[adc][0]) / 255
                one_lsb_vrefn = (vrefn_dacs[adc][-1] - vrefn_dacs[adc][0]) / 255
                one_lsb_vcmi = (vcmi_dacs[adc][-1] - vcmi_dacs[adc][0]) / 255
                one_lsb_vcmo = (vcmo_dacs[adc][-1] - vcmo_dacs[adc][0]) / 255
                
                # one_lsb = data['refv_dacs'][-1]['MON_VREFP'][1][adc] - data['refv_dacs'][0]['MON_VREFP'][1][adc]
                debug = False
                for i, dac in enumerate(dacs[1:]):
                    if debug or dac in one_hots: #one hot concept does not apply in debug mode since we test all codes
                        # print("dac",hex(dac),"one hot",i,"major carry",i-1)
                        one_hot = vrefp_dacs[adc][i+1]
                        major_carry = vrefp_dacs[adc][i]
                        dnl = (one_hot - major_carry - one_lsb_vrefp) / one_lsb_vrefp
                        vrefp_dnls.append(dnl)
                        
                        one_hot = vrefn_dacs[adc][i+1]
                        major_carry = vrefn_dacs[adc][i]
                        dnl = (one_hot - major_carry - one_lsb_vrefn) / one_lsb_vrefn
                        vrefn_dnls.append(dnl) 

                        one_hot = vcmi_dacs[adc][i+1]
                        major_carry = vcmi_dacs[adc][i]
                        dnl = (one_hot - major_carry - one_lsb_vcmi) / one_lsb_vcmi
                        vcmi_dnls.append(dnl)
                        
                        one_hot = vcmo_dacs[adc][i+1]
                        major_carry = vcmo_dacs[adc][i]
                        dnl = (one_hot - major_carry - one_lsb_vcmo) / one_lsb_vcmo
                        vcmo_dnls.append(dnl)                          
                # one_lsb = 2218 / 16 # approximate. measure directly later              
                # # print(one_lsb)
                # for dac in range(1,int(0x100/0x10)): #skip 0
                    # dnl = (vrefp_dacs[adc][dac] - vrefp_dacs[adc][dac-1] - one_lsb) / one_lsb
                    # vrefp_dnls.append(dnl)
                                            
                adc_vrefp_dnls.append(vrefp_dnls)
                adc_vrefn_dnls.append(vrefn_dnls)  
                adc_vcmi_dnls.append(vcmi_dnls)
                adc_vcmo_dnls.append(vcmo_dnls)  
                
                #Calculate INL for all dac levels by superposition principle
                vrefp_inls = []
                vrefn_inls = []
                vcmi_inls = []
                vcmo_inls = [] 
                
                #for debug:
                debug = False
                vrefp_inl_total = 0
                vrefn_inl_total = 0
                vcmi_inl_total = 0
                vcmo_inl_total = 0
                for dac_count in range(0x1,0x100):
                    if debug:
                        vrefp_inl_total = vrefp_inl_total + vrefp_dnls[dac_count-1] #list starts with DNL[1]
                        vrefp_inls.append(copy.copy(vrefp_inl_total))
                        vrefn_inl_total = vrefn_inl_total + vrefn_dnls[dac_count-1] #list starts with DNL[1]
                        vrefn_inls.append(copy.copy(vrefn_inl_total))
                        vcmi_inl_total = vcmi_inl_total + vcmi_dnls[dac_count-1] #list starts with DNL[1]
                        vcmi_inls.append(copy.copy(vcmi_inl_total))
                        vcmo_inl_total = vcmo_inl_total + vcmo_dnls[dac_count-1] #list starts with DNL[1]
                        vcmo_inls.append(copy.copy(vcmo_inl_total))                        
                    else:                    
                        p_inl, n_inl, i_inl, o_inl = 0, 0, 0, 0
                        for i, one_hot in enumerate(one_hots):                       
                            if dac_count & one_hot > 0:
                                p_inl = p_inl + vrefp_dnls[i]
                                n_inl = n_inl + vrefn_dnls[i]
                                i_inl = i_inl + vcmi_dnls[i]
                                o_inl = o_inl + vcmo_dnls[i]                            
                        vrefp_inls.append(p_inl)
                        vrefn_inls.append(n_inl)
                        vcmi_inls.append(i_inl)
                        vcmo_inls.append(o_inl)                    
                print("ADC%d"%(adc))
                print("VREFP worst DNL:", max(vrefp_dnls, key=abs))
                print("VREFP worst INL:", max(vrefp_inls, key=abs))
                print("VREFN worst DNL:", max(vrefn_dnls, key=abs))
                print("VREFN worst INL:", max(vrefn_inls, key=abs))
                print("VCMI worst DNL:", max(vcmi_dnls, key=abs))
                print("VCMI worst INL:", max(vcmi_inls, key=abs))
                print("VCMO worst DNL:", max(vcmo_dnls, key=abs))
                print("VCMO worst INL:", max(vcmo_inls, key=abs))                
                
            print(adc_vrefp_dnls)
            print(adc_vrefn_dnls)
            print(adc_vcmi_dnls)
            print(adc_vcmo_dnls)
            print(adc_vrefp_dnls)            
            
    # x = [0, 0b1, 0b10, 0b11, 0b100, 0b111, 0b1000, 0b1111, 0b10000, 0b11111, 0b100000, 0b111111, 0b1000000, 0b1111111, 0b10000000, 0b11111111]
    # vrefp_dacs = [[] for adc in range(8)]
    # vrefn_dacs = [[] for adc in range(8)]
    # vcmi_dacs = [[] for adc in range(8)]
    # vcmo_dacs = [[] for adc in range(8)]
    
    # for bit in range(8):
        # x.append((1<<bit)-1)
        # x.append(1<<bit)
        # print(bin((1<<bit)-1))
        # print(bin((1<<bit)))
        # for adc in range(8):
            # vrefp_dacs[adc].append(data['refv_dacs'][(1<<bit)-1]['MON_VREFP'][1][adc])
            # vrefp_dacs[adc].append(data['refv_dacs'][1<<bit]['MON_VREFP'][1][adc])
            # vrefn_dacs[adc].append(data['refv_dacs'][(1<<bit)-1]['MON_VREFN'][1][adc])
            # vrefn_dacs[adc].append(data['refv_dacs'][1<<bit]['MON_VREFN'][1][adc])
            # vcmi_dacs[adc].append(data['refv_dacs'][(1<<bit)-1]['MON_VCMI'][1][adc])
            # vcmi_dacs[adc].append(data['refv_dacs'][1<<bit]['MON_VCMI'][1][adc])
            # vcmo_dacs[adc].append(data['refv_dacs'][(1<<bit)-1]['MON_VCMO'][1][adc])
            # vcmo_dacs[adc].append(data['refv_dacs'][1<<bit]['MON_VCMO'][1][adc])            
    # x.append(0xff)
    # vrefp_dacs[adc].append(data['refv_dacs'][0xff]['MON_VREFP'][1][adc])
    # vrefn_dacs[adc].append(data['refv_dacs'][0xff]['MON_VREFN'][1][adc])
    # vcmi_dacs[adc].append(data['refv_dacs'][0xff]['MON_VCMI'][1][adc])
    # vcmo_dacs[adc].append(data['refv_dacs'][0xff]['MON_VCMO'][1][adc])
    
    # for xi in x:
            x = np.array(dacs)
                
            import matplotlib.pyplot as plt
            fig = plt.figure(figsize=(9,6))      
            plt_log(plt,logsd, "ADC Reference Voltage DAC Sweep")
                  
            ax1 = plt.subplot2grid((2, 2), (0, 0), colspan=1, rowspan=1)
            ax2 = plt.subplot2grid((2, 2), (0, 1), colspan=1, rowspan=1)
            ax3 = plt.subplot2grid((2, 2), (1, 0), colspan=1, rowspan=1)
            ax4 = plt.subplot2grid((2, 2), (1, 1), colspan=1, rowspan=1)
            
            ax1.set_title("VREFP", fontsize=10)
            ax1.set_ylabel("Voltage (mV)", fontsize=8)
            ax1.set_xlabel("DAC setting", fontsize=8)
            
            ax2.set_title("VREFN", fontsize=10)
            ax2.set_ylabel("Voltage (mV)", fontsize=8)
            ax2.set_xlabel("DAC setting", fontsize=8)
            
            ax3.set_title("VCMI", fontsize=10)
            ax3.set_ylabel("Voltage (mV)", fontsize=8)
            ax3.set_xlabel("DAC setting", fontsize=8)

            ax4.set_title("VCMO", fontsize=10)
            ax4.set_ylabel("Voltage (mV)", fontsize=8)
            ax4.set_xlabel("DAC setting", fontsize=8)
            
            # dac_set = list(range(0,0x100,0x10))
            # x = np.array(dac_set)

            
            for adc in range(8):
                ax1.scatter(x, vrefp_dacs[adc], color="C%d"%(adc), marker='.', label='ADC%d'%(adc))
                m, b = np.polyfit(x,vrefp_dacs[adc],1)
                ax1.plot(x,m*x+b,color="C%d"%(adc))
                ax1.text(1, (300-150*adc)+1750, 'y = ' + '{:.2f}'.format(b) + ' + {:.2f}'.format(m) + 'x', size=9, color="C%d"%(adc))
                
                ax2.scatter(x, vrefn_dacs[adc], color="C%d"%(adc), marker='.')
                m, b = np.polyfit(x,vrefn_dacs[adc],1)
                ax2.plot(x,m*x+b,color="C%d"%(adc))
                ax2.text(1, (300-150*adc)+1750, 'y = ' + '{:.2f}'.format(b) + ' + {:.2f}'.format(m) + 'x', size=9, color="C%d"%(adc))
                
                ax3.scatter(x, vcmi_dacs[adc], color="C%d"%(adc), marker='.')
                m, b = np.polyfit(x,vcmi_dacs[adc],1)
                ax3.plot(x,m*x+b,color="C%d"%(adc))
                ax3.text(1, (300-150*adc)+1750, 'y = ' + '{:.2f}'.format(b) + ' + {:.2f}'.format(m) + 'x', size=9, color="C%d"%(adc))
                
                ax4.scatter(x, vcmo_dacs[adc], color="C%d"%(adc), marker='.')
                m, b = np.polyfit(x,vcmo_dacs[adc],1)
                ax4.plot(x,m*x+b,color="C%d"%(adc))
                ax4.text(1, (300-150*adc)+1750, 'y = ' + '{:.2f}'.format(b) + ' + {:.2f}'.format(m) + 'x', size=9, color="C%d"%(adc))
                
                
            ax1.legend(loc=(1.04, 0))    
            ax1.grid()
            ax2.grid()
            ax3.grid()
            ax4.grid()
            plt.tight_layout( rect=[0.05, 0.05, 0.95, 0.95])
            plt.plot()
            plt.show()
      
    
    # print(data['Imons'].keys())
    
    if ana_adc_imon(data['Imons']): #warn_flag == True
        print(Fore.RED + "Current check failed")
        
if 4 in tms:
    print ("-------------------------------------------------------------------------")
    print ("4: ADC autocalibration check  ")
    print ("command on WIB terminal to retake data for this test item is as bellow :")
    fp = fdir + "QC_AUTOCALI" + ".bin"
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
        
    
    print(dkeys) 
    if ana_adc_weightchk(data['weights']): #warn_flag
        print(Fore.RED + "Autocali check failed.")
        default_weights = [[0xc000, 0x4000], [0xe000, 0x2000], [0xf000, 0x1000], [0xf800, 0x0800],
                            [0xfc00, 0x0400], [0xfe00, 0x0200], [0xff00, 0x0100], [0xff80, 0x0080],
                            [0xffc0, 0x0040], [0xffe0, 0x0020], [0xfff0, 0x0010], [0xfff8, 0x0008],
                            [0xfffc, 0x0004], [0xfffe, 0x0002], [0xffff, 0x0001], [0x0000, 0x0000]] #last pair are gain and offset      
        for wt in range(2): #W0 or W2
           for stage_num in range(16): 
               default_weight = default_weights[stage_num][wt]
       
        if False:
            import matplotlib.pyplot as plt
            import matplotlib.ticker as ticker
            from matplotlib.ticker import MaxNLocator
            fig = plt.figure(figsize=(12, 6))
            cm = plt.get_cmap('gist_rainbow')
            dash, = plt.plot([10],[0],c='black',linestyle='dashed', label="ADC0 autocali")
            dot, = plt.plot([10],[0],c='black',linestyle='dotted', label="ADC1 autocali")                
            for wt in range(2): #W0 or W2
                for stage_num in range(16): 
                    default_weight = default_weights[stage_num][wt]
                    linecolor = (wt << 4) | (stage_num << 0)
                    
                    plt.plot(list(range(8)),[default_weight for chip in range(8)],label="Stage %d W%d default"%(stage_num, wt*2),c=cm(linecolor/32))                    
                    for adc in range(2): #ADC0 or ADC1
                        style = ['dashed','dotted']
                        chips_weights = [data['weights'][chip][adc][wt][stage_num] for chip in range(8)]
                        plt.plot(list(range(8)), chips_weights, c=cm(linecolor/32), linestyle=style[adc]) #, label="%d stage%d W%d"%(adc, stage_num, wt*2)
            axes = plt.gca()
            axes.get_yaxis().set_major_locator(MaxNLocator(integer=True))
            # axes.get_yaxis().set_major_formatter(ticker.FormatStrFormatter("0x%x")) # throws an error for some reason
            # plt.legend()
            plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1),ncol=5)
            # axes.add_artist(mainlegend)        
            plt.xlim((-0.35000000000000003, 7.35))
            plt.ylim((-3276.75, 68811.75))
            plt.ylabel('Weight')
            plt.xlabel('Chip #')
            plt.title('ADC autocalibration weight readout')

            # legend1 = plt.legend([dash, dot], ["ADC0","ADC1"], loc=1)

            # axes.add_artist(legend1)
            plt.tight_layout()
            plt.show()
            plt.close() 

if 5 in tms:
    print ("-------------------------------------------------------------------------")
    print ("5: ADC noise measurement  ")
    print ("command on WIB terminal to retake data for this test item is as bellow :")
    fp = fdir + "QC_RMS" + ".bin"
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
        
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(8,6))
    fig.canvas.manager.set_window_title('ADC RMS measurement failing tests')
    plt.rcParams.update({'font.size': 8})
    ax1 = plt.subplot2grid((2, 1), (0, 0), colspan=1, rowspan=1)
    ax2 = plt.subplot2grid((2, 1), (1, 0), colspan=1, rowspan=1)
    
    
    for onekey in dkeys:
        cfgdata = data[onekey]
        fembs = cfgdata[0]
        rawdata = cfgdata[1]
        cfg_info = cfgdata[2]
        chns, rmss, peds, pkps, pkns, wfs, wfsf = data_ana(fembs, rawdata, rms_flg=True)
        if "RMS_OUTPUT_" in onekey:
            sdd = int(onekey[onekey.find("_SDD")+4])
            sdf = int(onekey[onekey.find("_SDF")+4])
            snc = int(onekey[onekey.find("_SNC")+4])
            ax1.plot(np.array(peds), marker='.', label="FE_SDD%d_SDF%d_SNC%d"%(sdd, sdf, snc) )
            ax2.plot(np.array(rmss), marker='.', label="FE_SDD%d_SDF%d_SNC%d"%(sdd, sdf, snc) )                    
        else:
            ax1.plot(np.array(peds), marker='.', label=onekey )
            ax2.plot(np.array(rmss), marker='.', label=onekey )                    


    plt.suptitle('ADC RMS noise measurement',fontsize=12)
    # ax1.set_xlim((-10,130))
    ax1.set_title('Pedestal')
    ax1.set_ylabel('ADCs', fontsize=10)
    ax1.legend()
    # ax2.set_xlim((-10,130))
    ax2.set_title('RMS noise')
    ax2.set_xlabel('Channel', fontsize=10)
    ax2.set_ylabel('ADCs', fontsize=10)
    ax2.legend()

    plt.tight_layout( rect=[0.05, 0.05, 0.95, 0.95])
    plt.plot()
    plt.show()
    plt.close()

    print ("#########################################################################")
    
if 6 in tms:
    print ("-------------------------------------------------------------------------")
    print ("6: ADC DNL/INL measurement  ")
    print ("command on WIB terminal to retake data for this test item is as bellow :")
    fp = fdir + "QC_DNL_INL" + ".bin"
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
        
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(8,6))
    plt.rcParams.update({'font.size': 8})
    ax2 = plt.subplot2grid((3, 1), (0, 0), colspan=1, rowspan=1) #hist (not necessary?)
    ax3 = plt.subplot2grid((3, 1), (1, 0), colspan=1, rowspan=1) #dnl
    ax1 = plt.subplot2grid((3, 1), (2, 0), colspan=1, rowspan=1) #inl
    x = np.arange(2**14)
    
    for onekey in dkeys:
        if 'histdata' in onekey:
            cfgdata = data[onekey]
            fembs = cfgdata[0]
            histdata = cfgdata[1]
            cfg_info = cfgdata[2]
            for ch, ch_hist_data in enumerate(histdata):
                chip = ch // 16
                num_16bwords = 0x8000 / 2        
                words16b = list(struct.unpack_from("<%dH"%(num_16bwords),ch_hist_data)) 
                tmp = 1000
                x1 = x[tmp:-1*tmp]
                y = np.array(words16b[tmp:-1*tmp])
                ax2.plot(x1, y, c="C%d"%(chip))

                tot = np.sum(y)/len(x1)
                ny = (y*1.0)/tot - 1
                inl = []
                for i in range(len(ny)):
                    inl.append(np.sum(ny[0:i+1]))
                ax3.plot (x1, ny)

                ax1.plot(x1, inl)

        ax1.title.set_text('INL')            
        ax1.set(xlabel="ADC code", ylabel="LSB")

        ax2.title.set_text('Histogram from '+str(data['num_samples'])+' samples')
        ax2.set(xlabel='ADC code',ylabel='Counts per code')

        ax3.set_ylim((-2,2))
        ax3.set(xlabel="ADC code", ylabel="LSB")
        ax3.title.set_text('DNL')            
    plt.tight_layout()
    plt.show()
    plt.close()
    
if 7 in tms:
    print ("-------------------------------------------------------------------------")
    print ("7: ADC DAT-DAC SCAN  ")
    print ("command on WIB terminal to retake data for this test item is as bellow :")
    fp = fdir + "QC_DACSCAN" + ".bin"
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
    femb = int(data['logs']['DAT_on_WIB_slot'])   


    dacdiffs = []
    dacses = []
    for onekey in dkeys:
        if "DACDIFF_" in onekey or "DACSE_" in onekey:
            pass
        else:
            continue
        cfgdata = data[onekey]
        fembs = cfgdata[0]
        rawdata = cfgdata[1]
        cfg_info = cfgdata[2]
        dacv = cfgdata[3]
        chns, rmss, peds, pkps, pkns, wfs, wfsf = data_ana(fembs, rawdata, rms_flg=True)
        if "DACDIFF_" in onekey:
            dacdiffs.append([dacv, peds, rmss])
            print (dacv, peds[0], rmss[0])
        else:
            dacses.append([dacv, peds, rmss])
            print (dacv, peds[0], rmss[0])
            #exit()
    exit()

    print(dkeys)  
    for onekey in dkeys:
        if 'rawdata_under' in onekey:
            wibdata = wib_dec(data[onekey],[femb], spy_num=20, cd0cd1sync=False)
            show_flg = False
            failing_chs = []
            for sample in wibdata:
                for ch, chdata in enumerate(sample[femb]):
                    if not all(samp < 1000 for samp in chdata):
                       print("Channel",ch,"failed underflow test.")
                       show_flg = True
                       failing_chs.append(ch)
            show_flg = True
            failing_chs = list(range(128))
            if show_flg:
                import matplotlib.pyplot as plt
                fig = plt.figure(figsize=(8,6))
                plt.rcParams.update({'font.size': 8})  
                for ch, chdata in enumerate(sample[femb]):
                    chip = ch // 16
                    ch_allsamps = []
                    if ch in failing_chs:
                        for sample in range(20):
                            ch_allsamps = ch_allsamps + list(wibdata[sample][femb][ch])
                    plt.plot(ch_allsamps,c='C%d'%(chip),label="Ch%d"%(ch))
                plt.legend()
                plt.show()
                plt.close()
        if 'rawdata_over' in onekey:
            wibdata = wib_dec(data[onekey],[femb], spy_num=20, cd0cd1sync=False)
            show_flg = False
            failing_chs = []
            for sample in wibdata:
                for ch, chdata in enumerate(sample[femb]):
                    if not all(samp > 16000 for samp in chdata):
                       print("Channel",ch,"failed overflow test.")
                       show_flg = True
                       failing_chs.append(ch)
            show_flg = True
            failing_chs = list(range(128))
            if show_flg:
                import matplotlib.pyplot as plt
                fig = plt.figure(figsize=(8,6))
                plt.rcParams.update({'font.size': 8})  
                for ch, chdata in enumerate(sample[femb]):
                    chip = ch // 16
                    ch_allsamps = []
                    if ch in failing_chs:
                        for sample in range(20):
                            ch_allsamps = ch_allsamps + list(wibdata[sample][femb][ch])
                    plt.plot(ch_allsamps,c='C%d'%(chip),label="Ch%d"%(ch))
                plt.legend()
                plt.show()
                plt.close()                        
            
if 8 in tms:
    print ("-------------------------------------------------------------------------")
    print ("8: ADC ENOB measurement  ")
    print ("command on WIB terminal to retake data for this test item is as bellow :")
    fp = fdir + "QC_ENOB_00358104Hz" + ".bin"
    fp = fdir + "QC_ENOB_00008106Hz" + ".bin"
    #fp = fdir + "QC_ENOB_1V_00008106Hz" + ".bin"
    #fp = fdir + "QC_ENOB_08V_00008106Hz" + ".bin"
    fp = fdir + "QC_ENOB_00014781Hz" + ".bin"
    fp = fdir + "QC_ENOB_00031948Hz" + ".bin"
    fp = fdir + "QC_ENOB_00072002Hz" + ".bin"
    fp = fdir + "QC_ENOB_00072002Hz" + ".bin"
    fp = fdir + "QC_ENOB_00200748Hz" + ".bin"
    fp = fdir + "QC_ENOB_00358104Hz" + ".bin"
    fp = fdir + "QC_ENOB_00119686Hz" + ".bin"
    fp = fdir + "QC_ENOB_00008106Hz" + ".bin"
    fp = fdir + "QC_ENOB_00014781Hz" + ".bin"
    
    
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
        if 'enobdata' in onekey:     
            cfgdata = data[onekey]
            fembs = cfgdata[0]
            enobdata = cfgdata[1]
            cfg_info = cfgdata[2]

# Plot all waveforms, but hide all but ch0 by default since they are asynchronously captured
# Toggle waveform visibility by clicking on the white space to the left of the channel # (this can be improved)       
# https://learndataanalysis.org/source-code-how-to-toggle-graphs-visibility-by-clicking-legend-label-in-matplotlib/#google_vignette            
            from adc_enob import adc_enob
            
            chsenob = []
            # extent = (0, 16384, 0, 16384)
            x = list(range(16384))
            for ch, raw in enumerate(enobdata):
                if raw is None:
                    continue
                num_16bwords = 0x8000 / 2
                words16b = list(struct.unpack_from("<%dH"%(num_16bwords),raw))
                if ch == 0:
                    ffig = True
                else:
                    ffig = False

                if ch == 0:
                    import matplotlib.pyplot as plt
                    plt.plot(words16b)
                    plt.show()
                    plt.close()
                ENOB, NAD, SFDR, SINAD, psd_dbfs, points_dbfs = adc_enob(chndata=words16b, fs=1953125, Ntot=2**12, Vfullscale=1.4, Vinput=1.2, ffig=ffig)
                chsenob.append(ENOB)
            exit()
            #import matplotlib.pyplot as plt
            #fig, ax = plt.subplots(figsize=(12, 6))
            #plt.plot(chsenob)
            #
            #    
            #plt.tight_layout()
            #plt.show()
            break
            
if 9 in tms:
    print ("-------------------------------------------------------------------------")
    print ("9: ADC ring oscillator frequency readout  ")
    print ("command on WIB terminal to retake data for this test item is as bellow :")
    fp = fdir + "QC_RINGO" + ".bin"
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
        if 'ring_osc_freq' in onekey:     
            freqs = data['ring_osc_freq']
            for chip, freq in enumerate(freqs):
                print("ADC"+str(chip)+": "+str(freq)+" Hz ("+str(freq/1000000)+" MHz)")
                
if 10 in tms:
    print ("-------------------------------------------------------------------------")
    print ("10: ADC triangle test  ")
    print ("command on WIB terminal to retake data for this test item is as bellow :")
    fp = fdir + "QC_TRIG" + ".bin"
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
    femb = int(data['logs']['DAT_on_WIB_slot'])   
    
    for onekey in dkeys:
        if 'rawdata' in onekey:     
            cfgdata = data[onekey]
            fembs = cfgdata[0]
            rawdata = cfgdata[1]
            cfg_info = cfgdata[2]

# Plot all waveforms, but hide all but ch0 by default since they are asynchronously captured
# Toggle waveform visibility by clicking on the white space to the left of the channel # (this can be improved)       
# https://learndataanalysis.org/source-code-how-to-toggle-graphs-visibility-by-clicking-legend-label-in-matplotlib/#google_vignette            
            import matplotlib.pyplot as plt

            fig, ax = plt.subplots(figsize=(12, 6))


            chdata = []
            chplot = []
            
            # extent = (0, 16384, 0, 16384)
            x = list(range(16384))
            for ch, raw in enumerate(rawdata):
                if raw is None:
                    continue
                num_16bwords = 0x8000 / 2
                words16b = list(struct.unpack_from("<%dH"%(num_16bwords),raw))

                chip = ch // 16
                chdata.append(words16b)
                # if any(word == 0x0 for word in words16b):
                    # print("Channel",ch,"has a glitch")
                chplot.append(ax.plot(words16b,label='Ch%d'%(ch))[0])#, extent=extent))
                # if ch != 0:
                    # chplot[-1].set_visible(False)
                
            # legend = plt.legend(loc='center left', bbox_to_anchor=(1, 0.5),ncol=8)
            box = ax.get_position()
            # ax.set_position([box.x0, box.y0 + box.height * 0.3,
                     # box.width, box.height * 0.7])  
            
            legend = plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05),ncol=8)
            legends = legend.get_lines()
            
            for leg in legends:
                leg.set_picker(True)
                leg.set_pickradius(10)   
                
            for ch, plot in enumerate(chplot):
                if ch != 0:
                    plot.set_visible(False)
                    legends[ch].set_visible(False)

            graphs = {}
            for i in range(128):
                graphs[legends[i]] = chplot[i]
                
            plt.tight_layout()
            plt.connect('pick_event',onpick)
            plt.show()
