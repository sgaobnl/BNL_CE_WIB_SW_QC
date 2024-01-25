import time
import sys
import numpy as np
import pickle
import copy
import time, datetime, random, statistics    
from spymemory_decode import wib_dec
from scipy.fftpack import fft,rfft,ifft,fftn
import matplotlib.pyplot as plt

def chn_rfft_psd(chndata, fs = 2000000.0, fft_s = 2000, avg_cycle = 50):  
    #Averaged RFFT and Power Spectral Density calculations
    ts = 1.0/fs 
    len_chndata = len(chndata)
    avg_cycle_tmp = avg_cycle
    if ( len_chndata >= fft_s * avg_cycle_tmp):
        pass
    else:
        avg_cycle_tmp = (len_chndata//fft_s)

    p = np.array([])
    for i in range(0,avg_cycle_tmp,1):
        x = chndata[i*fft_s:(i+1)*fft_s]
        #window = np.hanning(len(x))
        #x = x * window 
        if ( i == 0 ):
            #FFT computing and normalization
            p = abs(rfft(x, 2048)/fft_s)**2     
        else:
            p = p + (abs(rfft(x)/fft_s))**2   
    #PSD calculation
    psd = p / avg_cycle_tmp
    psd = p / ( fs/fft_s)
    psd = p*2
    f = np.linspace(0,fs/2,len(psd))
    psd = 10*np.log10(psd)
    return f,p,psd


fdir = "./tmp_data/"
fp = fdir + "LN_QC_sine_21_12_2023_15_21_31.bin"
with open(fp, 'rb') as fn:
    data = pickle.load( fn)

dkeys = list(data.keys())
if "logs" in dkeys:
    dkeys.remove("logs")


fin = 50544.738 #Hz input 
fs = 1953125 #Hz
Ntot = 2**(14)
avgs =1 
Nsamps = (avgs+2)*Ntot

print (dkeys)
for onekey in dkeys:
    print (onekey)
    cfgdata = data[onekey]
    fembs = [0] 
    rawdata = cfgdata 
    #fembs = cfgdata[1]
    #rawdata = cfgdata[0]

    wibdata = wib_dec(rawdata,fembs, spy_num=1)[0]
    print (len(wibdata))
    #wibdata = wib_dec(rawdata,fembs, spy_num=1)

    datd = [wibdata[0], wibdata[1],wibdata[2],wibdata[3]][0]

    for fe in range(8):
        #for fe_chn in range(16):
        for fe_chn in [1]:
            fechndata = datd[fe*16+fe_chn]
            print (np.max(fechndata), np.min(fechndata))
            fig = plt.figure(figsize=(10,8))
            plt.plot(fechndata[0:200])
            plt.show()
            plt.close()
            f, p, psd = chn_rfft_psd(fechndata, fs = fs, fft_s = 2048, avg_cycle = 1)
            trunc = 10
            p = p[trunc:Ntot-trunc]

            #Span three bins at side of fundamental to calculate signal power
            p_aux = np.copy(p)
            noise = min(p)
            mx_arr = np.where(p_aux == max(p_aux))
            mx = mx_arr[0][0]
            signal_pwr = max(p_aux)
            span = 3
            p_aux[mx] = noise
            for k in range(1, span+1):
                signal_pwr = signal_pwr + p[mx+k] + p[mx-k]
                p_aux[mx+k] = noise
                p_aux[mx-k] = noise

            
            ##### Extract parameters of interest #####
            NAD = np.sum(p) - signal_pwr
            SINAD = 10*np.log10( signal_pwr / NAD )
            Vfullscale = 1.4
            Vinput = 1.2
            ENOB = (SINAD - 1.76 + 20*np.log10(Vfullscale/Vinput)) / 6.02
            #continue
            
            fundamental = max(p)
            SFDR = 10*np.log10( fundamental / max(p_aux))
            print (SINAD, ENOB, NAD, 20*np.log10(Vfullscale/Vinput), Vfullscale, Vinput)
            print (SFDR)
            #enob_all.append(ENOB)

            fig = plt.figure(figsize=(10,8))
            #psd = psd[trunc:Ntot-trunc]
            psd = psd
            psd_dbfs = psd - max(psd) - 20*np.log10(Vfullscale/Vinput)
            points_dbfs = np.linspace(0,fs/2, len(psd_dbfs))
            plt.plot(points_dbfs, psd_dbfs)
            #plt.title('%s Environment. %s Reference. Channel %d'%(env, refs,chnno))
            #plt.xlabel('Frequency [kHz]')
            #plt.ylabel('Amplitude [dBFS]')
            #plt.annotate('SFDR = %0.2f dB \nSINAD = %0.2f dB \nENOB = %0.2f bits' %(np.around(SFDR, decimals=2), np.around(SINAD, decimals=2), np.around(ENOB, decimals = 2)), 
            #             xy=(0.6,0.8),xycoords='axes fraction', textcoords='offset points', size=22, bbox=dict(boxstyle="round", fc=(1.0, 1.0, 1.0), ec="none"))
            
            plt.tight_layout()
            #figure_name =  enob_dir + "ENOB_%s_%s_ch%d"%(env,refs,chnno) + ".png" 
            #print (figure_name)
            #plt.savefig(figure_name)
            plt.show()
            plt.close()  
            input ()
    
    import matplotlib.pyplot as plt
    for fe in range(8):
        for fe_chn in range(16):
            fechndata = datd[fe*16+fe_chn]
#            if np.max(fechndata) - np.mean(fechndata) > 8000:
#                pass
#            else:
#                print (fe*16+fe_chn,fe, fe_chn) 
            plt.plot(fechndata[0:2100])
    plt.show()
    plt.close()
            #    pp = np.max(fechndata[500:1500])
            #    pp_pos = np.where(fechndata[500:1500] == pp)[0][0]
            #    x = np.arange(300)
            #    plt.plot(x,fechndata[500+pp_pos-100:500+pp_pos+200])
            #    ped = np.mean(fechndata[pp_pos-200:pp_pos-150])
            #    npmin = np.min(fechndata)
            #    print (fe, fe_chn, pp, ped, npmin)
            #    plt.show()
            #    plt.close()

# ... (rest of your code)
 
#    print (pwr)
            




    
