from wib_cfgs import WIB_CFGS
import time
import sys
import numpy as np
import pickle
import copy
import time, datetime


wibno = input ("please input WIB slot number (1-6):")
chk = WIB_CFGS()
ts = datetime.datetime.now().strftime("%d_%m_%Y_%H_%M_%S")

fdir = "./wiec_data/"
fp = fdir + "WIB%s_Temperature_"%wibno + ts  + ".bin"
fn = open(fp, 'wb') 

try:
    while True:
        curts = datetime.datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
        print ("WIB temperature is measured at  %s"%curts)
        pwr_meas = chk.get_sensors()
        tsns = time.time_ns()
        pickle.dump({tsns:pwr_meas}, fn)
except KeyboardInterrupt:
    print ("\nKeyboardInterrupt detected. Exiting gracefully.")

fn.close()

print ("Done")

