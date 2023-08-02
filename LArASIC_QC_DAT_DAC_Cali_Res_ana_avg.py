import time
import sys
import numpy as np
import pickle
import copy
import time, datetime, random, statistics    
#from spymemory_decode import wib_spy_dec_syn
from spymemory_decode import wib_dec
from spymemory_decode import avg_aligned_by_ts

fdir = "./tmp_data/"
fp = fdir + "QC_DAT_DAC_Cali_Res" + ".bin"
with open(fp, 'rb') as fn:
    rawdata = pickle.load( fn)

fembs=[0]

wibdata = wib_dec(rawdata,fembs, spy_num=10)
for i in range(10):
    print (i)
    chndata = avg_aligned_by_ts(wibdata, chn=i, period=512)
print (len(chndata))
print (len(chndata[0]))
print (chndata[2], chndata[3], chndata[4])
import matplotlib.pyplot as plt
plt.plot(chndata[0], marker = '.')
plt.plot(chndata[1], marker = '*')
plt.show()
plt.close()

#print (len(dec_data))
#print (len(dec_data[0]))
#print (len(dec_data[1]))
#print (len(dec_data[2]))
#print (len(dec_data[3]))
#print (len(dec_data[4]))


#datd = [femb0, femb1, femb2, femb3][fembs[0]]
#datd = list(zip(*datd))
#
#for fe in range(8):
#    import matplotlib.pyplot as plt
#    for fe_chn in range(16):
#        fechndata = datd[fe*16+fe_chn]
#        pp = np.max(fechndata[500:1500])
#        pp_pos = np.where(fechndata[500:1500] == pp)[0][0]
#        x = np.arange(800)
#        plt.plot(x,fechndata[500+pp_pos-100:500+pp_pos+700])
#        ped = np.mean(fechndata[pp_pos-200:pp_pos-150])
#        npmin = np.min(fechndata)
#        print (fe, fe_chn, pp, ped, npmin)
#    plt.show()
#    plt.close()
#
# ... (rest of your code)
            




    
