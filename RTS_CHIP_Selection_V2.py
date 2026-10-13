import sys 
import os
import subprocess
import time 
import random
import pickle
import numpy as np


from colorama import just_fix_windows_console
just_fix_windows_console()

####### Input test information #######
#Red = '\033[91m'
#Green = '\033[92m'
#Blue = '\033[94m'
#Cyan = '\033[96m'
#White = '\033[97m'
#Yellow = '\033[93m'
#Magenta = '\033[95m'
#Grey = '\033[90m'
#Black = '\033[90m'
#Default = '\033[99m'

#start robot
from RTS_CFG import RTS_CFG
sys.path.append('./SN_recognition/')  
from SN_CLASS import SN_CLASS
from SN_chip_CPM_scan import ocr_chip
import datetime

global TRAY_N 
TRAY_N = 90
global PASS_TRAY_SPOT 
PASS_TRAY_SPOT = 7 

global  trayno
trayno =2 # tray with chips to be tested
global  pass_trayno
pass_trayno =1 #


def RTS_debug (info,  status=None, trayno=None, trayc=None, trayr=None, sinkno=None, sktn=None):
    while True:
        print ("444-> Shutdown RTS and exit anyway")
        print ("6->fixed,")

        userinput = input ("Please contatc tech coordinator : ")
        if len(userinput) > 0:
            if "444" in userinput :
                rts.MotorOn()
                rts.JumpToCamera()
                rts.rts_shutdown()
                print ("Exit anyway")
                exit()
            elif "6" in userinput[0] :
                input ("Make sure the chip back to orginal position and click anykey")
                if "OCR" not in info:
                    rts.MotorOn()
                break


import csv
def get_ocr_sn_list(csv_file):
    """
    Return all values from Column L (OCR_SN),
    excluding Row 1/header and blank cells
    """

    with open(csv_file, "r", newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        next(reader, None)  # Skip Row 1: header

        return [
            row[11].strip()
            for row in reader
            if len(row) >= 12 and row[11].strip()
        ]


def Tray_SCAN_Selection(rootdir,csv_fp):
    ocr_sn_list = get_ocr_sn_list(csv_file=csv_fp)

    ocrbin_fp = rootdir + "ocr_results.bin"
    passocrbin_fp = rootdir + "pass_ocr_results.bin"
    if os.path.isfile(ocrbin_fp) :
        with open(ocrbin_fp, 'rb') as fn:
            chip_ocr  = pickle.load(fn)
    else:
        rts.PumpOn()
        time.sleep(5)
        rts.PumpOff()
        print ("Wait a few minutes until the scanning is done")
        rts.ScanTray_Lar(rootdir=rootdir)
        rts.JumpToCamera()
        sn=SN_CLASS()
        chip_ocr = sn.chip_ocr(rootdir)

#    passchips = {} 
#    for key in list(chip_ocr.keys()):
#        if chip_ocr[key][0] :
#            chip_SN = chip_ocr[key][1]
#            chip_SN_r = chip_SN.replace('-', '_')
#            if chip_SN_r in ocr_sn_list:
#                passchips[key]= chip_ocr[key]    
#                print (passchips[key])
#
#    with open(passocrbin_fp, 'wb') as fn:
#        pickle.dump(passchips, fn)
#
#    exit()

    bad_chip_ds = {} 
    for key in list(chip_ocr.keys()):
        if (not chip_ocr[key][0]) and (len(chip_ocr[key]) == 8) :
            bad_chip_ds[key]= chip_ocr[key]    

    if len(bad_chip_ds) > 0:
        sys.path.append('./SN_recognition/')  
        from pyqt import ocr_correct_gui
        chip_ds = ocr_correct_gui(bad_chip_ds)
        chip_ocr.update(chip_ds)
        for key in chip_ds.keys():
            print (key, chip_ocr[key])
        with open(ocrbin_fp, 'wb') as fn:
            pickle.dump(chip_ocr, fn)


    badchips = {} 
    for key in list(chip_ocr.keys()):
        if not chip_ocr[key][0] :
            badchips[key]= chip_ocr[key]    

    passchips = {} 
    for key in list(chip_ocr.keys()):
        if chip_ocr[key][0] :
            chip_SN = chip_ocr[key][1]
            chip_SN_r = chip_SN.replace('-', '_')
            if chip_SN_r in ocr_sn_list:
                passchips[key]= chip_ocr[key]    

#    BAD_TRAY_SPOT = 1
    print ("PASS:", len(passchips))
    global PASS_TRAY_SPOT, trayno
    for key in list(passchips.keys()):
        if passchips[key][0] :
            tray_slot = key
            trayc = (tray_slot-1)%15 + 1
            trayr = (tray_slot-1)//15 + 1
            while True:
                pass_trayc = (PASS_TRAY_SPOT-1)%15 + 1
                pass_trayr = (PASS_TRAY_SPOT-1)//15 + 1
                status = rts.MoveChipFromTrayToTray(trayno, trayc, trayr, pass_trayno, pass_trayc,pass_trayr)    
                if status > 0 :
                    PASS_TRAY_SPOT += 1
                    if PASS_TRAY_SPOT > 90:
                        rts.JumpToCamera()
                        input ("Tray is full, put a new tray!")
                        yorn = input ("confirmed(y/n)!")
                        if 'y' in yorn or 'Y' in yorn:
                            PASS_TRAY_SPOT = 1
                    break
                else:
                    del passchips[key]
    with open(passocrbin_fp, 'wb') as fn:
        pickle.dump(passchips, fn)
    print ('PASS_TRAY_SPOT = ', PASS_TRAY_SPOT)
    print ('Update ....')
   

############################################################


rdir = 'C:/SGAO/ColdTest/Tested/QC_PASS'
csv_fp = '/'.join([rdir,'qc_results_1_J_blank_0928_decoded_ocr.csv'])

ocrsub = "QC_PASS_" + input ("any number TXXXX: ")
rootdir = '/'.join([rdir, ocrsub]) + "/"

if not os.path.exists(rootdir):
    try:
        os.makedirs(rootdir)
    except OSError:
        print ("Error to create folder %s"%rootdir)
        sys.exit()
else:
    print ("folder %s exist, please make sure the tray ID is unique"%rootdir)
        
rts = RTS_CFG()

rts.msg = "10000000000"
rts.rts_init(port=2001, host_ip='192.168.0.2')
rts.RootDirSet(rootdir=rootdir)
rts.MotorOn()
#rts.JumpToCamera()
Tray_SCAN_Selection(rootdir=rootdir, csv_fp=csv_fp)

rts.rts_shutdown()
