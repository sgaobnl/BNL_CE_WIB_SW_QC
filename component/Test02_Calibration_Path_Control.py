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
import function.Rigol_DP800 as rigol

psu = rigol.RigolDP800()
psu.safe_power_off()
print("Turn FM on")
psu.set_channel(1, 12.0, 3.0, on=True)
psu.set_channel(2, 12.0, 3.0, on=True)
time.sleep(10)
v1, c1 = psu.measure(1)
v2, c2 = psu.measure(1)

time.sleep(20)

time.sleep(1)

# Begin
tcp = TCP_CFG()
udp = CLS_UDP()
conv = RAW_CONV()
now = datetime.datetime.now()
import component.temp as initial
initial

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

# Define test thresholds for validation
test_configs = [
    {
        "name": "DAC Voltage Test",
        "description": "Test Four SLOT with DAC voltage (1V expected)",
        "slots": ['1v_slot_0_P8', '1v_slot_1_P7', '1v_slot_2_P6', '1v_slot_3_P4'],
        "min": 0.9, "max": 1.1
    },
    {
        "name": "Reference Voltage Test",
        "description": "Test Four SLOT with Ref voltage (1.65V expected)",
        "slots": ['1_6v_slot_0_P8', '1_6v_slot_1_P7', '1_6v_slot_2_P6', '1_6v_slot_3_P4'],
        "min": 1.6, "max": 1.7
    },
    {
        "name": "Path Control Test A",
        "description": "SLOT0/2 output, SLOT1/3 input with DAC voltage",
        "slots": ['0123_slot_0_P8', '0123_slot_1_P7', '0123_slot_2_P6', '0123_slot_3_P4'],
        "min": 0.5, "max": 0.55
    },
    {
        "name": "Path Control Test B",
        "description": "SLOT0/2 input, SLOT1/3 output with DAC voltage",
        "slots": ['3210_slot_0_P8', '3210_slot_1_P7', '3210_slot_2_P6', '3210_slot_3_P4'],
        "min": 0.5, "max": 0.55
    },
    {
        "name": "LEMO P5 Injection Test",
        "description": "Test LEMO P5 Calibration pulse injection",
        "slots": ['P5_slot_0_P8', 'P5_slot_1_P7', 'P5_slot_2_P6', 'P5_slot_3_P4'],
        "min": 0.7, "max": 0.85
    },
    {
        "name": "Test Points",
        "description": "Test Points measurement",
        "slots": ['TP_slot_0_P8', 'TP_slot_1_P7', 'TP_slot_2_P6', 'TP_slot_3_P4'],
        "min": 0.0, "max": 0.5
    }
]

# Validate all measurements
all_passed = True
for test in test_configs:
    for slot_key in test['slots']:
        value = cal.get(slot_key, 0)
        if not (test['min'] <= value <= test['max']):
            all_passed = False
            break

overall_status = "PASS" if all_passed else "FAIL"
overall_status_class = "pass" if all_passed else "fail"

# HTML content with professional styling (Clean & Simple)
html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>WIB Calibration Path Control Test Report</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Segoe UI', Arial, sans-serif;
            background: #ffffff;
            color: #000000;
            padding: 30px;
            line-height: 1.6;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: white;
        }}

        /* Header Section */
        .header {{
            border-bottom: 3px solid #000000;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .header h1 {{
            font-size: 24px;
            font-weight: bold;
            color: #000000;
            margin-bottom: 5px;
        }}
        .header .subtitle {{
            font-size: 14px;
            color: #666666;
        }}

        /* Status Badge */
        .status-badge {{
            display: inline-block;
            padding: 8px 16px;
            font-weight: bold;
            font-size: 16px;
            margin-top: 15px;
            border: 2px solid;
        }}
        .status-badge.pass {{
            color: #166534;
            background-color: #dcfce7;
            border-color: #166534;
        }}
        .status-badge.fail {{
            color: #991b1b;
            background-color: #fee2e2;
            border-color: #991b1b;
        }}

        /* Info Section */
        .info-section {{
            margin: 20px 0;
            padding: 15px;
            background: #f9fafb;
            border-left: 4px solid #000000;
        }}
        .info-row {{
            display: flex;
            margin: 8px 0;
        }}
        .info-label {{
            font-weight: bold;
            width: 150px;
            color: #000000;
        }}
        .info-value {{
            color: #374151;
        }}

        /* Test Section */
        .section {{
            margin: 30px 0;
        }}
        .section-title {{
            font-size: 18px;
            font-weight: bold;
            color: #000000;
            margin-bottom: 15px;
            padding-bottom: 8px;
            border-bottom: 2px solid #e5e7eb;
        }}

        /* Tables */
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
            border: 1px solid #000000;
        }}
        th {{
            background-color: #f3f4f6;
            color: #000000;
            font-weight: bold;
            text-align: left;
            padding: 12px;
            border: 1px solid #000000;
        }}
        td {{
            padding: 12px;
            border: 1px solid #d1d5db;
        }}
        tr:nth-child(even) {{
            background-color: #f9fafb;
        }}
        .status-cell {{
            font-weight: bold;
            text-align: center;
        }}
        .status-pass {{
            color: #166534;
        }}
        .status-fail {{
            color: #991b1b;
        }}
        .error-cell {{
            background: #fee2e2 !important;
            color: #991b1b !important;
            font-weight: bold;
        }}

        /* Test Description Box */
        .test-description {{
            margin: 10px 0;
            padding: 10px;
            background: #fafafa;
            border-left: 3px solid #9ca3af;
            font-size: 14px;
            color: #4b5563;
        }}

        /* Footer */
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #e5e7eb;
            text-align: center;
            color: #6b7280;
            font-size: 12px;
        }}

        /* Print Styles */
        @media print {{
            body {{
                padding: 0;
            }}
            .container {{
                max-width: 100%;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>DUNE WIB Quality Control</h1>
            <div class="subtitle">Calibration Path Control Test Report (Test02)</div>
            <div class="status-badge {overall_status_class}">Overall Status: {overall_status}</div>
        </div>

        <!-- Test Information -->
        <div class="info-section">
            <div class="info-row">
                <div class="info-label">Test Date:</div>
                <div class="info-value">{now.strftime("%Y-%m-%d %H:%M:%S UTC")}</div>
            </div>
            <div class="info-row">
                <div class="info-label">Total Test Time:</div>
                <div class="info-value">{cal['Communication_Time_Consumption']} seconds</div>
            </div>
            <div class="info-row">
                <div class="info-label">Test Items:</div>
                <div class="info-value">6 calibration path tests, 24 total measurements</div>
            </div>
        </div>

        <!-- Test Results Summary -->
        <div class="section">
            <div class="section-title">Test Results Summary</div>"""

# Generate table for each test configuration
for idx, test in enumerate(test_configs, 1):
    # Check if this test passed
    test_passed = all(test['min'] <= cal.get(slot_key, 0) <= test['max'] for slot_key in test['slots'])

    html_content += f"""
            <div class="test-description">
                <strong>Test {idx}: {test['name']}</strong> - {test['description']}
            </div>
            <table>
                <thead>
                    <tr>
                        <th style="width: 20%;">SLOT</th>
                        <th style="width: 20%;">Measured (V)</th>
                        <th style="width: 30%;">Expected Range (V)</th>
                        <th style="width: 15%;">Status</th>
                        <th style="width: 15%;">Port</th>
                    </tr>
                </thead>
                <tbody>"""

    slot_names = ['SLOT0', 'SLOT1', 'SLOT2', 'SLOT3']
    port_names = ['P8', 'P7', 'P6', 'P4']

    for slot_idx, slot_key in enumerate(test['slots']):
        value = cal.get(slot_key, 0)
        in_range = test['min'] <= value <= test['max']
        status_text = "PASS" if in_range else "FAIL"
        status_class = "status-pass" if in_range else "status-fail"
        error_class = "" if in_range else ' class="error-cell"'

        html_content += f"""
                    <tr>
                        <td><strong>{slot_names[slot_idx]}</strong></td>
                        <td{error_class}>{value:.4f} V</td>
                        <td>{test['min']:.2f} - {test['max']:.2f} V</td>
                        <td class="status-cell {status_class}">{status_text}</td>
                        <td>{port_names[slot_idx]}</td>
                    </tr>"""

    html_content += """
                </tbody>
            </table>"""

html_content += f"""
        </div>

        <!-- Footer -->
        <div class="footer">
            <p>DUNE WIB Quality Control System - Test02 Calibration Path Control</p>
            <p>Report generated: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")}</p>
        </div>
    </div>
</body>
</html>
"""

# Always create new file (overwrite if exists)
with open(target_file_path, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"HTML report saved (new file) to {target_file_path}")

