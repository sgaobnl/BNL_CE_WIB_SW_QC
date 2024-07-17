import os
# from cts_ssh_FEMB import cts_ssh_FEMB
import cts_ssh_FEMB as cts


############################################################
#       01 Function Part                                   #
############################################################

def FEMB_QC(QC_TST_EN):
    while True:
        QCresult = cts.cts_ssh_FEMB(root="E:/FEMB_QC/Tested/", QC_TST_EN=QC_TST_EN, input_info=info)
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


############################################################
#       02 Execute Part                                    #
############################################################

# A Before Power On
csv_file = 'femb_info.csv'
file_path = r'.\femb_info.csv'

print("\033[35m" + "A00 : Put FEMB; Please check the connection of Data and Power Cables" + "\033[0m")
input('Put FEMB#0 into SLOT#0; Enter to next ...')
input('Put FEMB#1 into SLOT#1; Enter to next ...')
input('Put FEMB#2 into SLOT#2; Enter to next ...')
input('Put FEMB#3 into SLOT#3; Enter to next ...')

# print("00 : Please Review the information")
print("\033[35m" + "A01 : Please Review the information" + "\033[0m")
os.system(f'notepad {file_path}')
info = cts.read_csv_to_dict(csv_file)

# B Power On Warm Interface Board
print("\033[35m" + "B00 : Turn Power Supply on to Power On WIB" + "\033[0m")
input("Enter to next ...")
print("\033[35m" + "B01 : Please Wait the Fiber Converter Light on (30 second)" + "\033[0m")

print("If Fiber Converter works, Enter to next ...")
input()
# first run
# ###############STEP1#################################
skts = [0, 1, 2, 3, 4, 5, 6, 7]

# C FEMB QC
print("\033[35m" + "C : FEMB Quality Control Excute (takes < 1800s)" + "\033[0m")

# ======== Button 00 WIB initial =====================
input('Enter to Begin!')
QCstatus, badchips = FEMB_QC(QC_TST_EN = 0) # initial wib

# ======== Button 01 WIB FEMB ========================
# input('Button#01 FEMB Initial SLOT')
FEMB_QC(QC_TST_EN = 1) # initial FEMB I2C

# ======== Button 02 Checkout ========================
# input('Button#02 FEMB Assembly Checkout')
FEMB_QC(QC_TST_EN = 2)  # assembly checkout

# ======== Button 03 QC ==============================
input('Button#03 FEMB Quality Control')
FEMB_QC(QC_TST_EN=3)  # QC

print("Done")
