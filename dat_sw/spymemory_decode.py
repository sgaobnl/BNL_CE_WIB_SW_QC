import sys
import numpy as np
import pickle
import time, datetime, random, statistics
import copy
import struct

SOF = 0X3C
IDLE = 0XBC
PKT_LEN = 120

def deframe(words): #based on WIB-DAQ_Format_2021-12-01_daq_hdr.xlsx
    frame_dict = {
            "Version":0,   
            "DetID":0,     
            "CrateID":0,   
            "Slot":0,      
            "Link":0,      
            "TMTS":0,      
            "TMTS_low5":0,      
            "CDTS_ID":0,   
            "FEMB_Valid":0,
            "link_mask_femb0_2":0, 
            "link_mask_femb1_3":0, 
            "LOL":0,       
            "FEMB_PIFB":0, 
            "FEMB_SF":0,   
            "FEMB_CDTS":0, 
            "FEMB_CDTS_low5":0, 
            "FEMB0_2":[0 for i in range(128)],
            "FEMB1_3":[0 for i in range(128)],
            "FLEX_bits":0, 
            "WS":0, 
            "PSR_Cal":0,
            "Ready":0,
            "Contex_code":0 }

    frame_dict["Version"]    = words[0]&0x3f
    frame_dict["DetID"]      = (words[0]>>6)&0x3f
    frame_dict["CrateID"]    = (words[0]>>12)&0x3ff
    frame_dict["Slot"]       = (words[0]>>22)&0x0f
    frame_dict["Link"]       = (words[0]>>26)&0x3f
    frame_dict["TMTS"]       = ((words[2]<<32) + words[1])>>5 #high 59 bits timing mast time stamp
    frame_dict["TMTS_low5"]  = (words[1])&0x1f #low 5 bits of timing mast time stamp
    frame_dict["CDTS_ID"]    = (words[3]>>13)&0x7
    frame_dict["FEMB_Valid"] = (words[3]>>16)&0x3
    frame_dict["link_mask_femb0_2"] = (words[3]>>18)&0x0f
    frame_dict["link_mask_femb1_3"] = (words[3]>>22)&0x0f
    frame_dict["LOL"]        = (words[3]>>26)&0x01
    frame_dict["FEMB_PIFB"]  =words[4]&0xff
    frame_dict["FEMB_SF"]    =(words[4]>>8)&0xff
    frame_dict["FEMB_CDTS"]  =((words[4]>>16)>>5)&0x7ff
    frame_dict["FEMB_CDTS_low5"]  =(words[4]>>16)&0x1f

    #print (hex(frame_dict["FEMB_SF"]), hex(frame_dict["TMTS"]), hex(frame_dict["TMTS_low5"] ),  hex(frame_dict["FEMB_CDTS"]),  hex(frame_dict["FEMB_CDTS_low5"]), hex(frame_dict["CDTS_ID"])  )

    # how U,V,X numbers map to channels on a single FEMB
    u_to_ch = [20, 59, 19, 60, 18, 61, 17, 62, 16, 63, 4, 43, 3, 44, 2, 
        45, 1, 46, 0, 47, 68, 107, 67, 108, 66, 109, 65, 110, 64, 
        111, 84, 123, 83, 124, 82, 125, 81, 126, 80, 127];
    v_to_ch = [25, 54, 24, 55, 23, 56, 22, 57, 21, 58, 9, 38, 8, 39, 7, 
        40, 6, 41, 5, 42, 73, 102, 72, 103, 71, 104, 70, 105, 69,
        106, 89, 118, 88, 119, 87, 120, 86, 121, 85, 122];
    x_to_ch = [31, 48, 30, 49, 29, 50, 28, 51, 27, 52, 26, 53, 15, 32,
        14, 33, 13, 34, 12, 35, 11, 36, 10, 37, 79, 96, 78, 97, 
        77, 98, 76, 99, 75, 100, 74, 101, 95, 112, 94, 113, 93, 
        114, 92, 115, 91, 116, 90, 117];        
    
    #deframe data
    #unpack14 https://github.com/DUNE-DAQ/dune-wib-firmware/blob/master/sw/src/unpack.cc#L6        
    frame_data = [words[5:5+56], words[5+56:5+56*2]]
    #if n == 0:
    #    for w, word in enumerate(frame):
    #        print("%08x"%(word),end=" ")
    #        if w%8 == 7:
    #            print("")
    unpacked_buf = [[0 for i in range(128)],[0 for i in range(128)]]
    for femb in range(2):
        u = [0 for l in range(40)]
        v = [0 for l in range(40)]
        x = [0 for l in range(48)]
        #see https://docs.google.com/spreadsheets/d/1-Ag-uCqHwvNReRzjYC8EQuY1Dn0n_ttM/edit#gid=1930588249
        #for channel data structure
        
        for i in range(128): #i == n'th U,V,X value
            if i < len(u):
                a = u
                ii = i
            elif i < len(u) + len(v):
                a = v
                ii = i - len(v)
            else:
                a = x
                ii = i - len(u) - len(v)
            low_bit = i*14
            low_word = low_bit // 32
            high_bit = (i+1)*14-1
            high_word = high_bit // 32
            #print("word %d :: low %d (%d[%d]) high %d (%d[%d])"%(i,low_bit,low_word,low_bit%32,high_bit,high_word,high_bit%32));
            #channel endianness?
            if low_word == high_word:
                a[ii] = (frame_data[femb][low_word] >> (low_bit%32)) & 0x3fff
            else:
                high_off = high_word*32-low_bit

                a[ii] = (frame_data[femb][low_word] >> (low_bit%32)) & (0x3fff >> (14-high_off))
                a[ii] = a[ii] | (frame_data[femb][high_word] << high_off) & ((0x3fff << high_off) & 0x3fff)
            #uvx to channel index converter
        #unpacked_buf["timestamp"][n] = timestamps_ordered[n]

        for j in range(len(u)):
            k = u_to_ch[j]
            unpacked_buf[femb][k] = u[j]
        for j in range(len(v)):
            k = v_to_ch[j]
            unpacked_buf[femb][k] = v[j]
        for j in range(len(x)):
            k = x_to_ch[j]
            unpacked_buf[femb][k] = x[j]

    frame_dict["FEMB0_2"] = unpacked_buf[0]
    frame_dict["FEMB1_3"] = unpacked_buf[1]
    frame_dict["FLEX_bits"]   = words[117]&0xffff
    frame_dict["WS"]          = (words[117]>>18)&0x01
    frame_dict["PSR_Cal"]     = (words[117]>>19)&0x0f
    frame_dict["Ready"]       = (words[117]>>23)&0x01
    frame_dict["Contex_code"] = (words[117]>>24)&0xff

    if (frame_dict["TMTS_low5"] != frame_dict["FEMB_CDTS_low5"]) and (frame_dict["link_mask_femb0_2"] == 0x00) and (frame_dict["link_mask_femb1_3"] == 0x00):
        print ("Warning, fast command 'edge' and 'sync' are missing for Coldata chips")

    return frame_dict


def spymemory_decode(buf, trigmode="SW", buf_end_addr = 0x0, trigger_rec_ticks=0x3f000):
    num_words = int(len(buf) // 4)
    words = list(struct.unpack_from("<%dI"%(num_words),buf))       

    if trigmode == "SW" :
        pass
        deoding_start_addr = 0x0
    else:
        spy_addr_word = buf_end_addr>>2
        if spy_addr_word <= trigger_rec_ticks:
            deoding_start_addr = spy_addr_word + 0x40000 - trigger_rec_ticks
        else:
            deoding_start_addr = spy_addr_word  - trigger_rec_ticks

    buf2 = buf + buf
    newbuf = buf[deoding_start_addr*4: deoding_start_addr*4 + trigger_rec_ticks*4]

    f_heads = []
    i = 0
    for i in range(num_words-121):
        if words[i] == SOF:
            f0 = words[i] == SOF         
            f1 = words[i+120] == IDLE  

            if f0&f1:
                #print("SOF at %d is a valid frame"%(i))
                tmts = ((words[i+3]<<32) + words[i+2])>>5 #64 bit timing mast time stamp
                if (tmts == 0):
                    print ("Timing system is missing, if there isn't any external timing system, please enable fake timing in WIB and then retake the data")
                    print ("exit anyway")
                    exit()
                f_heads.append([i, tmts])
                #print ([i, tmts])
                i = i + PKT_LEN
            else:
                i = i + 1
        else:
            i = i + 1
    w_sofs, tmsts = zip(*f_heads)
    tmts_min = np.min(tmsts)
    minpos = np.where(tmsts == tmts_min)[0][0]
    frame_mints = w_sofs[minpos] #find the position of frame with minimum timestamp
    #print (tmts_min, minpos, frame_mints)
    #reorder the data accodingto the timestamp
    words = words[frame_mints:] + words[0:frame_mints] 

    num_frams = num_words//PKT_LEN
    ordered_frames = []
    words = words[0:num_frams*PKT_LEN]
    for i in range(num_frams*(PKT_LEN-1)):
        if words[i] == SOF:
            f0 = words[i] == SOF
            f1 = words[i+120] == IDLE  
            if f0&f1:
                frame_dict = deframe(words = words[i+1:i+119])
                tmts = frame_dict["TMTS"]
                ordered_frames.append(frame_dict)
                i = i + PKT_LEN
            else:
                i = i + 1
        else:
            i = i + 1
    return ordered_frames

def wib_spy_dec_syn(buf0, buf1, trigmode="SW", buf_end_addr=0x0,  trigger_rec_ticks=0x3f000, fembs=range(4)): #synchronize samples in two spy buffers

    frames0={}
    frames1={}
    buf0_flg = False
    buf1_flg = False
  
    if (0 in fembs) or (1 in fembs):
       #print ("Decoding BUF0")
       frames0 = spymemory_decode(buf=buf0, buf_end_addr=buf_end_addr, trigger_rec_ticks=trigger_rec_ticks)
       buf0_flg = True
    if (2 in fembs) or (3 in fembs):
       #print ("Decoding BUF1")
       frames1 = spymemory_decode(buf=buf1, buf_end_addr=buf_end_addr, trigger_rec_ticks=trigger_rec_ticks)
       buf1_flg = True
     
    if fembs==[0,1,2,3]:
       flen = len(frames0)
       len1 = len(frames1)
       if flen>len1:
           flen = len1
       frames0 = frames0[0:flen]
       frames1 = frames1[0:flen]

    if buf0_flg and buf1_flg:
        if frames0[0]["TMTS"] == frames1[0]["TMTS"]:
            pass #two spymemory are synced 
        elif frames0[0]["TMTS"] > frames1[0]["TMTS"]:
            oft = frames0[0]["TMTS"] - frames1[0]["TMTS"]
            if frames0[0]["TMTS"] == frames1[oft]["TMTS"]:
                frames0 =frames0[0: 0-oft] 
                frames1 =frames1[oft:] 
        elif frames0[0]["TMTS"] < frames1[0]["TMTS"]:
            oft = abs(frames0[0]["TMTS"] - frames1[0]["TMTS"])
            print (oft, hex(frames0[0]["TMTS"]), hex(frames1[0]["TMTS"]))
            if frames0[oft]["TMTS"] == frames1[0]["TMTS"]:
                frames0 =frames0[oft:] 
                frames1 =frames1[0: 0-oft] 
    return frames0, frames1



