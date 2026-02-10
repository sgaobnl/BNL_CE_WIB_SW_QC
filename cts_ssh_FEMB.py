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
import GUI.send_email as send_email_module
import components.assembly_log as log
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Read network path from config
_csv_data = {}
_csv_file = os.path.join(BASE_DIR, 'init_setup.csv')
try:
    with open(_csv_file, mode='r', newline='', encoding='utf-8-sig') as _file:
        _reader = csv.reader(_file)
        for _row in _reader:
            if len(_row) == 2:
                _csv_data[_row[0].strip()] = _row[1].strip()
    _top_path = _csv_data.get('QC_data_root_folder', '')
    _network_path = _csv_data.get('Network_Upload_Path', '')
except Exception:
    _top_path = ''
    _network_path = ''


def sync_to_network(local_dir, dir_type='data'):
    """Copy local directory to network path

    Args:
        local_dir: Local directory path to sync
        dir_type: 'data' or 'report' for logging
    """
    try:
        if not _network_path or _network_path == _top_path:
            return

        if not os.path.exists(local_dir):
            print(f"[SYNC] {dir_type} dir does not exist: {local_dir}")
            return

        # Calculate relative path and network destination
        if local_dir.startswith(_top_path):
            rel_path = os.path.relpath(local_dir, _top_path)
            network_dir = os.path.join(_network_path, rel_path)

            print(f"[SYNC] Copying {dir_type}: {local_dir}")
            print(f"[SYNC]      -> {network_dir}")

            # Create parent directory and copy
            os.makedirs(os.path.dirname(network_dir), exist_ok=True)
            shutil.copytree(local_dir, network_dir, dirs_exist_ok=True)
            print(f"[SYNC] SUCCESS: {dir_type} synced to network")
        else:
            print(f"[SYNC] SKIP: path does not start with top_path")
    except Exception as e:
        print(f"[SYNC] ERROR: Network sync failed: {e}")


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


def cts_ssh_FEMB(root="D:/FEMB_QC/", QC_TST_EN=0, input_info=None, email_info=None):
    # QC_TST_EN = True
    logs = {}  # from collections import defaultdict report_log01 = defaultdict(dict)

    # ============= Common Utility Functions =============
    def power_off_femb_channels():
        """Power off FEMB channels (normal operation)"""
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

    def emergency_shutdown():
        """Emergency shutdown of all power supplies (only for unexpected errors)"""
        print(Fore.RED + '\n!!! EMERGENCY SHUTDOWN - Unexpected Error Detected !!!' + Style.RESET_ALL)
        print('Shutting down ALL power supplies for safety...')
        try:
            # 1. Power off all FEMB channels
            print('  - Powering off FEMB channels...')
            power_off_cmd = [
                "ssh", "root@192.168.121.123",
                "cd BNL_CE_WIB_SW_QC; python3 top_femb_powering.py off off off off"
            ]
            subrun(power_off_cmd, timeout=60, out=False)

            # 2. Power off WIB
            print('  - Powering off WIB...')
            subrun(["ssh", "root@192.168.121.123", "poweroff"], check=False, out=False)
            time.sleep(5)

            # 3. Close Rigol power supply
            print('  - Closing Rigol power supply...')
            rigol.RigolDP800().close()

            print(Fore.GREEN + "Emergency shutdown completed" + Style.RESET_ALL)
        except Exception as e:
            print(Fore.RED + f"Error during emergency shutdown: {e}" + Style.RESET_ALL)

    def confirm_user_action(action_name, require_confirm=False):
        """Confirm user action"""
        if require_confirm:
            confirmation = input(f"Enter 'confirm' to {action_name}: ").strip().lower()
            if confirmation == "confirm":
                return True
            print("Action cancelled")
            return False
        return True

    def prompt_retry_or_exit(error_context="", attempt=1, max_attempts=3):
        """Prompt user to choose retry or exit (always ask even if max attempts exceeded)"""
        print("\n" + "=" * 60)
        if error_context:
            print(Fore.RED + f"Error: {error_context}" + Style.RESET_ALL)

        # If maximum attempts reached or exceeded
        if attempt >= max_attempts:
            print(Fore.RED + f"Maximum attempts ({max_attempts}) reached!" + Style.RESET_ALL)
            print("=" * 60)
        else:
            print(f"Attempt {attempt}/{max_attempts}")
            print("=" * 60)

            # Provide suggestions based on attempt number
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

    # ============= Original Variable Initialization =============
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

    # ========== Begin of 01 FEMB Slot Confirm (Optimized) ==========================

    def check_slot_connection(slot_check_output, slot_num, slot_info):
        """Check power connection status for a single SLOT"""
        slot_msg = f'SLOT#{slot_num} Power Connection Normal'

        if slot_msg in slot_check_output:
            print(f"\033[32m{slot_msg}\033[0m")
            return slot_info, False
        else:
            print(f"\033[33mSLOT#{slot_num} Power Connection LOST Warning !!!\033[0m")
            return ' ', True

    def parse_ln_current_status(ln_output, slot_list):
        """Parse LN power output to check current status for each slot

        Returns:
            dict: {slot_num: {'normal': bool, 'message': str}} for each slot in slot_list
        """
        status = {}
        if ln_output is None:
            return status

        for slot_num in ['0', '1', '2', '3']:
            if slot_num not in slot_list:
                continue

            normal_msg = f'SLOT#{slot_num} Power Connection Normal'
            warning_msg = f'Warning: SLOT#{slot_num} LOSS Power Connection'

            if normal_msg in ln_output:
                status[slot_num] = {'normal': True, 'message': normal_msg}
            elif warning_msg in ln_output:
                status[slot_num] = {'normal': False, 'message': f'SLOT#{slot_num} current abnormal'}
            else:
                # If no message found, assume abnormal
                status[slot_num] = {'normal': False, 'message': f'SLOT#{slot_num} status unknown'}

        return status

    def run_femb_powering(power_en, is_ln_mode=False):
        """Run FEMB power-on sequence"""
        ln_result = None

        if is_ln_mode:
            print("Cold initial (LN mode)")
            ln_command = [
                "ssh", "root@192.168.121.123",
                f"cd BNL_CE_WIB_SW_QC; python3 top_femb_powering_LN.py {power_en}"
            ]
            ln_result = subrun(ln_command, timeout=120, out=True)  # Display output
            time.sleep(2)
            print("FEMB Cold Power On")
            ln_result = ln_result.stdout
        else:
            print("Warm initial")

        # Execute regular power-on
        command = [
            "ssh", "root@192.168.121.123",
            f"cd BNL_CE_WIB_SW_QC; python3 top_femb_powering.py {power_en}"
        ]
        result = subrun(command, timeout=120, out=True)  # Display output

        # Extract stdout for checking
        if hasattr(result, 'stdout'):
            slot_check = result.stdout
            if isinstance(slot_check, bytes):
                slot_check = slot_check.decode('utf-8')
        else:
            slot_check = str(result)

        return slot_check, ln_result

    def check_ln_current_with_retry(power_en, slot_list, max_retries=3):
        """Check LN current with retry for persistent failures

        Args:
            power_en: Power enable string (e.g., 'on off on off')
            slot_list: Current slot list string (e.g., ' 0  1 ')
            max_retries: Number of retries for current check

        Returns:
            tuple: (failed_slots, all_failed)
                - failed_slots: list of slot numbers with persistent current failures
                - all_failed: True if all slots in slot_list failed
        """
        failure_count = {}  # {slot_num: count}

        # Initialize failure count for each slot
        for slot_num in ['0', '1', '2', '3']:
            if slot_num in slot_list:
                failure_count[slot_num] = 0

        for attempt in range(max_retries):
            print(Fore.CYAN + f"\n[LN Current Check - Attempt {attempt + 1}/{max_retries}]" + Style.RESET_ALL)

            # Run LN power command
            ln_command = [
                "ssh", "root@192.168.121.123",
                f"cd BNL_CE_WIB_SW_QC; python3 top_femb_powering_LN.py {power_en}"
            ]
            ln_result = subrun(ln_command, timeout=60, out=True)
            time.sleep(2)

            ln_output = ln_result.stdout if ln_result else ""

            # Parse current status
            current_status = parse_ln_current_status(ln_output, slot_list)

            # Update failure counts
            for slot_num, status in current_status.items():
                if not status['normal']:
                    failure_count[slot_num] += 1
                    print(Fore.YELLOW + f"  ⚠️  {status['message']} (failure {failure_count[slot_num]}/{max_retries})" + Style.RESET_ALL)
                else:
                    print(Fore.GREEN + f"  ✓ SLOT#{slot_num} current normal" + Style.RESET_ALL)

            # Check if any slot recovered (reset its count)
            for slot_num in failure_count.keys():
                if slot_num in current_status and current_status[slot_num]['normal']:
                    failure_count[slot_num] = 0

            # Early exit if all slots are normal
            all_normal = all(count == 0 for count in failure_count.values())
            if all_normal:
                print(Fore.GREEN + "  ✓ All FEMB currents normal" + Style.RESET_ALL)
                return [], False

            if attempt < max_retries - 1:
                print(Fore.YELLOW + "  Waiting 3 seconds before retry..." + Style.RESET_ALL)
                time.sleep(3)

        # Determine which slots have persistent failures
        failed_slots = [slot for slot, count in failure_count.items() if count >= max_retries]
        active_slots = [slot for slot in failure_count.keys() if slot not in failed_slots]
        all_failed = len(active_slots) == 0

        return failed_slots, all_failed

    def run_cable_test(slot_list, is_cold=False):
        """Run cable test slot by slot with retry logic.

        Tests each slot individually with up to 3 attempts each.
        At warm: sends email after 3 failures per slot, returns failure.
        At cold: sends email, removes failed slot from test list.
          - 1 slot fails: remove and continue with remaining slots.
          - 2+ slots fail: skip checkout and QC entirely.

        Returns:
            tuple: (passed_slots, failed_slots, combined_output)
        """
        MAX_CABLE_RETRIES = 3
        slots = slot_list.strip().split()
        passed_slots = []
        failed_slots = []
        combined_output = ""

        for slot in slots:
            slot_passed = False
            for cable_attempt in range(1, MAX_CABLE_RETRIES + 1):
                print(f"\n[Cable Test] Slot {slot} - Attempt {cable_attempt}/{MAX_CABLE_RETRIES}")
                time.sleep(1)
                command = [
                    "ssh", "root@192.168.121.123",
                    f"cd BNL_CE_WIB_SW_QC; python3 top_chkout_pls_fake_timing.py {slot} save 5"
                ]
                result = subrun(command, timeout=60, out=True)

                output = ""
                if result is not None and hasattr(result, 'stdout'):
                    output = result.stdout
                    if isinstance(output, bytes):
                        output = output.decode('utf-8')
                combined_output += output

                if "Cable Test Done" in output:
                    print(Fore.GREEN + f"Slot {slot} Continuity Test PASSED" + Style.RESET_ALL)
                    slot_passed = True
                    break
                else:
                    print(Fore.RED + f"Slot {slot} Cable Test FAILED (Attempt {cable_attempt}/{MAX_CABLE_RETRIES})" + Style.RESET_ALL)
                    print(f"Output: {output}")
                    if cable_attempt < MAX_CABLE_RETRIES:
                        print(Fore.YELLOW + f"Retrying slot {slot}..." + Style.RESET_ALL)

            if slot_passed:
                passed_slots.append(slot)
            else:
                failed_slots.append(slot)
                # Send email notification for this slot failure
                if email_info:
                    try:
                        test_site = logs.get('CTS_IDs', 'Unknown')
                        mode_str = "Cold" if is_cold else "Warm"
                        subject = f"{mode_str} Cable Test Failed - Slot {slot} - CTS {test_site}"
                        body = (
                            f"{mode_str} Cable Test: Slot {slot} failed after {MAX_CABLE_RETRIES} attempts.\n"
                            f"Test Site: CTS {test_site}\n\n"
                            f"Please check data cable connection for Slot {slot}.\n\n"
                            f"Script: {os.path.basename(__file__)} (called by CTS_FEMB_QC_top.py)"
                        )
                        if is_cold:
                            body += f"\nSlot {slot} has been removed from the test list."
                        send_email_module.send_email(
                            email_info['sender'], email_info['password'], email_info['receiver'],
                            subject, body
                        )
                    except Exception as e:
                        print(f"Failed to send cable test email notification: {e}")

        return passed_slots, failed_slots, combined_output

    # Main flow: QC_TST_EN == 1
    # LN_result = ""
    MAX_RETRIES = 3

    if QC_TST_EN == 1:
        try:
            is_ln_mode = 'LN' in tmp

            slot_mapping = {
                '0': ('SLOT0', 'slot0'),
                '1': ('SLOT1', 'slot1'),
                '2': ('SLOT2', 'slot2'),
                '3': ('SLOT3', 'slot3')
            }

            # Track slots with critical current failures (for skipping in checkout/QC)
            critical_failed_slots = []

            # ========== LN Mode: Pre-check current with retry ==========
            if is_ln_mode:
                print(Fore.CYAN + "\n" + "=" * 70)
                print("  LN MODE: FEMB CURRENT PRE-CHECK")
                print("=" * 70 + Style.RESET_ALL)
                print(Fore.YELLOW + "  Checking FEMB current status with retry..." + Style.RESET_ALL)

                failed_slots, all_failed = check_ln_current_with_retry(power_en, slot_list, max_retries=3)

                if all_failed:
                    # All FEMBs have persistent current failures - skip entire test
                    print(Fore.RED + "\n" + "=" * 70)
                    print("  ⛔ CRITICAL WARNING: ALL FEMBs HAVE PERSISTENT CURRENT FAILURES")
                    print("=" * 70 + Style.RESET_ALL)
                    print(Fore.RED + "  All FEMBs show abnormal current after 3 retries." + Style.RESET_ALL)
                    print(Fore.RED + "  Skipping Checkout and QC tests for this session." + Style.RESET_ALL)
                    print(Fore.YELLOW + "\n  Please check:" + Style.RESET_ALL)
                    print("    1. FEMB power connections")
                    print("    2. Cable connections")
                    print("    3. FEMB hardware status")

                    # Power off all FEMBs
                    power_off_femb_channels()

                    # Record critical failure
                    logs['critical_current_failure'] = True
                    logs['failed_slots'] = list(failed_slots)

                    # Return special tuple indicating critical failure (compatible with QC_Process)
                    # Format: (QCstatus, bads, data_path, report_path)
                    return ("CRITICAL_CURRENT_FAILURE", list(failed_slots), None, None)

                elif failed_slots:
                    # Some FEMBs have persistent current failures - remove from slot_list
                    print(Fore.RED + "\n" + "-" * 70)
                    print("  ⚠️  CRITICAL WARNING: PERSISTENT CURRENT FAILURES DETECTED")
                    print("-" * 70 + Style.RESET_ALL)

                    for slot in failed_slots:
                        slot_name = f"SLOT#{slot}"
                        femb_id = input_info.get(f'SLOT{slot}', 'Unknown')
                        print(Fore.RED + f"  ⛔ {slot_name} ({femb_id}): Persistent current failure - SKIPPING" + Style.RESET_ALL)
                        critical_failed_slots.append(slot)

                    # Update slot_list and power_en to remove failed slots
                    original_slot_list = slot_list
                    slot_list_new = ''
                    power_en_new = ''
                    power_parts = power_en.strip().split()

                    for i, slot_num in enumerate(['0', '1', '2', '3']):
                        if slot_num in original_slot_list and slot_num not in failed_slots:
                            slot_list_new += f' {slot_num} '
                            power_en_new += ' on '
                        else:
                            power_en_new += ' off '

                    slot_list = slot_list_new
                    power_en = power_en_new

                    print(Fore.YELLOW + f"\n  Updated slot list: [{slot_list.strip()}]" + Style.RESET_ALL)
                    print(Fore.YELLOW + f"  Updated power config: [{power_en.strip()}]" + Style.RESET_ALL)

                    # Record critical failures
                    logs['critical_current_failure'] = True
                    logs['failed_slots'] = list(failed_slots)

                    # Check if any slots remain
                    if not slot_list.strip():
                        print(Fore.RED + "\n  ⛔ No valid FEMBs remaining. Skipping tests." + Style.RESET_ALL)
                        power_off_femb_channels()
                        return ("CRITICAL_CURRENT_FAILURE", list(failed_slots), None, None)

                else:
                    print(Fore.GREEN + "\n  ✓ All FEMB currents normal - proceeding with tests" + Style.RESET_ALL)

                print()

            attempt = 0
            while True:  # Infinite loop, user decides when to exit
                attempt += 1

                print(f"\n{datetime.now(timezone.utc)}")
                print(Fore.MAGENTA + f"SLOT Confirmation - Attempt {attempt}" + Style.RESET_ALL)
                print("=" * 60)

                # ========== Step 1: FEMB Power-On and SLOT Check ==========
                print("\n[1/3] FEMB Power-On and SLOT Check...")
                SlotCheck, ln_res = run_femb_powering(power_en, is_ln_mode)
                log.tmp_log00["LN_result"] = ln_res

                # Check SLOT connections
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

                # SLOT connection check failed
                if Slot_change:
                    print(Fore.RED + "\nSLOT connection check FAILED" + Style.RESET_ALL)
                    print("Please check SLOT connections and femb_info.csv")

                    # Only power off FEMB channels (do not power off Rigol and WIB)
                    power_off_femb_channels()

                    # Ask user (ask even if max attempts exceeded)
                    choice = prompt_retry_or_exit("SLOT connection error", attempt, MAX_RETRIES)

                    if choice == 'retry':
                        continue
                    elif choice == 'exit':
                        # User chose to exit, only power off FEMB
                        power_off_femb_channels()
                        print(Fore.YELLOW + "User exited. FEMB powered off." + Style.RESET_ALL)
                        return None

                # ========== Step 2: Cable Test (slot by slot) ==========
                print("\n[2/3] Continuity Test...")
                passed_slots, cable_failed_slots, cable_output = run_cable_test(
                    slot_list, is_cold=is_ln_mode
                )

                if cable_failed_slots:
                    if not is_ln_mode:
                        # Warm mode: any cable failure is blocking
                        print(Fore.RED + "\nContinuity test FAILED for slot(s): " +
                              ", ".join(cable_failed_slots) + Style.RESET_ALL)

                        # Only power off FEMB channels (do not power off Rigol and WIB)
                        power_off_femb_channels()

                        # Ask user (ask even if max attempts exceeded)
                        choice = prompt_retry_or_exit("Cable connection error", attempt, MAX_RETRIES)

                        if choice == 'retry':
                            continue
                        elif choice == 'exit':
                            # User chose to exit, only power off FEMB
                            power_off_femb_channels()
                            print(Fore.YELLOW + "User exited. FEMB powered off." + Style.RESET_ALL)
                            return None
                    else:
                        # Cold mode: handle based on number of failures
                        if len(cable_failed_slots) >= 2:
                            # Two or more slots failed - skip checkout and QC
                            print(Fore.RED + "\n" + "=" * 70)
                            print("  CABLE TEST: 2+ SLOTS FAILED - SKIPPING CHECKOUT AND QC")
                            print("=" * 70 + Style.RESET_ALL)
                            for s in cable_failed_slots:
                                print(Fore.RED + f"  Slot {s}: Cable test failed after 3 attempts" + Style.RESET_ALL)
                            power_off_femb_channels()
                            logs['cable_test_failure'] = True
                            logs['cable_failed_slots'] = cable_failed_slots
                            return ("CABLE_TEST_FAILURE", cable_failed_slots, None, None)
                        else:
                            # One slot failed - remove from list and continue
                            failed_slot = cable_failed_slots[0]
                            print(Fore.YELLOW + f"\nCold mode: Removing failed slot {failed_slot} from test list" + Style.RESET_ALL)
                            # Update input_info so subsequent QC_TST_EN calls exclude this slot
                            input_info[f'SLOT{failed_slot}'] = ' '

                            # Rebuild slot_list and power_en for current session
                            slot_list_new = ''
                            power_en_new = ''
                            for sn in ['0', '1', '2', '3']:
                                if input_info.get(f'SLOT{sn}', ' ') != ' ':
                                    slot_list_new += f' {sn} '
                                    power_en_new += ' on '
                                else:
                                    power_en_new += ' off '
                            slot_list = slot_list_new
                            power_en = power_en_new

                            print(Fore.YELLOW + f"Updated slot list: [{slot_list.strip()}]" + Style.RESET_ALL)
                            print(Fore.YELLOW + f"Updated power config: [{power_en.strip()}]" + Style.RESET_ALL)

                            if not slot_list.strip():
                                print(Fore.RED + "No valid slots remaining." + Style.RESET_ALL)
                                power_off_femb_channels()
                                return ("CABLE_TEST_FAILURE", cable_failed_slots, None, None)

                            logs['cable_test_failure'] = True
                            logs['cable_failed_slots'] = cable_failed_slots

                # ========== Step 3: Power off FEMB ==========
                print("\n[3/3] Powering off all FEMBs...")
                command = [
                    "ssh", "root@192.168.121.123",
                    "cd BNL_CE_WIB_SW_QC; python3 top_femb_powering.py off off off off"
                ]
                subrun(command, timeout=120, out=False)

                # ========== SUCCESS ==========
                print(f"\n{datetime.now(timezone.utc)}")
                print(Fore.GREEN + "  SLOT Confirmation SUCCESS!" + Style.RESET_ALL)

                logs['WIB_start_up'] = cable_output

                break  # Success, exit loop

        except KeyboardInterrupt:
            # User pressed Ctrl+C, only power off FEMB
            print(Fore.YELLOW + "\n\nKeyboard Interrupt detected." + Style.RESET_ALL)
            power_off_femb_channels()
            raise
        except Exception as e:
            # Unexpected error, emergency shutdown of all power supplies
            print(Fore.RED + f"\n\nUnexpected error: {e}" + Style.RESET_ALL)
            emergency_shutdown()
            raise

    # ========== End of 01 FEMB Slot Confirm ==========================

    # ========== Begin of 02 FEMB Checkout (Optimized) ==========================
    # Configuration constants
    class Config:
        WIB_HOST = "root@192.168.121.123"
        WIB_CHK_DIR = "/home/root/BNL_CE_WIB_SW_QC/CHK/"
        WIB_REPORT_DIR = "/home/root/BNL_CE_WIB_SW_QC/CHK/Report/"
        WIB_LNP_DIR = "/home/root/BNL_CE_WIB_SW_QC/tmp_ln/"
        CHECKOUT_TIMEOUT = 200
        SCP_TIMEOUT = 10
        MAX_RETRIES = 3
        VALID_SLOTS = ['0', '1', '2', '3']

    class CheckoutResult:
        """Encapsulate checkout result"""

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
            """Main execution flow (with infinite retry mechanism, decided by user)"""
            attempt = 0

            while True:  # Infinite loop, user decides when to exit
                attempt += 1

                print(f"\n{datetime.now(timezone.utc)}")
                print(Fore.MAGENTA + f"FEMB Checkout - Attempt {attempt}" + Style.RESET_ALL)
                print("=" * 60)

                result = self._execute_checkout()

                if result.success:
                    return result

                # Special case: user chose to retry after validation failure, no need to ask again
                if result.message == "User requested retry from validation":
                    continue

                # Handle failure
                print(Fore.RED + f"\nCheckout FAILED: {result.message}" + Style.RESET_ALL)

                # Special handling: LN mode first failure auto-retry
                if self.is_ln_mode and attempt == 1:
                    print(Fore.YELLOW + "LN mode: Automatic retry (1st attempt)" + Style.RESET_ALL)
                    continue

                # Ask user (ask even if max attempts exceeded)
                choice = prompt_retry_or_exit(result.message, attempt, Config.MAX_RETRIES)

                if choice == 'retry':
                    continue
                elif choice == 'exit':
                    # User chose to exit, only power off FEMB
                    power_off_femb_channels()
                    print(Fore.YELLOW + "User exited. FEMB powered off." + Style.RESET_ALL)
                    return CheckoutResult(False, "User cancelled")

        def _execute_checkout(self):
            """Execute a complete checkout process"""
            try:
                # 1. Clean WIB data
                print("\n[1/5] Cleaning WIB data...")
                self._cleanup_wib_data()

                # 2. Run checkout test
                print("\n[2/5] Running FEMB test...")
                test_result = self._run_femb_test()
                if not test_result:
                    return CheckoutResult(False, "Test execution failed")

                # 3. Transfer data
                print("\n[3/5] Transferring data to PC...")
                data_dirs = self._transfer_data(test_result)
                if not data_dirs:
                    return CheckoutResult(False, "Data transfer failed")

                # 4. Validate results
                print("\n[4/5] Validating results...")
                validation = self._validate_checkout(test_result.stdout)

                # 5. Open reports
                # print("\n[5/5] Opening reports...")
                # self._open_reports(data_dirs['raw'])

                # Clean WIB data
                self._cleanup_wib_data()

                # Handle based on validation results
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
            """Clean WIB data directory"""
            command = [
                "ssh", "-o", "BatchMode=yes", Config.WIB_HOST,
                f"rm -rf {Config.WIB_CHK_DIR}"
            ]
            try:
                subprocess.run(command, timeout=Config.SCP_TIMEOUT, capture_output=True)
            except subprocess.TimeoutExpired:
                print('Cleanup timeout, continuing...')

        def _run_femb_test(self):
            """Run FEMB test"""
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

            result = subrun(command, timeout=Config.CHECKOUT_TIMEOUT, user_input=user_input, out=True)  # Display output

            if result is None:
                return None

            # Record logs
            self.logs["QC_TestItemID_000"] = [command, result.stdout]
            self.logs['wib_raw_dir'] = Config.WIB_CHK_DIR
            self.logs['checkout_terminal'] = result.stdout

            # Check test results
            if any(keyword in result.stdout for keyword in ["Pass", "is on", "Turn All FEMB off"]):
                return result
            else:
                print(Fore.RED + "Test execution failed" + Style.RESET_ALL)
                print(result.stdout)
                return None

        def _transfer_data(self, test_result):
            """Transfer data to PC and sync to network path"""
            # Create target directories
            time_prefix = self.current_time.strftime("%Y_%m/%d_%H_%M_%S")
            base_name = f"Time_{time_prefix}_CTS_{self.logs['CTS_IDs']}{self.savename}"

            raw_dir = os.path.join(self.root, "Data", f"{base_name}_CHK/")
            report_dir = os.path.join(self.root, "Report", f"{base_name}_CHK/")

            # Store the actual data directories (not parent directories)
            self.logs['PC_rawdata_root'] = raw_dir
            self.logs['PC_rawreport_root'] = report_dir

            # Create directories
            for directory in [raw_dir, report_dir]:
                try:
                    os.makedirs(directory, exist_ok=True)
                except OSError as e:
                    print(f"Error creating folder {directory}: {e}")
                    return None

            # SCP transfer
            wib_src = f"{Config.WIB_HOST}:{Config.WIB_CHK_DIR}"
            wib_report_src = f"{Config.WIB_HOST}:{Config.WIB_REPORT_DIR}"
            wib_ln_power = f"{Config.WIB_HOST}:{Config.WIB_LNP_DIR}"

            # Transfer reports
            self._scp_transfer(wib_report_src, report_dir)

            # Transfer raw data
            if not self._scp_transfer(wib_src, raw_dir):
                return None
            # If LN test, save additional data
            if self.is_ln_mode:
                self._scp_transfer(wib_ln_power, report_dir)

            self.logs['pc_raw_dir'] = raw_dir

            # Sync to network disk
            print("\n[SYNC] Syncing to network disk...")
            sync_to_network(raw_dir, 'raw data')
            sync_to_network(report_dir, 'report')

            return {'raw': raw_dir, 'report': report_dir}

        def _scp_transfer(self, src, dst):
            """Execute SCP transfer"""
            command = [f"scp -r {src} {dst}"]
            result = subrun(command, timeout=Config.SCP_TIMEOUT, check=False, out=False)
            time.sleep(0.01)
            return result is not None

        # def _save_ln_data(self, report_dir):
        #     """Save LN test data"""
        #     fname = os.path.join(report_dir, "LN_first_power_output.txt")
        #     ln_output = str(log.tmp_log00["LN_result"] )
        #     with open(fname, "w", encoding="utf-8") as f:
        #         f.write(ln_output)

        def _validate_checkout(self, stdout):
            """Validate checkout results for each slot"""
            validation = {'all_passed': True, 'failed_slots': []}

            for slot in Config.VALID_SLOTS:
                if slot not in self.slot_list:
                    continue

                expected_msg = f'Slot {slot} PASS\t ALL ASSEMBLY CHECKOUT'
                if expected_msg in stdout:
                    print(f"\033[32mSLOT#{slot} CHECKOUT Normal\033[0m")
                    log.ck_log00[slot] = "pass"
                else:
                    print(f"\033[33mSLOT#{slot} CHECKOUT FAILED !!!\033[0m")
                    log.ck_log00[slot] = "fail"
                    validation['all_passed'] = False
                    validation['failed_slots'].append(slot)

            return validation

        def _open_reports(self, data_dir):
            """Open markdown report files"""
            for root, dirs, files in os.walk(data_dir):
                for file in files:
                    if file.endswith('.md') and any(f'N{i}.md' in file for i in range(4)):
                        file_path = os.path.join(root, file).replace('\\', '/')
                        webbrowser.open(f'file://{file_path}')

        def _handle_validation_failure(self, validation, data_dir):
            """Handle validation failure"""
            print("\n" + "=" * 60)
            print(Fore.RED + f"Failed slots: {', '.join(validation['failed_slots'])}" + Style.RESET_ALL)
            print("=" * 60)
            print("\nOptions:")
            print("  'c' - Continue anyway (save data)")
            print("  'r' - Retry checkout")
            print("  'e' - Exit and power off")

            while True:
                choice = 'c'
                # choice = input(Fore.YELLOW + '>> ' + Style.RESET_ALL).strip().lower()

                if choice == 'c':
                    # if confirm_user_action("continue", require_confirm=True):
                    #     self._save_logs(data_dir)
                    return CheckoutResult(True, "Continued despite failures", data_dir)

                elif choice == 'r':
                    if confirm_user_action("retry"):
                        # Return special message to tell run() method to retry directly without asking again
                        return CheckoutResult(False, "User requested retry from validation")

                elif choice == 'e':
                    if confirm_user_action("exit"):
                        # User chose to exit, only power off FEMB
                        power_off_femb_channels()
                        print(Fore.YELLOW + "User exited. FEMB powered off." + Style.RESET_ALL)
                        sys.exit()
                else:
                    print("Invalid input. Please enter 'c', 'r', or 'e'")

        def _save_logs(self, data_dir):
            """Save log files"""
            filename = os.path.join(data_dir, 'logs.txt')
            with open(filename, 'w') as f:
                pprint.pprint(self.logs, stream=f)
            print(f"Logs saved to {filename}")

    # Usage
    if QC_TST_EN == 2:
        try:
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

        except KeyboardInterrupt:
            # User pressed Ctrl+C, only power off FEMB
            print(Fore.YELLOW + "\n\nKeyboard Interrupt detected." + Style.RESET_ALL)
            power_off_femb_channels()
            raise
        except Exception as e:
            # Unexpected error, emergency shutdown of all power supplies
            print(Fore.RED + f"\n\nUnexpected error: {e}" + Style.RESET_ALL)
            emergency_shutdown()
            raise

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
                    print(datetime.now(timezone.utc), "\033[92m  : FEMB QC  \033[0m")
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

            # Build actual QC data directory paths
            base_path_data = root + "Data/" + "Time_{}_CTS_{}{}".format(
                current_time.strftime("%Y_%m/%d_%H_%M_%S"), logs['CTS_IDs'], savename)
            base_path_report = root + "Report/" + "Time_{}_CTS_{}{}".format(
                current_time.strftime("%Y_%m/%d_%H_%M_%S"), logs['CTS_IDs'], savename)

            # Set to actual QC directories (with _QC suffix)
            fddir = base_path_data + '_QC/'
            freport_dir = base_path_report + '_QC/'

            logs['PC_rawdata_root'] = fddir
            logs['PC_rawreport_root'] = freport_dir
            # fddir = logs['PC_rawdata_root'] + fsubdirs[-1] + "/"
            # print(fddir)

            # Create both data and report directories
            for directory in [fddir, freport_dir]:
                if not os.path.exists(directory):
                    try:
                        os.makedirs(directory)
                    except OSError:
                        print(f"Error to create folder {directory}")
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

            # Network sync is handled by CTS_Real_Time_Monitor.py

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
        # time.sleep(500)
        t2 = time.time()
        time.sleep(200)
        print('QC time consumption is: {}'.format(t2 - t1))


    # Usage
    if QC_TST_EN == 5:
        try:
            checkout = FEMBCheckout(
                slot_list=slot_list,
                tmp=tmp,
                input_info=input_info,
                logs=logs,
                root=root,
                savename="{}".format(savename),
                # savename="{}_last".format(savename),
                current_time=current_time
            )

            result = checkout.run()

            if not result.success:
                print(f"Checkout failed: {result.message}")
                return None

        except KeyboardInterrupt:
            # User pressed Ctrl+C, only power off FEMB
            print(Fore.YELLOW + "\n\nKeyboard Interrupt detected." + Style.RESET_ALL)
            power_off_femb_channels()
            raise
        except Exception as e:
            # Unexpected error, emergency shutdown of all power supplies
            print(Fore.RED + f"\n\nUnexpected error: {e}" + Style.RESET_ALL)
            emergency_shutdown()
            raise

    if QC_TST_EN == 6:
        print("Power Off the Linux on WIB PS [6 second]")
        subrun(["ssh", "root@192.168.121.123", "poweroff"], check=False, out=False)
        time.sleep(6)
        print("Done! [Check that the current should be less than 1.5 A]")

    # ========== End of 03 QC ==========================

    # if True:
    if QC_TST_EN == 10:
        print("save log info during QC")
        if True:
            logging.basicConfig(filename='QC.log',
                                level=logging.INFO,
                                format='%(asctime)s - %(levelname)s - %(message)s')  # Lingyun Ke set
            logging.info('info: %s', logs)

    # Network sync is handled by CTS_Real_Time_Monitor.py

    QCstatus = "PASS"
    bads = []
    data_path = logs['PC_rawdata_root']
    report_path = logs['PC_rawreport_root']

    return QCstatus, bads, data_path, report_path