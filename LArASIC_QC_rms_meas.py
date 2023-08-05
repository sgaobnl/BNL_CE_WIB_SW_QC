import time
import sys
import numpy as np
import pickle
import copy
import time, datetime, random, statistics    
from dat_cfg import DAT_CFGS
                
dat =  DAT_CFGS()
dat.fembs = [0]

adac_pls_en, sts, swdac, dac = dat.dat_cali_source(cali_mode=3)
cfg_info = dat.dat_fe_qc_cfg(adac_pls_en=adac_pls_en, sts=sts, swdac=swdac, dac=dac) 

fdir = "./tmp_data/"
sdd=0
sdf=0
slk0=0
slk1=0
snc=0
st0=0
st1=0
sg0=0
sg1=0

datad = {}

if True:
    print ("Test RMS noise with differnt BLs, peak times and gains")
    sdd=0
    sdf=0
    slk0=0
    slk1=0
    for snc in [0, 1]:
        for sg0 in [0,1]:
            for sg1 in [0,1]:
                for st0 in [0,1]:
                    for st1 in [0,1]:
                        fe_cfg_info = dat.dat_fe_only_cfg(snc=snc, sg0=sg0, sg1=sg1, st0=st0, st1=st1, slk0=slk0, slk1=slk1, sdd=sdd, sdf=sdf) 
                        data = dat.dat_fe_qc_acq(num_samples=10)
                        cfgstr = "RMS_SDD%d_SDF%d_SLK0%d_SLK1%d_SNC%d_ST0%d_ST1%d_SG0%d_SG1%d"%(sdd, sdf, slk0, slk1, snc, st0, st1, sg0, sg1)
                        print (cfgstr)
                        datad[cfgstr] = [data, fe_cfg_info, cfg_info]

if True:
    print ("Test RMS noise with differnt output modes under 14mV/fC, 2us")
    slk0=0
    slk1=0
    st0=1
    st1=1
    sg0=0
    sg1=0
    for snc in [0, 1]:
        for buf in [0,1,2]:
            sdd = buf//2
            sdf = buf%2
            fe_cfg_info = dat.dat_fe_only_cfg(snc=snc, sg0=sg0, sg1=sg1, st0=st0, st1=st1, slk0=slk0, slk1=slk1, sdd=sdd, sdf=sdf) 
            data = dat.dat_fe_qc_acq(num_samples=10)
            cfgstr = "RMS_OUTPUT_SDD%d_SDF%d_SLK0%d_SLK1%d_SNC%d_ST0%d_ST1%d_SG0%d_SG1%d"%(sdd, sdf, slk0, slk1, snc, st0, st1, sg0, sg1)
            print (cfgstr)
            datad[cfgstr] = [data, fe_cfg_info, cfg_info]

if True:
    print ("Test RMS noise with differnt leakage currents under 14mV/fC, 2us")
    sdd=0
    sdf=0
    snc=0
    st0=1
    st1=1
    sg0=0
    sg1=0
    for slk0 in [0, 1]:
        for slk1 in [0,1]:
            fe_cfg_info = dat.dat_fe_only_cfg(snc=snc, sg0=sg0, sg1=sg1, st0=st0, st1=st1, slk0=slk0, slk1=slk1, sdd=sdd, sdf=sdf) 
            data = dat.dat_fe_qc_acq(num_samples=10)
            cfgstr = "RMS_SLK_SDD%d_SDF%d_SLK0%d_SLK1%d_SNC%d_ST0%d_ST1%d_SG0%d_SG1%d"%(sdd, sdf, slk0, slk1, snc, st0, st1, sg0, sg1)
            print (cfgstr)
            datad[cfgstr] = [data, fe_cfg_info, cfg_info]

fp = fdir + "QC_RMS" + ".bin"
with open(fp, 'wb') as fn:
    pickle.dump(datad, fn)


#for buf in [0,1,2]:
#    sdd = buf//2
#    sdf = buf%2
#    for slk0 in [0,1]:
#        for slk1 in [0,1]:
#            for snc in [0,1]:
#                for st0 in [0,1]:
#                    for st1 in [0,1]:
#                        for sg0 in [0,1]:
#                            for sg1 in [0,1]:
#                                fe_cfg_info = dat.dat_fe_only_cfg(snc=snc, sg0=sg0, sg1=sg1, st0=st0, st1=st1, slk0=slk0, slk1=slk1, sdd=sdd, sdf=sdf) 
#                                data = dat.dat_fe_qc_acq(num_samples=10)
#                                cfgstr = "RMS_SDD%d_SDF%d_SLK0%d_SLK1%d_SNC%d_ST0%d_ST1%d_SG0%d_SG1%d"%(sdd, sdf, slk0, slk1, snc, st0, st1, sg0, sg1)
#                                print (cfgstr)
#                                datad[cfgstr] = [data, fe_cfg_info, cfg_info]
#
#    fp = fdir + "QC_RMS_SDD%d_SDF%d"%(sdd, sdf) + ".bin"
#    with open(fp, 'wb') as fn:
#        pickle.dump(datad, fn)
#
