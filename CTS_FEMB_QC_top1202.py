import os
import sys
import time
import cts_ssh_FEMB as cts
import csv
import colorama
from colorama import Fore, Style
import GUI.pop_window as pop
import GUI.State_List as state
from email.mime.text import MIMEText
import GUI.Rigol_DP800 as rigol
import GUI.send_email as send_email
import psutil
import signal
from datetime import datetime

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


sender = "bnlr216@gmail.com"
password = "vvef tosp minf wwhf"
receiver = "lke@bnl.gov"




wcdata_path    = r"D:\data\temp"
wcreport_path  = r"D:\data\temp"
wqdata_path    = r"D:\data\temp"
wqreport_path  = r"D:\data\temp"
lcdata_path    = r"D:\data\temp"
lcreport_path  = r"D:\data\temp"
lqdata_path    = r"D:\data\temp"
lqreport_path  = r"D:\data\temp"
fcdata_path    = r"D:\data\temp"
fcreport_path  = r"D:\data\temp"


colorama.init()
def QC_Process(path = "D:", QC_TST_EN=None, input_info=None):
    global data_path, report_path
    while True:
        QCresult = cts.cts_ssh_FEMB(root="{}/FEMB_QC/".format(path), QC_TST_EN=QC_TST_EN, input_info=input_info)
        if QCresult != None:
            QCstatus = QCresult[0]
            badchips = QCresult[1]
            data_path = QCresult[2]
            report_path = QCresult[3]
            break
        else:
            print("139-> terminate, 2->retest")
            send_email.send_email(sender, password, receiver, "Issue Found at {}".format(pre_info['test_site']),
                                  "Issue Found, Please Check the Detail")
            userinput = input("Please contact tech coordinator")
            if len(userinput) > 0:
                if "139" in userinput:
                    QCstatus = "Terminate"
                    badchips = []
                    data_path = []
                    report_path = []
                    break
                elif "2" in userinput[0]:
                    print("retest, ")
                    input("click any key to start again ...")
    return data_path, report_path  # badchips range from 0 to 7

def confirm(prompt):
    """简单 confirm，要求输入 confirm 才继续"""
    while True:
        print(prompt)
        print('Enter "confirm" to continue')
        com = input(Fore.YELLOW + '>> ' + Style.RESET_ALL)
        if com.lower() == "confirm":
            return True
        else:
            print("Retry Please")
            break

def safe_power_off(psu, current_threshold=0.2, max_attempts=5):
    """
    自动关闭WIB电源。自动尝试 max_attempts 次，如果电流仍然偏高，
    则进入人工确认模式并验证电流直到安全为止。
    """
    attempt = 0
    while True:
        time.sleep(1)
        # 测量两路电流
        total_i = 0
        for ch in (1, 2):
            v, i = psu.measure(ch)
            print(f"CH{ch}: {v:.3f} V, {i:.3f} A")
            total_i += i
        print(f"Total current: {total_i:.3f} A")
        # 尝试关断
        psu.turn_off_all()
        # 成功
        if total_i < current_threshold:
            print("Power is OFF successfully.")
            return True
        # 失败 → 自动重试
        attempt += 1
        print(f"Power off attempt {attempt}/{max_attempts} failed (current too high).")
        # 到达最大尝试 → 人工介入
        if attempt >= max_attempts:
            print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print("WARNING: Auto power-off failed after several attempts.")
            print("Manual power shutdown is required.")
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
            # 人工确认模式 + 验证
            while True:
                print("Please manually turn OFF the WIB power.")
                com = input(Fore.YELLOW + '>> ' + Style.RESET_ALL)
                if com.lower() == "confirm":
                    # 验证是否真的关电
                    v1, i1 = psu.measure(1)
                    v2, i2 = psu.measure(2)
                    if (i1 + i2) < current_threshold:
                        print("Manual power-off verified. Proceeding...")
                        return True
                    else:
                        print(f"Verification failed: Current still high ({i1 + i2:.3f} A)")
                        print("Please ensure power is OFF and retry.")
                else:
                    print("Retry Please")
        print("Retrying auto power off...\n")


def FEMB_QC(input_info):
    print("B01 : wait to Enable Fiber Converter [30 second]")
    time.sleep(30)
    print("B02 : Begin to Ping Warm Interface Board")
    QC_Process(path = input_info['top_path'], QC_TST_EN=77, input_info=input_info)  # initial wib
    # first run
    # ###############STEP1#################################
    skts = [0, 1, 2, 3, 4, 5, 6, 7]

    # C FEMB QC
    print("C1 : FEMB Quality Control Execution (takes < 1800s)")
    QC_Process(path = input_info['top_path'], QC_TST_EN=0, input_info=input_info)  # initial wib
    QC_Process(path = input_info['top_path'], QC_TST_EN=1, input_info=input_info)  # initial FEMB I2C
    QC_Process(path = input_info['top_path'], QC_TST_EN=2, input_info=input_info)  # assembly checkout
    QC_Process(path = input_info['top_path'], QC_TST_EN=3, input_info=input_info)  # QC
    QC_Process(path = input_info['top_path'], QC_TST_EN=6, input_info=input_info)  # QC
    QC_Process(path = input_info['top_path'], QC_TST_EN=10, input_info=input_info)  # QC
    return 0

print(ROOT_DIR)
technician_csv = os.path.join(ROOT_DIR, "init_setup.csv")
csv_file = os.path.join(ROOT_DIR, "femb_info.csv")
csv_file_implement = os.path.join(ROOT_DIR, "femb_info_implement.csv")

version = "HD"
# 创建空的CSV文件
if not os.path.exists(technician_csv):
    with open(technician_csv, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # 写入表头（可根据需要修改）
        writer.writerow(['TechnicianID', 'Lingyun Ke'])
        # 写入一些示例数据
        writer.writerow(['test_site', 'BNL'])
        writer.writerow(['top_path', '/home/dune/'])
        writer.writerow(['Email', 'LKE@BNL.GOV'])
    print(f"✅ Created and initialized: {technician_csv}")

if not os.path.exists(csv_file):
    open(csv_file, 'w').close()
    print(f"✅ Created: {csv_file}")

if not os.path.exists(csv_file_implement):
    open(csv_file_implement, 'w').close()
    print(f"✅ Created: {csv_file_implement}")

# 0.2 Input Tester Name
print('\n')
print(Fore.CYAN + "Welcome to CTS CE QC" + Style.RESET_ALL)

input_name = input('Please input your name: \n' + Fore.YELLOW + '>> ' + Style.RESET_ALL)
print('\n')

# check email
def get_email():
    while True:
        email1 = input('Please input your email address: \n'
                       + Fore.YELLOW + '>> ' + Style.RESET_ALL)

        email2 = input('Please input again to confirm: \n'
                       + Fore.YELLOW + '>> ' + Style.RESET_ALL)

        # 检查是否含 @
        if "@" not in email1:
            print(Fore.RED + "❌ Invalid email: missing '@' symbol!" + Style.RESET_ALL)
            continue

        # 检查是否一致
        if email1 != email2:
            print(Fore.RED + "❌ The two inputs do not match, please try again!" + Style.RESET_ALL)
            continue

        # 都通过
        print(Fore.GREEN + "✔ Email confirmed!" + Style.RESET_ALL)
        return email1
receiver = get_email()


# 0.3 pop window 1 Initial Checkout List Confirm
pop.show_image_popup(
    title="Initial Checkout List Confirm",
    image_path = os.path.join(ROOT_DIR, "GUI", "output_pngs", "2.png")
)

# 0.4 pop window 2 Initial Checkout List Confirm
pop.show_image_popup(
    title="Checklist for accessory tray #1",
    image_path = os.path.join(ROOT_DIR, "GUI", "output_pngs", "3.png")
)

# 0.5 pop window 3 Initial Checkout List Confirm
pop.show_image_popup(
    title="Checklist for accessory tray #2",
    image_path = os.path.join(ROOT_DIR, "GUI", "output_pngs", "4.png")
)



hour = datetime.now().hour
if 1 <= hour <= 11:
    LN2 = '1800 [at Morning]'
else:
    LN2 = '1200 [at Afternoon]'
# 0.6 LN2 Refill Notification Logic
while True:
    # print("Please Check if the Dewar Level Higher than {}".format(LN2))
    print('Was 50L dewar refilled to {}? (Y/N)'.format(LN2))
    result = input(Fore.YELLOW + '>> ' + Style.RESET_ALL)
    if (result == 'n') or (result == 'N'):
        pop.show_image_popup(
            title="Test Dewar Refill",
            image_path=os.path.join(ROOT_DIR, "GUI", "output_pngs", "5.png")
        )
    elif (result == 'y') or (result == 'Y'):
        break

state_list = state.select_test_states()
print("Items {} are selected".format(state_list))


# 1.11 Select Phase 1
# if 1, fill the info
# else, load info from csv
if 1 in state_list:
    print("=====================================================================")
    print("=============     Phase 1. Preparation                   ============")
    print("=====================================================================")
    print('\n')

    # 1.12 Install Bottom CE box Logic
    while True:
        print('         Step 1.1 Assemble the CE box in the ' + Fore.CYAN + 'Bottom slot' + Style.RESET_ALL + ' (Cable#1)')
        print("         Pop 1.111: Bottom slot CE Box Visual Inspection")
        my_options = ["Install MiniSAS Cable and Clamp", "Install Test Cover", "Install Power Cable",
                      "Install Toy_TPCs and Cables", "Insert into Bottom Slot"]
        pop01 = pop.show_image_popup(
            # my_options,
            title="Bottom slot Visual Inspection",
            image_path=os.path.join(ROOT_DIR, "GUI", "output_pngs", "6.png")
        )
        while True:
            print('         Step 1.11 Please ' + Fore.CYAN + 'Scan the QR ID' + Style.RESET_ALL + ' 1st time')
            femb_id_00 = input(Fore.YELLOW + '         >> ' + Style.RESET_ALL)
            if ("IO-1826-1" in femb_id_00) or ("IO-1865-1" in femb_id_00):
                break
            else:
                print("no FEMB ID Detected, retry ...")
        while True:
            print('         Step 1.12 Please ' + Fore.CYAN + 'Scan the QR ID' + Style.RESET_ALL + ' 2nd time')
            femb_id_01 = input(Fore.YELLOW + '         >> ' + Style.RESET_ALL)
            if ("IO-1826-1" in femb_id_01) or ("IO-1865-1" in femb_id_01):
                break
            else:
                print("no FEMB ID Detected, retry ...")
        if femb_id_01 == femb_id_00:
            print(Fore.GREEN + "         The QR ID for bottom CE box has been recorded" + Style.RESET_ALL)
            femb_id_0 = femb_id_01
        else:
            print(Fore.MAGENTA + '         Please scan the QR ID a 3rd time and check carefully' + Style.RESET_ALL)
            while True:
                while True:
                    print("Scan Bottom QR code (try 1): ")
                    femb_id_2 = input(Fore.YELLOW + '>> ' + Style.RESET_ALL).strip()
                    if ("IO-1826-1" in femb_id_2) or ("IO-1865-1" in femb_id_2):
                        break
                    else:
                        print("no FEMB ID Detected, retry ...")
                while True:
                    print("Scan Bottom QR code (try 2): ")
                    femb_id_3 = input(Fore.YELLOW + '>> ' + Style.RESET_ALL).strip()
                    if ("IO-1826-1" in femb_id_3) or ("IO-1865-1" in femb_id_3):
                        break
                    else:
                        print("no FEMB ID Detected, retry ...")

                if femb_id_2 == femb_id_3:
                    print(Fore.GREEN + "QR codes match. Proceeding ..." + Style.RESET_ALL)
                    femb_id_0 = femb_id_2
                    break
                else:
                    print(Fore.RED + "QR codes do not match. Please scan again." + Style.RESET_ALL)
        femb_id_0 = femb_id_0.replace('/', '_')
        if "1826" in femb_id_0:
            version = "HD"
        else:
            version = "VD"

        while True:
            print(Fore.RED + "         Step 1.13 Please confirm Top FEMB SN is {} (y/n) : ".format(femb_id_0) + Style.RESET_ALL)
            user_input = input(Fore.YELLOW + '         >> ' + Style.RESET_ALL)
            if user_input == 'y':
                print(Fore.GREEN + "         Bottom Slot confirm ..." + Style.RESET_ALL)
                exit_outer = True
                break             # exit the loop
            elif user_input == 'n':
                exit_outer = False
                break
                print('ID wrong, please scan ID again')
        if 'exit_outer' in locals() and exit_outer:
            break  # 真正跳出外层 while



    print("         Step 1.14 Continue assembly the CE box into the Bottom Slot.")
    # pop02
    print("         Pop 1.15: Bottom slot assembly instruction")
    my_options = ["Install MiniSAS Cable and Clamp", "Install Test Cover", "Install Power Cable", "Install Toy_TPCs and Cables", "Insert into Bottom Slot"]
    if version == "VD":
        pop01 = pop.show_image_popup(
            title="Bottom slot assembly instruction",
            image_path=os.path.join(ROOT_DIR, "GUI", "output_pngs", "7.png")
        )
    else:
        pop01 = pop.show_image_popup(
            title="Bottom slot assembly instruction",
            image_path=os.path.join(ROOT_DIR, "GUI", "output_pngs", "9.png")
        )

    print('\n')

    while True:
        print('         Step 1.2 Assemble the CE box in the ' + Fore.CYAN + 'Top slot' + Style.RESET_ALL + ' (Cable#2)')
        print("         Pop 1.211: Top slot CE Box Visual Inspection")
        my_options = ["Install MiniSAS Cable and Clamp", "Install Test Cover", "Install Power Cable",
                      "Install Toy_TPCs and Cables", "Insert into Top Slot"]
        pop01 = pop.show_image_popup(
            title="Top slot Visual Inspection",
            image_path=os.path.join(ROOT_DIR, "GUI", "output_pngs", "6.png")
        )
        while True:
            print('         Step 1.21 Please ' + Fore.CYAN + 'Scan the QR ID' + Style.RESET_ALL + ' 1st time')
            femb_id_10 = input(Fore.YELLOW + '         >> ' + Style.RESET_ALL)
            if ("IO-1826-1" in femb_id_10) or ("IO-1865-1" in femb_id_10):
                break
            else:
                print("no FEMB ID Detected, retry ...")

        while True:
            print('         Step 1.22 Please ' + Fore.CYAN + 'Scan the QR ID' + Style.RESET_ALL + ' 2nd time')
            femb_id_11 = input(Fore.YELLOW + '         >> ' + Style.RESET_ALL)
            if ("IO-1826-1" in femb_id_11) or ("IO-1865-1" in femb_id_11):
                break
            else:
                print("no FEMB ID Detected, retry ...")
        if femb_id_11 == femb_id_10:
            print(Fore.GREEN + "         The QR ID for top CE box has been recorded" + Style.RESET_ALL)
            femb_id_1 = femb_id_11
        else:
            print(Fore.MAGENTA + '      Please scan the QR ID a 3rd time and check carefully' + Style.RESET_ALL)

            while True:
                while True:
                    print("Scan Top QR code (try 1): ")
                    femb_id_2 = input(Fore.YELLOW + '>> ' + Style.RESET_ALL)
                    if ("IO-1826-1" in femb_id_2) or ("IO-1865-1" in femb_id_2):
                        break
                    else:
                        print("no FEMB ID Detected, retry ...")
                while True:
                    print("Scan Top QR code (try 2): ")
                    femb_id_3 = input(Fore.YELLOW + '>> ' + Style.RESET_ALL)
                    if ("IO-1826-1" in femb_id_3) or ("IO-1865-1" in femb_id_3):
                        break
                    else:
                        print("no FEMB ID Detected, retry ...")

                if femb_id_2 == femb_id_3:
                    print(Fore.GREEN + "QR codes match. Proceeding..." + Style.RESET_ALL)
                    femb_id_1 = femb_id_2
                    break
                else:
                    print(Fore.RED + "QR codes do not match. Please scan again." + Style.RESET_ALL)


        femb_id_1 = femb_id_1.replace('/', '_')
        if "1826" in femb_id_1:
            version = "HD"
        else:
            version = "VD"
        while True:
            print(Fore.RED + "         Step 1.23 Please confirm Top FEMB SN is {} (y/n) : ".format(femb_id_1) + Style.RESET_ALL)
            user_input = input(Fore.YELLOW + '         >> ' + Style.RESET_ALL)
            if user_input == 'y':
                print(Fore.GREEN + "         Top Slot confirm ..." + Style.RESET_ALL)
                exit_outer = True
                break             # exit the loop
            elif user_input == 'n':
                exit_outer = False
                break
                print('ID wrong, please scan ID again')
        if 'exit_outer' in locals() and exit_outer:
            break  # 真正跳出外层 while

    # pop03
    print("         Step 1.24 Continue assembly the CE box into the Top Slot.")
    print("         Pop 1.25: Top slot assembly instruction")
    my_options = ["Install MiniSAS Cable and Clamp", "Install Test Cover", "Install Power Cable", "Install Toy_TPCs and Cables", "Insert into Bottom Slot"]
    if version == "HD":
        pop01 = pop.show_image_popup(
            # my_options,
            title="Top slot assembly instruction",
            image_path=os.path.join(ROOT_DIR, "GUI", "output_pngs", "10.png")
        )
    else:
        pop01 = pop.show_image_popup(
            # my_options,
            title="Top slot assembly instruction",
            image_path=os.path.join(ROOT_DIR, "GUI", "output_pngs", "8.png")
        )

        # print("You selected:", pop03)

    # 1.14 Update Record CSV
    print('\n')
    csv_data = {}
    with open(csv_file, mode='r', newline='', encoding='utf-8-sig') as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) == 2:
                key, value = row
                csv_data[key.strip()] = value.strip()
    with open(technician_csv, mode='r', newline='', encoding='utf-8-sig') as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) == 2:
                key, value = row
                csv_data[key.strip()] = value.strip()
    if 'tester' not in csv_data:
        csv_data['tester'] = 'sgao'
    else:
        csv_data['tester'] = input_name
    if 'SLOT0' not in csv_data:
        csv_data['SLOT0'] = 'H01'
    else:
        csv_data['SLOT0'] = femb_id_0
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
    if 'top_path' not in csv_data:
        csv_data['top_path'] = 'D:'
    with open(csv_file, mode="w", newline="", encoding='utf-8-sig') as file:
        writer = csv.writer(file)
        for key, value in csv_data.items():
            writer.writerow([key, value])
    inform = cts.read_csv_to_dict(csv_file, 'RT')

# 2 Connect with CTS Notification
if 2 in state_list:
    # 2.1 Check CTS Chamber
    while True:
        print("Please confirm the chamber is empty, and type in 'I confirm the chamber is empty' to completed ...")
        com = input(Fore.YELLOW + '>> ' + Style.RESET_ALL)
        if com.lower() == 'i confirm the chamber is empty':
            print('Great, Please install the CE to CTS')
            break

    # 2.2 Connect the Cables
    print('Pop05: Please Connect the CE Test Structure with CTS WIB')
    my_options = ["Open CTS Cover", "Place the CE boxes structure"]
    pop04 = pop.show_image_popup(
        # my_options,
        title="Pop05: Pop-up window Instruction of placing CE boxes into crate",
        image_path = os.path.join(ROOT_DIR, "GUI", "output_pngs", "11.png")
    )

    # 2.2 Connect the Cables
    print('Pop05: Please Connect the CE Test Structure with CTS WIB')
    my_options = ["Open CTS Cover", "Place the CE boxes structure"]
    pop04 = pop.show_image_popup(
        # my_options,
        title="Pop05: Pop-up window Instruction of placing CE boxes into crate",
        image_path=os.path.join(ROOT_DIR, "GUI", "output_pngs", "12.png")
    )


    # print("Pop06: Pop-up window Instruction of WIB cable connection")
    # my_options = ["Bottom Data Cable in Slot B", "Top Data Cable in Slot T", "install Data Cable clamp", "Install Bottom Power Cable", "Install Top Power Cable"]
    # pop05 = pop.show_image_popup(
    #     # my_options,
    #     title="Pop06: Pop-up window Instruction of WIB cable connection",
    #     image_path="./GUI/output_pngs/11.png"  # local image file
    # )

    # 2.3 Close the Cover of CTS
    print("Pop07: Pop-up window Instruction of closing cover")
    my_options = ["Close the CTS Cover"]
    pop06 = pop.show_image_popup(
        # my_options,
        title="Pop07: Pop-up window Instruction of closing cover",
        image_path = os.path.join(ROOT_DIR, "GUI", "output_pngs", "13.png")
    )
    with open(csv_file, 'r') as source:
        with open(csv_file_implement, 'w') as destination:
            destination.write(source.read())

else:
    # 1.21 load Record CSV directly
    print('\n')
    csv_data = {}
    inform = cts.read_csv_to_dict(csv_file_implement, 'RT', True)
    while True:
        print(
            '[If the info is not right, enter "m" to modify the info.] \n[If the info is right, just enter "confirm" to next]')
        phase_2_2 = input(Fore.YELLOW + '>> ' + Style.RESET_ALL)
        if phase_2_2 == 'm':
            os.system(f'gedit "{csv_file_implement}"')
            inform = cts.read_csv_to_dict(csv_file_implement, 'RT', True)  # Warm test in Room Temperature
        elif phase_2_2 == 'confirm':
            inform = cts.read_csv_to_dict(csv_file_implement, 'RT')
            break

pre_info = cts.read_csv_to_dict(csv_file_implement, 'RT')
send_email.send_email(sender, password, receiver, "New Test Group at {}".format(pre_info['test_site']), "QC has begun.\nPlease run CTS_Top.desktop to prepare the new test group.")

# 3 Warm QC Test
if any(x in state_list for x in [3, 4, 5]):
    psu = rigol.RigolDP800()

if 3 in state_list:
    # 3.1 information load
    inform = cts.read_csv_to_dict(csv_file_implement, 'RT')
    while True:
        # 3.2 action select
        print(Fore.CYAN + "\n[Enter 'y' to continue] \n[Enter 'e' to exit]\t  \n[Enter 's' to skip the Warm QC to Cold]" + Style.RESET_ALL)
        Next = input(Fore.YELLOW + '>> ' + Style.RESET_ALL)
        # 3.21 skip the warm and do cold test directly
        if Next == 's':
            print("Do you want to skip the Warm?")
            print("Enter 'confirm' to skip")
            com = input(Fore.YELLOW + '>> ' + Style.RESET_ALL)
            if com == "confirm":
                print("Skip the Warm Test ...")
                break
            else:
                print("Retry Please")
        # 3.22 exit the whole QC script
        elif Next == 'e':
            # Next2 = input("\nEnter Any Key to exit ...\nEnter 'N' to continue the Warm test \n")
            # if Next2 != 'y':
            print("Do you want to Exit the Test?")
            print("Enter 'confirm' to Exit")
            com = input(Fore.YELLOW + '>> ' + Style.RESET_ALL)
            if com == "confirm":
                print("Exit QC ...")
                sys.exit()
            else:
                print("Retry Please")
        # 3.23 exit the whole QC script
        elif Next == 'y':
            print("Do you want to begin the Warm QC?")
            print("Enter 'confirm' to begin")
            com = input(Fore.YELLOW + '>> ' + Style.RESET_ALL)
            if com == "confirm":
                print('\n')
                print("=====================================================================")
                print("=============     Phase 2 Warm QC Begin                  ============")
                print("=====================================================================")
                print('\n')
                # pop07
                # 3.231 power on WIB
                print("Warm Power ON WIB power supply")
                psu.set_channel(1, 12.0, 3.0, on=True)
                psu.set_channel(2, 12.0, 3.0, on=True)
                print("B01 : build Ethernet communication between PC and WIB[30 second]")
                time.sleep(35)
                # 3.232 Ping WIB
                print("B02 : Ping Warm Interface Board")
                QC_Process(path=inform['top_path'], QC_TST_EN=77, input_info=inform)  # ping wib
                print('Activate Next Group')
                terminal_path = os.path.join(ROOT_DIR, "CTS_FEMB_QC_top.py")
                # run_in_new_terminal(terminal_path, geometry="100x25+960+200")
                # 3.233 WIB Initial [time, startup, power connection, cable connection]
                print("C1 : Warm Interface Board Initial (takes < 120s)")
                QC_Process(path=inform['top_path'], QC_TST_EN=0, input_info=inform)  # initial wib
                QC_Process(path=inform['top_path'], QC_TST_EN=1, input_info=inform)  # initial FEMB I2C
                # 3.234 Warm Checkout
                print("C2 : FEMB Checkout Execution (takes < 180s)")
                wcdata_path, wcreport_path = QC_Process(path=inform['top_path'], QC_TST_EN=2, input_info=inform)  # assembly checkout
                # 3.235 Warm QC Test
                print("C3 : FEMB Quality Control Execution (takes < 1800s)")
                wqdata_path, wqreport_path = QC_Process(path=inform['top_path'], QC_TST_EN=3, input_info=inform)  # qc
                # 3.236 WIB Linux System Close
                QC_Process(path=inform['top_path'], QC_TST_EN=6, input_info=inform)  # Power Off Linux
                print("Warm Power OFF WIB power supply")
                # 3.237 Power Off WIB
                while True:
                    total_i = 0
                    for ch in (1, 2):
                        v, i = psu.measure(ch)
                        print(f"CH{ch}: {v:.3f} V, {i:.3f} A")
                        total_i += i  # 累加电流
                    print(f"Total current: {total_i:.3f} A")
                    psu.turn_off_all()
                    if total_i < 0.2:
                        break
                    else:
                        print('power off again')
                break
            else:
                print("Retry Please")
    print('\n\n')
    print("Warm QC Done !")
    print("---------------------------------------------------------------------")
    print('\n')

    # 3.3 Human confirm the Power is Off
    while True:
        print("Please check the Power is OFF")
        print('enter "confirm" to continue')
        com = input(Fore.YELLOW + '>> ' + Style.RESET_ALL)
        if com == 'confirm':
            print('Great, WIB Power OFF')
            break

# 4 Cold QC Test
# ------------------------- Phase 4 --------------------------
if 4 in state_list:

    # ---------------------------------------------------------
    # 4.1 CTS Cooling Down (Cold Down)
    # ---------------------------------------------------------
    print("Pop09: CTS Cool Down Instruction")
    pop.show_image_popup(
        title="Pop09: CTS Cool Down – Power ON",
        image_path=os.path.join(ROOT_DIR, "GUI", "output_pngs", "14.png")
    )

    print("Please cool down the CTS.")
    send_email.send_email(
        sender, password, receiver,
        f"Cold Down Request [{pre_info['test_site']}]",
        '"Switch to COLD for 5 min", "Switch to IMMENSE, wait for LN2 to reach Level 3", "Double confirm heat LED OFF"'
    )

    # Ask whether to wait 30 min cool down
    while True:
        do_sleep = input("Do you need to wait for LN2 refill? (y/n): ").lower()

        if do_sleep == 'y':
            print("Enter 'confirm' to wait 30 minutes for CTS cool down.")
            com = input(Fore.YELLOW + '>> ' + Style.RESET_ALL)
            if com == "confirm":
                time.sleep(1800)
                send_email.send_email(
                    sender, password, receiver,
                    f"CTS cold down completed [{pre_info['test_site']}]",
                    '"Please double confirm LN2 reach Level 3, heat LED OFF"'
                )
                break
            else:
                print("Invalid input. Retry.\n")

        elif do_sleep == 'n':
            print("Enter 'confirm' to skip waiting.")
            com = input(Fore.YELLOW + '>> ' + Style.RESET_ALL)
            if com == "confirm":
                break
            else:
                print("Invalid input. Retry.\n")

    # ---------------------------------------------------------
    # 4.2 Confirm LN2 Level
    # ---------------------------------------------------------
    print("\n===== CTS Cold Down Status =====")
    print("Please ensure LN2 level has reached LEVEL 3 and the heat LED is OFF.")

    while True:
        print("Enter 'confirm' once CTS is fully cooled down:")
        com = input(Fore.YELLOW + '>> ' + Style.RESET_ALL)
        if com.lower() == 'confirm':
            print("CTS Cold Down confirmed.")
            break
        else:
            print("Not confirmed. Please check again.\n")

    # ---------------------------------------------------------
    # 4.3 Load Cold QC Info
    # ---------------------------------------------------------
    infoln = cts.read_csv_to_dict(csv_file_implement, 'LN')

    # ---------------------------------------------------------
    # 4.4 Cold QC Action Selection
    # ---------------------------------------------------------
    while True:
        print(Fore.RED +
              "\n[Enter 'y' to start Cold QC]"
              "\n[Enter 's' to skip Cold QC]"
              "\n[Enter 'e' to exit test]" + Style.RESET_ALL)
        Next = input(Fore.YELLOW + '>> ' + Style.RESET_ALL)

        # ---- Skip Cold QC ----
        if Next == 's':
            print("Enter 'confirm' to skip Cold QC:")
            com = input(Fore.YELLOW + '>> ' + Style.RESET_ALL)
            if com.lower() == "confirm":
                print("Skipping Cold QC...")
                break
            else:
                print("Retry.\n")

        # ---- Exit Test ----
        elif Next == 'e':
            print("Enter 'confirm' to exit:")
            com = input(Fore.YELLOW + '>> ' + Style.RESET_ALL)
            if com.lower() == "confirm":
                print("Exiting QC program...")
                sys.exit()
            else:
                print("Retry.\n")

        # ---- Start Cold QC ----
        elif Next == 'y':
            print("Enter 'confirm' to begin Cold QC:")
            com = input(Fore.YELLOW + '>> ' + Style.RESET_ALL)
            if com.lower() != "confirm":
                print("Retry.\n")
                continue

            print("\n===============================================")
            print("==== Phase 4: Cold FEMB Quality Control =======")
            print("===============================================\n")

            # Power ON WIB
            print("Power ON: WIB Supply")
            psu.set_channel(1, 12.0, 3.0, on=True)
            psu.set_channel(2, 12.0, 3.0, on=True)
            print("Initializing ethernet link (35 seconds)...")
            time.sleep(35)

            # Cold QC Steps
            print("B02 : Ping WIB")
            QC_Process(path=infoln['top_path'], QC_TST_EN=77, input_info=infoln)

            print("C1 : WIB Initial (120 sec)")
            QC_Process(path=infoln['top_path'], QC_TST_EN=0, input_info=infoln)
            QC_Process(path=infoln['top_path'], QC_TST_EN=1, input_info=infoln)

            print("C2 : FEMB Cold Checkout (180 sec)")
            QC_Process(path=infoln['top_path'], QC_TST_EN=2, input_info=infoln)

            print("C3 : FEMB Cold QC (1800 sec)")
            QC_Process(path=infoln['top_path'], QC_TST_EN=3, input_info=infoln)

            print("Closing WIB Linux system...")
            QC_Process(path=infoln['top_path'], QC_TST_EN=6, input_info=infoln)

            # ---------------- Power Off WIB (with retries) ----------------
            max_attempts = 5
            attempt = 0

            while True:
                total_i = 0
                print("\nChecking WIB current...")

                for ch in (1, 2):
                    v, i = psu.measure(ch)
                    print(f"CH{ch}: {v:.3f} V, {i:.3f} A")
                    total_i += i

                print(f"Total current: {total_i:.3f} A")
                psu.turn_off_all()

                if total_i < 0.2:
                    print("WIB Power OFF successful.")
                    break

                attempt += 1
                print(f"Power off attempt {attempt}/{max_attempts} failed.")

                if attempt >= max_attempts:
                    print("\n!!! Manual intervention required !!!")
                    while True:
                        print("Please manually power off the WIB.")
                        print("Enter 'confirm' when done:")
                        com = input(Fore.YELLOW + '>> ' + Style.RESET_ALL)
                        if com.lower() == "confirm":
                            print("Manual confirmation received.")
                            break
                    break  # end power-off loop

            print("\nCold QC Completed.\n")
            break  # exit Phase 4 loop

    # ---------------------------------------------------------
    # 4.5 Warm Up CTS
    # ---------------------------------------------------------
    print("Pop12: CTS Warm Up")
    pop.show_image_popup(
        title="Pop12: CTS Warm-Up (60 minutes)",
        image_path=os.path.join(ROOT_DIR, "GUI", "output_pngs", "15.png")
    )

    send_email.send_email(
        sender, password, receiver,
        f"Cold QC Finished [{pre_info['test_site']}]",
        "Please switch CTS to WARM GAS and wait 60 minutes."
    )

    while True:
        do_sleep = input("Do you want to wait 60 min warm-up? (y/n): ").lower()
        if do_sleep == 'y':
            print("Enter 'confirm' to start warm-up timer (60 min).")
            com = input(Fore.YELLOW + '>> ' + Style.RESET_ALL)
            if com == "confirm":
                time.sleep(3600)
                break
        elif do_sleep == 'n':
            print("Enter 'confirm' to skip warm-up.")
            com = input(Fore.YELLOW + '>> ' + Style.RESET_ALL)
            if com == "confirm":
                break
        print("Retry.\n")

    send_email.send_email(
        sender, password, receiver,
        f"CTS Warm-Up Completed [{pre_info['test_site']}]",
        "Please proceed to Final Checkout."
    )


# ------------------------- Phase 4 --------------------------
if 5 in state_list:

    print("=====================================================================")
    print("=============     Phase 4:   FEMB Final Checkout         ============")
    print("=============     [takes < 300s]                         ============")
    print("=====================================================================")
    inform = cts.read_csv_to_dict(csv_file_implement, 'RT')
    # Final Checkout 选项
    while True:
        print("\nEnter 'y' to continue")
        print("Enter 'e' to exit")
        print("Enter 's' to skip the Final Checkout")
        Next = input(Fore.YELLOW + '>> ' + Style.RESET_ALL)

        # ----------------- Skip Final Checkout -----------------
        if Next == 's':
            if confirm("Do you want to skip the Final Checkout?"):
                print("Skip the Final Checkout ...")
                break

        # ------------------------- Exit -------------------------
        elif Next == 'e':
            if confirm("Do you want to Exit the Test?"):
                print("Exit ...")
                sys.exit()

        # ----------------------- Begin Phase 4 -------------------
        elif Next == 'y':
            if not confirm("Do you want to begin the Final Checkout?"):
                continue

            print('\n')
            print("=====================================================================")
            print("=============     Phase 4 Post QC Checkout               ============")
            print("=====================================================================")
            print('\n')

            # 5.431 Power on WIB
            print("Post QC Checkout Power ON WIB power supply")
            psu.set_channel(1, 12.0, 3.0, on=True)
            psu.set_channel(2, 12.0, 3.0, on=True)

            print("B01 : Build Ethernet communication between PC and WIB [35 second]")
            time.sleep(35)

            # 5.432 Ping WIB
            print("B02 : Begin to Ping WIB")
            QC_Process(path=inform['top_path'], QC_TST_EN=77, input_info=inform)

            # 5.433 WIB Initial
            print("C1 : WIB Initial (takes < 120s)")
            QC_Process(path=inform['top_path'], QC_TST_EN=0, input_info=inform)
            QC_Process(path=inform['top_path'], QC_TST_EN=1, input_info=inform)

            # 5.434 FEMB Checkout Execution
            print("C2 : FEMB Checkout Execution (takes < 180s)")
            fcdata_path, fcreport_path = QC_Process(
                path=inform['top_path'], QC_TST_EN=2, input_info=inform
            )

            # 5.435 FEMB QC Execution
            print("C3 : FEMB Quality Control Execution (takes < 1800s)")
            QC_Process(path=inform['top_path'], QC_TST_EN=6, input_info=inform)

            # --------------------------- Finish -------------------------
            print("\033[35m" + "=========================================================" + "\033[0m")
            print("\033[35m" + "=============     Final Checkout Done!       ============" + "\033[0m")
            print("\033[94m" + "=============     Please Power Off the WIB!  ============" + "\033[0m")
            print("\033[35m" + "=========================================================" + "\033[0m")

            # 自动 / 人工 power off（已合并）
            safe_power_off(psu)

            break  # 结束 Phase 4 主循环


    # pop15
    # print("Pop15: Post-Cold checkout is done →  power off WIB power supply Double confirmation ! ")
    # my_options = ["Power Off WIB"]
    # pop15 = pop.show_image_popup(
    #     # my_options,
    #     title="Pop15: Post checkout is done →  power off WIB power supply Double confirmation ! ",
    #     image_path="./GUI/picture01.png"  # local image file
    # )



# 6 Disassembly
# ------------------------- Phase 6 --------------------------
if 6 in state_list:

    print("\033[94m" + "Please power OFF the CTS." + "\033[0m")
    print("\033[94m" + "Remove and disassemble the FEMB CE boxes." + "\033[0m")

    # ---------------- Pop16 ----------------
    print("Pop16: Move CE boxes out of chamber")
    pop.show_image_popup(
        title="Pop16: Move CE boxes out of chamber",
        image_path=os.path.join(ROOT_DIR, "GUI", "output_pngs", "16.png")
    )

    # Helper: 返回正确的图片路径
    def get_cebox_image(version):
        """Return image path for CE box disassembly based on VD / HD."""
        return os.path.join(
            ROOT_DIR, "GUI", "output_pngs",
            "17.png" if version == "VD" else "18.png"
        )

    img_cebox = get_cebox_image(version)

    # ---------------- Pop17 ----------------
    print("Pop17: Disassembly Top CE Box")
    pop.show_image_popup(
        title="Pop17: Disassembly Top CE Box",
        image_path=img_cebox
    )

    # ---------------- Pop18 ----------------
    print("Pop18: Disassembly Bottom CE Box")
    pop.show_image_popup(
        title="Pop18: Disassembly Bottom CE Box",
        image_path=img_cebox
    )

    # ---------------- Pop19 ----------------
    while True:
        print("Pop19: Return all accessories to their original positions.")
        pop.show_image_popup(
            title="Pop19: Return Accessories to Their Original Position",
            image_path=os.path.join(ROOT_DIR, "GUI", "output_pngs", "19.png")
        )

        print("Please confirm all accessories have been returned.")
        print('Enter "confirm" to continue.')
        order = input(Fore.YELLOW + '>> ' + Style.RESET_ALL)

        if order.lower() == "confirm":
            print("Accessories check completed. Thank you!")
            break
        else:
            print("Not confirmed. Please verify again.\n")

if any(x in state_list for x in [3, 4, 5]):
    psu.close()
print("QC Test Cycle Done!")
print("Please Prepared Next Test Cycle!")







time.sleep(2)

paths = [
    wcdata_path, wcreport_path, wqdata_path, wqreport_path,
    lcdata_path, lcreport_path, lqdata_path, lqreport_path,
    fcdata_path, fcreport_path
]

def check_fault_files(paths, show_p_files=False):

    f_files = []   # 带 _F_ 的文件
    p_files = []   # 带 _P_ 的文件

    for path in paths:
        if not os.path.isdir(path):
            continue

        for root, dirs, files in os.walk(path):
            for file in files:
                if "_F_" in file:
                    f_files.append(os.path.join(root, file))
                elif "_P_" in file:
                    p_files.append(os.path.join(root, file))

    # 如果没有 _F_ 文件 → 判定 PASS
    if not f_files:
        print("Result：The Group PASS")
        if show_p_files:
            print("\n包含 '_P_' 的文件：")
            for pf in p_files:
                print(pf)
        return

    # 有 _F_ 文件 → 判断是否有故障
    print("False test Found")
    for ff in f_files:
        print(ff)

    fault_found = False
    for ff in f_files:
        try:
            with open(ff, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                # 判断是否有故障标记（根据你实际情况调整）
                if "fault" in content.lower() or "error" in content.lower():
                    fault_found = True
                    break
        except Exception as e:
            print(f"无法读取文件：{ff}, 错误：{e}")

    if fault_found:
        print("\n结果：FAIL（'_F_' 文件中检测到故障）")
    else:
        print("\n结果：PASS（'_F_' 文件中未检测到故障）")

    # 如果需要打印 P 文件
    if show_p_files:
        print("\n包含 '_P_' 的文件：")
        for pf in p_files:
            print(pf)
check_fault_files(paths, show_p_files=True)



def close_terminal():
    # 当前进程
    p = psutil.Process(os.getpid())

    # 逐层向上找到终端窗口进程
    while True:
        parent = p.parent()
        if parent is None:
            break

        # GNOME Terminal 常见名称
        if parent.name() in ["gnome-terminal-server", "gnome-terminal", "konsole", "xfce4-terminal"]:
            # 关闭终端窗口
            os.kill(parent.pid, signal.SIGTERM)
            break

        p = parent



if __name__ == "__main__":
    print("on going…")
    print("Completed, Close the windows ...")
    time.sleep(1)
    close_terminal()


