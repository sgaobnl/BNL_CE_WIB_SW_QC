# ============================================================================
# CTS FEMB QC Top Level Script
# Cold Electronics Quality Control System for DUNE
# ============================================================================

# ----------------------------------------------------------------------------
# Module Imports
# ----------------------------------------------------------------------------
# 1. Module Imports - System and third-party libraries
import cts_ssh_FEMB as cts
import cts_cryo_uart
import csv
import colorama
from colorama import Fore, Style
import GUI.pop_window as pop
import GUI.State_List as state
import GUI.Rigol_DP800 as rigol
import GUI.send_email as send_email
from datetime import datetime
import os
import time
import sys
import threading

# Import QC modules - Custom utility modules
from qc_utils import timer_count, countdown_timer, check_fault_files, QC_Process, close_terminal, check_checkout_result
from qc_power import safe_power_off
from qc_ui import confirm, get_email, get_cebox_image
from qc_results import handle_qc_results, display_qc_results, analyze_test_results

# ----------------------------------------------------------------------------
# UI Helper Functions
# ----------------------------------------------------------------------------
def print_phase_header(phase_num, total_phases, title, estimated_time=None):
    """Print a standardized phase header with progress tracking"""
    print("\n" + Fore.CYAN + "=" * 70)
    progress = f"[Phase {phase_num}/{total_phases}]"
    time_str = f" (Est. {estimated_time})" if estimated_time else ""
    print(f"  {progress} {title.upper()}{time_str}")
    print("=" * 70 + Style.RESET_ALL + "\n")

def print_step(step_desc, step_num=None, total_steps=None, estimated_time=None):
    """Print a standardized step with optional numbering and time estimate"""
    step_prefix = ""
    if step_num and total_steps:
        step_prefix = f"[{step_num}/{total_steps}] "
    time_str = f" (est. {estimated_time})" if estimated_time else ""
    print(Fore.CYAN + f"▶ {step_prefix}{step_desc}{time_str}" + Style.RESET_ALL)

def print_status(status_type, message):
    """Print a standardized status message
    status_type: 'success', 'error', 'warning', 'info'
    """
    icons = {
        'success': ('✓', Fore.GREEN),
        'error': ('✗', Fore.RED),
        'warning': ('⚠', Fore.YELLOW),
        'info': ('ℹ', Fore.CYAN)
    }
    icon, color = icons.get(status_type, ('•', Fore.WHITE))
    print(color + f"{icon} {message}" + Style.RESET_ALL)

def print_separator(char="-", length=70):
    """Print a separator line"""
    print(Fore.CYAN + char * length + Style.RESET_ALL)

def print_progress_bar(current, total, prefix="Progress", length=40):
    """Print a progress bar"""
    percent = int((current / total) * 100)
    filled = int((current / total) * length)
    bar = "█" * filled + "░" * (length - filled)
    print(f"\r{Fore.CYAN}{prefix}: [{bar}] {percent}%{Style.RESET_ALL}", end="")
    if current == total:
        print()  # New line when complete

def background_timer_reminder(wait_seconds, task_name, ready_message):
    """
    Background timer that prints reminders and alerts when ready.
    Runs in a separate thread so main script can continue.

    Args:
        wait_seconds: Number of seconds to wait
        task_name: Name of the task (e.g., "CTS Warm Gas")
        ready_message: Message to display when ready
    """
    def timer_thread():
        # Print initial message
        print(Fore.YELLOW + f"\n⏰ {task_name} timer started: {wait_seconds//60} minutes" + Style.RESET_ALL)
        print(Fore.CYAN + f"   You can continue with other tasks. Will remind you when ready." + Style.RESET_ALL)

        # Calculate reminder intervals (e.g., halfway point)
        halfway = wait_seconds // 2

        # Wait for halfway point
        if wait_seconds >= 120:  # Only remind if wait is >= 2 minutes
            time.sleep(halfway)
            remaining = wait_seconds - halfway
            print(Fore.YELLOW + f"\n⏰ {task_name}: {remaining//60} minutes remaining..." + Style.RESET_ALL)
            time.sleep(remaining)
        else:
            time.sleep(wait_seconds)

        # Alert when ready
        print("\n" + Fore.GREEN + "=" * 70)
        print(f"  ✓ {ready_message}")
        print("=" * 70 + Style.RESET_ALL)

        # Audible alert (optional - beep)
        try:
            print('\a')  # System beep
        except:
            pass

    # Start timer in background thread
    timer = threading.Thread(target=timer_thread, daemon=True)
    timer.start()
    return timer

# def upload_to_network(qc_data_root, csv_file, csv_file_implement, network_path, femb_ids=None):
#     """
#     Upload all test data and reports to network drive.
#     Copies data structure directly to network path without creating additional subfolders.
#
#     Args:
#         qc_data_root: Root folder containing FEMB_QC test data (e.g., /mnt/data)
#         csv_file: Path to femb_info.csv
#         csv_file_implement: Path to femb_info_implement.csv
#         network_path: Network drive upload path (e.g., /data/rtss/femb)
#         femb_ids: List of FEMB IDs being tested (for logging only)
#
#     Returns:
#         bool: True if upload successful, False otherwise
#     """
#     import shutil
#     from datetime import datetime
#
#     try:
#         print("\n" + Fore.CYAN + "=" * 70)
#         print("  UPLOADING TEST DATA TO NETWORK DRIVE")
#         print("=" * 70 + Style.RESET_ALL)
#
#         # Check if network path exists
#         if not os.path.exists(network_path):
#             print_status('warning', f"Network path does not exist: {network_path}")
#             print(Fore.YELLOW + "Attempting to create directory..." + Style.RESET_ALL)
#             try:
#                 os.makedirs(network_path, exist_ok=True)
#                 print_status('success', "Network directory created")
#             except Exception as e:
#                 print_status('error', f"Failed to create network directory: {e}")
#                 return False
#
#         print(Fore.CYAN + f"Source: {qc_data_root}" + Style.RESET_ALL)
#         print(Fore.CYAN + f"Destination: {network_path}" + Style.RESET_ALL)
#
#         files_copied = 0
#         total_size = 0
#
#         # 1. Copy FEMB_QC data folder
#         femb_qc_source = os.path.join(qc_data_root, "FEMB_QC")
#         femb_qc_dest = os.path.join(network_path, "FEMB_QC")
#
#         if os.path.exists(femb_qc_source) and os.path.isdir(femb_qc_source):
#             print_status('info', f"Copying FEMB_QC data...")
#
#             # Copy the entire FEMB_QC directory tree
#             shutil.copytree(femb_qc_source, femb_qc_dest, dirs_exist_ok=True)
#
#             # Count files and calculate size
#             for root, dirs, files in os.walk(femb_qc_dest):
#                 files_copied += len(files)
#                 for file in files:
#                     total_size += os.path.getsize(os.path.join(root, file))
#
#             print_status('success', f"Copied FEMB_QC ({files_copied} files)")
#         else:
#             print_status('warning', f"FEMB_QC folder not found: {femb_qc_source}")
#
#         # 2. Copy CSV files to network path root
#         csv_files_to_copy = [
#             (csv_file, "femb_info.csv"),
#             (csv_file_implement, "femb_info_implement.csv")
#         ]
#
#         for src_file, dest_name in csv_files_to_copy:
#             if os.path.exists(src_file):
#                 dest_file = os.path.join(network_path, dest_name)
#                 shutil.copy2(src_file, dest_file)
#                 files_copied += 1
#                 total_size += os.path.getsize(dest_file)
#                 print_status('success', f"Copied {dest_name}")
#             else:
#                 print_status('warning', f"File not found: {src_file}")
#
#         # Final summary
#         print(Fore.CYAN + "\n" + "=" * 70)
#         print("  UPLOAD COMPLETE")
#         print("=" * 70 + Style.RESET_ALL)
#         print(Fore.GREEN + f"  ✓ Files uploaded: {files_copied}" + Style.RESET_ALL)
#         print(Fore.GREEN + f"  ✓ Total size: {total_size / (1024*1024):.2f} MB" + Style.RESET_ALL)
#         print(Fore.GREEN + f"  ✓ Location: {network_path}" + Style.RESET_ALL)
#         print(Fore.CYAN + "=" * 70 + Style.RESET_ALL + "\n")
#
#         return True
#
#     except Exception as e:
#         print_status('error', f"Upload failed: {e}")
#         print(Fore.RED + f"Error details: {str(e)}" + Style.RESET_ALL)
#         return False

def parse_assembly_data_from_comment(comment_str):
    """
    Parse assembly data from csv_data['comment'] string.

    Format: "Bottom_HWDB=A123,Bottom_CE=ZZZ1234,Bottom_Cover=1234,Bottom_FEMB=...,Top_HWDB=...,..."

    Args:
        comment_str: CSV-style comment string from assembly

    Returns:
        dict: {
            'bottom': {'hwdb_qr': str, 'ce_box_sn': str, 'cover_last4': str, 'femb_sn': str},
            'top': {'hwdb_qr': str, 'ce_box_sn': str, 'cover_last4': str, 'femb_sn': str}
        }
    """
    result = {
        'bottom': {'hwdb_qr': '', 'ce_box_sn': '', 'cover_last4': '', 'femb_sn': ''},
        'top': {'hwdb_qr': '', 'ce_box_sn': '', 'cover_last4': '', 'femb_sn': ''}
    }

    # Parse CSV-style string
    parts = comment_str.split(',')
    data_dict = {}
    for part in parts:
        if '=' in part:
            key, value = part.split('=', 1)
            data_dict[key.strip()] = value.strip()

    # Extract bottom slot data
    result['bottom']['hwdb_qr'] = data_dict.get('Bottom_HWDB', '')
    result['bottom']['ce_box_sn'] = data_dict.get('Bottom_CE', '')
    result['bottom']['cover_last4'] = data_dict.get('Bottom_Cover', '')
    result['bottom']['femb_sn'] = data_dict.get('Bottom_FEMB', '')

    # Extract top slot data
    result['top']['hwdb_qr'] = data_dict.get('Top_HWDB', '')
    result['top']['ce_box_sn'] = data_dict.get('Top_CE', '')
    result['top']['cover_last4'] = data_dict.get('Top_Cover', '')
    result['top']['femb_sn'] = data_dict.get('Top_FEMB', '')

    return result

def generate_qc_summary(test_phase, inform, qc_result, output_file):
    """
    Generate QC test summary and save to file

    Args:
        test_phase: "Warm QC", "Cold QC", or "Final Checkout"
        inform: FEMB information dictionary
        qc_result: QCResult object from analyze_test_results
        output_file: Path to save summary text file

    Returns:
        str: Path to generated summary file
    """
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            # Header
            f.write("=" * 70 + "\n")
            f.write(f"  {test_phase.upper()} - TEST SUMMARY\n")
            f.write("=" * 70 + "\n\n")

            # Test site and timestamp
            f.write(f"Test Site: {inform.get('test_site', 'N/A')}\n")
            f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            # Summary statistics
            f.write(f"Summary Statistics:\n")
            f.write(f"  Total Fault Files: {qc_result.total_faults}\n")
            f.write(f"  Total Pass Files:  {qc_result.total_passes}\n\n")

            # Slot-by-slot results
            f.write(f"FEMB Status by Slot:\n")
            f.write("-" * 70 + "\n")
            all_passed = True
            failed_slots = []

            for slot_num in sorted(qc_result.slot_status.keys()):
                passed, femb_id = qc_result.slot_status[slot_num]
                slot_position = "Bottom" if slot_num == '0' else "Top" if slot_num == '1' else f"Slot{slot_num}"

                # Get slot-specific file counts
                slot_faults = qc_result.slot_files.get(slot_num, {}).get('faults', [])
                slot_passes = qc_result.slot_files.get(slot_num, {}).get('passes', [])
                fault_count = len(slot_faults)
                pass_count = len(slot_passes)

                status_text = "PASS" if passed else "FAIL"
                f.write(f"  {slot_position} Slot{slot_num}: FEMB {femb_id} - {status_text}\n")
                f.write(f"    Files: {fault_count} faults, {pass_count} passes\n")

                if not passed:
                    all_passed = False
                    failed_slots.append((slot_num, femb_id))

                # List fault files for this slot
                if slot_faults:
                    f.write(f"    Fault files:\n")
                    for fault_file in slot_faults:
                        f.write(f"      - {os.path.basename(fault_file)}\n")

                f.write("\n")

            # Overall result
            f.write("=" * 70 + "\n")
            if all_passed:
                f.write("  OVERALL RESULT: PASS\n")
            else:
                f.write("  OVERALL RESULT: FAIL\n")
                f.write("\n  Failed FEMBs:\n")
                for slot_num, femb_id in failed_slots:
                    slot_name = "Bottom" if slot_num == '0' else "Top" if slot_num == '1' else f"Slot{slot_num}"
                    f.write(f"    - {slot_name} Slot{slot_num}: {femb_id}\n")
            f.write("=" * 70 + "\n")

        print(Fore.GREEN + f"✓ Summary saved to: {output_file}" + Style.RESET_ALL)
        return output_file
    except Exception as e:
        print(Fore.RED + f"✗ Failed to generate summary: {e}" + Style.RESET_ALL)
        return None

def validate_disassembly_for_slot(slot_name, assembly_data, test_passed):
    """
    Guide user through disassembly validation for one CE box slot.
    Ensures CE box is returned to correct foam box with correct cover.

    Args:
        slot_name: "bottom" or "top"
        assembly_data: dict from parse_assembly_data_from_comment for this slot
        test_passed: Boolean indicating if QC test passed

    Returns:
        None
    """
    # Check if slot was empty during assembly
    if assembly_data['ce_box_sn'] == 'EMPTY':
        print_status('info', f"{slot_name.upper()} slot was EMPTY - skipping disassembly validation")
        return

    print_separator()
    print(Fore.CYAN + f"📦 Disassembly & Packaging for {slot_name.upper()} Slot" + Style.RESET_ALL)
    print_separator()

    # Retrieve original assembly data
    orig_hwdb = assembly_data['hwdb_qr']
    orig_ce_box = assembly_data['ce_box_sn']
    orig_cover = assembly_data['cover_last4']
    femb_sn = assembly_data['femb_sn']

    # Display summary of what needs to be done
    print(Fore.YELLOW + f"\n📋 {slot_name.upper()} Slot Components:" + Style.RESET_ALL)
    print(Fore.CYAN + f"   • FEMB ID:        {femb_sn}" + Style.RESET_ALL)
    print(Fore.CYAN + f"   • CE Box SN:      {orig_ce_box}" + Style.RESET_ALL)
    print(Fore.CYAN + f"   • Cover (last 4): {orig_cover}" + Style.RESET_ALL)
    print(Fore.CYAN + f"   • Foam Box QR:    {orig_hwdb}" + Style.RESET_ALL)
    print()

    # Step 1: Scan CE box QR code
    while True:
        print(Fore.YELLOW + f"\n✓ Step 1: Scan CE box QR code for {slot_name.upper()} slot" + Style.RESET_ALL)
        ce_box_scanned = input(Fore.YELLOW + '         Scan or type CE box SN: ' + Style.RESET_ALL).strip()

        if ce_box_scanned == orig_ce_box:
            print_status('success', f"         ✓ CE box SN matches: {ce_box_scanned}")
            break
        else:
            print_status('error', f"         ✗ Mismatch! Expected: {orig_ce_box}, Got: {ce_box_scanned}")
            print(Fore.RED + "         Please scan the correct CE box or check assembly records." + Style.RESET_ALL)

    # Step 2: Cover installation validation
    print(Fore.CYAN + f"\n✓ Step 2: Install cover to CE box" + Style.RESET_ALL)
    print(Fore.GREEN + "=" * 70 + Style.RESET_ALL)
    print(Fore.GREEN + f"         >>> Please install COVER (last 4: {orig_cover}) <<<" + Style.RESET_ALL)
    print(Fore.GREEN + f"         >>> To CE BOX SN: {orig_ce_box} <<<" + Style.RESET_ALL)
    print(Fore.GREEN + "=" * 70 + Style.RESET_ALL)

    while True:
        cover_input = input(Fore.YELLOW + '         After cover is installed, type cover last 4 digits: ' + Style.RESET_ALL).strip()

        if cover_input == orig_cover:
            print_status('success', f"         ✓ Cover SN matches: {cover_input}")
            break
        else:
            print_status('error', f"         ✗ Mismatch! Expected: {orig_cover}, Got: {cover_input}")
            print(Fore.RED + "         Please re-check the cover SN." + Style.RESET_ALL)

    # Step 3: Foam box packaging validation
    print(Fore.CYAN + f"\n✓ Step 3: Package CE box into foam box" + Style.RESET_ALL)
    print(Fore.GREEN + "=" * 70 + Style.RESET_ALL)
    print(Fore.GREEN + f"         >>> Please package CE BOX ({orig_ce_box}) <<<" + Style.RESET_ALL)
    print(Fore.GREEN + f"         >>> Into FOAM BOX QR: {orig_hwdb} <<<" + Style.RESET_ALL)
    print(Fore.GREEN + "=" * 70 + Style.RESET_ALL)

    while True:
        foam_box_scanned = input(Fore.YELLOW + '         Scan QR code on the foam box: ' + Style.RESET_ALL).strip()

        if foam_box_scanned == orig_hwdb:
            print_status('success', f"         ✓ Foam box matches: {foam_box_scanned}")
            break
        else:
            print_status('error', f"         ✗ Mismatch! Expected: {orig_hwdb}, Got: {foam_box_scanned}")
            print(Fore.RED + "         Please use the correct foam box that originally contained this CE box." + Style.RESET_ALL)

    # Step 4: QC result sticker instruction
    print(Fore.CYAN + f"\n✓ Step 4: Apply QC result sticker" + Style.RESET_ALL)
    print(Fore.CYAN + f"         FEMB ID: {femb_sn}" + Style.RESET_ALL)
    if test_passed:
        print(Fore.GREEN + "         >>> Put on Green 'PASS' sticker near HWDB QR sticker <<<" + Style.RESET_ALL)
    else:
        print(Fore.RED + "         >>> Put on Red 'NG' sticker near HWDB QR sticker <<<" + Style.RESET_ALL)

    # Step 5: Storage instruction
    print(Fore.YELLOW + "\n         Store the foam box in the designated location." + Style.RESET_ALL)

    print_status('success', f"         {slot_name.upper()} slot CE box disassembly validation complete!")
    print_separator()

def collect_assembly_data(slot_name):
    """
    Collect pre-assembly data for a CE box slot.
    Returns dict with HWDB QR, CE box SN, cover last 4 digits.
    Validates that cover SN matches CE box SN.

    Args:
        slot_name: String like "BOTTOM" or "TOP" for display purposes

    Returns:
        dict: {'hwdb_qr': str, 'ce_box_sn': str, 'cover_last4': str}
    """
    print_separator()
    print(Fore.CYAN + f"Pre-Assembly Data Collection for {slot_name} Slot" + Style.RESET_ALL)
    print_separator()

    # Step 1: Scan HWDB QR code on foam box
    while True:
        print(Fore.CYAN + "         Step: Scan HWDB QR code on foam box" + Style.RESET_ALL)
        hwdb_qr = input(Fore.YELLOW + '         Scan or type HWDB QR code: ' + Style.RESET_ALL).strip()

        if hwdb_qr:
            print_status('success', f"         HWDB QR recorded: {hwdb_qr}")
            break
        else:
            print_status('error', "         HWDB QR code cannot be empty. Please try again.")

    # Step 2: Scan/Type CE box QR code
    while True:
        print(Fore.CYAN + "         Step: Scan CE box QR code" + Style.RESET_ALL)
        ce_box_sn = input(Fore.YELLOW + '         Scan CE box QR code or type SN: ' + Style.RESET_ALL).strip()

        if ce_box_sn:
            print_status('success', f"         CE box SN recorded: {ce_box_sn}")
            break
        else:
            print_status('error', "         CE box SN cannot be empty. Please try again.")

    # Step 3: Type last 4 digits on CE box cover with validation
    while True:
        print(Fore.CYAN + "         Step: Type last 4 digits on CE box cover" + Style.RESET_ALL)
        cover_last4 = input(Fore.YELLOW + '         Type last 4 digits: ' + Style.RESET_ALL).strip()

        if not cover_last4:
            print_status('error', "         Cover digits cannot be empty. Please try again.")
            continue

        # Validation: Check if KKKK matches last 4 of ZZZXXXX
        if len(ce_box_sn) >= 4:
            expected_last4 = ce_box_sn[-4:]
            if cover_last4 == expected_last4:
                print_status('success', f"         ✓ Cover SN ({cover_last4}) matches CE box SN")
                break
            else:
                print_status('error', f"         ✗ Mismatch: Cover shows '{cover_last4}' but CE box ends with '{expected_last4}'")
                print(Fore.RED + "         Please re-enter the correct last 4 digits from the CE box cover." + Style.RESET_ALL)
        else:
            print_status('warning', "         CE box SN too short to validate, but recording anyway.")
            break

    print_separator()
    return {
        'hwdb_qr': hwdb_qr,
        'ce_box_sn': ce_box_sn,
        'cover_last4': cover_last4
    }

# ----------------------------------------------------------------------------
# Global Configuration
# ----------------------------------------------------------------------------
# 2. Global Configuration Settings
print(Fore.YELLOW + "⚠ WARNING: Do not open the CTS during LN₂ filling." + Style.RESET_ALL)
print(Fore.YELLOW + "⚠ WARNING: Do not touch LN₂. Risk of serious injury." + Style.RESET_ALL)

script = "CTS_Real_Time_Monitor.py"
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

## Email configuration for notifications
sender = "bnlr216@gmail.com"
password = "vvef tosp minf wwhf"
receiver = "lke@bnl.gov"

## Data path configuration for test results
# wc = Warm Checkout, wq = Warm QC
# lc = Cold Checkout (LN2), lq = Cold QC (LN2)
# fc = Final Checkout
wcdata_path = r"D:\data\temp"
wcreport_path = r"D:\data\temp"
wqdata_path = r"D:\data\temp"
wqreport_path = r"D:\data\temp"
lcdata_path = r"D:\data\temp"
lcreport_path = r"D:\data\temp"
lqdata_path = r"D:\data\temp"
lqreport_path = r"D:\data\temp"
fcdata_path = r"D:\data\temp"
fcreport_path = r"D:\data\temp"

colorama.init()

# ----------------------------------------------------------------------------
# Initialization Stage (Lines 44-143)
# ----------------------------------------------------------------------------
print(ROOT_DIR)
## 3. CSV File Path Configuration
technician_csv = os.path.join(ROOT_DIR, "init_setup.csv")
csv_file = os.path.join(ROOT_DIR, "femb_info.csv")
csv_file_implement = os.path.join(ROOT_DIR, "femb_info_implement.csv")

## FEMB version (HD = Horizontal Drift, VD = Vertical Drift)
version = "HD"

## 3. CSV File Initialization - Create if not exists
if not os.path.exists(technician_csv):
    with open(technician_csv, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['TechnicianID', 'Lingyun Ke'])
        writer.writerow(['test_site', 'BNL'])
        writer.writerow(['QC_data_root_folder', '/home/dune/'])
        writer.writerow(['Email', 'LKE@BNL.GOV'])
    print(Fore.GREEN + f"✓ Created and initialized: {technician_csv}" + Style.RESET_ALL)

### Create femb_info.csv if not exists
if not os.path.exists(csv_file):
    open(csv_file, 'w').close()
    print(Fore.GREEN + f"✓ Created: {csv_file}" + Style.RESET_ALL)

### Create femb_info_implement.csv if not exists
if not os.path.exists(csv_file_implement):
    open(csv_file_implement, 'w').close()
    print(Fore.GREEN + f"✓ Created: {csv_file_implement}" + Style.RESET_ALL)

## 4. Welcome Interface
print('\n')
print(Fore.CYAN + "=" * 70)
print("  WELCOME TO CTS COLD ELECTRONICS QC SYSTEM")
print("  Brookhaven National Laboratory (BNL)")
print("=" * 70 + Style.RESET_ALL)

### Get tester name input
input_name = input('Please enter your name:\n' + Fore.YELLOW + '>> ' + Style.RESET_ALL)


## 5. Launch Real-Time Monitoring Script
### Kill old monitoring process if running
os.system(f'pkill -f "{script}"')
time.sleep(1)

### Launch monitoring script in minimal-size terminal
current_dir = os.path.dirname(os.path.abspath(__file__))
# Launch very small terminal window in bottom-right corner
# geometry: 15 columns x 5 rows, positioned at bottom-right
os.system(f'gnome-terminal --title="CTS Monitor" --hide-menubar --geometry=15x5-0-0 --working-directory="{current_dir}" -- bash -c "python3 {script}; exec bash" &')
print(f"✓ Analysis Code Launched" + Fore.GREEN + "(A terminal for real time analysis is launched, please minimize it.)" + Style.RESET_ALL)

## 6. Pre-Test Preparation
### 6.1 Email Validation - Get and confirm user email
receiver = get_email()

### 6.2 Display Checklist Popups
#### Pop window 1: Initial Checkout List
pop.show_image_popup(
    title="Initial Discharge Human Body",
    image_path=os.path.join(ROOT_DIR, "GUI", "output_pngs", "2.png")
)

#### Pop window 2: Accessory tray #1
pop.show_image_popup(
    title="Initial Check",
    image_path=os.path.join(ROOT_DIR, "GUI", "output_pngs", "3.png")
)

#### Pop window 2: Accessory tray #1
pop.show_image_popup(
    title="Checklist for accessory tray #1",
    image_path=os.path.join(ROOT_DIR, "GUI", "output_pngs", "4.png")
)

#### Pop window 3: Accessory tray #2
pop.show_image_popup(
    title="Checklist for accessory tray #2",
    image_path=os.path.join(ROOT_DIR, "GUI", "output_pngs", "5.png")
)

#### Pop window 3: Accessory tray #2
pop.show_image_popup(
    title="CTS Initial Checkout",
    image_path=os.path.join(ROOT_DIR, "GUI", "output_pngs", "6.png")
)

# ----------------------------------------------------------------------------
# CTS Cryogenic System Initialization
# ----------------------------------------------------------------------------
## Load CTS configuration from init_setup.csv
cts_config = {}
try:
    with open(technician_csv, mode='r', newline='', encoding='utf-8-sig') as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) == 2:
                key, value = row
                cts_config[key.strip()] = value.strip()
except Exception as e:
    print(Fore.YELLOW + f"⚠ Warning: Could not load CTS configuration: {e}" + Style.RESET_ALL)

## Get CTS wait times from config (in seconds)
try:
    cts_ln2_fill_wait = int(cts_config.get('CTS_LN2_Fill_Wait', 1800))  # Default 30 min
    cts_warmup_wait = int(cts_config.get('CTS_Warmup_Wait', 3600))     # Default 60 min
except ValueError:
    cts_ln2_fill_wait = 1800
    cts_warmup_wait = 3600
    print(Fore.YELLOW + "⚠ Invalid CTS wait time values in config, using defaults" + Style.RESET_ALL)

## Initialize CTS cryogenic control box
print(Fore.CYAN + "\n" + "=" * 70)
print("  CTS CRYOGENIC SYSTEM INITIALIZATION")
print("=" * 70 + Style.RESET_ALL)
print(Fore.CYAN + f"Configuration:" + Style.RESET_ALL)
print(f"  LN₂ Fill Wait Time: {cts_ln2_fill_wait//60} minutes")
print(f"  Warm-up Wait Time: {cts_warmup_wait//60} minutes")
print()

cryo = cts_cryo_uart.cryobox()
cryo_initialized = cryo.cts_init_setup()

if cryo_initialized:
    print_status('success', "CTS cryogenic box connected via USB - automatic control enabled")
    cryo_auto_mode = True
else:
    if cryo.manual_flg:
        print_status('warning', "CTS cryogenic box not found - manual control mode")
        print(Fore.YELLOW + "  You will be prompted to control the cryogenic system manually" + Style.RESET_ALL)
        cryo_auto_mode = False
    else:
        print_status('error', "CTS initialization failed")
        cryo_auto_mode = False

print(Fore.CYAN + "=" * 70 + Style.RESET_ALL + "\n")

### 7. LN2 Dewar Level Check and Refill
print(Fore.CYAN + "\n" + "=" * 70)
print("  LN₂ DEWAR LEVEL CHECK")
print("=" * 70 + Style.RESET_ALL)

# Determine shift and set dewar level threshold
hour = datetime.now().hour
if 1 <= hour <= 11:
    DEWAR_LEVEL_THRESHOLD = 1700
    shift_name = "Morning"
else:
    DEWAR_LEVEL_THRESHOLD = 1200
    shift_name = "Afternoon"

print(Fore.CYAN + f"Current Shift: {shift_name}" + Style.RESET_ALL)
print(Fore.CYAN + f"Required Dewar Level: >= {DEWAR_LEVEL_THRESHOLD}" + Style.RESET_ALL)

# Initialize CTS ready time (will be set if warm gas is started)
cts_ready_time = None

if cryo_auto_mode:
    # Automatic mode - check dewar level via CTS with verification loop
    refill_needed = True
    refill_performed = False  # Track if refill actually happened

    while refill_needed:
        print_status('info', "Checking dewar level via CTS...")
        tc_level, dewar_level = cryo.cts_status()

        print(Fore.CYAN + f"Current Dewar Level: {dewar_level}" + Style.RESET_ALL)

        if dewar_level < DEWAR_LEVEL_THRESHOLD:
            print_status('warning', f"Dewar level ({dewar_level}) is below {shift_name} threshold ({DEWAR_LEVEL_THRESHOLD})")
            print(Fore.YELLOW + "⚠️  Dewar refill required!" + Style.RESET_ALL)

            # Show refill instructions popup
            pop.show_image_popup(
                title="Test Dewar Refill",
                image_path=os.path.join(ROOT_DIR, "GUI", "output_pngs", "8.png")
            )

            # Wait for refill confirmation or skip
            while True:
                print(Fore.CYAN + "\nHas the 50L dewar been refilled?" + Style.RESET_ALL)
                print("Enter " + Fore.GREEN + "'Y'" + Style.RESET_ALL + " (Yes) - Refill completed, verify level")
                print("Enter " + Fore.YELLOW + "'J'" + Style.RESET_ALL + " (Jump) - Skip refill and continue anyway")
                result = input(Fore.YELLOW + '>> ' + Style.RESET_ALL)
                if result.upper() == 'Y':
                    print(Fore.GREEN + "✓ Dewar refill confirmed." + Style.RESET_ALL)
                    refill_performed = True
                    break
                elif result.upper() == 'J':
                    print(Fore.YELLOW + "⏩ Skipping LN₂ refill..." + Style.RESET_ALL)
                    refill_performed = False
                    print_status('warning', f"Dewar level ({dewar_level}) bypass - continuing without refill")
                    refill_needed = False  # Exit outer loop
                    break
                else:
                    print_status('error', "Invalid input. Please enter 'Y' or 'J'")

            # Only verify if user said they refilled (not if they chose to skip)
            if refill_performed and refill_needed:
                print_status('info', "Verifying dewar level after refill...")
                tc_level, dewar_level = cryo.cts_status()
                print(Fore.CYAN + f"Verified Dewar Level: {dewar_level}" + Style.RESET_ALL)

                if dewar_level < DEWAR_LEVEL_THRESHOLD:
                    print_status('error', f"Dewar level ({dewar_level}) is still below threshold ({DEWAR_LEVEL_THRESHOLD})")
                    print(Fore.RED + "⚠️  Refill was insufficient." + Style.RESET_ALL)
                    while True:
                        print(Fore.CYAN + "\nWhat would you like to do?" + Style.RESET_ALL)
                        print("Enter " + Fore.YELLOW + "'J'" + Style.RESET_ALL + " (Jump) - Skip and continue anyway")
                        print("Enter " + Fore.GREEN + "'R'" + Style.RESET_ALL + " (Retry) - Refill again")
                        result = input(Fore.YELLOW + '>> ' + Style.RESET_ALL)
                        if result.upper() == 'J':
                            print_status('warning', f"Dewar level ({dewar_level}) bypass - continuing without sufficient level")
                            refill_needed = False  # Exit loop
                            break
                        elif result.upper() == 'R':
                            # Loop continues - will show popup and ask for refill again
                            break
                        else:
                            print_status('error', "Invalid input. Please enter 'J' or 'R'")
                else:
                    print_status('success', f"Dewar level ({dewar_level}) is now sufficient!")
                    refill_needed = False  # Exit loop
        else:
            print_status('success', f"Dewar level ({dewar_level}) is sufficient for {shift_name} shift (>= {DEWAR_LEVEL_THRESHOLD})")
            refill_needed = False  # Exit loop

    # If refill was performed, start automatic warm gas purge in background (20 minutes)
    if refill_performed:
        print_status('info', "Starting automatic warm gas purge (20 minutes)...")
        cts_ready_time = cryo.cryo_warmgas_start(waitminutes=20)
        if cts_ready_time:
            print_status('success', "Warm gas purge started in background")
            # Start background timer to remind when CTS is ready
            background_timer_reminder(
                wait_seconds=20*60,
                task_name="CTS Warm Gas Purge",
                ready_message="CTS WARM GAS PURGE COMPLETE - CTS is ready for testing!"
            )
            print(Fore.GREEN + "\n✓ You can now proceed with CE assembly (Phase 1)" + Style.RESET_ALL)
            print(Fore.CYAN + "  The system will remind you when CTS is ready.\n" + Style.RESET_ALL)
        else:
            print_status('error', "Warm gas purge failed to start")
            cts_ready_time = None

else:
    # Manual mode - prompt user to check dewar level with verification loop
    print_status('warning', "Manual mode - please check dewar level manually")

    refill_performed = False
    level_sufficient = False

    while not level_sufficient:
        while True:
            print(Fore.CYAN + "\nPlease check the dewar level manually." + Style.RESET_ALL)
            print(Fore.CYAN + f"Required minimum level for {shift_name} shift: {DEWAR_LEVEL_THRESHOLD}" + Style.RESET_ALL)
            print("Is the dewar level sufficient for testing?")
            print("Enter " + Fore.GREEN + "'Y'" + Style.RESET_ALL + " (Yes) or " + Fore.RED + "'N'" + Style.RESET_ALL + " (No, needs refill)")
            result = input(Fore.YELLOW + '>> ' + Style.RESET_ALL)

            if result.upper() in ['Y', 'N']:
                break
            else:
                print_status('error', "Invalid input. Please enter 'Y' or 'N'")

        if result.upper() == 'N':
            # Show refill popup
            pop.show_image_popup(
                title="Test Dewar Refill",
                image_path=os.path.join(ROOT_DIR, "GUI", "output_pngs", "8.png")
            )

            # Wait for refill
            while True:
                print(Fore.CYAN + "\nHas the 50L dewar been refilled?" + Style.RESET_ALL)
                print("Enter " + Fore.GREEN + "'Y'" + Style.RESET_ALL + " (Yes) when refill is complete")
                refill_result = input(Fore.YELLOW + '>> ' + Style.RESET_ALL)
                if refill_result.upper() == 'Y':
                    print(Fore.GREEN + "✓ Dewar refill confirmed." + Style.RESET_ALL)
                    refill_performed = True
                    break

            # Verify dewar level after refill
            while True:
                print_status('info', "Please verify the dewar level after refill")
                print(Fore.CYAN + f"Required minimum level: {DEWAR_LEVEL_THRESHOLD}" + Style.RESET_ALL)
                print("Is the dewar level now sufficient?")
                print("Enter " + Fore.GREEN + "'Y'" + Style.RESET_ALL + " (Yes) or " + Fore.RED + "'N'" + Style.RESET_ALL + " (No, still insufficient)")
                verify_result = input(Fore.YELLOW + '>> ' + Style.RESET_ALL)

                if verify_result.upper() in ['Y', 'N']:
                    break
                else:
                    print_status('error', "Invalid input. Please enter 'Y' or 'N'")

            if verify_result.upper() == 'Y':
                print_status('success', "Dewar level verified sufficient")
                level_sufficient = True  # Exit loop
            else:
                print_status('error', "Dewar level still insufficient")
                print(Fore.RED + "⚠️  Please refill again." + Style.RESET_ALL)
                # Loop continues - will ask for refill again

        elif result.upper() == 'Y':
            print(Fore.GREEN + "✓ Dewar level confirmed sufficient." + Style.RESET_ALL)
            level_sufficient = True  # Exit loop

    # If refill was performed, start manual warm gas purge (20 minutes)
    if refill_performed:
        # Manual warm gas instructions
        print("\n" + Fore.YELLOW + "=" * 70)
        print("  MANUAL WARM GAS PURGE REQUIRED (20 minutes)")
        print("=" * 70 + Style.RESET_ALL)
        print(Fore.CYAN + "Instructions:" + Style.RESET_ALL)
        print("  1. Set CTS to " + Fore.CYAN + "STATE 2 (Warm Gas)" + Style.RESET_ALL)
        print("  2. Wait for 20-minute countdown (you can skip with 'j')")
        print("  3. After countdown, set CTS back to " + Fore.CYAN + "STATE 1 (IDLE)" + Style.RESET_ALL)

        # Ask for confirmation that warm gas mode is set
        while True:
            print(Fore.YELLOW + "\nHave you set CTS to STATE 2 (Warm Gas)?" + Style.RESET_ALL)
            print("Enter " + Fore.GREEN + "'Y'" + Style.RESET_ALL + " when ready")
            confirm_warmgas = input(Fore.YELLOW + '>> ' + Style.RESET_ALL)
            if confirm_warmgas.upper() == 'Y':
                print_status('success', "Warm gas mode confirmed")
                break
            else:
                print_status('error', "Invalid input. Please enter 'Y'")

        # Display countdown timer (can be skipped with 'j')
        completed = countdown_timer(
            total_seconds=20*60,
            message="CTS Warm Gas Purge (20 min)",
            allow_skip=True
        )

        print(Fore.GREEN + "\n✓ Warm gas purge time elapsed" + Style.RESET_ALL)
        print(Fore.YELLOW + "⚠️  Please set CTS to STATE 1 (IDLE)" + Style.RESET_ALL)

        # Confirm IDLE state set
        while True:
            print("Enter " + Fore.GREEN + "'Y'" + Style.RESET_ALL + " when CTS is set to IDLE")
            idle_confirm = input(Fore.YELLOW + '>> ' + Style.RESET_ALL)
            if idle_confirm.upper() == 'Y':
                print_status('success', "CTS warm gas purge completed")
                break

print(Fore.CYAN + "=" * 70 + Style.RESET_ALL + "\n")

## 8. Test Phase Selection - User selects which phases to execute (1-6)
state_list = state.select_test_states()
print(Fore.CYAN + f"Selected test phases: {state_list}" + Style.RESET_ALL)

# Initialize checkout failure flag for cross-phase communication
# Set to True if warm checkout fails and user chooses to skip to disassembly
goto_disassembly = False

# ============================================================================
## PHASE 1: PREPARATION
# ============================================================================
if 1 in state_list:
    print_phase_header(1, 6, "FEMB Installation & Setup")

    # ------------------------------------------------------------------------
    ### 9-13. Bottom Slot FEMB Installation
    # ------------------------------------------------------------------------
    while True:
        print_step("Assemble CE box in BOTTOM SLOT (Cable #1)", 1, 2)
        print_status('info', "Visual inspection popup opening...")

        #### 9. Display bottom slot visual inspection popup
        my_options = ["Install MiniSAS Cable and Clamp", "Install Test Cover", "Install Power Cable",
                      "Install Toy_TPCs and Cables", "Insert into Bottom Slot"]
        pop01 = pop.show_image_popup(
            title="Bottom slot Visual Inspection",
            image_path=os.path.join(ROOT_DIR, "GUI", "output_pngs", "9.png")
        )

        #### 9a. Check if slot is empty first
        slot_status = None
        while True:
            print(Fore.CYAN + "         Will this slot have a FEMB installed?" + Style.RESET_ALL)
            print(Fore.YELLOW + "         (Enter 'Y' for Yes, 'EMPTY' or 'N' if this slot will be empty)" + Style.RESET_ALL)
            slot_input = input(Fore.YELLOW + '         >> ' + Style.RESET_ALL).strip().upper()

            if slot_input in ['Y', 'YES', 'EMPTY', 'NONE', 'N', 'NO', 'N/A', 'NA', '空', '']:
                slot_status = slot_input
                break
            else:
                print_status('error', "         Invalid input. Please enter 'Y', 'EMPTY', or 'N'")

        if slot_status in ['EMPTY', 'NONE', 'N', 'NO', 'N/A', 'NA', '空', '']:
            # Slot is empty - skip assembly data collection
            femb_id_0 = 'EMPTY'
            bottom_assembly_data = {
                'hwdb_qr': 'EMPTY',
                'ce_box_sn': 'EMPTY',
                'cover_last4': 'EMPTY'
            }
            print_status('warning', "         Bottom slot marked as EMPTY (no FEMB installed)")
        else:
            # Slot will have a FEMB - collect assembly data
            #### 9b. Pre-Assembly Data Collection (HWDB, CE box, Cover SN)
            bottom_assembly_data = collect_assembly_data("BOTTOM")

            #### 10. QR Code Scanning & Validation (Triple verification)
            ##### First scan
            femb_id_0 = None  # Initialize
            while True:
                print(Fore.CYAN + "         [1/2] Scan the FEMB QR code (1st scan)" + Style.RESET_ALL)
                femb_id_00 = input(Fore.YELLOW + '         >> ' + Style.RESET_ALL).strip()

                ##### Validate: Must contain IO-1826-1 (HD) or IO-1865-1 (VD)
                if ("-1826-1" in femb_id_00) or ("-1865-1" in femb_id_00):
                    break
                else:
                    print_status('error', "         No valid FEMB ID detected. Please try again.")

            ##### Second scan
            while True:
                print(Fore.CYAN + "         [2/2] Scan the FEMB QR code (2nd scan)" + Style.RESET_ALL)
                femb_id_01 = input(Fore.YELLOW + '         >> ' + Style.RESET_ALL).strip()

                if ("-1826-1" in femb_id_01) or ("-1865-1" in femb_id_01):
                    break
                else:
                    print_status('error', "         No valid FEMB ID detected. Please try again.")

            ##### Match check - If scans match, proceed; else require 3rd scan
            if femb_id_01 == femb_id_00:
                print_status('success', "         Bottom CE box QR ID recorded successfully")
                femb_id_0 = femb_id_01
            else:
                ##### Third scan verification (if first two don't match)
                print_status('warning', '         QR codes do not match! Please scan a 3rd time and verify carefully.')
                while True:
                    while True:
                        print("         Scan bottom FEMB QR code " + Fore.CYAN + "(3rd attempt - try 1):" + Style.RESET_ALL)
                        femb_id_2 = input(Fore.YELLOW + '         >> ' + Style.RESET_ALL).strip()
                        if ("-1826-1" in femb_id_2) or ("-1865-1" in femb_id_2):
                            break
                        else:
                            print(Fore.RED + "         ✗ No valid FEMB ID detected. Please try again." + Style.RESET_ALL)

                    while True:
                        print("         Scan bottom FEMB QR code " + Fore.CYAN + "(3rd attempt - try 2):" + Style.RESET_ALL)
                        femb_id_3 = input(Fore.YELLOW + '         >> ' + Style.RESET_ALL).strip()
                        if ("-1826-1" in femb_id_3) or ("-1865-1" in femb_id_3):
                            break
                        else:
                            print(Fore.RED + "         ✗ No valid FEMB ID detected. Please try again." + Style.RESET_ALL)

                    if femb_id_2 == femb_id_3:
                        print(Fore.GREEN + "         ✓ QR codes match. Proceeding..." + Style.RESET_ALL)
                        femb_id_0 = femb_id_2
                        break
                    else:
                        print(
                            Fore.RED + "         ✗ QR codes still do not match. Please scan again carefully." + Style.RESET_ALL)

        #### 11. Version Identification based on ID
        if femb_id_0 != 'EMPTY':
            femb_id_0 = femb_id_0.replace('/', '_')
            if "1826" in femb_id_0:
                version = "HD"  # Horizontal Drift
            else:
                version = "VD"  # Vertical Drift
        else:
            # Keep previous version or set default
            if 'version' not in locals():
                version = "VD"  # Default to VD if no previous version set

        #### 12. Serial Number Final Confirmation
        while True:
            print(Fore.RED + f"         Step 1.13: Confirm bottom FEMB SN is {femb_id_0}" + Style.RESET_ALL)
            print(
                "         Enter " + Fore.GREEN + "'y'" + Style.RESET_ALL + " to confirm, " + Fore.RED + "'n'" + Style.RESET_ALL + " to re-scan")
            user_input = input(Fore.YELLOW + '         >> ' + Style.RESET_ALL)
            if user_input.lower() == 'y':
                print(Fore.GREEN + "         ✓ Bottom slot confirmed." + Style.RESET_ALL)
                exit_outer = True
                break
            elif user_input.lower() == 'n':
                print(Fore.YELLOW + "         Restarting ID scanning..." + Style.RESET_ALL)
                exit_outer = False
                break
            else:
                print_status('error', "         Invalid input. Please enter 'y' or 'n'")

        if 'exit_outer' in locals() and exit_outer:
            break

    #### 13. Bottom Slot Assembly Guidance
    print(Fore.CYAN + "         Step 1.14: Continue assembly into bottom slot..." + Style.RESET_ALL)
    print("         Assembly instruction popup opening...")

    my_options = ["Install MiniSAS Cable and Clamp", "Install Test Cover", "Install Power Cable",
                  "Install Toy_TPCs and Cables", "Insert into Bottom Slot"]
    ##### Display assembly instructions based on version
    if version == "VD":
        pop01 = pop.show_image_popup(
            title="Bottom slot assembly instruction",
            image_path=os.path.join(ROOT_DIR, "GUI", "output_pngs", "10.png")
        )
    else:  # HD version
        pop01 = pop.show_image_popup(
            title="Bottom slot assembly instruction",
            image_path=os.path.join(ROOT_DIR, "GUI", "output_pngs", "12.png")
        )
    ##### Confirm installation complete
    confirm("Please Confirm the CE is install in the Bottom Slot")

    # ------------------------------------------------------------------------
    ### 14. Top Slot FEMB Installation (Repeat steps 9-13 for top slot)
    # ------------------------------------------------------------------------
    while True:
        print(
            Fore.CYAN + "Step 1.2: Assemble CE box in the " + Fore.YELLOW + "TOP SLOT" + Fore.CYAN + " (Cable #2)" + Style.RESET_ALL)
        print("         Visual inspection popup opening...")

        my_options = ["Install MiniSAS Cable and Clamp", "Install Test Cover", "Install Power Cable",
                      "Install Toy_TPCs and Cables", "Insert into Top Slot"]
        pop01 = pop.show_image_popup(
            title="Top slot Visual Inspection",
            image_path=os.path.join(ROOT_DIR, "GUI", "output_pngs", "9.png")
        )

        #### 14a. Check if slot is empty first
        slot_status = None
        while True:
            print(Fore.CYAN + "         Will this slot have a FEMB installed?" + Style.RESET_ALL)
            print(Fore.YELLOW + "         (Enter 'Y' for Yes, 'EMPTY' or 'N' if this slot will be empty)" + Style.RESET_ALL)
            slot_input = input(Fore.YELLOW + '         >> ' + Style.RESET_ALL).strip().upper()

            if slot_input in ['Y', 'YES', 'EMPTY', 'NONE', 'N', 'NO', 'N/A', 'NA', '空', '']:
                slot_status = slot_input
                break
            else:
                print_status('error', "         Invalid input. Please enter 'Y', 'EMPTY', or 'N'")

        if slot_status in ['EMPTY', 'NONE', 'N', 'NO', 'N/A', 'NA', '空', '']:
            # Slot is empty - skip assembly data collection
            femb_id_1 = 'EMPTY'
            top_assembly_data = {
                'hwdb_qr': 'EMPTY',
                'ce_box_sn': 'EMPTY',
                'cover_last4': 'EMPTY'
            }
            print_status('warning', "         Top slot marked as EMPTY (no FEMB installed)")
        else:
            # Slot will have a FEMB - collect assembly data
            #### 14b. Pre-Assembly Data Collection (HWDB, CE box, Cover SN)
            top_assembly_data = collect_assembly_data("TOP")

            #### 15. QR Code Scanning & Validation (Triple verification)
            ##### First scan
            femb_id_1 = None  # Initialize
            while True:
                print(Fore.YELLOW + "         Step 1.21: " + Style.RESET_ALL + "Scan the FEMB QR code " + Fore.CYAN + "(1st scan)" + Style.RESET_ALL)
                femb_id_10 = input(Fore.YELLOW + '         >> ' + Style.RESET_ALL).strip()

                ##### Validate: Must contain IO-1826-1 (HD) or IO-1865-1 (VD)
                if ("-1826-1" in femb_id_10) or ("-1865-1" in femb_id_10):
                    break
                else:
                    print_status('error', "         No valid FEMB ID detected. Please try again.")

            ##### Second scan
            while True:
                print(Fore.YELLOW + "         Step 1.22: " + Style.RESET_ALL + "Scan the FEMB QR code " + Fore.CYAN + "(2nd scan)" + Style.RESET_ALL)
                femb_id_11 = input(Fore.YELLOW + '         >> ' + Style.RESET_ALL).strip()

                if ("-1826-1" in femb_id_11) or ("-1865-1" in femb_id_11):
                    break
                else:
                    print_status('error', "         No valid FEMB ID detected. Please try again.")

            ##### Match check - If scans match, proceed; else require 3rd scan
            if femb_id_11 == femb_id_10:
                print(Fore.GREEN + "         ✓ Top CE box QR ID recorded successfully" + Style.RESET_ALL)
                femb_id_1 = femb_id_11
            else:
                ##### Third scan verification (if first two don't match)
                print(
                    Fore.MAGENTA + '         ⚠️  QR codes do not match! Please scan a 3rd time and verify carefully.' + Style.RESET_ALL)
                while True:
                    while True:
                        print("         Scan top FEMB QR code " + Fore.CYAN + "(3rd attempt - try 1):" + Style.RESET_ALL)
                        femb_id_2 = input(Fore.YELLOW + '         >> ' + Style.RESET_ALL).strip()
                        if ("-1826-1" in femb_id_2) or ("-1865-1" in femb_id_2):
                            break
                        else:
                            print(Fore.RED + "         ✗ No valid FEMB ID detected. Please try again." + Style.RESET_ALL)

                    while True:
                        print("         Scan top FEMB QR code " + Fore.CYAN + "(3rd attempt - try 2):" + Style.RESET_ALL)
                        femb_id_3 = input(Fore.YELLOW + '         >> ' + Style.RESET_ALL).strip()
                        if ("-1826-1" in femb_id_3) or ("-1865-1" in femb_id_3):
                            break
                        else:
                            print(Fore.RED + "         ✗ No valid FEMB ID detected. Please try again." + Style.RESET_ALL)

                    if femb_id_2 == femb_id_3:
                        print(Fore.GREEN + "         ✓ QR codes match. Proceeding..." + Style.RESET_ALL)
                        femb_id_1 = femb_id_2
                        break
                    else:
                        print(
                            Fore.RED + "         ✗ QR codes still do not match. Please scan again carefully." + Style.RESET_ALL)

        # Version identification
        if femb_id_1 != 'EMPTY':
            femb_id_1 = femb_id_1.replace('/', '_')
            if "1826" in femb_id_1:
                version = "HD"
            else:
                version = "VD"
        # else: keep the version from bottom slot

        while True:
            print(Fore.RED + f"         Step 1.23: Confirm top FEMB SN is {femb_id_1}" + Style.RESET_ALL)
            print(
                "         Enter " + Fore.GREEN + "'y'" + Style.RESET_ALL + " to confirm, " + Fore.RED + "'n'" + Style.RESET_ALL + " to re-scan")
            user_input = input(Fore.YELLOW + '         >> ' + Style.RESET_ALL)
            if user_input.lower() == 'y':
                print(Fore.GREEN + "         ✓ Top slot confirmed." + Style.RESET_ALL)
                exit_outer = True
                break
            elif user_input.lower() == 'n':
                print(Fore.YELLOW + "         Restarting ID scanning..." + Style.RESET_ALL)
                exit_outer = False
                break
            else:
                print_status('error', "         Invalid input. Please enter 'y' or 'n'")

        if 'exit_outer' in locals() and exit_outer:
            break

    print(Fore.CYAN + "         Step 1.24: Continue assembly into top slot..." + Style.RESET_ALL)
    print("         Assembly instruction popup opening...")

    my_options = ["Install MiniSAS Cable and Clamp", "Install Test Cover", "Install Power Cable",
                  "Install Toy_TPCs and Cables", "Insert into Bottom Slot"]
    if version == "HD":
        pop01 = pop.show_image_popup(
            title="Top slot assembly instruction",
            image_path=os.path.join(ROOT_DIR, "GUI", "output_pngs", "11.png")
        )
    else:
        pop01 = pop.show_image_popup(
            title="Top slot assembly instruction",
            image_path=os.path.join(ROOT_DIR, "GUI", "output_pngs", "13.png")
        )

    confirm("Please Confirm the CE is install in the Top Slot")

    # Update Record CSV
    print()
    csv_data = {}
    with open(csv_file, mode='r', newline='', encoding='utf-8-sig') as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) == 2:
                key, value = row
                csv_data[key.strip()] = value.strip()

    with open(technician_csv, mode='r', newline='', encoding='utf-8-sig') as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) == 2:
                key, value = row
                csv_data[key.strip()] = value.strip()

    if 'tester' not in csv_data:
        csv_data['tester'] = 'sgao'
    else:
        csv_data['tester'] = input_name
    if 'SLOT0' not in csv_data:
        csv_data['SLOT0'] = 'H01'
    else:
        # If slot is marked as EMPTY, store as single space ' '
        csv_data['SLOT0'] = ' ' if femb_id_0 == 'EMPTY' else femb_id_0
    if 'SLOT1' not in csv_data:
        csv_data['SLOT1'] = 'H02'
    else:
        # If slot is marked as EMPTY, store as single space ' '
        csv_data['SLOT1'] = ' ' if femb_id_1 == 'EMPTY' else femb_id_1
    if 'SLOT2' not in csv_data:
        csv_data['SLOT2'] = ' '
    if 'SLOT3' not in csv_data:
        csv_data['SLOT3'] = ' '
    if 'test_site' not in csv_data:
        csv_data['test_site'] = 'BNL'
    if 'toy_TPC' not in csv_data:
        csv_data['toy_TPC'] = 'y'
    if 'comment' not in csv_data:
        # Format assembly data in CSV-style string
        csv_data['comment'] = (
            f"Bottom_HWDB={bottom_assembly_data['hwdb_qr']},"
            f"Bottom_CE={bottom_assembly_data['ce_box_sn']},"
            f"Bottom_Cover={bottom_assembly_data['cover_last4']},"
            f"Bottom_FEMB={femb_id_0},"
            f"Top_HWDB={top_assembly_data['hwdb_qr']},"
            f"Top_CE={top_assembly_data['ce_box_sn']},"
            f"Top_Cover={top_assembly_data['cover_last4']},"
            f"Top_FEMB={femb_id_1}"
        )
    if 'top_path' not in csv_data:
        csv_data['top_path'] = 'D:'

    with open(csv_file, mode="w", newline="", encoding='utf-8-sig') as file:
        writer = csv.writer(file)
        for key, value in csv_data.items():
            writer.writerow([key, value])

    #### 17. Read configuration to dictionary
    inform = cts.read_csv_to_dict(csv_file, 'RT')

# ============================================================================
## PHASE 2: CONNECT WITH CTS
# ============================================================================
if 2 in state_list:
    print_phase_header(2, 6, "Connect FEMB to CTS")
    ### 18. CTS Chamber Safety Check
    while True:
        print(Fore.YELLOW + "\n⚠️  SAFETY CHECK:" + Style.RESET_ALL)
        print("Please confirm the CTS chamber is empty.")
        print("Type " + Fore.GREEN + "'I confirm the chamber is empty'" + Style.RESET_ALL + " to proceed")
        com = input(Fore.YELLOW + '>> ' + Style.RESET_ALL)
        if com.lower() == 'i confirm the chamber is empty':
            print(
                Fore.GREEN + '✓ Chamber confirmed empty. Please install the CE test structure into CTS.' + Style.RESET_ALL)
            break

    ### 19. CE Test Structure Installation
    print(Fore.CYAN + '\nOpening installation instructions...' + Style.RESET_ALL)
    my_options = ["Open CTS Cover", "Place the CE boxes structure"]
    pop04 = pop.show_image_popup(
        title="Placing CE boxes into crate",
        image_path=os.path.join(ROOT_DIR, "GUI", "output_pngs", "14.png")
    )

    ### 20. Cable Connection
    print(Fore.CYAN + 'Opening cable connection instructions...' + Style.RESET_ALL)
    my_options = ["Open CTS Cover", "Place the CE boxes structure"]
    pop04 = pop.show_image_popup(
        title="WIB cable connection",
        image_path=os.path.join(ROOT_DIR, "GUI", "output_pngs", "15.png")
    )

    ### 21. Close CTS Cover
    print(Fore.CYAN + "Opening cover closing instructions..." + Style.RESET_ALL)
    my_options = ["Close the CTS Cover"]
    pop06 = pop.show_image_popup(
        title="Closing CTS cover",
        image_path=os.path.join(ROOT_DIR, "GUI", "output_pngs", "16.png")
    )

    ### 22. Copy configuration file to implementation file
    with open(csv_file, 'r') as source:
        with open(csv_file_implement, 'w') as destination:
            destination.write(source.read())

    ### 22a. Send email notification - Assembly Complete
    print_separator()
    print(Fore.CYAN + "📧 Sending assembly completion notification..." + Style.RESET_ALL)
    try:
        pre_info_temp = cts.read_csv_to_dict(csv_file_implement, 'RT')
        email_body = f"""Initial Assembly Complete - Ready for QC Testing

Test Site: {pre_info_temp.get('test_site', 'N/A')}
Tester: {pre_info_temp.get('tester', 'N/A')}

FEMBs Installed:
  - Slot 0 (Bottom): {pre_info_temp.get('SLOT0', 'N/A')}
  - Slot 1 (Top): {pre_info_temp.get('SLOT1', 'N/A')}

Next Step: Warm QC Test

Please prepare for QC testing.
"""
        send_email.send_email(sender, password, receiver,
                            f"Assembly Complete - {pre_info_temp.get('test_site', 'N/A')}",
                            email_body)
        print_status('success', "Assembly completion email sent")
    except Exception as e:
        print_status('warning', f"Failed to send email: {e}")
    print_separator()

else:
    ### 23. Load configuration directly (if Phase 2 skipped)
    print()
    csv_data = {}
    inform = cts.read_csv_to_dict(csv_file_implement, 'RT', True)
    while True:
        print(Fore.CYAN + 'Current configuration loaded.' + Style.RESET_ALL)
        print("Enter " + Fore.YELLOW + "'m'" + Style.RESET_ALL + " to modify the info")
        print("Enter " + Fore.GREEN + "'confirm'" + Style.RESET_ALL + " if info is correct")
        phase_2_2 = input(Fore.YELLOW + '>> ' + Style.RESET_ALL)
        if phase_2_2 == 'm':
            os.system(f'gedit "{csv_file_implement}"')
            inform = cts.read_csv_to_dict(csv_file_implement, 'RT', True)
        elif phase_2_2 == 'confirm':
            inform = cts.read_csv_to_dict(csv_file_implement, 'RT')
            break
        else:
            print_status('error', "Invalid input. Please enter 'm' or 'confirm'")

### 24. Send test start email notification
pre_info = cts.read_csv_to_dict(csv_file_implement, 'RT')
send_email.send_email(sender, password, receiver, "FEMB CE QC {}".format(pre_info['test_site']),
                      "FEMB QC start, stay tuned ...")

# ----------------------------------------------------------------------------
# CTS Warm Gas Completion Check (if started in Phase 0)
# ----------------------------------------------------------------------------
### 24a. Check and finish CTS warm gas if it was started in Phase 0
if 'cts_ready_time' in locals() and cts_ready_time is not None:
    print_separator()
    print(Fore.CYAN + "🌡️  Checking CTS Warm Gas status..." + Style.RESET_ALL)

    # Calculate remaining time
    current_time = time.time()
    remaining_time = cts_ready_time - current_time

    if remaining_time > 0:
        # Still waiting - use countdown_timer with skip option
        print_status('info', f"CTS Warm Gas still in progress ({int(remaining_time//60)} min {int(remaining_time%60)} sec remaining)")
        countdown_timer(
            total_seconds=remaining_time,
            message="CTS Warm Gas Purge - Waiting for completion",
            allow_skip=True
        )

    # Finish warm gas (set to IDLE)
    print_status('info', "Completing CTS Warm Gas procedure...")
    if cryo_auto_mode:
        if cryo.cryo_warmgas_finish():
            print_status('success', "CTS Warm Gas completed - CTS is now in IDLE state")
        else:
            print_status('error', "Failed to complete CTS Warm Gas - please check manually")
    else:
        # Manual mode - prompt user to set to IDLE
        print(Fore.YELLOW + "\n⚠️  Please set CTS to STATE 1 (IDLE)" + Style.RESET_ALL)
        while True:
            confirm_idle = input(Fore.YELLOW + "Enter 'Y' when CTS is in IDLE state >> " + Style.RESET_ALL)
            if confirm_idle.upper() == 'Y':
                print_status('success', "CTS is now in IDLE state")
                break
    print_separator()

# ----------------------------------------------------------------------------
# Power Supply Initialization
# ----------------------------------------------------------------------------
### 25. Initialize power supply for warm/cold/final tests
if any(x in state_list for x in [3, 4, 5]):
    psu = rigol.PowerSupplyController()

# ============================================================================
## PHASE 3: WARM QC TEST
# ============================================================================
if 3 in state_list:
    inform = cts.read_csv_to_dict(csv_file_implement, 'RT')
    ### 26. Warm QC Test Selection Menu
    while True:
        print("\n" + Fore.CYAN + "=" * 70)
        print("  OPTIONS:")
        print("=" * 70 + Style.RESET_ALL)
        print("  " + Fore.GREEN + "'y'" + Style.RESET_ALL + " - Continue with Warm QC")
        print("  " + Fore.YELLOW + "'s'" + Style.RESET_ALL + " - Skip Warm QC (proceed directly to Cold)")
        print("  " + Fore.RED + "'e'" + Style.RESET_ALL + " - Exit test program")
        Next = input(Fore.YELLOW + '>> ' + Style.RESET_ALL)

        #### Skip warm test option
        if Next == 's':
            if confirm("Do you want to skip the Warm QC?"):
                print(Fore.YELLOW + "⏩ Skipping Warm QC..." + Style.RESET_ALL)
                break

        #### Exit program option
        elif Next == 'e':
            if confirm("Do you want to exit the test program?"):
                print(Fore.RED + "Exiting QC program..." + Style.RESET_ALL)
                sys.exit()

        #### 27. Begin Warm QC Execution
        elif Next == 'y':
            if confirm("Do you want to begin the Warm QC?"):
                print_phase_header(3, 6, "Warm QC Test", "~35 min")

                ##### 27a. Power ON WIB
                print_step("Powering ON WIB", 1, 4)
                psu.set_channel(1, 12.0, 3.0, on=True)
                psu.set_channel(2, 12.0, 3.0, on=True)
                print_status('info', "Establishing Ethernet communication (35 seconds)...")
                time.sleep(35)

                ##### 27b. Ping WIB
                print_step("Testing WIB connection", 2, 4)
                QC_Process(path=inform['QC_data_root_folder'], QC_TST_EN=77, input_info=inform)
                print_status('success', 'WIB connection established')

                ##### 27c. WIB Initialization (Step C1, <2 min)
                print_step("WIB initialization", 3, 4, "<2 min")
                QC_Process(path=inform['QC_data_root_folder'], QC_TST_EN=0, input_info=inform)
                QC_Process(path=inform['QC_data_root_folder'], QC_TST_EN=1, input_info=inform)

                ##### 27d. FEMB Warm Checkout with Auto-Retry (Step C2, <3 min)
                print_step("FEMB warm checkout", 4, 4, "<3 min")

                # Auto-retry loop: max 3 attempts (1 initial + 2 retries)
                max_checkout_attempts = 3
                checkout_attempt = 0
                checkout_passed = False
                first_auto_retry_done = False  # Track if we've done initial auto-retry

                while checkout_attempt < max_checkout_attempts:
                    checkout_attempt += 1

                    if checkout_attempt > 1 and not first_auto_retry_done:
                        print_status('warning', f"Checkout Retry {checkout_attempt - 1}/2")

                    # Run checkout
                    wcdata_path, wcreport_path = QC_Process(
                        path=inform['QC_data_root_folder'],
                        QC_TST_EN=2,
                        input_info=inform
                    )

                    # Wait for test files to be fully written
                    time.sleep(2)

                    # Check result using the specific paths returned by QC_Process
                    checkout_passed = check_checkout_result(wcdata_path, wcreport_path)

                    if checkout_passed:
                        print_status('success', f"Checkout PASSED (attempt {checkout_attempt})")
                        break
                    else:
                        print_status('error', f"Checkout FAILED (attempt {checkout_attempt})")

                        # Only auto-retry during first 3 attempts
                        if checkout_attempt < max_checkout_attempts and not first_auto_retry_done:
                            print(Fore.YELLOW + f"  Automatically retrying... ({max_checkout_attempts - checkout_attempt} attempts remaining)" + Style.RESET_ALL)
                            time.sleep(2)  # Brief pause before retry
                        else:
                            # After 3 automatic attempts failed, switch to manual retry mode
                            first_auto_retry_done = True

                            # Send email notification (only once after initial 3 failures)
                            if checkout_attempt == max_checkout_attempts:
                                print(Fore.RED + "\n" + "=" * 70)
                                print("  ⚠️  CHECKOUT FAILED AFTER 3 ATTEMPTS")
                                print("=" * 70 + Style.RESET_ALL)
                                print(Fore.YELLOW + "📧 Sending failure notification email..." + Style.RESET_ALL)
                                send_email.send_email(
                                    sender, password, receiver,
                                    f"Warm Checkout Failed - {pre_info.get('test_site', 'Unknown')}",
                                    f"Warm Checkout failed after {max_checkout_attempts} attempts. Awaiting operator decision."
                                )

                            # User decision with retry option
                            print("\n" + Fore.YELLOW + "⚠️  What would you like to do?" + Style.RESET_ALL)
                            print("  " + Fore.CYAN + "'r'" + Style.RESET_ALL + " - Retry checkout once more")
                            print("  " + Fore.GREEN + "'c'" + Style.RESET_ALL + " - Continue with QC test anyway (not recommended)")
                            print("  " + Fore.RED + "'e'" + Style.RESET_ALL + " - Exit and disassemble test structure")

                            while True:
                                decision = input(Fore.CYAN + ">> " + Style.RESET_ALL).lower()
                                if decision == 'r':
                                    print(Fore.CYAN + "🔄 Retrying checkout once..." + Style.RESET_ALL)
                                    # Continue the while loop for one more attempt
                                    max_checkout_attempts += 1  # Extend the limit by 1
                                    break
                                elif decision == 'c':
                                    # Confirm before continuing despite failure
                                    if confirm("⚠️  Are you sure you want to continue despite checkout failure?"):
                                        print(Fore.YELLOW + "⚠️  Continuing despite checkout failure..." + Style.RESET_ALL)
                                        # Exit checkout loop and continue to QC
                                        checkout_attempt = max_checkout_attempts  # Force exit
                                        break
                                    else:
                                        print(Fore.YELLOW + "Cancelled. Please choose another option." + Style.RESET_ALL)
                                        continue
                                elif decision == 'e':
                                    # Confirm before exiting to disassembly
                                    if confirm("⚠️  Are you sure you want to exit and skip to disassembly?"):
                                        print(Fore.RED + "Exiting QC test. Proceeding to disassembly..." + Style.RESET_ALL)
                                        goto_disassembly = True
                                        checkout_attempt = max_checkout_attempts  # Force exit
                                        break
                                    else:
                                        print(Fore.YELLOW + "Cancelled. Please choose another option." + Style.RESET_ALL)
                                        continue
                                else:
                                    print(Fore.RED + "Invalid input. Please enter 'r', 'c', or 'e'" + Style.RESET_ALL)

                            # If user chose to exit, break out of checkout loop
                            if goto_disassembly:
                                break

                # Only continue to QC if checkout passed or user chose to continue
                if goto_disassembly:
                    # Skip remaining QC steps - will jump to disassembly
                    print(Fore.YELLOW + "⚠️  Skipping Warm QC Test due to checkout failure..." + Style.RESET_ALL)
                else:
                    ##### 27e. FEMB Warm QC Test (Step C3, <30 min) with Manual Retry Only
                    print_separator()
                    print_step("FEMB Warm Quality Control Test", estimated_time="<30 min")

                    # Manual retry loop - NO automatic retries (test is too long ~30 min)
                    qc_passed = False
                    wqdata_path = None
                    wqreport_path = None

                    while True:
                        # Run QC test (single attempt)
                        wqdata_path, wqreport_path = QC_Process(
                            path=inform['QC_data_root_folder'],
                            QC_TST_EN=3,
                            input_info=inform
                        )

                        # Wait for test files to be fully written
                        time.sleep(60)

                        # Sync report to network if it exists (reports may be generated locally after data transfer)
                        if wqreport_path and os.path.exists(wqreport_path):
                            try:
                                import shutil
                                network_path = inform.get('Network_Upload_Path', '/data/rtss/femb')
                                qc_data_root = inform['QC_data_root_folder']

                                if network_path and network_path != qc_data_root:
                                    femb_qc_root = os.path.join(qc_data_root, "FEMB_QC")
                                    if wqreport_path.startswith(femb_qc_root):
                                        report_rel_path = os.path.relpath(wqreport_path, femb_qc_root)
                                        network_report_dir = os.path.join(network_path, "FEMB_QC", report_rel_path)

                                        print(Fore.CYAN + f"📤 Syncing Warm QC report to network..." + Style.RESET_ALL)
                                        os.makedirs(os.path.dirname(network_report_dir), exist_ok=True)
                                        shutil.copytree(wqreport_path, network_report_dir, dirs_exist_ok=True)
                                        print(Fore.GREEN + f"  ✓ Report synced" + Style.RESET_ALL)
                            except Exception as e:
                                print(Fore.YELLOW + f"⚠️  Report network sync failed: {e}" + Style.RESET_ALL)

                        # Check result using the specific paths returned by QC_Process
                        qc_passed = check_checkout_result(wqdata_path, wqreport_path)

                        if qc_passed:
                            print(Fore.GREEN + "✓ Warm QC PASSED" + Style.RESET_ALL)
                            break
                        else:
                            print(Fore.RED + "✗ Warm QC FAILED" + Style.RESET_ALL)

                            # Print fault file paths
                            print(Fore.YELLOW + "\n" + "-" * 70)
                            print("  📋 Checking for fault files in Warm QC results...")
                            print("-" * 70 + Style.RESET_ALL)
                            check_fault_files(
                                paths=[wqdata_path, wqreport_path],
                                show_p_files=False,
                                inform=inform,
                                time_limit_hours=None
                            )

                            # Send email notification
                            print(Fore.RED + "\n" + "=" * 70)
                            print("  ⚠️  WARM QC TEST FAILED")
                            print("=" * 70 + Style.RESET_ALL)
                            print(Fore.YELLOW + "📧 Sending failure notification email..." + Style.RESET_ALL)
                            send_email.send_email(
                                sender, password, receiver,
                                f"Warm QC Test Failed - {pre_info.get('test_site', 'Unknown')}",
                                "Warm QC Test failed. Awaiting operator decision."
                            )

                            # User decision with retry option
                            print("\n" + Fore.YELLOW + "⚠️  What would you like to do?" + Style.RESET_ALL)
                            print("  " + Fore.CYAN + "'r'" + Style.RESET_ALL + " - Retry Warm QC once more (~30 min)")
                            print("  " + Fore.GREEN + "'c'" + Style.RESET_ALL + " - Continue anyway (not recommended)")
                            print("  " + Fore.RED + "'e'" + Style.RESET_ALL + " - Exit and disassemble test structure")

                            while True:
                                decision = input(Fore.CYAN + ">> " + Style.RESET_ALL).lower()
                                if decision == 'r':
                                    # Confirm before retrying (takes ~30 min)
                                    if confirm("⚠️  Retry will take ~30 minutes. Are you sure?"):
                                        print(Fore.CYAN + "🔄 Retrying Warm QC (this will take ~30 min)..." + Style.RESET_ALL)
                                        break  # Continue outer while loop for retry
                                    else:
                                        print(Fore.YELLOW + "Cancelled. Please choose another option." + Style.RESET_ALL)
                                        continue
                                elif decision == 'c':
                                    # Confirm before continuing despite failure
                                    if confirm("⚠️  Are you sure you want to continue despite Warm QC failure?"):
                                        print(Fore.YELLOW + "⚠️  Continuing despite Warm QC failure..." + Style.RESET_ALL)
                                        # Exit retry loop and continue to cleanup
                                        qc_passed = False  # Mark as not passed but continue
                                        break
                                    else:
                                        print(Fore.YELLOW + "Cancelled. Please choose another option." + Style.RESET_ALL)
                                        continue
                                elif decision == 'e':
                                    # Confirm before exiting to disassembly
                                    if confirm("⚠️  Are you sure you want to exit and skip to disassembly?"):
                                        print(Fore.RED + "Exiting QC test. Will cleanup then proceed to disassembly..." + Style.RESET_ALL)
                                        goto_disassembly = True
                                        break
                                    else:
                                        print(Fore.YELLOW + "Cancelled. Please choose another option." + Style.RESET_ALL)
                                        continue
                                else:
                                    print(Fore.RED + "Invalid input. Please enter 'r', 'c', or 'e'" + Style.RESET_ALL)

                            # Break out of outer while loop if user chose 'c' or 'e'
                            if decision in ['c', 'e']:
                                break

                    ##### 27f. Close WIB Linux (always run after QC test for cleanup)
                    if wqdata_path is not None:  # Only if we actually ran the test
                        print(Fore.CYAN + "🔄 Shutting down WIB Linux system..." + Style.RESET_ALL)
                        QC_Process(path=inform['QC_data_root_folder'], QC_TST_EN=6, input_info=inform)

                    ##### 27g. Power OFF WIB (always run after QC test for safety)
                    if wqdata_path is not None:  # Only if we actually ran the test
                        print(Fore.YELLOW + "⚡ Powering OFF WIB..." + Style.RESET_ALL)
                        while True:
                            total_i = 0
                            for ch in (1, 2):
                                v, i = psu.measure(ch)
                                print(f"  CH{ch}: {v:.3f} V, {i:.3f} A")
                                total_i += i
                            print(Fore.CYAN + f"  Total current: {total_i:.3f} A" + Style.RESET_ALL)
                            psu.turn_off_all()
                            if total_i < 0.2:
                                print(Fore.GREEN + "✓ Power OFF successful" + Style.RESET_ALL)
                                break
                            else:
                                print(
                                    Fore.YELLOW + '⚠️  High current detected, attempting power off again...' + Style.RESET_ALL)

                #### 28-29. Warm QC Result Check and Handling
                # Only check results if we didn't skip due to checkout/QC failure
                if not goto_disassembly:
                    time.sleep(2)

                    # Use the specific paths from the most recent test execution
                    paths = []
                    if wqdata_path:
                        paths.append(wqdata_path)
                    if wqreport_path:
                        paths.append(wqreport_path)

                    # If no paths available, skip result display
                    if paths:
                        # Display detailed results (retry already handled in individual tests)
                        # Set allow_retry=False to avoid double-asking user
                        all_passed, should_retry, failed_slots = handle_qc_results(
                            paths=paths,
                            inform=inform,
                            test_phase="Warm QC Final Report",
                            allow_retry=False,  # Retry already handled in Checkout and QC Test
                            verbose=True
                        )

                    # Exit the Warm QC loop after showing results
                    break
                else:
                    # Checkout or QC test failed and user chose to exit, skip to disassembly
                    break

        else:
            print_status('error', "Invalid input. Please enter 'y', 's', or 'e'")


    ### 30. Warm QC Completion
    print_separator()
    print_status('success', "Warm QC completed!")
    print_separator()

    ### 30a. Generate Warm QC Summary and Send Email
    print(Fore.CYAN + "📧 Generating Warm QC summary and sending notification..." + Style.RESET_ALL)
    try:
        # Analyze Warm QC results
        warm_qc_paths = []
        if 'wqdata_path' in locals() and wqdata_path:
            warm_qc_paths.append(wqdata_path)
        if 'wqreport_path' in locals() and wqreport_path:
            warm_qc_paths.append(wqreport_path)

        if warm_qc_paths:
            # Generate summary
            warm_qc_result = analyze_test_results(warm_qc_paths, inform, time_limit_hours=None)
            summary_filename = f"Warm_QC_Summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            summary_path = os.path.join(inform['QC_data_root_folder'], summary_filename)
            generate_qc_summary("Warm QC", inform, warm_qc_result, summary_path)

            # Prepare email body
            email_body = f"""Warm QC Test Completed - Ready for Cold Down

Test Site: {pre_info.get('test_site', 'N/A')}
Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Summary:
  Total Fault Files: {warm_qc_result.total_faults}
  Total Pass Files: {warm_qc_result.total_passes}
  Overall Result: {'PASS' if warm_qc_result.total_faults == 0 else 'FAIL'}

Next Steps:
  1. Switch CTS to COLD mode for 5 minutes
  2. Switch to IMMERSE mode
  3. Wait for LN2 to reach Level 3
  4. Double confirm heat LED is OFF

Detailed summary is attached.
"""
            # Send email with attachment
            send_email.send_email_with_attachment(
                sender, password, receiver,
                f"Warm QC Complete - {pre_info.get('test_site', 'N/A')}",
                email_body,
                summary_path
            )
            print_status('success', "Warm QC summary email sent with attachment")
        else:
            # Fallback if no paths available
            send_email.send_email(
                sender, password, receiver,
                f"Warm QC Complete - {pre_info.get('test_site', 'N/A')}",
                "Warm QC Done. Switch to COLD for 5 min, then IMMERSE. Wait for LN2 to reach Level 3. Double confirm heat LED OFF."
            )
            print_status('success', "Warm QC completion email sent")
    except Exception as e:
        print_status('warning', f"Failed to send Warm QC summary email: {e}")

# ============================================================================
## PHASE 4: COLD QC TEST
# ============================================================================
# Skip if checkout failed in Phase 3
if 4 in state_list and not goto_disassembly:
    print_phase_header(4, 6, "Cold QC Test (LN₂)", "~90 min")

    ### 32. CTS Cool Down Procedure
    # print_status('info', "Opening CTS cool down instructions...")
    # pop.show_image_popup(
    #     title="CTS Cool Down – Power ON",
    #     image_path=os.path.join(ROOT_DIR, "GUI", "output_pngs", "14.png")
    # )

    print(Fore.CYAN + "🌡️  Initiating CTS cool down procedure..." + Style.RESET_ALL)

    if cryo_auto_mode:
        # Automatic CTS Control Mode
        print_status('info', "Automatic CTS control enabled")

        ### 32a. Cold Gas Pre-cooling (5 minutes)
        print_step("Cold gas pre-cooling", 1, 3, "~5 min")
        if cryo.cryo_coldgas(waitminutes=5):
            print_status('success', "Cold gas pre-cooling completed")
        else:
            print_status('error', "Cold gas pre-cooling failed or manual control required")

        ### 32b. LN₂ Immersion with Automatic Level Monitoring
        print_step("LN₂ immersion with level monitoring", 2, 3, f"~{cts_ln2_fill_wait//60} min")
        if cryo.cryo_immerse(waitminutes=cts_ln2_fill_wait//60):
            print_status('success', "LN₂ immersion complete - Level 3 or 4 reached")
        else:
            print_status('error', "LN₂ immersion failed or manual control required")

        ### 32c. Final Status Check
        print_step("Checking CTS status", 3, 3)
        tc_level, dewar_level = cryo.cts_status()
        if tc_level >= 3:
            print_status('success', f"Chamber Level: {tc_level}, Dewar Level: {dewar_level}")
        else:
            print_status('warning', f"Chamber Level: {tc_level}, Dewar Level: {dewar_level}")
            print(Fore.YELLOW + "⚠️  Level may be insufficient for cold testing" + Style.RESET_ALL)

    else:
        # Manual CTS Control Mode
        print_status('warning', "Manual CTS control mode - follow instructions below")

        ### Manual Instructions
        print("\n" + Fore.YELLOW + "=" * 70)
        print("  MANUAL CTS CONTROL INSTRUCTIONS")
        print("=" * 70 + Style.RESET_ALL)
        print(Fore.CYAN + "Step 1: Cold Gas Pre-cooling (~5 minutes)" + Style.RESET_ALL)
        print("  1. Set CTS to " + Fore.CYAN + "STATE 3 (Cold Gas)" + Style.RESET_ALL)
        print("  2. Wait for 5-minute countdown")

        # Confirm cold gas mode is set
        while True:
            print(Fore.YELLOW + "\nHave you set CTS to STATE 3 (Cold Gas)?" + Style.RESET_ALL)
            print("Enter " + Fore.GREEN + "'Y'" + Style.RESET_ALL + " when ready")
            confirm_coldgas = input(Fore.YELLOW + '>> ' + Style.RESET_ALL)
            if confirm_coldgas.upper() == 'Y':
                print_status('success', "Cold gas mode confirmed")
                break
            else:
                print_status('error', "Invalid input. Please enter 'Y'")

        # Display countdown timer (can be skipped with 'j')
        countdown_timer(
            total_seconds=5*60,
            message="CTS Cold Gas Pre-cooling (5 min)",
            allow_skip=True
        )

        print("\n" + Fore.CYAN + f"Step 2: LN₂ Immersion (~{cts_ln2_fill_wait//60} minutes)" + Style.RESET_ALL)
        print("  1. Set CTS to " + Fore.CYAN + "STATE 4 (LN₂ Immersion)" + Style.RESET_ALL)
        print(f"  2. Wait for LN₂ to reach " + Fore.CYAN + "LEVEL 3 or 4" + Style.RESET_ALL)
        print(f"  3. Monitor level sensors every few minutes")
        print(f"  4. Expected wait time: ~{cts_ln2_fill_wait//60} minutes")

        ### LN2 Refill Wait Timer
        timer_count(
            start_message=f"⏰ Wait for LN2 Refill (~{cts_ln2_fill_wait//60} min)!",
            exit_hint="Type 's' to stop",
            end_message="✅ Timer complete!",
            auto_exit_seconds=cts_ln2_fill_wait,
            exit_chars=['s', 'stop']
        )

        # Confirm LN2 Level
        print("\n" + Fore.CYAN + "=" * 70)
        print("  CTS COLD DOWN STATUS CHECK")
        print("=" * 70 + Style.RESET_ALL)
        print(Fore.YELLOW + "⚠️  Please ensure:" + Style.RESET_ALL)
        print("   • LN2 level has reached " + Fore.CYAN + "LEVEL 3 or 4" + Style.RESET_ALL)
        print("   • Heat LED is " + Fore.GREEN + "OFF" + Style.RESET_ALL)

        print(Fore.YELLOW + "\n⚠️  Please verify CTS is fully cooled down:" + Style.RESET_ALL)
        print("   • LN₂ level has reached LEVEL 3 or 4")
        print("   • Heat LED is OFF")
        print("\nType " + Fore.GREEN + "'confirm'" + Style.RESET_ALL + " to continue, or " + Fore.CYAN + "'j'" + Style.RESET_ALL + " to skip")

        while True:
            com = input(Fore.YELLOW + '>> ' + Style.RESET_ALL).strip().lower()
            if com == 'confirm':
                print(Fore.GREEN + "✓ CTS cool down confirmed." + Style.RESET_ALL)
                break
            elif com == 'j':
                print_status('warning', "⚠️  Skipping CTS cool down confirmation - ensure conditions are met!")
                break
            else:
                print(Fore.RED + "Invalid input. Type 'confirm' or 'j'" + Style.RESET_ALL)

    # Load Cold QC Info
    infoln = cts.read_csv_to_dict(csv_file_implement, 'LN')

    # Cold QC Action Selection
    while True:
        # print("\n" + Fore.CYAN + "=" * 70)
        # print("  OPTIONS:")
        # print("=" * 70 + Style.RESET_ALL)
        # print("  " + Fore.GREEN + "'y'" + Style.RESET_ALL + " - Start Cold QC")
        # print("  " + Fore.YELLOW + "'s'" + Style.RESET_ALL + " - Skip Cold QC")
        # print("  " + Fore.RED + "'e'" + Style.RESET_ALL + " - Exit test program")
        # Next = input(Fore.YELLOW + '>> ' + Style.RESET_ALL)
        #
        # # Skip Cold QC
        # if Next == 's':
        #     if confirm("Do you want to skip Cold QC?"):
        #         print(Fore.YELLOW + "⏩ Skipping Cold QC..." + Style.RESET_ALL)
        #         break
        #
        # # Exit Test and go to warm-up + disassembly
        # elif Next == 'e':
        #     if confirm("Do you want to skip Cold QC and proceed to warm-up + disassembly?"):
        #         print(Fore.YELLOW + "Skipping Cold QC, will proceed to warm-up then disassembly..." + Style.RESET_ALL)
        #         goto_disassembly = True
        #         break
        #
        # # Start Cold QC
        # elif Next == 'y':
        if True:
            # if confirm("Do you want to begin Cold QC?"):
            if True:
                print_separator()

                # Power ON WIB
                print_step("Powering ON WIB", 1, 4)
                psu.set_channel(1, 12.0, 3.0, on=True)
                psu.set_channel(2, 12.0, 3.0, on=True)
                print_status('info', "Initializing ethernet link (35 seconds)...")
                time.sleep(35)

                # Cold QC Steps
                print_step("Testing WIB connection", 2, 4)
                QC_Process(path=infoln['QC_data_root_folder'], QC_TST_EN=77, input_info=infoln)

                print_step("WIB initialization", 3, 4, "<2 min")
                QC_Process(path=infoln['QC_data_root_folder'], QC_TST_EN=0, input_info=infoln)
                QC_Process(path=infoln['QC_data_root_folder'], QC_TST_EN=1, input_info=infoln)

                ##### Cold Checkout with Auto-Retry (Step C2, <3 min)
                print_step("FEMB cold checkout", 4, 4, "<3 min")

                # Auto-retry loop: max 3 attempts (1 initial + 2 retries)
                max_cold_checkout_attempts = 3
                cold_checkout_attempt = 0
                cold_checkout_passed = False
                lcdata_path = None
                lcreport_path = None

                while cold_checkout_attempt < max_cold_checkout_attempts:
                    cold_checkout_attempt += 1

                    if cold_checkout_attempt > 1:
                        print(Fore.YELLOW + f"\n🔄 Cold Checkout Retry {cold_checkout_attempt - 1}/2" + Style.RESET_ALL)

                    # Run cold checkout
                    lcdata_path, lcreport_path = QC_Process(
                        path=infoln['QC_data_root_folder'],
                        QC_TST_EN=2,
                        input_info=infoln
                    )

                    # Wait for test files to be fully written
                    time.sleep(2)

                    # Check result using the specific paths returned by QC_Process
                    cold_checkout_passed = check_checkout_result(lcdata_path, lcreport_path)

                    if cold_checkout_passed:
                        print_status('success', f"Cold Checkout PASSED (attempt {cold_checkout_attempt})")
                        break
                    else:
                        print_status('error', f"Cold Checkout FAILED (attempt {cold_checkout_attempt})")

                        if cold_checkout_attempt < max_cold_checkout_attempts:
                            print(Fore.YELLOW + f"  Automatically retrying... ({max_cold_checkout_attempts - cold_checkout_attempt} attempts remaining)" + Style.RESET_ALL)
                            time.sleep(2)  # Brief pause before retry

                # Handle cold checkout failure after all retries
                if not cold_checkout_passed:
                    print(Fore.RED + "\n" + "=" * 70)
                    print("  ⚠️  COLD CHECKOUT FAILED AFTER 3 ATTEMPTS")
                    print("  ➡️  Proceeding to Cold QC anyway...")
                    print("=" * 70 + Style.RESET_ALL)

                    # Print fault file paths
                    print(Fore.YELLOW + "\n" + "-" * 70)
                    print("  📋 Checking for fault files in Cold Checkout results...")
                    print("-" * 70 + Style.RESET_ALL)
                    check_fault_files(
                        paths=[lcdata_path, lcreport_path],
                        show_p_files=False,
                        inform=infoln,
                        time_limit_hours=None
                    )

                    # Send email notification
                    print(Fore.YELLOW + "\n📧 Sending failure notification email..." + Style.RESET_ALL)
                    send_email.send_email(
                        sender, password, receiver,
                        f"Cold Checkout Failed - {pre_info.get('test_site', 'Unknown')}",
                        f"Cold Checkout failed after {max_cold_checkout_attempts} attempts. Proceeding to Cold QC test."
                    )

                # CTS Level Monitoring (if automatic mode)
                if cryo_auto_mode:
                    print_step("Checking CTS LN₂ level", estimated_time="<5 sec")
                    tc_level, dewar_level = cryo.cts_status()
                    if tc_level >= 3:
                        print_status('success', f"LN₂ Level OK - Chamber: Level {tc_level}, Dewar: {dewar_level}")
                    else:
                        print_status('warning', f"LN₂ Level Low - Chamber: Level {tc_level}, Dewar: {dewar_level}")
                        print(Fore.YELLOW + "⚠️  Consider refilling before continuing" + Style.RESET_ALL)

                print_separator()
                print_step("FEMB Cold Quality Control Test", estimated_time="<30 min")
                lqdata_path, lqreport_path = QC_Process(path=infoln['QC_data_root_folder'], QC_TST_EN=3, input_info=infoln)

                # Sync report to network if it exists
                if lqreport_path and os.path.exists(lqreport_path):
                    try:
                        import shutil
                        network_path = infoln.get('Network_Upload_Path', '/data/rtss/femb')
                        qc_data_root = infoln['QC_data_root_folder']

                        if network_path and network_path != qc_data_root:
                            femb_qc_root = os.path.join(qc_data_root, "FEMB_QC")
                            if lqreport_path.startswith(femb_qc_root):
                                report_rel_path = os.path.relpath(lqreport_path, femb_qc_root)
                                network_report_dir = os.path.join(network_path, "FEMB_QC", report_rel_path)

                                print(Fore.CYAN + f"📤 Syncing Cold QC report to network..." + Style.RESET_ALL)
                                os.makedirs(os.path.dirname(network_report_dir), exist_ok=True)
                                shutil.copytree(lqreport_path, network_report_dir, dirs_exist_ok=True)
                                print(Fore.GREEN + f"  ✓ Report synced" + Style.RESET_ALL)
                    except Exception as e:
                        print(Fore.YELLOW + f"⚠️  Report network sync failed: {e}" + Style.RESET_ALL)

                print(Fore.CYAN + "🔄 Closing WIB Linux system..." + Style.RESET_ALL)
                QC_Process(path=infoln['QC_data_root_folder'], QC_TST_EN=6, input_info=infoln)

                # Power Off WIB (with retries)
                print(Fore.YELLOW + "⚡ Powering OFF WIB..." + Style.RESET_ALL)
                max_attempts = 5
                attempt = 0

                while True:
                    total_i = 0
                    print("\n" + Fore.CYAN + "Checking WIB current..." + Style.RESET_ALL)

                    for ch in (1, 2):
                        v, i = psu.measure(ch)
                        print(f"  CH{ch}: {v:.3f} V, {i:.3f} A")
                        total_i += i

                    print(Fore.CYAN + f"  Total current: {total_i:.3f} A" + Style.RESET_ALL)
                    psu.turn_off_all()

                    if total_i < 0.2:
                        print(Fore.GREEN + "✓ WIB power OFF successful." + Style.RESET_ALL)
                        break

                    attempt += 1
                    print(Fore.YELLOW + f"⚠️  Power off attempt {attempt}/{max_attempts} failed." + Style.RESET_ALL)

                    if attempt >= max_attempts:
                        print(Fore.RED + "\n" + "=" * 60)
                        print("⚠️  MANUAL INTERVENTION REQUIRED")
                        print("=" * 60 + Style.RESET_ALL)
                        while True:
                            print(Fore.YELLOW + "Please manually power off the WIB." + Style.RESET_ALL)
                            print('Type ' + Fore.GREEN + '"confirm"' + Style.RESET_ALL + ' when done')
                            com = input(Fore.YELLOW + '>> ' + Style.RESET_ALL)
                            if com.lower() == "confirm":
                                print(Fore.GREEN + "✓ Manual confirmation received." + Style.RESET_ALL)
                                break
                        break

                print_separator()
                print_status('success', "Cold QC completed!")

                # CTS Level Monitoring after Cold QC (if automatic mode)
                if cryo_auto_mode:
                    print_step("Final CTS LN₂ level check", estimated_time="<5 sec")
                    tc_level, dewar_level = cryo.cts_status()
                    if tc_level >= 3:
                        print_status('success', f"LN₂ Level maintained - Chamber: Level {tc_level}, Dewar: {dewar_level}")
                    else:
                        print_status('warning', f"LN₂ Level depleted - Chamber: Level {tc_level}, Dewar: {dewar_level}")

                print_separator()


            #### Cold QC Result Check and Handling
            time.sleep(2)

            # Use the specific paths from the Cold QC test execution
            paths = []
            if lqdata_path:
                paths.append(lqdata_path)
            if lqreport_path:
                paths.append(lqreport_path)

            # Use enhanced result checking
            if paths:
                all_passed, should_retry, failed_slots = handle_qc_results(
                    paths=paths,
                    inform=infoln,  # Use Cold QC info, not Warm QC info
                    test_phase="Cold QC Test",
                    allow_retry=True,
                    verbose=False
                )
            else:
                all_passed = False
                should_retry = False
                failed_slots = []

            if all_passed:
                print(Fore.GREEN + "\n🎉 Cold QC Test Passed!" + Style.RESET_ALL)
                print(Fore.CYAN + "📧 Generating Cold QC summary and sending notification..." + Style.RESET_ALL)

                # Generate Cold QC summary and send email
                try:
                    cold_qc_paths = []
                    if 'lqdata_path' in locals() and lqdata_path:
                        cold_qc_paths.append(lqdata_path)
                    if 'lqreport_path' in locals() and lqreport_path:
                        cold_qc_paths.append(lqreport_path)

                    if cold_qc_paths:
                        # Generate summary
                        cold_qc_result = analyze_test_results(cold_qc_paths, infoln, time_limit_hours=None)
                        summary_filename = f"Cold_QC_Summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                        summary_path = os.path.join(infoln['QC_data_root_folder'], summary_filename)
                        generate_qc_summary("Cold QC", infoln, cold_qc_result, summary_path)

                        # Prepare email body
                        email_body = f"""Cold QC Test Completed - Ready for Warm-Up

Test Site: {pre_info.get('test_site', 'N/A')}
Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Summary:
  Total Fault Files: {cold_qc_result.total_faults}
  Total Pass Files: {cold_qc_result.total_passes}
  Overall Result: PASS

Next Step:
  Please perform the warm-up procedure ({cts_warmup_wait//60} minutes)

Detailed summary is attached.
"""
                        # Send email with attachment
                        send_email.send_email_with_attachment(
                            sender, password, receiver,
                            f"Cold QC Complete - {pre_info.get('test_site', 'N/A')}",
                            email_body,
                            summary_path
                        )
                        print_status('success', "Cold QC summary email sent with attachment")
                    else:
                        # Fallback if no paths available
                        send_email.send_email(
                            sender, password, receiver,
                            f"Cold QC Complete - {pre_info.get('test_site', 'N/A')}",
                            "Cold QC Done - Pass cold test is done, please perform the warm-up procedure"
                        )
                        print_status('success', "Cold QC completion email sent")
                except Exception as e:
                    print_status('warning', f"Failed to send Cold QC summary email: {e}")

                break
            else:
                # Cold QC Test failed
                print(Fore.RED + "\n" + "=" * 70)
                print("  ⚠️  COLD QC TEST FAILED")
                print("=" * 70 + Style.RESET_ALL)

                # Print fault file paths
                print(Fore.YELLOW + "\n" + "-" * 70)
                print("  📋 Checking for fault files in Cold QC results...")
                print("-" * 70 + Style.RESET_ALL)
                check_fault_files(
                    paths=[lqdata_path, lqreport_path],
                    show_p_files=False,
                    inform=infoln,
                    time_limit_hours=None
                )

                # Send failure notification
                print(Fore.YELLOW + "\n📧 Sending failure notification email..." + Style.RESET_ALL)
                send_email.send_email(
                    sender, password, receiver,
                    f"Cold QC Test Failed - {pre_info.get('test_site', 'Unknown')}",
                    "Cold QC Test failed. Awaiting operator decision."
                )

                # User decision with retry option
                print("\n" + Fore.YELLOW + "⚠️  What would you like to do?" + Style.RESET_ALL)
                print("  " + Fore.CYAN + "'r'" + Style.RESET_ALL + " - Retry Cold QC once more (~30 min)")
                print("  " + Fore.GREEN + "'c'" + Style.RESET_ALL + " - Continue to warm-up anyway (not recommended)")
                print("  " + Fore.RED + "'e'" + Style.RESET_ALL + " - Exit Cold QC, proceed to warm-up then disassembly")

                while True:
                    decision = input(Fore.CYAN + ">> " + Style.RESET_ALL).lower()
                    if decision == 'r':
                        # Confirm before retrying (takes ~30 min)
                        if confirm("⚠️  Retry will take ~30 minutes. Are you sure?"):
                            print(Fore.CYAN + "🔄 Retrying Cold QC (this will take ~30 min)..." + Style.RESET_ALL)
                            break  # Continue outer while loop for retry
                        else:
                            print(Fore.YELLOW + "Cancelled. Please choose another option." + Style.RESET_ALL)
                            continue
                    elif decision == 'c':
                        # Confirm before continuing despite failure
                        if confirm("⚠️  Are you sure you want to continue to warm-up despite Cold QC failure?"):
                            print(Fore.YELLOW + "⚠️  Continuing to warm-up despite Cold QC failure..." + Style.RESET_ALL)
                            # Exit retry loop and continue to warm-up
                            break
                        else:
                            print(Fore.YELLOW + "Cancelled. Please choose another option." + Style.RESET_ALL)
                            continue
                    elif decision == 'e':
                        # Confirm before exiting to warm-up + disassembly
                        if confirm("⚠️  Are you sure you want to exit Cold QC and proceed to warm-up then disassembly?"):
                            print(Fore.RED + "Exiting Cold QC. Will proceed to warm-up then disassembly..." + Style.RESET_ALL)
                            goto_disassembly = True
                            break
                        else:
                            print(Fore.YELLOW + "Cancelled. Please choose another option." + Style.RESET_ALL)
                            continue
                    else:
                        print(Fore.RED + "Invalid input. Please enter 'r', 'c', or 'e'" + Style.RESET_ALL)

                # Break out of outer while loop if user chose 'c' or 'e'
                if decision in ['c', 'e']:
                    break

        else:
            print_status('error', "Invalid input. Please enter 'y', 's', or 'e'")

    # Warm Up CTS
    print("\n" + Fore.CYAN + "=" * 70)
    print("  CTS WARM-UP PROCEDURE")
    print("=" * 70 + Style.RESET_ALL)

    # print(Fore.CYAN + "Opening CTS warm-up instructions..." + Style.RESET_ALL)
    # pop.show_image_popup(
    #     title="CTS Warm-Up",
    #     image_path=os.path.join(ROOT_DIR, "GUI", "output_pngs", "15.png")
    # )

    if cryo_auto_mode:
        # Automatic CTS Warm-up
        print_status('info', "Automatic CTS warm-up control enabled")
        print_step("CTS warm gas purge", estimated_time=f"~{cts_warmup_wait//60} min")

        if cryo.cryo_warmgas(waitminutes=cts_warmup_wait//60):
            print_status('success', "CTS warm-up completed successfully")
        else:
            print_status('error', "CTS warm-up failed or manual control required")

        # Set to IDLE state
        if cryo.cryo_create():
            cryo.cryo_cmd(mode=b'1')  # Set to STATE 1 (IDLE)
            cryo.cryo_close()
            print_status('success', "CTS set to IDLE state")

    else:
        # Manual CTS Warm-up
        print_status('warning', "Manual CTS warm-up control mode")

        print("\n" + Fore.YELLOW + "=" * 70)
        print("  MANUAL CTS WARM-UP INSTRUCTIONS")
        print("=" * 70 + Style.RESET_ALL)
        print(Fore.CYAN + "Step 1: Set CTS to Warm Gas mode" + Style.RESET_ALL)
        print("  1. Set CTS to " + Fore.CYAN + "STATE 2 (Warm Gas)" + Style.RESET_ALL)
        print(f"  2. Wait approximately {cts_warmup_wait//60} minutes for warm-up")
        print()

        timer_count(
            start_message=f"⏰ Wait for warm up (~{cts_warmup_wait//60} min)!",
            exit_hint="Type 's' to stop",
            end_message="✅ Timer complete!",
            auto_exit_seconds=cts_warmup_wait,
            exit_chars=['s', 'stop']
        )

        print("\n" + Fore.CYAN + "Step 2: Return CTS to IDLE state" + Style.RESET_ALL)
        print("  1. Set CTS to " + Fore.CYAN + "STATE 1 (IDLE)" + Style.RESET_ALL)

        # Confirm IDLE state
        while True:
            print(Fore.YELLOW + "\nHave you set CTS to STATE 1 (IDLE)?" + Style.RESET_ALL)
            print("Enter " + Fore.GREEN + "'Y'" + Style.RESET_ALL + " when ready, or " + Fore.CYAN + "'j'" + Style.RESET_ALL + " to skip")
            user_input = input(Fore.YELLOW + ">> " + Style.RESET_ALL).strip().lower()

            if user_input == 'y':
                print_status('success', "CTS warm-up complete")
                break
            elif user_input == 'j':
                print_status('warning', "⚠️  Skipping IDLE confirmation - ensure CTS is in proper state!")
                break
            else:
                print_status('error', "Invalid input. Enter 'Y' or 'j'")

    print(Fore.CYAN + "=" * 70 + Style.RESET_ALL)

# ============================================================================
## PHASE 5: FINAL CHECKOUT
# ============================================================================
# Skip if checkout failed in Phase 3
if 5 in state_list and not goto_disassembly:
    print_phase_header(5, 6, "Final Checkout", "<35 min")
    inform = cts.read_csv_to_dict(csv_file_implement, 'RT')

    ### 41. Send Final Checkout Email Notification
    send_email.send_email(
        sender, password, receiver,
        "FEMB CE QC {}".format('test_site'),
        "Please proceed to Final Checkout."
    )

    while True:
        # print("\n" + Fore.CYAN + "OPTIONS:" + Style.RESET_ALL)
        # print("  " + Fore.GREEN + "'y'" + Style.RESET_ALL + " - Continue with Final Checkout")
        # print("  " + Fore.YELLOW + "'s'" + Style.RESET_ALL + " - Skip Final Checkout")
        # print("  " + Fore.RED + "'e'" + Style.RESET_ALL + " - Exit test program")
        # Next = input(Fore.YELLOW + '>> ' + Style.RESET_ALL)
        #
        # # Skip Final Checkout
        # if Next == 's':
        #     if confirm("Do you want to skip the Final Checkout?"):
        #         print(Fore.YELLOW + "⏩ Skipping Final Checkout..." + Style.RESET_ALL)
        #         break
        #
        # # Exit
        # elif Next == 'e':
        #     if confirm("Do you want to exit the test program?"):
        #         print(Fore.RED + "Exiting..." + Style.RESET_ALL)
        #         sys.exit()
        #
        # # Begin Phase 5
        # elif Next == 'y':
        if True:
            # if not confirm("Do you want to begin the Final Checkout?"):
            #     continue
            print_separator()

            # Power on WIB
            print_step("Powering ON WIB", 1, 4)
            psu.set_channel(1, 12.0, 3.0, on=True)
            psu.set_channel(2, 12.0, 3.0, on=True)

            print_status('info', "Establishing Ethernet communication (35 seconds)...")
            time.sleep(35)

            # Ping WIB
            print_step("Testing WIB connection", 2, 4)
            QC_Process(path=inform['QC_data_root_folder'], QC_TST_EN=77, input_info=inform)

            # WIB Initial
            print_step("WIB initialization", 3, 4, "<2 min")
            QC_Process(path=inform['QC_data_root_folder'], QC_TST_EN=0, input_info=inform)
            QC_Process(path=inform['QC_data_root_folder'], QC_TST_EN=1, input_info=inform)

            ##### Final Checkout with Auto-Retry (Step C2, <3 min)
            print_step("FEMB final checkout", 4, 4, "<3 min")

            # Auto-retry loop: max 3 attempts (1 initial + 2 retries)
            max_final_checkout_attempts = 3
            final_checkout_attempt = 0
            final_checkout_passed = False
            first_final_auto_retry_done = False
            fcdata_path = None
            fcreport_path = None

            while final_checkout_attempt < max_final_checkout_attempts:
                final_checkout_attempt += 1

                if final_checkout_attempt > 1 and not first_final_auto_retry_done:
                    print(Fore.YELLOW + f"\n🔄 Final Checkout Retry {final_checkout_attempt - 1}/2" + Style.RESET_ALL)

                # Run final checkout
                fcdata_path, fcreport_path = QC_Process(
                    path=inform['QC_data_root_folder'],
                    QC_TST_EN=5,
                    input_info=inform
                )

                # Wait for test files to be fully written
                time.sleep(2)

                # Check result using the specific paths returned by QC_Process
                final_checkout_passed = check_checkout_result(fcdata_path, fcreport_path)

                if final_checkout_passed:
                    print_status('success', f"Final Checkout PASSED (attempt {final_checkout_attempt})")
                    break
                else:
                    print_status('error', f"Final Checkout FAILED (attempt {final_checkout_attempt})")

                    # Only auto-retry during first 3 attempts
                    if final_checkout_attempt < max_final_checkout_attempts and not first_final_auto_retry_done:
                        print(Fore.YELLOW + f"  Automatically retrying... ({max_final_checkout_attempts - final_checkout_attempt} attempts remaining)" + Style.RESET_ALL)
                        time.sleep(2)
                    else:
                        # After 3 automatic attempts failed, switch to manual retry mode
                        first_final_auto_retry_done = True

                        # Send email notification (only once after initial 3 failures)
                        if final_checkout_attempt == max_final_checkout_attempts:
                            print(Fore.RED + "\n" + "=" * 70)
                            print("  ⚠️  FINAL CHECKOUT FAILED AFTER 3 ATTEMPTS")
                            print("=" * 70 + Style.RESET_ALL)
                            print(Fore.YELLOW + "📧 Sending failure notification email..." + Style.RESET_ALL)
                            send_email.send_email(
                                sender, password, receiver,
                                f"Final Checkout Failed - {pre_info.get('test_site', 'Unknown')}",
                                f"Final Checkout failed after {max_final_checkout_attempts} attempts. Awaiting operator decision."
                            )

                        # User decision with retry option
                        print("\n" + Fore.YELLOW + "⚠️  What would you like to do?" + Style.RESET_ALL)
                        print("  " + Fore.CYAN + "'r'" + Style.RESET_ALL + " - Retry final checkout once more")
                        print("  " + Fore.GREEN + "'c'" + Style.RESET_ALL + " - Continue anyway (not recommended)")
                        print("  " + Fore.RED + "'e'" + Style.RESET_ALL + " - Exit test program")

                        while True:
                            decision = input(Fore.CYAN + ">> " + Style.RESET_ALL).lower()
                            if decision == 'r':
                                print(Fore.CYAN + "🔄 Retrying final checkout once..." + Style.RESET_ALL)
                                # Continue the while loop for one more attempt
                                max_final_checkout_attempts += 1
                                break
                            elif decision == 'c':
                                # Confirm before continuing despite failure
                                if confirm("⚠️  Are you sure you want to continue despite final checkout failure?"):
                                    print(Fore.YELLOW + "⚠️  Continuing despite final checkout failure..." + Style.RESET_ALL)
                                    # Exit checkout loop and continue
                                    final_checkout_attempt = max_final_checkout_attempts
                                    break
                                else:
                                    print(Fore.YELLOW + "Cancelled. Please choose another option." + Style.RESET_ALL)
                                    continue
                            elif decision == 'e':
                                # Confirm before exiting
                                if confirm("⚠️  Are you sure you want to exit the test program?"):
                                    print(Fore.RED + "Exiting test program..." + Style.RESET_ALL)
                                    sys.exit()
                                else:
                                    print(Fore.YELLOW + "Cancelled. Please choose another option." + Style.RESET_ALL)
                                    continue
                            else:
                                print(Fore.RED + "Invalid input. Please enter 'r', 'c', or 'e'" + Style.RESET_ALL)

            # Final QC
            print_separator()
            print_step("Shutting down WIB Linux system")
            QC_Process(path=inform['QC_data_root_folder'], QC_TST_EN=6, input_info=inform)

            # Finish
            print_separator("=")
            print_status('success', "FINAL CHECKOUT COMPLETED!")
            print_separator("=")

            ### Send Final QC Summary Email
            print(Fore.CYAN + "📧 Generating overall QC summary and sending final notification..." + Style.RESET_ALL)
            try:
                # Collect all test paths for comprehensive summary
                all_test_paths = []

                # Add Warm QC paths
                if 'wqdata_path' in locals() and wqdata_path:
                    all_test_paths.append(wqdata_path)
                if 'wqreport_path' in locals() and wqreport_path:
                    all_test_paths.append(wqreport_path)

                # Add Cold QC paths
                if 'lqdata_path' in locals() and lqdata_path:
                    all_test_paths.append(lqdata_path)
                if 'lqreport_path' in locals() and lqreport_path:
                    all_test_paths.append(lqreport_path)

                # Add Final Checkout paths
                if 'fcdata_path' in locals() and fcdata_path:
                    all_test_paths.append(fcdata_path)
                if 'fcreport_path' in locals() and fcreport_path:
                    all_test_paths.append(fcreport_path)

                if all_test_paths:
                    # Generate comprehensive summary
                    overall_result = analyze_test_results(all_test_paths, inform, time_limit_hours=None)
                    summary_filename = f"Overall_QC_Summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                    summary_path = os.path.join(inform['QC_data_root_folder'], summary_filename)
                    generate_qc_summary("Overall QC Test", inform, overall_result, summary_path)

                    # Determine overall pass/fail
                    overall_passed = overall_result.total_faults == 0

                    # Prepare detailed email body
                    email_body = f"""QC Testing Complete - Ready for Classification

Test Site: {pre_info.get('test_site', 'N/A')}
Completion Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

OVERALL TEST SUMMARY:
=====================
  Total Fault Files: {overall_result.total_faults}
  Total Pass Files: {overall_result.total_passes}
  Overall Result: {'✓ PASS' if overall_passed else '✗ FAIL'}

FEMB Results:
"""
                    # Add per-slot details
                    for slot_num in sorted(overall_result.slot_status.keys()):
                        passed, femb_id = overall_result.slot_status[slot_num]
                        slot_position = "Bottom" if slot_num == '0' else "Top"
                        status = "PASS" if passed else "FAIL"
                        email_body += f"  {slot_position} Slot{slot_num}: {femb_id} - {status}\n"

                    email_body += f"""
Next Steps:
  1. Power OFF the WIB
  2. Proceed to disassembly and classification
  3. Store FEMBs according to test results

Detailed comprehensive summary is attached.
"""
                    # Send email with overall summary attachment
                    send_email.send_email_with_attachment(
                        sender, password, receiver,
                        f"QC Complete - Please Classify - {pre_info.get('test_site', 'N/A')}",
                        email_body,
                        summary_path
                    )
                    print_status('success', "Final QC summary email sent with comprehensive report")
                else:
                    # Fallback if no paths available
                    send_email.send_email(
                        sender, password, receiver,
                        f"QC Complete - {pre_info.get('test_site', 'N/A')}",
                        "Final Checkout Complete. Please power OFF the WIB and proceed to disassembly and classification."
                    )
                    print_status('success', "Final QC email sent")
            except Exception as e:
                print_status('warning', f"Failed to send final QC summary email: {e}")

            print_status('warning', "IMPORTANT: Please power OFF the WIB!")

            # Auto/manual power off
            safe_power_off(psu)

            break

        else:
            print_status('error', "Invalid input. Please enter 'y', 's', or 'e'")

# ============================================================================
## PHASE 6: DISASSEMBLY
# ============================================================================
# Always execute Phase 6 if selected, or if goto_disassembly flag is set
if 6 in state_list or goto_disassembly:

    # Display reason for entering disassembly phase
    if goto_disassembly:
        print_separator("=")
        print_status('warning', "ENTERING DISASSEMBLY DUE TO TEST FAILURE")
        print_separator("=")
        print(Fore.YELLOW + "\nTest failed and user chose to exit. Proceeding to disassembly...\n" + Style.RESET_ALL)

    print_phase_header(6, 6, "Disassembly")
    print(Fore.YELLOW + "\n⚠️  Please:" + Style.RESET_ALL)
    print("   • Power OFF the CTS")
    print("   • Remove and disassemble the FEMB CE boxes\n")

    ### 46. Disassembly Preparation
    ### 47. Remove CE Boxes from Chamber
    print(Fore.CYAN + "Opening removal instructions..." + Style.RESET_ALL)
    pop.show_image_popup(
        title="Move CE boxes out of chamber",
        image_path=os.path.join(ROOT_DIR, "GUI", "output_pngs", "17.png")
    )

    img_cebox = get_cebox_image(version, ROOT_DIR)

    ### Important Note
    print_separator("=")
    print(Fore.CYAN + "CE BOX DISASSEMBLY & PACKAGING" + Style.RESET_ALL)
    print_separator("=")
    print(Fore.YELLOW + "\n⚠️  Important: Each CE box must be returned to its ORIGINAL foam box with ORIGINAL cover" + Style.RESET_ALL)
    print(Fore.YELLOW + "We will disassemble one slot at a time and immediately package it.\n" + Style.RESET_ALL)

    # Read assembly data from csv_data
    csv_data_dis = {}
    if os.path.exists(csv_file):
        with open(csv_file, mode='r', newline='', encoding='utf-8-sig') as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) == 2:
                    key, value = row
                    csv_data_dis[key.strip()] = value.strip()

    # Parse assembly data
    comment_str = csv_data_dis.get('comment', '')
    if comment_str and comment_str != 'QC test':
        assembly_data_all = parse_assembly_data_from_comment(comment_str)

        # Collect test paths for result analysis
        disassembly_paths = []
        # Add warm checkout paths (Phase 3)
        if 'wcdata_path' in locals() and wcdata_path and wcdata_path != r"D:\data\temp":
            disassembly_paths.extend([wcdata_path, wcreport_path])
        # Add warm QC paths (Phase 3)
        if 'wqdata_path' in locals() and wqdata_path and wqdata_path != r"D:\data\temp":
            disassembly_paths.extend([wqdata_path, wqreport_path])
        # Add cold checkout paths (Phase 4)
        if 'lcdata_path' in locals() and lcdata_path and lcdata_path != r"D:\data\temp":
            disassembly_paths.extend([lcdata_path, lcreport_path])
        # Add cold QC paths (Phase 4)
        if 'lqdata_path' in locals() and lqdata_path and lqdata_path != r"D:\data\temp":
            disassembly_paths.extend([lqdata_path, lqreport_path])
        # Add final checkout paths (Phase 5)
        if 'fcdata_path' in locals() and fcdata_path and fcdata_path != r"D:\data\temp":
            disassembly_paths.extend([fcdata_path, fcreport_path])

        # Get QC test results to determine PASS/FAIL for each slot
        qc_result = None
        if len(disassembly_paths) > 0:
            try:
                # Analyze test results for disassembly validation
                qc_result = analyze_test_results(disassembly_paths, pre_info, time_limit_hours=None)
            except Exception as e:
                # If result analysis fails, default to None
                print(Fore.YELLOW + f"⚠️  Could not analyze test results: {e}" + Style.RESET_ALL)
                qc_result = None
        else:
            print(Fore.YELLOW + "⚠️  No test results available for analysis" + Style.RESET_ALL)

        # Get test results for pass/fail status
        # Top slot test result
        top_passed = True
        if qc_result and qc_result.slot_status:
            slot_info = qc_result.slot_status.get('1', (True, ''))
            top_passed = slot_info[0] if isinstance(slot_info, tuple) else slot_info

        # Bottom slot test result
        bottom_passed = True
        if qc_result and qc_result.slot_status:
            slot_info = qc_result.slot_status.get('0', (True, ''))
            bottom_passed = slot_info[0] if isinstance(slot_info, tuple) else slot_info

        ### 48. Disassemble and Package TOP CE Box
        print_separator("=")
        print(Fore.CYAN + "STEP 1: DISASSEMBLE AND PACKAGE TOP SLOT" + Style.RESET_ALL)
        print_separator("=")

        if assembly_data_all['top']['ce_box_sn'] != 'EMPTY':
            # Show disassembly instructions
            print(Fore.CYAN + "\n📖 Opening TOP CE box disassembly instructions..." + Style.RESET_ALL)
            # pop.show_image_popup(
            #     title="Disassembly TOP CE Box",
            #     image_path=img_cebox
            # )

            print(Fore.GREEN + "✓ Please disassemble TOP slot CE box" + Style.RESET_ALL)

            # Validate cover ID, foam box ID, and package
            print(Fore.CYAN + "\n📦 Now validate and package TOP slot..." + Style.RESET_ALL)
            validate_disassembly_for_slot('top', assembly_data_all['top'], top_passed)
            if version == "VD":
                pop01 = pop.show_image_popup(
                    title="Top slot Disassembly instruction",
                    image_path=os.path.join(ROOT_DIR, "GUI", "output_pngs", "18.png")
                )
            else:  # HD version
                pop01 = pop.show_image_popup(
                    title="Top slot Disassembly instruction",
                    image_path=os.path.join(ROOT_DIR, "GUI", "output_pngs", "19.png")
                )
        else:
            print_status('info', "TOP slot was EMPTY - skipping")

        ### 49. Disassemble and Package BOTTOM CE Box
        print_separator("=")
        print(Fore.CYAN + "STEP 2: DISASSEMBLE AND PACKAGE BOTTOM SLOT" + Style.RESET_ALL)
        print_separator("=")

        if assembly_data_all['bottom']['ce_box_sn'] != 'EMPTY':
            # Show disassembly instructions
            print(Fore.CYAN + "\n📖 Opening BOTTOM CE box disassembly instructions..." + Style.RESET_ALL)
            # pop.show_image_popup(
            #     title="Disassembly BOTTOM CE Box",
            #     image_path=img_cebox
            # )

            print(Fore.GREEN + "✓ Please disassemble BOTTOM slot CE box" + Style.RESET_ALL)

            # Validate cover ID, foam box ID, and package
            print(Fore.CYAN + "\n📦 Now validate and package BOTTOM slot..." + Style.RESET_ALL)
            validate_disassembly_for_slot('bottom', assembly_data_all['bottom'], bottom_passed)
            if version == "VD":
                pop01 = pop.show_image_popup(
                    title="BOTTOM slot Disassembly instruction",
                    image_path=os.path.join(ROOT_DIR, "GUI", "output_pngs", "18.png")
                )
            else:  # HD version
                pop01 = pop.show_image_popup(
                    title="BOTTOM slot Disassembly instruction",
                    image_path=os.path.join(ROOT_DIR, "GUI", "output_pngs", "19.png")
                )
        else:
            print_status('info', "BOTTOM slot was EMPTY - skipping")

        print_separator("=")
        print_status('success', "All CE box disassembly and packaging complete!")
        print_separator("=")

    else:
        print_status('warning', "No assembly data found - skipping disassembly and packaging validation")
        print(Fore.YELLOW + "         (This may be an older test run without assembly tracking)\n" + Style.RESET_ALL)

    ### 50. Accessory Return Confirmation
    print_separator("=")
    print(Fore.CYAN + "STEP 3: ACCESSORY RETURN CONFIRMATION" + Style.RESET_ALL)
    print_separator("=")
    while True:
        print(Fore.CYAN + "\nOpening accessory return instructions..." + Style.RESET_ALL)
        pop.show_image_popup(
            title="Return Accessories to Their Original Position",
            image_path=os.path.join(ROOT_DIR, "GUI", "output_pngs", "20.png")
        )

        print(
            Fore.YELLOW + "\n⚠️  Please confirm all accessories have been returned to their original positions." + Style.RESET_ALL)
        print('Type ' + Fore.GREEN + '"confirm"' + Style.RESET_ALL + ' to continue')
        order = input(Fore.YELLOW + '>> ' + Style.RESET_ALL)

        if order.lower() == "confirm":
            print(Fore.GREEN + "✓ Accessories check completed. Thank you!" + Style.RESET_ALL)
            break
        else:
            print(Fore.RED + "Not confirmed. Please verify again." + Style.RESET_ALL)

# ============================================================================
## ENDING STAGE (Lines 1019-1069)
# ============================================================================

### 51. Close Power Supply Connection
if any(x in state_list for x in [3, 4, 5]):
    psu.close()

### 52. Display Completion Message
print("\n" + Fore.GREEN + "=" * 70)
print_status('success', "QC TEST CYCLE COMPLETED!")
print("=" * 70 + Style.RESET_ALL)
print(Fore.CYAN + "\nPlease prepare for the next test cycle.\n" + Style.RESET_ALL)

### 53. Final Comprehensive Result Check (Optional)
time.sleep(2)

# Collect actual paths generated during this test run
# Use specific paths from QC_Process instead of scanning entire directories
paths = []

print(Fore.CYAN + "\n" + "=" * 70)
print("  FINAL COMPREHENSIVE RESULTS REVIEW")
print("=" * 70 + Style.RESET_ALL)

print(Fore.YELLOW + "\n📁 Collecting test result paths from this run..." + Style.RESET_ALL)

# Add warm checkout paths (Phase 3)
if wcdata_path != r"D:\data\temp":
    paths.extend([wcdata_path, wcreport_path])
    print(Fore.CYAN + f"  ✓ Warm Checkout Data:   {wcdata_path}" + Style.RESET_ALL)
    print(Fore.CYAN + f"  ✓ Warm Checkout Report: {wcreport_path}" + Style.RESET_ALL)

# Add warm QC paths (Phase 3)
if wqdata_path != r"D:\data\temp":
    paths.extend([wqdata_path, wqreport_path])
    print(Fore.CYAN + f"  ✓ Warm QC Data:         {wqdata_path}" + Style.RESET_ALL)
    print(Fore.CYAN + f"  ✓ Warm QC Report:       {wqreport_path}" + Style.RESET_ALL)

# Add cold checkout paths (Phase 4)
if lcdata_path != r"D:\data\temp":
    paths.extend([lcdata_path, lcreport_path])
    print(Fore.CYAN + f"  ✓ Cold Checkout Data:   {lcdata_path}" + Style.RESET_ALL)
    print(Fore.CYAN + f"  ✓ Cold Checkout Report: {lcreport_path}" + Style.RESET_ALL)

# Add cold QC paths (Phase 4)
if lqdata_path != r"D:\data\temp":
    paths.extend([lqdata_path, lqreport_path])
    print(Fore.CYAN + f"  ✓ Cold QC Data:         {lqdata_path}" + Style.RESET_ALL)
    print(Fore.CYAN + f"  ✓ Cold QC Report:       {lqreport_path}" + Style.RESET_ALL)

# Add final checkout paths (Phase 5)
if fcdata_path != r"D:\data\temp":
    paths.extend([fcdata_path, fcreport_path])
    print(Fore.CYAN + f"  ✓ Final Checkout Data:  {fcdata_path}" + Style.RESET_ALL)
    print(Fore.CYAN + f"  ✓ Final Checkout Report: {fcreport_path}" + Style.RESET_ALL)

if len(paths) == 0:
    print(Fore.YELLOW + "  ⚠️  No test paths were generated during this run" + Style.RESET_ALL)
else:
    print(Fore.GREEN + f"\n✓ Total paths collected: {len(paths)}" + Style.RESET_ALL)

print(Fore.CYAN + "=" * 70 + Style.RESET_ALL)
print("\nWould you like to review the complete test results?")
print("  " + Fore.GREEN + "'y'" + Style.RESET_ALL + " - Yes, show detailed results")
print("  " + Fore.YELLOW + "'n'" + Style.RESET_ALL + " - No, skip to completion")

while True:
    choice = input(Fore.YELLOW + ">> " + Style.RESET_ALL).lower()
    if choice == 'y':
        # Display comprehensive results using actual test paths (no time filtering needed)
        result = analyze_test_results(paths, pre_info, time_limit_hours=None)
        display_qc_results(result, "Complete QC Cycle", verbose=True)
        break
    elif choice == 'n':
        print(Fore.CYAN + "Skipping detailed review..." + Style.RESET_ALL)
        break
    else:
        print(Fore.RED + "Invalid input. Please enter 'y' or 'n'" + Style.RESET_ALL)

### 53b. Labeling Instructions Based on Test Results
print("\n" + Fore.CYAN + "=" * 70)
print("  📋 FEMB LABELING INSTRUCTIONS")
print("=" * 70 + Style.RESET_ALL)

# Analyze final results to determine which FEMBs passed/failed
if len(paths) > 0:
    final_result = analyze_test_results(paths, pre_info, time_limit_hours=None)

    print(Fore.YELLOW + "\nPlease label the FEMB boards according to test results:\n" + Style.RESET_ALL)

    # Check each slot and provide labeling instructions
    labeled_count = 0
    for slot_num in ['0', '1', '2', '3']:
        if slot_num in final_result.slot_status:
            passed, femb_id = final_result.slot_status[slot_num]
            slot_name = "Bottom" if slot_num == '0' else ("Top" if slot_num == '1' else f"Slot{slot_num}")

            if passed:
                print(Fore.GREEN + f"  ✓ {slot_name} Slot{slot_num}: FEMB {femb_id}" + Style.RESET_ALL)
                print(Fore.GREEN + f"     → Apply GREEN label" + Style.RESET_ALL)
            else:
                print(Fore.RED + f"  ✗ {slot_name} Slot{slot_num}: FEMB {femb_id}" + Style.RESET_ALL)
                print(Fore.RED + f"     → Apply RED label" + Style.RESET_ALL)
            print()
            labeled_count += 1

    if labeled_count == 0:
        print(Fore.YELLOW + "  ⚠️  No FEMB boards found in this test session" + Style.RESET_ALL)
else:
    print(Fore.YELLOW + "\n⚠️  No test results available. Please label boards manually.\n" + Style.RESET_ALL)

print(Fore.CYAN + "=" * 70 + Style.RESET_ALL)
confirm("Have you labeled all FEMB boards correctly?")

# ----------------------------------------------------------------------------
# Upload Test Data to Network Drive
# ----------------------------------------------------------------------------
### 53a. Upload all test data and reports to network drive
print("\n" + Fore.CYAN + "Preparing to upload test data to network drive..." + Style.RESET_ALL)

# Load network upload path from config
try:
    with open(technician_csv, mode='r', newline='', encoding='utf-8-sig') as file:
        reader = csv.reader(file)
        upload_config = {}
        for row in reader:
            if len(row) == 2:
                key, value = row
                upload_config[key.strip()] = value.strip()

    network_upload_path = upload_config.get('Network_Upload_Path', '/data/rtss/femb')
    qc_root = upload_config.get('QC_data_root_folder', '/mnt/data')
except Exception as e:
    print_status('warning', f"Could not load upload configuration: {e}")
    network_upload_path = '/data/rtss/femb'
    qc_root = '/mnt/data'

# Collect FEMB IDs for upload folder naming
femb_ids = []
try:
    # Try to read from csv_file_implement to get FEMB IDs
    if os.path.exists(csv_file_implement):
        with open(csv_file_implement, mode='r', newline='', encoding='utf-8-sig') as file:
            reader = csv.reader(file)
            temp_data = {}
            for row in reader:
                if len(row) == 2:
                    key, value = row
                    temp_data[key.strip()] = value.strip()

            # Extract FEMB IDs from SLOT0 and SLOT1
            for slot_key in ['SLOT0', 'SLOT1', 'SLOT2', 'SLOT3']:
                if slot_key in temp_data:
                    femb_id = temp_data[slot_key]
                    if femb_id and femb_id not in ['EMPTY', 'N/A', '', ' ']:
                        femb_ids.append(femb_id)
except Exception as e:
    print_status('warning', f"Could not read FEMB IDs: {e}")

print(Fore.CYAN + f"Network upload path: {network_upload_path}" + Style.RESET_ALL)
print(Fore.CYAN + f"FEMB IDs: {', '.join(femb_ids) if femb_ids else 'None'}" + Style.RESET_ALL)

# Perform upload
# upload_success = upload_to_network(
#     qc_data_root=qc_root,
#     csv_file=csv_file,
#     csv_file_implement=csv_file_implement,
#     network_path=network_upload_path,
#     femb_ids=femb_ids
# )

# if upload_success:
#     print_status('success', "All test data uploaded successfully")
# else:
#     print_status('warning', "Upload failed or incomplete - please upload manually")
#     print(Fore.YELLOW + f"  Manual upload: Copy data from {qc_root}/FEMB_QC to {network_upload_path}" + Style.RESET_ALL)

# ----------------------------------------------------------------------------

### 54. Record Test Result
confirm("Please Record the Test Result")

### 55. Close CTS and Exit
confirm("Please Close The CTS, then, exit ...")

# ============================================================================
## MAIN PROGRAM ENTRY POINT
# ============================================================================
### 56. Main Entry - Close Terminal Window
if __name__ == "__main__":
    print(Fore.CYAN + "Process ongoing..." + Style.RESET_ALL)
    print(Fore.GREEN + "✓ Completed. Closing window..." + Style.RESET_ALL)
    time.sleep(1)
    close_terminal()