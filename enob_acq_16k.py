import ctypes, ctypes.util
import struct, os, sys
import time, datetime
import pickle
import importlib.machinery

from wib_cfgs import WIB_CFGS
from adc_hist_buf import histbuf


def acq_16ksamp(fembs):
    print("WIB ENOB 16,384 samples test")  
    print("before running this script: configure the FEMB chips and trigger")  
    
    chs = []
    for femb in fembs:
        for ch in range(128):
            chs.append(femb*128+ch)    

    chk = WIB_CFGS()

    #2^14 continous samples of channel 0
    hist_start_addr = 0xa00c8000
    
    ch_data = []
    #fig, ax = plt.subplots(figsize=(10,6))
    for ch in chs:
        
        chk.poke(0xa00c0078, ch)
        #trigger capture
        chk.poke(0xa00c0074, 0x3)
        chk.poke(0xa00c0074, 0x2)
        #wait till capture done
        while (chk.peek(0xa00c00f0) & 0x100) == 0:
           #print(hex(chk.peek(0xa00c00f0)))
           pass
        chk.poke(0xa00c0074, 0x0)
        data = histbuf() #block read
        # num_16bwords = 0x8000 / 2
        # words16b = list(struct.unpack_from("<%dH"%(num_16bwords),data))
        
        # chip = ch // 16
        # plt.plot(words16b,color='C%d'%chip)
        ch_data.append(data)
        print("Ch",ch)

    
        # if ch%16 < 8:
            # pattern = 0x2af3
        # else:
            # pattern = 0x48d    
            
        # if any([x!=pattern for x in words16b]): #
            # print(words16b)
            # print("Oh no! ch %d has non-pattern values inside the slice"%(ch))
                   
            # mem = []
            # for i in range(int(0x8000/4)): 
                # reg = chk.peek(hist_start_addr + i*4)
                # mem.append(reg&0xFFFF)
                # mem.append((reg&0xFFFF0000)>>16)
            # if all(x == y for x, y in zip(words16b, mem)):
                # print("Readout correct")
            # else:
                # print("Readout incorrect")
            # input("")  
    return ch_data
    
# print(words16b)
# plt.plot(words16b)
# plt.savefig(os.getcwd()+"/tmp_data/enob_signal.jpg")
if __name__ == "__main__":
    
    if len(sys.argv) > 1:
        fembs = [int(sys.argv[1])]
    else:
        fembs = [0]
    ch_data = acq_16ksamp(fembs)
 
    #write _data to file
    fdir = "./tmp_data/"
    ts = datetime.datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
    fp = fdir + "Raw16k_" + ts  + ".bin"
    with open(fp, 'wb') as fn:
        pickle.dump(ch_data, fn)     
