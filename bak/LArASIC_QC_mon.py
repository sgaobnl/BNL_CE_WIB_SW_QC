import time
import sys
import numpy as np
import pickle
import copy
import time, datetime, random, statistics    
from dat_cfg import DAT_CFGS
                
dat =  DAT_CFGS()
data  = {}
data.update( dat.dat_fe_vbgrs() )
data.update( dat.dat_fe_mons(mon_type=0x01) )
data.update( dat.dat_fe_mons(mon_type=0x02) )
data.update( dat.dat_fe_mons(mon_type=0x04) )
data.update( dat.dat_fe_mons(mon_type=0x08) )
data.update( dat.dat_fe_mons(mon_type=0x10) )

fdir = "./tmp_data/"
fp = fdir + "QC2_mon" + ".bin"
with open(fp, 'wb') as fn:
    pickle.dump(data, fn)

