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

# 03        print <Leakage Current>
            file.write('## ITEM 03 Leakage Current' + '\n')
            file.write("------\n")
            # 03_01 500 pA
            file.write('### Pulse LC 500 pA' + '\n')
            info = dict_to_markdown_table(log.report_log03_01[femb_id])
            file.write(info + '\n')
            file.write("![ped](./{}/pulse_LC_SE_200mVBL_14_0mVfC_2_0us_0x20_500pA.png)".format(log.item3) + "\n")

            # 03_02 100 pA
            file.write('### Pulse LC 100 pA' + '\n')
            info = dict_to_markdown_table(log.report_log03_02[femb_id])
            file.write(info + '\n')
            file.write("![ped](./{}/pulse_LC_SE_200mVBL_14_0mVfC_2_0us_0x20_100pA.png)".format(log.item3) + "\n")

            # 03_03 5 nA
            file.write('### Pulse LC 5 nA' + '\n')
            info = dict_to_markdown_table(log.report_log03_03[femb_id])
            file.write(info + '\n')
            file.write("![ped](./{}/pulse_LC_SE_200mVBL_14_0mVfC_2_0us_0x20_5nA.png)".format(log.item3) + "\n")

            # 03_04 1 nA
            file.write('### Pulse LC 1 nA' + '\n')
            info = dict_to_markdown_table(log.report_log03_04[femb_id])
            file.write(info + '\n')
            file.write("![ped](./{}/pulse_LC_SE_200mVBL_14_0mVfC_2_0us_0x20_1nA.png)".format(log.item3) + "\n")






# 04        print <Check Pulse>




# 05




# 10        print <FE_MON>
            file.write('### FE_MON' + '\n')
            # 10_01
            file.write('#### mon_bandgap' + '\n')
            info = dict_to_markdown_table(log.report_log10_01[femb_id])
            file.write(info + '\n')
            file.write("![ped](./{}/mon_bandgap.png)".format(log.item10) + "\n")

            # 10_02
            file.write('#### mon_temperature' + '\n')
            info = dict_to_markdown_table(log.report_log10_02[femb_id])
            file.write(info + '\n')
            file.write("![ped](./{}/mon_temperature.png)".format(log.item10) + "\n")

            # 10_03
            file.write('#### mon_200mVBL_sdf1' + '\n')
            info = dict_to_markdown_table(log.report_log10_03[femb_id])
            file.write(info + '\n')
            file.write("![ped](./{}/mon_200mVBL_sdf1.png)".format(log.item10) + "\n")

            # 10_04
            file.write('#### mon_200mVBL_sdf0' + '\n')
            info = dict_to_markdown_table(log.report_log10_04[femb_id])
            file.write(info + '\n')
            file.write("![ped](./{}/mon_200mVBL_sdf0.png)".format(log.item10) + "\n")

            # 10_05
            file.write('#### mon_900mVBL_sdf1' + '\n')
            info = dict_to_markdown_table(log.report_log10_05[femb_id])
            file.write(info + '\n')
            file.write("![ped](./{}/mon_900mVBL_sdf1.png)".format(log.item10) + "\n")

            # 10_06
            file.write('#### mon_900mVBL_sdf0' + '\n')
            info = dict_to_markdown_table(log.report_log10_06[femb_id])
            file.write(info + '\n')
            file.write("![ped](./{}/mon_900mVBL_sdf0.png)".format(log.item10) + "\n")



# 11        print <FE_DAC_MON>
            # 11_01
            file.write('### FE_DAC_MON' + '\n')
            info = dict_to_markdown_table(log.report_log11_01[femb_id])
            file.write(info + '\n')
            file.write("![ped](./{}/mon_LArASIC_DAC_25mVfC.png)".format(log.item11) + "\n")
