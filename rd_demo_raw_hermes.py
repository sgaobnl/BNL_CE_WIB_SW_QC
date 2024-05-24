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
#fembs = [int(sys.argv[2])]
fembs = [0]

wibdata = wib_dec(rawdata,fembs, spy_num=10)
#wibdata = wib_dec(rawdata,fembs, spy_num=1)

datd = []
fechndata = []
for i in [0]:
    wibdatai = wibdata[i]
    datd = [wibdatai[0], wibdatai[1],wibdatai[2],wibdatai[3]][fembs[0]]


if 1:
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(8,6))
    plt.rcParams.update({'font.size': 14})
    rms = []
    pkp  = []
    for fe in range(8):
        for fe_chn in range(16):
    
            fechndata = datd[fe*16+fe_chn]
            #if fe == 5 and (fe_chn in [11, 12, 13]):
            #if fe == 6 and (fe_chn in [3, 4, 5]):
            #if fe == 3 and (fe_chn in [0, 1]):
            #if fe == 4 and (fe_chn in [3, 4,5]):
            #if fe == 7 and (fe_chn in [0, 1,2]):
            #if fe == 3  :
            if True :
            #if fe == 4 and (fe_chn in [0, 8, 10]):
            #if fe == 1 and (fe_chn in [5, 6,7]):
            #if fe == 2 : #femb1
            #if fe == 2 and (fe_chn in [11, 12]):
            #if fe == 6 and (fe_chn in [0, 1]):
            #if fe == 3 and (fe_chn in [0, 1]):
            #if fe == 0 and (fe_chn in [3, 4, 5]):
                plt.plot(fechndata, label="%d"%fe_chn)
            #if fe == 6 and fe_chn==4:
            #    plt.plot(fechndata)
            #if fe == 6 and fe_chn==5:
            #    plt.plot(fechndata)
    #        print (np.std(fechndata))
#            rms.append(np.std(fechndata))
#            pkp.append(np.max(fechndata))
            rms.append(np.mean(fechndata))
            if fe==0 and fe_chn==2:
                print (np.mean(fechndata))
    plt.legend()
    plt.grid()
    plt.show()
    plt.close()
    exit()

    plt.plot(np.arange(128),rms, color='b', marker = '.', label="RMS")
#    plt.plot(np.arange(64,128,1),rms[64:128], color='r', label="Separate")
#    plt.legend()
#    plt.grid()
#    
    for i in range(0,128,8):
        plt.vlines(i-0.5, -1, 17000, color='y')
#
#    plt.title("ADC noise distribution (bypass SHA) ")
#    plt.title("ADC noise distribution (known anlog patten, SHA) ")
#    plt.ylabel("RMS noise / bit")
#    plt.ylim((-1,5))
#    plt.xlim((-1,130))
#    plt.xlabel("Channel")
###    plt.grid()
#    plt.tight_layout( rect=[0.05, 0.05, 0.95, 0.95])
#    plt.show()
#    plt.close()
#

#    #plt.title("ADC pedestal distribution (bypass SHA) ")
#    plt.title("ADC pedestal distribution (known anlog patten, diff) ")
#    plt.title("ADC pedestal distribution (known anlog patten, SHA) ")
    plt.title("ADC pedestal distribution (Vrefp DAC = 0x33) ")
#    #plt.ylabel("RMS noise / bit")
    plt.ylabel("ADC count / bit")
    plt.ylim((0,17000))
    plt.xlim((-1,130))
    plt.xlabel("Channel")
#    plt.grid()
    plt.tight_layout( rect=[0.05, 0.05, 0.95, 0.95])
    plt.show()
    plt.close()

#    plt.title("ADC test pattern")
#    #plt.ylabel("RMS noise / bit")
#    plt.ylabel("RMS noise / bit")
#    plt.ylim((0,17000))
#    plt.xlim((-10,130))
#    plt.xlabel("Channel")
#    plt.grid()
#    plt.tight_layout( rect=[0.05, 0.05, 0.95, 0.95])
#    plt.show()
#    plt.close()


    exit()



#for xi in [0,4]:
#    datd = []
#    fechndata = []
#    for i in range(10):
#    #for i in [0]:
#        wibdatai = wibdata[i]
#        datd = [wibdatai[0], wibdatai[1],wibdatai[2],wibdatai[3]][fembs[0]]
#        for fe in [xi]:
#            for fe_chn in [0]:
#                fechndata = fechndata + list(datd[fe*16+fe_chn])
#    
#    print (fe*16+fe_chn, "RMS=%.3f"%np.std(fechndata))
#    #print (len(fechndata))
##    import matplotlib.pyplot as plt
##    plt.plot(fechndata)
##    #plt.title("Waveform (leakage current = 500pA)")
##    plt.title("Waveform ")
##    plt.ylabel("ADC readout / bit")
##    plt.xlabel("Time (512ns/step)")
##    plt.show()
##    plt.close()
##
#    from fft_chn import chn_rfft_psd
#    f,p = chn_rfft_psd(fechndata,  fft_s = 2000, avg_cycle = 20)
#    import matplotlib.pyplot as plt
#    plt.plot(f,p)
#    #plt.title("Waveform (leakage current = 500pA)")
#    plt.title("FFT ")
#    plt.ylabel(" / dB ")
#    plt.xlabel("Freq / Hz")
#    plt.show()
#    plt.close()
##exit()
#####

if 0:
    import matplotlib.pyplot as plt
    rms = []
    pkp  = []
    for fe in range(8):
        for fe_chn in range(16):
    
            fechndata = datd[fe*16+fe_chn]
#            plt.plot(fechndata)
    #        print (np.std(fechndata))
            rms.append(np.std(fechndata))
#            pkp.append(np.max(fechndata))
#            rms.append(np.mean(fechndata))
    plt.plot(np.arange(64),rms[0:64], color='b', label="Tied")
    plt.plot(np.arange(64,128,1),rms[64:128], color='r', label="Separate")
    plt.legend()
#    plt.plot(np.arange(128),pkp)

#    ax1.set_title("Overlap Waveforms of CH0-63")
#    ax1.set_ylabel("ADC readout / bit")
#    ax1.set_xlabel("Time (512ns/step)")
#    ax2.set_title("Overlap Waveforms of CH64-127")
#    ax2.set_ylabel("ADC readout / bit")
#    ax2.set_xlabel("Time (512ns/step)")
#
#
#    ax1.grid()
#    ax2.grid()
    plt.grid()
    
    plt.title("Noise distribution")
    plt.ylabel("RMS noise / bit")
    plt.xlabel("Channel")
    plt.tight_layout( rect=[0.05, 0.05, 0.95, 0.95])
    plt.show()
    plt.close()
    exit()


if 1:
    import matplotlib.pyplot as plt
    rms = []
    pkp  = []
    ax1 = plt.subplot(211)
    ax2 = plt.subplot(212)
    for fe in range(8):
    #for fe in [4,5,6,7]:
    #for fe in [0,1,2,3]:
        for fe_chn in range(16):
    #for fe in [3]:
    #   for fe_chn in [0]:
    
            fechndata = datd[fe*16+fe_chn]
            if np.max(fechndata) > 12000: 
                if fe*16+fe_chn < 64:
                    print ("PLS w/ SE ON CHN %d"%(fe*16+fe_chn))
            if fe*16+fe_chn < 64: 
                ax1.plot(fechndata[000:1400], color='b' )
            else:
                ax2.plot(fechndata[000:1400], color='r' )

#            if fe*16+fe_chn < 16: 
#                ax1.plot(fechndata[000:2000], color='b' )
#                #ax1.plot(fechndata, color='b' )
#            elif fe*16+fe_chn < 32: 
#                ax1.plot(fechndata[000:2000], color='g' )
#                #ax1.plot(fechndata, color='g' )
#            elif fe*16+fe_chn < 48: 
#                ax1.plot(fechndata[000:2000], color='m' )
#                #ax1.plot(fechndata, color='m' )
#            elif fe*16+fe_chn < 64: 
#                ax1.plot(fechndata[000:2000], color='y' )
#                #ax1.plot(fechndata, color='y' )
#            else:
#                #ax2.plot(fechndata[400:900], color='r')
#                #ax2.plot(fechndata, color='r')
#                if fe*16+fe_chn < 80: 
#                    ax2.plot(fechndata[000:2000], color='b' )
#                    #ax1.plot(fechndata, color='b' )
#                elif fe*16+fe_chn < 96: 
#                    ax2.plot(fechndata[000:2000], color='g' )
#                    #ax1.plot(fechndata, color='g' )
#                elif fe*16+fe_chn < 112: 
#                    ax2.plot(fechndata[000:2000], color='m' )
#                    #ax1.plot(fechndata, color='m' )
#                elif fe*16+fe_chn < 128: 
#                    ax2.plot(fechndata[000:2000], color='y' )
#                    #ax1.plot(fechndata, color='y' )

    #        print (np.std(fechndata))
    #        rms.append(np.std(fechndata))
#            pkp.append(np.max(fechndata))
#            rms.append(np.mean(fechndata))
#    plt.plot(np.arange(128),rms)
#    plt.plot(np.arange(128),pkp)

    ax1.set_title("Overlap Waveforms of CH0-63")
    ax1.set_ylabel("ADC readout / bit")
    ax1.set_xlabel("Time (512ns/step)")
    ax2.set_title("Overlap Waveforms of CH64-127")
    ax2.set_ylabel("ADC readout / bit")
    ax2.set_xlabel("Time (512ns/step)")


    ax1.grid()
    ax2.grid()
    
#    plt.title("Noise distribution")
#    plt.ylabel("RMS noise / bit")
#    plt.xlabel("Channel")
    plt.tight_layout( rect=[0.05, 0.05, 0.95, 0.95])
    plt.show()
    plt.close()
    exit()

##for xi in range(16):
for xi in [15]:
    datd = []
    fechndata = []
    for i in range(10):
    #for i in [0]:
        wibdatai = wibdata[i]
        datd = [wibdatai[0], wibdatai[1],wibdatai[2],wibdatai[3]][fembs[0]]
        for fe in [1]:
            for fe_chn in [xi]:
                fechndata = fechndata + list(datd[fe*16+fe_chn])
    
    print (fe*16+fe_chn, "RMS=%.3f"%np.std(fechndata))
    #print (len(fechndata))
    import matplotlib.pyplot as plt
    plt.plot(fechndata)
    #plt.title("Waveform (leakage current = 500pA)")
    plt.title("Waveform ")
    plt.ylabel("ADC readout / bit")
    plt.xlabel("Time (512ns/step)")
    plt.show()
    plt.close()

    import matplotlib.pyplot as plt
    # Create a histogram
    plt.hist(fechndata, bins=(np.max(fechndata)-np.min(fechndata)+1),rwidth=0.8, color='blue', alpha=0.7)
    # Add labels and title
    plt.xlabel('Amplitude / bit')
    plt.ylabel('Counts')
    plt.title('Histogram Plot')
    # Show the plot
    plt.show()
    plt.close()

#exit()

#import matplotlib.pyplot as plt
#rms = []
#for fe in range(8):
##for fe in [2]:
#    for fe_chn in range(16):
#        fechndata = datd[fe*16+fe_chn]
#        #print (fe, fe_chn, np.std(fechndata))
#        #if np.max(fechndata) - np.mean(fechndata) > 6000:
#        #    pass
#        #else:
#        #    print (fe*16+fe_chn,fe, fe_chn) 
#        #if fe*16+fe_chn < 64:
#        #    c = 'r'
#        #else:
#        #    c = 'b'
#        #c = 'r'
#        #plt.plot(fechndata)
#        #print (np.std(fechndata))
#        #rms.append(np.std(fechndata))
##print (rms)
##plt.plot(np.arange(128),rms)
#plt.show()
#plt.close()
#

#rms = []
##for fe in range(8):
#for fe in [1]:
##    for fe_chn in range(16):
#    for fe_chn in [15]:
#        import matplotlib.pyplot as plt
#        fechndata = datd[fe*16+fe_chn]
#        #print (fe, fe_chn, np.std(fechndata))
#        #if np.max(fechndata) - np.mean(fechndata) > 6000:
#        #    pass
#        #else:
#        #    print (fe*16+fe_chn,fe, fe_chn) 
#        #if fe*16+fe_chn < 64:
#        #    c = 'r'
#        #else:
#        #    c = 'b'
#        c = 'r'
#        plt.plot(fechndata, color=c)
#        print (fe*16+fe_chn, np.std(fechndata))
#        #rms.append(np.std(fechndata))
#        #print (rms)
#        #plt.plot(np.arange(128),rms)
#        plt.show()
#        plt.close()
##bufs = [[],[],[],[],[],[],[],[]]
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
