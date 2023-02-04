from wib_cfgs import WIB_CFGS
import time
import sys

print ("this script ONLY runs once after power cycle or reboot!")
ynstr = input ("Do you want to run this scrit (y/n)?: ")

if ("Y" in ynstr) or ("y" in ynstr):
    chk = WIB_CFGS()
    chk.wib_fw()
    chk.wib_rst_tp()
    time.sleep(1)
    chk.wib_timing(ts_clk_sel=True, fp1_ptc0_sel=0, cmd_stamp_sync = 0x0)
    time.sleep(1)
    if len(sys.argv) > 2: 
        if "PTC"in sys.argv[2]:
            time.sleep(1)
            chk.wib_timing(ts_clk_sel=False, fp1_ptc0_sel=0, cmd_stamp_sync = 0x0)
        elif "FP"in sys.argv[2]:#timing from front-panel
            time.sleep(1)
            chk.wib_timing(ts_clk_sel=False, fp1_ptc0_sel=1, cmd_stamp_sync = 0x0)
        chk.wib_i2c_adj(n = int(sys.argv[1]))
    else:
        print ("EFMB I2C phase adjustment...")
        chk.wib_i2c_adj(n = 300)
    print ("Done")

else:
    print ("Exit")
