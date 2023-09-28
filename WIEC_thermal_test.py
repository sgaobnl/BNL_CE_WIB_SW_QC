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
        pwr_meas["ZYNQ_MON"] = chk.wib_zynq_mon()
#        print (pwr_meas['LTC4644_BRD0_temp']*1.299/1.25)
#        print (pwr_meas['LTC4644_BRD1_temp']*1.299/1.25)
#        print (pwr_meas['LTC4644_BRD2_temp']*1.299/1.25)
#        print (pwr_meas['LTC4644_BRD3_temp']*1.299/1.25)
#        print (pwr_meas['LTC4644_WIB1_temp']*1.299/1.25)
#        print (pwr_meas['LTC4644_WIB2_temp']*1.299/1.25)
#        print (pwr_meas['LTC4644_WIB3_temp']*1.299/1.25)


        print ("LTC4644_WIB1_temp", (1.543-pwr_meas["LTC4644_WIB1_temp"])/0.0033 - 273)
        print ("LTC4644_WIB2_temp", (1.543-pwr_meas["LTC4644_WIB2_temp"])/0.0033 - 273)
        print ("LTC4644_WIB3_temp", (1.543-pwr_meas["LTC4644_WIB3_temp"])/0.0033 - 273)
        print ("LTC4644_BRD0_temp", (1.543-pwr_meas["LTC4644_BRD0_temp"])/0.0033 - 273)
        print ("LTC4644_BRD1_temp", (1.543-pwr_meas["LTC4644_BRD1_temp"])/0.0033 - 273)
        print ("LTC4644_BRD2_temp", (1.543-pwr_meas["LTC4644_BRD2_temp"])/0.0033 - 273)
        print ("LTC4644_BRD3_temp", (1.543-pwr_meas["LTC4644_BRD3_temp"])/0.0033 - 273)
        print ("ZYNQ_MON         ", pwr_meas["ZYNQ_MON"][0])

#        print ((1.2-pwr_meas['LTC4644_BRD0_temp']*1.299/1.25)/0.002 - 273 )
#        print ((1.2-pwr_meas['LTC4644_BRD1_temp']*1.299/1.25)/0.002 - 273 )
#        print ((1.2-pwr_meas['LTC4644_BRD2_temp']*1.299/1.25)/0.002 - 273 )
#        print ((1.2-pwr_meas['LTC4644_BRD3_temp']*1.299/1.25)/0.002 - 273 )
#        print ((1.2-pwr_meas['LTC4644_WIB1_temp']*1.299/1.25)/0.002 - 273 )
#        print ((1.2-pwr_meas['LTC4644_WIB2_temp']*1.299/1.25)/0.002 - 273 )
#        print ((1.2-pwr_meas['LTC4644_WIB3_temp']*1.299/1.25)/0.002 - 273 )
        tsns = time.time_ns()
        pickle.dump({tsns:pwr_meas}, fn)
        #input()
except KeyboardInterrupt:
    print ("\nKeyboardInterrupt detected. Exiting gracefully.")

fn.close()

print ("Done")

