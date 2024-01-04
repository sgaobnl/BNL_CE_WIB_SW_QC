import components.assembly_log as log
import subprocess


#================   Final Report    ===================================

def dict_to_markdown_table(dictionary, KEY = "KEY", VALUE = "VALUE"):
    # 获取字典的键和值
    keys = list(dictionary.keys())
    values = list(dictionary.values())

    if VALUE == "PWRVALUE":
        # 构建表格头部
        table = "| {} | {} |\n| --- | --- | --- | --- | --- |\n".format(KEY, " | | | ")
    else:
        table = "| {} | {} |\n| --- | --- |\n".format(KEY, VALUE)

    # 构建表格内容
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

        log.final_status[femb_id]["item2"] = log.report_log02[femb_id]["Result"]
        log.final_status[femb_id]["item3"] = log.report_log03[femb_id]["Result"]
        log.final_status[femb_id]["item4"] = log.report_log04[femb_id]["Result"]
        log.final_status[femb_id]["item5"] = log.report_log05[femb_id]["Result"]
        #log.final_status[femb_id]["item6"] = log.report_log06[femb_id]["Result"]
        log.final_status[femb_id]["item7"] = log.report_log07[femb_id]["Result"]
        log.final_status[femb_id]["item8"] = log.report_log08[femb_id]["Result"]
        #log.final_status[femb_id]["item9"] = log.report_log09[femb_id]["Result"]

        all_true[femb_id] = all(value for value in log.final_status[femb_id].values())

        if all_true[femb_id]:
            print("FEMB ID {}\t PASS\t ALL ASSEMBLY CHECKOUT".format(fembNo['femb%d'%ifemb]))
        else:
            print("femb id {}\t faild\t the assembly checkout".format(fembNo['femb%d' % ifemb]))
    print("\n\n")
    print("Detail for Issues")

    for ifemb in fembs:
        femb_id = "FEMB ID {}".format(fembNo['femb%d' % ifemb])
        dict_list = [log.report_log02, log.report_log03, log.report_log04, log.report_log05, log.report_log06, log.report_log07, log.report_log08, log.report_log09]
        issue_note = ""
        if all_true[femb_id]:
            pass
            summary = "FEMB # {}\t      PASS\t    ALL ASSEMBLY CHECKOUT".format(fembNo['femb%d' % ifemb])
            note = "### See the Report"
        else:
            print(femb_id)
            summary = "femb id {}\t      faild\t the assembly checkout".format(fembNo['femb%d' % ifemb])
            for dict in dict_list:
                if dict[femb_id]["Result"] == False:
                    print(dict["ITEM"])
                    issue_note += dict["ITEM"]
                    for key, value in dict[femb_id].items():
                        print(f"{key}: {value}")
                        issue_note += f"{key}: {value}"
            note = "### Here is the issue: \n" + "issue_note"



        fpmd = datareport[ifemb] + 'report_FEMB_{}.md'.format(fembNo['femb%d' % ifemb])

        with open(fpmd, 'w', encoding = "utf-8") as file:
            # file.write('')
            file.write('\n')
            file.write('\n')
            file.write('# ' + summary + '\n')
            file.write('### ' + "Configuration:" + '\n')
            file.write('### ' + "    14 mV/fC;   2 us;  200 mV; SE, DIFF;" + '\n')
            file.write('\n')
            file.write('\n')
            file.write(note + '\n')
            file.write('\n')
            file.write('\n')

# 01        Print <Input Information>
            file.write('## PART 01 INPUT INFORMATION' + '\n')
            # file.write('## ' + str(log.report_log01["ITEM"]) + '\n')
            info = dict_to_markdown_table(log.report_log01["Detail"])
            file.write(info + '\n')

# 02        Print <Initial test Result>
            if (log.report_log02[femb_id]["Result"] == True) and (log.report_log03[femb_id]["Result"] == True):
                Head02 = '## ' + '<span style="color:blue;">' + 'PART 02 Initial Test' + '    |    < Pass >' + '</span>'  + '\n'
            else:
                Head02 = '## ' + '<span style="color:red;">' + 'PART 02 Initial Test' + ' | Fail' + '</span>' + '\n'
            file.write(Head02 + '\n')
            file.write('#### ' + str(log.report_log02["ITEM"]) + '\n')
            info = dict_to_markdown_table(log.report_log02[femb_id], KEY = "Initial Current Measurement", VALUE = "VALUE")
            file.write(info + '\n')

            file.write('#### ' + str(log.report_log03["ITEM"]) + '\n')
            info = dict_to_markdown_table(log.report_log03[femb_id], KEY = "Initial Register Check", VALUE = "VALUE")
            file.write(info + '\n')

# 03        Print <SE OFF RMS, PED, Pulse, Power Current, Power Rail>
            file.write('## ' + 'PART 03 SE Pulse Measurement' + '\n')
            file.write('#### ' + str(log.report_log04["ITEM"]) + '\n')
            info = dict_to_markdown_table(log.report_log04[femb_id], KEY = "SE Pulse Measurement", VALUE = "VALUE")
            file.write("![ped](./ped_Raw_SE_200mVBL_14_0mVfC_2_0us_0x00.png)" + "![rms](./rms_Raw_SE_200mVBL_14_0mVfC_2_0us_0x00.png)" + "\n")
            file.write(info + '\n')

            file.write('#### ' + str(log.report_log05["ITEM"]) + '\n')
            info = dict_to_markdown_table(log.report_log05[femb_id], KEY = "SE Current Measurement", VALUE = "PWRVALUE")
            file.write(info + '\n')


            file.write('## ' + str(log.report_log06["ITEM"]) + '\n')
            info = dict_to_markdown_table(log.report_log06[femb_id], KEY = "SE Power Rail", VALUE = "PRail_VALUE")
            file.write(info + '\n')


            file.write('## ' + str(log.report_log07["ITEM"]) + '\n')
            info = dict_to_markdown_table(log.report_log07[femb_id], KEY = "3.4 SE Pulse Response", VALUE = "VALUE")
            file.write("![ped](./pulse_Raw_SE_900mVBL_14_0mVfC_2_0us_0x10.bin.png)" + "\n")
            file.write(info + '\n')



            # file.write('## ' + str(log.report_log07["ITEM"]) + '\n')
            # file.write('#### ' + 'Result:    ' + str(log.report_log07[femb_id]["Result"]) + '\n\n')
            # for key, value in log.report_log07[femb_id].items():
            #     file.write('#### ' + f"{key}: {value}\n")
            # file.write("![ped](./pulse_Raw_SE_900mVBL_14_0mVfC_2_0us_0x10.bin.png)")
            # file.write('\n')
# 04        Print <DIFF RMS, PED, Pulse, Power Current, Power Rail>
            file.write('## ' + str(log.report_log08["ITEM"]) + '\n')
            file.write('#### ' + 'Result:    ' + str(log.report_log08[femb_id]["Result"]) + '\n\n')
            for key, value in log.report_log08[femb_id].items():
                file.write('#### ' + f"{key}: {value}\n")
            file.write("![ped](./pulse_Raw_DIFF_900mVBL_14_0mVfC_2_0us_0x10.png)")
            file.write('\n')

            file.write('## ' + str(log.report_log09["ITEM"]) + '\n')
            file.write('#### ' + 'Result:    ' + str(log.report_log09[femb_id]["Result"]) + '\n\n')
            for key, value in log.report_log09[femb_id].items():
                file.write('#### ' + f"{key}: {value}\n")
            file.write("![ped](./MON_PWR_DIFF_200mVBL_14_0mVfC_2_0us_0x00.png)")
            file.write('\n')

            file.write('## ' + str(log.report_log10["ITEM"]) + '\n')
            file.write('#### ' + 'Result:    ' + str(log.report_log10[femb_id]["Result"]) + '\n\n')
            for key, value in log.report_log10[femb_id].items():
                file.write('#### ' + f"{key}: {value}\n")
            #file.write("![ped](./MON_PWR_DIFF_200mVBL_14_0mVfC_2_0us_0x00.png)")
            file.write('\n')


        # with open(fpmd, 'r', encoding='utf-8') as file:
        #     markdown_content = file.read()
        #
        # command = f'pandoc -s -f markdown -t html'
        # process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        # html_content, error = process.communicate(input=markdown_content.encode('utf-8'))
        #
        # html_file_path = 'report_FEMB_{}.html'.format(fembNo['femb%d' % ifemb])
        # with open(html_file_path, 'w', encoding='utf-8') as html_file:
        #     html_file.write(html_content.decode('utf-8'))

        # inputfile = "# Hello\nThis is a *Markdown* example."
        # inputfile = "# Hello\nThis is a *Markdown* example."
        # output_html_file = datareport[ifemb] + "output.html"
        # with open(fpmd, "r", encoding = "utf-8") as md_file:
        #     markdown_content = md_file.read()
        # html_output = markdown.markdown(markdown_content)
        # print(html_output)
        # with open(output_html_file, 'w', encoding = "utf-8") as html_file:
        #     html_file.write((html_output))

        print("file_saved")
