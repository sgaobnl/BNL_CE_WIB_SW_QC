import sys
from QC_report import QC_reports
import argparse
import time
import csv
import os
import shutil

# Read network path from config
csv_data = {}
csv_file = 'init_setup.csv'
with open(csv_file, mode='r', newline='', encoding='utf-8-sig') as file:
    reader = csv.reader(file)
    for row in reader:
        if len(row) == 2:
            key, value = row
            csv_data[key.strip()] = value.strip()
top_path = csv_data.get('QC_data_root_folder', '')
network_path = csv_data.get('Network_Upload_Path', '')

print(f"[DEBUG] top_path: {top_path}")
print(f"[DEBUG] network_path: {network_path}")


def sync_report_to_network(data_dir):
    """Copy generated reports to network path"""
    print(f"\n[SYNC] Starting sync_report_to_network")
    print(f"[SYNC] data_dir: {data_dir}")
    print(f"[SYNC] top_path: {top_path}")
    print(f"[SYNC] network_path: {network_path}")

    try:
        if not network_path:
            print(f"[SYNC] SKIP: network_path is empty")
            return
        if network_path == top_path:
            print(f"[SYNC] SKIP: network_path == top_path")
            return

        # Convert data path to report path
        report_dir = data_dir.replace('/Data/', '/Report/')
        print(f"[SYNC] report_dir: {report_dir}")

        if not os.path.exists(report_dir):
            print(f"[SYNC] report_dir does not exist: {report_dir}")
            # Try parent directory (without /QC suffix)
            report_dir_parent = os.path.dirname(report_dir)
            print(f"[SYNC] Trying parent: {report_dir_parent}")
            if os.path.exists(report_dir_parent):
                report_dir = report_dir_parent
                print(f"[SYNC] Using parent report_dir: {report_dir}")
            else:
                # List what's in the Report base folder
                report_base = os.path.join(top_path, 'FEMB_QC', 'Report')
                print(f"[SYNC] Checking report_base: {report_base}")
                if os.path.exists(report_base):
                    print(f"[SYNC] Contents of {report_base}:")
                    for item in os.listdir(report_base):
                        print(f"[SYNC]   - {item}")
                else:
                    print(f"[SYNC] report_base does not exist")
                print(f"[SYNC] SKIP: No valid report directory found")
                return

        print(f"[SYNC] report_dir exists: {report_dir}")

        # Calculate relative path and network destination
        if report_dir.startswith(top_path):
            rel_path = os.path.relpath(report_dir, top_path)
            network_report_dir = os.path.join(network_path, rel_path)
            print(f"[SYNC] rel_path: {rel_path}")
            print(f"[SYNC] network_report_dir: {network_report_dir}")

            # Copy report to network
            parent_dir = os.path.dirname(network_report_dir)
            print(f"[SYNC] Creating parent dir: {parent_dir}")
            os.makedirs(parent_dir, exist_ok=True)

            print(f"[SYNC] Copying {report_dir} -> {network_report_dir}")
            shutil.copytree(report_dir, network_report_dir, dirs_exist_ok=True)
            print(f"[SYNC] SUCCESS: Report synced to network: {network_report_dir}")
        else:
            print(f"[SYNC] SKIP: report_dir does not start with top_path")
            print(f"[SYNC]   report_dir: {report_dir}")
            print(f"[SYNC]   top_path: {top_path}")
    except Exception as e:
        print(f"[SYNC] ERROR: Network sync failed: {e}")
        import traceback
        traceback.print_exc()

ag = argparse.ArgumentParser()
ag.add_argument("folder", help="data folder", type=str)
ag.add_argument("-t", "--tasks",help="a list of tasks to be analyzed", type=int, choices=range(1,16+1), nargs='+',default=range(1,16+1))
ag.add_argument("-n", "--fembs", help="a list of fembs to be analyzed", type=int, choices=range(0,4), nargs='+')
args = ag.parse_args()

fdir = args.folder
fdir = fdir.replace('\\', '/')
print("debug01 = {}".format(fdir))
tasks = args.tasks
fembs = args.fembs

if 'OW' in sys.argv:
    NewWIB = False
else:
    NewWIB = True



rp = QC_reports(fdir, fembs, NewWIB = NewWIB)

# Output the actual report directory for CTS_Real_Time_Monitor.py to parse
# Get the base report directory (parent of FEMB-specific directories)
if rp.savedir:
    first_savedir = list(rp.savedir.values())[0]
    # Go up two levels to get base report directory (remove FEMB_xxx_Sx/ part)
    report_base_dir = os.path.dirname(os.path.dirname(first_savedir.rstrip('/')))
    print(f"REPORT_PATH_OUTPUT={report_base_dir}")

tt={}
t1=time.time()
for tm in tasks:

    print("start tm=",tm)
    if tm==1:
       rp.PWR_consumption_report()

    if tm==2:
       rp.PWR_cycle_report()
       
    if tm==3:
       rp.LCCHKPULSE("Leakage_Current")
       
    if tm==4:
       rp.CHKPULSE("CHK")

    if tm==5:
       rp.RMS_report()

    if tm==6:
       rp.CALI_report_1()

    if tm==7:
       rp.CALI_report_2()

    if tm==8:
       rp.CALI_report_3()

    if tm==9:
       rp.CALI_report_4()

    if tm==10:
       rp.FE_MON_report()

    if tm==11:
       rp.FE_DAC_MON_report()

    if tm==12:
       rp.ColdADC_DAC_MON_report()

    if tm==13:
       rp.CALI_report_5()

    if tm==14:
       rp.CALI_report_6()

    if tm==15:
       rp.femb_adc_sync_pat_report("ADC_SYNC_PAT")

    if tm==16:
       rp.PLL_scan_report("PLL_PAT")

    # if tm==17:
    #    rp.CHK_report()

    # if tm==13:
    #    rp.CHK_report()
    rp.report()

t2=time.time()
tt=t2-t1
time.sleep(1)

print(tt)

# Sync reports to network
sync_report_to_network(fdir)
