import sys 
import numpy as np
import pickle
import time, datetime, random, statistics
import copy

import struct
import platform
system_info = platform.system()

index_tmts = 5
if system_info=='Linux':
    sys.path.append('./Analysis/decode/')
    from dunedaq_decode import wib_dec
    index_tmts=4
    sys.path.append('../../')
elif system_info=='Windows':
    from spymemory_decode import wib_dec
    index_tmts=5

def data_ana(fembs, rawdata, rms_flg=False, period=512, spy_num=10):
    wibdatas = wib_dec(rawdata,fembs, spy_num=spy_num, cd0cd1sync=False)
    dat_tmts_l = []
    dat_tmts_h = []
    for wibdata in wibdatas:
        dat_tmts_l.append(wibdata[index_tmts][fembs[0]*2][0]) #LSB of timestamp = 16ns
        dat_tmts_h.append(wibdata[index_tmts][fembs[0]*2+1][0])

    # period = 512
    dat_tmtsl_oft = (np.array(dat_tmts_l)//32)%period #ADC sample rate = 16ns*32 = 512ns
    dat_tmtsh_oft = (np.array(dat_tmts_h)//32)%period #ADC sample rate = 16ns*32 = 512ns

    # concatenate data
    all_data = []
    #import matplotlib.pyplot as plt
    for achn in range(128):
        conchndata = []

        for i in range(len(wibdatas)):
            if achn<64:
                oft = dat_tmtsl_oft[i]
            else:
                oft = dat_tmtsh_oft[i]

            wibdata = wibdatas[i]
            datd = [wibdata[0], wibdata[1],wibdata[2],wibdata[3]][fembs[0]]
            chndata = np.array(datd[achn], dtype=np.uint32)
            lench = len(chndata)
            tmp = int(period-oft)
            conchndata = conchndata + list(chndata[tmp : ((lench-tmp)//period)*period + tmp])
        all_data.append(conchndata)

    chns = list(range(128))
    rmss = []
    peds = []
    pkps, pkns = [], []
    wfs, wfsf = [], []
    for achn in range(128):
        chdata = []
        N_period = len(all_data[achn])//period
        for iperiod in range(N_period):
            istart = iperiod*period
            iend = istart + period
            chunkdata = all_data[achn][istart : iend]
            chdata.append(chunkdata)
        chdata = np.array(chdata)
        avg_wf = np.average(np.transpose(chdata), axis=1, keepdims=False)
        wfsf.append(avg_wf)
        amax = np.max(avg_wf)
        amin = np.min(avg_wf)
        pkps.append(amax)
        pkns.append(amin)
        if achn == 0:
            ppos = np.where(avg_wf==amax)[0][0]
            p0=ppos + period

        peddata = []
        for iperiod in range(N_period-3):
            #print (p0 + iperiod*period - 250, p0 + iperiod*period - 50, len(all_data[achn][p0 + iperiod*period - 250: p0 + iperiod*period-50]))
            peddata += all_data[achn][p0 + iperiod*period - 250: p0 + iperiod*period-50]
        rmss.append(np.std(peddata))
        peds.append(np.mean(peddata))

    
        tmpwf = avg_wf
        wfs.append(tmpwf)

    return chns, rmss, peds, pkps, pkns, wfs,wfsf


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


chns, rmss, peds, pkps, pkns, wfs,wfsf = data_ana(fembs, rawdata, rms_flg=False, period=1000, spy_num=10)

import matplotlib.pyplot as plt
ch = 0
print (rmss[ch], peds[ch], pkps[ch], pkns[ch])
oft = int(input("shift waveform = "))

for ch in range(16):
    if oft == 0:
        wfdata = np.array(wfs[ch])-peds[ch]
    else:
        wfdata = (list(np.array(wfs[ch])-peds[ch]))[oft:] + (list(np.array(wfs[ch])-peds[ch]))[0:oft]
    plt.plot(wfdata, color="C%d"%(ch//16))

for ch in range(64,80,1):
    if oft == 0:
        wfdata = np.array(wfs[ch])-peds[ch]
    else:
        wfdata = (list(np.array(wfs[ch])-peds[ch]))[oft:] + (list(np.array(wfs[ch])-peds[ch]))[0:oft]
    plt.plot(wfdata, color="C%d"%(ch//16))


plt.show()
plt.close()


print ("Done")

exit()

wibdata = wib_dec(rawdata,fembs, spy_num=10)

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
            if True :
                plt.plot(fechndata, label="%d"%fe_chn)
            rms.append(np.mean(fechndata))
            if fe==0 and fe_chn==2:
                print (np.mean(fechndata))
    plt.legend()
    plt.grid()
    plt.show()
    plt.close()
    exit()

    plt.plot(np.arange(128),rms, color='b', marker = '.', label="RMS")
    for i in range(0,128,8):
        plt.vlines(i-0.5, -1, 17000, color='y')
    plt.title("ADC pedestal distribution (Vrefp DAC = 0x33) ")
    plt.ylabel("ADC count / bit")
    plt.ylim((0,17000))
    plt.xlim((-1,130))
    plt.xlabel("Channel")
    plt.tight_layout( rect=[0.05, 0.05, 0.95, 0.95])
    plt.show()
    plt.close()



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


    ax1.set_title("Overlap Waveforms of CH0-63")
    ax1.set_ylabel("ADC readout / bit")
    ax1.set_xlabel("Time (512ns/step)")
    ax2.set_title("Overlap Waveforms of CH64-127")
    ax2.set_ylabel("ADC readout / bit")
    ax2.set_xlabel("Time (512ns/step)")


    ax1.grid()
    ax2.grid()
    
    plt.tight_layout( rect=[0.05, 0.05, 0.95, 0.95])
    plt.show()
    plt.close()
    exit()

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

