import sys 
import numpy as np
import pickle
import time, datetime, random, statistics
import matplotlib.pyplot as plt
import copy

import struct
from spymemory_decode import wib_dec
from highpass_filter import hp_flt_applied

fp = sys.argv[1]
sfn = fp.split("/") #default
if "/" in fp:
    sfn = fp.split("/")
elif "\\" in fp:
    sfn = fp.split("\\")
p = fp.find(sfn[-1])
fdir = fp[0:p]

with open(fp, 'rb') as fn:
    raw = pickle.load(fn)
    
rawdata = raw[0]
pwr_meas = raw[1]
runi = 0
#fembs = [int(sys.argv[2])]
fembs = [0]

wibdata = wib_dec(rawdata,fembs, spy_num=1)

datd = []
fechndata = []
for i in [0]:
    wibdatai = wibdata[i]
    datd = [wibdatai[0], wibdatai[1],wibdatai[2],wibdatai[3]][fembs[0]]
    for fe in [70//16]:
        for fe_chn in [70%16]:
            fechndata = datd[fe*16+fe_chn]


import matplotlib.pyplot as plt
if 1:
    rms = []
    rms2 = []
    pkp  = []
    for fe in range(8):
    #for fe in [3]:
        for fe_chn in range(16):
    
            fechndata = datd[fe*16+fe_chn]

            rms.append(np.std(fechndata))
            hpfechndata = hp_flt_applied (fechndata, fs=1953125, passfreq=2000, flt_order=3)
            rms2.append(np.std(hpfechndata))
            brdchn = fe*16+fe_chn
            #if fe == 2:
            #if brdchn in [17, 18, 19, 29, 30, 31, 49, 50, 83   ]:
#            if brdchn in [15, 48, 53, 55, 80, 97,122, 121    ]:
            #if True:
#                plt.plot(fechndata[0:2000], label = "%d"%brdchn)
#                plt.plot(hpfechndata[0:2000], label = "%d"%brdchn)
    plt.plot(np.arange(64),rms[0:64], marker = '.', color='b', label="left")
    plt.plot(np.arange(64,128,1),rms[64:128], marker = '.',color='r', label="right")

    plt.plot(np.arange(64),rms2[0:64], marker = '.', color='m', label="left_hpf")
    plt.plot(np.arange(64,128,1),rms2[64:128], marker = '.',color='g', label="right_hpf")

#    plt.legend()
    plt.grid()
#    
    plt.title(sfn[-1])
#    plt.ylabel("RMS noise / bit")
#    #plt.ylim((5,25))
#    plt.xlabel("Channel")
#    plt.tight_layout( rect=[0.05, 0.05, 0.95, 0.95])
    plt.legend()
    plt.show()
    plt.close()
#    if 'n' in input ("Would you like to check FFT plot? y/n : "):
#        exit()
#    else:
#        print ("It takes a few minutes to analyze data, keep patient :)")


print ("It takes a few minutes to analyze data, keep patient :)")

import matplotlib.pyplot as plt
from fft_chn import chn_rfft_psd

while True:

    if True:
        print ("please view noise distribution and record a few channels you would like to check FFT plots")

        plt.plot(np.arange(64),rms[0:64], marker = '.', color='b', label="left")
  #      plt.plot(np.arange(64),rms2[0:64], marker = '.', color='m', label="left")
        plt.plot(np.arange(64,128,1),rms[64:128], marker = '.',color='r', label="right")
  #      plt.plot(np.arange(64,128,1),rms2[64:128], marker = '.',color='g', label="right")
        plt.legend()
        plt.grid()
        
        plt.title("Noise distribution")
        plt.ylabel("RMS noise / bit")
        #plt.ylim((5,25))
        plt.xlabel("Channel")
        plt.tight_layout( rect=[0.05, 0.05, 0.95, 0.95])
        plt.show()
        plt.close()


    if True:
        print("Channel numbers must be between 0 and 127.")
        numbers = input("Enter a list of channel numbers separated by commas (-1 to exit): ").strip()
        if "-1" in numbers:
            exit()

        wibdata = wib_dec(rawdata,fembs, spy_num=100)


        if numbers == "":
            print("Input cannot be empty.")
            continue

        numberstrs = numbers.split(",")

        chns = []
        for astr in numberstrs:
            try:
                x = int(astr)
            except ValueError:
                print (f"{astr} is invalid, ignor")
                continue
            if 0 <= x <= 127:
                chns.append(x)
            else:
                print(f"{x} is out of range and was skipped.")
           

        print("FFT of channels to be plotted:", chns)



    for ch in chns:
        fechndata = []
        for i in range(100):
            wibdatai = wibdata[i]
            datd = [wibdatai[0], wibdatai[1],wibdatai[2],wibdatai[3]][fembs[0]]
            fechndata += datd[ch]
        hpfechndata = hp_flt_applied (fechndata, fs=1953125, passfreq=2000, flt_order=3)
        plt.plot(np.array(fechndata[0:10000])-np.mean(fechndata[0:10000]), color='r')
        plt.plot(hpfechndata[0:10000], color='g')
        #f,p = chn_rfft_psd(fechndata, fs=1953125, fft_s = 5000, avg_cycle = 50)
        #plt.plot(f,p, label="CH%d"%ch, color='C%d'%(ch%10))
    plt.legend()
    plt.title("FFT ")
    plt.grid()
    plt.ylabel(" / dB ")
    plt.xlabel("Freq / Hz")
    plt.show()
    plt.close()

    
