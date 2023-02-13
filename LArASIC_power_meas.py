from wib_cfgs import WIB_CFGS
import time
import sys
import numpy as np
import pickle
import copy
import time, datetime, random, statistics    
    
chk = WIB_CFGS()
 

print("FE INA226")
fe_name = ["FE1", "FE2", "FE3", "FE4", "FE5", "FE6", "FE7", "FE8"]
addrs = [0x40, 0x41, 0x42]
pwrrails = ["VDD", "VDDO", "VPPP"]
V_LSB = 1.25e-3
I_LSB = 0.01e-3 #amps
R = 0.1 #ohms
#cal = 0.00512/(I_LSB*R)
#print("cal is",hex(int(cal)))
for fe in range(8):
    for i in range(3):
        addr = addrs[i]
        bus_voltage = chk.datpower_getvoltage(addr, fe=fe)
        current = chk.datpower_getcurrent(addr, fe=fe)
        print (fe_name[fe], pwrrails[i], "Voltage =\t", bus_voltage, "V") 
        print (fe_name[fe], pwrrails[i], "Current =\t", current*1e+3, "mA")
        print (fe_name[fe], pwrrails[i], "Power =\t", bus_voltage*current*1e+3, "mW")
    print("")


