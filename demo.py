from wib_cfgs import WIB_CFGS
import time
import sys
import numpy as np
import pickle
import copy
import time, datetime, random, statistics


chk = WIB_CFGS()
reg_read = chk.peek(0xA00C0004)
print (reg_read)

