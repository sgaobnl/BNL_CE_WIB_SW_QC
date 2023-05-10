from wib_cfgs import WIB_CFGS
import time
import sys
import numpy as np
import pickle
import copy
import time, datetime, random, statistics    
    
chk = WIB_CFGS()
 

#print("FE INA226")
#fe_name = ["FE1", "FE2", "FE3", "FE4", "FE5", "FE6", "FE7", "FE8"]
#addrs = [0x40, 0x41, 0x42]
#pwrrails = ["VDD", "VDDO", "VPPP"]
#V_LSB = 1.25e-3
#I_LSB = 0.01e-3 #amps
#R = 0.1 #ohms
##cal = 0.00512/(I_LSB*R)
##print("cal is",hex(int(cal)))
#for fe in range(8):
#    for i in range(3):
#        addr = addrs[i]
#        bus_voltage = chk.datpower_getvoltage(addr, fe=fe)
#        current = chk.datpower_getcurrent(addr, fe=fe)
#        print (fe_name[fe], pwrrails[i], "Voltage =\t", bus_voltage, "V") 
#        print (fe_name[fe], pwrrails[i], "Current =\t", current*1e+3, "mA")
#        print (fe_name[fe], pwrrails[i], "Power =\t", bus_voltage*current*1e+3, "mW")
#    print("")

print("CD INA226")
addrs = [0x40, 0x41, 0x43, 0x45, 0x44]
cd_name = ["CD1", "CD2"]
name = ["CD_VDDA", "FE_VDDA", "CD_VDDCORE", "CD_VDDD", "CD_VDDIO"]
V_LSB = 1.25e-3
I_LSB = 0.01e-3 #amps
R = 0.1 #ohms
cal = 0.00512/(I_LSB*R)

cvs = []
for cd in range(2):
    total_pwr_mw = 0
    for i in range(5):    
        addr = addrs[i]
        
        bus_voltage = chk.datpower_getvoltage(addr, cd=cd)
        current = chk.datpower_getcurrent(addr, cd=cd)
        total_pwr_mw = total_pwr_mw + bus_voltage*current*1e+3
        cvs.append( [bus_voltage, current])
        

#        print (cd_name[cd], name[i], "Voltage =\t", bus_voltage, "V") #0x40 nominal vals: 1.19 V
#        print (cd_name[cd], name[i], "Current =\t", current*1e+3, "mA")# print("Current I (mA)=",  current*1e+3, "mA", hex(current_reg))                  #9.2 mA
#        print (cd_name[cd], name[i], "Power =\t", bus_voltage*current*1e+3, "mW")                         #11 mW
#    print (cd_name[cd], "Total Power =\t", total_pwr_mw)
#    print("")

print("FE/ADC INA226")
fe_name = ["FE1", "FE2", "FE3", "FE4", "FE5", "FE6", "FE7", "FE8"]
addrs = [0x40, 0x41, 0x42, 0x43, 0x45, 0x46, 0x44]
name = ["VDD", "VDDO", "VPPP", "VDDA2P5", "VDDD2P5", "VDDIO", "VDDD1P2"]
V_LSB = 1.25e-3
I_LSB = 0.01e-3 #amps
R = 0.1 #ohms
cal = 0.00512/(I_LSB*R)
print("cal is",hex(int(cal)))
for fe in range(8):
# for cd in range(1):
    total_pwr_mw = 0
    for i in range(7):
    #addr = 0x40
        addr = addrs[i]


        bus_voltage = chk.datpower_getvoltage(addr, fe=fe)
        current = chk.datpower_getcurrent(addr, fe=fe)
        total_pwr_mw = total_pwr_mw + bus_voltage*current*1e+3

        cvs.append( [bus_voltage, current])
#        print (fe_name[fe], name[i], "Voltage =\t", bus_voltage, "V") #0x40 nominal vals: 1.19 V
#        print (fe_name[fe], name[i], "Current =\t", current*1e+3, "mA")# print("Current I (mA)=",  current*1e+3, "mA", hex(current_reg))                  #9.2 mA
#        print (fe_name[fe], name[i], "Power =\t", bus_voltage*current*1e+3, "mW")
#    print (fe_name[fe], "Total Power =\t", total_pwr_mw, "mW")
#    print("")


fcsv = "/home/root/BNL_CE_WIB_SW_QC/power.csv"
with open(fcsv, 'w+') as fp:
    for cv in cvs:
        fp.write(",".join(str(i) for i in cv) + "," + "\n")

