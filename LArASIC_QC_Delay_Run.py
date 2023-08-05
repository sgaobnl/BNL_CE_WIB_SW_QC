import time
import sys
import numpy as np
import pickle
import copy
import time, datetime, random, statistics    
from dat_cfg import DAT_CFGS
                
dat =  DAT_CFGS()
dat.fembs = [0]
datad = {}

period = 1000
width = 800
val = 1.4
adac_pls_en, sts, swdac, dac = dat.dat_cali_source(cali_mode=1, val=val, period=period, width=width)
cfg_info = dat.dat_fe_qc_cfg(adac_pls_en=adac_pls_en, sts=sts, swdac=swdac, dac=dac) 

QCdata = {}
for phase in range(0,32,1):
    dat.cdpoke(0, 0xC, 0, dat.DAT_TEST_PULSE_DELAY, phase%32)  #cali input
    time.sleep(0.1)
    data = dat.dat_fe_qc_acq(num_samples = 5)
    QCdata["Phase%04d_freq%04d"%(phase, period)] = data

fdir = "./tmp_data/"
fp = fdir + "QC_DLY_RUN" + ".bin"
with open(fp, 'wb') as fn:
    pickle.dump(QCdata, fn)

