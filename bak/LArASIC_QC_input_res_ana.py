import time
import sys
import numpy as np
import pickle
import copy
import time, datetime, random, statistics    
from spymemory_decode import wib_spy_dec_syn
from spymemory_decode import wib_dec

fdir = "./tmp_data/"
fp = fdir + "QC3_mon" + ".bin"
with open(fp, 'rb') as fn:
    rawdata = pickle.load( fn)
rawdata = rawdata[0]

print (len(rawdata))
print (len(rawdata[0]))
print (len(rawdata[0][0]))
print (len(rawdata[0][0][0]))

fembs=[0]
#dec_data = wib_spy_dec_syn(buf0=rawdata[0][0][0], buf1=rawdata[0][0][0], trigmode='SW', buf_end_addr=rawdata[0][1], trigger_rec_ticks=rawdata[0][1], fembs=fembs)
#if fembs[0]<=1:
#    link = 0
#else:
#    link = 1
#flen = len(dec_data[link])
#tmts = []
#sfs0 = []
#sfs1 = []
#cdts_l0 = []
#cdts_l1 = []
#femb0 = []
#femb1 = []
#femb2 = []
#femb3 = []
#for i in range(flen):
#    tmts.append(dec_data[link][i]["TMTS"])  # timestampe(64bit) * 512ns  = real time in ns (UTS)
#    sfs0.append(dec_data[link][i]["FEMB_SF"])
#    cdts_l0.append(dec_data[link][i]["FEMB_CDTS"])
#
#    if link == 0:
#        femb0.append(dec_data[0][i]["FEMB0_2"])
#        femb1.append(dec_data[0][i]["FEMB1_3"])
#    else:
#        femb2.append(dec_data[1][i]["FEMB0_2"])
#        femb3.append(dec_data[1][i]["FEMB1_3"])
#
#datd = [femb0, femb1, femb2, femb3][fembs[0]]


wibdata = wib_dec(rawdata,fembs, spy_num=1)
print (len(wibdata))
datd = [wibdata[0], wibdata[1],wibdata[2],wibdata[3]][0]
#datd = wibdata[0]
#datd = list(zip(*datd))
for ch in range(128):
    import matplotlib.pyplot as plt
    plt.plot(datd[ch])
    plt.show()
    plt.close()

for ch in range(16*8):
   chmax = np.max(datd[ch][0:1500])
   chped = np.mean(datd[ch][0:1500])
   chmin = np.min(datd[ch][0:1500])
   print ("Cali Input ERROR", ch, chmax, chped, chmin)

#for fe in range(8):

#    import matplotlib.pyplot as plt
#    for fe_chn in range(16):
#        fechndata = datd[fe*16+fe_chn]
#        pp = np.max(fechndata[500:1500])
#        pp_pos = np.where(fechndata[500:1500] == pp)[0][0]
#        x = np.arange(300)
#        #plt.plot(x,fechndata[500+pp_pos-100:500+pp_pos+200])
#        ped = np.mean(fechndata[pp_pos-200:pp_pos-150])
#        npmin = np.min(fechndata)
#        print (fe, fe_chn, pp, ped, npmin)
#    plt.show()
#    plt.close()

# ... (rest of your code)
            




    