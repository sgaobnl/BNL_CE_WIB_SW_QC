import time
import sys
import numpy as np
import pickle
import copy
import time, datetime


fdir = "./wiec_data/"
fp = fdir + "WIB1_Temperature_25_09_2023_12_54_05.bin"
fn = open(fp, 'rb') 

pwrs = {}
while True:
    try:
        tmp = pickle.load(fn)
        dkeys = list(tmp.keys())
        for key in dkeys:
            pwrs[key] = tmp[key]
    except EOFError:
        break
fn.close()

ts = []
temp_u42=[]
temp_ltc4644_wib1 = []
temp_ltc4644_wib2 = []
temp_ltc4644_wib3 = []
temp_ltc4644_brd0 = []
temp_ltc4644_brd1 = []
temp_ltc4644_brd2 = []
temp_ltc4644_brd3 = []
temp_zynq = []

dkeys = list(pwrs.keys())
dkeys2=sorted(dkeys)

t0 = dkeys2[0]

for key in dkeys2:
    ts.append(key-t0)
    temp_u42.append(pwrs[key]["Temp_U42_0x4d"])
    #temp_ltc4644_wib1.append(pwrs[key]["LTC4644_WIB1_temp"])
    #temp_ltc4644_wib2.append(pwrs[key]["LTC4644_WIB2_temp"])
    #temp_ltc4644_wib3.append(pwrs[key]["LTC4644_WIB3_temp"])
    #temp_ltc4644_brd0.append(pwrs[key]["LTC4644_BRD0_temp"])
    #temp_ltc4644_brd1.append(pwrs[key]["LTC4644_BRD1_temp"])
    #temp_ltc4644_brd2.append(pwrs[key]["LTC4644_BRD2_temp"])
    #temp_ltc4644_brd3.append(pwrs[key]["LTC4644_BRD3_temp"])

    temp_ltc4644_wib1.append((1.543-pwrs[key]["LTC4644_WIB1_temp"])/0.0033 - 273)
    temp_ltc4644_wib2.append((1.543-pwrs[key]["LTC4644_WIB2_temp"])/0.0033 - 273)
    temp_ltc4644_wib3.append((1.543-pwrs[key]["LTC4644_WIB3_temp"])/0.0033 - 273)
    temp_ltc4644_brd0.append((1.543-pwrs[key]["LTC4644_BRD0_temp"])/0.0033 - 273)
    temp_ltc4644_brd1.append((1.543-pwrs[key]["LTC4644_BRD1_temp"])/0.0033 - 273)
    temp_ltc4644_brd2.append((1.543-pwrs[key]["LTC4644_BRD2_temp"])/0.0033 - 273)
    temp_ltc4644_brd3.append((1.543-pwrs[key]["LTC4644_BRD3_temp"])/0.0033 - 273)
    temp_zynq.append(pwrs[key]["ZYNQ_MON"][0])

print (np.mean(temp_u42))
print (np.mean(temp_ltc4644_brd0))
print (np.mean(temp_ltc4644_brd1))
print (np.mean(temp_ltc4644_brd2))
print (np.mean(temp_ltc4644_brd3))


print ("Done")

