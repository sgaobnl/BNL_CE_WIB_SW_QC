import time
import sys
import numpy as np
import pickle
import copy
import time, datetime, random, statistics    
from dat_cfg import DAT_CFGS
                
dat =  DAT_CFGS()
val = 1.00
dat.dat_set_dac(val=val, fe_cal=0)
dat.cdpoke(0, 0xC, 0, dat.DAT_FE_CMN_SEL, 4)    
while True:
    width = int(input())
    period = int(input())
    #width = 0x200&0xffff
    dat.cdpoke(0, 0xC, 0, dat.DAT_TEST_PULSE_WIDTH_MSB, ((width*32)>>8)&0xff)
    dat.cdpoke(0, 0xC, 0, dat.DAT_TEST_PULSE_WIDTH_LSB, (width*32)&0xff)  
    dat.cdpoke(0, 0xC, 0, dat.DAT_TEST_PULSE_PERIOD_MSB, period>>8)  
    dat.cdpoke(0, 0xC, 0, dat.DAT_TEST_PULSE_PERIOD_LSB, period&0xff)  

dat.cdpoke(0, 0xC, 0, dat.DAT_TEST_PULSE_EN, 0x4)  
dat.cdpoke(0, 0xC, 0, dat.DAT_EXT_PULSE_CNTL, 1)    

dat.cdpoke(0, 0xC, 0, dat.DAT_ADC_FE_TEST_SEL, 3<<4)    
dat.cdpoke(0, 0xC, 0, dat.DAT_FE_TEST_SEL_INHIBIT, 0x00)   

dat.cdpoke(0, 0xC, 0, dat.DAT_FE_CALI_CS, 0xff)  #cali input
dat.cdpoke(0, 0xC, 0, dat.DAT_FE_IN_TST_SEL_MSB, 0xff)   #cali input
dat.cdpoke(0, 0xC, 0, dat.DAT_FE_IN_TST_SEL_LSB, 0xff)   #cali input

data = dat.dat_fe_qc(snc=1, sts=1,swdac=2) #external DAC (common DAC)

fdir = "./tmp_data/"
fp = fdir + "QC_DAT_DAC_Cali_Res" + ".bin"
with open(fp, 'wb') as fn:
    pickle.dump(data, fn)

