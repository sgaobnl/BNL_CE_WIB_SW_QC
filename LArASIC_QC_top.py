import time
import sys
import numpy as np
import pickle
import copy
import time, datetime, random, statistics    
from dat_cfg import DAT_CFGS
                
dat =  DAT_CFGS()

####### Input test information #######
debug_mode = True

logs={}
if debug_mode:
    tester="SGAO"
else:
    tester=input("please input your name:  ")
logs['tester']=tester

if debug_mode:
    env_cs = "RT"
else:
    env_cs = input("Test is performed at cold(LN2) (Y/N)? : ")

if ("Y" in env_cs) or ("y" in env_cs):
    env = "LN"
else:
    env = "RT"
logs['env']=env

if debug_mode:
    note = "debug..."
else:
    note = input("A short note (<200 letters):")
logs['note']=note

while True:
    if debug_mode:
        datawib = "0"
    else:
        datonwib=input("DAT on WIB slot (0, 1, 2, 3) :")
    try int(datonwib):
        if int(datonwib) >=0 and int(datonwib) <=3:
            dat.fembs = [int(datonwib)]
            break
        else:
            print ("Wrong input, please input number 0 to 3")
    except:
        print ("Wrong input, please input number 0 to 3")

logs['DAT_on_WIB_slot']=fembNo

fe_id = {}
for fe in range(8):
    if debug_mode:
        fe_id['FE{}'.format(i)] = "%d"%fe 
    else:
        fe_id['FE{}'.format(i)] =input("FE SN on socket {}: ".format(i))

logs['date']=datetime.datetime.now().strftime("%m_%d_%Y_%H_%M_%S")

####### Input test information #######

data = {}
for snc in [0, 1]:
    for sdd in [0, 1]:
        for sdf in [0, 1]:
            if (sdd == 1) and (sdf==1):
                continue
            else:
                adac_pls_en, sts, swdac, dac = dat.dat_cali_source(cali_mode=2, asicdac=0x10)
                rawdata = dat.dat_fe_qc(adac_pls_en=adac_pls_en, sts=sts, swdac=swdac, dac=dac,snc=snc, sdd=sdd, sdf=sdf ) 
                pwr_meas = dat.fe_pwr_meas()
                data["PWR_SDD%d_SDF%d_SNC%d"%(sdd,sdf,snc)] = [dat.fembs, snc, sdd, sdf, rawdata, pwr_meas]

fdir = "./tmp_data/"
fp = fdir + "QC_PWR" + ".bin"
with open(fp, 'wb') as fn:
    pickle.dump(data, fn)

