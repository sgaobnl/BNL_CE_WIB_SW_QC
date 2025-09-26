import sys 
import os
import subprocess
import time 
import random
import pickle
import numpy as np

# Tosend notification email
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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
sys.path.append('./SN_recognition/')  
from SN_CLASS import SN_CLASS
from SN_chip_CPM_scan import ocr_chip

TRAY_N = 90
import datetime

def Tray_SCAN_OCR(rootdir):
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

    badchips = {} 
    for key in list(chip_ocr.keys()):
        if not chip_ocr[key][0] :
            badchips[key]= chip_ocr[key]    
   
    bad_tray_spot = 1
    for key in list(chip_ocr.keys()):
        if not chip_ocr[key][0] :
            if ("Failed" in chip_ocr[key][-2]) and ("Moved" in chip_ocr[key][-1]): #already removed
                continue
            tray_slot = key
            trayc = (tray_slot-1)%15 + 1
            trayr = (tray_slot-1)//15 + 1
            bad_tray_spot = FindSpotOnBadTray(user_email, bad_tray_spot)
            bad_trayc = (bad_tray_spot-1)%15 + 1
            bad_trayr = (bad_tray_spot-1)//15 + 1
            while True:
                status = rts.MoveChipFromTrayToTray(trayno, trayc, trayr, bad_trayno, bad_trayc,bad_trayr)    
                if status > 0 :
                    #print (f'remove {key}, {chip_ocr[key]}')
                    #chip_ocr.pop(key) #remove it from bad chip
                    chip_ocr[key] = chip_ocr[key] + ["Failed_in_OCR"] + [f'Moved_to_bad_tray_slot_{bad_tray_spot}']
                    print (chip_ocr[key])
                    with open(ocrbin_fp, 'wb') as fn:
                        pickle.dump(chip_ocr, fn)
                    bad_tray_spot += 1
                    break
                else:
                    RTS_debug ("T2T", user_email, status )
    
    return bad_tray_spot, chip_ocr, ocrbin_fp 

rootdir = rootdir + trayid + "/"

Tray_SCAN_OCR(rootdir)

