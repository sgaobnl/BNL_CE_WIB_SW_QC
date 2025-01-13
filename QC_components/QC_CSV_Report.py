import os
import pickle
import csv
import QC_components.qc_log as log
import re


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




def CSV_section_report(datareport, fembs, fembNo):


#   Start Markdown
    for ifemb in fembs:
        femb_id = "FEMB ID {}".format(fembNo['femb%d' % ifemb])
        fpmd = datareport[ifemb] + 'report_FEMB_{}_item{}_slot{}.csv'.format(fembNo['femb%d' % ifemb], log.test_label, ifemb)
        print(datareport[ifemb])

        with open(fpmd, 'w', encoding = "utf-8") as file:
# Title        FEMB ID
# 00           Print <Input Information>
            writer = csv.writer(file)
            info = log.report_log00
            for key, value in log.report_log00.items():
                log.report_log00[key] = re.sub(r'\\.', '', str(value))
                writer.writerow([key, value])

            if 1 in log.test_label:
                # csv REPORT
                # POWER CONSUMPTION
                section = 'Single-End Interface OFF\n'
                file.write(section)
                for key, value in log.report_log01_11[femb_id].items():
                    writer.writerow([key, value])
                section = 'Single-End Interface ON\n'
                file.write(section)
                for key, value in log.report_log01_21[femb_id].items():
                    writer.writerow([key, value])
                section = 'Differential Interface ON\n'
                file.write(section)
                for key, value in log.report_log01_31[femb_id].items():
                    writer.writerow([key, value])


                section = 'SE OFF Voltage power rail\n'
                file.write(section)
                for key, value in log.report_log01_13[femb_id].items():
                    writer.writerow([key, value])
                section = 'SE ON Voltage power rail\n'
                file.write(section)
                for key, value in log.report_log01_23[femb_id].items():
                    writer.writerow([key, value])
                section = 'DIFF Voltage power rail\n'
                file.write(section)
                for key, value in log.report_log01_33[femb_id].items():
                    writer.writerow([key, value])

                section = 'General Pulse Review at Power Consumption Test\n'
                file.write(section)
                section = 'SE OFF\n'
                file.write(section)
                for key, value in log.report_log01_12[femb_id].items():
                    writer.writerow([key, value])
                section = 'SE ON\n'
                file.write(section)
                for key, value in log.report_log01_22[femb_id].items():
                    writer.writerow([key, value])
                section = 'SEDC (DIFF)\n'
                file.write(section)
                for key, value in log.report_log01_32[femb_id].items():
                    writer.writerow([key, value])

            # if 2 in log.test_label:

            if 3 in log.test_label:
                section = 'Pulse check at 4 Leakage current setting\n'
                file.write(section)
                section = '100 pA\n'
                file.write(section)
                for key, value in log.report_log03_02[femb_id].items():
                    writer.writerow([key, value])
                section = '500 pA\n'
                file.write(section)
                for key, value in log.report_log03_01[femb_id].items():
                    writer.writerow([key, value])
                section = '1 nA\n'
                file.write(section)
                for key, value in log.report_log03_04[femb_id].items():
                    writer.writerow([key, value])
                section = '5 nA\n'
                file.write(section)
                for key, value in log.report_log03_03[femb_id].items():
                    writer.writerow([key, value])

            if 4 in log.test_label:
                section = 'Pulse response at different setting\n'
                file.write(section)
                section = 'SE OFF baseline = 200 mV 4.7 mV/fC 0.5 us \n'
                file.write(section)
                for key, value in log.report_log04_01_4705[femb_id].items():
                    writer.writerow([key, value])
                section = 'SE OFF baseline = 200 mV 4.7 mV/fC 1 us \n'
                file.write(section)
                for key, value in log.report_log04_01_4710[femb_id].items():
                    writer.writerow([key, value])
                section = 'SE OFF baseline = 200 mV 4.7 mV/fC 2 us \n'
                file.write(section)
                for key, value in log.report_log04_01_4720[femb_id].items():
                    writer.writerow([key, value])
                section = 'SE OFF baseline = 200 mV 4.7 mV/fC 3 us \n'
                file.write(section)
                for key, value in log.report_log04_01_4730[femb_id].items():
                    writer.writerow([key, value])

                section = 'SE OFF baseline = 200 mV 7.8 mV/fC 0.5 us \n'
                file.write(section)
                for key, value in log.report_log04_01_7805[femb_id].items():
                    writer.writerow([key, value])
                section = 'SE OFF baseline = 200 mV 7.8 mV/fC 1 us \n'
                file.write(section)
                for key, value in log.report_log04_01_7810[femb_id].items():
                    writer.writerow([key, value])
                section = 'SE OFF baseline = 200 mV 7.8 mV/fC 2 us \n'
                file.write(section)
                for key, value in log.report_log04_01_7820[femb_id].items():
                    writer.writerow([key, value])
                section = 'SE OFF baseline = 200 mV 7.8 mV/fC 3 us \n'
                file.write(section)
                for key, value in log.report_log04_01_7830[femb_id].items():
                    writer.writerow([key, value])

                section = 'SE OFF baseline = 200 mV 14 mV/fC 0.5 us \n'
                file.write(section)
                for key, value in log.report_log04_01_1405[femb_id].items():
                    writer.writerow([key, value])
                section = 'SE OFF baseline = 200 mV 14 mV/fC 1 us \n'
                file.write(section)
                for key, value in log.report_log04_01_1410[femb_id].items():
                    writer.writerow([key, value])
                section = 'SE OFF baseline = 200 mV 14 mV/fC 2 us \n'
                file.write(section)
                for key, value in log.report_log04_01_1420[femb_id].items():
                    writer.writerow([key, value])
                section = 'SE OFF baseline = 200 mV 14 mV/fC 3 us \n'
                file.write(section)
                for key, value in log.report_log04_01_1430[femb_id].items():
                    writer.writerow([key, value])

                section = 'SE OFF baseline = 200 mV 25 mV/fC 0.5 us \n'
                file.write(section)
                for key, value in log.report_log04_01_2505[femb_id].items():
                    writer.writerow([key, value])
                section = 'SE OFF baseline = 200 mV 25 mV/fC 1 us \n'
                file.write(section)
                for key, value in log.report_log04_01_2510[femb_id].items():
                    writer.writerow([key, value])
                section = 'SE OFF baseline = 200 mV 25 mV/fC 2 us \n'
                file.write(section)
                for key, value in log.report_log04_01_2520[femb_id].items():
                    writer.writerow([key, value])
                section = 'SE OFF baseline = 200 mV 25 mV/fC 3 us \n'
                file.write(section)
                for key, value in log.report_log04_01_2530[femb_id].items():
                    writer.writerow([key, value])




                section = 'Pulse response at different setting\n'
                file.write(section)
                section = 'SE OFF baseline = 900 mV 4.7 mV/fC 0.5 us \n'
                file.write(section)
                for key, value in log.report_log04_02_4705[femb_id].items():
                    writer.writerow([key, value])
                section = 'SE OFF baseline = 900 mV 4.7 mV/fC 1 us \n'
                file.write(section)
                for key, value in log.report_log04_02_4710[femb_id].items():
                    writer.writerow([key, value])
                section = 'SE OFF baseline = 900 mV 4.7 mV/fC 2 us \n'
                file.write(section)
                for key, value in log.report_log04_02_4720[femb_id].items():
                    writer.writerow([key, value])
                section = 'SE OFF baseline = 900 mV 4.7 mV/fC 3 us \n'
                file.write(section)
                for key, value in log.report_log04_02_4730[femb_id].items():
                    writer.writerow([key, value])

                section = 'SE OFF baseline = 900 mV 7.8 mV/fC 0.5 us \n'
                file.write(section)
                for key, value in log.report_log04_02_7805[femb_id].items():
                    writer.writerow([key, value])
                section = 'SE OFF baseline = 900 mV 7.8 mV/fC 1 us \n'
                file.write(section)
                for key, value in log.report_log04_02_7810[femb_id].items():
                    writer.writerow([key, value])
                section = 'SE OFF baseline = 900 mV 7.8 mV/fC 2 us \n'
                file.write(section)
                for key, value in log.report_log04_02_7820[femb_id].items():
                    writer.writerow([key, value])
                section = 'SE OFF baseline = 900 mV 7.8 mV/fC 3 us \n'
                file.write(section)
                for key, value in log.report_log04_02_7830[femb_id].items():
                    writer.writerow([key, value])

                section = 'SE OFF baseline = 900 mV 14 mV/fC 0.5 us \n'
                file.write(section)
                for key, value in log.report_log04_02_1405[femb_id].items():
                    writer.writerow([key, value])
                section = 'SE OFF baseline = 900 mV 14 mV/fC 1 us \n'
                file.write(section)
                for key, value in log.report_log04_02_1410[femb_id].items():
                    writer.writerow([key, value])
                section = 'SE OFF baseline = 900 mV 14 mV/fC 2 us \n'
                file.write(section)
                for key, value in log.report_log04_02_1420[femb_id].items():
                    writer.writerow([key, value])
                section = 'SE OFF baseline = 900 mV 14 mV/fC 3 us \n'
                file.write(section)
                for key, value in log.report_log04_02_1430[femb_id].items():
                    writer.writerow([key, value])

                section = 'SE OFF baseline = 900 mV 25 mV/fC 0.5 us \n'
                file.write(section)
                for key, value in log.report_log04_02_2505[femb_id].items():
                    writer.writerow([key, value])
                section = 'SE OFF baseline = 900 mV 25 mV/fC 1 us \n'
                file.write(section)
                for key, value in log.report_log04_02_2510[femb_id].items():
                    writer.writerow([key, value])
                section = 'SE OFF baseline = 900 mV 25 mV/fC 2 us \n'
                file.write(section)
                for key, value in log.report_log04_02_2520[femb_id].items():
                    writer.writerow([key, value])
                section = 'SE OFF baseline = 900 mV 25 mV/fC 3 us \n'
                file.write(section)
                for key, value in log.report_log04_02_2530[femb_id].items():
                    writer.writerow([key, value])

            if 5 in log.test_label:
                section = 'RMS noise at different setting\n'
                file.write(section)
                section = 'Mean, std, max, min\n'
                file.write(section)
                print(log.report_log057_fembrms[ifemb])
                print(121212121)
                for key, value in log.report_log057_fembrms[ifemb].items():
                    writer.writerow([key, value])

            if 6 in log.test_label:
                section = 'CALI1 200mVBL 14_0mVfC 2_0us\n'
                file.write(section)
                for key, value in log.report_log0603csvgain[ifemb].items():
                    writer.writerow([key, value])
                for key, value in log.report_log0603csvinl[ifemb].items():
                    writer.writerow([key, value])
                for key, value in log.report_log0603csvlinerange[ifemb].items():
                    writer.writerow([key, value])

                section = 'CALI1 200mVBL 4_7mVfC 2_0us\n'
                file.write(section)
                for key, value in log.report_log0601csvgain[ifemb].items():
                    writer.writerow([key, value])
                for key, value in log.report_log0601csvinl[ifemb].items():
                    writer.writerow([key, value])
                for key, value in log.report_log0601csvlinerange[ifemb].items():
                    writer.writerow([key, value])

                section = 'CALI1 200mVBL 7_8mVfC 2_0us\n'
                file.write(section)
                for key, value in log.report_log0602csvgain[ifemb].items():
                    writer.writerow([key, value])
                for key, value in log.report_log0602csvinl[ifemb].items():
                    writer.writerow([key, value])
                for key, value in log.report_log0602csvlinerange[ifemb].items():
                    writer.writerow([key, value])

                section = 'CALI1 200mVBL 25_0mVfC 2_0us\n'
                file.write(section)
                for key, value in log.report_log0604csvgain[ifemb].items():
                    writer.writerow([key, value])
                for key, value in log.report_log0604csvinl[ifemb].items():
                    writer.writerow([key, value])
                for key, value in log.report_log0604csvlinerange[ifemb].items():
                    writer.writerow([key, value])

            if 7 in log.test_label:
                section = 'CALI2 900mVBL 14_0mVfC 2_0us\n'
                file.write(section)
                for key, value in log.report_log0701csvgain[ifemb].items():
                    writer.writerow([key, value])
                for key, value in log.report_log0701csvinl[ifemb].items():
                    writer.writerow([key, value])
                for key, value in log.report_log0701csvlinerange[ifemb].items():
                    writer.writerow([key, value])

            if 8 in log.test_label:
                section = 'CALI3 SGP=1 200mVBL 14_0mVfC 2_0us\n'
                file.write(section)
                for key, value in log.report_log0801csvgain[ifemb].items():
                    writer.writerow([key, value])
                for key, value in log.report_log0801csvinl[ifemb].items():
                    writer.writerow([key, value])
                for key, value in log.report_log0801csvlinerange[ifemb].items():
                    writer.writerow([key, value])

            if 9 in log.test_label:
                section = 'CALI4 SGP=1 900mVBL 14_0mVfC 2_0us\n'
                file.write(section)
                for key, value in log.report_log0901csvgain[ifemb].items():
                    writer.writerow([key, value])
                for key, value in log.report_log0901csvinl[ifemb].items():
                    writer.writerow([key, value])
                for key, value in log.report_log0901csvlinerange[ifemb].items():
                    writer.writerow([key, value])

            if 10 in log.test_label:
                # femb_id = "FEMB ID {}".format(self.fembsID['femb%d' % ifemb])
                section = 'Item #10 LArASIC Sensor (Bandgap, Baseline)\n'
                file.write(section)
                print(log.mon_pulse["bandgap"][femb_id])
                # for key, value in log.mon_pulse["bandgap"][femb_id]:
                writer.writerow(log.mon_pulse["bandgap"][femb_id])
                writer.writerow(log.mon_pulse["temperature"][femb_id])
                writer.writerow(log.mon_pulse["200mVBL_sdf0"][femb_id])
                writer.writerow(log.mon_pulse["900mVBL_sdf0"][femb_id])
                writer.writerow(log.mon_pulse["200mVBL_sdf1"][femb_id])
                writer.writerow(log.mon_pulse["900mVBL_sdf1"][femb_id])

            if 11 in log.test_label:
                # femb_id = "FEMB ID {}".format(self.fembsID['femb%d' % ifemb])
                section = 'Item #11 LArASIC Linearity\n'
                file.write(section)
                # for key, value in log.mon_pulse[bandgap"][femb_id]:
                for key, value in log.report_log1101csv[femb_id].items():
                    writer.writerow([key, value])

            if 12 in log.test_label:
                # femb_id = "FEMB ID {}".format(self.fembsID['femb%d' % ifemb])
                section = 'Item #12 ColdADC ref_voltage Linearity\n'
                file.write(section)
                # for key, value in log.mon_pulse[bandgap"][femb_id]:
                for key, value in log.ADCMON_table_cell[femb_id].items():
                    writer.writerow([key, value])

            if 13 in log.test_label:
                section = 'CALI5 external pulse 900mVBL 14_0mVfC 2_0us\n'
                file.write(section)
                for key, value in log.report_log1301csvgain[ifemb].items():
                    writer.writerow([key, value])
                for key, value in log.report_log1301csvinl[ifemb].items():
                    writer.writerow([key, value])
                for key, value in log.report_log1301csvlinerange[ifemb].items():
                    writer.writerow([key, value])

            if 14 in log.test_label:
                section = 'CALI6 external pulse 200mVBL 14_0mVfC 2_0us\n'
                file.write(section)
                for key, value in log.report_log1401csvgain[ifemb].items():
                    writer.writerow([key, value])
                for key, value in log.report_log1401csvinl[ifemb].items():
                    writer.writerow([key, value])
                for key, value in log.report_log1401csvlinerange[ifemb].items():
                    writer.writerow([key, value])

            if 15 in log.test_label:
                section = 'QC_femb_adc_sync_pat_t15\n'
                file.write(section)
                for key, value in log.check_log15csv[femb_id].items():
                    writer.writerow([key, value])

            if 16 in log.test_label:
                section = 'QC_femb_test_pattern_pll_t16\n'
                file.write(section)
                for key, value in log.check_log16csv[femb_id].items():
                    writer.writerow([key, value])

##  Detail Pages ================================================
'''

#   08      Calibration 03:
            if 8 in log.test_label:
                if check_status08:
                    Head08 = '### ' + '</span>' + '<span id="item8"> Chapter_8 </span>' + '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: green;">' + 'ITEM_08_Cali_3 SE 200 SGP' + '    < Pass >' + '</span>' + '\n'
                else:
                    Head08 = '### ' + '</span>' + '<span id="item8"> Chapter_8 </span>' + '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: red;">' + 'ITEM_08_Cali_3 SE 200 SGP' + '    < Fail >' + '</span>' + '\n'
            # SE    200 mVBL    4_7 mVfC       2 us    SGP1
                file.write(Head08 + '\n')
                file.write('### Calibration 03 SE SGP1 200 mVBL    4_7 mVfC    2 us' + '\n')
                file.write('<img src="./{}/enc_200mVBL_14_0mVfC_2_0us_sgp1.png" alt="picture" height={}>'.format(log.item081, PH) + "\n")  # width="200"
                file.write('<img src="./{}/Line_range_200mVBL_14_0mVfC_2_0us_sgp1.png" alt="picture" height={}>'.format(log.item081, PH) + "\n\n")  # width="200"
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
                file.write('### Calibration 04 SE SGP1 900 mVBL    4_7 mVfC    2 us' + '\n')
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
                file.write("![ped](./{}/ped_ADC_Test_mode_DC_Noise_SE.png)".format(log.item15))
                file.write("![ped](./{}/ped_ADC_SYNC_PAT_SHA_SE.png)".format(log.item15))
                file.write("![ped](./{}/ped_ADC_SYNC_PAT_SHA_DIFF.png)".format(log.item15))
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
            summary = '<span style="color: dark;">' + " FEMB # {}\t       Quality Control in Test ".format(fembNo['femb%d' % ifemb]) + '</span>' + '\n'
        else:
            if all_true:
                summary = '<span style="color: green;">' + " FEMB # {}\t      PASS\t    ALL Quality Control".format(fembNo['femb%d' % ifemb]) + '</span>'  + '\n'
            else:
                summary = '<span style="color: red;">' + " FEMB # {}\t      fail\t    the Quality Control tests".format(fembNo['femb%d' % ifemb]) + '</span>'  + '\n'
        print(summary)

###======================================================================

#   Start Markdown

        print('\n')
        frmd = datareport[ifemb] + 'Final_Report_FEMB_{}_S{}.md'.format(fembNo['femb%d' % ifemb], ifemb)
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
                Item01 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: green;">' + 'Item_01 POWER CONSUMPTION' + '&nbsp;&nbsp;&nbsp;&nbsp; < Pass > [Detail](./{})'.format(item_file[1-1]) + '</span>'
            elif check_status[1-1] is False:
                Item01 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: red;">' + 'Item_01 POWER CONSUMPTION' + '&nbsp;&nbsp;&nbsp;&nbsp; < Fail > [Detail](./{})'.format(item_file[1-1]) + '</span>'
            else:
                Item01 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: gray;">' + 'Item_01 POWER CONSUMPTION' + '&nbsp;&nbsp;&nbsp;&nbsp; < No Test >' + '</span>'
            file.write(Item01 + '\n\n')

            if check_status[2-1] is True:
                Item02 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: green;">' + 'Item_02 Power Cycle' + '&nbsp;&nbsp;&nbsp;&nbsp; < Pass > [Detail](./{})'.format(item_file[2-1]) + '</span>'
            elif check_status[2 - 1] is False:
                Item02 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: red;">' + 'Item_02 Power Cycle' + '&nbsp;&nbsp;&nbsp;&nbsp; < Fail > [Detail](./{})'.format(item_file[2-1]) + '</span>'
            else:
                Item02 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: gray;">' + 'Item_02 Power Cycle' + '&nbsp;&nbsp;&nbsp;&nbsp; < No Test >' + '</span>'
            file.write(Item02 + '\n\n')

            if check_status[3-1] is True:
                Item03 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: green;">' + 'Item_03 Leakage Current Pulse Response' + '&nbsp;&nbsp;&nbsp;&nbsp; < Pass > [Detail](./{})'.format(item_file[3-1]) + '</span>'
            elif check_status[3 - 1] is False:
                Item03 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: red;">' + 'Item_03 Leakage Current Pulse Response' + '&nbsp;&nbsp;&nbsp;&nbsp; < Fail > [Detail](./{})'.format(item_file[3-1]) + '</span>'
            else:
                Item03 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: gray;">' + 'Item_03 Leakage Current Pulse Response' + '&nbsp;&nbsp;&nbsp;&nbsp; < No Test >' + '</span>'
            file.write(Item03 + '\n\n')

            if check_status[4-1] is True:
                Item04 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: green;">' + 'Item_04 Whole Pulse Response' + '&nbsp;&nbsp;&nbsp;&nbsp; < Pass > [Detail](./{})'.format(item_file[4-1]) + '</span>'
            elif check_status[4 - 1] is False:
                Item04 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: red;">' + 'Item_04 Whole Pulse Response' + '&nbsp;&nbsp;&nbsp;&nbsp; < Fail > [Detail](./{})'.format(item_file[4-1]) + '</span>'
            else:
                Item04 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: gray;">' + 'Item_04 Whole Pulse Response' + '&nbsp;&nbsp;&nbsp;&nbsp; < No Test >' + '</span>'
            file.write(Item04 + '\n\n')

            if check_status[5-1] is True:
                Item05 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: green;">' + 'Item_05 RMS Evaluation' + '&nbsp;&nbsp;&nbsp;&nbsp; < Pass > [Detail](./{})'.format(item_file[5-1]) + '</span>'
            elif check_status[5 - 1] is False:
                Item05 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: red;">' + 'Item_05 RMS Evaluation' + '&nbsp;&nbsp;&nbsp;&nbsp; < Fail > [Detail](./{})'.format(item_file[5-1]) + '</span>'
            else:
                Item05 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: gray;">' + 'Item_05 RMS Evaluation' + '&nbsp;&nbsp;&nbsp;&nbsp; < No Test >' + '</span>'
            file.write(Item05 + '\n\n')

            if check_status[6-1] is True:
                Item06 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: green;">' + 'Item_06 Cali_1 configuration SE 200 mV' + '&nbsp;&nbsp;&nbsp;&nbsp; < Pass > [Detail](./{})'.format(item_file[6-1]) + '</span>'
            elif check_status[6 - 1] is False:
                Item06 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: red;">' + 'Item_06 Cali_1 configuration SE 200 mV' + '&nbsp;&nbsp;&nbsp;&nbsp; < Fail > [Detail](./{})'.format(item_file[6-1]) + '</span>'
            else:
                Item06 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: gray;">' + 'Item_06 Cali_1 configuration SE 200 mV' + '&nbsp;&nbsp;&nbsp;&nbsp; < No Test >' + '</span>'
            file.write(Item06 + '\n\n')

            if check_status[7-1] is True:
                Item07 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: green;">' + 'Item_07 Cali_2 configuration SE 900 mV' + '&nbsp;&nbsp;&nbsp;&nbsp; < Pass > [Detail](./{})'.format(item_file[7-1]) + '</span>'
            elif check_status[7 - 1] is False:
                Item07 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: red;">' + 'Item_07 Cali_2 configuration SE 900 mV' + '&nbsp;&nbsp;&nbsp;&nbsp; < Fail > [Detail](./{})'.format(item_file[7-1]) + '</span>'
            else:
                Item07 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: gray;">' + 'Item_07 Cali_2 configuration SE 900 mV' + '&nbsp;&nbsp;&nbsp;&nbsp; < No Test >' + '</span>'
            file.write(Item07 + '\n\n')

            if check_status[8-1] is True:
                Item08 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: green;">' + 'Item_08 Cali_3 SGP1 SE 200 mV' + '&nbsp;&nbsp;&nbsp;&nbsp; < Pass > [Detail](./{})'.format(item_file[8-1]) + '</span>'
            elif check_status[8 - 1] is False:
                Item08 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: red;">' + 'Item_08 Cali_3 SGP1 SE 200 mV' + '&nbsp;&nbsp;&nbsp;&nbsp; < Fail > [Detail](./{})'.format(item_file[8-1]) + '</span>'
            else:
                Item08 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: gray;">' + 'Item_08 Cali_3 SGP1 SE 200 mV' + '&nbsp;&nbsp;&nbsp;&nbsp; < No Test >' + '</span>'
            file.write(Item08 + '\n\n')

            if check_status[9-1] is True:
                Item09 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: green;">' + 'Item_09 Cali_4 SGP1 SE 900 mV' + '&nbsp;&nbsp;&nbsp;&nbsp; < Pass > [Detail](./{})'.format(item_file[9-1]) + '</span>'
            elif check_status[9 - 1] is False:
                Item09 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: red;">' + 'Item_09 Cali_4 SGP1 SE 900 mV' + '&nbsp;&nbsp;&nbsp;&nbsp; < Fail > [Detail](./{})'.format(item_file[9-1]) + '</span>'
            else:
                Item09 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: gray;">' + 'Item_09 Cali_4 SGP1 SE 900 mV' + '&nbsp;&nbsp;&nbsp;&nbsp; < No Test >' + '</span>'
            file.write(Item09 + '\n\n')

            if check_status[10-1] is True:
                Item10 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: green;">' + 'Item_10 FE Monitor' + '&nbsp;&nbsp;&nbsp;&nbsp; < Pass > [Detail](./{})'.format(item_file[10-1]) + '</span>'
            elif check_status[10 - 1] is False:
                Item10 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: red;">' + 'Item_10 FE Monitor' + '&nbsp;&nbsp;&nbsp;&nbsp; < Fail > [Detail](./{})'.format(item_file[10-1]) + '</span>'
            else:
                Item10 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: gray;">' + 'Item_10 FE Monitor' + '&nbsp;&nbsp;&nbsp;&nbsp; < No Test >' + '</span>'
            file.write(Item10 + '\n\n')

            if check_status[11-1] is True:
                Item11 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: green;">' + 'Item_11 FE DAC Linearity' + '&nbsp;&nbsp;&nbsp;&nbsp; < Pass > [Detail](./{})'.format(item_file[11-1]) + '</span>'
            elif check_status[11 - 1] is False:
                Item11 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: red;">' + 'Item_11 FE DAC Linearity' + '&nbsp;&nbsp;&nbsp;&nbsp; < Fail > [Detail](./{})'.format(item_file[11-1]) + '</span>'
            else:
                Item11 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: gray;">' + 'Item_11 FE DAC Linearity' + '&nbsp;&nbsp;&nbsp;&nbsp; < No Test >' + '</span>'
            file.write(Item11 + '\n\n')

            if check_status[12-1] is True:
                Item12 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: green;">' + 'Item_12 ColdADC ref_voltage Linearity' + '&nbsp;&nbsp;&nbsp;&nbsp; < Pass > [Detail](./{})'.format(item_file[12-1]) + '</span>'
            elif check_status[12 - 1] is False:
                Item12 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: red;">' + 'Item_12 ColdADC ref_voltage Linearity' + '&nbsp;&nbsp;&nbsp;&nbsp; < Fail > [Detail](./{})'.format(item_file[12-1]) + '</span>'
            else:
                Item12 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: gray;">' + 'Item_12 ColdADC ref_voltage Linearity' + '&nbsp;&nbsp;&nbsp;&nbsp; < No Test >' + '</span>'
            file.write(Item12 + '\n\n')

            if check_status[13-1] is True:
                Item13 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: green;">' + 'Item_13 External Pulse Calibration 900mV baseline' + '&nbsp;&nbsp;&nbsp;&nbsp; < Pass > [Detail](./{})'.format(item_file[13-1]) + '</span>'
            elif check_status[13 - 1] is False:
                Item13 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: red;">' + 'Item_13 External Pulse Calibration 900mV baseline' + '&nbsp;&nbsp;&nbsp;&nbsp; < Fail > [Detail](./{})'.format(item_file[13-1]) + '</span>'
            else:
                Item13 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: gray;">' + 'Item_13 External Pulse Calibration 900mV baseline' + '&nbsp;&nbsp;&nbsp;&nbsp; < No Test >' + '</span>'
            file.write(Item13 + '\n\n')

            if check_status[14-1] is True:
                Item14 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: green;">' + 'Item_14 External Pulse Calibration 200mV baseline' + '&nbsp;&nbsp;&nbsp;&nbsp; < Pass > [Detail](./{})'.format(item_file[14-1]) + '</span>'
            elif check_status[14 - 1] is False:
                Item14 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: red;">' + 'Item_14 External Pulse Calibration 200mV baseline' + '&nbsp;&nbsp;&nbsp;&nbsp; < Fail > [Detail](./{})'.format(item_file[14-1]) + '</span>'
            else:
                Item14 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: gray;">' + 'Item_14 External Pulse Calibration 200mV baseline' + '&nbsp;&nbsp;&nbsp;&nbsp; < No Test >' + '</span>'
            file.write(Item14 + '\n\n')

            if check_status[15-1] is True:
                Item15 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: green;">' + 'Item_15 ColdADC_sync_pat_report' + '&nbsp;&nbsp;&nbsp;&nbsp; < Pass > [Detail](./{})'.format(item_file[15-1]) + '</span>'
            elif check_status[15 - 1] is False:
                Item15 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: red;">' + 'Item_15 ColdADC_sync_pat_report' + '&nbsp;&nbsp;&nbsp;&nbsp; < Fail > [Detail](./{})'.format(item_file[15-1]) + '</span>'
            else:
                Item15 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: gray;">' + 'Item_15 ColdADC_sync_pat_report' + '&nbsp;&nbsp;&nbsp;&nbsp; < No Test >' + '</span>'
            file.write(Item15 + '\n\n')

            if check_status[16-1] is True:
                Item16 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: green;">' + 'Item_16 PLL_scan_report' + '&nbsp;&nbsp;&nbsp;&nbsp; < Pass > [Detail](./{})'.format(item_file[16-1]) + '</span>'
            elif check_status[16 - 1] is False:
                Item16 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: red;">' + 'Item_16 PLL_scan_report' + '&nbsp;&nbsp;&nbsp;&nbsp; < Fail > [Detail](./{})'.format(item_file[16-1]) + '</span>'
            else:
                Item16 = '&nbsp;&nbsp;&nbsp;&nbsp; <span style="color: gray;">' + 'Item_16 PLL_scan_report' + '&nbsp;&nbsp;&nbsp;&nbsp; < No Test >' + '</span>'
            file.write(Item16 + '\n\n')

            file.write("------\n")

            if check_status[1-1] is not None:
                file.write('<img src="./PWR_Meas/Power_Total.png" alt="picture" height="250">' + "\n\n")  # width="200"
            if check_status[6-1] is not None:
                file.write('<img src="./CALI1_DIFF/SE_Gain.png" alt="picture" height="250">' + "\n\n")  # width="200"
                file.write('<img src="./CALI1_DIFF/SE_ENC.png" alt="picture" height="250">' + "\n\n")  # width="200"
            if check_status[11-1] is not None:
                file.write('<img src="./MON_FE/mon_LArASIC_DAC_25mVfC.png" alt="picture" height="250">' + "\n\n")  # width="200"

            file.write("------\n")
'''