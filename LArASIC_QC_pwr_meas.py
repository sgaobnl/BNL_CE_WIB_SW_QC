import time
import sys
import numpy as np
import pickle
import copy
import time, datetime, random, statistics    
from dat_cfg import DAT_CFGS
                
dat =  DAT_CFGS()
dat.fembs = [0]
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

