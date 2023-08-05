import time
import sys
import numpy as np
import pickle
import copy
import time, datetime, random, statistics    
from dat_cfg import DAT_CFGS
                
dat =  DAT_CFGS()
dat.fembs = [0]

adac_pls_en, sts, swdac, dac = dat.dat_cali_source(cali_mode=0, val=1.53, period=500, width=400)
rawdata = dat.dat_fe_qc(adac_pls_en=adac_pls_en, sts=sts, swdac=swdac, dac=dac, snc=1, sdd=0, sdf=0 ) #200mV, 500pA, SDD off, SDF off, Direct-input
fdir = "./tmp_data/"
datad = {}
datad["CHK"] = [dat.fembs, rawdata]

fp = fdir + "QC_CHK.bin"
with open(fp, 'wb') as fn:
    pickle.dump(datad, fn)

