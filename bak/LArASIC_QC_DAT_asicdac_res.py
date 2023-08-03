import time
import sys
import numpy as np
import pickle
import copy
import time, datetime, random, statistics    
from dat_cfg import DAT_CFGS
                
dat =  DAT_CFGS()

data = dat.dat_fe_qc( num_samples = 1, adac_pls_en = 1, sts=1, snc=1,sg0=0, sg1=0, st0=1, st1=1, swdac=1, sdd=1, sdf=0, dac=0x20, slk0=0, slk1=0)

fdir = "./tmp_data/"
fp = fdir + "QC_DAT_asicdac_Res" + ".bin"
with open(fp, 'wb') as fn:
    pickle.dump(data, fn)

