import time
import sys
import numpy as np
import pickle
import copy
import time, datetime, random, statistics    
from dat_cfg import DAT_CFGS
                

#analog ref = 1.586V

cap_data = {}
dat =  DAT_CFGS()
dat.cdpoke(0, 0xC, 0, dat.DAT_FE_CMN_SEL, 4)    
width = 0x380&0xfff # width = duty, it must be less than (perod-2)
period = 0x400&0xfff #period = ADC samples between uplses
if period <= width - 2:
    width = period - 2
dat.cdpoke(0, 0xC, 0, dat.DAT_TEST_PULSE_WIDTH_MSB, ((width*32)>>8)&0xff)
dat.cdpoke(0, 0xC, 0, dat.DAT_TEST_PULSE_WIDTH_LSB, (width*32)&0xff)  
dat.cdpoke(0, 0xC, 0, dat.DAT_TEST_PULSE_PERIOD_MSB, period>>8)  
dat.cdpoke(0, 0xC, 0, dat.DAT_TEST_PULSE_PERIOD_LSB, period&0xff)  

dat.cdpoke(0, 0xC, 0, dat.DAT_TEST_PULSE_EN, 0x4)  
dat.cdpoke(0, 0xC, 0, dat.DAT_EXT_PULSE_CNTL, 1)    

dat.cdpoke(0, 0xC, 0, dat.DAT_ADC_FE_TEST_SEL, 3<<4)    
dat.cdpoke(0, 0xC, 0, dat.DAT_FE_TEST_SEL_INHIBIT, 0x00)   

chn = 5
#inject through test pin (cali)
#val = 0.60
dat.cdpoke(0, 0xC, 0, dat.DAT_FE_IN_TST_SEL_MSB, 0xff)   #cali input
dat.cdpoke(0, 0xC, 0, dat.DAT_FE_IN_TST_SEL_LSB, 0xff)   #cali input
data = dat.dat_fe_qc_cfg(snc=1, sg0=1, sg1=1, st0=0, st1=1, sts=1, swdac=2, chn=chn) #external DAC (common DAC), tp=3us, sg=4.7mV

for val in [0.60, 1.20]:
    val = int(val*1000)/1000.0
    dat.dat_set_dac(val=val, fe_cal=0)
    dat.cdpoke(0, 0xC, 0, dat.DAT_FE_CALI_CS, 0xff)  #cali input
    data = dat.dat_fe_qc_acq(num_samples=5)
    cap_data["FECHN%02d_%04dmV_CALI"%(chn, int(val*1000))] = data

#inject directly (cali)
chn_sel = 0x01<<chn
dat.cdpoke(0, 0xC, 0, dat.DAT_FE_IN_TST_SEL_MSB, (chn_sel>>8)&0xff)   #direct input
dat.cdpoke(0, 0xC, 0, dat.DAT_FE_IN_TST_SEL_LSB, chn_sel&0xff)   #direct input
dat.dat_fe_only_cfg(snc=1, sg0=1, sg1=1, st0=0, st1=1, sts=0, swdac=0, chn=chn) #direct input, tp=3us, sg=4.7mV
time.sleep(3)
for val in [1.40, 1.55]:
    val = int(val*1000)/1000.0
    dat.dat_set_dac(val=val, fe_cal=0)
    dat.cdpoke(0, 0xC, 0, dat.DAT_FE_CALI_CS, 0x00)  #direct input
    data = dat.dat_fe_qc_acq(num_samples=5)
    cap_data["FECHN%02d_%04dmV_INPUT"%(chn, int(val*1000))] = data



fdir = "./tmp_data/"
fp = fdir + "QC_DAT_DAC_Cap_Meas" + ".bin"
with open(fp, 'wb') as fn:
    pickle.dump(cap_data, fn)

