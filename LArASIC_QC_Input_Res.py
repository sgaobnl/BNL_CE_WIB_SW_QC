import time
import sys
import numpy as np
import pickle
import copy
import time, datetime, random, statistics    
from dat_cfg import DAT_CFGS
                
dat =  DAT_CFGS()
#dat.dat_fe_qc(sts=1,swdac=2) #external DAC (common DAC)
dat.dat_fe_qc(snc=1,sts=0,swdac=0) #direct FE input
while True:
    val = float(input ("next"))
    dat.dat_set_dac(val=val, fe_cal=0)
    dat.cdpoke(0, 0xC, 0, dat.DAT_FE_CMN_SEL, 4)    
    dat.cdpoke(0, 0xC, 0, dat.DAT_TEST_PULSE_WIDTH_MSB, 0x10)  
    dat.cdpoke(0, 0xC, 0, dat.DAT_TEST_PULSE_WIDTH_LSB, 0x00)  
    dat.cdpoke(0, 0xC, 0, dat.DAT_TEST_PULSE_PERIOD_MSB, 0x20)  
    dat.cdpoke(0, 0xC, 0, dat.DAT_TEST_PULSE_PERIOD_LSB, 0x00)  
    dat.cdpoke(0, 0xC, 0, dat.DAT_TEST_PULSE_EN, 0x4)  
    dat.cdpoke(0, 0xC, 0, dat.DAT_EXT_PULSE_CNTL, 1)    

    dat.cdpoke(0, 0xC, 0, dat.DAT_ADC_FE_TEST_SEL, 3<<4)    
    dat.cdpoke(0, 0xC, 0, dat.DAT_FE_TEST_SEL_INHIBIT, 0x00)   
    #dat.cdpoke(0, 0xC, 0, dat.DAT_FE_CALI_CS, 0xff)  #cali input
    #dat.cdpoke(0, 0xC, 0, dat.DAT_FE_IN_TST_SEL_MSB, 0xff)   #cali input
    #dat.cdpoke(0, 0xC, 0, dat.DAT_FE_IN_TST_SEL_LSB, 0xff)   #cali input

    dat.cdpoke(0, 0xC, 0, dat.DAT_FE_CALI_CS, 0x00)  #direct input
    dat.cdpoke(0, 0xC, 0, dat.DAT_FE_IN_TST_SEL_MSB, 0x00)   #direct input
    dat.cdpoke(0, 0xC, 0, dat.DAT_FE_IN_TST_SEL_LSB, 0x01)   #direct input



#    dat.cdpoke(0, 0xC, 0, dat.DAT_ADC_FE_TEST_SEL, 3<<4)    
#    dat.cdpoke(0, 0xC, 0, dat.DAT_FE_TEST_SEL_INHIBIT, 0x00)   
#    dat.cdpoke(0, 0xC, 0, dat.DAT_FE_CALI_CS, 0x00)  
#    dat.cdpoke(0, 0xC, 0, dat.DAT_TEST_PULSE_SOCKET_EN, 0xff)  
#    dat.cdpoke(0, 0xC, 0, dat.DAT_FE_IN_TST_SEL_MSB, 0xff)  
#    dat.cdpoke(0, 0xC, 0, dat.DAT_FE_IN_TST_SEL_LSB, 0xff)  



#    dat.dat_set_dac(val=val, fe=0)
#    dat.dat_set_dac(val=val, fe=1)
#    dat.dat_set_dac(val=val, fe=2)
#    dat.dat_set_dac(val=val, fe=3)
#    dat.dat_set_dac(val=val, fe=4)
#    dat.dat_set_dac(val=val, fe=5)
#    dat.dat_set_dac(val=val, fe=6)
#    dat.dat_set_dac(val=val, fe=7)

#fdir = "./tmp_data/"
#fp = fdir + "QC2_mon" + ".bin"
#with open(fp, 'wb') as fn:
#    pickle.dump(data, fn)
#
