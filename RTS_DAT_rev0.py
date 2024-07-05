import sys 
import os
import subprocess
import time 
import random
import pickle


#start robot
from RTS_CFG import RTS_CFG
from rts_ssh_LArASIC import DAT_power_off
from rts_ssh_LArASIC import Sinkcover
from rts_ssh_LArASIC import rts_ssh_LArASIC

############################################################
BypassRTS = False

logs = {}

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
trayno =2
badtrayno = 1 #some issue with tray#1
bad_dut_order=0
datno =2
rootdir = "C:/DAT_LArASIC_QC/Tested/" + trayid + "/"

logs["TrayID"] = trayid
logs["TrayNo"] = 2
logs["BadTrayNo"] = 1
logs["Bad_dut_order"] = bad_dut_order
logs["DATNo"] = 2
logs["rootdir"] = rootdir

print ("start trayID: {}".format(trayid))
status = 0
duts = list(range(0,90,1))
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
    sys.exit()

############################################################
rts = RTS_CFG()
rts.msg = "10000000000"
if BypassRTS:
    pass
else:
    rts.rts_init(port=2001, host_ip='192.168.0.2')
    rts.MotorOn()
    rts.JumpToCamera()

#rts.MotorOn()
#rts.MoveChipFromSocketToTray(2, 3, 2, 11, 1)
#rts.rts_idle()
#rts.MotorOn()
#rts.MoveChipFromSocketToTray(2, 4, 2, 12, 1)
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

def DAT_debug (QCstatus):
    print (QCstatus)
    while True:
        print ("444-> Move chips back to original positions")
        print ("2->fixed,")
        userinput = input ("Please contatc tech coordinator : ")
        if len(userinput) > 0:
            if "444" in userinput :
                return "444"
            elif "2" in userinput :
                yorn = input ("Fixed. Are you sure? (y/Y):")
                if "Y" in yorn or "y" in yorn:
                    return "2"

def RTS_debug (info, status=None, trayno=None, trayc=None, trayr=None, datno=None, sktn=None):
    print ("Please check the error information on EPSON RC")
    if "T2S" in info:
        print ("Chip is moved from Tray") 
        print ("Chip on orignial TrayNo(1-2)={}, Col(1-15)={}, Row(1-6)={}".format(trayno, trayc, trayr)) 
    elif "S2T" in info:
        print ("Chip is moved from Socket") 
        print ("Chip on orignial DATno(1-2)={}, Skt(1-8)={} ".format(datno, sktn)) 
    else:
        print (info)

    while True:
        print ("444-> Shutdown RTS and exit anyway")
        print ("1->move chip to Tray#1_Col#15_Row#6")
        print ("2->move chip to orignal position")
        print ("6->fixed,")
        userinput = input ("Please contatc tech coordinator : ")
        if len(userinput) > 0:
            if "444" in userinput :
                rts.JumpToCamera()
                rts.rts_shutdown()
                print ("Exit anyway")
                exit()
#            elif "1" in userinput[0] :
#                while True:
#                    yorn = input ("Is Tray#1_Col#15_Row#6 empty? (Y/N) : ")
#                    if ("Y" in yorn) or ("y" in yorn): 
#                        break
#                print ("Move chip to Tray#1_Col#15_Row#6")
#                rts.JumptoTray(trayno=1, trayc=15, trayr=6)    
#                rts.DroptoTray()    
#                rts.JumpToCamera()
#                rts.PumpOff()
#                rts.MoterOff()
#                print ("please fix the issue...")
#            elif "2" in userinput[0] :
#                while True:
#                    if "T2S" in info:
#                        yorn = input ("Is Tray#{}_Col#{}_Row#{} empty? (Y/N) : ".format(trayno, trayc, trayr))
#                    elif "S2T" in info:
#                        yorn = input ("Is DATno#{}_Skt#{} empty? (Y/N) : ".format(datno, sktn)
#                    if ("Y" in yorn) or ("y" in yorn): 
#                        break
#                print ("Move chip to Tray#{}_Col#{}_Row#{} empty? (Y/N) : ".format(trayno, trayc, trayr))
#                rts.PumpOn()
#                rts.MoterOn()
#                time.sleep(1)
#                if "T2S" in info:
#                    rts.JumpToTray(trayno=1, trayc=15, trayr=6)    
#                    rts.PickupToTray()    
#                    rts.JumpToTray(trayno=trayno, trayc=trayc, trayr=r)    
#                    rts.DroptoTray()    
#                    rts.JumpToCamera()
#                elif "S2T" in info:
#                    rts.JumpToTray(trayno=1, trayc=15, trayr=6)    
#                    rts.PickupToTray()    
#                    rts.JumpToSocket(datno=datno, sktn=sktn)    
#                    rts.DroptoSocket()    
#                    rts.JumpToCamera()

            elif "6" in userinput[0] :
                input ("Make sure the chip back to orginal position and click anykey")
                break

def MovetoSoket(duts,ids_dict, skts=[0,1,2,3,4,5,6,7]) :
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

        trayc=(chipi%15) +1
        trayr=(chipi//15) +1
        sktn = skt + 1
        
        if BypassRTS:
            rts.msg = str(int(rts.msg) + 1)
            status = 0
        else:
            status = rts.MoveChipFromTrayToSocket(trayno, trayc, trayr, datno, sktn)    

        if status < 0:
            RTS_debug ("T2S", status, trayno, trayc, trayr, datno, sktn)
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

def DAT_QC(dut_skt) :
    while True:
        QCresult = rts_ssh_LArASIC(dut_skt, root=rootdir)
        if QCresult != None:
            QCstatus = QCresult[0]
            badchips = QCresult[1]
            break
        else:
            print ("139-> terminate, 2->debugging")
            userinput = input ("Please contatc tech coordinator")
            if len(userinput) > 0:
                if "139" in userinput :
                    QCstatus = "Terminate"
                    badchips = []
                    break
                elif "2" in userinput[0] :
                    print ("debugging, ")
                    input ("click any key to start ASIC QC again...")
    return QCstatus, badchips #badchips range from 0 to7

################STEP3#################################
def MovetoTray(duts, dut_skt, QCstatus, badchips, bad_dut_order) :
    ids_goods = {}
    ids_bads = {}
    print ("ChIP ID back to tray")

    ids_g = list(dut_skt.keys())
    if BypassRTS:
        pass
    else:
        DAT_power_off()
        rts.MotorOn()

    #if "Terminate" in QCstatus: #move back to original positions
    if ("Code#E001" in QCstatus) or ("Terminate" in QCstatus) : #move back to original positions
        rts.rts_idle()
        admincode = DAT_debug (QCstatus)
        if "2" in admincode:
            QCstatus, badchips = DAT_QC(dut_skt) 
        elif "444" in admincode:
            RTS_debug ("DAT")
        rts.MotorOn()
            
        tmpi = 0
        while tmpi < 8:
            for ids in ids_g:
                if dut_skt[ids][1] == tmpi:
                    chipi=dut_skt[ids][0]
                    sktn =dut_skt[ids][1] + 1
                    break
            trayc=(chipi%15) +1
            trayr=(chipi//15) +1
            if BypassRTS:
                rts.msg = str(int(rts.msg) + 1)
                status = 0
                pass
            else:
                status = rts.MoveChipFromSocketToTray(datno, sktn, trayno, trayc, trayr)

            if status < 0:
                RTS_debug ("S2T", status, trayno, trayc, trayr, datno, sktn)
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
                trayc=(chipi%15) +1
                trayr=(chipi//15) +1
                trayc=(bad_dut_order%15) +1
                trayr=(bad_dut_order//15) +1
                if BypassRTS:
                    rts.msg = str(int(rts.msg) + 1)
                    status = 0
                else:
                    status = rts.MoveChipFromSocketToTray(datno, sktn, badtrayno, trayc, trayr)
                if status < 0:
                    RTS_debug ("S2T", status, trayno, trayc, trayr, datno, sktn)
                    tmpi = tmpi
                    continue
                else:
                    ids_bads[rts.msg] = (chipi, skt)
                    bad_dut_order +=1
                    tmpi = tmpi + 1
            return duts,dut_skt, bad_dut_order, ids_goods, ids_bads

        if "PASS" in QCstatus:
            tmpi = 0
            while tmpi < 8:
                for ids in ids_g:
                    if dut_skt[ids][1] == tmpi:
                        chipi=dut_skt[ids][0]
                        sktn =dut_skt[ids][1] + 1
                        break
                trayc=(chipi%15) +1
                trayr=(chipi//15) +1
                if tmpi in badchips:
                    trayc=(bad_dut_order%15) +1
                    trayr=(bad_dut_order//15) +1
                    if BypassRTS:
                        rts.msg = str(int(rts.msg) + 1)
                        status = 0
                    else:
                        status = rts.MoveChipFromSocketToTray(datno, sktn, badtrayno, trayc, trayr)
                else:
                    if BypassRTS:
                        rts.msg = str(int(rts.msg) + 1)
                        status = 0
                    else:
                        status = rts.MoveChipFromSocketToTray(datno, sktn, trayno, trayc, trayr)

                if status < 0:
                    RTS_debug ("S2T", status, trayno, trayc, trayr, datno, sktn)
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


#first run
################STEP1#################################
skts=[0,1,2,3,4,5,6,7]
dut_skt = {}
while (len(duts) > 0) or (len(skts) != 8):
    duts, dut_skt_n = MovetoSoket(duts,ids_dict, skts=skts) 
    print ("Remain chips on tray: ", duts)

    dut_skt.update(dut_skt_n)
    print ("Chips to be tested: ", dut_skt)

    QCstatus, badchips = DAT_QC(dut_skt) 
    print (QCstatus, "Badchips:", badchips)

    if "PASS" not in QCstatus :
        duts, dut_skt, bad_dut_order, ids_goods, ids_bads= MovetoTray(duts, dut_skt, QCstatus, badchips, bad_dut_order) 
        if len(badchips) > 0:
            skts=badchips
        ids_dict_bad.update(ids_bads)
    else: #PASS
        duts, dut_skt, bad_dut_order, ids_goods, ids_bads = MovetoTray(duts, dut_skt, QCstatus, badchips, bad_dut_order) 
        print ("PASS", dut_skt)
        ids_dict.update(dut_skt)
        ids_dict_good.update(ids_goods)
        ids_dict_bad.update(ids_bads)
        dut_skt = {}
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
rts_msg = manip.read_rtsmsgfp()
manip.manip_extract(rts_r, rts_msg)
print ("Done")






