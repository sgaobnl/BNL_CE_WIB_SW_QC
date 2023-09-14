import time
import sys
import numpy as np
import pickle
import copy
import time, datetime, random, statistics    
from dat_cfg import DAT_CFGS
                
dat =  DAT_CFGS()
dat.fembs = [0]

adac_pls_en, sts, swdac, dac = dat.dat_cali_source(cali_mode=3)
cfg_info = dat.dat_fe_qc_cfg(adac_pls_en=adac_pls_en, sts=sts, swdac=swdac, dac=dac)
dat.dat_coldadc_cali_cs()
dat.dat_set_dac(0, adc=1) #set ADC_N to 0 V

t0 = time.time_ns()

datad = {}
for i in range(1000):
    dat.dat_set_dac(i*0.001, adc=0)
    data =  dat.dat_fe_qc_acq(1)
    datad["ColdADC_DAC%06d"%i] = [dat.fembs, data, i]
t1 = time.time_ns()
print (t1-t0)

if False:
    fdir = "./tmp_data/"
    fp = fdir + "QC_ColdADC.bin"
    with open(fp, 'wb') as fn:
        pickle.dump(datad, fn)


