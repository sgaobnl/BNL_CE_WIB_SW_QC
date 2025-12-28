import os, sys, time
import numpy as np
import pickle
import ctypes
import struct

#Let Python see the C++ libary file
sys.path.append('./decoding_cpp/build/')


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
    

def order_buf(buf, trigmode="SW", buf_end_addr = 0x0, trigger_rec_ticks=0x3f000, fastchk=False):
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
                #print("tmts",hex(tmts),"at",i)
                i = i + PKT_LEN
                
            else:
                i = i + 1   

#        with open("./tmp_data/hexdata.txt", "w") as fp:
#            for x in range(0, len(buf), 8):
#                fp.write ("%02x%02x%02x%02x%02x%02x%02x%02x\n"%(buf[x+7], buf[x+6], buf[x+5], buf[x+4], buf[x+3], buf[x+2], buf[x+1], buf[x+0]))
#        exit()

        if tryi == 0:
            if (len(f_heads) < 30):
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
        else:
            w_sofs, tmsts = zip(*f_heads)
            f_heads = sorted(f_heads, key=lambda ts: ts[1]) 

    if fastchk:
        if (len(f_heads) > 30):
            return f_heads[0][1] 
        else:
            return False
    
    #print([hex(w) for w in words[:5]])        
    
    return buf, len(f_heads) #need to know n_frames for C++ functions


def wib_spy_dec_syn(bufs, trigmode="SW", buf_end_addr=0x0, trigger_rec_ticks=0x3f000, fembs=range(4), fastchk=False):
    frames = [[], [], [], [], [], [], [], []]  # frame buffers
    for femb in fembs:
        buf0 = bufs[femb * 2]
        buf1 = bufs[femb * 2 + 1]

        # order buffers
        if fastchk:
            frames[femb * 2] = order_buf(buf=buf0, buf_end_addr=buf_end_addr, trigger_rec_ticks=trigger_rec_ticks, fastchk=fastchk)
            frames[femb * 2 + 1] = order_buf(buf=buf1, buf_end_addr=buf_end_addr, trigger_rec_ticks=trigger_rec_ticks, fastchk=fastchk)
        else:
            buf0_ordered, n_frames0 = order_buf(buf=buf0, buf_end_addr=buf_end_addr, trigger_rec_ticks=trigger_rec_ticks, fastchk=fastchk)
            buf1_ordered, n_frames1 = order_buf(buf=buf1, buf_end_addr=buf_end_addr, trigger_rec_ticks=trigger_rec_ticks, fastchk=fastchk)

            frames[femb * 2] = decode(buf0_ordered, n_frames0, 0)  # 0=CD 0
            frames[femb * 2 + 1] = decode(buf1_ordered, n_frames1, 1)  # 1=CD 1

    # buf0 data is frame[0][0], buf0 timestamps are frame[0][1]

    # do syncing stuff

    return frames

# reuse from DAT pro
def wib_dec(data, fembs=range(4), spy_num=1, fastchk=False, cd0cd1sync=True):  # data from one WIB
    spy_num_all = len(data)
    if spy_num_all < spy_num:
        spy_num = spy_num_all
    wibdata = []
    if fastchk == True:
        spy_num = 1
    for sn in range(spy_num):
        tmts = [[], [], [], [], [], [], [], []]
        cd_tmts = [[], [], [], [], [], [], [], []]
        femb00 = []
        femb01 = []
        femb10 = []
        femb11 = []
        femb20 = []
        femb21 = []
        femb30 = []
        femb31 = []
        raw = data[sn]
        bufs = raw[0]
        buf_end_addr = raw[1]
        spy_rec_ticks = raw[2]
        trig_cmd = raw[3]
        if trig_cmd == 0:
            trigmode = "SW"
        else:
            trigmode = "HW"
        dec_data = wib_spy_dec_syn(bufs, trigmode, buf_end_addr, spy_rec_ticks, fembs, fastchk)
        if fastchk:
            for fembno in fembs:
                if (dec_data[fembno * 2] != False) and (dec_data[fembno * 2 + 1] != False) and (
                        dec_data[fembno * 2] == dec_data[fembno * 2 + 1]):
                    # buf0 and buf1 of the same FEMB has sampe time stamp
                    return True
                else:
                    print("Data of FEMB{} is not synchoronized...".format(fembno))
                    return False
        # finessing data into correct format, used to be in rd demo
        # tmts = [list(dec_data[b][1]) for b in range(8)]
        # flen is always going to be 32
        if 0 in fembs:
            femb00 = np.transpose(dec_data[0][0])
            femb01 = np.transpose(dec_data[1][0])
            tmts[0] = dec_data[0][1]
            tmts[1] = dec_data[1][1]
            cd_tmts[0] = dec_data[0][3]
            cd_tmts[1] = dec_data[1][3]
        if 1 in fembs:
            femb10 = np.transpose(dec_data[2][0])
            femb11 = np.transpose(dec_data[3][0])
            tmts[2] = dec_data[2][1]
            tmts[3] = dec_data[3][1]
            cd_tmts[2] = dec_data[2][3]
            cd_tmts[3] = dec_data[3][3]
        if 2 in fembs:
            femb20 = np.transpose(dec_data[4][0])
            femb21 = np.transpose(dec_data[5][0])
            tmts[4] = dec_data[4][1]
            tmts[5] = dec_data[5][1]
            cd_tmts[4] = dec_data[4][3]
            cd_tmts[5] = dec_data[5][3]
        if 3 in fembs:
            femb30 = np.transpose(dec_data[6][0])
            femb31 = np.transpose(dec_data[7][0])
            tmts[6] = dec_data[6][1]
            tmts[7] = dec_data[7][1]
            cd_tmts[6] = dec_data[6][3]
            cd_tmts[7] = dec_data[7][3]
        if cd0cd1sync:
            t0s = [-1, -1, -1, -1, -1, -1, -1, -1]
            if 0 in fembs:
                t0s[0] = tmts[0][0]
                t0s[1] = tmts[1][0]
            if 1 in fembs:
                t0s[2] = tmts[2][0]
                t0s[3] = tmts[3][0]
            if 2 in fembs:
                t0s[4] = tmts[4][0]
                t0s[5] = tmts[5][0]
            if 3 in fembs:
                t0s[6] = tmts[6][0]
                t0s[7] = tmts[7][0]
            t0max = np.max(t0s)
            for i in range(8):
                if t0s[i] != -1:
                    t0s[i] = int((t0max - t0s[i]) // 32)  # 0x20
        else:
            t0s = [0, 0, 0, 0, 0, 0, 0, 0]
            t0max = 0
        if 0 in fembs:
            for i in range(len(femb00)):
                femb00[i] = femb00[i][t0s[0]:]
            for i in range(len(femb01)):
                femb01[i] = femb01[i][t0s[1]:]
            femb0 = list(femb00) + list(femb01)
            tmts[0] = tmts[0][t0s[0]:]
            cd_tmts[0] = cd_tmts[0][t0s[0]:]
            tmts[1] = tmts[1][t0s[1]:]
            cd_tmts[1] = cd_tmts[1][t0s[1]:]
        else:
            femb0 = None
        if 1 in fembs:
            for i in range(len(femb10)):
                femb10[i] = femb10[i][t0s[2]:]
            for i in range(len(femb11)):
                femb11[i] = femb11[i][t0s[3]:]
            femb1 = list(femb10) + list(femb11)
            tmts[2] = tmts[2][t0s[2]:]
            cd_tmts[2] = cd_tmts[2][t0s[2]:]
            tmts[3] = tmts[3][t0s[3]:]
            cd_tmts[3] = cd_tmts[3][t0s[3]:]
        else:
            femb1 = None
        if 2 in fembs:
            for i in range(len(femb20)):
                femb20[i] = femb20[i][t0s[4]:]
            for i in range(len(femb21)):
                femb21[i] = femb21[i][t0s[5]:]
            femb2 = list(femb20) + list(femb21)
            tmts[4] = tmts[4][t0s[4]:]
            cd_tmts[4] = cd_tmts[4][t0s[4]:]
            tmts[5] = tmts[5][t0s[5]:]
            cd_tmts[5] = cd_tmts[5][t0s[5]:]
        else:
            femb2 = None
        if 3 in fembs:
            for i in range(len(femb30)):
                femb30[i] = femb30[i][t0s[6]:]
            for i in range(len(femb31)):
                femb31[i] = femb31[i][t0s[7]:]
            femb3 = list(femb30) + list(femb31)
            tmts[6] = tmts[6][t0s[6]:]
            cd_tmts[6] = cd_tmts[6][t0s[6]:]
            tmts[7] = tmts[7][t0s[7]:]
            cd_tmts[7] = cd_tmts[7][t0s[7]:]
        else:
            femb3 = None
        wibdata.append([femb0, femb1, femb2, femb3, t0max, tmts, cd_tmts])  # temp for graphing
    return wibdata

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
#
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
#         #print(dec_data)
#         if fastchk:
#             for fembno in fembs:
#                 if (dec_data[fembno*2] != False) and (dec_data[fembno*2+1] != False) and (dec_data[fembno*2] == dec_data[fembno*2+1]) :
#                 #CD0 and CD1 of the same FEMB has different time stamp
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
#         # print(t0s)
#         if 0 in fembs:
#             #femb00 = list(zip(*femb00))
#             for i in range(len(femb00)):
#                 femb00[i]=femb00[i][t0s[0]:]
#             #femb01 = list(zip(*femb01))
#             for i in range(len(femb01)):
#                 femb01[i]=femb01[i][t0s[1]:]
#             femb0 = list(femb00) + list(femb01)
#         else:
#             femb0 = None
#         if 1 in fembs:
#             #femb10 = list(zip(*femb10))
#             for i in range(len(femb10)):
#                 femb10[i]=femb10[i][t0s[2]:]
#             #femb11 = list(zip(*femb11))
#             for i in range(len(femb11)):
#                 femb11[i]=femb11[i][t0s[3]:]
#             femb1 = list(femb10) + list(femb11)
#         else:
#             femb1 = None
#         if 2 in fembs:
#             #femb20 = list(zip(*femb20))
#             for i in range(len(femb20)):
#                 femb20[i]=femb20[i][t0s[4]:]
#             #femb21 = list(zip(*femb21))
#             for i in range(len(femb21)):
#                 femb21[i]=femb21[i][t0s[5]:]
#             femb2 = list(femb20) + list(femb21)
#         else:
#             femb2 = None
#         if 3 in fembs:
#             #femb30 = list(zip(*femb30))
#             for i in range(len(femb30)):
#                 femb30[i]=femb30[i][t0s[6]:]
#             #femb31 = list(zip(*femb31))
#             for i in range(len(femb31)):
#                 femb31[i]=femb31[i][t0s[7]:]
#             femb3 = list(femb30) + list(femb31)
#         else:
#             femb3 = None

        ##timestamp plotting test for FEMB 0
        # import matplotlib.pyplot as plt
        # import os
        # fig = plt.figure(figsize=(10,6))
        # x_tmts = np.arange(len(tmts[0]))
        # # plt.savefig(fdir + "timestamp.jpg")
        # # plt.close()
        # #master timestamp
        # plt.plot(x_tmts, np.array(tmts[0])-tmts[0][0], label ="Time Master Timestamp 0")
        # plt.plot(x_tmts, np.array(tmts[0])-tmts[0][0], label ="Time Master Timestamp 1")
        # plt.plot(x_tmts, np.array(cd_tmts[0])-cd_tmts[0][0], label ="Coldata Timestamp (FEMB0 CD0)")
        # plt.plot(x_tmts, np.array(cd_tmts[1])-cd_tmts[0][0], label ="Coldata Timestamp (FEMB0 CD1)")
        # plt.legend()
        # # plt.show()
        # plt.savefig(os.getcwd() + "/tmp_data/timestamp_dunedaq.jpg")
        # plt.close()
        
        # if 
        # for i, cdts in enumerate(cd_tmts[0]):
            # if True:#i % 64 == 0:
                # print(cdts-cd_tmts[0][0])

        #print(np.shape(femb00),np.shape(femb01),len(femb0))
        # print(tmts[0])
        # print(cd_tmts[0])
        
    #
    #     wibdata.append([femb0, femb1, femb2, femb3, t0max])
    #     #print(wibdata)
    #     #wibdata.append([femb0, femb1, femb2, femb3, tmts, cd_tmts]) #temp for graphing
    # return wibdata