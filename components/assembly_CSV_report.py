import csv

import components.assembly_log as log
import subprocess


#================   Final Report    ===================================

def dict_to_markdown_table(dictionary, KEY = "KEY", VALUE = "RECORD"):
    # 获取字典的键和值
    keys = list(dictionary.keys())
    values = list(dictionary.values())

    if VALUE == "PWRVALUE":
        # 构建表格头部
        table = "| {} | {} |\n| --- | --- | --- | --- | --- |\n".format(KEY, " | | | ")
        for key, value in zip(keys, values):
            table += f"| {key} | {value} |\n"
    elif VALUE == "MonPath":
        table = "| {} | {} |\n| --- | --- | --- | --- | --- | --- | --- | --- | --- |\n".format(KEY, " | | | | | | |")
        for key, value in zip(keys, values):
            table += f"| {key} | {value} |\n"
    elif VALUE == "Horizontal":
        table = '|' + '|'.join(dictionary.keys()) + '|' + '\n'
        table += '|' + '|'.join(['---' for _ in dictionary.keys()]) + '|' + '\n'
        table += '|' + '|'.join(str(dictionary[key]).strip() for key in dictionary.keys()) + '|' + '\n'
    else:
        table = "| {} | {} |\n| --- | --- |\n".format(KEY, VALUE)
        for key, value in zip(keys, values):
            table += f"| {key} | {value} |\n"

    return table

def final_CSV(datareport, fembs, fembNo, Rail = True):
    for key, value in log.report_log01["Detail"].items():
        print(f"{key}: {value}")
    all_true = {}
    status = 'P'
    for ifemb in fembs:
        femb_id = "FEMB ID {}".format(fembNo['femb%d' % ifemb])
        print("CSV Generated")
        fpmd = datareport[ifemb] + 'DataBase_FEMB_{}_S{}_{}.csv'.format(fembNo['femb%d' % ifemb], ifemb ,status)

        with open(fpmd, 'w', newline='', encoding = "utf-8") as file:
            writer = csv.writer(file)

            # part01 input info
            for key, value in log.report_log01["Detail"].items():
                writer.writerow([key, value])

            # part02 Power Consumption
            for key, value in log.report_log02[femb_id].items():
                writer.writerow([key, value])
            for key, value in log.report_log03[femb_id].items():
                writer.writerow([key, value])

            # part03 SE Pulse Response
            for key, value in log.report_log04[femb_id].items():
                writer.writerow([key, value])
            for key, value in log.report_log04csv[femb_id].items():
                writer.writerow([key, value])
            for key, value in log.report_log05[femb_id].items():
                writer.writerow([key, value])
            for key, value in log.report_log06csv[femb_id].items():
                writer.writerow([key, value])
            for key, value in log.report_log07[femb_id].items():
                writer.writerow([key, value])
            for key, value in log.report_log07csv[femb_id].items():
                writer.writerow([key, value])
            # part04 DIFF Pulse Response
            for key, value in log.report_log08[femb_id].items():
                writer.writerow([key, value])
            for key, value in log.report_log09[femb_id].items():
                writer.writerow([key, value])
            for key, value in log.report_log10csv[femb_id].items():
                writer.writerow([key, value])
            # part05 Monitoring Path
            for key, value in log.report_log11[femb_id].items():
                writer.writerow([key, value])


'''

# 04        Print <DIFF RMS, PED, Pulse, Power Current, Power Rail>
            if Rail:
                if (log.report_log08[femb_id]["Result"] == True) and (log.report_log091[femb_id]["Result"] == True) and (log.report_log101[femb_id]["Result"] == True):
                    Head04 = '### ' + '<span style="color: green;">' + 'PART 04 DIFF Interface Measurement' + '    < Pass >' + '</span>'  + '\n'
                else:
                    Head04 = '### ' + '<span style="color: red;">' + 'PART 04 DIFF Interface Measurement' + ' | Fail' + '</span>' + '\n'
            else:
                if (log.report_log08[femb_id]["Result"] == True) and (log.report_log091[femb_id]["Result"] == True):
                    Head04 = '### ' + '<span style="color: green;">' + 'PART 04 DIFF Interface Measurement' + '    < Pass >' + '</span>'  + '\n'
                else:
                    Head04 = '### ' + '<span style="color: red;">' + 'PART 04 DIFF Interface Measurement' + ' | Fail' + '</span>' + '\n'
            file.write(Head04 + '\n')
            file.write('## ' + str(log.report_log08["ITEM"]) + '\n')
            # file.write('#### ' + 'Result:    ' + str(log.report_log08[femb_id]["Result"]) + '\n\n')

            info = dict_to_markdown_table(log.report_log08[femb_id], KEY="4.1 DIFF Pulse Measurement", VALUE="VALUE")
            # for key, value in log.report_log08[femb_id].items():
            #     file.write('#### ' + f"{key}: {value}\n")
            file.write("![ped](./pulse_Raw_DIFF_900mVBL_14_0mVfC_2_0us_0x10.png)" + "\n\n")
            file.write(info + '\n')
            file.write('\n')

            file.write('## ' + str(log.report_log09["ITEM"]) + '\n')
            # file.write('#### ' + 'Result:    ' + str(log.report_log09[femb_id]["Result"]) + '\n\n')
            # for key, value in log.report_log09[femb_id].items():
            #     file.write('#### ' + f"{key}: {value}\n")
            info = dict_to_markdown_table(log.report_log09[femb_id], KEY = "4.2 DIFF Current Measurement", VALUE = "PWRVALUE")
            file.write(info + '\n')
            file.write('\n')

            if Rail:
                file.write('## ' + str(log.report_log10["ITEM"]) + '\n')
                # file.write('#### ' + 'Result:    ' + str(log.report_log10[femb_id]["Result"]) + '\n\n')
                # for key, value in log.report_log10[femb_id].items():
                #     file.write('#### ' + f"{key}: {value}\n")
                info = dict_to_markdown_table(log.report_log10[femb_id], KEY = "4.3 DIFF Power Rail", VALUE = "Horizontal")
                file.write(info + '\n')

# 05        PART 05 Monitoring Path Measurement
            if (log.report_log111[femb_id]["Result"] == True):
                Head05 = '## ' + '<span style="color: green;">' + 'PART 05 Monitoring Path Measurement' + '    < Pass >' + '</span>'  + '\n'
            else:
                Head05 = '## ' + '<span style="color: red;">' + 'PART 05 Monitoring Path Measurement' + '{} | Fail'.format(femb_id) + '</span>' + '\n'
            file.write(Head05 + '\n')

            file.write('## ' + str(log.report_log11["ITEM"]) + '\n')
            info = dict_to_markdown_table(log.report_log11[femb_id], KEY = "Monitor Path", VALUE = "MonPath")
            file.write(info + '\n')
            file.write('\n')

        print("file_saved")
'''