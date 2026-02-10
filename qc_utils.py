"""
QC Utility Functions
Contains general-purpose utility functions for the FEMB QC system
"""

import os
import sys
import time
import threading
import json
import colorama
from colorama import Fore, Style
import cts_ssh_FEMB as cts
import GUI.send_email as send_email

colorama.init()

# Shared path file for communication between CTS_FEMB_QC_top.py and CTS_Real_Time_Monitor.py
QC_PATHS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'current_qc_paths.json')


def save_qc_paths(data_path, report_path, qc_type="QC"):
    """
    Save current QC paths to a shared JSON file.
    Called by CTS_FEMB_QC_top.py after QC_Process returns.

    Args:
        data_path: Path to the data directory
        report_path: Path to the report directory
        qc_type: Type of QC test ("Warm", "Cold", "Checkout", etc.)
    """
    try:
        paths_data = {}
        if os.path.exists(QC_PATHS_FILE):
            with open(QC_PATHS_FILE, 'r') as f:
                paths_data = json.load(f)

        paths_data[qc_type] = {
            'data_path': data_path,
            'report_path': report_path,
            'timestamp': time.time()
        }

        # Also store as 'latest' for easy access
        paths_data['latest'] = {
            'data_path': data_path,
            'report_path': report_path,
            'qc_type': qc_type,
            'timestamp': time.time()
        }

        with open(QC_PATHS_FILE, 'w') as f:
            json.dump(paths_data, f, indent=2)

        print(Fore.CYAN + f"  [QC Paths] Saved {qc_type} paths to shared file" + Style.RESET_ALL)
    except Exception as e:
        print(Fore.YELLOW + f"  [QC Paths] Warning: Could not save paths: {e}" + Style.RESET_ALL)


def load_qc_paths(qc_type=None):
    """
    Load QC paths from the shared JSON file.
    Called by CTS_Real_Time_Monitor.py to get the correct report path.

    Args:
        qc_type: Type of QC test to load, or None for latest

    Returns:
        tuple: (data_path, report_path) or (None, None) if not found
    """
    try:
        if not os.path.exists(QC_PATHS_FILE):
            return None, None

        with open(QC_PATHS_FILE, 'r') as f:
            paths_data = json.load(f)

        if qc_type and qc_type in paths_data:
            return paths_data[qc_type].get('data_path'), paths_data[qc_type].get('report_path')
        elif 'latest' in paths_data:
            return paths_data['latest'].get('data_path'), paths_data['latest'].get('report_path')
        else:
            return None, None
    except Exception as e:
        print(f"  [QC Paths] Warning: Could not load paths: {e}")
        return None, None


def get_report_path_for_data_path(data_path):
    """
    Get the report path corresponding to a data path from the shared file.

    Args:
        data_path: The data path to match

    Returns:
        str: The report path, or None if not found
    """
    try:
        if not os.path.exists(QC_PATHS_FILE):
            return None

        with open(QC_PATHS_FILE, 'r') as f:
            paths_data = json.load(f)

        # Search for matching data_path
        for key, value in paths_data.items():
            if isinstance(value, dict) and value.get('data_path') == data_path:
                return value.get('report_path')

        return None
    except Exception as e:
        print(f"  [QC Paths] Warning: Could not get report path: {e}")
        return None


def timer_thread(stop_event):
    """Timer thread that counts seconds"""
    seconds = 0
    while not stop_event.is_set():
        print(f"\rElapsed time: {seconds}s", end="", flush=True)
        time.sleep(1)
        seconds += 1
    print(f"\nTotal time: {seconds}s")


def countdown_timer(total_seconds, message="Waiting", allow_skip=True):
    """
    Display a countdown timer with animation and optional skip feature.

    Args:
        total_seconds: Total time to count down in seconds
        message: Message to display during countdown
        allow_skip: If True, user can press 'j' to skip

    Returns:
        bool: True if completed normally, False if skipped
    """
    import select

    spinner = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    spinner_idx = 0

    print(Fore.CYAN + f"\n{'='*70}" + Style.RESET_ALL)
    print(Fore.YELLOW + f"  {message}" + Style.RESET_ALL)
    if allow_skip:
        print(Fore.CYAN + f"  Press 'j' to skip wait" + Style.RESET_ALL)
    print(Fore.CYAN + f"{'='*70}\n" + Style.RESET_ALL)

    start_time = time.time()

    while True:
        elapsed = time.time() - start_time
        remaining = total_seconds - elapsed

        if remaining <= 0:
            # Completed
            print(f"\r{Fore.GREEN}✓ Wait complete!{' '*60}{Style.RESET_ALL}")
            print()
            return True

        # Format time display
        mins, secs = divmod(int(remaining), 60)
        hours, mins = divmod(mins, 60)

        if hours > 0:
            time_str = f"{hours:02d}:{mins:02d}:{secs:02d}"
        else:
            time_str = f"{mins:02d}:{secs:02d}"

        # Progress bar
        progress = (elapsed / total_seconds) * 100
        bar_length = 40
        filled = int(bar_length * progress / 100)
        bar = '█' * filled + '░' * (bar_length - filled)

        # Display with spinner
        print(f"\r{Fore.CYAN}{spinner[spinner_idx]} {Fore.YELLOW}[{bar}] {progress:5.1f}% "
              f"{Fore.GREEN}{time_str} remaining{Style.RESET_ALL}",
              end="", flush=True)

        spinner_idx = (spinner_idx + 1) % len(spinner)

        # Check for user input to skip (non-blocking)
        if allow_skip:
            if sys.platform == 'win32':
                import msvcrt
                if msvcrt.kbhit():
                    key = msvcrt.getch().decode('utf-8', errors='ignore').lower()
                    if key == 'j':
                        print(f"\r{Fore.YELLOW}⚠️  Skipped by user{' '*60}{Style.RESET_ALL}")
                        print()
                        return False
            else:
                # Unix/Linux/Mac
                if select.select([sys.stdin], [], [], 0)[0]:
                    key = sys.stdin.read(1).lower()
                    if key == 'j':
                        print(f"\r{Fore.YELLOW}⚠️  Skipped by user{' '*60}{Style.RESET_ALL}")
                        print()
                        return False

        time.sleep(0.1)


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


def check_fault_files(paths, show_p_files=False, inform=None, time_limit_hours=None):
    """
    Check for fault files (_F_) and pass files (_P_) in test results.

    Args:
        paths: List of directories to check
        show_p_files: If True, display pass files
        inform: FEMB information dictionary
        time_limit_hours: Optional time filter (None = check all files in provided paths)
    """
    import time

    # Calculate time threshold if specified
    time_threshold = 0
    if time_limit_hours is not None:
        time_threshold = time.time() - (time_limit_hours * 3600)

    f_files = []  # Files with _F_
    p_files = []  # Files with _P_
    for path in paths:
        if path is None or not os.path.isdir(path):
            continue
        for root, dirs, files in os.walk(path):
            for file in files:
                file_path = os.path.join(root, file)

                # Apply time filter if specified
                if time_limit_hours is not None:
                    try:
                        file_mtime = os.path.getmtime(file_path)
                        if file_mtime < time_threshold:
                            continue
                    except OSError:
                        continue

                if "_F." in file:
                    f_files.append(file_path)
                elif "_F_S" in file:
                    f_files.append(file_path)
                elif "_P." in file:
                    p_files.append(file_path)
                elif "_P_S" in file:
                    p_files.append(file_path)

    s0 = True
    s1 = True
    s2 = True
    s3 = True

    if len(f_files) > 0:
        print(Fore.YELLOW + "\n⚠️  Fault files detected:" + Style.RESET_ALL)
        # Print all fault files with proper formatting
        for ff in f_files:
            print(Fore.RED + f"  ✗ {ff}" + Style.RESET_ALL)
    else:
        print(Fore.GREEN + "\n✓ No fault files detected" + Style.RESET_ALL)

    # Check slot status
    for ff in f_files:
        if 'S0' in ff:
            s0 = False
        if 'S1' in ff:
            s1 = False
        if 'S2' in ff:
            s2 = False
        if 'S3' in ff:
            s3 = False

    if inform:
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

    return s0, s1


def check_checkout_result(data_path, report_path):
    """
    Check if checkout test passed by looking for fault files

    Returns:
        bool: True if passed (no fault files), False if failed
    """
    if not data_path or not report_path:
        return False

    paths = [data_path, report_path] if isinstance(data_path, str) else [data_path, report_path]

    # Look for fault files
    for path in paths:
        if not os.path.isdir(path):
            continue
        for root, dirs, files in os.walk(path):
            for file in files:
                if "_F." in file or "_F_S" in file:
                    return False  # Found fault file

    return True  # No fault files found


def QC_Process(path="D:", QC_TST_EN=None, input_info=None, pre_info=None):
    """Execute QC process and handle errors"""
    sender = "bnlr216@gmail.com"
    password = "vvef tosp minf wwhf"
    receiver = pre_info.get('Email', 'lke@bnl.gov') if pre_info else 'lke@bnl.gov'

    email_info = {'sender': sender, 'password': password, 'receiver': receiver}

    while True:
        QCresult = cts.cts_ssh_FEMB(root="{}/FEMB_QC/".format(path), QC_TST_EN=QC_TST_EN, input_info=input_info, email_info=email_info)
        if QCresult != None:
            QCstatus = QCresult[0]
            badchips = QCresult[1]
            data_path = QCresult[2]
            report_path = QCresult[3]

            # Handle critical current failure
            if QCstatus == "CRITICAL_CURRENT_FAILURE":
                print(Fore.RED + "\n" + "=" * 70)
                print("  ⛔ CRITICAL CURRENT FAILURE - TEST SKIPPED")
                print("=" * 70 + Style.RESET_ALL)
                print(Fore.RED + f"  Failed slots: {badchips}" + Style.RESET_ALL)
                print(Fore.YELLOW + "\n  Please check FEMB hardware and connections before retesting." + Style.RESET_ALL)

                test_site = 'Unknown'
                if input_info:
                    test_site = input_info.get('test_site', 'Unknown')
                elif pre_info:
                    test_site = pre_info.get('test_site', 'Unknown')
                failed_slots_str = ', '.join([f'SLOT#{s}' for s in badchips])
                send_email.send_email(sender, password, receiver,
                                     f"CRITICAL: FEMB Current Failure at {test_site}",
                                     f"Critical current failure detected.\nFailed slots: {failed_slots_str}\n\nTest skipped. Please check FEMB hardware and connections.\n\nTest Root Path: {path}\nScript: {os.path.basename(__file__)} (called by CTS_FEMB_QC_top.py)")

                # Return None paths to indicate skip
                return None, None

            # Handle cable test failure (cold mode: 2+ slots failed)
            if QCstatus == "CABLE_TEST_FAILURE":
                print(Fore.RED + "\n" + "=" * 70)
                print("  CABLE TEST FAILURE - CHECKOUT AND QC SKIPPED")
                print("=" * 70 + Style.RESET_ALL)
                print(Fore.RED + f"  Failed slots: {badchips}" + Style.RESET_ALL)
                print(Fore.YELLOW + "\n  Please check data cable connections before retesting." + Style.RESET_ALL)

                # Return None paths to indicate skip
                return None, None

            break
        else:
            print(Fore.RED + "⚠️  Issue detected!" + Style.RESET_ALL)
            print(Fore.YELLOW + "Enter '139' to terminate test" + Style.RESET_ALL)
            print(Fore.YELLOW + "Enter '2' to retest" + Style.RESET_ALL)

            issue_test_site = 'Unknown'
            if input_info:
                issue_test_site = input_info.get('test_site', 'Unknown')
            elif pre_info:
                issue_test_site = pre_info.get('test_site', 'Unknown')
            send_email.send_email(sender, password, receiver,
                                 "Issue Found at {}".format(issue_test_site),
                                 f"Issue Found, Please Check the Detail\n\nTest Data Path: {data_path}\nTest Report Path: {report_path}\nScript: {os.path.basename(__file__)} (called by CTS_FEMB_QC_top.py)")

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


def close_terminal():
    """Close the terminal window after test completion."""
    import psutil
    import signal

    p = psutil.Process(os.getpid())

    while True:
        parent = p.parent()
        if parent is None:
            break

        if parent.name() in ["gnome-terminal-server", "gnome-terminal", "konsole", "xfce4-terminal"]:
            os.kill(parent.pid, signal.SIGTERM)
            break

        p = parent