import struct, os, sys
import time, datetime
import pickle
import ctypes

from wib_cfgs import WIB_CFGS

self = WIB_CFGS()

def histbuf(): #adapted from llc.spybuf()
    HIST_MEM_SIZE = 0x8000 #rom A00C8000 to A00CFFFF
    buf = (ctypes.c_char*HIST_MEM_SIZE)()
    buf_bytes = bytearray(HIST_MEM_SIZE)
    

    self.wib.bufread(buf,8) #read from histogram memory
    byte_ptr = (ctypes.c_char*HIST_MEM_SIZE).from_buffer(buf_bytes)            
    if not ctypes.memmove(byte_ptr, buf, HIST_MEM_SIZE):
        print('memmove failed')
        exit()
                
    return buf_bytes 
    
def histbuf_trig(fembs,num_samples=1639000):

    print("WIB histogram test")  
    print("before running this script: configure the FEMB chips and trigger")  

#    print("Connecting ADCP channels to WIB external signal")
#    # Set ADC_PN_TST_SEL to 0x1 to select TST_PULSE_AMON on the ADC P mux and GND on the ADC N mux
#    self.cdpoke(0, 0xC, 0, self.DAT_ADC_PN_TST_SEL, 0x1)
#
#    # Set ADC_TEST_IN_SEL to 0x0 to connect the P&N mux outputs to ADC_test_P and ADC_test_N, respectively
#    self.cdpoke(0, 0xC, 0, self.DAT_ADC_TEST_IN_SEL, 0x0)
#
#    # Set ADC_SRC_CS_P_MSB and ADC_SRC_CS_P_LSB both to 0x0 to connect all ColdADC positive and negative 
#    # input channels to ADC_test_P and ADC_test_N, respectively.
#    self.cdpoke(0, 0xC, 0, self.DAT_ADC_SRC_CS_P_LSB, 0x0)
#    self.cdpoke(0, 0xC, 0, self.DAT_ADC_SRC_CS_P_MSB, 0x0)


    #set samples to take
    self.poke(0xA00C007C, num_samples)

    hist_data = []

    #chs = 128
    chs = []
    for femb in fembs:
        for ch in range(128):
            chs.append(femb*128+ch)

    start = time.time()
    #for ch in range(chs):   
    t0 = time.time_ns()
    #for ch in chs:    
    for ch in [1]:    
        #indicate which channel is to be analyzed
        self.poke(0xA00C0078, ch)
        
#        while True:
#            print (hex(self.peek(0xA00C00F0) & ~(0x3ff)))
#            time.sleep(0.100)
        while self.peek(0xA00C00F0) & ~(0x3ff) != 0x000: #wait till monitor output = 0x000
            pass
        
        #trigger histogram
        self.poke(0xA00C0074, 0x1)
        self.poke(0xA00C0074, 0x0)
        
        num_waits = 0
        while self.peek(0xA00C00F0) & (0x1<<9) == 0: #while hist not done
            num_waits = num_waits + 1
            pass
            
        ch_hist_data = histbuf()
        #print (ch_hist_data)
        print ("ch{}".format(ch), (time.time_ns()-t0)/(10**9) )
            

        hist_data.append(ch_hist_data)

#    print("Connecting ADC back to ASIC channels")
#    self.cdpoke(0, 0xC, 0, self.DAT_ADC_SRC_CS_P_LSB, 0xFF)
#    self.cdpoke(0, 0xC, 0, self.DAT_ADC_SRC_CS_P_MSB, 0xFF)
    
    #Set P12 LEMO output to 10mhz clock
    self.poke(0xA00C0078, 0x0)
    
    return hist_data
    

if __name__ == "__main__":
    
    fembs = [0]
    if len(sys.argv) > 1:
        num_samples = int(sys.argv[1])
        hist_data = histbuf_trig(fembs,num_samples)
    else:
        #num_samples = 1639000 #default    
        hist_data = histbuf_trig(fembs)

    #write hist_data to file
    fdir = "./tmp_data/"
    ts = datetime.datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
    fp = fdir + "ADChist_" + ts  + ".bin"
    with open(fp, 'wb') as fn:
        pickle.dump(hist_data, fn)  
