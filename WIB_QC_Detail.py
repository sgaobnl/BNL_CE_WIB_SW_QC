import numpy as np
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import file.report_dict as rd
import csv
import os
import subprocess

print("\033[35m" + "A_RT00 : Input the Test Information" + "\033[0m")
base_dir = os.path.dirname(os.path.abspath(__file__))
target_file_path = os.path.join(base_dir, ".", "file", "wib_info.csv")
input_name = input('Please input your name: ')
Initial_Scaner = print("Initial Scaner")
WIB_id_0 = input('Scan WIB ID in Slot #0\t')

csv_data = {}
with open(target_file_path, mode='r', newline='', encoding='utf-8-sig') as file:
    reader = csv.reader(file)
    for row in reader:
        if len(row) == 2:
            key, value = row
            csv_data[key.strip()] = value.strip()
if 'tester' not in csv_data:
    csv_data['tester'] = 'LingyunKe'
else:
    csv_data['tester'] = input_name
if 'WIB_ID' not in csv_data:
    csv_data['WIB_ID'] = 'H01'
else:
    csv_data['WIB_ID'] = WIB_id_0

if 'test_site' not in csv_data:
    csv_data['test_site'] = 'BNL'
if 'comment' not in csv_data:
    csv_data['comment'] = 'WIB Reception Checkout test'

with open(target_file_path, mode="w", newline="", encoding='utf-8-sig') as file:
    writer = csv.writer(file)
    for key, value in csv_data.items():
        writer.writerow([key, value])
rd.wib_info = csv_data
print(csv_data)

subprocess.run(["python", "./component/Test01_Serial_TCPIP_Communication.py"])
subprocess.run(["python", "./component/Test02_Calibration_Path_Control.py"])
subprocess.run(["python", "./component/Test03_power_rail_for_FEMB_1V.py"])
subprocess.run(["python", "./component/Test03_power_rail_for_FEMB_2V.py"])
subprocess.run(["python", "./component/Test03_power_rail_for_FEMB_3V.py"])
subprocess.run(["python", "./component/Test03_power_rail_for_FEMB_4V.py"])
subprocess.run(["python", "./component/Test0400_WIB_FEMB_Pulse.py"])
subprocess.run(["python", "./component/Test0401_WIB_FEMB_Pulse.py"])
subprocess.run(["python", "./component/Test0402_WIB_FEMB_Pulse.py"])
subprocess.run(["python", "./component/Test0403_WIB_FEMB_Pulse.py"])
subprocess.run(["python", "./component/Test05_Search_I2C.py"])
subprocess.run(["python", "./component/Test052_getInfoFromI2C.py"])
subprocess.run(["python", "./component/Test06_PTB_Interface_Path.py"])
print("Test07   IBERT Test Begin ...")
subprocess.run(["python", "./component/Test07_IBERT.py"])
subprocess.run(["python", "./component/Final_Report.py"])
