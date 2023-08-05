import time
import sys
import numpy as np
import pickle
import copy
import time, datetime, random, statistics    
from dat_cfg import DAT_CFGS
                

#analog ref = 1.586V

dat =  DAT_CFGS()
datad = {}

#bl200mV
snc=1
#3.0us
st0=0
st1=1
Vref = 1.583
if True:
    #4.7mV/fC
    sg0=1
    sg1=1
    cali_vals=[0.6, 1.4]
    dire_vals=[1.40, 1.55]
if False:
    #7.8mV/fC
    sg0=0
    sg1=1
    cali_vals=[0.95, 1.55]
    dire_vals=[1.47, 1.57]

if False:
    #14mV/fC
    sg0=0
    sg1=0
    cali_vals=[1.2, 1.55]
    dire_vals=[1.52, 1.58]

period = 1000
width = 800

cfg_info = dat.dat_fe_qc_cfg() #default setting 


#for chn in range(16):
for chn in [0]:
    print ("DAC DAT cali for FE CH%02d"%chn)
    val = 1.4
    adac_pls_en, sts, swdac, dac = dat.dat_cali_source(cali_mode=1, val=val, period=period, width=width)
    cali_fe_info = dat.dat_fe_only_cfg(snc=snc, sg0=sg0, sg1=sg1, st0=st0, st1=st1, sts=sts, swdac=swdac, chn=chn) #direct input, tp=3us, sg=4.7mV
    
    for val in cali_vals:
        val = int(val*1000)/1000.0
        dat.dat_set_dac(val=val, fe_cal=0)
        data = dat.dat_fe_qc_acq(num_samples=5)
        datad["FECHN%02d_%04dmV_CALI"%(chn, int(val*1000))] = [ data, dat.fembs, chn, val, period, width, cali_fe_info, cfg_info]
    
    #inject directly (cali)
    val = 1.4
    print ("inject directly (cali) for FE CH%02d"%chn)
    adac_pls_en, sts, swdac, dac = dat.dat_cali_source(cali_mode=0, val=val, period=period, width=width)
    chn_sel = 0x01<<chn
    dat.cdpoke(0, 0xC, 0, dat.DAT_FE_IN_TST_SEL_MSB, (chn_sel>>8)&0xff)   #direct input
    dat.cdpoke(0, 0xC, 0, dat.DAT_FE_IN_TST_SEL_LSB, chn_sel&0xff)   #direct input
    direct_fe_info = dat.dat_fe_only_cfg(snc=snc, sg0=sg0, sg1=sg1, st0=st0, st1=st1, sts=0, swdac=0, chn=chn) #direct input, tp=3us, sg=4.7mV
    
    for val in  dire_vals:
        val = int(val*1000)/1000.0
        dat.dat_set_dac(val=val, fe_cal=0)
        data = dat.dat_fe_qc_acq(num_samples=5)
        datad["FECHN%02d_%04dmV_INPUT"%(chn, int(val*1000))] = [ data, dat.fembs, chn, val, period, width, direct_fe_info, cfg_info]

fdir = "./tmp_data/"
fp = fdir + "QC_Cap_Meas" + ".bin"
with open(fp, 'wb') as fn:
    pickle.dump(datad, fn)

