"""
QC Results Module
Enhanced result checking and reporting for FEMB QC tests
"""

import os
import sys
import time
import re
import colorama
from colorama import Fore, Style
from datetime import datetime

colorama.init()


class QCResult:
    """Data class to hold QC test results"""
    def __init__(self):
        self.fault_files = []
        self.pass_files = []
        self.slot_status = {}  # {slot_num: (passed, femb_id)}
        self.slot_files = {}  # {slot_num: {'faults': [], 'passes': [], 'tests_found': set()}}
        self.slot_missing_tests = {}  # {slot_num: [list of missing test numbers]}
        self.test_phase = ""
        self.total_faults = 0
        self.total_passes = 0


def analyze_test_results(paths, inform=None, time_limit_hours=None):
    result = QCResult()

    # Calculate time threshold if specified
    time_threshold = 0
    if time_limit_hours is not None:
        time_threshold = time.time() - (time_limit_hours * 3.600)

    # Initialize slot file groups
    for slot_num in ['0', '1', '2', '3']:
        result.slot_files[slot_num] = {'faults': [], 'passes': [], 'tests_found': set()}
        result.slot_missing_tests[slot_num] = []

    # All 16 test items that should be present
    all_test_items = set(range(1, 17))  # t1 through t16

    # Scan all paths for fault and pass files, grouping by slot
    # Only count .md and .html files with _S0 (slot0/bottom) or _S1 (slot1/top)
    for path in paths:
        if not os.path.isdir(path):
            print(f"  Path not found: {path}")
            continue
        for root, dirs, files in os.walk(path):
            for file in files:
                # Only process .md and .html files
                if not (file.endswith('.md') or file.endswith('.html')):
                    continue

                file_path = os.path.join(root, file)

                # Apply time filter if specified
                if time_limit_hours is not None:
                    try:
                        file_mtime = os.path.getmtime(file_path)
                        if file_mtime < time_threshold:
                            continue
                    except OSError:
                        continue

                # Identify slot from filename: _S0 = slot0 (bottom), _S1 = slot1 (top)
                slot_identified = None
                if "_S0" in file:
                    slot_identified = '0'
                elif "_S1" in file:
                    slot_identified = '1'
                elif "_S2" in file:
                    slot_identified = '2'
                elif "_S3" in file:
                    slot_identified = '3'

                if slot_identified is None:
                    continue

                # Extract test item number from filename (_t1_, _t2_, ..., _t16_)
                test_match = re.search(r'_t(\d+)', file)
                if test_match:
                    test_num = int(test_match.group(1))
                    if 1 <= test_num <= 16:
                        result.slot_files[slot_identified]['tests_found'].add(test_num)

                # Determine if this is a fault or pass file using _F_ and _P_
                is_fault = "_F_" in file
                is_pass = "_P_" in file

                if not (is_fault or is_pass):
                    continue

                # Group file by slot and type
                if is_fault:
                    result.fault_files.append(file_path)
                    result.slot_files[slot_identified]['faults'].append(file_path)
                    print(f"  Fault file (Slot{slot_identified}): {file}")
                elif is_pass:
                    result.pass_files.append(file_path)
                    result.slot_files[slot_identified]['passes'].append(file_path)
                    print(f"  Pass file (Slot{slot_identified}): {file}")

    result.total_faults = len(result.fault_files)
    result.total_passes = len(result.pass_files)

    # Check for missing test items in each slot
    print(f"\n  Checking test item completeness (t1-t16)...")

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
        tests_found = result.slot_files[slot_num]['tests_found']

        # Check for missing test items (t1-t16)
        missing_tests = sorted(all_test_items - tests_found)
        result.slot_missing_tests[slot_num] = missing_tests

        # Report missing tests
        slot_position = "Bottom" if slot_num == '0' else "Top" if slot_num == '1' else f"Slot{slot_num}"
        if missing_tests:
            print(f"  WARNING: {slot_position} Slot{slot_num} missing tests: {missing_tests}")
        else:
            print(f"  {slot_position} Slot{slot_num}: All 16 tests found")

        # Slot passes only if:
        # 1. No fault files (_F_)
        # 2. All 16 test items are present
        has_faults = len(slot_faults) > 0
        has_missing_tests = len(missing_tests) > 0
        passed = not has_faults and not has_missing_tests

        # Print slot summary
        print(f"    - Fault files: {len(slot_faults)}")
        print(f"    - Pass files: {len(slot_passes)}")
        print(f"    - Tests found: {len(tests_found)}/16")
        if has_faults:
            print(f"    - FAILED: Has {len(slot_faults)} fault file(s)")
        if has_missing_tests:
            print(f"    - FAILED: Missing {len(missing_tests)} test(s): t{', t'.join(map(str, missing_tests))}")

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

        # Get slot-specific file counts and test info
        slot_faults = result.slot_files.get(slot_num, {}).get('faults', [])
        slot_passes = result.slot_files.get(slot_num, {}).get('passes', [])
        tests_found = result.slot_files.get(slot_num, {}).get('tests_found', set())
        missing_tests = result.slot_missing_tests.get(slot_num, [])
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
        print(f"      Tests: {len(tests_found)}/16 found")
        if missing_tests:
            print(f"      {Fore.YELLOW}Missing tests: t{', t'.join(map(str, missing_tests))}{Style.RESET_ALL}")

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
            # decision = input(Fore.CYAN + ">> " + Style.RESET_ALL).lower()
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

                # Get slot-specific file counts and test info
                slot_faults = qc_result.slot_files.get(slot_num, {}).get('faults', [])
                slot_passes = qc_result.slot_files.get(slot_num, {}).get('passes', [])
                tests_found = qc_result.slot_files.get(slot_num, {}).get('tests_found', set())
                missing_tests = qc_result.slot_missing_tests.get(slot_num, [])
                fault_count = len(slot_faults)
                pass_count = len(slot_passes)

                status_text = "PASS" if passed else "FAIL"
                f.write(f"  {slot_position} Slot{slot_num}: FEMB {femb_id} - {status_text}\n")
                f.write(f"    Files: {fault_count} faults, {pass_count} passes\n")
                f.write(f"    Tests: {len(tests_found)}/16 found\n")

                if not passed:
                    all_passed = False
                    failed_slots.append((slot_num, femb_id))

                # List fault files for this slot
                if slot_faults:
                    f.write(f"    Fault files:\n")
                    for fault_file in slot_faults:
                        f.write(f"      - {os.path.basename(fault_file)}\n")

                # List missing tests for this slot
                if missing_tests:
                    f.write(f"    Missing tests: t{', t'.join(map(str, missing_tests))}\n")

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
