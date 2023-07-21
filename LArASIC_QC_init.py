from wib_cfgs import WIB_CFGS
import time
import sys
import numpy as np
import pickle
import copy
import time, datetime, random, statistics    

dat_wib_slot = 0
outputFile = "./tmp_data/LArASIC_QC_init.bin"


def fe_adc_pwr_info(asic_list, dat_addrs, pwrrails):
    asics_pwr_info = {}
    for asic in range(8):
        for i in range(len(dat_addrs)):
            addr = addrs[i]
            bus_voltage = chk.datpower_getvoltage(addr, fe=asic)
            current = chk.datpower_getcurrent(addr, fe=asic)
            asics_pwr_info[asic_list[asic] + "_" + pwrrails[i]] = [bus_voltage, current*1e+3, bus_voltage*current*1e+3]
    return asics_pwr_info

chk = WIB_CFGS()
chk.wib_fw()
fembs=[dat_wib_slot]

print ("Turn off all power rails for FEMBs")
#chk.femb_powering([])
time.sleep(1)

#set FEMB voltages
chk.fembs_vol_set(vfe=4.0, vcd=4.0, vadc=4.0)
#power on FEMBs
chk.femb_powering(fembs)
chk.femb_cd_rst()
print ("Wait 10 seconds ...")
#time.sleep(10)

pwr_meas = chk.get_sensors()
for key in pwr_meas:
    if "FEMB%d"%dat_wib_slot in key:
        init_f = False
        print (key, ":", pwr_meas[key])
        if "BIAS_V" in key:
            if pwr_meas[key] < 4.5:
                init_f = True
        if "DC2DC0_V" in key:
            if pwr_meas[key] < 3.5:
                init_f = True
        if "DC2DC1_V" in key:
            if pwr_meas[key] < 3.5:
                init_f = True
        if "DC2DC2_V" in key:
            if pwr_meas[key] < 3.5:
                init_f = True
        if "DC2DC3_V" in key:
            if pwr_meas[key] < 3.5:
                init_f = True

        if "BIAS_I" in key:
            if pwr_meas[key] > 0.1:
                init_f = True
        if "DC2DC0_I" in key:
            if (pwr_meas[key] < 0.2) or (pwr_meas[key] > 0.6) :
                init_f = True
        if "DC2DC1_I" in key:
            if (pwr_meas[key] < 0.2) or (pwr_meas[key] > 0.6) :
                init_f = True
        if "DC2DC2_I" in key:
            if (pwr_meas[key] < 1) or (pwr_meas[key] > 2) :
                init_f = True
        if "DC2DC3_I" in key:
            if pwr_meas[key] > 1:
                init_f = True
        if init_f:
            print ("DAT power consumption @ (power on) is not right, please contact tech coordinator!")
            print ("Turn DAT off, exit anyway!")
            chk.femb_powering([])
            time.sleep(1)
            exit()

chk.wib_femb_link_en(fembs)


print("Power Check for All power rails")
fe_list = ["FE1", "FE2", "FE3", "FE4", "FE5", "FE6", "FE7", "FE8"]
addrs = [0x40, 0x41, 0x42]
pwrrails = ["VDDA", "VDDO", "VPPP"]
V_LSB = 1.25e-3
I_LSB = 0.01e-3 #amps
R = 0.1 #ohms
#cal = 0.00512/(I_LSB*R)
#print("cal is",hex(int(cal)))

fes_pwr_info = fe_adc_pwr_info(asic_list=fe_list, dat_addrs=addrs, pwrrails=pwrrails)
kl = list(fes_pwr_info.keys())
for onekey in kl:
    print (onekey, fes_pwr_info[onekey])


adc_list = ["ADC1", "ADC2", "ADC3", "ADC4", "ADC5", "ADC6", "ADC7", "ADC8"]
addrs = [0x43, 0x44, 0x45, 0x46]
pwrrails = ["VDDA2P5", "VDDD2P5", "VDDIO", "VDDD1P2"]
V_LSB = 1.25e-3
I_LSB = 0.01e-3 #amps
R = 0.1 #ohms
#cal = 0.00512/(I_LSB*R)
#print("cal is",hex(int(cal)))

adcs_pwr_info = fe_adc_pwr_info(asic_list=adc_list, dat_addrs=addrs, pwrrails=pwrrails)
kl = list(adcs_pwr_info.keys())
print (kl)
for onekey in kl:
    print (onekey, adcs_pwr_info[onekey])

print ("Data save in %s"%outputFile)
with open(outputFile, 'wb') as f:
    pickle.dump([pwr_meas, fes_pwr_info], f)
