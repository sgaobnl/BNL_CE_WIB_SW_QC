import sys 
import subprocess
import time 


from RTS_CFG import RTS_CFG

rts = RTS_CFG()
rts.rts_init(port=2001, host_ip='192.168.0.2')

trayid = "b001t0001"

status = 0
print "start trayID: {}".format(trayid)


chipi = 0
duts = list(range(0,90,1))
dut_ps = [] 
dut_fs = []

trayno =2
datno =2

while len(duts) > 0:
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
        rts.MoveChipFromTrayToSocket(trayno, trayc, trayr, datno, skt)    
    print ("ChIP ID under testing", dut_run)

    #######run the testing...##########
    for i in range(8):
        x = input("chip#{} pass?".format(i))
        if "Y" in x or "y" in x:
            chip_passed.append(i)
        else:
            chip_failed.append(i)
    print ("PASS", chip_passed)
    print ("FAIL", chip_failed)

    #move 8 chips back to tray
    print ("ChIP ID back to tray", dut_run)
    for skt in range(8):
        chipi=dut_run[skt]
        trayc=(chipi%15) +1
        trayr=(chipi//15) +1
        rts.MoveChipFromSocketToTray(datno, skt, trayno, trayc, trayr)

    ####classify
    if len(chip_failed) > 0:
        tmp = [ dut_run[i] for i in chip_passed] 
        duts=tmp + duts
        for i in chip_faied:
            dut_fs.append(dut_run[i])

    else:
        for i in chip_passed: #only all chips pass QC can be treated a good run (at this moment)
            dut_ps.append(dut_run[i])
    print ("One run")
    print (duts)
    print (duts_ps)
    print (duts_fs)
    print ("One run Done")


rts.rts_close()



