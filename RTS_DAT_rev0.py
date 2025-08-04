import sys 
import os
import subprocess
import time 
import random
import pickle
import numpy as np

# To send notification email
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
from sendemail import sendemail
from User_Input import get_user_input
from init_check import init_chk 
TRAY_N = 90

def DAT_debug (QCstatus):
    print (QCstatus)
    sendemail(message="Please contact tech coordinator (DAT issue)", user_email=user_email)
    while True:#
        print ("444-> Move chips back to original positions")
        print ("2->fixed,")
        userinput = input ("Please contact tech coordinator : ")
        if len(userinput) > 0:
            if "444" in userinput :
                return "444"
            elif "2" in userinput :
                yorn = input ("Fixed. Are you sure? (y/Y):")
                if "Y" in yorn or "y" in yorn:
                    return "2"

def RTS_debug (info, status=None, trayno=None, trayc=None, trayr=None, sinkno=None, sktn=None):
    sendemail(message="Please contact tech coordinator (RTS issue)", user_email=user_email)
    print ("Please check the error information on EPSON RC")
    if "T2S" in info:
        print ("Chip is moved from Tray") 
        print ("Chip on orignial TrayNo(1-2)={}, Col(1-15)={}, Row(1-6)={}".format(trayno, trayc, trayr)) 
    elif "S2T" in info:
        print ("Chip is moved from Socket") 
        print ("Chip on orignial Sinkno(1-2)={}, Skt(1-8)={} ".format(sinkno, sktn)) 
    elif "T2T" in info:
        print ("Chip is moved from Tray to Tray") 

    rts.rts_idle()

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
                rts.MotorOn()
                break

def MovetoSoket(sinkno, duts,ids_dict,  skts=[0,1,2,3,4,5,6,7], duttype="FE") :
    print ("DUTtype", duttype)
    dut_skt = {}
    #make sure DAT is powered off
    DAT_power_off()
    rts.MotorOn()

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
            RTS_debug ("T2S", status, trayno, trayc, trayr, sinkno, sktn)
            tmpi = tmpi
            duts=[chipi] + duts
            continue
        else:
            dut_skt[rts.msg] = (chipi, skt)
            tmpi = tmpi + 1
    rts.rts_idle()
    return duts, dut_skt

def DAT_QC(dut_skt, duttype="FE", LN2_flg = True) :
    while True:
        QCresult = rts_ssh(dut_skt, root=rootdir, duttype=duttype, env="RT")
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
            sendemail(message="Please contact tech coordinator (QC error)", user_email=user_email)
            userinput = input ("Please contact tech coordinator")
            if len(userinput) > 0:
                if "139" in userinput :
                    QCstatus = "Terminate"
                    badchips = []
                    break
                elif "2" in userinput[0] :
                    print ("debugging, ")
                    input ("click any key to start ASIC QC again...")
    if len(badchips) > 0:
        return QCstatus, badchips #badchips range from 0 to7

    if LN2_flg:
        sendemail(message="Do you want to perform cold test? ", user_email=user_email)
        yorn = input ("\033[96m Do you want to perform cold test? (Y/N) :\033[0m")
    else:
        print ("Bypass cold test")
        yorn = 'no'
    if "Y" in yorn or "y" in yorn:
        while True:
            cover_sts = rts.CoverStatus()
            if "-198" in cover_sts:
                print ("Cover is close! Start the cold test in 10 seconds")
                time.sleep(10)
                break
            else:
                time.sleep(5)

        try:
            cryo.cryo_fill()
        except KeyboardInterrupt:
            print ("####################")

        cryo.cryo_lowlevel(waitminutes=10)
        cryo.cryo_highlevel(waitminutes=5)

        LNQCresult = rts_ssh(dut_skt, root=rootdir, duttype=duttype, env="LN" )

        cryo.cryo_warmup(waitminutes=30)

        sendemail(message="Cold test is done, please open the sink cover ...", user_email=user_email)

        while True:
            cover_sts = rts.CoverStatus()
            if "197" in cover_sts:
                print ("Cover is open! Activate robot in 10 seconds")
                time.sleep(10)
                break
            else:
                time.sleep(5)

    return QCstatus, badchips #badchips range from 0 to7

################STEP3#################################
def MovetoTray(sinkno, duts, dut_skt, QCstatus, badchips, bad_tray_spot, duttype="FE", LN2_flg=True) :
    ids_goods = {}
    ids_bads = {}

    ids_g = list(dut_skt.keys())
    DAT_power_off()
    rts.MotorOn()

    if "CD" in duttype:
        CHIPS = 2
    else:
        CHIPS = 8

    #if "Terminate" in QCstatus: #move back to original positions
    if ("Code#E001" in QCstatus) or ("Terminate" in QCstatus) : #move back to original positions
        rts.rts_idle()
        admincode = DAT_debug (QCstatus)
        if "2" in admincode:
            QCstatus, badchips = DAT_QC(dut_skt,duttype, LN2_flg=LN2_flg)  
        elif "444" in admincode:
            RTS_debug ("DAT")
        rts.MotorOn()
            
        tmpi = 0
        while tmpi < CHIPS:
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
                RTS_debug ("S2T", status, trayno, trayc, trayr, sinkno, sktn)
                tmpi = tmpi
                continue
            else:
                tmpi = tmpi + 1

        tmps = []
        for ids in ids_g:
            tmps.append(dut_skt[ids][0])
        tmps = sorted(tmps)
        duts = tmps + duts

        return duts, {}, bad_tray_spot, ids_goods, ids_bads
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
                bad_tray_spot = FindSpotOnBadTray(bad_tray_spot)
                bad_dut_order = bad_tray_spot - 1
                if "CD" in duttype:
                    trayc=(bad_dut_order%10) +1
                    trayr=(bad_dut_order//10) +1
                else:
                    trayc=(bad_dut_order%15) +1
                    trayr=(bad_dut_order//15) +1
                status = rts.MoveChipFromSocketToTray(sinkno, sktn, badtrayno, trayc, trayr, duttype)

                if status < 0:
                    RTS_debug ("S2T", status, trayno, trayc, trayr, sinkno, sktn)
                    tmpi = tmpi
                    continue
                else:
                    ids_bads[rts.msg] = (chipi, skt)
                    bad_tray_spot +=1
                    tmpi = tmpi + 1
            return duts,dut_skt, bad_tray_spot , ids_goods, ids_bads

        if "PASS" in QCstatus:
            tmpi = 0
            while tmpi < CHIPS:
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
                    bad_tray_spot = FindSpotOnBadTray(bad_tray_spot)
                    bad_dut_order = bad_tray_spot - 1
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
                    RTS_debug ("S2T", status, trayno, trayc, trayr, sinkno, sktn)
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
                        bad_tray_spot +=1
                    else:
                        ids_goods[rts.msg] = (chipi,tmpi)
                    tmpi = tmpi + 1

            return duts, dut_skt, bad_tray_spot, ids_goods, ids_bads

def FindSpotOnBadTray(bad_tray_spot = 1):
    while True:
        if bad_tray_spot >= TRAY_N:
            sendemail(message="!WARNING! Tray#1 (bac chips) is full, please replace with a new empty tray. ", user_email=user_email)
            print ("\033[91m !WARNING! Tray#1 (bac chips) is full: \033[0m")
            yorn = input ("\033[91m Replace with a new tray? (y/Y): \033[0m")
            if "Y" in yorn or "y" in yorn:
                bad_tray_spot = 1
        bad_trayc = (bad_tray_spot-1)%15 + 1
        bad_trayr = (bad_tray_spot-1)//15 + 1
        flg = rts.isChipInTray(bad_trayno,bad_trayc, bad_trayr)
        if not flg:#no chip in it
            return bad_tray_spot
        else:
            bad_tray_spot += 1

def Tray_SCAN_OCR(rootdir):
    ocrbin_fp = rootdir + "ocr_results.bin"
    if os.path.isfile(ocrbin_fp) :
        with open(ocrbin_fp, 'rb') as fn:
            chip_ocr  = pickle.load(fn)
    else:
        print ("Wait a few minutes until the scanning is done")
        rts.ScanTray_Lar(rootdir=rootdir)
        rts.JumpToCamera()
        sn=SN_CLASS()
        chip_ocr = sn.chip_ocr(rootdir)

    bad_chip_ds = {} 
    for key in list(chip_ocr.keys()):
        if not chip_ocr[key][0] :
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
    bad_tray_spot = FindSpotOnBadTray(bad_tray_spot = 1)
    for key in list(chip_ocr.keys()):
        if not chip_ocr[key][0] :
            tray_id = key
            trayc = (tray_id-1)%15 + 1
            trayr = (tray_id-1)//15 + 1
            bad_trayc = (bad_tray_spot-1)%15 + 1
            bad_trayr = (bad_tray_spot-1)//15 + 1
            status = rts.MoveChipFromTrayToTray(trayno, trayc, trayr, bad_trayno, bad_trayc,bad_trayr)    
            if status > 0 :
                print (f'remove {key}, {chip_ocr[key]}')
                chip_ocr.pop(key) #remove it from bad chip
                with open(ocrbin_fp, 'wb') as fn:
                    pickle.dump(chip_ocr, fn)
                bad_tray_spot += 1
            else:
                RTS_debug ("T2T", status )
    
    return bad_tray_spot, chip_ocr 

############################################################

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
    print ("Exit anyway")

############################################################
rts = RTS_CFG()
cryo = cryobox()

rts.msg = "10000000000"
rts.rts_init(port=2001, host_ip='192.168.0.2')
rts.RootDirSet(rootdir=rootdir)
rts.MotorOn()
rts.PumpOn()
time.sleep(5)
rts.PumpOff()
rts.JumpToCamera()
bad_tray_spot, chip_ocr = Tray_SCAN_OCR(rootdir)
rts.rts_idle()

#rts.MoveChipFromTrayToSocket(2, 8, 2, 2, 8, "FE")    
#rts.MoveChipFromTrayToSocket(2, 1, 1, 2, 1, "ADC")    
##rts.MoveChipFromTrayToSocket(2, 1, 1, 2, 1, "CD")    
#rts.MoveChipFromSocketToTray(2, 1, 2, 1, 1, "CD")
#rts.rts_idle()
##rts.rts_shutdown()
#print ("XXXXXX")
#exit()

duts = list(np.array(list(chip_ocr.keys())) - 1)
logs["duts"] = duts 
logs["ocr"] = chip_ocr

#first run
################STEP1#################################
if "CD" in duttype:
    skts=[0,1]
else:
    skts=[0,1,2,3,4,5,6,7]
dut_skt = {}

while (len(duts) > 0) :
    duts, dut_skt_n = MovetoSoket(sinkno, duts,ids_dict, skts=skts,duttype=duttype) 
    print ("Remain chips on tray: ", duts)

    dut_skt.update(dut_skt_n)
    print ("Chips to be tested: ", dut_skt)
    sendemail(message="Chips to be tested: " + ','.join(map(str, dut_skt.values())), user_email=user_email)

    if True:
        QCstatus, badchips = DAT_QC(dut_skt,duttype, LN2_flg) 
    else:
        QCstatus = "PASS"
        badchips = []
    print (QCstatus, "Badchips:", badchips)

    if "PASS" not in QCstatus :
        duts, dut_skt, bad_tray_spot, ids_goods, ids_bads= MovetoTray(sinkno, duts, dut_skt, QCstatus, badchips, bad_tray_spot,duttype=duttype, LN2_flg=LN2_flg) 
        if len(badchips) > 0:
            skts=badchips
        ids_dict_bad.update(ids_bads)
    else: #PASS
        duts, dut_skt, bad_tray_spot, ids_goods, ids_bads = MovetoTray(sinkno, duts, dut_skt, QCstatus, badchips,bad_tray_spot,duttype=duttype, LN2_flg=LN2_flg) 
        ids_dict.update(dut_skt)
        ids_dict_good.update(ids_goods)
        ids_dict_bad.update(ids_bads)
        dut_skt = {}
        if "CD" in duttype:
            skts=[0,1]
        else:
            skts=[0,1,2,3,4,5,6,7]

    print ("**********save ID info*************")
    ids_k = list(ids_dict.keys())
    if len(ids_k) > 0:
        fp = rootdir + ids_k[0] + "_log.bin"
        logs["RTS_MSG_R2S_P"] = ids_dict
        logs["RTS_MSG_S2R_P"] = ids_dict_good
        logs["RTS_MSG_S2R_F"] = ids_dict_bad

        with open(fp, 'wb') as fn:
            pickle.dump(logs, fn)

#ids_k = list(ids_dict.keys())

#for ids in ids_k:
#    print (ids, ids_dict[ids])

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
print ("Done")






