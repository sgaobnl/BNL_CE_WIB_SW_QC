"""
QC Results Module
Enhanced result checking and reporting for FEMB QC tests
"""

import os
import sys
import time
import colorama
from colorama import Fore, Style

colorama.init()


class QCResult:
    """Data class to hold QC test results"""
    def __init__(self):
        self.fault_files = []
        self.pass_files = []
        self.slot_status = {}  # {slot_num: (passed, femb_id)}
        self.slot_files = {}  # {slot_num: {'faults': [], 'passes': []}}
        self.test_phase = ""
        self.total_faults = 0
        self.total_passes = 0


def analyze_test_results(paths, inform=None, time_limit_hours=None):
    """
    Analyze test result files and return structured result data
    Files are grouped by slot based on filename patterns (FEMB_0_ for slot0, FEMB_1_ for slot1)

    Args:
        paths: List of directories to check for result files
        inform: Dictionary containing FEMB slot information
        time_limit_hours: Optional time filter (in hours) - set to None to check all files in paths

    Returns:
        QCResult object with analysis results
    """
    result = QCResult()

    # Calculate time threshold if specified
    time_threshold = 0
    if time_limit_hours is not None:
        time_threshold = time.time() - (time_limit_hours * 3600)

    # Initialize slot file groups
    for slot_num in ['0', '1', '2', '3']:
        result.slot_files[slot_num] = {'faults': [], 'passes': []}

    # Scan all paths for fault and pass files, grouping by slot
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

                # Determine if this is a fault or pass file
                is_fault = "_F." in file or "_F_S" in file
                is_pass = "_P." in file or "_P_S" in file

                if not (is_fault or is_pass):
                    continue

                # Identify which slot this file belongs to based on filename
                slot_identified = None
                file_upper = file.upper()

                # Check for FEMB_X_ pattern (where X is slot number)
                # This is the primary pattern: FEMB_0_ for slot0, FEMB_1_ for slot1
                for slot_num in ['0', '1', '2', '3']:
                    if f"FEMB_{slot_num}_" in file_upper:
                        slot_identified = slot_num
                        break

                # Fallback: check other slot patterns if primary pattern not found
                if slot_identified is None:
                    for slot_num in ['0', '1', '2', '3']:
                        slot_patterns = [
                            f"SLOT{slot_num}",   # e.g., "Slot0" or "SLOT0"
                            f"_S{slot_num}_",    # e.g., "_S0_"
                            f"_S{slot_num}.",    # e.g., "_S0."
                            f"-S{slot_num}_",    # e.g., "-S0_"
                            f"S{slot_num}_",     # e.g., "S0_" at start
                        ]

                        for pattern in slot_patterns:
                            if pattern in file_upper:
                                slot_identified = slot_num
                                break
                        if slot_identified:
                            break

                # Group file by slot and type
                if is_fault:
                    result.fault_files.append(file_path)
                    if slot_identified:
                        result.slot_files[slot_identified]['faults'].append(file_path)
                elif is_pass:
                    result.pass_files.append(file_path)
                    if slot_identified:
                        result.slot_files[slot_identified]['passes'].append(file_path)

    result.total_faults = len(result.fault_files)
    result.total_passes = len(result.pass_files)

    # Analyze slot-specific results based on grouped files
    slots_to_check = ['Slot0', 'Slot1', 'Slot2', 'Slot3']

    for slot_name in slots_to_check:
        slot_num = slot_name[-1]  # Extract slot number
        femb_id = inform.get(slot_name.upper(), 'N/A') if inform else 'N/A'

        # Only process this slot if FEMB is installed (has valid ID)
        if not (inform and slot_name.upper() in inform and
                inform[slot_name.upper()] not in ['', ' ', 'N/A', 'EMPTY', 'NONE']):
            continue

        # Determine pass/fail based on files grouped for this slot
        slot_faults = result.slot_files[slot_num]['faults']
        slot_passes = result.slot_files[slot_num]['passes']

        # Slot passes only if it has no fault files
        passed = len(slot_faults) == 0

        # Debug: print slot file summary (if debug enabled)
        if os.environ.get('QC_DEBUG') == '1':
            print(f"DEBUG: Slot{slot_num} (FEMB {femb_id}):")
            print(f"  - Fault files: {len(slot_faults)}")
            print(f"  - Pass files: {len(slot_passes)}")
            if slot_faults:
                for fault_file in slot_faults:
                    print(f"    • {os.path.basename(fault_file)}")

        result.slot_status[slot_num] = (passed, femb_id)

    return result


def display_qc_results(result, test_phase="QC Test", verbose=False):
    """
    Display formatted QC test results with per-slot file breakdown

    Args:
        result: QCResult object
        test_phase: Name of the test phase (e.g., "Warm QC", "Cold QC")
        verbose: If True, show detailed file lists for each slot
    """
    print("\n" + "=" * 70)
    print(f"  {test_phase.upper()} - TEST RESULTS")
    print("=" * 70)

    # Summary statistics
    print(f"\n📊 Test Summary:")
    print(f"   Total Fault Files: {Fore.RED}{result.total_faults}{Style.RESET_ALL}")
    print(f"   Total Pass Files:  {Fore.GREEN}{result.total_passes}{Style.RESET_ALL}")

    # Slot-by-slot results
    print(f"\n🔍 FEMB Status by Slot:")
    all_passed = True
    failed_slots = []

    for slot_num in sorted(result.slot_status.keys()):
        passed, femb_id = result.slot_status[slot_num]
        slot_position = "Bottom" if slot_num == '0' else "Top" if slot_num == '1' else f"Slot{slot_num}"

        # Get slot-specific file counts
        slot_faults = result.slot_files.get(slot_num, {}).get('faults', [])
        slot_passes = result.slot_files.get(slot_num, {}).get('passes', [])
        fault_count = len(slot_faults)
        pass_count = len(slot_passes)

        if passed:
            status_icon = "✓"
            status_text = "PASS"
            color = Fore.GREEN
        else:
            status_icon = "✗"
            status_text = "FAIL"
            color = Fore.RED
            all_passed = False
            failed_slots.append((slot_num, femb_id))

        print(f"   {color}{status_icon} {slot_position} Slot{slot_num}: FEMB {femb_id} - {status_text}{Style.RESET_ALL}")
        print(f"      Files: {Fore.RED}{fault_count} faults{Style.RESET_ALL}, {Fore.GREEN}{pass_count} passes{Style.RESET_ALL}")

        # Show detailed file list for this slot if verbose
        if verbose and (slot_faults or slot_passes):
            if slot_faults:
                print(f"      {Fore.YELLOW}Fault files for Slot{slot_num}:{Style.RESET_ALL}")
                for fault_file in slot_faults:
                    print(f"        {Fore.RED}• {os.path.basename(fault_file)}{Style.RESET_ALL}")
            if slot_passes and verbose:
                print(f"      {Fore.CYAN}Pass files for Slot{slot_num}:{Style.RESET_ALL}")
                for pass_file in slot_passes[:3]:  # Show first 3 pass files
                    print(f"        {Fore.GREEN}• {os.path.basename(pass_file)}{Style.RESET_ALL}")
                if len(slot_passes) > 3:
                    print(f"        {Fore.CYAN}... and {len(slot_passes)-3} more{Style.RESET_ALL}")

    # Overall fault file summary (if there are faults)
    if result.fault_files and result.total_faults > 0:
        print(f"\n⚠️  All Fault Files Detected ({result.total_faults} total):")
        # Group by slot for display
        for slot_num in sorted(result.slot_files.keys()):
            slot_faults = result.slot_files[slot_num]['faults']
            if slot_faults:
                slot_name = "Bottom" if slot_num == '0' else "Top" if slot_num == '1' else f"Slot{slot_num}"
                print(f"   {Fore.YELLOW}{slot_name} Slot{slot_num}:{Style.RESET_ALL}")
                for fault_file in slot_faults:
                    print(f"      {Fore.RED}• {os.path.basename(fault_file)}{Style.RESET_ALL}")

    # Overall result
    print("\n" + "=" * 70)
    if all_passed:
        print(f"  {Fore.GREEN}✓✓✓ OVERALL RESULT: PASS ✓✓✓{Style.RESET_ALL}")
    else:
        print(f"  {Fore.RED}✗✗✗ OVERALL RESULT: FAIL ✗✗✗{Style.RESET_ALL}")
        print(f"\n  Failed FEMBs:")
        for slot_num, femb_id in failed_slots:
            slot_name = "Bottom" if slot_num == '0' else "Top" if slot_num == '1' else f"Slot{slot_num}"
            print(f"    {Fore.RED}• {slot_name} Slot{slot_num}: {femb_id}{Style.RESET_ALL}")
    print("=" * 70 + "\n")

    return all_passed, failed_slots


def handle_qc_results(paths, inform, test_phase="QC Test", allow_retry=True, verbose=False, time_limit_hours=None):
    """
    Complete QC result handling workflow: analyze, display, and handle user decisions

    Args:
        paths: List of directories to check
        inform: FEMB information dictionary
        test_phase: Name of the test phase
        allow_retry: If True, ask user if they want to retry on failure
        verbose: If True, show detailed information
        time_limit_hours: Optional time filter (None = check all files in provided paths)

    Returns:
        tuple: (all_passed, should_retry, failed_slots)
    """
    # Analyze results from the specific test directories
    result = analyze_test_results(paths, inform, time_limit_hours=time_limit_hours)

    # Display results
    all_passed, failed_slots = display_qc_results(result, test_phase, verbose)

    # Handle user decision
    should_retry = False
    if not all_passed and allow_retry:
        print(Fore.YELLOW + "⚠️  Test failed. What would you like to do?" + Style.RESET_ALL)
        print("  " + Fore.GREEN + "'r'" + Style.RESET_ALL + " - Retry the test")
        print("  " + Fore.RED + "'c'" + Style.RESET_ALL + " - Continue anyway (not recommended)")
        print("  " + Fore.YELLOW + "'e'" + Style.RESET_ALL + " - Exit program")

        while True:
            decision = input(Fore.CYAN + ">> " + Style.RESET_ALL).lower()
            if decision == 'r':
                should_retry = True
                print(Fore.GREEN + "🔄 Retrying test..." + Style.RESET_ALL)
                break
            elif decision == 'c':
                print(Fore.YELLOW + "⚠️  Continuing with failed test..." + Style.RESET_ALL)
                break
            elif decision == 'e':
                print(Fore.RED + "Exiting program..." + Style.RESET_ALL)
                # Display replacement recommendations
                print("\n" + Fore.YELLOW + "Recommended actions:" + Style.RESET_ALL)
                for slot_num, femb_id in failed_slots:
                    slot_name = "Bottom" if slot_num == '0' else "Top"
                    print(f"  • Replace {slot_name} Slot{slot_num} FEMB {femb_id}")
                sys.exit(1)
            else:
                print(Fore.RED + "Invalid input. Please enter 'r', 'c', or 'e'" + Style.RESET_ALL)

    return all_passed, should_retry, failed_slots


def get_slot_results(paths, inform):
    """
    Quick function to get slot pass/fail status (backward compatible)

    Returns:
        tuple: (slot0_passed, slot1_passed)
    """
    result = analyze_test_results(paths, inform)
    s0 = result.slot_status.get('0', (True, 'N/A'))[0]
    s1 = result.slot_status.get('1', (True, 'N/A'))[0]
    return s0, s1
