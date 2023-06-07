import time
import sys
import numpy as np
import pickle
import copy
import time, datetime, random, statistics
import os
from fft_chn import chn_rfft_psd
from highpass_filter import hp_flt_applied

def noise_a_chn(chnrmsdata, chnno, fft_en = True, fft_s=2000, fft_avg_cycle=50, wibno=0,  fembno=0 ):
    len_chnrmsdata = len(chnrmsdata)
    chnrmsdata = chnrmsdata[0:len_chnrmsdata ]
    rms =  np.std(chnrmsdata[0:10000])
    ped = np.mean(chnrmsdata[0:10000])
    data_slice = chnrmsdata

    avg_cycle_l = 1
    if (len_chnrmsdata >= 400000):
        fft_s_l = 400000//avg_cycle_l
    else:
        fft_s_l =len(chnrmsdata) 

    if (fft_en):
        f,p = chn_rfft_psd(chnrmsdata,  fft_s = fft_s, avg_cycle = fft_avg_cycle)
        f_l, p_l = chn_rfft_psd(chnrmsdata, fft_s = fft_s_l, avg_cycle = avg_cycle_l)
    else:
        f = None
        p = None
        f_l = None
        p_l = None

#   data after highpass filter
    flt_chn_data = hp_flt_applied(chnrmsdata, fs = 1953125, passfreq = 1000, flt_order = 3)
    flt_chn_data = np.array(flt_chn_data) +  ped 
    hfped = ped
    hfrms = np.std(flt_chn_data)
    if (fft_en):
        hff,hfp = chn_rfft_psd(flt_chn_data, fft_s = fft_s, avg_cycle = fft_avg_cycle)
        hff_l,hfp_l = chn_rfft_psd(flt_chn_data, fft_s = fft_s_l, avg_cycle = avg_cycle_l)
    else:
        hff = None
        hfp = None
        hff_l = None
        hfp_l = None
        
    hfdata_slice = flt_chn_data

    chn_noise_paras = [chnno, 
                       rms,   ped,   data_slice, f,  p, f_l, p_l,
                       hfrms, hfped, hfdata_slice, hff, hfp, hff_l, hfp_l]
    return chn_noise_paras


fp = sys.argv[1] 

with open(fp, 'rb') as fn:
    rawdata = pickle.load(fn)

rawdata = rawdata


while True:
    strch =  input("CH: ")
    chn = int(strch)
    
    wibi = chn//512
    fembi = chn//128 + 1
    chi = chn%128


    chrms = []
    for chx in range(4*128):
        chrms.append(np.std(rawdata[chx][0:1000]))
        if np.std(rawdata[chx][0:1000]) > 35:
                print ("Large RMS", chx, np.std(rawdata[chx][0:1000]))


    chnrmsdata= rawdata[chn]
    chninfo = noise_a_chn(chnrmsdata, chnno=chn, fft_en = True, fft_s=2000, fft_avg_cycle=50)
    
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(10,8))
    plt.rcParams.update({'font.size':12})
    plt.subplot(221)
    xlen = 2000
    x = (np.arange(xlen))*512/1000.0
    plt.plot(x, chninfo[3][0:xlen], marker='.',color='r', label = "%d"%chn)
    plt.legend()
    plt.title ("Waveform @ WIB%dFEMB%dCH%d"%(wibi, (fembi%4-1), chi,))
    plt.xlabel ("Time / us")
    plt.ylabel ("ADC / bit" )
    plt.grid()
    
    plt.subplot(222)
    xlen = 200000
    if xlen > len(chninfo[3]):
        xlen = len(chninfo[3])
    x = (np.arange(xlen))*512/1000.0
    plt.plot(x, chninfo[3][0:xlen], marker='.',color='r', label = "%d"%chn)
    print (np.std(chninfo[3][0:2000]), np.std(chninfo[3][0:20000]), len(chninfo[3]))
    plt.legend()
    plt.title ("Waveform @ WIB%dFEMB%dCH%d"%(wibi, (fembi%4-1), chi))
    plt.xlabel ("Time / us")
    plt.ylabel ("ADC / bit" )
    plt.grid()
    
    plt.subplot(223)
    plt.plot(chninfo[4], chninfo[5], marker='.',color='r', label = "%d"%chn)
    plt.legend()
    plt.title ("FFT @ WIB%dFEMB%dCH%d"%(wibi, (fembi%4-1), chi))
    plt.xlabel ("Frequency / Hz")
    plt.ylabel (" / dB" )
    plt.grid()

    plt.subplot(224)
    plt.plot(chninfo[6], chninfo[7], marker='.',color='r', label = "%d"%chn)
    plt.legend()
    plt.title ("FFT @ WIB%dFEMB%dCH%d"%(wibi, (fembi%4-1), chi ))
    plt.xlim((0,30000))
    plt.xlabel ("Frequency / Hz")
    plt.ylabel (" / dB" )
    plt.grid()

    #chrms =  np.std(rawdata, axis=(1)) 
    #chped = np.mean(rawdata, axis=(1)) 
    #chmax =  np.max(rawdata, axis=(1)) 
    #chmin =  np.min(rawdata, axis=(1)) 

    chped = []
    chmax = []
    chmin = []
    chrms = []
    for ch in range(len(rawdata)):
        chmax.append(np.max(rawdata[ch][0:10000]))
        chped.append(np.mean(rawdata[ch][0:10000]))
        chmin.append(np.min(rawdata[ch][0:10000]))
        chrms.append(np.std(rawdata[ch][0:10000]))


#    plt.subplot(224)
#    x = np.arange(12*128)
#    plt.plot(x, ch_rms_map, marker='.',color='r', label = "RMS")
#    plt.legend()
#    plt.title("RMS noise distribution")
#    plt.xlabel ("CH# ")
#    plt.ylim((0,100))
#    plt.ylabel ("ADC / bit" )
#    plt.grid()
#
    plt.tight_layout()
    
    plt.show()
    plt.close()

