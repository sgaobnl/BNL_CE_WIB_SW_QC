import sys
import numpy as np
import copy
import os
import pickle


rootdir = "C:\SGAO\ColdTest\Tested\DAT_LArASIC_QC\B006T0035/"
#rootdir = '''C:\SGAO\ColdTest\Tested\DAT_LArASIC_QC\B006T0011/'''
ocrbin_fp = rootdir + "ocr_results.bin"
if os.path.isfile(ocrbin_fp) :
    with open(ocrbin_fp, 'rb') as fn:
        chip_ocr  = pickle.load(fn)
for key in chip_ocr.keys():
    print (key, chip_ocr[key])
##
##    if key in [17,18,19,20,21,22,23,24]:
#    if key in [16]:
    if key in [85,88]:
        chip_ocr[key] = chip_ocr[key][0:8]
        chip_ocr[key][0] = True 
#        chip_ocr[key][-1] = "Failed_in_QC"
#        chip_ocr[key].append( "Moved_to_bad_tray_slot")
#
#for key in chip_ocr.keys():
#    print (key, chip_ocr[key])
#
ocrbin_fp = rootdir + "ocr_results_2nd.bin"
with open(ocrbin_fp, 'wb') as fn:
    pickle.dump(chip_ocr,fn)
