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

#LArASIC register configuration
    chk.set_fe_board(sts=1, snc=1,sg0=0, sg1=0, st0=0, st1=0, swdac=1, sdd=0,dac=0x20 )
    adac_pls_en = 1 #enable LArASIC interal calibraiton pulser
    cfg_paras_rec.append( (femb_id, copy.deepcopy(chk.adcs_paras), copy.deepcopy(chk.regs_int8), adac_pls_en) )
#step 3
    chk.femb_cfg(femb_id, adac_pls_en )

if True: # FE monitoring 
    if True: # FE monitoring 
        sps = 1
        chips = 8
        if False:
            print ("monitor bandgap reference")
            mon_refs = {}
            for mon_chip in range(chips):
                adcrst = chk.wib_fe_mon(femb_ids=fembs, mon_type=2, mon_chip=mon_chip, sps=sps, sdf=1)
                print (adcrst)
                adcrst = chk.wib_fe_mon(femb_ids=fembs, mon_type=2, mon_chip=mon_chip, sps=sps, sdf=0)
                print (adcrst)
                print ("###################")

#
        if False:
            print ("monitor temperature")
            mon_temps = {}
            for mon_chip in range(chips):
                adcrst = chk.wib_fe_mon(femb_ids=fembs, mon_type=1, mon_chip=mon_chip, sps=sps, sdf=1)
                print (adcrst)
                adcrst = chk.wib_fe_mon(femb_ids=fembs, mon_type=1, mon_chip=mon_chip, sps=sps, sdf=0)
                print (adcrst)
                print ("###################")


        if True:
            print ("monitor BL")
            mon_temps = {}
            #for mon_chip in range(chips):
            for mon_chip in range(8):
                print ("""""""""""""""""""""""""""""""""""""""""""")
                print (mon_chip)
                for i in range(16):
                    adcrst = chk.wib_fe_mon(femb_ids=fembs, mon_type=0, mon_chip=mon_chip, mon_chipchn=0, snc=0, sdf=0, sps=sps)
                    print (adcrst)
#                adcrst = chk.wib_fe_mon(femb_ids=fembs, mon_type=0, mon_chip=mon_chip, mon_chipchn=0, snc=0, sdf=1, sps=sps)
#                print (adcrst)
#                adcrst = chk.wib_fe_mon(femb_ids=fembs, mon_type=0, mon_chip=mon_chip, mon_chipchn=0, snc=1, sdf=0, sps=sps)
#                print (adcrst)
#                adcrst = chk.wib_fe_mon(femb_ids=fembs, mon_type=0, mon_chip=mon_chip, mon_chipchn=0, snc=1, sdf=1, sps=sps)
#                print (adcrst)

        #if True:
        if False:
            print ("monitor vdac ")
            mon_refs = {}
            #for mon_chip in range(chips):
            #for mon_chip in [1]:
            while True:
                for mon_chip in range(chips):
                    #adcrst = chk.wib_fe_dac_mon(femb_ids=fembs, mon_chip=mon_chip, sgp=True, sg0=0, sg1=0, vdacs=range(0,64,8), sps = 1 )
                    adcrst = chk.wib_fe_dac_mon(femb_ids=fembs, mon_chip=mon_chip, sgp=True, sg0=0, sg1=0, vdacs=[63], sps = 1 )
                    print (adcrst)
                for mon_chip in range(chips):
                    #adcrst = chk.wib_fe_dac_mon(femb_ids=fembs, mon_chip=mon_chip, sgp=True, sg0=0, sg1=0, vdacs=range(0,64,8), sps = 1 )
                    adcrst = chk.wib_fe_dac_mon(femb_ids=fembs, mon_chip=mon_chip, sgp=True, sg0=0, sg1=0, vdacs=[0], sps = 1 )
                    print (adcrst)
                break

#        if True:
#            print ("monitor vdac ")
#            mon_refs = {}
#            #for mon_chip in range(chips):
#            #for mon_chip in [1]:
#            for mon_chip in range(chips):
#                adcrst = chk.wib_fe_dac_mon(femb_ids=fembs, mon_chip=mon_chip, sgp=True, sg0=1, sg1=0, vdacs=[64], sps = 1 )
#                print (adcrst)

        #if True:
        if False:
            print ("monitor bandgap reference")
            mon_refs = {}
            #for mon_chip in range(chips):
            #for mon_chip in [1]:
            for mon_chip in range(chips):
                adcrst = chk.wib_fe_mon(femb_ids=fembs, mon_type=2, mon_chip=mon_chip, sps=sps)
                #chk.wib_fe_dac_mon(femb_ids=fembs, mon_chip=0,sgp=True, sg0=1, sg1=0, vdacs=range(64), sps = 3 )
                print (adcrst)
     
        #if True:
        #    print ("monitor temperature")
        #    mon_temps = {}
        #    for mon_chip in range(chips):
        #        adcrst = chk.wib_fe_mon(femb_ids=fembs, mon_type=1, mon_chip=mon_chip, sps=sps)
        #        mon_ts=time.time_ns()
        #        mon_temps[f"chip{mon_chip}_temper"] = adcrst
        #    mon_paras.append([ip,mon_temps, mon_ts])

