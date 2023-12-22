import sys 
import numpy as np
import pickle
import struct
import time, datetime, random, statistics
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

fp = sys.argv[1]
sfn = fp.split("/") #default
if "/" in fp:
    sfn = fp.split("/")
elif "\\" in fp:
    sfn = fp.split("\\")
p = fp.find(sfn[-1])
fdir = fp[0:p]

with open(fp, 'rb') as fn:
    hist_data = pickle.load(fn)
    

num_bins = 50
x = np.arange(0,pow(2,14)+1)
real_max = 0 #for stuff with a lot of data outside bounds
ch_cs = int(input("select a channel (0-127):"))
for ch, ch_hist_data in enumerate(hist_data):
#    if ch == ch_cs:
#        fig, ax = plt.subplots(figsize=(10,6)) #one "FEMB"
#        
#        chip = ch // 16
#        print (chip)
#
#        num_32bwords = 0x8000 / 4
#        num_16bwords = 0x8000 / 2        
#
#        words16b = list(struct.unpack_from("<%dH"%(num_16bwords),ch_hist_data))
#        if any(height > real_max for height in words16b[1:-1]): 
#            real_max = max(words16b[1:-1])                
#
#        ax.stairs(words16b, x, fill=True, color='C%d'%chip)
#        plt.ylim([0, 200])
#        plt.ylabel("Count")
#        plt.xlabel("ADC code / bit")
#        plt.show()
#
#        plt.close()


        chip = ch // 16
        print (chip)
        num_16bwords = 0x8000 / 2        
        words16b = list(struct.unpack_from("<%dH"%(num_16bwords),ch_hist_data))
        #if any(height > real_max for height in words16b[1:-1]): 
        #    real_max = max(words16b[1:-1])                
        #ax.stairs(words16b, x, fill=True, color='C%d'%chip)
        fig, ax = plt.subplots(figsize=(10,6)) #one "FEMB"

        x = np.arange(2**14)
        tmp = 500
        x = x[tmp:-1*tmp]
        y = np.array(words16b[tmp:-1*tmp])
        tot = np.sum(y)/len(x)
        ny = (y*1.0)/tot - 1
        #print (tot, ny[1000:1100])
        inl = []
        for i in range(len(ny)):
            inl.append(np.sum(ny[0:i+1]))

        ax.plot (x, ny)
        ax.set_ylim((-1,1))
#        ax.plot (x, inl, c="C1")
        #ax.plot (x[2000:-2000], np.array(inl[2000:-2000])-inl[2000])
        plt.ylabel("LSB")
        plt.xlabel("ADC code / bit")

        plt.show()
        plt.close()
#        


#        num_16bwords = 0x8000 / 2        
#
#        words16b = list(struct.unpack_from("<%dH"%(num_16bwords),ch_hist_data))
#        if any(height > real_max for height in words16b[1:-1]): 
#            real_max = max(words16b[1:-1])                
#
#        ax.stairs(words16b, x, fill=True, color='C%d'%chip)
#        plt.ylim([0, 200])
#        plt.show()
#
#        plt.close()


#plt.savefig(fdir+"adc_hist.jpg")






