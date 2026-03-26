import sys 
import numpy as np
import pickle
import time, datetime, random, statistics
import matplotlib.pyplot as plt
import copy

import struct
from spymemory_decode import wib_dec

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
fembs = [1]

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
    pkp  = []
    for fe in range(8):
        for fe_chn in range(16):
    
            fechndata = datd[fe*16+fe_chn]
            rms.append(np.std(fechndata))
#    plt.plot(np.arange(64),rms[0:64], marker = '.', color='b', label="left")
#    plt.plot(np.arange(64,128,1),rms[64:128], marker = '.',color='r', label="right")
#    plt.legend()
#    plt.grid()
#    
#    plt.title("Noise distribution")
#    plt.ylabel("RMS noise / bit")
#    #plt.ylim((5,25))
#    plt.xlabel("Channel")
#    plt.tight_layout( rect=[0.05, 0.05, 0.95, 0.95])
#    plt.show()
#    plt.close()
#    if 'n' in input ("Would you like to check FFT plot? y/n : "):
#        exit()
#    else:
#        print ("It takes a few minutes to analyze data, keep patient :)")

print ("It takes a few minutes to analyze data, keep patient :)")

from fft_chn import chn_rfft_psd
wibdata = wib_dec(rawdata,fembs, spy_num=100)

while True:

    if True:
        print ("please view noise distribution and record a few channels you would like to check FFT plots")

        plt.plot(np.arange(64),rms[0:64], marker = '.', color='b', label="left")
        plt.plot(np.arange(64,128,1),rms[64:128], marker = '.',color='r', label="right")
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
        f,p = chn_rfft_psd(fechndata,  fft_s = 5000, avg_cycle = 50)
        plt.plot(f,p, label="CH%d"%ch, color='C%d'%(ch%10))
    plt.legend()
    plt.title("FFT ")
    plt.grid()
    plt.ylabel(" / dB ")
    plt.xlabel("Freq / Hz")
    plt.show()
    plt.close()

    
