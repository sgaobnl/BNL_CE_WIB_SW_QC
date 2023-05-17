import pickle
import matplotlib.pyplot as plt
import numpy as np
from QC_tools import ana_tools


fp = "QC_data/femb2687_femb2602_femb2619_LN_150pF/CHK/CHK_SE_900mVBL_14_0mVfC_0_5us_0x10.bin"
nfemb=1
chan=0
fembs=[nfemb]

qc = ana_tools()
with open(fp, 'rb') as fn:
     raw = pickle.load(fn)

rawdata = raw[0]
pwr_meas = raw[1]

pldata,tmst = qc.data_decode(rawdata, fembs)
pldata = np.array(pldata)
tmst = np.array(tmst)

print(len(pldata))
for iev in range(len(pldata)):
    global_chan = nfemb*128+chan
    event0 = pldata[iev][global_chan]
    
    #qc.GetPeaks(pldata, tmst, nfemb, '', '')
    plt.plot(range(len(event0)),event0)
    plt.show()
