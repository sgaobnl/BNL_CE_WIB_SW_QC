import os
import sys
import time

# from cts_ssh_FEMB import cts_ssh_FEMB
import cts_ssh_FEMB as cts

# Please Open Real_Time_Monitor.py and run first
# Then, Run this CTS_FEMB_QC_top.py
############################################################
#       01 Function Part                                   #
############################################################

def QC_Process(QC_TST_EN=None, input_info=None):
    while True:
        QCresult = cts.cts_ssh_FEMB(root="E:/FEMB_QC/Tested/", QC_TST_EN=QC_TST_EN, input_info=input_info)
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
    print("\033[35m" + "C1 : Room Temperature FEMB Quality Control Execution (takes < 1800s)" + "\033[0m")

    # ======== Button 00 WIB initial =====================
    # input("\033[35m" + 'Enter to Begin!' + "\033[0m")
    QC_Process(QC_TST_EN=0, input_info=input_info)  # initial wib

    # ======== Button 01 WIB FEMB ========================
    # input('Button#01 FEMB Initial SLOT')
    QC_Process(QC_TST_EN=1, input_info=input_info)  # initial FEMB I2C

    # ======== Button 02 Checkout ========================
    # input('Button#02 FEMB Assembly Checkout')
    time.sleep(1)
    QC_Process(QC_TST_EN=2, input_info=input_info)  # assembly checkout
    # ======== Button 03 QC ==============================
    # input('Button#03 FEMB Quality Control')
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
input('Please Install FEMB #0 #1 #2 #3 into SLOT #0 #1 #2 #3; Enter to next ...')
# print("00 : Please Review the information")
print("\033[35m" + "A_RT01 : Please Review the information" + "\033[0m")
os.system(f'notepad {file_path}')
inform = cts.read_csv_to_dict(csv_file, 'RT')  # Warm test in Room Temperature
Next = input("\nEnter Any Key to continue \nEnter 'e' to exit\nEnter 'n' to skip the Warm QC")
if Next == 'n':
    print('No Warm QC execute!')
elif Next == 'e':
    Next2 = input("\nEnter Any Key to exit ...\nEnter 'N' to continue the LN test")
    if Next2 != 'y':
        sys.exit()
else:
    FEMB_QC(inform)
    print("Warm FEMB QC Done!")
    print("Please Turn OFF the Power!")

print('\n\n')

# Cold FEMB QC (LN2)

print("\033[94m" + "A_LN2 : Liquid Nitrogen FEMB Quality Control Execution (takes < 1800s)" + "\033[0m")
print("\033[94m" + "Please set IMMERSE to fill the Liquid Nitrogen into Cold Box (takes about 30 minutes)" + "\033[0m")
input()

# A Before Power On
csv_file = 'femb_info.csv'
file_path = r'.\femb_info.csv'
print("\033[35m" + "A_LN00 : Put FEMB; Please check the connection of Data and Power Cables" + "\033[0m")
# print("00 : Please Review the information")
print("\033[35m" + "A_LN01 : Please Review the information" + "\033[0m")
os.system(f'notepad {file_path}')
infoln = cts.read_csv_to_dict(csv_file, 'LN')  # Cold test in Liquid Nitrogen
Next = input("\nEnter Any Key to continue \nEnter 'e' to exit\nEnter 'n' to skip the Cold QC")
if Next == 'n':
    print('No Cold QC execute!')
elif Next == 'e':
    Next2 = input("\nEnter Any Key to exit ...\nEnter 'N' to continue the LN test")
    if Next2 != 'y':
        sys.exit()
else:
    FEMB_QC(infoln)
    print("Cold FEMB QC Done!")
    print("Please Turn OFF the Power!")

