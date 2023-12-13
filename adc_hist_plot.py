import sys 
import numpy as np
import pickle
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
    if ch == ch_cs:
        fig, ax = plt.subplots(figsize=(10,6)) #one "FEMB"
        
        chip = ch // 16
        print (chip)
        
        if any(height > real_max for height in ch_hist_data[1:-1]): 
            real_max = max(ch_hist_data[1:-1])
            
        ax.stairs(ch_hist_data, x, fill=True, color='C%d'%chip)

        plt.ylim([0, 200])
        plt.show()

        plt.close()

#plt.savefig(fdir+"adc_hist.jpg")






