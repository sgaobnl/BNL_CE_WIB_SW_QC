"""
QC Utility Functions
Contains general-purpose utility functions for the FEMB QC system
"""

import os
import sys
import time
import threading
import colorama
from colorama import Fore, Style
import cts_ssh_FEMB as cts
import GUI.send_email as send_email

colorama.init()


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
        if not os.path.isdir(path):
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

            if pre_info:
                send_email.send_email(sender, password, receiver,
                                     "Issue Found at {}".format(pre_info.get('test_site', 'Unknown')),
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