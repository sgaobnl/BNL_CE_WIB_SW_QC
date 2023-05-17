import sys 
import numpy as np
import pickle
import time, datetime, random, statistics
import matplotlib.pyplot as plt
import copy

import struct
from spymemory_decode import wib_spy_dec_syn

fp = sys.argv[1]
femb = int(sys.argv[2])
if "/" in fp:
    sfn = fp.split("/")
elif "\\" in fp:
    sfn = fp.split("\\")
p = fp.find(sfn[-1])
fdir = fp[0:p]

with open(fp, 'rb') as fn:
    raw = pickle.load(fn)

rawdata = raw[0]
pwr_meas = raw[1]
runi = int(sys.argv[3])

buf0 = rawdata[runi][0][0]
buf1 = rawdata[runi][0][1]
buf_end_addr = rawdata[runi][1] 
trigger_rec_ticks = rawdata[runi][2]
if rawdata[runi][3] != 0:
    trigmode = 'HW'; 
else:
    trigmode = 'SW'; 
dec_data = wib_spy_dec_syn(buf0, buf1, trigmode, buf_end_addr, trigger_rec_ticks, [femb])

if femb<=1:
    link = 0
else:
    link = 1

flen = len(dec_data[link])
print (flen)

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

    #sfs1.append(dec_data[1][i]["FEMB_SF"])
    #cdts_l1.append(dec_data[1][i]["FEMB_CDTS"])
    #femb2.append(dec_data[1][i]["FEMB0_2"])
    #femb3.append(dec_data[1][i]["FEMB1_3"])
 
print (f"timestampe of first 10 events {tmts[0:10]}")

femb0 = list(zip(*femb0))
femb1 = list(zip(*femb1))
femb2 = list(zip(*femb2))
femb3 = list(zip(*femb3))
    
wibs = [femb0, femb1, femb2, femb3]
    
x = np.arange(len(tmts))

if True:
    fig = plt.figure(figsize=(10,6))
    plt.plot(x, np.array(tmts)-tmts[0], label ="Time Master Timestamp")
    plt.plot(x, np.array(cdts_l0)-cdts_l0[0], label ="Coldata Timestamp")
#    plt.plot(x, np.array(cdts_l1)-cdts_l1[0], label ="Coldata Timestamp")
    plt.legend()
    plt.show()
#    plt.savefig(fdir + "timestamp.jpg")
    plt.close()
        
    #for fembi in range(4):
    for fembi in [femb]:
        #maxpos = np.where(wibs[fembi][0][0:1500] == np.max(wibs[fembi][0][0:1500]))[0][0]
        fig = plt.figure(figsize=(10,6))
        for chip in range(8):
            for chn in range(16):
                i = chip*16 + chn
                #if chn == 0:
                #    plt.plot(x, wibs[fembi][i],color = 'C%d'%chip, label = "Chip%dCH0"%chip )
                #else:
                #plt.plot(x, wibs[fembi][i],color = 'C%d'%chip, label=chip )
                if chn == 0:
                    plt.plot(x, wibs[fembi][i],color = 'C%d'%chip, label=chip )
                else:
                    plt.plot(x, wibs[fembi][i],color = 'C%d'%chip )
                pp = np.max(wibs[fembi][i])
                pm = np.min(wibs[fembi][i])
                if pm > 15000:
                    print ("FEMB%d CHIP%d CHN%d"%(fembi, chip, chn))

                #if pp-pm < 2000:
                #    print ("FEMB%d CHIP%d CHN%d"%(fembi, chip, chn))
        plt.title(f"Waveform of FEMB{fembi}")
        plt.legend()
        plt.show()
        #plt.savefig(fdir + f"{fembi}_wf.jpg")
        plt.close()
