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
                    print ("FE v VDDA", chip, vddas[chip], vin[0], vin[1])
            if not ((cddas[chip] >= cdda[0] ) and (cddas[chip] <= cdda[1] )) :
                if chip not in bads:
                    bads.append(chip)
                    print ("FE C VDDA", chip, cddas[chip], cdda[0], cdda[1])

        if "VDDO" in kpwrs[i]:
            vddos.append(pwr_meas[kpwrs[i]][0])
            cddos.append(pwr_meas[kpwrs[i]][1])
            if not ((vddos[chip] >= vin[0] )  and (vddos[chip] <= vin[1] ) ):
                if chip not in bads:
                    bads.append(chip)
                    print ("FE v VDDO", chip, vddos[chip], vin[0], vin[1])
            if not ((cddos[chip] >= cddo[0] ) and (cddos[chip] <= cddo[1] )) :
                if chip not in bads:
                    bads.append(chip)
                    print ("FE C VDDO", chip, cddos[chip], cddo[0], cddo[1])

        if "VPPP" in kpwrs[i]:
            vddps.append(pwr_meas[kpwrs[i]][0])
            cddps.append(pwr_meas[kpwrs[i]][1])
            if not ((vddps[chip] >= vin[0] )  and (vddps[chip] <= vin[1] ) ):
                if chip not in bads:
                    bads.append(chip)
                    print ("FE v VPPP", chip, vddps[chip], vin[0], vin[1])
            if not ((cddps[chip] >= cddp[0] ) and (cddps[chip] <= cddp[1] )) :
                if chip not in bads:
                    bads.append(chip)
                    print ("FE C VPPP", chip, cddps[chip], cddp[0], cddp[1])
    return bads

def ana_cdpwr(pwr_meas, vddfe = [1.7, 1.9], v1p1 = [1.15, 1.25], vddio = [2.15, 2.35], cdda = [7, 11], cddfe = [-1, 1], cddcore = [8, 13], cddd = [20, 25], cddio = [60, 75]):
    bads = []
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
        chip = int(kpwrs[i][2])
        if "CD_VDDA" in kpwrs[i]:
            vddas.append(pwr_meas[kpwrs[i]][0])
            cddas.append(pwr_meas[kpwrs[i]][1])
            #print ("v VDDA", chip, vddas[chip], v1p1[0], v1p1[1])
            #print ("C VDDA", chip, cddas[chip], cdda[0], cdda[1])
            if not ((vddas[chip] >= v1p1[0] )  and (vddas[chip] <=v1p1[1] ) ):
                if chip not in bads:
                    bads.append(chip)
                    print ("CD v VDDA", chip, vddas[chip], v1p1[0], v1p1[1])
            if not ((cddas[chip] >= cdda[0] ) and (cddas[chip] <= cdda[1] )) :
                if chip not in bads:
                    bads.append(chip)
                    print ("CD C VDDA", chip, cddas[chip], cdda[0], cdda[1])

        if "FE_VDDA" in kpwrs[i]:
            fe_vddas.append(pwr_meas[kpwrs[i]][0])
            fe_cddas.append(pwr_meas[kpwrs[i]][1]) 
            #print ("v FE_VDDA", chip, vddas[chip], vddfe[0], vddfe[1])
            #print ("C FE_VDDA", chip, fe_cddas[chip], cddfe[0], cddfe[1])
            if not ((fe_vddas[chip] >= vddfe[0] )  and (fe_vddas[chip] <= vddfe[1] ) ):
                if chip not in bads:
                    bads.append(chip)
                    print ("CD v FE_VDDA", chip, fe_vddas[chip], vddfe[0], vddfe[1])
            if not ((fe_cddas[chip] >= cddfe[0] ) and (fe_cddas[chip] <= cddfe[1] )) :
                if chip not in bads:
                    bads.append(chip)
                    print ("CD C FE_VDDA", chip, fe_cddas[chip], cddfe[0], cddfe[1])


        if "VDDCORE" in kpwrs[i]:
            vddcores.append(pwr_meas[kpwrs[i]][0])
            cddcores.append(pwr_meas[kpwrs[i]][1])
            #print ("v VDDCORE", chip, vddcores[chip], v1p1[0], v1p1[1])
            #print ("C VDDCORE", chip, cddcores[chip], cddcore[0], cddcore[1])
            if not ((vddcores[chip] >= v1p1[0] )  and (vddcores[chip] <= v1p1[1] ) ):
                if chip not in bads:
                    bads.append(chip)
                    print ("CD v VDDCORE", chip, vddcores[chip], v1p1[0], v1p1[1])
            if not ((cddcores[chip] >= cddfe[0] ) and (cddcores[chip] <= cddcore[1] )) :
                if chip not in bads:
                    bads.append(chip)
                    print ("CD C VDDCORE", chip, cddcores[chip], cddcore[0], cddcore[1])

        if "VDDD" in kpwrs[i]:
            vddds.append(pwr_meas[kpwrs[i]][0])
            cddds.append(pwr_meas[kpwrs[i]][1])        
            #print ("v VDDD", chip, vddds[chip], v1p1[0], v1p1[1])
            #print ("C VDDD", chip, cddds[chip], cddd[0], cddd[1])
            if not ((vddds[chip] >= v1p1[0] )  and (vddds[chip] <= v1p1[1] ) ):
                if chip not in bads:
                    bads.append(chip)
                    print ("CD v VDDD", chip, vddds[chip], v1p1[0], v1p1[1])
            if not ((cddds[chip] >= cddd[0] ) and (cddds[chip] <= cddd[1] )) :
                if chip not in bads:
                    bads.append(chip)
                    print ("CD C VDDD", chip, cddds[chip], cddd[0], cddd[1])


        if "VDDIO" in kpwrs[i]:
            vddios.append(pwr_meas[kpwrs[i]][0])
            cddios.append(pwr_meas[kpwrs[i]][1])
            #print ("v VDDD", chip, vddios[chip], vddio[0], vddio[1])
            #print ("C VDDD", chip, cddios[chip], cddio[0], cddio[1])
            if not ((vddios[chip] >= vddio[0] )  and (vddios[chip] <= vddio[1] ) ):
                if chip not in bads:
                    bads.append(chip)
                    print ("CD v VDDD", chip, vddios[chip], vddio[0], vddio[1])
            if not ((cddios[chip] >= cddio[0] ) and (cddios[chip] <= cddio[1] )) :
                if chip not in bads:
                    bads.append(chip)
                    print ("CD C VDDD", chip, cddios[chip], cddio[0], cddio[1])

    return bads

        #print (kpwrs[i], pwr_meas[kpwrs[i]][0], pwr_meas[kpwrs[i]][1])
  
def ana_adcpwr(pwr_meas, v2p5 = [2.10, 2.35], v1p2 = [1.05, 1.15], ca2p5=[115,145], cd1p2=[0,5], cio=[15,25], cd2p5 = [3,10]):
    bads =[]
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
        chip = int(kpwrs[i][3])
        if "VDDA2P5" in kpwrs[i]:
            vdda2p5s.append(pwr_meas[kpwrs[i]][0])
            cdda2p5s.append(pwr_meas[kpwrs[i]][1])
#            print ("v VDDA2P5", chip, vdda2p5s[chip], v2p5[0], v2p5[1])
#            print ("C VDDA2P5", chip, cdda2p5s[chip], ca2p5[0], ca2p5[1])

            if not ((vdda2p5s[chip] >= v2p5[0] ) and (vdda2p5s[chip] <= v2p5[1] ) ):
                if chip not in bads:
                    bads.append(chip)
                    print ("ADC v VDDA2P5", chip, vdda2p5s[chip], v2p5[0], v2p5[1])
            if not ((cdda2p5s[chip] >= ca2p5[0] ) and (cdda2p5s[chip] <= ca2p5[1] )) :
                if chip not in bads:
                    bads.append(chip)
                    print ("ADC C VDDA2P5", chip, cdda2p5s[chip], ca2p5[0], ca2p5[1])

        if "VDDD1P2" in kpwrs[i]:
            vddd1p2s.append(pwr_meas[kpwrs[i]][0])
            cddd1p2s.append(pwr_meas[kpwrs[i]][1])
#            print ("v VDDD1P2", chip, vddd1p2s[chip], v1p2[0], v1p2[1])
#            print ("C VDDD1P2", chip, cddd1p2s[chip], cd1p2[0], cd1p2[1])

            if not ((vddd1p2s[chip] >= v1p2[0] )  and (vddd1p2s[chip] <= v1p2[1] ) ):
                if chip not in bads:
                    bads.append(chip)
                    print ("ADC v VDDD1P2", chip, vddd1p2s[chip], v1p2[0], v1p2[1])
            if not ((cddd1p2s[chip] >= cd1p2[0] ) and (cddd1p2s[chip] <= cd1p2[1] )) :
                if chip not in bads:
                    bads.append(chip)
                    print ("ADC C VDDD1P2", chip, cddd1p2s[chip], cd1p2[0], cd1p2[1])


        if "VDDIO" in kpwrs[i]:
            vddios.append(pwr_meas[kpwrs[i]][0])
            cddios.append(pwr_meas[kpwrs[i]][1])
#            print ("v VDDIO", chip, vddios[chip], v2p5[0], v2p5[1])
#            print ("C VDDIO", chip, cddios[chip], cio[0], cio[1])

            if not ((vddios[chip] >= v2p5[0] )  and (vddios[chip] <= v2p5[1] ) ):
                if chip not in bads:
                    bads.append(chip)
                    print ("ADC v VDDIO", chip, vddios[chip], v2p5[0], v2p5[1])
            if not ((cddios[chip] >= cio[0] ) and (cddios[chip] <= cio[1] )) :
                if chip not in bads:
                    bads.append(chip)
                    print ("ADC C VDDIO", chip, cddios[chip], cio[0], cio[1])


        if "VDDD2P5" in kpwrs[i]:
            vddd2p5s.append(pwr_meas[kpwrs[i]][0])
            cddd2p5s.append(pwr_meas[kpwrs[i]][1])        
#            print ("v VDDD2P5", chip, vddd2p5s[chip], v2p5[0], v2p5[1])
#            print ("C VDDD2P5", chip, cddd2p5s[chip], cd2p5[0], cd2p5[1])

            if not ((vddd2p5s[chip] >= v2p5[0] )  and (vddd2p5s[chip] <= v2p5[1] ) ):
                if chip not in bads:
                    bads.append(chip)
                    print ("ADC v VDDD2P5", chip, vddd2p5s[chip], v2p5[0], v2p5[1])
            if not ((cddd2p5s[chip] >= cd2p5[0] ) and (cddd2p5s[chip] <= cd2p5[1] )) :
                if chip not in bads:
                    bads.append(chip)
                    print ("ADC C VDDD2P5", chip, cddd2p5s[chip], cd2p5[0], cd2p5[1])
    return bads
    

def dat_initchk(fdir="/."):
    fp = fdir + "QC_INIT_CHK" + ".bin"
    with open(fp, 'rb') as fn:
        data = pickle.load( fn)
    
    dkeys = list(data.keys())
    
    logsd = data["logs"]

    QCstatus = data["QCstatus"]

    if "Code#E001" in QCstatus:
        return QCstatus, [0,1,2,3,4,5,6,7]
    if "Code#E002" in QCstatus:
        return QCstatus, sorted(data["FE_Fail"])
    if "Code#E003" in QCstatus:
        return QCstatus, sorted(data["FE_Fail"])
    if "Code#E005" in QCstatus:
        return QCstatus, sorted(data["FE_Fail"])


    if "Code#E101" in QCstatus:
        return QCstatus, [0,1,2,3,4,5,6,7]
    if "Code#E102" in QCstatus:
        return QCstatus, sorted(data["CD_Fail"])
#    if "Code#W103" in QCstatus:
#        return QCstatus, sorted(data["CD_Fail"])
    if "Code#E105" in QCstatus:
        return QCstatus, sorted(data["CD_Fail"])


    if "Code#E201" in QCstatus:
        return QCstatus, [0,1,2,3,4,5,6,7]
    if "Code#E202" in QCstatus:
        return QCstatus, sorted(data["ADC_Fail"])
#    if "Code#W103" in QCstatus:
#        return QCstatus, sorted(data["ADC_Fail"])
    if "Code#E205" in QCstatus:
        return QCstatus, sorted(data["ADC_Fail"])


    if "Code#W004" in QCstatus or "Code#W104" in QCstatus or "Code#W204" in QCstatus:
        bads = []
        datakeys = list(data.keys())
        vkeys = []
        for onekey in datakeys:
            if "DIRECT_" in onekey or "ASICDAC_" in onekey :
                vkeys.append(onekey)
        for onekey in vkeys:
            cfgdata = data[onekey]
            fembs = cfgdata[0]
            rawdata = cfgdata[1]
            cfg_info = cfgdata[2]

            bads0 = []
            bads1 = []
            bads2 = []
            bads3 = []

            if ("DIRECT_PLS_CHK" in onekey) :
                bads0 = ana_res2(fembs, rawdata, par=[3000,10000], rmsr=[2.5,50], pedr=[300,3000] , period=512)
            if ("ASICDAC_CALI_CHK" in onekey):
                bads0 = ana_res2(fembs, rawdata, par=[7000,10000], rmsr=[3,50], pedr=[100,3000] , period=500)
            if ("ASICDAC_47mV_CHK" in onekey) and ("ASICDAC_47mV_CHK_x10" not in onekey) and ("ASICDAC_47mV_CHK_x18" not in onekey):
                bads0 = ana_res2(fembs, rawdata, par=[5500,7500], rmsr=[2,50], pedr=[300,3000] , period=500)
            if ("ASICDAC_47mV_CHK_x10" in onekey):
                bads0 = ana_res2(fembs, rawdata, par=[2000,4000], rmsr=[2,50], pedr=[300,3000] , period=500)
            if ("ASICDAC_47mV_CHK_x18" in onekey):
                bads0 = ana_res2(fembs, rawdata, par=[3500,5500], rmsr=[2,50], pedr=[300,3000] , period=500)
            if ("DIRECT_PLS_RMS" in onekey) :
                bads0 = ana_res2(fembs, rawdata, par=[0000,1000], rmsr=[3,30], pedr=[300,3000] , period=512)
            if ("ASICDAC_CALI_RMS" in onekey):
                bads0 = ana_res2(fembs, rawdata, par=[0000,1000], rmsr=[3,30], pedr=[100,3000] , period=500)
            if ("ASICDAC_47mV_RMS" in onekey):
                bads0 = ana_res2(fembs, rawdata, par=[000,1000], rmsr=[2,10], pedr=[300,3000] , period=500)

            if ("DIRECT_PLS_CHK" in onekey) :
                pwr_meas_fe = cfgdata[3]
                pwr_meas_adc = cfgdata[4]
                pwr_meas_cd = cfgdata[5]
                bads1 = ana_fepwr2(pwr_meas_fe, vin=[1.7,1.95], cdda=[10,25], cddp=[25,35], cddo=[-0.1,5])
                bads2 = ana_adcpwr(pwr_meas_adc, v2p5 = [2.10, 2.35], v1p2 = [1.05, 1.15], ca2p5=[115,145], cd1p2=[0,5], cio= [10,25], cd2p5 = [3,10])
                bads3 = ana_cdpwr(pwr_meas_cd, vddfe = [1.7, 1.95], v1p1 = [1.15, 1.25], vddio = [2.15, 2.35], cdda = [7, 11], cddfe = [-1, 1], cddcore = [8, 13], cddd = [15, 25], cddio = [60, 75])
            elif  ("ASICDAC_CALI_CHK" in onekey):
                pwr_meas_fe = cfgdata[3]
                pwr_meas_adc = cfgdata[4]
                pwr_meas_cd = cfgdata[5]
                bads1 = ana_fepwr2(pwr_meas_fe, vin=[1.60,1.8], cdda=[40,60], cddp=[25,35], cddo=[5,15])
                bads2 = ana_adcpwr(pwr_meas_adc, v2p5 = [2.10, 2.35], v1p2 = [1.05, 1.15], ca2p5=[115,145], cd1p2=[0,5], cio= [10,25], cd2p5 = [3,10])
                bads3 = ana_cdpwr(pwr_meas_cd, vddfe = [1.6, 1.8], v1p1 = [1.15, 1.25], vddio = [2.15, 2.35], cdda = [7, 11], cddfe = [-1, 1], cddcore = [8, 13], cddd = [15, 25], cddio = [60, 75])

            print(onekey, 'Bads0_Pulse = {} \t Bads1_FE_Power = {}\t Bads1_ADC_Power = {}\t Bads1_CD_Power = {}'.format(bads0, bads1, bads2, bads3))

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

    if "Code#P001" in QCstatus :
        return QCstatus, []

if __name__=="__main__":
    #fdir = '''D:\DAT_CD_QC\Tested\Time_20241015202741_DUT_1000_2000\RT_CD_031702417_031752417/'''
    fdir = '''D:\DAT_LArASIC_QC\Tested\Time_20241205140938_DUT_1000_2000_3000_4000_5000_6000_7000_8000\RT_FE_001000001_001000002_001000003_001000004_001000005_001000006_001000007_001000008/'''
    fdir = '''D:/DAT_CD_QC/Tested/Time_20241205160750_DUT_1000_2000/RT_CD_031712417_031882417/'''
    fdir = '''D:\DAT_ColdADC_QC\\RT_ADC_000100001_000100002_000100003_000100004_000100005_000100006_000100007_000100008/'''
#    fdir = '''D:\DAT_LArASIC_QC\Tested\Time_20250102143601_DUT_1000_2000_3000_4000_5000_6000_7000_8000\RT_FE_001000001_001000002_001000003_001000004_001000005_001000006_001000007_001000008/'''
    fdir = '''D:\DAT_LArASIC_QC\Tested\Time_20250116211125_DUT_1000_2000_3000_4000_5000_6000_7000_8000\LN_FE_001000001_001000002_001000003_001000004_001000005_001000006_001000007_001000008/'''
    fdir = '''C:\SGAO\ColdTest\Tested\DAT_LArASIC_QC\B006T0001\Time_20250926173225_DUT_0001_0001_0001_0001_0001_0001_0001_0001\RT_FE_006002301_006002301_006002301_006002301_006002301_006002301_006002301_006002301/'''
    print (fdir)
    #QCstatus, bads = dat_initchk(fdir=fdir)
    print (  dat_initchk(fdir=fdir))


    #print (QCstatus)
    #print (bads)


