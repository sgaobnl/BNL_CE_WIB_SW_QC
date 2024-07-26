import time
import sys
import subprocess
import datetime
import filecmp
import pickle
import os
from DAT_read_cfg import dat_read_cfg
from DAT_LArASIC_InitChk import dat_larasic_initchk
import random

from colorama import just_fix_windows_console
just_fix_windows_console()

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
            return None
            #exit()
            

        #continue
    except subprocess.TimeoutExpired as e:
        print ("No reponse in %d seconds"%(timeout))
        if exitflg:
            #print (result.stdout)
            print ("Timoout FAIL!")
            print ("Exit anyway")
            return None
            #exit()

        #continue
    return result


def DAT_power_off():
    logs = {}
    print (datetime.datetime.utcnow(), " : Power DAT down (it takes < 60s)")
    command = ["ssh", "root@192.168.121.123", "cd BNL_CE_WIB_SW_QC; python3 top_femb_powering.py off off off off"]
    result=subrun(command, timeout = 60)
    if result != None:
        if "Done" in result.stdout:
            print (datetime.datetime.utcnow(), "\033[92m  : SUCCESS!  \033[0m")
        else:
            print ("FAIL!")
            print (result.stdout)
            return None
    else:
        print ("FAIL!")
        return None

def DAT_power_on():
    logs = {}
    print (datetime.datetime.utcnow(), " : Power DAT On (it takes < 60s)")
    command = ["ssh", "root@192.168.121.123", "cd BNL_CE_WIB_SW_QC; python3 top_femb_powering.py on off off off"]
    result=subrun(command, timeout = 60)
    if result != None:
        if "Done" in result.stdout:
            print (datetime.datetime.utcnow(), "\033[92m  : SUCCESS!  \033[0m")
        else:
            print ("FAIL!")
            print (result.stdout)
            return None
    else:
        print ("FAIL!")
        return None

def Sinkcover():
    while True:
        ccflg=input("\033[93m Do covers of shielding box close? (Y/N) : \033[0m")
        if ("Y" in ccflg) or ("y" in ccflg):
            break
        else:
            print ("Please close the covers and continue...")

def rts_ssh_LArASIC(dut_skt, root = "C:/DAT_LArASIC_QC/Tested/" ):
    #if True:
    #    x = random.randint(0,24)
    #    #x = 10
    #    #x = int(input("a numer:"))
    #    #if x >= 20:
    #    #    return ("Code#E001", [])
    #    if x >= 8:
    #        #b = int(input("PASS a numer:"))
    #        #return ("PASS", [b])
    #        return ("PASS", [])
    #    else:
    #        return ("Code#W004", [x])

    QC_TST_EN =  True 
    
    logs = {}
    logs['RTS_IDs'] = dut_skt
    x = list(dut_skt.keys())
    logs['PC_rawdata_root'] = root + "Time_{}_DUT_{:04d}_{:04d}_{:04d}_{:04d}_{:04d}_{:04d}_{:04d}_{:04d}/".format(x[0],
                                                                            dut_skt[x[0]][1]*1000 + dut_skt[x[0]][0], 
                                                                            dut_skt[x[1]][1]*1000 + dut_skt[x[1]][0], 
                                                                            dut_skt[x[2]][1]*1000 + dut_skt[x[2]][0], 
                                                                            dut_skt[x[3]][1]*1000 + dut_skt[x[3]][0], 
                                                                            dut_skt[x[4]][1]*1000 + dut_skt[x[4]][0], 
                                                                            dut_skt[x[5]][1]*1000 + dut_skt[x[5]][0], 
                                                                            dut_skt[x[6]][1]*1000 + dut_skt[x[6]][0], 
                                                                            dut_skt[x[7]][1]*1000 + dut_skt[x[7]][0] 
                                                                            ) 
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
    logs['tms_items'] = tms_items
    
    if QC_TST_EN:
        tms = list(tms_items.keys())
        #print (datetime.datetime.utcnow(), "\033[93m   : Please put chips into the sockets carefully \033[0m")
        #print ("Please update chip serial numbers")
        #command = ["notepad.exe", logs['PC_WRCFG_FN']]
        #result=subrun(command, timeout = None, check=False)
        from DAT_chk_cfgfile import dat_chk_cfgfile
        pf= dat_chk_cfgfile(fcfg = logs['PC_WRCFG_FN'] )
        if pf:
            logs['New_chips'] = True
            logs['TestIDs'] = tms
    
    if QC_TST_EN:
        print (datetime.datetime.utcnow(), " : Check if WIB is pingable (it takes < 60s)" )
        timeout = 10 
        command = ["ping", "192.168.121.123"]
        print ("COMMAND:", command)
        for i in range(6):
            if i == 5:
                print ("Please check if WIB is powered and Ethernet connection,exit anyway")
                return None

            result = subrun(command=command, timeout=timeout, exitflg=False)
            if result != None:
                log = result.stdout
                chk1 = "Reply from 192.168.121.123: bytes=32"
                chk2p = log.find("Received =")
                chk2 =  int(log[chk2p+11])
                if chk1 in log and chk2 >= 1:  #improve it later
                    print (datetime.datetime.utcnow(), "\033[92m  : SUCCESS!  \033[0m")
                    logs['WIB_Pingable'] = log
                    break
    
    if QC_TST_EN:
        print (datetime.datetime.utcnow(), " : sync WIB time")
        # Get the current date and time
        now = datetime.datetime.utcnow()
        # Format it to match the output of the `date` command
        formatted_now = now.strftime('%a %b %d %H:%M:%S UTC %Y')
        command = ["ssh", "root@192.168.121.123", "date -s \'{}\'".format(formatted_now)]
        result=subrun(command, timeout = 30)
        if result != None:
            print ("WIB Time: ", result.stdout)
            print (datetime.datetime.utcnow(), "\033[92m  : SUCCESS!  \033[0m")
            logs['WIB_UTC_Date_Time'] = result.stdout
        else:
            print ("FAIL!")
            return None
   
    if QC_TST_EN:
        print (datetime.datetime.utcnow(), " : Load WIB bin file(it takes < 30s)" )
        command = ["ssh", "root@192.168.121.123", "fpgautil -b /boot/wib_top_0506.bin"]
        result=subrun(command, timeout = 30)
        if result != None:
            if "BIN FILE loaded through FPGA manager successfully" in result.stdout:
                print (datetime.datetime.utcnow(), "\033[92m  : SUCCESS!  \033[0m")
            logs['WIB_bin_file'] = result.stdout
        else:
            print ("FAIL!")
            return None
    
    if QC_TST_EN:
        print (datetime.datetime.utcnow(), " : Start WIB initialization (it takes < 30s)")
        command = ["ssh", "root@192.168.121.123", "cd BNL_CE_WIB_SW_QC;  python3 wib_startup.py"]
        result=subrun(command, timeout = 30)
        if result != None:
            if "Done" in result.stdout:
                print (datetime.datetime.utcnow(), "\033[92m  : SUCCESS!  \033[0m")
            else:
                print ("FAIL!")
                print (result.stdout)
                return None
                #exit()
            logs['WIB_start_up'] = result.stdout
        else:
            print ("FAIL!")
            return None
   
    

    
    
    if QC_TST_EN:
        print ("later use pyqt to pop out a configuration windows")
        #input ("anykey to continue now")
        print (datetime.datetime.utcnow(), " : load configuration file from PC")
    
        wibdst = "root@192.168.121.123:/home/root/BNL_CE_WIB_SW_QC/"
        command = ["scp", "-r", logs['PC_WRCFG_FN'] , wibdst]
        result=subrun(command, timeout = None)
        if result != None:
            logs['CFG_wrto_WIB'] = [command, result.stdout]
    
            wibsrc = "root@192.168.121.123:/home/root/BNL_CE_WIB_SW_QC/asic_info.csv"
            pcdst = "./readback/"
            command = ["scp", "-r", wibsrc , pcdst]
            result=subrun(command, timeout = None)
            if result != None:
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
                    return None
                    #exit()
            else:
                print ("FAIL!")
                return None
        else:
            print ("FAIL!")
            return None

    
    if QC_TST_EN:
        print (datetime.datetime.utcnow(), " : Start DUT (%s) QC.(takes < 1200s)"%DUT)
        for testid in tms:
        #for testid in [0]:
            print (datetime.datetime.utcnow(), " : New Test Item Starts, please wait...")
            print (tms_items[testid])
            if "FE" in DUT:
                command = ["ssh", "root@192.168.121.123", "cd BNL_CE_WIB_SW_QC; python3 DAT_LArASIC_QC_top.py -t {}".format(testid)]
            result=subrun(command, timeout = None) #rewrite with Popen later
            if result != None:
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
                    return None
                    #exit()
            else:
                print ("FAIL!")
                return None
    
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
                    #sys.exit()
                    return None
            wibhost = "root@192.168.121.123:"
            fsrc = wibhost + fs
            command = ["scp", "-r",fsrc , fddir]
            result=subrun(command, timeout = None)
            if result != None:
                print ("data save at {}".format(fddir))
                logs['pc_raw_dir'] = fddir #later save it into log file
                logs["QC_TestItemID_%03d_SCP"%testid] = [command, result]
                logs["QC_TestItemID_%03d_Save"%testid] = logs['pc_raw_dir']
                print (datetime.datetime.utcnow(), "\033[92m  : SUCCESS!  \033[0m")
            else:
                print ("FAIL!")
                return None

            if testid == 0: #checkout
                print ("Run quick analysis...")
                QCstatus, bads = dat_larasic_initchk(fdir=logs['pc_raw_dir'])
                if len(bads) > 0 :
                    if logs['New_chips']:
                        fp = logs['pc_raw_dir'] + "QC.log"
                        with open(fp, 'wb') as fn:
                            pickle.dump(logs, fn)
                    return (QCstatus, bads)
   
    #if True:
    if QC_TST_EN:
        print ("save log info during QC")
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
    
    print ("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
    print ("QC analysis script from Rado will add here")
    print ("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
    QCstatus = "PASS"
    bads = []
    #chip_passed = [0,1,2,3,4,5,6,7]
    #chip_failed = []

    return QCstatus, bads 


