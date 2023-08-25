from wib_cfgs import WIB_CFGS
import time
import sys
import numpy as np


chk = WIB_CFGS()
####################WIB init################################
#check if WIB is in position
chk.wib_fw()
time.sleep(1)

i = 0
#chk.wib_cali_dac(dacvol=1.5)
while True:
    i = i + 1
    chk.wib_cali_dac(dacvol=(i%200)*0.01)
    chk.wib_mon_switches(dac0_sel=1, mon_vs_pulse_sel=1, inj_cal_pulse=i%2)
    time.sleep(0.001)
    


