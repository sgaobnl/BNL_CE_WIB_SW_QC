# -*- coding: utf-8 -*-
"""
File Name: cls_femb_config.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description:
Created Time: 3/20/2019 4:50:34 PM
Last modified: 10/21/2022 5:02:04 PM

"""

import numpy as np
import sys
import os
import string
import time
from datetime import datetime
import struct
import matplotlib.pyplot as plt
import h5py
import datetime


def generate_report(result_dict):
    print("Generator the test report...")
    from fpdf import FPDF
    import pickle
    pdf = FPDF(orientation='P', unit='mm', format='Letter')
    pdf.alias_nb_pages()
    print("##### FEMB Checkout Test Report #####")
    pdf.add_page()
    pdf.set_font('Times', 'B', 20)
    pdf.cell(85)
    print(pdf.l_margin)
    pdf.l_margin = pdf.l_margin * 2
    pdf.cell(30, 5, 'FEMB#{} Checkout Test Report'.format(result_dict["FEMB_SN"]), 0, 1, 'C')
    pdf.ln(2)

    pdf.set_font('Times', '', 12)
    pdf.cell(30, 5, 'FEMB ID = {}'.format(result_dict["FEMB_SN"]), 0, 1)

    pdf.set_font('Times', '', 12)
    pdf.cell(30, 5, 'Date&Time: %s' % result_dict["datetime"].strftime("%Y-%m-%d %H:%M:%S"), 0, 0)
    pdf.cell(80)
    pdf.cell(30, 5, 'Tester: {}'.format(result_dict["Tester"]), 0, 1)

    pdf.cell(30, 5, 'WIB_TCP_Version: 0x{:02x}'.format(result_dict["WIB_TCP_FW_ver"]), 0, 0)
    pdf.cell(80)
    pdf.cell(30, 5, 'WIB_UDP_Version: 0x{:02x}'.format(result_dict["WIB_UDP_FW_ver"]), 0, 1)

    pdf.cell(30, 5, 'Temperature: {}'.format(result_dict["Env"]), 0, 0)
    pdf.cell(80)
    pdf.cell(30, 5, 'Input Capacitor(Cd): {}'.format(result_dict["Cd"]), 0, 1)
    pdf.cell(30, 5, 'Note: {}'.format(result_dict["Note"][0:80]), 0, 1)
    #    for i in range((len(result_dict["Note"])//70) + 1):
    #        if i == 0:
    #            pdf.cell(30, 5, 'Note: {}'.format(result_dict["Note"][i*70:(i+1)*70]), 0, 1)
    #        else:
    #            pdf.cell(30, 5, '      {}'.format(result_dict["Note"][i*70:(i+1)*70]), 0, 1)

    print("# FEMB configuration #")
    pdf.ln(2)
    pdf.cell(70)
    pdf.cell(30, 5, 'FEMB Configuration', 0, 1, 'C')
    pdf.cell(30, 5, 'FE_CFG: {}'.format(result_dict["FE_CFG"]), 0, 1)
    pdf.cell(30, 5, 'ADC_CFG: {}'.format(result_dict["ADC_CFG0"]), 0, 1)
    pdf.cell(30, 5, 'ADC_CFG: {}'.format(result_dict["ADC_CFG1"]), 0, 1)
    pdf.cell(30, 5, 'CD_FE_pulse: {}'.format(result_dict["CD_FE_pulse"]), 0, 1)

    # Generate Power Check table
    print("# Generate Power Check table")
    data = [["Power rail", "V_set /V", "V_meas /V", "I_meas /A", "P_meas /W"],
            ["LArASIC", 0, 0, 0, 0],
            ["ColdADC", 0, 0, 0, 0],
            ["COLDATA", 0, 0, 0, 0],
            [" BIAS  ", 0, 0, 0, 0]
            ]
    data[1][1] = result_dict["power_vfe_ref"][0]
    data[1][2] = result_dict["power_vfe_meas"][0]
    data[1][3] = result_dict["power_vfe_meas"][1]
    data[1][4] = result_dict["power_vfe_meas"][0] * result_dict["power_vfe_meas"][1]
    data[2][1] = result_dict["power_vadc_ref"][0]
    data[2][2] = result_dict["power_vadc_meas"][0]
    data[2][3] = result_dict["power_vadc_meas"][1]
    data[2][4] = result_dict["power_vadc_meas"][0] * result_dict["power_vadc_meas"][1]
    data[3][1] = result_dict["power_vcd_ref"][0]
    data[3][2] = result_dict["power_vcd_meas"][0]
    data[3][3] = result_dict["power_vcd_meas"][1]
    data[3][4] = result_dict["power_vcd_meas"][0] * result_dict["power_vcd_meas"][1]
    data[4][1] = result_dict["power_bias_ref"][0]
    data[4][2] = result_dict["power_bias_meas"][0]
    data[4][3] = result_dict["power_bias_meas"][1]
    data[4][4] = result_dict["power_bias_meas"][0] * result_dict["power_bias_meas"][1]
    femb_pwr_con = data[1][4] + data[2][4] + data[3][4] + data[4][4]

    pdf.ln(2)
    pdf.cell(70)
    pdf.cell(30, 5, 'FE SE OFF Interface Power Consumption (including cable dissipation) = {:0.3f}W'.format(femb_pwr_con), 0, 1, 'C')
    epw = pdf.w - 2 * pdf.l_margin
    col_width = epw / 5
    pdf.set_font('Times', '', 12)
    th = pdf.font_size  # print ("# Text height is the same as current font size")
    pdf.ln(0.4 * th)
    for j in range(len(data)):
        for i in range(len(data[j])):
            if j == 0 or i == 0:
                pdf.cell(col_width, 2 * th, "{}".format(data[j][i]), border=1, align='C')
            else:
                pdf.cell(col_width, 2 * th, "{:0.3f}".format(data[j][i]), border=1, align='C')
        pdf.ln(2 * th)
    pdf.ln(2)
















    #
    #
    # # Generate Power Check table
    # print("# Generate Power Check table [SDC mode]")
    # data = [["Power rail", "V_set /V", "V_meas /V", "I_meas /A", "P_meas /W"],
    #         ["LArASIC", 0, 0, 0, 0],
    #         ["ColdADC", 0, 0, 0, 0],
    #         ["COLDATA", 0, 0, 0, 0],
    #         [" BIAS  ", 0, 0, 0, 0]
    #         ]
    # data[1][1] = result_dict["power_vfe_ref"][0]
    # data[1][2] = result_dict["power_vfe_meas_diff"][0]
    # data[1][3] = result_dict["power_vfe_meas_diff"][1]
    # data[1][4] = result_dict["power_vfe_meas_diff"][0] * result_dict["power_vfe_meas_diff"][1]
    # data[2][1] = result_dict["power_vadc_ref"][0]
    # data[2][2] = result_dict["power_vadc_meas_diff"][0]
    # data[2][3] = result_dict["power_vadc_meas_diff"][1]
    # data[2][4] = result_dict["power_vadc_meas_diff"][0] * result_dict["power_vadc_meas_diff"][1]
    # data[3][1] = result_dict["power_vcd_ref"][0]
    # data[3][2] = result_dict["power_vcd_meas_diff"][0]
    # data[3][3] = result_dict["power_vcd_meas_diff"][1]
    # data[3][4] = result_dict["power_vcd_meas_diff"][0] * result_dict["power_vcd_meas_diff"][1]
    # data[4][1] = result_dict["power_bias_ref"][0]
    # data[4][2] = result_dict["power_bias_meas_diff"][0]
    # data[4][3] = result_dict["power_bias_meas_diff"][1]
    # data[4][4] = result_dict["power_bias_meas_diff"][0] * result_dict["power_bias_meas_diff"][1]
    # femb_pwr_con = data[1][4] + data[2][4] + data[3][4] + data[4][4]
    #
    # pdf.ln(2)
    # pdf.cell(70)
    # pdf.cell(30, 5, 'FE DIFF Interface Power Consumption (including cable dissipation) = {:0.3f}W'.format(femb_pwr_con), 0, 1, 'C')
    # epw = pdf.w - 2 * pdf.l_margin
    # col_width = epw / 5
    # pdf.set_font('Times', '', 12)
    # th = pdf.font_size  # print ("# Text height is the same as current font size")
    # pdf.ln(0.4 * th)
    # for j in range(len(data)):
    #     for i in range(len(data[j])):
    #         if j == 0 or i == 0:
    #             pdf.cell(col_width, 2 * th, "{}".format(data[j][i]), border=1, align='C')
    #         else:
    #             pdf.cell(col_width, 2 * th, "{:0.3f}".format(data[j][i]), border=1, align='C')
    #     pdf.ln(2 * th)
    # pdf.ln(2)







    # Generate Monitoring Check table
    asic = 0
    print("# Generate Monitoring Check table")
    data = [["ASIC# ", "FE Vref", "FE T", "ADC VCMI", "ADC VCMO", "ADC VREFP", "ADC VREFN", ],
            ["{}".format(0), 0, 0, 0, 0, 0, 0],
            ["{}".format(4), 0, 0, 0, 0, 0, 0],
            ]
    asic = 0
    # data[1][1] = int(result_dict["Mon_LArASIC{:02d}_BGR".format(asic)][0])
    # data[1][2] = int(result_dict["Mon_LArASIC{:02d}_Temperature".format(asic)][0])
    data[1][3] = int(result_dict["ADC{:02d}_MeasRef".format(asic)][1][0])
    data[1][4] = int(result_dict["ADC{:02d}_MeasRef".format(asic)][2][0])
    data[1][5] = int(result_dict["ADC{:02d}_MeasRef".format(asic)][3][0])
    data[1][6] = int(result_dict["ADC{:02d}_MeasRef".format(asic)][4][0])

    asic = 4
    # data[2][1] = int(result_dict["Mon_LArASIC{:02d}_BGR".format(asic)][0])
    # data[2][2] = int(result_dict["Mon_LArASIC{:02d}_Temperature".format(asic)][0])
    data[2][3] = int(result_dict["ADC{:02d}_MeasRef".format(asic)][1][0])
    data[2][4] = int(result_dict["ADC{:02d}_MeasRef".format(asic)][2][0])
    data[2][5] = int(result_dict["ADC{:02d}_MeasRef".format(asic)][3][0])
    data[2][6] = int(result_dict["ADC{:02d}_MeasRef".format(asic)][4][0])

    pdf.ln(1)
    pdf.cell(70)
    pdf.cell(30, 5, 'Monitoring path for FE-ADC#0 (unit: mV)', 0, 1, 'C')
    epw = pdf.w - 2 * pdf.l_margin
    col_width = epw / 7
    pdf.set_font('Times', '', 12)
    th = pdf.font_size  # print ("# Text height is the same as current font size")
    pdf.ln(0.4 * th)
    for j in range(len(data)):
        for i in range(len(data[j])):
            if j == 0 or i == 0:
                pdf.cell(col_width, 2 * th, "{}".format(data[j][i]), border=1, align='C')
            else:
                pdf.cell(col_width, 2 * th, "{:0.3f}".format(data[j][i]), border=1, align='C')
        pdf.ln(2 * th)
    pdf.ln(2)
    #######################################################
    pdf.image(result_dict["response.png"], 10, 160, 190)

    filename = result_dict["save_dir"] + "result.pdf"
    pdf.output(filename, 'F')
    pdf.close()

    with open(result_dict["save_dir"] + "result.bin", 'wb') as fp:
        pickle.dump(result_dict, fp)


def data_ana(femb_data):
    chn_rmss = []
    chn_peds = []
    chn_pkps = []
    chn_pkns = []
    chn_onewfs = []
    chn_avgwfs = []

    for chipi in range(8):
        plsn = (len(femb_data[chipi][0]) // 512) - 10
        if plsn > 100:
            psln = 100

        for i in range(plsn):
            if i == 0:
                avg_wf = np.array(femb_data[chipi][0][0:512]) & 0xffff
            else:
                avg_wf = avg_wf + (np.array(femb_data[chipi][0][512 * i:512 * i + 512]) & 0xffff)
        avg_wf = avg_wf // plsn
        posp = np.where(avg_wf == np.max(avg_wf))[0][0] + 512 - 50

        for chn in range(16):
            peddata = []
            chndata = femb_data[chipi][chn][posp:]
            one_wf = chndata[0:512]
            for i in range(plsn):
                peddata += chndata[100 + 512 * i: 270 + 512 * i]
                if i == 0:
                    avg_wf = np.array(chndata[0:512]) & 0xffff
                else:
                    avg_wf = avg_wf + (np.array(chndata[512 * i:512 * i + 512]) & 0xffff)
            avg_wf = avg_wf // plsn

            rms = np.std(peddata)
            ped = int(np.mean(peddata))
            peakp = np.max(avg_wf)
            peakn = np.min(avg_wf)

            chn_rmss.append(rms)
            chn_peds.append(ped)
            chn_pkps.append(peakp)
            chn_pkns.append(peakn)
            chn_onewfs.append(one_wf)
            chn_avgwfs.append(avg_wf)
    return chn_rmss, chn_peds, chn_pkps, chn_pkns, chn_onewfs, chn_avgwfs


def FEMB_SUB_PLOT(ax, x, y, title, xlabel, ylabel, color='b', marker='.', atwinx=False, ylabel_twx="", e=None):
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(True)
    if (atwinx):
        ax.errorbar(x, y, e, marker=marker, color=color)
        y_min = int(np.min(y)) - 1000
        y_max = int(np.max(y)) + 1000
        ax.set_ylim([y_min, y_max])
        ax2 = ax.twinx()
        ax2.set_ylabel(ylabel_twx)
        ax2.set_ylim([int((y_min / 16384.0) * 2048), int((y_max / 16384.0) * 2048)])
    else:
        ax.plot(x, y, marker=marker, color=color)


def FEMB_PLOT(chn_rmss, chn_peds, chn_pkps, chn_pkns, chn_onewfs, chn_avgwfs, save_dir):
    #    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(10, 6))
    ax1 = plt.subplot2grid((4, 4), (0, 0), colspan=2, rowspan=2)
    plt.ylim(0, 5)
    ax2 = plt.subplot2grid((4, 4), (0, 2), colspan=2, rowspan=2)
    ax3 = plt.subplot2grid((4, 4), (2, 0), colspan=2, rowspan=2)
    ax4 = plt.subplot2grid((4, 4), (2, 2), colspan=2, rowspan=2)
    chns = range(128)
    FEMB_SUB_PLOT(ax1, chns, chn_rmss, title="RMS Noise", xlabel="CH number", ylabel="ADC / bin", color='r', marker='.')
    FEMB_SUB_PLOT(ax2, chns, chn_peds, title="Red: Pos Peak. Blue: Pedestal. Green: Neg Peak", xlabel="CH number",
                  ylabel="ADC / bin", color='r', marker='.')
    FEMB_SUB_PLOT(ax2, chns, chn_pkps, title="Red: Pos Peak. Blue: Pedestal. Green: Neg Peak", xlabel="CH number",
                  ylabel="ADC / bin", color='b', marker='.')
    FEMB_SUB_PLOT(ax2, chns, chn_pkns, title="Red: Pos Peak. Blue: Pedestal. Green: Neg Peak", xlabel="CH number",
                  ylabel="ADC / bin", color='g', marker='.')
    for chni in chns:
        if chni != 500:
            ts = 300
            x = (np.arange(125)) * 0.5
            y1 = chn_onewfs[chni]
            y3 = chn_onewfs[chni][25:75] + chn_onewfs[chni][ts - 50:ts + 25]

            y4 = chn_onewfs[chni][25:75] + chn_onewfs[chni][ts - 50:ts + 25]

            # print(y1)
            # print(y3)
            # print(y4)
            FEMB_SUB_PLOT(ax3, x, y3, title="Waveform Overlap (1 cycle)", xlabel="Time", ylabel="ADC /bin",
                          color='C%d' % (chni % 9))
            FEMB_SUB_PLOT(ax4, x, y4, title="Averaging(100 Cycles) Waveform Overlap", xlabel="Time",
                          ylabel="ADC /bin", color='C%d' % (chni % 9))

    plt.tight_layout(rect=[0.05, 0.05, 0.95, 0.95])
    fn = save_dir + "response.png"
    plt.savefig(fn)
    plt.close()
    return fn


def FEMB_CHKOUT_Input(SN = '4', rootdir = 'D:/Warm_Integrated_Board/Report/'):
    tester = 'lke'
    femb_sn = SN # int(input("please input FEMB SN (000-999): "))
    env = 'RT'
    note = 'for WIB QC' #input("A short note (<80 letters):")
    ToyTPC = '0pF'
    save_dir = rootdir + "FEMB{}_{}_{}/".format(femb_sn, env, ToyTPC)
    if (os.path.exists(save_dir)):
        print("Folder exist, please check the entering infomation...")
        exit_en = "n"
        if ("Y" in exit_en) or ("y" in exit_en):
            input("hit any button and then 'Enter' to exit")
            exit()
        else:
            i = 0
            while (True):
                i = i + 1
                fd_new = save_dir[:-1] + "_R{:03d}/".format(i)
                if (os.path.exists(fd_new)):
                    pass
                else:
                    try:
                        os.makedirs(fd_new)
                    except OSError:
                        print("Error to create folder %s" % fd_new)
                        input("hit any button and then 'Enter' to exit")
                        sys.exit()
                    save_dir = fd_new
                    break
    else:
        try:
            os.makedirs(save_dir)
        except OSError:
            print("Error to create folder %s" % save_dir)
            input("hit any button and then 'Enter' to exit")
            sys.exit()
    return femb_sn, env, ToyTPC, save_dir, tester, note


def pwr_chk(pwr_info, v_fe, v_adc, v_cd, v_bias, iref_fe, iref_adc, iref_cd, iref_bias):
    pwr_en = 1
    if abs(v_fe - pwr_info[0][0]) > 0.2:
        print("Power rail for FE, set={}V, read={}V, please check connection".format(v_fe, pwr_info[0][0]))
        pwr_en = 0
    if abs(v_adc - pwr_info[1][0]) > 0.2:
        print("Power rail for ADC, set={}V, read={}V, please check connection".format(v_adc, pwr_info[1][0]))
        pwr_en = 0
    if abs(v_cd - pwr_info[2][0]) > 0.2:
        print("Power rail for CD, set={}V, read={}V, please check connection".format(v_cd, pwr_info[2][0]))
        pwr_en = 0
    if abs(v_bias - pwr_info[4][0]) > 0.2:
        print("Power rail for BIAS, set={}V, read={}V, please check connection".format(v_bias, pwr_info[4][0]))
        pwr_en = 0

    if abs(iref_fe - pwr_info[0][1]) > 0.1:
        if abs(0.63 - pwr_info[0][1]) > 0.1:
            if abs(iref_fe - pwr_info[0][1]) > 0.1:
                print("Power rail for FE, current of range, ref={}A, read={}A, please check connection".format(iref_fe,
                                                                                                       pwr_info[0][1]))
                pwr_en = 0
    if abs(iref_adc - pwr_info[1][1]) > 0.2:
        print("Power rail for ADC, current of range, ref={}A, read={}A, please check connection".format(iref_adc,
                                                                                                        pwr_info[1][1]))
        pwr_en = 0
    if abs(iref_cd - pwr_info[2][1]) > 0.1:
        print("Power rail for CD, current of range, ref={}A, read={}A, please check connection".format(iref_cd,
                                                                                                       pwr_info[2][1]))
        pwr_en = 0
    if abs(iref_bias - pwr_info[4][1]) > 0.1:
        print("Power rail for BIAS, current of range, ref={}A, read={}A, please check connection".format(iref_bias,
                                                                                                         pwr_info[4][1]))
        pwr_en = 0
    return pwr_en


'''

tcp = TCP_CFG()
udp = CLS_UDP()
conv = RAW_CONV()

now = datetime.datetime.now()
rootdir ="D:/Warm_Integrated_Board/Report/"

print ("Initial experiment start...")
result_dict ={} 
result_dict["datetime"] = now
result_dict["rootdir"] = rootdir

print("01")
ver = tcp.wib_ver()
print("011")   
if (ver[1] == 0x100):
    print ("TCP link built.")

result_dict["WIB_TCP_FW_ver"] = ver[1]
print("02")
longcable = False 
if longcable: 
    print ("Long cable is in use...")
    tcp.tcp_poke(addr=0x08, data=longcable)
    if (tcp.tcp_peek(addr=0x08) == longcable):
        pass
    else:
        print("Configuration for long cable is error, please check, exit anyway.")
        input ("hit any button and then 'Enter' to exit")
        exit()
else:
    print ("Short cable is in use...")
    tcp.tcp_poke(addr=0x08, data=longcable)
    if tcp.tcp_peek(addr=0x08) == longcable:
        pass
    else:
        print("Configuration for short cable is error, please check, exit anyway.")
        input ("hit any button and then 'Enter' to exit")
        exit()
print("03")
udpver = udp.read_reg_wib(reg=0x100)
if (udpver == 0x1A5):
    print ("UDP link built.")
result_dict["WIB_UDP_FW_ver"] = udpver

femb = int(input("FEMB (0-3): "))
#femb=0
if femb == 0:
    tcp.link_cs = 0
elif femb == 1:
    tcp.link_cs = 2
elif femb == 2:
    tcp.link_cs = 4
elif femb == 3:
    tcp.link_cs = 6
print("04")
femb_sn, env, toytpc, save_dir, tester, note = FEMB_CHKOUT_Input(rootdir)
result_dict["FEMB_SN"] = femb_sn
result_dict["Env"] = env 
result_dict["Cd"] = toytpc 
result_dict["save_dir"] = save_dir 
result_dict["Tester"] =  tester
result_dict["Note"] = note 

################################################################################################
##power consumption
print ("Turn on FEMB on WIB slot {}".format(femb))
v_fe=3.0
v_adc=3.5
v_cd=2.8
v_bias = 5.0
iref_fe=0.42
iref_adc=1.29
iref_cd=0.18
iref_bias =0.05

tcp.femb_pwr_set(femb=femb, pwr_on=0)
time.sleep(5)

tcp.femb_pwr_set(femb=femb, pwr_on=1, v_fe=v_fe, v_adc=v_adc, v_cd=v_cd)
time.sleep(2)
tcp.set_fe_board(sts=0,snc=0,sg0=0,sg1=0,st0=1,st1=1,swdac=0,dac=0x0)
tcp.femb_cfg()
time.sleep(2)
for i in range(5):
    pwr_info = tcp.femb_pwr_rd(femb=femb)
    time.sleep(.2)
pwr_info = tcp.femb_pwr_rd(femb=femb)
time.sleep(1)
pwr_info = tcp.femb_pwr_rd(femb=femb)
pwr_info = tcp.femb_pwr_rd(femb=femb)
pwr_info = tcp.femb_pwr_rd(femb=femb)
pwr_en = pwr_chk(pwr_info, v_fe, v_adc, v_cd, v_bias, iref_fe, iref_adc, iref_cd, iref_bias)
if pwr_en ==0 :
    tcp.femb_pwr_set(femb=femb, pwr_on=0)
    input ("hit any button and then 'Enter' to exit")
    exit()
    print ("Turn FEMB off and exit...")
else:
    print ("FEMB power consumption is in the normal range")
result_dict["power_vfe_ref"] =  (v_fe,  iref_fe)
result_dict["power_vadc_ref"] = (v_adc, iref_adc)
result_dict["power_vcd_ref"] =  (v_cd,  iref_cd,)
result_dict["power_bias_ref"] = (v_bias,iref_bias)

##########1#####################################################################################
#FEMB configuration: 14mV/fC, 200mV BL, 2.0us, single-ended, 500pA, ASICDAC=0x10, Cali_enable, SDC off,
result_dict["FE_CFG"] = "14mV/fC, 900mV BL, 2.0us, SE_OFF, 500pA, ASIC_CAL, ASICDAC=0x10"
result_dict["ADC_CFG0"] = "CMOS reference set to default, Auto Calibration, "  
result_dict["ADC_CFG1"] = "SE, SDC off, offset_binary_format, Auto Calibration, "  
result_dict["CD_FE_pulse"] = "500 samples/pulse, CD Addr0x06:0x30,0x07:0x00, 0x08:0x38, 0x09:0x80"  

print ("Measure monitoring parameters")
tcp.set_fe_board(sts=0,snc=0,sg0=0,sg1=0,st0=1,st1=1,swdac=0,dac=0x0)
tcp.femb_cfg()
#for asic in range(8):
for asic in [0, 4]:
    print ("Measure ASIC {}".format(asic))
    tmp = tcp.femb_adc_mon_cs(femb_no=femb, adc_no=asic)
    result_dict["ADC{:02d}_SetRef".format(asic)] = tmp[1]
    result_dict["ADC{:02d}_MeasRef".format(asic)] = tmp[0]
    tmp = tcp.femb_fe_mon_cs(femb_no=femb, ext_lemo=0, rst_fe=1, mon_type=2, mon_chip = asic)
    result_dict["Mon_LArASIC{:02d}_BGR".format(asic)] = tmp
    tmp = tcp.femb_fe_mon_cs(femb_no=femb, ext_lemo=0, rst_fe=1, mon_type=1, mon_chip = asic)
    result_dict["Mon_LArASIC{:02d}_Temperature".format(asic)] = tmp
#    print (result_dict["ADC{:02d}_MeasRef".format(asic)]) 


print ("Start FEMB configuration: 14mV/fC, 900mV BL, 2.0us, single-ended, 500pA, ASICDAC=0x10, Cali_enable, SDC off")
tcp.set_fe_reset()
tcp.set_fe_board(sts=0,snc=0,sg0=0,sg1=0,st0=1,st1=1,swdac=1,dac=0x10)
tcp.femb_cfg()

#check channel response
print ("Check channel response")
#tcp.cd_fe_cali()
#tcp.fc_act_cal() #enalbe LArASIC calibration

hdf_fp = save_dir + "rawdata.h5"
result_dict["H5"] = hdf_fp

udp.write_reg_wib_checked(2, 1)
time.sleep(1)
print("Enable UDP data stream")
udp.write_reg_wib_checked(2, 1)
time.sleep(1)
ASICs = 8

#to avoid potential cache data in PC
asic=0
wib_asic = (((femb << 16) & 0x000F0000) + ((asic << 8) & 0xFF00))
udp.write_reg_wib_checked(7, 0x80000000)
udp.write_reg_wib_checked(7, wib_asic | 0x80000000)
udp.write_reg_wib_checked(7, wib_asic)
time.sleep(0.01)
data = udp.get_rawdata_packets(val=1000)

femb_data = []
dset = [ [] for i in range(128)]
while True:
    if os.path.isfile(hdf_fp):
        os.remove(hdf_fp)
    with h5py.File(hdf_fp, "a") as f:
        for asic in range(ASICs):
            print("FEMB{} ASIC{} is selected".format(femb, asic))
            asic = asic & 0x0F
            wib_asic = (((femb << 16) & 0x000F0000) + ((asic << 8) & 0xFF00))
            udp.write_reg_wib_checked(7, 0x80000000)
            udp.write_reg_wib_checked(7, wib_asic | 0x80000000)
            udp.write_reg_wib_checked(7, wib_asic)
            time.sleep(0.01)
        #    fn = "Rawdata_" + data_time + "_" + strin + "_FEMB{}_ASIC{}".format(femb,asic) + ".bin"
        #    if "RMS" in strin:
        #        val = 20000
        #    else:
            val = 1000
            data = udp.get_rawdata_packets(val=val)
            chip_data = conv.raw_conv_feedloc(data)
            if chip_data != None:
                end_while = True
                femb_data.append(chip_data)
                for i in range(16):
                    dset[i] = f.create_dataset('CH{}'.format(asic*16 + i), (len(chip_data[i]),), maxshape=(None,), dtype='u2', chunks=True) 
                    dset[i][:] = chip_data[i]
            else:
                end_while = False
        print ("Start data analysis...")
        ana = data_ana(femb_data)
        if end_while:
            break

print ("Measure power consumption...")
pwr_info = tcp.femb_pwr_rd(femb=femb)
result_dict["power_vfe_ref"] =  (v_fe,  iref_fe)
result_dict["power_vadc_ref"] = (v_adc, iref_adc)
result_dict["power_vcd_ref"] =  (v_cd,  iref_cd,)
result_dict["power_bias_ref"] = (v_bias,iref_bias)
result_dict["power_vfe_meas"] =  pwr_info[0]
result_dict["power_vadc_meas"] = pwr_info[1]
result_dict["power_vcd_meas"] =  pwr_info[2]
result_dict["power_bias_meas"] = pwr_info[3]


fn = FEMB_PLOT(ana[0],ana[1],ana[2],ana[3],ana[4],ana[5],save_dir)
result_dict["response.png"] = fn
generate_report(result_dict)

print ("Turn FEMB off")
tcp.femb_pwr_set(femb=femb, pwr_on=0)

print ("Test is done...")
print ("Report is saved at {}".format(result_dict["save_dir"]))

#
'''