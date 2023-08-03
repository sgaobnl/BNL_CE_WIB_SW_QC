import time
import sys
import numpy as np
import pickle
import copy
import time, datetime, random, statistics    
from spymemory_decode import wib_spy_dec_syn

fdir = "./tmp_data/"
fp = fdir + "QC_DAT_DAC_Cap_Meas" + ".bin"
with open(fp, 'rb') as fn:
    QCdata = pickle.load( fn)

dkeys = list(QCdata.keys())
print (dkeys)

fembs=[0]
pps4 = []
import matplotlib.pyplot as plt
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
    
    pps = []
    for fe in [3]:
        for fe_chn in [5]:
            fechndata = datd[fe*16+fe_chn]

            import matplotlib.pyplot as plt
            x = np.arange(len(fechndata))

            pfreq = 512*2
            pp = np.max(fechndata[0:pfreq])
            pps.append(pp)
            
            pp_pos = np.where(fechndata[0:pfreq] == pp)[0][0]
            if pp_pos < 100:
                fechndata = fechndata[pp_pos+pfreq-50:pp_pos+pfreq-50+pfreq] 
            else:
                fechndata = fechndata[pp_pos-50:pp_pos-50+pfreq] 


            ###pp = np.max(fechndata[500:1500])
            ###pp_pos = np.where(fechndata[500:1500] == pp)[0][0]
            xspan = 1000
            x = np.arange(xspan)
            ###plt.plot(x,fechndata[500+pp_pos-100:500+pp_pos+x-100])
            ###plt.scatter(x,fechndata[500+pp_pos-100:500+pp_pos+xspan-100])
            #import matplotlib.pyplot as plt
            plt.plot(x,fechndata[0:xspan], marker='.', label = onekey)
            #plt.show()
            #plt.close()

            ##ped = np.mean(fechndata[pp_pos-200:pp_pos-150])
            ##npmin = np.min(fechndata)
            #print (fe, fe_chn, pp, ped, npmin)
    #print (pps)
    #pps4.append(pps)
plt.legend()
plt.grid()
plt.show()
plt.close()

#print (pps)
#print (pps[1]-pps[0], pps[3]-pps[2])

# ... (rest of your code)
            




    
