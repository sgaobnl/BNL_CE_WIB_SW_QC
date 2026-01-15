import os
import pickle
from colorama import Fore, Style, init
import QC_components.qc_log as log
import subprocess
import matplotlib.pyplot as plt
from tabulate import tabulate

def dict_to_markdown_table(dictionary, KEY = "KEY", VALUE = "RECORD"):
    # 获取字典的键和值
    keys = list(dictionary.keys())
    values = list(dictionary.values())

    if VALUE == "PWRVALUE":
        # 构建表格头部
        table = "| {} | {} |\n| --- | --- | --- | --- | --- |\n".format(KEY, " | | | ")
        for key, value in zip(keys, values):
            table += f"| {key} | {value} |\n"
    elif VALUE == "RMS":
        # 构建表格头部
        table = "| | {} |\n| --- | --- | --- | --- | --- | --- | --- | --- |\n".format(" | | | | | |")
        for key, value in zip(keys, values):
            table += f"| {key} | {value} |\n"
    elif VALUE == "ADC_MON":
        table = "| Voltage Type| Chip 0 | Chip 1 | Chip 2 | Chip 3 | Chip 4 | Chip 5 | Chip 6 | Chip 7 |\n| --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
        for key, value in zip(keys, values):
            table += f"| {key} | {value} |\n"
    elif VALUE == "Horizontal":
        table = '|' + '|'.join(dictionary.keys()) + '|' + '\n'
        table += '|' + '|'.join(['---' for _ in dictionary.keys()]) + '|' + '\n'
        table += '|' + '|'.join(str(dictionary[key]).strip() for key in dictionary.keys()) + '|' + '\n'
    elif VALUE == "Rail":
        table = "| {} | {} |\n| --- | --- |\n".format(KEY, VALUE)
        for key, value in zip(keys, values):
            table += f"| {key} | {value} |\n"
    elif VALUE == "Pulse":
        table = "| {} | {} |\n| --- | --- |\n".format(KEY, 'VALUE')
        for key, value in zip(keys, values):
            table += f"| {key} | {value} |\n"
    else:
        table = "| {} | {} |\n| --- | --- |\n".format(KEY, VALUE)
        for key, value in zip(keys, values):
            table += f"| {key} | {value} |\n"

    return table




def section_report(datareport, fembs, fembNo, fembsName):
    global fpmd
    print("\n\n\n")
    print("==================================================================================")
    print("+++++++               GENERAL REPORT for FEMB BOARDS TESTING               +++++++")
    print("+++++++                                                                    +++++++")
    print("==================================================================================")
    print("\n")
    print(log.report_log01["ITEM"])
    for key, value in log.report_log01["Detail"].items():
        print(f"{key}: {value}")

    print('\n')

    all_true = {}
    PH = 250
    for ifemb in fembs:
        femb_id = "FEMB ID {}".format(fembNo['femb%d' % ifemb])
###======================== Whole judgement =============================
#   item 01 Power Consumption
        check_list = []
        check_status01 = True
        check_status02 = True
        check_status03 = True
        check_status04 = True
        check_status05 = True
        check_status06 = True
        check_status07 = True
        check_status08 = True
        check_status09 = True
        check_status10 = True
        check_status11 = True
        check_status12 = True
        check_status13 = True
        check_status14 = True
        check_status15 = True
        check_status16 = True
        Status = 'P'
        if 1 in log.test_label:
            dict_list01 = [log.check_log01_11[femb_id], log.check_log01_12[femb_id], log.check_log01_13[femb_id], log.check_log01_21[femb_id], log.check_log01_22[femb_id], log.check_log01_23[femb_id], log.check_log01_31[femb_id], log.check_log01_32[femb_id], log.check_log01_33[femb_id]]

            check_list01 = []
            for dict_i in dict_list01:
                if dict_i['Result'] == False:
                    check_status01 = False
                    Status = 'F'
            check_list.append(check_status01)
        if 2 in log.test_label:
            # dict_list01 = [log.check_log01_11[femb_id], log.check_log01_12[femb_id], log.check_log01_13[femb_id], log.check_log01_21[femb_id], log.check_log01_22[femb_id], log.check_log01_23[femb_id], log.check_log01_31[femb_id], log.check_log01_32[femb_id], log.check_log01_33[femb_id]]

            check_list02 = []
            check_status02 = True
            check_list.append(check_status02)

        if 3 in log.test_label:
            dict_list03 = [log.check_log03_01[femb_id], log.check_log03_02[femb_id], log.check_log03_03[femb_id], log.check_log03_04[femb_id]]

            check_list03 = []
            for dict_i in dict_list03:
                if dict_i['Result'] == False:
                    check_status03 = False
                    Status = 'F'
            check_list.append(check_status03)

        if 4 in log.test_label:
            dict_list04 = [log.check_log04_01[femb_id]]

            check_list04 = []
            for dict_i in dict_list04:
                if dict_i['Result'] == False:
                    check_status04 = False
                    Status = 'F'
            check_list.append(check_status04)

        if 5 in log.test_label:
            print(log.report_log0500[ifemb]['Result'])
            print(log.report_log0500[ifemb]['Result'])
            print(log.report_log0500[ifemb]['Result'])
            print(log.report_log0500[ifemb]['Result'])
            if log.report_log0500[ifemb]['Result'] == False:
                print(log.report_log0500[ifemb]['Result'])
                check_status05 = False
                Status = 'F'
            check_list.append(check_status05)

        if 6 in log.test_label:
            dict_list06 = [log.check_log0601[femb_id], log.check_log0602[femb_id], log.check_log0603[femb_id], log.check_log0604[femb_id]]#, log.check_log0605[femb_id]]
            for dict_i in dict_list06:
                if dict_i['Result'] == False:
                    check_status06 = False
                    Status = 'F'
            check_list.append(check_status06)

        if 7 in log.test_label:
            dict_list07 = [log.check_log0701[femb_id]]#, log.check_log0702[femb_id]]

            check_list07 = []
            for dict_i in dict_list07:
                if dict_i['Result'] == False:
                    check_status07 = False
                    Status = 'F'
                    # check_list07.append(str(dict_i['Label']) + "\n")
                    check_list07.append(str(dict_i['Issue List']) + "\n")
            check_list.append(check_status07)

        if 8 in log.test_label:
            dict_list08 = [log.check_log0801[femb_id]]

            check_list08 = []
            for dict_i in dict_list08:
                if dict_i['Result'] == False:
                    check_status08 = False
                    Status = 'F'
                    print(log.check_log0801[femb_id])
                    # check_list07.append(str(dict_i['Label']) + "\n")
                    check_list08.append(str(dict_i['Issue List']) + "\n")
            check_list.append(check_status08)

        if 9 in log.test_label:
            dict_list09 = [log.check_log0901[femb_id]]

            check_list09 = []
            for dict_i in dict_list09:
                if dict_i['Result'] == False:
                    check_status09 = False
                    Status = 'F'
                    # check_list07.append(str(dict_i['Label']) + "\n")
                    check_list09.append(str(dict_i['Issue List']) + "\n")
            check_list.append(check_status09)

        if 10 in log.test_label:
            dict_list10 = [log.check_log1001[femb_id]]

            check_list10 = []
            for dict_i in dict_list10:
                if dict_i['Result'] == False:
                    check_status10 = False
                    Status = 'F'
                    # check_list07.append(str(dict_i['Label']) + "\n")
                    # check_list10.append(str(dict_i['Issue List']) + "\n")
            check_list.append(check_status10)


        if 11 in log.test_label:
            dict_list11 = [log.check_log1101[femb_id]]

            check_list11 = []
            for dict_i in dict_list11:
                if dict_i['Result'] == False:
                    check_status11 = False
                    Status = 'F'
                    # check_list07.append(str(dict_i['Label']) + "\n")
                    # check_list11.append(str(dict_i['Issue List']) + "\n")
            check_list.append(check_status11)

        if 12 in log.test_label:
            dict_list12 = [log.check_log1201[femb_id]]

            check_list12 = []
            for dict_i in dict_list12:
                if dict_i['Result'] == False:
                    check_status12 = False
                    Status = 'F'
                    # check_list07.append(str(dict_i['Label']) + "\n")
                    # check_list12.append(str(dict_i['Issue List']) + "\n")
            check_list.append(check_status12)

        if 13 in log.test_label:
            dict_list13 = [log.check_log1301[femb_id]]

            check_list13 = []
            for dict_i in dict_list13:
                if dict_i['Result'] == False:
                    check_status13 = False
                    Status = 'F'
                    # check_list07.append(str(dict_i['Label']) + "\n")
                    # check_list13.append(str(dict_i['Issue List']) + "\n")
            check_list.append(check_status13)

        if 14 in log.test_label:
            dict_list14 = [log.check_log1401[femb_id]]

            check_list14 = []
            for dict_i in dict_list14:
                if dict_i['Result'] == False:
                    check_status14 = False
                    Status = 'F'
            check_list.append(check_status14)

        if 15 in log.test_label:
            dict_list15 = [log.check_log1501[femb_id], log.check_log1502[femb_id], log.check_log1503[femb_id]]

            for dict_i in dict_list15:
                if dict_i['Result'] == False:
                    check_status15 = False
                    Status = 'F'
            check_list.append(check_status15)

        if 16 in log.test_label:
            dict_list16 = [log.check_log1601[femb_id]]
            for dict_i in dict_list16:
                if dict_i['Result'] == False:
                    check_status16 = False
                    Status = 'F'
            check_list.append(check_status16)

        all_true = all(value for value in check_list)
        if all_true:
            summary = '<span style="color: green;">' + " FEMB # {}\t      PASS\t    ALL Quality Control".format(fembsName['femb%d' % ifemb]) + '</span>'  + '\n'
        else:
            summary = '<span style="color: red;">' + " FEMB # {}\t      Fail\t    ALL Quality Control".format(fembsName['femb%d' % ifemb]) + '</span>'  + '\n'
###======================================================================

#   Start Markdown

        print(Status)
        if Status:
            print("\033[32m" + "The FEMB {} PASS the ITEM {} QC test".format(fembsName['femb%d' % ifemb], *log.test_label) + "\033[0m")
        else:
            print("\033[31m" + "The FEMB {} fail the ITEM {} QC test".format(fembsName['femb%d' % ifemb], *log.test_label) + "\033[0m")
        print('\n')
        fpmd = datareport[ifemb] + 'report_FEMB_{}_t{}_{}_S{}.md'.format(fembNo['femb%d' % ifemb], *log.test_label, Status, ifemb)
        print(datareport[ifemb])
        with open(fpmd, 'w', encoding = "utf-8") as file:
            # file.write('')
            file.write('\n')
            file.write('\n')
            file.write('# ' + summary + '\n')
            file.write('\n')
            file.write('\n')
# Title     FEMB ID
# 00        Print <Input Information>
            file.write('## INPUT INFORMATION &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; {}'.format(fembsName['femb%d' % ifemb]) + '\n')
            info = dict_to_markdown_table(log.report_log00, VALUE="Horizontal")
            file.write(info + '\n')

            file.write('## Test Content' + '\n')


##  Content Pages ================================================

            if 1 in log.test_label:
                if check_status01:
                    Item01 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: green;">' + 'Item_01 POWER CONSUMPTION' + '&nbsp;&nbsp;&nbsp;&nbsp; < Pass >' + '</span>'
                else:
                    Item01 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: red;">' + 'Item_01 POWER CONSUMPTION' + '&nbsp;&nbsp;&nbsp;&nbsp; < Fail >' + '</span>'
                file.write('[Chapter_1](#item1)' + Item01 + '\n\n')

            if 2 in log.test_label:
                if check_status02:
                    Item02 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: green;">' + 'Item_02 POWER CYCLE' + '&nbsp;&nbsp;&nbsp;&nbsp; < Pass >' + '</span>'
                else:
                    Item02 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: red;">' + 'Item_02 POWER CYCLE' + '&nbsp;&nbsp;&nbsp;&nbsp; < Fail >' + '</span>'
                file.write('[Chapter_2](#item2)' + Item02 + '\n\n')

            if 3 in log.test_label:
                if check_status03:
                    Item03 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: green;">' + 'Item_03 FE Pulse Response at Different Leakage Current Setting' + '&nbsp;&nbsp;&nbsp;&nbsp; < Pass >' + '</span>'
                else:
                    Item03 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: red;">' + 'Item_03 FE Pulse Response at Different Leakage Current Setting' + '&nbsp;&nbsp;&nbsp;&nbsp; < Fail >' + '</span>'
                file.write('[Chapter_3](#item3)' + Item03 + '\n\n')

            if 4 in log.test_label:
                if check_status04:
                    Item04 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: green;">' + 'Item_04 Whole Pulse Response' + '&nbsp;&nbsp;&nbsp;&nbsp; < Pass >' + '</span>'
                else:
                    Item04 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: red;">' + 'Item_04 Whole Pulse Response' + '&nbsp;&nbsp;&nbsp;&nbsp; < Fail >' + '</span>'
                file.write('[Chapter_4](#item4)' + Item04 + '\n\n')

            if 5 in log.test_label:
                if check_status05:
                    Item05 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: green;">' + 'Item_05 RMS Evaluation' + '&nbsp;&nbsp;&nbsp;&nbsp; < Pass >' + '</span>'
                else:
                    Item05 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: red;">' + 'Item_05 RMS Evaluation' + '&nbsp;&nbsp;&nbsp;&nbsp; < Fail >' + '</span>'
                file.write('[Chapter_5](#item5)' + Item05 + '\n\n')

            if 6 in log.test_label:
                if check_status06:
                    Item06 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: green;">' + 'Item_06 Cali_1 configuration SE 200 mV' + '&nbsp;&nbsp;&nbsp;&nbsp; < Pass >' + '</span>'
                else:
                    Item06 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: red;">' + 'Item_06 Cali_1 configuration SE 200 mV' + '&nbsp;&nbsp;&nbsp;&nbsp; < Fail >' + '</span>'
                file.write('[Chapter_6](#item6)' + Item06 + '\n\n')

            if 7 in log.test_label:
                if check_status07:
                    Item07 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: green;">' + 'Item_07 Cali_2 configuration SE 900 mV' + '&nbsp;&nbsp;&nbsp;&nbsp; < Pass >' + '</span>'
                else:
                    Item07 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: red;">' + 'Item_07 Cali_2 configuration SE 900 mV' + '&nbsp;&nbsp;&nbsp;&nbsp; < Fail >' + '</span>'
                file.write('[Chapter_7](#item7)' + Item07 + '\n\n')

            if 8 in log.test_label:
                if check_status08:
                    Item08 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: green;">' + 'Item_08 Cali_3 SGP1 SE 200 mV' + '&nbsp;&nbsp;&nbsp;&nbsp; < Pass >' + '</span>'
                else:
                    Item08 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: red;">' + 'Item_08 Cali_3 SGP1 SE 200 mV' + '&nbsp;&nbsp;&nbsp;&nbsp; < Fail >' + '</span>'
                file.write('[Chapter_8](#item8)' + Item08 + '\n\n')

            if 9 in log.test_label:
                if check_status09:
                    Item09 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: green;">' + 'Item_09 Cali_4 SGP1 SE 900 mV' + '&nbsp;&nbsp;&nbsp;&nbsp; < Pass >' + '</span>'
                else:
                    Item09 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: red;">' + 'Item_09 Cali_4 SGP1 SE 900 mV' + '&nbsp;&nbsp;&nbsp;&nbsp; < Fail >' + '</span>'
                file.write('[Chapter_9](#item9)' + Item09 + '\n\n')

            if 10 in log.test_label:
                if check_status10:
                    Item10 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: green;">' + 'Item_10 FE Monitor via WIB ADC' + '&nbsp;&nbsp;&nbsp;&nbsp; < Pass >' + '</span>'
                else:
                    Item10 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: red;">' + 'Item_10 FE Monitor via WIB ADC' + '&nbsp;&nbsp;&nbsp;&nbsp; < Fail >' + '</span>'
                file.write('[Chapter_10](#item10)' + Item10 + '\n\n')

            if 11 in log.test_label:
                if check_status11:
                    Item11 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: green;">' + 'Item_11 FE DAC Linearity Monitor via WIB ADC' + '&nbsp;&nbsp;&nbsp;&nbsp; < Pass >' + '</span>'
                else:
                    Item11 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: red;">' + 'Item_11 FE DAC Linearity Monitor via WIB ADC' + '&nbsp;&nbsp;&nbsp;&nbsp; < Fail >' + '</span>'
                file.write('[Chapter_11](#item11)' + Item11 + '\n\n')

            if 12 in log.test_label:
                if check_status12:
                    Item12 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: green;">' + 'Item_12 ColdADC ref_voltage Linearity' + '&nbsp;&nbsp;&nbsp;&nbsp; < Pass >' + '</span>'
                else:
                    Item12 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: red;">' + 'Item_12 ColdADC ref_voltage Linearity' + '&nbsp;&nbsp;&nbsp;&nbsp; < Fail >' + '</span>'
                file.write('[Chapter_12](#item12)' + Item12 + '\n\n')
            if 13 in log.test_label:
                if check_status13:
                    Item13 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: green;">' + 'Item_13 External Pulse Calibration 900mV baseline' + '&nbsp;&nbsp;&nbsp;&nbsp; < Pass >' + '</span>'
                else:
                    Item13 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: red;">' + 'Item_13 External Pulse Calibration 900mV baseline' + '&nbsp;&nbsp;&nbsp;&nbsp; < Fail >' + '</span>'
                file.write('[Chapter_13](#item13)' + Item13 + '\n\n')
            if 14 in log.test_label:
                if check_status14:
                    Item14 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: green;">' + 'Item_14 External Pulse Calibration 200mV baseline' + '&nbsp;&nbsp;&nbsp;&nbsp; < Pass >' + '</span>'
                else:
                    Item14 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: red;">' + 'Item_14 External Pulse Calibration 200mV baseline' + '&nbsp;&nbsp;&nbsp;&nbsp; < Fail >' + '</span>'
                file.write('[Chapter_14](#item14)' + Item14 + '\n\n')

            if 15 in log.test_label:
                if check_status15:
                    Item15 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: green;">' + 'Item_15 ColdADC_sync_pat_report' + '&nbsp;&nbsp;&nbsp;&nbsp; < Pass >' + '</span>'
                else:
                    Item15 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: red;">' + 'Item_15 ColdADC_sync_pat_report' + '&nbsp;&nbsp;&nbsp;&nbsp; < Fail >' + '</span>'
                file.write('[Chapter_15](#item15)' + Item15 + '\n\n')
            if 16 in log.test_label:
                if check_status16:
                    Item16 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: green;">' + 'Item_16 PLL_scan_report' + '&nbsp;&nbsp;&nbsp;&nbsp; < Pass >' + '</span>'
                else:
                    Item16 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: red;">' + 'Item_16 PLL_scan_report' + '&nbsp;&nbsp;&nbsp;&nbsp; < Fail >' + '</span>'
                file.write('[Chapter_16](#item16)' + Item16 + '\n\n')
            file.write("------\n")

            if 1 in log.test_label:
                file.write('<img src="./PWR_Meas/Power_Total.png" alt="picture" height="250">' + "\n\n")  # width="200"
            if 6 in log.test_label:
                file.write('<img src="./{}/SE_Gain.png" alt="picture" height="250">'.format(log.item062) + "\n\n")  # width="200"
                file.write('<img src="./{}/SE_ENC.png" alt="picture" height="250">'.format(log.item062) + "\n\n")  # width="200"
            # if 11 in log.test_label:
            #     file.write('<img src="./{}/mon_LArASIC_DAC_25mVfC.png" alt="picture" height="250">'.format(log.item11) + "\n\n")  # width="200"

            file.write("------\n")
##  Detail Pages ================================================

# 01        Print <Power Consumption>
            if 1 in log.test_label:
                if check_status01:
                    Head01 = '### ' + '</span>' + '<span id="item1"> Chapter_1 </span>'  + '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: green;">' + 'ITEM_01_POWER_CONSUMPTION' + '    < Pass >' + '</span>' + '\n'
                else:
                    Head01 = '### ' + '</span>' + '<span id="item1"> Chapter_1 </span>'  + '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: red;">' + 'ITEM_01_POWER_CONSUMPTION' + '    < Fail >' + '</span>'  + '\n'
                file.write(Head01 + '\n')
                file.write("------\n")
                file.write('### 1_1 &nbsp;&nbsp;&nbsp;&nbsp; Power Measurement'  + '\n')
                info = dict_to_markdown_table(log.report_log01_11[femb_id], KEY = "SE OFF [SDF = 0; SDD = 0]", VALUE="PWRVALUE")
                file.write(info + '\n')

                info = dict_to_markdown_table(log.report_log01_21[femb_id], KEY = "SE ON [SDF = 1; SDD = 0]", VALUE="PWRVALUE")
                file.write(info + '\n')

                info = dict_to_markdown_table(log.report_log01_31[femb_id], KEY = "DIFF [SDF = 0; SDD = 1]", VALUE="PWRVALUE")
                file.write(info + '\n')

                file.write('### 1_2 &nbsp;&nbsp;&nbsp;&nbsp; LDO Measurement / mV' + '\n')
                file.write('<div style = "display: flex; justify-content: space-between;">'+'\n\n')
                info = dict_to_markdown_table(log.report_log01_13[femb_id], KEY="SE OFF [SDF = 0; SDD = 0]", VALUE = "Rail")
                file.write(info + '\n\n')
                info = dict_to_markdown_table(log.report_log01_23[femb_id], KEY="SE ON [SDF = 1; SDD = 0]", VALUE = "Rail")
                file.write(info + '\n\n')
                info = dict_to_markdown_table(log.report_log01_33[femb_id], KEY="DIFF [SDF = 0; SDD = 1]", VALUE="Rail")
                file.write(info + '\n\n')
                file.write('</div>' + '\n\n')

                file.write('### 1_3 &nbsp;&nbsp;&nbsp;&nbsp; Initial Pulse Response' + '\n')
                file.write('<div style = "display: flex; justify-content: space-between;">' + '\n\n')
                info = dict_to_markdown_table(log.report_log01_12[femb_id], KEY="SE OFF [SDF = 0; SDD = 0]", VALUE = "Pulse")
                file.write(info + '\n\n')
                info = dict_to_markdown_table(log.report_log01_22[femb_id], KEY="SE ON [SDF = 1; SDD = 0]", VALUE = "Pulse")
                file.write(info + '\n\n')
                info = dict_to_markdown_table(log.report_log01_32[femb_id], KEY="DIFF [SDF = 0; SDD = 1]", VALUE = "Pulse")
                file.write(info + '\n\n')
                file.write('</div>' + '\n\n')
                file.write('<details>'+ '\n\n')
                file.write('<img src="./PWR_Meas/pulse_PWR_SE_OFF_200mVBL_14_0mVfC_2_0us.png" alt="picture" height="200">' + "\n") #width="200"
                file.write('<img src="./PWR_Meas/pulse_PWR_SE_ON_200mVBL_14_0mVfC_2_0us.png" alt="picture" height="200">' + "\n") #width="200"
                file.write('<img src="./PWR_Meas/pulse_PWR_DIFF_200mVBL_14_0mVfC_2_0us.png" alt="picture" height="200">' + "\n") #width="200"
                file.write('</details>'+ '\n\n')

            if 2 in log.test_label:
                if check_status02:
                    Head02 = '### ' + '</span>' + '<span id="item2"> Chapter_2 </span>'  + '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: green;">' + 'ITEM_02_POWER_CYCLE' + '    < Pass >' + '</span>' + '\n'
                else:
                    Head02 = '### ' + '</span>' + '<span id="item2"> Chapter_2 </span>'  + '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: red;">' + 'ITEM_02_POWER_CYCLE' + '    < Fail >' + '</span>'  + '\n'
                file.write(Head02 + '\n')
                file.write("------\n")
                file.write('### 2_01 cycle0_SE DAC = 0' + '\n')
                file.write('### 1_1 &nbsp;&nbsp;&nbsp;&nbsp; Power Measurement' + '\n')
                info = dict_to_markdown_table(log.tmp_log02_01[femb_id], KEY="SE OFF [SDF = 0; SDD = 0]", VALUE="PWRVALUE")
                file.write(info + '\n')
                file.write("![ped](./PWR_Cycle/Pulse_PWR_cycle0_SE_200mVBL_14_0mVfC_2_0us_0x20_pulse.png)" + "\n\n")
                file.write('### 2_02 cycle1_SE DAC = 0' + '\n')
                file.write('### 1_2 &nbsp;&nbsp;&nbsp;&nbsp; Power Measurement' + '\n')
                info = dict_to_markdown_table(log.tmp_log02_02[femb_id], KEY="SE OFF [SDF = 0; SDD = 0]", VALUE="PWRVALUE")
                file.write(info + '\n')
                file.write("![ped](./PWR_Cycle/Pulse_PWR_cycle1_SE_200mVBL_14_0mVfC_2_0us_0x20_pulse.png)" + "\n\n")
                file.write('### 2_03 cycle2_SE DAC = 0' + '\n')
                file.write('### 1_3 &nbsp;&nbsp;&nbsp;&nbsp; Power Measurement' + '\n')
                info = dict_to_markdown_table(log.tmp_log02_03[femb_id], KEY="SE OFF [SDF = 0; SDD = 0]", VALUE="PWRVALUE")
                file.write(info + '\n')
                file.write("![ped](./PWR_Cycle/Pulse_PWR_cycle2_SE_200mVBL_14_0mVfC_2_0us_0x20_pulse.png)" + "\n\n")
                file.write('### 2_04 SE_SDF' + '\n')
                file.write('### 1_3 &nbsp;&nbsp;&nbsp;&nbsp; Power Measurement' + '\n')
                info = dict_to_markdown_table(log.tmp_log02_04[femb_id], KEY="SE ON [SDF = 1; SDD = 0]", VALUE="PWRVALUE")
                file.write(info + '\n')
                file.write("![ped](./PWR_Cycle/pulse_PWR_SE_SDF_200mVBL_14_0mVfC_2_0us.png)" + "\n\n")
                file.write('### 2_05 DIFF' + '\n')
                file.write('### 1_3 &nbsp;&nbsp;&nbsp;&nbsp; Power Measurement' + '\n')
                info = dict_to_markdown_table(log.tmp_log02_05[femb_id], KEY="DIFF [SDF = 0; SDD = 1]", VALUE="PWRVALUE")
                file.write(info + '\n')
                file.write("![ped](./PWR_Cycle/pulse_PWR_DIFF_200mVBL_14_0mVfC_2_0us.png)" + "\n\n")
# 03
            if 3 in log.test_label:
                if check_status03:
                    Head03 = '### ' + '</span>' + '<span id="item3"> Chapter_3 </span>'  + '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: green;">' + 'ITEM 03 FE Pulse Response at Different Leakage Current Setting' + '    < Pass >' + '</span>'  + '\n'
                else:
                    Head03 = '### ' + '</span>' + '<span id="item3"> Chapter_3 </span>'  + '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: red;">' + 'ITEM 03 FE Pulse Response at Different Leakage Current Setting' + '    < Fail >' + '</span>'  + '\n'
                file.write(Head03 + '\n')
                file.write("------\n")
                file.write("![ped](./Leakage_Current/LC_pulse.png)" + "\n\n")

                log.check_log03_table_01[femb_id]['title'] = " | FE Leakage <bar> Current | 100 pA | 500 pA | 1 nA | 5 nA | \n"
                log.check_log03_table_01[femb_id]['table line'] = " | --- | --- | --- | --- | --- | \n"
                log.check_log03_table_01[femb_id]['ppk_mean'] = " | Amplitude Mean | {} | {} | {} | {} | \n".format(log.report_log03_02[femb_id]["ppk_mean"], log.report_log03_01[femb_id]["ppk_mean"], log.report_log03_04[femb_id]["ppk_mean"], log.report_log03_03[femb_id]["ppk_mean"])
                # log.check_log03_table_01[femb_id]['ppk_err'] = " | PPK Std | {} | {} | {} | {} | \n".format(log.report_log03_02[femb_id]["LC_SE_200mVBL_14_0mVfC_2_0us_0x20_100pA_ppk_err0"], log.report_log03_01[femb_id]["LC_SE_200mVBL_14_0mVfC_2_0us_0x20_500pA_ppk_err0"], log.report_log03_04[femb_id]["LC_SE_200mVBL_14_0mVfC_2_0us_0x20_1nA_ppk_err0"], log.report_log03_03[femb_id]["LC_SE_200mVBL_14_0mVfC_2_0us_0x20_5nA_ppk_err0"])
                log.check_log03_table_01[femb_id]['npk_mean'] = " | Pedestal Mean | {} | {} | {} | {} | \n".format(log.report_log03_02[femb_id]["bbl_mean"], log.report_log03_01[femb_id]["bbl_mean"], log.report_log03_04[femb_id]["bbl_mean"], log.report_log03_03[femb_id]["bbl_mean"])
                # log.check_log03_table_01[femb_id]['npk_err'] = " | NPK Std | {} | {} | {} | {} | \n".format(log.report_log03_02[femb_id]["LC_SE_200mVBL_14_0mVfC_2_0us_0x20_100pA_npk_err0"], log.report_log03_01[femb_id]["LC_SE_200mVBL_14_0mVfC_2_0us_0x20_500pA_npk_err0"], log.report_log03_04[femb_id]["LC_SE_200mVBL_14_0mVfC_2_0us_0x20_1nA_npk_err0"], log.report_log03_03[femb_id]["LC_SE_200mVBL_14_0mVfC_2_0us_0x20_5nA_npk_err0"])

                file.write(log.check_log03_table_01[femb_id]['title'])
                file.write(log.check_log03_table_01[femb_id]['table line'])
                file.write(log.check_log03_table_01[femb_id]['ppk_mean'])
                # file.write(log.check_log03_table_01[femb_id]['ppk_err'])
                file.write(log.check_log03_table_01[femb_id]['npk_mean'] + '\n')
                # file.write(log.check_log03_table_01[femb_id]['npk_err'] + '\n')
                file.write('<details>' + '\n\n')
                file.write("------\n")
                file.write('### 3_01 FE Leakage Current = 100 pA' + '\n')
                info = dict_to_markdown_table(log.report_log03_02[femb_id], VALUE="Horizontal")
                file.write(info + '\n')
                file.write("![ped](./Leakage_Current/pulse_LC_SE_200mVBL_14_0mVfC_2_0us_0x20_100pA.png)" + "\n")

                file.write("------\n")
                file.write('### 3_02 FE Leakage Current = 500 pA' + '\n')
                info = dict_to_markdown_table(log.report_log03_01[femb_id], VALUE="Horizontal")
                file.write(info + '\n')
                file.write("![ped](./Leakage_Current/pulse_LC_SE_200mVBL_14_0mVfC_2_0us_0x20_500pA.png)" + "\n")

                file.write("------\n")
                file.write('### 3_03 FE Leakage Current = 1 nA' + '\n')
                info = dict_to_markdown_table(log.report_log03_04[femb_id], VALUE="Horizontal")
                file.write(info + '\n')
                file.write("![ped](./Leakage_Current/pulse_LC_SE_200mVBL_14_0mVfC_2_0us_0x20_1nA.png)" + "\n")

                file.write("------\n")
                file.write('### 3_04 FE Leakage Current = 5 nA' + '\n')
                info = dict_to_markdown_table(log.report_log03_03[femb_id], VALUE="Horizontal")
                file.write(info + '\n')
                file.write("![ped](./Leakage_Current/pulse_LC_SE_200mVBL_14_0mVfC_2_0us_0x20_5nA.png)" + "\n")
                file.write('</details >' + '\n\n')









# 04        print <Check Pulse>
            if 4 in log.test_label:
                if check_status04:
                    Head04 = '### ' + '</span>' + '<span id="item4"> Chapter_4 </span>'  + '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: green;">' + 'ITEM 04 Pulse Response' + '    < Pass >' + '</span>'  + '\n'
                else:
                    Head04 = '### ' + '</span>' + '<span id="item4"> Chapter_4 </span>'  + '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: red;">' + 'ITEM 04 Pulse Response' + '    < Fail >' + '</span>'  + '\n'
                file.write(Head04 + '\n')
                file.write("------\n")
                # SE 200 mV
                file.write('<img src="./CHK/SE_200_Gain_Pulse_ErrorBar.png" alt="picture" height="350">' + "\n")  # width="200"
                file.write('<details>' + '\n\n')
                file.write('### SE OFF    Baseline 200 mV [SDF = 0; SDD = 0; SNC = 1] DAC = 0x10' + '\n')
                log.check_log04_table_01[femb_id]['title'] = " | Gain | PeakTime | PPK Mean | PPK std | Baseline Mean | Baseline std |\n"
                log.check_log04_table_01[femb_id]['table line'] = " | --- | --- | --- | --- | --- | --- | \n"

                log.check_log04_table_01[femb_id]['line1'] = " | 4.7 mV/fC | 0.5 us | {} | {} | {} | {} | \n".format(log.report_log04_01_4705[femb_id]["ppk_mean"], log.report_log04_01_4705[femb_id]["ppk_std"], log.report_log04_01_4705[femb_id]["bbl_mean"], log.report_log04_01_4705[femb_id]["bbl_std"])
                log.check_log04_table_01[femb_id]['line2'] = " | 4.7 mV/fC | 1 us | {} | {} | {} | {} | \n".format(log.report_log04_01_4710[femb_id]["ppk_mean"], log.report_log04_01_4710[femb_id]["ppk_std"], log.report_log04_01_4710[femb_id]["bbl_mean"], log.report_log04_01_4710[femb_id]["bbl_std"])
                log.check_log04_table_01[femb_id]['line3'] = " | 4.7 mV/fC | 2 us | {} | {} | {} | {} | \n".format(log.report_log04_01_4720[femb_id]["ppk_mean"], log.report_log04_01_4720[femb_id]["ppk_std"], log.report_log04_01_4720[femb_id]["bbl_mean"], log.report_log04_01_4720[femb_id]["bbl_std"])
                log.check_log04_table_01[femb_id]['line4'] = " | 4.7 mV/fC | 3 us | {} | {} | {} | {} | \n".format(log.report_log04_01_4730[femb_id]["ppk_mean"], log.report_log04_01_4730[femb_id]["ppk_std"], log.report_log04_01_4730[femb_id]["bbl_mean"], log.report_log04_01_4730[femb_id]["bbl_std"])

                log.check_log04_table_01[femb_id]['line5'] = " 7.8 mV/fC | 0.5 us | {} | {} | {} | {} |\n".format(log.report_log04_01_7805[femb_id]['ppk_mean'], log.report_log04_01_7805[femb_id]["ppk_std"], log.report_log04_01_7805[femb_id]['bbl_mean'], log.report_log04_01_7805[femb_id]["bbl_std"])
                log.check_log04_table_01[femb_id]['line6'] = " 7.8 mV/fC | 1 us | {} | {} | {} | {} | \n".format(log.report_log04_01_7810[femb_id]['ppk_mean'], log.report_log04_01_7810[femb_id]["ppk_std"], log.report_log04_01_7810[femb_id]['bbl_mean'], log.report_log04_01_7810[femb_id]["bbl_std"])
                log.check_log04_table_01[femb_id]['line7'] = " 7.8 mV/fC | 2 us | {} | {} | {} | {} | \n".format(log.report_log04_01_7820[femb_id]['ppk_mean'], log.report_log04_01_7820[femb_id]["ppk_std"], log.report_log04_01_7820[femb_id]['bbl_mean'], log.report_log04_01_7820[femb_id]["bbl_std"])
                log.check_log04_table_01[femb_id]['line8'] = " 7.8 mV/fC | 3 us | {} | {} | {} | {} | \n".format(log.report_log04_01_7830[femb_id]['ppk_mean'], log.report_log04_01_7830[femb_id]["ppk_std"], log.report_log04_01_7830[femb_id]['bbl_mean'], log.report_log04_01_7830[femb_id]["bbl_std"])

                log.check_log04_table_01[femb_id]['line9'] = " 14 mV/fC | 0.5 us | {} | {} | {} | {} | \n".format(log.report_log04_01_1405[femb_id]['ppk_mean'], log.report_log04_01_1405[femb_id]["ppk_std"], log.report_log04_01_1405[femb_id]['bbl_mean'], log.report_log04_01_1405[femb_id]["bbl_std"])
                log.check_log04_table_01[femb_id]['line10'] = " 14 mV/fC | 1 us | {} | {} | {} | {} | \n".format(log.report_log04_01_1410[femb_id]['ppk_mean'], log.report_log04_01_1410[femb_id]["ppk_std"],  log.report_log04_01_1410[femb_id]['bbl_mean'], log.report_log04_01_1410[femb_id]["bbl_std"])
                log.check_log04_table_01[femb_id]['line11'] = " 14 mV/fC | 2 us | {} | {} | {} | {} | \n".format(log.report_log04_01_1420[femb_id]['ppk_mean'], log.report_log04_01_1420[femb_id]["ppk_std"],  log.report_log04_01_1420[femb_id]['bbl_mean'], log.report_log04_01_1420[femb_id]["bbl_std"])
                log.check_log04_table_01[femb_id]['line12'] = " 14 mV/fC | 3 us | {} | {} | {} | {} | \n".format(log.report_log04_01_1430[femb_id]['ppk_mean'], log.report_log04_01_1430[femb_id]["ppk_std"],  log.report_log04_01_1430[femb_id]['bbl_mean'], log.report_log04_01_1430[femb_id]["bbl_std"])

                log.check_log04_table_01[femb_id]['line13'] = " 25 mV/fC | 0.5 us | {} | {} | {} | {} | \n".format(log.report_log04_01_2505[femb_id]['ppk_mean'], log.report_log04_01_2505[femb_id]["ppk_std"], log.report_log04_01_2505[femb_id]['bbl_mean'], log.report_log04_01_2505[femb_id]["bbl_std"])
                log.check_log04_table_01[femb_id]['line14'] = " 25 mV/fC | 1 us | {} | {} | {} | {} | \n".format(log.report_log04_01_2510[femb_id]['ppk_mean'], log.report_log04_01_2510[femb_id]["ppk_std"], log.report_log04_01_2510[femb_id]['bbl_mean'], log.report_log04_01_2510[femb_id]["bbl_std"])
                log.check_log04_table_01[femb_id]['line15'] = " 25 mV/fC | 2 us | {} | {} | {} | {} | \n".format(log.report_log04_01_2520[femb_id]['ppk_mean'], log.report_log04_01_2520[femb_id]["ppk_std"], log.report_log04_01_2520[femb_id]['bbl_mean'], log.report_log04_01_2520[femb_id]["bbl_std"])
                log.check_log04_table_01[femb_id]['line16'] = " 25 mV/fC | 3 us | {} | {} | {} | {} | \n".format(log.report_log04_01_2530[femb_id]['ppk_mean'], log.report_log04_01_2530[femb_id]["ppk_std"], log.report_log04_01_2530[femb_id]['bbl_mean'], log.report_log04_01_2530[femb_id]["bbl_std"])

                file.write('\n')
                file.write(log.check_log04_table_01[femb_id]['title'])
                file.write(log.check_log04_table_01[femb_id]['table line'])
                file.write(log.check_log04_table_01[femb_id]['line1'])
                file.write(log.check_log04_table_01[femb_id]['line2'])
                file.write(log.check_log04_table_01[femb_id]['line3'])
                file.write(log.check_log04_table_01[femb_id]['line4'])
                file.write(log.check_log04_table_01[femb_id]['line5'])
                file.write(log.check_log04_table_01[femb_id]['line6'])
                file.write(log.check_log04_table_01[femb_id]['line7'])
                file.write(log.check_log04_table_01[femb_id]['line8'])
                file.write(log.check_log04_table_01[femb_id]['line9'])
                file.write(log.check_log04_table_01[femb_id]['line10'])
                file.write(log.check_log04_table_01[femb_id]['line11'])
                file.write(log.check_log04_table_01[femb_id]['line12'])
                file.write(log.check_log04_table_01[femb_id]['line13'])
                file.write(log.check_log04_table_01[femb_id]['line14'])
                file.write(log.check_log04_table_01[femb_id]['line15'])
                file.write(log.check_log04_table_01[femb_id]['line16'])
                file.write('</details>' + '\n\n')

                #   SE 900 mV
                file.write('<img src="./CHK/SE_900_Gain_Pulse_ErrorBar.png" alt="picture" height="350">' + "\n")  # width="200"
                file.write('<details>' + '\n\n')
                file.write('### SE OFF    Baseline 900 mV [SDF = 0; SDD = 0; SNC = 0] DAC = 0x10' + '\n')
                log.check_log04_table_02[femb_id][
                    'title'] = " | Gain | PeakTime | PPK Mean | PPK std | NPK Mean | NPK td |\n"
                log.check_log04_table_02[femb_id]['table line'] = " | --- | --- | --- | --- | --- | --- | \n"

                log.check_log04_table_02[femb_id]['line1'] = " | 4.7 mV/fC | 0.5 us | {} | {} | {} | {} | \n".format(
                    log.report_log04_02_4705[femb_id]["ppk_mean"], log.report_log04_02_4705[femb_id]["ppk_std"],
                    log.report_log04_02_4705[femb_id]["npk_mean"], log.report_log04_02_4705[femb_id]["npk_std"])
                log.check_log04_table_02[femb_id]['line2'] = " | 4.7 mV/fC | 1 us | {} | {} | {} | {} | \n".format(
                    log.report_log04_02_4710[femb_id]["ppk_mean"], log.report_log04_02_4710[femb_id]["ppk_std"],
                    log.report_log04_02_4710[femb_id]["npk_mean"], log.report_log04_02_4710[femb_id]["npk_std"])
                log.check_log04_table_02[femb_id]['line3'] = " | 4.7 mV/fC | 2 us | {} | {} | {} | {} | \n".format(
                    log.report_log04_02_4720[femb_id]["ppk_mean"], log.report_log04_02_4720[femb_id]["ppk_std"],
                    log.report_log04_02_4720[femb_id]["npk_mean"], log.report_log04_02_4720[femb_id]["npk_std"])
                log.check_log04_table_02[femb_id]['line4'] = " | 4.7 mV/fC | 3 us | {} | {} | {} | {} | \n".format(
                    log.report_log04_02_4730[femb_id]["ppk_mean"], log.report_log04_02_4730[femb_id]["ppk_std"],
                    log.report_log04_02_4730[femb_id]["npk_mean"], log.report_log04_02_4730[femb_id]["npk_std"])

                log.check_log04_table_02[femb_id]['line5'] = " 7.8 mV/fC | 0.5 us | {} | {} | {} | {} |\n".format(
                    log.report_log04_02_7805[femb_id]['ppk_mean'], log.report_log04_02_7805[femb_id]["ppk_std"],
                    log.report_log04_02_7805[femb_id]['npk_mean'], log.report_log04_02_7805[femb_id]["npk_std"])
                log.check_log04_table_02[femb_id]['line6'] = " 7.8 mV/fC | 1 us | {} | {} | {} | {} | \n".format(
                    log.report_log04_02_7810[femb_id]['ppk_mean'], log.report_log04_02_7810[femb_id]["ppk_std"],
                    log.report_log04_02_7810[femb_id]['npk_mean'], log.report_log04_02_7810[femb_id]["npk_std"])
                log.check_log04_table_02[femb_id]['line7'] = " 7.8 mV/fC | 2 us | {} | {} | {} | {} | \n".format(
                    log.report_log04_02_7820[femb_id]['ppk_mean'], log.report_log04_02_7820[femb_id]["ppk_std"],
                    log.report_log04_02_7820[femb_id]['npk_mean'], log.report_log04_02_7820[femb_id]["npk_std"])
                log.check_log04_table_02[femb_id]['line8'] = " 7.8 mV/fC | 3 us | {} | {} | {} | {} | \n".format(
                    log.report_log04_02_7830[femb_id]['ppk_mean'], log.report_log04_02_7830[femb_id]["ppk_std"],
                    log.report_log04_02_7830[femb_id]['npk_mean'], log.report_log04_02_7830[femb_id]["npk_std"])

                log.check_log04_table_02[femb_id]['line9'] = " 14 mV/fC | 0.5 us | {} | {} | {} | {} | \n".format(
                    log.report_log04_02_1405[femb_id]['ppk_mean'], log.report_log04_02_1405[femb_id]["ppk_std"],
                    log.report_log04_02_1405[femb_id]['npk_mean'], log.report_log04_02_1405[femb_id]["npk_std"])
                log.check_log04_table_02[femb_id]['line10'] = " 14 mV/fC | 1 us | {} | {} | {} | {} | \n".format(
                    log.report_log04_02_1410[femb_id]['ppk_mean'], log.report_log04_02_1410[femb_id]["ppk_std"],
                    log.report_log04_02_1410[femb_id]['npk_mean'], log.report_log04_02_1410[femb_id]["npk_std"])
                log.check_log04_table_02[femb_id]['line11'] = " 14 mV/fC | 2 us | {} | {} | {} | {} | \n".format(
                    log.report_log04_02_1420[femb_id]['ppk_mean'], log.report_log04_02_1420[femb_id]["ppk_std"],
                    log.report_log04_02_1420[femb_id]['npk_mean'], log.report_log04_02_1420[femb_id]["npk_std"])
                log.check_log04_table_02[femb_id]['line12'] = " 14 mV/fC | 3 us | {} | {} | {} | {} | \n".format(
                    log.report_log04_02_1430[femb_id]['ppk_mean'], log.report_log04_02_1430[femb_id]["ppk_std"],
                    log.report_log04_02_1430[femb_id]['npk_mean'], log.report_log04_02_1430[femb_id]["npk_std"])

                log.check_log04_table_02[femb_id]['line13'] = " 25 mV/fC | 0.5 us | {} | {} | {} | {} | \n".format(
                    log.report_log04_02_2505[femb_id]['ppk_mean'], log.report_log04_02_2505[femb_id]["ppk_std"],
                    log.report_log04_02_2505[femb_id]['npk_mean'], log.report_log04_02_2505[femb_id]["npk_std"])
                log.check_log04_table_02[femb_id]['line14'] = " 25 mV/fC | 1 us | {} | {} | {} | {} | \n".format(
                    log.report_log04_02_2510[femb_id]['ppk_mean'], log.report_log04_02_2510[femb_id]["ppk_std"],
                    log.report_log04_02_2510[femb_id]['npk_mean'], log.report_log04_02_2510[femb_id]["npk_std"])
                log.check_log04_table_02[femb_id]['line15'] = " 25 mV/fC | 2 us | {} | {} | {} | {} | \n".format(
                    log.report_log04_02_2520[femb_id]['ppk_mean'], log.report_log04_02_2520[femb_id]["ppk_std"],
                    log.report_log04_02_2520[femb_id]['npk_mean'], log.report_log04_02_2520[femb_id]["npk_std"])
                log.check_log04_table_02[femb_id]['line16'] = " 25 mV/fC | 3 us | {} | {} | {} | {} | \n".format(
                    log.report_log04_02_2530[femb_id]['ppk_mean'], log.report_log04_02_2530[femb_id]["ppk_std"],
                    log.report_log04_02_2530[femb_id]['npk_mean'], log.report_log04_02_2530[femb_id]["npk_std"])

                file.write('\n')
                file.write(log.check_log04_table_02[femb_id]['title'])
                file.write(log.check_log04_table_02[femb_id]['table line'])
                file.write(log.check_log04_table_02[femb_id]['line1'])
                file.write(log.check_log04_table_02[femb_id]['line2'])
                file.write(log.check_log04_table_02[femb_id]['line3'])
                file.write(log.check_log04_table_02[femb_id]['line4'])
                file.write(log.check_log04_table_02[femb_id]['line5'])
                file.write(log.check_log04_table_02[femb_id]['line6'])
                file.write(log.check_log04_table_02[femb_id]['line7'])
                file.write(log.check_log04_table_02[femb_id]['line8'])
                file.write(log.check_log04_table_02[femb_id]['line9'])
                file.write(log.check_log04_table_02[femb_id]['line10'])
                file.write(log.check_log04_table_02[femb_id]['line11'])
                file.write(log.check_log04_table_02[femb_id]['line12'])
                file.write(log.check_log04_table_02[femb_id]['line13'])
                file.write(log.check_log04_table_02[femb_id]['line14'])
                file.write(log.check_log04_table_02[femb_id]['line15'])
                file.write(log.check_log04_table_02[femb_id]['line16'])
                file.write('</details>' + '\n\n')


                #   SGP 200 mV
                file.write('<img src="./CHK/SGP1_200_fC_Pulse.png" alt="picture" height="350">' + "\n")  # width="200"
                file.write('<details>' + '\n\n')
                file.write('### SGP1    Baseline 200 mV [SDF = 0; SDD = 0; SNC = 0] DAC = 0x0C' + '\n')
                file.write('\n')
                log.check_log04_table_06[femb_id][
                    'title'] = " | Gain | PeakTime | PPK Mean | PPK std | Baseline Mean | Baseline std |\n"
                log.check_log04_table_06[femb_id]['table line'] = " | --- | --- | --- | --- | --- | --- |\n"

                log.check_log04_table_06[femb_id]['line1'] = " | 4_7 mV/fC | 2 us | {} | {} | {} | {} | \n".format(
                    log.report_log04_03_4720[femb_id]["ppk_mean"],
                    log.report_log04_03_4720[femb_id]["ppk_std"],
                    log.report_log04_03_4720[femb_id]["bbl_mean"],
                    log.report_log04_03_4720[femb_id]["bbl_std"])
                log.check_log04_table_06[femb_id]['line2'] = " | 7_8 mV/fC | 2 us | {} | {} | {} | {} | \n".format(
                    log.report_log04_03_7820[femb_id]["ppk_mean"],
                    log.report_log04_03_7820[femb_id]["ppk_std"],
                    log.report_log04_03_7820[femb_id]["bbl_mean"],
                    log.report_log04_03_7820[femb_id]["bbl_std"])
                log.check_log04_table_06[femb_id]['line3'] = " | 14 mV/fC | 2 us | {} | {} | {} | {} | \n".format(
                    log.report_log04_03_1420[femb_id]["ppk_mean"],
                    log.report_log04_03_1420[femb_id]["ppk_std"],
                    log.report_log04_03_1420[femb_id]["bbl_mean"],
                    log.report_log04_03_1420[femb_id]["bbl_std"])
                log.check_log04_table_06[femb_id]['line4'] = " | 25 mV/fC | 2 us | {} | {} | {} | {} | \n".format(
                    log.report_log04_03_2520[femb_id]["ppk_mean"],
                    log.report_log04_03_2520[femb_id]["ppk_std"],
                    log.report_log04_03_2520[femb_id]["bbl_mean"],
                    log.report_log04_03_2520[femb_id]["bbl_std"])

                file.write('\n')
                file.write(log.check_log04_table_06[femb_id]['title'])
                file.write(log.check_log04_table_06[femb_id]['table line'])
                file.write(log.check_log04_table_06[femb_id]['line1'])
                file.write(log.check_log04_table_06[femb_id]['line2'])
                file.write(log.check_log04_table_06[femb_id]['line3'])
                file.write(log.check_log04_table_06[femb_id]['line4'])
                file.write('</details>' + '\n\n')



                # file.write(log.check_log04_table_06[femb_id]['line2'])
                file.write('\n\n')
                file.write("[PDF](./{}/report.pdf)".format(log.item04) + "\n")







# 05        RMS configuration
            if 5 in log.test_label:
                if check_status05 == True:
                    file.write('### ' + '</span>' + '<span id="item5"> Chapter_5 </span>'  + '&nbsp;&nbsp;&nbsp;&nbsp; <span style = "color : green;">' + "Noise Evaluation"  + '    < Pass >' + '</span>' + '\n')
                else:
                    file.write('### ' + '</span>' + '<span id="item5"> Chapter_5 </span>'  + '&nbsp;&nbsp;&nbsp;&nbsp; <span style = "color : red;">' + "Noise Evaluation" + '    < Fail >' + '</span>'  + '\n')
                    file.write(str(log.report_log0500[ifemb]['Issue List']))
                file.write('#### ' + "1. Noise at SE OFF &nbsp;&nbsp;&nbsp;&nbsp; 200 mV & 900 mV" + '\n')
                file.write('<img src="./{}/SE_200_900_mV_RMS_ErrorBar.png" alt="picture" height="350">'.format(log.item05) + "\n\n")  # width="200"
                file.write('#### ' + "2. Noise at SE ON and DIFF &nbsp;&nbsp;&nbsp;&nbsp; 200 mV & 900 mV" + '\n')
                file.write('<img src="./{}/SEON_DIFF_200_900_mV_RMS_ErrorBar.png" alt="picture" height="350">'.format(log.item05) + "\n\n")  # width="200"
                file.write('#### ' + "3. Noise at Leakage Current with SE OFF &nbsp;&nbsp;&nbsp;&nbsp; 200 mV" + '\n')
                file.write('<img src="./{}/SELC_200_2us_ErrorBar.png" alt="picture" height="350">'.format(log.item05) + "\n\n")  # width="200"
                # file.write("![ped](./{}/SEON_DIFF_200_900_mV_RMS_ErrorBar.png)".format(log.item05) + "\n")
                file.write('<details>' + '\n\n')
                file.write('\n' + '#### ' + 'All_200mVBL_Configuration' + '\n')
                info = dict_to_markdown_table(log.report_log05_table[femb_id], VALUE="RMS")
                file.write(info + '\n')
                file.write('\n' + '#### ' + 'All_900mVBL_Configuration' + '\n')
                info = dict_to_markdown_table(log.report_log05_table2[femb_id], VALUE="RMS")
                file.write(info + '\n')
                file.write("![ped](./{}/200mV_All_Configuration.png)".format(log.item05) + "\n")
                file.write('#### All_900mVBL_Configuration' + '\n')
                file.write("![ped](./{}/900mV_All_Configuration.png)".format(log.item05) + "\n")
                file.write('#### Noise Report' + '\n')
                file.write("[PDF](./{}/report.pdf)".format(log.item05) + "\n")
                file.write('</details>' + '\n\n')

# 06        Calibration 01:
            # SE    200 mVBL    4_7 mVfC    2 us
            # SE    200 mVBL    7_8 mVfC    2 us
            # SE    200 mVBL    14 mVfC     2 us
            # SE    200 mVBL    25 mVfC     2 us
            # DIFF  200 mVBL    14 mVfC     2 us
            if 6 in log.test_label:
                if check_status06:
                    Head06 = '### ' + '</span>' + '<span id="item6"> Chapter_6 </span>' + '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: green;">' + 'ITEM_06_Cali_1 SE_OFF 200' + '    < Pass >' + '</span>' + '\n'
                else:
                    Head06 = '### ' + '</span>' + '<span id="item6"> Chapter_6 </span>' + '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: red;">' + 'ITEM_06_Cali_1 SE_OFF 200' + '    < Fail >' + '</span>' + '\n'

                file.write(Head06 + '\n')
                file.write("![ped](./{}/Cali1.png)".format(log.item062) + "\n\n")

                file.write('### 6_1 Calibration SE 200 mVBL    4_7 mVfC    2 us' + '\n')
                file.write('<img src="./{}/enc_200mVBL_4_7mVfC_2_0us.png" alt="picture" height="230">'.format(
                    log.item061) + "\n")  # width="200"
                file.write('<img src="./{}/Line_range_200mVBL_4_7mVfC_2_0us.png" alt="picture" height="230">'.format(
                    log.item061) + "\n\n")  # width="200"
                # file.write("![ped](./{}/enc_200mVBL_4_7mVfC_2_0us.png)".format(log.item061) + "![ped](./{}/Line_range_200mVBL_4_7mVfC_2_0us.png)".format(log.item061) + "\n")
                file.write("![ped](./{}/gain_200mVBL_4_7mVfC_2_0us.png)".format(log.item061) + "\n")

                file.write('### 6_2 Calibration SE 200 mVBL    7_8 mVfC    2 us' + '\n')
                file.write('<img src="./{}/enc_200mVBL_7_8mVfC_2_0us.png" alt="picture" height="230">'.format(
                    log.item061) + "\n")  # width="200"
                file.write('<img src="./{}/Line_range_200mVBL_7_8mVfC_2_0us.png" alt="picture" height="230">'.format(
                    log.item061) + "\n\n")  # width="200"
                # file.write("![ped](./{}/enc_200mVBL_7_8mVfC_2_0us.png)".format(log.item061) + "![ped](./{}/Line_range_200mVBL_7_8mVfC_2_0us.png)".format(log.item061) + "\n")
                file.write("![ped](./{}/gain_200mVBL_7_8mVfC_2_0us.png)".format(log.item061) + "\n")

                file.write('### 6_3 Calibration SE 200 mVBL    14_0 mVfC    2 us' + '\n')
                file.write('<img src="./{}/enc_200mVBL_14_0mVfC_2_0us.png" alt="picture" height="230">'.format(
                    log.item061) + "\n")  # width="200"
                file.write('<img src="./{}/Line_range_200mVBL_14_0mVfC_2_0us.png" alt="picture" height="230">'.format(
                    log.item061) + "\n\n")  # width="200"
                # file.write("![ped](./{}/enc_200mVBL_14_0mVfC_2_0us.png)".format(log.item061) + "![ped](./{}/Line_range_200mVBL_14_0mVfC_2_0us.png)".format(log.item061) + "\n")
                file.write("![ped](./{}/gain_200mVBL_14_0mVfC_2_0us.png)".format(log.item061) + "\n")

                file.write('### 6_4 Calibration SE 200 mVBL    25_0 mVfC    2 us' + '\n')
                file.write('<img src="./{}/enc_200mVBL_25_0mVfC_2_0us.png" alt="picture" height="230">'.format(
                    log.item061) + "\n")  # width="200"
                file.write('<img src="./{}/Line_range_200mVBL_25_0mVfC_2_0us.png" alt="picture" height="230">'.format(
                    log.item061) + "\n\n")  # width="200"
                file.write("![ped](./{}/gain_200mVBL_25_0mVfC_2_0us.png)".format(log.item061) + "\n")

                # file.write('### 6_5 Calibration DIFF 200 mVBL    14_0 mVfC    2 us' + '\n')
                # file.write('<img src="./{}/enc_200mVBL_14_0mVfC_2_0us.png" alt="picture" height="230">'.format(
                #     log.item062) + "\n")  # width="200"
                # file.write('<img src="./{}/Line_range_200mVBL_14_0mVfC_2_0us.png" alt="picture" height="230">'.format(
                #     log.item062) + "\n\n")  # width="200"
                # file.write("![ped](./{}/gain_200mVBL_14_0mVfC_2_0us.png)".format(log.item062) + "\n")

#   07      Calibration 02:
            if 7 in log.test_label:
                if check_status07:
                    Head07 = '### ' + '</span>' + '<span id="item7"> Chapter_7 </span>' + '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: green;">' + 'ITEM_07_Cali_2 SE 900' + '    < Pass >' + '</span>' + '\n'
                else:
                    Head07 = '### ' + '</span>' + '<span id="item7"> Chapter_7 </span>' + '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: red;">' + 'ITEM_07_Cali_2 SE 900' + '    < Fail >' + '</span>' + '\n'

                file.write(Head07 + '\n')

                # file.write("![ped](./{}/Cali2.png)".format(log.item072) + "\n\n")

                # SE    900 mVBL    14_0 mVfC       2 us
                file.write('### Calibration 021 SE 900 mVBL    14_0 mVfC    2 us' + '\n')
                file.write('<img src="./{}/enc_900mVBL_14_0mVfC_2_0us.png" alt="picture" height="230">'.format(
                    log.item071) + "\n")  # width="200"
                file.write('<img src="./{}/Line_range_900mVBL_14_0mVfC_2_0us.png" alt="picture" height="230">'.format(
                    log.item071) + "\n\n")  # width="200"

                # file.write("![ped](./{}/enc_900mVBL_14_0mVfC_2_0us.png)".format(log.item071) + "![ped](./{}/Line_range_900mVBL_14_0mVfC_2_0us.png)".format(log.item071) + "\n")
                file.write("![ped](./{}/gain_900mVBL_14_0mVfC_2_0us.png)".format(log.item071) + "\n")
                #DIFF  900 mVBL    14 mVfC     2 us
                file.write('### Calibration 022 DIFF 900 mVBL    14_0 mVfC    2 us' + '\n')
                file.write('<img src="./{}/enc_900mVBL_14_0mVfC_2_0us.png" alt="picture" height="230">'.format(
                    log.item072) + "\n")  # width="200"
                file.write('<img src="./{}/Line_range_900mVBL_14_0mVfC_2_0us.png" alt="picture" height="230">'.format(
                    log.item072) + "\n\n")  # width="200"
                # file.write("![ped](./{}/enc_900mVBL_14_0mVfC_2_0us.png)".format(log.item072) + "![ped](./{}/Line_range_900mVBL_14_0mVfC_2_0us.png)".format(log.item072) + "\n")
                file.write("![ped](./{}/gain_900mVBL_14_0mVfC_2_0us.png)".format(log.item072) + "\n")

#   08      Calibration 03:
            if 8 in log.test_label:
                if check_status08:
                    Head08 = '### ' + '</span>' + '<span id="item8"> Chapter_8 </span>' + '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: green;">' + 'ITEM_08_Cali_3 SE 200 SGP' + '    < Pass >' + '</span>' + '\n'
                else:
                    Head08 = '### ' + '</span>' + '<span id="item8"> Chapter_8 </span>' + '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: red;">' + 'ITEM_08_Cali_3 SE 200 SGP' + '    < Fail >' + '</span>' + '\n'
            # SE    200 mVBL    4_7 mVfC       2 us    SGP1
                file.write(Head08 + '\n')
                file.write('### Calibration 03 SE SGP1 200 mVBL    14_0 mVfC    2 us' + '\n')
                # file.write('<img src="./{}/enc_200mVBL_14_0mVfC_2_0us_sgp1.png" alt="picture" height={}>'.format(log.item081, PH) + "\n")  # width="200"
                # file.write('<img src="./{}/Line_range_200mVBL_14_0mVfC_2_0us_sgp1.png" alt="picture" height={}>'.format(log.item081, PH) + "\n\n")  # width="200"
                # file.write("![ped](./{}/enc_200mVBL_4_7mVfC_2_0us_sgp1.png)".format(log.item081) + "![ped](./{}/Line_range_200mVBL_4_7mVfC_2_0us_sgp1.png)".format(log.item081) + "\n")
                file.write("![ped](./{}/gain_200mVBL_14_0mVfC_2_0us_sgp1.png)".format(log.item081) + "\n")
            # # DIFF  900 mVBL    4_7 mVfC     2 us
            # file.write('### Calibration 022 DIFF 900 mVBL    4_7 mVfC    2 us' + '\n')
            # file.write("![ped](./{}/enc_900mVBL_4_7mVfC_2_0us.png)".format(log.item072) + "![ped](./{}/ped_900mVBL_4_7mVfC_2_0us.png)".format(log.item072) + "\n")
            # file.write("![ped](./{}/gain_900mVBL_4_7mVfC_2_0us.png)".format(log.item072) + "\n")

#   09      Calibration 04:
            if 9 in log.test_label:
                if check_status09:
                    Head09 = '### ' + '</span>' + '<span id="item9"> Chapter_9 </span>' + '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: green;">' + 'ITEM_09_Cali_4 SE 900 SGP1' + '    < Pass >' + '</span>' + '\n'
                else:
                    Head09 = '### ' + '</span>' + '<span id="item9"> Chapter_9 </span>' + '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: red;">' + 'ITEM_09_Cali_4 SE 900 SGP1' + '    < Fail >' + '</span>' + '\n'
                file.write(Head09 + '\n')
                file.write('### Calibration 04 SE SGP1 900 mVBL    14_0 mVfC    2 us' + '\n')
                file.write('<img src="./{}/enc_900mVBL_14_0mVfC_2_0us_sgp1.png" alt="picture" height={}>'.format(log.item091, PH) + "\n")  # width="200"
                file.write('<img src="./{}/Line_range_900mVBL_14_0mVfC_2_0us_sgp1.png" alt="picture" height={}>'.format(log.item091, PH) + "\n\n")  # width="200"
                file.write("![ped](./{}/gain_900mVBL_14_0mVfC_2_0us_sgp1.png)".format(log.item091) + "\n")
            # DIFF  900 mVBL    14 mVfC     2 us
            # file.write('### Calibration 022 DIFF 900 mVBL    14_0 mVfC    2 us' + '\n')
            # file.write("![ped](./{}/enc_900mVBL_14_0mVfC_2_0us.png)".format(log.item092) + "![ped](./{}/ped_900mVBL_14_0mVfC_2_0us.png)".format(log.item092) + "\n")
            # file.write("![ped](./{}/gain_900mVBL_14_0mVfC_2_0us.png)".format(log.item092) + "\n")
            


# 10        print <FE_MON>
            if 10 in log.test_label:
                if check_status10 == True:
                    file.write('### ' + '</span>' + '<span id="item10"> Chapter_10 </span>'  + '&nbsp;&nbsp;&nbsp;&nbsp; <span style = "color : green;">' + "FE Mon"  + '    < Pass >' + '</span>' + '\n')
                else:
                    file.write('### ' + '</span>' + '<span id="item10"> Chapter_10 </span>'  + '&nbsp;&nbsp;&nbsp;&nbsp; <span style = "color : red;">' "FE Mon" + '    < Pass >' + '</span>' + '\n')
                    file.write(log.report_log10_01[ifemb])
                file.write('#### mon_bandgap' + '\n')
                info = dict_to_markdown_table(log.report_log10_01[femb_id], VALUE="Horizontal")
                file.write(info + '\n')
                file.write("![ped](./{}/FE_Mon.png)".format(log.item10) + "\n")

# 11        print <FE_DAC_MON>
            # 11_01
            if 11 in log.test_label:
                if check_status11 == True:
                    file.write('### ' + '</span>' + '<span id="item11"> Chapter_11 </span>'  + '&nbsp;&nbsp;&nbsp;&nbsp; <span style = "color : green;">' + "FE DAC linearity"  + '    < Pass >' + '</span>' + '\n')
                else:
                    file.write('### ' + '</span>' + '<span id="item11"> Chapter_11 </span>'  + '&nbsp;&nbsp;&nbsp;&nbsp; <span style = "color : red;">' + "FE DAC linearity"  + '    < Pass >' + '</span>' + '\n')
                file.write('### FE_DAC_MON' + '\n')
                info = dict_to_markdown_table(log.check_log1101[femb_id])
                file.write(info + '\n')
                file.write("![ped](./{}/mon_LArASIC_DAC_25mVfC.png)".format(log.item11) + "\n")

# 12        print <ADC_MON>
            # 12_01
            if 12 in log.test_label:
                if check_status12 == True:
                    file.write(
                        '### ' + '</span>' + '<span id="item12"> Chapter_12 </span>' + '&nbsp;&nbsp;&nbsp;&nbsp; <span style = "color : green;">' + "ColdADC linearity" + '    < Pass >' + '</span>' + '\n')
                else:
                    file.write('### ' + '</span>' + '<span id="item12"> Chapter_12 </span>'  + '&nbsp;&nbsp;&nbsp;&nbsp; <span style = "color : red;">' + "ColdADC linearity"  + '    < Pass >' + '</span>' + '\n')

                file.write('### FE_ADC_MON' + '\n')
                info = dict_to_markdown_table(log.ADCMON_table[femb_id], VALUE="ADC_MON")
                file.write(info + '\n')
                file.write(
                    '<img src="./{}/mon_VCMI.png" alt="picture" height="230">'.format(log.item12) + "\n")  # width="200"
                file.write(
                    '<img src="./{}/mon_VCMO.png" alt="picture" height="230">'.format(log.item12) + "\n")  # width="200"
                file.write(
                    '<img src="./{}/mon_VREFN.png" alt="picture" height="230">'.format(log.item12) + "\n")  # width="200"
                file.write(
                    '<img src="./{}/mon_VREFP.png" alt="picture" height="230">'.format(log.item12) + "\n")  # width="200"
                file.write('\n')

#   13      Calibration 04:
            if 13 in log.test_label:
                if check_status13 == True:
                    file.write('### ' + '</span>' + '<span id="item13"> Chapter_13 </span>' + '&nbsp;&nbsp;&nbsp;&nbsp; <span style = "color : green;">' + "External Pulse Calibration 900mV baseline" + '    < Pass >' + '</span>' + '\n')
                else:
                    file.write('### ' + '</span>' + '<span id="item13"> Chapter_13 </span>' + '&nbsp;&nbsp;&nbsp;&nbsp; <span style = "color : red;">' + "External Pulse Calibration 900mV baseline" + '    < fail >' + '</span>' + '\n')

                # SE    900 mVBL    14_0 mVfC       2 us
                file.write('### Calibration 05 SE 900 mVBL    14_0 mVfC    2 us' + '\n')
                file.write('<img src="./{}/enc_900mVBL_14_0mVfC_2_0us.png" alt="picture" height="230">'.format(log.item13) + "\n")  # width="200"
                file.write('<img src="./{}/Line_range_900mVBL_14_0mVfC_2_0us.png" alt="picture" height="230">'.format(log.item13) + "\n\n")  # width="200"
                # file.write("![ped](./{}/enc_900mVBL_14_0mVfC_2_0us.png)".format(log.item13) + "![ped](./{}/Line_range_900mVBL_14_0mVfC_2_0us.png)".format(log.item13) + "\n")
                file.write("![ped](./{}/gain_900mVBL_14_0mVfC_2_0us.png)".format(log.item13) + "\n")
                # file.write("![ped](./{}/ped_900mVBL_14_0mVfC_2_0us.png)".format(log.item13) + "\n")

            #   14      Calibration 04:
            if 14 in log.test_label:
                if check_status14 == True:
                    file.write('### ' + '</span>' + '<span id="item14"> Chapter_14 </span>' + '&nbsp;&nbsp;&nbsp;&nbsp; <span style = "color : green;">' + "External Pulse Calibration 200mV baseline" + '    < Pass >' + '</span>' + '\n')
                else:
                    file.write('### ' + '</span>' + '<span id="item14"> Chapter_14 </span>' + '&nbsp;&nbsp;&nbsp;&nbsp; <span style = "color : red;">' + "External Pulse Calibration 200mV baseline" + '    < fail >' + '</span>' + '\n')
                # SE    900 mVBL    14_0 mVfC       2 us
                file.write('### Calibration 06 200 mVBL    14_0 mVfC    2 us' + '\n')
                file.write('<img src="./{}/enc_200mVBL_14_0mVfC_2_0us.png" alt="picture" height="230">'.format(log.item14) + "\n")  # width="200"
                file.write('<img src="./{}/Line_range_200mVBL_14_0mVfC_2_0us.png" alt="picture" height="230">'.format(log.item14) + "\n\n")  # width="200"
                # file.write("![ped](./{}/enc_200mVBL_14_0mVfC_2_0us.png)".format(log.item14) + "![ped](./{}/Line_range_200mVBL_14_0mVfC_2_0us.png)".format(log.item14) + "\n")
                file.write("![ped](./{}/gain_200mVBL_14_0mVfC_2_0us.png)".format(log.item14) + "\n")
                # file.write("![ped](./{}/ped_200mVBL_14_0mVfC_2_0us.png)".format(log.item14) + "\n")

# 15        print <ADC_DC noise measurement>
            # 12_01
            if 15 in log.test_label:
                if check_status15:
                    file.write(
                        '### ' + '</span>' + '<span id="item15"> Chapter_15 </span>' + '&nbsp;&nbsp;&nbsp;&nbsp; <span style = "color : green;">' + "ColdADC_sync_pat_report" + '    < Pass >' + '</span>' + '\n')
                else:
                    file.write(
                        '### ' + '</span>' + '<span id="item15"> Chapter_15 </span>' + '&nbsp;&nbsp;&nbsp;&nbsp; <span style = "color : red;">' + "ColdADC_sync_pat_report" + '    < fail >' + '</span>' + '\n')

                file.write('### ADC_DC noise measurement' + '\n')
                # info = dict_to_markdown_table(log.ADCMON_table[femb_id], VALUE="ADC_MON")
                # file.write(info + '\n')
                file.write('#### ADC Test mode DC Noise SE' + '\n\n')
                file.write("![ped](./{}/ped_ADC_Test_mode_DC_Noise_SE.png)".format(log.item15))
                file.write("![ped](./{}/rms_ADC_Test_mode_DC_Noise_SE.png)".format(log.item15) + '\n\n')
                file.write('#### ADC SYNC PAT SHA SE' + '\n\n')
                file.write("![ped](./{}/ped_ADC_SYNC_PAT_SHA_SE.png)".format(log.item15))
                file.write("![ped](./{}/rms_ADC_SYNC_PAT_SHA_SE.png)".format(log.item15) + '\n\n')
                file.write('#### ADC SYNC PAT SHA DIFF' + '\n\n')
                file.write("![ped](./{}/ped_ADC_SYNC_PAT_SHA_DIFF.png)".format(log.item15))
                file.write("![ped](./{}/rms_ADC_SYNC_PAT_SHA_DIFF.png)".format(log.item15))
                file.write('\n\n')
# 16        print <ADC_DC noise measurement>
            # 12_01
            if 16 in log.test_label:
                if check_status16 == True:
                    file.write('### ' + '</span>' + '<span id="item16"> Chapter_16 </span>' + '&nbsp;&nbsp;&nbsp;&nbsp; <span style = "color : green;">' + "PLL_scan_report" + '    < Pass >' + '</span>' + '\n')
                else:
                    file.write('### ' + '</span>' + '<span id="item16"> Chapter_16 </span>'  + '&nbsp;&nbsp;&nbsp;&nbsp; <span style = "color : red;">' + "PLL_scan_report" + '    < Fail >' + '</span>'  + '\n')
                info = dict_to_markdown_table(log.report_log1601[femb_id])
                file.write(info + '\n')
                file.write("[PDF](./{}/report.pdf)".format(log.item16) + "\n")
    return fpmd







# final report, generate every analysis
def final_report(datareport, fembs, fembNo, fembsName):
    print("\n\n\n")
    print("==================================================================================")
    print("+++++++               GENERAL REPORT for FEMB BOARDS TESTING               +++++++")
    print("+++++++                                                                    +++++++")
    print("==================================================================================")
    print("\n")
    print(log.report_log01["ITEM"])
    for key, value in log.report_log01["Detail"].items():
        print(f"{key}: {value}")

    print('\n')

    all_true = {}
    PH = 250
    for ifemb in fembs:
        femb_id = "FEMB ID {}".format(fembNo['femb%d' % ifemb])
###======================== Whole judgement =============================
#   item 01 Power Consumption
        check_list = []
        check_status = [None for _ in range(1, 17)]
        item_file = [None for _ in range(1, 17)]
        print(check_status)

        for root, dirs, files in os.walk(datareport[ifemb]):
            for file in files:
                if file.endswith('.md'):
                    for i in range(1,17,1):
                        if 't{}_F'.format(i) in file:
                            check_status[i - 1] = False
                            item_file[i - 1] = file
                        elif 't{}_P'.format(i) in file:
                            check_status[i - 1] = True
                            item_file[i - 1] = file
        print(check_status)
        all_true = all(check_status)
        if None in check_status:
            summary = '<span style="color: dark;">' + " FEMB # {}\t       Quality Control in Test ".format(fembsName['femb%d' % ifemb]) + '</span>' + '\n'
        else:
            if all_true:
                summary = '<span style="color: green;">' + " FEMB # {}\t      PASS\t    Quality Control".format(fembsName['femb%d' % ifemb]) + '</span>'  + '\n'
            else:
                summary = '<span style="color: red;">' + " FEMB # {}\t      fail\t    the Quality Control tests".format(fembsName['femb%d' % ifemb]) + '</span>'  + '\n'
        print(summary)

###======================================================================

#   Start Markdown

        print('\n')
        frmd = datareport[ifemb] + 'Final_Report_FEMB_{}_S{}.md'.format(fembsName['femb%d' % ifemb], ifemb)
        print(datareport[ifemb])
        with open(frmd, 'w', encoding = "utf-8") as file:
            # file.write('')
            file.write('\n')
            file.write('\n')
            file.write('# ' + summary + '\n')
            file.write('\n')
            file.write('\n')
# Title     FEMB ID
# 00        Print <Input Information>
            file.write('## INPUT INFORMATION &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; {}'.format(femb_id) + '\n')
            info = dict_to_markdown_table(log.report_log00, VALUE="Horizontal")
            file.write(info + '\n')

            file.write('## Test Content' + '\n')


##  Content Pages ================================================
            if check_status[1-1] is True:
                Item01 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: green;">' + 'Item_01 POWER CONSUMPTION' + '&nbsp;&nbsp;&nbsp;&nbsp; [Pass](./{})'.format(item_file[1-1]) + '</span>\n\n'
                Item01 += "&nbsp;&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp;&nbsp; Power Consumption in the accepted range.\n\n &nbsp;&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp;&nbsp;  Total Power at Typical Configuration [14 mV/fC; 2 us; 1 nA; 200 mV] is normal"
            elif check_status[1-1] is False:
                Item01 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: red;">' + 'Item_01 POWER CONSUMPTION' + '&nbsp;&nbsp;&nbsp;&nbsp; < Fail > [Detail](./{})'.format(item_file[1-1]) + '</span>'
            else:
                Item01 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: gray;">' + 'Item_01 POWER CONSUMPTION' + '&nbsp;&nbsp;&nbsp;&nbsp; < No Test >' + '</span>'
            file.write(Item01 + '\n\n')

            if check_status[2-1] is True:
                Item02 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: green;">' + 'Item_02 Power Cycle' + '&nbsp;&nbsp;&nbsp;&nbsp; [Pass](./{})'.format(item_file[2-1]) + '</span>\n\n'
                Item02 += "&nbsp;&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp;&nbsp; PASS five time Power Cycles with different configuratoin\n\n &nbsp;&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp;&nbsp; Power consumption are all in accepted range\n Each Ch in FE is activated and response to pulse"
            elif check_status[2 - 1] is False:
                Item02 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: red;">' + 'Item_02 Power Cycle' + '&nbsp;&nbsp;&nbsp;&nbsp; < Fail > [Detail](./{})'.format(item_file[2-1]) + '</span>'
            else:
                Item02 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: gray;">' + 'Item_02 Power Cycle' + '&nbsp;&nbsp;&nbsp;&nbsp; < No Test >' + '</span>'
            file.write(Item02 + '\n\n')

            if check_status[3-1] is True:
                Item03 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: green;">' + 'Item_03 FE Pulse Response at Different Leakage Current Setting' + '&nbsp;&nbsp;&nbsp;&nbsp; [Pass](./{})'.format(item_file[3-1]) + '</span>\n\n'
                Item03 += "&nbsp;&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp;&nbsp; Each FE channel is activated to the injected charge pulser under 100 pA, 500 pA, 1 nA, 5 nA FE Leakage current \n"
            elif check_status[3 - 1] is False:
                Item03 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: red;">' + 'Item_03 FE Pulse Response at Different Leakage Current Setting' + '&nbsp;&nbsp;&nbsp;&nbsp; < Fail > [Detail](./{})'.format(item_file[3-1]) + '</span>'
            else:
                Item03 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: gray;">' + 'Item_03 FE Pulse Response at Different Leakage Current Setting' + '&nbsp;&nbsp;&nbsp;&nbsp; < No Test >' + '</span>'
            file.write(Item03 + '\n\n')

            if check_status[4-1] is True:
                Item04 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: green;">' + 'Item_04 Pulse Response' + '&nbsp;&nbsp;&nbsp;&nbsp; [Pass](./{})'.format(item_file[4-1]) + '</span>\n\n'
                Item04 += "&nbsp;&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp;&nbsp; Each FE Chann\el is activated to the whole pulse response \n\n&nbsp;&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp;&nbsp; The pulser under configurations combined with different Gains different Tps, different FE output mode, different Baseline"
            elif check_status[4 - 1] is False:
                Item04 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: red;">' + 'Item_04 Pulse Response' + '&nbsp;&nbsp;&nbsp;&nbsp; < Fail > [Detail](./{})'.format(item_file[4-1]) + '</span>'
            else:
                Item04 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: gray;">' + 'Item_04 Pulse Response' + '&nbsp;&nbsp;&nbsp;&nbsp; < No Test >' + '</span>'
            file.write(Item04 + '\n\n')

            if check_status[5-1] is True:
                Item05 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: green;">' + 'Item_05 Noise Evaluation' + '&nbsp;&nbsp;&nbsp;&nbsp; [Pass](./{})'.format(item_file[5-1]) + '</span>\n\n'
                Item05 += "&nbsp;&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp;&nbsp; Noise is in the accepted range. \n\n&nbsp;&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp;&nbsp; Each FE channel presents noise level under Cd ~100 pF. Indicate the route from FE input connnector to FE ASIC input is good"
            elif check_status[5 - 1] is False:
                Item05 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: red;">' + 'Item_05 Noise Evaluation' + '&nbsp;&nbsp;&nbsp;&nbsp; < Fail > [Detail](./{})'.format(item_file[5-1]) + '</span>'
            else:
                Item05 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: gray;">' + 'Item_05 Noise Evaluation' + '&nbsp;&nbsp;&nbsp;&nbsp; < No Test >' + '</span>'
            file.write(Item05 + '\n\n')

            if check_status[6-1] is True:
                Item06 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: green;">' + 'Item_06 Cali_1 configuration SE_OFF 200 mV' + '&nbsp;&nbsp;&nbsp;&nbsp; [Pass](./{})'.format(item_file[6-1]) + '</span>\n\n'
                Item06 += '&nbsp;&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp;&nbsp; Calibrated with LArASIC embeded DAC [200 mV Baseline]\n\n'
                Item06 += '&nbsp;&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp;&nbsp; Measured Inverted Gain at 4.7 mV/fC, DAC = [0, 63, 8] Pass\n\n'
                Item06 += '&nbsp;&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp;&nbsp; Measured Inverted Gain at 7.8 mV/fC, DAC = [0, 63, 1] Pass\n\n'
                Item06 += '&nbsp;&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp;&nbsp; Measured Inverted Gain at 14 mV/fC, DAC = [0, 63, 8] Pass\n\n'
                Item06 += '&nbsp;&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp;&nbsp; Measured Inverted Gain at 25 mV/fC, DAC = [0, 63, 8] Pass\n\n'
            elif check_status[6 - 1] is False:
                Item06 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: red;">' + 'Item_06 Cali_1 configuration SE_OFF 200 mV' + '&nbsp;&nbsp;&nbsp;&nbsp; < Fail > [Detail](./{})'.format(item_file[6-1]) + '</span>\n'
            else:
                Item06 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: gray;">' + 'Item_06 Cali_1 configuration SE_OFF 200 mV' + '&nbsp;&nbsp;&nbsp;&nbsp; < No Test >' + '</span>'
            file.write(Item06 + '\n\n')

            if check_status[7-1] is True:
                Item07 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: green;">' + 'Item_07 Cali_2 configuration SE_OFF 900 mV' + '&nbsp;&nbsp;&nbsp;&nbsp; [Pass](./{})'.format(item_file[7-1]) + '</span>\n\n'
                Item07 += "&nbsp;&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp;&nbsp; Calibrated with LArASIC embeded DAC [900 mV Baseline]\n\n"
                Item07 += '&nbsp;&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp;&nbsp; Measured Inverted Gain at 14 mV/fC, DAC = [0, 63, 8] Pass'

            elif check_status[7 - 1] is False:
                Item07 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: red;">' + 'Item_07 Cali_2 configuration SE_OFF 900 mV' + '&nbsp;&nbsp;&nbsp;&nbsp; < Fail > [Detail](./{})'.format(item_file[7-1]) + '</span>'
            else:
                Item07 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: gray;">' + 'Item_07 Cali_2 configuration SE_OFF 900 mV' + '&nbsp;&nbsp;&nbsp;&nbsp; < No Test >' + '</span>'
            file.write(Item07 + '\n\n')

            if check_status[8-1] is True:
                Item08 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: green;">' + 'Item_08 Cali_3 SGP1 SE_OFF 200 mV' + '&nbsp;&nbsp;&nbsp;&nbsp; [Pass](./{})'.format(item_file[8-1]) + '</span>\n\n'
                Item08 += "&nbsp;&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp;&nbsp; Calibrated with LArASIC embeded DAC [200 mV Baseline]\n\n"
                Item08 += '&nbsp;&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp;&nbsp; Measured Inverted Gain at 14 mV/fC, DAC = [0, 63, 8] Pass\n\n'
                Item08 += "&nbsp;&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp;&nbsp; No Rall back issue is observed from large Charge pulse while FE is staurated"
            elif check_status[8 - 1] is False:
                Item08 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: red;">' + 'Item_08 Cali_3 SGP1 SE_OFF 200 mV' + '&nbsp;&nbsp;&nbsp;&nbsp; < Fail > [Detail](./{})'.format(item_file[8-1]) + '</span>'
            else:
                Item08 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: gray;">' + 'Item_08 Cali_3 SGP1 SE_OFF 200 mV' + '&nbsp;&nbsp;&nbsp;&nbsp; < No Test >' + '</span>'
            file.write(Item08 + '\n\n')

            if check_status[9-1] is True:
                Item09 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: green;">' + 'Item_09 Cali_4 SGP1 SE_OFF 900 mV' + '&nbsp;&nbsp;&nbsp;&nbsp; [Pass](./{})'.format(item_file[9-1]) + '</span>\n\n'
                Item09 += "&nbsp;&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp;&nbsp; Calibrated with LArASIC embeded DAC [900 mV Baseline]\n\n"
                Item09 += '&nbsp;&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp;&nbsp; Measured Inverted Gain at 14 mV/fC, DAC = [0, 32, 4] Pass\n\n'
                Item09 += "&nbsp;&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp;&nbsp; No Rall back issue is observed from large Charge pulse while FE is staurated"
            elif check_status[9 - 1] is False:
                Item09 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: red;">' + 'Item_09 Cali_4 SGP1 SE_OFF 900 mV' + '&nbsp;&nbsp;&nbsp;&nbsp; < Fail > [Detail](./{})'.format(item_file[9-1]) + '</span>'
            else:
                Item09 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: gray;">' + 'Item_09 Cali_4 SGP1 SE_OFF 900 mV' + '&nbsp;&nbsp;&nbsp;&nbsp; < No Test >' + '</span>'
            file.write(Item09 + '\n\n')

            if check_status[10-1] is True:
                Item10 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: green;">' + 'Item_10 FE Monitor via WIB DAC' + '&nbsp;&nbsp;&nbsp;&nbsp; [Pass](./{})'.format(item_file[10-1]) + '</span>\n\n'
                Item10 += "&nbsp;&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp;&nbsp; Measured Temperature FE PASS\n\n"
                Item10 += "&nbsp;&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp;&nbsp; Measured Bandgap FE PASS\n\n"
                Item10 += "&nbsp;&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp;&nbsp; Measured Baseline 200 mV of FE PASS\n\n"
                Item10 += "&nbsp;&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp;&nbsp; Measured Baseline 900 mV of FE PASS"
            elif check_status[10 - 1] is False:
                Item10 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: red;">' + 'Item_10 FE Monitor' + '&nbsp;&nbsp;&nbsp;&nbsp; < Fail > [Detail](./{})'.format(item_file[10-1]) + '</span>'
            else:
                Item10 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: gray;">' + 'Item_10 FE Monitor' + '&nbsp;&nbsp;&nbsp;&nbsp; < No Test >' + '</span>'
            file.write(Item10 + '\n\n')

            if check_status[11-1] is True:
                Item11 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: green;">' + 'Item_11 FE DAC Linearity Monitor via WIB ADC' + '&nbsp;&nbsp;&nbsp;&nbsp; [Pass](./{})'.format(item_file[11-1]) + '</span>\n\n'
                Item11 += "&nbsp;&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp;&nbsp; Gain mV/fC, LSB, Range, INL\n\n"
                Item11 += "&nbsp;&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp;&nbsp; 4.7, LSB, Range, INL\n\n"
                Item11 += "&nbsp;&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp;&nbsp; 7.8, LSB, Range, INL\n\n"
                Item11 += "&nbsp;&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp;&nbsp; 14, LSB, Range, INL\n\n"
                Item11 += "&nbsp;&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp;&nbsp; 25, LSB, Range, INL"
            elif check_status[11 - 1] is False:
                Item11 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: red;">' + 'Item_11 FE DAC Linearity Monitor via WIB ADC' + '&nbsp;&nbsp;&nbsp;&nbsp; < Fail > [Detail](./{})'.format(item_file[11-1]) + '</span>'
            else:
                Item11 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: gray;">' + 'Item_11 FE DAC Linearity Monitor via WIB ADC' + '&nbsp;&nbsp;&nbsp;&nbsp; < No Test >' + '</span>'
            file.write(Item11 + '\n\n')

            if check_status[12-1] is True:
                Item12 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: green;">' + 'Item_12 ColdADC ref_voltage Linearity' + '&nbsp;&nbsp;&nbsp;&nbsp; [Pass](./{})'.format(item_file[12-1]) + '</span>\n\n'
            elif check_status[12 - 1] is False:
                Item12 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: red;">' + 'Item_12 ColdADC ref_voltage Linearity' + '&nbsp;&nbsp;&nbsp;&nbsp; < Fail > [Detail](./{})'.format(item_file[12-1]) + '</span>'
            else:
                Item12 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: gray;">' + 'Item_12 ColdADC ref_voltage Linearity' + '&nbsp;&nbsp;&nbsp;&nbsp; < No Test >' + '</span>'
            file.write(Item12 + '\n\n')

            rows = [
                ["Voltage", "LSB", "Range", "INL", "Status"],
                ["Vrefp", "LSB", "Range", "INL", "PASS"],
                ["Vrefn", "LSB", "Range", "INL", "PASS"],
                ["Vcmi", "LSB", "Range", "INL", "PASS"],
                ["Vcmo", "LSB", "Range", "INL", "PASS"]
            ]

            # Use GitHub-style markdown table
            md_table = tabulate(rows, headers="firstrow", tablefmt="github")
            file.write(md_table + '\n\n')

            if check_status[13-1] is True:
                Item13 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: green;">' + 'Item_13 External Pulse Calibration 900mV baseline' + '&nbsp;&nbsp;&nbsp;&nbsp; [Pass](./{})'.format(item_file[13-1]) + '</span>\n\n'
                Item13 += "&nbsp;&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp;&nbsp; Calibrated with External pulse from WIB\n\n"
                Item13 += "&nbsp;&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp;&nbsp; Measured Inverted Gain at 14 mV/fC, baseline = 900 mV\n\n"
            elif check_status[13 - 1] is False:
                Item13 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: red;">' + 'Item_13 External Pulse Calibration 900mV baseline' + '&nbsp;&nbsp;&nbsp;&nbsp; < Fail > [Detail](./{})'.format(item_file[13-1]) + '</span>'
            else:
                Item13 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: gray;">' + 'Item_13 External Pulse Calibration 900mV baseline' + '&nbsp;&nbsp;&nbsp;&nbsp; < No Test >' + '</span>'
            file.write(Item13 + '\n\n')

            if check_status[14-1] is True:
                Item14 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: green;">' + 'Item_14 External Pulse Calibration 200mV baseline' + '&nbsp;&nbsp;&nbsp;&nbsp; [Pass](./{})'.format(item_file[14-1]) + '</span>\n\n'
                Item14 += "&nbsp;&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp;&nbsp; Calibrated with External pulse from WIB\n\n"
                Item14 += "&nbsp;&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp;&nbsp; Measured Inverted Gain at 14 mV/fC, baseline = 200 mV\n\n"
            elif check_status[14 - 1] is False:
                Item14 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: red;">' + 'Item_14 External Pulse Calibration 200mV baseline' + '&nbsp;&nbsp;&nbsp;&nbsp; < Fail > [Detail](./{})'.format(item_file[14-1]) + '</span>'
            else:
                Item14 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: gray;">' + 'Item_14 External Pulse Calibration 200mV baseline' + '&nbsp;&nbsp;&nbsp;&nbsp; < No Test >' + '</span>'
            file.write(Item14 + '\n\n')

            if check_status[15-1] is True:
                Item15 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: green;">' + 'Item_15 ColdADC_sync_pat_report' + '&nbsp;&nbsp;&nbsp;&nbsp; [Pass](./{})'.format(item_file[15-1]) + '</span>\n\n'
                Item15 += "&nbsp;&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp;&nbsp; ADC Noise Under ADC Test Mode (Bypass MUX inputs) PASS\n\n"
                Item15 += "&nbsp;&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp;&nbsp; ADC SYNC PAT SHA DIFF PASS\n\n"
                Item15 += "&nbsp;&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp;&nbsp; ADC SYNC PAT SHA Test PASS\n\n"
            elif check_status[15 - 1] is False:
                Item15 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: red;">' + 'Item_15 ColdADC_sync_pat_report' + '&nbsp;&nbsp;&nbsp;&nbsp; < Fail > [Detail](./{})'.format(item_file[15-1]) + '</span>'
            else:
                Item15 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: gray;">' + 'Item_15 ColdADC_sync_pat_report' + '&nbsp;&nbsp;&nbsp;&nbsp; < No Test >' + '</span>'
            file.write(Item15 + '\n\n')

            if check_status[16-1] is True:  # Lingyun Ke set
                Item16 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: green;">' + 'Item_16 PLL_scan_report' + '&nbsp;&nbsp;&nbsp;&nbsp; [Pass](./{})'.format(item_file[16-1]) + '</span>\n\n'
                Item16 += "&nbsp;&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp;&nbsp; COLDATA PLL Bandgap is in the accepted range (0x21 ~ 0x28)"
            elif check_status[16 - 1] is False:
                Item16 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: red;">' + 'Item_16 PLL_scan_report' + '&nbsp;&nbsp;&nbsp;&nbsp; < Fail > [Detail](./{})'.format(item_file[16-1]) + '</span>'
            else:
                Item16 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: gray;">' + 'Item_16 PLL_scan_report' + '&nbsp;&nbsp;&nbsp;&nbsp; < No Test >' + '</span>'
            file.write(Item16 + '\n\n')

            file.write("------\n")

            if check_status[1-1] is not None:
                file.write('Power Consumption:' + "\n\n")
                file.write('&nbsp;&nbsp;&nbsp;&nbsp; <img src="./PWR_Meas/Power_Total.png" alt="picture" height="500">' + "\n\n")  # width="200"
            if check_status[4-1] is not None:
                file.write('Pulse Measurement:' + "\n\n")
                file.write('<img src="./CHK/SE_900_Gain_Pulse_ErrorBar.png" alt="picture" height="500">' + "\n\n")  # width="200"
            if check_status[5-1] is not None:
                file.write('Noise Measurement 14mV/fC, 2 us, SE OFF, 200 & 900 mV BL:' + "\n\n")
                file.write('<img src="./RMS/SE_200_900_mV_RMS_ErrorBar.png" alt="picture" height="500">' + "\n\n")  # width="200"
            if check_status[6-1] is not None:
                file.write('Calibration Measurement:' + "\n\n")
                file.write('<img src="./CALI1_DIFF/SE_Gain.png" alt="picture" height="500">' + "\n\n")  # width="200"
                file.write('<img src="./CALI1_DIFF/SE_ENC_noise.png" alt="picture" height="500">' + "\n\n")  # width="200"
            if check_status[10-1] is not None:
                file.write('FE Mon Measurement:' + "\n\n")
                file.write('<img src="./MON_FE/FE_Mon.png" alt="picture" height="500">' + "\n\n")  # width="200"
            if check_status[11-1] is not None:
                file.write('FE DAC Measurement:' + "\n\n")
                file.write('<img src="./MON_FE/mon_LArASIC_DAC_25mVfC.png" alt="picture" height="500">' + "\n\n")  # width="200"
            if check_status[12-1] is not None:
                file.write('ColdADC Linearity Measurement:' + "\n\n")
                file.write(
                    '<img src="./{}/mon_VREFP.png" alt="picture" height="230">'.format(log.item12))  # width="200"
                file.write(
                    '<img src="./{}/mon_VREFN.png" alt="picture" height="230">'.format(log.item12) + "\n\n")  # width="200"
                file.write(
                    '<img src="./{}/mon_VCMI.png" alt="picture" height="230">'.format(
                        log.item12))  # width="200"
                file.write(
                    '<img src="./{}/mon_VCMO.png" alt="picture" height="230">'.format(
                        log.item12) + "\n")  # width="200"
                file.write('\n')


            # if check_status[11-1] is not None:
            #     file.write('<img src="./MON_FE/mon_LArASIC_DAC_25mVfC.png" alt="picture" height="250">' + "\n\n")  # width="200"
            file.write("------\n")
            # file.write('lke@bnl.gov' + '<br>\n')

            print("QC Report file saved")