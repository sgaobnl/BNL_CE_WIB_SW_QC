from wib_cfgs import WIB_CFGS
import time
import sys
import numpy as np
import pickle
import copy
import time, datetime, random, statistics

def CreateFolders(fembNo, env):

    datadir = "coldbox_data/"
    for key,femb_no in fembNo.items():
        datadir = datadir + "femb{}_".format(femb_no)

    datadir = datadir + env

    n=1
    while (os.path.exists(datadir)):
        if n==1:
            datadir = datadir + "_R{:03d}".format(n)
        else:
            datadir = datadir[:-3] + "{:03d}".format(n)
        n=n+1
        if n>20:
            raise Exception("There are more than 20 folders...")

    try:
        os.makedirs(datadir)
    except OSError:
        print ("Error to create folder %s"%datadir)
        sys.exit()

    datadir = datadir+"/"

    return datadir

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
    if sample_N < 10:
        sample_N = 10
    sys.argv.remove('save')
else:
    save = False
    sample_N = 10

logs={}
tester=input("please input your name:  ")
logs['tester']=tester

env_cs = input("Test is performed at cold(LN2) (Y/N)? : ")
if ("Y" in env_cs) or ("y" in env_cs):
    env = "LN"
else:
    env = "RT"
logs['env']=env

fembs = [int(a) for a in sys.argv[1:pos]] 

fembNo={}
for i in fembs:
    fembNo['femb{}'.format(i)]=input("FEMB{} ID: ".format(i))

logs['femb id']=fembNo
logs['date']=datetime.datetime.now().strftime("%m_%d_%Y_%H_%M_%S")

if save:
    datadir=CreateFolders(fembNo, env)
    fp = datadir + "logs_env.bin"
    with open(fp, 'wb') as fn:
         pickle.dump(logs, fn)

chk = WIB_CFGS()

for snc in [0,1]:
    for st0 in [0,1]:
        for st1 in [0,1]:
        ####################WIB init################################
        #check if WIB is in position
        chk.wib_fw()
        ####################FEMBs Configuration################################
        #step 1
        #reset all FEMBs on WIB
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
            chk.set_fe_board(sts=0, snc=snc,sg0=0, sg1=0, st0=st0, st1=st1, swdac=0, sdd=0,dac=0x00 )
            adac_pls_en = 0 #enable LArASIC interal calibraiton pulser
            cfg_paras_rec.append( (femb_id, copy.deepcopy(chk.adcs_paras), copy.deepcopy(chk.regs_int8), adac_pls_en) )
        #step 3
            chk.femb_cfg(femb_id, adac_pls_en )
        
        chk.data_align(fembs)
        
        time.sleep(0.5)
        
        ####################FEMBs Data taking################################
        rawdata = chk.spybuf_trig(fembs=fembs, num_samples=sample_N, trig_cmd=0x08) #returns list of size 1
        
        pwr_meas = chk.get_sensors()
        
        if save:
            fp = datadir + "Raw_snc%d_st0%d_st1%d"%(snc,st0,st1) + ".bin"
            with open(fp, 'wb') as fn:
                pickle.dump( [rawdata, pwr_meas, cfg_paras_rec], fn)

