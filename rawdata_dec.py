import sys 
import numpy as np
import pickle
import time,  random, statistics
from datetime import datetime
import matplotlib.pyplot as plt
import copy
import os
import struct
from tools import Tools
from spymemory_decode import wib_spy_dec_syn

def rawdata_dec (raw, runs=1, plot_show_en = False, plot_fn = "./pulse_respons.png", rms_flg = False, chdat_flg=False, femb_plt_sq = False, ts_flg = False):
    tl=Tools()
    rawdata = raw[0]
    pwr_meas = raw[1]
    crate_runs = []
    for runi in range(runs):
        print ("RUN%03d"%runi)
        dec_datas = []
        for wibdata in rawdata[runi]:
            ip = wibdata[0]
            buf0 = wibdata[1][0]
            buf1 = wibdata[1][1]
            trigmode = "HW"
            buf_end_addr = wibdata[2] 
            trigger_rec_ticks = wibdata[3]
            dec_data = wib_spy_dec_syn(buf0, buf1, trigmode, buf_end_addr, trigger_rec_ticks)
            dec_datas.append(dec_data)
    
        crate = []
        wibi = 0
        for wib_data in dec_datas:
            
            flen = len(wib_data[0])
            
            tmts = []
            sfs0 = []
            sfs1 = []
            cdts_l0 = []
            cdts_l1 = []
            femb0 = []
            femb1 = []
            femb2 = []
            femb3 = []
            for i in range(flen):
                tmts.append(wib_data[0][i]["TMTS"])
                sfs0.append(wib_data[0][i]["FEMB_SF"])
                sfs1.append(wib_data[1][i]["FEMB_SF"])
                cdts_l0.append(wib_data[0][i]["FEMB_CDTS"])
                cdts_l1.append(wib_data[1][i]["FEMB_CDTS"])
                femb0.append(wib_data[0][i]["FEMB0_2"])
                femb1.append(wib_data[0][i]["FEMB1_3"])
                femb2.append(wib_data[1][i]["FEMB0_2"])
                femb3.append(wib_data[1][i]["FEMB1_3"])
            
            femb0 = list(zip(*femb0))
            femb1 = list(zip(*femb1))
            femb2 = list(zip(*femb2))
            femb3 = list(zip(*femb3))
            
            wibs = [femb0, femb1, femb2, femb3, tmts]
            crate.append(wibs)
            
            T0 = tmts[0]*512
            dt = datetime.utcfromtimestamp(T0 / 1000000000)
            t0_str = dt.strftime('%Y-%m-%d %H:%M:%S.%f')
        crate_runs.append(crate)
    
    chns_data =[]
    tmts_wibs =[]
    wib_num = 3
    femb_num = 4
    for wibi in  range(wib_num):
        tmts_wibs.append([])
        for fembi in  range(femb_num):
            for ch in range(128):
                chns_data.append([])
    
    for runi in range(runs):
        for wibi in  range(wib_num):
            tmts_wibs[wibi] += crate_runs[runi][wibi][4]
            for fembi in  range(femb_num):
                for ch in range(128):
                    chns_data[wibi*512 + fembi*128 + ch] += crate_runs[runi][wibi][fembi][ch]
    if chdat_flg:
        if ts_flg:
            return [chns_data, tmts_wibs]
        else:
            return chns_data
#    chrms = np.std(chns_data, axis=(1)) 
#    chped = np.mean(chns_data, axis=(1)) 
#    chmax = np.max(chns_data, axis=(1)) 
#    chmin = np.min(chns_data, axis=(1)) 
    chped = []
    chmax = []
    chmin = []
    chrms = []
    for ch in range(len(chns_data)):
        if ch == 0:
            print (len((chns_data[ch])))
        chn_max = np.max(chns_data[ch])
        chn_max_pos = np.where(chns_data[ch] == chn_max)[0][0]
        chmax.append(np.max(chns_data[ch]))
        chped.append(np.mean(chns_data[ch]))
        chmin.append(np.min(chns_data[ch]))
        if (chn_max_pos > 100) and (chn_max_pos < len(chns_data[ch])-100):
            chdata = chns_data[ch][0:chn_max_pos-50] + chns_data[ch][chn_max_pos+200:] 
        else:
            chdata = chns_data[ch][200:-200] 
        chrms.append(np.std(chdata))
   
    uplanerms = np.zeros(476)
    vplanerms = np.zeros(476)
    xplanerms = np.zeros(584)
    uplanemax = np.zeros(476)
    vplanemax = np.zeros(476)
    xplanemax = np.zeros(584)
    uplanemin = np.zeros(476)
    vplanemin = np.zeros(476)
    xplanemin = np.zeros(584)
    uplaneped = np.zeros(476)
    vplaneped = np.zeros(476)
    xplaneped = np.zeros(584)

    for i in range(wib_num*4*128):
        nfemb = i//128 + 1
        nch = i %128
    
        dfmap = tl.LoadMap(nfemb)
        plane,strip = tl.FindStrips(dfmap, nfemb, nch)
        #print(i, plane, strip)
    
        if plane==1:
           uplanerms[strip-1]=chrms[i]
           uplaneped[strip-1]=chped[i]
           uplanemax[strip-1]=chmax[i]
           uplanemin[strip-1]=chmin[i]
        if plane==2:
           vplanerms[strip-1]=chrms[i]
           vplaneped[strip-1]=chped[i]
           vplanemax[strip-1]=chmax[i]
           vplanemin[strip-1]=chmin[i]
        if plane==3:
           xplanerms[strip-1]=chrms[i]
           xplaneped[strip-1]=chped[i]
           xplanemax[strip-1]=chmax[i]
           xplanemin[strip-1]=chmin[i]


    ch_rms_map = np.concatenate((uplanerms,vplanerms,xplanerms)) 
    ch_ped_map = np.concatenate((uplaneped,vplaneped,xplaneped)) 
    ch_max_map = np.concatenate((uplanemax,vplanemax,xplanemax)) 
    ch_min_map = np.concatenate((uplanemin,vplanemin,xplanemin)) 

    print ("UTC: " + t0_str )
    x = np.arange(wib_num*4*128)
    fig = plt.figure(figsize=(14,8))
    plt.rcParams.update({'font.size':12})
    if rms_flg :
        plt.subplot(221)
    else:
        plt.subplot(111)
    if femb_plt_sq:
        plt.plot(x, chmax, marker='.',color='r', label = "pp")
        plt.plot(x, chped, marker='.',color='b',  label = "ped")
        plt.plot(x, chmin, marker='.',color='g',  label = "np")
        for tmpx in range(12):
            plt.axvline(x=tmpx*128, color = 'r', linestyle='--')

    else:
        plt.plot(x, ch_max_map, marker='.',color='r', label = "pp")
        plt.plot(x, ch_ped_map, marker='.',color='b',  label = "ped")
        plt.plot(x, ch_min_map, marker='.',color='g',  label = "np")
        plt.axvline(x=475, color = 'r', linestyle='--')
        plt.axvline(x=951, color = 'r', linestyle='--')


    plt.legend()
    plt.title ("Pulse Distribution @ UTC:" + t0_str)
    plt.xlabel ("CH#")
    plt.ylabel ("ADC / bit" )
    plt.grid()

    if rms_flg :
        plt.subplot(222)
        if femb_plt_sq:
            plt.plot(x, chrms, marker='.',color='r', label = "RMS")
            for tmpx in range(12):
                plt.axvline(x=tmpx*128, color = 'r', linestyle='--')

        else:
            plt.plot(x, ch_rms_map, marker='.',color='r', label = "RMS")
            plt.axvline(x=475, color = 'm', linestyle='--')
            plt.axvline(x=951, color = 'm', linestyle='--')
        plt.legend()
        plt.title ("RMS Noise Distribution @ UTC:" + t0_str)
        plt.xlabel ("CH# (According to CRP mapping)")
        plt.ylabel ("ADC RMS Noise / bit" )
        plt.ylim((0,50))
        plt.grid()

    if rms_flg :
        plt.subplot(223)
        #for chp in range(370, 400, 1):
        #    print (chp, ch_rms_map[chp])
        plt.plot(x, np.array(ch_rms_map)*39, marker='.',color='r', label = "RMS")
        plt.legend()
        plt.title ("ENC Distribution @ UTC:" + t0_str)
        plt.xlabel ("CH# (According to CRP mapping)")
        plt.ylabel ("ENC / e-" )
        plt.ylim((0,2000))
        plt.grid()
        plt.axvline(x=475, color = 'm', linestyle='--')
        plt.axvline(x=951, color = 'm', linestyle='--')

    if rms_flg :
        plt.subplot(224)
        wavelen = len(chns_data[1300])
        x = np.arange(wavelen)
        plt.plot(x, chns_data[1300][0:wavelen], marker='.',color='r', label = "CH1300")
        plt.legend()
        plt.title ("Waveform of CH1300")
        plt.xlabel ("samples #")
        plt.ylabel ("ADC / bit" )
        plt.grid()

        #plt.subplot(224)
        #plt.plot(x, chrms, marker='.',color='r', label = "RMS")
        #plt.legend()
        #plt.title ("RMS Noise Distribution @ UTC:" + t0_str)
        #plt.xlabel ("CH# (According to FEMB mapping)")
        #plt.ylabel ("ADC RMS Noise / bit" )
        #plt.ylim((0,50))
        #plt.grid()
        #for x in range(0, 128*12, 128):
        #    plt.axvline(x=x, color = 'm', linestyle='--')

    plt.tight_layout()
    if plot_show_en:
        plt.show()
    else:
        plt.savefig(plot_fn)
    plt.close()
    return ch_ped_map, ch_max_map, ch_min_map, ch_rms_map
    
#
#plt.title ("Timestamp in WIB data")
#plt.text(0,1000, "T0 = " + t0_str)
#plt.text(0,800, "T0 = %d ns"%T0 )
#plt.xlabel ("Time / $\mu$s")
#plt.ylabel (f"Timestamp ID - T0({tmts[0]})" )
#plt.grid()
#plt.legend()
#plt.show()
#plt.close()
        
#        for fembi in range(4):
#            maxpos = np.where(wibs[fembi][0][0:1500] == np.max(wibs[fembi][0][0:1500]))[0][0]
#            fig = plt.figure(figsize=(10,6))
#            for chip in range(8):
#                for chn in range(16):
#                    i = chip*16 + chn
#                    if chn == 0:
#                        plt.plot(x, wibs[fembi][i],color = 'C%d'%chip, label = "Chip%dCH0"%chip )
#                    else:
#                        plt.plot(x, wibs[fembi][i],color = 'C%d'%chip )
#            plt.title(f"Waveform of FEMB{fembi}")
#            plt.legend()
#            plt.show()
#            plt.close()
#
#maxpos = np.where(crates[0][0][0][0:1500] == np.max(crates[0][0][0][0:1500]))[0][0]
#x = np.arange(20)
#fig = plt.figure(figsize=(10,6))
#plt.rcParams.update({'font.size':12})
#plt.plot(x, crates[0][0][1][maxpos-10: maxpos+10], marker='o', label = "WIB0FEMB0 Ch1")
#plt.plot(x, crates[0][1][1][maxpos-10: maxpos+10], marker='o', label = "WIB0FEMB1 Ch1")
#plt.plot(x, crates[0][2][1][maxpos-10: maxpos+10], marker='o', label = "WIB0FEMB2 Ch1")
#plt.plot(x, crates[0][3][1][maxpos-10: maxpos+10], marker='o', label = "WIB0FEMB3 Ch1")
#plt.plot(x, crates[1][0][1][maxpos-10: maxpos+10], marker='o', label = "WIB1FEMB0 Ch1")
#plt.plot(x, crates[1][1][1][maxpos-10: maxpos+10], marker='o', label = "WIB1FEMB1 Ch1")
#plt.plot(x, crates[1][2][1][maxpos-10: maxpos+10], marker='o', label = "WIB1FEMB2 Ch1")
#plt.plot(x, crates[1][3][1][maxpos-10: maxpos+10], marker='o', label = "WIB1FEMB3 Ch1")
#
#plt.plot(x, crates[0][0][65][maxpos-10: maxpos+10], marker='s', label = "WIB0FEMB0 Ch65")
#plt.plot(x, crates[0][1][65][maxpos-10: maxpos+10], marker='s', label = "WIB0FEMB1 Ch65")
#plt.plot(x, crates[0][2][65][maxpos-10: maxpos+10], marker='s', label = "WIB0FEMB2 Ch65")
#plt.plot(x, crates[0][3][65][maxpos-10: maxpos+10], marker='s', label = "WIB0FEMB3 Ch65")
#plt.plot(x, crates[1][0][65][maxpos-10: maxpos+10], marker='s', label = "WIB1FEMB0 Ch65")
#plt.plot(x, crates[1][1][65][maxpos-10: maxpos+10], marker='s', label = "WIB1FEMB1 Ch65")
#plt.plot(x, crates[1][2][65][maxpos-10: maxpos+10], marker='s', label = "WIB1FEMB2 Ch65")
#plt.plot(x, crates[1][3][65][maxpos-10: maxpos+10], marker='s', label = "WIB1FEMB3 Ch65")
#
#plt.title ("Waveforms")
#plt.xlabel ("Time / $\mu$s")
#plt.ylabel ("ADC / bit" )
#
#plt.legend()
#plt.show()
#plt.close()


#for wibi in range(len(crates)):
#    for fembi in range(4):
#for fembi in range(4):
#    maxpos = np.where(wibs[fembi][0][0:1500] == np.max(wibs[fembi][0][0:1500]))[0][0]
#    fig = plt.figure(figsize=(10,6))
#    plt.plot(x, wibs[fembi][0][maxpos-10: maxpos+10], marker='s', label = f"FEMB{fembi} Ch0")
#    plt.plot(x, wibs[fembi][16][maxpos-10: maxpos+10], marker='o', label = f"FEMB{fembi} Ch16")
#    plt.plot(x, wibs[fembi][32][maxpos-10: maxpos+10], marker='^', label = f"FEMB{fembi} Ch32")
#    plt.plot(x, wibs[fembi][48][maxpos-10: maxpos+10], marker='*', label = f"FEMB{fembi} Ch48")
#    plt.plot(x, wibs[fembi][64][maxpos-10: maxpos+10], marker='>', label = f"FEMB{fembi} Ch64")
#    plt.plot(x, wibs[fembi][80][maxpos-10: maxpos+10], marker='<', label = f"FEMB{fembi} Ch80")
#    plt.plot(x, wibs[fembi][96][maxpos-10: maxpos+10], marker='+', label = f"FEMB{fembi} Ch96")
#    plt.plot(x, wibs[fembi][112][maxpos-10: maxpos+10], marker='.', label = f"FEMB{fembi} Ch112")
#
#    plt.legend()
#    plt.show()
#    plt.close()
#
#fig = plt.figure(figsize=(10,6))
#fembi = 0
#maxpos = np.where(wibs[fembi][0][0:1500] == np.max(wibs[fembi][0][0:1500]))[0][0]
#markers = ['o', '.', '+', '*']
#for fembi in range(4):
#    plt.plot(x, wibs[fembi][0][maxpos-10: maxpos+10],  marker=markers[fembi], label = f"FEMB{fembi} Ch0")
#    plt.plot(x, wibs[fembi][16][maxpos-10: maxpos+10], marker=markers[fembi], label = f"FEMB{fembi} Ch16")
#    plt.plot(x, wibs[fembi][32][maxpos-10: maxpos+10], marker=markers[fembi], label = f"FEMB{fembi} Ch32")
#    plt.plot(x, wibs[fembi][48][maxpos-10: maxpos+10], marker=markers[fembi], label = f"FEMB{fembi} Ch48")
#    plt.plot(x, wibs[fembi][64][maxpos-10: maxpos+10], marker=markers[fembi], label = f"FEMB{fembi} Ch64")
#    plt.plot(x, wibs[fembi][80][maxpos-10: maxpos+10], marker=markers[fembi], label = f"FEMB{fembi} Ch80")
#    plt.plot(x, wibs[fembi][96][maxpos-10: maxpos+10], marker=markers[fembi], label = f"FEMB{fembi} Ch96")
#    plt.plot(x, wibs[fembi][112][maxpos-10: maxpos+10], marker=markers[fembi], label = f"FEMB{fembi} Ch112")
#plt.legend()
#plt.show()
#plt.close()
#
#x = np.arange(20)
#fig = plt.figure(figsize=(10,6))
#fembi = 0
#maxpos = np.where(wibs[fembi][0][0:1500] == np.max(wibs[fembi][0][0:1500]))[0][0]
#markers = ['o', '.', '+', '*']
#for fembi in range(4):
#    for chn in range(128):
#        if chn == 0:
#            plt.plot(x, wibs[fembi][chn][maxpos-10: maxpos+10],  marker='.', color = "C%d"%fembi, label = f"FEMB{fembi}")
#        else:
#            plt.plot(x, wibs[fembi][chn][maxpos-10: maxpos+10],  marker='.', color = "C%d"%fembi)
#plt.legend()
#plt.show()
#plt.close()

