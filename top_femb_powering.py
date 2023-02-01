from wib_cfgs import WIB_CFGS

import time
import sys
import numpy as np
import pickle
import copy
import time, datetime, random, statistics

print ("Powering FEMB")
print ("help: python chkout_powering on on on on") 

if len(sys.argv) !=5 :
    print('Please specify 4 FEMBs power operation (on or off)')
    exit()    

fembs = []
if 'on' in sys.argv[1]:
    fembs.append(0)
if 'on' in sys.argv[2]:
    fembs.append(1)
if 'on' in sys.argv[3]:
    fembs.append(2)
if 'on' in sys.argv[4]:
    fembs.append(3)

chk = WIB_CFGS()

chk.wib_fw()
####################FEMBs powering################################
#set FEMB voltages
chk.fembs_vol_set(vfe=4.0, vcd=4.0, vadc=4.0)

#power on FEMBs
chk.femb_powering(fembs)

if len(fembs) != 0:
    print (f"Turn FEMB {fembs} on")
    chk.femb_cd_rst()
else:
    print (f"Turn All FEMB off")
#Measure powers on FEMB
time.sleep(2)
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

