from wib_cfgs import WIB_CFGS

import time
import sys
import numpy as np
import pickle
import copy
import time, datetime, random, statistics


chk = WIB_CFGS()

chk.wib_fw()
####################FEMBs powering################################
#set FEMB voltages
pwr_meas = chk.get_sensors()
for key in pwr_meas:
    print (key, ":", pwr_meas[key])
#print (pwr_meas)

#fdir = "D:/debug_data/"
#ts = datetime.datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
#fp = fdir + "Power_" + ts  + ".bin"
#with open(fp, 'wb') as fn:
#    pickle.dump(pwr_meas, fn)
#
print ("Done")

