import logging
import os
import time
import subprocess
from datetime import datetime
import QC_components.qc_log as main_dict
import csv
import shutil
import webbrowser



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
                report_dir = path.replace('/Data/', '/Report/')
                sync_to_network(raw_dir, report_dir)
                open_reports(raw_dir)

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
