import components.assembly_log as log
import subprocess


#================   Final Report    ===================================
# LKE@BNL.GOV

def dict_to_html_table(dictionary, KEY="KEY", VALUE="RECORD"):
    keys = list(dictionary.keys())
    values = list(dictionary.values())
    html = "<table border='1' style='border-collapse: collapse;'>"
    if VALUE == "PWRVALUE":
        # 確認是 list 的形式 → 使用多欄 table 輸出
        max_len = max(len(v) if isinstance(v, list) else 1 for v in values)
        html += f"<tr><th>{KEY}</th>" + "".join(f"<th>CH{i}</th>" for i in range(max_len)) + "</tr>\n"

        for key, value in zip(keys, values):
            if isinstance(value, list):
                html += f"<tr><td>{key}</td>" + "".join(f"<td>{v}</td>" for v in value) + "</tr>\n"
            else:
                html += f"<tr><td>{key}</td><td colspan='{max_len}'>{value}</td></tr>\n"

    elif VALUE == "MonPath":
    # 多欄表格：KEY 是行名，每個 value 是 list，顯示為一整列
        max_len = max(len(v) if isinstance(v, list) else 1 for v in values)
        html += f"<tr><th>{KEY}</th>" + "".join(f"<th>CH{i}</th>" for i in range(max_len)) + "</tr>\n"
        for key, value in zip(keys, values):
            if isinstance(value, list):
                html += f"<tr><td>{key}</td>" + "".join(f"<td>{v}</td>" for v in value) + "</tr>\n"
            else:
                html += f"<tr><td>{key}</td><td colspan='{max_len}'>{value}</td></tr>\n"

    elif VALUE == "Horizontal":
        html += "<tr>" + "".join(f"<th>{key}</th>" for key in keys) + "</tr>"
        html += "<tr>" + "".join(f"<td>{str(dictionary[key]).strip()}</td>" for key in keys) + "</tr>"
    else:
        html += f"<tr><th>{KEY}</th><th>{VALUE}</th></tr>"
        for key, value in zip(keys, values):
            html += f"<tr><td>{key}</td><td>{value}</td></tr>"
    html += "</table>"
    return html


def final_report(datareport, fembs, fembNo, Rail=True):
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
        if Rail:
            log.final_status[femb_id]["item6"] = log.report_log061[femb_id]["Result"]
        log.final_status[femb_id]["item7"] = log.report_log07[femb_id]["Result"]
        log.final_status[femb_id]["item8"] = log.report_log08[femb_id]["Result"]
        log.final_status[femb_id]["item9"] = log.report_log091[femb_id]["Result"]
        if Rail:
            log.final_status[femb_id]["item10"] = log.report_log101[femb_id]["Result"]
        log.final_status[femb_id]["Monitor_Path"] = log.report_log111[femb_id]["Result"]

        all_true[femb_id] = all(value for value in log.final_status[femb_id].values())

        if all_true[femb_id]:
            print("FEMB ID {}\t Slot {} PASS\t ALL ASSEMBLY CHECKOUT".format(fembNo['femb%d' % ifemb], ifemb))
        else:
            print("femb id {}\t Slot {} faild\t the checkout".format(fembNo['femb%d' % ifemb], ifemb))
    print("\n\n")
    print("Here is the Summary")

    for ifemb in fembs:
        femb_id = "FEMB ID {}".format(fembNo['femb%d' % ifemb])

        # 根据Rail变量确定需要检查的日志列表
        if Rail:
            dict_list = [
                log.report_log021, log.report_log03, log.report_log04, log.report_log051,
                log.report_log061, log.report_log07, log.report_log08, log.report_log091,
                log.report_log101, log.report_log111
            ]
        else:
            dict_list = [
                log.report_log021, log.report_log03, log.report_log04, log.report_log051,
                log.report_log07, log.report_log08, log.report_log091, log.report_log111
            ]

        issue_note = ""
        if all_true[femb_id]:
            # 若所有测试通过，则标记为绿色通过状态
            summary = "<span style='color: green;'>" + "FEMB SN {}\t      PASS\t  CHECKOUT".format(fembNo['femb%d' % ifemb]) + "</span>"
            note = "### Here is the Summary"
            status = 'P'
            fhtml = datareport[ifemb] + 'report_FEMB_{}_Slot{}_{}.html'.format(fembNo['femb%d' % ifemb], ifemb, status)
        else:
            # 若存在测试失败，则标记为红色失败状态，并输出问题详情
            print(femb_id)
            summary = "<span style='color: red;'>" + "femb id {}\t      faild\t checkout".format(fembNo['femb%d' % ifemb]) + "</span>"
            status = 'F'  # 注意：此处原代码为'P'，可能是笔误，应检查是否应设为'F'

            for dict in dict_list:
                if dict[femb_id]["Result"] == False:
                    print(dict[femb_id])
                    issue_note += "{} \n".format(dict[femb_id])

            note = "### Here is the issue: \n" + str(issue_note) + "\n"
        fhtml = datareport[ifemb] + 'report_FEMB_{}_Slot{}_{}.html'.format(fembNo['femb%d' % ifemb], ifemb, status)
        # fhtml = datareport[ifemb] + 'report_FEMB_{}_Slot{}_{}.html'.format(fembNo['femb%d' % ifemb], ifemb, status)
        with open(fhtml, 'w', encoding="utf-8") as file:
            file.write('<!DOCTYPE html>\n<html>\n<head>\n<meta charset="utf-8">\n<title>FEMB Report</title>\n</head>\n<body>\n')
            file.write('<br><br>\n')

            # Summary（带颜色的标题）
            file.write(f'<h1>{summary}</h1>\n')
            file.write('<br>\n<br>\n')

            # Part 01：输入信息标题
            Head01 = '<h3>PART 01 INPUT INFORMATION</h3>\n'
            file.write(Head01)

            # 使用HTML版本的表格写入 input info
            info = dict_to_html_table(log.report_log01["Detail"], VALUE="Horizontal")
            file.write(info + '<br>\n')

            text_line = "{}".format(femb_id)
            file.write(text_line + '<br>\n')
            text_line = "COLDATA_SN_CD0: {}".format(log.report_log00[femb_id]["COLDATA_SN_CD0"])
            file.write(text_line + '<br>\n')
            text_line = "COLDATA_SN_CD1: {}".format(log.report_log00[femb_id]["COLDATA_SN_CD1"])
            file.write(text_line + '<br>\n')

            # Note（问题详情 or 通用说明）
            file.write('<div>\n' + note.replace('###', '<h3>').replace('\n', '<br>\n') + '\n</div>\n')

            # 分割线
            file.write('<hr>\n')

            file.write('</body>\n</html>\n')

            # 02 打印 <初始测试结果>
            if (log.report_log021[femb_id]["Result"] == True) and (log.report_log03[femb_id]["Result"] == True):
                Head02 = '<h3><span style="color: green;">PART 02 POR Measurement &nbsp;&nbsp; &lt; Pass &gt;</span></h3>\n'
            else:
                Head02 = '<h3><span style="color: red;">PART 02 POR Measurement &nbsp;&nbsp; | Fail</span></h3>\n'

            file.write(Head02)

            # 写入 Initial Current Measurement 的标题
            file.write(f'<h4>{log.report_log02["ITEM"]}</h4>\n')

            # 转换表格为 HTML 表格格式
            info = dict_to_html_table(log.report_log02[femb_id], KEY="2.1 Initial Current Measurement", VALUE="PWRVALUE")
            file.write(info + '<br>\n')

            # 写入 Initial Register Check 的标题
            file.write(f'<h4>{log.report_log03["ITEM"]}</h4>\n')

            # 转换表格为 HTML 表格格式
            info = dict_to_html_table(log.report_log03[femb_id], KEY="Initial Register Check", VALUE="Horizontal")
            file.write(info + '<br>\n')

            # 03 打印 <SE OFF RMS, PED, Pulse, Power Current, Power Rail>
            if Rail:
                if (log.report_log04[femb_id]["Result"] == True) and (log.report_log051[femb_id]["Result"] == True) and (log.report_log061[femb_id]["Result"] == True):
                    Head03 = '<h3><span style="color: green;">PART 03 SE OFF Measurement &nbsp;&nbsp; &lt; Pass &gt;</span></h3>\n'
                else:
                    Head03 = '<h3><span style="color: red;">PART 03 SE OFF Measurement &nbsp;&nbsp; | Fail</span></h3>\n'
            else:
                if (log.report_log04[femb_id]["Result"] == True) and (log.report_log051[femb_id]["Result"] == True):
                    Head03 = '<h3><span style="color: green;">PART 03 SE OFF Measurement &nbsp;&nbsp; &lt; Pass &gt;</span></h3>\n'
                else:
                    Head03 = '<h3><span style="color: red;">PART 03 SE OFF Measurement &nbsp;&nbsp; | Fail</span></h3>\n'

            file.write(Head03)

            # 写入 SE Noise Measurement 标题
            file.write(f'<h4>{log.report_log04["ITEM"]}</h4>\n')

            # 噪声图像插入 (ped + rms)
            file.write('<div>\n')
            file.write('<img src="./ped_Raw_SE_200mVBL_14_0mVfC_2_0us_0x00.png" alt="ped" style="max-width: 45%; margin-right: 10px;">\n')
            file.write('<img src="./rms_Raw_SE_200mVBL_14_0mVfC_2_0us_0x00.png" alt="rms" style="max-width: 45%;">\n')
            file.write('</div><br>\n')

            # 表格输出：SE Noise Measurement
            info = dict_to_html_table(log.report_log04[femb_id], KEY="3.1 Noise Measurement  200 mVBL  14 mV/fC  2 us", VALUE="VALUE")
            file.write(info + '<br>\n')

            # 写入 SE Current Measurement 标题
            file.write(f'<h4>{log.report_log05["ITEM"]}</h4>\n')
            info = dict_to_html_table(log.report_log05[femb_id], KEY="3.2 SE OFF Power Measurement", VALUE="PWRVALUE")
            file.write(info + '<br>\n')

            # 若包含 Rail 测试，写入 Power Rail 信息
            if Rail:
                file.write(f'<h4>{log.report_log06["ITEM"]}</h4>\n')
                info = dict_to_html_table(log.report_log06[femb_id], KEY="3.3 SE OFF LDO Measurement / mV", VALUE="Horizontal")
                file.write(info + '<br>\n')

            # 写入 Pulse Response 测试项
            file.write(f'<h4>{log.report_log07["ITEM"]}</h4>\n')

            # Pulse 图像插入
            file.write('<div>\n')
            file.write('<img src="./pulse_Raw_SE_900mVBL_14_0mVfC_2_0us_0x10.bin.png" alt="pulse response" style="max-width: 90%;">\n')
            file.write('</div><br>\n')

            info = dict_to_html_table(log.report_log07[femb_id], KEY="3.4 SE OFF Pulse Response [900mV 14mV/fC 2us]", VALUE="VALUE")
            file.write(info + '<br>\n')

            # 04 打印 <DIFF RMS, PED, Pulse, Power Current, Power Rail>
            if Rail:
                if (log.report_log08[femb_id]["Result"] == True) and (log.report_log091[femb_id]["Result"] == True) and (log.report_log101[femb_id]["Result"] == True):
                    Head04 = '<h3><span style="color: green;">PART 04 DIFF Measurement &nbsp;&nbsp; &lt; Pass &gt;</span></h3>\n'
                else:
                    Head04 = '<h3><span style="color: red;">PART 04 DIFF Measurement &nbsp;&nbsp; | Fail</span></h3>\n'
            else:
                if (log.report_log08[femb_id]["Result"] == True) and (log.report_log091[femb_id]["Result"] == True):
                    Head04 = '<h3><span style="color: green;">PART 04 DIFF Measurement &nbsp;&nbsp; &lt; Pass &gt;</span></h3>\n'
                else:
                    Head04 = '<h3><span style="color: red;">PART 04 DIFF Measurement &nbsp;&nbsp; | Fail</span></h3>\n'

            file.write(Head04)

            # 4.1 DIFF Pulse Measurement
            file.write(f'<h2>{log.report_log08["ITEM"]}</h2>\n')
            file.write('<div>\n')
            file.write('<img src="./pulse_Raw_DIFF_900mVBL_14_0mVfC_2_0us_0x10.png" alt="diff pulse" style="max-width: 90%;">\n')
            file.write('</div><br>\n')

            info = dict_to_html_table(log.report_log08[femb_id], KEY="4.1 DIFF Pulse Measurement at 900mV, 14mV/fC, 2us", VALUE="VALUE")
            file.write(info + '<br>\n')

            # 4.2 DIFF Current Measurement
            file.write(f'<h2>{log.report_log09["ITEM"]}</h2>\n')
            info = dict_to_html_table(log.report_log09[femb_id], KEY="4.2 DIFF Power Measurement", VALUE="PWRVALUE")
            file.write(info + '<br>\n')

            # 4.3 DIFF Power Rail（仅在 Rail 为 True 时写入）
            if Rail:
                file.write(f'<h2>{log.report_log10["ITEM"]}</h2>\n')
                info = dict_to_html_table(log.report_log10[femb_id], KEY="4.3 DIFF LDO Measurement / mV", VALUE="Horizontal")
                file.write(info + '<br>\n')



            # 05 PART 05 Monitoring Path Measurement  # Lingyun Ke set
            if log.report_log111[femb_id]["Result"] == True:
                Head05 = f'<h2><span style="color: green;">PART 05 Monitoring Measurement &nbsp;&nbsp; &lt; Pass &gt;</span></h2>\n'
            else:
                Head05 = f'<h2><span style="color: red;">PART 05 Monitoring Measurement {femb_id} | Fail</span></h2>\n'

            file.write(Head05)

            # 写入该项标题
            file.write(f'<h2>{log.report_log11["ITEM"]}</h2>\n')

            # 表格：监测路径测量数据
            info = dict_to_html_table(log.report_log11[femb_id], KEY="Monitor Path", VALUE="MonPath")
            file.write(info + '<br>\n')
            line = "------\n"
            file.write(line + '<br>\n')
            file.write('lke@bnl.gov' + '<br>\n')

            print("Checkout Report Saved")
