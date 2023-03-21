import pickle
import matplotlib.pyplot as plt
import numpy as np
from QC_tools import ana_tools


fp = "D:/lke_1826_1E/QC/QC_data/femb0067_femb0029_femb0048_femb0054_RT_150pF/CALI3/CALI3_SE_200mVBL_14_0mVfC_2_0us_0x0e_sgp1.bin"
nfemb=3
chan=1
fembs=[nfemb]

qc = ana_tools()
with open(fp, 'rb') as fn:
     raw = pickle.load(fn)

rawdata = raw[0]
pwr_meas = raw[1]

pldata,tmst = qc.data_decode(rawdata, fembs)
pldata = np.array(pldata)
tmst = np.array(tmst)

global_chan = nfemb*128+chan
event0 = pldata[0][global_chan]

#qc.GetPeaks(pldata, tmst, nfemb, '', '')
plt.plot(range(len(event0)),event0)
plt.show()
