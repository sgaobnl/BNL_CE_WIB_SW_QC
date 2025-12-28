import sys
import numpy as np
import socket
#import pickle
#import time, datetime, random, statistics
#import copy
import struct
import platform
import ctypes, ctypes.util
# from dunedaq_decode import wib_dec
system_info = platform.system()
hostname = socket.gethostname()
local_ip = socket.gethostbyname(hostname)
# if "Linux" in system_info:
if local_ip == "192.168.121.123":
    Py_Dec_Flg = False
    print ("WIB Control")
else:
    Py_Dec_Flg = True
    print("Host Control")


if Py_Dec_Flg: # line#10 to line#371 use python for decoding
    #get_bin = lambda x, n: format(x, 'b').zfill(n)
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
        
    def spymemory_decode(buf, trigmode="SW", buf_end_addr = 0x0, trigger_rec_ticks=0x7fff, fastchk=False): #change default trigger_rec_ticks?
        PKT_LEN = 899 #in words
        pkgn =  trigger_rec_ticks//PKT_LEN
    
        if trigmode == "SW" :
            try_num = 2
        else:
            try_num = 1
        for tryi in range(try_num):
            f_heads = []
            #tryi : find the position of frame with minimum timestamp, re-order the buffer
            #tryi==2: decode it only when trigmode is software trigger
            if tryi == 0:
                if trigmode == "SW" :
                    deoding_start_addr = 0x0
                else:
                    spy_addr_word = buf_end_addr
                    if spy_addr_word <= trigger_rec_ticks:
                        deoding_start_addr = spy_addr_word + 0x8000 - trigger_rec_ticks #? to be updated
                    else:
                        deoding_start_addr = spy_addr_word  - trigger_rec_ticks
                    buf2=buf+buf
                    buf = buf2[deoding_start_addr*8: deoding_start_addr*8 + trigger_rec_ticks*8]
    
            buflen=len(buf)
            num_words = int (buflen// 8) 
            words = list(struct.unpack_from("<%dQ"%(num_words),buf)) #unpack [num_words] big-endian 64-bit unsigned integers
            i = 0
            xlen = num_words-PKT_LEN
            while i < xlen:       
                if   (words[i+PKT_LEN] - words[i]==0x800) and (words[i+1]&0x7fff == (words[i+1]>>16)&0x7fff) and  (words[i+2]==0):
                    tmts = words[i]
                    f_heads.append([i,tmts])
                    i = i + PKT_LEN
                else:
                    i = i + 1   
    
    #        with open("./tmp_data/hexdata.txt", "w") as fp:
    #            for x in range(0, len(buf), 8):
    #                fp.write ("%02x%02x%02x%02x%02x%02x%02x%02x\n"%(buf[x+7], buf[x+6], buf[x+5], buf[x+4], buf[x+3], buf[x+2], buf[x+1], buf[x+0]))
    #        exit()
    
            if tryi == 0:
                if (len(f_heads) < pkgn-2):
                    print ("Invalid data length...")
                    return False
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
    
        if fastchk:
            if (len(f_heads) > pkgn-2):
                return f_heads[0][1] 
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
            
            frames[femb*2] = spymemory_decode(buf=buf0, trigmode=trigmode, buf_end_addr=buf_end_addr, trigger_rec_ticks=trigger_rec_ticks, fastchk=fastchk)
            frames[femb*2+1] = spymemory_decode(buf=buf1,trigmode=trigmode,buf_end_addr=buf_end_addr, trigger_rec_ticks=trigger_rec_ticks, fastchk=fastchk)
        return frames
       
    
    def wib_dec(data, fembs=range(4), spy_num= 1, fastchk = False, cd0cd1sync=True): #data from one WIB
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
            #print (len(bufs),buf_end_addr,  spy_rec_ticks )
            if trig_cmd == 0:
                trigmode="SW"
            else:
                trigmode="HW"
            dec_data = wib_spy_dec_syn(bufs, trigmode, buf_end_addr, spy_rec_ticks, fembs, fastchk)
            if fastchk:
                for fembno in fembs:
                    if (dec_data[fembno*2] != False) and (dec_data[fembno*2+1] != False) and (dec_data[fembno*2] == dec_data[fembno*2+1]) :
                        print ("FEMB%d_SYNCED"%fembno, hex(dec_data[fembno*2]), hex(dec_data[fembno*2+1]) )
                    #CD0 and CD1 of the same FEMB has different time stamp
                        #return False
                    else:
                        print ("Not SYNCED", hex(dec_data[fembno*2]), hex(dec_data[fembno*2+1]) )
                        print ("Data of FEMB{} is not synchoronized...".format(fembno))
                        return False
                return True

            if 0 in fembs:
                flen = min(len(dec_data[0]), len(dec_data[1]))
                for i in range(flen):
                    chdata_64ticks0 = [dec_data[0][i]["CD_data"][tick] for tick in range(64)]
                    chdata_64ticks1 = [dec_data[1][i]["CD_data"][tick] for tick in range(64)]
                    femb00 = femb00 + chdata_64ticks0
                    #tmts[0].append(dec_data[0][i]["FEMB_CD0TS"])
                    tmts[0].append(dec_data[0][i]["TMTS"])
                    femb01 = femb01 + chdata_64ticks1
                    #tmts[1].append(dec_data[1][i]["FEMB_CD1TS"])
                    tmts[1].append(dec_data[1][i]["TMTS"])

            if 1 in fembs:
                flen = min(len(dec_data[2]), len(dec_data[3]))
                for i in range(flen):
                    chdata_64ticks0 = [dec_data[2][i]["CD_data"][tick] for tick in range(64)]
                    chdata_64ticks1 = [dec_data[3][i]["CD_data"][tick] for tick in range(64)]
                    femb10 = femb10 + chdata_64ticks0
                    #tmts[2].append(dec_data[2][i]["FEMB_CD0TS"])
                    tmts[2].append(dec_data[2][i]["TMTS"])
                    femb11 = femb11 + chdata_64ticks1
                    #tmts[3].append(dec_data[3][i]["FEMB_CD1TS"])
                    tmts[3].append(dec_data[3][i]["TMTS"])

            if 2 in fembs:
                flen = min(len(dec_data[4]), len(dec_data[5]))
                for i in range(flen):
                    chdata_64ticks0 = [dec_data[4][i]["CD_data"][tick] for tick in range(64)]
                    chdata_64ticks1 = [dec_data[5][i]["CD_data"][tick] for tick in range(64)]
                    femb20 = femb20 + chdata_64ticks0
                    #tmts[4].append(dec_data[4][i]["FEMB_CD0TS"])
                    tmts[4].append(dec_data[4][i]["TMTS"])
                    femb21 = femb21 + chdata_64ticks1
                    #tmts[5].append(dec_data[5][i]["FEMB_CD1TS"])
                    tmts[5].append(dec_data[5][i]["TMTS"])

            if 3 in fembs:
                flen = min(len(dec_data[6]), len(dec_data[7]))
                for i in range(flen):
                    chdata_64ticks0 = [dec_data[6][i]["CD_data"][tick] for tick in range(64)]
                    chdata_64ticks1 = [dec_data[7][i]["CD_data"][tick] for tick in range(64)]
                    femb30 = femb30 + chdata_64ticks0
                    #tmts[6].append(dec_data[6][i]["FEMB_CD0TS"])
                    tmts[6].append(dec_data[6][i]["TMTS"])
                    femb31 = femb31 + chdata_64ticks1
                    #tmts[7].append(dec_data[7][i]["FEMB_CD1TS"])
                    tmts[7].append(dec_data[7][i]["TMTS"])

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
                    femb10[i]=femb10[i][t0s[2]:]
                femb11 = list(zip(*femb11))
                for i in range(len(femb11)):
                    femb11[i]=femb11[i][t0s[3]:]
                femb1 = femb10 + femb11
            else:
                femb1 = None
            if 2 in fembs:
                femb20 = list(zip(*femb20))
                for i in range(len(femb20)):
                    femb20[i]=femb20[i][t0s[4]:]
                femb21 = list(zip(*femb21))
                for i in range(len(femb21)):
                    femb21[i]=femb21[i][t0s[5]:]
                femb2 = femb20 + femb21
            else:
                femb2 = None
            if 3 in fembs:
                femb30 = list(zip(*femb30))
                for i in range(len(femb30)):
                    femb30[i]=femb30[i][t0s[6]:]
                femb31 = list(zip(*femb31))
                for i in range(len(femb31)):
                    femb31[i]=femb31[i][t0s[7]:]
                femb3 = femb30 + femb31
            else:
                femb3 = None

            wibdata.append([femb0, femb1, femb2, femb3, t0max])
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
else:
    sys.path.append('./build/')
    from _daq_rawdatautils_py.unpack.wibeth import *

    def decode(buf,n_frames,cd_id):
        #n_frames = 32 
        
        #get buffer into a format that c++ can work with
        buf = bytes(buf)    
        PyCapsule_Destructor = ctypes.CFUNCTYPE(None, ctypes.py_object)
        PyCapsule_New = ctypes.pythonapi.PyCapsule_New
        PyCapsule_New.restype = ctypes.py_object
        PyCapsule_New.argtypes = (ctypes.c_void_p, ctypes.c_char_p, PyCapsule_Destructor)    
        capsule = PyCapsule_New(buf, None, PyCapsule_Destructor(0))
        
        #pass the buffer into C++ functions
        adcs = np_array_adc_data(capsule,n_frames)
        timestamps = np_array_timestamp_data(capsule,n_frames) 
        totals = np_array_total_data(capsule,n_frames) 
        cd_timestamps = np_array_cd_timestamp_data(capsule,cd_id,n_frames)
        
        return adcs, timestamps, totals, cd_timestamps

    def order_buf(buf, trigmode="SW", buf_end_addr = 0x0, trigger_rec_ticks=0x7fff, fastchk=False): #change default trigger_rec_ticks?
        PKT_LEN = 899 #in words
        pkgn =  trigger_rec_ticks//PKT_LEN
    
        if trigmode == "SW" :
            try_num = 2
        else:
            try_num = 1
        for tryi in range(try_num):
            f_heads = []
            #tryi : find the position of frame with minimum timestamp, re-order the buffer
            #tryi==2: decode it only when trigmode is software trigger
            if tryi == 0:
                if trigmode == "SW" :
                    deoding_start_addr = 0x0
                else:
                    spy_addr_word = buf_end_addr
                    if spy_addr_word <= trigger_rec_ticks:
                        deoding_start_addr = spy_addr_word + 0x8000 - trigger_rec_ticks #? to be updated
                    else:
                        deoding_start_addr = spy_addr_word  - trigger_rec_ticks
                    buf2=buf+buf
                    buf = buf2[deoding_start_addr*8: deoding_start_addr*8 + trigger_rec_ticks*8]
    
            buflen=len(buf)
            num_words = int (buflen// 8) 
            words = list(struct.unpack_from("<%dQ"%(num_words),buf)) #unpack [num_words] big-endian 64-bit unsigned integers
            i = 0
            xlen = num_words-PKT_LEN
            while i < xlen:       
                if   (words[i+PKT_LEN] - words[i]==0x800) and (words[i+1]&0x7fff == (words[i+1]>>16)&0x7fff) and  (words[i+2]==0):
                    tmts = words[i]
                    f_heads.append([i,tmts])
                    i = i + PKT_LEN
                else:
                    i = i + 1   
    
    #        with open("./tmp_data/hexdata.txt", "w") as fp:
    #            for x in range(0, len(buf), 8):
    #                fp.write ("%02x%02x%02x%02x%02x%02x%02x%02x\n"%(buf[x+7], buf[x+6], buf[x+5], buf[x+4], buf[x+3], buf[x+2], buf[x+1], buf[x+0]))
    #        exit()
    
            if tryi == 0:
                if (len(f_heads) < pkgn-2):
                    print ("Invalid data length...")
                    return False
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
    
        if fastchk:
            if (len(f_heads) > pkgn-2):
                return f_heads[0][1] 
            else:
                return False
    
        #return buf,  
        return buf, len(f_heads) #need to know n_frames for C++ functions
   
    
    def wib_spy_dec_syn(bufs, trigmode="SW", buf_end_addr=0x0, trigger_rec_ticks=0x3f000, fembs=range(4), fastchk=False):
        frames = [[],[],[],[],[],[],[],[]] #frame buffers
        for femb in fembs:
            buf0 = bufs[femb*2]
            buf1 = bufs[femb*2+1]   
            
            #order buffers
            wib_dec0 = order_buf(buf=buf0, buf_end_addr=buf_end_addr, trigger_rec_ticks=trigger_rec_ticks, fastchk=fastchk)
            wib_dec1 = order_buf(buf=buf1, buf_end_addr=buf_end_addr, trigger_rec_ticks=trigger_rec_ticks, fastchk=fastchk)
            if not fastchk:
                buf0_ordered, n_frames0 = wib_dec0
                buf1_ordered, n_frames1 = wib_dec1
                frames[femb*2] = decode(buf0_ordered,n_frames0,0) #0=CD 0
                frames[femb*2+1] = decode(buf1_ordered,n_frames1,1) #1=CD 1
            else:
                frames[femb*2]  = wib_dec0
                frames[femb*2+1] = wib_dec1
        return frames
        
    # def wib_dec(data, fembs=range(4), spy_num= 1, fastchk = False, cd0cd1sync=True): #data from one WIB
    #     spy_num_all = len(data)
    #     if spy_num_all < spy_num:
    #         spy_num = spy_num_all
    #     wibdata = []
    #     if fastchk == True:
    #         spy_num=1
    #
    #     for sn in range(spy_num):
    #         tmts = [[],[],[],[],[],[],[],[]]
    #         cd_tmts = [[],[],[],[],[],[],[],[]]
    #         femb00 = []
    #         femb01 = []
    #         femb10 = []
    #         femb11 = []
    #         femb20 = []
    #         femb21 = []
    #         femb30 = []
    #         femb31 = []
    #
    #         raw  = data[sn]
    #         bufs = raw[0]
    #         buf_end_addr = raw[1]
    #         spy_rec_ticks = raw[2]
    #         trig_cmd      = raw[3]
    #         if trig_cmd == 0:
    #             trigmode="SW"
    #         else:
    #             trigmode="HW"
    #
    #         dec_data = wib_spy_dec_syn(bufs, trigmode, buf_end_addr, spy_rec_ticks, fembs, fastchk)
    #
    #         if fastchk:
    #             for fembno in fembs:
    #                 if (dec_data[fembno*2] != False) and (dec_data[fembno*2+1] != False) and (dec_data[fembno*2] == dec_data[fembno*2+1]) :
    #                 #buf0 and buf1 of the same FEMB has sampe time stamp
    #                     return True
    #                 else:
    #                     print ("Data of FEMB{} is not synchoronized...".format(fembno))
    #                     return False
    #
    #         #finessing data into correct format, used to be in rd demo
    #         # tmts = [list(dec_data[b][1]) for b in range(8)]
    #         #flen is always going to be 32
    #         if 0 in fembs:
    #             femb00 = np.transpose(dec_data[0][0])
    #             femb01 = np.transpose(dec_data[1][0])
    #             tmts[0] = dec_data[0][1]
    #             tmts[1] = dec_data[1][1]
    #             cd_tmts[0] = dec_data[0][3]
    #             cd_tmts[1] = dec_data[1][3]
    #         if 1 in fembs:
    #             femb10 = np.transpose(dec_data[2][0])
    #             femb11 = np.transpose(dec_data[3][0])
    #             tmts[2] = dec_data[2][1]
    #             tmts[3] = dec_data[3][1]
    #             cd_tmts[2] = dec_data[2][3]
    #             cd_tmts[3] = dec_data[3][3]
    #         if 2 in fembs:
    #             femb20 = np.transpose(dec_data[4][0])
    #             femb21 = np.transpose(dec_data[5][0])
    #             tmts[4] = dec_data[4][1]
    #             tmts[5] = dec_data[5][1]
    #             cd_tmts[4] = dec_data[4][3]
    #             cd_tmts[5] = dec_data[5][3]
    #         if 3 in fembs:
    #             femb30 = np.transpose(dec_data[6][0])
    #             femb31 = np.transpose(dec_data[7][0])
    #             tmts[6] = dec_data[6][1]
    #             tmts[7] = dec_data[7][1]
    #             cd_tmts[6] = dec_data[6][3]
    #             cd_tmts[7] = dec_data[7][3]
    #
    #         if cd0cd1sync:
    #             t0s = [-1, -1, -1, -1, -1, -1, -1, -1]
    #             if 0 in fembs:
    #                 t0s[0]=tmts[0][0]
    #                 t0s[1]=tmts[1][0]
    #             if 1 in fembs:
    #                 t0s[2]=tmts[2][0]
    #                 t0s[3]=tmts[3][0]
    #             if 2 in fembs:
    #                 t0s[4]=tmts[4][0]
    #                 t0s[5]=tmts[5][0]
    #             if 3 in fembs:
    #                 t0s[6]=tmts[6][0]
    #                 t0s[7]=tmts[7][0]
    #
    #             t0max = np.max(t0s)
    #             for i in range(8):
    #                 if t0s[i] != -1:
    #                     t0s[i] = int((t0max - t0s[i])//32)  #0x20
    #         else:
    #             t0s = [0, 0, 0, 0, 0, 0, 0, 0]
    #             t0max = 0
    #
    #         if 0 in fembs:
    #             for i in range(len(femb00)):
    #                 femb00[i]=femb00[i][t0s[0]:]
    #             for i in range(len(femb01)):
    #                 femb01[i]=femb01[i][t0s[1]:]
    #             femb0 = list(femb00) + list(femb01)
    #             tmts[0] = tmts[0][t0s[0]:]
    #             cd_tmts[0] = cd_tmts[0][t0s[0]:]
    #             tmts[1] = tmts[1][t0s[1]:]
    #             cd_tmts[1] = cd_tmts[1][t0s[1]:]
    #
    #         else:
    #             femb0 = None
    #         if 1 in fembs:
    #             for i in range(len(femb10)):
    #                 femb10[i]=femb10[i][t0s[2]:]
    #             for i in range(len(femb11)):
    #                 femb11[i]=femb11[i][t0s[3]:]
    #             femb1 = list(femb10) + list(femb11)
    #             tmts[2] = tmts[2][t0s[2]:]
    #             cd_tmts[2] = cd_tmts[2][t0s[2]:]
    #             tmts[3] = tmts[3][t0s[3]:]
    #             cd_tmts[3] = cd_tmts[3][t0s[3]:]
    #
    #         else:
    #             femb1 = None
    #         if 2 in fembs:
    #             for i in range(len(femb20)):
    #                 femb20[i]=femb20[i][t0s[4]:]
    #             for i in range(len(femb21)):
    #                 femb21[i]=femb21[i][t0s[5]:]
    #             femb2 = list(femb20) + list(femb21)
    #             tmts[4] = tmts[4][t0s[4]:]
    #             cd_tmts[4] = cd_tmts[4][t0s[4]:]
    #             tmts[5] = tmts[5][t0s[5]:]
    #             cd_tmts[5] = cd_tmts[5][t0s[5]:]
    #
    #         else:
    #             femb2 = None
    #         if 3 in fembs:
    #             for i in range(len(femb30)):
    #                 femb30[i]=femb30[i][t0s[6]:]
    #             for i in range(len(femb31)):
    #                 femb31[i]=femb31[i][t0s[7]:]
    #             femb3 = list(femb30) + list(femb31)
    #             tmts[6] = tmts[6][t0s[6]:]
    #             cd_tmts[6] = cd_tmts[6][t0s[6]:]
    #             tmts[7] = tmts[7][t0s[7]:]
    #             cd_tmts[7] = cd_tmts[7][t0s[7]:]
    #
    #         else:
    #             femb3 = None
    #
    #         wibdata.append([femb0, femb1, femb2, femb3, t0max, tmts, cd_tmts]) #temp for graphing
    #     return wibdata
        






