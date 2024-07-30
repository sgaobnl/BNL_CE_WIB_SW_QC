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
    for ifemb in fembs:
        femb_id = "FEMB ID {}".format(fembNo['femb%d' % ifemb])

        log.final_status[femb_id]["item2"] = log.report_log021[femb_id]["Result"]
        log.final_status[femb_id]["item3"] = log.report_log03[femb_id]["Result"]
        log.final_status[femb_id]["item4"] = log.report_log04[femb_id]["Result"]
        log.final_status[femb_id]["item5"] = log.report_log051[femb_id]["Result"]
        log.final_status[femb_id]["item6"] = log.report_log061[femb_id]["Result"]
        log.final_status[femb_id]["item7"] = log.report_log07[femb_id]["Result"]
        log.final_status[femb_id]["item8"] = log.report_log08[femb_id]["Result"]
        log.final_status[femb_id]["item9"] = log.report_log091[femb_id]["Result"]
        log.final_status[femb_id]["item10"] = log.report_log101[femb_id]["Result"]
        log.final_status[femb_id]["Monitor_Path"] = log.report_log111[femb_id]["Result"]
        #log.final_status[femb_id]["item9"] = log.report_log09[femb_id]["Result"]

        all_true[femb_id] = all(value for value in log.final_status[femb_id].values())

        if all_true[femb_id]:
            print("FEMB ID {}\t N{} PASS\t ALL ASSEMBLY CHECKOUT".format(fembNo['femb%d'%ifemb], ifemb))
        else:
            print("femb id {}\t N{} faild\t the assembly checkout".format(fembNo['femb%d' % ifemb], ifemb))
    print("\n\n")
    print("Detail for Issues")

    for ifemb in fembs:
        femb_id = "FEMB ID {}".format(fembNo['femb%d' % ifemb])
        dict_list = [log.report_log021, log.report_log03, log.report_log04, log.report_log051, log.report_log061, log.report_log07, log.report_log08, log.report_log091, log.report_log101, log.report_log111]
        issue_note = ""
        if all_true[femb_id]:
            pass
            summary = "<span style='color: green;'>" + "FEMB # {}\t      PASS\t    ALL ASSEMBLY CHECKOUT".format(fembNo['femb%d' % ifemb]) + "</span>"
            note = "### See the Report"
            status = 'P'
        else:
            print(femb_id)
            summary = "<span style='color: red;'>" + "femb id {}\t      faild\t the assembly checkout".format(fembNo['femb%d' % ifemb]) + "</span>"
            status = 'P'
            for dict in dict_list:
                if dict[femb_id]["Result"] == False:
                    print(dict[femb_id])
                    issue_note += "{} \n".format(dict[femb_id])
            note = "### Here is the issue: \n" + str(issue_note) + "\n"

        fpmd = datareport[ifemb] + 'report_FEMB_{}_N{}_{}.md'.format(fembNo['femb%d' % ifemb], ifemb ,status)

        with open(fpmd, 'w', encoding = "utf-8") as file:
            file.write('\n')
            file.write('\n')
            file.write('# ' + summary + '\n')

            file.write('\n')

            file.write('\n')

#   Begin   lke@bnl.gov

# 01        Print <Input Information>
            Head01 = '### ' + 'PART 01 INPUT INFORMATION' + '\n'
            file.write(Head01 + '\n')
            info = dict_to_markdown_table(log.report_log01["Detail"], VALUE = "Horizontal")
            file.write(info + '\n')
            file.write('### ' + "Configuration:" + '\t')
            file.write('   ' + "    14 mV/fC;   2 us;  200 mV; SE, DIFF;" + '\n')
            file.write('\n')
            file.write(note + '\n')
            file.write('\n')
            file.write('\n');            file.write('------');            file.write('\n')

# 02        Print <Initial test Result>
            if (log.report_log021[femb_id]["Result"] == True) and (log.report_log03[femb_id]["Result"] == True):
                Head02 = '### ' + '<span style="color: green;">' + 'PART 02 Initial Test' + '    < Pass >' + '</span>'  + '\n'
            else:
                Head02 = '### ' + '<span style="color: red;">' + 'PART 02 Initial Test' + ' | Fail' + '</span>' + '\n'
            file.write(Head02 + '\n')
            file.write('#### ' + str(log.report_log02["ITEM"]) + '\n')
            info = dict_to_markdown_table(log.report_log02[femb_id], KEY = "Initial Current Measurement", VALUE = "PWRVALUE")
            file.write(info + '\n')

            file.write('#### ' + str(log.report_log03["ITEM"]) + '\n')
            info = dict_to_markdown_table(log.report_log03[femb_id], KEY = "Initial Register Check", VALUE = "Horizontal")
            file.write(info + '\n')

# 03        Print <SE OFF RMS, PED, Pulse, Power Current, Power Rail>
            if (log.report_log04[femb_id]["Result"] == True) and (log.report_log051[femb_id]["Result"] == True) and (log.report_log061[femb_id]["Result"] == True):
                Head02 = '### ' + '<span style="color: green;">' + 'PART 03 SE Interface Measurement' + '    < Pass >' + '</span>'  + '\n'
            else:
                Head02 = '### ' + '<span style="color: red;">' + 'PART 03 SE Interface Measurement' + ' | Fail' + '</span>' + '\n'
            file.write(Head02 + '\n')
            file.write('#### ' + str(log.report_log04["ITEM"]) + '\n')
            info = dict_to_markdown_table(log.report_log04[femb_id], KEY = "SE Noise Measurement", VALUE = "VALUE")
            file.write("![ped](./ped_Raw_SE_200mVBL_14_0mVfC_2_0us_0x00.png)" + "\n\n")
            file.write(info + '\n')
            # "![rms](./rms_Raw_SE_200mVBL_14_0mVfC_2_0us_0x00.png)" +
            file.write('#### ' + str(log.report_log05["ITEM"]) + '\n')
            info = dict_to_markdown_table(log.report_log05[femb_id], KEY = "SE Current Measurement", VALUE = "PWRVALUE")
            file.write(info + '\n')


            file.write('#### ' + str(log.report_log06["ITEM"]) + '\n')
            info = dict_to_markdown_table(log.report_log06[femb_id], KEY = "SE Power Rail", VALUE = "Horizontal")
            file.write(info + '\n')


            file.write('#### ' + str(log.report_log07["ITEM"]) + '\n')
            info = dict_to_markdown_table(log.report_log07[femb_id], KEY = "SE Pulse Response", VALUE = "VALUE")
            file.write("![ped](./pulse_Raw_SE_900mVBL_14_0mVfC_2_0us_0x10.bin.png)" + "\n\n")
            file.write(info + '\n')



            # file.write('## ' + str(log.report_log07["ITEM"]) + '\n')
            # file.write('#### ' + 'Result:    ' + str(log.report_log07[femb_id]["Result"]) + '\n\n')
            # for key, value in log.report_log07[femb_id].items():
            #     file.write('#### ' + f"{key}: {value}\n")
            # file.write("![ped](./pulse_Raw_SE_900mVBL_14_0mVfC_2_0us_0x10.bin.png)")
            # file.write('\n')
# 04        Print <DIFF RMS, PED, Pulse, Power Current, Power Rail>
            if (log.report_log08[femb_id]["Result"] == True) and (log.report_log091[femb_id]["Result"] == True) and (log.report_log101[femb_id]["Result"] == True):
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
