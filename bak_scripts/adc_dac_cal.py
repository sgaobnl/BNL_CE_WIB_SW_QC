import time, datetime
import pickle

from wib_cfgs import WIB_CFGS
chk = WIB_CFGS()

print("before running this script: configure the FEMB chips and trigger")

print("ADC Calibration w/ ADC DACs")
num_samples = 2000
enable = 1

start = time.time()

#read VREFP and VREFN
##set ColdADC MonADC mux register ADC_FE_TEST_SEL to 2

##trigger MonADCs
###make sure adcs are done

##read each ADC's MonADC

##set ColdADC MonADC mux register ADC_FE_TEST_SEL to 3

##trigger MonADCs
###make sure adcs are done

##read each ADC's MonADC

chk.poke(0xA00C0070, num_samples << 10)

dac_setting_ch_avgs = [[] for dac_val in range(pow(2,16))]

#DAC ADC N to 0V
chk.dat_set_dac(0,adc=1)

#make sure ADCs are hooked to their ADCs
# ##Set ADC_P_TST_CSABC to 3, set ADC_N_TST_CSABC to 3  [Set ADC_PN_TST_SEL to 3 | (3 << 4)]
chk.cdpoke(0, 0xC, 0, chk.DAT_ADC_PN_TST_SEL, 0x33)
# ##Set ADC_TEST_IN_SEL to 0
chk.cdpoke(0, 0xC, 0, chk.DAT_ADC_TEST_IN_SEL, 0)
# ##Set ADC_SRC_CS_P to 0x0000 (ADC_SRC_CS_P_MSB, ADC_SRC_CS_P_LSB)
chk.cdpoke(0, 0xC, 0, chk.DAT_ADC_SRC_CS_P_LSB, 0x0)
chk.cdpoke(0, 0xC, 0, chk.DAT_ADC_SRC_CS_P_MSB, 0x0)


for dac_val in range(pow(2,16)): # for x in range(50):    
    #set DAC ADC P 
    chk.dat_set_dac(dac_val,adc=0)

    ch_avgs = []

    chk.poke(0xA00C0070, (num_samples << 10) | enable)
    chk.poke(0xA00C0070, num_samples << 10)

    accum_ready = False
    num_waits = 0
    while not (chk.peek(0xA00C00F0) & (0x3)) == 0x3: #notall ready
        num_waits = num_waits + 1
        # print("hi")
    
    for cd in range(2):
        # accum_ready = chk.peek(0xA00C00D4) & (0x1 << cd)
        #if accum_ready:  #  if True: #         
        for ch_id in range(64):
            ch = cd*64 + ch_id
            # wib.poke(REG_ACCUM_CH_ID, ch)            
            chk.poke(0xA00C0070, ch << 1)
            # ch_average = wib.peek(REG_ACCUM_CH_TOTAL) / num_samples
            ch_avg = chk.peek(0xA00C00F4) // num_samples
            # print("cd %d ch %d (overall ch %d): average of 0x%X (%d)"%(cd,ch_id,ch,ch_avg,ch_avg))
            ch_avgs.append(ch_avg)
            # # if ch % 16 < 8:
                # # expected = expect1#0x2af3
            # # else:
                # # expected = expect2#0x48d
            # # if ch_avg != expected:
                # # print("cd %d ch %d (overall ch %d): average of 0x%X, expected 0x%X"%(cd,ch_id,ch,ch_avg,expected))
        # else:
            # print("not ready")
            # break
    if dac_val % 1000 == 0:
        avg_of_avgs = sum(ch_avgs) / len(ch_avgs)
        print("dac_val %d: Avg ch_avg %f ranging from %d to %d. num_waits = %d"%(dac_val,avg_of_avgs,min(ch_avgs),max(ch_avgs),num_waits))
            # //store average
    dac_setting_ch_avgs[dac_val] = ch_avgs.copy()

#write dac_setting_ch_avgs to file
fdir = "./tmp_data/"
ts = datetime.datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
fp = fdir + "ADCcal_" + ts  + ".bin"
with open(fp, 'wb') as fn:
    pickle.dump(dac_setting_ch_avgs, fn)

#connect ADC back to ASIC channels
chk.cdpoke(0, 0xC, 0, chk.DAT_ADC_SRC_CS_P_LSB, 0xFF)
chk.cdpoke(0, 0xC, 0, chk.DAT_ADC_SRC_CS_P_MSB, 0xFF)

end = time.time()
elapsed = end - start
print("Time elapsed: %d seconds"%(elapsed))
