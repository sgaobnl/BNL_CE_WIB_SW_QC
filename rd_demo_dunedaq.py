import sys 
import numpy as np
import pickle
import time, datetime, random, statistics
import matplotlib.pyplot as plt
import copy

import struct
from dunedaq_decode import wib_dec

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

# bufs = [[],[],[],[],[],[],[],[]]

# for i in range(8):
    # bufs[i] = rawdata[runi][0][i]

# buf_end_addr = rawdata[runi][1] 
# trigger_rec_ticks = rawdata[runi][2]
# if rawdata[runi][3] != 0:
    # trigmode = 'HW'; 
# else:
    # trigmode = 'SW'; 
    
start_time = time.time()     
#dec_data = wib_spy_dec_syn_dunedaq(bufs,fembs)
wibdata = wib_dec(rawdata,fembs, spy_num=1)
# print("Done decoding")
wibdata = wibdata[0]

datd = [wibdata[0], wibdata[1],wibdata[2],wibdata[3]][fembs[0]]

###TODO add a way to get coldata timestamps?

    
# for femb in fembs:
    # data0 = dec_data[femb*2][0]
    # data1 = dec_data[femb*2+1][0]
    # data0 = np.transpose(data0)
    # #print(np.shape(data0))
    # data1 = np.transpose(data1)
    # wib[femb] = np.concatenate((data0, data1))
    # #print(np.shape(wib[femb]))
    # # wib[femb] = list(wib[femb])

end_time = time.time()
elapsed = end_time - start_time
print("Done decoding and transposing. Total elapsed:",elapsed)
#print("tmts",len(tmts))
#print("num samples",len(wib[0][0]))
# x = np.arange(len(tmts))

for fe in range(8):
    for fe_chn in range(16):
        fechndata = datd[fe*16+fe_chn]
        if np.max(fechndata) - np.mean(fechndata) > 6000:
            pass
        else:
            print (fe*16+fe_chn,fe, fe_chn, hex(fechndata[0])) 
        if fe*16+fe_chn < 64:
            c = 'r'
        else:
            c = 'b'
        plt.plot(fechndata, color=c)
        #rms.append(np.std(fechndata[350:450]))
#print (rms)
#plt.plot(np.arange(128),rms)
plt.savefig(fdir + f"{fembs[0]}_wf.jpg")#plt.show()
plt.show()
plt.close()
    
# if True:
    # fig = plt.figure(figsize=(10,6))
    # plt.plot(tmts)
    # plt.savefig(fdir + "timestamp.jpg")
    # plt.close()
    # # plt.plot(x_tmts, np.array(tmts)-tmts[0], label ="Time Master Timestamp")
    # # plt.plot(x_tmts, np.array(cdts_0[0])-cdts_0[0][0], label ="Coldata Timestamp (FEMB0 CD0)")
    # # plt.plot(x_tmts, np.array(cdts_1[0])-cdts_1[0][0], label ="Coldata Timestamp (FEMB0 CD1)")
    # # plt.legend()
    # ## plt.show()
    # # plt.savefig(fdir + "timestamp.jpg")
    # # plt.close()

    # for fembi in fembs:
        # #maxpos = np.where(wib[fembi][0][0:1500] == np.max(wib[fembi][0][0:1500]))[0][0] #not used?
        # fig = plt.figure(figsize=(10,6))
        
        # for chip in range(8): #adc
            # for chn in range(16):
                # i = chip*16 + chn
                # # if chn == 0:
                   # # plt.plot(x, wib[fembi][i],color = 'C%d'%chip, label = "Chip%dCH0"%chip )
                   
                # # if not all(wib[fembi][i][tick] == wib[fembi][i][0] for tick in range(len(wib[fembi][i]))):
                    # # print("FEMB%dChip%dCH%d messed up"%(fembi,chip,chn))
                # # else:
                    # # print("Chip%dCH%d all channels = 0x%x"%(chip,chn,wib[fembi][i][0])) #all channels same value
                
                # plt.plot(x, wib[fembi][i],color = 'C%d'%i )
                # # if i % 16 < 8 and not all (samp == 0x2af3 for samp in wib[fembi][i]):
                    # # print("Channel",i,"not correct:")
                    # # print([hex(samp) for samp in wib[fembi][i]])
                # # elif i % 16 >= 8 and not all (samp == 0x48d for samp in wib[fembi][i]):
                    # # print("Channel",i,"not correct:")
                    # # print([hex(samp) for samp in wib[fembi][i]])                
                # # if i == 0 or i == 8:
                    # # plt.plot(x, wib[fembi][i],color = 'C%d'%i )
        # plt.title(f"Waveform of FEMB{fembi}")
        # #plt.xlim([0,75])
        # #plt.ylim([800,1000])
        # #plt.legend()
        # ##plt.show()
        # plt.savefig(fdir + f"{fembi}_wf_dunedaq.jpg")
        # plt.close()   