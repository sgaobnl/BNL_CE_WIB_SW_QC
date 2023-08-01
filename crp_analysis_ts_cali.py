import time
import sys
import numpy as np
import pickle
import copy
import time, datetime, random, statistics
import os
from rawdata_dec import rawdata_dec 
from tools import Tools
import matplotlib.pyplot as plt

def noise_a_chn(chnrmsdata, chnno):
    len_chnrmsdata = len(chnrmsdata)
    rmss = []
    poss = []
    dl = 5000
    for x in range(0, len_chnrmsdata-dl, dl):
        chndata = chnrmsdata[x:x+dl ]
        rms =  np.std(chndata)
        rmss.append(rms)
        poss.append(x)
    minrms = np.min(rmss)
    minrms_pos = np.where(rmss == minrms)[0][0]
    x_pos = poss[minrms_pos]
    return minrms, chnrmsdata[x_pos:x_pos+dl] 

#fp = sys.argv[1] 
fdir = sys.argv[1] 
#runs = int(sys.argv[2])

if (os.path.exists(fdir)):
    for root, dirs, files in os.walk(fdir):
        break

for fbin in files:
    #if (".dat" in fbin) and ("02_12_09" in fbin):
    if (".dat" in fbin) :
        fp = fdir + fbin
        print (fp)
    else:
        continue

    with open(fp, 'rb') as fn:
        raw = pickle.load(fn)
    rawdata = raw[0]
    tmts_wibs = raw[1]
#    tmts_wib0 = tmts_wibs[0]
#    tmts_wib1 = tmts_wibs[1]
#    tmts_wib2 = tmts_wibs[2]
#    fig = plt.figure(figsize=(14,8))
#    plt.rcParams.update({'font.size':12})
##
#    tmts_wib0 = np.array(tmts_wibs[0]) - tmts_wibs[0][0]
#    plt.plot(tmts_wib0[0:10000], rawdata[0][0:10000], marker='.',color='r', label = "waveform")
#    plt.show()
#    plt.close()
#    exit()

    
    
    avgs = []
    for ch in range(len(rawdata)):
        wibi = ch//512
        tmts_t0 = np.array(tmts_wibs[wibi]) - tmts_wibs[wibi][0]
        period = 500
        tmts_t0_sets = [tmts_t0[0]]
        tmts_t0_sete = []
        for i in range(len(tmts_t0) - 10):
            if tmts_t0[i+1] - tmts_t0[i] > 1: 
                tmts_t0_sets.append(tmts_t0[i+1])
                tmts_t0_sete.append(tmts_t0[i])
    
        tmts_t0_sete.append(tmts_t0[-1])

        cnti = 0
        f_flg = True
        for runi in range(len(tmts_t0_sets)):
            ni = tmts_t0_sets[runi]%period
            for x in range(tmts_t0_sets[runi]+period-ni, tmts_t0_sete[runi]-period, period):
                post = np.where(tmts_t0 == x)[0][0]
                if f_flg:
                    f_flg = False
                    tdata = np.array(rawdata[ch][post:post+period]) 
                    cnti = 1
                else:
                    tdata = tdata + np.array(rawdata[ch][post:post+period]) 
                    cnti += 1
        tdata = tdata/cnti

#        fig = plt.figure(figsize=(14,8))
#        plt.rcParams.update({'font.size':12})
#        #tmts_wib0 = np.array(tmts_wibs[0]) - tmts_wibs[0][0]
#        #plt.plot(tmts_wib0[0:10000], rawdata[0][0:10000], marker='.',color='r', label = "waveform")
#        plt.plot(tdata)
#        plt.show()
#        plt.close()
#        exit()

        avgs.append(tdata)
    
    fp = fp[0:-4] + ".avg"
    with open(fp, 'wb') as fn:
        pickle.dump(avgs, fn)

exit()


#
#fig = plt.figure(figsize=(14,8))
#plt.rcParams.update({'font.size':12})
#
##plt.plot(x, rawdata[0], marker='.',color='r', label = "waveform")
#plt.plot(tmts_t0, rawdata[1], marker='.',color='b', label = "waveform")
#plt.legend()
#plt.grid()
#plt.show()
#plt.close()
#exit()


#f120hz = int ((1/120)*1e9/512)
#print ("Hz")
#print (f120hz)
#peak_poss = []
#for x in range(tmts_t0[5439], tmts_t0[-1],  f120hz):
#    if x in tmts_t0:
#        peak_poss.append(x)
#
#print (peak_poss)
#pps =[]
#for y in peak_poss:
#    if ((y-200) in tmts_t0) and ((y+200) in tmts_t0):
#        pps.append(y)
#
#print (pps)

#x = np.arange(len(tmts_t0))
#fig = plt.figure(figsize=(14,8))
#plt.rcParams.update({'font.size':12})
#for xp in pps:
#    pos = np.where(tmts_t0 == xp)[0][0]
#    ys = rawdata[0][pos-200:pos+200]
#    x = np.arange(400)
#    plt.plot(x, ys)
#x = np.arange(len(tmts_t0))
#fig = plt.figure(figsize=(14,8))
#plt.rcParams.update({'font.size':12})
#
#plt.plot(x, rawdata[0], marker='.',color='r', label = "waveform")
##plt.plot(tmts_t0, rawdata[1], marker='.',color='b', label = "waveform")
#plt.legend()
#plt.grid()
#plt.show()
#plt.close()
#print (tmts_t0[0:10], tmts_t0[2100:2150])
#exit()

#fp = fp[0:-4] + ".set"
#with open(fp, 'rb') as fn:
#    fesets = pickle.load(fn)
#[sts, snc, sg0, sg1, st0, st1, sdf, slk0, slk1] = fesets
#print (fesets)
#tl=Tools()
#
#
#chped = []
#chmax = []
#chmin = []
#chrms = []
#for ch in range(len(rawdata)):
#    chnrmsdata= rawdata[ch]
#    chninfo = noise_a_chn(chnrmsdata, chnno=ch)
#    chrms.append(np.std(chninfo[1]))
#    chmax.append(np.max(chninfo[1]))
#    chped.append(np.mean(chninfo[0]))
#    chmin.append(np.min(chninfo[0]))
#
#
#uplanerms = np.zeros(476)
#vplanerms = np.zeros(476)
#xplanerms = np.zeros(584)
#uplanemax = np.zeros(476)
#vplanemax = np.zeros(476)
#xplanemax = np.zeros(584)
#uplanemin = np.zeros(476)
#vplanemin = np.zeros(476)
#xplanemin = np.zeros(584)
#uplaneped = np.zeros(476)
#vplaneped = np.zeros(476)
#xplaneped = np.zeros(584)
#
#for i in range(3*4*128):
#    nfemb = i//128 + 1
#    nch = i %128
#
#    dfmap = tl.LoadMap(nfemb)
#    plane,strip = tl.FindStrips(dfmap, nfemb, nch)
#    #print(i, plane, strip)
#
#    if plane==1:
#       uplanerms[strip-1]=chrms[i]
#       uplaneped[strip-1]=chped[i]
#       uplanemax[strip-1]=chmax[i]
#       uplanemin[strip-1]=chmin[i]
#    if plane==2:
#       vplanerms[strip-1]=chrms[i]
#       vplaneped[strip-1]=chped[i]
#       vplanemax[strip-1]=chmax[i]
#       vplanemin[strip-1]=chmin[i]
#    if plane==3:
#       xplanerms[strip-1]=chrms[i]
#       xplaneped[strip-1]=chped[i]
#       xplanemax[strip-1]=chmax[i]
#       xplanemin[strip-1]=chmin[i]
#
#ch_rms_map = np.concatenate((uplanerms,vplanerms,xplanerms)) 
#ch_ped_map = np.concatenate((uplaneped,vplaneped,xplaneped)) 
#ch_max_map = np.concatenate((uplanemax,vplanemax,xplanemax)) 
#ch_min_map = np.concatenate((uplanemin,vplanemin,xplanemin)) 
#
#
#chs = np.arange(12*128)
#fig = plt.figure(figsize=(14,8))
#plt.rcParams.update({'font.size':12})
#plt.subplot(221)
#plt.plot(chs, ch_rms_map, marker='.',color='r', label = "RMS")
#plt.legend()
#plt.title ("RMS Noise Distribution")
#plt.xlabel ("CH# (According to CRP mapping)")
#plt.ylabel ("ADC RMS Noise / bit" )
#plt.ylim((0,50))
#plt.grid()
#plt.axvline(x=475, color = 'm', linestyle='--')
#plt.axvline(x=951, color = 'm', linestyle='--')
#
#plt.subplot(222)
#plt.plot(chs, np.array(ch_rms_map)*39, marker='.',color='b', label = "ENC")
#plt.legend()
#plt.title ("ENC Distribution")
#plt.xlabel ("CH# (According to CRP mapping)")
#plt.ylabel ("ENC / e-" )
#plt.ylim((0,2000))
#plt.grid()
#plt.axvline(x=475, color = 'm', linestyle='--')
#plt.axvline(x=951, color = 'm', linestyle='--')
#
#plt.subplot(223)
#plt.grid()
#plt.plot(chs, chrms, marker='.',color='r', label = "RMS")
#plt.legend()
#plt.title ("RMS Noise Distribution")
#plt.xlabel ("CH# (According to FEMB mapping)")
#plt.ylabel ("ADC RMS Noise / bit" )
#plt.ylim((0,50))
#for x in range(0, 128*12, 128):
#    plt.axvline(x=x, color = 'm', linestyle='--')
#
#plt.subplot(224)
#plt.grid()
#plt.plot(chs, np.array(chrms)*39, marker='.',color='b', label = "ENC")
#plt.legend()
#plt.title ("ENC Distribution")
#plt.xlabel ("CH# (According to FEMB mapping)")
#plt.ylabel ("ENC / e-" )
#plt.ylim((0,2000))
#for x in range(0, 128*12, 128):
#    plt.axvline(x=x, color = 'm', linestyle='--')
#
##
##
##plt.subplot(111)
##x = np.arange(12*128)
##plt.plot(x, ch_rms_map, marker='.',color='r', label = "RMS")
##plt.legend()
##plt.title("RMS noise distribution")
##plt.xlabel ("CH# ")
##plt.ylim((0,100))
##plt.ylabel ("ADC / bit" )
##plt.grid()
##
#plt.tight_layout()
#
#plt.show()
#plt.close()
#
#
#
##while True:
##    strch =  input("CH/PX/PU/PV#(EX to exit) : ")
##    if "EX" in strch:
##        exit()
##    elif "CH" in strch:
##        chn = int(strch[2:])
##
##    elif "PX" in strch:
##        pxch = int(strch[2:])
##        find_flg = False
##        for fembi in range(1,13,1):
##            dfmap = tl.LoadMap(fembi)
##            for chi in range(128):
##                plane,strip = tl.FindStrips(dfmap, fembi, chi)
##                if (plane == 3) and (strip == pxch):
##                    chn = (fembi-1)*128 + chi
##                    find_flg = True
##                    break
##            if find_flg:
##                break
##
##    elif "PU" in strch:
##        puch = int(strch[2:])
##        find_flg = False
##        for fembi in range(1,13,1):
##            dfmap = tl.LoadMap(fembi)
##            for chi in range(128):
##                plane,strip = tl.FindStrips(dfmap, fembi, chi)
##                if (plane == 1) and (strip == puch):
##                    chn = (fembi-1)*128 + chi
##                    find_flg = True
##                    break
##            if find_flg:
##                break
##
##    elif "PV" in strch:
##        pvch = int(strch[2:])
##        find_flg = False
##        for fembi in range(1,13,1):
##            dfmap = tl.LoadMap(fembi)
##            for chi in range(128):
##                plane,strip = tl.FindStrips(dfmap, fembi, chi)
##                if (plane == 2) and (strip == pvch):
##                    chn = (fembi-1)*128 + chi
##                    find_flg = True
##                    break
##            if find_flg:
##                break
##    else:
##        continue
#    
##    wibi = chn//512
##    fembi = chn//128 + 1
##    chi = chn%128
##    dfmap = tl.LoadMap(fembi)
##    plane,strip = tl.FindStrips(dfmap, fembi, chi)
##    if plane ==1:
##        pl = "U"
##    if plane ==2:
##        pl = "V"
##    if plane ==3:
##        pl = "X"
##    print ("Waveform @ WIB%dFEMB%dCH%d, %s plane # %d"%(wibi, (fembi%4-1), chi, pl, strip ))
#
##    chrms = []
##    for chx in range(12*128):
##        chrms.append(np.std(rawdata[chx][0:1000]))
##        if np.std(rawdata[chx][0:1000]) > 100:
##                print ("Large RMS", chx, np.std(rawdata[chx][0:1000]))
#
#
##    chnrmsdata= rawdata[chn]
##    chninfo = noise_a_chn(chnrmsdata, chnno=chn, fft_en = True, fft_s=2000, fft_avg_cycle=50)
##    
##    import matplotlib.pyplot as plt
##    fig = plt.figure(figsize=(10,8))
##    plt.rcParams.update({'font.size':12})
##    plt.subplot(221)
##    xlen = 2000
##    x = (np.arange(xlen))*512/1000.0
##    plt.plot(x, chninfo[3][0:xlen], marker='.',color='r', label = "%d"%chn)
##    plt.legend()
##    plt.title ("Waveform @ WIB%dFEMB%dCH%d, %s plane # %d"%(wibi, (fembi%4-1), chi, pl, strip ))
##    plt.xlabel ("Time / us")
##    plt.ylabel ("ADC / bit" )
##    plt.grid()
##    
##    plt.subplot(222)
##    xlen = 200000
##    if xlen > len(chninfo[3]):
##        xlen = len(chninfo[3])
##    x = (np.arange(xlen))*512/1000.0
##    plt.plot(x, chninfo[3][0:xlen], marker='.',color='r', label = "%d"%chn)
##    print (np.std(chninfo[3][0:2000]), np.std(chninfo[3][0:20000]), len(chninfo[3]))
##    plt.legend()
##    plt.title ("Waveform @ WIB%dFEMB%dCH%d, %s plane # %d"%(wibi, (fembi%4-1), chi, pl, strip ))
##    plt.xlabel ("Time / us")
##    plt.ylabel ("ADC / bit" )
##    plt.grid()
##    
##    plt.subplot(223)
##    plt.plot(chninfo[4], chninfo[5], marker='.',color='r', label = "%d"%chn)
##    plt.legend()
##    plt.title ("FFT @ WIB%dFEMB%dCH%d, %s plane # %d"%(wibi, (fembi%4-1), chi, pl, strip ))
##    plt.xlabel ("Frequency / Hz")
##    plt.ylabel (" / dB" )
##    plt.grid()
##
##    plt.subplot(224)
##    plt.plot(chninfo[6], chninfo[7], marker='.',color='r', label = "%d"%chn)
##    plt.legend()
##    plt.title ("FFT @ WIB%dFEMB%dCH%d, %s plane # %d"%(wibi, (fembi%4-1), chi, pl, strip ))
##    plt.xlim((0,30000))
##    plt.xlabel ("Frequency / Hz")
##    plt.ylabel (" / dB" )
##    plt.grid()
##
#    #chrms =  np.std(rawdata, axis=(1)) 
#    #chped = np.mean(rawdata, axis=(1)) 
#    #chmax =  np.max(rawdata, axis=(1)) 
#    #chmin =  np.min(rawdata, axis=(1)) 


