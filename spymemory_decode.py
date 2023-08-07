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
    
def spymemory_decode(buf, trigmode="SW", buf_end_addr = 0x0, trigger_rec_ticks=0x3f000): #change default trigger_rec_ticks?
    num_words = int(len(buf) // 8) 
    words = list(struct.unpack_from("<%dQ"%(num_words),buf)) #unpack [num_words] big-endian 64-bit unsigned integers
    
    PKT_LEN = 899 #in words
    
    if trigmode == "SW" :
        pass
        deoding_start_addr = 0x0
    else: #the following 5 lines to be updated
        spy_addr_word = buf_end_addr>>2
        if spy_addr_word <= trigger_rec_ticks:
            deoding_start_addr = spy_addr_word + 0x40000 - trigger_rec_ticks #? to be updated
        else:
            deoding_start_addr = spy_addr_word  - trigger_rec_ticks

    f_heads = []
    i = 0
    while i < num_words-PKT_LEN:       
        if abs(words[i+PKT_LEN] - words[i]) % 0x800 == 0 and not (words[i+PKT_LEN] == 0 and words[i] == 0):
            #print(hex(words[i]))
            tmts = words[i]
            f_heads.append([i,tmts])
            i = i + PKT_LEN
        else:
            i = i + 1   
    
    #print(f_heads)  
    w_sofs, tmsts = zip(*f_heads)
    tmts_min = np.min(tmsts)
    minpos = np.where(tmsts == tmts_min)[0][0]
    frame_mints = w_sofs[minpos]
    words = words[frame_mints:] + words[0:frame_mints]
    
    num_frams = num_words // PKT_LEN
    ordered_frames = []
    words = words[0:num_frams*PKT_LEN] #remove any words from a cut-off fram
    i = 0
    while i < (num_frams-2)*PKT_LEN:
        if abs(words[i+PKT_LEN] - words[i]) == 0x800:
            # print(hex(words[i]))
            frame_dict = deframe(words = words[i:i+PKT_LEN])
            ordered_frames.append(frame_dict)
            i = i + PKT_LEN
        else:
            i = i + 1    
    # print("deframe final frame")
    # print(hex(words[i]))
    # frame_dict = deframe(words = words[i:i+PKT_LEN])
    # ordered_frames.append(frame_dict)    
    
    return ordered_frames
    
def wib_spy_dec_syn(bufs, trigmode="SW", buf_end_addr=0x0, trigger_rec_ticks=0x3f000, fembs=range(4)): #synchronize samples in 8 spy buffers
    #^change default trigger_rec_ticks?
    frames = [[],[],[],[],[],[],[],[]] #frame buffers
    #buf_flag = [False, False, False, False, False, False, False, False] #can be accomplished by checking if frames[n] is empty
    
    for femb in fembs:
        buf0 = bufs[femb*2]
        buf1 = bufs[femb*2+1]
        
        frames[femb*2] = spymemory_decode(buf=buf0, buf_end_addr=buf_end_addr, trigger_rec_ticks=trigger_rec_ticks)
        frames[femb*2+1] = spymemory_decode(buf=buf1, buf_end_addr=buf_end_addr, trigger_rec_ticks=trigger_rec_ticks)
        
        #buf_flag[femb*2] = True
        #buf_flag[femb*2+1] = True
    
    if fembs == list(range(4)):
        #find minimum length frame and make everything that length
        min_len = len(min(frames, key=len))
        
        for frame in frames:
            frame = frame[0:min_len]
    
    if all([frame for frame in frames]): #if no frames buffers are empty
        #check if all spymemories are synced
        tmts0_all = [frame[0]["TMTS"] for frame in frames]
        while not all(tmts0 == tmts0_all[0] for tmts0 in tmts0_all): #if spymemory synced, pass
            for frame in frames[1:]:
                if frames[0][0]["TMTS"] > frame[0]["TMTS"]:
                    oft = frames[0][0]["TMTS"] - frame[0]["TMTS"] // 0x800 #0x800 = difference between 3 adjacent DAQ frames
                    if frames[0][0]["TMTS"] == frame[0]["TMTS"]:
                        frames[0] = frames[0][0:0-oft]
                        frame = frame[oft:]
                elif frames[0][0]["TMTS"] < frame[0]["TMTS"]: 
                    oft = abs(frames[0][0]["TMTS"] - frame[0]["TMTS"]) // 0x800
                    print("spymemory sync", oft, hex(frames[0][0]["TMTS"]), hex(frame[0]["TMTS"]))
                    if frames[0][oft]["TMTS"] == frame[0]["TMTS"]:
                        frames[0] = frames[0][oft:]
                        frame = frame[0:0-oft]
    return frames
   

def wib_dec(data, fembs=range(4), spy_num= 1): #data from one WIB  
    spy_num_all = len(data)
    if spy_num_all < spy_num:
        spy_num = spy_num_all
    tmts = []
    sfs0 = []
    sfs1 = []
    cdts_l0 = []
    cdts_l1 = []
    femb0 = []
    femb1 = []
    femb2 = []
    femb3 = []

    for i in range(spy_num):
        raw  = data[i]
        buf0 = raw[0][0]
        buf1 = raw[0][1]
        buf0_end_addr = raw[1]
        spy_rec_ticks = raw[2]
        trig_cmd      = raw[3]
        if trig_cmd == 0:
            trigmode="SW"
        else:
            trigmode="HW"
        
        dec_data = wib_spy_dec_syn(bufs, trigmode, buf_end_addr=buf0_end_addr, trigger_rec_ticks=spy_rec_ticks, fembs=fembs)

##########to be updated
        flen = len(dec_data[link])
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

    if 0 in fembs:
        femb0 = list(zip(*femb0))
    else:
        femb0 = None
    if 1 in fembs:
        femb1 = list(zip(*femb1))
    else:
        femb1 = None
    if 2 in fembs:
        femb2 = list(zip(*femb2))
    else:
        femb2 = None
    if 3 in fembs:
        femb3 = list(zip(*femb3))
    else:
        femb3 = None

    wibdata = [femb0, femb1, femb2, femb3, tmts]
    return wibdata


def avg_aligned_by_ts(wibdata, chn=0, period = 512): #data from one WIB  

    femb0 = wibdata[0] 
    femb1 = wibdata[1] 
    femb2 = wibdata[2] 
    femb3 = wibdata[3] 
    tmts  = wibdata[4] 
    tmts  = np.array(tmts) - tmts[0] 

    tmts_sets = [tmts[0]]
    tmts_sete = []
    for i in range(len(tmts) - 10):
        if tmts[i+1] - tmts[i] > 1: 
            tmts_sets.append(tmts[i+1])
            tmts_sete.append(tmts[i])
    
    tmts_sete.append(tmts[-1])


    femb_id = chn//128
    fembchn = chn%128

    if femb_id == 0:
        fembdata = femb0
    elif femb_id == 1:
        fembdata = femb1
    elif femb_id == 2:
        fembdata = femb2
    else:
        fembdata = femb3

    cnti = 0
    f_flg = True
    for runi in range(len(tmts_sets)):
        ni = tmts_sets[runi]%period
        for x in range(tmts_sets[runi]+period-ni, tmts_sete[runi]-period, period):
            post = np.where(tmts == x)[0][0]
            if f_flg:
                f_flg = False
                tdata0 = np.array(fembdata[fembchn][post:post+period]) 
                tdata = tdata0
                cnti = 1
            else:
                tdata = tdata + np.array(fembdata[fembchn][post:post+period]) 
                cnti += 1
    tdata = tdata/cnti

    return tdata,tdata0, chn, period, cnti


        






