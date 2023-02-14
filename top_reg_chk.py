from wib_cfgs import WIB_CFGS
import time
import sys
import numpy as np
import pickle
import copy
import time, datetime, random, statistics

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
    sys.argv.remove('save')
else:
    save = False
    sample_N = 1

fembs = [int(a) for a in sys.argv[1:pos]] 

chk = WIB_CFGS()

####################WIB init################################
#check if WIB is in position
chk.wib_fw()
time.sleep(1)

####################FEMBs Configuration################################
#step 1
#reset all FEMBs on WIB
chk.wib_femb_link_en(fembs)

chk.femb_cd_rst()

cfg_paras_rec = []
for femb_id in fembs:
    chk.femb_cd_chk( femb_id) 

print ("Done")


