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
    # LN_result = ""
    # if QC_TST_EN == 1:
    #     while True:
    #         print(datetime.utcnow(), "\033[35m  : Start FEMB SLOT Confirm (it takes < 60s)\n  \033[0m")
    #         if 'LN' in tmp:
    #             command1 = ["ssh", "root@192.168.121.123", "cd BNL_CE_WIB_SW_QC;  python3 top_femb_powering_LN.py {}".format(power_en)]
    #             result = subrun(command1, timeout=60)
    #             LN_result = result
    #
    #             time.sleep(2)
    #             print("Cold initial")
    #             command1 = ["ssh", "root@192.168.121.123",
    #                         "cd BNL_CE_WIB_SW_QC;  python3 top_femb_powering.py {}".format(power_en)]
    #             result1 = subrun(command1, timeout=60, out=False)
    #             print("FEMB Cold Power On")
    #         else:
    #             command1 = ["ssh", "root@192.168.121.123", "cd BNL_CE_WIB_SW_QC;  python3 top_femb_powering.py {}".format(power_en)]
    #             print("Warm initial")
    #             result1 = subrun(command1, timeout=60, out = False)
    #         SlotCheck = result1.stdout
    #         print(SlotCheck)
    #         if '0' in slot_list:
    #             if 'SLOT#0 Power Connection Normal' in SlotCheck:
    #                 print("\033[32m" + 'SLOT#0 Power Connection Normal' + "\033[0m")
    #                 slot0 = input_info['SLOT0']
    #             else:
    #                 print("\033[33m" + 'SLOT#0 LOSS Power Connection Warning !!!' + "\033[0m")
    #                 Slot_change = True
    #                 slot0 = ' '
    #         if '1' in slot_list:
    #             if 'SLOT#1 Power Connection Normal' in SlotCheck:
    #                 print("\033[32m" + 'SLOT#1 Power Connection Normal' + "\033[0m")
    #                 slot1 = input_info['SLOT1']
    #             else:
    #                 print("\033[33m" + 'SLOT#1 LOSS Power Connection Warning !!!' + "\033[0m")
    #                 slot1 = ' '
    #                 Slot_change = True
    #         if '2' in slot_list:
    #             if 'SLOT#2 Power Connection Normal' in SlotCheck:
    #                 print("\033[32m" + 'SLOT#2 Power Connection Normal' + "\033[0m")
    #                 slot2 = input_info['SLOT2']
    #             else:
    #                 print("\033[33m" + 'SLOT#2 LOSS Power Connection Warning !!!' + "\033[0m")
    #                 slot2 = ' '
    #                 Slot_change = True
    #         if '3' in slot_list:
    #             if 'SLOT#3 Power Connection Normal' in SlotCheck:
    #                 print("\033[32m" + 'SLOT#3 Power Connection Normal' + "\033[0m")
    #                 slot3 = input_info['SLOT3']
    #             else:
    #                 print("\033[33m" + 'SLOT#3 LOSS Power Connection Warning !!!' + "\033[0m")
    #                 slot3 = ' '
    #                 Slot_change = True
    #         # print("\033[34m" + '\nPlease Check the Result: \n    press y to continue \n    press n to break' + "\033[0m")
    #
    #         if Slot_change:
    #             print('Check the SLOT or rewrite the femb_info.csv and Restart, Wait ...')
    #             power_off = ["ssh", "root@192.168.121.123", "cd BNL_CE_WIB_SW_QC; python3 top_femb_powering.py off off off off"]
    #             subrun(power_off, timeout=60)
    #             while True:
    #                 print('Enter "R" to restart, Enter "E" to exit')
    #                 order = input('')
    #                 if order.lower() == "r":
    #                     print('Restart this section')
    #                     break
    #                 elif order.lower() == "e":
    #                     rigol.RigolDP800().close()
    #                     sys.exit()
    #         else:
    #             time.sleep(1)
    #             command2 = ["ssh", "root@192.168.121.123", "cd BNL_CE_WIB_SW_QC;  python3 top_chkout_pls_fake_timing.py {} save 5".format(slot_list)]
    #             result2 = subrun(command2, timeout=60)
    #             time.sleep(1)
    #             command3 = ["ssh", "root@192.168.121.123", "cd BNL_CE_WIB_SW_QC; python3 top_femb_powering.py off off off off"]
    #             result3 = subrun(command3, timeout=60)
    #             result = result1 and result2 and result3
    #             if result != None:
    #                 if "Done" in result.stdout:
    #                     print(datetime.utcnow(), "\033[92m  : SUCCESS!  \033[0m")
    #                 else:
    #                     print("FAIL!")
    #                     print(result.stdout)
    #                     return None
    #                     # exit()
    #                 logs['WIB_start_up'] = result.stdout
    #             else:
    #                 print("FAIL!")
    #                 return None
    #             break

    # ========== Begin of 01 FEMB Slot Confirm ==========================

    # ========== Begin of 01 FEMB Slot Confirm ==========================

    def check_slot_connection(slot_check_output, slot_num, slot_info):
        """
        检查单个SLOT的电源连接状态

        Args:
            slot_check_output: SlotCheck输出字符串
            slot_num: SLOT编号 (0-3)
            slot_info: 对应的SLOT信息

        Returns:
            tuple: (slot_value, is_changed)
        """
        slot_msg = f'SLOT#{slot_num} Power Connection Normal'

        if slot_msg in slot_check_output:
            print(f"\033[32m{slot_msg}\033[0m")
            return slot_info, False
        else:
            print(f"\033[33mSLOT#{slot_num} LOSS Power Connection Warning !!!\033[0m")
            return ' ', True

    def power_off_all_slots():
        """关闭所有SLOT电源"""
        power_off_cmd = [
            "ssh", "root@192.168.121.123",
            "cd BNL_CE_WIB_SW_QC; python3 top_femb_powering.py off off off off"
        ]
        subrun(power_off_cmd, timeout=60)

    def run_femb_powering(power_en, is_ln_mode=False):
        """
        运行FEMB上电流程

        Args:
            power_en: 电源使能参数
            is_ln_mode: 是否为LN(液氮)模式

        Returns:
            str: SlotCheck输出字符串
        """
        if is_ln_mode:
            # LN模式：先执行液氮上电
            print("Cold initial")
            ln_command = [
                "ssh", "root@192.168.121.123",
                f"cd BNL_CE_WIB_SW_QC; python3 top_femb_powering_LN.py {power_en}"
            ]
            ln_result = subrun(ln_command, timeout=60)
            time.sleep(2)

            # 再执行常规上电
            command = [
                "ssh", "root@192.168.121.123",
                f"cd BNL_CE_WIB_SW_QC; python3 top_femb_powering.py {power_en}"
            ]
            print("FEMB Cold Power On")
        else:
            # 常温模式
            print("Warm initial")
            command = [
                "ssh", "root@192.168.121.123",
                f"cd BNL_CE_WIB_SW_QC; python3 top_femb_powering.py {power_en}"
            ]

        result = subrun(command, timeout=60, out=False)

        # 确保返回字符串
        if hasattr(result, 'stdout'):
            slot_check = result.stdout
            if isinstance(slot_check, bytes):
                slot_check = slot_check.decode('utf-8')
        else:
            slot_check = str(result)

        return slot_check, ln_result if is_ln_mode else None

    def handle_slot_check_failure():
        """处理SLOT检查失败的情况"""
        print('Check the SLOT or rewrite the femb_info.csv and Restart, Wait ...')
        power_off_all_slots()

        while True:
            print('Enter "R" to restart, Enter "E" to exit')
            order = input('').strip().lower()

            if order == "r":
                print('Restart this section')
                return True  # 返回True表示重启
            elif order == "e":
                rigol.RigolDP800().close()
                sys.exit()
            else:
                print("Invalid input. Please enter 'R' or 'E'")

    def run_post_slot_check_commands(slot_list):
        """
        运行SLOT检查成功后的后续命令

        Args:
            slot_list: SLOT列表字符串

        Returns:
            tuple: (success, combined_output)
        """
        try:
            # 命令1: checkout timing
            time.sleep(1)
            command2 = [
                "ssh", "root@192.168.121.123",
                f"cd BNL_CE_WIB_SW_QC; python3 top_chkout_pls_fake_timing.py {slot_list} save 5"
            ]
            result2 = subrun(command2, timeout=60)

            # 命令2: 关闭电源
            time.sleep(1)
            command3 = [
                "ssh", "root@192.168.121.123",
                "cd BNL_CE_WIB_SW_QC; python3 top_femb_powering.py off off off off"
            ]
            result3 = subrun(command3, timeout=60)

            # 合并结果输出
            outputs = []
            for result in [result2, result3]:
                if hasattr(result, 'stdout'):
                    output = result.stdout
                    if isinstance(output, bytes):
                        output = output.decode('utf-8')
                    outputs.append(output)

            combined_output = '\n'.join(outputs)

            # 检查cable连接失败
            if "Cable Test Done" not in combined_output:
                print("\033[31m!!! Cable Test FAILED: Check data cable connection !!!\033[0m")
                print("\033[33m(All FEMBs are powered off)\033[0m")
                return False, combined_output

            # 检查是否成功
            if 'Cable Test Done'and "Done" in combined_output:
                print('Cable Test Normal')
                return True, combined_output
            else:
                return False, combined_output

        except Exception as e:
            print(f"Error during post-check commands: {e}")
            return False, str(e)

    # ========== 主流程 ==========================
    LN_result = ""

    if QC_TST_EN == 1:
        while True:
            print(datetime.utcnow(), "\033[35m  : Start FEMB SLOT Confirm (it takes < 60s)\n  \033[0m")

            # 执行FEMB上电并获取SlotCheck结果
            is_ln_mode = 'LN' in tmp
            SlotCheck, LN_result = run_femb_powering(power_en, is_ln_mode)

            # 检查各个SLOT的连接状态
            Slot_change = False
            slot_mapping = {
                '0': ('SLOT0', 'slot0'),
                '1': ('SLOT1', 'slot1'),
                '2': ('SLOT2', 'slot2'),
                '3': ('SLOT3', 'slot3')
            }

            for slot_num, (info_key, var_name) in slot_mapping.items():
                if slot_num in slot_list:
                    slot_value, is_changed = check_slot_connection(
                        SlotCheck,
                        slot_num,
                        input_info[info_key]
                    )
                    # 动态设置变量
                    globals()[var_name] = slot_value
                    Slot_change = Slot_change or is_changed

            # 根据检查结果执行相应操作
            if Slot_change:
                # SLOT连接有问题，处理失败情况
                should_restart = handle_slot_check_failure()
                if should_restart:
                    continue  # 重新开始循环
            else:
                # SLOT连接正常，执行后续命令
                success, output = run_post_slot_check_commands(slot_list)

                if success:
                    print(datetime.utcnow(), "\033[92m  : SUCCESS!  \033[0m")
                    logs['WIB_start_up'] = output
                    break  # 成功，退出循环
                else:
                    print("FAIL!")
                    # print(output)
                    return None

    # ========== End of 01 FEMB Slot Confirm ==========================



    # 配置常量
    class Config:
        WIB_HOST = "root@192.168.121.123"
        WIB_CHK_DIR = "/home/root/BNL_CE_WIB_SW_QC/CHK/"
        WIB_REPORT_DIR = "/home/root/BNL_CE_WIB_SW_QC/CHK/Report/"
        CHECKOUT_TIMEOUT = 300
        SCP_TIMEOUT = 10
        MAX_RETRIES = 3
        VALID_SLOTS = ['0', '1', '2', '3']

    class CheckoutResult:
        """封装checkout结果"""

        def __init__(self, success, message, data_dir=None):
            self.success = success
            self.message = message
            self.data_dir = data_dir

    class FEMBCheckout:
        def __init__(self, slot_list, tmp, input_info, logs, root, savename, current_time):
            self.slot_list = slot_list
            self.tmp = tmp
            self.input_info = input_info
            self.logs = logs
            self.root = root
            self.savename = savename
            self.current_time = current_time

        def run(self):
            """主执行流程"""
            for attempt in range(1, Config.MAX_RETRIES + 1):
                print(f"{datetime.utcnow()} : Start FEMB Checkout (Attempt {attempt}/{Config.MAX_RETRIES})")

                result = self._execute_checkout()

                if result.success:
                    return result

                if not self._handle_failure(attempt):
                    return CheckoutResult(False, "User cancelled")

            return CheckoutResult(False, "Max retries exceeded")

        def _execute_checkout(self):
            """执行一次完整的checkout流程"""
            # 1. 清理WIB端数据
            self._cleanup_wib_data()

            # 2. 运行checkout测试
            test_result = self._run_femb_test()
            if not test_result:
                return CheckoutResult(False, "Test execution failed")

            # 3. 传输数据
            data_dirs = self._transfer_data(test_result)
            if not data_dirs:
                return CheckoutResult(False, "Data transfer failed")

            # 4. 验证结果
            validation = self._validate_checkout(test_result.stdout)

            # 5. 打开报告
            self._open_reports(data_dirs['raw'])

            # 6. 清理WIB端数据
            self._cleanup_wib_data()

            if validation['all_passed']:
                self._save_logs(data_dirs['raw'])
                return CheckoutResult(True, "Checkout completed", data_dirs['raw'])
            else:
                return self._handle_validation_failure(validation, data_dirs['raw'])

        def _cleanup_wib_data(self):
            """清理WIB端的数据目录"""
            command = [
                "ssh", "-o", "BatchMode=yes", Config.WIB_HOST,
                f"rm -rf {Config.WIB_CHK_DIR}"
            ]
            try:
                subprocess.run(command, timeout=Config.SCP_TIMEOUT, capture_output=True)
            except subprocess.TimeoutExpired:
                print('Cleanup timeout, continuing...')

        def _run_femb_test(self):
            """运行FEMB测试"""
            print(f"\033[96m 0 : Initialization {self.tmp} Temperature Checkout\033[0m")

            command = [
                "ssh", Config.WIB_HOST,
                f"cd BNL_CE_WIB_SW_QC; python3 femb_assembly_chk.py {self.slot_list} save 5"
            ]

            user_input = "\n".join([
                self.input_info['tester'],
                self.input_info['env'],
                self.input_info['toy_TPC'],
                self.input_info['comment'],
                FEMB_list
            ])

            result = subrun(command, timeout=Config.CHECKOUT_TIMEOUT, user_input=user_input)

            if result is None:
                return None

            # 记录日志
            self.logs["QC_TestItemID_000"] = [command, result.stdout]
            self.logs['wib_raw_dir'] = Config.WIB_CHK_DIR
            self.logs['checkout_terminal'] = result.stdout

            # 检查测试结果
            if any(keyword in result.stdout for keyword in ["Pass", "is on", "Turn All FEMB off"]):
                print(f"{datetime.utcnow()} \033[92m : SUCCESS! \033[0m")
                return result
            else:
                print("FAIL!")
                print(result.stdout)
                return None

        def _transfer_data(self, test_result):
            """传输数据到PC"""
            print("Transfer data to PC...")

            # 创建目标目录
            time_prefix = self.current_time.strftime("%Y_%m/%d_%H_%M_%S")
            base_name = f"Time_{time_prefix}_CTS_{self.logs['CTS_IDs']}{self.savename}"

            raw_dir = os.path.join(self.root, "Data", f"{base_name}_CHK/CHK")
            report_dir = os.path.join(self.root, "Report", f"{base_name}_CHK/CHK")

            self.logs['PC_rawdata_root'] = os.path.dirname(raw_dir)
            self.logs['PC_rawreport_root'] = os.path.dirname(report_dir)

            # 创建目录
            for directory in [raw_dir, report_dir]:
                try:
                    os.makedirs(directory, exist_ok=True)
                except OSError as e:
                    print(f"Error creating folder {directory}: {e}")
                    return None

            # SCP传输
            wib_src = f"{Config.WIB_HOST}:{Config.WIB_CHK_DIR}"
            wib_report_src = f"{Config.WIB_HOST}:{Config.WIB_REPORT_DIR}"

            # 传输报告
            self._scp_transfer(wib_report_src, report_dir)

            # 传输原始数据
            if not self._scp_transfer(wib_src, raw_dir):
                return None

            # 如果是LN测试，保存额外数据
            if 'LN' in self.tmp:
                self._save_ln_data(report_dir)

            self.logs['pc_raw_dir'] = raw_dir
            print(f"{datetime.utcnow()} \033[92m : SUCCESS! \033[0m")

            return {'raw': raw_dir, 'report': report_dir}

        def _scp_transfer(self, src, dst):
            """执行SCP传输"""
            command = [f"scp -r {src} {dst}"]
            result = subrun(command, timeout=Config.SCP_TIMEOUT, check=False, out=False)
            time.sleep(0.01)
            return result is not None

        def _save_ln_data(self, report_dir):
            """保存LN测试数据"""
            fname = os.path.join(report_dir, "LN_first_power_output.txt")
            with open(fname, "w", encoding="utf-8") as f:
                f.write(LN_result)

        def _validate_checkout(self, stdout):
            """验证每个slot的checkout结果"""
            validation = {'all_passed': True, 'failed_slots': []}

            for slot in Config.VALID_SLOTS:
                if slot not in self.slot_list:
                    continue

                expected_msg = f'Slot {slot} PASS\t ALL ASSEMBLY CHECKOUT'
                if expected_msg in stdout:
                    print(f"\033[32mSLOT#{slot} CHECKOUT Normal\033[0m")
                else:
                    print(f"\033[33mSLOT#{slot} LOSS CHECKOUT Warning !!!\033[0m")
                    validation['all_passed'] = False
                    validation['failed_slots'].append(slot)

            return validation

        def _open_reports(self, data_dir):
            """打开markdown报告文件"""
            for root, dirs, files in os.walk(data_dir):
                for file in files:
                    if file.endswith('.md') and any(f'N{i}.md' in file for i in range(4)):
                        file_path = os.path.join(root, file).replace('\\', '/')
                        print(file_path)
                        webbrowser.open(f'file://{file_path}')

        def _handle_validation_failure(self, validation, data_dir):
            """处理验证失败的情况"""
            while True:
                print("\n" + "=" * 50)
                print(f"Failed slots: {', '.join(validation['failed_slots'])}")
                print("=" * 50)
                print("Options:")
                print("  'y' - Continue anyway")
                print("  'r' - Retry checkout")
                print("  'e' - Exit")

                choice = input(Fore.YELLOW + '>> ' + Style.RESET_ALL).lower()

                if choice == 'y':
                    if self._confirm_action("continue"):
                        self._save_logs(data_dir)
                        return CheckoutResult(True, "Continued despite failures", data_dir)

                elif choice == 'r':
                    if self._confirm_action("retry"):
                        return CheckoutResult(False, "User requested retry")

                elif choice == 'e':
                    if self._confirm_action("exit"):
                        self._shutdown_system()
                        sys.exit()

        def _confirm_action(self, action):
            """确认用户操作"""
            confirmation = input(f"Enter 'confirm' to {action}: ")
            if confirmation == "confirm":
                return True
            print("Action cancelled, please try again")
            return False

        def _handle_failure(self, attempt):
            """处理测试失败"""
            if 'LN' in self.tmp:
                if attempt == 1:
                    print("Retry please")
                    return True
                else:
                    print("Issue in LN2 checkout, continuing for debug")
                    return False

            error_messages = {
                1: "Please check the Data Cable Connection at WIB side",
                2: "Please check the Data Cable Connection at Chamber CE side",
            }

            if attempt in error_messages:
                print(error_messages[attempt])
                return self._confirm_action("retry")

            print("FAIL Checkout - max retries exceeded")
            print('Please Power OFF and Close the Power Supply!')
            subrun(["ssh", Config.WIB_HOST, "poweroff"], check=False, out=False)
            time.sleep(5)
            rigol.RigolDP800().close()
            return False

        def _save_logs(self, data_dir):
            """保存日志文件"""
            filename = os.path.join(data_dir, 'logs.txt')
            with open(filename, 'w') as f:
                pprint.pprint(self.logs, stream=f)
            print(f"Logs saved to {filename}")

        def _shutdown_system(self):
            """关闭系统"""
            print('Please Power OFF and Close the Power Supply!')
            subrun(["ssh", Config.WIB_HOST, "poweroff"], check=False, out=False)
            time.sleep(5)
            rigol.RigolDP800().close()

    # 使用方式
    if QC_TST_EN == 2:
        checkout = FEMBCheckout(
            slot_list=slot_list,
            tmp=tmp,
            input_info=input_info,
            logs=logs,
            root=root,
            savename=savename,
            current_time=current_time
        )

        result = checkout.run()

        if not result.success:
            print(f"Checkout failed: {result.message}")
            # 处理失败情况


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
