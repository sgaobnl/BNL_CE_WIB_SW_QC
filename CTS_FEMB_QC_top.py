import os
import sys
import time
import cts_ssh_FEMB as cts
from PIL import Image
import csv
from GUI.initial_csv import check_csv
from ast import literal_eval

# Please Open Real_Time_Monitor.py and run first
# Then, Run this CTS_FEMB_QC_top.py
############################################################
#       01 Function Part                                   #
############################################################

def QC_Process(QC_TST_EN=None, input_info=None):
    while True:
        QCresult = cts.cts_ssh_FEMB(root="D:/FEMB_QC/Data/", QC_TST_EN=QC_TST_EN, input_info=input_info)
        if QCresult != None:
            QCstatus = QCresult[0]
            badchips = QCresult[1]
            break
        else:
            print("139-> terminate, 2->debugging")
            userinput = input("Please contatc tech coordinator")
            if len(userinput) > 0:
                if "139" in userinput:
                    QCstatus = "Terminate"
                    badchips = []
                    break
                elif "2" in userinput[0]:
                    print("debugging, ")
                    input("click any key to start FEMB QC again ...")
    return QCstatus, badchips  # badchips range from 0 to7


def FEMB_QC(input_info):
    # B Power On Warm Interface Board
    print("\033[35m" + "B00 : Turn Power Supply on to Power On WIB" + "\033[0m")
    input("Enter to next ...\n")
    print("\033[35m" + "B01 : Please Wait the Fiber Converter Light on (30 second)" + "\033[0m")

    print("If Fiber Converter works, Enter to next ...\n")
    input()
    # first run
    # ###############STEP1#################################
    skts = [0, 1, 2, 3, 4, 5, 6, 7]

    # C FEMB QC
    print("\033[35m" + "C1 : FEMB Quality Control Execution (takes < 1800s)" + "\033[0m")

    # ======== Button 00 WIB initial =====================
    # input("\033[35m" + 'Enter to Begin!' + "\033[0m")
    QC_Process(QC_TST_EN=0, input_info=input_info)  # initial wib
    QC_Process(QC_TST_EN=1, input_info=input_info)  # initial FEMB I2C
    QC_Process(QC_TST_EN=2, input_info=input_info)  # assembly checkout
    QC_Process(QC_TST_EN=3, input_info=input_info)  # QC
    # storage the log file
    QC_Process(QC_TST_EN=10, input_info=input_info)  # QC

    return 0


############################################################
#       02 Execute Part                                    #
############################################################

# Warm FEMB QC (Room Temperature)
# A Before Power On

csv_file = 'femb_info.csv'
file_path = r'.\femb_info.csv'
print("\033[35m" + "A_RT00 : Install FEMB boards, check the connection of Data and Power Cables" + "\033[0m")
input_name = input('Please input your name: ')
Initial_Scaner = input("Initial Scaner. \n\tEnter Any Key to exit ...\n\tEnter 'H' to check help")
if (Initial_Scaner == 'H') or (Initial_Scaner == 'h'):
    image = Image.open('D:\GitHub\BNL_CE_WIB_SW_QC\BNL_CE_WIB_SW_QC\Help\Initial_Scaner.png')
    print('Close the picture to continue')
    image.show()
femb_id_0 = input('Scan FEMB ID in Slot #0\t')
femb_id_1 = input('Scan FEMB ID in Slot #1\t')
csv_data = {}
with open(csv_file, mode='r', newline='', encoding='utf-8-sig') as file:
    reader = csv.reader(file)
    for row in reader:
        if len(row) == 2:
            key, value = row
            csv_data[key.strip()] = value.strip()
print(csv_data)
if 'tester' not in csv_data:
    csv_data['tester'] = 'sgao'
else:
    csv_data['tester'] = input_name
if 'SLOT0' not in csv_data:
    csv_data['SLOT0'] = 'H01'
    print(232323232)
else:
    csv_data['SLOT0'] = femb_id_0
    print(femb_id_0)
if 'SLOT1' not in csv_data:
    csv_data['SLOT1'] = 'H02'
else:
    csv_data['SLOT1'] = femb_id_1
if 'SLOT2' not in csv_data:
    csv_data['SLOT2'] = ' '
if 'SLOT3' not in csv_data:
    csv_data['SLOT3'] = ' '
if 'test_site' not in csv_data:
    csv_data['test_site'] = 'BNL'
if 'toy_TPC' not in csv_data:
    csv_data['toy_TPC'] = 'y'
if 'comment' not in csv_data:
    csv_data['comment'] = 'QC test'
with open(csv_file, mode="w", newline="", encoding='utf-8-sig') as file:
    writer = csv.writer(file)
    for key, value in csv_data.items():
        writer.writerow([key, value])
inform = cts.read_csv_to_dict(csv_file, 'RT')
info_check = input('please review the test information. \n\tIf the info is not right, enter "m" to modify the info. \n\tIf the info is right, jsut enter to next')
if info_check == 'm':
    os.system(f'notepad {file_path}')
    inform = cts.read_csv_to_dict(csv_file, 'RT')  # Warm test in Room Temperature

input('Please Install FEMB #0 #1 #2 #3 into SLOT #0 #1 #2 #3; Enter to next ... \n')
# with open(csv_file, mode='w', newline='', encoding='utf-8-sig') as file:
#     writer = csv.DictWriter(file)
#     writer.writeheader()
#     writer = writer.writerows(csv_data)
# print("00 : Please Review the information")
# print("\033[35m" + "A_RT01 : Please Review the information" + "\033[0m")
# os.system(f'notepad {file_path}')
# inform = cts.read_csv_to_dict(csv_file, 'RT')  # Warm test in Room Temperature
Next = input("\nEnter Any Key to continue \nEnter 'e' to exit\nEnter 'n' to skip the Warm QC \n")
if Next == 'n':
    print('No Warm QC execute!')
elif Next == 'e':
    Next2 = input("\nEnter Any Key to exit ...\nEnter 'N' to continue the LN test \n")
    if Next2 != 'y':
        sys.exit()
else:
    FEMB_QC(input_info=inform)
    print("Warm FEMB QC Done!")
    print("Please Turn OFF the Power!")

print('\n\n')

# Cold FEMB QC (LN2)

print("\033[94m" + "A_LN2 : Liquid Nitrogen FEMB Quality Control Execution (takes < 1800s)" + "\033[0m")
print("\033[94m" + "Please set IMMERSE to fill the Liquid Nitrogen into Cold Box (takes about 30 minutes)\n" + "\033[0m")
print("\033[94m" + "If LEVEL = 3, Enter to next ..." + "\033[0m")
input()

# A Before Power On
csv_file = 'femb_info.csv'
file_path = r'.\femb_info.csv'
print("\033[35m" + "A_LN00 : Put FEMB; Please check the connection of Data and Power Cables" + "\033[0m")
# print("00 : Please Review the information")
print("\033[35m" + "A_LN01 : Please Review the information" + "\033[0m")
infoln = cts.read_csv_to_dict(csv_file, 'LN')
info_check = input('please review the test information. \n\tIf the info is not right, enter "m" to modify the info. \n\tIf the info is right, jsut enter to next')
if info_check == 'm':
    os.system(f'notepad {file_path}')
    infoln = cts.read_csv_to_dict(csv_file, 'LN')  # Warm test in Room Temperature
Next = input("\nEnter Any Key to continue \nEnter 'e' to exit\nEnter 'n' to skip the Cold QC")
if Next == 'n':
    print('No Cold QC execute!')
elif Next == 'e':
    Next2 = input("\nEnter Any Key to exit ...\nEnter 'y' to exit the LN test")
    if Next2 != 'y':
        sys.exit()
else:
    FEMB_QC(infoln)
    print("Cold FEMB QC Done!")
print("Please Turn OFF the Power!")

print("Please wait for Warm UP (45 Minutes)")
print("Enter to Final Quick Checkout")
input()
print("Final Quick Checkout (3 Minutes)")

Next = input("\nEnter Any Key to continue \nEnter 'e' to exit\nEnter 'n' to skip the Final Checkout")
if Next == 'n':
    print('No Final Checkout execute!')
elif Next == 'e':
    Next2 = input("\nEnter Any Key to exit ...\nEnter 'y' to exit the Final Checkout test")
    if Next2 != 'y':
        sys.exit()
else:
    print("\033[35m" + "B00 : Turn Power Supply on to Power On WIB" + "\033[0m")
    input("Enter to next ...\n")
    print("\033[35m" + "B01 : Please Wait the Fiber Converter Light on (30 second)" + "\033[0m")

    print("If Fiber Converter works, Enter to next ...\n")
    input()
    # first run
    # ###############STEP1#################################
    skts = [0, 1, 2, 3, 4, 5, 6, 7]

    # C FEMB QC
    print("\033[35m" + "C1 : FEMB Quality Control Execution (takes < 1800s)" + "\033[0m")

    # ======== Button 00 WIB initial =====================
    # input("\033[35m" + 'Enter to Begin!' + "\033[0m")
    QC_Process(QC_TST_EN=0, input_info=inform)  # initial wib
    QC_Process(QC_TST_EN=1, input_info=inform)  # initial FEMB I2C
    QC_Process(QC_TST_EN=2, input_info=inform)  # assembly checkout
    print("Final Checkout Done!")

print("Please Close all Power and Pick up FEMB CE boards")

