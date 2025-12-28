import os
import sys
import time
import argparse

# from cts_ssh_FEMB import cts_ssh_FEMB
import cts_ssh_FEMB as cts

# Please Open Real_Time_Monitor.py and run first
# Then, Run this CTS_FEMB_QC_top.py
############################################################

#       01 Function Part                                   #
############################################################
ag = argparse.ArgumentParser()
ag.add_argument("folder", help="data folder", type=str)

args = ag.parse_args()
fdir = args.folder

def QC_Process(QC_TST_EN=None, input_info=None, save_path = "D:/FEMB_QC/Data/"):
    while True:
        QCresult = cts.cts_ssh_FEMB(root=save_path, QC_TST_EN=QC_TST_EN, input_info=input_info)
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


def FEMB_QC(input_info, save_path="D:/FEMB_QC/Data/"):
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
    QC_Process(QC_TST_EN=0, input_info=input_info, save_path = save_path)  # initial wib
    QC_Process(QC_TST_EN=1, input_info=input_info, save_path = save_path)  # initial FEMB I2C
    QC_Process(QC_TST_EN=2, input_info=input_info, save_path = save_path)  # assembly checkout
    # QC_Process(QC_TST_EN=3, input_info=input_info)  # QC
    # storage the log file
    QC_Process(QC_TST_EN=10, input_info=input_info, save_path = save_path)  # QC

    return 0


############################################################
#       02 Execute Part                                    #
############################################################

# Warm FEMB QC (Room Temperature)
# A Before Power On

csv_file = 'readback/femb_info.csv'
file_path = r'readback/femb_info.csv'
print("\033[35m" + "A_RT00 : Install FEMB boards, check the connection of Data and Power Cables" + "\033[0m")
input('Please Install FEMB #0 #1 #2 #3 into SLOT #0 #1 #2 #3; Enter to next ...')
# print("00 : Please Review the information")
print("\033[35m" + "A_RT01 : Please Review the information" + "\033[0m")
print("\033[35m" + "Example: SLOT0 : J00 --> J means Board version <A B C D E F G H J>" + "\033[0m")
print("\033[35m" + "Example: SLOT0 : J00 --> 00 means Board SN (must be in number)" + "\033[0m")

os.system(f'notepad {file_path}')
inform = cts.read_csv_to_dict(csv_file, 'RT')  # Warm test in Room Temperature
Next = input("\nEnter Any Key to continue \nEnter 'e' to exit\nEnter 'n' to skip the Warm QC")
if Next == 'n':
    print('No Warm Checkout execute!')
elif Next == 'e':
    Next2 = input("\nEnter Any Key to exit ...\nEnter 'N' to continue the LN test")
    if Next2 != 'y':
        sys.exit()
else:
    FEMB_QC(input_info=inform, save_path = fdir)
    print("Warm FEMB Checkout Done!")
    print("Please Turn OFF the Power!")

print('\n\n')



