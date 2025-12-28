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
        # if version == "VD":
        #     pop01 = pop.show_image_popup(
        #         title="Top slot Visual Inspection",
        #         image_path=os.path.join(ROOT_DIR, "GUI", "output_pngs", "8.png")
        #     )
        # else:
        #     pop01 = pop.show_image_popup(
        #         # my_options,
        #         title="Top slot Visual Inspection",
        #         image_path=os.path.join(ROOT_DIR, "GUI", "output_pngs", "10.png")
        #     )
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


    def safe_power_off(psu, current_threshold=0.2, max_attempts=5):
        """
        自动尝试关闭WIB电源，如果连续 max_attempts 次电流仍然过大，
        则进入人工确认模式，直到人工确认已断电。
        """

        attempt = 0

        while True:
            total_i = 0
            time.sleep(1)

            # 读取 CH1 & CH2 电流
            for ch in (1, 2):
                v, i = psu.measure(ch)
                print(f"CH{ch}: {v:.3f} V, {i:.3f} A")
                total_i += i

            print(f"Total current: {total_i:.3f} A")

            # 自动关断尝试
            psu.turn_off_all()

            # 成功关断
            if total_i < current_threshold:
                print("Power is OFF successfully.")
                return True

            # 自动关断失败
            attempt += 1
            print(f"Power off attempt {attempt}/{max_attempts} failed (current too high).")

            # 五次失败 → 人工介入
            if attempt >= max_attempts:
                print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                print("WARNING: Power could NOT be turned off after several attempts.")
                print("Human intervention is required.")
                print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")

                while True:
                    print('Please manually check WIB power status.')
                    print('Enter "confirm" after you manually turn off the power.')
                    com = input(Fore.YELLOW + '>> ' + Style.RESET_ALL)

                    if com.lower() == "confirm":
                        # 再次验证电流是否真的变小
                        v1, i1 = psu.measure(1)
                        v2, i2 = psu.measure(2)
                        if (i1 + i2) < current_threshold:
                            print("Verification passed: Power is OFF.")
                            return True
                        else:
                            print(f"Verification failed: Current still high ({i1 + i2:.3f} A).")
                            print("Please ensure the power is OFF and try again.")
                    else:
                        print("Retry Please")

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
if 4 in state_list:
    # pop09
    # 4.1 Cold Down the CE
    print("Pop09: Pop-up window CTS Cool Down Power on")
    my_options = ["Switch to cold 5 minutes", "Switch to immense, wait until level 3", "** Double confirm: reach level3, heat LED off"]
    pop09 = pop.show_image_popup(
        # my_options,
        title="Pop09: Pop-up windowCTS power on",
        image_path = os.path.join(ROOT_DIR, "GUI", "output_pngs", "14.png")
    )

    print('Please Cool Down the CTS')
    send_email.send_email(
        sender, password, receiver,
        f"Cold Down Please [{pre_info['test_site']}]",
        '"Switch to cold 5 minutes", "Switch to immense, wait until level 3", "** Double confirm: reach level3, heat LED off"'
    )
    while True:
        do_sleep = input("Do you need to wait for the refill? (y/n): ").lower()
        if do_sleep == 'y':
            print("Enter 'confirm' to wait for Cold Down [{} minutes]".format(30))
            com = input(Fore.YELLOW + '>> ' + Style.RESET_ALL)
            if com == "confirm":
                time.sleep(1800)
                send_email.send_email(
                    sender, password, receiver,
                    f"CTS has been cold down [{pre_info['test_site']}]",
                    '"** Please Double confirm: reach level3, heat LED off"'
                )
                break
            else:
                print("Retry Please")
        elif do_sleep == 'n':
            print("Enter 'confirm' to skip cold down")
            com = input(Fore.YELLOW + '>> ' + Style.RESET_ALL)
            if com == "confirm":
                break
            else:
                print("Retry Please")

    print("\033[94m" + "===============================================================================================" + "\033[0m")
    print("\033[94m" + "=============     QC Phase 3:   Cold CE Boxes Quality Control Execution            ============" + "\033[0m")
    print("\033[94m" + "=============     QC Phase 3.1: Cold Down the CTS                                  ============" + "\033[0m")
    print("\033[94m" + "=============     Please set IMMERSE to fill the Liquid Nitrogen into Cold Box     ============" + "\033[0m")
    print("\033[94m" + "=============     (takes about 33 minutes)                                         ============" + "\033[0m")
    print("\033[94m" + "===============================================================================================" + "\033[0m")

    # 4.2 Check if the LN2 reach to lever 3
    while True:
        print("Please check the LN2 level, if it reach to Level 3, heat LED off, \n[Enter 'confirm' to continue]")
        com = input(Fore.YELLOW + '>> ' + Style.RESET_ALL)
        if com == 'confirm':
            print('Great, LN2 is Ready for Cold QC')
            break

    # 4.3 information load
    infoln = cts.read_csv_to_dict(csv_file_implement, 'LN')

    # 4.4 action select
    while True:
        print(Fore.RED + "\n[Enter 'y' to next] \n[Enter 'e' to exit]\t  \n[Enter 's' to skip the Cold QC]" + Style.RESET_ALL)
        Next = input(Fore.YELLOW + '>> ' + Style.RESET_ALL)
        # 4.41 skip the Cold QC and do Post-QC checkout directly
        if Next == 's':
            print("Do you want to skip the Cold Cycle?")
            print("Enter 'confirm' to skip")
            com = input(Fore.YELLOW + '>> ' + Style.RESET_ALL)
            if com == "confirm":
                print("Skip the Cold Cycle ...")
                break
            else:
                print("Retry Please")
            print("=====================================================================")
            print("=============     Cold FEMB QC Skip                      ============")
            print("=============     Please Turn OFF the Power              ============")
            print("=====================================================================")
        # 4.42 exit the whole QC script
        elif Next == 'e':
            print("Do you want to Exit the Test?")
            print("Enter 'confirm' to Exit")
            com = input(Fore.YELLOW + '>> ' + Style.RESET_ALL)
            if com == "confirm":
                print("Exit ...")
                sys.exit()
            else:
                print("Retry Please")
        # 4.43 exit the whole QC script
        elif Next == 'y':
            print("Enter 'confirm' to begin the Cold QC")
            com = input(Fore.YELLOW + '>> ' + Style.RESET_ALL)
            if com == "confirm":
                print('\n')
                print("=====================================================================")
                print("=============     Phase 3 Cold QC Begin                  ============")
                print("=====================================================================")
                print('\n')
                # pop07
                # 4.431 power on WIB
                print("Cold Power ON WIB power supply")
                psu.set_channel(1, 12.0, 3.0, on=True)
                psu.set_channel(2, 12.0, 3.0, on=True)
                print("B01 : Build Ethernet communication between PC and WIB [35 second]")
                time.sleep(35)
                # 4.432 Ping WIB
                print("B02 : Begin to Ping WIB")
                QC_Process(path=infoln['top_path'], QC_TST_EN=77, input_info=infoln)  # ping wib
                # first run
                # C FEMB QC
                # 4.433 WIB Initial [time, startup, power connection, cable connection]
                print("C1 : WIB Initial (takes < 120s)")
                QC_Process(path=infoln['top_path'], QC_TST_EN=0, input_info=infoln)  # initial wib
                QC_Process(path=infoln['top_path'], QC_TST_EN=1, input_info=infoln)  # initial FEMB I2C
                # 4.434 Cold Checkout
                print("C2 : FEMB Checkout Execution (takes < 180s)")
                lcdata_path, lcreport_path = QC_Process(path=infoln['top_path'], QC_TST_EN=2, input_info=infoln)  # assembly checkout
                # 4.435 Cold QC Test
                print("C3 : FEMB Quality Control Execution (takes < 1800s)")
                lqdata_path, lqreport_path = QC_Process(path=infoln['top_path'], QC_TST_EN=3, input_info=infoln)  # qc
                # 4.436 WIB Linux System Close
                QC_Process(path=infoln['top_path'], QC_TST_EN=6, input_info=infoln)  # Power Off Linux
                print("Cold Power OFF WIB power supply")
                # 4.437 Power Off WIB
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
                # 4.5 Human confirm the Power is Off
                while True:
                    print("Please check the Power is OFF")
                    print('enter "confirm" to continue')
                    com = input(Fore.YELLOW + '>> ' + Style.RESET_ALL)
                    if com == 'confirm':
                        print("=====================================================================")
                        print("=============     Cold FEMB QC Done                      ============")
                        print("=============     Please Turn OFF the Power              ============")
                        print("=============     Please Set CTS as Warm Gas             ============")
                        print("=============     Please wait for Warm UP (60 Minutes)!  ============")
                        print("=====================================================================")
                        outer = True
                        break
                    else:
                        outer = False
                if outer:
                    psu.turn_off_all()
                    break
            else:
                print("Retry Please")
    # pop12
    # 5.1 Warm Up the CE
    print("Pop12: CTS switch to warm, wait for 60 minutes")
    my_options = ["Switch to Warm Gas", "Wait for 60 minutes", "Temperature reach to 45 degree"]
    pop12 = pop.show_image_popup(
        # my_options,
        title="Pop12: CTS switch to warm, wait for 60 minutes",
        image_path = os.path.join(ROOT_DIR, "GUI", "output_pngs", "15.png")
    )
    send_email.send_email(sender, password, receiver, "Warm Up Done at [{}]".format(pre_info['test_site']),
                          'Please check CTS and continue the Final Checkout')


    send_email.send_email(sender, password, receiver, "Cold QC Done at [{}]".format(pre_info['test_site']),
                          'Please Warm up the CTS')
    do_sleep = input("Do you decide to Warm Up? (y/n): ").lower()
    if do_sleep == 'y':
        time.sleep(1800)

    send_email.send_email(
        sender, password, receiver,
        f"CTS has been cold down [{pre_info['test_site']}]",
        '"** Please Double confirm: reach level3, heat LED off"'
    )

if 5 in state_list:
    print("=====================================================================")
    print("=============     Phase 4:   FEMB Final Checkout         ============")
    print("=============     [takes < 300s]                         ============")
    print("=====================================================================")

    inform = cts.read_csv_to_dict(csv_file_implement, 'RT')
    # 5.3 information load

    # Final Quick Checkout
    # 5.4 action select
    while True:
        print("\nEnter 'y' to continue \nEnter 'e' to exit\nEnter 's' to skip the Final Checkout")
        Next = input(Fore.YELLOW + '>> ' + Style.RESET_ALL)
        # 5.41 skip the Post QC Checkout and do cold test directly
        if Next == 's':
            print("Do you want to skip the Final Checkout?")
            print("Enter 'confirm' to skip")
            com = input(Fore.YELLOW + '>> ' + Style.RESET_ALL)
            if com == "confirm":
                print("Skip the Final Checkout ...")
                break
            else:
                print("Retry Please")
        # 5.42 exit the whole QC script
        elif Next == 'e':
            print("Do you want to Exit the Test?")
            print("Enter 'confirm' to Exit")
            com = input(Fore.YELLOW + '>> ' + Style.RESET_ALL)
            if com == "confirm":
                print("Exit ...")
                sys.exit()
            else:
                print("Retry Please")
        # 5.43 exit the whole QC script
        elif Next == 'y':
            print("Do you want to begin the Final Checkout?")
            print("Enter 'confirm' to begin")
            com = input(Fore.YELLOW + '>> ' + Style.RESET_ALL)
            if com == "confirm":
                print('\n')
                print("=====================================================================")
                print("=============     Phase 4 Post QC Checkout               ============")
                print("=====================================================================")
                print('\n')
                # 5.431 power on WIB
                print("Post QC Checkout Power ON WIB power supply")
                psu.set_channel(1, 12.0, 3.0, on=True)
                psu.set_channel(2, 12.0, 3.0, on=True)
                print("B01 : Build Ethernet communication between PC and WIB [35 second]")
                time.sleep(35)
                # 5.432 Ping WIB
                print("B02 : Begin to Ping WIB")
                QC_Process(path=inform['top_path'], QC_TST_EN=77, input_info=inform)  # ping wib
                # first run
                # ###############STEP1#################################
                # ======== Button 00 WIB initial =====================
                # input("\033[35m" + 'Enter to Begin!' + "\033[0m")
                # 5.433 WIB Initial [time, startup, power connection, cable connection]
                print("C1 : WIB Initial (takes < 120s)")
                QC_Process(path = inform['top_path'], QC_TST_EN=0, input_info=inform)  # initial wib
                QC_Process(path = inform['top_path'], QC_TST_EN=1, input_info=inform)  # initial FEMB I2C
                # 5.434 Warm Checkout
                print("C2 : FEMB Checkout Execution (takes < 180s)")
                fcdata_path, fcreport_path = QC_Process(path = inform['top_path'], QC_TST_EN=2, input_info=inform)  # assembly checkout
                # 5.435 WIB Linux System Close
                print("C3 : FEMB Quality Control Execution (takes < 1800s)")
                QC_Process(path = inform['top_path'], QC_TST_EN=6, input_info=inform)  # Power Off Linux

                print("\033[35m" + "=========================================================" + "\033[0m")
                print("\033[35m" + "=============     Final Checkout Done!       ============" + "\033[0m")
                print("\033[94m" + "=============     Please Power Off the WIB!  ============" + "\033[0m")
                print("\033[35m" + "=========================================================" + "\033[0m")
                # 自动关断尝试次数
                max_attempts = 5
                attempt = 0

                while True:
                    total_i = 0
                    time.sleep(1)

                    # 读两路电流
                    for ch in (1, 2):
                        v, i = psu.measure(ch)
                        print(f"CH{ch}: {v:.3f} V, {i:.3f} A")
                        total_i += i

                    print(f"Total current: {total_i:.3f} A")

                    # 尝试关断
                    psu.turn_off_all()

                    if total_i < 0.2:
                        print("Power is OFF successfully.")
                        break  # 关电成功，退出循环

                    attempt += 1
                    print(f"Power off attempt {attempt}/{max_attempts} failed (current too high).")

                    if attempt >= max_attempts:
                        print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                        print("WARNING: Power could NOT be turned off after 5 attempts.")
                        print("Human intervention is required.")
                        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")

                        # 人工确认模式
                        while True:
                            print('Please manually check WIB power status.')
                            print('Enter "confirm" after you manually turn off the power.')
                            com = input(Fore.YELLOW + '>> ' + Style.RESET_ALL)

                            if com.lower() == "confirm":
                                print("Manual confirmation received. Continuing...")
                                break
                            else:
                                print("Retry Please")

                        break  # 跳出自动关断循环（进入下一流程）
                    else:
                        print("Retrying auto power off...\n")

                break

    # pop15
    # print("Pop15: Post-Cold checkout is done →  power off WIB power supply Double confirmation ! ")
    # my_options = ["Power Off WIB"]
    # pop15 = pop.show_image_popup(
    #     # my_options,
    #     title="Pop15: Post checkout is done →  power off WIB power supply Double confirmation ! ",
    #     image_path="./GUI/picture01.png"  # local image file
    # )



# 6 Disassembly
if 6 in state_list:
    print("\033[94m" + "Please Power Off the CTS!" + "\033[0m")
    print("\033[94m" + "Pick up and Disassembly FEMB CE Boxes!" + "\033[0m")
    print("Pop16: Move ce boxes out of chamber ")
    my_options = ["Open CTS Cover", "Disassembly Cables", "Pick up CE Support Structure", "Move to the Desk", "CTS Power OFF"]
    pop16 = pop.show_image_popup(
        # my_options,
        title="Pop16: Move ce boxes out of chamber ",
        image_path = os.path.join(ROOT_DIR, "GUI", "output_pngs", "16.png")
    )

    # pop17
    # 6.2 Disassembly Top CE box
    print("Pop17: Disassembly Top CE Box")
    my_options = ["Remove the CE box", "Disassembly the Toy_TPCs", "Remove the Power Cable", "Remove the Test Cover", "Remove the Cable Clamp of Data Cable", "Remove the Data Cable", "Install the Original Cover", " Install the Terminator", "Packaged into ESD Bag and Foam Box"]
    if version == "VD":
        pop17 = pop.show_image_popup(
            # my_options,
            title="Pop17: Disassembly Top CE Box",
            image_path = os.path.join(ROOT_DIR, "GUI", "output_pngs", "17.png")
        )
    else:
        pop17 = pop.show_image_popup(
            # my_options,
            title="Pop17: Disassembly Top CE Box",
            image_path=os.path.join(ROOT_DIR, "GUI", "output_pngs", "18.png")
        )


    # pop18
    # 6.3 Disassembly Bottom CE box
    print("Pop18: Disassembly Bottom CE Box")
    my_options = ["Remove the CE box", "Disassembly the Toy_TPCs", "Remove the Power Cable", "Remove the Test Cover", "Remove the Cable Clamp of Data Cable", "Remove the Data Cable", "Install the Original Cover", " Install the Terminator", "Packaged into ESD Bag and Foam Box"]
    if version == "VD":
        pop17 = pop.show_image_popup(
            # my_options,
            title="Pop17: Disassembly Bottom CE Box",
            image_path = os.path.join(ROOT_DIR, "GUI", "output_pngs", "17.png")
        )
    else:
        pop17 = pop.show_image_popup(
            # my_options,
            title="Pop17: Disassembly Bottom CE Box",
            image_path=os.path.join(ROOT_DIR, "GUI", "output_pngs", "18.png")
        )

    while True:
        pop17 = pop.show_image_popup(
            # my_options,
            title="Pop17: Return Accessories to Their Original Position",
            image_path=os.path.join(ROOT_DIR, "GUI", "output_pngs", "19.png")
        )
        print("Please confirm that all accessories have been returned to their original positions. Enter “confirm” to continue.")
        order = input()
        if order == 'confirm':
            print('Thanks, the Accessories are put back!')
            break
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


