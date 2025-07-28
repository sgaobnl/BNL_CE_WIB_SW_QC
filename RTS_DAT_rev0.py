import sys 
import os
import subprocess
import time 
import random
import pickle


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
from rts_ssh import Sinkcover
from rts_ssh import rts_ssh
from set_rootpath import rootdir_cs
from cryo_uart import cryobox

sys.path.append('./SN_recognition/')  
from SN_CLASS import SN_CLASS


def send_rts_email(message):
    sender_email = "rtshibay@gmail.com"
    receiver_email = "sgao@bnl.gov;gao33.bnl@gmail.com;lke@bnl.gov"
    #receiver_email = ningxuyang0202@gmail.com
    password = "mbqx qfca voue zwfr"
    subject = "Message from RTS"
    body = message
    msg = MIMEMultipart()

    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    # Attach the body text to the email
    msg.attach(MIMEText(body, 'plain'))
    
    try: 
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.ehlo()
            server.starttls()  # Start TLS encryption
            server.ehlo()
            server.login(sender_email, password)  # Login to the server
            server.send_message(msg)  # Send the email
            print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

def DAT_debug (QCstatus):
    print (QCstatus)
    send_rts_email(message="Please contact tech coordinator (DAT issue)")
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
    send_rts_email(message="Please contact tech coordinator (RTS issue)")
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
    if BypassRTS:
        pass
    else:
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
        
        if BypassRTS:
            rts.msg = str(int(rts.msg) + 1)
            status = 0
        else:
            status = rts.MoveChipFromTrayToSocket(trayno, trayc, trayr, sinkno, sktn,duttype)    

        if status < 0:
            RTS_debug ("T2S", status, trayno, trayc, trayr, sinkno, sktn)
            tmpi = tmpi
            duts=[chipi] + duts
            continue
        else:
            dut_skt[rts.msg] = (chipi, skt)
            tmpi = tmpi + 1
    if BypassRTS:
        pass
    else:
        rts.rts_idle()
    return duts, dut_skt

def DAT_QC(dut_skt, duttype="FE") :
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
            send_rts_email(message="Please contact tech coordinator (QC error)")
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

    send_rts_email(message="Do you want to perform cold test? ")
    yorn = input ("\033[96m Do you want to perform cold test? (Y/N) :\033[0m")
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

        send_rts_email(message="Cold test is done, please open the sink cover ...")

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
def MovetoTray(sinkno, duts, dut_skt, QCstatus, badchips, bad_dut_order, duttype="FE") :
    print ("DUTtype", duttype)
    ids_goods = {}
    ids_bads = {}
    print ("ChIP ID back to tray")

    ids_g = list(dut_skt.keys())
    if BypassRTS:
        pass
    else:
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
            QCstatus, badchips = DAT_QC(dut_skt,duttype)  
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
            if BypassRTS:
                rts.msg = str(int(rts.msg) + 1)
                status = 0
                pass
            else:
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

        return duts, {}, bad_dut_order, ids_goods, ids_bads
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
                if "CD" in duttype:
                    trayc=(bad_dut_order%10) +1
                    trayr=(bad_dut_order//10) +1
                else:
                    trayc=(bad_dut_order%15) +1
                    trayr=(bad_dut_order//15) +1
                if BypassRTS:
                    rts.msg = str(int(rts.msg) + 1)
                    status = 0
                else:
                    status = rts.MoveChipFromSocketToTray(sinkno, sktn, badtrayno, trayc, trayr, duttype)

                if status < 0:
                    RTS_debug ("S2T", status, trayno, trayc, trayr, sinkno, sktn)
                    tmpi = tmpi
                    continue
                else:
                    ids_bads[rts.msg] = (chipi, skt)
                    bad_dut_order +=1
                    tmpi = tmpi + 1
            return duts,dut_skt, bad_dut_order, ids_goods, ids_bads

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
                    if "CD" in duttype:
                        trayc=(bad_dut_order%10) +1
                        trayr=(bad_dut_order//10) +1
                    else:
                        trayc=(bad_dut_order%15) +1
                        trayr=(bad_dut_order//15) +1
                    if BypassRTS:
                        rts.msg = str(int(rts.msg) + 1)
                        status = 0
                    else:
                        status = rts.MoveChipFromSocketToTray(sinkno, sktn, badtrayno, trayc, trayr, duttype)
                else:
                    if BypassRTS:
                        rts.msg = str(int(rts.msg) + 1)
                        status = 0
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
                        bad_dut_order +=1
                    else:
                        ids_goods[rts.msg] = (chipi,tmpi)
                    tmpi = tmpi + 1

            return duts, dut_skt, bad_dut_order, ids_goods, ids_bads


############################################################

BypassRTS = False
logs = {}

#chiptype = 1
#print ("RTS only support FE chip testing at the current development phase)")
chiptype = 1

if chiptype == 1:
    duttype = "FE"
    rootdir = rootdir_cs(duttype)
elif chiptype == 2:
    duttype = "ADC"
    rootdir = rootdir_cs(duttype)
elif chiptype == 3:
    duttype = "CD"
    rootdir = rootdir_cs(duttype)

while True:
    print ("\033[96m Root folder of test data is: "+ "\033[93m" + rootdir + "\033[0m")
    yns = input ("\033[96m Is path correct (Y/N): " + "\033[95m" )
    if "Y" in yns or "y" in yns:
        break
    else:
        print ( "\033[91m Wrong path, please edit set_rootpath.py" + "\033[0m")
        print ( "\033[91m exit anyway" + "\033[0m")
        exit()

while True:
    print ("Read TrayID (BxxxTxxxx) from the tray")
    bno = input("Input TrayID (-1 to exit): ")
    if len(bno) ==9:
        if (bno[0] == "B" ) and (bno[4] == "T" ) :
            try:
                int(bno[1:4])
                int(bno[5:9])
                break
            except BaseException as e:
                print ("Wrong Tray ID, please input again")
        else:
            print ("Wrong Tray ID, please input again")
    elif bno[0:2] == "-1":
        sys.exit()
    else:
        print ("Wrong Tray ID length")
        sys.exit()


trayid = bno
#trayid = "B001T0001"
trayno =2 # tray with chips to be tested
bad_trayno =1 # tray with bad chips
badtrayno = 1 #some issue with tray#1
bad_dut_order=0
sinkno =2
rootdir = rootdir + trayid + "/"
#rootdir = "C:/DAT_LArASIC_QC/Tested/" + trayid + "/"

logs["TrayID"] = trayid
logs["TrayNo"] = 2
logs["BadTrayNo"] = 1
logs["Bad_dut_order"] = bad_dut_order
logs["SinkNo"] = 2
logs["rootdir"] = rootdir

print ("start trayID: {}".format(trayid))
status = 0
#duts = [47,48,49,66,67,68,69,82,83,84,85,86,87] # list(range(47,484950,88,1))
#duts = [47,48,49,66,67,68,69,82,83,84,85,86,87] # list(range(47,484950,88,1))
duts = list(range(0,24,1))
#duts = [82,83,84,2,86,87,88,89]
duts = sorted(duts)
logs["duts"] = duts 
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
    #sys.exit()

############################################################
rts = RTS_CFG()
cryo = cryobox()

rts.msg = "10000000000"
if BypassRTS:
    pass
else:
    rts.rts_init(port=2001, host_ip='192.168.0.2')
    rts.RootDirSet(rootdir=rootdir)
    rts.MotorOn()
    rts.JumpToCamera()

    ocrbin_fp = rootdir + "ocr_results.bin"
    if os.path.isfile(ocrbin_fp) :
        with open(ocrbin_fp, 'rb') as fn:
            goodchips, badchips = pickle.load(fn)
    else:
        rts.ScanTray_Lar(rootdir=rootdir)
        sn=SN_CLASS()
        goodchips, badchips = sn.chip_ocr(rootdir)

    
    if len(badchips) > 0:
        bad_tray_id = 1
        while len(badchips) :
            tray_id = badchips.keys()[0]
            while True:
                if bad_tray_id >= 90:
                    print ("\033[91m !WARNING! Tray#1 (bac chips) is full: \033[0m")
                    yorn = input ("\033[91m Replace with a new tray? (y/Y): \033[0m")
                    if "Y" in yorn or "y" in yorn:
                        bad_tray_id = 1
                #bad_trayc = bad_tray_id - ((bad_tray_id-1)//15)*15
                bad_trayc = (bad_tray_id-1)%15 + 1
                bad_trayr = (bad_tray_id-1)//15 + 1
                flg = rts.isChipInTray(bad_trayno,bad_trayc, bad_trayr)
                if not flg:#no chip in it
                    trayc = (tray_id-1)%15 + 1
                    trayr = (tray_id-1)//15 + 1
                    status = rts.MoveChipFromTrayToTray(trayno, trayc, trayr, bad_trayno, bad_trayc,bad_trayr)    
                    if status > 0 :
                        badchips.pop(tray_id) #remove it from bad chip
                        with open(ocrbin_fp, 'wb') as fn:
                            pickle.load([goodchips, badchips], fn)
                        bad_tray_id += 1
                        break
                    else:
                        RTS_debug ("T2T", status )
                else:
                    bad_tray_id += 1





#    ischip = rts.isChipInTray(2,1,1)
#    print (ischip)


    #rts.MoveChipFromTrayToSocket(2, 1, 1, 2, 1, "FE")    
    #rts.MoveChipFromSocketToTray(2, 1, 2, 1, 1, "FE")
#    rmsg = rts.ScanTray_Lar(rootdir=rootdir)
#    with open(rootdir  + "/chips_on_tray.txt", "w") as fp:
#        fp.write(rmsg)
rts.rts_shutdown()
exit()

#rts.MoveChipFromSocketToTray(2, 1, 2, 8, 6, "FE")
#rts.MoveChipFromSocketToTray(2, 1, 2, 9, 6, "FE")
#rts.MoveChipFromSocketToTray(2, 1, 2, , 5, "FE")
#rts.MoveChipFromSocketToTray(2, 1, 2, , 5, "FE")
#rts.MoveChipFromSocketToTray(2, 1, 2, , 5, "FE")
#rts.MoveChipFromTrayToSocket(2, 7, 1, 2, 7, "FE")    
#rts.MoveChipFromSocketToTray(2, 7, 2, 7, 1, "FE")
#rts.MoveChipFromSocketToTray(2, 1, 2, 4, 3)
#rts.MoveChipFromTrayToSocket(2, 1, 2, 2, 1, "FE")    
#rts.MoveChipFromTrayToSocket(2, 2, 2, 2, 2, "FE")    
#rts.MoveChipFromTrayToSocket(2, 3, 2, 2, 3, "FE")    
#rts.MoveChipFromTrayToSocket(2, 4, 2, 2, 4, "FE")    
#rts.MoveChipFromTrayToSocket(2, 5, 2, 2, 5, "FE")    
#rts.MoveChipFromTrayToSocket(2, 6, 2, 2, 6, "FE")    
#rts.MoveChipFromTrayToSocket(2, 7, 2, 2, 7, "FE")    
#rts.MoveChipFromTrayToSocket(2, 8, 2, 2, 8, "FE")    
#
#
#rts.MoveChipFromTrayToSocket(2, 1, 1, 2, 1, "ADC")    
#rts.MoveChipFromTrayToSocket(2, 2, 1, 2, 2, "ADC")    
#rts.MoveChipFromTrayToSocket(2, 3, 1, 2, 3, "ADC")    
#rts.MoveChipFromTrayToSocket(2, 4, 1, 2, 4, "ADC")    
#rts.MoveChipFromTrayToSocket(2, 5, 1, 2, 5, "ADC")    
#rts.MoveChipFromTrayToSocket(2, 6, 1, 2, 6, "ADC")    
#rts.MoveChipFromTrayToSocket(2, 7, 1, 2, 7, "ADC")    
#rts.MoveChipFromTrayToSocket(2, 8, 1, 2, 8, "ADC")    
#
#
##rts.MoveChipFromTrayToSocket(2, 1, 1, 2, 1, "CD")    
##rts.MoveChipFromTrayToSocket(2, 2, 1, 2, 2, "CD")    
#rts.rts_shutdown()
#exit()
#rts.MoveChipFromSocketToTray(2, 1, 2, 1, 1, "CD")
#rts.MoveChipFromSocketToTray(2, 2, 2, 2, 1, "CD")
#rts.rts_idle()
#exit()

#rts.MoveChipFromSocketToTray(2, 1, 2, 4, 3)
#sts_tmp = rts.CoverStatus()
#print (sts_tmp)
#sts_tmp2 = rts.CoverStatus()
#print ("kkk", sts_tmp2)
# 
##rts.MoveChipFromSocketToTray(2, 1, 2, 4, 3)
##rts.MoveChipFromSocketToTray(2, 2, 2, 5, 3)
##rts.MoveChipFromSocketToTray(2, 3, 2, 6, 3)
##rts.MoveChipFromSocketToTray(2, 4, 2, 7, 3)
##rts.MoveChipFromSocketToTray(2, 5, 2, 8, 3)
##rts.MoveChipFromSocketToTray(2, 6, 2, 9, 3)
##rts.MoveChipFromSocketToTray(2, 7, 2, 10, 3)
##rts.MoveChipFromSocketToTray(2, 8, 2, 11, 3)
####rts.MotorOn()
####rts.MoveChipFromTrayToSocket(2, 1, 1, 2, 1)    
####rts.MoveChipFromSocketToTray(2, 1, 2, 1, 1)
####rts.MoveChipFromTrayToTray(2, 1, 1, 1, 1,1)    
####rts.JumpToTray(2,1,1)
####rts.DropToTray()
###
###print ("KKKKKKKKKKKKKK")
####rts.rts_idle()
##rts.MotorOn()
##rts.MoveChipFromSocketToTray(2, 1, 2, 4, 3)
##for i in range(3):
##    rts.MoveChipFromTrayToSocket(2, 1, 1, 2, 1)    
##    rts.MoveChipFromSocketToTray(2, 1, 2, 1, 1)
##rts.MoveChipFromTrayToSocket(2, 1, 2, 2, 2)    
##while True:
##    rts.JumpToCamera()
##    time.sleep(1)
#rts.rts_shutdown()
###
#exit()
#

#rts.MotorOn()
#rts.rts_idle()
#exit()
#rts.MoveChipFromTrayToSocket(2, 1, 1, 2, 1)    
#rts.MoveChipFromTrayToSocket(2, 2, 1, 2, 1)    
#rts.MoveChipFromTrayToSocket(2, 3, 1, 2, 1)    
#rts.MoveChipFromTrayToSocket(2, 4, 1, 2, 1)    
#rts.MoveChipFromTrayToSocket(2, 5, 1, 2, 1)    
#rts.MoveChipFromTrayToSocket(2, 6, 1, 2, 1)    
#rts.MoveChipFromTrayToSocket(2, 7, 1, 2, 1)    
#rts.MoveChipFromTrayToSocket(2, 7, 1, 2, 1)    
#rts.rts_idle()
##for i in range(2):
#if True:
#    rts.MotorOn()
#    rts.MoveChipFromTrayToSocket(2, 1, 1, 2, 1)    
#    print ("XXXXXX")
###    rts.rts_idle()
###    time.sleep(50)
###    print ("MXXXXXX")
###    rts.MotorOn()
###    time.sleep(2)
###    rts.JumpToCamera()
#    rts.rts_idle()
#    print ("KXXXXXX")
#    rts.MotorOn()
#    rts.MoveChipFromSocketToTray(2, 1, 2, 1, 1)
##    print ("MKXXXXXX")
#    rts.rts_idle()
##rts.MoveChipFromSocketToTray(2, 12, 2, 1, 1)
##rts.MoveChipFromTrayToTray(2, 2, 2, 1, 2,2)    
##rts.MoveChipFromTrayToTray(2, 2, 1, 1, 2,1)    
##rts.MoveChipFromTrayToTray(1, 2, 2, 2, 2,2)    
##rts.MoveChipFromTrayToTray(1, 2, 1, 2, 2,1)    
##
##rts.PumpOff()
##rts.rts_shutdown()
#print ("XXXXXX")
#exit()


#first run
################STEP1#################################
if "CD" in duttype:
    skts=[0,1]
else:
    skts=[0,1,2,3,4,5,6,7]
dut_skt = {}
#while (len(duts) > 0) or (len(skts) != 8):
while (len(duts) > 0) :
    duts, dut_skt_n = MovetoSoket(sinkno, duts,ids_dict, skts=skts,duttype=duttype) 
    print ("Remain chips on tray: ", duts)

    dut_skt.update(dut_skt_n)
    print ("Chips to be tested: ", dut_skt)
    send_rts_email(message="Chips to be tested: " + ','.join(map(str, dut_skt.values())))

    if True:
        QCstatus, badchips = DAT_QC(dut_skt,duttype) 
    else:
        QCstatus = "PASS"
        badchips = []
    print (QCstatus, "Badchips:", badchips)

    if "PASS" not in QCstatus :
        duts, dut_skt, bad_dut_order, ids_goods, ids_bads= MovetoTray(sinkno, duts, dut_skt, QCstatus, badchips, bad_dut_order,duttype=duttype) 
        if len(badchips) > 0:
            skts=badchips
        ids_dict_bad.update(ids_bads)
    else: #PASS
        duts, dut_skt, bad_dut_order, ids_goods, ids_bads = MovetoTray(sinkno, duts, dut_skt, QCstatus, badchips, bad_dut_order,duttype=duttype) 
        print ("PASS", dut_skt)
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



ids_k = list(ids_dict.keys())

for ids in ids_k:
    print (ids, ids_dict[ids])

if BypassRTS:
    pass
else:
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






