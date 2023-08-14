import sys 
import numpy as np
import pickle
import time, datetime, random, statistics
import matplotlib.pyplot as plt
import copy

import struct
from spymemory_decode import wib_dec

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
runi = 0

wib_data = wib_dec(rawdata, fembs=[femb], spy_num=1)


tmts = wib_data[4]
femb0 = wib_data[0]
femb1 = wib_data[1]
femb2 = wib_data[2]
femb3 = wib_data[3]

wibs = [femb0, femb1, femb2, femb3]
    
if True:
#    fig = plt.figure(figsize=(10,6))
#    plt.plot(x, np.array(tmts[0])-tmts[0][0], label ="Time Master Timestamp")
##    plt.plot(x, np.array(cdts_l0)-cdts_l0[0], label ="Coldata Timestamp")
##    plt.plot(x, np.array(cdts_l1)-cdts_l1[0], label ="Coldata Timestamp")
#    plt.legend()
#    plt.show()
#    #plt.savefig(fdir + "timestamp.jpg")
#    plt.close()
        
    #for fembi in range(4):
    if True :
#        chn_cs = int(input("Chn = "))
        for chn in range(16):
            print (chn)
            for fembi in [femb]:
                maxpos = np.where(wibs[fembi][0][0:1500] == np.max(wibs[fembi][0][0:1500]))[0][0]
                fig = plt.figure(figsize=(10,6))
                for chip in range(8):
                    plt.subplot(2,4,chip+1)
                    #for chn in range(16):
                    if True:
                        i = chip*16 + chn
                        #if chn == 0:
                        plt.plot(wibs[fembi][i],color = 'C%d'%chip, label = "Chip%dCH0"%chip )
                        ##else:
                        #xmin = 0
                        #xmax = 1000
                        #plt.plot(wibs[fembi][i][xmin:xmax],color = 'C%d'%chip, label = "Chip%dCH%d"%(chip, chn))
                        plt.ylim((0,16000))
                        plt.legend()
                #plt.title(f"Waveform of FEMB{fembi}_CHN{chn}")
                plt.show()
                plt.tight_layout( rect=[0.05, 0.05, 0.95, 0.95])
                #plt.savefig(fdir + f"FEMB_{fembi}_wf_{chn}_ab.jpg")
                plt.close()
                exit()
