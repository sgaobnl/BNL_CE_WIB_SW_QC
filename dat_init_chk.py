import time
import sys
import numpy as np
import pickle
import copy
import time, datetime, random, statistics    
from dat_cfg import DAT_CFGS
                
dat =  DAT_CFGS()
dat.wib_pwr_on_dat()
fes_pwr_info = dat.fe_pwr_meas()
adcs_pwr_info = dat.adc_pwr_meas()
cds_pwr_info = dat.cd_pwr_meas()
dat.asic_init_pwrchk(fes_pwr_info, adcs_pwr_info, cds_pwr_info)
dat.dat_asic_chk()

