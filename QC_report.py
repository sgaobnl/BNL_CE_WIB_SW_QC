import pickle
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
import csv
import sys
import time
import glob
from QC_tools import ana_tools
import QC_check
from fpdf import FPDF
import argparse
import Path as newpath
import components.item_report as item_report
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
from PIL import Image
import QC_components.qc_a_function as a_func
import QC_components.qc_log as log
import QC_components.All_Report as a_repo

class QC_reports:

    def __init__(self, fdir, fembs=[]):
        savedir = newpath.report_dir_RTQC
        #self.datadir = "./tmp_data/"+fdir+"/"
        self.datadir = newpath.data_dir_RTQC + fdir + "/"
#            savedir = "/nfs/hothstor1/towibs/tmp/FEMB_QC_reports/QC/"+fdir+"/"
#            self.datadir = "/nfs/hothstor1/towibs/tmp/FEMB_QC_data/QC/"+fdir+"/"
        self.report_source_doc = 0
        fp = self.datadir+"logs_env.bin"
        with open(fp, 'rb') as fn:
            logs = pickle.load(fn)
        log.report_log00 = dict(logs)
        logs["datadir"]=self.datadir
        self.logs= logs
        self.fembsName={}
        self.fembsID={}
        if fembs:
            self.fembs = fembs
            for ifemb in fembs:
                self.fembsName[f'femb{ifemb}'] = logs['femb id'][f'femb{ifemb}']
                self.fembsID[f'femb{ifemb}'] = logs['femb id'][f'femb{ifemb}'][1:]
        else:
            # self.fembsID = logs['femb id']
            self.fembs=[]
            for key,value in logs['femb id'].items():
                self.fembs.append(int(key[-1]))
            for ifemb in self.fembs:
                self.fembsName[f'femb{ifemb}'] = logs['femb id'][f'femb{ifemb}']
                self.fembsID[f'femb{ifemb}'] = logs['femb id'][f'femb{ifemb}'][1:]
        self.savedir={}
        print("Will analyze the following fembs: ", self.fembs)
        ##### create results dir for each FEMB #####
        for ifemb in self.fembs:
            # self.fembsID[f'femb{ifemb}'] = self.fembsName[f'femb{ifemb}'][1:]
            fembid = self.fembsID[f'femb{ifemb}']
            fembName = self.fembsName[f'femb{ifemb}']
            one_savedir = savedir+"FEMB{}_{}_{}".format(fembName, logs["env"], logs["toytpc"])
            n=1
            while (os.path.exists(one_savedir)):
                if n==1:
                    one_savedir = one_savedir + "_R{:03d}".format(n)
                else:
                    one_savedir = one_savedir[:-3] + "{:03d}".format(n)
                n=n+1
                if n>20:
                    raise Exception("There are more than 20 folders...")
            try:
                os.makedirs(one_savedir)
            except OSError:
                print ("Error to create folder %s"%one_savedir)
                sys.exit()
            self.savedir[ifemb]=one_savedir+"/"
            fp = self.savedir[ifemb] + "logs_env.bin"
            with open(fp, 'wb') as fn:
                pickle.dump(self.logs, fn)

    def CreateDIR(self, fdir):
        for ifemb in self.fembs:
            fp = self.savedir[ifemb] + fdir + "/"
            if not os.path.exists(fp):
                try:
                    os.makedirs(fp)
                except OSError:
                    print ("Error to create folder %s"%fp)
                    sys.exit()

    def Gather_PNG_PDF(self, fdir):
        #input_folder_path = fdir + '/path/to/your/png/files'
        output_pdf_path = fdir + '/report.pdf'
        png_files = [f for f in os.listdir(fdir) if f.endswith('.png')]
        c = canvas.Canvas(output_pdf_path, pagesize=letter)
        #image_count = 0  # 记录已经处理的图像数量
        current_page = 0  # 记录当前页数
        for i, png_file in enumerate(png_files):
            png_path = os.path.join(fdir, png_file)
            img = Image.open(png_path)
            # 通过 drawImage 将图像添加到 PDF 文件
            remainder = i%4
            c.drawImage(png_path, 0, 600-remainder*160, width=img.width*160/img.height, height=40 * 4)
            if remainder == 3:
                c.showPage()  # 开始新的一页
            current_page += 1
        c.save()

# 1     Power Consumption
# ================================================================================================
    def PWR_consumption_report(self):
        log.test_label.append(1)
        qc = ana_tools()
        self.CreateDIR("PWR_Meas")
        datadir = self.datadir+"PWR_Meas/"
#     01    01_11 SE Power   01_12 SE Pulse Measure   01_13 SE Power Rail Regular
#     SE Power Measurement      Power
        f_pwr = datadir+"PWR_SE_OFF_200mVBL_14_0mVfC_2_0us_0x00.bin"
        with open(f_pwr, 'rb') as fn:
            pwr_meas = pickle.load(fn)[1]
        for ifemb in range(len(self.fembs)):
            femb_id = "FEMB ID {}".format(self.fembsID['femb%d' % self.fembs[ifemb]])
            initial_power = a_func.power_ana(self.fembs, ifemb, femb_id, pwr_meas, self.logs['env'], '01_11 SE OFF Power Consumption')
            pwr1 = dict(log.tmp_log)
            check1 = dict(log.check_log)
            log.report_log01_11.update(pwr1)
            log.check_log01_11.update(check1)

#     SE Pulse Measurement      Pulse
        f_pl = datadir+"PWR_SE_OFF_pulse_200mVBL_14_0mVfC_2_0us_0x20.bin"
        with open(f_pl, 'rb') as fn:
             rawdata = pickle.load(fn)[0]
        pldata = qc.data_decode(rawdata, self.fembs)
        a_func.pulse_ana(pldata, self.fembs, self.fembsID, self.savedir, "PWR_SE_OFF_200mVBL_14_0mVfC_2_0us", "PWR_Meas/", '01_12 SE Power Pulse')
        # log.report_log01_12.update(se_pulse)
        pulse = dict(log.tmp_log)
        pulse_check = dict(log.check_log)
        log.report_log01_12.update(pulse)
        log.check_log01_12.update(pulse_check)

#     SE Power Rail             Rail
        a_func.monitor_power_rail_analysis("SE_OFF", datadir, self.fembsID, '01_13 SE OFF Power Rail -- Regular')
        power_rail = dict(log.tmp_log)
        power_rail_check = dict(log.check_log)
        log.report_log01_13.update(power_rail)
        log.check_log01_13.update(power_rail_check)



#     SE ON Power Measurement    Power
        f_pwr = datadir+"PWR_SE_ON_200mVBL_14_0mVfC_2_0us_0x00.bin"
        with open(f_pwr, 'rb') as fn:
             pwr_meas = pickle.load(fn)[1]
        for ifemb in range(len(self.fembs)):
            femb_id = "FEMB ID {}".format(self.fembsID['femb%d' % self.fembs[ifemb]])
            initial_power = a_func.power_ana(self.fembs, ifemb, femb_id, pwr_meas, self.logs['env'], '01_21 SE ON Power Consumption')
            pwr1 = dict(log.tmp_log)
            check1 = dict(log.check_log)
            log.report_log01_21.update(pwr1)
            log.check_log01_21.update(check1)

#     SE ON Pulse Measurement      Pulse
        f_pl = datadir+"PWR_SE_ON_pulse_200mVBL_14_0mVfC_2_0us_0x20.bin"
        with open(f_pl, 'rb') as fn:
             rawdata = pickle.load(fn)[0]
        pldata = qc.data_decode(rawdata, self.fembs)
        a_func.pulse_ana(pldata, self.fembs, self.fembsID, self.savedir, "PWR_SE_ON_200mVBL_14_0mVfC_2_0us", "PWR_Meas/", '01_22 SE ON Power Pulse')
        # log.report_log01_12.update(se_pulse)
        pulse = dict(log.tmp_log)
        pulse_check = dict(log.check_log)
        log.report_log01_22.update(pulse)
        log.check_log01_22.update(pulse_check)

#     SE ON Power Rail             Rail
        a_func.monitor_power_rail_analysis("SE_ON", datadir, self.fembsID, '01_23 SE ON Power Rail')
        power_rail = dict(log.tmp_log)
        power_rail_check = dict(log.check_log)
        log.report_log01_23.update(power_rail)
        log.check_log01_23.update(power_rail_check)



#     DIFF Power Measurement    Power
        f_pwr = datadir + "PWR_DIFF_200mVBL_14_0mVfC_2_0us_0x00.bin"
        with open(f_pwr, 'rb') as fn:
            pwr_meas = pickle.load(fn)[1]
        for ifemb in range(len(self.fembs)):
            femb_id = "FEMB ID {}".format(self.fembsID['femb%d' % self.fembs[ifemb]])
            initial_power = a_func.power_ana(self.fembs, ifemb, femb_id, pwr_meas, self.logs['env'], 'DIFF Power Consumption')
            pwr1 = dict(log.tmp_log)
            check1 = dict(log.check_log)
            log.report_log01_31.update(pwr1)
            log.check_log01_31.update(check1)

#     DIFF Pulse Measurement      Pulse
        f_pl = datadir + "PWR_DIFF_pulse_200mVBL_14_0mVfC_2_0us_0x20.bin"
        with open(f_pl, 'rb') as fn:
            rawdata = pickle.load(fn)[0]
        pldata = qc.data_decode(rawdata, self.fembs)
        a_func.pulse_ana(pldata, self.fembs, self.fembsID, self.savedir, "PWR_DIFF_200mVBL_14_0mVfC_2_0us", "PWR_Meas/", 'DIFF Power Pulse')
        # log.report_log01_12.update(se_pulse)
        pulse = dict(log.tmp_log)
        pulse_check = dict(log.check_log)
        log.report_log01_32.update(pulse)
        log.check_log01_32.update(pulse_check)


#     DIFF Power Rail
        power_rail_diff = a_func.monitor_power_rail_analysis("DIFF", datadir, self.fembsID, 'DIFF Power Rail')
        power_rail = dict(log.tmp_log)
        power_rail_check = dict(log.check_log)
        log.report_log01_33.update(power_rail)
        log.check_log01_33.update(power_rail_check)

        # plot Power Measurement
        for ifemb in range(len(self.fembs)):
            femb_id = "FEMB ID {}".format(self.fembsID['femb%d' % self.fembs[ifemb]])
            df = ["SE_OFF", "SE_ON", "DIFF"]
            x = np.arange(0, len(df) * 3, 3)
            width = 0.9
            x1 = x+0.325
            x2 = x
            x3 = x-0.325
            y1 = [log.check_log01_11[femb_id]["LArASIC_I"], log.check_log01_21[femb_id]["LArASIC_I"], log.check_log01_31[femb_id]["LArASIC_I"]]
            plt.bar(x1, y1, width=0.3, label = 'LArASIC_I', color = 'darkred', edgecolor = 'k', zorder = 3)

            plt.plot(x1, [log.check_log01_11[femb_id]["LArASIC_I"]+0.05, log.check_log01_21[femb_id]["LArASIC_I"]+0.05, log.check_log01_31[femb_id]["LArASIC_I"]+0.05], marker='^', linestyle='--', color='darkred')
            y2 = [log.check_log01_11[femb_id]["ColdADC_I"], log.check_log01_21[femb_id]["ColdADC_I"], log.check_log01_31[femb_id]["ColdADC_I"]]
            plt.bar(x2, y2, width=0.35, label='ColdADC_I', color='darkorange', edgecolor='k', zorder=3)
            y3 = [log.check_log01_11[femb_id]["COLDATA_I"], log.check_log01_21[femb_id]["COLDATA_I"], log.check_log01_31[femb_id]["COLDATA_I"]]

            plt.bar(x3, y3, width=0.3, label='COLDATA_I', color='cornflowerblue', edgecolor='k', zorder=3)

            plt.text(0, log.check_log01_11[femb_id]["ColdADC_I"]+0.05, 'P=' + str(round(log.check_log01_11[femb_id]["TPower"],2))+'W \n'+str(round(log.check_log01_11[femb_id]["ColdADC_I"],2)), horizontalalignment='center')
            plt.text(3, log.check_log01_21[femb_id]["ColdADC_I"]+0.05, 'P=' + str(round(log.check_log01_21[femb_id]["TPower"],2))+'W \n'+str(round(log.check_log01_21[femb_id]["ColdADC_I"],2)), horizontalalignment='center')
            plt.text(6, log.check_log01_31[femb_id]["ColdADC_I"]+0.05, 'P=' + str(round(log.check_log01_31[femb_id]["TPower"],2))+'W \n'+str(round(log.check_log01_31[femb_id]["ColdADC_I"],2)), horizontalalignment='center')
            plt.text(0.325, log.check_log01_11[femb_id]["LArASIC_I"]+0.1, str(log.check_log01_11[femb_id]["LArASIC_I"]), horizontalalignment='center')
            plt.text(3.325, log.check_log01_21[femb_id]["LArASIC_I"]+0.1, str(log.check_log01_21[femb_id]["LArASIC_I"]), horizontalalignment='center')
            plt.text(6.325, log.check_log01_31[femb_id]["LArASIC_I"]+0.1, str(log.check_log01_31[femb_id]["LArASIC_I"]), horizontalalignment='center')
            plt.text(-0.3, log.check_log01_11[femb_id]["COLDATA_I"]+0.05, str(log.check_log01_11[femb_id]["COLDATA_I"]), horizontalalignment='center')
            plt.text(2.7, log.check_log01_21[femb_id]["COLDATA_I"]+0.05, str(log.check_log01_21[femb_id]["COLDATA_I"]), horizontalalignment='center')
            plt.text(5.7, log.check_log01_31[femb_id]["COLDATA_I"]+0.05, str(log.check_log01_31[femb_id]["COLDATA_I"]), horizontalalignment='center')
            plt.legend(loc="upper left", ncol=3, shadow=False)
            plt.xticks(x, df, fontsize=10)
            plt.ylabel('Current / A')
            plt.title('Power Consumption')
            plt.ylim(0, 2.2)
            plt.gca().set_facecolor('none')  # set background as transparent
            plt.savefig(self.savedir[self.fembs[ifemb]] + "PWR_Meas/" + 'Power_Total.png', transparent = True)
            plt.close()

# 2     Power cycle test, only in LN2
    def PWR_cycle_report(self):
        log.test_label.append(2)
        if 'RT' in self.logs['env']:
            return
        self.CreateDIR("PWR_Cycle")
        datadir = self.datadir+"PWR_Cycle/"
        qc=ana_tools()
        for i in range(3):
            f_pwr = datadir+"PWR_cycle{}_SE_200mVBL_14_0mVfC_2_0us_0x00.bin".format(i)
            with open(f_pwr, 'rb') as fn:
                 pwr_meas = pickle.load(fn)[1]
            f_pl = datadir+"PWR_cycle{}_SE_200mVBL_14_0mVfC_2_0us_0x20.bin".format(i)
            with open(f_pl, 'rb') as fn:
                 rawdata = pickle.load(fn)[0]
            pldata = qc.data_decode(rawdata, self.fembs)
            for ifemb in self.fembs:
                fp_pwr = self.savedir[ifemb] + "PWR_Cycle/PWR_cycle{}_SE_200mVBL_14_0mVfC_2_0us_pwr_meas".format(i)
                qc.PrintPWR(pwr_meas, ifemb, fp_pwr)
                fp = self.savedir[ifemb] + "PWR_Cycle/"
                qc.GetPeaks(pldata, ifemb, fp, "PWR_cycle{}_SE_200mVBL_14_0mVfC_2_0us".format(i))
        f_pwr = datadir+"PWR_DIFF_200mVBL_14_0mVfC_2_0us_0x00.bin"
        with open(f_pwr, 'rb') as fn:
             pwr_meas = pickle.load(fn)[1]
        f_pl = datadir+"PWR_DIFF_200mVBL_14_0mVfC_2_0us_0x20.bin"
        with open(f_pl, 'rb') as fn:
             rawdata = pickle.load(fn)[0]
        pldata = qc.data_decode(rawdata, self.fembs)
        for ifemb in self.fembs:
            fp_pwr = self.savedir[ifemb] + "PWR_Cycle/PWR_DIFF_200mVBL_14_0mVfC_2_0us_pwr_meas"
            qc.PrintPWR(pwr_meas, ifemb, fp_pwr)
            fp = self.savedir[ifemb] + "PWR_Cycle/"
            qc.GetPeaks(pldata, ifemb, fp, "PWR_DIFF_200mVBL_14_0mVfC_2_0us")
        f_pwr = datadir+"PWR_SE_SDF_200mVBL_14_0mVfC_2_0us_0x00.bin"
        with open(f_pwr, 'rb') as fn:
             pwr_meas = pickle.load(fn)[1]
        f_pl = datadir+"PWR_SE_SDF_200mVBL_14_0mVfC_2_0us_0x20.bin"
        with open(f_pl, 'rb') as fn:
             rawdata = pickle.load(fn)[0]
        pldata = qc.data_decode(rawdata, self.fembs)
        for ifemb in self.fembs:
            fp_pwr = self.savedir[ifemb] + "PWR_Cycle/PWR_SE_SDF_200mVBL_14_0mVfC_2_0us_pwr_meas"
            qc.PrintPWR(pwr_meas, ifemb, fp_pwr)
            fp = self.savedir[ifemb] + "PWR_Cycle/"
            qc.GetPeaks(pldata, ifemb, fp, "PWR_SE_SDF_200mVBL_14_0mVfC_2_0us")
        for ifemb in self.fembs:
            fdir = self.savedir[ifemb] + "PWR_Cycle/"
            fembid = int(self.fembsID[f'femb{ifemb}'])
            # self.GEN_PWR_PDF(fdir, fembid)

#     03 04    01_11 SE Power   01_12 SE Pulse Measure   01_13 SE Power Rail
    def LCCHKPULSE(self, fdir):
        log.test_label.append(3)
        self.CreateDIR(fdir)
        datadir = self.datadir+fdir+"/"
        log_dict = log.report_log3
        qc=ana_tools()
        files = sorted(glob.glob(datadir+"*.bin"), key=os.path.getmtime)  # list of data files in the dir
        dict_list = [log.report_log03_01, log.report_log03_02, log.report_log03_03, log.report_log03_04]
        check_list = [log.check_log03_01, log.check_log03_02, log.check_log03_03, log.check_log03_04]
        i = 0
        for afile in files:
            with open(afile, 'rb') as fn:
                 raw = pickle.load(fn)
            rawdata = raw[0]
            pwr_meas = raw[1]
            pldata = qc.data_decode(rawdata, self.fembs)
            if '\\' in afile:
                fname = afile.split("\\")[-1][:-4]
            else:
                fname = afile.split("/")[-1][:-4]
            label = fname[fname.find("0x20_")+5:]
            a_func.pulse_ana(pldata, self.fembs, self.fembsID, self.savedir, fname, fdir + '/', 'SE_'+label)
            pulse = dict(log.tmp_log)
            pulse_check = dict(log.check_log)
            if "100" in fname:
                dict_list[1].update(pulse)
                check_list[1].update(pulse_check)
            elif "500" in fname:
                dict_list[0].update(pulse)
                check_list[0].update(pulse_check)
            elif "1n" in fname:
                dict_list[3].update(pulse)
                check_list[3].update(pulse_check)
            else:
                dict_list[2].update(pulse)
                check_list[2].update(pulse_check)
            i = i + 1
        for ifemb in range(len(self.fembs)):
            femb_id = "FEMB ID {}".format(self.fembsID['femb%d' % self.fembs[ifemb]])
            plt.figure(figsize=(6, 3))
            x = ["100pA", "500pA", "1nA", "5nA"]
            y1 = [log.check_log03_02[femb_id]["ppk_mean"], log.check_log03_01[femb_id]["ppk_mean"], log.check_log03_04[femb_id]["ppk_mean"], log.check_log03_03[femb_id]["ppk_mean"]]
            yer = [log.check_log03_02[femb_id]["ppk_std"], log.check_log03_01[femb_id]["ppk_std"], log.check_log03_04[femb_id]["ppk_std"], log.check_log03_03[femb_id]["ppk_std"]]
            plt.errorbar(x, y1, yer, fmt='.', capsize=5, color='darkblue', linestyle='-', label='Amplitude')
            y2 = [log.check_log03_02[femb_id]["bbl_mean"], log.check_log03_01[femb_id]["bbl_mean"], log.check_log03_04[femb_id]["bbl_mean"], log.check_log03_03[femb_id]["bbl_mean"]]
            y2er = [log.check_log03_02[femb_id]["bbl_std"], log.check_log03_01[femb_id]["bbl_std"], log.check_log03_04[femb_id]["bbl_std"], log.check_log03_03[femb_id]["bbl_std"]]
            plt.errorbar(x, y2, y2er, fmt='.', capsize=5, color='darkred', linestyle='-', label='Pedestal')
            plt.ylim(0, 16385)
            plt.grid(True, axis='y', linestyle='--')
            for i in range(len(x)):
                plt.text(x[i], y1[i] + 100, f'{round(y1[i], 1)}±{round(yer[i], 1)}', fontsize=10, ha='center', va='bottom', color='darkblue')
                plt.text(x[i], y2[i] + 100, f'{round(y2[i], 1)}±{round(y2er[i], 1)}', fontsize=10, ha='center', va='bottom', color='darkred')
            plt.title('Postive Pulse Response')
            plt.ylabel('ADC Count')
            plt.xlabel('leakage current')
            plt.margins(x=0.15)
            plt.legend(loc="upper left", ncol=3, shadow=False)
            fp = self.savedir[self.fembs[ifemb]] + "Leakage_Current/"
            plt.gca().set_facecolor('none')     # set background as transparent
            plt.savefig(fp + "LC_pulse.png", transparent = True)
            plt.close()



# 04 pulse check
    def CHKPULSE(self, fdir):
        log.test_label.append(4)
        self.CreateDIR(fdir)
        datadir = self.datadir+fdir+"/"
        qc=ana_tools()
        files = sorted(glob.glob(datadir+"*.bin"), key=os.path.getmtime)  # list of data files in the dir
        # dict_list_SE_200 = [log.report_log04_01, log.report_log04_02, log.report_log04_03, log.report_log04_04]
        # check_list_SE_200 = [log.check_log04_01, log.check_log04_02, log.check_log04_03, log.check_log04_04]
        # dict_list_SE_200 = [log.report_log04_01, log.report_log04_02, log.report_log04_03, log.report_log04_04]
        # check_list_SE_200 = [log.check_log04_01, log.check_log04_02, log.check_log04_03, log.check_log04_04]
        i = 0
        for ifemb in range(len(self.fembs)):
            femb_id = "FEMB ID {}".format(self.fembsID['femb%d' % self.fembs[ifemb]])
            log.check_log04_01[femb_id]['Result'] = True

        for afile in files:
            with open(afile, 'rb') as fn:
                raw = pickle.load(fn)
            rawdata = raw[0]
            pwr_meas = raw[1]
# =======================================
            pldata = qc.data_decode(rawdata, self.fembs)
            if '\\' in afile:
                fname = afile.split("\\")[-1][:-4]
            else:
                fname = afile.split("/")[-1][:-4]
            a_func.pulse_ana(pldata, self.fembs, self.fembsID, self.savedir, fname, fdir + '/')
            pulse = dict(log.tmp_log)
            pulse_check = dict(log.check_log)
            for ifemb in range(len(self.fembs)):
                femb_id = "FEMB ID {}".format(self.fembsID['femb%d' % self.fembs[ifemb]])
                log.check_log04_01[femb_id]['Result'] = log.check_log04_01[femb_id]['Result'] & pulse_check[femb_id]['Result']
                # plt.figure(figsize=(9, 6))
                # x = [1, 2, 3, 4]
                if "SE_200mVBL_4_7mVfC_0_5us" in afile:
                    log.report_log04_01_4705[femb_id].update(pulse[femb_id]); log.check_log04_01_4705[femb_id].update(pulse_check[femb_id])
                if "SE_200mVBL_4_7mVfC_1_0us" in afile:
                    log.report_log04_01_4710[femb_id].update(pulse[femb_id]); log.check_log04_01_4710[femb_id].update(pulse_check[femb_id])
                if "SE_200mVBL_4_7mVfC_2_0us" in afile:
                    log.report_log04_01_4720[femb_id].update(pulse[femb_id]); log.check_log04_01_4720[femb_id].update(pulse_check[femb_id])
                if "SE_200mVBL_4_7mVfC_3_0us" in afile:
                    log.report_log04_01_4730[femb_id].update(pulse[femb_id]); log.check_log04_01_4730[femb_id].update(pulse_check[femb_id])

                if "SE_200mVBL_7_8mVfC_0_5us" in afile:
                    log.report_log04_01_7805[femb_id].update(pulse[femb_id]); log.check_log04_01_7805[femb_id].update(pulse_check[femb_id])
                if "SE_200mVBL_7_8mVfC_1_0us" in afile:
                    log.report_log04_01_7810[femb_id].update(pulse[femb_id]); log.check_log04_01_7810[femb_id].update(pulse_check[femb_id])
                if "SE_200mVBL_7_8mVfC_2_0us" in afile:
                    log.report_log04_01_7820[femb_id].update(pulse[femb_id]); log.check_log04_01_7820[femb_id].update(pulse_check[femb_id])
                if "SE_200mVBL_7_8mVfC_3_0us" in afile:
                    log.report_log04_01_7830[femb_id].update(pulse[femb_id]); log.check_log04_01_7830[femb_id].update(pulse_check[femb_id])

                if "SE_200mVBL_14_0mVfC_0_5us" in afile:
                    log.report_log04_01_1405[femb_id].update(pulse[femb_id]); log.check_log04_01_1405[femb_id].update(pulse_check[femb_id])
                if "SE_200mVBL_14_0mVfC_1_0us" in afile:
                    log.report_log04_01_1410[femb_id].update(pulse[femb_id]); log.check_log04_01_1410[femb_id].update(pulse_check[femb_id])
                if "SE_200mVBL_14_0mVfC_2_0us" in afile:
                    log.report_log04_01_1420[femb_id].update(pulse[femb_id]); log.check_log04_01_1420[femb_id].update(pulse_check[femb_id])
                if "SE_200mVBL_14_0mVfC_3_0us" in afile:
                    log.report_log04_01_1430[femb_id].update(pulse[femb_id]); log.check_log04_01_1430[femb_id].update(pulse_check[femb_id])

                if "SE_200mVBL_25_0mVfC_0_5us" in afile:
                    log.report_log04_01_2505[femb_id].update(pulse[femb_id]); log.check_log04_01_2505[femb_id].update(pulse_check[femb_id])
                if "SE_200mVBL_25_0mVfC_1_0us" in afile:
                    log.report_log04_01_2510[femb_id].update(pulse[femb_id]); log.check_log04_01_2510[femb_id].update(pulse_check[femb_id])
                if "SE_200mVBL_25_0mVfC_2_0us" in afile:
                    log.report_log04_01_2520[femb_id].update(pulse[femb_id]); log.check_log04_01_2520[femb_id].update(pulse_check[femb_id])
                if "SE_200mVBL_25_0mVfC_3_0us" in afile:
                    log.report_log04_01_2530[femb_id].update(pulse[femb_id]); log.check_log04_01_2530[femb_id].update(pulse_check[femb_id])



                if "SE_900mVBL_4_7mVfC_0_5us" in afile:
                    log.report_log04_02_4705[femb_id].update(pulse[femb_id]); log.check_log04_02_4705[femb_id].update(pulse_check[femb_id])
                if "SE_900mVBL_4_7mVfC_1_0us" in afile:
                    log.report_log04_02_4710[femb_id].update(pulse[femb_id]); log.check_log04_02_4710[femb_id].update(pulse_check[femb_id])
                if "SE_900mVBL_4_7mVfC_2_0us" in afile:
                    log.report_log04_02_4720[femb_id].update(pulse[femb_id]); log.check_log04_02_4720[femb_id].update(pulse_check[femb_id])
                if "SE_900mVBL_4_7mVfC_3_0us" in afile:
                    log.report_log04_02_4730[femb_id].update(pulse[femb_id]); log.check_log04_02_4730[femb_id].update(pulse_check[femb_id])

                if "SE_900mVBL_7_8mVfC_0_5us" in afile:
                    log.report_log04_02_7805[femb_id].update(pulse[femb_id]); log.check_log04_02_7805[femb_id].update(pulse_check[femb_id])
                if "SE_900mVBL_7_8mVfC_1_0us" in afile:
                    log.report_log04_02_7810[femb_id].update(pulse[femb_id]); log.check_log04_02_7810[femb_id].update(pulse_check[femb_id])
                if "SE_900mVBL_7_8mVfC_2_0us" in afile:
                    log.report_log04_02_7820[femb_id].update(pulse[femb_id]); log.check_log04_02_7820[femb_id].update(pulse_check[femb_id])
                if "SE_900mVBL_7_8mVfC_3_0us" in afile:
                    log.report_log04_02_7830[femb_id].update(pulse[femb_id]); log.check_log04_02_7830[femb_id].update(pulse_check[femb_id])

                if "SE_900mVBL_14_0mVfC_0_5us" in afile:
                    log.report_log04_02_1405[femb_id].update(pulse[femb_id]); log.check_log04_02_1405[femb_id].update(pulse_check[femb_id])
                if "SE_900mVBL_14_0mVfC_1_0us" in afile:
                    log.report_log04_02_1410[femb_id].update(pulse[femb_id]); log.check_log04_02_1410[femb_id].update(pulse_check[femb_id])
                if "SE_900mVBL_14_0mVfC_2_0us" in afile:
                    log.report_log04_02_1420[femb_id].update(pulse[femb_id]); log.check_log04_02_1420[femb_id].update(pulse_check[femb_id])
                if "SE_900mVBL_14_0mVfC_3_0us" in afile:
                    log.report_log04_02_1430[femb_id].update(pulse[femb_id]); log.check_log04_02_1430[femb_id].update(pulse_check[femb_id])

                if "SE_900mVBL_25_0mVfC_0_5us" in afile:
                    log.report_log04_02_2505[femb_id].update(pulse[femb_id]); log.check_log04_02_2505[femb_id].update(pulse_check[femb_id])
                if "SE_900mVBL_25_0mVfC_1_0us" in afile:
                    log.report_log04_02_2510[femb_id].update(pulse[femb_id]); log.check_log04_02_2510[femb_id].update(pulse_check[femb_id])
                if "SE_900mVBL_25_0mVfC_2_0us" in afile:
                    log.report_log04_02_2520[femb_id].update(pulse[femb_id]); log.check_log04_02_2520[femb_id].update(pulse_check[femb_id])
                if "SE_900mVBL_25_0mVfC_3_0us" in afile:
                    log.report_log04_02_2530[femb_id].update(pulse[femb_id]); log.check_log04_02_2530[femb_id].update(pulse_check[femb_id])

                if "SGP_200mVBL_4_7" in afile:
                    log.report_log04_03_4720[femb_id].update(pulse[femb_id]); log.check_log04_03_4720[femb_id].update(pulse_check[femb_id])
                if "SGP_200mVBL_7_8" in afile:
                    log.report_log04_03_7820[femb_id].update(pulse[femb_id]); log.check_log04_03_7820[femb_id].update(pulse_check[femb_id])
                if "SGP_200mVBL_14_0" in afile:
                    log.report_log04_03_1420[femb_id].update(pulse[femb_id]); log.check_log04_03_1420[femb_id].update(pulse_check[femb_id])
                if "SGP_200mVBL_25_0" in afile:
                    log.report_log04_03_2520[femb_id].update(pulse[femb_id]); log.check_log04_03_2520[femb_id].update(pulse_check[femb_id])
                #   different items plot together
                if "SEON_200mVBL" in afile:
                    log.report_log04_04_14201[femb_id].update(pulse[femb_id]); log.check_log04_04_14201[femb_id].update(pulse_check[femb_id])
                if "SEON_900mVBL" in afile:
                    log.report_log04_04_14202[femb_id].update(pulse[femb_id]); log.check_log04_04_14202[femb_id].update(pulse_check[femb_id])
                if "DIFF_200mVBL" in afile:
                    log.report_log04_04_14203[femb_id].update(pulse[femb_id]); log.check_log04_04_14203[femb_id].update(pulse_check[femb_id])
                if "DIFF_900mVBL" in afile:
                    log.report_log04_04_14204[femb_id].update(pulse[femb_id]); log.check_log04_04_14204[femb_id].update(pulse_check[femb_id])
                if "CHK_EX_200mVBL_14_0mVfC_2_0us_vdac000000mV" in afile:
                    log.report_log04_04_14205[femb_id].update(pulse[femb_id]); log.check_log04_04_14205[femb_id].update(pulse_check[femb_id])
                if "CHK_EX_200mVBL_14_0mVfC_2_0us_vdac000050mV" in afile:
                    log.report_log04_04_14206[femb_id].update(pulse[femb_id]); log.check_log04_04_14206[femb_id].update(pulse_check[femb_id])


        for ifemb in self.fembs:
            fp = self.savedir[ifemb] + fdir+"/"
            if 'vdac' in fname:
                print("vdac")
              #qc.GetPeaks(pldata, ifemb, fp, fname, period = 1000)
            else:
                qc.GetPeaks(pldata, ifemb, fp, fname)
            femb_id = "FEMB ID {}".format(self.fembsID['femb%d' % ifemb])
            # plot 1
            plt.figure(figsize=(6, 4))
            x = [1, 2, 3, 4]
            x_sticks = ()
            SE_200_4_7mV_ppk = [log.check_log04_01_4705[femb_id]["ppk_mean"]-log.check_log04_01_4705[femb_id]["bbl_mean"], log.check_log04_01_4710[femb_id]["ppk_mean"]-log.check_log04_01_4710[femb_id]["bbl_mean"], log.check_log04_01_4720[femb_id]["ppk_mean"]-log.check_log04_01_4720[femb_id]["bbl_mean"], log.check_log04_01_4730[femb_id]["ppk_mean"]-log.check_log04_01_4730[femb_id]["bbl_mean"]]
            SE_200_4_7mV_ppkerr = [log.check_log04_01_4705[femb_id]["ppk_std"], log.check_log04_01_4710[femb_id]["ppk_std"], log.check_log04_01_4720[femb_id]["ppk_std"], log.check_log04_01_4730[femb_id]["ppk_std"]]

            SE_200_7_8mV_ppk = [
                log.check_log04_01_7805[femb_id]["ppk_mean"] - log.check_log04_01_7805[femb_id]["bbl_mean"],
                log.check_log04_01_7810[femb_id]["ppk_mean"] - log.check_log04_01_7810[femb_id]["bbl_mean"],
                log.check_log04_01_7820[femb_id]["ppk_mean"] - log.check_log04_01_7820[femb_id]["bbl_mean"],
                log.check_log04_01_7830[femb_id]["ppk_mean"] - log.check_log04_01_7830[femb_id]["bbl_mean"]]

            SE_200_7_8mV_ppkerr = [log.check_log04_01_7805[femb_id]["ppk_std"], log.check_log04_01_7810[femb_id]["ppk_std"], log.check_log04_01_7820[femb_id]["ppk_std"], log.check_log04_01_7830[femb_id]["ppk_std"]]

            SE_200_14_0mV_ppk = [
                log.check_log04_01_1405[femb_id]["ppk_mean"] - log.check_log04_01_1405[femb_id]["bbl_mean"],
                log.check_log04_01_1410[femb_id]["ppk_mean"] - log.check_log04_01_1410[femb_id]["bbl_mean"],
                log.check_log04_01_1420[femb_id]["ppk_mean"] - log.check_log04_01_1420[femb_id]["bbl_mean"],
                log.check_log04_01_1430[femb_id]["ppk_mean"] - log.check_log04_01_1430[femb_id]["bbl_mean"]]
            SE_200_14_0mV_ppkerr = [log.check_log04_01_1405[femb_id]["ppk_std"],
                                   log.check_log04_01_1410[femb_id]["ppk_std"],
                                   log.check_log04_01_1420[femb_id]["ppk_std"],
                                   log.check_log04_01_1430[femb_id]["ppk_std"]]

            SE_200_25_0mV_ppk = [
                log.check_log04_01_2505[femb_id]["ppk_mean"] - log.check_log04_01_2505[femb_id]["bbl_mean"],
                log.check_log04_01_2510[femb_id]["ppk_mean"] - log.check_log04_01_2510[femb_id]["bbl_mean"],
                log.check_log04_01_2520[femb_id]["ppk_mean"] - log.check_log04_01_2520[femb_id]["bbl_mean"],
                log.check_log04_01_2530[femb_id]["ppk_mean"] - log.check_log04_01_2530[femb_id]["bbl_mean"]]
            SE_200_25_0mV_ppkerr = [log.check_log04_01_2505[femb_id]["ppk_std"],
                                   log.check_log04_01_2510[femb_id]["ppk_std"],
                                   log.check_log04_01_2520[femb_id]["ppk_std"],
                                   log.check_log04_01_2530[femb_id]["ppk_std"]]

            plt.errorbar(x, SE_200_4_7mV_ppk, yerr=SE_200_4_7mV_ppkerr, color='darkred', linestyle='-', capsize=5,alpha=0.7, label='SE_200_4_7mV_ppk')
            plt.errorbar(x, SE_200_7_8mV_ppk, yerr=SE_200_7_8mV_ppkerr, color='darkorange', linestyle='-', capsize=5,alpha=0.7, label='SE_200_7_8mV_ppk')
            plt.errorbar(x, SE_200_14_0mV_ppk, yerr=SE_200_14_0mV_ppkerr, color='darkgreen', linestyle='-', capsize=5,alpha=0.7,label='SE_200_14_0mV_ppk')
            plt.errorbar(x, SE_200_25_0mV_ppk, yerr=SE_200_25_0mV_ppkerr, color='darkblue', linestyle='-', capsize=5,alpha=0.7,label='SE_200_25_0mV_ppk')
            plt.legend()
            plt.xlabel("Peaking Time", fontsize=12)
            plt.ylabel("ADC count", fontsize=12)
            plt.xticks(x, ['0.5 us', '1 us', '2 us', '3 us'])
            plt.grid(True, axis='y', linestyle='--')
            plt.ylim(0, 6000)
            plt.title("SE 200 Pulse Response ErrorBar", fontsize=12)
            plt.margins(x=0.15)
            plt.gca().set_facecolor('none')     # set background as transparent
            plt.savefig(fp + 'SE_200_Gain_Pulse_ErrorBar.png', transparent = True)
            plt.close()
            # plot 2
            plt.figure(figsize=(6, 4))
            x = [1, 2, 3, 4]
            x_sticks = ()
            SE_900_4_7mV_ppk = [log.check_log04_02_4705[femb_id]["ppk_mean"] - log.check_log04_02_4705[femb_id]["bbl_mean"],
                                log.check_log04_02_4710[femb_id]["ppk_mean"] - log.check_log04_02_4710[femb_id]["bbl_mean"],
                                log.check_log04_02_4720[femb_id]["ppk_mean"] - log.check_log04_02_4720[femb_id]["bbl_mean"],
                                log.check_log04_02_4730[femb_id]["ppk_mean"] - log.check_log04_02_4730[femb_id]["bbl_mean"]]
            SE_900_4_7mV_ppkerr = [log.check_log04_02_4705[femb_id]["ppk_std"],
                                   log.check_log04_02_4710[femb_id]["ppk_std"],
                                   log.check_log04_02_4720[femb_id]["ppk_std"],
                                   log.check_log04_02_4730[femb_id]["ppk_std"]]
            SE_900_4_7mV_npk = [log.check_log04_02_4705[femb_id]["npk_mean"] - log.check_log04_02_4705[femb_id]["bbl_mean"],
                                log.check_log04_02_4710[femb_id]["npk_mean"] - log.check_log04_02_4710[femb_id]["bbl_mean"],
                                log.check_log04_02_4720[femb_id]["npk_mean"] - log.check_log04_02_4720[femb_id]["bbl_mean"],
                                log.check_log04_02_4730[femb_id]["npk_mean"] - log.check_log04_02_4730[femb_id]["bbl_mean"]]
            SE_900_4_7mV_npkerr = [log.check_log04_02_4705[femb_id]["npk_std"],
                                   log.check_log04_02_4710[femb_id]["npk_std"],
                                   log.check_log04_02_4720[femb_id]["npk_std"],
                                   log.check_log04_02_4730[femb_id]["npk_std"]]
            SE_900_7_8mV_ppk = [log.check_log04_02_7805[femb_id]["ppk_mean"] - log.check_log04_02_7805[femb_id]["bbl_mean"],
                                log.check_log04_02_7810[femb_id]["ppk_mean"] - log.check_log04_02_7810[femb_id]["bbl_mean"],
                                log.check_log04_02_7820[femb_id]["ppk_mean"] - log.check_log04_02_7820[femb_id]["bbl_mean"],
                                log.check_log04_02_7830[femb_id]["ppk_mean"] - log.check_log04_02_7830[femb_id]["bbl_mean"]]
            SE_900_7_8mV_ppkerr = [log.check_log04_02_7805[femb_id]["ppk_std"],
                                   log.check_log04_02_7810[femb_id]["ppk_std"],
                                   log.check_log04_02_7820[femb_id]["ppk_std"],
                                   log.check_log04_02_7830[femb_id]["ppk_std"]]
            SE_900_7_8mV_npk = [log.check_log04_02_7805[femb_id]["npk_mean"] - log.check_log04_02_7805[femb_id]["bbl_mean"],
                                log.check_log04_02_7810[femb_id]["npk_mean"] - log.check_log04_02_7810[femb_id]["bbl_mean"],
                                log.check_log04_02_7820[femb_id]["npk_mean"] - log.check_log04_02_7820[femb_id]["bbl_mean"],
                                log.check_log04_02_7830[femb_id]["npk_mean"] - log.check_log04_02_7830[femb_id]["bbl_mean"]]
            SE_900_7_8mV_npkerr = [log.check_log04_02_7805[femb_id]["npk_std"],
                                   log.check_log04_02_7810[femb_id]["npk_std"],
                                   log.check_log04_02_7820[femb_id]["npk_std"],
                                   log.check_log04_02_7830[femb_id]["npk_std"]]
            SE_900_14_0mV_ppk = [log.check_log04_02_1405[femb_id]["ppk_mean"] - log.check_log04_02_1405[femb_id]["bbl_mean"],
                                 log.check_log04_02_1410[femb_id]["ppk_mean"] - log.check_log04_02_1410[femb_id]["bbl_mean"],
                                 log.check_log04_02_1420[femb_id]["ppk_mean"] - log.check_log04_02_1420[femb_id]["bbl_mean"],
                                 log.check_log04_02_1430[femb_id]["ppk_mean"] - log.check_log04_02_1430[femb_id]["bbl_mean"]]
            SE_900_14_0mV_ppkerr = [log.check_log04_02_1405[femb_id]["ppk_std"],
                                    log.check_log04_02_1410[femb_id]["ppk_std"],
                                    log.check_log04_02_1420[femb_id]["ppk_std"],
                                    log.check_log04_02_1430[femb_id]["ppk_std"]]
            SE_900_14_0mV_npk = [log.check_log04_02_1405[femb_id]["npk_mean"] - log.check_log04_02_1405[femb_id]["bbl_mean"],
                                 log.check_log04_02_1410[femb_id]["npk_mean"] - log.check_log04_02_1410[femb_id]["bbl_mean"],
                                 log.check_log04_02_1420[femb_id]["npk_mean"] - log.check_log04_02_1420[femb_id]["bbl_mean"],
                                 log.check_log04_02_1430[femb_id]["npk_mean"] - log.check_log04_02_1430[femb_id]["bbl_mean"]]
            SE_900_14_0mV_npkerr = [log.check_log04_02_1405[femb_id]["npk_std"],
                                    log.check_log04_02_1410[femb_id]["npk_std"],
                                    log.check_log04_02_1420[femb_id]["npk_std"],
                                    log.check_log04_02_1430[femb_id]["npk_std"]]
            SE_900_25_0mV_ppk = [log.check_log04_02_2505[femb_id]["ppk_mean"] - log.check_log04_02_2505[femb_id]["bbl_mean"],
                                 log.check_log04_02_2510[femb_id]["ppk_mean"] - log.check_log04_02_2510[femb_id]["bbl_mean"],
                                 log.check_log04_02_2520[femb_id]["ppk_mean"] - log.check_log04_02_2520[femb_id]["bbl_mean"],
                                 log.check_log04_02_2530[femb_id]["ppk_mean"] - log.check_log04_02_2530[femb_id]["bbl_mean"]]
            SE_900_25_0mV_ppkerr = [log.check_log04_02_2505[femb_id]["ppk_std"],
                                    log.check_log04_02_2510[femb_id]["ppk_std"],
                                    log.check_log04_02_2520[femb_id]["ppk_std"],
                                    log.check_log04_02_2530[femb_id]["ppk_std"]]
            SE_900_25_0mV_npk = [log.check_log04_02_2505[femb_id]["npk_mean"] - log.check_log04_02_2505[femb_id]["bbl_mean"],
                                 log.check_log04_02_2510[femb_id]["npk_mean"] - log.check_log04_02_2510[femb_id]["bbl_mean"],
                                 log.check_log04_02_2520[femb_id]["npk_mean"] - log.check_log04_02_2520[femb_id]["bbl_mean"],
                                 log.check_log04_02_2530[femb_id]["npk_mean"] - log.check_log04_02_2530[femb_id]["bbl_mean"]]
            SE_900_25_0mV_npkerr = [log.check_log04_02_2505[femb_id]["npk_std"],
                                    log.check_log04_02_2510[femb_id]["npk_std"],
                                    log.check_log04_02_2520[femb_id]["npk_std"],
                                    log.check_log04_02_2530[femb_id]["npk_std"]]
            plt.errorbar(x, SE_900_4_7mV_ppk, yerr=SE_900_4_7mV_ppkerr, capsize=5, color='darkred', linestyle='-', alpha=0.7, label='SE_900_4_7mV_ppk')
            plt.errorbar(x, SE_900_4_7mV_npk, yerr=SE_900_4_7mV_npkerr, capsize=5, color='darkred', linestyle='--', alpha=0.7,label='SE_900_4_7mV_npk')
            plt.errorbar(x, SE_900_7_8mV_ppk, yerr=SE_900_7_8mV_ppkerr, capsize=5, color='darkorange', linestyle='-', alpha=0.7, label='SE_900_7_8mV_ppk')
            plt.errorbar(x, SE_900_7_8mV_npk, yerr=SE_900_7_8mV_npkerr, capsize=5, color='darkorange', linestyle='--', alpha=0.7,label='SE_900_7_8mV_npk')
            plt.errorbar(x, SE_900_14_0mV_ppk, yerr=SE_900_14_0mV_ppkerr, capsize=5, color='darkgreen', linestyle='-', alpha=0.7,label='SE_900_14_0mV_ppk')
            plt.errorbar(x, SE_900_14_0mV_npk, yerr=SE_900_14_0mV_npkerr, capsize=5, color='darkgreen', linestyle='--', alpha=0.7,label='SE_900_14_0mV_npk')
            plt.errorbar(x, SE_900_25_0mV_ppk, yerr=SE_900_25_0mV_ppkerr, capsize=5, color='darkblue', linestyle='-', alpha=0.7,label='SE_900_25_0mV_ppk')
            plt.errorbar(x, SE_900_25_0mV_npk, yerr=SE_900_25_0mV_npkerr, capsize=5, color='darkblue', linestyle='--', alpha=0.7,label='SE_900_25_0mV_npk')
            plt.legend()
            plt.xlabel("Peaking Time", fontsize=12)
            plt.ylabel("ADC Count", fontsize=12)
            # plt.yticks([log.report_log056_fembrms[ifemb]["SE_200mVBL_4_7mVfC_0_5us"], log.report_log056_fembrms[ifemb]["SE_200mVBL_7_8mVfC_0_5us"], log.report_log056_fembrms[ifemb]["SE_200mVBL_14_0mVfC_0_5us"], log.report_log056_fembrms[ifemb]["SE_200mVBL_25_0mVfC_0_5us"]], ['4.7 mV', '7.8 mV', '14 mV', '25 mV'])
            plt.xticks(x, ['0.5 us', '1 us', '2 us', '3 us'])
            plt.grid(True, axis='y', linestyle='--')
            plt.ylim(-9000, 9000)
            plt.title("SE 900 Pulse Response ErrorBar", fontsize=12)
            plt.margins(x=0.15)
            plt.gca().set_facecolor('none')     # set background as transparent
            plt.savefig(fp + 'SE_900_Gain_Pulse_ErrorBar.png', transparent = True)
            plt.close()
            # plot 3
            plt.figure(figsize=(6, 4))
            x = [1, 2, 3, 4]
            x_sticks = ()
            SGP1_200_ppk = [log.check_log04_03_4720[femb_id]["ppk_mean"]-log.check_log04_03_4720[femb_id]["bbl_mean"],
                                log.check_log04_03_7820[femb_id]["ppk_mean"]-log.check_log04_03_7820[femb_id]["bbl_mean"],
                                log.check_log04_03_1420[femb_id]["ppk_mean"]-log.check_log04_03_1420[femb_id]["bbl_mean"],
                                log.check_log04_03_2520[femb_id]["ppk_mean"]-log.check_log04_03_2520[femb_id]["bbl_mean"]]
            SGP1_200_ppkerr = [log.check_log04_03_4720[femb_id]["ppk_std"],
                                   log.check_log04_03_7820[femb_id]["ppk_std"],
                                   log.check_log04_03_1420[femb_id]["ppk_std"],
                                   log.check_log04_03_2520[femb_id]["ppk_std"]]
            plt.errorbar(x, SGP1_200_ppk, yerr=SGP1_200_ppkerr, capsize=5, linestyle='-', alpha=0.7, color='darkgreen', label='SGP1_200_ppk')
            plt.legend()
            plt.xlabel("Gain Setting", fontsize=12)
            plt.ylabel("ADC Count", fontsize=12)
            # plt.yticks([log.report_log056_fembrms[ifemb]["SE_200mVBL_4_7mVfC_0_5us"], log.report_log056_fembrms[ifemb]["SE_200mVBL_7_8mVfC_0_5us"], log.report_log056_fembrms[ifemb]["SE_200mVBL_14_0mVfC_0_5us"], log.report_log056_fembrms[ifemb]["SE_200mVBL_25_0mVfC_0_5us"]], ['4.7 mV', '7.8 mV', '14 mV', '25 mV'])
            plt.xticks(x, ['4.7 mV', '7.8 mV', '14 mV', '25 mV'])
            plt.grid(True, axis='y', linestyle='--')
            for i in range(len(x)):
                plt.text(x[i], SGP1_200_ppk[i] + 100, f'{round(SGP1_200_ppk[i], 1)}±{round(SGP1_200_ppkerr[i], 1)}', fontsize=10, ha='center', va='bottom', color='darkorange')
            plt.title("SGP1 200 Pulse Response ErrorBar", fontsize=12)
            plt.ylim(0, 17000)
            plt.margins(x=0.15)
            plt.gca().set_facecolor('none')  # set background as transparent
            plt.savefig(fp + 'SGP1_200_fC_Pulse.png', transparent = True)
            plt.close()
        self.Gather_PNG_PDF(fp)


    def RMS_report(self):
        log.test_label.append(5)
        self.CreateDIR("RMS")
        datadir = self.datadir+"RMS/"
        section_status = True
        check = True
        check_list = []
        datafiles = sorted(glob.glob(datadir+"RMS*.bin"), key=os.path.getmtime)
        for afile in datafiles:
            with open(afile, 'rb') as fn:
                raw = pickle.load(fn)
            print("analyze file: %s"%afile)
            rawdata=raw[0]
            if '\\' in afile:
                fname = afile.split("\\")[-1][4:-9]
            else:
                fname = afile.split("/")[-1][4:-9]
            qc=ana_tools()
            pldata = qc.data_decode(rawdata, self.fembs)
            for ifemb in self.fembs:
                fp = self.savedir[ifemb]+"RMS/"
                ped, rms = qc.GetRMS(pldata, ifemb, fp, fname)
                tmp = QC_check.CHKPulse(ped, 800)
                log.chkflag["BL"] = (tmp[0])
                log.badlist["BL"] = (tmp[1])
                ped_status = tmp[0]
                baseline_err_content = tmp[1]
                log.tmp_log[ifemb]["PED 128-CH std"] = tmp[2]
                tmp = QC_check.CHKPulse(rms, 0.3)
                log.chkflag["RMS"] = (tmp[0])
                log.badlist["RMS"] = (tmp[1])
                rms_status = tmp[0]
                rms_err_content = tmp[1]
                log.report_log056_fembrms[ifemb][fname] = tmp[2]
                log.report_log057_fembrmsstd[ifemb][fname] = tmp[3]
                index_of_keyword = fname.find("mVfC_")
                keyword = fname[index_of_keyword-4 : index_of_keyword]
                if (ped_status == True) and (rms_status == True):
                    log.report_log05_result[ifemb][fname] = True
                    log.report_log05_tablecell[ifemb][fname] = "{}".format(keyword)
                else:
                    log.report_log054_pedestal_issue[ifemb][fname] = baseline_err_content
                    log.report_log055_rms_issue[ifemb][fname] = rms_err_content
                    section_status = False
                    log.report_log05_result[ifemb][fname] = False
                    check = False
                    check_list.append(rms_err_content)
                    log.report_log05_tablecell[ifemb][fname] = "<span style = 'color:red;'> {} </span>".format(keyword)
                log.report_log052_pedestal[ifemb][fname] = ped
                log.report_log053_rms[ifemb][fname] = rms
        for ifemb in self.fembs:
            fp = self.savedir[ifemb] + "RMS/"
            femb_id = "FEMB ID {}".format(self.fembsID['femb%d' % ifemb])
            log.report_log0500[ifemb]['Result'] = check
            log.report_log0500[ifemb]['Issue List'] = check_list
            log.report_log05_table[femb_id]["Baseline"] = "200 mV | | | | | |"
            log.report_log05_table[femb_id]["interface"] = "SE OFF | | | | SE ON | DIFF | SE Leakage Current"
            log.report_log05_table[femb_id]["peak time"] = "0.5 us | 1 us | 2 us | 3 us | 2 us | 2 us | 2 us 14 mVfC "
            log.report_log05_table[femb_id]["4.7 mV"] = " {} | {} | {} | {} | {} | {} | {} ".format(log.report_log05_tablecell[ifemb]['SE_200mVBL_4_7mVfC_0_5us'], log.report_log05_tablecell[ifemb]['SE_200mVBL_4_7mVfC_1_0us'], log.report_log05_tablecell[ifemb]['SE_200mVBL_4_7mVfC_2_0us'], log.report_log05_tablecell[ifemb]['SE_200mVBL_4_7mVfC_3_0us'], log.report_log05_tablecell[ifemb]['SEON_200mVBL_4_7mVfC_2_0us'], log.report_log05_tablecell[ifemb]['DIFF_200mVBL_4_7mVfC_2_0us'], log.report_log05_tablecell[ifemb]['SELC_200mVBL_14_0mVfC_2_0us_100pA'])
            log.report_log05_table[femb_id]["7.8 mV"] = " {} | {} | {} | {} | {} | {} | {} ".format(log.report_log05_tablecell[ifemb]['SE_200mVBL_7_8mVfC_0_5us'], log.report_log05_tablecell[ifemb]['SE_200mVBL_7_8mVfC_1_0us'], log.report_log05_tablecell[ifemb]['SE_200mVBL_7_8mVfC_2_0us'], log.report_log05_tablecell[ifemb]['SE_200mVBL_7_8mVfC_3_0us'], log.report_log05_tablecell[ifemb]['SEON_200mVBL_7_8mVfC_2_0us'], log.report_log05_tablecell[ifemb]['DIFF_200mVBL_7_8mVfC_2_0us'], log.report_log05_tablecell[ifemb]['SELC_200mVBL_14_0mVfC_2_0us_500pA'])
            log.report_log05_table[femb_id]["14 mV"] = " {} | {} | {} | {} | {} | {} | {} ".format(log.report_log05_tablecell[ifemb]['SE_200mVBL_14_0mVfC_0_5us'], log.report_log05_tablecell[ifemb]['SE_200mVBL_14_0mVfC_1_0us'], log.report_log05_tablecell[ifemb]['SE_200mVBL_14_0mVfC_2_0us'], log.report_log05_tablecell[ifemb]['SE_200mVBL_14_0mVfC_3_0us'], log.report_log05_tablecell[ifemb]['SEON_200mVBL_14_0mVfC_2_0us'], log.report_log05_tablecell[ifemb]['DIFF_200mVBL_14_0mVfC_2_0us'], log.report_log05_tablecell[ifemb]['SELC_200mVBL_14_0mVfC_2_0us_1nA'])
            log.report_log05_table[femb_id]["25 mV"] = " {} | {} | {} | {} | {} | {} | {} ".format(log.report_log05_tablecell[ifemb]['SE_200mVBL_25_0mVfC_0_5us'], log.report_log05_tablecell[ifemb]['SE_200mVBL_25_0mVfC_1_0us'], log.report_log05_tablecell[ifemb]['SE_200mVBL_25_0mVfC_2_0us'], log.report_log05_tablecell[ifemb]['SE_200mVBL_25_0mVfC_3_0us'], log.report_log05_tablecell[ifemb]['SEON_200mVBL_25_0mVfC_2_0us'], log.report_log05_tablecell[ifemb]['DIFF_200mVBL_25_0mVfC_2_0us'], log.report_log05_tablecell[ifemb]['SELC_200mVBL_14_0mVfC_2_0us_5nA'])
            log.report_log05_table2[femb_id]["Baseline"] = "900 mV | | | | | | |"
            log.report_log05_table2[femb_id]["interface"] = "SE OFF | | | | SE ON | DIFF |"
            log.report_log05_table2[femb_id]["peak time"] = "0.5 us | 1 us | 2 us | 3 us | 2 us | 2 us |"
            log.report_log05_table2[femb_id]["4.7 mV"] = " {} | {} | {} | {} | {} | {} |".format(log.report_log05_tablecell[ifemb]['SE_200mVBL_4_7mVfC_0_5us'], log.report_log05_tablecell[ifemb]['SE_200mVBL_4_7mVfC_1_0us'], log.report_log05_tablecell[ifemb]['SE_900mVBL_4_7mVfC_2_0us'], log.report_log05_tablecell[ifemb]['SE_900mVBL_4_7mVfC_3_0us'], log.report_log05_tablecell[ifemb]['SEON_900mVBL_4_7mVfC_2_0us'], log.report_log05_tablecell[ifemb]['DIFF_900mVBL_4_7mVfC_2_0us'])
            log.report_log05_table2[femb_id]["7.8 mV"] = " {} | {} | {} | {} | {} | {} |".format(log.report_log05_tablecell[ifemb]['SE_200mVBL_7_8mVfC_0_5us'], log.report_log05_tablecell[ifemb]['SE_200mVBL_7_8mVfC_1_0us'], log.report_log05_tablecell[ifemb]['SE_900mVBL_7_8mVfC_2_0us'], log.report_log05_tablecell[ifemb]['SE_900mVBL_7_8mVfC_3_0us'], log.report_log05_tablecell[ifemb]['SEON_900mVBL_7_8mVfC_2_0us'], log.report_log05_tablecell[ifemb]['DIFF_900mVBL_7_8mVfC_2_0us'])
            log.report_log05_table2[femb_id]["14 mV"] = " {} | {} | {} | {} | {} | {} |".format(log.report_log05_tablecell[ifemb]['SE_200mVBL_14_0mVfC_0_5us'], log.report_log05_tablecell[ifemb]['SE_200mVBL_14_0mVfC_1_0us'], log.report_log05_tablecell[ifemb]['SE_900mVBL_14_0mVfC_2_0us'], log.report_log05_tablecell[ifemb]['SE_900mVBL_14_0mVfC_3_0us'], log.report_log05_tablecell[ifemb]['SEON_900mVBL_14_0mVfC_2_0us'], log.report_log05_tablecell[ifemb]['DIFF_900mVBL_14_0mVfC_2_0us'])
            log.report_log05_table2[femb_id]["25 mV"] = " {} | {} | {} | {} | {} | {} |".format(log.report_log05_tablecell[ifemb]['SE_200mVBL_25_0mVfC_0_5us'], log.report_log05_tablecell[ifemb]['SE_200mVBL_25_0mVfC_1_0us'], log.report_log05_tablecell[ifemb]['SE_900mVBL_25_0mVfC_2_0us'], log.report_log05_tablecell[ifemb]['SE_900mVBL_25_0mVfC_3_0us'], log.report_log05_tablecell[ifemb]['SEON_900mVBL_25_0mVfC_2_0us'], log.report_log05_tablecell[ifemb]['DIFF_900mVBL_25_0mVfC_2_0us'])
            plt.figure(figsize=(20, 4))
            plt.subplot(1, 4, 1)
            x_sticks = range(0, 129, 16)
            for key in log.report_log053_rms[ifemb]:
                if "SE_200mVBL_4_7mVfC" in key:
                    plt.plot(range(128), log.report_log053_rms[ifemb][key], linestyle='-', alpha=0.7, color='red')
                if "SE_200mVBL_7_8mVfC" in key:
                    plt.plot(range(128), log.report_log053_rms[ifemb][key], linestyle='-', alpha=0.7, color='orange')
                if "SE_200mVBL_14_0mVfC" in key:
                    plt.plot(range(128), log.report_log053_rms[ifemb][key], linestyle='-', alpha=0.7, color='green')
                if "SE_200mVBL_25_0mVfC" in key:
                    plt.plot(range(128), log.report_log053_rms[ifemb][key], linestyle='-', alpha=0.7, color='blue')
            plt.xlabel("Channel", fontsize=12)
            plt.ylabel("SE OFF RMS", fontsize=12)
            plt.xticks(x_sticks)
            plt.grid(axis='x')
            plt.title("SE OFF 200 mV RMS Distribution", fontsize=12)
            plt.subplot(1, 4, 2)
            for key in log.report_log053_rms[ifemb]:
                if "SEON_200" in key:
                    plt.plot(range(128), log.report_log053_rms[ifemb][key], linestyle='-', alpha=0.7)
            plt.xlabel("Channel", fontsize=12)
            plt.ylabel("SEON RMS", fontsize=12)
            plt.xticks(x_sticks)
            plt.grid(axis='x')
            plt.title("SE ON 200 mV RMS Distribution", fontsize=12)
            plt.subplot(1, 4, 3)
            for key in log.report_log053_rms[ifemb]:
                if "SELC_200" in key:
                    plt.plot(range(128), log.report_log053_rms[ifemb][key], linestyle='-', alpha=0.7)
            plt.xlabel("Channel", fontsize=12)
            plt.ylabel("SELC RMS", fontsize=12)
            plt.xticks(x_sticks)
            plt.grid(axis='x')
            plt.title("SE Leakage Current 200 mV RMS Distribution", fontsize=12)
            plt.subplot(1, 4, 4)
            for key in log.report_log053_rms[ifemb]:
                if "DIFF_200" in key:
                    plt.plot(range(128), log.report_log053_rms[ifemb][key], linestyle='-', alpha=0.7)
            plt.xlabel("Channel", fontsize=12)
            plt.ylabel("DIFF RMS", fontsize=12)
            plt.xticks(x_sticks)
            plt.grid(axis='x')
            plt.title("DIFF 200 mV RMS Distribution", fontsize=12)
            plt.savefig(fp + '200mV_All_Configuration.png')
            plt.close()
            plt.figure(figsize=(15, 4))
            plt.subplot(1, 3, 1)
            x_sticks = range(0, 129, 16)
            for key in log.report_log053_rms[ifemb]:
                if "SE_900" in key:
                    plt.plot(range(128), log.report_log053_rms[ifemb][key], linestyle='-', alpha=0.7)
            plt.xlabel("Channel", fontsize=12)
            plt.ylabel("SE OFF RMS", fontsize=12)
            plt.xticks(x_sticks)
            plt.grid(axis='x')
            plt.title("SE OFF 900 mV RMS Distribution", fontsize=12)
            plt.subplot(1, 3, 2)
            for key in log.report_log053_rms[ifemb]:
                if "SEON_900" in key:
                    plt.plot(range(128), log.report_log053_rms[ifemb][key], linestyle='-', alpha=0.7)
            plt.xlabel("Channel", fontsize=12)
            plt.ylabel("SEON RMS", fontsize=12)
            plt.xticks(x_sticks)
            plt.grid(axis='x')
            plt.title("SE ON 900 mV RMS Distribution", fontsize=12)
            plt.subplot(1, 3, 3)
            for key in log.report_log053_rms[ifemb]:
                if "DIFF_900" in key:
                    plt.plot(range(128), log.report_log053_rms[ifemb][key], linestyle='-', alpha=0.7)
            plt.xlabel("Channel", fontsize=12)
            plt.ylabel("DIFF RMD", fontsize=12)
            plt.xticks(x_sticks)
            plt.grid(axis='x')
            plt.title("DIFF 900 mV RMS Distribution", fontsize=12)
            plt.savefig(fp + '900mV_All_Configuration.png')
            plt.close()
            # error bar plot
            plt.figure(figsize=(6, 4))
            x = [0.5, 1, 2, 3]
            x_sticks = ()
            SE_200_4_7mV = [log.report_log056_fembrms[ifemb]["SE_200mVBL_4_7mVfC_0_5us"], log.report_log056_fembrms[ifemb]["SE_200mVBL_4_7mVfC_1_0us"], log.report_log056_fembrms[ifemb]["SE_200mVBL_4_7mVfC_2_0us"], log.report_log056_fembrms[ifemb]["SE_200mVBL_4_7mVfC_3_0us"]]
            SE_200_7_8mV = [log.report_log056_fembrms[ifemb]["SE_200mVBL_7_8mVfC_0_5us"], log.report_log056_fembrms[ifemb]["SE_200mVBL_7_8mVfC_1_0us"], log.report_log056_fembrms[ifemb]["SE_200mVBL_7_8mVfC_2_0us"], log.report_log056_fembrms[ifemb]["SE_200mVBL_7_8mVfC_3_0us"]]
            SE_200_14_0mV = [log.report_log056_fembrms[ifemb]["SE_200mVBL_14_0mVfC_0_5us"], log.report_log056_fembrms[ifemb]["SE_200mVBL_14_0mVfC_1_0us"], log.report_log056_fembrms[ifemb]["SE_200mVBL_14_0mVfC_2_0us"], log.report_log056_fembrms[ifemb]["SE_200mVBL_14_0mVfC_3_0us"]]
            SE_200_25_0mV = [log.report_log056_fembrms[ifemb]["SE_200mVBL_25_0mVfC_0_5us"], log.report_log056_fembrms[ifemb]["SE_200mVBL_25_0mVfC_1_0us"], log.report_log056_fembrms[ifemb]["SE_200mVBL_25_0mVfC_2_0us"], log.report_log056_fembrms[ifemb]["SE_200mVBL_25_0mVfC_3_0us"]]
            SE_900_4_7mV = [log.report_log056_fembrms[ifemb]["SE_900mVBL_4_7mVfC_0_5us"], log.report_log056_fembrms[ifemb]["SE_900mVBL_4_7mVfC_1_0us"], log.report_log056_fembrms[ifemb]["SE_900mVBL_4_7mVfC_2_0us"], log.report_log056_fembrms[ifemb]["SE_900mVBL_4_7mVfC_3_0us"]]
            SE_900_7_8mV = [log.report_log056_fembrms[ifemb]["SE_900mVBL_7_8mVfC_0_5us"], log.report_log056_fembrms[ifemb]["SE_900mVBL_7_8mVfC_1_0us"], log.report_log056_fembrms[ifemb]["SE_900mVBL_7_8mVfC_2_0us"], log.report_log056_fembrms[ifemb]["SE_900mVBL_7_8mVfC_3_0us"]]
            SE_900_14_0mV = [log.report_log056_fembrms[ifemb]["SE_900mVBL_14_0mVfC_0_5us"], log.report_log056_fembrms[ifemb]["SE_900mVBL_14_0mVfC_1_0us"], log.report_log056_fembrms[ifemb]["SE_900mVBL_14_0mVfC_2_0us"], log.report_log056_fembrms[ifemb]["SE_900mVBL_14_0mVfC_3_0us"]]
            SE_900_25_0mV = [log.report_log056_fembrms[ifemb]["SE_900mVBL_25_0mVfC_0_5us"], log.report_log056_fembrms[ifemb]["SE_900mVBL_25_0mVfC_1_0us"], log.report_log056_fembrms[ifemb]["SE_900mVBL_25_0mVfC_2_0us"], log.report_log056_fembrms[ifemb]["SE_900mVBL_25_0mVfC_3_0us"]]
            SE_200_4_7mV_err = [log.report_log057_fembrmsstd[ifemb]["SE_200mVBL_4_7mVfC_0_5us"], log.report_log057_fembrmsstd[ifemb]["SE_200mVBL_4_7mVfC_1_0us"], log.report_log057_fembrmsstd[ifemb]["SE_200mVBL_4_7mVfC_2_0us"], log.report_log057_fembrmsstd[ifemb]["SE_200mVBL_4_7mVfC_3_0us"]]
            SE_200_7_8mV_err = [log.report_log057_fembrmsstd[ifemb]["SE_200mVBL_7_8mVfC_0_5us"], log.report_log057_fembrmsstd[ifemb]["SE_200mVBL_7_8mVfC_1_0us"], log.report_log057_fembrmsstd[ifemb]["SE_200mVBL_7_8mVfC_2_0us"], log.report_log057_fembrmsstd[ifemb]["SE_200mVBL_7_8mVfC_3_0us"]]
            SE_200_14_0mV_err = [log.report_log057_fembrmsstd[ifemb]["SE_200mVBL_14_0mVfC_0_5us"], log.report_log057_fembrmsstd[ifemb]["SE_200mVBL_14_0mVfC_1_0us"], log.report_log057_fembrmsstd[ifemb]["SE_200mVBL_14_0mVfC_2_0us"], log.report_log057_fembrmsstd[ifemb]["SE_200mVBL_14_0mVfC_3_0us"]]
            SE_200_25_0mV_err = [log.report_log057_fembrmsstd[ifemb]["SE_200mVBL_25_0mVfC_0_5us"], log.report_log057_fembrmsstd[ifemb]["SE_200mVBL_25_0mVfC_1_0us"], log.report_log057_fembrmsstd[ifemb]["SE_200mVBL_25_0mVfC_2_0us"], log.report_log057_fembrmsstd[ifemb]["SE_200mVBL_25_0mVfC_3_0us"]]
            SE_900_4_7mV_err = [log.report_log057_fembrmsstd[ifemb]["SE_900mVBL_4_7mVfC_0_5us"], log.report_log057_fembrmsstd[ifemb]["SE_900mVBL_4_7mVfC_1_0us"], log.report_log057_fembrmsstd[ifemb]["SE_900mVBL_4_7mVfC_2_0us"], log.report_log057_fembrmsstd[ifemb]["SE_900mVBL_4_7mVfC_3_0us"]]
            SE_900_7_8mV_err = [log.report_log057_fembrmsstd[ifemb]["SE_900mVBL_7_8mVfC_0_5us"], log.report_log057_fembrmsstd[ifemb]["SE_900mVBL_7_8mVfC_1_0us"], log.report_log057_fembrmsstd[ifemb]["SE_900mVBL_7_8mVfC_2_0us"], log.report_log057_fembrmsstd[ifemb]["SE_900mVBL_7_8mVfC_3_0us"]]
            SE_900_14_0mV_err = [log.report_log057_fembrmsstd[ifemb]["SE_900mVBL_14_0mVfC_0_5us"], log.report_log057_fembrmsstd[ifemb]["SE_900mVBL_14_0mVfC_1_0us"], log.report_log057_fembrmsstd[ifemb]["SE_900mVBL_14_0mVfC_2_0us"], log.report_log057_fembrmsstd[ifemb]["SE_900mVBL_14_0mVfC_3_0us"]]
            SE_900_25_0mV_err = [log.report_log057_fembrmsstd[ifemb]["SE_900mVBL_25_0mVfC_0_5us"], log.report_log057_fembrmsstd[ifemb]["SE_900mVBL_25_0mVfC_1_0us"], log.report_log057_fembrmsstd[ifemb]["SE_900mVBL_25_0mVfC_2_0us"], log.report_log057_fembrmsstd[ifemb]["SE_900mVBL_25_0mVfC_3_0us"]]
            # for key in log.report_log056_fembrms[ifemb]:
            #     if "SE_200" in key:
            plt.errorbar(x, SE_200_4_7mV, yerr=SE_200_4_7mV_err,capsize=5, linestyle='-', alpha=0.7, color = 'darkred', label = 'SE_200_4_7mV')
            plt.errorbar(x, SE_200_7_8mV, yerr=SE_200_7_8mV_err,capsize=5, linestyle='-', alpha=0.7, color = 'darkorange', label = 'SE_200_7_8mV')
            plt.errorbar(x, SE_200_14_0mV, yerr=SE_200_14_0mV_err,capsize=5, linestyle='-', alpha=0.7, color = 'darkgreen', label = 'SE_200_14_0mV')
            plt.errorbar(x, SE_200_25_0mV, yerr=SE_200_25_0mV_err,capsize=5, linestyle='-', alpha=0.7, color = 'darkblue', label = 'SE_200_25_0mV')
            plt.errorbar(x, SE_900_4_7mV, yerr=SE_900_4_7mV_err,capsize=5, linestyle='--', alpha=0.7, color = 'darkred', label = 'SE_900_4_7mV')
            plt.errorbar(x, SE_900_7_8mV, yerr=SE_900_7_8mV_err,capsize=5, linestyle='--', alpha=0.7, color = 'darkorange', label = 'SE_900_7_8mV')
            plt.errorbar(x, SE_900_14_0mV, yerr=SE_900_14_0mV_err,capsize=5, linestyle='--', alpha=0.7, color = 'darkgreen', label = 'SE_900_14_0mV')
            plt.errorbar(x, SE_900_25_0mV, yerr=SE_900_25_0mV_err,capsize=5, linestyle='--', alpha=0.7, color = 'darkblue', label = 'SE_900_25_0mV')
            plt.legend()
            plt.xlabel("Peaking Time / us", fontsize=12)
            plt.ylabel("RMS", fontsize=12)
            # plt.yticks([log.report_log056_fembrms[ifemb]["SE_200mVBL_4_7mVfC_0_5us"], log.report_log056_fembrms[ifemb]["SE_200mVBL_7_8mVfC_0_5us"], log.report_log056_fembrms[ifemb]["SE_200mVBL_14_0mVfC_0_5us"], log.report_log056_fembrms[ifemb]["SE_200mVBL_25_0mVfC_0_5us"]], ['4.7 mV', '7.8 mV', '14 mV', '25 mV'])
            plt.xticks(x, ['0.5', '1', '2', '3'])
            plt.ylim(0, 70)
            plt.grid(axis='x')
            plt.title("SE 200 & 900 mV RMS ErrorBar", fontsize=12)
            plt.margins(x=0.15)
            plt.gca().set_facecolor('none')  # set background as transparent
            plt.savefig(fp + 'SE_200_900_mV_RMS_ErrorBar.png', transparent = True)
            plt.close()
            plt.figure(figsize=(6, 4))
            x = [4.7, 7.8, 14, 25]
            SEON_200_2_0us = [log.report_log056_fembrms[ifemb]["SEON_200mVBL_4_7mVfC_2_0us"], log.report_log056_fembrms[ifemb]["SEON_200mVBL_7_8mVfC_2_0us"], log.report_log056_fembrms[ifemb]["SEON_200mVBL_14_0mVfC_2_0us"], log.report_log056_fembrms[ifemb]["SEON_200mVBL_25_0mVfC_2_0us"]]
            SEON_900_2_0us = [log.report_log056_fembrms[ifemb]["SEON_900mVBL_4_7mVfC_2_0us"], log.report_log056_fembrms[ifemb]["SEON_900mVBL_7_8mVfC_2_0us"], log.report_log056_fembrms[ifemb]["SEON_900mVBL_14_0mVfC_2_0us"], log.report_log056_fembrms[ifemb]["SEON_900mVBL_25_0mVfC_2_0us"]]
            DIFF_200_2_0us = [log.report_log056_fembrms[ifemb]["DIFF_200mVBL_4_7mVfC_2_0us"], log.report_log056_fembrms[ifemb]["DIFF_200mVBL_7_8mVfC_2_0us"], log.report_log056_fembrms[ifemb]["DIFF_200mVBL_14_0mVfC_2_0us"], log.report_log056_fembrms[ifemb]["DIFF_200mVBL_25_0mVfC_2_0us"]]
            DIFF_900_2_0us = [log.report_log056_fembrms[ifemb]["DIFF_900mVBL_4_7mVfC_2_0us"], log.report_log056_fembrms[ifemb]["DIFF_900mVBL_7_8mVfC_2_0us"], log.report_log056_fembrms[ifemb]["DIFF_900mVBL_14_0mVfC_2_0us"], log.report_log056_fembrms[ifemb]["DIFF_900mVBL_25_0mVfC_2_0us"]]
            SEON_200_2_0us_err = [log.report_log057_fembrmsstd[ifemb]["SEON_200mVBL_4_7mVfC_2_0us"], log.report_log057_fembrmsstd[ifemb]["SEON_200mVBL_7_8mVfC_2_0us"], log.report_log057_fembrmsstd[ifemb]["SEON_200mVBL_14_0mVfC_2_0us"], log.report_log057_fembrmsstd[ifemb]["SEON_200mVBL_25_0mVfC_2_0us"]]
            SEON_900_2_0us_err = [log.report_log057_fembrmsstd[ifemb]["SEON_900mVBL_4_7mVfC_2_0us"], log.report_log057_fembrmsstd[ifemb]["SEON_900mVBL_7_8mVfC_2_0us"], log.report_log057_fembrmsstd[ifemb]["SEON_900mVBL_14_0mVfC_2_0us"], log.report_log057_fembrmsstd[ifemb]["SEON_900mVBL_25_0mVfC_2_0us"]]
            DIFF_200_2_0us_err = [log.report_log057_fembrmsstd[ifemb]["DIFF_200mVBL_4_7mVfC_2_0us"], log.report_log057_fembrmsstd[ifemb]["DIFF_200mVBL_7_8mVfC_2_0us"], log.report_log057_fembrmsstd[ifemb]["DIFF_200mVBL_14_0mVfC_2_0us"], log.report_log057_fembrmsstd[ifemb]["DIFF_200mVBL_25_0mVfC_2_0us"]]
            DIFF_900_2_0us_err = [log.report_log057_fembrmsstd[ifemb]["DIFF_900mVBL_4_7mVfC_2_0us"], log.report_log057_fembrmsstd[ifemb]["DIFF_900mVBL_7_8mVfC_2_0us"], log.report_log057_fembrmsstd[ifemb]["DIFF_900mVBL_14_0mVfC_2_0us"], log.report_log057_fembrmsstd[ifemb]["DIFF_900mVBL_25_0mVfC_2_0us"]]
            # for key in log.report_log056_fembrms[ifemb]:
            #     if "SE_200" in key:
            plt.errorbar(x, SEON_200_2_0us, yerr=SEON_200_2_0us_err,capsize=5, linestyle='-', alpha=0.7, color = 'darkred', label = 'SEON_200_2_0us')
            plt.errorbar(x, SEON_900_2_0us, yerr=SEON_900_2_0us_err,capsize=5, linestyle='-', alpha=0.7, color = 'darkgreen', label = 'SEON_900_2_0us')
            plt.errorbar(x, DIFF_200_2_0us, yerr=DIFF_200_2_0us_err,capsize=5, linestyle='--', alpha=1, color = 'darkblue', label = 'DIFF_200_2_0us')
            plt.errorbar(x, DIFF_900_2_0us, yerr=DIFF_900_2_0us_err,capsize=5, linestyle='--', alpha=1, color = 'darkorange', label = 'DIFF_900_2_0us')
            plt.legend()
            plt.xlabel("Gain / mV/fC", fontsize=12)
            plt.ylabel("RMS", fontsize=12)
            # plt.yticks([log.report_log056_fembrms[ifemb]["SE_200mVBL_4_7mVfC_0_5us"], log.report_log056_fembrms[ifemb]["SE_200mVBL_7_8mVfC_0_5us"], log.report_log056_fembrms[ifemb]["SE_200mVBL_14_0mVfC_0_5us"], log.report_log056_fembrms[ifemb]["SE_200mVBL_25_0mVfC_0_5us"]], ['4.7 mV', '7.8 mV', '14 mV', '25 mV'])
            plt.xticks(x, ['4.7', '7.8', '14', '25'])
            plt.grid(axis='x')
            plt.ylim(0, 60)
            plt.title("SEON DIFF 200 & 900 mV RMS ErrorBar", fontsize=12)
            plt.margins(x=0.15)
            plt.gca().set_facecolor('none')  # set background as transparent
            plt.savefig(fp + 'SEON_DIFF_200_900_mV_RMS_ErrorBar.png', transparent = True)
            plt.close()
            plt.figure(figsize=(6, 4))
            x = [1, 5, 10, 50]
            SELC_200_2_0us = [log.report_log056_fembrms[ifemb]["SELC_200mVBL_14_0mVfC_2_0us_100pA"], log.report_log056_fembrms[ifemb]["SELC_200mVBL_14_0mVfC_2_0us_500pA"], log.report_log056_fembrms[ifemb]["SELC_200mVBL_14_0mVfC_2_0us_1nA"], log.report_log056_fembrms[ifemb]["SELC_200mVBL_14_0mVfC_2_0us_5nA"]]
            SELC_200_2_0us_err = [log.report_log057_fembrmsstd[ifemb]["SELC_200mVBL_14_0mVfC_2_0us_100pA"], log.report_log057_fembrmsstd[ifemb]["SELC_200mVBL_14_0mVfC_2_0us_500pA"], log.report_log057_fembrmsstd[ifemb]["SELC_200mVBL_14_0mVfC_2_0us_1nA"], log.report_log057_fembrmsstd[ifemb]["SELC_200mVBL_14_0mVfC_2_0us_5nA"]]
            # for key in log.report_log056_fembrms[ifemb]:
            #     if "SE_200" in key:
            plt.errorbar(x, SELC_200_2_0us, yerr=SELC_200_2_0us_err, capsize=5, linestyle='-', alpha=0.7, color = 'blue', label = 'SELC_200_2_0us')
            plt.legend()
            plt.xlabel("Leakage Current / pA", fontsize=12)
            plt.ylabel("RMS", fontsize=12)
            # plt.yticks([log.report_log056_fembrms[ifemb]["SE_200mVBL_4_7mVfC_0_5us"], log.report_log056_fembrms[ifemb]["SE_200mVBL_7_8mVfC_0_5us"], log.report_log056_fembrms[ifemb]["SE_200mVBL_14_0mVfC_0_5us"], log.report_log056_fembrms[ifemb]["SE_200mVBL_25_0mVfC_0_5us"]], ['4.7 mV', '7.8 mV', '14 mV', '25 mV'])
            plt.xticks(x, ['100', '500', '1 000', '5 000'])
            plt.grid(axis='x')
            plt.ylim(0, 40)
            plt.title("Single-Ended RMS at different Leakage Current", fontsize=12)
            plt.margins(x=0.15)
            plt.gca().set_facecolor('none')  # set background as transparent
            plt.savefig(fp + 'SELC_200_2us_ErrorBar.png', transparent = True)
            plt.close()
        self.Gather_PNG_PDF(fp)
        log.report_log05_fin_result = section_status


    def report(self):
        print(self.savedir)
        a_repo.final_report(self.savedir, self.fembs, self.fembsID)

    #   6  CALI_report_1
    def CALI_report_1(self):
        log.test_label.append(6)
        a_func=ana_tools()
        self.CreateDIR("CALI1")
        self.CreateDIR("CALI1_DIFF")
        dac_list = range(0,64,1)
        datadir = self.datadir+"CALI1/"
        print("analyze CALI1 200mVBL 4_7mVfC 2_0us")
        a_func.GetGain(self.fembs, self.fembsID, datadir, self.savedir, "CALI1/", "CALI1_SE_{}_{}_{}_0x{:02x}", "200mVBL", "4_7mVfC", "2_0us", dac_list, 10000)
        a_func.GetENC(self.fembs, self.fembsID, "200mVBL", "4_7mVfC", "2_0us", 0, self.savedir, "CALI1/")
        inl_gain = dict(log.tmp_log)
        inl_gain_check = dict(log.check_log)
        log.report_log0601.update(inl_gain)
        log.check_log0601.update(inl_gain_check)
        datadir = self.datadir+"CALI1/"
        print("analyze CALI1 200mVBL 7_8mVfC 2_0us")
        a_func.GetGain(self.fembs, self.fembsID, datadir, self.savedir, "CALI1/", "CALI1_SE_{}_{}_{}_0x{:02x}", "200mVBL", "7_8mVfC", "2_0us", dac_list)
        a_func.GetENC(self.fembs, self.fembsID, "200mVBL", "7_8mVfC", "2_0us", 0, self.savedir, "CALI1/")
        inl_gain = dict(log.tmp_log)
        inl_gain_check = dict(log.check_log)
        log.report_log0602.update(inl_gain)
        log.check_log0602.update(inl_gain_check)
        datadir = self.datadir+"CALI1/"
        print("analyze CALI1 200mVBL 14_0mVfC 2_0us")
        a_func.GetGain(self.fembs, self.fembsID, datadir, self.savedir, "CALI1/", "CALI1_SE_{}_{}_{}_0x{:02x}", "200mVBL", "14_0mVfC", "2_0us", dac_list)
        a_func.GetENC(self.fembs, self.fembsID, "200mVBL", "14_0mVfC", "2_0us", 0, self.savedir, "CALI1/")
        inl_gain = dict(log.tmp_log)
        inl_gain_check = dict(log.check_log)
        log.report_log0603.update(inl_gain)
        log.check_log0603.update(inl_gain_check)
        datadir = self.datadir+"CALI1/"
        print("analyze CALI1 200mVBL 25_0mVfC 2_0us")
        a_func.GetGain(self.fembs, self.fembsID, datadir, self.savedir, "CALI1/", "CALI1_SE_{}_{}_{}_0x{:02x}", "200mVBL", "25_0mVfC", "2_0us", dac_list)
        a_func.GetENC(self.fembs, self.fembsID, "200mVBL", "25_0mVfC", "2_0us", 0, self.savedir, "CALI1/")
        inl_gain = dict(log.tmp_log)
        inl_gain_check = dict(log.check_log)
        log.report_log0604.update(inl_gain)
        log.check_log0604.update(inl_gain_check)
        datadir = self.datadir+"CALI1/"
        print("analyze CALI1 DIFF 200mVBL 14_0mVfC 2_0us")
        a_func.GetGain(self.fembs, self.fembsID, datadir, self.savedir, "CALI1_DIFF/", "CALI1_DIFF_{}_{}_{}_0x{:02x}", "200mVBL", "14_0mVfC", "2_0us", dac_list)
        a_func.GetENC(self.fembs, self.fembsID, "200mVBL", "14_0mVfC", "2_0us", 0, self.savedir, "CALI1_DIFF/")
        inl_gain = dict(log.tmp_log)
        inl_gain_check = dict(log.check_log)
        log.report_log0605.update(inl_gain)
        log.check_log0605.update(inl_gain_check)
        for ifemb in self.fembs:
            report_dir = self.savedir[ifemb] + "CALI1_DIFF/"
            femb_id = "FEMB ID {}".format(self.fembsID['femb%d' % ifemb])



            inl_set = [log.report_log0601[femb_id]["INL"], log.report_log0602[femb_id]["INL"], log.report_log0603[femb_id]["INL"], log.report_log0604[femb_id]["INL"]]
            gain_set = [log.report_log0601[femb_id]["Gain"], log.report_log0602[femb_id]["Gain"], log.report_log0603[femb_id]["Gain"], log.report_log0604[femb_id]["Gain"]]
            gain_std = [log.report_log0601[femb_id]["Gainstd"], log.report_log0602[femb_id]["Gainstd"], log.report_log0603[femb_id]["Gainstd"], log.report_log0604[femb_id]["Gainstd"]]
            ENC_set = [log.report_log0601[femb_id]["ENC"], log.report_log0602[femb_id]["ENC"], log.report_log0603[femb_id]["ENC"], log.report_log0604[femb_id]["ENC"]]
            ENC_std = [log.report_log0601[femb_id]["ENC_std"], log.report_log0602[femb_id]["ENC_std"], log.report_log0603[femb_id]["ENC_std"], log.report_log0604[femb_id]["ENC_std"]]
            plt.figure(figsize=(10, 4))
            plt.subplot(1, 2, 1)
            plt.plot(range(4), inl_set, marker='o', linestyle='-', alpha=0.7, label = 'INL_SE_OFF')
            plt.plot(2, log.report_log0601[femb_id]["INL"], marker='o', linestyle='-', alpha=0.7, label = 'INL_DIFF')
            plt.xlabel("Voltage Gain", fontsize=12)
            plt.ylabel("INL value", fontsize=12)
            plt.grid(axis='x')
            plt.legend()
            plt.title("INL in 4.7 7.8 14 25 mV/fC", fontsize=12)

            plt.subplot(1, 2, 2)
            plt.plot(range(4), gain_set, marker='o', linestyle='-', alpha=0.7, label = 'Gain_SE_OFF')
            plt.plot(2, log.report_log0605[femb_id]["Gain"], marker='o', linestyle='-', alpha=0.7, label = 'Gain_DIFF')
            plt.xlabel("Voltage Gain", fontsize=12)
            plt.ylabel("Gain", fontsize=12)
            plt.grid(axis='x')
            plt.legend()
            plt.title("Gain in 4.7 7.8 14 25 mV/fC", fontsize=12)
            plt.savefig(report_dir + 'Cali1.png')
            plt.close()

            plt.figure(figsize=(6,4))
            x = ["4.7", "7.8", "14", "25"]
            plt.errorbar(x, gain_set, yerr=gain_std, color='darkblue', linestyle='-', capsize=5,
                         alpha=0.7, label='Amplitude Gain')
            plt.ylim(0, 120)
            plt.xlabel("Gain Setting", fontsize = 14)
            plt.ylabel("Amplitude Gain / e-/bit", fontsize = 14)
            plt.xticks(x, ["4.7", "7.8", "14", "25"])
            plt.grid(True, axis='y', linestyle='--')
            plt.margins(x=0.15)
            for i in range(len(x)):
                plt.text(x[i], gain_set[i] + 5, f'{round(gain_set[i], 1)}±{round(gain_std[i], 1)}', fontsize=10, ha='center', va='bottom', color='darkblue')
            plt.title("Amplitude Gain in 4.7 7.8 14 25 mV/fC", fontsize = 14)
            plt.gca().set_facecolor('none')
            plt.savefig(report_dir + 'SE_Gain.png', transparent = True)
            plt.close()

            plt.figure(figsize=(6,4))
            x = ["4.7", "7.8", "14", "25"]
            plt.errorbar(x, ENC_set, yerr=ENC_std, color='darkblue', linestyle='-', capsize=5,
                         alpha=0.7, label='ENC')
            plt.ylim(0, 1200)
            plt.xlabel("Gain Setting", fontsize = 14)
            plt.ylabel("ENC / e-", fontsize = 14)
            plt.xticks(x, ["4.7", "7.8", "14", "25"])
            plt.grid(True, axis='y', linestyle='--')
            plt.margins(x=0.15)
            for i in range(len(x)):
                plt.text(x[i], ENC_set[i] + 50, f'{round(ENC_set[i], 1)}±{round(ENC_std[i], 1)}', fontsize=10, ha='center', va='bottom', color='darkblue')
            plt.title("ENC in 4.7 7.8 14 25 mV/fC", fontsize = 14)
            plt.gca().set_facecolor('none')
            plt.savefig(report_dir + 'SE_ENC.png', transparent = True)
            plt.close()


    #   7  CALI_report_2
    def CALI_report_2(self):
        log.test_label.append(7)
        qc=ana_tools()
        dac_list = range(0,32,1)
        datadir = self.datadir + "CALI2/"
        self.CreateDIR("CALI2")
        print("analyze CALI2 900mVBL 14_0mVfC 2_0us")
        qc.GetGain(self.fembs, self.fembsID, datadir, self.savedir, "CALI2/", "CALI2_SE_{}_{}_{}_0x{:02x}", "900mVBL", "14_0mVfC", "2_0us", dac_list)
        qc.GetENC(self.fembs, self.fembsID, "900mVBL", "14_0mVfC", "2_0us", 0, self.savedir, "CALI2/")
        inl_gain = dict(log.tmp_log)
        inl_gain_check = dict(log.check_log)
        log.report_log0701.update(inl_gain)
        log.check_log0701.update(inl_gain_check)
        self.CreateDIR("CALI2_DIFF")
        print("analyze CALI2 900mVBL 14_0mVfC 2_0us")
        qc.GetGain(self.fembs, self.fembsID, datadir, self.savedir, "CALI2_DIFF/", "CALI2_DIFF_{}_{}_{}_0x{:02x}", "900mVBL", "14_0mVfC", "2_0us", dac_list)
        qc.GetENC(self.fembs, self.fembsID, "900mVBL", "14_0mVfC", "2_0us", 0, self.savedir, "CALI2_DIFF/")
        inl_gain = dict(log.tmp_log)
        inl_gain_check = dict(log.check_log)
        log.report_log0702.update(inl_gain)
        log.check_log0702.update(inl_gain_check)
        for ifemb in self.fembs:
            report_dir = self.savedir[ifemb] + "CALI2_DIFF/"
            femb_id = "FEMB ID {}".format(self.fembsID['femb%d' % ifemb])
            inl_set = [log.report_log0701[femb_id]["INL"], log.report_log0702[femb_id]["INL"]]
            gain_set = [log.report_log0701[femb_id]["Gain"], log.report_log0702[femb_id]["Gain"]]
            plt.figure(figsize=(10, 4))
            plt.subplot(1, 2, 1)
            plt.plot(range(len(inl_set)), inl_set, marker='o', linestyle='-', alpha=0.7, label = 'INL')
            # plt.plot(2, log.report_log0702[femb_id]["INL"], marker='o', linestyle='-', alpha=0.7, label = 'DIFF')
            plt.xlabel("Chip", fontsize=12)
            plt.ylabel("ADC", fontsize=12)
            plt.grid(axis='x')
            plt.legend()
            plt.title("INL in 14 mV/fC SE/DIFF", fontsize=12)
            plt.subplot(1, 2, 2)
            plt.plot(range(len(gain_set)), gain_set, marker='o', linestyle='-', alpha=0.7, label = 'Gain')
            # plt.plot(2, log.report_log0702[femb_id]["Gain"], marker='o', linestyle='-', alpha=0.7, label = 'DIFF')
            plt.xlabel("Chip", fontsize=12)
            plt.ylabel("ADC", fontsize=12)
            plt.grid(axis='x')
            plt.legend()
            plt.title("INL in 14 mV/fC SE/DIFF", fontsize=12)
            plt.savefig(report_dir + 'Cali2.png')
            plt.close()

          # self.GenCALIPDF("900mVBL", "14_0mVfC", "2_0us", 0, "CALI2_DIFF/")

    #   8  CALI_report_3
    def CALI_report_3(self):
        log.test_label.append(8)
        qc=ana_tools()
        dac_list = range(0,64)
        self.CreateDIR("CALI3")
        datadir = self.datadir+"CALI3/"
        print("analyze CALI3 200mVBL 4_7mVfC sgp=1")
        qc.GetGain(self.fembs, self.fembsID, datadir, self.savedir, "CALI3/", "CALI3_SE_{}_{}_{}_0x{:02x}_sgp1", "200mVBL", "4_7mVfC", "2_0us", dac_list,20,10)
        qc.GetENC(self.fembs, self.fembsID, "200mVBL", "4_7mVfC", "2_0us", 1, self.savedir, "CALI3/")
        inl_gain = dict(log.tmp_log)
        inl_gain_check = dict(log.check_log)
        log.report_log0801.update(inl_gain)
        log.check_log0801.update(inl_gain_check)

    #   9  CALI_report_4
    def CALI_report_4(self):
        log.test_label.append(9)
        qc=ana_tools()
        dac_list = range(0,32)
        self.CreateDIR("CALI4")
        datadir = self.datadir+"CALI4/"
        print("analyze CALI4 900mVBL 4_7mVfC sgp=1")
        qc.GetGain(self.fembs, self.fembsID, datadir, self.savedir, "CALI4/", "CALI4_SE_{}_{}_{}_0x{:02x}_sgp1", "900mVBL", "4_7mVfC", "2_0us", dac_list, 10, 4)
        qc.GetENC(self.fembs, self.fembsID, "900mVBL", "4_7mVfC", "2_0us", 1, self.savedir, "CALI4/")
        inl_gain = dict(log.tmp_log)
        inl_gain_check = dict(log.check_log)
        log.report_log0901.update(inl_gain)
        log.check_log0901.update(inl_gain_check)
        # self.GenCALIPDF("900mVBL", "14_0mVfC", "2_0us", 1, "CALI4/")
        # self.CreateDIR("CALI4_DIFF")
        # datadir = self.datadir+"CALI4/"
        # print("analyze CALI4 900mVBL 14_0mVfC sgp=1")
        # qc.GetGain(self.fembs, datadir, self.savedir, "CALI4_DIFF/", "CALI4_DIFF_{}_{}_{}_0x{:02x}_sgp1", "900mVBL", "14_0mVfC", "2_0us", dac_list, 10, 4)
        # qc.GetENC(self.fembs, "900mVBL", "14_0mVfC", "2_0us", 1, self.savedir, "CALI4_DIFF/")
        # self.GenCALIPDF("900mVBL", "14_0mVfC", "2_0us", 1, "CALI4_DIFF/"

    #   10  FE_MON_report
    def FE_MON_report(self):
        log.test_label.append(10)
        self.CreateDIR("MON_FE")
        datadir = self.datadir+"MON_FE/"
        fp = datadir+"LArASIC_mon.bin"
        with open(fp, 'rb') as fn:
             raw = pickle.load(fn)
        print("analyze file: %s"%fp)
        mon_BDG=raw[0]
        mon_TEMP=raw[1]
        mon_200bls_sdf1=raw[2]
        mon_200bls_sdf0=raw[3]
        mon_900bls_sdf1=raw[4]
        mon_900bls_sdf0=raw[5]
        qc=ana_tools()
        bandgap, log.mon_pulse["bandgap"] = qc.PlotMon(self.fembs, mon_BDG, self.savedir, "MON_FE", "bandgap", self.fembsID)
        temp, log.mon_pulse["temperature"] = qc.PlotMon(self.fembs, mon_TEMP, self.savedir, "MON_FE", "temperature", self.fembsID)
        sdf1_200, log.mon_pulse["200mVBL_sdf1"] = qc.PlotMon(self.fembs, mon_200bls_sdf1, self.savedir, "MON_FE", "200mVBL_sdf1", self.fembsID)
        sdf0_200, log.mon_pulse["200mVBL_sdf0"] = qc.PlotMon(self.fembs, mon_200bls_sdf0, self.savedir, "MON_FE", "200mVBL_sdf0", self.fembsID)
        sdf1_900, log.mon_pulse["900mVBL_sdf1"] = qc.PlotMon(self.fembs, mon_900bls_sdf1, self.savedir, "MON_FE", "900mVBL_sdf1", self.fembsID)
        sdf0_900, log.mon_pulse["900mVBL_sdf0"] = qc.PlotMon(self.fembs, mon_900bls_sdf0, self.savedir, "MON_FE", "900mVBL_sdf0", self.fembsID)
        for ifemb in self.fembs:
            report_dir = self.savedir[ifemb] + "MON_FE/"
            femb_id = "FEMB ID {}".format(self.fembsID['femb%d' % ifemb])
            log.report_log10_01[femb_id]["bandgap"] = bandgap[femb_id]["Result"]
            log.report_log10_01[femb_id]["temperature"] = temp[femb_id]["Result"]
            log.report_log10_01[femb_id]["200mVBL_sdf1"] = sdf1_200[femb_id]["Result"]
            log.report_log10_01[femb_id]["200mVBL_sdf0"] = sdf0_200[femb_id]["Result"]
            log.report_log10_01[femb_id]["900mVBL_sdf1"] = sdf1_900[femb_id]["Result"]
            log.report_log10_01[femb_id]["900mVBL_sdf0"] = sdf0_900[femb_id]["Result"]
            if ((bandgap[femb_id]) and (temp[femb_id]) and (sdf1_200[femb_id]) and (sdf0_200[femb_id]) and (sdf1_900[femb_id]) and (sdf0_900[femb_id])):
                log.check_log1001[femb_id]['Result'] = True
            else:
                log.check_log1001[femb_id]['Result'] = False
            plt.figure(figsize=(15, 4))
            plt.subplot(1, 3, 1)
            plt.plot(range(8), log.mon_pulse["bandgap"][femb_id], marker='o', linestyle='-', alpha=0.7, label = 'Bandgap')
            plt.plot(range(8), log.mon_pulse["temperature"][femb_id], marker='o', linestyle='-', alpha=0.7, label = 'temperature')
            plt.xlabel("FEMB Chip", fontsize=12)
            plt.ylabel("ADC", fontsize=12)
            plt.grid(axis='x')
            plt.legend()
            plt.title("SE OFF 200 mV RMS Distribution", fontsize=12)
            plt.subplot(1, 3, 2)
            x_sticks = range(0, 129, 16)
            plt.plot(range(128), log.mon_pulse["200mVBL_sdf0"][femb_id], marker='|', linestyle='-', alpha=0.7, label = '200mVBL_sdf0')
            plt.plot(range(128), log.mon_pulse["900mVBL_sdf0"][femb_id], marker='|', linestyle='-', alpha=0.7, label = '900mVBL_sdf0')
            plt.xlabel("FEMB Channel", fontsize=12)
            plt.ylabel("ADC", fontsize=12)
            plt.xticks(x_sticks)
            plt.grid(axis='x')
            plt.legend()
            plt.title("200mVBL_900mVBL_sdf0", fontsize=12)
            plt.subplot(1, 3, 3)
            x_sticks = range(0, 129, 16)
            plt.plot(range(128), log.mon_pulse["200mVBL_sdf1"][femb_id], marker='|', linestyle='-', alpha=0.7, label = '200mVBL_sdf1')
            plt.plot(range(128), log.mon_pulse["900mVBL_sdf1"][femb_id], marker='|', linestyle='-', alpha=0.7, label = '900mVBL_sdf1')
            plt.xlabel("Channel", fontsize=12)
            plt.ylabel("ADC", fontsize=12)
            plt.xticks(x_sticks)
            plt.grid(axis='x')
            plt.legend()
            plt.title("200mVBL_900mVBL_sdf1", fontsize=12)
            plt.gca().set_facecolor('none')  # set background as transparent
            plt.savefig(report_dir + 'FE_Mon.png', transparent = True)
            plt.close()


    #   11  FE_DAC_MON_report
    def FE_DAC_MON_report(self):
        log.test_label.append(11)
        self.CreateDIR("MON_FE")
        datadir = self.datadir+"MON_FE/"
        fp = datadir+"LArASIC_mon_DAC.bin"
        with open(fp, 'rb') as fn:
             raw = pickle.load(fn)
        print("analyze file: %s"%fp)
        mon_sgp1=raw[0]
        # print(mon_sgp1)
        mon_14mVfC=raw[1]
        mon_7_8mVfC=raw[2]
        mon_25mVfC=raw[3]
        #mon_dict = {'dict1' : mon_sgp1}
        mon_dict = {'LArASIC_DAC_sgp1': mon_sgp1, 'LArASIC_DAC_14mVfC': mon_14mVfC, 'LArASIC_DAC_7_8mVfC': mon_7_8mVfC, 'LArASIC_DAC_25mVfC': mon_25mVfC}
        qc = ana_tools()
        #qc.plotDACMon(self.fembs, mon_dic, self.savedir, "MON_FE", "LArASIC_DAC_sgp1")
        #
        chip_inl = qc.PlotMonDAC(self.fembs, mon_dict, self.savedir, "MON_FE", self.fembsID)
        log.check_log1101.update(chip_inl)
        # print(log.report_log11_01)
        # qc.PlotMonDAC(self.fembs, mon_14mVfC, self.savedir, "MON_FE", "LArASIC_DAC_14mVfC")
        # qc.PlotMonDAC(self.fembs, mon_7_8mVfC, self.savedir, "MON_FE", "LArASIC_DAC_7_8mVfC")
        # qc.PlotMonDAC(self.fembs, mon_25mVfC, self.savedir, "MON_FE", "LArASIC_DAC_25mVfC")

    #   12  ColdADC_DAC_MON_report
    def ColdADC_DAC_MON_report(self):
        log.test_label.append(12)
        self.CreateDIR("MON_ADC")
        datadir = self.datadir+"MON_ADC/"
        fp = datadir+"LArASIC_ColdADC_mon.bin"
        with open(fp, 'rb') as fn:
             raw = pickle.load(fn)
        print("analyze file: %s"%fp)
        mon_default=raw[0]
        mon_dac=raw[1]
        qc=ana_tools()
        qc.PlotADCMon(self.fembs, mon_dac, self.savedir, "MON_ADC",  self.fembsID)
        # inl_gain = dict(log.tmp_log)
        inl_check = dict(log.check_log)
        # log.report_log1202.update(inl_gain)
        log.check_log1201.update(inl_check)


    #   13  Calibration for External Pulse 900 mV Baseline
    def CALI_report_5(self):
        log.test_label.append(13)
        qc=ana_tools()
        dac_list = list(range(125, 325, 25))
        dac_list.append(0)
        self.CreateDIR("CALI5")
        datadir = self.datadir+"CALI5/"
        print("analyze CALI5 900mVBL 14_0mVfC External")
        qc.GetGain(self.fembs, self.fembsID, datadir, self.savedir, "CALI5/", "CALI5_SE_{}_{}_{}_vdac{:06d}mV", "900mVBL", "14_0mVfC", "2_0us", dac_list, 7500, 4)
        qc.GetENC(self.fembs, self.fembsID, "900mVBL", "14_0mVfC", "2_0us", 0, self.savedir, "CALI5/")
        inl_gain = dict(log.tmp_log)
        inl_gain_check = dict(log.check_log)
        log.report_log1301.update(inl_gain)
        log.check_log1301.update(inl_gain_check)
        # self.GenCALIPDF("900mVBL", "14_0mVfC", "2_0us", 0, "CALI5/")

    #   14  Calibration for External Pulse 200 mV Baseline
    def CALI_report_6(self):
        log.test_label.append(14)
        qc=ana_tools()
        dac_list = list(range(125, 500, 25))
        dac_list.append(0)
        self.CreateDIR("CALI6")
        datadir = self.datadir+"CALI6/"
        print("analyze CALI6 200mVBL 14_0mVfC External")
        qc.GetGain(self.fembs, self.fembsID, datadir, self.savedir, "CALI6/", "CALI6_SE_{}_{}_{}_vdac{:06d}mV", "200mVBL", "14_0mVfC", "2_0us", dac_list, 15000, 4)
        qc.GetENC(self.fembs, self.fembsID, "200mVBL", "14_0mVfC", "2_0us", 0, self.savedir, "CALI6/")
        inl_gain = dict(log.tmp_log)
        inl_gain_check = dict(log.check_log)
        log.report_log1401.update(inl_gain)
        log.check_log1401.update(inl_gain_check)
        # self.GenCALIPDF("200mVBL", "14_0mVfC", "2_0us", 0, "CALI6/")

    #   15  ADC DC Noise
    def femb_adc_sync_pat_report(self, fdir):
        log.test_label.append(15)
        self.CreateDIR(fdir)
        datadir = self.datadir+fdir+"/"
        qc = ana_tools()
        files = sorted(glob.glob(datadir+"*.bin"), key=os.path.getmtime)  # list of data files in the dir
        for afile in files:
            with open(afile, 'rb') as fn:
                raw = pickle.load(fn)
            #print("analyze file: %s"%afile)
            rawdata = raw[0]
            pwr_meas = raw[1]
            pldata = qc.data_decode(rawdata, self.fembs)
            if '\\' in afile:
                fname = afile.split("\\")[-1][:-4]
            else:
                fname = afile.split("/")[-1][:-4]
            for ifemb in self.fembs:
                femb_id = "FEMB ID {}".format(self.fembsID['femb%d' % ifemb])
                fp = self.savedir[ifemb] + fdir+"/"
                ped, rms = qc.GetRMS(pldata, ifemb, fp, fname)
                if 'DC_Noise' in fname:
                    if np.max(rms) > 2:
                        log.check_log1501[femb_id]['Result'] = "False"
                    else:
                        log.check_log1501[femb_id]['Result'] = "True"
                if "SHA_SE" in fname:
                    if np.max(rms) > 4:
                        log.check_log1502[femb_id]['Result'] = "False"
                    else:
                        log.check_log1502[femb_id]['Result'] = "True"
                if "SHA_DIFF" in fname:
                    if np.max(rms) > 4:
                        log.check_log1503[femb_id]['Result'] = "False"
                    else:
                        log.check_log1503[femb_id]['Result'] = "True"

#   16  PLL SCAN
    def PLL_scan_report(self, fdir):
        log.test_label.append(16)
        self.CreateDIR(fdir)
        datadir = self.datadir+fdir+"/"
        qc = ana_tools()
        files = sorted(glob.glob(datadir+"*.bin"), key=os.path.getmtime)  # list of data files in the dir
        check = True
        for afile in files:
            with open(afile, 'rb') as fn:
                raw = pickle.load(fn)

            # =========== analysis ===================
            rmsdata = raw[0]
            fembs = raw[2]

                #pldata,_ = qc_tools.data_decode(rmsdata, fembs)
            pldata = qc.data_decode(rmsdata, fembs)
                # pldata = np.array(pldata)

            if '\\' in afile:
                fname = afile.split("\\")[-1][:-4]
            else:
                fname = afile.split("/")[-1][:-4]

            for ifemb in self.fembs:
                femb_id = "FEMB ID {}".format(self.fembsID['femb%d' % ifemb])
                fp = self.savedir[ifemb] + fdir+"/"
                ped,rms=qc.GetRMS(pldata, ifemb, fp, fname)
                if not(max(rms) == 0):
                    check = False
                for i in ped:
                    if not((int(i) == 10901) or (int(i) == 5482)):
                        check = False
                log.report_log1601[femb_id][fname] = check

            self.Gather_PNG_PDF(fp)

        for ifemb in self.fembs:
            femb_id = "FEMB ID {}".format(self.fembsID['femb%d' % ifemb])

            log.check_log1601[femb_id]["Result"] = check







if __name__=='__main__':

    ag = argparse.ArgumentParser()
    ag.add_argument("task", help="a list of tasks to be analyzed", type=int, choices=range(1,13), nargs='+')
    ag.add_argument("-n", "--fembs", help="a list of fembs to be analyzed", type=int, choices=range(0,4), nargs='+')
    args = ag.parse_args()

    tasks = args.task
    fembs = args.fembs

    rp = QC_reports("femb101_femb107_femb105_femb111_LN_150pF", fembs)

    tt={}

    for tm in tasks:
        t1=time.time()
        print("start tm=",tm)
        if tm==1:
           rp.PWR_consumption_report()
        if tm==2:
           rp.PWR_cycle_report()

        if tm==3:
           rp.CHKPULSE("Leakage_Current")

        if tm==4:
           rp.CHKPULSE("CHK")
        if tm==5:
           rp.RMS_report()
        if tm==6:
           rp.CALI_report_1()
        if tm==7:
           rp.CALI_report_2()
        if tm==8:
           rp.CALI_report_3()
        if tm==9:
           rp.CALI_report_4()
        if tm==10:
           rp.FE_MON_report()
        if tm==11:
           rp.FE_DAC_MON_report()
        if tm==12:
           rp.ColdADC_DAC_MON_report()
        t2=time.time()
        tt[tm]=t2-t1
        time.sleep(1)
   
    print(tt)
