import time
import sys
import numpy as np
import pickle
import copy
import time, datetime, random, statistics    
from dat_cfg import DAT_CFGS
                
dat =  DAT_CFGS()
dat.fembs = [0]
dat.femb_cd_rst()

def test():
    dat.cdpoke(0, 0x3, 0, 0x1f,1)
    time.sleep(0.1)
    efusev18 = dat.cdpeek(0, 0x3, 0, 0x18)
    efusev19 = dat.cdpeek(0, 0x3, 0, 0x19)
    efusev1A = dat.cdpeek(0, 0x3, 0, 0x1A)
    efusev1B = dat.cdpeek(0, 0x3, 0, 0x1B)
    print ("Efuse", hex(efusev18 + (efusev19<<8) + (efusev1A<<16) +(efusev1B<<24)))
    dat.cdpoke(0, 0x3, 0, 0x1f,0)

print ("AAAAAAAAAAAAAAAA",0, 0)
dat.femb_cd_rst()
test()

for i in range(1):
    time.sleep(0.1)
    efuseid = int (input("hex number between 0 and 0x7FFFFFFF >> "), 16)
    dat.dat_coldata_efuse_prm(efuseid=efuseid)
    time.sleep(0.1)
    test()


