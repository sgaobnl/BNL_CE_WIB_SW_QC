from wib_cfgs import WIB_CFGS
import time
import sys
import pickle
import copy
import os
import time, datetime, random, statistics

def CreateFolders(fembNo, env, toytpc):

    datadir = "tmp_data/"
    for key,femb_no in fembNo.items():
        datadir = datadir + "femb{}_".format(femb_no)
    
    datadir = datadir+"{}_{}".format(env,toytpc)
    
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

####### Input FEMB slots #######

if len(sys.argv) < 2:
    print('Please specify at least one FEMB # to test')
    print('e.g. python3 quick_checkout.py 0')
    exit()

if 'save' in sys.argv:
    save = True
    for i in range(len(sys.argv)):
        if sys.argv[i] == 'save':
            pos = i
            break
    sample_N = int(sys.argv[pos+1] )
    sys.argv.remove('save')
    fembs = [int(a) for a in sys.argv[1:pos]]
else:
    save = False
    sample_N = 1
    fembs = [int(a) for a in sys.argv[1:]]

####### Input test information #######

logs={}
tester=input("please input your name:  ")
logs['tester']=tester

env_cs = input("Test is performed at cold(LN2) (Y/N)? : ")
if ("Y" in env_cs) or ("y" in env_cs):
    env = "LN"
else:
    env = "RT"
logs['env']=env

ToyTPC_en = input("ToyTPC at FE inputs (Y/N) : ")
if ("Y" in ToyTPC_en) or ("y" in ToyTPC_en):
    toytpc = "150pF"
else:
    toytpc = "0pF"
logs['toytpc']=toytpc

note = input("A short note (<200 letters):")
logs['note']=note

fembNo={}
for i in fembs:
    fembNo['femb{}'.format(i)]=input("FEMB{} ID: ".format(i))

logs['femb id']=fembNo
logs['date']=datetime.datetime.now().strftime("%m_%d_%Y_%H_%M_%S")

####### Create data save directory #######
if save:
    datadir=CreateFolders(fembNo, env, toytpc)
    fp = datadir + "logs_env.bin"
    with open(fp, 'wb') as fn:
         pickle.dump(logs, fn)

t1 = time.time()
####### Power and configue FEMBs #######
chk = WIB_CFGS()
chk.wib_fw()

#set FEMB voltages
chk.fembs_vol_set(vfe=3.0, vcd=3.0, vadc=3.5)
chk.femb_powering(fembs)
time.sleep(2)

pwr_meas = chk.get_sensors()

chk.wib_femb_link_en(fembs)
chk.femb_cd_rst()

snc = 1 # 200 mV
sg0 = 0
sg1 = 0 # 14mV/fC
st0 = 1 
st1 = 1 # 2us 

cfg_paras_rec = []
for femb_id in fembs:
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
    chk.set_fe_board(sts=1, snc=snc, sg0=sg0, sg1=sg1, st0=st0, st1=st1, swdac=1, dac=0x20 )
    adac_pls_en = 1 
    cfg_paras_rec.append( (femb_id, copy.deepcopy(chk.adcs_paras), copy.deepcopy(chk.regs_int8), adac_pls_en) )
    chk.femb_cfg(femb_id, adac_pls_en )

chk.data_align(fembs)
time.sleep(0.5)

####### Take data #######
rawdata = chk.spybuf_trig(fembs=fembs, num_samples=sample_N, trig_cmd=0) #returns list of size 1
pwr_meas = chk.get_sensors()

####### Save data #######
if save:
    fp = datadir + "Raw_SE_{}_{}_{}_0x{:02x}.bin".format("200mVBL","14_0mVfC","2_0us",0x20)

    with open(fp, 'wb') as fn:
        pickle.dump( [rawdata, pwr_meas, cfg_paras_rec, logs], fn)

####### Take monitoring data #######
sps=1
print ("monitor bandgap reference")
nchips=range(8)
mon_refs = {}
for i in nchips:   # 8 chips per femb
    adcrst = chk.wib_fe_mon(femb_ids=fembs, mon_type=2, mon_chip=i, snc=snc, sg0=sg0, sg1=sg1, sps=sps)
    mon_refs[f"chip{i}"] = adcrst

print ("monitor temperature")
mon_temps = {}
for i in nchips:
    adcrst = chk.wib_fe_mon(femb_ids=fembs, mon_type=1, mon_chip=i, snc=snc, sg0=sg0, sg1=sg1, sps=sps)
    mon_temps[f"chip{i}"] = adcrst

print ("monitor ColdADCs")
mon_adcs = {}
for i in nchips:
    mon_adc =  chk.wib_adc_mon_chip(femb_ids=fembs, mon_chip=i, sps=sps)
    mon_adcs[f"chip{i}"] = mon_adc

if save:
    fp = datadir + "Mon_{}_{}.bin".format("200mVBL","14_0mVfC")

    with open(fp, 'wb') as fn:
        pickle.dump( [mon_refs, mon_temps, mon_adcs, logs], fn)
####### Power off FEMBs #######
print("Turning off FEMBs")
chk.femb_powering([])

t2=time.time()
print(t2-t1)
