import sys
import numpy as np
import pickle
import time, datetime, random, statistics
import copy
import struct


get_bin = lambda x, n: format(x, 'b').zfill(n)

def deframe(words): #based on WIB DEIMOS format - WIB-DAQ-formats-all.xlsx
    data_begin = 3 #word # in frame where data starts
    tick_word_length = 14
    
    frame_data = words[data_begin:]
    num_ticks = len(frame_data) // tick_word_length #always 64?
    #print(str(num_ticks)+" ticks")    
    
    frame_dict = {
            "TMTS":0,
            "FEMB_CD0TS":0,
            "FEMB_CD1TS":0,
            "CRC_error":0,
            "Link_valid":0,
            "LOL":0,
            "WS":0, 
            "FS":0,
            "Pulser":0,
            "Cal":0,
            "Ready":0,
            "Context_code":0,
            "Version":0,
            "Chn_ID":0,
            "CD_data": [[0 for ch in range(64)] for tick in range(num_ticks)] }
            
    frame_dict["TMTS"]          = words[0]
    frame_dict["FEMB_CD0TS"]    = words[1]&0x7fff
    frame_dict["FEMB_CD1TS"]    = (words[1]>>16)&0x7fff
    frame_dict["CRC_error"]     = (words[1]>>33)&0x3
    frame_dict["Link_valid"]    = (words[1]>>35)&0x3
    frame_dict["LOL"]           = (words[1]>>37)&0x1
    frame_dict["WS"]            = (words[1]>>38)&0x1
    frame_dict["FS"]            = (words[1]>>39)&0x3
    frame_dict["Pulser"]        = (words[1]>>41)&0x1
    frame_dict["Cal"]           = (words[1]>>42)&0x1
    frame_dict["Ready"]         = (words[1]>>43)&0x1
    frame_dict["Context_code"]  = (words[1]>>44)&0xff
    frame_dict["Version"]       = (words[1]>>52)&0xf
    frame_dict["Chn_ID"]        = (words[1]>>56)&0xff
    #see latest wib firmware doc for descriptions

    for tick in range(num_ticks):
        
        tick_data = frame_data[tick*tick_word_length:(tick+1)*tick_word_length]
        for ch in range(64): #channel num = adc num * 16 + adc ch num
            
            low_bit = ch*14
            low_word = low_bit // 64
            high_bit = (ch+1)*14-1
            high_word = high_bit // 64
            
            
            
            if low_word == high_word:
                frame_dict["CD_data"][tick][ch] = (tick_data[low_word] >> (low_bit%64)) & 0x3fff
                
                adc = ch // 16
                adc_ch = ch % 16
            else:
                high_off = high_word*64-low_bit
                frame_dict["CD_data"][tick][ch] = (tick_data[low_word] >> (low_bit%64)) & (0x3fff >> (14-high_off))
                frame_dict["CD_data"][tick][ch] = frame_dict["CD_data"][tick][ch] | (tick_data[high_word] << high_off) & ((0x3fff << high_off) & 0x3fff)
                
                adc = ch // 16
                adc_ch = ch % 16                
                

    return frame_dict
    
def spymemory_decode(buf, trigmode="SW", buf_end_addr = 0x0, trigger_rec_ticks=0x3f000, fastchk=False): #change default trigger_rec_ticks?
    PKT_LEN = 899 #in words

    for tryi in range(2):
        f_heads = []
        #tryi : find the position of frame with minimum timestamp, re-order the buffer
        #tryi==2: decode it
        buflen=len(buf)
        num_words = int (buflen// 8) 
        words = list(struct.unpack_from("<%dQ"%(num_words),buf)) #unpack [num_words] big-endian 64-bit unsigned integers
        if trigmode == "SW" :
            pass
            deoding_start_addr = 0x0
        else: #the following 5 lines to be updated
            print ("hardware trigger decoding to be updated...")
            spy_addr_word = buf_end_addr>>2
            if spy_addr_word <= trigger_rec_ticks:
                deoding_start_addr = spy_addr_word + 0x40000 - trigger_rec_ticks #? to be updated
            else:
                deoding_start_addr = spy_addr_word  - trigger_rec_ticks

        i = 0
        xlen = num_words-PKT_LEN
        while i < xlen:       
            if   (words[i+PKT_LEN] - words[i]==0x800) and (words[i+1]&0x7fff == (words[i+1]>>16)&0x7fff) and  (words[i+2]==0):
                tmts = words[i]
                f_heads.append([i,tmts])
                if tryi == 1:
                    print ([i,tmts])
                i = i + PKT_LEN
            else:
                i = i + 1   

#        with open("./tmp_data/hexdata.txt", "w") as fp:
#            for x in range(0, len(buf), 8):
#                fp.write ("%02x%02x%02x%02x%02x%02x%02x%02x\n"%(buf[x+7], buf[x+6], buf[x+5], buf[x+4], buf[x+3], buf[x+2], buf[x+1], buf[x+0]))
#        exit()

        if tryi == 0:
            w_sofs, tmsts = zip(*f_heads)
            tmst0 = tmsts[0]
            w_sof0 = w_sofs[0]
            f_heads = sorted(f_heads, key=lambda ts: ts[1]) 
            w_min = f_heads[0][0]
            tmstmin=f_heads[0][1]
            w_max = f_heads[-1][0]
            if (tmst0-tmstmin)//0x20 < ((buflen//8//899)*64 + 64): #ring buffer was rolled back (data is larger than the length of ring buffer)
                buf = buf[w_min*8:] + buf[:w_min*8]
#                with open("./tmp_data/hexdata2.txt", "w+") as fp:
#                    for x in range(0, len(buf), 8):
#                        fp.write ("%02x%02x%02x%02x%02x%02x%02x%02x\n"%(buf[x+7], buf[x+6], buf[x+5], buf[x+4], buf[x+3], buf[x+2], buf[x+1], buf[x+0]))
#                exit()
            else:
                buf = buf[w_sof0*8:w_max*8+PKT_LEN ]
        else:
            w_sofs, tmsts = zip(*f_heads)
            f_heads = sorted(f_heads, key=lambda ts: ts[1]) 

    if fastchk:
        if (len(f_heads) > 30):
            return True
        else:
            return False

    w_sofs, tmsts = zip(*f_heads)
    ordered_frames = []
    for i in range( len(w_sofs)):
        frame_dict = deframe(words = words[w_sofs[i]:w_sofs[i]+PKT_LEN])
        ordered_frames.append(frame_dict)
   
    return ordered_frames


def wib_spy_dec_syn(bufs, trigmode="SW", buf_end_addr=0x0, trigger_rec_ticks=0x3f000, fembs=range(4), fastchk=False): #synchronize samples in 8 spy buffers
    #^change default trigger_rec_ticks?
    frames = [[],[],[],[],[],[],[],[]] #frame buffers
    
    for femb in fembs:
        buf0 = bufs[femb*2]
        buf1 = bufs[femb*2+1]
        
        frames[femb*2] = spymemory_decode(buf=buf0, buf_end_addr=buf_end_addr, trigger_rec_ticks=trigger_rec_ticks, fastchk=fastchk)
        frames[femb*2+1] = spymemory_decode(buf=buf1, buf_end_addr=buf_end_addr, trigger_rec_ticks=trigger_rec_ticks, fastchk=fastchk)
    return frames
   

def wib_dec(data, fembs=range(4), spy_num= 1, fastchk = False, cd0cd1sync=False): #data from one WIB  
    spy_num_all = len(data)
    if spy_num_all < spy_num:
        spy_num = spy_num_all
    wibdata = []
    if fastchk == True:
        spy_num=1

    for sn in range(spy_num):
        tmts = [[],[],[],[],[],[],[],[]]
        femb00 = []
        femb01 = []
        femb10 = []
        femb11 = []
        femb20 = []
        femb21 = []
        femb30 = []
        femb31 = []

        raw  = data[sn]
        bufs = raw[0]
        buf_end_addr = raw[1]
        spy_rec_ticks = raw[2]
        trig_cmd      = raw[3]
        if trig_cmd == 0:
            trigmode="SW"
        else:
            trigmode="HW"
        
        dec_data = wib_spy_dec_syn(bufs, trigmode, buf_end_addr, spy_rec_ticks, fembs, fastchk)
        if fastchk:
            for fembno in fembs:
                if (dec_data[fembno*2] != True) or (dec_data[fembno*2+1] != True):
                    print ("Data of FEMB{} is not synchoronized...".format(fembno))
                    return False
            return True
            
        if 0 in fembs:
            flen = min(len(dec_data[0]), len(dec_data[1]))
            for i in range(flen):
                chdata_64ticks0 = [dec_data[0][i]["CD_data"][tick] for tick in range(64)]        
                chdata_64ticks1 = [dec_data[1][i]["CD_data"][tick] for tick in range(64)]        
                femb00 = femb00 + chdata_64ticks0        
                tmts[0].append(dec_data[0][i]["FEMB_CD0TS"])
                femb01 = femb01 + chdata_64ticks1        
                tmts[1].append(dec_data[1][i]["FEMB_CD1TS"])

        if 1 in fembs:        
            flen = min(len(dec_data[2]), len(dec_data[3]))
            for i in range(flen):
                chdata_64ticks0 = [dec_data[2][i]["CD_data"][tick] for tick in range(64)]        
                chdata_64ticks1 = [dec_data[3][i]["CD_data"][tick] for tick in range(64)]        
                femb10 = femb10 + chdata_64ticks0        
                tmts[2].append(dec_data[2][i]["FEMB_CD0TS"])
                femb11 = femb11 + chdata_64ticks1        
                tmts[3].append(dec_data[3][i]["FEMB_CD1TS"])

        if 2 in fembs:       
            flen = min(len(dec_data[4]), len(dec_data[5]))
            for i in range(flen):
                chdata_64ticks0 = [dec_data[4][i]["CD_data"][tick] for tick in range(64)]        
                chdata_64ticks1 = [dec_data[5][i]["CD_data"][tick] for tick in range(64)]        
                femb20 = femb20 + chdata_64ticks0        
                tmts[4].append(dec_data[4][i]["FEMB_CD0TS"])
                femb21 = femb21 + chdata_64ticks1        
                tmts[5].append(dec_data[5][i]["FEMB_CD1TS"])

        if 3 in fembs:
            flen = min(len(dec_data[6]), len(dec_data[7]))
            for i in range(flen):
                chdata_64ticks0 = [dec_data[6][i]["CD_data"][tick] for tick in range(64)]        
                chdata_64ticks1 = [dec_data[7][i]["CD_data"][tick] for tick in range(64)]        
                femb30 = femb30 + chdata_64ticks0        
                tmts[6].append(dec_data[6][i]["FEMB_CD0TS"])
                femb31 = femb31 + chdata_64ticks1        
                tmts[7].append(dec_data[7][i]["FEMB_CD1TS"])

        if cd0cd1sync:
            t0s = [-1, -1, -1, -1, -1, -1, -1, -1]
            if 0 in fembs:
                t0s[0]=tmts[0][0]
                t0s[1]=tmts[1][0]
            if 1 in fembs:
                t0s[2]=tmts[2][0]
                t0s[3]=tmts[3][0]
            if 2 in fembs:
                t0s[4]=tmts[4][0]
                t0s[5]=tmts[5][0]
            if 3 in fembs:
                t0s[6]=tmts[6][0]
                t0s[7]=tmts[7][0]

            t0max = np.max(t0s)
            for i in range(8):
                if t0s[i] != -1:
                    t0s[i] = (t0max - t0s[i])//32 
        else:
            t0s = [0, 0, 0, 0, 0, 0, 0, 0]
            t0max = 0

        if 0 in fembs:
            femb00 = list(zip(*femb00))
            for i in range(len(femb00)):
                femb00[i]=femb00[i][t0s[0]:]
            femb01 = list(zip(*femb01))
            for i in range(len(femb01)):
                femb01[i]=femb01[i][t0s[1]:]
            femb0 = femb00 + femb01
        else:
            femb0 = None
        if 1 in fembs:
            femb10 = list(zip(*femb10))
            for i in range(len(femb10)):
                femb10[i]=femb10[i][t0s[0]:]
            femb11 = list(zip(*femb11))
            for i in range(len(femb11)):
                femb11[i]=femb11[i][t0s[1]:]
            femb1 = femb10 + femb11
        else:
            femb1 = None
        if 2 in fembs:
            femb20 = list(zip(*femb20))
            for i in range(len(femb20)):
                femb20[i]=femb20[i][t0s[0]:]
            femb21 = list(zip(*femb21))
            for i in range(len(femb21)):
                femb21[i]=femb21[i][t0s[1]:]
            femb2 = femb20 + femb21
        else:
            femb2 = None
        if 3 in fembs:
            femb30 = list(zip(*femb30))
            for i in range(len(femb30)):
                femb30[i]=femb30[i][t0s[0]:]
            femb31 = list(zip(*femb31))
            for i in range(len(femb31)):
                femb31[i]=femb31[i][t0s[1]:]
            femb3 = femb30 + femb31
        else:
            femb3 = None

        wibdata.append([femb0, femb1, femb2, femb3, t0max])
    return wibdata


#def avg_aligned_by_ts(wibdata, chn=0, period = 512): #data from one WIB  
#
#    femb0 = wibdata[0] 
#    femb1 = wibdata[1] 
#    femb2 = wibdata[2] 
#    femb3 = wibdata[3] 
#    tmts  = wibdata[4] 
#    tmts  = np.array(tmts) - tmts[0] 
#
#    tmts_sets = [tmts[0]]
#    tmts_sete = []
#    for i in range(len(tmts) - 10):
#        if tmts[i+1] - tmts[i] > 1: 
#            tmts_sets.append(tmts[i+1])
#            tmts_sete.append(tmts[i])
#    
#    tmts_sete.append(tmts[-1])
#
#
#    femb_id = chn//128
#    fembchn = chn%128
#
#    if femb_id == 0:
#        fembdata = femb0
#    elif femb_id == 1:
#        fembdata = femb1
#    elif femb_id == 2:
#        fembdata = femb2
#    else:
#        fembdata = femb3
#
#    cnti = 0
#    f_flg = True
#    for runi in range(len(tmts_sets)):
#        ni = tmts_sets[runi]%period
#        for x in range(tmts_sets[runi]+period-ni, tmts_sete[runi]-period, period):
#            post = np.where(tmts == x)[0][0]
#            if f_flg:
#                f_flg = False
#                tdata0 = np.array(fembdata[fembchn][post:post+period]) 
#                tdata = tdata0
#                cnti = 1
#            else:
#                tdata = tdata + np.array(fembdata[fembchn][post:post+period]) 
#                cnti += 1
#    tdata = tdata/cnti
#
#    return tdata,tdata0, chn, period, cnti


        






