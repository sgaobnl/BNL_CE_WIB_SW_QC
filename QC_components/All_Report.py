import QC_components.qc_log as log
import subprocess
import matplotlib.pyplot as plt


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
        table += '|' + '|'.join(str(dictionary[key]) for key in dictionary.keys()) + '|' + '\n'
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




def final_report(datareport, fembs, fembNo):
    print("\n\n\n")
    print("==================================================================================")
    print("+++++++               GENERAL REPORT for FEMB BOARDS TESTING               +++++++")
    print("+++++++                                                                    +++++++")
    print("==================================================================================")
    print("\n")
    print(log.report_log01["ITEM"])
    for key, value in log.report_log01["Detail"].items():
        print(f"{key}: {value}")

    print('/n')

    all_true = {}

    for ifemb in fembs:
        femb_id = "FEMB ID {}".format(fembNo['femb%d' % ifemb])
###======================== Whole judgement =============================
#   item 01 Power Consumption
        check_list = []
        if 1 in log.test_label:
            dict_list01 = [log.check_log01_11[femb_id], log.check_log01_12[femb_id], log.check_log01_13[femb_id], log.check_log01_21[femb_id], log.check_log01_22[femb_id], log.check_log01_23[femb_id], log.check_log01_31[femb_id], log.check_log01_32[femb_id], log.check_log01_33[femb_id]]
            check_status01 = True
            check_list01 = []
            for dict_i in dict_list01:
                if dict_i['Result'] == False:
                    check_status01 = False
                    check_list01.append(str(dict_i['Label']) + "\n")
                    check_list01.append(str(dict_i['Issue List']) + "\n")
            check_list.append(check_status01)

        if 3 in log.test_label:
            dict_list03 = [log.check_log03_01[femb_id], log.check_log03_02[femb_id], log.check_log03_03[femb_id], log.check_log03_04[femb_id]]
            check_status03 = True
            check_list03 = []
            for dict_i in dict_list03:
                if dict_i['Result'] == False:
                    check_status03 = False
                    check_list03.append(str(dict_i['Label']) + "\n")
                    check_list03.append(str(dict_i['Issue List']) + "\n")
            check_list.append(check_status03)

        if 4 in log.test_label:
            dict_list04 = [log.check_log04_01[femb_id], log.check_log04_02[femb_id], log.check_log04_03[femb_id], log.check_log04_04[femb_id], log.check_log04_05[femb_id], log.check_log04_06[femb_id]]
            check_status04 = True
            check_list04 = []
            for dict_i in dict_list04:
                if dict_i['Result'] == False:
                    check_status04 = False
                    check_list04.append(str(dict_i['Label']) + "\n")
                    check_list04.append(str(dict_i['Issue List']) + "\n")
            check_list.append(check_status04)

        if 5 in log.test_label:
            # dict_list05 = [log.report_log0500[femb_id]]
            check_status05 = True
            # check_list05 = []
            # for dict_i in dict_list05:
            if log.report_log0500[femb_id] == False:
                check_status05 = False
                # check_list05.append(str(dict_i['Label']) + "\n")
                # check_list05.append(str(dict_i['Issue List']) + "\n")
            # check_list.append(check_status05)

        if 6 in log.test_label:
            dict_list06 = [log.check_log0601[femb_id], log.check_log0602[femb_id], log.check_log0603[femb_id], log.check_log0604[femb_id], log.check_log0605[femb_id]]
            check_status06 = True
            check_list06 = []
            for dict_i in dict_list06:
                if dict_i['Result'] == False:
                    check_status06 = False
                    # check_list06.append(str(dict_i['Label']) + "\n")
                    check_list06.append(str(dict_i['Issue List']) + "\n")
            check_list.append(check_status06)

        if 7 in log.test_label:
            dict_list07 = [log.check_log0701[femb_id], log.check_log0702[femb_id]]
            check_status07 = True
            check_list07 = []
            for dict_i in dict_list07:
                if dict_i['Result'] == False:
                    check_status07 = False
                    # check_list07.append(str(dict_i['Label']) + "\n")
                    check_list07.append(str(dict_i['Issue List']) + "\n")
            check_list.append(check_status07)

        if 8 in log.test_label:
            dict_list08 = [log.check_log0801[femb_id]]
            check_status08 = True
            check_list08 = []
            for dict_i in dict_list08:
                if dict_i['Result'] == False:
                    check_status08 = False
                    # check_list07.append(str(dict_i['Label']) + "\n")
                    check_list08.append(str(dict_i['Issue List']) + "\n")
            check_list.append(check_status08)

        if 9 in log.test_label:
            dict_list09 = [log.check_log0901[femb_id]]
            check_status09 = True
            check_list09 = []
            for dict_i in dict_list09:
                if dict_i['Result'] == False:
                    check_status09 = False
                    # check_list07.append(str(dict_i['Label']) + "\n")
                    check_list09.append(str(dict_i['Issue List']) + "\n")
            check_list.append(check_status09)

        if 10 in log.test_label:
            dict_list10 = [log.check_log1001[femb_id]]
            check_status10 = True
            check_list10 = []
            for dict_i in dict_list10:
                if dict_i['Result'] == False:
                    check_status10 = False
                    # check_list07.append(str(dict_i['Label']) + "\n")
                    check_list10.append(str(dict_i['Issue List']) + "\n")
            check_list.append(check_status10)


        if 11 in log.test_label:
            dict_list11 = [log.check_log1101[femb_id]]
            check_status11 = True
            check_list11 = []
            for dict_i in dict_list11:
                if dict_i['Result'] == False:
                    check_status11 = False
                    # check_list07.append(str(dict_i['Label']) + "\n")
                    # check_list11.append(str(dict_i['Issue List']) + "\n")
            check_list.append(check_status11)

        if 12 in log.test_label:
            dict_list12 = [log.check_log1201[femb_id]]
            check_status12 = True
            check_list12 = []
            for dict_i in dict_list12:
                if dict_i['Result'] == False:
                    check_status12 = False
                    # check_list07.append(str(dict_i['Label']) + "\n")
                    # check_list12.append(str(dict_i['Issue List']) + "\n")
            check_list.append(check_status12)

        if 13 in log.test_label:
            dict_list13 = [log.check_log1301[femb_id]]
            check_status13 = True
            check_list13 = []
            for dict_i in dict_list13:
                if dict_i['Result'] == False:
                    check_status13 = False
                    # check_list07.append(str(dict_i['Label']) + "\n")
                    # check_list13.append(str(dict_i['Issue List']) + "\n")
            check_list.append(check_status13)

        if 14 in log.test_label:
            dict_list14 = [log.check_log1401[femb_id]]
            check_status14 = True
            check_list14 = []
            for dict_i in dict_list14:
                if dict_i['Result'] == False:
                    check_status14 = False
                    # check_list07.append(str(dict_i['Label']) + "\n")
                    # check_list14.append(str(dict_i['Issue List']) + "\n")
            check_list.append(check_status14)

        if 16 in log.test_label:
            dict_list16 = [log.check_log1601[femb_id]]
            check_status16 = True
            check_list16 = []
            for dict_i in dict_list16:
                if dict_i['Result'] == False:
                    check_status16 = False
                    # check_list07.append(str(dict_i['Label']) + "\n")
                    # check_list16.append(str(dict_i['Issue List']) + "\n")
            check_list.append(check_status16)

        all_true = all(value for value in check_list)
        if all_true:
            summary = '<span style="color: green;">' + " FEMB # {}\t      PASS\t    ALL Quality Control".format(fembNo['femb%d' % ifemb]) + '</span>'  + '\n'
        else:
            summary = '<span style="color: red;">' + " FEMB # {}\t      Fail\t    ALL Quality Control".format(fembNo['femb%d' % ifemb]) + '</span>'  + '\n'
###======================================================================

#   Start Markdown
        fpmd = datareport[ifemb] + 'report_FEMB_{}.md'.format(fembNo['femb%d' % ifemb])
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
            file.write('## INPUT INFORMATION &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; {}'.format(femb_id) + '\n')
            info = dict_to_markdown_table(log.report_log00, VALUE="Horizontal")
            file.write(info + '\n')

            file.write('## Test Status' + '\n')
            if 1 in log.test_label:
                if check_status01:
                    Item01 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: green;">' + 'Item_01 POWER CONSUMPTION' + '&nbsp;&nbsp;&nbsp;&nbsp; < Pass >' + '</span>'
                else:
                    Item01 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: red;">' + 'Item_01 POWER CONSUMPTION' + '&nbsp;&nbsp;&nbsp;&nbsp; < Fail >' + '</span>'
                file.write('[Chapter_1](#item1)' + Item01 + '\n\n')
            file.write("------\n")
            file.write('<img src="./PWR_Meas/Power_Total.png" alt="picture" height="270">' + "\n\n")  # width="200"
            file.write("------\n")

##  Detail Pages

# 01        Print <Power Consumption>
            if 1 in log.test_label:
                if check_status01:
                    Head01 = '### ' + '</span>' + '<span id="item1"> Chapter_1 </span>'  + '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: green;">' + 'ITEM_01_POWER_CONSUMPTION' + '    < Pass >' + '</span>' + '\n'
                else:
                    Head01 = '### ' + '</span>' + '<span id="item1"> Chapter_1 </span>'  + '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: red;">' + 'ITEM_01_POWER_CONSUMPTION' + '    < Fail >' + '</span>'  + '\n'
                file.write(Head01 + '\n')
                file.write("------\n")
                file.write('### 1_1 &nbsp;&nbsp;&nbsp;&nbsp; Power Measurement'  + '\n')
                info = dict_to_markdown_table(log.report_log01_11[femb_id], KEY = "Single-End Interface OFF", VALUE="PWRVALUE")
                file.write(info + '\n')

                info = dict_to_markdown_table(log.report_log01_21[femb_id], KEY = "Single-End Interface ON", VALUE="PWRVALUE")
                file.write(info + '\n')

                info = dict_to_markdown_table(log.report_log01_31[femb_id], KEY = "Differential Interface ON", VALUE="PWRVALUE")
                file.write(info + '\n')

                file.write('### 1_2 &nbsp;&nbsp;&nbsp;&nbsp; Power Rail' + '\n')
                file.write('<div style = "display: flex; justify-content: space-between;">'+'\n\n')
                info = dict_to_markdown_table(log.report_log01_13[femb_id], KEY="SE OFF Voltage", VALUE = "Rail")
                file.write(info + '\n\n')
                info = dict_to_markdown_table(log.report_log01_23[femb_id], KEY="SE ON Voltage", VALUE = "Rail")
                file.write(info + '\n\n')
                info = dict_to_markdown_table(log.report_log01_33[femb_id], KEY="DIFF Voltage", VALUE="Rail")
                file.write(info + '\n\n')
                file.write('</div>' + '\n\n')

                file.write('### 01_3 &nbsp;&nbsp;&nbsp;&nbsp; Initial Pulse Check' + '\n')
                file.write('<div style = "display: flex; justify-content: space-between;">' + '\n\n')
                info = dict_to_markdown_table(log.report_log01_12[femb_id], KEY="SE OFF pulse", VALUE = "Pulse")
                file.write(info + '\n\n')
                info = dict_to_markdown_table(log.report_log01_22[femb_id], KEY="SE ON pulse", VALUE = "Pulse")
                file.write(info + '\n\n')
                info = dict_to_markdown_table(log.report_log01_32[femb_id], KEY="DIFF pulse", VALUE = "Pulse")
                file.write(info + '\n\n')
                file.write('</div>' + '\n\n')
                file.write('<details>'+ '\n\n')
                file.write('<img src="./PWR_Meas/pulse_PWR_SE_OFF_200mVBL_14_0mVfC_2_0us.png" alt="picture" height="200">' + "\n") #width="200"
                file.write('<img src="./PWR_Meas/pulse_PWR_SE_ON_200mVBL_14_0mVfC_2_0us.png" alt="picture" height="200">' + "\n") #width="200"
                file.write('<img src="./PWR_Meas/pulse_PWR_DIFF_200mVBL_14_0mVfC_2_0us.png" alt="picture" height="200">' + "\n") #width="200"
                file.write('</details>'+ '\n\n')



# 03
            if 3 in log.test_label:
                if check_status03:
                    Head03 = '### ' + '<span style="color: green;">' + 'ITEM 03 Leakage Current Pulse Response' + '    < Pass >' + '</span>'  + '\n'
                else:
                    Head03 = '### ' + '<span style="color: red;">' + 'ITEM 03 Leakage Current Pulse Response' + '    < Fail >' + '</span>'  + '\n'
                file.write(Head03 + '\n')
                file.write("------\n")
                file.write("![ped](./Leakage_Current/LC_pulse.png)" + "\n")

                log.check_log03_table_01[femb_id]['title'] = " | Leakage <bar> Current | 100 pA | 500 pA | 1 nA | 5 nA | \n"
                log.check_log03_table_01[femb_id]['table line'] = " | --- | --- | --- | --- | --- | \n"
                log.check_log03_table_01[femb_id]['ppk_mean'] = " | Amplitude Mean | {} | {} | {} | {} | \n".format(log.report_log03_02[femb_id]["LC_SE_200mVBL_14_0mVfC_2_0us_0x20_100pA_ppk_mean0"], log.report_log03_01[femb_id]["LC_SE_200mVBL_14_0mVfC_2_0us_0x20_500pA_ppk_mean0"], log.report_log03_04[femb_id]["LC_SE_200mVBL_14_0mVfC_2_0us_0x20_1nA_ppk_mean0"], log.report_log03_03[femb_id]["LC_SE_200mVBL_14_0mVfC_2_0us_0x20_5nA_ppk_mean0"])
                # log.check_log03_table_01[femb_id]['ppk_err'] = " | PPK Std | {} | {} | {} | {} | \n".format(log.report_log03_02[femb_id]["LC_SE_200mVBL_14_0mVfC_2_0us_0x20_100pA_ppk_err0"], log.report_log03_01[femb_id]["LC_SE_200mVBL_14_0mVfC_2_0us_0x20_500pA_ppk_err0"], log.report_log03_04[femb_id]["LC_SE_200mVBL_14_0mVfC_2_0us_0x20_1nA_ppk_err0"], log.report_log03_03[femb_id]["LC_SE_200mVBL_14_0mVfC_2_0us_0x20_5nA_ppk_err0"])
                log.check_log03_table_01[femb_id]['npk_mean'] = " | Pedestal Mean | {} | {} | {} | {} | \n".format(log.report_log03_02[femb_id]["LC_SE_200mVBL_14_0mVfC_2_0us_0x20_100pA_npk_mean0"], log.report_log03_01[femb_id]["LC_SE_200mVBL_14_0mVfC_2_0us_0x20_500pA_npk_mean0"], log.report_log03_04[femb_id]["LC_SE_200mVBL_14_0mVfC_2_0us_0x20_1nA_npk_mean0"], log.report_log03_03[femb_id]["LC_SE_200mVBL_14_0mVfC_2_0us_0x20_5nA_npk_mean0"])
                # log.check_log03_table_01[femb_id]['npk_err'] = " | NPK Std | {} | {} | {} | {} | \n".format(log.report_log03_02[femb_id]["LC_SE_200mVBL_14_0mVfC_2_0us_0x20_100pA_npk_err0"], log.report_log03_01[femb_id]["LC_SE_200mVBL_14_0mVfC_2_0us_0x20_500pA_npk_err0"], log.report_log03_04[femb_id]["LC_SE_200mVBL_14_0mVfC_2_0us_0x20_1nA_npk_err0"], log.report_log03_03[femb_id]["LC_SE_200mVBL_14_0mVfC_2_0us_0x20_5nA_npk_err0"])

                file.write(log.check_log03_table_01[femb_id]['title'])
                file.write(log.check_log03_table_01[femb_id]['table line'])
                file.write(log.check_log03_table_01[femb_id]['ppk_mean'])
                # file.write(log.check_log03_table_01[femb_id]['ppk_err'])
                file.write(log.check_log03_table_01[femb_id]['npk_mean'] + '\n')
                # file.write(log.check_log03_table_01[femb_id]['npk_err'] + '\n')
                file.write('<details>' + '\n')
                file.write('<summary> Detail </summary>' + '\n')
                file.write("------\n")
                file.write('### 03_01 {} pulse'.format(log.check_log03_01[femb_id]['Label']) + '\n')
                info = dict_to_markdown_table(log.report_log03_01[femb_id], VALUE="Horizontal")
                file.write(info + '\n')
                file.write("![ped](./Leakage_Current/pulse_LC_SE_200mVBL_14_0mVfC_2_0us_0x20_500pA.png)" + "\n")

                file.write("------\n")
                file.write('### 03_02 {} pulse'.format(log.check_log03_02[femb_id]['Label']) + '\n')
                info = dict_to_markdown_table(log.report_log03_02[femb_id], VALUE="Horizontal")
                file.write(info + '\n')
                file.write("![ped](./Leakage_Current/pulse_LC_SE_200mVBL_14_0mVfC_2_0us_0x20_100pA.png)" + "\n")

                file.write("------\n")
                file.write('### 03_03 {} pulse'.format(log.check_log03_03[femb_id]['Label']) + '\n')
                info = dict_to_markdown_table(log.report_log03_03[femb_id], VALUE="Horizontal")
                file.write(info + '\n')
                file.write("![ped](./Leakage_Current/pulse_LC_SE_200mVBL_14_0mVfC_2_0us_0x20_5nA.png)" + "\n")

                file.write("------\n")
                file.write('### 03_04 {} pulse'.format(log.check_log03_04[femb_id]['Label']) + '\n')
                info = dict_to_markdown_table(log.report_log03_04[femb_id], VALUE="Horizontal")
                file.write(info + '\n')
                file.write("![ped](./Leakage_Current/pulse_LC_SE_200mVBL_14_0mVfC_2_0us_0x20_1nA.png)" + "\n")
                file.write('</details >' + '\n')
# 04        print <Check Pulse>
            if 4 in log.test_label:
                if check_status04:
                    Head04 = '### ' + '<span style="color: green;">' + 'ITEM 04 Whole Pulse Response' + '    < Pass >' + '</span>'  + '\n'
                else:
                    Head04 = '### ' + '<span style="color: red;">' + 'ITEM 04 Whole Pulse Response' + '    < Fail >' + '</span>'  + '\n'
                file.write(Head04 + '\n')
                file.write("------\n")

                file.write("![ped](./CHK/SE_200_Gain_Pulse_ErrorBar.png)" + "\n")
                file.write("![ped](./CHK/SE_900_Gain_Pulse_ErrorBar.png)" + "\n")
                file.write("![ped](./CHK/SGP1_200_fC_Pulse.png)" + "\n")

                file.write('### SE OFF    Baseline 200 mV' + '\n')
                log.check_log04_table_01[femb_id]['title'] = " | Gain | PeakTime | PPK Mean | PPK Error | NPK Mean | NPK Error |\n"
                log.check_log04_table_01[femb_id]['table line'] = " | --- | --- | --- | --- | --- | --- | \n"

                log.check_log04_table_01[femb_id]['line1'] = " | 4.7 mV/fC | 0.5 us | {} | {} | {} | {} | \n".format(log.report_log04_01[femb_id]["CHK_SE_200mVBL_4_7mVfC_0_5us_0x10_ppk_mean"], log.report_log04_01[femb_id]["CHK_SE_200mVBL_4_7mVfC_0_5us_0x10_ppk_err"], log.report_log04_01[femb_id]["CHK_SE_200mVBL_4_7mVfC_0_5us_0x10_npk_mean"], log.report_log04_01[femb_id]["CHK_SE_200mVBL_4_7mVfC_0_5us_0x10_npk_err"])
                log.check_log04_table_01[femb_id]['line2'] = " | 4.7 mV/fC | 1 us | {} | {} | {} | {} | \n".format(log.report_log04_01[femb_id]["CHK_SE_200mVBL_4_7mVfC_1_0us_0x10_ppk_mean"], log.report_log04_01[femb_id]["CHK_SE_200mVBL_4_7mVfC_1_0us_0x10_ppk_err"], log.report_log04_01[femb_id]["CHK_SE_200mVBL_4_7mVfC_1_0us_0x10_npk_mean"], log.report_log04_01[femb_id]["CHK_SE_200mVBL_4_7mVfC_1_0us_0x10_npk_err"])
                log.check_log04_table_01[femb_id]['line3'] = " | 4.7 mV/fC | 2 us | {} | {} | {} | {} | \n".format(log.report_log04_01[femb_id]["CHK_SE_200mVBL_4_7mVfC_2_0us_0x10_ppk_mean"], log.report_log04_01[femb_id]["CHK_SE_200mVBL_4_7mVfC_2_0us_0x10_ppk_err"], log.report_log04_01[femb_id]["CHK_SE_200mVBL_4_7mVfC_2_0us_0x10_npk_mean"], log.report_log04_01[femb_id]["CHK_SE_200mVBL_4_7mVfC_2_0us_0x10_npk_err"])
                log.check_log04_table_01[femb_id]['line4'] = " | 4.7 mV/fC | 3 us | {} | {} | {} | {} | \n".format(log.report_log04_01[femb_id]["CHK_SE_200mVBL_4_7mVfC_3_0us_0x10_ppk_mean"], log.report_log04_01[femb_id]["CHK_SE_200mVBL_4_7mVfC_3_0us_0x10_ppk_err"], log.report_log04_01[femb_id]["CHK_SE_200mVBL_4_7mVfC_3_0us_0x10_npk_mean"], log.report_log04_01[femb_id]["CHK_SE_200mVBL_4_7mVfC_3_0us_0x10_npk_err"])

                log.check_log04_table_01[femb_id]['line5'] = " 7.8 mV/fC | 0.5 us | {} | {} | {} | {} |\n".format(log.report_log04_01[femb_id]['CHK_SE_200mVBL_7_8mVfC_0_5us_0x10_ppk_mean'], log.report_log04_01[femb_id]["CHK_SE_200mVBL_7_8mVfC_0_5us_0x10_ppk_err"], log.report_log04_01[femb_id]['CHK_SE_200mVBL_7_8mVfC_0_5us_0x10_npk_mean'], log.report_log04_01[femb_id]["CHK_SE_200mVBL_7_8mVfC_0_5us_0x10_npk_err"])
                log.check_log04_table_01[femb_id]['line6'] = " 7.8 mV/fC | 1 us | {} | {} | {} | {} | \n".format(log.report_log04_01[femb_id]['CHK_SE_200mVBL_7_8mVfC_1_0us_0x10_ppk_mean'], log.report_log04_01[femb_id]["CHK_SE_200mVBL_7_8mVfC_1_0us_0x10_ppk_err"],  log.report_log04_01[femb_id]['CHK_SE_200mVBL_7_8mVfC_1_0us_0x10_npk_mean'], log.report_log04_01[femb_id]["CHK_SE_200mVBL_7_8mVfC_1_0us_0x10_npk_err"])
                log.check_log04_table_01[femb_id]['line7'] = " 7.8 mV/fC | 2 us | {} | {} | {} | {} | \n".format(log.report_log04_01[femb_id]['CHK_SE_200mVBL_7_8mVfC_2_0us_0x10_ppk_mean'], log.report_log04_01[femb_id]["CHK_SE_200mVBL_7_8mVfC_2_0us_0x10_ppk_err"], log.report_log04_01[femb_id]['CHK_SE_200mVBL_7_8mVfC_2_0us_0x10_npk_mean'], log.report_log04_01[femb_id]["CHK_SE_200mVBL_7_8mVfC_2_0us_0x10_npk_err"])
                log.check_log04_table_01[femb_id]['line8'] = " 7.8 mV/fC | 3 us | {} | {} | {} | {} | \n".format(log.report_log04_01[femb_id]['CHK_SE_200mVBL_7_8mVfC_3_0us_0x10_ppk_mean'], log.report_log04_01[femb_id]["CHK_SE_200mVBL_7_8mVfC_3_0us_0x10_ppk_err"], log.report_log04_01[femb_id]['CHK_SE_200mVBL_7_8mVfC_3_0us_0x10_npk_mean'], log.report_log04_01[femb_id]["CHK_SE_200mVBL_7_8mVfC_3_0us_0x10_npk_err"])

                log.check_log04_table_01[femb_id]['line9'] = " 14 mV/fC | 0.5 us | {} | {} | {} | {} | \n".format(log.report_log04_01[femb_id]['CHK_SE_200mVBL_14_0mVfC_0_5us_0x10_ppk_mean'], log.report_log04_01[femb_id]["CHK_SE_200mVBL_14_0mVfC_0_5us_0x10_ppk_err"], log.report_log04_01[femb_id]['CHK_SE_200mVBL_14_0mVfC_0_5us_0x10_npk_mean'], log.report_log04_01[femb_id]["CHK_SE_200mVBL_7_8mVfC_0_5us_0x10_npk_err"])
                log.check_log04_table_01[femb_id]['line10'] = " 14 mV/fC | 1 us | {} | {} | {} | {} | \n".format(log.report_log04_01[femb_id]['CHK_SE_200mVBL_14_0mVfC_1_0us_0x10_ppk_mean'], log.report_log04_01[femb_id]["CHK_SE_200mVBL_14_0mVfC_1_0us_0x10_ppk_err"],  log.report_log04_01[femb_id]['CHK_SE_200mVBL_14_0mVfC_1_0us_0x10_npk_mean'], log.report_log04_01[femb_id]["CHK_SE_200mVBL_7_8mVfC_1_0us_0x10_npk_err"])
                log.check_log04_table_01[femb_id]['line11'] = " 14 mV/fC | 2 us | {} | {} | {} | {} | \n".format(log.report_log04_01[femb_id]['CHK_SE_200mVBL_14_0mVfC_2_0us_0x10_ppk_mean'], log.report_log04_01[femb_id]["CHK_SE_200mVBL_14_0mVfC_2_0us_0x10_ppk_err"],  log.report_log04_01[femb_id]['CHK_SE_200mVBL_14_0mVfC_2_0us_0x10_npk_mean'], log.report_log04_01[femb_id]["CHK_SE_200mVBL_7_8mVfC_2_0us_0x10_npk_err"])
                log.check_log04_table_01[femb_id]['line12'] = " 14 mV/fC | 3 us | {} | {} | {} | {} | \n".format(log.report_log04_01[femb_id]['CHK_SE_200mVBL_14_0mVfC_3_0us_0x10_ppk_mean'], log.report_log04_01[femb_id]["CHK_SE_200mVBL_14_0mVfC_3_0us_0x10_ppk_err"],  log.report_log04_01[femb_id]['CHK_SE_200mVBL_14_0mVfC_3_0us_0x10_npk_mean'], log.report_log04_01[femb_id]["CHK_SE_200mVBL_7_8mVfC_3_0us_0x10_npk_err"])

                log.check_log04_table_01[femb_id]['line13'] = " 25 mV/fC | 0.5 us | {} | {} | {} | {} | \n".format(log.report_log04_01[femb_id]['CHK_SE_200mVBL_25_0mVfC_0_5us_0x10_ppk_mean'], log.report_log04_01[femb_id]["CHK_SE_200mVBL_25_0mVfC_0_5us_0x10_ppk_err"], log.report_log04_01[femb_id]['CHK_SE_200mVBL_25_0mVfC_0_5us_0x10_npk_mean'], log.report_log04_01[femb_id]["CHK_SE_200mVBL_25_0mVfC_0_5us_0x10_npk_err"])
                log.check_log04_table_01[femb_id]['line14'] = " 25 mV/fC | 1 us | {} | {} | {} | {} | \n".format(log.report_log04_01[femb_id]['CHK_SE_200mVBL_25_0mVfC_1_0us_0x10_ppk_mean'], log.report_log04_01[femb_id]["CHK_SE_200mVBL_25_0mVfC_1_0us_0x10_ppk_err"], log.report_log04_01[femb_id]['CHK_SE_200mVBL_25_0mVfC_1_0us_0x10_npk_mean'], log.report_log04_01[femb_id]["CHK_SE_200mVBL_25_0mVfC_1_0us_0x10_npk_err"])
                log.check_log04_table_01[femb_id]['line15'] = " 25 mV/fC | 2 us | {} | {} | {} | {} | \n".format(log.report_log04_01[femb_id]['CHK_SE_200mVBL_25_0mVfC_2_0us_0x10_ppk_mean'], log.report_log04_01[femb_id]["CHK_SE_200mVBL_25_0mVfC_2_0us_0x10_ppk_err"], log.report_log04_01[femb_id]['CHK_SE_200mVBL_25_0mVfC_2_0us_0x10_npk_mean'], log.report_log04_01[femb_id]["CHK_SE_200mVBL_25_0mVfC_2_0us_0x10_npk_err"])
                log.check_log04_table_01[femb_id]['line16'] = " 25 mV/fC | 3 us | {} | {} | {} | {} | \n".format(log.report_log04_01[femb_id]['CHK_SE_200mVBL_25_0mVfC_3_0us_0x10_ppk_mean'], log.report_log04_01[femb_id]["CHK_SE_200mVBL_25_0mVfC_3_0us_0x10_ppk_err"], log.report_log04_01[femb_id]['CHK_SE_200mVBL_25_0mVfC_3_0us_0x10_npk_mean'], log.report_log04_01[femb_id]["CHK_SE_200mVBL_25_0mVfC_3_0us_0x10_npk_err"])

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


#   SE 900 mV
                file.write('### SE OFF    Baseline 900 mV' + '\n')
                log.check_log04_table_02[femb_id]['title'] = " | Gain | PeakTime | PPK Mean | PPK Error | NPK Mean | NPK Error |\n"
                log.check_log04_table_02[femb_id]['table line'] = " | --- | --- | --- | --- | --- | --- | \n"

                log.check_log04_table_02[femb_id]['line1'] = " | 4.7 mV/fC | 0.5 us | {} | {} | {} | {} | \n".format(log.report_log04_02[femb_id]["CHK_SE_900mVBL_4_7mVfC_0_5us_0x10_ppk_mean"], log.report_log04_02[femb_id]["CHK_SE_900mVBL_4_7mVfC_0_5us_0x10_ppk_err"], log.report_log04_02[femb_id]["CHK_SE_900mVBL_4_7mVfC_0_5us_0x10_npk_mean"], log.report_log04_02[femb_id]["CHK_SE_900mVBL_4_7mVfC_0_5us_0x10_ppk_err"])
                log.check_log04_table_02[femb_id]['line2'] = " | 4.7 mV/fC | 1 us | {} | {} | {} | {} | \n".format(log.report_log04_02[femb_id]['CHK_SE_900mVBL_4_7mVfC_1_0us_0x10_ppk_mean'], log.report_log04_02[femb_id]["CHK_SE_900mVBL_4_7mVfC_1_0us_0x10_npk_err"], log.report_log04_02[femb_id]['CHK_SE_900mVBL_4_7mVfC_1_0us_0x10_npk_mean'], log.report_log04_02[femb_id]["CHK_SE_900mVBL_4_7mVfC_1_0us_0x10_npk_err"])
                log.check_log04_table_02[femb_id]['line3'] = " | 4.7 mV/fC | 2 us | {} | {} | {} | {} | \n".format(log.report_log04_02[femb_id]['CHK_SE_900mVBL_4_7mVfC_2_0us_0x10_ppk_mean'], log.report_log04_02[femb_id]["CHK_SE_900mVBL_4_7mVfC_2_0us_0x10_npk_err"], log.report_log04_02[femb_id]['CHK_SE_900mVBL_4_7mVfC_2_0us_0x10_npk_mean'], log.report_log04_02[femb_id]["CHK_SE_900mVBL_4_7mVfC_2_0us_0x10_npk_err"])
                log.check_log04_table_02[femb_id]['line4'] = " | 4.7 mV/fC | 3 us | {} | {} | {} | {} | \n".format(log.report_log04_02[femb_id]['CHK_SE_900mVBL_4_7mVfC_3_0us_0x10_ppk_mean'], log.report_log04_02[femb_id]["CHK_SE_900mVBL_4_7mVfC_3_0us_0x10_npk_err"], log.report_log04_02[femb_id]['CHK_SE_900mVBL_4_7mVfC_3_0us_0x10_npk_mean'], log.report_log04_02[femb_id]["CHK_SE_900mVBL_4_7mVfC_3_0us_0x10_npk_err"])

                log.check_log04_table_02[femb_id]['line5'] = " | 7.8 mV/fC | 0.5 us | {} | {} | {} | {} | \n".format(log.report_log04_02[femb_id]['CHK_SE_900mVBL_7_8mVfC_0_5us_0x10_ppk_mean'], log.report_log04_02[femb_id]["CHK_SE_900mVBL_7_8mVfC_0_5us_0x10_ppk_err"], log.report_log04_02[femb_id]['CHK_SE_900mVBL_7_8mVfC_0_5us_0x10_npk_mean'], log.report_log04_02[femb_id]["CHK_SE_900mVBL_7_8mVfC_0_5us_0x10_npk_err"])
                log.check_log04_table_02[femb_id]['line6'] = " | 14 mV/fC | 1 us | {} | {} | {} | {} | \n".format(log.report_log04_02[femb_id]['CHK_SE_900mVBL_7_8mVfC_1_0us_0x10_ppk_mean'], log.report_log04_02[femb_id]["CHK_SE_900mVBL_7_8mVfC_1_0us_0x10_ppk_err"], log.report_log04_02[femb_id]['CHK_SE_900mVBL_7_8mVfC_1_0us_0x10_npk_mean'], log.report_log04_02[femb_id]["CHK_SE_900mVBL_7_8mVfC_1_0us_0x10_npk_err"])
                log.check_log04_table_02[femb_id]['line7'] = " | 14 mV/fC | 2 us | {} | {} | {} | {} | \n".format(log.report_log04_02[femb_id]['CHK_SE_900mVBL_7_8mVfC_2_0us_0x10_ppk_mean'], log.report_log04_02[femb_id]["CHK_SE_900mVBL_7_8mVfC_2_0us_0x10_ppk_err"], log.report_log04_02[femb_id]['CHK_SE_900mVBL_7_8mVfC_2_0us_0x10_npk_mean'], log.report_log04_02[femb_id]["CHK_SE_900mVBL_7_8mVfC_2_0us_0x10_npk_err"])
                log.check_log04_table_02[femb_id]['line8'] = " | 14 mV/fC | 3 us | {} | {} | {} | {} | \n".format(log.report_log04_02[femb_id]['CHK_SE_900mVBL_7_8mVfC_3_0us_0x10_ppk_mean'], log.report_log04_02[femb_id]["CHK_SE_900mVBL_7_8mVfC_3_0us_0x10_ppk_err"], log.report_log04_02[femb_id]['CHK_SE_900mVBL_7_8mVfC_3_0us_0x10_npk_mean'], log.report_log04_02[femb_id]["CHK_SE_900mVBL_7_8mVfC_3_0us_0x10_npk_err"])

                log.check_log04_table_02[femb_id]['line9'] = " | 14 mV/fC | 0.5 us | {} | {} | {} | {} | \n".format(log.report_log04_02[femb_id]['CHK_SE_900mVBL_14_0mVfC_0_5us_0x10_ppk_mean'], log.report_log04_02[femb_id]["CHK_SE_900mVBL_14_0mVfC_0_5us_0x10_ppk_err"], log.report_log04_02[femb_id]['CHK_SE_900mVBL_14_0mVfC_0_5us_0x10_npk_mean'], log.report_log04_02[femb_id]["CHK_SE_900mVBL_14_0mVfC_0_5us_0x10_npk_err"])
                log.check_log04_table_02[femb_id]['line10'] = " | 14 mV/fC | 1 us | {} | {} | {} | {} | \n".format(log.report_log04_02[femb_id]['CHK_SE_900mVBL_14_0mVfC_1_0us_0x10_ppk_mean'], log.report_log04_02[femb_id]["CHK_SE_900mVBL_14_0mVfC_1_0us_0x10_ppk_err"],  log.report_log04_02[femb_id]['CHK_SE_900mVBL_14_0mVfC_1_0us_0x10_npk_mean'], log.report_log04_02[femb_id]["CHK_SE_900mVBL_14_0mVfC_1_0us_0x10_npk_err"])
                log.check_log04_table_02[femb_id]['line11'] = " | 14 mV/fC | 2 us | {} | {} | {} | {} | \n".format(log.report_log04_02[femb_id]['CHK_SE_900mVBL_14_0mVfC_2_0us_0x10_ppk_mean'], log.report_log04_02[femb_id]["CHK_SE_900mVBL_14_0mVfC_2_0us_0x10_ppk_err"],  log.report_log04_02[femb_id]['CHK_SE_900mVBL_14_0mVfC_2_0us_0x10_npk_mean'], log.report_log04_02[femb_id]["CHK_SE_900mVBL_14_0mVfC_2_0us_0x10_npk_err"])
                log.check_log04_table_02[femb_id]['line12'] = " | 14 mV/fC | 3 us | {} | {} | {} | {} | \n".format(log.report_log04_02[femb_id]['CHK_SE_900mVBL_14_0mVfC_3_0us_0x10_ppk_mean'], log.report_log04_02[femb_id]["CHK_SE_900mVBL_14_0mVfC_3_0us_0x10_ppk_err"],  log.report_log04_02[femb_id]['CHK_SE_900mVBL_14_0mVfC_3_0us_0x10_npk_mean'], log.report_log04_02[femb_id]["CHK_SE_900mVBL_14_0mVfC_3_0us_0x10_npk_err"])

                log.check_log04_table_02[femb_id]['line13'] = " | 25 mV/fC | 0.5 us | {} | {} | {} | {} | \n".format(log.report_log04_02[femb_id]['CHK_SE_900mVBL_25_0mVfC_0_5us_0x10_ppk_mean'], log.report_log04_02[femb_id]["CHK_SE_900mVBL_25_0mVfC_0_5us_0x10_ppk_err"], log.report_log04_02[femb_id]['CHK_SE_900mVBL_25_0mVfC_0_5us_0x10_npk_mean'], log.report_log04_02[femb_id]["CHK_SE_900mVBL_25_0mVfC_0_5us_0x10_npk_err"])
                log.check_log04_table_02[femb_id]['line14'] = " | 25 mV/fC | 1 us | {} | {} | {} | {} | \n".format(log.report_log04_02[femb_id]['CHK_SE_900mVBL_25_0mVfC_1_0us_0x10_ppk_mean'], log.report_log04_02[femb_id]["CHK_SE_900mVBL_25_0mVfC_1_0us_0x10_ppk_err"], log.report_log04_02[femb_id]['CHK_SE_900mVBL_25_0mVfC_1_0us_0x10_npk_mean'], log.report_log04_02[femb_id]["CHK_SE_900mVBL_25_0mVfC_1_0us_0x10_npk_err"])
                log.check_log04_table_02[femb_id]['line15'] = " | 25 mV/fC | 2 us | {} | {} | {} | {} | \n".format(log.report_log04_02[femb_id]['CHK_SE_900mVBL_25_0mVfC_2_0us_0x10_ppk_mean'], log.report_log04_02[femb_id]["CHK_SE_900mVBL_25_0mVfC_2_0us_0x10_ppk_err"], log.report_log04_02[femb_id]['CHK_SE_900mVBL_25_0mVfC_2_0us_0x10_npk_mean'], log.report_log04_02[femb_id]["CHK_SE_900mVBL_25_0mVfC_2_0us_0x10_npk_err"])
                log.check_log04_table_02[femb_id]['line16'] = " | 25 mV/fC | 3 us | {} | {} | {} | {} | \n".format(log.report_log04_02[femb_id]['CHK_SE_900mVBL_25_0mVfC_3_0us_0x10_ppk_mean'], log.report_log04_02[femb_id]["CHK_SE_900mVBL_25_0mVfC_3_0us_0x10_ppk_err"], log.report_log04_02[femb_id]['CHK_SE_900mVBL_25_0mVfC_3_0us_0x10_npk_mean'], log.report_log04_02[femb_id]["CHK_SE_900mVBL_25_0mVfC_3_0us_0x10_npk_err"])
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



#   SE ON 200 & 900 mV
                file.write('### SE ON    Baseline 200 mV & 900 mV' + '\n')
                file.write('\n')
                log.check_log04_table_03[femb_id][
                    'title'] = " | Baseline | Gain | PeakTime | PPK Mean | PPK Error | NPK Mean | NPK Error |\n"
                log.check_log04_table_03[femb_id]['table line'] = " | --- | --- | --- | --- | --- | --- | --- |\n"

                log.check_log04_table_03[femb_id]['line1'] = " | 200 mV | 14 mV/fC | 2 us | {} | {} | {} | {} | \n".format(
                    log.report_log04_03[femb_id]["CHK_SEON_200mVBL_14_0mVfC_2_0us_0x10_ppk_mean"],
                    log.report_log04_03[femb_id]["CHK_SEON_200mVBL_14_0mVfC_2_0us_0x10_ppk_err"],
                    log.report_log04_03[femb_id]["CHK_SEON_200mVBL_14_0mVfC_2_0us_0x10_npk_mean"],
                    log.report_log04_03[femb_id]["CHK_SEON_200mVBL_14_0mVfC_2_0us_0x10_npk_err"])
                log.check_log04_table_03[femb_id]['line2'] = " | 900 mV | 14 mV/fC | 2 us | {} | {} | {} | {} | \n".format(
                    log.report_log04_03[femb_id]['CHK_SEON_900mVBL_14_0mVfC_2_0us_0x10_ppk_mean'],
                    log.report_log04_03[femb_id]["CHK_SEON_900mVBL_14_0mVfC_2_0us_0x10_ppk_err"],
                    log.report_log04_03[femb_id]['CHK_SEON_900mVBL_14_0mVfC_2_0us_0x10_npk_mean'],
                    log.report_log04_03[femb_id]["CHK_SEON_900mVBL_14_0mVfC_2_0us_0x10_npk_err"])
                file.write('\n')
                file.write(log.check_log04_table_03[femb_id]['title'])
                file.write(log.check_log04_table_03[femb_id]['table line'])
                file.write(log.check_log04_table_03[femb_id]['line1'])
                file.write(log.check_log04_table_03[femb_id]['line2'])

#   DIFF 200 & 900 mV
                file.write('### DIFF    Baseline 200 mV & 900 mV' + '\n')
                file.write('\n')
                log.check_log04_table_04[femb_id][
                    'title'] = " | Baseline | Gain | PeakTime | PPK Mean | PPK Error | NPK Mean | NPK Error |\n"
                log.check_log04_table_04[femb_id]['table line'] = " | --- | --- | --- | --- | --- | --- | --- |\n"

                log.check_log04_table_04[femb_id]['line1'] = " | 200 mV | 14 mV/fC | 2 us | {} | {} | {} | {} | \n".format(
                    log.report_log04_04[femb_id]["CHK_DIFF_200mVBL_14_0mVfC_2_0us_0x10_ppk_mean"],
                    log.report_log04_04[femb_id]["CHK_DIFF_200mVBL_14_0mVfC_2_0us_0x10_ppk_err"],
                    log.report_log04_04[femb_id]["CHK_DIFF_200mVBL_14_0mVfC_2_0us_0x10_npk_mean"],
                    log.report_log04_04[femb_id]["CHK_DIFF_200mVBL_14_0mVfC_2_0us_0x10_npk_err"])
                log.check_log04_table_04[femb_id]['line2'] = " | 900 mV | 14 mV/fC | 2 us | {} | {} | {} | {} | \n".format(
                    log.report_log04_04[femb_id]['CHK_DIFF_900mVBL_14_0mVfC_2_0us_0x10_ppk_mean'],
                    log.report_log04_04[femb_id]["CHK_DIFF_900mVBL_14_0mVfC_2_0us_0x10_ppk_err"],
                    log.report_log04_04[femb_id]['CHK_DIFF_900mVBL_14_0mVfC_2_0us_0x10_npk_mean'],
                    log.report_log04_04[femb_id]["CHK_DIFF_900mVBL_14_0mVfC_2_0us_0x10_npk_err"])
                file.write('\n')
                file.write(log.check_log04_table_04[femb_id]['title'])
                file.write(log.check_log04_table_04[femb_id]['table line'])
                file.write(log.check_log04_table_04[femb_id]['line1'])
                file.write(log.check_log04_table_04[femb_id]['line2'])

#   SGP1 200 mV
                file.write('### SGP1    Baseline 200 mV ' + '\n')
                file.write('\n')
                log.check_log04_table_06[femb_id][
                    'title'] = " | Gain | PeakTime | PPK Mean | PPK Error | NPK Mean | NPK Error |\n"
                log.check_log04_table_06[femb_id]['table line'] = " | --- | --- | --- | --- | --- | --- |\n"

                log.check_log04_table_06[femb_id]['line1'] = " | 4_7 mV/fC | 2 us | {} | {} | {} | {} | \n".format(
                    log.report_log04_06[femb_id]["CHK_SGP_200mVBL_4_7mVfC_2_0us_0x10_ppk_mean"],
                    log.report_log04_06[femb_id]["CHK_SGP_200mVBL_4_7mVfC_2_0us_0x10_ppk_err"],
                    log.report_log04_06[femb_id]["CHK_SGP_200mVBL_4_7mVfC_2_0us_0x10_npk_mean"],
                    log.report_log04_06[femb_id]["CHK_SGP_200mVBL_4_7mVfC_2_0us_0x10_npk_err"])
                log.check_log04_table_06[femb_id]['line2'] = " | 7_8 mV/fC | 2 us | {} | {} | {} | {} | \n".format(
                    log.report_log04_06[femb_id]["CHK_SGP_200mVBL_7_8mVfC_2_0us_0x10_ppk_mean"],
                    log.report_log04_06[femb_id]["CHK_SGP_200mVBL_7_8mVfC_2_0us_0x10_ppk_err"],
                    log.report_log04_06[femb_id]["CHK_SGP_200mVBL_7_8mVfC_2_0us_0x10_npk_mean"],
                    log.report_log04_06[femb_id]["CHK_SGP_200mVBL_7_8mVfC_2_0us_0x10_npk_err"])
                log.check_log04_table_06[femb_id]['line3'] = " | 14 mV/fC | 2 us | {} | {} | {} | {} | \n".format(
                    log.report_log04_06[femb_id]["CHK_SGP_200mVBL_4_7mVfC_2_0us_0x10_ppk_mean"],
                    log.report_log04_06[femb_id]["CHK_SGP_200mVBL_14_0mVfC_2_0us_0x10_ppk_err"],
                    log.report_log04_06[femb_id]["CHK_SGP_200mVBL_14_0mVfC_2_0us_0x10_npk_mean"],
                    log.report_log04_06[femb_id]["CHK_SGP_200mVBL_14_0mVfC_2_0us_0x10_npk_err"])
                log.check_log04_table_06[femb_id]['line4'] = " | 25 mV/fC | 2 us | {} | {} | {} | {} | \n".format(
                    log.report_log04_06[femb_id]["CHK_SGP_200mVBL_25_0mVfC_2_0us_0x10_ppk_mean"],
                    log.report_log04_06[femb_id]["CHK_SGP_200mVBL_25_0mVfC_2_0us_0x10_ppk_err"],
                    log.report_log04_06[femb_id]["CHK_SGP_200mVBL_25_0mVfC_2_0us_0x10_npk_mean"],
                    log.report_log04_06[femb_id]["CHK_SGP_200mVBL_25_0mVfC_2_0us_0x10_npk_err"])

                file.write('\n')
                file.write(log.check_log04_table_06[femb_id]['title'])
                file.write(log.check_log04_table_06[femb_id]['table line'])
                file.write(log.check_log04_table_06[femb_id]['line1'])
                file.write(log.check_log04_table_06[femb_id]['line2'])
                file.write(log.check_log04_table_06[femb_id]['line3'])
                file.write(log.check_log04_table_06[femb_id]['line4'])
                # file.write(log.check_log04_table_06[femb_id]['line2'])
                file.write("[PDF](./{}/report.pdf)".format(log.item04) + "\n")







# 05        RMS configuration
            if 5 in log.test_label:
                if check_status05 == True:
                    file.write('### <span style = "color : green;"> "Item 05 RMS configuration SE/SEON/SELC/DIFF 200/900 mV 4_7/7_8/14/25 mV/fC 0.5/1/2/3 us" </span>' + '\n')
                else:
                    file.write('### <span style = "color : red;"> "Item 05 RMS configuration SE/SEON/SELC/DIFF 200/900 mV 4_7/7_8/14/25 mV/fC 0.5/1/2/3 us" </span>' + '\n')
                file.write("![ped](./{}/SE_200_900_mV_RMS_ErrorBar.png)".format(log.item05) + "\n")
                file.write("![ped](./{}/SEON_DIFF_200_900_mV_RMS_ErrorBar.png)".format(log.item05) + "\n")
                file.write("![ped](./{}/SELC_200_2us_ErrorBar.png)".format(log.item05) + "\n")
                file.write('#### All_200mVBL_Configuration' + '\n')
                info = dict_to_markdown_table(log.report_log05_table[femb_id], VALUE="RMS")
                file.write(info + '\n')
                info = dict_to_markdown_table(log.report_log05_table2[femb_id], VALUE="RMS")
                file.write(info + '\n')
                file.write("![ped](./{}/200mV_All_Configuration.png)".format(log.item05) + "\n")
                file.write('#### All_900mVBL_Configuration' + '\n')
                file.write("![ped](./{}/900mV_All_Configuration.png)".format(log.item05) + "\n")
                file.write('#### RMS whole Report' + '\n')
                file.write("[PDF](./{}/report.pdf)".format(log.item05) + "\n")

# 06        Calibration 01:
            # SE    200 mVBL    4_7 mVfC    2 us
            # SE    200 mVBL    7_8 mVfC    2 us
            # SE    200 mVBL    14 mVfC     2 us
            # SE    200 mVBL    25 mVfC     2 us
            # DIFF  200 mVBL    14 mVfC     2 us
            if 6 in log.test_label:
                if check_status06 == True:
                    file.write(
                        '### <span style = "color : green;"> "Item 06 Cali_1 configuration SE 4.7 7.8 14 25 mVfC DIFF 14 mVfC" </span>' + '\n')
                else:
                    file.write(
                        '### <span style = "color : red;"> "Item 06 Cali_1 configuration SE 4.7 7.8 14 25 mVfC DIFF 14 mVfC" </span>' + '\n')

                file.write("![ped](./{}/Cali1.png)".format(log.item062) + "\n\n")

                file.write('### 6_1 Calibration SE 200 mVBL    4_7 mVfC    2 us' + '\n')
                file.write("![ped](./{}/enc_200mVBL_4_7mVfC_2_0us.png)".format(log.item061) + "![ped](./{}/Line_range_200mVBL_4_7mVfC_2_0us.png)".format(log.item061) + "\n")
                file.write("![ped](./{}/gain_200mVBL_4_7mVfC_2_0us.png)".format(log.item061) + "\n")
                file.write("![ped](./{}/ped_200mVBL_4_7mVfC_2_0us.png)".format(log.item061) + "\n")

                file.write('### 6_2 Calibration SE 200 mVBL    7_8 mVfC    2 us' + '\n')
                file.write("![ped](./{}/enc_200mVBL_7_8mVfC_2_0us.png)".format(log.item061) + "![ped](./{}/Line_range_200mVBL_7_8mVfC_2_0us.png)".format(log.item061) + "\n")
                file.write("![ped](./{}/gain_200mVBL_7_8mVfC_2_0us.png)".format(log.item061) + "\n")
                file.write("![ped](./{}/ped_200mVBL_7_8mVfC_2_0us.png)".format(log.item061) + "\n")

                file.write('### 6_3 Calibration SE 200 mVBL    14_0 mVfC    2 us' + '\n')
                file.write("![ped](./{}/enc_200mVBL_14_0mVfC_2_0us.png)".format(log.item061) + "![ped](./{}/Line_range_200mVBL_14_0mVfC_2_0us.png)".format(log.item061) + "\n")
                file.write("![ped](./{}/gain_200mVBL_14_0mVfC_2_0us.png)".format(log.item061) + "\n")
                file.write("![ped](./{}/ped_200mVBL_14_0mVfC_2_0us.png)".format(log.item061) + "\n")

                file.write('### 6_4 Calibration SE 200 mVBL    25_0 mVfC    2 us' + '\n')
                file.write("![ped](./{}/enc_200mVBL_25_0mVfC_2_0us.png)".format(log.item061) + "![ped](./{}/Line_range_200mVBL_25_0mVfC_2_0us.png)".format(log.item061) + "\n")
                file.write("![ped](./{}/gain_200mVBL_25_0mVfC_2_0us.png)".format(log.item061) + "\n")
                file.write("![ped](./{}/ped_200mVBL_25_0mVfC_2_0us.png)".format(log.item061) + "\n")

                file.write('### 6_5 Calibration DIFF 200 mVBL    14_0 mVfC    2 us' + '\n')
                file.write("![ped](./{}/enc_200mVBL_14_0mVfC_2_0us.png)".format(log.item062) + "![ped](./{}/Line_range_200mVBL_14_0mVfC_2_0us.png)".format(log.item062) + "\n")
                file.write("![ped](./{}/gain_200mVBL_14_0mVfC_2_0us.png)".format(log.item062) + "\n")
                file.write("![ped](./{}/ped_200mVBL_14_0mVfC_2_0us.png)".format(log.item062) + "\n")

#   07      Calibration 02:
            if 7 in log.test_label:
                if check_status07 == True:
                    file.write(
                        '### <span style = "color : green;"> "Item_07 Cali_2 configuration SE & DIFF 14 mVfC" </span>' + '\n')
                else:
                    file.write(
                        '### <span style = "color : red;"> "Item_07 Cali_2 configuration SE & DIFF 14 mVfC" </span>' + '\n')

                file.write("![ped](./{}/Cali2.png)".format(log.item072) + "\n\n")

                # SE    900 mVBL    14_0 mVfC       2 us
                file.write('### Calibration 021 SE 900 mVBL    14_0 mVfC    2 us' + '\n')
                file.write("![ped](./{}/enc_900mVBL_14_0mVfC_2_0us.png)".format(log.item071) + "![ped](./{}/Line_range_900mVBL_14_0mVfC_2_0us.png)".format(log.item071) + "\n")
                file.write("![ped](./{}/gain_900mVBL_14_0mVfC_2_0us.png)".format(log.item071) + "\n")
                file.write("![ped](./{}/ped_900mVBL_14_0mVfC_2_0us.png)".format(log.item071) + "\n")
                #DIFF  900 mVBL    14 mVfC     2 us
                file.write('### Calibration 022 DIFF 900 mVBL    14_0 mVfC    2 us' + '\n')
                file.write("![ped](./{}/enc_900mVBL_14_0mVfC_2_0us.png)".format(log.item072) + "![ped](./{}/Line_range_900mVBL_14_0mVfC_2_0us.png)".format(log.item072) + "\n")
                file.write("![ped](./{}/gain_900mVBL_14_0mVfC_2_0us.png)".format(log.item072) + "\n")
                file.write("![ped](./{}/ped_900mVBL_14_0mVfC_2_0us.png)".format(log.item072) + "\n")

#   08      Calibration 03:
            if 8 in log.test_label:
                if check_status08 == True:
                    file.write(
                        '### <span style = "color : green;"> "Item_08 Cali_3 configuration SG1 SE & DIFF 14 mVfC" </span>' + '\n')
                else:
                    file.write(
                        '### <span style = "color : red;"> "Item_08 Cali_3 configuration SG1 SE & DIFF 14 mVfC" </span>' + '\n')
            # SE    900 mVBL    14_0 mVfC       2 us
                file.write('### Calibration 03 SE SGP1 200 mVBL    14_0 mVfC    2 us' + '\n')
                file.write("![ped](./{}/enc_200mVBL_14_0mVfC_2_0us_sgp1.png)".format(log.item081) + "![ped](./{}/Line_range_200mVBL_14_0mVfC_2_0us_sgp1.png)".format(log.item081) + "\n")
                file.write("![ped](./{}/gain_200mVBL_14_0mVfC_2_0us_sgp1.png)".format(log.item081) + "\n")
                file.write("![ped](./{}/ped_200mVBL_14_0mVfC_2_0us_sgp1.png)".format(log.item081) + "\n")
            # # DIFF  900 mVBL    14 mVfC     2 us
            # file.write('### Calibration 022 DIFF 900 mVBL    14_0 mVfC    2 us' + '\n')
            # file.write("![ped](./{}/enc_900mVBL_14_0mVfC_2_0us.png)".format(log.item072) + "![ped](./{}/ped_900mVBL_14_0mVfC_2_0us.png)".format(log.item072) + "\n")
            # file.write("![ped](./{}/gain_900mVBL_14_0mVfC_2_0us.png)".format(log.item072) + "\n")

#   09      Calibration 04:
            if 9 in log.test_label:
                if check_status09 == True:
                    file.write(
                        '### <span style = "color : green;"> "Item_09 Cali_4 configuration SG1 SE & DIFF 14 mVfC" </span>' + '\n')
                else:
                    file.write(
                        '### <span style = "color : red;"> "Item_09 Cali_4 configuration SG1 SE & DIFF 14 mVfC" </span>' + '\n')

            # SE    900 mVBL    14_0 mVfC       2 us
                file.write('### Calibration 04 SE SGP1 900 mVBL    14_0 mVfC    2 us' + '\n')
                file.write("![ped](./{}/enc_900mVBL_14_0mVfC_2_0us_sgp1.png)".format(log.item091) + "![ped](./{}/Line_range_900mVBL_14_0mVfC_2_0us_sgp1.png)".format(log.item091) + "\n")
                file.write("![ped](./{}/gain_900mVBL_14_0mVfC_2_0us_sgp1.png)".format(log.item091) + "\n")
                file.write("![ped](./{}/ped_900mVBL_14_0mVfC_2_0us_sgp1.png)".format(log.item091) + "\n")
            # DIFF  900 mVBL    14 mVfC     2 us
            # file.write('### Calibration 022 DIFF 900 mVBL    14_0 mVfC    2 us' + '\n')
            # file.write("![ped](./{}/enc_900mVBL_14_0mVfC_2_0us.png)".format(log.item092) + "![ped](./{}/ped_900mVBL_14_0mVfC_2_0us.png)".format(log.item092) + "\n")
            # file.write("![ped](./{}/gain_900mVBL_14_0mVfC_2_0us.png)".format(log.item092) + "\n")
            


# 10        print <FE_MON>
            if 10 in log.test_label:
                if check_status10 == True:
                    file.write(
                        '### <span style = "color : green;"> "Item_10 FE Mon" </span>' + '\n')
                else:
                    file.write(
                        '### <span style = "color : red;"> "Item_10 FE Mon" </span>' + '\n')

                file.write('#### mon_bandgap' + '\n')
                info = dict_to_markdown_table(log.report_log10_01[femb_id], VALUE="Horizontal")
                file.write(info + '\n')
                file.write("![ped](./{}/FE_Mon.png)".format(log.item10) + "\n")

# 11        print <FE_DAC_MON>
            # 11_01
            if 11 in log.test_label:
                if check_status11 == True:
                    file.write(
                        '### <span style = "color : green;"> "Item_11 FE DAC linearity" </span>' + '\n')
                else:
                    file.write(
                        '### <span style = "color : red;"> "Item_11 FE DAC linearity" </span>' + '\n')
                file.write('### FE_DAC_MON' + '\n')
                info = dict_to_markdown_table(log.report_log11_01[femb_id])
                file.write(info + '\n')
                file.write("![ped](./{}/mon_LArASIC_DAC_25mVfC.png)".format(log.item11) + "\n")

# 12        print <ADC_MON>
            # 12_01
            if 12 in log.test_label:
                if check_status12 == True:
                    file.write(
                        '### <span style = "color : green;"> "Item_12 FE DAC linearity" </span>' + '\n')
                else:
                    file.write(
                        '### <span style = "color : red;"> "Item_12 FE DAC linearity" </span>' + '\n')

                file.write('### FE_ADC_MON' + '\n')
                info = dict_to_markdown_table(log.ADCMON_table[femb_id], VALUE="ADC_MON")
                file.write(info + '\n')
                file.write("![ped](./{}/mon_VCMI.png)".format(log.item12) + "![ped](./{}/mon_VCMO.png)".format(log.item12)  + "![ped](./{}/mon_VREFN.png)".format(log.item12)  + "![ped](./{}/mon_VREFP.png)".format(log.item12) + "\n")

#   13      Calibration 04:
            if 13 in log.test_label:
                if check_status13 == True:
                    file.write(
                        '### <span style = "color : green;"> "Item_13 Cali_5 configuration SG1 SE & DIFF 14 mVfC" </span>' + '\n')
                else:
                    file.write(
                        '### <span style = "color : red;"> "Item_13 Cali_5 configuration SG1 SE & DIFF 14 mVfC" </span>' + '\n')
                # SE    900 mVBL    14_0 mVfC       2 us
                file.write('### Calibration 04 SE SGP1 900 mVBL    14_0 mVfC    2 us' + '\n')
                file.write("![ped](./{}/enc_900mVBL_14_0mVfC_2_0us.png)".format(log.item13) + "![ped](./{}/Line_range_900mVBL_14_0mVfC_2_0us.png)".format(log.item13) + "\n")
                file.write("![ped](./{}/gain_900mVBL_14_0mVfC_2_0us.png)".format(log.item13) + "\n")
                file.write("![ped](./{}/ped_900mVBL_14_0mVfC_2_0us.png)".format(log.item13) + "\n")

            #   14      Calibration 04:
            if 14 in log.test_label:
                if check_status14 == True:
                    file.write(
                        '### <span style = "color : green;"> "Item_13 Cali_5 configuration SG1 SE & DIFF 14 mVfC" </span>' + '\n')
                else:
                    file.write(
                        '### <span style = "color : red;"> "Item_13 Cali_5 configuration SG1 SE & DIFF 14 mVfC" </span>' + '\n')
                # SE    900 mVBL    14_0 mVfC       2 us
                file.write('### Calibration 04 SE SGP1 900 mVBL    14_0 mVfC    2 us' + '\n')
                file.write("![ped](./{}/enc_200mVBL_14_0mVfC_2_0us.png)".format(log.item14) + "![ped](./{}/Line_range_200mVBL_14_0mVfC_2_0us.png)".format(log.item14) + "\n")
                file.write("![ped](./{}/gain_200mVBL_14_0mVfC_2_0us.png)".format(log.item14) + "\n")
                file.write("![ped](./{}/ped_200mVBL_14_0mVfC_2_0us.png)".format(log.item14) + "\n")

# 15        print <ADC_DC noise measurement>
            # 12_01
            if 15 in log.test_label:
                file.write('### <span style = "color : green;"> "Item_15 femb_adc_sync_pat_report" </span>' + '\n')

                file.write('### ADC_DC noise measurement' + '\n')
                # info = dict_to_markdown_table(log.ADCMON_table[femb_id], VALUE="ADC_MON")
                # file.write(info + '\n')
                file.write("![ped](./{}/ped_ADC_Test_mode_DC_Noise_SE.png)".format(log.item15))
                file.write("![ped](./{}/ped_ADC_SYNC_PAT_SHA_SE.png)".format(log.item15))
                file.write("![ped](./{}/ped_ADC_SYNC_PAT_SHA_DIFF.png)".format(log.item15))
                file.write("[PDF](./{}/report.pdf)".format(log.item15) + "\n")

# 16        print <ADC_DC noise measurement>
            # 12_01
            if 16 in log.test_label:
                if check_status16 == True:
                    file.write('### <span style = "color : green;"> "Item_16 PLL_scan_report" </span>' + '\n')
                else:
                    file.write('### <span style = "color : red;"> "Item_16 PLL_scan_report" </span>' + '\n')
                file.write("[PDF](./{}/report.pdf)".format(log.item16) + "\n")
'''
'''   


