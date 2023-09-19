import time
import sys
import numpy as np
import pickle
import copy
import time, datetime, random, statistics    
from spymemory_decode import wib_dec

fdir = "./tmp_data/"
fp = fdir + "QC_TRI_chn3" + ".bin"
with open(fp, 'rb') as fn:
    data = pickle.load( fn)

dkeys = list(data.keys())
if "logs" in dkeys:
    dkeys.remove("logs")

print (dkeys)
for onekey in dkeys:
    print (onekey)
    fembs = [0]
    rawdata = data[onekey]
    
    datd = wib_dec(rawdata,fembs, spy_num=1)[0][0]

    import matplotlib.pyplot as plt
    for fe in range(8):
        for fe_chn in range( 16):
            fechndata = datd[fe*16+fe_chn]
            print (fe_chn, np.mean(fechndata), np.std(fechndata))
            if np.max(fechndata) - np.mean(fechndata) > 3000:
                print (fe*16+fe_chn)
#            if np.max(fechndata) - np.mean(fechndata) > 8000:
#                pass
#            else:
#                print (fe*16+fe_chn,fe, fe_chn) 
            plt.plot(fechndata, marker = '.', label="%d"%fe_chn)
    plt.legend()
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
            




    
