from wib_cfgs import WIB_CFGS
import time
import sys
import numpy as np
import pickle
import copy
import time, datetime, random, statistics


chk = WIB_CFGS()
#reg_read = chk.poke(0xA00C0004, 1)
#reg_read = chk.peek(0xA00C0004)
#print (reg_read)
#reg_read = chk.peek(0xA00C0004)
#print (hex(reg_read))
#reg_read = chk.wib_peek(0xA00C0004)
#print (hex(reg_read))
#reg_read = chk.poke(0xA00C0004, 2)
#reg_read = chk.peek(0xA00C0004)
#print (hex(reg_read))
#reg_read = chk.wib_peek(0xA00C0004)
#print (hex(reg_read))
#reg_read = chk.wib_poke(0xA00C0004, 3)
#reg_read = chk.peek(0xA00C0004)
#print (hex(reg_read))
#reg_read = chk.wib_peek(0xA00C0004)
#print (hex(reg_read))
#
##chk.femb_power_en_ctrl(femb_id=2, enable=1)
#chk.femb_power_set(0,1, 2.5, 3.0, 3.5)
#time.sleep(1)
#chk.femb_power_set(1,1, 2.5, 3.0, 3.5)
#time.sleep(1)
#chk.femb_power_set(2,1, 2.5, 3.0, 3.5)
#time.sleep(1)
#chk.femb_power_set(3,1, 2.5, 3.0, 3.5)
#time.sleep(2)


chk.script (fp = "./coldata_power_on")
a = chk.get_sensors()
print (a)
time.sleep(3)

chk.script (fp = "./coldata_power_off")
time.sleep(3)
a = chk.get_sensors()

print (a)

