import os
import sys
import time
import cts_ssh_FEMB as cts
import csv
import colorama
from colorama import Fore, Style
import GUI.pop_window as pop
import GUI.State_List as state
from email.mime.text import MIMEText
import GUI.Rigol_DP800 as rigol
import GUI.send_email as send_email
import psutil
import signal
from datetime import datetime

import os
import time

script = "CTS_Real_Time_Monitor.py"









ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

sender = "bnlr216@gmail.com"
password = "vvef tosp minf wwhf"
receiver = "lke@bnl.gov"

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

import threading
import time
import sys


def timer_thread(stop_event):
    """Timer thread that counts seconds"""
    seconds = 0
    while not stop_event.is_set():
        print(f"\rElapsed time: {seconds}s", end="", flush=True)
        time.sleep(1)
        seconds += 1
    print(f"\nTotal time: {seconds}s")


def timer_count(start_message="Timer started!",
         exit_hint="Type 'q' or 'quit' to exit",
         end_message="Timer stopped!",
         auto_exit_seconds=None,
         exit_chars=['q', 'quit']):
    """
    Customizable timer main function

    Args:
        start_message: Message displayed at start
        exit_hint: Exit instruction message
        end_message: Message displayed at end
        auto_exit_seconds: Seconds before auto-exit (None = no auto-exit)
        exit_chars: List of characters that trigger exit
    """
    print(start_message)
    if auto_exit_seconds:
        print(f"Will auto-exit after {auto_exit_seconds} seconds")
    print(exit_hint + "\n")

    # Create stop event
    stop_event = threading.Event()

    # Start timer thread
    timer = threading.Thread(target=timer_thread, args=(stop_event,))
    timer.daemon = True
    timer.start()

    # Track start time for auto-exit
    if auto_exit_seconds:
        start_time = time.time()

    # Wait for user input or auto-exit
    while True:
        # Check if auto-exit time reached
        if auto_exit_seconds and (time.time() - start_time >= auto_exit_seconds):
            stop_event.set()
            timer.join()
            print(f"\n{end_message} (time limit reached)")
            break

        # Check for user input (non-blocking)
        if sys.platform == 'win32':
            import msvcrt
            if msvcrt.kbhit():
                user_input = input().strip().lower()
                if user_input in exit_chars:
                    stop_event.set()
                    timer.join()
                    print(end_message)
                    break
        else:
            # Unix/Linux/Mac
            import select
            if select.select([sys.stdin], [], [], 0.1)[0]:
                user_input = input().strip().lower()
                if user_input in exit_chars:
                    stop_event.set()
                    timer.join()
                    print(end_message)
                    break

        time.sleep(0.1)  # Prevent high CPU usage


    # Example 3: Custom messages only, no auto-exit
    # main(
    #     start_message="Work session started...",
    #     exit_hint="Type 'done' when finished",
    #     end_message="Work session complete!",
    #     exit_chars=['done']
    # )
def check_fault_files(paths, show_p_files=False):
    """Check for fault files (_F_) and pass files (_P_) in test results."""
    f_files = []  # Files with _F_
    p_files = []  # Files with _P_
    for path in paths:
        if not os.path.isdir(path):
            continue
        for root, dirs, files in os.walk(path):
            for file in files:
                if "_F." in file:
                    f_files.append(os.path.join(root, file))
                elif "_F_S" in file:
                    f_files.append(os.path.join(root, file))
                elif "_P." in file:
                    p_files.append(os.path.join(root, file))
                elif "_P_S" in file:
                    p_files.append(os.path.join(root, file))
    s0 = True
    s1 = True
    s2 = True
    s3 = True
    # Found _F_ files → check for actual faults
    print(Fore.YELLOW + "\n⚠️  Fault files detected:" + Style.RESET_ALL)
    for ff in f_files:
        # print(f"  • {ff}")
        if 'Slot0' in ff:
            # print("Slot0 Failed the QC")
            s0 = False
            print(ff)
        if 'Slot1' in ff:
            # print("Slot1 Failed the QC")
            s1 = False
            print(ff)
        if 'Slot2' in ff:
            # print("Slot2 Failed the QC")
            s2 = False
            print(ff)
        if 'Slot3' in ff:
            # print("Slot3 Failed the QC")
            s3 = False
            print(ff)
    if s0:
        print(Fore.GREEN + "Bottom Slot0 FEMB {} Pass the QC".format(inform['SLOT0']) + Style.RESET_ALL)
    else:
        print(Fore.RED + "Bottom Slot0 FEMB {} Failed the QC".format(inform['SLOT0']) + Style.RESET_ALL)
    if s1:
        print(Fore.GREEN + "Top Slot1 FEMB {} Pass the QC".format(inform['SLOT1']) + Style.RESET_ALL)
    else:
        print(Fore.RED + "Top Slot1 FEMB {} Failed the QC".format(inform['SLOT1']) + Style.RESET_ALL)
    fault_found = False
    for ff in f_files:
        try:
            with open(ff, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                if "fault" in content.lower() or "error" in content.lower():
                    fault_found = True
                    break
        except Exception as e:
            print(Fore.RED + f"✗ Unable to read file: {ff}, Error: {e}" + Style.RESET_ALL)
    if show_p_files:
        print(Fore.CYAN + "\nPass files (_P_):" + Style.RESET_ALL)
        for pf in p_files:
            print(f"  • {pf}")
    # If no _F_ files → PASS
    if not f_files:
        print(Fore.GREEN + "\n" + "=" * 70)
        print("  TEST RESULT: PASS ✓")
        print("=" * 70 + Style.RESET_ALL)
        if show_p_files:
            print(Fore.CYAN + "\nPass files (_P.):" + Style.RESET_ALL)
            for pf in p_files:
                print(f"  • {pf}")
        return s0, s1

def QC_Process(path="D:", QC_TST_EN=None, input_info=None):
    global data_path, report_path
    while True:
        QCresult = cts.cts_ssh_FEMB(root="{}/FEMB_QC/".format(path), QC_TST_EN=QC_TST_EN, input_info=input_info)
        if QCresult != None:
            QCstatus = QCresult[0]
            badchips = QCresult[1]
            data_path = QCresult[2]
            report_path = QCresult[3]
            break
        else:
            print(Fore.RED + "⚠️  Issue detected!" + Style.RESET_ALL)
            print(Fore.YELLOW + "Enter '139' to terminate test" + Style.RESET_ALL)
            print(Fore.YELLOW + "Enter '2' to retest" + Style.RESET_ALL)
            send_email.send_email(sender, password, receiver, "Issue Found at {}".format(pre_info['test_site']),
                                  "Issue Found, Please Check the Detail")
            userinput = input(Fore.CYAN + "Please contact tech coordinator: " + Style.RESET_ALL)
            if len(userinput) > 0:
                if "139" in userinput:
                    QCstatus = "Terminate"
                    badchips = []
                    data_path = []
                    report_path = []
                    break
                elif "2" in userinput[0]:
                    print(Fore.GREEN + "Retesting..." + Style.RESET_ALL)
                    input("Press any key to start again...")
    return data_path, report_path


def confirm(prompt):
    """Simple confirmation - requires typing 'confirm' to continue"""
    while True:
        print(Fore.CYAN + prompt + Style.RESET_ALL)
        print('Type ' + Fore.GREEN + '"confirm"' + Style.RESET_ALL + ' to continue')
        com = input(Fore.YELLOW + '>> ' + Style.RESET_ALL)
        if com.lower() == "confirm":
            return True
        else:
            print(Fore.RED + "Invalid input. Please try again." + Style.RESET_ALL)
            break


def safe_power_off(psu, current_threshold=0.2, max_attempts=5):
    """
    Automatically power off WIB. Attempts up to max_attempts times.
    If current remains high, enters manual confirmation mode with current verification.
    """
    attempt = 0
    while True:
        time.sleep(1)
        # Measure current on both channels
        total_i = 0
        for ch in (1, 2):
            v, i = psu.measure(ch)
            print(f"  CH{ch}: {v:.3f} V, {i:.3f} A")
            total_i += i
        print(Fore.CYAN + f"  Total current: {total_i:.3f} A" + Style.RESET_ALL)

        # Attempt power off
        psu.turn_off_all()

        # Success
        if total_i < current_threshold:
            print(Fore.GREEN + "✓ Power OFF successful." + Style.RESET_ALL)
            return True

        # Failed → auto retry
        attempt += 1
        print(
            Fore.YELLOW + f"⚠️  Power off attempt {attempt}/{max_attempts} failed (current too high)." + Style.RESET_ALL)

        # Max attempts reached → manual intervention
        if attempt >= max_attempts:
            print(Fore.RED + "\n" + "=" * 60)
            print("⚠️  WARNING: AUTO POWER-OFF FAILED")
            print("    Manual power shutdown is REQUIRED!")
            print("=" * 60 + "\n" + Style.RESET_ALL)

            # Manual confirmation mode with verification
            while True:
                print(Fore.YELLOW + "Please manually turn OFF the WIB power supply." + Style.RESET_ALL)
                print('Type ' + Fore.GREEN + '"confirm"' + Style.RESET_ALL + ' after power is OFF')
                com = input(Fore.YELLOW + '>> ' + Style.RESET_ALL)
                if com.lower() == "confirm":
                    # Verify power is actually off
                    v1, i1 = psu.measure(1)
                    v2, i2 = psu.measure(2)
                    if (i1 + i2) < current_threshold:
                        print(Fore.GREEN + "✓ Manual power-off verified. Proceeding..." + Style.RESET_ALL)
                        return True
                    else:
                        print(
                            Fore.RED + f"✗ Verification failed: Current still high ({i1 + i2:.3f} A)" + Style.RESET_ALL)
                        print(Fore.YELLOW + "Please ensure power is completely OFF and try again." + Style.RESET_ALL)
                else:
                    print(Fore.RED + "Invalid input. Please type 'confirm'." + Style.RESET_ALL)

        print(Fore.CYAN + "Retrying auto power off...\n" + Style.RESET_ALL)


def FEMB_QC(input_info):
    print(Fore.CYAN + "⏱️  Waiting 30 seconds to enable Fiber Converter..." + Style.RESET_ALL)
    time.sleep(30)
    print(Fore.CYAN + "🔌 Pinging Warm Interface Board..." + Style.RESET_ALL)
    QC_Process(path=input_info['QC_data_root_folder'], QC_TST_EN=77, input_info=input_info)  # initial wib

    # C FEMB QC
    print(Fore.GREEN + "▶️  Starting FEMB Quality Control (estimated: <30 min)" + Style.RESET_ALL)
    QC_Process(path=input_info['QC_data_root_folder'], QC_TST_EN=0, input_info=input_info)  # initial wib
    QC_Process(path=input_info['QC_data_root_folder'], QC_TST_EN=1, input_info=input_info)  # initial FEMB I2C
    QC_Process(path=input_info['QC_data_root_folder'], QC_TST_EN=2, input_info=input_info)  # assembly checkout
    QC_Process(path=input_info['QC_data_root_folder'], QC_TST_EN=3, input_info=input_info)  # QC
    QC_Process(path=input_info['QC_data_root_folder'], QC_TST_EN=6, input_info=input_info)  # QC
    QC_Process(path=input_info['QC_data_root_folder'], QC_TST_EN=10, input_info=input_info)  # QC
    return 0


print(ROOT_DIR)
technician_csv = os.path.join(ROOT_DIR, "init_setup.csv")
csv_file = os.path.join(ROOT_DIR, "femb_info.csv")
csv_file_implement = os.path.join(ROOT_DIR, "femb_info_implement.csv")

version = "HD"

# Create empty CSV files if they don't exist
if not os.path.exists(technician_csv):
    with open(technician_csv, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['TechnicianID', 'Lingyun Ke'])
        writer.writerow(['test_site', 'BNL'])
        writer.writerow(['QC_data_root_folder', '/home/dune/'])
        writer.writerow(['Email', 'LKE@BNL.GOV'])
    print(Fore.GREEN + f"✓ Created and initialized: {technician_csv}" + Style.RESET_ALL)

if not os.path.exists(csv_file):
    open(csv_file, 'w').close()
    print(Fore.GREEN + f"✓ Created: {csv_file}" + Style.RESET_ALL)

if not os.path.exists(csv_file_implement):
    open(csv_file_implement, 'w').close()
    print(Fore.GREEN + f"✓ Created: {csv_file_implement}" + Style.RESET_ALL)

# Input Tester Name
print('\n')
print(Fore.CYAN + "=" * 60)
print("  WELCOME TO CTS COLD ELECTRONICS QC SYSTEM")
print("=" * 60 + Style.RESET_ALL)

input_name = input('Please enter your name:\n' + Fore.YELLOW + '>> ' + Style.RESET_ALL)


# # Kill old
# os.system(f'pkill -f "{script}"')
# time.sleep(1)
#
# # Run script, then keep shell open
# current_dir = os.path.dirname(os.path.abspath(__file__))
# os.system(f'gnome-terminal --working-directory="{current_dir}" -- bash -c "python3 {script}; exec bash" &')
#
# print(f"✓ Analysis Code Launched")

# Kill old
os.system(f'pkill -f "{script}"')
time.sleep(1)

# Run script in bottom-right corner
current_dir = os.path.dirname(os.path.abspath(__file__))
os.system(f'gnome-terminal --geometry=10x20-0-0 --working-directory="{current_dir}" -- bash -c "python3 {script}; exec bash" &')
print(f"✓ Analysis Code Launched")




# Email validation
def get_email():
    while True:
        email1 = input('Please enter your email address:\n'
                       + Fore.YELLOW + '>> ' + Style.RESET_ALL)

        email2 = input('Please enter again to confirm:\n'
                       + Fore.YELLOW + '>> ' + Style.RESET_ALL)

        # Check for @ symbol
        if "@" not in email1:
            print(Fore.RED + "✗ Invalid email: missing '@' symbol!" + Style.RESET_ALL)
            continue

        # Check if they match
        if email1 != email2:
            print(Fore.RED + "✗ Email addresses do not match. Please try again." + Style.RESET_ALL)
            continue

        # Both passed
        print(Fore.GREEN + "✓ Email confirmed!" + Style.RESET_ALL)
        return email1


receiver = get_email()

# Pop window 1: Initial Checkout List
pop.show_image_popup(
    title="Initial Checkout List Confirm",
    image_path=os.path.join(ROOT_DIR, "GUI", "output_pngs", "2.png")
)

# Pop window 2: Accessory tray #1
pop.show_image_popup(
    title="Checklist for accessory tray #1",
    image_path=os.path.join(ROOT_DIR, "GUI", "output_pngs", "3.png")
)

# Pop window 3: Accessory tray #2
pop.show_image_popup(
    title="Checklist for accessory tray #2",
    image_path=os.path.join(ROOT_DIR, "GUI", "output_pngs", "4.png")
)

# LN2 Refill Notification
hour = datetime.now().hour
if 1 <= hour <= 11:
    LN2 = '1800 [Morning shift]'
else:
    LN2 = '1200 [Afternoon shift]'

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

state_list = state.select_test_states()
print(Fore.CYAN + f"Selected test phases: {state_list}" + Style.RESET_ALL)

# Phase 1: Preparation
if 1 in state_list:
    print("\n" + Fore.CYAN + "=" * 70)
    print("  PHASE 1: PREPARATION")
    print("=" * 70 + Style.RESET_ALL + "\n")

    # Install Bottom CE box
    while True:
        print(
            Fore.CYAN + "Step 1.1: Assemble CE box in the " + Fore.YELLOW + "BOTTOM SLOT" + Fore.CYAN + " (Cable #1)" + Style.RESET_ALL)
        print("         Visual inspection popup opening...")

        my_options = ["Install MiniSAS Cable and Clamp", "Install Test Cover", "Install Power Cable",
                      "Install Toy_TPCs and Cables", "Insert into Bottom Slot"]
        pop01 = pop.show_image_popup(
            title="Bottom slot Visual Inspection",
            image_path=os.path.join(ROOT_DIR, "GUI", "output_pngs", "6.png")
        )

        # First scan
        while True:
            print(
                Fore.YELLOW + "         Step 1.11: " + Style.RESET_ALL + "Scan the QR code " + Fore.CYAN + "(1st scan)" + Style.RESET_ALL)
            femb_id_00 = input(Fore.YELLOW + '         >> ' + Style.RESET_ALL)
            if ("IO-1826-1" in femb_id_00) or ("IO-1865-1" in femb_id_00):
                break
            else:
                print(Fore.RED + "         ✗ No valid FEMB ID detected. Please try again." + Style.RESET_ALL)

        # Second scan
        while True:
            print(
                Fore.YELLOW + "         Step 1.12: " + Style.RESET_ALL + "Scan the QR code " + Fore.CYAN + "(2nd scan)" + Style.RESET_ALL)
            femb_id_01 = input(Fore.YELLOW + '         >> ' + Style.RESET_ALL)
            if ("IO-1826-1" in femb_id_01) or ("IO-1865-1" in femb_id_01):
                break
            else:
                print(Fore.RED + "         ✗ No valid FEMB ID detected. Please try again." + Style.RESET_ALL)

        if femb_id_01 == femb_id_00:
            print(Fore.GREEN + "         ✓ Bottom CE box QR ID recorded successfully" + Style.RESET_ALL)
            femb_id_0 = femb_id_01
        else:
            print(
                Fore.MAGENTA + '         ⚠️  QR codes do not match! Please scan a 3rd time and verify carefully.' + Style.RESET_ALL)
            while True:
                while True:
                    print("         Scan bottom QR code " + Fore.CYAN + "(3rd attempt - try 1):" + Style.RESET_ALL)
                    femb_id_2 = input(Fore.YELLOW + '         >> ' + Style.RESET_ALL).strip()
                    if ("IO-1826-1" in femb_id_2) or ("IO-1865-1" in femb_id_2):
                        break
                    else:
                        print(Fore.RED + "         ✗ No valid FEMB ID detected. Please try again." + Style.RESET_ALL)

                while True:
                    print("         Scan bottom QR code " + Fore.CYAN + "(3rd attempt - try 2):" + Style.RESET_ALL)
                    femb_id_3 = input(Fore.YELLOW + '         >> ' + Style.RESET_ALL).strip()
                    if ("IO-1826-1" in femb_id_3) or ("IO-1865-1" in femb_id_3):
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

        femb_id_0 = femb_id_0.replace('/', '_')
        if "1826" in femb_id_0:
            version = "HD"
        else:
            version = "VD"

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

    print(Fore.CYAN + "         Step 1.14: Continue assembly into bottom slot..." + Style.RESET_ALL)
    print("         Assembly instruction popup opening...")

    my_options = ["Install MiniSAS Cable and Clamp", "Install Test Cover", "Install Power Cable",
                  "Install Toy_TPCs and Cables", "Insert into Bottom Slot"]
    if version == "VD":
        pop01 = pop.show_image_popup(
            title="Bottom slot assembly instruction",
            image_path=os.path.join(ROOT_DIR, "GUI", "output_pngs", "7.png")
        )
    else:
        pop01 = pop.show_image_popup(
            title="Bottom slot assembly instruction",
            image_path=os.path.join(ROOT_DIR, "GUI", "output_pngs", "9.png")
        )
    confirm("Please Confirm the CE is install in the Bottom Slot")

    # Install Top CE box
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
            if ("IO-1826-1" in femb_id_10) or ("IO-1865-1" in femb_id_10):
                break
            else:
                print(Fore.RED + "         ✗ No valid FEMB ID detected. Please try again." + Style.RESET_ALL)

        # Second scan
        while True:
            print(
                Fore.YELLOW + "         Step 1.22: " + Style.RESET_ALL + "Scan the QR code " + Fore.CYAN + "(2nd scan)" + Style.RESET_ALL)
            femb_id_11 = input(Fore.YELLOW + '         >> ' + Style.RESET_ALL)
            if ("IO-1826-1" in femb_id_11) or ("IO-1865-1" in femb_id_11):
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
                    if ("IO-1826-1" in femb_id_2) or ("IO-1865-1" in femb_id_2):
                        break
                    else:
                        print(Fore.RED + "         ✗ No valid FEMB ID detected. Please try again." + Style.RESET_ALL)

                while True:
                    print("         Scan top QR code " + Fore.CYAN + "(3rd attempt - try 2):" + Style.RESET_ALL)
                    femb_id_3 = input(Fore.YELLOW + '         >> ' + Style.RESET_ALL)
                    if ("IO-1826-1" in femb_id_3) or ("IO-1865-1" in femb_id_3):
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

    inform = cts.read_csv_to_dict(csv_file, 'RT')

# Phase 2: Connect with CTS
if 2 in state_list:
    # Check CTS Chamber
    while True:
        print(Fore.YELLOW + "\n⚠️  SAFETY CHECK:" + Style.RESET_ALL)
        print("Please confirm the CTS chamber is empty.")
        print("Type " + Fore.GREEN + "'I confirm the chamber is empty'" + Style.RESET_ALL + " to proceed")
        com = input(Fore.YELLOW + '>> ' + Style.RESET_ALL)
        if com.lower() == 'i confirm the chamber is empty':
            print(
                Fore.GREEN + '✓ Chamber confirmed empty. Please install the CE test structure into CTS.' + Style.RESET_ALL)
            break

    # Connect the Cables
    print(Fore.CYAN + '\nOpening installation instructions...' + Style.RESET_ALL)
    my_options = ["Open CTS Cover", "Place the CE boxes structure"]
    pop04 = pop.show_image_popup(
        title="Placing CE boxes into crate",
        image_path=os.path.join(ROOT_DIR, "GUI", "output_pngs", "11.png")
    )

    # Cable connection
    print(Fore.CYAN + 'Opening cable connection instructions...' + Style.RESET_ALL)
    my_options = ["Open CTS Cover", "Place the CE boxes structure"]
    pop04 = pop.show_image_popup(
        title="WIB cable connection",
        image_path=os.path.join(ROOT_DIR, "GUI", "output_pngs", "12.png")
    )

    # Close the Cover
    print(Fore.CYAN + "Opening cover closing instructions..." + Style.RESET_ALL)
    my_options = ["Close the CTS Cover"]
    pop06 = pop.show_image_popup(
        title="Closing CTS cover",
        image_path=os.path.join(ROOT_DIR, "GUI", "output_pngs", "13.png")
    )

    with open(csv_file, 'r') as source:
        with open(csv_file_implement, 'w') as destination:
            destination.write(source.read())

else:
    # Load Record CSV directly
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

pre_info = cts.read_csv_to_dict(csv_file_implement, 'RT')
send_email.send_email(sender, password, receiver, "FEMB CE QC {}".format(pre_info['test_site']),
                      "FEMB QC start, stay tuned ...")

# Initialize power supply for warm/cold/final tests
if any(x in state_list for x in [3, 4, 5]):
    psu = rigol.RigolDP800()

# Phase 3: Warm QC Test
if 3 in state_list:
    inform = cts.read_csv_to_dict(csv_file_implement, 'RT')
    while True:
        print("\n" + Fore.CYAN + "=" * 70)
        print("  OPTIONS:")
        print("=" * 70 + Style.RESET_ALL)
        print("  " + Fore.GREEN + "'y'" + Style.RESET_ALL + " - Continue with Warm QC")
        print("  " + Fore.YELLOW + "'s'" + Style.RESET_ALL + " - Skip Warm QC (proceed directly to Cold)")
        print("  " + Fore.RED + "'e'" + Style.RESET_ALL + " - Exit test program")
        Next = input(Fore.YELLOW + '>> ' + Style.RESET_ALL)

        # Skip warm test
        if Next == 's':
            if confirm("Do you want to skip the Warm QC?"):
                print(Fore.YELLOW + "⏩ Skipping Warm QC..." + Style.RESET_ALL)
                break

        # Exit
        elif Next == 'e':
            if confirm("Do you want to exit the test program?"):
                print(Fore.RED + "Exiting QC program..." + Style.RESET_ALL)
                sys.exit()

        # Begin warm QC
        elif Next == 'y':
            if confirm("Do you want to begin the Warm QC?"):
                print("\n" + Fore.CYAN + "=" * 70)
                print("  PHASE 3: WARM QC")
                print("=" * 70 + Style.RESET_ALL + "\n")

                # Power on WIB
                print(Fore.GREEN + "⚡ Powering ON WIB..." + Style.RESET_ALL)
                psu.set_channel(1, 12.0, 3.0, on=True)
                psu.set_channel(2, 12.0, 3.0, on=True)
                print(Fore.CYAN + "⏱️  Establishing Ethernet communication (35 seconds)..." + Style.RESET_ALL)
                time.sleep(35)

                # Ping WIB
                print(Fore.CYAN + "🔌 Pinging WIB..." + Style.RESET_ALL)
                QC_Process(path=inform['QC_data_root_folder'], QC_TST_EN=77, input_info=inform)
                print(Fore.GREEN + '✓ Activating next group' + Style.RESET_ALL)
                terminal_path = os.path.join(ROOT_DIR, "CTS_FEMB_QC_top.py")

                # WIB Initial
                print(Fore.CYAN + "▶️  Step C1: WIB initialization (estimated: <2 min)" + Style.RESET_ALL)
                QC_Process(path=inform['QC_data_root_folder'], QC_TST_EN=0, input_info=inform)
                QC_Process(path=inform['QC_data_root_folder'], QC_TST_EN=1, input_info=inform)

                # Warm Checkout
                print(Fore.CYAN + "▶️  Step C2: FEMB checkout (estimated: <3 min)" + Style.RESET_ALL)
                wcdata_path, wcreport_path = QC_Process(path=inform['QC_data_root_folder'], QC_TST_EN=2, input_info=inform)

                # Warm QC Test
                print(Fore.CYAN + "▶️  Step C3: FEMB quality control (estimated: <30 min)" + Style.RESET_ALL)
                wqdata_path, wqreport_path = QC_Process(path=inform['QC_data_root_folder'], QC_TST_EN=3, input_info=inform)

                # Close WIB Linux
                print(Fore.CYAN + "🔄 Shutting down WIB Linux system..." + Style.RESET_ALL)
                QC_Process(path=inform['QC_data_root_folder'], QC_TST_EN=6, input_info=inform)

                # Power off WIB
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
                    else:
                        print(
                            Fore.YELLOW + '⚠️  High current detected, attempting power off again...' + Style.RESET_ALL)


                # Check Result
            time.sleep(2)
            paths = [
                wcdata_path, wcreport_path, wqdata_path, wqreport_path
            ]
            # print(paths)






    print("\n" + Fore.GREEN + "✓ Warm QC completed!" + Style.RESET_ALL)
    print("-" * 70 + "\n")
    send_email.send_email(
        sender, password, receiver,
        "FEMB CE QC {}".format('test_site'),
        '"Warm QC Done", "Switch to COLD for 5 min", "Switch to IMMENSE, wait for LN2 to reach Level 3", "Double confirm heat LED OFF"'
    )

    # Confirm power is off
    while True:
        print(Fore.YELLOW + "⚠️  Please verify that WIB power is OFF" + Style.RESET_ALL)
        print('Type ' + Fore.GREEN + '"confirm"' + Style.RESET_ALL + ' to continue')
        com = input(Fore.YELLOW + '>> ' + Style.RESET_ALL)
        if com.lower() == 'confirm':
            print(Fore.GREEN + '✓ WIB power OFF confirmed' + Style.RESET_ALL)
            break

# Phase 4: Cold QC Test
if 4 in state_list:

    # CTS Cool Down
    print("\n" + Fore.CYAN + "Opening CTS cool down instructions..." + Style.RESET_ALL)
    pop.show_image_popup(
        title="CTS Cool Down – Power ON",
        image_path=os.path.join(ROOT_DIR, "GUI", "output_pngs", "14.png")
    )

    print(Fore.CYAN + "🌡️  Initiating CTS cool down procedure..." + Style.RESET_ALL)


    timer_count(
        start_message="⏰ Wait for LN2 Refill!",
        exit_hint="Type 's' to stop",
        end_message="✅ Timer complete!",
        auto_exit_seconds=1800,
        exit_chars=['s', 'stop']
    )
    # Wait for LN2 refill
    # while True:
    #     print(Fore.CYAN + "\nDoes the system need to wait for LN2 refill?" + Style.RESET_ALL)
    #     print(
    #         "Enter " + Fore.GREEN + "'y'" + Style.RESET_ALL + " (yes) or " + Fore.RED + "'n'" + Style.RESET_ALL + " (no)")
    #     do_sleep = input(Fore.YELLOW + '>> ' + Style.RESET_ALL).lower()
    #
    #     if do_sleep == 'y':
    #         if confirm("Confirm 30-minute wait for CTS cool down?"):
    #             print(Fore.CYAN + "⏱️  Waiting 30 minutes for CTS to cool down..." + Style.RESET_ALL)
    #             time.sleep(1800)
    #             print("Send Notification Email")
    #             send_email.send_email(
    #                 sender, password, receiver,
    #                 f"CTS cold down completed [{pre_info['test_site']}]",
    #                 '"Please double confirm LN2 reach Level 3, heat LED OFF"'
    #             )
    #             break
    #
    #     elif do_sleep == 'n':
    #         if confirm("Confirm skip waiting period?"):
    #             print(Fore.YELLOW + "⏩ Skipping wait period..." + Style.RESET_ALL)
    #             break

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

        # Exit Test
        elif Next == 'e':
            if confirm("Do you want to exit?"):
                print(Fore.RED + "Exiting QC program..." + Style.RESET_ALL)
                sys.exit()

        # Start Cold QC
        elif Next == 'y':
            if confirm("Do you want to begin Cold QC?"):
                print("\n" + Fore.CYAN + "=" * 70)
                print("  PHASE 4: COLD FEMB QUALITY CONTROL")
                print("=" * 70 + Style.RESET_ALL + "\n")

                # Power ON WIB
                print(Fore.GREEN + "⚡ Powering ON WIB..." + Style.RESET_ALL)
                psu.set_channel(1, 12.0, 3.0, on=True)
                psu.set_channel(2, 12.0, 3.0, on=True)
                print(Fore.CYAN + "⏱️  Initializing ethernet link (35 seconds)..." + Style.RESET_ALL)
                time.sleep(35)

                # Cold QC Steps
                print(Fore.CYAN + "🔌 Pinging WIB..." + Style.RESET_ALL)
                QC_Process(path=infoln['QC_data_root_folder'], QC_TST_EN=77, input_info=infoln)

                print(Fore.CYAN + "▶️  Step C1: WIB initialization (estimated: <2 min)" + Style.RESET_ALL)
                QC_Process(path=infoln['QC_data_root_folder'], QC_TST_EN=0, input_info=infoln)
                QC_Process(path=infoln['QC_data_root_folder'], QC_TST_EN=1, input_info=infoln)

                print(Fore.CYAN + "▶️  Step C2: FEMB cold checkout (estimated: <3 min)" + Style.RESET_ALL)
                lcdata_path, lcreport_path = QC_Process(path=infoln['QC_data_root_folder'], QC_TST_EN=2, input_info=infoln)

                print(Fore.CYAN + "▶️  Step C3: FEMB cold QC (estimated: <30 min)" + Style.RESET_ALL)
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

                print("\n" + Fore.GREEN + "✓ Cold QC completed!" + Style.RESET_ALL + "\n")
                break

    # Warm Up CTS
    time.sleep(10)

    print("Warm Up Begin, Send Notification Email!")
    send_email.send_email(
        sender, password, receiver,
        "FEMB CE QC {}".format('test_site'),
        "Cold QC Done"
    )

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
    # while True:
    #     print(Fore.CYAN + "\nDo you want to wait 60 minutes for warm-up?" + Style.RESET_ALL)
    #     print(
    #         "Enter " + Fore.GREEN + "'y'" + Style.RESET_ALL + " (yes) or " + Fore.RED + "'n'" + Style.RESET_ALL + " (no)")
    #     do_sleep = input(Fore.YELLOW + '>> ' + Style.RESET_ALL).lower()
    #
    #     if do_sleep == 'y':
    #         if confirm("Confirm 60-minute warm-up timer?"):
    #             print(Fore.CYAN + "⏱️  Warming up (60 minutes)..." + Style.RESET_ALL)
    #             time.sleep(3600)
    #             break
    #     elif do_sleep == 'n':
    #         if confirm("Confirm skip warm-up?"):
    #             print(Fore.YELLOW + "⏩ Skipping warm-up period..." + Style.RESET_ALL)
    #             break

    # send_email.send_email(
    #     sender, password, receiver,
    #     f"CTS Warm-Up Completed [{pre_info['test_site']}]",
    #     "Please proceed to Final Checkout."
    # )

# Phase 5: Final Checkout
if 5 in state_list:
    print("\n" + Fore.CYAN + "=" * 70)
    print("  PHASE 5: FEMB FINAL CHECKOUT")
    print("  (Estimated: <5 min)")
    print("=" * 70 + Style.RESET_ALL)
    inform = cts.read_csv_to_dict(csv_file_implement, 'RT')

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

            print("\n" + Fore.CYAN + "=" * 70)
            print("  PHASE 5: POST-QC CHECKOUT")
            print("=" * 70 + Style.RESET_ALL + "\n")

            # Power on WIB
            print(Fore.GREEN + "⚡ Powering ON WIB..." + Style.RESET_ALL)
            psu.set_channel(1, 12.0, 3.0, on=True)
            psu.set_channel(2, 12.0, 3.0, on=True)

            print(Fore.CYAN + "⏱️  Establishing Ethernet communication (35 seconds)..." + Style.RESET_ALL)
            time.sleep(35)

            # Ping WIB
            print(Fore.CYAN + "🔌 Pinging WIB..." + Style.RESET_ALL)
            QC_Process(path=inform['QC_data_root_folder'], QC_TST_EN=77, input_info=inform)

            # WIB Initial
            print(Fore.CYAN + "▶️  Step C1: WIB initialization (estimated: <2 min)" + Style.RESET_ALL)
            QC_Process(path=inform['QC_data_root_folder'], QC_TST_EN=0, input_info=inform)
            QC_Process(path=inform['QC_data_root_folder'], QC_TST_EN=1, input_info=inform)

            # FEMB Checkout
            print(Fore.CYAN + "▶️  Step C2: FEMB checkout (estimated: <3 min)" + Style.RESET_ALL)
            fcdata_path, fcreport_path = QC_Process(
                path=inform['QC_data_root_folder'], QC_TST_EN=5, input_info=inform
            )

            # Final QC
            print(Fore.CYAN + "▶️  Step C3: Final quality control (estimated: <30 min)" + Style.RESET_ALL)
            QC_Process(path=inform['QC_data_root_folder'], QC_TST_EN=6, input_info=inform)

            # Finish
            print("\n" + Fore.MAGENTA + "=" * 70)
            print("  ✓ FINAL CHECKOUT COMPLETED!")
            print("=" * 70 + Style.RESET_ALL)
            print(Fore.YELLOW + "\n⚠️  IMPORTANT: Please power OFF the WIB!\n" + Style.RESET_ALL)

            # Auto/manual power off
            safe_power_off(psu)

            break

# Phase 6: Disassembly
if 6 in state_list:

    print("\n" + Fore.CYAN + "=" * 70)
    print("  PHASE 6: DISASSEMBLY")
    print("=" * 70 + Style.RESET_ALL)
    print(Fore.YELLOW + "\n⚠️  Please:" + Style.RESET_ALL)
    print("   • Power OFF the CTS")
    print("   • Remove and disassemble the FEMB CE boxes\n")

    # Pop16
    print(Fore.CYAN + "Opening removal instructions..." + Style.RESET_ALL)
    pop.show_image_popup(
        title="Move CE boxes out of chamber",
        image_path=os.path.join(ROOT_DIR, "GUI", "output_pngs", "16.png")
    )


    # Helper function
    def get_cebox_image(version):
        """Return image path for CE box disassembly based on VD/HD."""
        return os.path.join(
            ROOT_DIR, "GUI", "output_pngs",
            "17.png" if version == "VD" else "18.png"
        )


    img_cebox = get_cebox_image(version)

    # Pop17
    print(Fore.CYAN + "Opening top CE box disassembly instructions..." + Style.RESET_ALL)
    pop.show_image_popup(
        title="Disassembly Top CE Box",
        image_path=img_cebox
    )

    # Pop18
    print(Fore.CYAN + "Opening bottom CE box disassembly instructions..." + Style.RESET_ALL)
    pop.show_image_popup(
        title="Disassembly Bottom CE Box",
        image_path=img_cebox
    )

    # Pop19
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

if any(x in state_list for x in [3, 4, 5]):
    psu.close()

print("\n" + Fore.GREEN + "=" * 70)
print("  ✓ QC TEST CYCLE COMPLETED!")
print("=" * 70 + Style.RESET_ALL)
print(Fore.CYAN + "\nPlease prepare for the next test cycle.\n" + Style.RESET_ALL)


# Check Result
time.sleep(2)

paths = [
    wcdata_path, wcreport_path, wqdata_path, wqreport_path,
    lcdata_path, lcreport_path, lqdata_path, lqreport_path,
    fcdata_path, fcreport_path
]

# print(paths)

check = confirm("do you want to check result")

if check:
    check_fault_files(paths, show_p_files=False)

    # exit terminal


    confirm("Please Record the Test Result")

confirm("Please Close The CTS, then, exit ...")

def close_terminal():
    """Close the terminal window after test completion."""
    p = psutil.Process(os.getpid())

    while True:
        parent = p.parent()
        if parent is None:
            break

        if parent.name() in ["gnome-terminal-server", "gnome-terminal", "konsole", "xfce4-terminal"]:
            os.kill(parent.pid, signal.SIGTERM)
            break

        p = parent

if __name__ == "__main__":
    print(Fore.CYAN + "Process ongoing..." + Style.RESET_ALL)
    print(Fore.GREEN + "✓ Completed. Closing window..." + Style.RESET_ALL)
    time.sleep(1)
    close_terminal()