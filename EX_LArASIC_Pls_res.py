import time
import sys
import numpy as np
import pickle
import copy
import time, datetime, random, statistics    
from dat_cfg import DAT_CFGS
                
dat =  DAT_CFGS()
dat.fembs = [0]
cycle_times = 8

datad = {}

dat.wib_pwr_on_dat() #turn DAT on

print ("Using FE-ASIC DAC pulser...")
adac_pls_en, sts, swdac, dac = dat.dat_cali_source(cali_mode=2,asicdac=0x10)
rawdata = dat.dat_fe_qc(adac_pls_en=adac_pls_en, sts=sts, swdac=swdac, dac=dac,snc=0, sdd=0, sdf=0, slk0=0, slk1=0) #900mV, 500pA, SDD off, SDF off, ASIC-DAC
datad["ASICDAC_CALI"] = [rawdata, fes_pwr_info, adcs_pwr_info, cds_pwr_info]

print ("Using DAT DAC (common) pulser...")
adac_pls_en, sts, swdac, dac = dat.dat_cali_source(cali_mode=1, val=1.0, period=500, width=400)
rawdata = dat.dat_fe_qc(adac_pls_en=adac_pls_en, sts=sts, swdac=swdac, dac=dac,snc=1, sdd=0, sdf=0 ) #200mV, 500pA, SDD off, SDF off, DAT-DAC
datad["DATDAC_CALI"] = [rawdata, fes_pwr_info, adcs_pwr_info, cds_pwr_info]

print ("Using Direct-Input (common) pulser...")
adac_pls_en, sts, swdac, dac = dat.dat_cali_source(cali_mode=0, val=1.5, period=500, width=400)
rawdata = dat.dat_fe_qc(adac_pls_en=adac_pls_en, sts=sts, swdac=swdac, dac=dac, snc=1, sdd=0, sdf=0 ) #200mV, 500pA, SDD off, SDF off, Direct-input
datad["Direct_CALI"] = [rawdata, fes_pwr_info, adcs_pwr_info, cds_pwr_info]

fdir = "./tmp_data/"
fp = fdir + "EX_CALI_MODE" + ".bin"
with open(fp, 'wb') as fn:
    pickle.dump(datad, fn)

