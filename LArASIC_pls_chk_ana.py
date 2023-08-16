import time
import sys
import numpy as np
import pickle
import copy
import time, datetime, random, statistics    
from spymemory_decode import wib_dec

fdir = "./tmp_data/"
fp = fdir + "QC_CHK" + ".bin"
with open(fp, 'rb') as fn:
    data = pickle.load( fn)

dkeys = list(data.keys())
if "logs" in dkeys:
    dkeys.remove("logs")

for onekey in dkeys:
    print (onekey)
    cfgdata = data[onekey]
    fembs = cfgdata[0]
    rawdata = cfgdata[1]
    #fembs = cfgdata[1]
    #rawdata = cfgdata[0]

    wibdata = wib_dec(rawdata[0],fembs, spy_num=1)
    wibdata = wibdata[0]
    #wibdata = wib_dec(rawdata,fembs, spy_num=1)

    datd = [wibdata[0], wibdata[1],wibdata[2],wibdata[3]][0]

    import matplotlib.pyplot as plt
    for fe in range(8):
        for fe_chn in range(16):
            fechndata = datd[fe*16+fe_chn]
            if np.max(fechndata) - np.mean(fechndata) > 6000:
                pass
            else:
                print (fe*16+fe_chn,fe, fe_chn) 
            if fe*16+fe_chn < 64:
                c = 'r'
            else:
                c = 'b'
            plt.plot(fechndata, color=c)
    plt.show()
    plt.close()
            #    pp = np.max(fechndata[500:1500])
            #    pp_pos = np.where(fechndata[500:1500] == pp)[0][0]
            #    x = np.arange(300)
            #    plt.plot(x,fechndata[500+pp_pos-100:500+pp_pos+200])
            #    ped = np.mean(fechndata[pp_pos-200:pp_pos-150])
            #    npmin = np.min(fechndata)
            #    print (fe, fe_chn, pp, ped, npmin)
            #    plt.show()
            #    plt.close()

# ... (rest of your code)
 
#    print (pwr)
            




    
