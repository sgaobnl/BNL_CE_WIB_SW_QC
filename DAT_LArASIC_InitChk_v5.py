import time
import os
import sys
import numpy as np
import pickle
import copy
import time, datetime
from spymemory_decode import wib_dec
#from spymemory_decode import avg_aligned_by_ts
#import statsmodels.api as sm
#import colorama
#from colorama import Fore, Back
#colorama.init(autoreset=True)

# Automatically adds a Style.RESET_ALL after each print statement
#print(Fore.RED + 'Red foreground text')
#print(Back.RED + 'Red background text')

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
    import matplotlib.pyplot as plt
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
        plt.plot(chndata)
    plt.show()
    plt.close()

    return chns, rmss, peds, pkps, pkns, wfs,wfsf

def ana_res2(fembs, rawdata, par=[7000,10000], rmsr=[5,25], pedr=[500,3000] ):
    badchs = []
    bads = []
    chns, rmss, peds, pkps, pkns, wfs, wfsf = data_ana(fembs, rawdata)
    amps = np.array(pkps) - np.array(peds)

    for chip in range(8):
        chipamps = list(amps[chip*16: chip*16 + 16])
        maxcamp = np.max(chipamps)
        mincamp = np.min(chipamps)
        #chipamps.remove(maxcamp)
        #chipamps.remove(mincamp)
        meanamp = np.mean(chipamps)
        rmsamp = np.std(chipamps)
        #print (maxcamp, mincamp, meanamp, rmsamp)
        if (abs(maxcamp-meanamp) > 5*rmsamp) or (abs(mincamp-meanamp) > 5*rmsamp ):
            #print ("Error", chip, maxcamp, mincamp, meanamp, rmsamp)
            if chip not in bads:
                bads.append(chip)

    for tmp in [rmss, peds, amps]:
##    for tmp in [rmss] :#, peds, amps]:
#    #    print (np.mean(tmp), np.std(tmp), np.max(tmp), np.min(tmp))
#
        import matplotlib.pyplot as plt
        plt.plot(chns, tmp)
        for i in range(0,128,16):
            plt.vlines(i-0.5, 0, 100, color='y')

        plt.title("Noise", fontsize=8)
       # plt.ylim((0,25))
       # plt.xlabel("ADC / bit", fontsize=8)
       # plt.ylabel("CH number", fontsize=8)
        plt.grid()
        plt.show()
        plt.close()

    for ch in range(len(chns)):
        if (amps[ch] > par[0]) and (amps[ch] < par[1]):
            pass
        else:
            if ch not in badchs:
                badchs.append(ch)
            #print ("par", ch)
            
        if (peds[ch] > pedr[0]) and (peds[ch] < pedr[1]):
            pass
        else:
            if ch not in badchs:
                badchs.append(ch)
            #print ("ped", ch)

        if (rmss[ch] > rmsr[0]) and (rmss[ch] < rmsr[1]):
            pass
        else:
            if ch not in badchs:
                badchs.append(ch)
            #print ("ped", ch)
    for badch in badchs:
        if (badch//16) not in bads:
            bads.append(badch//16)
    #print (bads)
    return bads

def ana_fepwr2(pwr_meas, vin=[1.7,1.9], cdda=[15,25], cddp=[20,35], cddo=[0,5]):
    bads = []
    kpwrs = list(pwr_meas.keys())

    vddas = []
    vddos = []
    vddps = []
    cddas = []
    cddos = []
    cddps = []

    for i in range(len(kpwrs)):
        chip = int(kpwrs[i][2])
        #print (chip, kpwrs[i],pwr_meas[kpwrs[i]] )
        if "VDDA" in kpwrs[i]:
            vddas.append(pwr_meas[kpwrs[i]][0])
            cddas.append(pwr_meas[kpwrs[i]][1])
            if not ((vddas[chip] >= vin[0] )  and (vddas[chip] <= vin[1] ) ):
                if chip not in bads:
                    bads.append(chip)
            if not ((cddas[chip] >= cdda[0] ) and (cddas[chip] <= cdda[1] )) :
                if chip not in bads:
                    bads.append(chip)

        if "VDDO" in kpwrs[i]:
            vddos.append(pwr_meas[kpwrs[i]][0])
            cddos.append(pwr_meas[kpwrs[i]][1])
            if not ((vddos[chip] >= vin[0] )  and (vddos[chip] <= vin[1] ) ):
                if chip not in bads:
                    bads.append(chip)
            if not ((cddos[chip] >= cddo[0] ) and (cddos[chip] <= cddo[1] )) :
                if chip not in bads:
                    bads.append(chip)

        if "VPPP" in kpwrs[i]:
            vddps.append(pwr_meas[kpwrs[i]][0])
            cddps.append(pwr_meas[kpwrs[i]][1])
            if not ((vddps[chip] >= vin[0] )  and (vddps[chip] <= vin[1] ) ):
                if chip not in bads:
                    bads.append(chip)
            if not ((cddps[chip] >= cddp[0] ) and (cddps[chip] <= cddp[1] )) :
                if chip not in bads:
                    bads.append(chip)
    return bads


def dat_larasic_initchk(fdir="/."):
    fp = fdir + "QC_INIT_CHK" + ".bin"
    with open(fp, 'rb') as fn:
        data = pickle.load( fn)
    
    dkeys = list(data.keys())
    
    logsd = data["logs"]

    QCstatus = data["QCstatus"]

    if "Code#E001" in QCstatus:
        return QCstatus, sorted(data["FE_Fail"])
    if "Code#E002" in QCstatus:
        return QCstatus, sorted(data["FE_Fail"])
    if "Code#E003" in QCstatus:
        return QCstatus, sorted(data["FE_Fail"])
    if "Code#E005" in QCstatus:
        return QCstatus, sorted(data["FE_Fail"])
    if "Code#W004" in QCstatus:
        bads = []
        for onekey in ["DIRECT_PLS_CHK", "ASICDAC_CALI_CHK", "ASICDAC_47mV_CHK", "DIRECT_PLS_RMS", "ASICDAC_CALI_RMS", "ASICDAC_47mV_RMS"]:
            print (onekey)
            cfgdata = data[onekey]
            fembs = cfgdata[0]
            rawdata = cfgdata[1]
            cfg_info = cfgdata[2]
            pwr_meas = cfgdata[3]
    
            if ("DIRECT_PLS_CHK" in onekey) :
                bads0 = ana_res2(fembs, rawdata, par=[9000,14000], rmsr=[5,25], pedr=[500,2000] )
                bads1 = ana_fepwr2(pwr_meas, vin=[1.7,1.9], cdda=[15,25], cddp=[25,35], cddo=[0,5])
            if ("ASICDAC_CALI_CHK" in onekey):
                bads0 = ana_res2(fembs, rawdata, par=[7000,10000], rmsr=[5,25], pedr=[300,2000] )
                bads1 = ana_fepwr2(pwr_meas, vin=[1.60,1.8], cdda=[40,50], cddp=[25,35], cddo=[5,15])
            if ("ASICDAC_47mV_CHK" in onekey):
                bads0 = ana_res2(fembs, rawdata, par=[5500,7500], rmsr=[2,10], pedr=[400,2000] )
                bads1 = ana_fepwr2(pwr_meas, vin=[1.7,1.9], cdda=[15,25], cddp=[25,35], cddo=[0,5])

            if ("DIRECT_PLS_RMS" in onekey) :
                bads0 = ana_res2(fembs, rawdata, par=[0000,1000], rmsr=[5,25], pedr=[500,2000] )
                bads1 = ana_fepwr2(pwr_meas, vin=[1.7,1.9], cdda=[15,25], cddp=[25,35], cddo=[0,5])
            if ("ASICDAC_CALI_RMS" in onekey):
                bads0 = ana_res2(fembs, rawdata, par=[0000,1000], rmsr=[5,25], pedr=[300,2000] )
                bads1 = ana_fepwr2(pwr_meas, vin=[1.60,1.8], cdda=[40,50], cddp=[25,35], cddo=[5,15])
            if ("ASICDAC_47mV_RMS" in onekey):
                bads0 = ana_res2(fembs, rawdata, par=[000,1000], rmsr=[2,10], pedr=[400,2000] )
                bads1 = ana_fepwr2(pwr_meas, vin=[1.7,1.9], cdda=[15,25], cddp=[25,35], cddo=[0,5])

            for badchip in bads0:
                if badchip not in bads:
                    bads.append(badchip)
            for badchip in bads1:
                if badchip not in bads:
                    bads.append(badchip)

        if len(bads) > 0 :
            return QCstatus, sorted(bads)
        else:
            return "PASS", []

if __name__ == '__main__':
    fdir = "./tmp_data/RT_FE_002010000_002020000_002030000_002040000_002050000_002060000_002070000_002080000/"
    fdir = "D:/DAT_LArASIC_QC/Tested/Time_DUT1_DUT_1000_2000_3000_4000_5000_6000_7000_8000/LN_FE_007000948_007001170_007001237_007001247_007001146_007001104_007001152_007001236/"
    fdir = "./tmp_data/LN_FE_017000948_017001170_017001237_017001247_017001146_017001104_017001152_017001236/"
    QCstatus, bads = dat_larasic_initchk(fdir)
    print (QCstatus)
    print (bads)

