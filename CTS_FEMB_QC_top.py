# ============================================================================
# CTS FEMB QC Top Level Script
# Cold Electronics Quality Control System for DUNE
# ============================================================================

# ----------------------------------------------------------------------------
# Module Imports
# ----------------------------------------------------------------------------
# 1. Module Imports - System and third-party libraries
import cts_ssh_FEMB as cts
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

# Import QC modules - Custom utility modules
from qc_utils import timer_count, check_fault_files, QC_Process, close_terminal, check_checkout_result
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
print(f"✓ Analysis Code Launched (Minimal monitor window at bottom-right)")

## 6. Pre-Test Preparation
### 6.1 Email Validation - Get and confirm user email
receiver = get_email()

### 6.2 Display Checklist Popups
#### Pop window 1: Initial Checkout List
pop.show_image_popup(
    title="Initial Checkout List Confirm",
    image_path=os.path.join(ROOT_DIR, "GUI", "output_pngs", "2.png")
)

#### Pop window 2: Accessory tray #1
pop.show_image_popup(
    title="Checklist for accessory tray #1",
    image_path=os.path.join(ROOT_DIR, "GUI", "output_pngs", "3.png")
)

#### Pop window 3: Accessory tray #2
pop.show_image_popup(
    title="Checklist for accessory tray #2",
    image_path=os.path.join(ROOT_DIR, "GUI", "output_pngs", "4.png")
)

### 7. LN2 Dewar Refill Confirmation
#### Determine shift and required LN2 volume
hour = datetime.now().hour
if 1 <= hour <= 11:
    LN2 = '1800 [Morning shift]'
else:
    LN2 = '1200 [Afternoon shift]'

#### Prompt for LN2 refill confirmation
while True:
    print(Fore.CYAN + f"Has the 50L dewar been refilled to {LN2}?" + Style.RESET_ALL)
    print("Enter " + Fore.GREEN + "'Y'" + Style.RESET_ALL + " (Yes) or " + Fore.RED + "'N'" + Style.RESET_ALL + " (No)")
    result = input(Fore.YELLOW + '>> ' + Style.RESET_ALL)
    if result.upper() == 'N':
        pop.show_image_popup(
            title="Test Dewar Refill",
            image_path=os.path.join(ROOT_DIR, "GUI", "output_pngs", "5.png")
        )
    elif result.upper() == 'Y':
        print(Fore.GREEN + "✓ LN2 refill confirmed." + Style.RESET_ALL)
        break

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
            image_path=os.path.join(ROOT_DIR, "GUI", "output_pngs", "6.png")
        )

        #### 10. QR Code Scanning & Validation (Triple verification)
        ##### First scan
        while True:
            print(Fore.CYAN + "         [1/2] Scan the QR code (1st scan)" + Style.RESET_ALL)
            femb_id_00 = input(Fore.YELLOW + '         >> ' + Style.RESET_ALL)
            ##### Validate: Must contain IO-1826-1 (HD) or IO-1865-1 (VD)
            if ("-1826-1" in femb_id_00) or ("-1865-1" in femb_id_00):
                break
            else:
                print_status('error', "         No valid FEMB ID detected. Please try again.")

        ##### Second scan
        while True:
            print(Fore.CYAN + "         [2/2] Scan the QR code (2nd scan)" + Style.RESET_ALL)
            femb_id_01 = input(Fore.YELLOW + '         >> ' + Style.RESET_ALL)
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
                    print("         Scan bottom QR code " + Fore.CYAN + "(3rd attempt - try 1):" + Style.RESET_ALL)
                    femb_id_2 = input(Fore.YELLOW + '         >> ' + Style.RESET_ALL).strip()
                    if ("-1826-1" in femb_id_2) or ("-1865-1" in femb_id_2):
                        break
                    else:
                        print(Fore.RED + "         ✗ No valid FEMB ID detected. Please try again." + Style.RESET_ALL)

                while True:
                    print("         Scan bottom QR code " + Fore.CYAN + "(3rd attempt - try 2):" + Style.RESET_ALL)
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
        femb_id_0 = femb_id_0.replace('/', '_')
        if "1826" in femb_id_0:
            version = "HD"  # Horizontal Drift
        else:
            version = "VD"  # Vertical Drift

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
            image_path=os.path.join(ROOT_DIR, "GUI", "output_pngs", "7.png")
        )
    else:  # HD version
        pop01 = pop.show_image_popup(
            title="Bottom slot assembly instruction",
            image_path=os.path.join(ROOT_DIR, "GUI", "output_pngs", "9.png")
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
            image_path=os.path.join(ROOT_DIR, "GUI", "output_pngs", "6.png")
        )

        # First scan
        while True:
            print(
                Fore.YELLOW + "         Step 1.21: " + Style.RESET_ALL + "Scan the QR code " + Fore.CYAN + "(1st scan)" + Style.RESET_ALL)
            femb_id_10 = input(Fore.YELLOW + '         >> ' + Style.RESET_ALL)
            if ("-1826-1" in femb_id_10) or ("-1865-1" in femb_id_10):
                break
            else:
                print(Fore.RED + "         ✗ No valid FEMB ID detected. Please try again." + Style.RESET_ALL)

        # Second scan
        while True:
            print(
                Fore.YELLOW + "         Step 1.22: " + Style.RESET_ALL + "Scan the QR code " + Fore.CYAN + "(2nd scan)" + Style.RESET_ALL)
            femb_id_11 = input(Fore.YELLOW + '         >> ' + Style.RESET_ALL)
            if ("-1826-1" in femb_id_11) or ("-1865-1" in femb_id_11):
                break
            else:
                print(Fore.RED + "         ✗ No valid FEMB ID detected. Please try again." + Style.RESET_ALL)

        if femb_id_11 == femb_id_10:
            print(Fore.GREEN + "         ✓ Top CE box QR ID recorded successfully" + Style.RESET_ALL)
            femb_id_1 = femb_id_11
        else:
            print(
                Fore.MAGENTA + '         ⚠️  QR codes do not match! Please scan a 3rd time and verify carefully.' + Style.RESET_ALL)

            while True:
                while True:
                    print("         Scan top QR code " + Fore.CYAN + "(3rd attempt - try 1):" + Style.RESET_ALL)
                    femb_id_2 = input(Fore.YELLOW + '         >> ' + Style.RESET_ALL)
                    if ("-1826-1" in femb_id_2) or ("-1865-1" in femb_id_2):
                        break
                    else:
                        print(Fore.RED + "         ✗ No valid FEMB ID detected. Please try again." + Style.RESET_ALL)

                while True:
                    print("         Scan top QR code " + Fore.CYAN + "(3rd attempt - try 2):" + Style.RESET_ALL)
                    femb_id_3 = input(Fore.YELLOW + '         >> ' + Style.RESET_ALL)
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

        femb_id_1 = femb_id_1.replace('/', '_')
        if "1826" in femb_id_1:
            version = "HD"
        else:
            version = "VD"

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

        if 'exit_outer' in locals() and exit_outer:
            break

    print(Fore.CYAN + "         Step 1.24: Continue assembly into top slot..." + Style.RESET_ALL)
    print("         Assembly instruction popup opening...")

    my_options = ["Install MiniSAS Cable and Clamp", "Install Test Cover", "Install Power Cable",
                  "Install Toy_TPCs and Cables", "Insert into Bottom Slot"]
    if version == "HD":
        pop01 = pop.show_image_popup(
            title="Top slot assembly instruction",
            image_path=os.path.join(ROOT_DIR, "GUI", "output_pngs", "10.png")
        )
    else:
        pop01 = pop.show_image_popup(
            title="Top slot assembly instruction",
            image_path=os.path.join(ROOT_DIR, "GUI", "output_pngs", "8.png")
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
        csv_data['SLOT0'] = femb_id_0
    if 'SLOT1' not in csv_data:
        csv_data['SLOT1'] = 'H02'
    else:
        csv_data['SLOT1'] = femb_id_1
    if 'SLOT2' not in csv_data:
        csv_data['SLOT2'] = ' '
    if 'SLOT3' not in csv_data:
        csv_data['SLOT3'] = ' '
    if 'test_site' not in csv_data:
        csv_data['test_site'] = 'BNL'
    if 'toy_TPC' not in csv_data:
        csv_data['toy_TPC'] = 'y'
    if 'comment' not in csv_data:
        csv_data['comment'] = 'QC test'
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
        image_path=os.path.join(ROOT_DIR, "GUI", "output_pngs", "11.png")
    )

    ### 20. Cable Connection
    print(Fore.CYAN + 'Opening cable connection instructions...' + Style.RESET_ALL)
    my_options = ["Open CTS Cover", "Place the CE boxes structure"]
    pop04 = pop.show_image_popup(
        title="WIB cable connection",
        image_path=os.path.join(ROOT_DIR, "GUI", "output_pngs", "12.png")
    )

    ### 21. Close CTS Cover
    print(Fore.CYAN + "Opening cover closing instructions..." + Style.RESET_ALL)
    my_options = ["Close the CTS Cover"]
    pop06 = pop.show_image_popup(
        title="Closing CTS cover",
        image_path=os.path.join(ROOT_DIR, "GUI", "output_pngs", "13.png")
    )

    ### 22. Copy configuration file to implementation file
    with open(csv_file, 'r') as source:
        with open(csv_file_implement, 'w') as destination:
            destination.write(source.read())

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

### 24. Send test start email notification
pre_info = cts.read_csv_to_dict(csv_file_implement, 'RT')
send_email.send_email(sender, password, receiver, "FEMB CE QC {}".format(pre_info['test_site']),
                      "FEMB QC start, stay tuned ...")

# ----------------------------------------------------------------------------
# Power Supply Initialization
# ----------------------------------------------------------------------------
### 25. Initialize power supply for warm/cold/final tests
if any(x in state_list for x in [3, 4, 5]):
    psu = rigol.RigolDP800()

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


    ### 30. Warm QC Completion
    print_separator()
    print_status('success', "Warm QC completed!")
    print_separator()
    send_email.send_email(
        sender, password, receiver,
        "FEMB CE QC {}".format('test_site'),
        '"Warm QC Done", "Switch to COLD for 5 min", "Switch to IMMENSE, wait for LN2 to reach Level 3", "Double confirm heat LED OFF"'
    )

    ### 31. Confirm WIB Power OFF
    while True:
        print(Fore.YELLOW + "⚠️  Please verify that WIB power is OFF" + Style.RESET_ALL)
        print('Type ' + Fore.GREEN + '"confirm"' + Style.RESET_ALL + ' to continue')
        com = input(Fore.YELLOW + '>> ' + Style.RESET_ALL)
        if com.lower() == 'confirm':
            print(Fore.GREEN + '✓ WIB power OFF confirmed' + Style.RESET_ALL)
            break

# ============================================================================
## PHASE 4: COLD QC TEST
# ============================================================================
# Skip if checkout failed in Phase 3
if 4 in state_list and not goto_disassembly:
    print_phase_header(4, 6, "Cold QC Test (LN₂)", "~90 min")

    ### 32. CTS Cool Down Procedure
    print_status('info', "Opening CTS cool down instructions...")
    pop.show_image_popup(
        title="CTS Cool Down – Power ON",
        image_path=os.path.join(ROOT_DIR, "GUI", "output_pngs", "14.png")
    )

    print(Fore.CYAN + "🌡️  Initiating CTS cool down procedure..." + Style.RESET_ALL)

    ### 33. LN2 Refill Wait Timer (30 min)
    timer_count(
        start_message="⏰ Wait for LN2 Refill!",
        exit_hint="Type 's' to stop",
        end_message="✅ Timer complete!",
        auto_exit_seconds=1800,
        exit_chars=['s', 'stop']
    )

    # Confirm LN2 Level
    print("\n" + Fore.CYAN + "=" * 70)
    print("  CTS COLD DOWN STATUS CHECK")
    print("=" * 70 + Style.RESET_ALL)
    print(Fore.YELLOW + "⚠️  Please ensure:" + Style.RESET_ALL)
    print("   • LN2 level has reached " + Fore.CYAN + "LEVEL 3" + Style.RESET_ALL)
    print("   • Heat LED is " + Fore.GREEN + "OFF" + Style.RESET_ALL)

    while True:
        print('\nType ' + Fore.GREEN + '"confirm"' + Style.RESET_ALL + ' once CTS is fully cooled down')
        com = input(Fore.YELLOW + '>> ' + Style.RESET_ALL)
        if com.lower() == 'confirm':
            print(Fore.GREEN + "✓ CTS cool down confirmed." + Style.RESET_ALL)
            break
        else:
            print(Fore.RED + "Not confirmed. Please verify conditions again." + Style.RESET_ALL)

    # Load Cold QC Info
    infoln = cts.read_csv_to_dict(csv_file_implement, 'LN')

    # Cold QC Action Selection
    while True:
        print("\n" + Fore.CYAN + "=" * 70)
        print("  OPTIONS:")
        print("=" * 70 + Style.RESET_ALL)
        print("  " + Fore.GREEN + "'y'" + Style.RESET_ALL + " - Start Cold QC")
        print("  " + Fore.YELLOW + "'s'" + Style.RESET_ALL + " - Skip Cold QC")
        print("  " + Fore.RED + "'e'" + Style.RESET_ALL + " - Exit test program")
        Next = input(Fore.YELLOW + '>> ' + Style.RESET_ALL)

        # Skip Cold QC
        if Next == 's':
            if confirm("Do you want to skip Cold QC?"):
                print(Fore.YELLOW + "⏩ Skipping Cold QC..." + Style.RESET_ALL)
                break

        # Exit Test and go to warm-up + disassembly
        elif Next == 'e':
            if confirm("Do you want to skip Cold QC and proceed to warm-up + disassembly?"):
                print(Fore.YELLOW + "Skipping Cold QC, will proceed to warm-up then disassembly..." + Style.RESET_ALL)
                goto_disassembly = True
                break

        # Start Cold QC
        elif Next == 'y':
            if confirm("Do you want to begin Cold QC?"):
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

                print_separator()
                print_step("FEMB Cold Quality Control Test", estimated_time="<30 min")
                lqdata_path, lqreport_path = QC_Process(path=infoln['QC_data_root_folder'], QC_TST_EN=3, input_info=infoln)

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
                print(Fore.CYAN + "Warm Up Begin, Send Notification Email!" + Style.RESET_ALL)
                send_email.send_email(
                    sender, password, receiver,
                    "FEMB CE QC {}".format(pre_info.get('test_site', 'Unknown')),
                    "Cold QC Done - Pass cold test is done, please perform the warm-up procedure"
                )
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

    # Warm Up CTS



    print(Fore.CYAN + "Opening CTS warm-up instructions..." + Style.RESET_ALL)
    pop.show_image_popup(
        title="CTS Warm-Up",
        image_path=os.path.join(ROOT_DIR, "GUI", "output_pngs", "15.png")
    )

    timer_count(
        start_message="⏰ Wait for warm up!",
        exit_hint="Type 's' to stop",
        end_message="✅ Timer complete!",
        auto_exit_seconds=3600,
        exit_chars=['s', 'stop']
    )

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
        print("\n" + Fore.CYAN + "OPTIONS:" + Style.RESET_ALL)
        print("  " + Fore.GREEN + "'y'" + Style.RESET_ALL + " - Continue with Final Checkout")
        print("  " + Fore.YELLOW + "'s'" + Style.RESET_ALL + " - Skip Final Checkout")
        print("  " + Fore.RED + "'e'" + Style.RESET_ALL + " - Exit test program")
        Next = input(Fore.YELLOW + '>> ' + Style.RESET_ALL)

        # Skip Final Checkout
        if Next == 's':
            if confirm("Do you want to skip the Final Checkout?"):
                print(Fore.YELLOW + "⏩ Skipping Final Checkout..." + Style.RESET_ALL)
                break

        # Exit
        elif Next == 'e':
            if confirm("Do you want to exit the test program?"):
                print(Fore.RED + "Exiting..." + Style.RESET_ALL)
                sys.exit()

        # Begin Phase 5
        elif Next == 'y':
            if not confirm("Do you want to begin the Final Checkout?"):
                continue

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
            print_status('warning', "IMPORTANT: Please power OFF the WIB!")

            # Auto/manual power off
            safe_power_off(psu)

            break

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
        image_path=os.path.join(ROOT_DIR, "GUI", "output_pngs", "16.png")
    )

    img_cebox = get_cebox_image(version, ROOT_DIR)

    ### 48. Disassemble Top CE Box
    print(Fore.CYAN + "Opening top CE box disassembly instructions..." + Style.RESET_ALL)
    pop.show_image_popup(
        title="Disassembly Top CE Box",
        image_path=img_cebox
    )

    ### 49. Disassemble Bottom CE Box
    print(Fore.CYAN + "Opening bottom CE box disassembly instructions..." + Style.RESET_ALL)
    pop.show_image_popup(
        title="Disassembly Bottom CE Box",
        image_path=img_cebox
    )

    ### 50. Accessory Return Confirmation
    while True:
        print(Fore.CYAN + "\nOpening accessory return instructions..." + Style.RESET_ALL)
        pop.show_image_popup(
            title="Return Accessories to Their Original Position",
            image_path=os.path.join(ROOT_DIR, "GUI", "output_pngs", "19.png")
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