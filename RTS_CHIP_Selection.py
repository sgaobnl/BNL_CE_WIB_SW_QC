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
global BAD_TRAY_SPOT 
BAD_TRAY_SPOT = 14

global  trayno
trayno =2 # tray with chips to be tested
global bad_trayno
bad_trayno =1 # tray with bad chips


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

def FindSpotOnBadTray():
    global BAD_TRAY_SPOT, TRAY_N, bad_trayno
    while True:
        if BAD_TRAY_SPOT >= TRAY_N:
            print ("\033[91m !WARNING! Tray#1 (bac chips) is full: \033[0m")
            yorn = input ("\033[91m Replace with a new tray? (y/Y): \033[0m")
            if "Y" in yorn or "y" in yorn:
                BAD_TRAY_SPOT = 1
        bad_trayc = (BAD_TRAY_SPOT-1)%15 + 1
        bad_trayr = (BAD_TRAY_SPOT-1)//15 + 1
        flg = rts.isChipInTray(bad_trayno,bad_trayc, bad_trayr)
        if not flg:#no chip in it
            break
        else:
            BAD_TRAY_SPOT += 1


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

    for key in list(chip_ocr.keys()):
        if chip_ocr[key][0] :
            chip_SN = chip_ocr[key][1]
            chip_SN_r = chip_SN.replace('-', '_')
            if chip_SN_r not in ocr_sn_list:
                chip_ocr[key][0] = False    
                badchips[key]= chip_ocr[key]    
                print ("Fail", badchips[key] ) 

#    BAD_TRAY_SPOT = 1
    global BAD_TRAY_SPOT
    for key in list(chip_ocr.keys()):
        if not chip_ocr[key][0] :
            tray_slot = key
            trayc = (tray_slot-1)%15 + 1
            trayr = (tray_slot-1)//15 + 1
            while True:
                bad_trayc = (BAD_TRAY_SPOT-1)%15 + 1
                bad_trayr = (BAD_TRAY_SPOT-1)//15 + 1
                status = rts.MoveChipFromTrayToTray(trayno, trayc, trayr, bad_trayno, bad_trayc,bad_trayr)    
                if status > 0 :
                    chip_ocr[key] = chip_ocr[key] + ["Failed_QC_Selection"] + [f'Moved_to_bad_tray_slot_{BAD_TRAY_SPOT}']
                    print (chip_ocr[key])
                    with open(ocrbin_fp, 'wb') as fn:
                        pickle.dump(chip_ocr, fn)
                    BAD_TRAY_SPOT += 1
                    break
                else:
#                    RTS_debug ("T2T", status )
                    BAD_TRAY_SPOT += 1
    
    return chip_ocr, ocrbin_fp 


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
chip_ocr, ocrbin_fp = Tray_SCAN_Selection(rootdir=rootdir, csv_fp=csv_fp)

rts.rts_shutdown()
