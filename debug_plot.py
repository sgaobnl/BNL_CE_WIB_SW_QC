import pickle
import matplotlib.pyplot as plt
import numpy as np
from QC_tools import ana_tools


fp = "tmp_data/femb0011_femb0057_femb0036_femb0046_RT_150pF/Raw_SE_900mVBL_14_0mVfC_2_0us_0x10.bin"
nfemb=2
chan=89
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
