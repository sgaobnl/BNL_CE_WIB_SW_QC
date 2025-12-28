# -*- coding: utf-8 -*-
"""
File Name: init_femb.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 7/15/2016 11:47:39 AM
Last modified: 11/22/2018 4:56:59 PM
"""

#defaut setting for scientific caculation
#import numpy
#import scipy
#from numpy import *
#import numpy as np
#import scipy as sp
#import pylab as pl
#from openpyxl import Workbook
import numpy as np
#import struct
#import os
#from sys import exit
#$import os.path
#import matplotlib.pyplot as plt
#from detect_peaks import detect_peaks
from scipy.fftpack import fft,rfft, ifft
#import math

def chn_rfft(chndata, fs = 2000000.0, fft_s = 2000, avg_cycle = 50):  
    ts = 1.0/fs;# sampling interval
    len_chndata = len(chndata)
#    rms =  np.std(chndata)
    avg_cycle_tmp = avg_cycle
    if ( len_chndata >= fft_s * avg_cycle_tmp):
        pass
    else:
        #fft_s = (len_chndata//(avg_cycle_tmp*1000))*1000
        avg_cycle_tmp = (len_chndata//fft_s)

    p = np.array([])
    for i in range(0,avg_cycle_tmp,1):
        x = chndata[i*fft_s:(i+1)*fft_s]
        if ( i == 0 ):
            p = abs(rfft(x)/fft_s)# fft computing and normalization
        else:
            p = p + (abs(rfft(x)/fft_s))# fft computing and normalization
    p = p / avg_cycle_tmp
    f = np.linspace(0,fs/2,len(p))
    p = 20*np.log10(p)
    return f,p

def chn_rfft_psd(chndata, fs = 2000000.0, fft_s = 2000, avg_cycle = 50):  
    ts = 1.0/fs;# sampling interval
    len_chndata = len(chndata)
    avg_cycle_tmp = avg_cycle
#    rms =  np.std(chndata)
    if ( len_chndata >= fft_s * avg_cycle_tmp):
        pass
    else:
        avg_cycle_tmp = (len_chndata//fft_s)
        #fft_s = (len_chndata//(avg_cycle_tmp*1000))*1000

    p = np.array([])
    for i in range(0,avg_cycle_tmp,1):
        x = chndata[i*fft_s:(i+1)*fft_s]
        if ( i == 0 ):
            p = abs(rfft(x)/fft_s)**2# fft computing and normalization
        else:
            p = p + (abs(rfft(x)/fft_s))**2# fft computing and normalization
    p = p / avg_cycle_tmp
    p = p / ( fs/fft_s)
    p = p*2
    f = np.linspace(0,fs/2,len(p))
    p = 10*np.log10(p)
    return f,p

def chn_fft(chndata, fs = 2000000.0, fft_s = 2000, avg_cycle = 50):  
    ts = 1.0/fs;# sampling interval
    len_chndata = len(chndata)
#    rms =  np.std(chndata)
    avg_cycle_tmp = avg_cycle
    if ( len_chndata >= fft_s * avg_cycle_tmp):
        pass
    else:
        avg_cycle_tmp = (len_chndata//fft_s)
        #fft_s = (len_chndata//(avg_cycle_tmp*1000))*1000

    p = np.array([])
    for i in range(0,avg_cycle_tmp,1):
        x = chndata[i*fft_s:(i+1)*fft_s]
        if ( i == 0 ):
            pt = (fft(x)/fft_s)# fft computing and normalization
            p = (np.abs(pt[0:fft_s/2+1]))
        else:
            pt = (fft(x)/fft_s)# fft computing and normalization
            p = p +  (np.abs(pt[0:fft_s/2+1]))
    f = np.linspace(0,fs/2,len(p))
    p = p / avg_cycle_tmp
    p = 20*np.log10(p)
    return f,p


def chn_fft_psd(chndata, fs = 2000000.0, fft_s = 2000, avg_cycle = 50): #power spectral density 
    ts = 1.0/fs;# sampling interval
    len_chndata = len(chndata)
#    rms =  np.std(chndata)
    avg_cycle_tmp = avg_cycle
    if ( len_chndata >= fft_s * avg_cycle_tmp):
        pass
    else:
        avg_cycle_tmp = (len_chndata//fft_s)
        #fft_s = (len_chndata//(avg_cycle_tmp*1000))*1000

    p = np.array([])
    for i in range(0,avg_cycle_tmp,1):
        x = chndata[i*fft_s:(i+1)*fft_s]
        if ( i == 0 ):
            pt = (fft(x)/fft_s)# fft computing and normalization 
            p = (np.abs(pt[0:fft_s/2+1]))**2 # take only positive frequency terms, other half identical# power ~ voltage squared, power in each bin. 
            # p[0] is the dc term
            # p[nfft/2] is the Nyquist term, note that Python 2.X indexing does NOT 
            # include the last element, therefore we need to use 0:nfft/2+1 to have an array
            # that is from 0 to nfft/2
            # p[nfft/2-x] = conjugate(p[nfft/2+x])
        else:
            pt = (fft(x)/fft_s)# fft computing and normalization
            p = p +  (np.abs(pt[0:fft_s/2+1]))**2  
    f = np.linspace(0,fs/2,len(p)) # frequency range of the fft spans from DC (0 Hz) to  Nyquist (Fs/2).
    p = p / avg_cycle_tmp  #averaging
    p = p / ( fs/fft_s)  # power is energy over -fs/2 to fs/2, with nfft bins
    p[1:-1] = 2*p[1:-1] # conserve power since we threw away 1/2 the spectrum 
    # note that DC (0 frequency) and Nyquist term only appear once, we don't double those.
    # Note that Python 2.X array indexing is not inclusive of the last element.
    p = 10*np.log10(p)
    return f,p

