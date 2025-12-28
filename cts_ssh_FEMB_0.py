import logging
import time
import sys
import subprocess
import datetime
import filecmp
import os
from datetime import datetime
import csv
import webbrowser
from colorama import Fore, Style
import pprint
import GUI.Rigol_DP800 as rigol

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
def subrun(command, timeout=30, check=True, out = True, exitflg=True, user_input=None, rm = False, shell=False):
    result = None
    # print("command = {}".format(command))
    if check:
        try:
            result = subprocess.run(command,
                                    input=user_input,
                                    capture_output=check,
                                    text=True,
                                    timeout=timeout,
                                    shell=shell,
                                    # stdout=subprocess.PIPE,
                                    # stderr=subprocess.PIPE,
                                    check=check
                                    )
        except subprocess.CalledProcessError as e:
            print("Call Error", e.returncode)
            if exitflg:
                # print("Call Error FAIL!")
                # print("Exit anyway")
                return None
                # exit()

            # continue

        except subprocess.TimeoutExpired as T:
            print("No reponse in %d seconds" % (timeout))
            if exitflg:
                # print (result.stdout)
                print("Timeout FAIL!")
                print("Exit anyway")
                return None

            # continue
        return result
    elif out:
        try:
            result = subprocess.run(command,
                                    input=user_input,
                                    capture_output=check,
                                    text=True,
                                    timeout=timeout,
                                    shell=True,
                                    # stdout=subprocess.PIPE,
                                    # stderr=subprocess.PIPE,
                                    check=check
                                    )
        except subprocess.CalledProcessError as e:
            print("Call Error", e.returncode)
            if exitflg:
                print("Call Error FAIL!")
                print("Exit anyway")
                return None
                # exit()

            # continue

        except subprocess.TimeoutExpired as T:
            print("No reponse in %d seconds" % (timeout))
            return None
        return result
    else:
        try:
            result = subprocess.run(command,
                                    input=user_input,
                                    capture_output=check,
                                    text=True,
                                    timeout=timeout,
                                    shell=True,
                                    stdout=subprocess.DEVNULL,  # discard stdout
                                    stderr=subprocess.DEVNULL,
                                    check=check
                                    )
        except subprocess.CalledProcessError as e:
            print("Call Error", e.returncode)
            if exitflg:
                return None
                # exit()

            # continue

        except subprocess.TimeoutExpired as T:
            print("No reponse in %d seconds" % (timeout))
            return None
        return result

# =================#
# FEMB QC Script: #
# LKE@BNL.GOV     #
# =================#

# Function 01 CSV Read
def read_csv_to_dict(filename, env, p = False):
    data = {}
    with open(filename, mode='r', newline='', encoding='utf-8-sig') as file:
        reader = csv.reader(file)
        # headers = next(reader)
        for row in reader:
            if len(row) >= 2:
                key = row[0]
                if row[1] == '':
                    row[1] = ' '
                value = row[1]
                data[key] = value
            if p:
                print("\033[96m" + key + "\t\t:\t\t" + data[key] + "\033[0m")
    if env == 'LN':
        data['env'] = 'y'
        if p:
            print("\033[96m" + 'environment' + "\t:\t\t" + data['env'] + '(Cold)' + "\033[0m")
    else:
        data['env'] = 'n'
        if p:
            print("\033[96m" + 'environment' + "\t:\t\t" + data['env'] + '(Warm)' + "\033[0m")
    return data


def cts_ssh_FEMB(root="D:/FEMB_QC/", QC_TST_EN=0, input_info=None):
    # QC_TST_EN = True
    logs = {}  # from collections import defaultdict report_log01 = defaultdict(dict)
    logs['CTS_IDs'] = input_info['test_site']
    slot0 = input_info['SLOT0']
    slot1 = input_info['SLOT1']
    slot2 = input_info['SLOT2']
    slot3 = input_info['SLOT3']
    Slot_change = False
    slot_list = ''
    FEMB_list = ''
    power_en = ''
    savename = ''
    tmp = ''
    if slot0 != ' ':
        slot_list += ' 0 '
        FEMB_list += slot0 + '\n'
        power_en += ' on '
        savename += '_S0{}'.format(slot0)
    else:
        power_en += ' off '
    if slot1 != ' ':
        slot_list += ' 1 '
        FEMB_list += slot1 + '\n'
        power_en += ' on '
        savename += '_S1{}'.format(slot1)
    else:
        power_en += ' off '
    if slot2 != ' ':
        slot_list += ' 2 '
        FEMB_list += slot2 + '\n'
        power_en += ' on '
        savename += '_S2{}'.format(slot2)
    else:
        power_en += ' off '
    if slot3 != ' ':
        slot_list += ' 3 '
        FEMB_list += slot3 + '\n'
        power_en += ' on '
        savename += '_S3{}'.format(slot3)
    else:
        power_en += ' off '

    if input_info['env'] == 'n':
        tmp = 'room 25C'
        savename += '_RT'.format(slot3)
    else:
        savename += '_LN'.format(slot3)
        tmp = 'LN -200C'

    # print(slot_list)
    # print(power_en)
    # print(savename)


    # [0 'is used for checkout', 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16 '1-16 are used for QC']
    tms_items = {}
    tms_items[12] = "\033[96m Item_12 : ColdADC ref_voltage Linearity [less than 120 second]\033[0m"
    tms_items[10] = "\033[96m Item_10 : FE Monitor [less than 120 second] \033[0m"
    tms_items[11] = "\033[96m Item_11 : FE DAC Linearity [less than 150 second] \033[0m"
    tms_items[1] = "\033[96m Item_01 : POWER CONSUMPTION [less than 80 second] \033[0m"
    tms_items[2] = "\033[96m Item_02 : POWER CYCLE [less than 180 second] \033[0m"
    tms_items[3] = "\033[96m Item_03 : Leakage Current Pulse Response [less than 50 second]\033[0m"
    tms_items[4] = "\033[96m Item_04 : Whole Pulse Response [less than 140 second]\033[0m"
    tms_items[5] = "\033[96m Item_05 : RMS Evaluation [less than 400 second]\033[0m"
    tms_items[6] = "\033[96m Item_06 : Cali_1 configuration SE 200 mV (ASIC-DAC) [less than 230 second]\033[0m"
    tms_items[7] = "\033[96m Item_07 : Cali_2 configuration SE 900 mV  [less than 140 second]\033[0m"
    tms_items[8] = "\033[96m Item_08 : Cali_3 SGP1 SE 200 mV [less than 140 second]\033[0m"
    tms_items[9] = "\033[96m Item_09 : Cali_4 SGP1 SE 900 mV [less than 140 second]\033[0m"
    tms_items[13] = "\033[96m Item_13 : External Pulse Calibration 900mV baseline [less than 50 second]\033[0m"
    tms_items[14] = "\033[96m Item_14 : External Pulse Calibration 200mV baseline [less than 50 second]\033[0m"
    tms_items[15] = "\033[96m Item_15 : ColdADC_sync_pat_report [less than 50 second]\033[0m"
    tms_items[16] = "\033[96m Item_16 : PLL_scan_report [less than 60 second]\033[0m"
    logs['tms_items'] = tms_items



# ==============================
    # if QC_TST_EN == 0:
    tms = list(tms_items.keys())
    current_time = datetime.utcnow()
    # add for AI
    logs['PC_rawdata_root'] = root + "Data/" + "Time_{}_CTS_{}{}".format(current_time.strftime("%Y_%m/%d_%H_%M_%S"), logs['CTS_IDs'], savename)
    logs['PC_rawreport_root'] = root + "Report/" + "Time_{}_CTS_{}{}".format(current_time.strftime("%Y_%m/%d_%H_%M_%S"), logs['CTS_IDs'], savename)
    logs['PC_WRCFG_FN'] = os.path.join(BASE_DIR, "femb_info_implement.csv")

    if QC_TST_EN == 77:
        print(datetime.utcnow(), " : Check if WIB is pingable (it takes < 60s)")
        command = ["ping", "-c", "3" , "192.168.121.123"]
        print("COMMAND: ", command)
        attempt = 0
        while True:
            #result = subrun(command, timeout=10)
            result = subrun(command, shell=False)
            if result != None and result.returncode == 0:
                print(datetime.utcnow(), "\033[92m  : SUCCESS!  \033[0m")
                logs['WIB_Pingable'] = 'true'
                break
            else:
                attempt += 1
                print('Connection issue {} time'.format(attempt))
                if attempt == 4:
                    print(Fore.CYAN + 'Fail Connection\nEnter y to retry\nEnter n to Exit ...' + Style.RESET_ALL)
                    choice = input(Fore.YELLOW + '>> ' + Style.RESET_ALL)
                    if choice == 'n':
                        print('Exit ...')
                        sys.exit()
                    else:
                        attempt = 0

    if QC_TST_EN == 0:
        print(datetime.utcnow(), " : sync WIB time")
        # Get the current date and time
        now = datetime.utcnow()
        # Format it to match the output of the `date` command
        formatted_now = now.strftime('%a %b %d %H:%M:%S UTC %Y')
        command = ["ssh", "root@192.168.121.123", "date -s \'{}\'".format(formatted_now)]
        result = subrun(command, timeout=30,shell=False)
        time.sleep(0.01)
        if result != None:
            print("WIB Time: ", result.stdout)
            print(datetime.utcnow(), "\033[92m  : SUCCESS!  \033[0m")
            logs['WIB_UTC_Date_Time'] = result.stdout
        else:
            print("FAIL!")
            return None

    if QC_TST_EN == 0:
        print(datetime.utcnow(), " : Start WIB initialization (it takes < 30s)")
        command = ["ssh", "root@192.168.121.123", "cd BNL_CE_WIB_SW_QC;  python3 wib_startup.py"]
        result = subrun(command, timeout=30)
        time.sleep(0.01)
        if result != None:
            if "Done" in result.stdout:
                print(datetime.utcnow(), "\033[92m  : SUCCESS!  \033[0m")
            else:
                print("FAIL!")
                print(result.stdout)
                return None
                # exit()
            logs['WIB_start_up'] = result.stdout
        else:
            print("FAIL!")
            return None

    if QC_TST_EN == 0:
        # input ("anykey to continue now")
        print(datetime.utcnow(), " : load configuration file from PC")
        wibdst = "root@192.168.121.123:/home/root/BNL_CE_WIB_SW_QC/"
        print(logs['PC_WRCFG_FN'])
        command = ["scp", "-r", logs['PC_WRCFG_FN'], wibdst]
        result = subrun(command, timeout=20)
        time.sleep(0.01)
        if result != None:
            logs['CFG_wrto_WIB'] = [command, result.stdout]

            wibsrc = "root@192.168.121.123:/home/root/BNL_CE_WIB_SW_QC/femb_info_implement.csv"
            pcdst = "./"
            command = ["scp", "-r", wibsrc, pcdst]
            result = subrun(command, timeout=20)
            time.sleep(0.01)
            if result != None:
                logs['CFG_rbfrom_WIB'] = [command, result.stdout]
                logs['PC_RBCFG_fn'] = os.path.join(BASE_DIR, "femb_info_implement.csv")
                # compare the csv file send to WIB and raw csv file
                result = filecmp.cmp(logs['PC_WRCFG_FN'], logs['PC_RBCFG_fn'])
                if result:
                    print(datetime.utcnow(), "\033[92m  : SUCCESS!  \033[0m")
                else:
                    print("FAIL!")
                    print("Exit anyway")
                    return None
                    # exit()
            else:
                print("FAIL!")
                return None
        else:
            print("FAIL!")
            return None

    # ========== Begin of 01 FEMB Slot Confirm ==========================
    LN_result = ""
    if QC_TST_EN == 1:
        while True:
            print(datetime.utcnow(), "\033[35m  : Start FEMB SLOT Confirm (it takes < 60s)\n  \033[0m")
            if 'LN' in tmp:
                command1 = ["ssh", "root@192.168.121.123", "cd BNL_CE_WIB_SW_QC;  python3 top_femb_powering_LN.py {}".format(power_en)]
                result = subrun(command1, timeout=60)
                LN_result = result.stdout

                time.sleep(2)
                print("Cold initial")
                command1 = ["ssh", "root@192.168.121.123",
                            "cd BNL_CE_WIB_SW_QC;  python3 top_femb_powering.py {}".format(power_en)]
                result1 = subrun(command1, timeout=60, out=False)
                print("FEMB Cold Power On")
            else:
                command1 = ["ssh", "root@192.168.121.123", "cd BNL_CE_WIB_SW_QC;  python3 top_femb_powering.py {}".format(power_en)]
                print("Warm initial")
                result1 = subrun(command1, timeout=60, out = False)
            SlotCheck = result1.stdout
            print(slot_list)
            if '0' in slot_list:
                if 'SLOT#0 Power Connection Normal' in SlotCheck:
                    print("\033[32m" + 'SLOT#0 Power Connection Normal' + "\033[0m")
                    slot0 = input_info['SLOT0']
                else:
                    print("\033[33m" + 'SLOT#0 LOSS Power Connection Warning !!!' + "\033[0m")
                    Slot_change = True
                    slot0 = ' '
            if '1' in slot_list:
                if 'SLOT#1 Power Connection Normal' in SlotCheck:
                    print("\033[32m" + 'SLOT#1 Power Connection Normal' + "\033[0m")
                    slot1 = input_info['SLOT1']
                else:
                    print("\033[33m" + 'SLOT#1 LOSS Power Connection Warning !!!' + "\033[0m")
                    slot1 = ' '
                    Slot_change = True
            if '2' in slot_list:
                if 'SLOT#2 Power Connection Normal' in SlotCheck:
                    print("\033[32m" + 'SLOT#2 Power Connection Normal' + "\033[0m")
                    slot2 = input_info['SLOT2']
                else:
                    print("\033[33m" + 'SLOT#2 LOSS Power Connection Warning !!!' + "\033[0m")
                    slot2 = ' '
                    Slot_change = True
            if '3' in slot_list:
                if 'SLOT#3 Power Connection Normal' in SlotCheck:
                    print("\033[32m" + 'SLOT#3 Power Connection Normal' + "\033[0m")
                    slot3 = input_info['SLOT3']
                else:
                    print("\033[33m" + 'SLOT#3 LOSS Power Connection Warning !!!' + "\033[0m")
                    slot3 = ' '
                    Slot_change = True
            # print("\033[34m" + '\nPlease Check the Result: \n    press y to continue \n    press n to break' + "\033[0m")

            if Slot_change:
                print('Check the SLOT or rewrite the femb_info.csv and Restart, Wait ...')
                power_off = ["ssh", "root@192.168.121.123", "cd BNL_CE_WIB_SW_QC; python3 top_femb_powering.py off off off off"]
                subrun(power_off, timeout=60)
                while True:
                    print('Enter "R" to restart, Enter "E" to exit')
                    order = input('')
                    if order.lower() == "r":
                        print('Restart this section')
                        break
                    elif order.lower() == "e":
                        rigol.RigolDP800().close()
                        sys.exit()
            else:
                time.sleep(1)
                command2 = ["ssh", "root@192.168.121.123", "cd BNL_CE_WIB_SW_QC;  python3 top_chkout_pls_fake_timing.py {} save 5".format(slot_list)]
                result2 = subrun(command2, timeout=60)
                time.sleep(1)
                command3 = ["ssh", "root@192.168.121.123", "cd BNL_CE_WIB_SW_QC; python3 top_femb_powering.py off off off off"]
                result3 = subrun(command3, timeout=60)
                result = result1 and result2 and result3
                if result != None:
                    if "Done" in result.stdout:
                        print(datetime.utcnow(), "\033[92m  : SUCCESS!  \033[0m")
                    else:
                        print("FAIL!")
                        print(result.stdout)
                        return None
                        # exit()
                    logs['WIB_start_up'] = result.stdout
                else:
                    print("FAIL!")
                    return None
                break

    # ========== Begin of 02 checkout ==========================
    if QC_TST_EN == 2:
        times = 0
        while True:
            times += 1
            print(datetime.utcnow(), " : Start FEMB Checkout.(takes < 180s)")
            print(datetime.utcnow(), " : New Test Item Starts, please wait...")
            command = [
                "ssh", "-o", "BatchMode=yes", "root@192.168.121.123",
                "rm -rf /home/root/BNL_CE_WIB_SW_QC/CHK/"
            ]
            try:
                result = subprocess.run(command, timeout=10, capture_output=True)
            except subprocess.TimeoutExpired:
                print('No previous document found. Skipping removal.')
            print("\033[96m 0 : Initilization {} Temperature Checkout\033[0m".format(tmp))
            command = ["ssh", "root@192.168.121.123", "cd BNL_CE_WIB_SW_QC; python3 femb_assembly_chk.py {} save 5".format(slot_list)]
            user_input_1 = "{}\n{}\n{}\n{}\n{}".format(input_info['tester'], input_info['env'], input_info['toy_TPC'], input_info['comment'], FEMB_list)
            result = subrun(command, timeout=300, user_input=user_input_1)  # rewrite with Popen later
            time.sleep(0.01)
            if result != None:
                resultstr = result.stdout
                logs["QC_TestItemID_%03d" % 0] = [command, resultstr]
                if "Pass" in result.stdout:
                    print(datetime.utcnow(), "\033[92m  : SUCCESS!  \033[0m")
                elif "is on" in result.stdout:
                    print(datetime.utcnow(), "\033[92m  : SUCCESS & Turn FEMB on!  \033[0m")
                elif "Turn All FEMB off" in result.stdout:
                    print(datetime.utcnow(), "\033[92m  : SUCCESS & Done!  \033[0m")
                else:
                    print("FAIL!")
                    print(result.stdout)
                    print("Exit anyway")
                    return None  ### we need to concern if the None is needed here, because it will fall in a loop
                    # exit()
                chkcheck = result.stdout

                # print(result.stdout)  # debug

                print("Transfer data to PC...")
                fdir = '/home/root/BNL_CE_WIB_SW_QC/CHK/'
                fdir2 = '/home/root/BNL_CE_WIB_SW_QC/CHK/Report/'

                # wib_raw_dir = fdir #later save it into log file
                logs['wib_raw_dir'] = fdir
                logs['checkout_termial'] = result.stdout
                # fs = resultstr[resultstr.find("save_file_start_") + 16:resultstr.find("_end_save_file")]
                fsubdirs = fdir.split("/")
                logs['PC_rawdata_root'] = root + "Data/" + "Time_{}_CTS_{}{}".format(
                    current_time.strftime("%Y_%m/%d_%H_%M_%S"), logs['CTS_IDs'], savename)
                logs['PC_rawreport_root'] = root + "Report/" + "Time_{}_CTS_{}{}".format(
                    current_time.strftime("%Y_%m/%d_%H_%M_%S"), logs['CTS_IDs'], savename)
                fddir = logs['PC_rawdata_root'] + '_CHK/' + fsubdirs[-1]
                fddir2 = logs['PC_rawreport_root'] + '_CHK/' + fsubdirs[-1]
                if not os.path.exists(fddir):
                    try:
                        os.makedirs(fddir)
                    except OSError:
                        print("Error to create folder")
                        print("Exit anyway")
                        # sys.exit()
                        return None
                if not os.path.exists(fddir2):
                    try:
                        os.makedirs(fddir2)
                    except OSError:
                        print("Error to create folder")
                        print("Exit anyway")
                        # sys.exit()
                        return None
                wibhost = "root@192.168.121.123:"
                fsrc = wibhost + fdir
                fsrc2 = wibhost + fdir2
                command = ["scp -r " + fsrc2 + " " + fddir2]
                subrun(command, timeout=10, check=False, out = False)
                time.sleep(1)
                command = ["scp -r " + fsrc + " " + fddir]
                result = subrun(command, timeout=10, check=False, out = False)
                if 'LN' in tmp:
                    os.makedirs(fddir2, exist_ok=True)
                    fname = fddir2 + "LN_first_power_output.txt"
                    with open(fname, "w", encoding="utf-8") as f:
                        f.write(LN_result)
                time.sleep(0.01)
                # if result != None:
                # print("data save at {}".format(fddir))
                logs['pc_raw_dir'] = fddir  # later save it into log file
                logs["QC_TestItemID_0_SCP"] = [command, result]
                logs["QC_TestItemID_0_Save"] = logs['pc_raw_dir']
                print(datetime.utcnow(), "\033[92m  : SUCCESS!  \033[0m")
                # else:
                #     print("FAIL!")
                #     return None

                # ##############################################
                check_tmp = True
                if '0' in slot_list:
                    if 'Slot 0 PASS	 ALL ASSEMBLY CHECKOUT' in chkcheck:
                        print("\033[32m" + 'SLOT#0 CHECKOUT Normal' + "\033[0m")
                    else:
                        print("\033[33m" + 'SLOT#0 LOSS CHECKOUT Warning !!!' + "\033[0m")
                        check_tmp = False
                if '1' in slot_list:
                    if 'Slot 1 PASS	 ALL ASSEMBLY CHECKOUT' in chkcheck:
                        print("\033[32m" + 'SLOT#1 CHECKOUT Normal' + "\033[0m")
                    else:
                        print("\033[33m" + 'SLOT#1 LOSS CHECKOUT Warning !!!' + "\033[0m")
                        check_tmp = False
                if '2' in slot_list:
                    if 'Slot 2 PASS	 ALL ASSEMBLY CHECKOUT' in chkcheck:
                        print("\033[32m" + 'SLOT#2 CHECKOUT Normal' + "\033[0m")
                    else:
                        print("\033[33m" + 'SLOT#2 LOSS CHECKOUT Warning !!!' + "\033[0m")
                        check_tmp = False
                if '3' in slot_list:
                    if 'Slot 3 PASS	 ALL ASSEMBLY CHECKOUT' in chkcheck:
                        print("\033[32m" + 'SLOT#3 CHECKOUT Normal' + "\033[0m")
                    else:
                        print("\033[33m" + 'SLOT#3 LOSS CHECKOUT Warning !!!' + "\033[0m")
                        check_tmp = False

                for root, dirs, files in os.walk(fddir):
                    for file in files:
                        file_name = os.path.join(root, file)
                        file_name = file_name.replace('\\', '/')
                        if 'N0.md' in file_name:
                            print(file_name)
                            preview_url = f'file://{file_name}'
                            webbrowser.open(preview_url)
                        if 'N1.md' in file_name:
                            print(file_name)
                            preview_url = f'file://{file_name}'
                            webbrowser.open(preview_url)
                        if 'N2.md' in file_name:
                            print(file_name)
                            preview_url = f'file://{file_name}'
                            webbrowser.open(preview_url)
                        if 'N3.md' in file_name:
                            print(file_name)
                            preview_url = f'file://{file_name}'
                            webbrowser.open(preview_url)

    #            ###################################################
                # remove raw folder in wib side
                print('Begin to remove data at WIB')
                command = [
                    "ssh", "-o", "BatchMode=yes", "root@192.168.121.123",
                    "rm -rf /home/root/BNL_CE_WIB_SW_QC/CHK/"
                ]
                try:
                    result = subprocess.run(command, timeout=10, capture_output=True)
                except subprocess.TimeoutExpired:
                    print('Jump Remove')

                if check_tmp:
                    print('Assembly Checkout Completed!')
                    filename = os.path.join(fddir, 'logs.txt')
                    with open(filename, 'w') as f:
                        pprint.pprint(logs, stream=f)  # Pretty print to file
                    print(f"Logs saved to {filename}")
                    break
                else:
                    while True:
                        print("Enter 'y' to continue\nEnter 'r' to Retry \nEnter 'e' to exit")
                        Next = input(Fore.YELLOW + '>> ' + Style.RESET_ALL)
                        if Next == 'y' or input_info['env'] == 'y':
                            print('Continue QC')
                            signal_1 = True
                            print("Enter 'confirm' to continue")
                            com = input(Fore.YELLOW + '>> ' + Style.RESET_ALL)
                            if com == "confirm":
                                break
                            else:
                                print("Retry Please")
                        elif Next == 'r':
                            print('Retest, Continue')
                            signal_1 = False
                            print("Enter 'confirm' to retest")
                            com = input(Fore.YELLOW + '>> ' + Style.RESET_ALL)
                            if com == "confirm":
                                break
                            else:
                                print("Retry Please")
                        elif Next == 'e':
                            print('Exit ...')
                            print('Please Power OFF and Close the Power Supply!')
                            signal_1 = False
                            print("Enter 'confirm' to exit")
                            com = input(Fore.YELLOW + '>> ' + Style.RESET_ALL)
                            if com == "confirm":
                                subrun(["ssh", "root@192.168.121.123", "poweroff"], check=False, out=False)
                                time.sleep(5)
                                rigol.RigolDP800().close()
                                sys.exit()
                            else:
                                print("Retry Please")
                    if signal_1:
                        break
            # error handling
            else:
                if 'LN' in tmp:
                    if times == 1:
                        print("Retry please")
                    elif times == 2:
                        print("Issue Checkout in LN2, continue QC for Debug")
                        break
                else:
                    if times == 1:
                        print("Please Check the Data Cable Connection at WIB side, and retry!")
                        a = input("enter 'confirm' to continue")
                        while True:
                            if a == 'confirm':
                                break
                    elif times == 2:
                        print("Please Check the Data Cable Connection at Chamber CE side, and retry!")
                        a = input("enter 'confirm' to continue")
                        while True:
                            if a == 'confirm':
                                break
                    else:
                        print("FAIL Checkout...")
                        return None


    # ========== begin of 03 QC ==========================
    if QC_TST_EN == 3:
        time.sleep(1)
        t1 = time.time()
        print(datetime.utcnow(), " : Start FEMB QC")
        # 03_1 QC item test
        for testid in tms:
            # t1 = time.time()
            print(datetime.utcnow(), " : New Test Item Starts, please wait...")
            print(tms_items[testid])
            # the & is used to close the client, so that the issue can be avoided
            command = ["ssh", "root@192.168.121.123", "cd BNL_CE_WIB_SW_QC; python3 QC_top.py {} -t {}".format(slot_list, testid)]
            user_input_1 = "{}\n{}\n{}\n{}\n{}".format(input_info['tester'], input_info['env'], input_info['toy_TPC'], input_info['comment'], FEMB_list)
            result = subrun(command, timeout=1000, user_input=user_input_1)  # rewrite with Popen later
            time.sleep(0.01)
            if result != None:
                resultstr = result.stdout
                logs["QC_TestItemID_%03d" % testid] = [command, resultstr]
                if "Pass!" in result.stdout:
                    print(datetime.utcnow(), "\033[92m  : Mission SUCCESS!  \033[0m")
                elif "QC Item Begin" in result.stdout:
                    print(datetime.utcnow(), "\033[92m  : FEMB QC Begin!  \033[0m")
                    # continue #in FEMB QC, we want to send the data first
                elif "QC Item Done" in result.stdout:
                    print(datetime.utcnow(), "\033[92m  : SUCCESS & Done!  \033[0m")
                    break
                else:
                    print("FAIL!")
                    print(result.stdout)
                    print("Exit anyway")
                    return None
                    # exit()
            else:
                print("FAIL!")
                #print(result.stdout)
                return None

            # 03_2 QC data transfer to PC
            print("Transfer data to PC...")
            fdir = '/home/root/BNL_CE_WIB_SW_QC/QC'
            logs['wib_raw_dir'] = fdir
            fsubdirs = fdir.split("/")
            logs['PC_rawdata_root'] = root + "Data/" + "Time_{}_CTS_{}{}".format(
                current_time.strftime("%Y_%m/%d_%H_%M_%S"), logs['CTS_IDs'], savename)
            logs['PC_rawreport_root'] = root + "Report/" + "Time_{}_CTS_{}{}".format(
                current_time.strftime("%Y_%m/%d_%H_%M_%S"), logs['CTS_IDs'], savename)
            fddir = logs['PC_rawdata_root'] + '_QC/'
            # fddir = logs['PC_rawdata_root'] + fsubdirs[-1] + "/"
            print(fddir)

            if not os.path.exists(fddir):
                try:
                    os.makedirs(fddir)
                except OSError:
                    print("Error to create folder")
                    print("Exit anyway")
                    return None
            wibhost = "root@192.168.121.123:"
            fsrc = wibhost + fdir
            # move folder
            command = ["scp -r " + fsrc + " " + fddir]
            result = subrun(command, timeout=100, check=False, out=False)
            # if result != None:
            print("data save at {}".format(fddir))
            logs['pc_raw_dir'] = fddir  # later save it into log file
            logs["QC_TestItemID_%03d_SCP" % testid] = [command, result]
            logs["QC_TestItemID_%03d_Save" % testid] = logs['pc_raw_dir']
            print(datetime.utcnow(), "\033[92m  : SUCCESS!  \033[0m")
            # else:
            #     print("FAIL!")
            #     return None

            # 03_3 raw folder in wib side
            print('Begin to remove data at WIB')
            time.sleep(1)
            command = [
                "ssh", "-o", "BatchMode=yes", "root@192.168.121.123",
                "rm -rf /home/root/BNL_CE_WIB_SW_QC/QC/"
            ]
            # t2 = time.time()
            # print('item {} time consumption {}'.format(tms_items[testid], t2 - t1))
            try:
                result = subprocess.run(command, timeout=10, capture_output=True)
            except subprocess.TimeoutExpired:
                print('Jump Remove')
        t2 = time.time()
        print('QC time consumption is: {}'.format(t2 - t1))


    if QC_TST_EN == 6:
        print("Power Off the Linux on WIB PS [6 second]")
        subrun(["ssh", "root@192.168.121.123", "poweroff"], check=False, out = False)
        time.sleep(6)
        print("Done! [Check that the current should be less than 1.5 A]")

    # ========== end of 03 QC ==========================

    # if True:
    if QC_TST_EN == 10:
        print("save log info during QC")
        if True:
            logging.basicConfig(filename='QC.log',
                                level=logging.INFO,
                                format='%(asctime)s - %(levelname)s - %(message)s') # Lingyun Ke set
            logging.info('info: %s', logs)
    QCstatus = "PASS"
    bads = []
    data_path = logs['PC_rawdata_root']
    report_path = logs['PC_rawreport_root']

    return QCstatus, bads, data_path, report_path
