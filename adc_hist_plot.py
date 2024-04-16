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
    

fig, ax = plt.subplots(figsize=(10,6)) #one "FEMB"
num_bins = 50
x = np.arange(0,pow(2,14)+1)
real_max = 0 #for stuff with a lot of data outside bounds
for ch, ch_hist_data in enumerate(hist_data):
    
    #idea sort of from https://stackoverflow.com/a/19361027: convert into un-binned data and then run
    # plt.hist(chdata_unordered,num_bins,color='C%d'%chip)
    
    # chdata_unordered = []
    # for addr, count in enumerate(ch_hist_data):
        # for i in range(count):
            # chdata_unordered.append(addr)
    
    
    # ch_group = int(ch % 16 < 8)    
    chip = ch // 16
    
    #for stuff with a lot of data outside bounds:
    if any(height > real_max for height in ch_hist_data[1:-1]): 
        real_max = max(ch_hist_data[1:-1])
        
    # ax.bar(x, ch_hist_data, linewidth=1, edgecolor='C%d'%chip, facecolor='C%d'%chip)
    # ax.hist(chdata_unordered,num_bins,color='C%d'%chip)
    # print(np.histogram(chdata_unordered))
    ax.stairs(ch_hist_data, x, fill=True, color='C%d'%chip)
    # ax.hist(chdata_unordered,bins=num_bins,color='C%d'%chip)
    
    print(ch)
    print (ch_hist_data[0:50])
    input ()
# plt.xticks(ticks=[0x48d, 0x2af3]) #<- the 2 values expected from test pattern   
# ax.get_xaxis().set_major_formatter(ticker.FormatStrFormatter("0x%x"))

# plt.title("ADC Histogram w/ No Pulse (2000 samples)")
# plt.title("ADC Histogram w/ DAC constant voltage of ~1.22V (2000 samples)")
# plt.title("ADC Histogram w/ Test Pattern (2000 samples)")
# plt.title("ADC Histogram Ch %d w/ Test Pattern (2000 samples)"%(ch))

#for stuff with a lot of data outside bounds
plt.ylim([0,real_max+10])


plt.savefig(fdir+"adc_hist.jpg")





# plt.savefig(fdir+"adc_hist"+str(ch)+".jpg")

plt.close()
