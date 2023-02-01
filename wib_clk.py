from wib_cfgs import WIB_CFGS
import time
import sys

print ("this script ONLY runs once after power cycle or reboot!")
chk = WIB_CFGS()
chk.wib_fw()
chk.wib_timing(ts_clk_sel=True, fp1_ptc0_sel=0, cmd_stamp_sync = 0x0)

