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


# write pulse response parameter
def write_pulse_to_csv(line1, line2, line3, file_path, test, configuration, data_dict, femb_id):
    """
    Writes multiple QC-related data entries to a CSV file with user-defined line numbers and incrementing test names.

    Parameters:
    - file_path: Path to the CSV file
    - test: Base test name (e.g., 'QC_03_03_Leakage_Current')
    - configuration: Configuration string
    - data_dict: Dictionary containing QC data
    - femb_id: Identifier for the FEMB being tested
    - line1, line2, line3: Custom line numbers for writing each entry
    """

    entries = [
        (line1, f"{test}_01", 'Positive Peak Mean', 'ppk'),
        (line2, f"{test}_02", 'Baseline Mean', 'bbl'),
        (line3, f"{test}_03", 'Negative Peak Mean', 'npk')
    ]

    for line, test_variant, label, key in entries:
        data = [
                   test_variant,  # Incrementing test name
                   configuration,
                   label, '{}'.format(data_dict[femb_id][f"{key}_mean"]),
                   '5-sigma-STD', '{}'.format(5 * data_dict[femb_id][f"{key}_std"]),
                   'MAX', '{}'.format(data_dict[femb_id][f"{key}_max"]),
                   'MIN', '{}'.format(data_dict[femb_id][f"{key}_min"]),
                   '128-Ch Distribution'
               ] + data_dict[femb_id][key]

        csv_style.write_to_csv_line(file_path, line, data)

def write_bandgap_to_csv(line, file_path, test, fname, ifemb):
    """
    Writes QC Bandgap RMS data to a CSV file.

    Parameters:
    - file_path: Path to the CSV file
    - line: Line number where the data should be written
    - test: Test name (e.g., 'QC_05_01_Bandgap_RMS')
    - configuration: Configuration string (e.g., '1nA_SEOFF_200mVBL_14_0mVfC_2_0us_0x20')
    - fname: Key used to access specific data (e.g., 'SE_900mVBL_14_0mVfC_1_0us')
    - ifemb: Identifier for the FEMB being tested
    """

    # Directly access the predefined dictionaries
    mean_data = log.report_log057_fembrmsmean[ifemb][fname]
    std_data = log.report_log057_fembrmsstd[ifemb][fname]
    max_data = log.report_log057_fembrmsmax[ifemb][fname]
    min_data = log.report_log057_fembrmsmin[ifemb][fname]
    rms_data = log.report_log053_rms[ifemb][fname]  # 128-Ch Distribution

    # Format the data for CSV writing
    data = [
        test,
        '{}_DAC0x10'.format(fname),
        'Positive Peak Mean', str(mean_data),
        '5-sigma-STD', str(5 * std_data),
        'MAX', str(max_data),
        'MIN', str(min_data),
        '128-Ch Distribution'
    ] + rms_data  # Append the 128-Ch Distribution list

    # Write to CSV
    csv_style.write_to_csv_line(file_path, line, data)




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

            write_pulse_to_csv(14, 15, 16, file_path, 'QC_01_07_Power_GeneralPulseChk_output', 'Signal-End-OFF_DAC0x10', log.check_log01_12, femb_id)
            write_pulse_to_csv(17, 18, 19, file_path, 'QC_01_08_Power_GeneralPulseChk_output', 'Signal-End-ON_DAC0x10', log.check_log01_22, femb_id)
            write_pulse_to_csv(20, 21, 22, file_path, 'QC_01_09_Power_GeneralPulseChk_output', 'DIFF_DAC0x10', log.check_log01_32, femb_id)

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
            write_pulse_to_csv(28, 29, 30, file_path, 'QC_03_01_Leakage_Current', '100pA_SEOFF_200mVBL_14_0mVfC_2_0us_DAC0x20', log.check_log03_02, femb_id)
            write_pulse_to_csv(31, 32, 33, file_path, 'QC_03_02_Leakage_Current', '500pA_SEOFF_200mVBL_14_0mVfC_2_0us_DAC0x20', log.check_log03_01, femb_id)
            write_pulse_to_csv(34, 35, 36, file_path, 'QC_03_03_Leakage_Current', '1nA_SEOFF_200mVBL_14_0mVfC_2_0us_DAC0x20', log.check_log03_04, femb_id)
            write_pulse_to_csv(37, 38, 39, file_path, 'QC_03_04_Leakage_Current', '5nA_SEOFF_200mVBL_14_0mVfC_2_0us_DAC0x20', log.check_log03_03, femb_id)

        if 4 in log.test_label:
            # SE_OFF 200 mV baseline, DAC=0x10
            write_pulse_to_csv(40, 41, 42, file_path, 'QC_04_01_Check_Pulse', 'SEOFF_200mVBL_4_7mVfC_0_5us_DAC0x10', log.check_log04_01_4705, femb_id)
            write_pulse_to_csv(43, 44, 45, file_path, 'QC_04_02_Check_Pulse', 'SEOFF_200mVBL_4_7mVfC_1_0us_DAC0x10', log.check_log04_01_4710, femb_id)
            write_pulse_to_csv(46, 47, 48, file_path, 'QC_04_03_Check_Pulse', 'SEOFF_200mVBL_4_7mVfC_2_0us_DAC0x10', log.check_log04_01_4720, femb_id)
            write_pulse_to_csv(49, 50, 51, file_path, 'QC_04_04_Check_Pulse', 'SEOFF_200mVBL_4_7mVfC_3_0us_DAC0x10', log.check_log04_01_4730, femb_id)

            write_pulse_to_csv(52, 53, 54, file_path, 'QC_04_05_Check_Pulse', 'SEOFF_200mVBL_7_8mVfC_0_5us_DAC0x10', log.check_log04_01_7805, femb_id)
            write_pulse_to_csv(55, 56, 57, file_path, 'QC_04_06_Check_Pulse', 'SEOFF_200mVBL_7_8mVfC_1_0us_DAC0x10', log.check_log04_01_7810, femb_id)
            write_pulse_to_csv(58, 59, 60, file_path, 'QC_04_07_Check_Pulse', 'SEOFF_200mVBL_7_8mVfC_2_0us_DAC0x10', log.check_log04_01_7820, femb_id)
            write_pulse_to_csv(61, 62, 63, file_path, 'QC_04_08_Check_Pulse', 'SEOFF_200mVBL_7_8mVfC_3_0us_DAC0x10', log.check_log04_01_7830, femb_id)

            write_pulse_to_csv(64, 65, 66, file_path, 'QC_04_09_Check_Pulse', 'SEOFF_200mVBL_14_0mVfC_0_5us_DAC0x10', log.check_log04_01_1405, femb_id)
            write_pulse_to_csv(67, 68, 69, file_path, 'QC_04_10_Check_Pulse', 'SEOFF_200mVBL_14_0mVfC_1_0us_DAC0x10', log.check_log04_01_1410, femb_id)
            write_pulse_to_csv(70, 71, 72, file_path, 'QC_04_11_Check_Pulse', 'SEOFF_200mVBL_14_0mVfC_2_0us_DAC0x10', log.check_log04_01_1420, femb_id)
            write_pulse_to_csv(73, 74, 75, file_path, 'QC_04_12_Check_Pulse', 'SEOFF_200mVBL_14_0mVfC_3_0us_DAC0x10', log.check_log04_01_1430, femb_id)

            write_pulse_to_csv(76, 77, 78, file_path, 'QC_04_13_Check_Pulse', 'SEOFF_200mVBL_25_0mVfC_0_5us_DAC0x10', log.check_log04_01_2505, femb_id)
            write_pulse_to_csv(79, 80, 81, file_path, 'QC_04_14_Check_Pulse', 'SEOFF_200mVBL_25_0mVfC_1_0us_DAC0x10', log.check_log04_01_2510, femb_id)
            write_pulse_to_csv(82, 83, 84, file_path, 'QC_04_15_Check_Pulse', 'SEOFF_200mVBL_25_0mVfC_2_0us_DAC0x10', log.check_log04_01_2520, femb_id)
            write_pulse_to_csv(85, 86, 87, file_path, 'QC_04_16_Check_Pulse', 'SEOFF_200mVBL_25_0mVfC_3_0us_DAC0x10', log.check_log04_01_2530, femb_id)

            # SE_OFF 900 mV baseline, DAC=0x10
            write_pulse_to_csv(88, 89, 90, file_path, 'QC_04_17_Check_Pulse', 'SEOFF_900mVBL_4_7mVfC_0_5us_DAC0x10', log.check_log04_02_4705, femb_id)
            write_pulse_to_csv(91, 92, 93, file_path, 'QC_04_18_Check_Pulse', 'SEOFF_900mVBL_4_7mVfC_1_0us_DAC0x10', log.check_log04_02_4710, femb_id)
            write_pulse_to_csv(94, 95, 96, file_path, 'QC_04_19_Check_Pulse', 'SEOFF_900mVBL_4_7mVfC_2_0us_DAC0x10', log.check_log04_02_4720, femb_id)
            write_pulse_to_csv(97, 98, 99, file_path, 'QC_04_20_Check_Pulse', 'SEOFF_900mVBL_4_7mVfC_3_0us_DAC0x10', log.check_log04_02_4730, femb_id)

            write_pulse_to_csv(100, 101, 102, file_path, 'QC_04_21_Check_Pulse', 'SEOFF_900mVBL_7_8mVfC_0_5us_DAC0x10', log.check_log04_02_7805, femb_id)
            write_pulse_to_csv(103, 104, 105, file_path, 'QC_04_22_Check_Pulse', 'SEOFF_900mVBL_7_8mVfC_1_0us_DAC0x10', log.check_log04_02_7810, femb_id)
            write_pulse_to_csv(106, 107, 108, file_path, 'QC_04_23_Check_Pulse', 'SEOFF_900mVBL_7_8mVfC_2_0us_DAC0x10', log.check_log04_02_7820, femb_id)
            write_pulse_to_csv(109, 110, 111, file_path, 'QC_04_24_Check_Pulse', 'SEOFF_900mVBL_7_8mVfC_3_0us_DAC0x10', log.check_log04_02_7830, femb_id)

            write_pulse_to_csv(112, 113, 114, file_path, 'QC_04_25_Check_Pulse', 'SEOFF_900mVBL_14_0mVfC_0_5us_DAC0x10', log.check_log04_02_1405, femb_id)
            write_pulse_to_csv(115, 116, 117, file_path, 'QC_04_26_Check_Pulse', 'SEOFF_900mVBL_14_0mVfC_1_0us_DAC0x10', log.check_log04_02_1410, femb_id)
            write_pulse_to_csv(118, 119, 120, file_path, 'QC_04_27_Check_Pulse', 'SEOFF_900mVBL_14_0mVfC_2_0us_DAC0x10', log.check_log04_02_1420, femb_id)
            write_pulse_to_csv(121, 122, 123, file_path, 'QC_04_28_Check_Pulse', 'SEOFF_900mVBL_14_0mVfC_3_0us_DAC0x10', log.check_log04_02_1430, femb_id)

            write_pulse_to_csv(124, 125, 126, file_path, 'QC_04_29_Check_Pulse', 'SEOFF_900mVBL_25_0mVfC_0_5us_DAC0x10', log.check_log04_02_2505, femb_id)
            write_pulse_to_csv(127, 128, 129, file_path, 'QC_04_30_Check_Pulse', 'SEOFF_900mVBL_25_0mVfC_1_0us_DAC0x10', log.check_log04_02_2510, femb_id)
            write_pulse_to_csv(130, 131, 132, file_path, 'QC_04_31_Check_Pulse', 'SEOFF_900mVBL_25_0mVfC_2_0us_DAC0x10', log.check_log04_02_2520, femb_id)
            write_pulse_to_csv(133, 134, 135, file_path, 'QC_04_32_Check_Pulse', 'SEOFF_900mVBL_25_0mVfC_3_0us_DAC0x10', log.check_log04_02_2530, femb_id)

            # SGP=1 200 mV baseline, DAC=0x10
            write_pulse_to_csv(136, 137, 138, file_path, 'QC_04_33_Check_Pulse', 'SGP_200mVBL_14_0mVfC_2_0us_DAC0x10', log.check_log04_03_4720, femb_id)
            write_pulse_to_csv(139, 140, 141, file_path, 'QC_04_34_Check_Pulse', 'SGP_200mVBL_14_0mVfC_2_0us_DAC0x10', log.check_log04_03_7820, femb_id)
            write_pulse_to_csv(142, 143, 144, file_path, 'QC_04_35_Check_Pulse', 'SGP_200mVBL_14_0mVfC_2_0us_DAC0x10', log.check_log04_03_1420, femb_id)
            write_pulse_to_csv(145, 146, 147, file_path, 'QC_04_36_Check_Pulse', 'SGP_200mVBL_14_0mVfC_2_0us_DAC0x10', log.check_log04_03_2520, femb_id)

            # SEON DAC=0x10
            write_pulse_to_csv(148, 149, 150, file_path, 'QC_04_37_Check_Pulse', 'SEON_200mVBL_14_0mVfC_2_0us_DAC0x10', log.check_log04_04_14201, femb_id)
            write_pulse_to_csv(151, 152, 153, file_path, 'QC_04_38_Check_Pulse', 'SEON_900mVBL_14_0mVfC_2_0us_DAC0x10', log.check_log04_04_14202, femb_id)
            # SEON DAC=0x10
            write_pulse_to_csv(154, 155, 156, file_path, 'QC_04_39_Check_Pulse', 'DIFF_200mVBL_14_0mVfC_2_0us_DAC0x10', log.check_log04_04_14203, femb_id)
            write_pulse_to_csv(157, 158, 159, file_path, 'QC_04_40_Check_Pulse', 'DIFF_900mVBL_14_0mVfC_2_0us_DAC0x10', log.check_log04_04_14204, femb_id)
            # DIFF
            write_pulse_to_csv(160, 161, 162, file_path, 'QC_04_41_Check_Pulse', 'CHK_EX_200mVBL_14_0mVfC_2_0us_vdac000050mV', log.check_log04_05_14201, femb_id)
            write_pulse_to_csv(163, 164, 165, file_path, 'QC_04_42_Check_Pulse', 'CHK_EX_200mVBL_14_0mVfC_2_0us_vdac000150mV', log.check_log04_05_14202, femb_id)
            write_pulse_to_csv(166, 167, 168, file_path, 'QC_04_43_Check_Pulse', 'CHK_EX_200mVBL_14_0mVfC_2_0us_vdac000350mV', log.check_log04_05_14203, femb_id)
            #write_pulse_to_csv(145, 146, 147, file_path, 'QC_04_36_Check_Pulse', 'SGP_200mVBL_14_0mVfC_2_0us_DAC0x10', log.check_log04_03_2520, femb_id)

        if 5 in log.test_label:
            # Baseline = 200 mV
            write_bandgap_to_csv(169, file_path, 'QC_05_01_Bandgap_RMS', 'SE_200mVBL_4_7mVfC_0_5us', ifemb)
            write_bandgap_to_csv(170, file_path, 'QC_05_02_Bandgap_RMS', 'SE_200mVBL_4_7mVfC_1_0us', ifemb)
            write_bandgap_to_csv(171, file_path, 'QC_05_03_Bandgap_RMS', 'SE_200mVBL_4_7mVfC_2_0us', ifemb)
            write_bandgap_to_csv(172, file_path, 'QC_05_04_Bandgap_RMS', 'SE_200mVBL_4_7mVfC_3_0us', ifemb)

            write_bandgap_to_csv(173, file_path, 'QC_05_05_Bandgap_RMS', 'SE_200mVBL_7_8mVfC_0_5us', ifemb)
            write_bandgap_to_csv(174, file_path, 'QC_05_06_Bandgap_RMS', 'SE_200mVBL_7_8mVfC_1_0us', ifemb)
            write_bandgap_to_csv(175, file_path, 'QC_05_07_Bandgap_RMS', 'SE_200mVBL_7_8mVfC_2_0us', ifemb)
            write_bandgap_to_csv(176, file_path, 'QC_05_08_Bandgap_RMS', 'SE_200mVBL_7_8mVfC_3_0us', ifemb)

            write_bandgap_to_csv(177, file_path, 'QC_05_09_Bandgap_RMS', 'SE_200mVBL_14_0mVfC_0_5us', ifemb)
            write_bandgap_to_csv(178, file_path, 'QC_05_10_Bandgap_RMS', 'SE_200mVBL_14_0mVfC_1_0us', ifemb)
            write_bandgap_to_csv(179, file_path, 'QC_05_11_Bandgap_RMS', 'SE_200mVBL_14_0mVfC_2_0us', ifemb)
            write_bandgap_to_csv(180, file_path, 'QC_05_12_Bandgap_RMS', 'SE_200mVBL_14_0mVfC_3_0us', ifemb)

            write_bandgap_to_csv(181, file_path, 'QC_05_13_Bandgap_RMS', 'SE_200mVBL_25_0mVfC_0_5us', ifemb)
            write_bandgap_to_csv(182, file_path, 'QC_05_14_Bandgap_RMS', 'SE_200mVBL_25_0mVfC_1_0us', ifemb)
            write_bandgap_to_csv(183, file_path, 'QC_05_15_Bandgap_RMS', 'SE_200mVBL_25_0mVfC_2_0us', ifemb)
            write_bandgap_to_csv(184, file_path, 'QC_05_16_Bandgap_RMS', 'SE_200mVBL_25_0mVfC_3_0us', ifemb)

            # Baseline = 900 mV
            write_bandgap_to_csv(185, file_path, 'QC_05_17_Bandgap_RMS', 'SE_900mVBL_4_7mVfC_0_5us', ifemb)
            write_bandgap_to_csv(186, file_path, 'QC_05_18_Bandgap_RMS', 'SE_900mVBL_4_7mVfC_1_0us', ifemb)
            write_bandgap_to_csv(187, file_path, 'QC_05_19_Bandgap_RMS', 'SE_900mVBL_4_7mVfC_2_0us', ifemb)
            write_bandgap_to_csv(188, file_path, 'QC_05_20_Bandgap_RMS', 'SE_900mVBL_4_7mVfC_3_0us', ifemb)

            write_bandgap_to_csv(189, file_path, 'QC_05_21_Bandgap_RMS', 'SE_900mVBL_7_8mVfC_0_5us', ifemb)
            write_bandgap_to_csv(190, file_path, 'QC_05_22_Bandgap_RMS', 'SE_900mVBL_7_8mVfC_1_0us', ifemb)
            write_bandgap_to_csv(191, file_path, 'QC_05_23_Bandgap_RMS', 'SE_900mVBL_7_8mVfC_2_0us', ifemb)
            write_bandgap_to_csv(192, file_path, 'QC_05_24_Bandgap_RMS', 'SE_900mVBL_7_8mVfC_3_0us', ifemb)

            write_bandgap_to_csv(193, file_path, 'QC_05_25_Bandgap_RMS', 'SE_900mVBL_14_0mVfC_0_5us', ifemb)
            write_bandgap_to_csv(194, file_path, 'QC_05_26_Bandgap_RMS', 'SE_900mVBL_14_0mVfC_1_0us', ifemb)
            write_bandgap_to_csv(195, file_path, 'QC_05_27_Bandgap_RMS', 'SE_900mVBL_14_0mVfC_2_0us', ifemb)
            write_bandgap_to_csv(196, file_path, 'QC_05_28_Bandgap_RMS', 'SE_900mVBL_14_0mVfC_3_0us', ifemb)

            write_bandgap_to_csv(197, file_path, 'QC_05_29_Bandgap_RMS', 'SE_900mVBL_25_0mVfC_0_5us', ifemb)
            write_bandgap_to_csv(198, file_path, 'QC_05_30_Bandgap_RMS', 'SE_900mVBL_25_0mVfC_1_0us', ifemb)
            write_bandgap_to_csv(199, file_path, 'QC_05_31_Bandgap_RMS', 'SE_900mVBL_25_0mVfC_2_0us', ifemb)
            write_bandgap_to_csv(200, file_path, 'QC_05_32_Bandgap_RMS', 'SE_900mVBL_25_0mVfC_3_0us', ifemb)

            # DIFF interface
            write_bandgap_to_csv(201, file_path, 'QC_05_33_Bandgap_RMS', 'DIFF_200mVBL_4_7mVfC_2_0us', ifemb)
            write_bandgap_to_csv(202, file_path, 'QC_05_34_Bandgap_RMS', 'DIFF_200mVBL_7_8mVfC_2_0us', ifemb)
            write_bandgap_to_csv(203, file_path, 'QC_05_35_Bandgap_RMS', 'DIFF_200mVBL_14_0mVfC_2_0us', ifemb)
            write_bandgap_to_csv(204, file_path, 'QC_05_36_Bandgap_RMS', 'DIFF_200mVBL_25_0mVfC_2_0us', ifemb)
            write_bandgap_to_csv(205, file_path, 'QC_05_37_Bandgap_RMS', 'DIFF_900mVBL_4_7mVfC_2_0us', ifemb)
            write_bandgap_to_csv(206, file_path, 'QC_05_38_Bandgap_RMS', 'DIFF_900mVBL_7_8mVfC_2_0us', ifemb)
            write_bandgap_to_csv(207, file_path, 'QC_05_39_Bandgap_RMS', 'DIFF_900mVBL_14_0mVfC_2_0us', ifemb)
            write_bandgap_to_csv(208, file_path, 'QC_05_40_Bandgap_RMS', 'DIFF_900mVBL_25_0mVfC_2_0us', ifemb)

            # SE-ON interface
            write_bandgap_to_csv(209, file_path, 'QC_05_41_Bandgap_RMS', 'SEON_200mVBL_4_7mVfC_2_0us', ifemb)
            write_bandgap_to_csv(210, file_path, 'QC_05_42_Bandgap_RMS', 'SEON_200mVBL_7_8mVfC_2_0us', ifemb)
            write_bandgap_to_csv(211, file_path, 'QC_05_43_Bandgap_RMS', 'SEON_200mVBL_14_0mVfC_2_0us', ifemb)
            write_bandgap_to_csv(212, file_path, 'QC_05_44_Bandgap_RMS', 'SEON_200mVBL_25_0mVfC_2_0us', ifemb)
            write_bandgap_to_csv(213, file_path, 'QC_05_45_Bandgap_RMS', 'SEON_900mVBL_4_7mVfC_2_0us', ifemb)
            write_bandgap_to_csv(214, file_path, 'QC_05_46_Bandgap_RMS', 'SEON_900mVBL_7_8mVfC_2_0us', ifemb)
            write_bandgap_to_csv(215, file_path, 'QC_05_47_Bandgap_RMS', 'SEON_900mVBL_14_0mVfC_2_0us', ifemb)
            write_bandgap_to_csv(216, file_path, 'QC_05_48_Bandgap_RMS', 'SEON_900mVBL_25_0mVfC_2_0us', ifemb)

            # SE-OFF Leakage Current test
            write_bandgap_to_csv(217, file_path, 'QC_05_49_Bandgap_RMS', 'SELC_200mVBL_14_0mVfC_2_0us_100pA', ifemb)
            write_bandgap_to_csv(218, file_path, 'QC_05_50_Bandgap_RMS', 'SELC_200mVBL_14_0mVfC_2_0us_500pA', ifemb)
            write_bandgap_to_csv(219, file_path, 'QC_05_51_Bandgap_RMS', 'SELC_200mVBL_14_0mVfC_2_0us_1nA', ifemb)
            write_bandgap_to_csv(220, file_path, 'QC_05_52_Bandgap_RMS', 'SELC_200mVBL_14_0mVfC_2_0us_5nA', ifemb)

        if 6 in log.test_label: # LSB =         dac_v['4_7mVfC']=18.66        dac_v['7_8mVfC']=14.33        dac_v['14_0mVfC']=8.08        dac_v['25_0mVfC']=4.61
            line_number = 221;
            data = ['QC_06_01_4_7mVfC_Calibration_GAIN_01', 'SEOFF_200mVBL_4_7mVfC_2_0us', 'Gain Mean', '{}'.format(log.report_log0601csvgain[ifemb]['mean']), '5-sigma-STD', '{}'.format(5*log.report_log0601csvgain[ifemb]['std']), 'MAX', '{}'.format(log.report_log0601csvgain[ifemb]['max']), 'MIN', '{}'.format(log.report_log0601csvgain[ifemb]['min']), '128-Ch Distribution'] + log.report_log0601csvgain[ifemb]['gain_list']
            csv_style.write_to_csv_line(file_path, line_number, data)
            line_number = 222;
            data = ['QC_06_01_4_7mVfC_Calibration_INL_02', 'SEOFF_200mVBL_4_7mVfC_2_0us', 'INL Mean / %', '{}'.format(log.report_log0601csvinl[ifemb]['mean']), '5-sigma-STD', '{}'.format(5*log.report_log0601csvinl[ifemb]['std']), 'MAX', '{}'.format(log.report_log0601csvinl[ifemb]['max']), 'MIN', '{}'.format(log.report_log0601csvinl[ifemb]['min']), '128-Ch Distribution'] + log.report_log0601csvinl[ifemb]['inl_list / %']
            csv_style.write_to_csv_line(file_path, line_number, data)
            line_number = 223;
            data = ['QC_06_01_4_7mVfC_Calibration_Linearity_Range_03', 'SEOFF_200mVBL_4_7mVfC_2_0us', 'Linearity_Range / fc', '{}'.format(log.report_log0601csvlinerange[ifemb]['mean']), '5-sigma-STD', '{}'.format(5*log.report_log0601csvlinerange[ifemb]['std']), 'MAX', '{}'.format(log.report_log0601csvlinerange[ifemb]['max']), 'MIN', '{}'.format(log.report_log0601csvlinerange[ifemb]['min']), '128-Ch Distribution'] + log.report_log0601csvlinerange[ifemb]['line_range_list']
            csv_style.write_to_csv_line(file_path, line_number, data)

            line_number = 224;
            data = ['QC_06_02_7_8mVfC_Calibration_GAIN_01', 'SEOFF_200mVBL_7_8mVfC_2_0us', 'Gain Mean', '{}'.format(log.report_log0602csvgain[ifemb]['mean']), '5-sigma-STD', '{}'.format(5*log.report_log0602csvgain[ifemb]['std']), 'MAX', '{}'.format(log.report_log0602csvgain[ifemb]['max']), 'MIN', '{}'.format(log.report_log0602csvgain[ifemb]['min']), '128-Ch Distribution'] + log.report_log0602csvgain[ifemb]['gain_list']
            csv_style.write_to_csv_line(file_path, line_number, data)
            line_number = 225;
            data = ['QC_06_02_7_8mVfC_Calibration_INL_02', 'SEOFF_200mVBL_7_8mVfC_2_0us', 'INL Mean / %', '{}'.format(log.report_log0602csvinl[ifemb]['mean']), '5-sigma-STD', '{}'.format(5*log.report_log0602csvinl[ifemb]['std']), 'MAX', '{}'.format(log.report_log0602csvinl[ifemb]['max']), 'MIN', '{}'.format(log.report_log0602csvinl[ifemb]['min']), '128-Ch Distribution'] + log.report_log0602csvinl[ifemb]['inl_list / %']
            csv_style.write_to_csv_line(file_path, line_number, data)
            line_number = 226;
            data = ['QC_06_02_7_8mVfC_Calibration_Linearity_Range_03', 'SEOFF_200mVBL_7_8mVfC_2_0us', 'Linearity_Range / fc', '{}'.format(log.report_log0602csvlinerange[ifemb]['mean']), '5-sigma-STD', '{}'.format(5*log.report_log0602csvlinerange[ifemb]['std']), 'MAX', '{}'.format(log.report_log0602csvlinerange[ifemb]['max']), 'MIN', '{}'.format(log.report_log0602csvlinerange[ifemb]['min']), '128-Ch Distribution'] + log.report_log0602csvlinerange[ifemb]['line_range_list']
            csv_style.write_to_csv_line(file_path, line_number, data)

            line_number = 227;
            data = ['QC_06_03_14_0mVfC_Calibration_GAIN_01', 'SEOFF_200mVBL_14_0mVfC_2_0us', 'Gain Mean', '{}'.format(log.report_log0603csvgain[ifemb]['mean']), '5-sigma-STD', '{}'.format(5*log.report_log0603csvgain[ifemb]['std']), 'MAX', '{}'.format(log.report_log0603csvgain[ifemb]['max']), 'MIN', '{}'.format(log.report_log0603csvgain[ifemb]['min']), '128-Ch Distribution'] + log.report_log0603csvgain[ifemb]['gain_list']
            csv_style.write_to_csv_line(file_path, line_number, data)
            line_number = 228;
            data = ['QC_06_03_14_0mVfC_Calibration_INL_02', 'SEOFF_200mVBL_14_0mVfC_2_0us', 'INL Mean / %', '{}'.format(log.report_log0603csvinl[ifemb]['mean']), '5-sigma-STD', '{}'.format(5*log.report_log0603csvinl[ifemb]['std']), 'MAX', '{}'.format(log.report_log0603csvinl[ifemb]['max']), 'MIN', '{}'.format(log.report_log0603csvinl[ifemb]['min']), '128-Ch Distribution'] + log.report_log0603csvinl[ifemb]['inl_list / %']
            csv_style.write_to_csv_line(file_path, line_number, data)
            line_number = 229;
            data = ['QC_06_03_14_0mVfC_Calibration_Linearity_Range_03', 'SEOFF_200mVBL_14_0mVfC_2_0us', 'Linearity_Range / fc', '{}'.format(log.report_log0603csvlinerange[ifemb]['mean']), '5-sigma-STD', '{}'.format(5*log.report_log0603csvlinerange[ifemb]['std']), 'MAX', '{}'.format(log.report_log0603csvlinerange[ifemb]['max']), 'MIN', '{}'.format(log.report_log0603csvlinerange[ifemb]['min']), '128-Ch Distribution'] + log.report_log0603csvlinerange[ifemb]['line_range_list']
            csv_style.write_to_csv_line(file_path, line_number, data)

            line_number = 230;
            data = ['QC_06_04_25_0mVfC_Calibration_GAIN_01', 'SEOFF_200mVBL_25_0mVfC_2_0us', 'Gain Mean', '{}'.format(log.report_log0604csvgain[ifemb]['mean']), '5-sigma-STD', '{}'.format(5*log.report_log0604csvgain[ifemb]['std']), 'MAX', '{}'.format(log.report_log0604csvgain[ifemb]['max']), 'MIN', '{}'.format(log.report_log0604csvgain[ifemb]['min']), '128-Ch Distribution'] + log.report_log0604csvgain[ifemb]['gain_list']
            csv_style.write_to_csv_line(file_path, line_number, data)
            line_number = 231;
            data = ['QC_06_04_25_0mVfC_Calibration_INL_02', 'SEOFF_200mVBL_25_0mVfC_2_0us', 'INL Mean / %', '{}'.format(log.report_log0604csvinl[ifemb]['mean']), '5-sigma-STD', '{}'.format(5*log.report_log0604csvinl[ifemb]['std']), 'MAX', '{}'.format(log.report_log0604csvinl[ifemb]['max']), 'MIN', '{}'.format(log.report_log0604csvinl[ifemb]['min']), '128-Ch Distribution'] + log.report_log0604csvinl[ifemb]['inl_list / %']
            csv_style.write_to_csv_line(file_path, line_number, data)
            line_number = 232;
            data = ['QC_06_04_25_0mVfC_Calibration_Linearity_Range_03', 'SEOFF_200mVBL_25_0mVfC_2_0us', 'Linearity_Range / fc', '{}'.format(log.report_log0604csvlinerange[ifemb]['mean']), '5-sigma-STD', '{}'.format(5*log.report_log0604csvlinerange[ifemb]['std']), 'MAX', '{}'.format(log.report_log0604csvlinerange[ifemb]['max']), 'MIN', '{}'.format(log.report_log0604csvlinerange[ifemb]['min']), '128-Ch Distribution'] + log.report_log0604csvlinerange[ifemb]['line_range_list']
            csv_style.write_to_csv_line(file_path, line_number, data)

        if 7 in log.test_label:
            line_number = 233;
            data = ['QC_07_01_14_0mVfC_Calibration_GAIN_01', 'SEOFF_900mVBL_14_0mVfC_2_0us', 'Gain Mean', '{}'.format(log.report_log0701csvgain[ifemb]['mean']), '5-sigma-STD', '{}'.format(5*log.report_log0701csvgain[ifemb]['std']), 'MAX', '{}'.format(log.report_log0701csvgain[ifemb]['max']), 'MIN', '{}'.format(log.report_log0701csvgain[ifemb]['min']), '128-Ch Distribution'] + log.report_log0701csvgain[ifemb]['gain_list']
            csv_style.write_to_csv_line(file_path, line_number, data)
            line_number = 234;
            data = ['QC_07_01_14_0mVfC_Calibration_INL_02', 'SEOFF_900mVBL_14_0mVfC_2_0us', 'INL Mean', '{}'.format(log.report_log0701csvinl[ifemb]['mean']), '5-sigma-STD', '{}'.format(5*log.report_log0701csvinl[ifemb]['std']), 'MAX', '{}'.format(log.report_log0701csvinl[ifemb]['max']), 'MIN', '{}'.format(log.report_log0701csvinl[ifemb]['min']), '128-Ch Distribution'] + log.report_log0701csvinl[ifemb]['inl_list / %']
            csv_style.write_to_csv_line(file_path, line_number, data)
            line_number = 235;
            data = ['QC_07_01_14_0mVfC_Calibration_Linearity_Range_03', 'SEOFF_900mVBL_14_0mVfC_2_0us', 'Linearity_Range', '{}'.format(log.report_log0701csvlinerange[ifemb]['mean']), '5-sigma-STD', '{}'.format(5*log.report_log0701csvlinerange[ifemb]['std']), 'MAX', '{}'.format(log.report_log0701csvlinerange[ifemb]['max']), 'MIN', '{}'.format(log.report_log0701csvlinerange[ifemb]['min']), '128-Ch Distribution'] + log.report_log0701csvlinerange[ifemb]['line_range_list']
            csv_style.write_to_csv_line(file_path, line_number, data)
        if 8 in log.test_label:
            line_number = 236;
            data = ['QC_08_01_14_0mVfC_Calibration_GAIN_01', 'SGP1_200mVBL_14_0mVfC_2_0us', 'Gain Mean', '{}'.format(log.report_log0801csvgain[ifemb]['mean']), '5-sigma-STD', '{}'.format(5*log.report_log0801csvgain[ifemb]['std']), 'MAX', '{}'.format(log.report_log0801csvgain[ifemb]['max']), 'MIN', '{}'.format(log.report_log0801csvgain[ifemb]['min']), '128-Ch Distribution'] + log.report_log0801csvgain[ifemb]['gain_list']
            csv_style.write_to_csv_line(file_path, line_number, data)
            line_number = 237;
            data = ['QC_08_01_14_0mVfC_Calibration_INL_02', 'SGP1_200mVBL_14_0mVfC_2_0us', 'INL Mean', '{}'.format(log.report_log0801csvinl[ifemb]['mean']), '5-sigma-STD', '{}'.format(5*log.report_log0801csvinl[ifemb]['std']), 'MAX', '{}'.format(log.report_log0801csvinl[ifemb]['max']), 'MIN', '{}'.format(log.report_log0801csvinl[ifemb]['min']), '128-Ch Distribution'] + log.report_log0801csvinl[ifemb]['inl_list / %']
            csv_style.write_to_csv_line(file_path, line_number, data)
            line_number = 238;
            data = ['QC_08_01_14_0mVfC_Calibration_Linearity_Range_03', 'SGP1_200mVBL_14_0mVfC_2_0us', 'Linearity_Range', '{}'.format(log.report_log0801csvlinerange[ifemb]['mean']), '5-sigma-STD', '{}'.format(5*log.report_log0801csvlinerange[ifemb]['std']), 'MAX', '{}'.format(log.report_log0801csvlinerange[ifemb]['max']), 'MIN', '{}'.format(log.report_log0801csvlinerange[ifemb]['min']), '128-Ch Distribution'] + log.report_log0801csvlinerange[ifemb]['line_range_list']
            csv_style.write_to_csv_line(file_path, line_number, data)
        if 9 in log.test_label:
            line_number = 239;
            data = ['QC_09_01_14_0mVfC_Calibration_GAIN_01', 'SGP1_900mVBL_14_0mVfC_2_0us', 'Gain Mean', '{}'.format(log.report_log0901csvgain[ifemb]['mean']), '5-sigma-STD', '{}'.format(5*log.report_log0901csvgain[ifemb]['std']), 'MAX', '{}'.format(log.report_log0901csvgain[ifemb]['max']), 'MIN', '{}'.format(log.report_log0901csvgain[ifemb]['min']), '128-Ch Distribution'] + log.report_log0901csvgain[ifemb]['gain_list']
            csv_style.write_to_csv_line(file_path, line_number, data)
            line_number = 240;
            data = ['QC_09_01_14_0mVfC_Calibration_INL_02', 'SGP1_900mVBL_14_0mVfC_2_0us', 'INL Mean', '{}'.format(log.report_log0901csvinl[ifemb]['mean']), '5-sigma-STD', '{}'.format(5*log.report_log0901csvinl[ifemb]['std']), 'MAX', '{}'.format(log.report_log0901csvinl[ifemb]['max']), 'MIN', '{}'.format(log.report_log0901csvinl[ifemb]['min']), '128-Ch Distribution'] + log.report_log0901csvinl[ifemb]['inl_list / %']
            csv_style.write_to_csv_line(file_path, line_number, data)
            line_number = 241;
            data = ['QC_09_01_14_0mVfC_Calibration_Linearity_Range_03', 'SGP1_900mVBL_14_0mVfC_2_0us', 'Linearity_Range', '{}'.format(log.report_log0901csvlinerange[ifemb]['mean']), '5-sigma-STD', '{}'.format(5*log.report_log0901csvlinerange[ifemb]['std']), 'MAX', '{}'.format(log.report_log0901csvlinerange[ifemb]['max']), 'MIN', '{}'.format(log.report_log0901csvlinerange[ifemb]['min']), '128-Ch Distribution'] + log.report_log0901csvlinerange[ifemb]['line_range_list']
            csv_style.write_to_csv_line(file_path, line_number, data)

        if 10 in log.test_label:
            line_number = 242;
            data = ['QC_10_01_LArASIC_Mon', 'bandgap', 'Bandgap_mean', '{}'.format(log.mon_pulse["bandgap_mean"][femb_id]), '5-sigma-STD', '{}'.format(5*log.mon_pulse["bandgap_std"][femb_id]), 'MAX', '{}'.format(log.mon_pulse["bandgap_max"][femb_id]), 'MIN', '{}'.format(log.mon_pulse["bandgap_min"][femb_id]), '128-Ch Distribution'] + log.mon_pulse["bandgap"][femb_id]
            csv_style.write_to_csv_line(file_path, line_number, data)
            line_number = 243;
            data = ['QC_10_02_LArASIC_Mon', 'temperature', 'temperature_mean', '{}'.format(log.mon_pulse["temperature_mean"][femb_id]), '5-sigma-STD', '{}'.format(5*log.mon_pulse["temperature_std"][femb_id]), 'MAX', '{}'.format(log.mon_pulse["temperature_max"][femb_id]), 'MIN', '{}'.format(log.mon_pulse["temperature_min"][femb_id]), '128-Ch Distribution'] + log.mon_pulse["temperature"][femb_id]
            csv_style.write_to_csv_line(file_path, line_number, data)
            line_number = 244;
            data = ['QC_10_03_LArASIC_Mon', '200mVBL_sdf1', '200mVBL_sdf1_mean', '{}'.format(log.mon_pulse["200mVBL_sdf1_mean"][femb_id]), '5-sigma-STD', '{}'.format(5*log.mon_pulse["200mVBL_sdf1_std"][femb_id]), 'MAX', '{}'.format(log.mon_pulse["200mVBL_sdf1_max"][femb_id]), 'MIN', '{}'.format(log.mon_pulse["200mVBL_sdf1_min"][femb_id]), '128-Ch Distribution'] + log.mon_pulse["200mVBL_sdf1"][femb_id]
            csv_style.write_to_csv_line(file_path, line_number, data)
            line_number = 245;
            data = ['QC_10_04_LArASIC_Mon', '200mVBL_sdf0', '200mVBL_sdf0_mean', '{}'.format(log.mon_pulse["200mVBL_sdf0_mean"][femb_id]), '5-sigma-STD', '{}'.format(5*log.mon_pulse["200mVBL_sdf0_std"][femb_id]), 'MAX', '{}'.format(log.mon_pulse["200mVBL_sdf0_max"][femb_id]), 'MIN', '{}'.format(log.mon_pulse["200mVBL_sdf0_min"][femb_id]), '128-Ch Distribution'] + log.mon_pulse["200mVBL_sdf0"][femb_id]
            csv_style.write_to_csv_line(file_path, line_number, data)
            line_number = 246;
            data = ['QC_10_05_LArASIC_Mon', '900mVBL_sdf1', '900mVBL_sdf1_mean', '{}'.format(log.mon_pulse["900mVBL_sdf1_mean"][femb_id]), '5-sigma-STD', '{}'.format(5*log.mon_pulse["900mVBL_sdf1_std"][femb_id]), 'MAX', '{}'.format(log.mon_pulse["900mVBL_sdf1_max"][femb_id]), 'MIN', '{}'.format(log.mon_pulse["900mVBL_sdf1_min"][femb_id]), '128-Ch Distribution'] + log.mon_pulse["900mVBL_sdf1"][femb_id]
            csv_style.write_to_csv_line(file_path, line_number, data)
            line_number = 247;
            data = ['QC_10_06_LArASIC_Mon', '900mVBL_sdf0', '900mVBL_sdf0_mean', '{}'.format(log.mon_pulse["900mVBL_sdf0_mean"][femb_id]), '5-sigma-STD', '{}'.format(5*log.mon_pulse["900mVBL_sdf0_std"][femb_id]), 'MAX', '{}'.format(log.mon_pulse["900mVBL_sdf0_max"][femb_id]), 'MIN', '{}'.format(log.mon_pulse["900mVBL_sdf0_min"][femb_id]), '128-Ch Distribution'] + log.mon_pulse["900mVBL_sdf0"][femb_id]
            csv_style.write_to_csv_line(file_path, line_number, data)
        if 11 in log.test_label:
            line_number = 248;
            list = []
            for key, value in log.report_log1101csv[femb_id].items():
                list.append(value)
            print(list)
            data = ['QC_11_01_LArASIC_DAC_LSB', 'LSB_of_LArASIC_DAC', 'LSB'] + list
            csv_style.write_to_csv_line(file_path, line_number, data)
            line_number = 249;
            list = []
            for key, value in log.report_log1102csv[femb_id].items():
                list.append(value)
            print(list)
            data = ['QC_11_02_LArASIC_DAC_LSB', 'INL_of_LArASIC_DAC', 'INL'] + list
            csv_style.write_to_csv_line(file_path, line_number, data)

        if 12 in log.test_label:
            line_number = 250;
            list = []
            for key, value in log.report_log1202csv[femb_id].items():
                list.append(value)
            print(list)
            data = ['QC_12_01_ColdADC_iDAC_LSB', 'LSB_of_ColdADC_iDAC', 'LSB'] + list
            csv_style.write_to_csv_line(file_path, line_number, data)
            line_number = 251;
            list = []
            for key, value in log.report_log1201csv[femb_id].items():
                list.append(value)
            print(list)
            data = ['QC_12_02_ColdADC_iDAC_INL', 'INL_of_ColdADC_iDAC', 'INL'] + list
            csv_style.write_to_csv_line(file_path, line_number, data)

        if 13 in log.test_label:
            line_number = 252;
            data = ['QC_13_01_14_0mVfC_Calibration_GAIN_01', 'EX_900mVBL_14_0mVfC_2_0us', 'Gain Mean', '{}'.format(log.report_log1301csvgain[ifemb]['mean']), '5-sigma-STD', '{}'.format(5*log.report_log1301csvgain[ifemb]['std']), 'MAX', '{}'.format(log.report_log1301csvgain[ifemb]['max']), 'MIN', '{}'.format(log.report_log1301csvgain[ifemb]['min']), '128-Ch Distribution'] + log.report_log1301csvgain[ifemb]['gain_list']
            csv_style.write_to_csv_line(file_path, line_number, data)
            line_number = 253;
            data = ['QC_13_01_14_0mVfC_Calibration_INL_02', 'EX_900mVBL_14_0mVfC_2_0us', 'INL Mean', '{}'.format(log.report_log1301csvinl[ifemb]['mean']), '5-sigma-STD', '{}'.format(5*log.report_log1301csvinl[ifemb]['std']), 'MAX', '{}'.format(log.report_log1301csvinl[ifemb]['max']), 'MIN', '{}'.format(log.report_log1301csvinl[ifemb]['min']), '128-Ch Distribution'] + log.report_log1301csvinl[ifemb]['inl_list / %']
            csv_style.write_to_csv_line(file_path, line_number, data)
            line_number = 254;
            data = ['QC_13_01_14_0mVfC_Calibration_Linearity_Range_03', 'EX_900mVBL_14_0mVfC_2_0us', 'Linearity_Range', '{}'.format(log.report_log1301csvlinerange[ifemb]['mean']), '5-sigma-STD', '{}'.format(5*log.report_log1301csvlinerange[ifemb]['std']), 'MAX', '{}'.format(log.report_log1301csvlinerange[ifemb]['max']), 'MIN', '{}'.format(log.report_log1301csvlinerange[ifemb]['min']), '128-Ch Distribution'] + log.report_log1301csvlinerange[ifemb]['line_range_list']
            csv_style.write_to_csv_line(file_path, line_number, data)
        if 14 in log.test_label:
            line_number = 255;
            data = ['QC_14_01_14_0mVfC_Calibration_GAIN_01', 'EX_200mVBL_14_0mVfC_2_0us', 'Gain Mean', '{}'.format(log.report_log1401csvgain[ifemb]['mean']), '5-sigma-STD', '{}'.format(5*log.report_log1401csvgain[ifemb]['std']), 'MAX', '{}'.format(log.report_log1401csvgain[ifemb]['max']), 'MIN', '{}'.format(log.report_log1401csvgain[ifemb]['min']), '128-Ch Distribution'] + log.report_log1401csvgain[ifemb]['gain_list']
            csv_style.write_to_csv_line(file_path, line_number, data)
            line_number = 256;
            data = ['QC_14_01_14_0mVfC_Calibration_INL_02', 'EX_200mVBL_14_0mVfC_2_0us', 'INL Mean', '{}'.format(log.report_log1401csvinl[ifemb]['mean']), '5-sigma-STD', '{}'.format(5*log.report_log1401csvinl[ifemb]['std']), 'MAX', '{}'.format(log.report_log1401csvinl[ifemb]['max']), 'MIN', '{}'.format(log.report_log1401csvinl[ifemb]['min']), '128-Ch Distribution'] + log.report_log1401csvinl[ifemb]['inl_list / %']
            csv_style.write_to_csv_line(file_path, line_number, data)
            line_number = 257;
            data = ['QC_14_01_14_0mVfC_Calibration_Linearity_Range_03', 'EX_200mVBL_14_0mVfC_2_0us', 'Linearity_Range', '{}'.format(log.report_log1401csvlinerange[ifemb]['mean']), '5-sigma-STD', '{}'.format(5*log.report_log1401csvlinerange[ifemb]['std']), 'MAX', '{}'.format(log.report_log1401csvlinerange[ifemb]['max']), 'MIN', '{}'.format(log.report_log1401csvlinerange[ifemb]['min']), '128-Ch Distribution'] + log.report_log1401csvlinerange[ifemb]['line_range_list']
            csv_style.write_to_csv_line(file_path, line_number, data)

        if 15 in log.test_label:
            line_number = 258;
            data = ['QC_15_01_ColdADC', 'ColdADC_DC_Noise_ped', 'DC_Noise_ped'] + log.check_log15csv[femb_id]['DC_Noise_ped']
            csv_style.write_to_csv_line(file_path, line_number, data)
            line_number = 259;
            data = ['QC_15_02_ColdADC', 'ColdADC_DC_Noise_rms', 'DC_Noise_rms'] + log.check_log15csv[femb_id]['DC_Noise_rms']
            csv_style.write_to_csv_line(file_path, line_number, data)
            line_number = 260;
            data = ['QC_15_03_ColdADC', 'ColdADC_DC_SHA_SE_ped', 'SHA_SE_ped'] + log.check_log15csv[femb_id]['SHA_SE_ped']
            csv_style.write_to_csv_line(file_path, line_number, data)
            line_number = 261;
            data = ['QC_15_04_ColdADC', 'ColdADC_DC_SHA_SE_rms', 'SHA_SE_rms'] + log.check_log15csv[femb_id]['SHA_SE_rms']
            csv_style.write_to_csv_line(file_path, line_number, data)
            line_number = 262;
            data = ['QC_15_05_ColdADC', 'ColdADC_DC_SHA_DIFF_ped', 'SHA_DIFF_ped'] + log.check_log15csv[femb_id]['SHA_DIFF_ped']
            csv_style.write_to_csv_line(file_path, line_number, data)
            line_number = 263;
            data = ['QC_15_06_ColdADC', 'ColdADC_DC_SHA_DIFF_rms', 'SHA_DIFF_rms'] + log.check_log15csv[femb_id]['SHA_DIFF_rms']
            csv_style.write_to_csv_line(file_path, line_number, data)

        if 16 in log.test_label:
            line_number = 264;
            data = ['QC_16_01_PLL', 'Raw_SE_200mVBL_14_0mVfC_2_0us_0x00_0x21', 'Raw_SE_200mVBL_14_0mVfC_2_0us_0x00_0x21'] + log.check_log16csv[femb_id]['Raw_SE_200mVBL_14_0mVfC_2_0us_0x00_0x21_ped']
            csv_style.write_to_csv_line(file_path, line_number, data)
            line_number = 265;
            data = ['QC_16_02_PLL', 'Raw_SE_200mVBL_14_0mVfC_2_0us_0x00_0x22', 'Raw_SE_200mVBL_14_0mVfC_2_0us_0x00_0x22'] + log.check_log16csv[femb_id]['Raw_SE_200mVBL_14_0mVfC_2_0us_0x00_0x22_ped']
            csv_style.write_to_csv_line(file_path, line_number, data)
            line_number = 266;
            data = ['QC_16_03_PLL', 'Raw_SE_200mVBL_14_0mVfC_2_0us_0x00_0x23', 'Raw_SE_200mVBL_14_0mVfC_2_0us_0x00_0x23'] + log.check_log16csv[femb_id]['Raw_SE_200mVBL_14_0mVfC_2_0us_0x00_0x23_ped']
            csv_style.write_to_csv_line(file_path, line_number, data)
            line_number = 267;
            data = ['QC_16_04_PLL', 'Raw_SE_200mVBL_14_0mVfC_2_0us_0x00_0x24', 'Raw_SE_200mVBL_14_0mVfC_2_0us_0x00_0x24'] + log.check_log16csv[femb_id]['Raw_SE_200mVBL_14_0mVfC_2_0us_0x00_0x24_ped']
            csv_style.write_to_csv_line(file_path, line_number, data)
            line_number = 268;
            data = ['QC_16_05_PLL', 'Raw_SE_200mVBL_14_0mVfC_2_0us_0x00_0x25', 'Raw_SE_200mVBL_14_0mVfC_2_0us_0x00_0x25'] + log.check_log16csv[femb_id]['Raw_SE_200mVBL_14_0mVfC_2_0us_0x00_0x25_ped']
            csv_style.write_to_csv_line(file_path, line_number, data)
            line_number = 269;
            data = ['QC_16_06_PLL', 'Raw_SE_200mVBL_14_0mVfC_2_0us_0x00_0x26', 'Raw_SE_200mVBL_14_0mVfC_2_0us_0x00_0x26'] + log.check_log16csv[femb_id]['Raw_SE_200mVBL_14_0mVfC_2_0us_0x00_0x26_ped']
            csv_style.write_to_csv_line(file_path, line_number, data)
            line_number = 270;
            data = ['QC_16_07_PLL', 'Raw_SE_200mVBL_14_0mVfC_2_0us_0x00_0x27', 'Raw_SE_200mVBL_14_0mVfC_2_0us_0x00_0x27'] + log.check_log16csv[femb_id]['Raw_SE_200mVBL_14_0mVfC_2_0us_0x00_0x27_ped']
            csv_style.write_to_csv_line(file_path, line_number, data)
            line_number = 271;
            data = ['QC_16_08_PLL', 'Raw_SE_200mVBL_14_0mVfC_2_0us_0x00_0x28', 'Raw_SE_200mVBL_14_0mVfC_2_0us_0x00_0x28'] + log.check_log16csv[femb_id]['Raw_SE_200mVBL_14_0mVfC_2_0us_0x00_0x28_ped']
            csv_style.write_to_csv_line(file_path, line_number, data)


