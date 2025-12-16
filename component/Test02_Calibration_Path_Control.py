## =========================================
import time
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from function.cls_udp import CLS_UDP
from function.tcp_cfg import TCP_CFG
from function.raw_convertor import RAW_CONV
import datetime
import file.report_dict as rp_dict
t1 = time.time()
import component.temp as initial
import function.Rigol_DP800 as rigol

initial
time.sleep(1)

# Begin
tcp = TCP_CFG()
udp = CLS_UDP()
conv = RAW_CONV()
now = datetime.datetime.now()


def Set_DAC(set_v = 1, CAL_PULSE_GEN = 1, DAC_SRC_SEL_BRD0 = 1, DAC_SRC_SEL_BRD1 = 1, DAC_SRC_SEL_BRD2 = 1, DAC_SRC_SEL_BRD3 = 1):
    DAC_step = 0.00003125
    dac_bit = format(int(set_v / DAC_step), '016b')
    tcp.tcp_poke(addr=0x10, data=0x04)
    time.sleep(0.05)
    tcp.tcp_poke(addr=0x10, data=0x06)
    tcp.tcp_poke(addr=0x10, data=0x04)
    tcp.tcp_poke(addr=0x10, data=0x02)
    tcp.tcp_poke(addr=0x10, data=0x00)
    tcp.tcp_poke(addr=0x10, data=0x00)
    tcp.tcp_poke(addr=0x10, data=0x02)
    tcp.tcp_poke(addr=0x10, data=0x00)
    for i in dac_bit:
        if i == '0':
            tcp.tcp_poke(addr=0x10, data=0x00)
            tcp.tcp_poke(addr=0x10, data=0x02)
            tcp.tcp_poke(addr=0x10, data=0x00)
        else:
            tcp.tcp_poke(addr=0x10, data=0x01)
            tcp.tcp_poke(addr=0x10, data=0x03)
            tcp.tcp_poke(addr=0x10, data=0x01)
    tcp.tcp_poke(addr=0x10, data=0x02)
    tcp.tcp_poke(addr=0x10, data=0x00)
    tcp.tcp_poke(addr=0x10, data=0x02)
    tcp.tcp_poke(addr=0x10, data=0x00)
    tcp.tcp_poke(addr=0x10, data=0x02)
    tcp.tcp_poke(addr=0x10, data=0x00)
    switch_combine = ((CAL_PULSE_GEN << 4) | (DAC_SRC_SEL_BRD3 << 3) | (DAC_SRC_SEL_BRD2 << 2) | (DAC_SRC_SEL_BRD1 << 1) | (DAC_SRC_SEL_BRD0 << 0))
    switch = (switch_combine << 16 | 4)
    tcp.tcp_poke(addr=0x10, data=switch)

def Set_switch(CAL_PULSE_GEN = 1, DAC_SRC_SEL_BRD0 = 1, DAC_SRC_SEL_BRD1 = 1, DAC_SRC_SEL_BRD2 = 1, DAC_SRC_SEL_BRD3 = 1, Mon_PULSE_SEL = 1):
    switch_combine = ((CAL_PULSE_GEN << 4) | (DAC_SRC_SEL_BRD3 << 3) | (DAC_SRC_SEL_BRD2 << 2) | (DAC_SRC_SEL_BRD1 << 1) | (DAC_SRC_SEL_BRD0 << 0))
    switch = (switch_combine << 16 | 4)

# def config_switch()
    tcp.tcp_poke(addr=0x12, data=Mon_PULSE_SEL)
    tcp.tcp_poke(addr=0x10, data=switch)

def WIB_ADC_read():
    tcp.tcp_poke(addr=0x11, data=0x01)
    time.sleep(0.05)
    tcp.tcp_poke(addr=0x11, data=0x00)
    channel_Value_0_1 = tcp.tcp_peek(addr = 0x13)
    adc0_v = ((channel_Value_0_1 >>16)&0xffff)*2.5/16384.0
    adc1_v = (channel_Value_0_1 & 0xffff)*2.5/16384.0
    channel_Value_2_3 = tcp.tcp_peek(addr = 0x14)
    adc2_v = ((channel_Value_2_3 >>16)&0xffff)*2.5/16384.0
    adc3_v = (channel_Value_2_3 & 0xffff)*2.5/16384.0
    return adc0_v, adc1_v, adc2_v, adc3_v


# DAC Set Test
Set_DAC(set_v = 1)
time.sleep(1)
slot0, slot1, slot2, slot3 = WIB_ADC_read()
print(slot0)
print(slot1)
print(slot2)
print(slot3)
time.sleep(1)

# test 1 V, expected output [1 1 1 1]
Set_switch(CAL_PULSE_GEN = 1, DAC_SRC_SEL_BRD0 = 1, DAC_SRC_SEL_BRD1 = 1, DAC_SRC_SEL_BRD2 = 1, DAC_SRC_SEL_BRD3 = 1, Mon_PULSE_SEL = 1)
time.sleep(1)
Set_DAC(set_v = 1)
Set_DAC(set_v = 1)
Set_DAC(set_v = 1)
Set_DAC(set_v = 1)
WIB_ADC_read()
WIB_ADC_read()
WIB_ADC_read()
WIB_ADC_read()
WIB_ADC_read()
time.sleep(2)
slot0, slot1, slot2, slot3 = WIB_ADC_read()
print('readout 01')
rp_dict.log05_Cal['1v_slot_0_P8'] = round(slot0, 4)
rp_dict.log05_Cal['1v_slot_1_P7'] = round(slot1, 4)
rp_dict.log05_Cal['1v_slot_2_P6'] = round(slot2, 4)
rp_dict.log05_Cal['1v_slot_3_P4'] = round(slot3, 4)
print(slot0)
print(slot1)
print(slot2)
print(slot3)
time.sleep(1)

# test 1.6 V, expected output [1.65 1.65 1.65 1.65]
print('readout t1')
Set_switch(CAL_PULSE_GEN = 0, DAC_SRC_SEL_BRD0 = 1, DAC_SRC_SEL_BRD1 = 1, DAC_SRC_SEL_BRD2 = 1, DAC_SRC_SEL_BRD3 = 1, Mon_PULSE_SEL = 1)
time.sleep(2)
WIB_ADC_read()
Set_DAC(set_v = 1, CAL_PULSE_GEN = 0)
Set_DAC(set_v = 1, CAL_PULSE_GEN = 0)
Set_DAC(set_v = 1, CAL_PULSE_GEN = 0)
Set_DAC(set_v = 1, CAL_PULSE_GEN = 0)
WIB_ADC_read()
WIB_ADC_read()
WIB_ADC_read()
WIB_ADC_read()
time.sleep(2)
slot0, slot1, slot2, slot3 = WIB_ADC_read()
rp_dict.log05_Cal['1_6v_slot_0_P8'] = round(slot0, 4)
rp_dict.log05_Cal['1_6v_slot_1_P7'] = round(slot1, 4)
rp_dict.log05_Cal['1_6v_slot_2_P6'] = round(slot2, 4)
rp_dict.log05_Cal['1_6v_slot_3_P4'] = round(slot3, 4)
print(slot0)
print(slot1)
print(slot2)
print(slot3)

# expected output [0.5 0.5 0.5 0.5]
Set_DAC(set_v = 1, CAL_PULSE_GEN = 1, DAC_SRC_SEL_BRD0 = 1, DAC_SRC_SEL_BRD1 = 0, DAC_SRC_SEL_BRD2 = 1, DAC_SRC_SEL_BRD3 = 0)
Set_DAC(set_v = 1, CAL_PULSE_GEN = 1, DAC_SRC_SEL_BRD0 = 1, DAC_SRC_SEL_BRD1 = 0, DAC_SRC_SEL_BRD2 = 1, DAC_SRC_SEL_BRD3 = 0)
Set_DAC(set_v = 1, CAL_PULSE_GEN = 1, DAC_SRC_SEL_BRD0 = 1, DAC_SRC_SEL_BRD1 = 0, DAC_SRC_SEL_BRD2 = 1, DAC_SRC_SEL_BRD3 = 0)
WIB_ADC_read()
WIB_ADC_read()
WIB_ADC_read()
WIB_ADC_read()
time.sleep(2)
slot0, slot1, slot2, slot3 = WIB_ADC_read()
print('readout t2')
print(slot0)
print(slot1)
print(slot2)
print(slot3)
rp_dict.log05_Cal['0123_slot_0_P8'] = round(slot0, 4)
rp_dict.log05_Cal['0123_slot_1_P7'] = round(slot1, 4)
rp_dict.log05_Cal['0123_slot_2_P6'] = round(slot2, 4)
rp_dict.log05_Cal['0123_slot_3_P4'] = round(slot3, 4)

# t3 expected output [0.5 0.5 0.5 0.5]
Set_DAC(set_v = 1, CAL_PULSE_GEN = 1, DAC_SRC_SEL_BRD0 = 0, DAC_SRC_SEL_BRD1 = 1, DAC_SRC_SEL_BRD2 = 0, DAC_SRC_SEL_BRD3 = 1)
Set_DAC(set_v = 1, CAL_PULSE_GEN = 1, DAC_SRC_SEL_BRD0 = 0, DAC_SRC_SEL_BRD1 = 1, DAC_SRC_SEL_BRD2 = 0, DAC_SRC_SEL_BRD3 = 1)
Set_DAC(set_v = 1, CAL_PULSE_GEN = 1, DAC_SRC_SEL_BRD0 = 0, DAC_SRC_SEL_BRD1 = 1, DAC_SRC_SEL_BRD2 = 0, DAC_SRC_SEL_BRD3 = 1)
WIB_ADC_read()
WIB_ADC_read()
WIB_ADC_read()
WIB_ADC_read()
time.sleep(2)
slot0, slot1, slot2, slot3 = WIB_ADC_read()
print('readout t3')
print(slot0)
print(slot1)
print(slot2)
print(slot3)
rp_dict.log05_Cal['3210_slot_0_P8'] = round(slot0, 4)
rp_dict.log05_Cal['3210_slot_1_P7'] = round(slot1, 4)
rp_dict.log05_Cal['3210_slot_2_P6'] = round(slot2, 4)
rp_dict.log05_Cal['3210_slot_3_P4'] = round(slot3, 4)

# t4 expected output [0.8 0.8 0.8 0.8]
while True:
    print('Test P5, enter to next')
    con = input("please enter y to continue")
    if con == 'y':
        print("continue test")
        break

Set_DAC(set_v = 1, CAL_PULSE_GEN = 0, DAC_SRC_SEL_BRD0 = 0, DAC_SRC_SEL_BRD1 = 0, DAC_SRC_SEL_BRD2 = 0, DAC_SRC_SEL_BRD3 = 1)
Set_DAC(set_v = 1, CAL_PULSE_GEN = 0, DAC_SRC_SEL_BRD0 = 0, DAC_SRC_SEL_BRD1 = 0, DAC_SRC_SEL_BRD2 = 0, DAC_SRC_SEL_BRD3 = 1)
Set_DAC(set_v = 1, CAL_PULSE_GEN = 0, DAC_SRC_SEL_BRD0 = 0, DAC_SRC_SEL_BRD1 = 0, DAC_SRC_SEL_BRD2 = 0, DAC_SRC_SEL_BRD3 = 1)
WIB_ADC_read()
WIB_ADC_read()
WIB_ADC_read()
WIB_ADC_read()
time.sleep(2)
slot0, slot1, slot2, slot3 = WIB_ADC_read()
print('readout t4')
print(slot0)
print(slot1)
print(slot2)
print(slot3)
rp_dict.log05_Cal['P5_slot_0_P8'] = round(slot0, 4)
rp_dict.log05_Cal['P5_slot_1_P7'] = round(slot1, 4)
rp_dict.log05_Cal['P5_slot_2_P6'] = round(slot2, 4)
rp_dict.log05_Cal['P5_slot_3_P4'] = round(slot3, 4)
while True:
    print('Test Test_Point, enter to next')
    con = input("please enter y to continue")
    if con == 'y':
        print("continue test")
        break
Set_DAC(set_v = 1, CAL_PULSE_GEN = 1, DAC_SRC_SEL_BRD0 = 0, DAC_SRC_SEL_BRD1 = 0, DAC_SRC_SEL_BRD2 = 0, DAC_SRC_SEL_BRD3 = 0)
# t5 expected output [0 0 0 0]
time.sleep(1)
Set_switch(CAL_PULSE_GEN = 1, DAC_SRC_SEL_BRD0 = 0, DAC_SRC_SEL_BRD1 = 0, DAC_SRC_SEL_BRD2 = 0, DAC_SRC_SEL_BRD3 = 0, Mon_PULSE_SEL = 0)
WIB_ADC_read()
WIB_ADC_read()
WIB_ADC_read()
WIB_ADC_read()
WIB_ADC_read()
WIB_ADC_read()
time.sleep(3)
slot0, slot1, slot2, slot3 = WIB_ADC_read()
print('readout t6')
print(slot0)
print(slot1)
print(slot2)
print(slot3)
rp_dict.log05_Cal['TP_slot_0_P8'] = round(slot0, 4)
rp_dict.log05_Cal['TP_slot_1_P7'] = round(slot1, 4)
rp_dict.log05_Cal['TP_slot_2_P6'] = round(slot2, 4)
rp_dict.log05_Cal['TP_slot_3_P4'] = round(slot3, 4)
tcp.tcp_cmd_io(cmd=0x02, aux=0, addr=0x08, data=0xFFFFFFFF)


# fm_ps.ps_init()
# fm_ps.off([1, 2, 3])
t2 = time.time()
print('time consumption = {}'.format(t2-t1))

print(rp_dict.log05_Cal)

rp_dict.log05_Cal['Communication_Time_Consumption'] = round(t2-t1, 3)
# time < 40 seconds

psu = rigol.RigolDP800()
psu.safe_power_off()
import os

# === Setup relative path to ../file/Calibration_report_02.html ===
base_dir = os.path.dirname(os.path.abspath(__file__))
target_file_path = os.path.join(base_dir, "..", "report", "WIB_02_Calibration_report_02.html")
print(target_file_path)

# Ensure target directory exists
os.makedirs(os.path.dirname(target_file_path), exist_ok=True)

# Collect values
cal = rp_dict.log05_Cal

# HTML content with CSS styling
html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>WIB_02 Calibration Test Report</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 40px;
            background-color: #f9f9f9;
            color: #333;
        }}
        h2 {{
            text-align: center;
            color: #444;
        }}
        .section {{
            margin: 20px 0;
            padding: 15px;
            border-radius: 10px;
            background: #fff;
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        }}
        .section h3 {{
            color: #2c3e50;
            border-bottom: 2px solid #ddd;
            padding-bottom: 5px;
        }}
        .slots {{
            margin: 10px 0;
            padding-left: 15px;
        }}
        .slot {{
            margin: 5px 0;
        }}
        .label {{
            font-weight: bold;
            color: #555;
        }}
        .value {{
            margin-left: 10px;
        }}
        .footer {{
            margin-top: 30px;
            font-style: italic;
            color: #666;
            text-align: right;
        }}
    </style>
</head>
<body>
    <h2>Calibration Test Report</h2>

    <div class="section">
        <h3>1. Test Four SLOT with DAC voltage</h3>
        <div class="slots">
            <div class="slot"><span class="label">SLOT0:</span><span class="value">{cal['1v_slot_0_P8']} [0.9–1.1]</span></div>
            <div class="slot"><span class="label">SLOT1:</span><span class="value">{cal['1v_slot_1_P7']} [0.9–1.1]</span></div>
            <div class="slot"><span class="label">SLOT2:</span><span class="value">{cal['1v_slot_2_P6']} [0.9–1.1]</span></div>
            <div class="slot"><span class="label">SLOT3:</span><span class="value">{cal['1v_slot_3_P4']} [0.9–1.1]</span></div>
        </div>
    </div>

    <div class="section">
        <h3>2. Test Four SLOT with Ref voltage</h3>
        <div class="slots">
            <div class="slot"><span class="label">SLOT0:</span><span class="value">{cal['1_6v_slot_0_P8']} [1.6–1.7]</span></div>
            <div class="slot"><span class="label">SLOT1:</span><span class="value">{cal['1_6v_slot_1_P7']} [1.6–1.7]</span></div>
            <div class="slot"><span class="label">SLOT2:</span><span class="value">{cal['1_6v_slot_2_P6']} [1.6–1.7]</span></div>
            <div class="slot"><span class="label">SLOT3:</span><span class="value">{cal['1_6v_slot_2_P6']} [1.6–1.7]</span></div>
        </div>
    </div>

    <div class="section">
        <h3>3. Test SLOT1_output SLOT2_input SLOT3_output SLOT4_input with DAC voltage</h3>
        <div class="slots">
            <div class="slot"><span class="label">SLOT0:</span><span class="value">{cal['0123_slot_0_P8']} [0.5–0.55]</span></div>
            <div class="slot"><span class="label">SLOT1:</span><span class="value">{cal['0123_slot_1_P7']} [0.5–0.55]</span></div>
            <div class="slot"><span class="label">SLOT2:</span><span class="value">{cal['0123_slot_2_P6']} [0.5–0.55]</span></div>
            <div class="slot"><span class="label">SLOT3:</span><span class="value">{cal['0123_slot_3_P4']} [0.5–0.55]</span></div>
        </div>
    </div>

    <div class="section">
        <h3>4. Test SLOT1_input SLOT2_output SLOT3_input SLOT4_output with DAC voltage</h3>
        <div class="slots">
            <div class="slot"><span class="label">SLOT0:</span><span class="value">{cal['3210_slot_0_P8']} [0.5–0.55]</span></div>
            <div class="slot"><span class="label">SLOT1:</span><span class="value">{cal['3210_slot_1_P7']} [0.5–0.55]</span></div>
            <div class="slot"><span class="label">SLOT2:</span><span class="value">{cal['3210_slot_2_P6']} [0.5–0.55]</span></div>
            <div class="slot"><span class="label">SLOT3:</span><span class="value">{cal['3210_slot_3_P4']} [0.5–0.55]</span></div>
        </div>
    </div>

    <div class="section">
        <h3>5. Test LEMO P5 Calibration pulse injection</h3>
        <div class="slots">
            <div class="slot"><span class="label">SLOT0:</span><span class="value">{cal['P5_slot_0_P8']} [0.7–0.85]</span></div>
            <div class="slot"><span class="label">SLOT1:</span><span class="value">{cal['P5_slot_1_P7']} [0.7–0.85]</span></div>
            <div class="slot"><span class="label">SLOT2:</span><span class="value">{cal['P5_slot_2_P6']} [0.7–0.85]</span></div>
            <div class="slot"><span class="label">SLOT3:</span><span class="value">{cal['P5_slot_3_P4']} [0.7–0.85]</span></div>
        </div>
    </div>

    <div class="section">
        <h3>6. Test Points</h3>
        <div class="slots">
            <div class="slot"><span class="label">SLOT0:</span><span class="value">{cal['TP_slot_0_P8']} [0–0.5]</span></div>
            <div class="slot"><span class="label">SLOT1:</span><span class="value">{cal['TP_slot_1_P7']} [0–0.5]</span></div>
            <div class="slot"><span class="label">SLOT2:</span><span class="value">{cal['TP_slot_2_P6']} [0–0.5]</span></div>
            <div class="slot"><span class="label">SLOT3:</span><span class="value">{cal['TP_slot_3_P4']} [0–0.5]</span></div>
        </div>
    </div>

    <div class="footer">
        Time Consumption = {cal['Communication_Time_Consumption']}
    </div>
</body>
</html>
"""

# Always create new file (overwrite if exists)
with open(target_file_path, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"HTML report saved (new file) to {target_file_path}")

