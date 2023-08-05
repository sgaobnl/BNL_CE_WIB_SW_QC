import time
import sys
import numpy as np
import pickle
import copy
import time, datetime, random, statistics    
from dat_cfg import DAT_CFGS
                
dat =  DAT_CFGS()
dat.fembs = [0]


fdir = "./tmp_data/"

if True:
    print ("perform ASIC-DAC calibration under 14mV/fC, 2us")
    adac_pls_en, sts, swdac, dac = dat.dat_cali_source(cali_mode=2, asicdac=0)
    cfg_info = dat.dat_fe_qc_cfg(adac_pls_en=adac_pls_en, sts=sts, swdac=swdac, dac=dac) 
    datad = {}

    slk0=0
    slk1=0
    st0=1
    st1=1
    sg0=0
    sg1=0
    for snc in [0, 1]:
#        for buf in [0,1,2]:
#            sdd = buf//2
#            sdf = buf%2
        if snc == 0:
            maxdac = 32
        else:
            maxdac = 64
        for dac in range(0, maxdac, maxdac//8):
            fe_cfg_info = dat.dat_fe_only_cfg(sts=sts, swdac=swdac, dac=dac, snc=snc, sg0=sg0, sg1=sg1, st0=st0, st1=st1, slk0=slk0, slk1=slk1, sdd=sdd, sdf=sdf) 
            data = dat.dat_fe_qc_acq(num_samples=5)
            cfgstr = "CALI_ASICDAC%02d"%(dac)
            print (cfgstr)
            datad[cfgstr] = [data, fe_cfg_info, cfg_info]

    fp = fdir + "QC_CALI_ASICDAC" + ".bin"
    with open(fp, 'wb') as fn:
        pickle.dump(datad, fn)
   
Vref = 1.583
if True:
    print ("perform DAC-DAC calibration under 14mV/fC, 2us")
    adac_pls_en, sts, swdac, dac = dat.dat_cali_source(cali_mode=1, val=Vref, period=1000, width=800) 
    cfg_info = dat.dat_fe_qc_cfg(adac_pls_en=adac_pls_en, sts=sts, swdac=swdac, dac=dac) 
    datad = {}

    slk0=0
    slk1=0
    st0=1
    st1=1
    sg0=0
    sg1=0
    sdd=0
    sdf=0
    for snc in [0, 1]:
        for buf in [0,1,2]:
            sdd = buf//2
            sdf = buf%2
            fe_cfg_info = dat.dat_fe_only_cfg(sts=sts, swdac=swdac, dac=dac, snc=snc, sg0=sg0, sg1=sg1, st0=st0, st1=st1, slk0=slk0, slk1=slk1, sdd=sdd, sdf=sdf) 
    
            if snc == 0:
                mindac = Vref - (75/185) 
            else:
                mindac = Vref - (150/185) 
    
            for dac in range(16):
                val = Vref-(dac*75/185/10)
                adac_pls_en, sts, swdac, dac = dat.dat_cali_source(cali_mode=1, val=val, period=1000, width=800) 
                data = dat.dat_fe_qc_acq(num_samples=5)
                cfgstr = "CALI_DATDAC_%dmV_SDD%d_SDF%d_SNC%d"%(int(val*1000), sdd, sdf, snc)
                print (cfgstr)
                datad[cfgstr] = [data, val, fe_cfg_info, cfg_info]
    
            fp = fdir + "QC_CALI_DATDAC" + ".bin"
            with open(fp, 'wb') as fn:
                pickle.dump(datad, fn)
   
if True:
    print ("perform DIRECT-input DAC calibration under 14mV/fC, 2us")
    adac_pls_en, sts, swdac, dac = dat.dat_cali_source(cali_mode=0, val=Vref, period=1000, width=800) 
    cfg_info = dat.dat_fe_qc_cfg(adac_pls_en=adac_pls_en, sts=sts, swdac=swdac, dac=dac) 
    datad = {}

    slk0=0
    slk1=0
    st0=1
    st1=1
    sg0=0
    sg1=0
    sdd=0
    sdf=0
    for snc in [0, 1]:
#        for buf in [0,1,2]:
#            sdd = buf//2
#            sdf = buf%2
        fe_cfg_info = dat.dat_fe_only_cfg(sts=sts, swdac=swdac, dac=dac, snc=snc, sg0=sg0, sg1=sg1, st0=st0, st1=st1, slk0=slk0, slk1=slk1, sdd=sdd, sdf=sdf) 

        if snc == 0:
            mindac = Vref - (75/1000) 
        else:
            mindac = Vref - (150/1000) 

        for dac in range(16):
            val = Vref-(dac*5/1000)
            adac_pls_en, sts, swdac, dac = dat.dat_cali_source(cali_mode=0, val=val, period=1000, width=800) 
            data = dat.dat_fe_qc_acq(num_samples=5)
            cfgstr = "CALI_DIRECT_%dmV"%(int(val*1000))
            print (cfgstr)
            datad[cfgstr] = [data, val, fe_cfg_info, cfg_info]

    fp = fdir + "QC_CALI_DIRECT" + ".bin"
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
