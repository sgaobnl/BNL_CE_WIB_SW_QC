import sys
import numpy as np
import copy
import os
import pickle


rootdir = "C:\SGAO\ColdTest\Tested\DAT_LArASIC_QC\B011T0069/"
#rootdir = '''C:\SGAO\ColdTest\Tested\DAT_LArASIC_QC\B006T0011/'''
ocrbin_fp = rootdir + "ocr_results.bin"
if os.path.isfile(ocrbin_fp) :
    with open(ocrbin_fp, 'rb') as fn:
        chip_ocr  = pickle.load(fn)
for key in chip_ocr.keys():
    print (key, chip_ocr[key])
    if key in [72]:
        chip_ocr[key][0] =  False
        chip_ocr[key].append(  "Failed_in_QC")
        chip_ocr[key].append( "Moved_to_bad_tray_slot")
#    if key in [83,84,85,86,87,88,89,90]:
#        chip_ocr[key][0] = True 
#        chip_ocr[key] = chip_ocr[key][0:8]
##
#    if key in [19,58,59,60,61,78,79,80,81,90]:
##    if key in [16]:
#    if key in [25,26,27,28,29]:
##    if key in [85,88]:
#        chip_ocr[key] = chip_ocr[key][0:8]
#        chip_ocr[key][0] = True 
##        chip_ocr[key][-1] = "Failed_in_QC"
##        chip_ocr[key].append( "Moved_to_bad_tray_slot")
#exit()
##
for key in chip_ocr.keys():
    print (key, chip_ocr[key])
##
ocrbin_fp = rootdir + "ocr_results_2nd.bin"
with open(ocrbin_fp, 'wb') as fn:
    pickle.dump(chip_ocr,fn)
