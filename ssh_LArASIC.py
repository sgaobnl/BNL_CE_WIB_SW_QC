import time
import sys
import subprocess
import datetime
import filecmp
import pickle
import os
from DAT_read_cfg import dat_read_cfg

from colorama import just_fix_windows_console
just_fix_windows_console()

QC_TST_EN =  True 
if "Y" in ynstr or "y" in ynstr:
    QC_TST_EN =  False

logs = {}
logs['PC_rawdata_root'] = "D:/DAT_LArASIC_QC/Tested2/" #path to save raw data at PC
logs['PC_WRCFG_FN'] = "./asic_info.csv"

#[0, 1, 2, 3, 4,5,61, 62, 63, 64, 7,8, 9]
tms_items = {}
tms_items[0 ] = "\033[96m 0 : Initilization checkout (not selectable for itemized test item) \033[0m"
tms_items[1 ] = "\033[96m 1 : FE power consumption measurement  \033[0m"
tms_items[2 ] = "\033[96m 2 : FE response measurement checkout  \033[0m" 
tms_items[3 ] = "\033[96m 3 : FE monitoring measurement  \033[0m"
tms_items[4 ] = "\033[96m 4 : FE power cycling measurement  \033[0m"
tms_items[5 ] = "\033[96m 5 : FE noise measurement  \033[0m"
tms_items[61] = "\033[96m 61: FE calibration measurement (ASIC-DAC)  \033[0m"
tms_items[62] = "\033[96m 62: FE calibration measurement (DAT-DAC) \033[0m"
tms_items[63] = "\033[96m 63: FE calibration measurement (Direct-Input) \033[0m"
tms_items[64] = "\033[96m 64: FE calibration measurement ((ASIC-DAC, 4.7mV/fC) \033[0m"
tms_items[7 ] = "\033[96m 7 : FE delay run  \033[0m"
tms_items[8 ] = "\033[96m 8 : FE cali-cap measurement \033[0m"
tms_items[9 ] = "\033[96m 9 : Turn DAT off \033[0m"
tms_items[10] = "\033[96m 10: Turn DAT (on WIB slot0) on without any check\033[0m"
tms=list(tms_items.keys())
logs['tms_items'] = tms_items


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

while QC_TST_EN:#
#while True:#
#while False:#
    ynstr = input("\033[93m  Please open the box to check if all LEDs OFF! (Y/N) \033[0m")
    if "Y" in ynstr or "y" in ynstr:
        break
        logs['DAT_init_power_status'] = "DAT is powered off"
    else:
        print (datetime.datetime.utcnow(), " : Power DAT down (it takes < 60s)")
        command = ["ssh", "root@192.168.121.123", "cd BNL_CE_WIB_SW_QC; python3 top_femb_powering.py off off off off"]
        result=subrun(command, timeout = 60)
        if "Done" in result.stdout:
            print (datetime.datetime.utcnow(), "\033[92m  : SUCCESS!  \033[0m")
        else:
            print ("FAIL!")
            print (result.stdout)
            print ("Exit anyway")
            exit()
        logs['DAT_init_power_status'] = result.stdout

if QC_TST_EN:
#if True:
    ynstr = input("\033[93m  new chips? (Y/N) \033[0m")
    tms = list(tms_items.keys())
    if "Y" in ynstr or "y" in ynstr:
        while True:#
            print (datetime.datetime.utcnow(), "\033[93m   : Please put chips into the sockets carefully \033[0m")
            print ("Please update chip serial numbers")
            command = ["notepad.exe", logs['PC_WRCFG_FN']]
            result=subrun(command, timeout = None, check=False)
            from DAT_chk_cfgfile import dat_chk_cfgfile
            pf= dat_chk_cfgfile(fcfg = logs['PC_WRCFG_FN'] )
            if pf:
                logs['New_chips'] = True
                logs['TestIDs'] = tms
                break
    else:
        for key in tms_items.keys():
            print ("TestID_%d: "%key, tms_items[key])
        while True:
            testid = input  ("\033[93m  input a TestID  \033[0m")
            try:
                testid = int(testid)
                if testid not in tms:
                    print ("Wrong Test ID!")
                    continue
                elif testid ==0:
                    print ("Wrong Test ID!")
                    continue
                else:
                    if testid !=9:
                        tms = [testid, 9]
                    else:
                        tms = [testid]
                    logs['New_chips'] = False
                    logs['TestIDs'] = tms
                    break
            except:
                print ("Wrong input format!")

    

if QC_TST_EN:
#if False: #sync WIB time
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
            print (datetime.datetime.utcnow(), "\033[92m  : SUCCESS!  \033[0m")
            break
        logs['WIB_Pingable'] = log


#if False: #sync WIB time
if QC_TST_EN:
    print (datetime.datetime.utcnow(), " : Load WIB bin file(it takes < 30s)" )
    command = ["ssh", "root@192.168.121.123", "fpgautil -b /boot/wib_top_0506.bin"]
    result=subrun(command, timeout = 30)
    if "BIN FILE loaded through FPGA manager successfully" in result.stdout:
        print (datetime.datetime.utcnow(), "\033[92m  : SUCCESS!  \033[0m")
    logs['WIB_bin_file'] = result.stdout

#if False:
if QC_TST_EN:
    print (datetime.datetime.utcnow(), " : Start WIB initialization (it takes < 30s)")
    command = ["ssh", "root@192.168.121.123", "cd BNL_CE_WIB_SW_QC;  python3 wib_startup.py"]
    result=subrun(command, timeout = 30)
    if "Done" in result.stdout:
        print (datetime.datetime.utcnow(), "\033[92m  : SUCCESS!  \033[0m")
    else:
        print ("FAIL!")
        print (result.stdout)
        print ("Exit anyway")
        exit()
    logs['WIB_start_up'] = result.stdout


#if False: 
if QC_TST_EN:
    print (datetime.datetime.utcnow(), " : sync WIB time")
    # Get the current date and time
    now = datetime.datetime.utcnow()
    # Format it to match the output of the `date` command
    formatted_now = now.strftime('%a %b %d %H:%M:%S UTC %Y')
    command = ["ssh", "root@192.168.121.123", "date -s \'{}\'".format(formatted_now)]
    result=subrun(command, timeout = 30)

    print ("WIB Time: ", result.stdout)
    print (datetime.datetime.utcnow(), "\033[92m  : SUCCESS!  \033[0m")
    logs['WIB_UTC_Date_Time'] = result.stdout


#if False: 
#if True:
if QC_TST_EN:
    print ("later use pyqt to pop out a configuration windows")
    #input ("anykey to continue now")
    print (datetime.datetime.utcnow(), " : load configuration file from PC")

    wibdst = "root@192.168.121.123:/home/root/BNL_CE_WIB_SW_QC/"
    command = ["scp", "-r", logs['PC_WRCFG_FN'] , wibdst]
    result=subrun(command, timeout = None)
    logs['CFG_wrto_WIB'] = [command, result.stdout]

    wibsrc = "root@192.168.121.123:/home/root/BNL_CE_WIB_SW_QC/asic_info.csv"
    pcdst = "./readback/"
    command = ["scp", "-r", wibsrc , pcdst]
    result=subrun(command, timeout = None)
    logs['CFG_rbfrom_WIB'] = [command, result.stdout]
    logs['PC_RBCFG_fn'] = pcdst + "asic_info.csv"

    logsd, fdir =  dat_read_cfg(infile_mode=True,  froot = logs['PC_RBCFG_fn'])
    DUT = logsd['DUT']

    result = filecmp.cmp(logs['PC_WRCFG_FN'], logs['PC_RBCFG_fn'])
    if result:
        print (datetime.datetime.utcnow(), "\033[92m  : SUCCESS!  \033[0m")
    else:
        print ("FAIL!")
        print ("Exit anyway")
        exit()

exit()
#if False:
#if True:
if QC_TST_EN:
    print (datetime.datetime.utcnow(), " : Start DUT (%s) QC.(takes < 1200s)"%DUT)
    for testid in tms:
        print ("")
        print ("")
        print (datetime.datetime.utcnow(), " : New Test Item Starts, please wait...")
        print (tms_items[testid])
        if "FE" in DUT:
            command = ["ssh", "root@192.168.121.123", "cd BNL_CE_WIB_SW_QC; python3 DAT_LArASIC_QC_top.py -t {}".format(testid)]
        result=subrun(command, timeout = None) #rewrite with Popen later
        resultstr = result.stdout
        logs["QC_TestItemID_%03d"%testid] = [command, resultstr]
        if "Pass!" in result.stdout:
            print (datetime.datetime.utcnow(), "\033[92m  : SUCCESS!  \033[0m")
        elif "DAT_Power_On" in result.stdout:
            print (datetime.datetime.utcnow(), "\033[92m  : SUCCESS & Turn DAT on!  \033[0m")
            continue
        elif "DAT_Power_Off" in result.stdout:
            print (datetime.datetime.utcnow(), "\033[92m  : SUCCESS & Done!  \033[0m")
            break
        else:
            print ("FAIL!")
            print (result.stdout)
            print ("Exit anyway")
            exit()

        print ("Transfer data to PC...")
        fdir = resultstr[resultstr.find("save_fdir_start_")+16:resultstr.find("_end_save_fdir")] 
        #wib_raw_dir = fdir #later save it into log file
        logs['wib_raw_dir'] = fdir
        fs = resultstr[resultstr.find("save_file_start_")+16:resultstr.find("_end_save_file")] 
        fsubdirs = fdir.split("/")
        fn = fs.split("/")[-1]
        fddir =logs['PC_rawdata_root'] + fsubdirs[-2] + "/" 

        if not os.path.exists(fddir):
            try:
                os.makedirs(fddir)
            except OSError:
                print ("Error to create folder %s"%save_dir)
                print ("Exit anyway")
                sys.exit()
        wibhost = "root@192.168.121.123:"
        fsrc = wibhost + fs
        command = ["scp", "-r",fsrc , fddir]
        result=subrun(command, timeout = None)
        print ("data save at {}".format(fddir))
        logs['pc_raw_dir'] = fddir #later save it into log file
        logs["QC_TestItemID_%03d_SCP"%testid] = [command, result]
        logs["QC_TestItemID_%03d_Save"%testid] = logs['pc_raw_dir']
        print (datetime.datetime.utcnow(), "\033[92m  : SUCCESS!  \033[0m")

#if True:
if QC_TST_EN:
    print ("")
    print ("")
    print ("save log info during QC")
    for key in list(logs.keys()):
        print (key)

    if logs['New_chips']:
        fp = logs['pc_raw_dir'] + "QC.log"
        with open(fp, 'wb') as fn:
            pickle.dump(logs, fn)
    else:
        tmpstr = "".join(str(x) + "_" for x in logs['TestIDs'])
        fp = logs['pc_raw_dir'] + "QC_Retest_{}.log".format(tmpstr)
        print (fp)
        with open(fp, 'wb') as fn:
            pickle.dump(logs, fn)

#if QC_ANA_EN:
#    print ("")
#    print ("")
#    print (datetime.datetime.utcnow(), " : Perform quick analysis")
#    if not QC_TST_EN:
#        print ("Please specify the path of log file")
#        fnlog = input("\033[93m >>  \033[0m") + "/QC.log"
#        #fnlog = "./tmp_data/FE_503010001_503000002_503000003_503000004_503000005_503000006_503000007_503000008/QC_Retest_1_9_.log"
#        print (fnlog)
#        try:
#            with open(fnlog, 'rb') as fn:
#                logs =  pickle.load(fn)
#        except:
#            print ("invalid log file path...")
#            print ("exit anyway")
#            exit()
#
#    from DAT_LArASIC_QC_quick_ana import dat_larasic_qc_quick_ana
#    dat_larasic_qc_quick_ana(fdir = logs['pc_raw_dir'])
#
#    if QC_TST_EN:
#        fnstr = input("\033[93m Can data on WIB be deleted? (Y/N)  \033[0m")
#        if "Y" in ynstr or "y" in ynstr:
#            command = ["ssh", "root@192.168.121.123", """cd BNL_CE_WIB_SW_QC; rm -rf {}""".format(logs['wib_raw_dir'])]
#            result=subrun(command, timeout = None)
#            print ("Deleted. Done")
#
