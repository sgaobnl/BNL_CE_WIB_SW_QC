import time
import sys
import subprocess
import datetime
import filecmp
import os

DUT = "LArASIC"
rawdata_dir = "./tmp_data/" #path to save raw data at PC
wib_raw_dir = "./tmp_data/"#path to save raw data at PC
fdir = """/home/root/BNL_CE_WIB_SW_QC/tmp_data/FE_403000001_403000002_403000003_403000004_403000005_403000006_403000007_403000008/"""
wib_raw_dir = fdir
pc_raw_dir = "./tmp_data/FE_403000001_403000002_403000003_403000004_403000005_403000006_403000007_403000008/"

def subrun(command, timeout = 30, check=True, exitflg = True):
    try:
        result = subprocess.run(command,
                                capture_output=True,
                                text=True,
                                timeout=timeout,
                                shell=True,
                                #stdout=subprocess.PIPE,
                                #stderr=subprocess.PIPE,
                                check=check
                                )
    except subprocess.CalledProcessError as e:
        print ("Call Error", e.returncode)
        if exitflg:
            print ("Call Error FAIL!")
            print ("Exit anyway")
            exit()

        #continue
    except subprocess.TimeoutExpired as e:
        print ("No reponse in %d seconds"%(timeout))
        if exitflg:
            print (result.stdout)
            print ("Timoout FAIL!")
            print ("Exit anyway")
            exit()

        #continue
    return result

#if True:#set the wib
if False: #sync WIB time
    print (datetime.datetime.utcnow(), " : Check if WIB is pingable (it takes < 60s)" )
    timeout = 10 
    command = ["ping", "192.168.121.123"]
    print ("COMMAND:", command)
    for i in range(6):
        result = subrun(command=command, timeout=timeout, exitflg=False)
        if i == 5:
            print ("Please check if WIB is powered and Ethernet connection,exit anyway")
            exit()
        log = result.stdout
        chk1 = "Reply from 192.168.121.123: bytes=32"
        chk2p = log.find("Received =")
        chk2 =  int(log[chk2p+11])
        if chk1 in log and chk2 >= 1:  #improve it later
            print (datetime.datetime.utcnow(), " : SUCCESS!")
            break


#if True:#load bin file
if False: #sync WIB time
    print (datetime.datetime.utcnow(), " : Load WIB bin file(it takes < 30s)" )
    command = ["ssh", "root@192.168.121.123", "fpgautil -b /boot/wib_top_0506.bin"]
    result=subrun(command, timeout = 30)
    if "BIN FILE loaded through FPGA manager successfully" in result.stdout:
        print (datetime.datetime.utcnow(), " : SUCCESS!")

if False:
    print (datetime.datetime.utcnow(), " : Start WIB initialization (it takes < 30s)")
    command = ["ssh", "root@192.168.121.123", "cd BNL_CE_WIB_SW_QC; alias python=python3; python3 wib_startup.py"]
    result=subrun(command, timeout = 30)
    if "Done" in result.stdout:
        print (datetime.datetime.utcnow(), " : SUCCESS!")
    else:
        print ("FAIL!")
        print (result.stdout)
        print ("Exit anyway")
        exit()


#if True: #sync WIB time
if False: #sync WIB time
    print (datetime.datetime.utcnow(), " : sync WIB time")
    # Get the current date and time
    now = datetime.datetime.utcnow()
    # Format it to match the output of the `date` command
    formatted_now = now.strftime('%a %b %d %H:%M:%S UTC %Y')
    command = ["ssh", "root@192.168.121.123", "date -s \'{}\'".format(formatted_now)]
    result=subrun(command, timeout = 30)

    print ("WIB Time: ", result.stdout)
    print (datetime.datetime.utcnow(), " : SUCCESS!")


if False:
    print ("later use pyqt to pop out a configuration windows")
    input ("anykey to continue now")
    print (datetime.datetime.utcnow(), " : load configuration file from PC")

    pcsrc = "./asic_info.csv"
    wibdst = "root@192.168.121.123:/home/root/BNL_CE_WIB_SW_QC/"
    command = ["scp", "-r", pcsrc , wibdst]
    result=subrun(command, timeout = None)

    wibsrc = "root@192.168.121.123:/home/root/BNL_CE_WIB_SW_QC/asic_info.csv"
    pcdst = "./readback/"
    command = ["scp", "-r", wibsrc , pcdst]
    result=subrun(command, timeout = None)

    pcdstfn = pcdst + "asic_info.csv"

    result = filecmp.cmp(pcsrc, pcdstfn)
    if result:
        print (datetime.datetime.utcnow(), " : SUCCESS!")
    else:
        print ("FAIL!")
        print ("Exit anyway")
        exit()

if False:
    print (datetime.datetime.utcnow(), " : Start DUT (%s) quick checkout.(takes < 60s)"%DUT)
    if "LArASIC" in DUT:
        command = ["ssh", "root@192.168.121.123", "cd BNL_CE_WIB_SW_QC; python3 DAT_LArASIC_QC_top.py -t 0"]
    result=subrun(command, timeout = 100)
    resultstr = result.stdout
    if "Pass init check" in result.stdout:
        print (datetime.datetime.utcnow(), " : SUCCESS!")
    else:
        print ("FAIL!")
        print (result.stdout)
        print ("Exit anyway")
        exit()

    print ("Transfer data to server...")
    fdir = resultstr[resultstr.find("save_fdir_start_")+16:resultstr.find("_end_save_fdir")] 
    wib_raw_dir = fdir #later save it into log file
    fs = resultstr[resultstr.find("save_file_start_")+16:resultstr.find("_end_save_file")] 
    fsubdirs = fdir.split("/")
    fn = fs.split("/")[-1]
    fddir =rawdata_dir + fsubdirs[-2] + "/" 
    pc_raw_dir = fddir #later save it into log file

    if not os.path.exists(fddir):
        try:
            os.makedirs(fddir)
        except OSError:
            print ("Error to create folder %s"%save_dir)
        sys.exit()

    wibhost = "root@192.168.121.123:"
    fsrc = wibhost + fs
    command = ["scp", "-r",fsrc , fddir]
    result=subrun(command, timeout = None)
    print ("SUCCESS! save data at: %s"%(fddir+fn))


if True:
#if False:
    print (datetime.datetime.utcnow(), " : Start DUT (%s) QC(takes ~ 1200s)"%DUT)
    if "LArASIC" in DUT:
        command = ["ssh", "root@192.168.121.123", "cd BNL_CE_WIB_SW_QC; python3 DAT_LArASIC_QC_top.py"]

    p = subprocess.Popen(command, 
                         shell = True,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         universal_newlines=True
                         )
   #from subprocess import Popen
    #from subprocess import PIPE
    while p.poll() is None:  # Continue loop until the subprocess terminates
#    if True:
        print ("wait for 1 seconds")
        #time.sleep(10)
        print ("check if WIB data updates...")
        cmd2 = ["ssh", "root@192.168.121.123", "cd BNL_CE_WIB_SW_QC; python3 file_walk.py %s"%wib_raw_dir]
        p1 = subprocess.Popen(cmd2,
                   shell = True,
                   start_new_session=True,
                   stdout=subprocess.PIPE,
                   stderr=subprocess.PIPE,
                   universal_newlines=True
                )
        #p1.poll()
        #p1.wait()
        try:
            result = p1.communicate(timeout = 5)
            print ("A")
        except TimeoutExpired:
            p1.kill()
            result = p1.communicate()
            print ("B")
        print (result)
        #resultstr = p1.stdout.read()
        resultstr = result.read()
        #print (resultstr)
        wibfns = {}
        for line in resultstr.splitlines():        
            if "ROOT" not in line:
                wibfns[line.split(":")[0]] = line.split(":")[1]
            else:
                wibsrc = line.split(":")[1]

        print ("BBB")
        cmd3 = ["python", "file_walk.py", "%s"%pc_raw_dir]
        p2 = subprocess.Popen(cmd3,
                   shell = True,
                   start_new_session=True,
                   stdout=subprocess.PIPE,
                   stderr=subprocess.PIPE,
                   universal_newlines=True
                )
        #p2.poll()
        #p2.wait()
        p2.communicate()
        resultstr = p2.stdout.read()
        print ("P2")
        pcfns = {}
        for line in resultstr.splitlines():        
            if "ROOT" not in line:
                pcfns[line.split(":")[0]] = line.split(":")[1]
            else:
                pcdst = line.split(":")[1]

        newfns = {} 
        wibfns_keys = wibfns.keys()
        pcfns_keys = pcfns.keys()
        for key in wibfns_keys:
            if key in pcfns_keys:
                pass
            else:
                #print ("Transfer %s on WIB to PC"%wibfns[key])
                src = wibfns[key]
                wibhost = "root@192.168.121.123:"
                src = wibhost + src
                command = ["scp", "-r", src , pcdst]
                result=subrun(command, timeout = None)

#        cmd2= ["ssh", "root@192.168.121.123", "cd %s; ls"%wib_raw_dir]
#        try:
#            result = subprocess.run(cmd2, 
#                               capture_output=True,
#                               timeout = 100,
#                               text=True,
#                               check=True
#                               )
#        except subprocess.CalledProcessError as e:
#            print ("Fail", e.returncode)
#            print ("Exit anyway")
#            exit()
#        #print (datetime.datetime.utcnow(), " : SUCCESS!")
#        resultstr = result.stdout
#        print (resultstr)
#
        #output_line = p.stdout.readline()
        #if output_line == '' :
        #print ("sleep")
        #time.sleep(0.2)
        #if output_line:
        #    print("STDOUT:", output_line.strip())
    print ("hellllllll")
    p.wait()

#    resultstr = result.stdout
#    if "Pass init check" in result.stdout:
#        print (datetime.datetime.utcnow(), " : SUCCESS!")
#    else:
#        print ("FAIL!")
#        print (result.stdout)
#        print ("Exit anyway")
#        exit()
#
#    print ("Transfer data to server...")
#    fdir = resultstr[resultstr.find("save_fdir_start_")+16:resultstr.find("_end_save_fdir")] 
#    fs = resultstr[resultstr.find("save_file_start_")+16:resultstr.find("_end_save_file")] 
#    #fdir = """/home/root/BNL_CE_WIB_SW_QC/tmp_data/FE_403000001_403000002_403000003_403000004_403000005_403000006_403000007_403000008/"""
#    #fs = """/home/root/BNL_CE_WIB_SW_QC/tmp_data/FE_403000001_403000002_403000003_403000004_403000005_403000006_403000007_403000008/QC_INIT_CHK.bin"""
#    fsubdirs = fdir.split("/")
#    fn = fs.split("/")[-1]
#    fddir =rawdata_dir + fsubdirs[-2] + "/"
#    if not os.path.exists(fddir):
#        try:
#            os.makedirs(fddir)
#        except OSError:
#            print ("Error to create folder %s"%save_dir)
#        sys.exit()
#
#
#    wibhost = "root@192.168.121.123:"
#    fsrc = wibhost + fs
#    command = ["scp", "-r",fsrc , fddir]
#    #print (command)
#    try:
#       result = subprocess.run(command,
#                                text = True,
#                                capture_output=True,
#                                check=True
#                                )
#    except subprocess.CalledProcessError as e:
#        print ("Fail to send CFG file to WIB", e.returncode)
#        print ("Exit anyway")
#        exit()
#    print ("SUCCESS! save data at: %s"%(fddir+fn))
#


if False:
    print (datetime.datetime.utcnow(), " : Start WIB initialization")

    p = subprocess.Popen(["ssh", "root@192.168.121.123", "cd BNL_CE_WIB_SW_QC; python3 testaa.py"],
                            shell=False,
                            text = True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE
                            )
    
    # Read and print output line by line in real-time
    while p.poll() is None:  # Continue loop until the subprocess terminates
        print ( time.time_ns() - t0)
        time.sleep(1)
    # Wait for the subprocess to finish
    
    p.wait()
    for line in p.stdout:
        print (line.strip())


if False:
    command = ["scp", "-r", "root@192.168.121.123:/home/root/BNL_CE_WIB_SW_QC/scp2.txt", "./reports/"]
    try:
       result = subprocess.run(command,
                                shell=False,
                                text = True,
                                capture_output=True,
                                #stdin=subprocess.PIPE,
                                #stdout=subprocess.PIPE,
                                #stderr=subprocess.PIPE,
                                check=True
                                )
    except subprocess.CalledProcessError as e:
        print (e.returncode)
#        print (subprocess.returncode)
    print (result.stdout)

