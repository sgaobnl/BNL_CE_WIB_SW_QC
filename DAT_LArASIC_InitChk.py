import time
import os
import sys
import numpy as np
import pickle
import copy
import time, datetime
import matplotlib.pyplot as plt
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
    #import matplotlib.pyplot as plt
    for achn in range(128):
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
    #    if True:
    #        plt.plot(conchndata)
    #plt.show()
    #plt.close()

    # # sumdata = np.array(all_data[0][0:period])
    # # for k in range(1,len(all_data[0])//period):
    # #     sumdata +=  np.array(all_data[0][k*period:(k+1)*period])
    # # print ("average the data %d times"%(len(all_data[0])//period))
    # # avgdata = sumdata/(len(all_data[0])//period)
    # # # import matplotlib.pyplot as plt
    # # plt.plot(avgdata, label="Averaging plot")
    # # plt.plot(all_data[0][0:period], label="one period of original waveform")
    # # plt.legend()
    # # #plt.plot(list(avgdata[300:]) + list(avgdata[0:300]) )
    # # plt.show()
    # # plt.close()


    # exit()
#code with issue
#    rmss = []
#    peds = []
#    for achn in chns:
#        arms = 0.0
#        aped = 0.0
#        if rms_flg:
#            aped = np.round(np.mean(all_data[achn]), 4)
#            arms = np.round(np.std(all_data[achn]), 4)
#        else:
#            posmax, pheights = find_peaks(x=all_data[achn], height=0.5*np.max(all_data[achn]))
#            N_pulses = len(posmax)
#            if N_pulses>20:
#                aped = np.round(np.mean(all_data[achn]), 4)
#                arms = np.round(np.std(all_data[achn]), 4)
#            else:
#                tmpdata = np.array([])
#                for ipulse in range(N_pulses):
#                    istart = i*period
#                    iend = posmax[ipulse]-10
#                    if (iend-istart) > 0:
#                        tmpdata = np.concatenate((tmpdata, all_data[achn][istart : iend]))
#                aped = np.round(np.mean(tmpdata), 4)
#                arms = np.round(np.std(tmpdata), 4)
#        rmss.append(arms)
#        peds.append(aped)

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
        #import matplotlib.pyplot as plt
        for iperiod in range(N_period-3):
            #print (p0 + iperiod*period - 250, p0 + iperiod*period - 50, len(all_data[achn][p0 + iperiod*period - 250: p0 + iperiod*period-50]))
            peddata += all_data[achn][p0 + iperiod*period - 250: p0 + iperiod*period-50]
        rmss.append(np.std(peddata))
        peds.append(np.mean(peddata))
        #plt.plot(peddata)
        #continue
    #plt.show()
    #plt.close()

    #if False:
        


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

#    import matplotlib.pyplot as plt
#    for ch in range(128):
#        #if np.max(wfs[ch]) < 6000:
#        if True:
#            print (ch,np.max(wfs[ch]) )
#            plt.plot(wfs[ch])
#    plt.show()
#    plt.close()
    # chns =[]
    # rmss = []
    # peds = []
    # pkps = []
    # pkns = []
    # wfs = []
    # wfsf = []

    # ppos0=0
    # npos0=0
    # ppos64=0
    # npos64=0
    # for achn in range(len(datd)):
    #     chndata = datd[achn]
    #     # import matplotlib.pyplot as plt
    #     for x in range(4):
    #         plt.plot(chndata[x*512+13:(x+1)*512+13])
    #     plt.show()
    #     plt.close()
    #     exit()

    #     amax = np.max(chndata[300:-150])
    #     amin = np.min(chndata[300:-150])
    #     if achn==0:
    #         ppos0 = np.where(chndata[300:-150]==amax)[0][0] + 300
    #         npos0 = np.where(chndata[300:-150]==amin)[0][0] + 300
    #     if achn==64:
    #         ppos64 = np.where(chndata[300:-150]==amax)[0][0] + 300
    #         npos64 = np.where(chndata[300:-150]==amin)[0][0] + 300

    #     if rms_flg:
    #         arms = np.std(chndata)
    #         aped = int(np.mean(chndata))
    #     else:
    #         if achn <64:
    #             arms = np.std(chndata[ppos0-150:ppos0-50])
    #             aped = int(np.mean(chndata[ppos0-150:ppos0-50]))
    #             wfs.append(chndata[ppos0-50:ppos0+150])
    #             wfsf.append(chndata)
    #         else:
    #             arms = np.std(chndata[ppos64-150:ppos64-50])
    #             aped = int(np.mean(chndata[ppos64-150:ppos64-50]))
    #             wfs.append(chndata[ppos64-50:ppos64+150])
    #             wfsf.append(chndata)
    #     chns.append(achn)
    #     rmss.append(arms)
    #     peds.append(aped)
    #     pkps.append(amax)
    #     pkns.append(amin)
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
        #chipamps.remove(maxcamp)
        #chipamps.remove(mincamp)
        meanamp = np.mean(chipamps)
        rmsamp = np.std(chipamps)
        #print (maxcamp, mincamp, meanamp, rmsamp)
        if (abs(maxcamp-meanamp) > 5*rmsamp) or (abs(mincamp-meanamp) > 5*rmsamp ):
            #print ("Error", chip, maxcamp, mincamp, meanamp, rmsamp)
            if chip not in bads:
                bads.append(chip)

    # for tmp in [rmss, peds, amps]:
    # #    for tmp in [rmss] :#, peds, amps]:
    # #    print (np.mean(tmp), np.std(tmp), np.max(tmp), np.min(tmp))

    #     # import matplotlib.pyplot as plt
    #     plt.plot(chns, tmp)
    #     for i in range(0,128,16):
    #         plt.vlines(i-0.5, 0, 100, color='y')

    #     plt.title("Noise", fontsize=8)
    #     # plt.ylim((0,25))
    #     # plt.xlabel("ADC / bit", fontsize=8)
    #     # plt.ylabel("CH number", fontsize=8)
    #     plt.grid()
    #     plt.show()
    #     plt.close()

    for ch in range(len(chns)):
        if (amps[ch] > par[0]) and (amps[ch] < par[1]):
            pass
        else:
            if ch not in badchs:
                badchs.append(ch)
                #print ("par", ch, amps[ch])
            
        if (peds[ch] > pedr[0]) and (peds[ch] < pedr[1]):
            pass
        else:
            if ch not in badchs:
                badchs.append(ch)
                #print ("ped", ch, peds[ch])

        if (rmss[ch] > rmsr[0]) and (rmss[ch] < rmsr[1]):
            pass
        else:
            if ch not in badchs:
                badchs.append(ch)
                #print ("rms", ch, rmss[ch])
    for badch in badchs:
        if (badch//16) not in bads:
            bads.append(badch//16)
    #print (bads)
    #exit()
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
                    #print ("v VDDA", chip, vddas[chip], vin[0], vin[1])
            if not ((cddas[chip] >= cdda[0] ) and (cddas[chip] <= cdda[1] )) :
                if chip not in bads:
                    bads.append(chip)
                    #print ("C VDDA", chip, cddas[chip], cdda[0], cdda[1])

        if "VDDO" in kpwrs[i]:
            vddos.append(pwr_meas[kpwrs[i]][0])
            cddos.append(pwr_meas[kpwrs[i]][1])
            if not ((vddos[chip] >= vin[0] )  and (vddos[chip] <= vin[1] ) ):
                if chip not in bads:
                    bads.append(chip)
                    #print ("v VDDO", chip, vddos[chip], vin[0], vin[1])
            if not ((cddos[chip] >= cddo[0] ) and (cddos[chip] <= cddo[1] )) :
                if chip not in bads:
                    bads.append(chip)
                    #print ("C VDDO", chip, cddos[chip], cddo[0], cddo[1])

        if "VPPP" in kpwrs[i]:
            vddps.append(pwr_meas[kpwrs[i]][0])
            cddps.append(pwr_meas[kpwrs[i]][1])
            if not ((vddps[chip] >= vin[0] )  and (vddps[chip] <= vin[1] ) ):
                if chip not in bads:
                    bads.append(chip)
                    #print ("v VPPP", chip, vddps[chip], vin[0], vin[1])
            if not ((cddps[chip] >= cddp[0] ) and (cddps[chip] <= cddp[1] )) :
                if chip not in bads:
                    bads.append(chip)
                    #print ("C VPPP", chip, cddps[chip], cddp[0], cddp[1])
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

            bads0 = []
            bads1 = []
            if ("DIRECT_PLS_CHK" in onekey) :
                bads0 = ana_res2(fembs, rawdata, par=[7000,12000], rmsr=[5,25], pedr=[500,2000] , period=512)
                bads1 = ana_fepwr2(pwr_meas, vin=[1.7,1.9], cdda=[15,25], cddp=[25,35], cddo=[-0.1,5])
            if ("ASICDAC_CALI_CHK" in onekey):
                bads0 = ana_res2(fembs, rawdata, par=[7000,10000], rmsr=[5,25], pedr=[100,2000] , period=500)
                bads1 = ana_fepwr2(pwr_meas, vin=[1.60,1.8], cdda=[40,50], cddp=[25,35], cddo=[5,15])
            if ("ASICDAC_47mV_CHK" in onekey):
                bads0 = ana_res2(fembs, rawdata, par=[5500,7500], rmsr=[2,10], pedr=[400,2000] , period=500)
                bads1 = ana_fepwr2(pwr_meas, vin=[1.7,1.9], cdda=[15,25], cddp=[25,35], cddo=[-0.1,5])

            if ("DIRECT_PLS_RMS" in onekey) :
                bads0 = ana_res2(fembs, rawdata, par=[0000,1000], rmsr=[5,25], pedr=[500,2000] , period=512)
                bads1 = ana_fepwr2(pwr_meas, vin=[1.7,1.9], cdda=[15,25], cddp=[25,35], cddo=[-0.1,5])
            if ("ASICDAC_CALI_RMS" in onekey):
                bads0 = ana_res2(fembs, rawdata, par=[0000,1000], rmsr=[5,25], pedr=[100,2000] , period=500)
                bads1 = ana_fepwr2(pwr_meas, vin=[1.60,1.8], cdda=[40,50], cddp=[25,35], cddo=[5,15])
            if ("ASICDAC_47mV_RMS" in onekey):
                bads0 = ana_res2(fembs, rawdata, par=[000,1000], rmsr=[2,10], pedr=[400,2000] , period=500)
                bads1 = ana_fepwr2(pwr_meas, vin=[1.7,1.9], cdda=[15,25], cddp=[25,35], cddo=[-0.1,5])
            print('Bads0 = {} \t Bads1 = {}'.format(bads0, bads1))

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
    QCstatus, bads = dat_larasic_initchk(fdir)
    print (QCstatus)
    print (bads)

