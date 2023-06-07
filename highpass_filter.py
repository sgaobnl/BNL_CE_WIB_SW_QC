# -*- coding: utf-8 -*-
"""
File Name: init_femb.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 7/15/2016 11:47:39 AM
Last modified: Mon Nov 27 09:29:21 2017
"""

#defaut setting for scientific caculation
#import numpy
#import scipy
#from numpy import *
#import numpy as np
#import scipy as sp
#import pylab as pl
import numpy as np
import struct
import os
from sys import exit
import os.path
import math
#import statsmodels.api as sm

from scipy import signal

def hp_FIR_applied(pre_flt_data, fs = 2000000, flt_stopfreq = 300, flt_passfreq = 600, flt_order = 1):
  # High-pass filter
  nyquist_rate = fs / 2.0
  desired = (0, 0, 1, 1)
  bands = (0, flt_stopfreq, flt_passfreq, nyquist_rate)
  flt_coefs = signal.firls(flt_order, bands, desired, nyq=nyquist_rate)
  freq, response = signal.freqz(flt_coefs)
#  return freq, response
  # Apply high-pass filter
  post_flt_data = signal.filtfilt(flt_coefs, [1], pre_flt_data)
  return post_flt_data

def butter_hp_flt(fs = 2000000, passfreq = 500, flt_order = 3):
  # bandstop filter
  nyquist_rate = fs / 2.0
  wn = passfreq/nyquist_rate
  b, a = signal.butter(N=flt_order, Wn=wn, btype='highpass')
  return b, a

def butter_bandstop_flt(fs = 2000000, stopfreq = 300, passfreq = 600, flt_order = 2):
  # bandstop filter
  nyquist_rate = fs / 2.0
  wn = [stopfreq/nyquist_rate, passfreq/nyquist_rate]
  b, a = signal.butter(N=flt_order, Wn=wn, btype='bandstop')
  return b, a

def hp_flt_applied(smp_data, fs = 2000000, passfreq = 500, flt_order = 3):
    b,a = butter_hp_flt(fs, passfreq, flt_order)
    w, h = signal.freqz(b,a, worN= int(fs/2))
    p_paras = [passfreq, flt_order, w, abs(h)]
    p_flt_data = signal.filtfilt(b,a, smp_data)
    return p_flt_data

