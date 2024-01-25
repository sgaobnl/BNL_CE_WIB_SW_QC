import time
import sys
import numpy as np
import pickle
import copy
import time, datetime, random, statistics    


fdir = "./tmp_data/"
fp = fdir + "QC_ColdADC_HISTO.bin"
with open(fp, 'rb') as fn:
    data = pickle.load( fn)

dkeys = list(data.keys())
if "logs" in dkeys:
    dkeys.remove("logs")

for onekey in dkeys:
    histo128s, rdacm128, rdacstd128 = data[onekey]

for ch in [0]:
    histo = histo128s[ch]
    rdacm = rdacm128[ch]
    rdacstd = rdacstd128[ch]

    import matplotlib.pyplot as plt
    plt.plot(histo)
    #plt.plot(rdacstd)
    plt.show()
    plt.close()
    exit()


    for i in range(len(histo)):
        if histo[i] != 0:
            print (i, histo[i])
    for i in range(len(rdacm)):
        if rdacm[i] != 0:
            print (i, rdacm[i])

    for i in range(len(rdacstd)):
        if rdacstd[i] != 0:
            print (i, rdacstd[i])
#
#histo = []
#for x in range(pow(2,14)):
#    histo.append(0)
#histo128s = []
#for x in range(128):
#    histo128s.append(list(histo))
#
#rdacm = []
#for x in range(pow(2,16)):
#    rdacm.append(0)
#rdacm128 = []
#for x in range(128):
#    rdacm128.append(list(rdacm))
#
#rdacstd = []
#for x in range(pow(2,16)):
#    rdacstd.append(0)
#rdacstd128 = []
#for x in range(128):
#    rdacstd128.append(list(rdacstd))
#
#
#fdir = "./tmp_data/ColdADC/"
#fembs = [0]
#for tmp in [10]: #range(65):
#    fp = fdir + "QC_ColdADC%06d"%tmp + ".bin"
#    with open(fp, 'rb') as fn:
#        data = pickle.load( fn)
#    dkeys = list(data.keys())
#    if "logs" in dkeys:
#        dkeys.remove("logs")
#    for onekey in dkeys:
#        print (onekey)
#        dacv = int(onekey[3:9])
#        rawdata = data[onekey]
#    
#        wibdata = wib_dec(rawdata,fembs, spy_num=1)[0][0]
#        for ch in range(128):
#            for addr in wibdata[ch]:
#                histo128s[ch][addr] = histo128s[ch][addr] + 1
#            rdacm128[ch][dacv] = np.mean(wibdata[ch])
#            rdacstd128[ch][dacv] = np.std(wibdata[ch])
#
#datad = {}
#datad["ColdADC_HISTO"] = [histo128s, rdacm128, rdacstd128]
#
#if False:
#    fdir = "./tmp_data/"
#    fp = fdir + "QC_ColdADC_HISTo.bin"
#    with open(fp, 'wb') as fn:
#        pickle.dump(datad, fn)

 
