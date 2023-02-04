import pickle
import numpy as np
import matplotlib.pyplot as plt
#from quick_checkout import GenReport
from tools import ana_tools

fp1 = '../data/femb2_RT_0pF/Raw_SE_200mVBL_14_0mVfC_2_0us_0x20.bin'
with open(fp1, 'rb') as fn:
    raw = pickle.load(fn)

fp2 = '../data/femb2_RT_0pF/Mon_200mVBL_14_0mVfC.bin'
with open(fp2, 'rb') as fn:
    mon = pickle.load(fn)

fp3 = '../data/femb2_RT_0pF/logs_env.bin'
with open(fp3, 'rb') as fn:
    logs = pickle.load(fn)


fembNo={}
#fembNo['femb0']=0
#fembNo['femb1']=1
fembNo['femb2']=2
#fembNo['femb3']=3

rawdata = raw[0]
pwr_meas = raw[1]

mon_refs = mon[0]
mon_temps = mon[1]
mon_adcs = mon[2]

PLOTDIR={}
#PLOTDIR['femb0'] = "reports/"
#PLOTDIR['femb1'] = "reports/"
PLOTDIR['femb2'] = "reports/"
#PLOTDIR['femb3'] = "reports/"

nchips=[0,2]
#GenReport(fembNo, rawdata, pwr_meas, mon_refs, mon_temps, mon_adcs, logs, PLOTDIR, nchips)

######## analyze individual channels #########
femb_list=[2]

qc_tools = ana_tools()
pldata = qc_tools.data_decode(rawdata, femb_list)
pldata = np.array(pldata)

qc_tools.data_ana(pldata, 2)

data_ch43 = pldata[:,2*128+43]
data_ch43 = data_ch43.reshape(-1)

data_ch42 = pldata[:,2*128+42]
data_ch42 = data_ch42.reshape(-1)

xx=range(len(data_ch43))
plt.plot(xx,data_ch43,label='ch43')
plt.plot(xx,data_ch42,label='ch42')
plt.legend()
plt.show()


