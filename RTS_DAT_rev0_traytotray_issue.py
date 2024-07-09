import sys 
import subprocess
import time 


from RTS_CFG import RTS_CFG

rts = RTS_CFG()
rts.rts_init(port=2001, host_ip='192.168.0.2')

trayid = "b001t0001"

status = 0
print ("start trayID: {}".format(trayid))


chipi = 0
#duts = list(range(0,90,1))
duts = list(range(0,10,1))
dut_ps = [] 
dut_fs = []

#rts.MoveChipFromTrayToTray(2, 1, 1, 1, 1,1)    
#rts.MoveChipFromTrayToTray(2, 15, 1, 1, 15,1)    
#rts.MoveChipFromTrayToTray(2, 15, 6, 2, 15,6)    
#rts.MoveChipFromTrayToTray(2, 15, 6, 1, 15,6)    
#rts.MoveChipFromTrayToTray(1, 15, 6, 2, 15,6)    
#rts.MoveChipFromTrayToTray(2, 15, 6, 1, 15,6)    
#rts.MoveChipFromTrayToTray(1, 15, 6, 2, 15,6)    
#rts.MoveChipFromTrayToTray(2, 1, 6, 1, 1,6)    
#rts.MoveChipFromSocketToTray(2, 12, 2, 1, 1)
#rts.MoveChipFromTrayToTray(2, 2, 2, 1, 2,2)    
#rts.MoveChipFromTrayToTray(2, 2, 1, 1, 2,1)    
#rts.MoveChipFromTrayToTray(1, 1, 1, 2, 1,1)    
#rts.MoveChipFromTrayToTray(1, 2, 1, 2, 2,1)    
#rts.MoveChipFromSocketToTray(2, 1, 2, 1, 1)
#rts.MoveChipFromTrayToSocket(1, 2, 2, 2, 1)    
#
#rts.PumpOff()
#rts.rts_shutdown()
rts.rts_idle()
exit()

trayno =2
badtrayno = 2 #some issue with tray#1
datno =2

ids = []
while len(duts) > 0:
################STEP1#################################
    if True:
    #move 8 chips to socket
        dut_run = []
        for skt in range(8):
            if len(duts)>0:
                chipi = duts[0]
                duts=duts[1:]
            else:
                chipi = dut_ps[skt]

            dut_run.append(chipi)
            trayc=(chipi%15) +1
            trayr=(chipi//15) +1
            sktn = skt + 1
            status = rts.MoveChipFromTrayToSocket(trayno, trayc, trayr, datno, sktn)    
            if status < 0:
                print("Error moving chips, exit anyway. Please check!")
                rts.rts_shutdown()
                exit()
                #break
            ids.append(rts.msg)
        if status > 0: #good to go
            rts.PumpOff() #pump off

        #rts.rts_idle()
        #exit()

################STEP2#################################
    #dut_run = [0, 1, 2, 3, 4, 5, 6, 7]
    print ("ChIP ID under testing", dut_run)
    #######run the testing...##########
    chip_passed = [0,1,2,3,4,5,6,7]
    chip_failed = []
    #for i in range(8):
    #    x = input("chip#{} pass?".format(i))
    #    if "Y" in x or "y" in x:
    #        chip_passed.append(i)
    #    else:
    #        chip_failed.append(i)
    #print ("PASS", chip_passed)
    #print ("FAIL", chip_failed)

    #move 8 chips back to tray

################STEP3#################################
    print ("ChIP ID back to tray", dut_run)
    for skt in range(8):
        chipi=dut_run[skt]
        trayc=(chipi%15) +1
        trayr=(chipi//15) +1
        sktn = skt + 1
        if skt in chip_failed:
            status = rts.MoveChipFromSocketToTray(datno, sktn, badtrayno, trayc, trayr)
        else:
            status = rts.MoveChipFromSocketToTray(datno, sktn, trayno, trayc, trayr)
        if status < 0:
            print("Error moving chips, exit anyway. Please check!")
            rts.rts_shutdown()
            exit()
            #break
    if status > 0: #good to go
        rts.PumpOff()

    ####classify
    if len(chip_failed) > 0:
        tmp = [ dut_run[i] for i in chip_passed] 
        duts=tmp + duts
        for i in chip_failed:
            dut_fs.append(dut_run[i])

    else:
        for i in chip_passed: #only all chips pass QC can be treated a good run (at this moment)
            dut_ps.append(dut_run[i])
    print ("One run")
    print (duts)
    print (dut_ps)
    print (dut_fs)
    print ("One run Done")


rts.rts_idle()



