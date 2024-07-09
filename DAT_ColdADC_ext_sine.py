import time, datetime
import sys
import numpy as np
import pickle
import copy
import time, datetime, random, statistics    
from dat_cfg import DAT_CFGS
                
dat =  DAT_CFGS()
dat.fembs = [0]
dat.en_ref10MHz(ref_en = True)

adac_pls_en, sts, swdac, dac = dat.dat_cali_source(cali_mode=3)
cfg_info = dat.dat_adc_qc_cfg(diff_en=1)
#dat.en_ref10MHz(ref_en=True)
dat.dat_coldadc_ext(ext_source ="P6")
#dat.dat_coldadc_ext(ext_source ="P6")
dat.dat_set_dac(0000, adc=0) #set ADC_P to 0 V
dat.dat_set_dac(0000, adc=1) #set ADC_N to 0 V
#dat.dat_coldadc_cali_cs()

time.sleep(1)

fdir = "./tmp_data/"
rawdata =  dat.dat_adc_qc_acq(50)
datad = {}
datad["SINE"] = rawdata 
ts = datetime.datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
fp = fdir + "LN_QC_sine_" + ts + ".bin"
with open(fp, 'wb') as fn:
    pickle.dump(datad, fn)





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

