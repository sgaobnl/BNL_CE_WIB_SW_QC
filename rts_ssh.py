import time
import sys
import subprocess
import datetime
import filecmp
import pickle
import os
from DAT_read_cfg import dat_read_cfg
from DAT_InitChk import dat_initchk
from colorama import just_fix_windows_console
from DAT_COLDATA_QC_ana import CD_QC_ANA 
just_fix_windows_console()

wibip = "192.168.121.123"
wibhost = "root@{}".format(wibip)
sshcmd = ["ssh","-o", "ConnectTimeout=60",  "-o", "ServerAliveInterval=20", "-o", "ServerAliveCountMax=2"]

def subrun(command, timeout = 30, check=False, exitflg = True):
    try:
        result = subprocess.run(command,
                                capture_output=True,
                                text=True,
                                timeout=timeout,
                                #shell=True,
                                shell=False,
                                #stdout=subprocess.PIPE,
                                #stderr=subprocess.PIPE,
                                #check=check
                                check=False #Disable check=True and handle errors yourself (recommended)
                                )

        if result.returncode != 0:
            print("Command failed:", result.returncode)
            print("STDERR:", result.stderr.strip())
            if exitflg:
                self.DAT_power_off()
                return 'Error'
        return result

    #except subprocess.CalledProcessError as e:
    #    print ("Call Error", e.returncode)
    #    if exitflg:
    #        print ("Call Error FAIL!")
    #        print ("Exit anyway")
    #        return None
    #        #exit()
        #continue
    except subprocess.TimeoutExpired as e:
        print ("No reponse in %d seconds"%(timeout))
        if exitflg:
            #print (result.stdout)
            print ("Timoout FAIL!")
            print ("Exit anyway")
            self.DAT_power_off()
            return 'Error'
            #exit()

        #continue


def DAT_power_off():
    logs = {}
    print (datetime.datetime.utcnow(), " : Power DAT down (it takes < 60s)")
    command = sshcmd + [wibhost, "cd BNL_CE_WIB_SW_QC; python3 top_femb_powering.py off off off off"]
    result=subrun(command, timeout = 60*3)
    if result != 'Error':
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
    command = sshcmd + [ wibhost, "cd BNL_CE_WIB_SW_QC; python3 top_femb_powering.py on off off off"]
    result=subrun(command, timeout = 60*3)
    if result != 'Error':
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

def rts_ssh(dut_skt, root = "C:/DAT_LArASIC_QC/Tested/", duttype="FE", env="RT", testid=0 ):
    logs = {}
    logs['RTS_IDs'] = dut_skt

    ocrfp = root + "ocr_results.bin"
    with open(ocrfp, 'rb') as fn:
        chip_ocr = pickle.load(fn)

    x = list(dut_skt.keys())
    lenx = len(x)
    if "FE"in duttype or "ADC"in duttype:
        logs['PC_rawdata_root'] = root + "Time_{}_DUT_{:04d}_{:04d}_{:04d}_{:04d}_{:04d}_{:04d}_{:04d}_{:04d}/".format(x[0],
                                                                            dut_skt[x[0%lenx]][1]*1000 + dut_skt[x[0%lenx]][0], 
                                                                            dut_skt[x[1%lenx]][1]*1000 + dut_skt[x[1%lenx]][0], 
                                                                            dut_skt[x[2%lenx]][1]*1000 + dut_skt[x[2%lenx]][0], 
                                                                            dut_skt[x[3%lenx]][1]*1000 + dut_skt[x[3%lenx]][0], 
                                                                            dut_skt[x[4%lenx]][1]*1000 + dut_skt[x[4%lenx]][0], 
                                                                            dut_skt[x[5%lenx]][1]*1000 + dut_skt[x[5%lenx]][0], 
                                                                            dut_skt[x[6%lenx]][1]*1000 + dut_skt[x[6%lenx]][0], 
                                                                            dut_skt[x[7%lenx]][1]*1000 + dut_skt[x[7%lenx]][0] 
                                                                            ) 
    else:
        logs['PC_rawdata_root'] = root + "Time_{}_DUT_{:04d}_{:04d}/".format(x[0],
                                                                            dut_skt[x[0%lenx]][1]*1000 + dut_skt[x[0%lenx]][0], 
                                                                            dut_skt[x[1%lenx]][1]*1000 + dut_skt[x[1%lenx]][0]
                                                                            )
    
    logs['PC_WRCFG_FN'] = "./asic_info.csv"
    csvfp = logs['PC_WRCFG_FN']
    tmps = []
    with open(csvfp, 'r') as fp:
        for cl in fp:
            tmp = cl.split(",")
            if "env" in tmp[0]:
                tmp[1] = env
            if "FE" in duttype:
                if "FE" in tmp[0][0:2]:
                    sktno = int(tmp[0][2])
                    key = dut_skt[x[sktno%lenx]][0] + 1
                    tmp[1] = chip_ocr[key][1]
                    print (tmp, sktno)
            if "DUT" in tmp[0][0:3]:
                tmp[1] = duttype
            cln=','.join(tmp)
            tmps.append(cln)

    
    with open(csvfp, 'w') as fp:
        for cl in tmps:
            fp.write(cl)

    if testid in [91,92,93,94,95,96,97,98]:
        QC_TST_EN =   False
    else:
        QC_TST_EN =  True 

    if testid in [91,92,93,94,95,96,97,98]:
        if "FE" in duttype:
            DUT = 'FE'
        elif "ADC" in duttype:
            DUT = 'ADC'
        elif "CD" in duttype:
            DUT = 'CD'
        print (datetime.datetime.utcnow(), " : check if there is a short")
        if True:
            print (datetime.datetime.utcnow(), " : New Test Item Starts, please wait...")
            if "FE" in DUT:
                command = sshcmd + [ wibhost, "cd BNL_CE_WIB_SW_QC; python3 DAT_LArASIC_QC_top.py -t {}".format(testid)]
            elif "ADC" in DUT:
                command = sshcmd + [ wibhost, "cd BNL_CE_WIB_SW_QC; python3 DAT_ColdADC_QC_top.py -t {}".format(testid)]
            elif "CD" in DUT:
                command = sshcmd + [ wibhost, "cd BNL_CE_WIB_SW_QC; python3 DAT_COLDATA_QC_top.py -t {}".format(testid)]
            #result=subrun(command, timeout = None) #rewrite with Popen later
            result=subrun(command, timeout = 60*20) #rewrite with Popen later
            if result != 'Error':
                resultstr = result.stdout
                logs["QC_TestItemID_%03d"%testid] = [command, resultstr]
                if "Pass!" in result.stdout:
                    print (datetime.datetime.utcnow(), "\033[92m  : SUCCESS!  \033[0m")
                elif "DAT_Power_On" in result.stdout:
                    print (datetime.datetime.utcnow(), "\033[92m  : SUCCESS & Turn DAT on!  \033[0m")
                elif "DAT_Power_Off" in result.stdout:
                    print (datetime.datetime.utcnow(), "\033[92m  : SUCCESS & Done!  \033[0m")
                else:
                    print ("FAIL!")
                    print (result.stdout)
                    print ("Exit anyway")
                    return None
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
                    print ("Error to create folder %s"%fddir)
                    print ("Exit anyway")
                    #sys.exit()
                    return None
            fsrc = wibhost + ":" + fs
            command = ["scp", "-r",fsrc , fddir]
            #result=subrun(command, timeout = None)
            result=subrun(command, timeout = 60*5)
            if result != 'Error':
                print ("data save at {}".format(fddir))
                logs['pc_raw_dir'] = fddir #later save it into log file
                logs["QC_TestItemID_%03d_SCP"%testid] = [command, result]
                logs["QC_TestItemID_%03d_Save"%testid] = logs['pc_raw_dir']
                print (datetime.datetime.utcnow(), "\033[92m  : SUCCESS!  \033[0m")
            else:
                print ("FAIL!")
                return None

            print ("Run quick analysis...")
            QCstatus, bads = dat_initchk(fdir=logs['pc_raw_dir'])
            print (QCstatus, bads)
            fdirdel = logs['wib_raw_dir']
            command = sshcmd + [wibhost, "rm -rf {}".format(fdirdel)] 
            #result=subrun(command, timeout = None)
            result=subrun(command, timeout = 60*5)
            if result != 'Error':
                print ("WIB folder {} is deleted!".format(fdirdel))
            return (QCstatus, bads)

    
    if QC_TST_EN:
        #[0, 1, 2, 3, 4,5,61, 62, 63, 64, 7,8, 9]
        tms_items = {}
        if "FE" in duttype:
            tms_items[0 ] = "\033[96m 0 : Initilization checkout (not selectable for itemized test item)  \033[0m"
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
    #        tms_items[10] = "\033[96m 10: Turn DAT (on WIB slot0) on without any check\033[0m"
        elif "ADC" in duttype:
            tms_items[0  ] = "\033[96m 0: Initilization checkout (not selectable for itemized test item) \033[0m"
            tms_items[1  ] = "\033[96m 1: ADC power cycling measurement  \033[0m"
    #        tms_items[2  ] = "\033[96m 2: ADC reserved...  \033[0m"
            tms_items[3  ] = "\033[96m 3: ADC reference voltage measurement  \033[0m"
            tms_items[4  ] = "\033[96m 4: ADC autocalibration check  \033[0m"
            tms_items[5  ] = "\033[96m 5: ADC noise measurement  \033[0m"
            tms_items[7  ] = "\033[96m 7: ADC DAT-DAC SCAN  \033[0m"
            tms_items[11 ] = "\033[96m 11: ADC ring oscillator frequency readout \033[0m"
            tms_items[12 ] = "\033[96m 12: ADC RANGE test \033[0m"
            tms_items[8  ] = "\033[96m 8: ADC ENOB measurement \033[0m"
            tms_items[6  ] = "\033[96m 6: ADC DNL/INL measurement  \033[0m"
            tms_items[9  ] = "\033[96m 9: Turn DAT off \033[0m"
    #        tms_items[10 ] = "\033[96m 10: Turn DAT (on WIB slot0) on without any check\033[0m"
        elif "CD" in duttype:
            tms_items[0  ] = "\033[96m 0: Initilization checkout (not selectable for itemized test item) \033[0m"
            tms_items[1  ] = "\033[96m 1: COLDATA basic functionality checkout  \033[0m"
            tms_items[2  ] = "\033[96m 2: COLDATA primary/secondary swap check  \033[0m"
            tms_items[3  ] = "\033[96m 3: COLDATA power consumption measurement  \033[0m"
            tms_items[4  ] = "\033[96m 4: COLDATA PLL lock range measurement  \033[0m"
            tms_items[5  ] = "\033[96m 5: COLDATA fast command verification  \033[0m"
            tms_items[6  ] = "\033[96m 6: COLDATA output link verification \033[0m"
            if False:
                tms_items[7  ] = "\033[96m 7: COLDATA EFUSE burn-in \033[0m"
            else: 
                print ("Burn-in is ignore")
            tms_items[9  ] = "\033[96m 9: Turn DAT off \033[0m"
    
        logs['tms_items'] = tms_items

        tms = list(tms_items.keys())
        logs['TestIDs'] = tms
    
    #if QC_TST_EN:
    if False:
        print (datetime.datetime.utcnow(), " : Check if WIB is pingable (it takes < 60s)" )
        timeout = 10 
        command = ["ping", wibip]
        print ("COMMAND:", command)
        for i in range(6):
            if i == 5:
                print ("Please check if WIB is powered and Ethernet connection,exit anyway")
                return None

            result = subrun(command=command, timeout=timeout, exitflg=False)
            if result != 'Error':
                log = result.stdout
                chk1 = "Reply from {}: bytes=32".format(wibip)
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
        command = sshcmd + [ wibhost, "date -s \'{}\'".format(formatted_now)]
        result=subrun(command, timeout = 30)
        if result != 'Error':
            print ("WIB Time: ", result.stdout)
            print (datetime.datetime.utcnow(), "\033[92m  : SUCCESS!  \033[0m")
            logs['WIB_UTC_Date_Time'] = result.stdout
        else:
            print ("FAIL!")
            return None
   
    if QC_TST_EN:
        print (datetime.datetime.utcnow(), " : Load WIB bin file(it takes < 30s)" )
        if (duttype=="ADC"):
            command = sshcmd + [ wibhost, "fpgautil -b /home/root/BNL_CE_WIB_SW_QC/DAT_QC_WIB_binfiles/wib_top_coldadc_qc_sim.wibbin"]
        else:
            command = sshcmd + [ wibhost, "fpgautil -b /home/root/BNL_CE_WIB_SW_QC/DAT_QC_WIB_binfiles/wib_top_production.wibbin"]
        result=subrun(command, timeout = 30)
        if result != 'Error':
            if "BIN FILE loaded through FPGA manager successfully" in result.stdout:
                print (datetime.datetime.utcnow(), "\033[92m  : SUCCESS!  \033[0m")
            logs['WIB_bin_file'] = result.stdout
        else:
            print ("FAIL!")
            return None
    
    if QC_TST_EN:
        print (datetime.datetime.utcnow(), " : Start WIB initialization (it takes < 30s)")
        command = sshcmd + [ wibhost, "cd BNL_CE_WIB_SW_QC;  python3 wib_startup.py"]
        result=subrun(command, timeout = 30)
        if result != 'Error':
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
        #print ("later use pyqt to pop out a configuration windows")
        #input ("anykey to continue now")
        print (datetime.datetime.utcnow(), " : load configuration file from PC")
    
        wibdst = "{}:/home/root/BNL_CE_WIB_SW_QC/".format(wibhost)
        command = ["scp", "-r", logs['PC_WRCFG_FN'] , wibdst]
        #result=subrun(command, timeout = None)
        result=subrun(command, timeout = 60*5)
        if result != 'Error':
            logs['CFG_wrto_WIB'] = [command, result.stdout]
    
            wibsrc = "{}:/home/root/BNL_CE_WIB_SW_QC/asic_info.csv".format(wibhost)
            pcdst = "./readback/"
            command = ["scp", "-r", wibsrc , pcdst]
            #result=subrun(command, timeout = None)
            result=subrun(command, timeout = 60*5)
            if result != 'Error':
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
        tmsi = 0
        retry_fi = 0
        while True:
            if tmsi >= len(tms):
                break
            
            testid = tms[tmsi]
            print (datetime.datetime.utcnow(), " : New Test Item Starts, please wait...")
            print (tms_items[testid])
            if "FE" in DUT:
                command = sshcmd + [ wibhost, "cd BNL_CE_WIB_SW_QC; python3 DAT_LArASIC_QC_top.py -t {}".format(testid)]
            elif "ADC" in DUT:
                command = sshcmd + [ wibhost, "cd BNL_CE_WIB_SW_QC; python3 DAT_ColdADC_QC_top.py -t {}".format(testid)]
            elif "CD" in DUT:
                command = sshcmd + [ wibhost, "cd BNL_CE_WIB_SW_QC; python3 DAT_COLDATA_QC_top.py -t {}".format(testid)]
            #result=subrun(command, timeout = None) #rewrite with Popen later
            result=subrun(command, timeout = 60*20) #rewrite with Popen later
            if result != 'Error':
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
                    print ("Error to create folder %s"%fddir)
                    print ("Exit anyway")
                    #sys.exit()
                    return None
            fsrc = wibhost + ":" + fs
            command = ["scp", "-r",fsrc , fddir]
            #result=subrun(command, timeout = None)
            result=subrun(command, timeout = 60*5)
            if result != 'Error':
                print ("data save at {}".format(fddir))
                logs['pc_raw_dir'] = fddir #later save it into log file
                logs["QC_TestItemID_%03d_SCP"%testid] = [command, result]
                logs["QC_TestItemID_%03d_Save"%testid] = logs['pc_raw_dir']
                print (datetime.datetime.utcnow(), "\033[92m  : SUCCESS!  \033[0m")
            else:
                print ("FAIL!")
                return None

            if (testid == 0) and ("RT" in env):
                print ("Run quick analysis...")
                QCstatus, bads = dat_initchk(fdir=logs['pc_raw_dir'])
                print (QCstatus, bads)

                #debugging, to be delete
                #QCstatus = "PASS"
                #bads = []

                if (len(bads) > 0) or ("Code#E" in QCstatus):
                    #if logs['New_chips']:
                    if True:
                        fp = logs['pc_raw_dir'] + "QC.log"
                        with open(fp, 'wb') as fn:
                            pickle.dump(logs, fn)
                    fdirdel = logs['wib_raw_dir']
                    #command = ["rm", "-rf",fdirdel] 
                    command = sshcmd + [ wibhost, "rm -rf {}".format(fdirdel)] 
                    #result=subrun(command, timeout = None)
                    result=subrun(command, timeout = 60*5)
                    if result != 'Error':
                        print ("WIB folder {} is deleted!".format(fdirdel))
                    return (QCstatus, bads)

            if duttype == "CD":
                cd_qc_ana = CD_QC_ANA()
                cd_qc_ana.env = env
                cd_qc_ana.qc_stats = {}
                cd_qc_ana.dat_cd_qc_ana(fdir=logs['pc_raw_dir'], tms=[testid])
                keys = list(cd_qc_ana.qc_stats.keys())
                retry_fi_pre = retry_fi
                for onekey in keys:
                    if "PASS" not in cd_qc_ana.qc_stats[onekey]:
                        retry_fi = retry_fi  +1
                        break
                if (retry_fi == 1) and (retry_fi != retry_fi_pre):
                    tmsi = tmsi
                    continue
                elif retry_fi >=2:
                    QCstatus = "PASS"
                    bads = []
                    tmsi = tmsi + 1
                    retry_fi = 0
                    #
                else:
                    tmsi = tmsi + 1
                    retry_fi = 0
            else:
                tmsi = tmsi + 1

        fdirdel = logs['wib_raw_dir']
        command = sshcmd + [ wibhost, "rm -rf {}".format(fdirdel)] 
        result=subrun(command, timeout = 60)
        if result != 'Error':
            print ("WIB folder {} is deleted!".format(fdirdel))

  
    if QC_TST_EN:
        print ("save log info during QC")
        #if logs['New_chips']:
        if True:
            fp = logs['pc_raw_dir'] + "QC.log"
            with open(fp, 'wb') as fn:
                pickle.dump(logs, fn)
        else:
            tmpstr = "".join(str(x) + "_" for x in logs['TestIDs'])
            fp = logs['pc_raw_dir'] + "QC_Retest_{}.log".format(tmpstr)
            print (fp)
            with open(fp, 'wb') as fn:
                pickle.dump(logs, fn)
    
    QCstatus = "PASS"
    bads = []

    return QCstatus, bads 

if __name__=="__main__":
    result = rts_ssh(dut_skt={20250926130804:(0,0)}, root = "C:/SGAO/ColdTest/Tested/DAT_LArASIC_QC/B006T0001/", duttype="FE", env="RT", chips=1 )
    if result != 'Error':
        QCstatus = result[0]
        print (QCstatus)
        print (result)


