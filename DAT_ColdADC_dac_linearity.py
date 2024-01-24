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
cfg_info = dat.dat_adc_qc_cfg(diff_en=0, autocali=1)

#dat.dat_coldadc_ext(ext_source ="P6")
dat.dat_coldadc_cali_cs(chsenl=0xFFFE)

dat.dat_set_dac(0000, adc=0) #set ADC_P to 0 V
dat.dat_set_dac(0000, adc=1) #set ADC_N to 0 V

for dac in range(0x0,0xFFFF,0x1000):
    dat.dat_set_dac(val=dac, adc=0) #set ADC_P to 0 V
    print (dat.poke(0xA00C0078, 0))
    input ()

        
#        chds = []
#        for ch in range(0,128,16):
#            dat.poke(0xA00C0078, ch)
#            tmpd = []
#            for i in range(20):    
#                tmp = (dat.peek(0xA00C00F0) & ~(0x3ff))>>10
#                tmpd.append(tmp)
#                time.sleep(0.01)
#            chds.append(int(np.mean(tmpd)))
#        print (chds)
#        tmr = input ("input:")
#        if "b" in tmr:
#            break

#fdir = "./tmp_data/"
#rawdata =  dat.dat_adc_qc_acq(1)
#datad = {}
#datad["TRI"] = rawdata 
#fp = fdir + "LN_QC_ramp.bin"
#with open(fp, 'wb') as fn:
#    pickle.dump(datad, fn)





#histo = []
#for x in range(pow(2,14)):
#    histo.append(0)
#histo128s = []
#for x in range(128):
#    histo128s.append(list(histo))
#
##histo128s[0][123] = histo128s[0][123]  + 1
##histo128s[127][123] = histo128s[127][123]  + 3
##print (histo128s[0][123], histo128s[127][123])
#
#
##for valint in range(pow(2,16)):
#for valint in range(20000,30000, 1000):
#    t0 = time.time_ns()
#    dat.dat_set_dac(val=valint, adc=0)
#    t1 = time.time_ns()
#    print ("A", t1-t0)
#    t0=t1
#    wibdata =  dat.dat_adc_qc_acq(1)
#    t1 = time.time_ns()
#    print ("B", t1-t0)
#    #print (len(wibdata))
#    #print (len(wibdata[0]))
#    #print (wibdata[0][0:10])
#    #print (wibdata[1][0:10])
#    for ch in range(128):
#        for addr in wibdata[ch]:
#            histo128s[ch][addr] = histo128s[ch][addr] + 1
#    #print (valint, np.mean(wibdata[5]), np.std(wibdata[5]))
#
#datad = {}
#datad["ColdADC_HISTO"] = histo128s 
#
#if False:
#    fdir = "./tmp_data/"
#    fp = fdir + "QC_ColdADC.bin"
#    with open(fp, 'wb') as fn:
#        pickle.dump(datad, fn)
#

