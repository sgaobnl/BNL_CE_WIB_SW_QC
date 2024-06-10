# -*- coding: utf-8 -*-
"""
Created on Mon Sep  9 11:17:56 2019

@author: Edoardo Lopriore
"""
# This file generates FFT and PSD (Power Spectral Density) calculations from sinewave inputs from DS360 Stanford Generator. 
# Input: reference.
# SFDR is calculated by dividing the signal power bins by the highest-amplitude spurious bins.
# SINAD is calculated by dividing the signal power bins by every noise and harmonic distortion bins. 
# ENOB is calculated with correction factor (Vfullscale/Vinput). We cannot use full-range sinewaves because of ColdADC overflowing issue. See MT-003 tutorial by Analog Devices for more information on this.
# Output: PSD plots (relative to full scale) with calculated ENOB, SFDR, SINAD. Values for ENOB are saved in Channel Characterization tables.

import numpy as np
import os
import sys
import os.path
import matplotlib.pyplot as plt
from scipy.fftpack import fft,rfft,ifft,fftn


def chn_rfft_psd(chndata, fs = 2000000.0, fft_s = 2000, avg_cycle = 50):  
    #Averaged RFFT and Power Spectral Density calculations
    ts = 1.0/fs 
    len_chndata = len(chndata)
    avg_cycle_tmp = avg_cycle
    if ( len_chndata >= fft_s * avg_cycle_tmp):
        pass
    else:
        avg_cycle_tmp = (len_chndata//fft_s)

    p = np.array([])
    for i in range(0,avg_cycle_tmp,1):
        x = chndata[i*fft_s:(i+1)*fft_s]
        if ( i == 0 ):
            #FFT computing and normalization
            p = abs(rfft(x)/fft_s)**2     
        else:
            p = p + (abs(rfft(x)/fft_s))**2   
    #PSD calculation
    psd = p / avg_cycle_tmp
    psd = p / ( fs/fft_s)
    psd = p*2
    f = np.linspace(0,fs/2,len(psd))
    psd = 10*np.log10(psd)
    return f,p,psd

def adc_enob(chndata, fs,  avg_cycle=50, Ntot=2**12,trunc=20, Vfullscale=1.4, Vinput=1.3, ffig= False):
    f, p, psd = chn_rfft_psd(chndata=chndata, fs = fs, fft_s = Ntot, avg_cycle = avg_cycle)
    #fig = plt.figure(figsize=(10,8))
    #plt.rcParams.update({'font.size': 18})
    #plt.plot(f,p)
    #plt.show()
    #plt.close()

    #Truncate DC and Nyquist bins
    #trunc = 20
    #Ntot = 2**(12)
    p = p[trunc:Ntot-trunc]
    f = f[trunc:Ntot-trunc]

    #Span three bins at side of fundamental to calculate signal power
    p_aux = np.copy(p)
    noise = min(p)
    mx_arr = np.where(p_aux == max(p_aux))
    mx = mx_arr[0][0]
    signal_pwr = max(p_aux)
    span = 3
    p_aux[mx] = noise
    for k in range(1, span+1):
        signal_pwr = signal_pwr + p[mx+k] + p[mx-k]
        p_aux[mx+k] = noise
        p_aux[mx-k] = noise
    
    ##### Extract parameters of interest #####
    NAD = np.sum(p) - signal_pwr
    SINAD = 10*np.log10( signal_pwr / NAD )
    ENOB = (SINAD - 1.76 + 20*np.log10(Vfullscale/Vinput)) / 6.02
    print (SINAD, ENOB, NAD, 20*np.log10(Vfullscale/Vinput), Vfullscale, Vinput)
    
    fundamental = max(p)
    SFDR = 10*np.log10( fundamental / max(p_aux))
    
    ##### Plot normalized power spectral density in dBFS #####
    psd = psd[trunc:Ntot-trunc]
    psd_dbfs = psd - max(psd) - 20*np.log10(Vfullscale/Vinput)
    #points_dbfs = np.linspace(0,fs/2, len(psd_dbfs))
    points_dbfs = f

    if ffig:
        fig = plt.figure(figsize=(10,8))
        plt.rcParams.update({'font.size': 18})
        #plt.plot(points_dbfs, psd_dbfs)
        plt.plot(f, psd_dbfs)
        #plt.title('%s Environment. %s Reference. Channel %d'%(env, refs,chnno))
        plt.xlabel('Frequency [Hz]')
        plt.ylabel('Amplitude [dBFS]')
        plt.annotate('SFDR = %0.2f dB \nSINAD = %0.2f dB \nENOB = %0.2f bits' %(np.around(SFDR, decimals=2), np.around(SINAD, decimals=2), np.around(ENOB, decimals = 2)), 
                     xy=(0.6,0.8),xycoords='axes fraction', textcoords='offset points', size=22, bbox=dict(boxstyle="round", fc=(1.0, 1.0, 1.0), ec="none"))
        
        plt.tight_layout()
        #figure_name =  enob_dir + "ENOB_%s_%s_ch%d"%(env,refs,chnno) + ".png" 
        #print (figure_name)
        #plt.savefig(figure_name)
        plt.show()
        plt.close()  
    return  ENOB, NAD, SFDR, SINAD, psd_dbfs, points_dbfs

##### Parameters for ENOB Calculation #####
#Ntot = 2**(11)
#avgs = 50
#Nsamps = (avgs+2)*Ntot

