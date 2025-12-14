import os
import sys
import time
from PIL import Image
import csv

print("\033[35m" + "DUNE CE WARM INTERFACE BOARD QUALITY TEST" + "\033[0m")
print("\033[35m" + "BASIC INFORMATION" + "\033[0m")
print('Equipment: \t#01 FEMB board \t#02 WIB adapter board \t#03 Power Supply \t#04 power and data cable \t#05 Test PC \t#06 WIB support structure\n')
csv_file = r'D:\WIB_QC\DUNE_WIB_QC_Script\file\wib_info.csv'
# print("\033[35m" + "A_RT00 : Install FEMB boards, check the connection of Data and Power Cables" + "\033[0m")
input_name = input('Please input your name: ')
Initial_Scaner = input("Initial Scaner \t\tEnter Any Key to exit ...")

WIB_id = input('Scan the WIB ID Under Test\t')
csv_data = {}
with open(csv_file, mode='r', newline='', encoding='utf-8-sig') as file:
    reader = csv.reader(file)
    for row in reader:
        if len(row) == 2:
            key, value = row
            csv_data[key.strip()] = value.strip()
if 'tester' not in csv_data:
    csv_data['tester'] = 'lke'
else:
    csv_data['tester'] = input_name
if 'SLOT0' not in csv_data:
    csv_data['SLOT0'] = '17501F08'
else:
    csv_data['SLOT0'] = WIB_id
if 'test_site' not in csv_data:
    csv_data['test_site'] = 'BNL'
if 'comment' not in csv_data:
    csv_data['comment'] = 'QC test'
print(csv_data)
with open(csv_file, mode="w", newline="", encoding='utf-8-sig') as file:
    writer = csv.writer(file)
    for key, value in csv_data.items():
        writer.writerow([key, value])
input('Please Install Panels on WIB Board')