import time
import sys
import numpy as np
import pickle
import copy
import time, datetime, random, statistics
import os
from rawdata_dec import rawdata_dec 

fdir = sys.argv[1] 
runs = int(sys.argv[2])

fps = []
for root, dirs, files in os.walk(fdir):
    break
for fn in files:
    if (".bin") in fn and ( ("sg00_sg10_snc0st01st10" in fn) or ("sg00_sg10_snc0st01st11" in fn) ):
    #if (".bin") in fn and ("sg00_sg10_snc0st01st10" in fn) :
        fps.append (fdir + fn)

for fp in fps:
    print (fp)
    with open(fp, 'rb') as fn:
        rawinfo = pickle.load(fn)
    
    lruns = len(rawinfo[0])
    if lruns < runs:
        runs = lruns
    rawdata = rawdata_dec(raw=rawinfo, runs=runs, plot_show_en = False, plot_fn = fp[0:-4] + ".png", rms_flg=True, chdat_flg=True )
    print (len(rawdata), len(rawdata[0]))
    pwr_meas = rawinfo[1]
    #print (pwr_meas)
    #set_feparas = rawinfo[3]
    #[sts, snc, sg0, sg1, st0, st1, sdf, slk0, slk1] = rawinfo[3]
    
    fp = fp[0:-4] + ".dat" 
    with open(fp, 'wb') as fn:
        pickle.dump(rawdata, fn)

#fp = fp[0:-4] + ".set" 
#with open(fp, 'wb') as fn:
#    pickle.dump(set_feparas, fn)
