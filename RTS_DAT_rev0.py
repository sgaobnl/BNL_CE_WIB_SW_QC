import sys 
import os
import subprocess
import time 
import random


#start robot
from RTS_CFG import RTS_CFG
from rts_ssh_LArASIC import DAT_power_off
from rts_ssh_LArASIC import Sinkcover
from rts_ssh_LArASIC import rts_ssh_LArASIC

############################################################
trayid = "b001t0001"
status = 0
print ("start trayID: {}".format(trayid))
#duts = list(range(0,90,1))
duts = list(range(0,8,1))
duts = sorted(duts)
ids_dict = {}
skts=[0,1,2,3,4,5,6,7]
trayno =2
badtrayno = 1 #some issue with tray#1
bad_dut_order=0
datno =2
rootdir = "C:/DAT_LArASIC_QC/Tested/"
if not os.path.exists(rootdir):
    try:
        os.makedirs(rootdir)
    except OSError:
        print ("Error to create folder %s"%rootdir)
        sys.exit()

############################################################

rts = RTS_CFG()
rts.rts_init(port=2001, host_ip='192.168.0.2')

#rts.MoveChipFromTrayToSocket(2, 1, 1, 2, 1)    
#rts.MoveChipFromSocketToTray(2, 1, 2, 1, 1)
#rts.MoveChipFromSocketToTray(2, 12, 2, 1, 1)
#rts.MoveChipFromTrayToTray(2, 2, 2, 1, 2,2)    
#rts.MoveChipFromTrayToTray(2, 2, 1, 1, 2,1)    
#rts.MoveChipFromTrayToTray(1, 2, 2, 2, 2,2)    
#rts.MoveChipFromTrayToTray(1, 2, 1, 2, 2,1)    
#
#rts.PumpOff()
#rts.rts_shutdown()
#rts.rts_idle()
#exit()

def MovetoSoket(duts,ids_dict, skts=[0,1,2,3,4,5,6,7]) :
    dut_skt = {}
    if True:
        #make sure DAT is powered off
        DAT_power_off()

        ids_load = []
        dut_run = []
        for skt in skts:
            if len(duts)>0:
                chipi = duts[0]
                duts=duts[1:]
            else:
                ids_g = list(ids_dict.keys())
                chipi = dut_ps[ids[ids_g[skt]]]

            trayc=(chipi%15) +1
            trayr=(chipi//15) +1
            sktn = skt + 1
            status = rts.MoveChipFromTrayToSocket(trayno, trayc, trayr, datno, sktn)    
            if status < 0:
                print("Error moving chips, exit anyway. Please check!")
                rts.rts_shutdown()
                return "ERROR", str(status)
                #exit()
                #break
            dut_run.append(chipi)
            ids_load.append(rts.msg)
            dut_skt[rts.msg] = chipi
        rts.rts_idle()
    else:#debug only
        ids_load=["20240613052421","20240613052422","20240613052423","20240613052424","20240613052425","20240613052426","20240613052427","20240613052428"]
        dut_run = [0, 1, 2, 3, 4, 5, 6, 7]
        for i in range(8):
            dut_skt[ids_load[i]] = dut_run[i]
    return duts, dut_skt

def DAT_QC(dut_skt) :
#    print ("ChIP ID under testing", dut_run)
    Sinkcover()
    while True:
        QCresult = rts_ssh_LArASIC(dut_skt, root=rootdir)
        if QCresult != None:
            QCstatus = QCresult[0]
            badchips = QCresult[1]
            break
        else:
            print ("139-> terminate, 2->debugging")
            userinput = input ("Please contatc tech coordinator")
            try:
                usercode = int(userinput)
                if usercode == 139:
                    QCstatus = "Terminate"
                    badchips = []
                    break
                elif usercode == 2:
                    print ("debugging...")
            except:
                print ("please input a number")
                pass
    return QCstatus, badchips

################STEP3#################################
#def MovetoTray(duts, ids_load, dut_run, QCstatus, badchips) 
def MovetoTray(duts, dut_skt, QCstatus, badchips) :
    print ("ChIP ID back to tray")
    ids_load = list(dut_skt.keys())
    dut_run = []
    for ids in ids_load:
        dut_run.append(dut_skt[ids])

    if "Terminate" in QCstatus: #move back to original positions
        for skt in range(8):
            chipi=dut_run[skt]
            trayc=(chipi%15) +1
            trayr=(chipi//15) +1
            sktn = skt + 1
            status = rts.MoveChipFromSocketToTray(datno, sktn, trayno, trayc, trayr)
            if status < 0:
                print("Error moving chips, exit anyway. Please check!")
                rts.rts_shutdown()
                return "ERROR", str(status)
                #exit()
        if status > 0: #good to go
            rts.PumpOff()
            rts.rts_shutdown()
            return "ERROR", str(status)
            #print (")XXXXXXXXXXXXXX")

        duts = dut_run + duts
        return duts, {}
    else:
        if "Code#" in QCstatus:
            for skt in badchips:
                chipi=dut_run[skt]
                trayc=(chipi%15) +1
                trayr=(chipi//15) +1
                sktn = skt + 1
                ids_load.remove(ids_load[skt-8])
                trayc=(bad_dut_order%15) +1
                trayr=(bad_dut_order//15) +1
                bad_dut_order +=1
                status = rts.MoveChipFromSocketToTray(datno, sktn, badtrayno, trayc, trayr)
                if status < 0:
                    print("Error moving chips, exit anyway. Please check!")
                    rts.rts_shutdown()
                    return "ERROR", str(status)
                    #exit()
            dut_skt_r = {}
            for ids in ids_load:
                dut_skt_r[ids] = dut_skt[ids]
            return duts,dut_skt_r

        if "PASS" in QCstatus:
            for skt in range(8):
                chipi=dut_run[skt]
                trayc=(chipi%15) +1
                trayr=(chipi//15) +1
                sktn = skt + 1
                if skt in badchips:
                    ids_load.remove(ids_load[skt-8])
                    trayc=(bad_dut_order%15) +1
                    trayr=(bad_dut_order//15) +1
                    bad_dut_order +=1
                    status = rts.MoveChipFromSocketToTray(datno, sktn, badtrayno, trayc, trayr)
                else:
                    status = rts.MoveChipFromSocketToTray(datno, sktn, trayno, trayc, trayr)

                if status < 0:
                    print("Error moving chips, exit anyway. Please check!")
                    rts.rts_shutdown()
                    return "ERROR", str(status)
                    #exit()
            dut_skt_r = {}
            for ids in ids_load:
                dut_skt_r[ids] = dut_skt[ids]
            return duts, dut_skt_r


#first run
################STEP1#################################
duts, dut_skt = MovetoSoket(duts,ids_dict, skts=skts) 
if duts != "ERROR":
    ################STEP2#################################
    #ids=ids.update(dut_skt)
    while len(duts) > 0:
        QCstatus, badchips = DAT_QC(dut_skt) 
    
        if "PASS" not in QCstatus :
            duts, dut_skt_r = MovetoTray(duts, dut_skt, QCstatus, badchips) 
            if duts != "ERROR":
                if len(badchips) > 0:
                    duts, dut_skt = MovetoSoket(duts,ids_dict, skts=badchips) 
                    if duts != "ERROR":
                        pass
                    else:
                        break
                    dut_skt=dut_skt.update(dut_skt_r)
            else:
                break
        else:
            duts, dut_skt_r = MovetoTray(duts, dut_skt, QCstatus, badchips) 
            if duts != "ERROR":
                pass
            else:
                break
            dut_skt=dut_skt.update(dut_skt_r)
            ids_dict=ids_dict.update(dut_skt_r)
            duts, dut_skt = MovetoSoket(duts,ids_dict, skts=skts) 
            if duts != "ERROR":
                pass
            else:
                break


    rts.rts_idle()

print (ids_dict())
ids_k = list(ids_dict.keys())
fp = rootdir + ids_k[0] + "_log.bin"
with open(fp, 'wb') as fn:
    pickle.dump(datad, fn)

print ("Done")
#####classify
#if len(chip_failed) > 0:
#    for i in chip_failed:
#        dut_fs.append(dut_run[i])
#
#for i in chip_passed: #only all chips pass QC can be treated a good run (at this moment)
#    dut_ps.append(dut_run[i])
#print ("One run")
#print (duts)
#print (dut_ps)
#print (dut_fs)
#print ("One run Done")






#            for skt in range(8):
#                chipi=dut_run[skt]
#                trayc=(chipi%15) +1
#                trayr=(chipi//15) +1
#                sktn = skt + 1
#                if skt in badchips:
#                    trayc=(bad_dut_order%15) +1
#                    trayr=(bad_dut_order//15) +1
#                    bad_dut_order +=1
#                    status = rts.MoveChipFromSocketToTray(datno, sktn, badtrayno, trayc, trayr)
#                else:
#                    duts = sorted([dut_run[skt]] + duts)
#                    status = rts.MoveChipFromSocketToTray(datno, sktn, trayno, trayc, trayr)
#                if status < 0:
#                    print("Error moving chips, exit anyway. Please check!")
#                    rts.rts_shutdown()
#                    exit()
#
#
#
#
#
#
#            for skt in badchips:
#                chipi=dut_run[skt]
#                trayc=(chipi%15) +1
#                trayr=(chipi//15) +1
#                sktn = skt + 1
#                trayc=(bad_dut_order%15) +1
#                trayr=(bad_dut_order//15) +1
#                bad_dut_order +=1
#                status = rts.MoveChipFromSocketToTray(datno, sktn, badtrayno, trayc, trayr)
#                if status < 0:
#                    print("Error moving chips, exit anyway. Please check!")
#                    rts.rts_shutdown()
#                    exit()
#            skts = badchips
#            return QCstatus, duts, skts
#            #break
#
#
#
#
#    for skt in range(8):
#        chipi=dut_run[skt]
#        trayc=(chipi%15) +1
#        trayr=(chipi//15) +1
#        sktn = skt + 1
#        if skt in chip_failed:
#            trayc=(bad_dut_order%15) +1
#            trayr=(bad_dut_order//15) +1
#            bad_dut_order +=1
#            status = rts.MoveChipFromSocketToTray(datno, sktn, badtrayno, trayc, trayr)
#        else:
#            status = rts.MoveChipFromSocketToTray(datno, sktn, trayno, trayc, trayr)
#        if status < 0:
#            print("Error moving chips, exit anyway. Please check!")
#            rts.rts_shutdown()
#            exit()
#            #break
#    if status > 0: #good to go
#        rts.PumpOff()



