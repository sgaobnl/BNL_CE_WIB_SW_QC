import QC_components.qc_log as log
import subprocess


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
#             file.write('# Quality Control for < ' + (femb_id) + ' >\n')
# 00        Print <Input Information>
            file.write('## INPUT INFORMATION' + '\n')
            info = dict_to_markdown_table(log.report_log00, VALUE="Horizontal")
            file.write(info + '\n')


# 01        Print <Power Consumption>
            if 1 in log.test_label:
                if check_status01:
                    Head01 = '### ' + '<span style="color: green;">' + 'ITEM 01 POWER CONSUMPTION' + '    < Pass >' + '</span>'  + '\n'
                else:
                    Head01 = '### ' + '<span style="color: red;">' + 'ITEM 01 POWER CONSUMPTION' + '    < Fail >' + '</span>'  + '\n'
                file.write(Head01 + '\n')
                file.write("------\n")
                file.write('### 01_11 SE Power Measurement' + '\n')
                # file.write('<div style = "display: flex; justify-content: space-between">' + '\n\n')
                info = dict_to_markdown_table(log.report_log01_11[femb_id], VALUE="PWRVALUE")
                file.write(info + '\n')
                # file.write('</div>' + '\n\n')

                file.write('### 01_12 SE Power pulse' + '\n')
                info = dict_to_markdown_table(log.report_log01_12[femb_id], VALUE="Horizontal")
                file.write(info + '\n')
                file.write("![ped](./PWR_Meas/pulse_PWR_SE_200mVBL_14_0mVfC_2_0us.png)" + "\n")

                file.write('### 01_13 SE power rail' + '\n')
                info = dict_to_markdown_table(log.report_log01_13[femb_id], VALUE="Horizontal")
                file.write(info + '\n')

                file.write("------\n")
                file.write('### 01_21 SE ON Power Measurement' + '\n')
                # file.write('<div style = "display: flex; justify-content: space-between">' + '\n\n')
                info = dict_to_markdown_table(log.report_log01_21[femb_id], VALUE="PWRVALUE")
                file.write(info + '\n')
                # file.write('</div>' + '\n\n')

                file.write('### 01_22 SE ON Power pulse' + '\n')
                info = dict_to_markdown_table(log.report_log01_22[femb_id], VALUE="Horizontal")
                file.write(info + '\n')
                file.write("![ped](./PWR_Meas/pulse_PWR_SE_ON_200mVBL_14_0mVfC_2_0us.png)" + "\n")

                file.write('### 01_23 SE ON power rail' + '\n')
                info = dict_to_markdown_table(log.report_log01_23[femb_id], VALUE="Horizontal")
                file.write(info + '\n')

                file.write("------\n")
                file.write('### 01_31 DIFF Power Measurement' + '\n')
                # file.write('<div style = "display: flex; justify-content: space-between">' + '\n\n')
                info = dict_to_markdown_table(log.report_log01_31[femb_id], VALUE="PWRVALUE")
                file.write(info + '\n')
                # file.write('</div>' + '\n\n')

                file.write('### 01_32 DIFF Power pulse' + '\n')
                info = dict_to_markdown_table(log.report_log01_32[femb_id], VALUE="Horizontal")
                file.write(info + '\n')
                file.write("![ped](./PWR_Meas/pulse_PWR_DIFF_200mVBL_14_0mVfC_2_0us.png)" + "\n")

                file.write('### 01_33 DIFF power rail' + '\n')
                info = dict_to_markdown_table(log.report_log01_33[femb_id], VALUE="Horizontal")
                file.write(info + '\n')


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
                log.check_log03_table_01[femb_id]['ppk_mean'] = " | PPK Mean | {} | {} | {} | {} | \n".format(log.report_log03_02[femb_id]["ppk_mean"], log.report_log03_01[femb_id]["ppk_mean"], log.report_log03_04[femb_id]["ppk_mean"], log.report_log03_03[femb_id]["ppk_mean"])
                log.check_log03_table_01[femb_id]['ppk_err'] = " | PPK Error | {} | {} | {} | {} | \n".format(log.report_log03_02[femb_id]["ppk_err"], log.report_log03_01[femb_id]["ppk_err"], log.report_log03_04[femb_id]["ppk_err"], log.report_log03_03[femb_id]["ppk_err"])
                log.check_log03_table_01[femb_id]['npk_mean'] = " | NPK Mean | {} | {} | {} | {} | \n".format(log.report_log03_02[femb_id]["npk_mean"], log.report_log03_01[femb_id]["npk_mean"], log.report_log03_04[femb_id]["npk_mean"], log.report_log03_03[femb_id]["npk_mean"])
                log.check_log03_table_01[femb_id]['npk_err'] = " | NPK Error | {} | {} | {} | {} | \n".format(log.report_log03_02[femb_id]["npk_err"], log.report_log03_01[femb_id]["npk_err"], log.report_log03_04[femb_id]["npk_err"], log.report_log03_03[femb_id]["npk_err"])

                file.write(log.check_log03_table_01[femb_id]['title'])
                file.write(log.check_log03_table_01[femb_id]['table line'])
                file.write(log.check_log03_table_01[femb_id]['ppk_mean'])
                file.write(log.check_log03_table_01[femb_id]['ppk_err'])
                file.write(log.check_log03_table_01[femb_id]['npk_mean'])
                file.write(log.check_log03_table_01[femb_id]['npk_err'] + '\n')







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
            '''
# 03        print <Leakage Current>
            file.write('## ITEM 03 Leakage Current' + '\n')
            file.write("------\n")

            # 03_01 100 pA
            file.write('### Pulse LC 100 pA' + '\n')
            info = dict_to_markdown_table(log.report_log03_02[femb_id], VALUE="Horizontal")
            file.write(info + '\n')
            file.write("![ped](./{}/pulse_LC_SE_200mVBL_14_0mVfC_2_0us_0x20_100pA.png)".format(log.item3) + "\n")

            # 03_02 500 pA
            file.write('### Pulse LC 500 pA' + '\n')
            info = dict_to_markdown_table(log.report_log03_01[femb_id], VALUE="Horizontal")
            file.write(info + '\n')
            file.write("![ped](./{}/pulse_LC_SE_200mVBL_14_0mVfC_2_0us_0x20_500pA.png)".format(log.item3) + "\n")

            # 03_03 1 nA
            file.write('### Pulse LC 1 nA' + '\n')
            info = dict_to_markdown_table(log.report_log03_04[femb_id], VALUE="Horizontal")
            file.write(info + '\n')
            file.write("![ped](./{}/pulse_LC_SE_200mVBL_14_0mVfC_2_0us_0x20_1nA.png)".format(log.item3) + "\n")

            # 03_04 5 nA
            file.write('### Pulse LC 5 nA' + '\n')
            info = dict_to_markdown_table(log.report_log03_03[femb_id], VALUE="Horizontal")
            file.write(info + '\n')
            file.write("![ped](./{}/pulse_LC_SE_200mVBL_14_0mVfC_2_0us_0x20_5nA.png)".format(log.item3) + "\n")






# 04        print <Check Pulse>
'''



# 05        RMS configuration
            if log.report_log05_fin_result == True:
                file.write('### <span style = "color : green;"> "RMS configuration SE/SEON/SELC/DIFF 200/900 mV 4_7/7_8/14/25 mV/fC 0.5/1/2/3 us" </span>' + '\n')
            else:
                file.write('### <span style = "color : red;"> "RMS configuration SE/SEON/SELC/DIFF 200/900 mV 4_7/7_8/14/25 mV/fC 0.5/1/2/3 us" </span>' + '\n')
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
            file.write('### Calibration 011 SE 200 mVBL    4_7 mVfC    2 us' + '\n')
            file.write("![ped](./{}/enc_200mVBL_4_7mVfC_2_0us.png)".format(log.item061) + "![ped](./{}/ped_200mVBL_4_7mVfC_2_0us.png)".format(log.item061) + "\n")
            file.write("![ped](./{}/gain_200mVBL_4_7mVfC_2_0us.png)".format(log.item061) + "\n")

            file.write('### Calibration 012 SE 200 mVBL    7_8 mVfC    2 us' + '\n')
            file.write("![ped](./{}/enc_200mVBL_7_8mVfC_2_0us.png)".format(log.item061) + "![ped](./{}/ped_200mVBL_7_8mVfC_2_0us.png)".format(log.item061) + "\n")
            file.write("![ped](./{}/gain_200mVBL_7_8mVfC_2_0us.png)".format(log.item061) + "\n")

            file.write('### Calibration 013 SE 200 mVBL    14_0 mVfC    2 us' + '\n')
            file.write("![ped](./{}/enc_200mVBL_14_0mVfC_2_0us.png)".format(log.item061) + "![ped](./{}/ped_200mVBL_14_0mVfC_2_0us.png)".format(log.item061) + "\n")
            file.write("![ped](./{}/gain_200mVBL_14_0mVfC_2_0us.png)".format(log.item061) + "\n")

            file.write('### Calibration 014 SE 200 mVBL    25_0 mVfC    2 us' + '\n')
            file.write("![ped](./{}/enc_200mVBL_25_0mVfC_2_0us.png)".format(log.item061) + "![ped](./{}/ped_200mVBL_25_0mVfC_2_0us.png)".format(log.item061)+ "\n")
            file.write("![ped](./{}/gain_200mVBL_25_0mVfC_2_0us.png)".format(log.item061) + "\n")

            file.write('### Calibration 015 DIFF 200 mVBL    14_0 mVfC    2 us' + '\n')
            file.write("![ped](./{}/enc_200mVBL_14_0mVfC_2_0us.png)".format(log.item062) + "![ped](./{}/ped_200mVBL_14_0mVfC_2_0us.png)".format(log.item062)+ "\n")
            file.write("![ped](./{}/gain_200mVBL_14_0mVfC_2_0us.png)".format(log.item062) + "\n")

#   07      Calibration 02:
            # SE    900 mVBL    14_0 mVfC       2 us
            file.write('### Calibration 021 SE 900 mVBL    14_0 mVfC    2 us' + '\n')
            file.write("![ped](./{}/enc_900mVBL_14_0mVfC_2_0us.png)".format(log.item071) + "![ped](./{}/ped_900mVBL_14_0mVfC_2_0us.png)".format(log.item071) + "\n")
            file.write("![ped](./{}/gain_900mVBL_14_0mVfC_2_0us.png)".format(log.item071) + "\n")
            # DIFF  900 mVBL    14 mVfC     2 us
            file.write('### Calibration 022 DIFF 900 mVBL    14_0 mVfC    2 us' + '\n')
            file.write("![ped](./{}/enc_900mVBL_14_0mVfC_2_0us.png)".format(log.item072) + "![ped](./{}/ped_900mVBL_14_0mVfC_2_0us.png)".format(log.item072) + "\n")
            file.write("![ped](./{}/gain_900mVBL_14_0mVfC_2_0us.png)".format(log.item072) + "\n")



# 10        print <FE_MON>
            file.write('### FE_MON' + '\n')
            # 10_01
            file.write('#### mon_bandgap' + '\n')
            info = dict_to_markdown_table(log.report_log10_01[femb_id], VALUE="Horizontal")
            file.write(info + '\n')
            file.write("![ped](./{}/FE_Mon.png)".format(log.item10) + "\n")

# 11        print <FE_DAC_MON>
            # 11_01
            file.write('### FE_DAC_MON' + '\n')
            info = dict_to_markdown_table(log.report_log11_01[femb_id])
            file.write(info + '\n')
            file.write("![ped](./{}/mon_LArASIC_DAC_25mVfC.png)".format(log.item11) + "\n")
# 12        print <ADC_MON>
            # 12_01
            file.write('### FE_ADC_MON' + '\n')
            info = dict_to_markdown_table(log.ADCMON_table[femb_id], VALUE="ADC_MON")
            file.write(info + '\n')
            file.write("![ped](./{}/mon_VCMI.png)".format(log.item12) + "![ped](./{}/mon_VCMO.png)".format(log.item12)  + "![ped](./{}/mon_VREFN.png)".format(log.item12)  + "![ped](./{}/mon_VREFP.png)".format(log.item12) + "\n")

# 15        print <ADC_DC noise measurement>
            # 12_01
            file.write('### ADC_DC noise measurement' + '\n')
            # info = dict_to_markdown_table(log.ADCMON_table[femb_id], VALUE="ADC_MON")
            # file.write(info + '\n')
            file.write("![ped](./{}/ped_ADC_SYNC_PAT_noSHA_SE.png)".format(log.item15))
            file.write("![ped](./{}/ped_ADC_SYNC_PAT_SHA_SE.png)".format(log.item15))
            file.write("![ped](./{}/ped_ADC_SYNC_PAT_SHA_DIFF.png)".format(log.item15))


'''   


'''