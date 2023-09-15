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

histo = []
for x in range(pow(2,16)):
    histo.append(0)
histo128s = []
for x in range(128):
    histo128s.append(histo)

t0 = time.time_ns()

#for valint in range(pow(2,16)):
for valint in range(100,10000, 100):
    dat.dat_set_dac(valint, adc=0)
    wibdata =  dat.dat_adc_qc_acq(1)
    for ch in range(128):
        for addr in wibdata[ch]:
            histo128s[ch][addr] = histo128s[ch][addr] + 1

datad = {}
datad["ColdADC_HISTO"] = histo128s 
t1 = time.time_ns()
print (t1-t0)

if False:
    fdir = "./tmp_data/"
    fp = fdir + "QC_ColdADC.bin"
    with open(fp, 'wb') as fn:
        pickle.dump(datad, fn)


