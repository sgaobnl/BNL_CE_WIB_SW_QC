import time
import sys
import numpy as np
import pickle
import copy
import time, datetime, random, statistics    
from dat_cfg import DAT_CFGS
                
dat =  DAT_CFGS()
dat.cdpoke(0, 0xC, 0, dat.DAT_FE_CMN_SEL, 4)    
width = 0x100&0xfff # width = duty, it must be less than (perod-2)
period = 0x200&0xfff #period = ADC samples between uplses
if period <= width - 2:
    width = period - 2
dat.cdpoke(0, 0xC, 0, dat.DAT_TEST_PULSE_WIDTH_MSB, ((width*32)>>8)&0xff)
dat.cdpoke(0, 0xC, 0, dat.DAT_TEST_PULSE_WIDTH_LSB, (width*32)&0xff)  
dat.cdpoke(0, 0xC, 0, dat.DAT_TEST_PULSE_PERIOD_MSB, width>>8)  
dat.cdpoke(0, 0xC, 0, dat.DAT_TEST_PULSE_PERIOD_LSB, width&0xff)  

dat.cdpoke(0, 0xC, 0, dat.DAT_TEST_PULSE_EN, 0x4)  
dat.cdpoke(0, 0xC, 0, dat.DAT_EXT_PULSE_CNTL, 1)    

dat.cdpoke(0, 0xC, 0, dat.DAT_ADC_FE_TEST_SEL, 3<<4)    
dat.cdpoke(0, 0xC, 0, dat.DAT_FE_TEST_SEL_INHIBIT, 0x00)   

dat.cdpoke(0, 0xC, 0, dat.DAT_FE_CALI_CS, 0xff)  #cali input
dat.cdpoke(0, 0xC, 0, dat.DAT_FE_IN_TST_SEL_MSB, 0xff)   #cali input
dat.cdpoke(0, 0xC, 0, dat.DAT_FE_IN_TST_SEL_LSB, 0xff)   #cali input

val = 1.10
dat.dat_set_dac(val=val, fe_cal=0)
data = dat.dat_fe_qc_cfg(snc=1, sts=1,swdac=2) #external DAC (common DAC)

QCdata = {}
for phase in range(0,32,1):
    dat.cdpoke(0, 0xC, 0, dat.DAT_TEST_PULSE_DELAY, phase%32)  #cali input
    time.sleep(0.1)
    data = dat.dat_fe_qc_acq(num_samples = 1)
    QCdata["Phase%02d_freq%02d"%(phase, width)] = copy.deepcopy(data)


fdir = "./tmp_data/"
fp = fdir + "QC_DAT_DAC_Cali_Res" + ".bin"
with open(fp, 'wb') as fn:
    pickle.dump(QCdata, fn)

