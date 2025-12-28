import struct, os, sys
import time, datetime
import pickle

from wib_cfgs import WIB_CFGS



self = WIB_CFGS()



def hist_reg_read(hist_addr):
    #address is 14-bit
    hist_addr = hist_addr & 0x3FFF
    #turn off hist_write and set address
    self.poke(0xA00C0074, (hist_addr<<2))   
    #sleep for >32 ns
    pass
    pass
    pass
    #read hist_dout  
    return self.peek(0xA00C00F8)
    
def hist(fembs,num_samples=1800000):

    print("WIB histogram test")  
    print("before running this script: configure the FEMB chips and trigger")  


    #print("Connecting ADCP channels to WIB external signal")
    ## Set ADC_PN_TST_SEL to 0x1 to select TST_PULSE_AMON on the ADC P mux and GND on the ADC N mux
    #self.cdpoke(0, 0xC, 0, self.DAT_ADC_PN_TST_SEL, 0x1)

    ## Set ADC_TEST_IN_SEL to 0x0 to connect the P&N mux outputs to ADC_test_P and ADC_test_N, respectively
    #self.cdpoke(0, 0xC, 0, self.DAT_ADC_TEST_IN_SEL, 0x0)

    ## Set ADC_SRC_CS_P_MSB and ADC_SRC_CS_P_LSB both to 0x0 to connect all ColdADC positive and negative 
    ## input channels to ADC_test_P and ADC_test_N, respectively.
    #self.cdpoke(0, 0xC, 0, self.DAT_ADC_SRC_CS_P_LSB, 0x0)
    #self.cdpoke(0, 0xC, 0, self.DAT_ADC_SRC_CS_P_MSB, 0x0)


    #set samples to take
    self.poke(0xA00C007C, num_samples)

    hist_data = []

    #chs = 128
    chs = []
    for femb in fembs:
        for ch in range(128):
            chs.append(femb*128+ch)

    #start = time.time()
    start = time.time_ns()
    #for ch in range(chs):   
    #for ch in chs:    
    for ch in [0,1]:    
        #indicate which channel is to be analyzed
        # self.poke(0xA00C0078, ch | (0x1<<9)) #extra bit is to make sure trigger is output over P12 LEMO
        self.poke(0xA00C0078, ch)
        
        #wait till monitor output = 0x000
        #while self.peek(0xA00C00F0) & ~(0x3ff) != 0x000:
        #    pass
        i = 0
        print ( time.time_ns() - start)
        while True:
            i = i + 1
            if ((self.peek(0xA00C00F0) >>10)&0x3FFF) == 0x0000:
                break
        print ( time.time_ns() - start)
        
        #trigger histogram
        self.poke(0xA00C0074, 0x1)
        self.poke(0xA00C0074, 0x0)
        print ( time.time_ns() - start)
        
        num_waits = 0
        while self.peek(0xA00C00F0) & (0x1<<9) == 0: #while hist not done
            num_waits = num_waits + 1
            pass
            
        print ( time.time_ns() - start)

        #read out data
        ch_hist_data = []
        for addr in range(pow(2,14)):
            ch_hist_data.append(hist_reg_read(addr))
            
        print("Ch",ch) # ,"stats:")
        # for addr,count in enumerate(ch_hist_data):
            # if count != 0:
                # print(count,"counts of ADC value",hex(addr),"num_waits =",num_waits)

        hist_data.append(ch_hist_data)
        print ( time.time_ns() - start)

    #print("Connecting ADC back to ASIC channels")
    #self.cdpoke(0, 0xC, 0, self.DAT_ADC_SRC_CS_P_LSB, 0xFF)
    #self.cdpoke(0, 0xC, 0, self.DAT_ADC_SRC_CS_P_MSB, 0xFF)
    
    #Set P12 LEMO output to 10mhz clock
    self.poke(0xA00C0078, 0x0)
    
    return hist_data
    
    
  

if __name__ == "__main__":
    fembs = [0]
#    while True:
#        print (self.peek(0xA00C00F0), hex(self.peek(0xA00C00F0)))
#        time.sleep(1)
        
    if len(sys.argv) > 1:
        num_samples = int(sys.argv[1])
        hist_data = hist(fembs,num_samples)
    else:
        #num_samples = 1639000 #default    
        hist_data = hist(fembs)

    #write hist_data to file
    fdir = "./tmp_data/"
    ts = datetime.datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
    fp = fdir + "ADChist_" + ts  + ".bin"
    with open(fp, 'wb') as fn:
        pickle.dump(hist_data, fn)  
