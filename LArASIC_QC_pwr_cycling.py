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

for ci in range(cycle_times):
    dat.dat_pwroff_chk() #make sure DAT is off
    dat.wib_pwr_on_dat() #turn DAT on
    cseti = ci%8
    if cseti == 0:
        adac_pls_en, sts, swdac, dac = dat.dat_cali_source(cali_mode=2,asicdac=0x10)
        rawdata = dat.dat_fe_qc(adac_pls_en=adac_pls_en, sts=sts, swdac=swdac, dac=dac,snc=0, sdd=0, sdf=0, slk0=0, slk1=0) #900mV, 500pA, SDD off, SDF off, ASIC-DAC
    if cseti == 1:
        adac_pls_en, sts, swdac, dac = dat.dat_cali_source(cali_mode=2,asicdac=0x10)
        rawdata = dat.dat_fe_qc(adac_pls_en=adac_pls_en, sts=sts, swdac=swdac, dac=dac,snc=0, sdd=0, sdf=0, slk0=1, slk1=0) #900mV, 100pA, SDD off, SDF off, ASIC-DAC
    if cseti == 2:
        adac_pls_en, sts, swdac, dac = dat.dat_cali_source(cali_mode=2,asicdac=0x10)
        rawdata = dat.dat_fe_qc(adac_pls_en=adac_pls_en, sts=sts, swdac=swdac, dac=dac,snc=0, sdd=0, sdf=0, slk0=1, slk1=1) #900mV, 1000pA, SDD off, SDF off, ASIC-DAC
    if cseti == 3:
        adac_pls_en, sts, swdac, dac = dat.dat_cali_source(cali_mode=2,asicdac=0x10)
        rawdata = dat.dat_fe_qc(adac_pls_en=adac_pls_en, sts=sts, swdac=swdac, dac=dac,snc=0, sdd=0, sdf=0, slk0=0, slk1=1) #900mV, 5000pA, SDD off, SDF off, ASIC-DAC
    if cseti == 4:
        adac_pls_en, sts, swdac, dac = dat.dat_cali_source(cali_mode=1, val=1.0, period=500, width=400)
        rawdata = dat.dat_fe_qc(adac_pls_en=adac_pls_en, sts=sts, swdac=swdac, dac=dac,snc=1, sdd=0, sdf=0 ) #200mV, 500pA, SDD off, SDF off, DAT-DAC
    if cseti == 5:
        adac_pls_en, sts, swdac, dac = dat.dat_cali_source(cali_mode=1, val=1.0, period=500, width=400)
        rawdata = dat.dat_fe_qc(adac_pls_en=adac_pls_en, sts=sts, swdac=swdac, dac=dac, snc=1, sdd=1, sdf=0 ) #200mV, 500pA, SDD on, SDF off, DAT-DAC
    if cseti == 6:
        adac_pls_en, sts, swdac, dac = dat.dat_cali_source(cali_mode=1, val=1.0, period=500, width=400)
        rawdata = dat.dat_fe_qc(adac_pls_en=adac_pls_en, sts=sts, swdac=swdac, dac=dac, snc=1, sdd=0, sdf=1 ) #200mV, 500pA, SDD off, SDF on, DAT-DAC
    if cseti == 7:
        adac_pls_en, sts, swdac, dac = dat.dat_cali_source(cali_mode=0, val=1.5, period=500, width=400)
        rawdata = dat.dat_fe_qc(adac_pls_en=adac_pls_en, sts=sts, swdac=swdac, dac=dac, snc=1, sdd=0, sdf=0 ) #200mV, 500pA, SDD off, SDF off, Direct-input

    fes_pwr_info = dat.fe_pwr_meas()
    adcs_pwr_info = dat.adc_pwr_meas()
    cds_pwr_info = dat.cd_pwr_meas()

    datad["PwrCycle_%d"%cseti] = [rawdata, fes_pwr_info, adcs_pwr_info, cds_pwr_info]

fdir = "./tmp_data/"
fp = fdir + "QC_PWR_CYCLE" + ".bin"
with open(fp, 'wb') as fn:
    pickle.dump(datad, fn)

