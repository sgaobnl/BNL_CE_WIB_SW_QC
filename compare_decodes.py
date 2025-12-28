import sys 
import numpy as np
import pickle
import time, datetime, random, statistics
import matplotlib.pyplot as plt
import copy

#decoding methods to compare:
import spymemory_decode, dunedaq_decode 

fp = sys.argv[1]
sfn = fp.split("/") #default
if "/" in fp:
    sfn = fp.split("/")
elif "\\" in fp:
    sfn = fp.split("\\")
p = fp.find(sfn[-1])
fdir = fp[0:p]

with open(fp, 'rb') as fn:
    raw = pickle.load(fn)
    
rawdata = raw[0]
pwr_meas = raw[1]
runi = 0
fembs = [0]

###SPYMEMORY_DECODE (Python)
start_time = time.time() 
wibdata_spy = spymemory_decode.wib_dec(rawdata,fembs, spy_num=1)



end_time = time.time()
elapsed_spy = end_time - start_time
print("spymemory_decode: Done decoding. Total elapsed:",elapsed_spy)
wibdata_spy = wibdata_spy[0]
datd_spy = [wibdata_spy[0], wibdata_spy[1],wibdata_spy[2],wibdata_spy[3]][fembs[0]]
# tmts_spy = wibdata_spy[4]
# cd_tmts_spy = wibdata_spy[5]

##DUNEDAQ_DECODE (C++)
start_time = time.time()     
wibdata_dd = dunedaq_decode.wib_dec(rawdata,fembs, spy_num=1)


end_time = time.time()
elapsed_dd = end_time - start_time
print("dunedaq_decode: Done decoding. Total elapsed:",elapsed_dd)
wibdata_dd = wibdata_dd[0]
datd_dd = [wibdata_dd[0], wibdata_dd[1],wibdata_dd[2],wibdata_dd[3]][fembs[0]]
# tmts_dd = wibdata_dd[4]
# cd_tmts_dd = wibdata_dd[5]

##COMPARE DATA & PLOT
fig = plt.figure()
dd_ax = plt.subplot(2,1,1)
spy_ax = plt.subplot(2,1,2)
for fe in range(8):
    for fe_chn in range(16):
        fechndata_spy = datd_spy[fe*16+fe_chn]
        fechndata_dd = datd_dd[fe*16+fe_chn]
        
        if not all(x == y for x, y in zip(fechndata_spy, fechndata_dd)): #if they don't perfectly match
            print ("Mismatch ch",fe*16+fe_chn)
            print("spy:",[hex(s) for s in fechndata_spy])
            print("dunedaq:",[hex(d) for d in fechndata_dd])
        
        if fe*16+fe_chn < 64:
            c = 'r'
        else:
            c = 'b'                       
        dd_ax.plot(fechndata_spy, color=c)
        spy_ax.plot(fechndata_dd, color=c)
dd_ax.set_title("spymemory_decode (Python)")
spy_ax.set_title("dunedaq_decode (C++)")
fig.suptitle("Waveform comparison for "+fp)
fig.tight_layout()
#plt.show()
plt.savefig(fdir + f"{fembs[0]}_wf_compare.jpg")
plt.close()
print("Data check and graphing done.")


##COMPARE TIMESTAMPS AND PLOT
#visual comparison from plotting is prob adequate since there are <35 frames
try:
    tmts_spy = wibdata_spy[4]
    cd_tmts_spy = wibdata_spy[5]

    tmts_dd = wibdata_dd[4]
    cd_tmts_dd = wibdata_dd[5]
except Excpetion as e:
    print("wib_dec does not currently return tmts and cd_tmts. Replace t0max with tmts and add cd_tmts at the end of wib_dec in both files if you would like to compare timestamps.")
    exit()

#timestamp plotting test for FEMB 0
fig = plt.figure(figsize=(10,6))
mast_ax = plt.subplot(2,1,1)
cd_ax = plt.subplot(2,1,2)
x_tmts = np.arange(len(tmts_spy[0]))
x_tmts2 = np.arange(len(tmts_dd[0])//64)

#[0::64] = the first element out of every 64 elements (dunedaq data is currently interpolated)

#note that the baseline initial timestamp value subtracted from the array is ..._spy[0][0] for all

#master timestamp
mast_ax.plot(x_tmts, np.array(tmts_spy[0], dtype=np.int64)-tmts_spy[0][0], label ="Master Timestamp 0 Python", c='b')
mast_ax.plot(x_tmts, np.array(tmts_spy[0], dtype=np.int64)-tmts_spy[0][0], label ="Master Timestamp 1 Python", c='b')
mast_ax.plot(x_tmts2, np.array(tmts_dd[0][0::64], dtype=np.int64)-tmts_spy[0][0], label ="Master Timestamp 0 C++", c='r')
mast_ax.plot(x_tmts2, np.array(tmts_dd[0][0::64], dtype=np.int64)-tmts_spy[0][0], label ="Master Timestamp 1 C++", c='r')
mast_ax.legend()
mast_ax.set_title("Master Timestamps")
#cd timestamp

cd_ax.plot(x_tmts, np.array(cd_tmts_spy[0], dtype=np.int64)-cd_tmts_spy[0][0], label ="Coldata Timestamp CD0 Python", c='b')
cd_ax.plot(x_tmts, np.array(cd_tmts_spy[1], dtype=np.int64)-cd_tmts_spy[0][0], label ="Coldata Timestamp CD1 Python", c='b')
cd_ax.plot(x_tmts2, np.array(cd_tmts_dd[0][0::64], dtype=np.int64)-cd_tmts_spy[0][0], label ="Coldata Timestamp CD0 C++", c='r')
cd_ax.plot(x_tmts2, np.array(cd_tmts_dd[1][0::64], dtype=np.int64)-cd_tmts_spy[0][0], label ="Coldata Timestamp CD1 C++", c='r')
cd_ax.legend()
cd_ax.set_title("COLDATA Timestamps")

fig.suptitle("Timestamp comparison for "+fp)
fig.tight_layout()
plt.legend()
# plt.show()
plt.savefig(fdir + "timestamp_compare.jpg")
plt.close()