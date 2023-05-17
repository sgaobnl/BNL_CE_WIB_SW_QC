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

snc=0
sg0=1
sg1=1
st0=0
st1=0
sdd=0
for runi in range(32):
    snc = runi%2
    sg0 = (runi>>1)%2
    sg1 = (runi>>1)%2
    st0 = (runi>>2)%2
    st1 = (runi>>3)%2
    sdd = (runi>>4)%2

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
                            [0x4, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 1],
                            [0x5, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 1],
                            [0x6, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 1],
                            [0x7, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 1],
                            [0x8, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 1],
                            [0x9, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 1],
                            [0xA, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 1],
                            [0xB, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 1],
                          ]
        if sdd==1:
            for i in range(8):
                chk.adcs_paras[i][2] = 1
    
    #LArASIC register configuration
        chk.set_fe_board(sts=0, snc=snc,sg0=sg0, sg1=sg1, st0=st0, st1=st1, swdac=0, sdd=sdd,dac=0x00 )
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
        fp = fdir + "Raw_" + ts + "sg0%d_sg1%d_snc%dst0%dst1%dsdd%d"%(sg0,sg1,snc,st0,st1,sdd) + ".bin"
        with open(fp, 'wb') as fn:
            pickle.dump( [rawdata, pwr_meas, cfg_paras_rec], fn)
    
