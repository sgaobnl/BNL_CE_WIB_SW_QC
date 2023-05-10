from wib_cfgs import WIB_CFGS
import time
import sys
import numpy as np
import pickle
import copy
import time, datetime, random, statistics    
    
chk = WIB_CFGS()
chk.wib_fw()
#step 1
#reset all FEMBs on WIB
fembs=[0]
chk.wib_femb_link_en(fembs)


print("FE INA226")
fe_name = ["FE1", "FE2", "FE3", "FE4", "FE5", "FE6", "FE7", "FE8"]
addrs = [0x40, 0x41, 0x42]
pwrrails = ["VDD", "VDDO", "VPPP"]
V_LSB = 1.25e-3
I_LSB = 0.01e-3 #amps
R = 0.1 #ohms
#cal = 0.00512/(I_LSB*R)
#print("cal is",hex(int(cal)))

def pwr_info():
    fes_pwr_info = {}
    for fe in range(8):
        for i in range(3):
            addr = addrs[i]
            bus_voltage = chk.datpower_getvoltage(addr, fe=fe)
            current = chk.datpower_getcurrent(addr, fe=fe)
            fes_pwr_info[fe_name[fe] + "_" + pwrrails[i]] = [bus_voltage, current*1e+3, bus_voltage*current*1e+3]
    return fes_pwr_info

####################FEMBs Configuration################################
def pwr_femb_cfg(sdc, sdd, snc):
    if (sdc ==1) and (sdd ==1):
        print ("error! sdc and sdd can't be on at the same time")
        exit()
    chk.femb_cd_rst()
    cfg_paras_rec = []
    for femb_id in fembs:
        chk.adcs_paras = [ # c_id, data_fmt(0x89), diff_en(0x84), sdc_en(0x80), vrefp, vrefn, vcmo, vcmi, autocali
                            [0x4, 0x08, 0, sdd, 0xDF, 0x33, 0x89, 0x67, 0],
                            [0x5, 0x08, 0, sdd, 0xDF, 0x33, 0x89, 0x67, 0],
                            [0x6, 0x08, 0, sdd, 0xDF, 0x33, 0x89, 0x67, 0],
                            [0x7, 0x08, 0, sdd, 0xDF, 0x33, 0x89, 0x67, 0],
                            [0x8, 0x08, 0, sdd, 0xDF, 0x33, 0x89, 0x67, 0],
                            [0x9, 0x08, 0, sdd, 0xDF, 0x33, 0x89, 0x67, 0],
                            [0xA, 0x08, 0, sdd, 0xDF, 0x33, 0x89, 0x67, 0],
                            [0xB, 0x08, 0, sdd, 0xDF, 0x33, 0x89, 0x67, 0],
                          ]
        chk.set_fe_board(sts=0, snc=snc,sg0=0, sg1=0, st0=0, st1=0, swdac=0, sdd=sdd, sdc=sdc, dac=0x00 )
        adac_pls_en = 0 #enable LArASIC interal calibraiton pulser
        cfg_paras_rec.append( (femb_id, copy.deepcopy(chk.adcs_paras), copy.deepcopy(chk.regs_int8), adac_pls_en) )
        chk.femb_cfg(femb_id, adac_pls_en )


print ("##############Configuration #1 ############")
fes_pwr_info = pwr_info()
kl = list(fes_pwr_info.keys())
for onekey in kl:
    print (onekey, fes_pwr_info[onekey])

rawData = []
for i in range(6):
    if (i == 0): 
        print ("SE=OFF SEDC=OFF BL=900mV)")
        pwr_femb_cfg(sdc=0, sdd=0, snc=0)   #0: OFF/900, 1: ON/200 
    if (i == 1): 
        print ("SE=ON SEDC=OFF BL=900mV)")
        pwr_femb_cfg(sdc=1, sdd=0, snc=0)
    if (i == 2): 
        print ("SE=OFF SEDC=ON BL=900mV)")
        pwr_femb_cfg(sdc=0, sdd=1, snc=0)
    if (i == 3): 
        print ("SE=OFF SEDC=OFF BL=200mV)")
        pwr_femb_cfg(sdc=0, sdd=0, snc=1)
    if (i == 4): 
        print ("SE=ON SEDC=OFF BL=200mV)")
        pwr_femb_cfg(sdc=1, sdd=0, snc=1)
    if (i == 5): 
        print ("SE=OFF SEDC=ON BL=200mV)")
        pwr_femb_cfg(sdc=0, sdd=1, snc=1)
    fes_pwr_info = pwr_info()
    kl = list(fes_pwr_info.keys())
    for onekey in kl:
        print (onekey, fes_pwr_info[onekey])
    rawData.append(fes_pwr_info);

for d in rawData:
    kl = list(d.keys())
    for onekey in kl:
        print (onekey, d[onekey])


outputFile = "./tmp_data/rawData.bin"
with open(outputFile, 'wb') as f:
    pickle.dump(rawData, f)
