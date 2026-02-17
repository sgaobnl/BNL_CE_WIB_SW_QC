import numpy as np
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import file.report_dict as rd
import csv
import subprocess
import time
from datetime import datetime

# Import GUI modules for email and pop-windows
import GUI.send_email as send_email
import GUI.pop_window as pop

# Email configuration
SENDER_EMAIL = "bnlr216@gmail.com"
SENDER_PASSWORD = "vvef tosp minf wwhf"

# Image paths for instruction popups
IMG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'GUI', 'output_pngs')

t1 = time.time()
print("\033[35m" + "A_RT00 : Input the Test Information" + "\033[0m")
base_dir = os.path.dirname(os.path.abspath(__file__))
target_file_path = os.path.join(base_dir, ".", "file", "wib_info.csv")


input_name = input('Please input your name: ')

# Get tester email using terminal input
print("\nEmail will be used for result notification.")
tester_email = input('Enter your email (press Enter to skip): ').strip()
if tester_email and '@' in tester_email:
    print(f"Email: {tester_email}")
else:
    tester_email = ""
    print("Email notification skipped.")

# Show instruction popup for test preparation
pop.show_image_popup(
    title="Page 1: WIB QC Test Preparation",
    image_path=os.path.join(IMG_DIR, "1.png") if os.path.exists(os.path.join(IMG_DIR, "1.png")) else None
)

pop.show_image_popup(
    title="Page 2: ESD Preparation",
    image_path=os.path.join(IMG_DIR, "2.png") if os.path.exists(os.path.join(IMG_DIR, "2.png")) else None
)

# Scan Foam Box ID and WIB ID using dual input popup (both with double-check)
print("\nInitial Scanner - Scan Foam Box ID and WIB ID")
foam_box_id, WIB_id_0 = pop.show_dual_input_popup(
    title="Page 3: Scan Foam Box ID and WIB ID",
    image_path=os.path.join(IMG_DIR, "3.png") if os.path.exists(os.path.join(IMG_DIR, "3.png")) else None,
    prompt1="Scan Foam Box ID:",
    prompt2="Scan WIB ID:",
    require_confirmation=True
)
print(f"Foam Box ID: {foam_box_id}")
print(f"WIB ID: {WIB_id_0}")

if not WIB_id_0:
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

# Add Foam Box ID
csv_data['Foam_Box_ID'] = foam_box_id

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

pop.show_image_popup(
    title="Page 4: Install WIB",
    image_path=os.path.join(IMG_DIR, "4.png") if os.path.exists(os.path.join(IMG_DIR, "4.png")) else None
)

pop.show_image_popup(
    title="Page 5: Insert SFP Module and SD Card",
    image_path=os.path.join(IMG_DIR, "5.png") if os.path.exists(os.path.join(IMG_DIR, "5.png")) else None
)

pop.show_image_popup(
    title="Page 6: Insert Test Cables into Slots",
    image_path=os.path.join(IMG_DIR, "6.png") if os.path.exists(os.path.join(IMG_DIR, "6.png")) else None
)

subprocess.run(["python", "./component/Test01_Serial_TCPIP_Communication.py"])
subprocess.run(["python", "./component/Test02_Calibration_Path_Control.py"])
subprocess.run(["python", "./component/Test03_power_rail_for_FEMB_1V.py"])
subprocess.run(["python", "./component/Test03_power_rail_for_FEMB_2V.py"])
subprocess.run(["python", "./component/Test03_power_rail_for_FEMB_3V.py"])
subprocess.run(["python", "./component/Test03_power_rail_for_FEMB_4V.py"])
# subprocess.run(["python", "./component/Test0400_WIB_FEMB_Pulse.py"])
subprocess.run(["python", "./component/Test0401_WIB_FEMB_Pulse.py"])
# subprocess.run(["python", "./component/Test0402_WIB_FEMB_Pulse.py"])
# subprocess.run(["python", "./component/Test0403_WIB_FEMB_Pulse.py"])
subprocess.run(["python", "./component/Test05_Search_I2C.py"])
subprocess.run(["python", "./component/Test052_getInfoFromI2C.py"])
subprocess.run(["python", "./component/Test06_PTB_Interface_Path.py"])
print("Test07   IBERT Test Begin ...")
subprocess.run(["python", "./component/Test07_IBERT.py"])
subprocess.run(["python", "./component/Final_Report.py"])
t2 = time.time()
test_duration = t2 - t1
print(f"Test duration: {test_duration:.2f} seconds")

# Show result popup
pop.show_result_popup(
    title="WIB QC Test Complete",
    result_status="pass",
    message=f"Foam Box ID: {foam_box_id}\nWIB ID: {WIB_id_0}\nTest Duration: {test_duration:.2f}s",
    detail_link="file/final_report.html"
)


pop.show_image_popup(
    title="Page 9: Remove Cables and SD Card",
    image_path=os.path.join(IMG_DIR, "9.png") if os.path.exists(os.path.join(IMG_DIR, "9.png")) else None
)

pop.show_image_popup(
    title="Page 10: Package WIB Board into ESD Bag & Foam",
    image_path=os.path.join(IMG_DIR, "10.png") if os.path.exists(os.path.join(IMG_DIR, "10.png")) else None
)

pop.show_image_popup(
    title="Page 11: Label WIB with Test Results",
    image_path=os.path.join(IMG_DIR, "11.png") if os.path.exists(os.path.join(IMG_DIR, "11.png")) else None
)



# Send email notification if email was provided
if tester_email:
    print("\nSending email notification...")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    subject = f"[WIB QC Test Complete] {csv_data.get('test_site', 'BNL')} - {WIB_id_0} - {timestamp}"
    body = f"""WIB QC Test Completed

{'='*60}
WIB QC TEST RESULTS
{'='*60}
Date/Time: {timestamp}
Tester: {input_name}
Foam Box ID: {foam_box_id}
WIB ID: {WIB_id_0}
Test Site: {csv_data.get('test_site', 'BNL')}
Test Duration: {test_duration:.2f} seconds

{'-'*60}
Please check the detailed report at:
file/final_report.html
{'-'*60}

---
This is an automated message from the WIB QC Test System.
"""
    try:
        recipients = [tester_email]
        send_email.send_email(
            SENDER_EMAIL,
            SENDER_PASSWORD,
            recipients,
            subject,
            body
        )
        print(f"Email sent to: {tester_email}")
    except Exception as e:
        print(f"Failed to send email: {e}")