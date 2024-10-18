import sys 
import os
import subprocess
import time 
import datetime
import random
import pickle
from DAT_read_cfg import dat_read_cfg
import filecmp
from colorama import just_fix_windows_console
just_fix_windows_console()

wibip = "192.168.121.123"
wibhost = "root@{}".format(wibip)

#start robot
from rts_ssh import subrun
from rts_ssh import rts_ssh
from rts_ssh import DAT_power_off

try:
    chiptype = int (input ("Chips under test. 1-FE, 2-ADC, 3-CD: "))
    if chiptype > 0 and chiptype <= 3:
        pass
    else:
        print ("Wrong number, please input number between 1 to 3")
        print ("exit anyway")
        exit()
except:
    print ("Not a number, please input number between 1 to 3")
    print ("exit anyway")
    exit()

if chiptype == 1:
    duttype = "FE"
    rootdir = "D:/DAT_LArASIC_QC/Tested/"
elif chiptype == 2:
    duttype = "ADC"
    rootdir = "D:/DAT_ADC_QC/Tested/"
elif chiptype == 3:
    duttype = "CD"
    rootdir = "D:/DAT_CD_QC/Tested/"


pc_wrcfg_fn = "./asic_info.csv"
############################################################

def DAT_QC(dut_skt, duttype="FE") :
    while True:
        QCresult = rts_ssh(dut_skt, root=rootdir, duttype=duttype)
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


if True:
    print (datetime.datetime.utcnow(), " : Check if WIB is pingable (it takes < 60s)" )
    timeout = 10 
    command = ["ping", wibip]
    print ("COMMAND:", command)
    for i in range(6):
        result = subrun(command=command, timeout=timeout, exitflg=False)
        if i == 5:
            print ("Please check if WIB is powered and Ethernet connection,exit anyway")
            exit()
        log = result.stdout
        chk1 = "Reply from {}: bytes=32".format(wibip)
        chk2p = log.find("Received =")
        chk2 =  int(log[chk2p+11])
        if chk1 in log and chk2 >= 1:  #improve it later
            print (datetime.datetime.utcnow(), "\033[92m  : SUCCESS!  \033[0m")
            break

while True:#
    ynstr = input("\033[93m  Please open the box to check if all LEDs OFF! (Y/N) \033[0m")
    if "Y" in ynstr or "y" in ynstr:
        break
    else:
        print (datetime.datetime.utcnow(), " : Power DAT down (it takes < 60s)")
        command = ["ssh", wibhost, "cd BNL_CE_WIB_SW_QC; python3 top_femb_powering.py off off off off"]
        result=subrun(command, timeout = 60)
        if "Done" in result.stdout:
            print (datetime.datetime.utcnow(), "\033[92m  : SUCCESS!  \033[0m")
        else:
            print ("FAIL!")
            print (result.stdout)
            print ("Exit anyway")
            exit()

if True:
    ynstr = "Y"
    if "Y" in ynstr or "y" in ynstr:
        while True:#
            print (datetime.datetime.utcnow(), "\033[93m   : Please put chips into the sockets carefully \033[0m")
            print ("Please update chip serial numbers")
            command = ["notepad.exe", pc_wrcfg_fn]
            result=subrun(command, timeout = None, check=False)
            from DAT_chk_cfgfile import dat_chk_cfgfile
            pf= dat_chk_cfgfile(fcfg = pc_wrcfg_fn, duttype=duttype )
            if pf:
                break

if True:
    print ("later use pyqt to pop out a configuration windows")
    print (datetime.datetime.utcnow(), " : load configuration file from PC")

    wibdst = "{}:/home/root/BNL_CE_WIB_SW_QC/".format(wibhost)
    command = ["scp", "-r", pc_wrcfg_fn , wibdst]
    result=subrun(command, timeout = None)

    wibsrc = "{}:/home/root/BNL_CE_WIB_SW_QC/asic_info.csv".format(wibhost)
    pcdst = "./readback/"
    command = ["scp", "-r", wibsrc , pcdst]
    result=subrun(command, timeout = None)
    pc_rbcfg_fn = pcdst + "asic_info.csv"

    logsd, fdir =  dat_read_cfg(infile_mode=True,  froot = pc_rbcfg_fn)

    result = filecmp.cmp(pc_wrcfg_fn, pc_rbcfg_fn)
    if result:
        print (datetime.datetime.utcnow(), "\033[92m  : SUCCESS!  \033[0m")
    else:
        print ("FAIL!")
        print ("Exit anyway")
        exit()

now = datetime.datetime.utcnow()
dut0 = int(now.strftime("%Y%m%d%H%M%S"))&0xFFFFFFFFFFFFFFFF
################STEP1#################################
skts=[0,1,2,3,4,5,6,7]
dut_skt = {str(dut0):(0,1), str(dut0+1):(0,2), str(dut0+2):(0,3), str(dut0+3):(0,4), str(dut0+4):(0,5), str(dut0+5):(0,6), str(dut0+6):(0,7), str(dut0+7):(0,8) }
QCstatus, badchips = DAT_QC(dut_skt, duttype) 

if "PASS" in QCstatus :
    print (QCstatus)
    print ("Well done, please move chips back to tray.")
elif ("Code#E001" in QCstatus) or ("Terminate" in QCstatus) :
    print (QCstatus, badchips)
    DAT_power_off()
    print ("Please contact the tech coordinator")
elif "Code#" in QCstatus:
    DAT_power_off()
    print (QCstatus, badchips)
    if len(badchips) > 0:
        for bc in badchips:
            print ("chip%d (1-8) is bad, please move it to bad tray and replace it with a new chip"%(bc+1))
            while True:
                ytstr = input ("Replace (y/n?): ")
                if "Y" in ytstr or "y" in ytstr:
                    break
        print ("please restart the test script")
    else:
        print ("Please contact the tech coordinator")
    
