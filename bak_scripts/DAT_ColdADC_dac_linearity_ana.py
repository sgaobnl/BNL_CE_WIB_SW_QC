import sys 
import numpy as np
import pickle
import struct
import time, datetime, random, statistics
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

def linear_fit(x, y):
    error_fit = False 
    try:
        results = sm.OLS(y,sm.add_constant(x)).fit()
    except ValueError:
        error_fit = True 
    if ( error_fit == False ):
        error_gain = False 
        try:
            slope = results.params[1]
        except IndexError:
            slope = 0
            error_gain = True
        try:
            constant = results.params[0]
        except IndexError:
            constant = 0
    else:
        slope = 0
        constant = 0
        error_gain = True

    y_fit = np.array(x)*slope + constant
    delta_y = abs(y - y_fit)
    inl = delta_y / (max(y)-min(y))
    peakinl = max(inl)
    return slope, constant, peakinl, error_gain

fp = sys.argv[1]
sfn = fp.split("/") #default
if "/" in fp:
    sfn = fp.split("/")
elif "\\" in fp:
    sfn = fp.split("\\")
p = fp.find(sfn[-1])
fdir = fp[0:p]

with open(fp, 'rb') as fn:
    raw = pickle.load(fn)
    raw = raw["LIN"]
    
dacs = []
chmeans = []
for i in range(len(raw)):
    dac = raw[i][0]
    hist_data = raw[i][1]

    num_16bwords = 0x8000 / 2        
    words16b = list(struct.unpack_from("<%dH"%(num_16bwords),hist_data))

    sumv = 0
    sumn = 0
    for i in range(len(words16b)):
        if words16b[i] != 0 :
            sumv = sumv + i*words16b[i]
            sumn = sumn + words16b[i]
    chmean = int(sumv/sumn)
    dacs.append(dac)
    chmeans.append(chmean)

dacvs = (np.array(dacs)/65535)*2.5

vmin=0.4
vmini = 0
vmax=1.4
vmaxi=len(dacvs)
for i in range(10000):
    if dacvs[i] > vmin:
        vmini = i
        break
for i in range(len(dacvs)-1, 0, -1):
    if dacvs[i] < vmax:
        vmaxi = i
        break

print (vmini, vmaxi)

import statsmodels.api as sm
results = linear_fit(x = dacvs[vmini:vmaxi], y =chmeans[vmini:vmaxi])
fitchmeans = results[1] + results[0]*np.array(dacvs)
diffs = chmeans-fitchmeans

fig, ax = plt.subplots(figsize=(10,6)) #one "FEMB"
ax.plot(dacvs, chmeans)
ax.plot(dacvs, fitchmeans, c='r')
plt.show()
plt.close()

fig, ax = plt.subplots(figsize=(10,6)) #one "FEMB"
ax.plot(dacvs, diffs)
plt.ylim((-50,50))
plt.show()
plt.close()

lims = []
for i in range(len(diffs)):
    if abs(diffs[i]) < 10:
        lims.append(i)
lim_min = np.min(lims)
lim_max = np.max(lims)
print (dacvs[lim_min], dacvs[lim_max], dacvs[lim_max]-dacvs[lim_min])



#chdiffs = []
#for i in range(len(chmeans)-1):
#    chdiffs.append(chmeans[i+1]-chmeans[i])
#
#print ((np.array(dacs)/65535)*2.5)
#print (chdiffs)

#num_bins = 50
#x = np.arange(0,pow(2,14)+1)
#real_max = 0 #for stuff with a lot of data outside bounds
#ch_cs = int(input("select a channel (0-127):"))
#for ch, ch_hist_data in enumerate(hist_data):
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
#
#
#        chip = ch // 16
#        print (chip)
#        num_16bwords = 0x8000 / 2        
#        words16b = list(struct.unpack_from("<%dH"%(num_16bwords),ch_hist_data))
#        #if any(height > real_max for height in words16b[1:-1]): 
#        #    real_max = max(words16b[1:-1])                
#        #ax.stairs(words16b, x, fill=True, color='C%d'%chip)
#        fig, ax = plt.subplots(figsize=(10,6)) #one "FEMB"
#
#        x = np.arange(2**14)
#        tmp = 600
#        x = x[tmp:-1*tmp]
#        y = np.array(words16b[tmp:-1*tmp])
#        tot = np.sum(y)/len(x)
#        ny = (y*1.0)/tot - 1
#        #print (tot, ny[1000:1100])
#        inl = []
#        for i in range(len(ny)):
#            inl.append(np.sum(ny[0:i+1]))
#
#        ax.plot (x, ny)
#        ax.plot (x, inl)
##        ax.set_ylim((-1,1))
##        ax.plot (x, inl, c="C1")
#        #ax.plot (x[2000:-2000], np.array(inl[2000:-2000])-inl[2000])
#        plt.ylabel("LSB")
#        plt.xlabel("ADC code / bit")
#
#        plt.show()
#        plt.close()
#        exit()
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






