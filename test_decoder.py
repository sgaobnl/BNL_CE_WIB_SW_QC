import pickle
from spymemory_decode import wib_spy_dec_syn

fp1 = 'tmp_data/femb0_femb1_femb2_femb3_RT_0pF/Raw_SE_200mVBL_14_0mVfC_2_0us_0x20.bin'
with open(fp1, 'rb') as fn:
    raw = pickle.load(fn)

rawdata = raw[0]

nevent = len(rawdata)
sss=[]
fembs=[1]

#for i in range(nevent):
for i in range(1):
    data = rawdata[i][0]
    buf_end_addr = rawdata[i][1]
    trigger_rec_ticks = rawdata[i][2]
    if raw[i][3] != 0:
        trigmode = 'HW';
    else:
        trigmode = 'SW';

    buf0 = data[0]
    buf1 = data[1]

    wib_data = wib_spy_dec_syn(buf0, buf1, trigmode, buf_end_addr, trigger_rec_ticks, fembs)
