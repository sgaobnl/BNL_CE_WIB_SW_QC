import sys 
import numpy as np
import pickle
import time, datetime, random, statistics
import matplotlib.pyplot as plt
import copy

import struct
from spymemory_decode import wib_dec

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
    
rawdata = raw[0]
pwr_meas = raw[1]
runi = 0
fembs = [int(sys.argv[2])]

wibdata = wib_dec(rawdata,fembs, spy_num=1)

wibdata = wibdata[0]

datd = [wibdata[0], wibdata[1],wibdata[2],wibdata[3]][fembs[0]]

import matplotlib.pyplot as plt
for fe in range(8):
    for fe_chn in range(16):
        fechndata = datd[fe*16+fe_chn]
        if np.max(fechndata) - np.mean(fechndata) > 6000:
            print (fe*16+fe_chn,fe, fe_chn) 
        else:
            pass
        if fe*16+fe_chn < 64:
            c = 'r'
        else:
            c = 'b'
        plt.plot(fechndata, color=c)
plt.show()
plt.close()
#bufs = [[],[],[],[],[],[],[],[]]
#
#for i in range(8):
#    bufs[i] = rawdata[runi][0][i]
#
#buf_end_addr = rawdata[runi][1] 
#trigger_rec_ticks = rawdata[runi][2]
#if rawdata[runi][3] != 0:
#    trigmode = 'HW'; 
#else:
#    trigmode = 'SW'; 
#    
#dec_data = wib_spy_dec_syn(bufs, trigmode, buf_end_addr, trigger_rec_ticks, fembs)
#print("Done decoding")
#flen = len(dec_data[0])
#for d in dec_data:
#    print(len(d))
#
#tmts = []
##sfs0 = [] #not in new format?
##sfs1 = []
#cdts_0 = [[],[],[],[],[],[],[],[]]
#cdts_1 = [[],[],[],[],[],[],[],[]]
#femb0 = []
#femb1 = []
#femb2 = []
#femb3 = []
#
#for i in range(flen):
#    tmts.append(dec_data[0][i]["TMTS"])
#    #print(hex(tmts[-1]))
#
#    for cd in range(8):
#        if cd // 2 in fembs:
#            cdts_0[cd].append(dec_data[cd][i]["FEMB_CD0TS"])
#            cdts_1[cd].append(dec_data[cd][i]["FEMB_CD1TS"])
#        
#    if 0 in fembs:
#        chdata_64ticks = [dec_data[0][i]["CD_data"][tick] + dec_data[1][i]["CD_data"][tick] for tick in range(64)]        
#        femb0 = femb0 + chdata_64ticks        
#    
#    if 1 in fembs:        
#        chdata_64ticks = [dec_data[2][i]["CD_data"][tick] + dec_data[3][i]["CD_data"][tick] for tick in range(64)]        
#        femb1 = femb1 + chdata_64ticks             
#    
#    if 2 in fembs:       
#        chdata_64ticks = [dec_data[4][i]["CD_data"][tick] + dec_data[5][i]["CD_data"][tick] for tick in range(64)]        
#        femb2 = femb2 + chdata_64ticks             
#    
#    if 3 in fembs:
#        chdata_64ticks = [dec_data[6][i]["CD_data"][tick] + dec_data[7][i]["CD_data"][tick] for tick in range(64)]        
#        femb3 = femb3 + chdata_64ticks             
#
#print (f"timestampe of first 10 events {tmts[0:10]}")
#
#femb0 = list(zip(*femb0))
#femb1 = list(zip(*femb1))
#femb2 = list(zip(*femb2))
#femb3 = list(zip(*femb3))
#
#wib = [femb0, femb1, femb2, femb3]
#
#x = np.arange(len(tmts)*64)
#x_tmts = np.arange(len(tmts))
#
#if True:
#    fig = plt.figure(figsize=(10,6))
#    plt.plot(x_tmts, np.array(tmts)-tmts[0], label ="Time Master Timestamp")
#    plt.plot(x_tmts, np.array(cdts_0[0])-cdts_0[0][0], label ="Coldata Timestamp (FEMB0 CD0)")
#    plt.plot(x_tmts, np.array(cdts_1[0])-cdts_1[0][0], label ="Coldata Timestamp (FEMB0 CD1)")
#    plt.legend()
#    #plt.show()
#    plt.savefig(fdir + "timestamp.jpg")
#    plt.close()
#
#    for fembi in fembs:
#        #maxpos = np.where(wib[fembi][0][0:1500] == np.max(wib[fembi][0][0:1500]))[0][0] #not used?
#        fig = plt.figure(figsize=(10,6))
#        
#        for chip in range(8): #coldata
#            for chn in range(16):
#                i = chip*16 + chn
#                # if chn == 0:
#                   # plt.plot(x, wib[fembi][i],color = 'C%d'%chip, label = "Chip%dCH0"%chip )
#                   
#                # if not all(wib[fembi][i][tick] == wib[fembi][i][0] for tick in range(len(wib[fembi][i]))):
#                    # print("FEMB%dChip%dCH%d messed up"%(fembi,chip,chn))
#                # else:
#                    # print("Chip%dCH%d all channels = 0x%x"%(chip,chn,wib[fembi][i][0])) #all channels same value
#                plt.plot(x, wib[fembi][i],color = 'C%d'%chip )        
#        plt.title(f"Waveform of FEMB{fembi}")
#        # plt.xlim([0,400])
#        # plt.ylim([0,1000])
#        #plt.legend()
#        ##plt.show()
#        plt.savefig(fdir + f"{fembi}_wf.jpg")
#        plt.close()    
#    
