import pickle
from quick_checkout import GenReport

fp1 = '../data/FEMB0_0pF/Raw_SE_200mVBL_14_0mVfC_2_0us_0x20.bin'
with open(fp1, 'rb') as fn:
    raw = pickle.load(fn)

fp2 = '../data/FEMB0_0pF/Mon_200mVBL_14_0mVfC.bin'
with open(fp2, 'rb') as fn:
    mon = pickle.load(fn)

fp3 = '../data/FEMB0_0pF/logs_env.bin'
with open(fp3, 'rb') as fn:
    logs = pickle.load(fn)


fembNo={}
fembNo['femb0']=0

rawdata = raw[0]
pwr_meas = raw[1]

mon_refs = mon[0]
mon_temps = mon[1]
mon_adcs = mon[2]

PLOTDIR={}
PLOTDIR['femb0'] = "../data/FEMB0_0pF/plots/"

nchips=[0,4]
GenReport(fembNo, rawdata, pwr_meas, mon_refs, mon_temps, mon_adcs, logs, PLOTDIR, nchips)

