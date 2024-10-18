import time
import os
import sys
import numpy as np
import pickle
import copy
import time, datetime
#import matplotlib.pyplot as plt
import platform
from scipy.signal import find_peaks
system_info = platform.system()
index_tmts = 5
if system_info=='Linux':
    sys.path.append('./Analysis/decode/')
    from dunedaq_decode import wib_dec
    index_tmts=4
    sys.path.append('../../')
elif system_info=='Windows':
    from spymemory_decode import wib_dec
    index_tmts=5
#from spymemory_decode import avg_aligned_by_ts
#import statsmodels.api as sm
#import colorama
#from colorama import Fore, Back
#colorama.init(autoreset=True)

# Automatically adds a Style.RESET_ALL after each print statement
#print(Fore.RED + 'Red foreground text')
#print(Back.RED + 'Red background text')

def data_ana(fembs, rawdata, rms_flg=False, period=512):
    wibdatas = wib_dec(rawdata,fembs, spy_num=5, cd0cd1sync=False)
    dat_tmts_l = []
    dat_tmts_h = []
    for wibdata in wibdatas:
        dat_tmts_l.append(wibdata[index_tmts][fembs[0]*2][0]) #LSB of timestamp = 16ns
        dat_tmts_h.append(wibdata[index_tmts][fembs[0]*2+1][0])

    # period = 512
    dat_tmtsl_oft = (np.array(dat_tmts_l)//32)%period #ADC sample rate = 16ns*32 = 512ns
    dat_tmtsh_oft = (np.array(dat_tmts_h)//32)%period #ADC sample rate = 16ns*32 = 512ns

    # concatenate data
    all_data = []
#    import matplotlib.pyplot as plt
    for achn in range(128):
    #chipi = 2
    #for achn in range(16*chipi,16*chipi+16,1):
        conchndata = []

        for i in range(len(wibdatas)):
            if achn<64:
                oft = dat_tmtsl_oft[i]
            else:
                oft = dat_tmtsh_oft[i]

            wibdata = wibdatas[i]
            datd = [wibdata[0], wibdata[1],wibdata[2],wibdata[3]][fembs[0]]
            chndata = np.array(datd[achn], dtype=np.uint32)
            lench = len(chndata)
            tmp = int(period-oft)
            conchndata = conchndata + list(chndata[tmp : ((lench-tmp)//period)*period + tmp])
        all_data.append(conchndata)
#        if True:
#            plt.plot(conchndata[0:1000])
#    plt.show()
#    plt.close()

    chns = list(range(128))
    rmss = []
    peds = []
    pkps, pkns = [], []
    wfs, wfsf = [], []
    for achn in range(128):
        chdata = []
        N_period = len(all_data[achn])//period
        for iperiod in range(N_period):
            istart = iperiod*period
            iend = istart + period
            chunkdata = all_data[achn][istart : iend]
            chdata.append(chunkdata)
        chdata = np.array(chdata)
        avg_wf = np.average(np.transpose(chdata), axis=1, keepdims=False)
        wfsf.append(avg_wf)
        amax = np.max(avg_wf)
        amin = np.min(avg_wf)
        pkps.append(amax)
        pkns.append(amin)
        ppos = np.where(avg_wf==amax)[0][0]
        p0=ppos + period

        peddata = []
        for iperiod in range(N_period-3):
            peddata += all_data[achn][p0 + iperiod*period - 250: p0 + iperiod*period-50]
        rmss.append(np.std(peddata))
        peds.append(np.mean(peddata))


        npos = np.where(avg_wf==amin)[0][0]
        tmpwf = avg_wf
        if ppos-50 < 0:
            front = avg_wf[ -50 : ]
            back = avg_wf[ : -50]
            tmpwf = np.concatenate((front, back))
        ppos = np.where(tmpwf==np.max(tmpwf))[0][0]
        if ppos+150 > period:
            front = tmpwf[ ppos-50 : ]
            back = tmpwf[ : ppos-50]
            tmpwf = np.concatenate((front, back))
        ppos = np.where(tmpwf==np.max(tmpwf))[0][0]
        wfs.append(tmpwf[ppos-50 : ppos+150])
    return chns, rmss, peds, pkps, pkns, wfs,wfsf

def ana_res2(fembs, rawdata, par=[7000,10000], rmsr=[5,25], pedr=[500,3000], period=512 ):
    badchs = []
    bads = []
    chns, rmss, peds, pkps, pkns, wfs, wfsf = data_ana(fembs, rawdata, period=period) # added the period here
    amps = np.array(pkps) - np.array(peds)

    for chip in range(8):
        chipamps = list(amps[chip*16: chip*16 + 16])
        maxcamp = np.max(chipamps)
        mincamp = np.min(chipamps)
        meanamp = np.mean(chipamps)
        rmsamp = np.std(chipamps)
        if (abs(maxcamp-meanamp) > 5*rmsamp) or (abs(mincamp-meanamp) > 5*rmsamp ):
            if chip not in bads:
                bads.append(chip)

    for ch in range(len(chns)):
        if (amps[ch] > par[0]) and (amps[ch] < par[1]):
            pass
        else:
            if ch not in badchs:
                badchs.append(ch)
                print ("par", ch, amps[ch])
            
        if (peds[ch] > pedr[0]) and (peds[ch] < pedr[1]):
            pass
        else:
            if ch not in badchs:
                badchs.append(ch)
                print ("ped", ch, peds[ch])

        if (rmss[ch] > rmsr[0]) and (rmss[ch] < rmsr[1]):
            pass
        else:
            if ch not in badchs:
                badchs.append(ch)
                print ("rms", ch, rmss[ch])
    for badch in badchs:
        if (badch//16) not in bads:
            bads.append(badch//16)
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
        if "VDDA" in kpwrs[i]:
            vddas.append(pwr_meas[kpwrs[i]][0])
            cddas.append(pwr_meas[kpwrs[i]][1])
            if not ((vddas[chip] >= vin[0] )  and (vddas[chip] <= vin[1] ) ):
                if chip not in bads:
                    bads.append(chip)
                    print ("v VDDA", chip, vddas[chip], vin[0], vin[1])
            if not ((cddas[chip] >= cdda[0] ) and (cddas[chip] <= cdda[1] )) :
                if chip not in bads:
                    bads.append(chip)
                    print ("C VDDA", chip, cddas[chip], cdda[0], cdda[1])

        if "VDDO" in kpwrs[i]:
            vddos.append(pwr_meas[kpwrs[i]][0])
            cddos.append(pwr_meas[kpwrs[i]][1])
            if not ((vddos[chip] >= vin[0] )  and (vddos[chip] <= vin[1] ) ):
                if chip not in bads:
                    bads.append(chip)
                    print ("v VDDO", chip, vddos[chip], vin[0], vin[1])
            if not ((cddos[chip] >= cddo[0] ) and (cddos[chip] <= cddo[1] )) :
                if chip not in bads:
                    bads.append(chip)
                    print ("C VDDO", chip, cddos[chip], cddo[0], cddo[1])

        if "VPPP" in kpwrs[i]:
            vddps.append(pwr_meas[kpwrs[i]][0])
            cddps.append(pwr_meas[kpwrs[i]][1])
            if not ((vddps[chip] >= vin[0] )  and (vddps[chip] <= vin[1] ) ):
                if chip not in bads:
                    bads.append(chip)
                    print ("v VPPP", chip, vddps[chip], vin[0], vin[1])
            if not ((cddps[chip] >= cddp[0] ) and (cddps[chip] <= cddp[1] )) :
                if chip not in bads:
                    bads.append(chip)
                    print ("C VPPP", chip, cddps[chip], cddp[0], cddp[1])
    return bads


def dat_initchk(fdir="/."):
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
        datakeys = list(data.keys())
        vkeys = []
        for onekey in datakeys:
            if "DIRECT_" in onekey or "ASICDAC_" in onekey :
                vkeys.append(onekey)
        for onekey in vkeys:
            #print (onekey)
            cfgdata = data[onekey]
            fembs = cfgdata[0]
            rawdata = cfgdata[1]
            cfg_info = cfgdata[2]
            pwr_meas = cfgdata[3]

            bads0 = []
            bads1 = []
            if ("DIRECT_PLS_CHK" in onekey) :
                bads0 = ana_res2(fembs, rawdata, par=[7000,12000], rmsr=[3,30], pedr=[500,2000] , period=512)
                bads1 = ana_fepwr2(pwr_meas, vin=[1.7,1.9], cdda=[10,25], cddp=[25,35], cddo=[-0.1,5])
            if ("ASICDAC_CALI_CHK" in onekey):
                bads0 = ana_res2(fembs, rawdata, par=[7000,10000], rmsr=[3,25], pedr=[100,2000] , period=500)
                bads1 = ana_fepwr2(pwr_meas, vin=[1.60,1.8], cdda=[40,60], cddp=[25,35], cddo=[5,15])
            if ("ASICDAC_47mV_CHK" in onekey):
                bads0 = ana_res2(fembs, rawdata, par=[5500,7500], rmsr=[2,25], pedr=[400,2000] , period=500)
                bads1 = ana_fepwr2(pwr_meas, vin=[1.7,1.9], cdda=[10,25], cddp=[25,35], cddo=[-0.1,5])

            if ("DIRECT_PLS_RMS" in onekey) :
                bads0 = ana_res2(fembs, rawdata, par=[0000,1000], rmsr=[3,25], pedr=[500,2000] , period=512)
                bads1 = ana_fepwr2(pwr_meas, vin=[1.7,1.9], cdda=[10,25], cddp=[25,35], cddo=[-0.1,5])
            if ("ASICDAC_CALI_RMS" in onekey):
                bads0 = ana_res2(fembs, rawdata, par=[0000,1000], rmsr=[3,25], pedr=[100,2000] , period=500)
                bads1 = ana_fepwr2(pwr_meas, vin=[1.60,1.8], cdda=[40,60], cddp=[25,35], cddo=[5,15])
            if ("ASICDAC_47mV_RMS" in onekey):
                bads0 = ana_res2(fembs, rawdata, par=[000,1000], rmsr=[2,10], pedr=[400,2000] , period=500)
                bads1 = ana_fepwr2(pwr_meas, vin=[1.7,1.9], cdda=[10,25], cddp=[25,35], cddo=[-0.1,5])
            #print('Bads0 = {} \t Bads1 = {}'.format(bads0, bads1))

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

if __name__=="__main__":
    # fdir = "D:/DAT_LArASIC_QC//B010T0004/Time_20240703122319_DUT_0000_1001_2002_3003_4004_5005_6006_7007/RT_FE_002010000_002020000_002030000_002040000_002050000_002060000_002070000_002080000/"
    fdir = "../B010T0004/Time_20240703122319_DUT_0000_1001_2002_3003_4004_5005_6006_7007/RT_FE_002010000_002020000_002030000_002040000_002050000_002060000_002070000_002080000/"
    fdir = "./tmp_data/RT_FE_027000948_027001170_027001237_027001247_027001146_027001104_027001152_027001236/"
    fdir = "D:/DAT_LArASIC_QC/Tested/Time_20240731191508_DUT_1000_2000_3000_4000_5000_6000_7000_8000/RT_FE_001000001_001000002_001000003_001000004_001000005_001000006_001000007_001000008/"
    fdir = "D:/DAT_LArASIC_QC/Tested/Time_20240801184549_DUT_1000_2000_3000_4000_5000_6000_7000_8000/LN_FE_001000001_001000002_001000003_001000004_001000005_001000006_001000007_001000008/"
    fdir = "./tmp_data/LN_FE_002000001_002000002_002000003_002000004_002000005_002000006_002000007_002000008/"
    fdir = "D:/DAT_LArASIC_QC/DAT_Rev1_SN3_Fermilab_data/RT_FE_002000001_002000002_002000003_002000004_002000005_002000006_002000007_002000008/"
    fdir = "D:/DAT_LArASIC_QC/DAT_Rev1_SN3_Fermilab_data/RT_FE_003000001_003000002_003000003_003000004_003000005_003000006_003000007_003000008/"
    fdir = '''D:\DAT_LArASIC_QC\Tested\Time_20240807183343_DUT_1000_2000_3000_4000_5000_6000_7000_8000\RT_FE_401000001_401000002_401000003_401000004_401000005_401000006_401000007_401000008/'''
    fdir = '''D:/DAT_LArASIC_QC/Tested/Time_20240816185815_DUT_1000_2000_3000_4000_5000_6000_7000_8000/RT_FE_031000001_031000002_031000003_031000004_031000005_031000006_031000007_031000008/'''
    fdir = '''D:\DAT_CD_QC\Tested\Time_20241015202741_DUT_1000_2000\RT_CD_031702417_031752417/'''
    QCstatus, bads = dat_initchk(fdir)
    print (QCstatus)
    print (bads)

