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


        fpmd = datareport[ifemb] + 'report_FEMB_{}.md'.format(fembNo['femb%d' % ifemb])
        print(datareport[ifemb])
        with open(fpmd, 'w', encoding = "utf-8") as file:
            # file.write('')
            file.write('\n')
            file.write('\n')
# Title     FEMB ID
            file.write('# Quality Control for < ' + (femb_id) + ' >\n')
# 00        Print <Input Information>
            file.write('## INPUT INFORMATION' + '\n')
            info = dict_to_markdown_table(log.report_log00, VALUE="Horizontal")
            file.write(info + '\n')


# 01        Print <Power Consumption>
            file.write('## ITEM 01 POWER CONSUMPTION' + '\n')
            file.write("------\n")
            file.write('### SE Power Measurement' + '\n')
            info = dict_to_markdown_table(log.report_log01_11[femb_id], VALUE="PWRVALUE")
            file.write(info + '\n')

            file.write('### SE Power pulse' + '\n')
            info = dict_to_markdown_table(log.report_log01_12[femb_id])
            file.write(info + '\n')
            file.write("![ped](./PWR_Meas/pulse_PWR_SE_200mVBL_14_0mVfC_2_0us.png)" + "\n")

            file.write('### SE power rail' + '\n')
            info = dict_to_markdown_table(log.report_log01_13[femb_id], VALUE="Horizontal")
            file.write(info + '\n')

            file.write("------\n")
            file.write('### SEDC power measurement' + '\n')
            info = dict_to_markdown_table(log.report_log01_21[femb_id], VALUE="PWRVALUE")
            file.write(info + '\n')

            file.write('### SEDC Power pulse' + '\n')
            info = dict_to_markdown_table(log.report_log01_22[femb_id])
            file.write(info + '\n')
            file.write("![ped](./PWR_Meas/pulse_PWR_SE_SDF_200mVBL_14_0mVfC_2_0us.png)" + "\n")

            file.write('### SEDC power rail' + '\n')
            info = dict_to_markdown_table(log.report_log01_23[femb_id], VALUE="Horizontal")
            file.write(info + '\n')

            file.write("------\n")
            file.write('### DIFF power measurement' + '\n')
            info = dict_to_markdown_table(log.report_log01_31[femb_id], VALUE="PWRVALUE")
            file.write(info + '\n')

            file.write('### DIFF Power pulse' + '\n')
            info = dict_to_markdown_table(log.report_log01_32[femb_id])
            file.write(info + '\n')
            file.write("![ped](./PWR_Meas/pulse_PWR_DIFF_200mVBL_14_0mVfC_2_0us.png)" + "\n")

            file.write('### DIFF power rail' + '\n')
            info = dict_to_markdown_table(log.report_log01_33[femb_id], VALUE="Horizontal")
            file.write(info + '\n')
            file.write("______\n")
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
            file.write('### RMS configuration SE/SEON/SELC/DIFF 200/900 mV 4_7/7_8/14/25 mV/fC 0.5/1/2/3 us' + '\n')
            file.write('#### All_200mVBL_Configuration' + '\n')
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
'''   


'''