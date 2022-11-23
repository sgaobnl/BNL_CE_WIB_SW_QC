from wib_cfgs import WIB_CFGS
import time
import sys

print ("this script ONLY runs once after power cycle or reboot!")
ynstr = input ("Do you want to run this scrit (y/n)?: ")

if ("Y" in ynstr) or ("y" in ynstr):
    chk = WIB_CFGS()
    chk.wib_rst_tp()
    chk.wib_i2c_adj(n=300)
    chk.wib_fw()
    chk.wib_timing(pll=True, fp1_ptc0_sel=0, cmd_stamp_sync = 0x0)
    print ("Done")
else:
    print ("Exit")

