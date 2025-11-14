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
from RTS_CFG import RTS_CFG
from rts_ssh import DAT_power_off
from rts_ssh import rts_ssh
from set_rootpath import rootdir_cs
from cryo_uart import cryobox
sys.path.append('./SN_recognition/')  
from SN_CLASS import SN_CLASS
from SN_chip_CPM_scan import ocr_chip
from sendemail import sendemail
from User_Input import get_user_input
from init_check import init_chk 

global TRAY_N 
TRAY_N = 90
global BAD_TRAY_SPOT 
BAD_TRAY_SPOT = 1

import datetime
def is_weekday_work_hours():
    now = datetime.datetime.now()  # FIXED
    current_time = now.time()

    is_weekday = 0 <= now.weekday() <= 4
    start_time = datetime.time(8, 00)
    end_time = datetime.time(20, 00)  # FIXED typo

    in_time_range = start_time <= current_time <= end_time
    return is_weekday and in_time_range


def DAT_debug (QCstatus, user_email):
    print (QCstatus)
    sendemail(message="Please contact tech coordinator (DAT issue)", user_email=user_email, inform_tech=True)
    while True:#
        #print ("444-> Move chips back to original positions")
        print ("444-> Shutdown RTS and exit anyway")
        print ("6->fixed,")
        userinput = input ("Please contact tech coordinator : ")
        if len(userinput) > 0:
            if "444" in userinput :
                rts.MotorOn()
                rts.JumpToCamera()
                rts.rts_shutdown()
                print ("Exit anyway")
                exit()
                #return "444"
            elif "6" in userinput :
                yorn = input ("Fixed. Are you sure? (y/Y):")
                if "Y" in yorn or "y" in yorn:
                    return "6"

def RTS_debug (info, user_email, status=None, trayno=None, trayc=None, trayr=None, sinkno=None, sktn=None):
    sendemail(message="Please contact tech coordinator (RTS issue)", user_email=user_email, inform_tech=True)
    print ("Please check the error information on EPSON RC")
    if "T2S" in info:
        print ("Chip is moved from Tray") 
        print ("Chip on orignial TrayNo(1-2)={}, Col(1-15)={}, Row(1-6)={}".format(trayno, trayc, trayr)) 
    elif "S2T" in info:
        print ("Chip is moved from Socket") 
        print ("Chip on orignial Sinkno(1-2)={}, Skt(1-8)={} ".format(sinkno, sktn)) 
    elif "T2T" in info:
        print ("Chip is moved from Tray to Tray") 

    while True:
        print ("444-> Shutdown RTS and exit anyway")
        #print ("1->move chip to Tray#1_Col#15_Row#6")
        #print ("2->move chip to orignal position")
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

def MovetoSoket(sinkno, duts,ids_dict,  skts=[0,1,2,3,4,5,6,7], duttype="FE") :
    print ("DUTtype", duttype)
    dut_skt = {}
    #make sure DAT is powered off
    DAT_power_off()

    rts.MotorOn()
    rts.PumpOn()
    time.sleep(5)
    rts.PumpOff()


    tmpi = 0
    tmpj = 0
    while tmpi < len(skts):
        skt = skts[tmpi]
        if len(duts)>0:
            chipi = duts[0]
            duts=duts[1:]
        else:
            ids_g = list(ids_dict.keys())
            chipi = ids_dict[ids_g[tmpj]][0]
            tmpj=tmpj+1

        if "CD" in duttype:
            trayc=(chipi%10) +1
            trayr=(chipi//10) +1
        else:
            trayc=(chipi%15) +1
            trayr=(chipi//15) +1
        sktn = skt + 1
        
        status = rts.MoveChipFromTrayToSocket(trayno, trayc, trayr, sinkno, sktn,duttype)    

        if status < 0:
            RTS_debug ("T2S",user_email,  status, trayno, trayc, trayr, sinkno, sktn)
            tmpi = tmpi
            duts=[chipi] + duts
            continue
        else:
            dut_skt[rts.msg] = (chipi, skt)
            current_ids = rts.msg

            if "CD" in duttype:
                if len(skts) < 2:
                    chips =2
                else:
                    chips = len(dut_skt)
            else:
                if len(skts) < 8:
                    chips =8
                else:
                    chips = len(dut_skt)

            QCstatus, badchips = DAT_QC(user_email, dut_skt,duttype, LN2_flg=LN2_flg, testid=90+chips)  
            if ("Code#E001" in QCstatus) : #move back to original positions and then move back
                while True: 
                    status = rts.MoveChipFromSocketToTray(sinkno, sktn, trayno, trayc, trayr, duttype)
                    if status < 0:
                        RTS_debug ("S2T", user_email, status, trayno, trayc, trayr, sinkno, sktn)
                        continue
                    else:
                        dut_skt.pop(current_ids, None)  

                    status = rts.MoveChipFromTrayToSocket(trayno, trayc, trayr, sinkno, sktn,duttype)    
                    if status < 0:
                        RTS_debug ("T2S", user_email, status, trayno, trayc, trayr, sinkno, sktn)
                        continue
                    else:
                        dut_skt[rts.msg] = (chipi, skt)
                        current_ids = rts.msg
                        chips = len(dut_skt)
                        break

                QCstatus, badchips = DAT_QC(user_email, dut_skt,duttype, LN2_flg=LN2_flg, testid=90+chips)  
                if ("Code#E001" in QCstatus) : #move back to bad tray 
                    ids = current_ids
                    #ids_bads[ids] = dut_skt[ids]
                    removekey = ids
                    dut_skt.pop(removekey, None)  
                    ids_g = list(dut_skt.keys())
                    while True: 
                        FindSpotOnBadTray(user_email)
                        bad_dut_order = BAD_TRAY_SPOT - 1
                        if "CD" in duttype:
                            trayc=(bad_dut_order%10) +1
                            trayr=(bad_dut_order//10) +1
                        else:
                            trayc=(bad_dut_order%15) +1
                            trayr=(bad_dut_order//15) +1
    
                        status = rts.MoveChipFromSocketToTray(sinkno, sktn, badtrayno, trayc, trayr, duttype)
                        if status < 0:
                            RTS_debug ("S2T", user_email, status, trayno, trayc, trayr, sinkno, sktn)
                            continue
                        else:

                            QCstatus, badchips = DAT_QC(user_email, dut_skt,duttype, LN2_flg=LN2_flg, testid=90+chips)  
                            if ("Code#E001" in QCstatus) : #move back to bad tray 
                                DAT_debug (QCstatus, user_email)
                                break
                    tmpi= tmpi
                    duts= duts #bad chip is removed
                    continue
                else:
                    tmpi = tmpi + 1 
            else:
                tmpi = tmpi + 1
    rts.rts_idle()
    return duts, dut_skt

def DAT_QC(user_email, dut_skt, duttype="FE", LN2_flg = True, testid=0) :
    while True:
        QCresult = rts_ssh(dut_skt, root=rootdir, duttype=duttype, env="RT", testid=testid)
        if QCresult != None:
            QCstatus = QCresult[0]
            if "CD" in duttype:
                badchips =[]
                if (0 in QCresult[1]) or (1 in QCresult[1]) or (2 in QCresult[1]) or (3 in QCresult[1]):
                    badchips.append(0)
                if (4 in QCresult[1]) or (5 in QCresult[1]) or (6 in QCresult[1]) or (7 in QCresult[1]):
                    badchips.append(1)
            else:
                badchips = QCresult[1]
            break
        else:
            print ("139-> terminate, 2->debugging")
            sendemail(message="Please contact tech coordinator (QC error)", user_email=user_email, inform_tech=True)
            userinput = input ("Please contact tech coordinator")
            if len(userinput) > 0:
                if "139" in userinput :
                    QCstatus = "Terminate"
                    badchips = []
                    break
                elif "2" in userinput[0] :
                    print ("debugging, ")
                    input ("click any key to start ASIC QC again...")
    if (len(badchips) > 0) or ("Code#P001" in QCstatus):
        return QCstatus, badchips #badchips range from 0 to7

    if LN2_flg:
        p_shifter=True
        s_shifter=False
        cover_sts = rts.CoverStatus()
        print (cover_sts)
        sendemail(subject = "Please close RTS chamber cover", message="Please close the chamber cover. ", user_email=user_email, p_shifter=p_shifter, s_shifter=s_shifter)
        #yorn = input ("\033[96m Do you want to perform cold test? (Y/N) :\033[0m")
        t0 = int(time.time())
        while True:
            cover_sts = rts.CoverStatus()
            if "-198" in cover_sts:
                print ("Cover is close! Start the cold test in 10 seconds")
                sendemail(subject = "A genius just closed cover", message="Next call is ~ 1 hour later. ", user_email=user_email, p_shifter=p_shifter, s_shifter=s_shifter)
                s_shifter=False
                time.sleep(10)
                break
            else:
                time.sleep(10)
                t1 = int(time.time()) - t0
                if (t1 > 600) :
                    if not is_weekday_work_hours()  :
                        pass
                    else:
                        t0 =time.time() 
                        s_shifter=True
                        sendemail(subject = "Reminder: Please close RTS chamber cover", message="Please close the chamber cover. ", user_email=user_email,  p_shifter=p_shifter, s_shifter=s_shifter)

        try:
            cryo.cryo_fill()
        except KeyboardInterrupt:
            print ("####################")

        cryo.cryo_lowlevel(waitminutes=10)
        cryo.cryo_highlevel(waitminutes=5)

        LNQCresult = rts_ssh(dut_skt, root=rootdir, duttype=duttype, env="LN" )

        cryo.cryo_warmup(waitminutes=30)

        s_shifter=False
        cover_sts = rts.CoverStatus()
        print (cover_sts)
        sendemail(subject = "Please open RTS chamber cover", message="Cold test is done, please open the sink cover", user_email=user_email, p_shifter=p_shifter, s_shifter=s_shifter)

        t0 = int(time.time())
        while True:
            cover_sts = rts.CoverStatus()
            if "197" in cover_sts:
                print ("Cover is open! Activate robot in 10 seconds")
                sendemail(subject = "A genius just opened cover", message="Next call is ~40 minutes later. ", user_email=user_email, p_shifter=p_shifter, s_shifter=s_shifter)
                s_shifter=False
                time.sleep(10)
                break
            else:
                time.sleep(10)
                t1 = int(time.time()) - t0
                if (t1 > 600) :
                    if not is_weekday_work_hours()  :
                        pass
                    else:
                        t0 =time.time() 
                        s_shifter=True
                        sendemail(subject = "Reminder: Please open RTS chamber cover", message="Please open the chamber cover. ", user_email=user_email, p_shifter=p_shifter, s_shifter=s_shifter)


    return QCstatus, badchips #badchips range from 0 to7

################STEP3#################################
def MovetoTray(sinkno, duts, dut_skt, QCstatus, badchips, duttype="FE", LN2_flg=True) :
    global BAD_TRAY_SPOT, TRAY_N, trayno, bad_trayno
    ids_goods = {}
    ids_bads = {}

    ids_g = list(dut_skt.keys())
    DAT_power_off()
    rts.MotorOn()
    rts.PumpOn()
    time.sleep(5)
    rts.PumpOff()


    if "CD" in duttype:
        SKT_N = 2
    else:
        SKT_N = 8

    #if "Terminate" in QCstatus: #move back to original positions
    if ("Terminate" in QCstatus) : #move back to original positions
        rts.rts_idle()
        admincode = DAT_debug (QCstatus, user_email)
        if "2" in admincode:
            QCstatus, badchips = DAT_QC(user_email, dut_skt,duttype, LN2_flg=LN2_flg)  
        elif "444" in admincode:
            RTS_debug ("DAT", user_email )
        rts.MotorOn()
        rts.PumpOn()
        time.sleep(5)
        rts.PumpOff()

            
        tmpi = 0
        while tmpi < SKT_N:
            for ids in ids_g:
                if dut_skt[ids][1] == tmpi:
                    chipi=dut_skt[ids][0]
                    sktn =dut_skt[ids][1] + 1
                    break
            if "CD" in duttype:
                trayc=(chipi%10) +1
                trayr=(chipi//10) +1
            else:
                trayc=(chipi%15) +1
                trayr=(chipi//15) +1
            status = rts.MoveChipFromSocketToTray(sinkno, sktn, trayno, trayc, trayr, duttype)

            if status < 0:
                RTS_debug ("S2T", user_email, status, trayno, trayc, trayr, sinkno, sktn)
                tmpi = tmpi
                continue
            else:
                tmpi = tmpi + 1

        tmps = []
        for ids in ids_g:
            tmps.append(dut_skt[ids][0])
        tmps = sorted(tmps)
        duts = tmps + duts

        return duts, {}, ids_goods, ids_bads
    else:
        if "Code#" in QCstatus:
            tmpi = 0
            while tmpi < len(badchips):
                skt = badchips[tmpi]
                for ids in ids_g:
                    if dut_skt[ids][1] == skt:
                        chipi=dut_skt[ids][0]
                        sktn =dut_skt[ids][1] + 1
                        ids_bads[ids] = dut_skt[ids]
                        removekey = ids
                        dut_skt.pop(removekey, None)  
                        ids_g = list(dut_skt.keys())
                        break
                FindSpotOnBadTray(user_email)
                bad_dut_order = BAD_TRAY_SPOT - 1
                if "CD" in duttype:
                    trayc=(bad_dut_order%10) +1
                    trayr=(bad_dut_order//10) +1
                else:
                    trayc=(bad_dut_order%15) +1
                    trayr=(bad_dut_order//15) +1
                status = rts.MoveChipFromSocketToTray(sinkno, sktn, badtrayno, trayc, trayr, duttype)

                if status < 0:
                    RTS_debug ("S2T", user_email, status, trayno, trayc, trayr, sinkno, sktn)
                    tmpi = tmpi
                    continue
                else:
                    ids_bads[rts.msg] = (chipi, skt)
                    BAD_TRAY_SPOT +=1
                    tmpi = tmpi + 1
            return duts,dut_skt , ids_goods, ids_bads

        if "PASS" in QCstatus:
            tmpi = 0
            while tmpi < SKT_N:
                for ids in ids_g:
                    if dut_skt[ids][1] == tmpi:
                        chipi=dut_skt[ids][0]
                        sktn =dut_skt[ids][1] + 1
                        break
                if "CD" in duttype:
                    trayc=(chipi%10) +1
                    trayr=(chipi//10) +1
                else:
                    trayc=(chipi%15) +1
                    trayr=(chipi//15) +1
                if tmpi in badchips:
                    FindSpotOnBadTray(user_email)
                    bad_dut_order = BAD_TRAY_SPOT - 1
                    if "CD" in duttype:
                        trayc=(bad_dut_order%10) +1
                        trayr=(bad_dut_order//10) +1
                    else:
                        trayc=(bad_dut_order%15) +1
                        trayr=(bad_dut_order//15) +1
                    status = rts.MoveChipFromSocketToTray(sinkno, sktn, badtrayno, trayc, trayr, duttype)
                else:
                    status = rts.MoveChipFromSocketToTray(sinkno, sktn, trayno, trayc, trayr, duttype)

                if status < 0:
                    RTS_debug ("S2T", user_email, status, trayno, trayc, trayr, sinkno, sktn)
                    tmpi = tmpi
                    continue
                else:
                    if tmpi in badchips:
                        skt = tmpi 
                        for ids in ids_g:
                            if dut_skt[ids][1] == skt:
                                ids_bads[ids] = dut_skt[ids]
                                removekey = ids
                                dut_skt.pop(removekey, None)  
                                ids_bads[rts.msg] = (chipi, skt)
                                ids_g = list(dut_skt.keys())
                                break
                        BAD_TRAY_SPOT +=1
                    else:
                        ids_goods[rts.msg] = (chipi,tmpi)
                    tmpi = tmpi + 1

            return duts, dut_skt, ids_goods, ids_bads

def FindSpotOnBadTray(user_email):
    global BAD_TRAY_SPOT, TRAY_N, bad_trayno
    while True:
        if BAD_TRAY_SPOT >= TRAY_N:
            sendemail(message="!WARNING! Tray#1 (bac chips) is full, please replace with a new empty tray. ", user_email=user_email, inform_tech=True)
            print ("\033[91m !WARNING! Tray#1 (bac chips) is full: \033[0m")
            yorn = input ("\033[91m Replace with a new tray? (y/Y): \033[0m")
            if "Y" in yorn or "y" in yorn:
                BAD_TRAY_SPOT = 1
        bad_trayc = (BAD_TRAY_SPOT-1)%15 + 1
        bad_trayr = (BAD_TRAY_SPOT-1)//15 + 1
        flg = rts.isChipInTray(bad_trayno,bad_trayc, bad_trayr)
        if not flg:#no chip in it
            break
        #return BAD_TRAY_SPOT
        else:
            BAD_TRAY_SPOT += 1

def Tray_SCAN_OCR(rootdir):
    global BAD_TRAY_SPOT, TRAY_N, trayno, bad_trayno
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
        sendemail(subject ="Correct OCR Error", message="!WARNING! Please check the pop-up windows to correct OCR error.", user_email=user_email, inform_tech=True)
        chip_ds = ocr_correct_gui(bad_chip_ds)
        chip_ocr.update(chip_ds)
        for key in chip_ds.keys():
            print (key, chip_ocr[key])

    badchips = {} 
    for key in list(chip_ocr.keys()):
        if not chip_ocr[key][0] :
            badchips[key]= chip_ocr[key]    
   
    BAD_TRAY_SPOT = 1
    for key in list(chip_ocr.keys()):
        if not chip_ocr[key][0] :
            if ("Failed" in chip_ocr[key][-2]) and ("Moved" in chip_ocr[key][-1]): #already removed
                continue
            tray_slot = key
            trayc = (tray_slot-1)%15 + 1
            trayr = (tray_slot-1)//15 + 1
            FindSpotOnBadTray(user_email)
            bad_trayc = (BAD_TRAY_SPOT-1)%15 + 1
            bad_trayr = (BAD_TRAY_SPOT-1)//15 + 1
            while True:
                status = rts.MoveChipFromTrayToTray(trayno, trayc, trayr, bad_trayno, bad_trayc,bad_trayr)    
                if status > 0 :
                    #print (f'remove {key}, {chip_ocr[key]}')
                    #chip_ocr.pop(key) #remove it from bad chip
                    chip_ocr[key] = chip_ocr[key] + ["Failed_in_OCR"] + [f'Moved_to_bad_tray_slot_{BAD_TRAY_SPOT}']
                    print (chip_ocr[key])
                    with open(ocrbin_fp, 'wb') as fn:
                        pickle.dump(chip_ocr, fn)
                    BAD_TRAY_SPOT += 1
                    break
                else:
                    RTS_debug ("T2T", user_email, status )
    
    return chip_ocr, ocrbin_fp 

############################################################
rts = RTS_CFG()
cryo = cryobox()

LN2_flg = init_chk()
gui_info = get_user_input()
logs = {}
logs.update(gui_info)

if 'LArASIC' in gui_info['DUTtype'] :
    duttype = "FE"
    rootdir = rootdir_cs(duttype)
    TRAY_N = 90
elif 'ColdADC' in gui_info['DUTtype'] :
    duttype = "ADC"
    rootdir = rootdir_cs(duttype)
    TRAY_N = 90
elif 'COLDATA' in gui_info['DUTtype'] :
    duttype = "CD"
    rootdir = rootdir_cs(duttype)
    TRAY_N = 40
else:
    print ("Wrong DUT type, exit anyway")
    sys.exit()

trayid = gui_info["Tray_ID"]
user_email= gui_info["Email"]
sendemail(subject ="Attention: ASIC QC start...", message="Stay tuned! You may be informed later.", user_email=user_email, inform_tech=True, p_shifter=True, s_shifter=True)

trayno =2 # tray with chips to be tested
bad_trayno =1 # tray with bad chips
badtrayno = 1 #some issue with tray#1
bad_dut_order=0
sinkno =2
rootdir = rootdir + trayid + "/"

logs["TrayID"] = trayid
logs["TrayNo"] = 2
logs["BadTrayNo"] = 1
logs["SinkNo"] = 2
logs["rootdir"] = rootdir

status = 0
ids_dict = {} #good chips ID with time that chips are moved from tray to socket
ids_dict_good = {} #good chips ID with time that chips are moved from socket to tray
ids_dict_bad = {} #good chips ID with time that chips are moved from socket to tray

if not os.path.exists(rootdir):
    try:
        os.makedirs(rootdir)
    except OSError:
        print ("Error to create folder %s"%rootdir)
        sys.exit()
else:
    print ("File exist, please make sure the tray ID is unique")
#    print ("Exit anyway")

############################################################
rts = RTS_CFG()
cryo = cryobox()

rts.msg = "10000000000"
rts.rts_init(port=2001, host_ip='192.168.0.2')
rts.RootDirSet(rootdir=rootdir)
rts.MotorOn()
rts.JumpToCamera()
chip_ocr, ocrbin_fp = Tray_SCAN_OCR(rootdir)
rts.rts_idle()

#rts.MoveChipFromTrayToSocket(2, 8, 2, 2, 8, "FE")    
#rts.MoveChipFromTrayToSocket(2, 1, 1, 2, 1, "ADC")    
##rts.MoveChipFromTrayToSocket(2, 1, 1, 2, 1, "CD")    
#rts.MoveChipFromSocketToTray(2, 1, 2, 1, 1, "CD")
#rts.rts_idle()
##rts.rts_shutdown()
#print ("XXXXXX")
#exit()

duts = []
for key in list(chip_ocr.keys()):
    if  (chip_ocr[key][0]) and (len(chip_ocr[key])==8) and ("PASS" not in chip_ocr[key][-1]):
            duts.append(key-1)

logs["duts"] = duts 
logs["ocr"] = chip_ocr

#first run
################STEP1#################################
if "CD" in duttype:
    skts=[0,1]
else:
    skts=[0,1,2,3,4,5,6,7]
dut_skt = {}

Undone_Flag = False 
while (len(duts) > 0) or Undone_Flag :
#    rts.PumpOn()
#    time.sleep(5)
#    rts.PumpOff()

    duts, dut_skt_n = MovetoSoket(sinkno, duts,ids_dict, skts=skts,duttype=duttype) 
    print ("Remain chips on tray: ", duts)

    for key in list(dut_skt_n.keys()):
        dut_chip_dir = "/".join([rootdir, 'images'])
        dut_chip_fn =  f'{key}_SN.bmp'
        sn_ocr_imgdir = "/".join([rootdir, 'images', 'SN_OCR']) 
        if not os.path.exists(sn_ocr_imgdir):  # Check if the folder already exists
            os.mkdir(sn_ocr_imgdir)

        if os.path.isfile(dut_chip_dir + "/" + dut_chip_fn):
            tray_slot = dut_skt_n[key][0]+1 #start from 1
            ocr_sn = chip_ocr[tray_slot][1]
            ocr_chip_fn =  f'SN_{ocr_sn}_Tray_{tray_slot}_{key}.bmp'.replace("-","_")
            ocr_image_dir = sn_ocr_imgdir + "/" + ocr_chip_fn
            ocr_info = ocr_chip(image_fp = dut_chip_dir, image_fn = dut_chip_fn, ocr_image_dir = ocr_image_dir, degree=180, x=1115, y=785, w=330, h=330, valid_flg=False)
            if ocr_sn not in ocr_info:
            #if False: #bypass the online check now
                print ("Chip to be tested have different SN from the tray scanning!")
                print (f"OCR while scaning tray: {ocr_sn}, OCR while moving to socket: {ocr_info}")
                p_shifter=True
                s_shifter=False
                sendemail(subject = "Chip SN mismatch, come to check pop-up window", message=f"OCR result {ocr_info} doesn't consist Chip SN {ocr_sn}", user_email=user_email, p_shifter=p_shifter, s_shifter=s_shifter)
                from sn_match_gui import run_sn_match_gui
                yorn = run_sn_match_gui(image_path=ocr_image_dir, text=f"Is chip SN {ocr_sn} ?")
                if yorn:
                    pass
                else:
                    RTS_debug ("OCR",user_email)

    dut_skt.update(dut_skt_n)
    print ("Chips to be tested: ", dut_skt)
    #sendemail(message="Chips to be tested: " + ','.join(map(str, dut_skt.values())), user_email=user_email)

    if True:
        QCstatus, badchips = DAT_QC(user_email, dut_skt,duttype, LN2_flg) 
    else:
        QCstatus = "PASS"
        badchips = []
    print (QCstatus, "Badchips:", badchips)


    duts, dut_skt, ids_goods, ids_bads= MovetoTray(sinkno, duts, dut_skt, QCstatus, badchips, duttype=duttype, LN2_flg=LN2_flg) 
    ids_dict_good.update(ids_goods)
    ids_dict_bad.update(ids_bads)

    for key in list(ids_goods.keys()):
        ocr_key = ids_goods[key][0] + 1
        chip_ocr[ocr_key] = chip_ocr[ocr_key] + [f'PASS_QC'] 
    for key in list(ids_bads.keys()):
        ocr_key = ids_bads[key][0] + 1
        chip_ocr[ocr_key] = [False] + chip_ocr[ocr_key][1:] + [f'Failed_in_QC'] + [f'Moved_to_bad_tray_slot_{BAD_TRAY_SPOT}']
    with open(ocrbin_fp, 'wb') as fn:
        pickle.dump(chip_ocr, fn)


    if "PASS" not in QCstatus :
        if len(badchips) > 0:
            skts=badchips
    else: #PASS
        if len(duts) == 0:
            Undone_Flag = True
        ids_dict.update(dut_skt)
        dut_skt = {}
        if "CD" in duttype:
            skts=[0,1]
        else:
            skts=[0,1,2,3,4,5,6,7]

    print ("**********save ID info*************")
    #ids_k = list(dut_skt.keys())
    #if len(ids_k) > 0:
    if True:
        fp = rootdir + datetime.datetime.now().strftime("%m_%d_%Y_%H_%M_%S") + "_log.bin"
        if not os.path.isfile(fp) :
            logs["RTS_MSG_R2S_P"] = dut_skt 
            logs["RTS_MSG_S2R_P"] = ids_goods
            logs["RTS_MSG_S2R_F"] = ids_bads
            with open(fp, 'wb') as fn:
                pickle.dump(logs, fn)

rts.rts_shutdown()

print ("save RTC infomation")
from RTS_record import RTS_MANIP
manip = RTS_MANIP()
manip.manip_fp = "C:/Users/coldelec/RTS/manip.csv"
manip.rootdir = rootdir
rts_r = manip.read_manipfp()
rts_msgs = manip.read_rtsmsgfp()
for rts_msg_wfp in rts_msgs:
    manip.manip_extract(rts_r, rts_msg_wfp)

from move_data import copy_and_delete_folder
src_root=rootdir +"/../"
src_folder= trayid
dst_root=r"S:/RTS_DAT_LArASIC_QC/"
copy_and_delete_folder(src_root, src_folder, dst_root)

print ("Done")
sendemail(subject ="Congratulations! The tray is done...", message="Please remove the tested tray and place a new tray with label.", user_email=user_email, inform_tech=True, p_shifter=True, s_shifter=True)






