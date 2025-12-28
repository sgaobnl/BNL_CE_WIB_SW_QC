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
        print(ifemb)
        print(femb_id)
        fpmd = datareport[ifemb] + 'report_FEMB_{}_slot{}.csv'.format(fembNo['femb%d' % ifemb], ifemb)
        info = log.report_log00
        # initial part
        file_path = fpmd
        line_number = 1;        data = ['CTS_Time', info['date']]
        csv_style.write_to_csv_line(file_path, line_number, data)
        line_number = 2;        data = ['Test_Site', 'BNL']
        csv_style.write_to_csv_line(file_path, line_number, data)
        line_number = 3;        data = ['CTS_ID', '1']
        csv_style.write_to_csv_line(file_path, line_number, data)
        line_number = 4;        data = ['Tester', info['tester'].replace('\r','')]
        csv_style.write_to_csv_line(file_path, line_number, data)
        line_number = 5;        data = ['Environment', info['env']]
        csv_style.write_to_csv_line(file_path, line_number, data)
        line_number = 6;        data = ['Toy_TPC', info['toytpc']]
        csv_style.write_to_csv_line(file_path, line_number, data)
        line_number = 7;        data = ['SLOT{}_FEMBID'.format(ifemb), info['femb id']['femb{}'.format(ifemb)]]
        csv_style.write_to_csv_line(file_path, line_number, data)
        if 1 in log.test_label:
            print(log.report_log01_11[femb_id])
        # Item#01 Power Consumption
            line_number = 8;        data = ['QC_01_01_Power_Consumption', 'Signal-End-OFF', 'BIAS_Voltage={}'.format(log.check_log01_11[femb_id]['BIAS_V']), 'BIAS_Current={}'.format(log.check_log01_11[femb_id]['BIAS_I']), 'BIAS_Power={}'.format(log.check_log01_11[femb_id]['bias_p']), 'LArASIC_Voltage={}'.format(log.check_log01_11[femb_id]['LArASIC_V']), 'LArASIC_Current={}'.format(log.check_log01_11[femb_id]['LArASIC_I']), 'LArASIC_Power={}'.format(log.check_log01_11[femb_id]['LArASIC_p']), 'ColdADC_Voltage={}'.format(log.check_log01_11[femb_id]['ColdADC_V']), 'ColdADC_Current={}'.format(log.check_log01_11[femb_id]['ColdADC_I']), 'ColdADC_Power={}'.format(log.check_log01_11[femb_id]['ColdADC_p']), 'COLDATA_Voltage={}'.format(log.check_log01_11[femb_id]['COLDATA_V']), 'COLDATA_Current={}'.format(log.check_log01_11[femb_id]['COLDATA_I']), 'COLDATA_Power={}'.format(log.check_log01_11[femb_id]['COLDATA_p']), 'Total_Power={}'.format(log.check_log01_11[femb_id]['TPower'])]
            csv_style.write_to_csv_line(file_path, line_number, data)
            line_number = 9;        data = ['QC_01_02_Power_Consumption', 'Signal-End-ON', 'BIAS_Voltage={}'.format(log.check_log01_21[femb_id]['BIAS_V']), 'BIAS_Current={}'.format(log.check_log01_21[femb_id]['BIAS_I']), 'BIAS_Power={}'.format(log.check_log01_21[femb_id]['bias_p']), 'LArASIC_Voltage={}'.format(log.check_log01_21[femb_id]['LArASIC_V']), 'LArASIC_Current={}'.format(log.check_log01_21[femb_id]['LArASIC_I']), 'LArASIC_Power={}'.format(log.check_log01_21[femb_id]['LArASIC_p']), 'ColdADC_Voltage={}'.format(log.check_log01_21[femb_id]['ColdADC_V']), 'ColdADC_Current={}'.format(log.check_log01_21[femb_id]['ColdADC_I']), 'ColdADC_Power={}'.format(log.check_log01_21[femb_id]['ColdADC_p']), 'COLDATA_Voltage={}'.format(log.check_log01_21[femb_id]['COLDATA_V']), 'COLDATA_Current={}'.format(log.check_log01_21[femb_id]['COLDATA_I']), 'COLDATA_Power={}'.format(log.check_log01_21[femb_id]['COLDATA_p']), 'Total_Power={}'.format(log.check_log01_21[femb_id]['TPower'])]
            csv_style.write_to_csv_line(file_path, line_number, data)
            line_number = 10;        data = ['QC_01_03_Power_Consumption', 'DIFF-Interface', 'BIAS_Voltage={}'.format(log.check_log01_31[femb_id]['BIAS_V']), 'BIAS_Current={}'.format(log.check_log01_31[femb_id]['BIAS_I']), 'BIAS_Power={}'.format(log.check_log01_31[femb_id]['bias_p']), 'LArASIC_Voltage={}'.format(log.check_log01_31[femb_id]['LArASIC_V']), 'LArASIC_Current={}'.format(log.check_log01_31[femb_id]['LArASIC_I']), 'LArASIC_Power={}'.format(log.check_log01_31[femb_id]['LArASIC_p']), 'ColdADC_Voltage={}'.format(log.check_log01_31[femb_id]['ColdADC_V']), 'ColdADC_Current={}'.format(log.check_log01_31[femb_id]['ColdADC_I']), 'ColdADC_Power={}'.format(log.check_log01_31[femb_id]['ColdADC_p']), 'COLDATA_Voltage={}'.format(log.check_log01_31[femb_id]['COLDATA_V']), 'COLDATA_Current={}'.format(log.check_log01_31[femb_id]['COLDATA_I']), 'COLDATA_Power={}'.format(log.check_log01_31[femb_id]['COLDATA_p']), 'Total_Power={}'.format(log.check_log01_31[femb_id]['TPower'])]
            csv_style.write_to_csv_line(file_path, line_number, data)

            line_number = 11;        data = ['QC_01_04_Power_LDO_output', 'Signal-End-OFF', 'CDVDDA={}'.format(log.report_log01_13[femb_id]['CDVDDA']), 'CDVDDIO={}'.format(log.report_log01_13[femb_id]['CDVDDIO']), 'ADCRVDDD1P2={}'.format(log.report_log01_13[femb_id]['ADCRVDDD1P2']), 'ADCLVDDD1P2={}'.format(log.report_log01_13[femb_id]['ADCLVDDD1P2']), 'ADCRP25V={}'.format(log.report_log01_13[femb_id]['ADCRP25V']), 'ADCLP25V={}'.format(log.report_log01_13[femb_id]['ADCLP25V']), 'FERVDDP={}'.format(log.report_log01_13[femb_id]['FERVDDP']), 'FELVDDP={}'.format(log.report_log01_13[femb_id]['FELVDDP']), 'GND={}'.format(log.report_log01_13[femb_id]['GND'])]
            csv_style.write_to_csv_line(file_path, line_number, data)
            line_number = 12;        data = ['QC_01_05_Power_LDO_output', 'Signal-End-ON', 'CDVDDA={}'.format(log.report_log01_23[femb_id]['CDVDDA']), 'CDVDDIO={}'.format(log.report_log01_23[femb_id]['CDVDDIO']), 'ADCRVDDD1P2={}'.format(log.report_log01_23[femb_id]['ADCRVDDD1P2']), 'ADCLVDDD1P2={}'.format(log.report_log01_23[femb_id]['ADCLVDDD1P2']), 'ADCRP25V={}'.format(log.report_log01_23[femb_id]['ADCRP25V']), 'ADCLP25V={}'.format(log.report_log01_23[femb_id]['ADCLP25V']), 'FERVDDP={}'.format(log.report_log01_23[femb_id]['FERVDDP']), 'FELVDDP={}'.format(log.report_log01_23[femb_id]['FELVDDP']), 'GND={}'.format(log.report_log01_13[femb_id]['GND'])]
            csv_style.write_to_csv_line(file_path, line_number, data)
            line_number = 13;        data = ['QC_01_06_Power_LDO_output', 'DIFF-Interface', 'CDVDDA={}'.format(log.report_log01_33[femb_id]['CDVDDA']), 'CDVDDIO={}'.format(log.report_log01_33[femb_id]['CDVDDIO']), 'ADCRVDDD1P2={}'.format(log.report_log01_33[femb_id]['ADCRVDDD1P2']), 'ADCLVDDD1P2={}'.format(log.report_log01_33[femb_id]['ADCLVDDD1P2']), 'ADCRP25V={}'.format(log.report_log01_33[femb_id]['ADCRP25V']), 'ADCLP25V={}'.format(log.report_log01_33[femb_id]['ADCLP25V']), 'FERVDDP={}'.format(log.report_log01_33[femb_id]['FERVDDP']), 'FELVDDP={}'.format(log.report_log01_33[femb_id]['FELVDDP']), 'GND={}'.format(log.report_log01_33[femb_id]['GND'])]
            csv_style.write_to_csv_line(file_path, line_number, data)

            line_number = 14;        data = ['QC_01_07_01_Power_GeneralPulseChk_output', 'Signal-End-OFF_DAC0x10', 'Positive Peak Mean', '{}'.format(log.check_log01_12[femb_id]['ppk_mean']), '5-sigma-STD', '{}'.format(5*log.check_log01_12[femb_id]['ppk_std']), 'MAX', '{}'.format(log.check_log01_12[femb_id]['ppk_max']), 'MIN', '{}'.format(log.check_log01_12[femb_id]['ppk_min']), '128-Ch Distribution'] + log.check_log01_12[femb_id]['ppk']
            csv_style.write_to_csv_line(file_path, line_number, data)
            line_number = 15;        data = ['QC_01_07_02_Power_GeneralPulseChk_output', 'Signal-End-OFF_DAC0x10', 'Baseline Mean', '{}'.format(log.report_log01_12[femb_id]['bbl_mean']), '5-sigma-STD', '{}'.format(5*log.check_log01_12[femb_id]['bbl_std']), 'MAX', '{}'.format(log.check_log01_12[femb_id]['bbl_max']), 'MIN', '{}'.format(log.check_log01_12[femb_id]['bbl_min']), '128-Ch Distribution'] + log.check_log01_12[femb_id]['bbl']
            csv_style.write_to_csv_line(file_path, line_number, data)
            line_number = 16;        data = ['QC_01_07_02_Power_GeneralPulseChk_output', 'Signal-End-OFF_DAC0x10', 'Negative Peak Mean', '{}'.format(log.report_log01_12[femb_id]['npk_mean']), '5-sigma-STD', '{}'.format(5*log.check_log01_12[femb_id]['npk_std']), 'MAX', '{}'.format(log.check_log01_12[femb_id]['npk_max']), 'MIN', '{}'.format(log.check_log01_12[femb_id]['npk_min']), '128-Ch Distribution'] + log.check_log01_12[femb_id]['npk']
            csv_style.write_to_csv_line(file_path, line_number, data)

            line_number = 17;        data = ['QC_01_08_01_Power_GeneralPulseChk_output', 'Signal-End-ON_DAC0x10', 'Positive Peak Mean', '{}'.format(log.check_log01_22[femb_id]['ppk_mean']), '5-sigma-STD', '{}'.format(5*log.check_log01_22[femb_id]['ppk_std']), 'MAX', '{}'.format(log.check_log01_22[femb_id]['ppk_max']), 'MIN', '{}'.format(log.check_log01_22[femb_id]['ppk_min']), '128-Ch Distribution']+log.check_log01_22[femb_id]['ppk']
            csv_style.write_to_csv_line(file_path, line_number, data)
            line_number = 18;        data = ['QC_01_08_02_Power_GeneralPulseChk_output', 'Signal-End-ON_DAC0x10', 'Baseline Mean', '{}'.format(log.check_log01_22[femb_id]['bbl_mean']), '5-sigma-STD', '{}'.format(5*log.check_log01_22[femb_id]['bbl_std']), 'MAX', '{}'.format(log.check_log01_22[femb_id]['bbl_max']), 'MIN', '{}'.format(log.check_log01_22[femb_id]['bbl_min']), '128-Ch Distribution']+log.check_log01_22[femb_id]['bbl']
            csv_style.write_to_csv_line(file_path, line_number, data)
            line_number = 19;        data = ['QC_01_08_03_Power_GeneralPulseChk_output', 'Signal-End-ON_DAC0x10', 'Negative Peak Mean', '{}'.format(log.check_log01_22[femb_id]['npk_mean']), '5-sigma-STD', '{}'.format(5*log.check_log01_22[femb_id]['npk_std']), 'MAX', '{}'.format(log.check_log01_22[femb_id]['npk_max']), 'MIN', '{}'.format(log.check_log01_22[femb_id]['npk_min']), '128-Ch Distribution']+log.check_log01_22[femb_id]['npk']
            csv_style.write_to_csv_line(file_path, line_number, data)

            line_number = 20;        data = ['QC_01_09_01_Power_GeneralPulseChk_output', 'DIFF_DAC0x10', 'Positive Peak Mean', '{}'.format(log.check_log01_32[femb_id]['ppk_mean']), '5-sigma-STD', '{}'.format(5*log.check_log01_32[femb_id]['ppk_std']), 'MAX', '{}'.format(log.check_log01_32[femb_id]['ppk_max']), 'MIN', '{}'.format(log.check_log01_32[femb_id]['ppk_min']), '128-Ch Distribution'] + log.check_log01_32[femb_id]['ppk']
            csv_style.write_to_csv_line(file_path, line_number, data)
            line_number = 21;        data = ['QC_01_09_02_Power_GeneralPulseChk_output', 'DIFF_DAC0x10', 'Baseline Mean', '{}'.format(log.check_log01_32[femb_id]['bbl_mean']), '5-sigma-STD', '{}'.format(5*log.check_log01_32[femb_id]['bbl_std']), 'MAX', '{}'.format(log.check_log01_32[femb_id]['bbl_max']), 'MIN', '{}'.format(log.check_log01_32[femb_id]['bbl_min']), '128-Ch Distribution'] + log.check_log01_32[femb_id]['bbl']
            csv_style.write_to_csv_line(file_path, line_number, data)
            line_number = 22;        data = ['QC_01_09_03_Power_GeneralPulseChk_output', 'DIFF_DAC0x10', 'Negative Peak Mean', '{}'.format(log.check_log01_32[femb_id]['npk_mean']), '5-sigma-STD', '{}'.format(5*log.check_log01_32[femb_id]['npk_std']), 'MAX', '{}'.format(log.check_log01_32[femb_id]['npk_max']), 'MIN', '{}'.format(log.check_log01_32[femb_id]['npk_min']), '128-Ch Distribution'] + log.check_log01_32[femb_id]['npk']
            csv_style.write_to_csv_line(file_path, line_number, data)

        if 2 in log.test_label:
            line_number = 23;
            data = ['QC_02_01_Power_Cycle', 'Signal-End-OFF', 'BIAS_Voltage={}'.format(log.check_log02_01[femb_id]['BIAS_V']), 'BIAS_Current={}'.format(log.check_log02_01[femb_id]['BIAS_I']), 'BIAS_Power={}'.format(log.check_log02_01[femb_id]['bias_p']), 'LArASIC_Voltage={}'.format(log.check_log02_01[femb_id]['LArASIC_V']), 'LArASIC_Current={}'.format(log.check_log02_01[femb_id]['LArASIC_I']), 'LArASIC_Power={}'.format(log.check_log02_01[femb_id]['LArASIC_p']),
                    'ColdADC_Voltage={}'.format(log.check_log02_01[femb_id]['ColdADC_V']), 'ColdADC_Current={}'.format(log.check_log02_01[femb_id]['ColdADC_I']), 'ColdADC_Power={}'.format(log.check_log02_01[femb_id]['ColdADC_p']), 'COLDATA_Voltage={}'.format(log.check_log02_01[femb_id]['COLDATA_V']), 'COLDATA_Current={}'.format(log.check_log02_01[femb_id]['COLDATA_I']), 'COLDATA_Power={}'.format(log.check_log02_01[femb_id]['COLDATA_p']),
                    'Total_Power={}'.format(log.check_log02_01[femb_id]['TPower'])]
            csv_style.write_to_csv_line(file_path, line_number, data)
            line_number = 24;
            data = ['QC_02_03_Power_Cycle', 'Signal-End-OFF', 'BIAS_Voltage={}'.format(log.check_log02_02[femb_id]['BIAS_V']), 'BIAS_Current={}'.format(log.check_log02_02[femb_id]['BIAS_I']), 'BIAS_Power={}'.format(log.check_log02_02[femb_id]['bias_p']), 'LArASIC_Voltage={}'.format(log.check_log02_02[femb_id]['LArASIC_V']), 'LArASIC_Current={}'.format(log.check_log02_02[femb_id]['LArASIC_I']), 'LArASIC_Power={}'.format(log.check_log02_02[femb_id]['LArASIC_p']),
                    'ColdADC_Voltage={}'.format(log.check_log02_02[femb_id]['ColdADC_V']), 'ColdADC_Current={}'.format(log.check_log02_02[femb_id]['ColdADC_I']), 'ColdADC_Power={}'.format(log.check_log02_02[femb_id]['ColdADC_p']), 'COLDATA_Voltage={}'.format(log.check_log02_02[femb_id]['COLDATA_V']), 'COLDATA_Current={}'.format(log.check_log02_02[femb_id]['COLDATA_I']), 'COLDATA_Power={}'.format(log.check_log02_02[femb_id]['COLDATA_p']),
                    'Total_Power={}'.format(log.check_log02_02[femb_id]['TPower'])]
            csv_style.write_to_csv_line(file_path, line_number, data)
            line_number = 25;
            data = ['QC_02_03_Power_Cycle', 'Signal-End-OFF', 'BIAS_Voltage={}'.format(log.check_log02_03[femb_id]['BIAS_V']), 'BIAS_Current={}'.format(log.check_log02_03[femb_id]['BIAS_I']), 'BIAS_Power={}'.format(log.check_log02_03[femb_id]['bias_p']), 'LArASIC_Voltage={}'.format(log.check_log02_03[femb_id]['LArASIC_V']), 'LArASIC_Current={}'.format(log.check_log02_03[femb_id]['LArASIC_I']), 'LArASIC_Power={}'.format(log.check_log02_03[femb_id]['LArASIC_p']),
                    'ColdADC_Voltage={}'.format(log.check_log02_03[femb_id]['ColdADC_V']), 'ColdADC_Current={}'.format(log.check_log02_03[femb_id]['ColdADC_I']), 'ColdADC_Power={}'.format(log.check_log02_03[femb_id]['ColdADC_p']), 'COLDATA_Voltage={}'.format(log.check_log02_03[femb_id]['COLDATA_V']), 'COLDATA_Current={}'.format(log.check_log02_03[femb_id]['COLDATA_I']), 'COLDATA_Power={}'.format(log.check_log02_03[femb_id]['COLDATA_p']),
                    'Total_Power={}'.format(log.check_log02_03[femb_id]['TPower'])]
            csv_style.write_to_csv_line(file_path, line_number, data)
            line_number = 26;
            data = ['QC_02_04_Power_Cycle', 'DIFF-Interface', 'BIAS_Voltage={}'.format(log.check_log02_04[femb_id]['BIAS_V']), 'BIAS_Current={}'.format(log.check_log02_04[femb_id]['BIAS_I']), 'BIAS_Power={}'.format(log.check_log02_04[femb_id]['bias_p']), 'LArASIC_Voltage={}'.format(log.check_log02_04[femb_id]['LArASIC_V']), 'LArASIC_Current={}'.format(log.check_log02_04[femb_id]['LArASIC_I']), 'LArASIC_Power={}'.format(log.check_log02_04[femb_id]['LArASIC_p']),
                    'ColdADC_Voltage={}'.format(log.check_log02_04[femb_id]['ColdADC_V']), 'ColdADC_Current={}'.format(log.check_log02_04[femb_id]['ColdADC_I']), 'ColdADC_Power={}'.format(log.check_log02_04[femb_id]['ColdADC_p']), 'COLDATA_Voltage={}'.format(log.check_log02_04[femb_id]['COLDATA_V']), 'COLDATA_Current={}'.format(log.check_log02_04[femb_id]['COLDATA_I']), 'COLDATA_Power={}'.format(log.check_log02_04[femb_id]['COLDATA_p']),
                    'Total_Power={}'.format(log.check_log02_04[femb_id]['TPower'])]
            csv_style.write_to_csv_line(file_path, line_number, data)
            line_number = 27;
            data = ['QC_02_05_Power_Cycle', 'SDF', 'BIAS_Voltage={}'.format(log.check_log02_05[femb_id]['BIAS_V']), 'BIAS_Current={}'.format(log.check_log02_05[femb_id]['BIAS_I']), 'BIAS_Power={}'.format(log.check_log02_05[femb_id]['bias_p']), 'LArASIC_Voltage={}'.format(log.check_log02_05[femb_id]['LArASIC_V']), 'LArASIC_Current={}'.format(log.check_log02_05[femb_id]['LArASIC_I']), 'LArASIC_Power={}'.format(log.check_log02_05[femb_id]['LArASIC_p']),
                    'ColdADC_Voltage={}'.format(log.check_log02_05[femb_id]['ColdADC_V']), 'ColdADC_Current={}'.format(log.check_log02_05[femb_id]['ColdADC_I']), 'ColdADC_Power={}'.format(log.check_log02_05[femb_id]['ColdADC_p']), 'COLDATA_Voltage={}'.format(log.check_log02_05[femb_id]['COLDATA_V']), 'COLDATA_Current={}'.format(log.check_log02_05[femb_id]['COLDATA_I']), 'COLDATA_Power={}'.format(log.check_log02_05[femb_id]['COLDATA_p']),
                    'Total_Power={}'.format(log.check_log02_05[femb_id]['TPower'])]
            csv_style.write_to_csv_line(file_path, line_number, data)

        if 3 in log.test_label:
            line_number = 28;
            data = ['QC_03_01_01_Leakage_Current', '100pA_SEOFF_200mVBL_14_0mVfC_2_0us_0x20', 'Positive Peak Mean', '{}'.format(log.check_log03_02[femb_id]['ppk_mean']), '5-sigma-STD', '{}'.format(5*log.check_log03_02[femb_id]['ppk_std']), 'MAX', '{}'.format(log.check_log03_02[femb_id]['ppk_max']), 'MIN', '{}'.format(log.check_log03_02[femb_id]['ppk_min']), '128-Ch Distribution'] + log.check_log03_02[femb_id]['ppk']
            csv_style.write_to_csv_line(file_path, line_number, data)
            line_number = 29;
            data = ['QC_03_01_02_Leakage_Current', '100pA_SEOFF_200mVBL_14_0mVfC_2_0us_0x20', 'Baseline Mean', '{}'.format(log.check_log03_02[femb_id]['bbl_mean']), '5-sigma-STD', '{}'.format(5*log.check_log03_02[femb_id]['bbl_std']), 'MAX', '{}'.format(log.check_log03_02[femb_id]['bbl_max']), 'MIN', '{}'.format(log.check_log03_02[femb_id]['bbl_min']), '128-Ch Distribution'] + log.check_log03_02[femb_id]['bbl']
            csv_style.write_to_csv_line(file_path, line_number, data)
            line_number = 30;
            data = ['QC_03_01_03_Leakage_Current', '100pA_SEOFF_200mVBL_14_0mVfC_2_0us_0x20', 'Negative Peak Mean', '{}'.format(log.check_log03_02[femb_id]['npk_mean']), '5-sigma-STD', '{}'.format(5*log.check_log03_02[femb_id]['npk_std']), 'MAX', '{}'.format(log.check_log03_02[femb_id]['npk_max']), 'MIN', '{}'.format(log.check_log03_02[femb_id]['npk_min']), '128-Ch Distribution'] + log.check_log03_02[femb_id]['npk']
            csv_style.write_to_csv_line(file_path, line_number, data)

            line_number = 31;
            data = ['QC_03_02_01_Leakage_Current', '500pA_SEOFF_200mVBL_14_0mVfC_2_0us_0x20', 'Positive Peak Mean', '{}'.format(log.check_log03_01[femb_id]['ppk_mean']), '5-sigma-STD', '{}'.format(5*log.check_log03_01[femb_id]['ppk_std']), 'MAX', '{}'.format(log.check_log03_01[femb_id]['ppk_max']), 'MIN', '{}'.format(log.check_log03_01[femb_id]['ppk_min']), '128-Ch Distribution'] + log.check_log03_01[femb_id]['ppk']
            csv_style.write_to_csv_line(file_path, line_number, data)
            line_number = 32;
            data = ['QC_03_02_02_Leakage_Current', '500pA_SEOFF_200mVBL_14_0mVfC_2_0us_0x20', 'Baseline Mean', '{}'.format(log.check_log03_01[femb_id]['bbl_mean']), '5-sigma-STD', '{}'.format(5*log.check_log03_01[femb_id]['bbl_std']), 'MAX', '{}'.format(log.check_log03_01[femb_id]['bbl_max']), 'MIN', '{}'.format(log.check_log03_01[femb_id]['bbl_min']), '128-Ch Distribution'] + log.check_log03_01[femb_id]['bbl']
            csv_style.write_to_csv_line(file_path, line_number, data)
            line_number = 33;
            data = ['QC_03_02_03_Leakage_Current', '500pA_SEOFF_200mVBL_14_0mVfC_2_0us_0x20', 'Negative Peak Mean', '{}'.format(log.check_log03_01[femb_id]['npk_mean']), '5-sigma-STD', '{}'.format(5*log.check_log03_01[femb_id]['npk_std']), 'MAX', '{}'.format(log.check_log03_01[femb_id]['npk_max']), 'MIN', '{}'.format(log.check_log03_01[femb_id]['npk_min']), '128-Ch Distribution'] + log.check_log03_01[femb_id]['npk']
            csv_style.write_to_csv_line(file_path, line_number, data)

            line_number = 34;
            data = ['QC_03_03_01_Leakage_Current', '1nA_SEOFF_200mVBL_14_0mVfC_2_0us_0x20', 'Positive Peak Mean', '{}'.format(log.check_log03_04[femb_id]['ppk_mean']), '5-sigma-STD', '{}'.format(5*log.check_log03_04[femb_id]['ppk_std']), 'MAX', '{}'.format(log.check_log03_04[femb_id]['ppk_max']), 'MIN', '{}'.format(log.check_log03_04[femb_id]['ppk_min']), '128-Ch Distribution'] + log.check_log03_04[femb_id]['ppk']
            csv_style.write_to_csv_line(file_path, line_number, data)
            line_number = 35;
            data = ['QC_03_03_02_Leakage_Current', '1nA_SEOFF_200mVBL_14_0mVfC_2_0us_0x20', 'Baseline Mean', '{}'.format(log.check_log03_04[femb_id]['bbl_mean']), '5-sigma-STD', '{}'.format(5*log.check_log03_04[femb_id]['bbl_std']), 'MAX', '{}'.format(log.check_log03_04[femb_id]['bbl_max']), 'MIN', '{}'.format(log.check_log03_04[femb_id]['bbl_min']), '128-Ch Distribution'] + log.check_log03_04[femb_id]['bbl']
            csv_style.write_to_csv_line(file_path, line_number, data)
            line_number = 36;
            data = ['QC_03_03_03_Leakage_Current', '1nA_SEOFF_200mVBL_14_0mVfC_2_0us_0x20', 'Negative Peak Mean', '{}'.format(log.check_log03_04[femb_id]['npk_mean']), '5-sigma-STD', '{}'.format(5*log.check_log03_04[femb_id]['npk_std']), 'MAX', '{}'.format(log.check_log03_04[femb_id]['npk_max']), 'MIN', '{}'.format(log.check_log03_04[femb_id]['npk_min']), '128-Ch Distribution'] + log.check_log03_04[femb_id]['npk']
            csv_style.write_to_csv_line(file_path, line_number, data)

            line_number = 37;
            data = ['QC_03_04_01_Leakage_Current', '5nA_SEOFF_200mVBL_14_0mVfC_2_0us_0x20', 'Positive Peak Mean', '{}'.format(log.check_log03_03[femb_id]['ppk_mean']), '5-sigma-STD', '{}'.format(5*log.check_log03_03[femb_id]['ppk_std']), 'MAX', '{}'.format(log.check_log03_03[femb_id]['ppk_max']), 'MIN', '{}'.format(log.check_log03_03[femb_id]['ppk_min']), '128-Ch Distribution'] + log.check_log03_03[femb_id]['ppk']
            csv_style.write_to_csv_line(file_path, line_number, data)
            line_number = 38;
            data = ['QC_03_04_02_Leakage_Current', '5nA_SEOFF_200mVBL_14_0mVfC_2_0us_0x20', 'Baseline Mean', '{}'.format(log.check_log03_03[femb_id]['bbl_mean']), '5-sigma-STD', '{}'.format(5*log.check_log03_03[femb_id]['bbl_std']), 'MAX', '{}'.format(log.check_log03_03[femb_id]['bbl_max']), 'MIN', '{}'.format(log.check_log03_03[femb_id]['bbl_min']), '128-Ch Distribution'] + log.check_log03_03[femb_id]['bbl']
            csv_style.write_to_csv_line(file_path, line_number, data)
            line_number = 39;
            data = ['QC_03_04_03_Leakage_Current', '5nA_SEOFF_200mVBL_14_0mVfC_2_0us_0x20', 'Negative Peak Mean', '{}'.format(log.check_log03_03[femb_id]['npk_mean']), '5-sigma-STD', '{}'.format(5*log.check_log03_03[femb_id]['npk_std']), 'MAX', '{}'.format(log.check_log03_03[femb_id]['npk_max']), 'MIN', '{}'.format(log.check_log03_03[femb_id]['npk_min']), '128-Ch Distribution'] + log.check_log03_03[femb_id]['npk']
            csv_style.write_to_csv_line(file_path, line_number, data)



        # Item#01 Power Consumption
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