# -*- coding: utf-8 -*-
"""
File Name: cls_femb_config.py
Author: GSS
Mail: gao.hillhill@gmail.com
      lingyun.lke@gmail.com
Description:
Created Time: 3/20/2019 4:50:34 PM
Last modified: 05/11/2025 5:02:04 PM
"""
## =========================================
import numpy as np
import sys
import os
import string
import time
from datetime import datetime

import sys
import os

# Add the parent directory to sys.path so 'function' can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from function.cls_udp import CLS_UDP
from function.tcp_cfg import TCP_CFG
import struct
from function.raw_convertor import RAW_CONV
import matplotlib.pyplot as plt
import h5py
import datetime
import function.chkout as chkout_top
import function.rigol_dp832_ps as Power  # import power component
from function.ping_host import ping_host
import platform
import subprocess

## =========================================

##  === 01 power start =====================







print("\033[35m" + "A_RT04_slot_03 : WIB_FEMB_Pulse" + "\033[0m")
print("Power on")
ps = Power.RIGOL_PS_CTL()
ps.ps_init()
ps.off([1, 2, 3])
time.sleep(2)
ps.set_channel(channel=2, voltage=11.95, v_limit=12, c_limit=3)
ps.set_channel(channel=1, voltage=11.8, v_limit=12, c_limit=3)

ps.on([2])
time.sleep(0.1)
ps.on([1])
time.sleep(1)
c1 = ps.measure_params(channel = 1)
c2 = ps.measure_params(channel = 2)
time.sleep(30)
print("Power is acquired, Please start")
## =========================================
time.sleep(1)
##  === 02 internet connection =====================
ping_host(ip_address="192.168.121.1", count=4)
ping_host(ip_address="192.168.121.2", count=4)
# WIB_IP = input("link with 192.168.121.1 (y/n)")
time.sleep(1)

# putty = input("link with putty (y/n)")

import temp as initial
## =========================================
tcp = TCP_CFG()
udp = CLS_UDP()
conv = RAW_CONV()
now = datetime.datetime.now()
base_dir = os.path.dirname(os.path.abspath(__file__))
target_file_path = os.path.join(base_dir, "..", "report", "WIB_to_FEMB_slot_03_power_report")
rootdir = target_file_path

## ========== WIB monitor ADC ================
monitor01 = tcp.wib_mon_adc_read()
print(monitor01)
## =========================================
result_dict = {}
result_dict["datetime"] = now
result_dict["rootdir"] = rootdir
ver = tcp.wib_ver()
if (ver[1] == 0x100):
    print("TCP link built.")  # 04 TCP/IP communication confirm
result_dict["WIB_TCP_FW_ver"] = ver[1]
longcable = False
if longcable:
    print("Long cable is in use...")
    tcp.tcp_poke(addr=0x08, data=longcable)
    if (tcp.tcp_peek(addr=0x08) == longcable):
        pass
    else:
        print("Configuration for long cable is error, please check, exit anyway.")
        input("hit any button and then 'Enter' to exit")
        exit()
else:
    print("Short cable is in use...")
    tcp.tcp_poke(addr=0x08, data=longcable)
    if tcp.tcp_peek(addr=0x08) == longcable:
        pass
    else:
        print("Configuration for short cable is error, please check, exit anyway.")
        input("hit any button and then 'Enter' to exit")
        exit()
udpver = udp.read_reg_wib(reg=0x100)
if (udpver == 0x1A5):  # 05 UDP communication Confirm
    print("UDP link built.")
result_dict["WIB_UDP_FW_ver"] = udpver

print("Initial experiment start...")

tcp.tcp_poke(addr=0x16, data=0x01)
tcp.tcp_peek(addr=0x16)
# ## ==========BREAK_FOR_DEBUG================
time.sleep(1)
# print("Break02")
# Break = input("Pass02 (y/n)")
## =========================================
tcp.tcp_poke(addr=0x16, data=0x00)
tcp.tcp_peek(addr=0x16)
## ==========BREAK_FOR_DEBUG================
time.sleep(1)
# print("Break03")
# Break = input("Pass03 (y/n)")
## =========================================

for fembi in [3]:
    print(fembi)
    femb = int(fembi)
    if femb == 0:
        tcp.link_cs = 0
    elif femb == 1:
        tcp.link_cs = 2
    elif femb == 2:
        tcp.link_cs = 4
    elif femb == 3:
        tcp.link_cs = 6
    femb_sn, env, toytpc, save_dir, tester, note = chkout_top.FEMB_CHKOUT_Input(SN = femb, rootdir=rootdir)
    result_dict["FEMB_SN"] = femb_sn
    result_dict["Env"] = env
    result_dict["Cd"] = toytpc
    result_dict["save_dir"] = save_dir
    result_dict["Tester"] = tester
    result_dict["Note"] = note

    # Power On
    print("Turn on FEMB on WIB slot {}".format(femb))
    v_fe = 3
    v_adc = 3.5
    v_cd = 3
    v_bias = 5.0
    iref_fe = 0.42
    iref_adc = 1.6
    iref_cd = 0.2
    iref_bias = 0.05
    tcp.femb_pwr_set(femb=femb, pwr_on=0)
    time.sleep(1)
    tcp.femb_pwr_set(femb=femb, pwr_on=1, v_fe=v_fe, v_adc=v_adc, v_cd=v_cd)
    time.sleep(1)

    #
    print('SEOFF')
    tcp.set_fe_board(sts=0, snc=0, sg0=0, sg1=0, st0=1, st1=1, swdac=0, dac=0x0)
    tcp.femb_cfg()
    time.sleep(1)
    for i in range(5):
        pwr_info = tcp.femb_pwr_rd(femb=femb)
        time.sleep(0.2)
    time.sleep(1)
    pwr_info = tcp.femb_pwr_rd(femb=femb)
    print(pwr_info)
    pwr_en = chkout_top.pwr_chk(pwr_info, v_fe, v_adc, v_cd, v_bias, iref_fe, iref_adc, iref_cd, iref_bias)
    if pwr_en == 0:
        tcp.femb_pwr_set(femb=femb, pwr_on=0)
        input("hit any button and then 'Enter' to exit")
        exit()
    else:
        print("FEMB power consumption is in the normal range")
    result_dict["power_vfe_ref"] = (v_fe, iref_fe)
    result_dict["power_vadc_ref"] = (v_adc, iref_adc)
    result_dict["power_vcd_ref"] = (v_cd, iref_cd)
    result_dict["power_bias_ref"] = (v_bias, iref_bias)



    # SEON
    print('SEON')
    tcp.set_fe_board(sts=0, snc=0, sg0=0, sg1=0, st0=1, st1=1, sdf = 1, swdac=1, dac=0x20)
    tcp.femb_cfg_sdc()
    time.sleep(1)
    for i in range(5):
        pwr_info = tcp.femb_pwr_rd(femb=femb)
        time.sleep(0.2)
    time.sleep(1)
    pwr_info_sdc = tcp.femb_pwr_rd(femb=femb)
    print(pwr_info)
    pwr_en = chkout_top.pwr_chk(pwr_info, v_fe, v_adc, v_cd, v_bias, iref_fe, iref_adc, iref_cd, iref_bias)
    if pwr_en == 0:
        tcp.femb_pwr_set(femb=femb, pwr_on=0)
        input("hit any button and then 'Enter' to exit")
        exit()
    else:
        print("FEMB power consumption is in the normal range")
    result_dict["power_vfe_ref_sdc"] = (v_fe, iref_fe)
    result_dict["power_vadc_ref_sdc"] = (v_adc, iref_adc)
    result_dict["power_vcd_ref_sdc"] = (v_cd, iref_cd)
    result_dict["power_bias_ref_sdc"] = (v_bias, iref_bias)

    # DIFF
    print('DIFF')
    tcp.set_fe_board(sts=0, snc=0, sg0=0, sg1=0, st0=1, st1=1, sdd = 1, swdac=1, dac=0x20)
    tcp.femb_cfg_diff()
    time.sleep(1)
    for i in range(5):
        pwr_info = tcp.femb_pwr_rd(femb=femb)
        time.sleep(0.2)
    time.sleep(1)
    pwr_info_diff = tcp.femb_pwr_rd(femb=femb)
    print(pwr_info)
    pwr_en = chkout_top.pwr_chk(pwr_info, v_fe, v_adc, v_cd, v_bias, iref_fe, iref_adc, iref_cd, iref_bias)
    if pwr_en == 0:
        tcp.femb_pwr_set(femb=femb, pwr_on=0)
        input("hit any button and then 'Enter' to exit")
        exit()
    else:
        print("FEMB power consumption is in the normal range")
    result_dict["power_vfe_ref_diff"] = (v_fe, iref_fe)
    result_dict["power_vadc_ref_diff"] = (v_adc, iref_adc)
    result_dict["power_vcd_ref_diff"] = (v_cd, iref_cd)
    result_dict["power_bias_ref_diff"] = (v_bias, iref_bias)



    ##########1#####################################################################################
    # FEMB configuration: 14mV/fC, 200mV BL, 2.0us, single-ended, 500pA, ASICDAC=0x10, Cali_enable, SDC off,
    result_dict["FE_CFG"] = "14mV/fC, 900mV BL, 2.0us, SE_OFF, 500pA, ASIC_CAL, ASICDAC=0x10"
    result_dict["ADC_CFG0"] = "CMOS reference set to default, Auto Calibration, "
    result_dict["ADC_CFG1"] = "SE, SDC off, offset_binary_format, Auto Calibration, "
    result_dict["CD_FE_pulse"] = "500 samples/pulse, CD Addr0x06:0x30,0x07:0x00, 0x08:0x38, 0x09:0x80"

    print("Measure monitoring parameters")
    tcp.set_fe_board(sts=0, snc=0, sg0=0, sg1=0, st0=1, st1=1, swdac=0, dac=0x0)
    tcp.femb_cfg()
    # for asic in range(8):
    for asic in [0, 4]:
        print("Measure ASIC {}".format(asic))
        tmp = tcp.femb_adc_mon_cs(femb_no=femb, adc_no=asic)
        result_dict["ADC{:02d}_SetRef".format(asic)] = tmp[1]
        result_dict["ADC{:02d}_MeasRef".format(asic)] = tmp[0]
    for asic in [0, 4]:
        tmp = tcp.femb_fe_mon_cs(femb_no=femb, ext_lemo=0, rst_fe=0, mon_type=2, mon_chip=asic)
        result_dict["Mon_LArASIC{:02d}_BGR".format(asic)] = tmp
    for asic in [0, 4]:
        tmp = tcp.femb_fe_mon_cs(femb_no=femb, ext_lemo=0, rst_fe=0, mon_type=1, mon_chip=asic)
        result_dict["Mon_LArASIC{:02d}_Temperature".format(asic)] = tmp

    print("Start FEMB configuration: 14mV/fC, 900mV BL, 2.0us, single-ended, 500pA, ASICDAC=0x10, Cali_enable, SDC off")
    #   [sg0 = 0, sg1 = 0 => 14mV/fC]   [snc = 0 => 900mV baseline] [st0 = 1, st1 = 1 => 2 us] [sts = 1 => test capacitance enable]
    tcp.set_fe_reset()
    tcp.set_fe_board(sts=1, snc=0, sg0=0, sg1=0, st0=1, st1=1, swdac=1, dac=0x20)
    tcp.set_fe_sync()
    tcp.femb_cfg()
    # check channel response
    print("Check channel response")

    hdf_fp = save_dir + "rawdata.h5"
    result_dict["H5"] = hdf_fp

    udp.write_reg_wib_checked(2, 1)
    time.sleep(1)
    print("Enable UDP data stream")
    udp.write_reg_wib_checked(2, 1)
    time.sleep(1)
    ASICs = 8

    # to avoid potential cache data in PC
    asic = 0
    wib_asic = (((femb << 16) & 0x000F0000) + ((asic << 8) & 0xFF00))
    udp.write_reg_wib_checked(7, 0x80000000)
    udp.write_reg_wib_checked(7, wib_asic | 0x80000000)
    udp.write_reg_wib_checked(7, wib_asic)
    time.sleep(0.01)
    data = udp.get_rawdata_packets(val=1000)

    femb_data = []
    dset = [[] for i in range(128)]
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
                val = 1000
                data = udp.get_rawdata_packets(val=val)
                chip_data = conv.raw_conv_feedloc(data)
                if chip_data != None:
                    end_while = True
                    femb_data.append(chip_data)
                    for i in range(16):
                        dset[i] = f.create_dataset('CH{}'.format(asic * 16 + i), (len(chip_data[i]),), maxshape=(None,),
                                                   dtype='u2', chunks=True)
                        dset[i][:] = chip_data[i]
                else:
                    end_while = False
            print("Start data analysis...")
            ana = chkout_top.data_ana(femb_data)
            if end_while:
                break

    print("Measure power consumption...")
    pwr_info = tcp.femb_pwr_rd(femb=femb)
    result_dict["power_vfe_ref"] = (v_fe, iref_fe)
    result_dict["power_vadc_ref"] = (v_adc, iref_adc)
    result_dict["power_vcd_ref"] = (v_cd, iref_cd,)
    result_dict["power_bias_ref"] = (v_bias, iref_bias)
    result_dict["power_vfe_meas"] = pwr_info[0]
    result_dict["power_vadc_meas"] = pwr_info[1]
    result_dict["power_vcd_meas"] = pwr_info[2]
    result_dict["power_bias_meas"] = pwr_info[4]

    result_dict["power_vfe_meas_sdc"] = pwr_info_sdc[0]
    result_dict["power_vadc_meas_sdc"] = pwr_info_sdc[1]
    result_dict["power_vcd_meas_sdc"] = pwr_info_sdc[2]
    result_dict["power_bias_meas_sdc"] = pwr_info_sdc[4]

    result_dict["power_vfe_meas_diff"] = pwr_info_diff[0]
    result_dict["power_vadc_meas_diff"] = pwr_info_diff[1]
    result_dict["power_vcd_meas_diff"] = pwr_info_diff[2]
    result_dict["power_bias_meas_diff"] = pwr_info_diff[4]

    fn = chkout_top.FEMB_PLOT(ana[0], ana[1], ana[2], ana[3], ana[4], ana[5], save_dir)
    result_dict["response.png"] = fn
    chkout_top.generate_report(result_dict)

    print("Turn FEMB off")
    tcp.femb_pwr_set(femb=femb, pwr_on=0)

    print("Test is done...")
    print("Report is saved at {}".format(result_dict["save_dir"]))

print("Turn Power Supply on")
ps.ps_init()
ps.off([1, 2, 3])
#
