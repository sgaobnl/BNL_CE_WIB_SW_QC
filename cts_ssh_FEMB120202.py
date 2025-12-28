import logging
import time
import sys
import subprocess
import datetime
import filecmp
import os
from datetime import datetime, timezone
import csv
import webbrowser
from colorama import Fore, Style
import pprint
import GUI.Rigol_DP800 as rigol

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def subrun(command, timeout=30, check=True, out=True, exitflg=True, user_input=None, rm=False, shell=False):
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
def read_csv_to_dict(filename, env, p=False):
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

    # ============= 通用工具函数 =============
    def power_off_femb_channels():
        """只关闭FEMB channel（用于重试前）"""
        print('Powering off FEMB channels...')
        try:
            power_off_cmd = [
                "ssh", "root@192.168.121.123",
                "cd BNL_CE_WIB_SW_QC; python3 top_femb_powering.py off off off off"
            ]
            subrun(power_off_cmd, timeout=60, out=False)
            print(Fore.GREEN + "FEMB channels powered off" + Style.RESET_ALL)
        except Exception as e:
            print(f"Error powering off FEMB channels: {e}")

    def shutdown_power_supply():
        """完整关闭所有电源供应（用于最终退出）"""
        print('Shutting down ALL power supplies...')
        try:
            # 1. 关闭所有FEMB电源
            print('  - Powering off FEMB channels...')
            power_off_cmd = [
                "ssh", "root@192.168.121.123",
                "cd BNL_CE_WIB_SW_QC; python3 top_femb_powering.py off off off off"
            ]
            subrun(power_off_cmd, timeout=60, out=False)

            # 2. 关闭Rigol电源
            print('  - Closing Rigol power supply...')
            rigol.RigolDP800().close()

            # 3. 关闭WIB
            print('  - Powering off WIB...')
            subrun(["ssh", "root@192.168.121.123", "poweroff"], check=False, out=False)
            time.sleep(5)

            print(Fore.GREEN + "All power supplies shut down successfully" + Style.RESET_ALL)
        except Exception as e:
            print(f"Error during shutdown: {e}")

    def confirm_user_action(action_name, require_confirm=False):
        """确认用户操作"""
        if require_confirm:
            confirmation = input(f"Enter 'confirm' to {action_name}: ").strip().lower()
            if confirmation == "confirm":
                return True
            print("Action cancelled")
            return False
        return True

    def prompt_retry_or_exit(error_context="", attempt=1, max_attempts=3):
        """提示用户选择重试或退出（即使超过最大次数也询问）"""
        print("\n" + "=" * 60)
        if error_context:
            print(Fore.RED + f"Error: {error_context}" + Style.RESET_ALL)

        # 如果已经达到或超过最大尝试次数
        if attempt >= max_attempts:
            print(Fore.RED + f"Maximum attempts ({max_attempts}) reached!" + Style.RESET_ALL)
            print("=" * 60)
        else:
            print(f"Attempt {attempt}/{max_attempts}")
            print("=" * 60)

            # 根据尝试次数给出建议
            if attempt == 1:
                print(Fore.YELLOW + "Suggestion: Check data cable connection at WIB side" + Style.RESET_ALL)
            elif attempt == 2:
                print(Fore.YELLOW + "Suggestion: Check data cable connection at Chamber CE side" + Style.RESET_ALL)

        print("\nOptions:")
        print("  'r' - Retry test")
        print("  'e' - Exit and power off")

        while True:
            choice = input(Fore.YELLOW + '>> ' + Style.RESET_ALL).strip().lower()

            if choice == 'r':
                if confirm_user_action("retry"):
                    return 'retry'
            elif choice == 'e':
                if confirm_user_action("exit"):
                    return 'exit'
            else:
                print("Invalid input. Please enter 'r' or 'e'")

    # ============= 原有变量初始化 =============
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
    current_time = datetime.now(timezone.utc)
    # add for AI
    logs['PC_rawdata_root'] = root + "Data/" + "Time_{}_CTS_{}{}".format(current_time.strftime("%Y_%m/%d_%H_%M_%S"),
                                                                         logs['CTS_IDs'], savename)
    logs['PC_rawreport_root'] = root + "Report/" + "Time_{}_CTS_{}{}".format(current_time.strftime("%Y_%m/%d_%H_%M_%S"),
                                                                             logs['CTS_IDs'], savename)
    logs['PC_WRCFG_FN'] = os.path.join(BASE_DIR, "femb_info_implement.csv")

    if QC_TST_EN == 77:
        print(datetime.now(timezone.utc), " : Check if WIB is pingable (it takes < 60s)")
        command = ["ping", "-c", "3", "192.168.121.123"]
        print("COMMAND: ", command)
        attempt = 0
        while True:
            # result = subrun(command, timeout=10)
            result = subrun(command, shell=False)
            if result != None and result.returncode == 0:
                print(datetime.now(timezone.utc), "\033[92m  : SUCCESS!  \033[0m")
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
        print(datetime.now(timezone.utc), " : sync WIB time")
        # Get the current date and time
        now = datetime.now(timezone.utc)
        # Format it to match the output of the `date` command
        formatted_now = now.strftime('%a %b %d %H:%M:%S UTC %Y')
        command = ["ssh", "root@192.168.121.123", "date -s \'{}\'".format(formatted_now)]
        result = subrun(command, timeout=30, shell=False)
        time.sleep(0.01)
        if result != None:
            print("WIB Time: ", result.stdout)
            print(datetime.now(timezone.utc), "\033[92m  : SUCCESS!  \033[0m")
            logs['WIB_UTC_Date_Time'] = result.stdout
        else:
            print("FAIL!")
            return None

    if QC_TST_EN == 0:
        print(datetime.now(timezone.utc), " : Start WIB initialization (it takes < 30s)")
        command = ["ssh", "root@192.168.121.123", "cd BNL_CE_WIB_SW_QC;  python3 wib_startup.py"]
        result = subrun(command, timeout=30)
        time.sleep(0.01)
        if result != None:
            if "Done" in result.stdout:
                print(datetime.now(timezone.utc), "\033[92m  : SUCCESS!  \033[0m")
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
        print(datetime.now(timezone.utc), " : load configuration file from PC")
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
                    print(datetime.now(timezone.utc), "\033[92m  : SUCCESS!  \033[0m")
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

    # ========== Begin of 01 FEMB Slot Confirm (优化版) ==========================

    def check_slot_connection(slot_check_output, slot_num, slot_info):
        """检查单个SLOT的电源连接状态"""
        slot_msg = f'SLOT#{slot_num} Power Connection Normal'

        if slot_msg in slot_check_output:
            print(f"\033[32m{slot_msg}\033[0m")
            return slot_info, False
        else:
            print(f"\033[33mSLOT#{slot_num} Power Connection LOST Warning !!!\033[0m")
            return ' ', True

    def run_femb_powering(power_en, is_ln_mode=False):
        """运行FEMB上电流程"""
        ln_result = None

        if is_ln_mode:
            print("Cold initial (LN mode)")
            ln_command = [
                "ssh", "root@192.168.121.123",
                f"cd BNL_CE_WIB_SW_QC; python3 top_femb_powering_LN.py {power_en}"
            ]
            ln_result = subrun(ln_command, timeout=60, out=True)  # 显示输出
            time.sleep(2)
            print("FEMB Cold Power On")
        else:
            print("Warm initial")

        # 执行常规上电
        command = [
            "ssh", "root@192.168.121.123",
            f"cd BNL_CE_WIB_SW_QC; python3 top_femb_powering.py {power_en}"
        ]
        result = subrun(command, timeout=60, out=True)  # 显示输出

        # 提取stdout用于检查
        if hasattr(result, 'stdout'):
            slot_check = result.stdout
            if isinstance(slot_check, bytes):
                slot_check = slot_check.decode('utf-8')
        else:
            slot_check = str(result)

        return slot_check, ln_result

    def run_cable_test(slot_list):
        """运行cable测试"""
        try:
            print("\n[Running Cable Test...]")
            time.sleep(1)
            command = [
                "ssh", "root@192.168.121.123",
                f"cd BNL_CE_WIB_SW_QC; python3 top_chkout_pls_fake_timing.py {slot_list} save 5"
            ]
            result = subrun(command, timeout=60, out=True)  # 显示输出

            # 提取输出
            output = ""
            if hasattr(result, 'stdout'):
                output = result.stdout
                if isinstance(output, bytes):
                    output = output.decode('utf-8')

            # 验证结果
            if "Cable Test Done" in output:
                print(Fore.GREEN + "Cable Test PASSED" + Style.RESET_ALL)
                return True, output
            else:
                print(Fore.RED + "Cable Test FAILED: Check data cable connection" + Style.RESET_ALL)
                return False, output

        except Exception as e:
            print(f"Error during cable test: {e}")
            return False, str(e)

    # 主流程：QC_TST_EN == 1
    LN_result = ""
    MAX_RETRIES = 3

    if QC_TST_EN == 1:
        is_ln_mode = 'LN' in tmp

        slot_mapping = {
            '0': ('SLOT0', 'slot0'),
            '1': ('SLOT1', 'slot1'),
            '2': ('SLOT2', 'slot2'),
            '3': ('SLOT3', 'slot3')
        }

        attempt = 0
        while True:  # 无限循环，由用户决定何时退出
            attempt += 1

            print(f"\n{datetime.now(timezone.utc)}")
            print(Fore.MAGENTA + f"SLOT Confirmation - Attempt {attempt}" + Style.RESET_ALL)
            print("=" * 60)

            # ========== 步骤1: FEMB上电和SLOT检查 ==========
            print("\n[1/3] FEMB Power-On and SLOT Check...")
            SlotCheck, ln_res = run_femb_powering(power_en, is_ln_mode)

            if is_ln_mode and ln_res:
                LN_result = ln_res

            # 检查各SLOT连接
            Slot_change = False
            for slot_num, (info_key, var_name) in slot_mapping.items():
                if slot_num in slot_list:
                    slot_value, is_changed = check_slot_connection(
                        SlotCheck,
                        slot_num,
                        input_info[info_key]
                    )
                    globals()[var_name] = slot_value
                    Slot_change = Slot_change or is_changed

            # SLOT连接检查失败
            if Slot_change:
                print(Fore.RED + "\nSLOT connection check FAILED" + Style.RESET_ALL)
                print("Please check SLOT connections and femb_info.csv")

                # 只关闭FEMB channel（不关闭Rigol和WIB）
                power_off_femb_channels()

                # 询问用户（即使超过最大次数也询问）
                choice = prompt_retry_or_exit("SLOT connection error", attempt, MAX_RETRIES)

                if choice == 'retry':
                    continue
                elif choice == 'exit':
                    # 用户选择退出，完整关闭所有电源
                    shutdown_power_supply()
                    return None

            # ========== 步骤2: Cable测试 ==========
            print("\n[2/3] Cable Test...")
            cable_success, cable_output = run_cable_test(slot_list)

            if not cable_success:
                # Cable测试失败
                print(Fore.RED + "\nCable test FAILED" + Style.RESET_ALL)

                # 只关闭FEMB channel（不关闭Rigol和WIB）
                power_off_femb_channels()

                # 询问用户（即使超过最大次数也询问）
                choice = prompt_retry_or_exit("Cable connection error", attempt, MAX_RETRIES)

                if choice == 'retry':
                    continue
                elif choice == 'exit':
                    # 用户选择退出，完整关闭所有电源
                    shutdown_power_supply()
                    return None

            # ========== 步骤3: 关闭FEMB电源 ==========
            print("\n[3/3] Powering off all FEMBs...")
            command = [
                "ssh", "root@192.168.121.123",
                "cd BNL_CE_WIB_SW_QC; python3 top_femb_powering.py off off off off"
            ]
            subrun(command, timeout=60, out=False)

            # ========== 成功 ==========
            print(f"\n{datetime.now(timezone.utc)}")
            print(Fore.GREEN + "  ✓ SLOT Confirmation SUCCESS!" + Style.RESET_ALL)

            logs['WIB_start_up'] = cable_output
            if LN_result:
                logs['LN_result'] = LN_result

            break  # 成功，退出循环

    # ========== End of 01 FEMB Slot Confirm ==========================

    # ========== Begin of 02 FEMB Checkout (优化版) ==========================
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
            self.is_ln_mode = 'LN' in tmp

        def run(self):
            """主执行流程（带无限重试机制，由用户决定）"""
            attempt = 0

            while True:  # 无限循环，由用户决定何时退出
                attempt += 1

                print(f"\n{datetime.now(timezone.utc)}")
                print(Fore.MAGENTA + f"FEMB Checkout - Attempt {attempt}" + Style.RESET_ALL)
                print("=" * 60)

                result = self._execute_checkout()

                if result.success:
                    return result

                # 特殊情况：验证失败时用户选择了重试，不需要再次询问
                if result.message == "User requested retry from validation":
                    continue

                # 失败处理
                print(Fore.RED + f"\nCheckout FAILED: {result.message}" + Style.RESET_ALL)

                # 特殊处理：LN模式第一次失败自动重试
                if self.is_ln_mode and attempt == 1:
                    print(Fore.YELLOW + "LN mode: Automatic retry (1st attempt)" + Style.RESET_ALL)
                    continue

                # 询问用户（即使超过最大次数也询问）
                choice = prompt_retry_or_exit(result.message, attempt, Config.MAX_RETRIES)

                if choice == 'retry':
                    continue
                elif choice == 'exit':
                    # 只有用户选择退出时才关闭所有电源
                    shutdown_power_supply()
                    return CheckoutResult(False, "User cancelled")

        def _execute_checkout(self):
            """执行一次完整的checkout流程"""
            try:
                # 1. 清理WIB端数据
                print("\n[1/5] Cleaning WIB data...")
                self._cleanup_wib_data()

                # 2. 运行checkout测试
                print("\n[2/5] Running FEMB test...")
                test_result = self._run_femb_test()
                if not test_result:
                    return CheckoutResult(False, "Test execution failed")

                # 3. 传输数据
                print("\n[3/5] Transferring data to PC...")
                data_dirs = self._transfer_data(test_result)
                if not data_dirs:
                    return CheckoutResult(False, "Data transfer failed")

                # 4. 验证结果
                print("\n[4/5] Validating results...")
                validation = self._validate_checkout(test_result.stdout)

                # 5. 打开报告
                print("\n[5/5] Opening reports...")
                self._open_reports(data_dirs['raw'])

                # 清理WIB端数据
                self._cleanup_wib_data()

                # 根据验证结果处理
                if validation['all_passed']:
                    self._save_logs(data_dirs['raw'])
                    print(f"\n{datetime.now(timezone.utc)}")
                    print(Fore.GREEN + "  ✓ FEMB Checkout SUCCESS!" + Style.RESET_ALL)
                    return CheckoutResult(True, "Checkout completed", data_dirs['raw'])
                else:
                    return self._handle_validation_failure(validation, data_dirs['raw'])

            except Exception as e:
                return CheckoutResult(False, f"Exception: {str(e)}")

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
            print(f"\033[96m Initialization {self.tmp} Temperature Checkout\033[0m")

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

            result = subrun(command, timeout=Config.CHECKOUT_TIMEOUT, user_input=user_input, out=True)  # 显示输出

            if result is None:
                return None

            # 记录日志
            self.logs["QC_TestItemID_000"] = [command, result.stdout]
            self.logs['wib_raw_dir'] = Config.WIB_CHK_DIR
            self.logs['checkout_terminal'] = result.stdout

            # 检查测试结果
            if any(keyword in result.stdout for keyword in ["Pass", "is on", "Turn All FEMB off"]):
                return result
            else:
                print(Fore.RED + "Test execution failed" + Style.RESET_ALL)
                print(result.stdout)
                return None

        def _transfer_data(self, test_result):
            """传输数据到PC"""
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
            if self.is_ln_mode and LN_result:
                self._save_ln_data(report_dir)

            self.logs['pc_raw_dir'] = raw_dir

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
            if hasattr(LN_result, 'stdout'):
                ln_output = LN_result.stdout
            else:
                ln_output = str(LN_result)

            with open(fname, "w", encoding="utf-8") as f:
                f.write(ln_output)

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
                    print(f"\033[33mSLOT#{slot} CHECKOUT FAILED !!!\033[0m")
                    validation['all_passed'] = False
                    validation['failed_slots'].append(slot)

            return validation

        def _open_reports(self, data_dir):
            """打开markdown报告文件"""
            for root, dirs, files in os.walk(data_dir):
                for file in files:
                    if file.endswith('.md') and any(f'N{i}.md' in file for i in range(4)):
                        file_path = os.path.join(root, file).replace('\\', '/')
                        webbrowser.open(f'file://{file_path}')

        def _handle_validation_failure(self, validation, data_dir):
            """处理验证失败的情况"""
            print("\n" + "=" * 60)
            print(Fore.RED + f"Failed slots: {', '.join(validation['failed_slots'])}" + Style.RESET_ALL)
            print("=" * 60)
            print("\nOptions:")
            print("  'c' - Continue anyway (save data)")
            print("  'r' - Retry checkout")
            print("  'e' - Exit and power off")

            while True:
                choice = input(Fore.YELLOW + '>> ' + Style.RESET_ALL).strip().lower()

                if choice == 'c':
                    if confirm_user_action("continue", require_confirm=True):
                        self._save_logs(data_dir)
                        return CheckoutResult(True, "Continued despite failures", data_dir)

                elif choice == 'r':
                    if confirm_user_action("retry"):
                        # 返回特殊消息，告诉 run() 方法直接重试，不要再次询问
                        return CheckoutResult(False, "User requested retry from validation")

                elif choice == 'e':
                    if confirm_user_action("exit"):
                        shutdown_power_supply()
                        sys.exit()
                else:
                    print("Invalid input. Please enter 'c', 'r', or 'e'")

        def _save_logs(self, data_dir):
            """保存日志文件"""
            filename = os.path.join(data_dir, 'logs.txt')
            with open(filename, 'w') as f:
                pprint.pprint(self.logs, stream=f)
            print(f"Logs saved to {filename}")

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
            return None

    # ========== End of 02 FEMB Checkout ==========================

    # ========== begin of 03 QC ==========================
    if QC_TST_EN == 3:
        time.sleep(1)
        t1 = time.time()
        print(datetime.now(timezone.utc), " : Start FEMB QC")
        # 03_1 QC item test
        for testid in tms:
            # t1 = time.time()
            print(datetime.now(timezone.utc), " : New Test Item Starts, please wait...")
            print(tms_items[testid])
            # the & is used to close the client, so that the issue can be avoided
            command = ["ssh", "root@192.168.121.123",
                       "cd BNL_CE_WIB_SW_QC; python3 QC_top.py {} -t {}".format(slot_list, testid)]
            user_input_1 = "{}\n{}\n{}\n{}\n{}".format(input_info['tester'], input_info['env'], input_info['toy_TPC'],
                                                       input_info['comment'], FEMB_list)
            result = subrun(command, timeout=1000, user_input=user_input_1)  # rewrite with Popen later
            time.sleep(0.01)
            if result != None:
                resultstr = result.stdout
                logs["QC_TestItemID_%03d" % testid] = [command, resultstr]
                if "Pass!" in result.stdout:
                    print(datetime.now(timezone.utc), "\033[92m  : Mission SUCCESS!  \033[0m")
                elif "QC Item Begin" in result.stdout:
                    print(datetime.now(timezone.utc), "\033[92m  : FEMB QC Begin!  \033[0m")
                    # continue #in FEMB QC, we want to send the data first
                elif "QC Item Done" in result.stdout:
                    print(datetime.now(timezone.utc), "\033[92m  : SUCCESS & Done!  \033[0m")
                    break
                else:
                    print("FAIL!")
                    print(result.stdout)
                    print("Exit anyway")
                    return None
                    # exit()
            else:
                print("FAIL!")
                # print(result.stdout)
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
            print(datetime.now(timezone.utc), "\033[92m  : SUCCESS!  \033[0m")
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
        subrun(["ssh", "root@192.168.121.123", "poweroff"], check=False, out=False)
        time.sleep(6)
        print("Done! [Check that the current should be less than 1.5 A]")

    # ========== end of 03 QC ==========================

    # if True:
    if QC_TST_EN == 10:
        print("save log info during QC")
        if True:
            logging.basicConfig(filename='QC.log',
                                level=logging.INFO,
                                format='%(asctime)s - %(levelname)s - %(message)s')  # Lingyun Ke set
            logging.info('info: %s', logs)
    QCstatus = "PASS"
    bads = []
    data_path = logs['PC_rawdata_root']
    report_path = logs['PC_rawreport_root']

    return QCstatus, bads, data_path, report_path