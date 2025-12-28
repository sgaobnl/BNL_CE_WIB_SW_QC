from wib_cfgs import WIB_CFGS
import time
import sys

print ("this script ONLY runs once after power cycle or reboot!")
#ynstr = input ("Do you want to run this scrit (y/n)?: ")
ynstr = "y"

if ("Y" in ynstr) or ("y" in ynstr):
    chk = WIB_CFGS()
    chk.wib_fw()
    chk.wib_rst_tp()
    time.sleep(1)
    ts_clk_sel=True
    fp1_ptc0_sel=0
    cmd_stamp_sync = 0x0
    chk.wib_timing(ts_clk_sel=ts_clk_sel, fp1_ptc0_sel=fp1_ptc0_sel, cmd_stamp_sync= cmd_stamp_sync)
    # chk.wib_mon_switches()
    time.sleep(1)
    if len(sys.argv) > 2: 
        if "PTC"in sys.argv[2]:
            ts_clk_sel=False
            fp1_ptc0_sel=0
            cmd_stamp_sync = 0x0
            chk.wib_timing(ts_clk_sel=ts_clk_sel, fp1_ptc0_sel=fp1_ptc0_sel, cmd_stamp_sync= cmd_stamp_sync)
            time.sleep(1)
        elif "FP"in sys.argv[2]:#timing from front-panel
            ts_clk_sel=False
            fp1_ptc0_sel=1
            cmd_stamp_sync = 0x0
            chk.wib_timing(ts_clk_sel=ts_clk_sel, fp1_ptc0_sel=fp1_ptc0_sel, cmd_stamp_sync= cmd_stamp_sync)
        chk.wib_i2c_adj(n = int(sys.argv[1]))
    else:
        print ("EFMB I2C phase adjustment...")
        chk.wib_i2c_adj(n = 300)
    print ("Done")
    with open("./timing.cfg", "w") as fp:
        fp.write("%d, %d, %d, 300,"%(int(ts_clk_sel), fp1_ptc0_sel, cmd_stamp_sync))

else:
    print ("Exit")

