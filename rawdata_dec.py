import sys 
import numpy as np
import pickle
import time,  random, statistics
from datetime import datetime
import matplotlib.pyplot as plt
import copy
import os
import struct
from spymemory_decode import wib_spy_dec_syn

def rawdata_dec (raw, runs=1, plot_show_en = False, plot_fn = "./pulse_respons.png", rms_flg = False, chdat_flg=False,  ts_flg = False):
        
    rawdata = raw[0]
    pwr_meas = raw[1]
    crate_runs = []
    for runi in range(runs):
        print ("RUN%03d"%runi)
        dec_datas = []
        buf0 = rawdata[runi][0][0]
        buf1 = rawdata[runi][0][1]
        trigmode = "SW"
        buf_end_addr = 0 
        trigger_rec_ticks = 0x3f000 
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
            for i in range(flen-10):
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
    wib_num = 1
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
   

    x = np.arange(wib_num*4*128)
    fig = plt.figure(figsize=(14,8))
    plt.rcParams.update({'font.size':12})
    if rms_flg :
        plt.subplot(211)
    else:
        plt.subplot(111)
    plt.plot(x, chmax, marker='.',color='r', label = "pp")
    plt.plot(x, chped, marker='.',color='b',  label = "ped")
    plt.plot(x, chmin, marker='.',color='g',  label = "np")
    for tmpx in range(4):
        plt.axvline(x=tmpx*128, color = 'r', linestyle='--')


    plt.legend()
    #plt.title ("Pulse Distribution @ UTC:" + t0_str)
    plt.title ("Pulse Distribution")
    plt.xlabel ("CH#")
    plt.ylabel ("ADC / bit" )
    plt.grid()

    if rms_flg :
        plt.subplot(212)
        plt.plot(x, chrms, marker='.',color='r', label = "RMS")
        for tmpx in range(4):
            plt.axvline(x=tmpx*128, color = 'r', linestyle='--')

        plt.legend()
        #plt.title ("RMS Noise Distribution @ UTC:" + t0_str)
        plt.title ("RMS Noise Distribution ")
        plt.xlabel ("CH# ")
        plt.ylabel ("ADC RMS Noise / bit" )
        plt.ylim((0,100))
        plt.grid()

    plt.tight_layout()
    if plot_show_en:
        plt.show()
    else:
        plt.savefig(plot_fn)
    plt.close()
    if chdat_flg:
     if ts_flg:
         return [chns_data, tmts_wibs]
     else:
         return chns_data
 
