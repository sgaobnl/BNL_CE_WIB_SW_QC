import time
import sys
import numpy as np
import pickle
import copy
import time, datetime, random, statistics    
from spymemory_decode import wib_spy_dec_syn

fdir = "./tmp_data/"
fp = fdir + "QC_DAT_DAC_Cali_Res" + ".bin"
with open(fp, 'rb') as fn:
    QCdata = pickle.load( fn)

dkeys = list(QCdata.keys())
print (dkeys)

fembs=[0]
import matplotlib.pyplot as plt
dly = 0
for onekey in dkeys:
    print (onekey)
    rawdata = QCdata[onekey]

    dec_data = wib_spy_dec_syn(buf0=rawdata[0][0][0], buf1=rawdata[0][0][1], trigmode='SW', buf_end_addr=rawdata[0][1], trigger_rec_ticks=rawdata[0][1], fembs=fembs)

    
    if fembs[0]<=1:
        link = 0
    else:
        link = 1
    flen = len(dec_data[link])
    tmts = []
    sfs0 = []
    sfs1 = []
    cdts_l0 = []
    cdts_l1 = []
    femb0 = []
    femb1 = []
    femb2 = []
    femb3 = []
    for i in range(flen):
        tmts.append(dec_data[link][i]["TMTS"])  # timestampe(64bit) * 512ns  = real time in ns (UTS)
        sfs0.append(dec_data[link][i]["FEMB_SF"])
        cdts_l0.append(dec_data[link][i]["FEMB_CDTS"])
    
        if link == 0:
            femb0.append(dec_data[0][i]["FEMB0_2"])
            femb1.append(dec_data[0][i]["FEMB1_3"])
        else:
            femb2.append(dec_data[1][i]["FEMB0_2"])
            femb3.append(dec_data[1][i]["FEMB1_3"])
    
    
    datd = [femb0, femb1, femb2, femb3][fembs[0]]
    datd = list(zip(*datd))
    
    for fe in range(8):
        for fe_chn in range(16):
            fechndata = datd[fe*16+fe_chn]
            x = np.arange(len(fechndata))
            #plt.plot(x, fechndata)
            pfreq = 512
            pp = np.max(fechndata[0:pfreq])
            pp_pos = np.where(fechndata[0:pfreq] == pp)[0][0]
            fechndata = fechndata[pp_pos+pfreq-50:pp_pos+pfreq-50+pfreq] 


            ##pp = np.max(fechndata[500:1500])
            ##pp_pos = np.where(fechndata[500:1500] == pp)[0][0]
            xspan = 100
            x = np.arange(xspan)
            x = x - (dly/32.0)
            ##plt.plot(x,fechndata[500+pp_pos-100:500+pp_pos+x-100])
            ##plt.scatter(x,fechndata[500+pp_pos-100:500+pp_pos+xspan-100])
            plt.scatter(x,fechndata[0:xspan])
            #ped = np.mean(fechndata[pp_pos-200:pp_pos-150])
            #npmin = np.min(fechndata)
            #print (fe, fe_chn, pp, ped, npmin)
            break
        break
    dly = dly + 1
plt.show()
plt.close()

# ... (rest of your code)
            




    
