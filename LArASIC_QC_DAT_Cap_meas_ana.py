import time
import sys
import numpy as np
import pickle
import copy
import time, datetime, random, statistics    
from spymemory_decode import wib_dec
from spymemory_decode import avg_aligned_by_ts

fdir = "./tmp_data/"
fp = fdir + "QC_Cap_Meas" + ".bin"
with open(fp, 'rb') as fn:
    QCdata = pickle.load( fn)

dkeys = list(QCdata.keys())

fembs=[0]
pps4 = []
chndatad = {} 
chncs = 0
vals = []
for onekey in dkeys:
    if "FECHN%02d"%chncs in onekey:
        print (onekey)
        data = QCdata[onekey]
        rawdata = data[0]
        fembs = data[1]
        fembchn = data[2]
        val = data[3]
        period =  data[4]
        width =  data[5]
        fe_info = data[6]
        cfg_info = data[7]
        vals.append(val)

        wibdata = wib_dec(rawdata, fembs, spy_num=1)
        chns = np.arange(fembs[0]*128 + fembchn, fembs[0]*128 + fembchn + 128, 16)
        pps = []
        import matplotlib.pyplot as plt
        for chn in chns:
            data = avg_aligned_by_ts(wibdata, chn, period)
            chndatad[onekey+"%03d"%chn] = data
            pps.append (np.max(data[0]))
            plt.plot(data[0], marker = '.')
#            plt.plot(data[1])
        plt.show()
        plt.close()
#            break

        pps4.append(pps)
        print (pps)
         
ratios = []
for i in range(8):
    ratios.append ((pps4[0][i]-pps4[1][i])/(pps4[2][i]-pps4[3][i]))
print (ratios)
#caps = np.array(ratios)*0.15/0.8/0.185
#caps = np.array(ratios)*0.06/0.35/0.185
del1 = vals[3]-vals[2]
del2 = vals[1] - vals[0]
print (del1, del2)
caps = np.array(ratios)*del1/del2/0.185
print (caps)
#print (pps[1]-pps[0], pps[3]-pps[2])
#plt.show()
#plt.close()

#    import matplotlib.pyplot as plt
#    plt.plot(chndata[0], marker = '.')
#    plt.plot(chndata[1])
#    plt.show()
#    plt.close()
#


    
#    pps = []
#    for fe in range(8):
#        for fe_chn in [5]:
#            fechndata = datd[fe*16+fe_chn]
#            x = np.arange(len(fechndata))
#            #plt.plot(x, fechndata)
#            #plt.show()
#            #plt.close()
#            #exit()
#            pfreq = 512*2
#            pp = np.max(fechndata[0:pfreq])
#            pps.append(pp)
#            
#            pp_pos = np.where(fechndata[0:pfreq] == pp)[0][0]
#            if pp_pos < 100:
#                fechndata = fechndata[pp_pos+pfreq-50:pp_pos+pfreq-50+pfreq] 
#            else:
#                fechndata = fechndata[pp_pos-50:pp_pos-50+pfreq] 
#
#
#            ##pp = np.max(fechndata[500:1500])
#            ##pp_pos = np.where(fechndata[500:1500] == pp)[0][0]
#            xspan = 1000
#            x = np.arange(xspan)
#            ##plt.plot(x,fechndata[500+pp_pos-100:500+pp_pos+x-100])
#            ##plt.scatter(x,fechndata[500+pp_pos-100:500+pp_pos+xspan-100])
##            plt.plot(x,fechndata[0:xspan], marker='.')
#            #ped = np.mean(fechndata[pp_pos-200:pp_pos-150])
#            #npmin = np.min(fechndata)
#            #print (fe, fe_chn, pp, ped, npmin)
#            break
#    print (pps)
#    pps4.append(pps)
#
##print (pps4)
#
#ratios = []
#for i in range(8):
#    ratios.append ((pps4[0][i]-pps4[1][i])/(pps4[2][i]-pps4[3][i]))
#print (ratios)
##print (pps[1]-pps[0], pps[3]-pps[2])
##plt.show()
##plt.close()
#
## ... (rest of your code)
            




    
