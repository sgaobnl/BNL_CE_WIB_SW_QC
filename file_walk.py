# -*- coding: utf-8 -*-
import os
import sys

froot = sys.argv[1]

qcfps = {}
for root, dirs, files in os.walk(froot):
    for fn in files: 
        if ".bin" in fn:
            print ('{}:{}:'.format(fn, os.path.join(root,fn)))
print ('ROOT:{}:'.format(froot))
