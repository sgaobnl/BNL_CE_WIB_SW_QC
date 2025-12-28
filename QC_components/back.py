import os
import pickle
import csv
import QC_components.qc_log as log
import re
import QC_components.csv_style as csv_style


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
        fpmd = datareport[ifemb] + 'report_FEMB_{}_slot{}.csv'.format(fembNo['femb%d' % ifemb], ifemb)
        print(datareport[ifemb])
        file_path = fpmd
        line_number = 1;        data = ['RTS_Time', '']
        csv_style.write_to_csv_line(file_path, line_number, data)
        line_number = 2;        data = ['Test_Site', '']
        csv_style.write_to_csv_line(file_path, line_number, data)
        line_number = 3;        data = ['CTS_ID', '1']
        csv_style.write_to_csv_line(file_path, line_number, data)
        line_number = 4;        data = ['Tester', '']
        csv_style.write_to_csv_line(file_path, line_number, data)
        line_number = 5;        data = ['Environment', '']
        csv_style.write_to_csv_line(file_path, line_number, data)
        line_number = 6;        data = ['Toy_TPC', '']
        csv_style.write_to_csv_line(file_path, line_number, data)
        line_number = 7;        data = ['SLOT0_FEMBID', '']
        csv_style.write_to_csv_line(file_path, line_number, data)
        line_number = 8;        data = ['SLOT1_FEMBID', '']
        csv_style.write_to_csv_line(file_path, line_number, data)
        line_number = 9;        data = ['SLOT2_FEMBID', '']
        csv_style.write_to_csv_line(file_path, line_number, data)
        line_number = 10;        data = ['SLOT3_FEMBID', '']
        csv_style.write_to_csv_line(file_path, line_number, data)

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
# line01
# file_path='./example.csv'
# line_number = 1; data = ['RTS_Time', '']
# csv_style.write_to_csv_line(file_path, line_number, data)
# line_number = 2; data = ['Test_Site', '']
# csv_style.write_to_csv_line(file_path, line_number, data)
# line_number = 3; data = ['CTS_ID', '1']
# csv_style.write_to_csv_line(file_path, line_number, data)
# line_number = 4; data = ['Tester', '']
# csv_style.write_to_csv_line(file_path, line_number, data)
# line_number = 5; data = ['Environment', '']
# csv_style.write_to_csv_line(file_path, line_number, data)
# line_number = 6; data = ['Toy_TPC', '']
# csv_style.write_to_csv_line(file_path, line_number, data)
# line_number = 7; data = ['SLOT0_FEMBID', '']
# csv_style.write_to_csv_line(file_path, line_number, data)
# line_number = 8; data = ['SLOT1_FEMBID', '']
# csv_style.write_to_csv_line(file_path, line_number, data)
# line_number = 9; data = ['SLOT2_FEMBID', '']
# csv_style.write_to_csv_line(file_path, line_number, data)
# line_number = 10; data = ['SLOT3_FEMBID', '']
# csv_style.write_to_csv_line(file_path, line_number, data)
# input()