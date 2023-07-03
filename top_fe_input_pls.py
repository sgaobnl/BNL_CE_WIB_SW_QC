from wib_cfgs import WIB_CFGS
import time
import sys
import numpy as np
import pickle
import copy
import time, datetime, random, statistics

if len(sys.argv) < 2:
    print('Please specify at least one FEMB # to test')
    print('Usage: python wib.py 0')
    exit()    

if 'save' in sys.argv:
    save = True
    for i in range(len(sys.argv)):
        if sys.argv[i] == 'save':
            pos = i
            break
    sample_N = int(sys.argv[pos+1] )
    sys.argv.remove('save')
else:
    save = False
    sample_N = 1

fembs = [int(a) for a in sys.argv[1:pos]] 

chk = WIB_CFGS()

####################WIB init################################
#check if WIB is in position
chk.wib_fw()
time.sleep(1)

while True:
    for fe in range(8):
        chk.dat_set_dac(0.5, fe, -1, -1)
        time.sleep(0.1)
        chk.dat_set_dac(0.5, fe, -1, -1)
        time.sleep(0.1)

#MUX (SN74LV405AD)
#select_names_fe = ["GND", "Ext_Test", "DAC", "FE_COMMON_DAC", "VBGR", "DNI[To_AmpADC]", "GND", "AUX_VOLTAGE_MUX"]
chk.cdpoke(0, 0xC, 0, chk.DAT_ADC_FE_TEST_SEL, 2<<4)    
chk.cdpoke(0, 0xC, 0, chk.DAT_FE_TEST_SEL_INHIBIT, 0x00)   
#select PLS_FE
chk.cdpoke(0, 0xC, 0, chk.DAT_FE_CALI_CS, 0x00)    
#select FE_INS_PLS_CS
chk.cdpoke(0, 0xC, 0, chk.DAT_FE_IN_TST_SEL_LSB, 0x00)    
chk.cdpoke(0, 0xC, 0, chk.DAT_FE_IN_TST_SEL_MSB, 0x00)    
chk.cdpoke(0, 0xC, 0, chk.DAT_TEST_PULSE_SOCKET_EN, 0xff)    

#program in period & width 
period =0x2e4 
width = 0x50 
delay = 0x00
chk.cdpoke(0, 0xC, 0, chk.DAT_TEST_PULSE_PERIOD_LSB, period&0xFF);
chk.cdpoke(0, 0xC, 0, chk.DAT_TEST_PULSE_PERIOD_MSB, (period&0xFF00)>>8)	
chk.cdpoke(0, 0xC, 0, chk.DAT_TEST_PULSE_WIDTH_LSB, width&0xFF);
chk.cdpoke(0, 0xC, 0, chk.DAT_TEST_PULSE_WIDTH_MSB, (width&0xFF00)>>8)
chk.cdpoke(0, 0xC, 0, chk.DAT_TEST_PULSE_DELAY, 0x0); #delay not relevant if you're not using ASIC_DAC_CNTL

chk.cdpoke(0, 0xC, 0, chk.DAT_TEST_PULSE_EN, 0x4);

#input ()


####################FEMBs Configuration################################
#step 1
#reset all FEMBs on WIB
chk.wib_femb_link_en(fembs)

chk.femb_cd_rst()

cfg_paras_rec = []
for femb_id in fembs:
#step 2
#Configur Coldata, ColdADC, and LArASIC parameters. 
#Here Coldata uses default setting in the script (not the ASIC default register values)
#ColdADC configuraiton
    chk.adcs_paras = [ # c_id, data_fmt(0x89), diff_en(0x84), sdc_en(0x80), vrefp, vrefn, vcmo, vcmi, autocali
                        [0x4, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 0],
                        [0x5, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 0],
                        [0x6, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 0],
                        [0x7, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 0],
                        [0x8, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 0],
                        [0x9, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 0],
                        [0xA, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 0],
                        [0xB, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 0],
                      ]

#LArASIC register configuration
    chk.set_fe_board(sts=0, snc=1,sg0=0, sg1=0, st0=0, st1=0, swdac=0, sdd=0,dac=0x00 )
    adac_pls_en = 0 #enable LArASIC interal calibraiton pulser
    cfg_paras_rec.append( (femb_id, copy.deepcopy(chk.adcs_paras), copy.deepcopy(chk.regs_int8), adac_pls_en) )
#step 3
    chk.femb_cfg(femb_id, adac_pls_en )

chk.data_align(fembs)

time.sleep(0.5)

####################FEMBs Data taking################################
rawdata = chk.spybuf_trig(fembs=fembs, num_samples=sample_N, trig_cmd=0) #returns list of size 1

pwr_meas = chk.get_sensors()

if save:
    fdir = "./tmp_data/"
    ts = datetime.datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
    fp = fdir + "Raw_" + ts  + ".bin"
    with open(fp, 'wb') as fn:
        pickle.dump( [rawdata, pwr_meas, cfg_paras_rec], fn)
