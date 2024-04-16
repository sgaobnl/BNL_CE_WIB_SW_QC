import time
import sys
import numpy as np
import pickle
import copy
import time, datetime, random, statistics    
from dat_cfg import DAT_CFGS
import ctypes
import struct

dat =  DAT_CFGS()
dat.fembs = [0]

def histbuf(): #adapted from llc.spybuf()
    HIST_MEM_SIZE = 0x8000 #rom A00C8000 to A00CFFFF
    buf = (ctypes.c_char*HIST_MEM_SIZE)()
    buf_bytes = bytearray(HIST_MEM_SIZE)
    

    dat.wib.bufread(buf,8) #read from histogram memory
    byte_ptr = (ctypes.c_char*HIST_MEM_SIZE).from_buffer(buf_bytes)            
    if not ctypes.memmove(byte_ptr, buf, HIST_MEM_SIZE):
        print('memmove failed')
        exit()
                
    return buf_bytes 
                

#adac_pls_en, sts, swdac, dac = dat.dat_cali_source(cali_mode=3)
#cfg_info = dat.dat_adc_qc_cfg(diff_en=0, autocali=1)

vrefp = 0xDF
vrefn = 0x33
vcmo = 0x89
vcmi = 0x67
#vrefp = 0xE8
#vrefn = 0x18
#vcmo = 0x90
#vcmi = 0x60

print (vrefp, vrefn, vcmo, vcmi)
adcs_paras = [ # c_id, data_fmt(0x89), diff_en(0x84), sdc_en(0x80), vrefp, vrefn, vcmo, vcmi, autocali
               [0x4, 0x08, 0, 0, vrefp, vrefn, vcmo, vcmi, 0],
               [0x5, 0x08, 0, 0, vrefp, vrefn, vcmo, vcmi, 0],
               [0x6, 0x08, 0, 0, vrefp, vrefn, vcmo, vcmi, 0],
               [0x7, 0x08, 0, 0, vrefp, vrefn, vcmo, vcmi, 0],
               [0x8, 0x08, 0, 0, vrefp, vrefn, vcmo, vcmi, 0],
               [0x9, 0x08, 0, 0, vrefp, vrefn, vcmo, vcmi, 0],
               [0xA, 0x08, 0, 0, vrefp, vrefn, vcmo, vcmi, 0],
               [0xB, 0x08, 0, 0, vrefp, vrefn, vcmo, vcmi, 0],
             ]

femb_id = 0
for adc_no in range(8):
    c_id    = adcs_paras[adc_no][0]
    data_fmt= adcs_paras[adc_no][1] 
    diff_en = adcs_paras[adc_no][2] 
    sdc_en  = adcs_paras[adc_no][3] 
    vrefp   = adcs_paras[adc_no][4] 
    vrefn   = adcs_paras[adc_no][5]  
    vcmo    = adcs_paras[adc_no][6] 
    vcmi    = adcs_paras[adc_no][7] 
    autocali= adcs_paras[adc_no][8] 
    dat.femb_i2c_wrchk(femb_id, chip_addr=c_id, reg_page=1, reg_addr=0x98, wrdata=vrefp)
    dat.femb_i2c_wrchk(femb_id, chip_addr=c_id, reg_page=1, reg_addr=0x99, wrdata=vrefn)
    dat.femb_i2c_wrchk(femb_id, chip_addr=c_id, reg_page=1, reg_addr=0x9a, wrdata=vcmo)
    dat.femb_i2c_wrchk(femb_id, chip_addr=c_id, reg_page=1, reg_addr=0x9b, wrdata=vcmi)



#dat.dat_coldadc_ext(ext_source ="P6")
dat.dat_coldadc_cali_cs(chsenl=0xFFFD)

dat.dat_set_dac(0000, adc=0) #set ADC_P to 0 V
dat.dat_set_dac(0000, adc=1) #set ADC_N to 0 V

#set samples to take
num_samples = 1000
dat.poke(0xA00C007C, num_samples)
ch = 65
dat.poke(0xA00C0078, ch)

t0 = time.time_ns()
ress = []

for dac in range(0x0,50001,50):
    dat.dat_set_dac(val=dac, adc=0) #set ADC_P to 0 V
    time.sleep(0.0005)
    #tmp = (dat.peek(0xA00C00F0) & ~(0x3ff))>>10
    #print (tmp, hex(tmp))
    #print ("XXXXXXXXXXX")

    #trigger histogram
    dat.poke(0xA00C0074, 0x1)
    dat.poke(0xA00C0074, 0x0)
        
    num_waits = 0
    while dat.peek(0xA00C00F0) & (0x1<<9) == 0: #while hist not done
        num_waits = num_waits + 1
        pass
            
    ch_hist_data = histbuf()
    ress.append([dac,ch_hist_data])
    print (dac, time.time_ns()-t0)

fdir = "./tmp_data/"
datad = {}
datad["LIN"] = ress 
fp = fdir + "lin.bin"
with open(fp, 'wb') as fn:
    pickle.dump(datad, fn)

    #num_16bwords = 0x8000 / 2        
    #words16b = list(struct.unpack_from("<%dH"%(num_16bwords),ch_hist_data))
    #print (time.time_ns() - t0)

    #sumv = 0
    #sumn = 0
    #for i in range(len(words16b)):
    #    if words16b[i] != 0 :
    #        sumv = sumv + i*words16b[i]
    #        sumn = sumn + words16b[i]
    #print (time.time_ns() - t0)
    #dacs.append(dac)
    #sumvs.append(sumv)
    #sumns.append(sumn)
    #print (time.time_ns() - t0)
    #exit()
    #t0 = time.time_ns()

#    print (suma)
#    tmp = (dat.peek(0xA00C00F0) & ~(0x3ff))>>10
#    print (tmp, hex(tmp))
#
#
#    input()
        
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

