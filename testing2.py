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

####################FEMBs Configuration################################
#step 1
#reset all FEMBs on WIB
chk.wib_femb_link_en(fembs)

while True:
    chk.femb_cd_rst()
    
    cfg_paras_rec = []
    for femb_id in fembs:
    #step 2
    #Configur Coldata, ColdADC, and LArASIC parameters. 
    #Here Coldata uses default setting in the script (not the ASIC default register values)
    #ColdADC configuraiton
        sdd = 0
        chk.adcs_paras = [ # c_id, data_fmt(0x89), diff_en(0x84), sdc_en(0x80), vrefp, vrefn, vcmo, vcmi, autocali
                            [0x4, 0x28, 0, 0, 0xDF, 0x33, 0x89, 0x67, 1],#fe4 
                            [0x5, 0x28, 0, 0, 0xDF, 0x33, 0x89, 0x67, 1],#fe5
                            [0x6, 0x28, 0, 0, 0xDF, 0x33, 0x89, 0x67, 1],#fe6
                            [0x7, 0x28, 0, 0, 0xDF, 0x33, 0x89, 0x67, 1],#fe7
                            [0x8, 0x28, 0, 0, 0xDF, 0x33, 0x89, 0x67, 1],#fe0
                            [0x9, 0x28, 0, 0, 0xDF, 0x33, 0x89, 0x67, 1],#fe1
                            [0xA, 0x28, 0, 0, 0xDF, 0x33, 0x89, 0x67, 1],#fe2
                            [0xB, 0x28, 0, 0, 0xDF, 0x33, 0x89, 0x67, 1],#fe3
                          ]
    
    #LArASIC register configuration
        #kk = int(input ("number"))
        kk=1
        k0 = kk%2
        k1 = kk//2
        chk.set_fe_board(sts=0, snc=0,sg0=0, sg1=0, st0=1, st1=1, swdac=0, slk1=k1, slk0=k0, sdd=sdd, sdf=0, dac=0x00 )
        adac_pls_en = 0 #enable LArASIC interal calibraiton pulser
        cfg_paras_rec.append( (femb_id, copy.deepcopy(chk.adcs_paras), copy.deepcopy(chk.regs_int8), adac_pls_en) )
    #step 1
        chk.femb_cfg(femb_id, adac_pls_en )
        #chk.femb_cd_gpio(femb_id=femb_id, cd1_0x26 = 0x00,cd1_0x27 = 0x1f, cd2_0x26 = 0x00,cd2_0x27 = 0x1f)
    #break
    print("XXXXXXXXXXXXXXXX")
    print(i)

    chk.data_align(fembs)

####################FEMBs Data taking################################
rawdata = chk.spybuf_trig(fembs=fembs, num_samples=sample_N, trig_cmd=0) #returns list of size 1

pwr_meas = chk.get_sensors()
#
if save:
    fdir = "./tmp_data/"
    fntmp = input ("filename: ")
    ts = datetime.datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
    fp = fdir + fntmp + "Raw_"  + ts  + ".bin"
    with open(fp, 'wb') as fn:
        pickle.dump( [rawdata, pwr_meas, cfg_paras_rec], fn)

