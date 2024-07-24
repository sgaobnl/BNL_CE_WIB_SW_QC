import sys 
import os
import subprocess
import time 
import random
import pickle

#start robot
from rts_ssh_LArASIC import rts_ssh_LArASIC

rootdir = "D:/DAT_LArASIC_QC/Tested/"

############################################################

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


################STEP1#################################
skts=[0,1,2,3,4,5,6,7]
dut_skt = {"DUT1":(0,1), "DUT2":(0,2), "DUT3":(0,3), "DUT4":(0,4), "DUT5":(0,5), "DUT6":(0,6), "DUT7":(0,7), "DUT8":(0,8) }
QCstatus, badchips = DAT_QC(dut_skt) 
print (QCstatus, badchips)







