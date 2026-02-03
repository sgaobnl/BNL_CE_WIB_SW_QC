import logging
import os
import time
import subprocess
from datetime import datetime
import QC_components.qc_log as main_dict
import csv
import shutil
import webbrowser
import GUI.send_email as send_email
from qc_results import analyze_test_results, generate_qc_summary



# common use the top_path
csv_data = {}
csv_file = 'init_setup.csv'
file_path = r'init_setup.csv'
with open(csv_file, mode='r', newline='', encoding='utf-8-sig') as file:
    reader = csv.reader(file)
    for row in reader:
        if len(row) == 2:
            key, value = row
            csv_data[key.strip()] = value.strip()
main_dict.top_path = csv_data['QC_data_root_folder']
top_path = main_dict.top_path
print(top_path)
target_folder = top_path + '/FEMB_QC/Data'
last_scan_file = top_path + '/FEMB_QC/Data/last_scan_results.txt'
network_path = csv_data.get('Network_Upload_Path', '/data/rtss/femb')

# Email configuration from init_setup
sender = csv_data.get('email_sender', 'bnlr216@gmail.com')
password = csv_data.get('email_password', 'vvef tosp minf wwhf')
receiver = csv_data.get('email_receiver', 'lke@bnl.gov')


def sync_to_network(raw_dir, report_dir):
    """Sync data to network path after local copy"""
    try:
        # Skip if network path not configured or same as local
        if not network_path or network_path == top_path:
            return

        # Extract relative path from root
        if raw_dir.startswith(top_path):
            raw_rel_path = os.path.relpath(raw_dir, top_path)
            report_rel_path = os.path.relpath(report_dir, top_path)

            network_raw_dir = os.path.join(network_path, raw_rel_path)
            network_report_dir = os.path.join(network_path, report_rel_path)

            # print(f"Syncing to network: {network_path}/FEMB_QC/")
            print(f"Syncing to network: {network_path}/")

            # Copy raw data to network
            if os.path.exists(raw_dir):
                os.makedirs(os.path.dirname(network_raw_dir), exist_ok=True)
                shutil.copytree(raw_dir, network_raw_dir, dirs_exist_ok=True)
                print(f"  Raw data synced")

            # Copy report to network
            if os.path.exists(report_dir):
                os.makedirs(os.path.dirname(network_report_dir), exist_ok=True)
                shutil.copytree(report_dir, network_report_dir, dirs_exist_ok=True)
                print(f"  Report synced")

    except Exception as e:
        # Don't fail if network sync fails, just warn
        print(f"Network sync failed: {e}")
        print("  (Data saved locally)")


def open_reports(data_dir):
    """Open markdown report files in browser"""
    for root, dirs, files in os.walk(data_dir):
        for file in files:
            if file.endswith('.md') and any(f'N{i}.md' in file for i in range(4)):
                file_path = os.path.join(root, file).replace('\\', '/')
                webbrowser.open(f'file://{file_path}')


def copy_file_to_network(file_path):
    """Copy a single new file to network path"""
    try:
        # Skip if network path not configured or same as local
        if not network_path or network_path == top_path:
            return

        # Extract relative path from top_path
        if file_path.startswith(top_path):
            rel_path = os.path.relpath(file_path, top_path)
            network_file_path = os.path.join(network_path, rel_path)

            # Create directory if needed
            os.makedirs(os.path.dirname(network_file_path), exist_ok=True)

            # Copy the file
            shutil.copy2(file_path, network_file_path)
            print(f"  Copied to network: {network_file_path}")
    except Exception as e:
        print(f"  Network copy failed for {file_path}: {e}")

def save_last_scan_results(results):
    with open(last_scan_file, 'w') as f:
        for file_path in results:
            f.write(file_path + '\n')

def load_last_scan_results():
    results = set()
    if os.path.exists(last_scan_file):
        with open(last_scan_file, 'r') as f:
            for line in f:
                results.add(line.strip())
    return results

def subrun(command, timeout=30, check=True, exitflg=True, user_input=None):
    print(command)
    global result
    try:
        result = subprocess.run(command,
                                input = user_input,
                                capture_output=True,
                                text=True,
                                timeout=timeout,
                                shell=True,
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
    except subprocess.TimeoutExpired as e:
        print("No reponse in %d seconds" % (timeout))
        if exitflg:
            # print (result.stdout)
            print("Timoout FAIL!")
            print("Exit anyway")
            return None
            # exit()
        # continue
    return result


def process_qc_summary_after_t16(report_path):
    """
    Process QC summary after t16 analysis completes:
    1. Wait 500 seconds for all reports to complete
    2. Read FEMB info from femb_info_implement.csv
    3. Analyze test results
    4. Send summary email with per-slot results

    Args:
        report_path: Path to the report directory (e.g., /FEMB_QC/Report/<timestamp>/)
    """
    try:
        print(f"\n{'='*70}")
        print(f"  QC Test Item 16 Completed - Preparing Summary")
        print(f"{'='*70}")
        print(f"  Waiting 500 seconds for all reports to complete...")

        # Wait 500 seconds for reports to complete
        time.sleep(100)

        print(f"  Analyzing QC results...")

        # Read FEMB info from femb_info_implement.csv
        csv_file_implement = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'femb_info_implement.csv')
        inform = {}
        if os.path.exists(csv_file_implement):
            with open(csv_file_implement, mode='r', newline='', encoding='utf-8-sig') as file:
                reader = csv.reader(file)
                for row in reader:
                    if len(row) == 2:
                        key, value = row
                        inform[key.strip()] = value.strip()

        # Determine QC type based on path (WQ = Warm QC, LQ = Cold QC)
        qc_type = "QC Test"
        if '_WQ_' in report_path or '/WQ/' in report_path or 'Warm' in report_path:
            qc_type = "Warm QC"
        elif '_LQ_' in report_path or '/LQ/' in report_path or 'Cold' in report_path or 'LN' in report_path:
            qc_type = "Cold QC"

        test_site = inform.get('test_site', csv_data.get('Test_Site', 'N/A'))

        # Use report_path directly (passed from real_time_monitor using QC_report.py formula)
        print(f"  Using report_path: {report_path}")
        paths = [report_path]  # Report path contains _F_ and _P_ result files

        # Analyze test results from Report directory
        qc_result = analyze_test_results(paths, inform, time_limit_hours=None)

        # Generate summary file in Report directory
        summary_filename = f"{qc_type.replace(' ', '_')}_Summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        summary_path = os.path.join(report_path, summary_filename)
        generate_qc_summary(qc_type, inform, qc_result, summary_path)

        # Build email body with per-slot results
        overall_passed = qc_result.total_faults == 0
        email_body = f"""{qc_type} Test Completed

Test Site: {test_site}
Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Summary:
  Total Fault Files: {qc_result.total_faults}
  Total Pass Files: {qc_result.total_passes}
  Overall Result: {'PASS' if overall_passed else 'FAIL'}

FEMB Results:
"""
        # Add per-slot details
        for slot_num in sorted(qc_result.slot_status.keys()):
            passed, femb_id = qc_result.slot_status[slot_num]
            slot_position = "Bottom" if slot_num == '0' else "Top" if slot_num == '1' else f"Slot{slot_num}"
            status = "PASS" if passed else "FAIL"
            email_body += f"  {slot_position} Slot{slot_num}: {femb_id} - {status}\n"

        # Add next steps based on QC type
        if qc_type == "Warm QC":
            email_body += f"""
Next Steps:
  1. Switch CTS to COLD mode for 5 minutes
  2. Switch to IMMERSE mode
  3. Wait for LN2 to reach Level 3
  4. Double confirm heat LED is OFF

Detailed summary is attached.
"""
        elif qc_type == "Cold QC":
            warmup_time = int(csv_data.get('CTS_Warmup_Wait', 3600)) // 60
            email_body += f"""
Next Step:
  Please perform the warm-up procedure ({warmup_time} minutes)

Detailed summary is attached.
"""
        else:
            email_body += "\nDetailed summary is attached.\n"

        # Send email with attachment
        try:
            send_email.send_email_with_attachment(
                sender, password, receiver,
                f"{qc_type} Complete - {test_site}",
                email_body,
                summary_path
            )
            print(f"  ✓ {qc_type} summary email sent with attachment")
        except Exception as email_err:
            print(f"  ✗ Failed to send email: {email_err}")

        # Delete summary file after email sent
        try:
            os.remove(summary_path)
        except Exception as del_e:
            print(f"  Warning: Failed to delete summary file: {del_e}")

        print(f"{'='*70}\n")

    except Exception as e:
        print(f"  ✗ Error processing QC summary: {e}")


logs = {}

def real_time_monitor():
    previous_files = load_last_scan_results()
    while True:
        current_files = set()
        for root, dirs, files in os.walk(target_folder):
            for file in files:
                current_files.add(os.path.join(root, file))
        # calculate new update document
        new_files = current_files - previous_files
        # update the scan result
        previous_files = current_files

        save_last_scan_results(current_files)

        for file_path in new_files:
            n = " "
            c = 0
            print(f'new file detected: {file_path}')
            # Copy new file to network disk immediately
            copy_file_to_network(file_path)
            if '_S0' in file_path:
                n += " 0 "
                c+=1
            if '_S1' in file_path:
                n += " 1 "
                c += 1
            if '_S2' in file_path:
                n += " 2 "
                c += 1
            if '_S3' in file_path:
                n += " 3 "
                c += 1

            desired_path = os.path.dirname(file_path)  # get last path
            path = os.path.dirname(desired_path)  # get last path
            path = path.replace('\\', '/')  # get last path
            t_char = file_path[-7:]
            t_num = ''.join([char for char in t_char if char.isdigit()])
            if '_t' in file_path[-9:]:
                if '_t6' in file_path[-9:]:
                    time.sleep(c*30)  # the time is used to copy the whole .bin file
                else:
                    time.sleep(c*7)  # the time is used to copy the whole .bin file
                slot = n
                item = t_num
                command = ["python3 QC_report_all.py" + " " + path  + " " +  "-n " + slot + " -t " + item]
                # command.extend(map(str, n))  # Convert integers to strings
                # command.extend([" -t ", t_num])  # Add other arguments
                result = subrun(command, timeout=1000)  # rewrite with Popen later

                # After report generation, sync to network and open reports
                raw_dir = path

                # Parse report path from QC_report_all.py output
                report_dir = None
                if result and result.stdout:
                    for line in result.stdout.split('\n'):
                        if line.startswith('REPORT_PATH_OUTPUT='):
                            print(line)
                            print(line.split('=', 1))
                            print(line.startswith('REPORT_PATH_OUTPUT='))
                            print(report_dir)
                            report_dir = line.split('=', 1)[1].strip()
                            print(f"  Parsed report_dir from QC_report_all.py: {report_dir}")
                            break

                # Fallback to string replacement if parsing failed
                if not report_dir:
                    report_dir = path.replace('/Data/', '/Report/')
                    print(f"  Fallback report_dir: {report_dir}")

                # sync_to_network(raw_dir, report_dir)
                # open_reports(raw_dir)
                qc_report_path = top_path + '/FEMB_QC/Report/' + path.split("/")[-3] + '/' + path.split("/")[-2] + '/'
                targets = ["_t16.bin", "_t15.bin", "_t14.bin", "_t13.bin"]
                print(targets)

                exists = {
                             t
                             for _, _, files in os.walk(qc_report_path)
                             for fname in files
                             for t in targets
                             if t in fname
                         } == set(targets)
                # After t16 completes, generate QC summary email
                if exists:
                    print(f"  t16 detected - triggering QC summary process")
                    # Construct report_path using same formula as QC_report.py line 46
                    qc_report_path = top_path + '/FEMB_QC/Report/' + path.split("/")[-3] + '/' + path.split("/")[-2] + '/'
                    print(f"  Constructed report_path: {qc_report_path}")
                    process_qc_summary_after_t16(qc_report_path)

        time.sleep(5)   # when monitor works in wait, 5 seconds wait in one scan cycle

print("Real-Time Monitor script, you can minize it in background")
directory__Report_path = top_path + '/FEMB_QC/Report'
if not os.path.exists(directory__Report_path):
    os.makedirs(directory__Report_path)
    print(f"Directory '{directory__Report_path}' created.")
else:
    print(f"Directory '{directory__Report_path}' already exists. ")

directory_Data_path = top_path + '/FEMB_QC/Data'
if not os.path.exists(directory_Data_path):
    os.makedirs(directory_Data_path)
    print(f"Directory '{directory_Data_path}' created.")
else:
    print(f"Directory '{directory_Data_path}' already exists. ")


real_time_monitor()

if True:
    logging.basicConfig(filename='{}FEMB_QC/Data/QC.log'.format(top_path),
                        level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')
    logging.info('info: %s', logs)
