from wib_cfgs import WIB_CFGS
import sys

chk = WIB_CFGS()
chk.wib_i2c_adj(n=int(sys.argv[1]))
print ("Done")

