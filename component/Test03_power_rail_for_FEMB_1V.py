
import sys
import os
# Add the parent directory to sys.path so 'function' can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# from function.rigol_dp832_ps import RIGOL_PS_CTL
import function.Rigol_DP800 as rigol
from function.csv_manager import WIB_QC_CSV_Manager

from function.ping_host import ping_host
from datetime import datetime
from function.cls_udp import CLS_UDP
from function.tcp_cfg import TCP_CFG
import function.tcp as tcp_con
from function.raw_convertor import RAW_CONV
import time
import file.report_dict as rp_dict

print("\n" + "="*60)
print("\033[35m" + "A_RT03_01 : FEMB Power Rail Test (1V)" + "\033[0m")
print("="*60)
print("Testing 4 FEMB slots with 5 power rails each")
print("Power rails: FE, CD, ADC, IDLE, BIAS")
print("="*60 + "\n")

t1 = time.time()
psu = rigol.RigolDP800()

# Safe power off first
psu.safe_power_off()
time.sleep(2)

print("Powering on WIB...")
psu.set_channel(1, 12.0, 3.0, on=True)
psu.set_channel(2, 12.0, 3.0, on=True)
time.sleep(10)

# Measure WIB power supply
v1_wib, c1_wib = psu.measure(1)
v2_wib, c2_wib = psu.measure(2)
print(f"WIB Power - Ch1: {v1_wib:.3f}V {c1_wib:.3f}A, Ch2: {v2_wib:.3f}V {c2_wib:.3f}A")

# Record WIB power measurements
rp_dict.log03_femb_slot0['wib_v1'] = round(v1_wib, 3)
rp_dict.log03_femb_slot0['wib_c1'] = round(c1_wib, 3)
rp_dict.log03_femb_slot0['wib_v2'] = round(v2_wib, 3)
rp_dict.log03_femb_slot0['wib_c2'] = round(c2_wib, 3)

# Update CSV with WIB power measurements
if rp_dict.csv_manager:
    v1_status = "PASS" if 11.0 <= v1_wib <= 13.0 else "FAIL"
    c1_status = "PASS" if 0.5 <= c1_wib <= 3.0 else "FAIL"
    v2_status = "PASS" if 11.0 <= v2_wib <= 13.0 else "FAIL"
    c2_status = "PASS" if 0.5 <= c2_wib <= 3.0 else "FAIL"

    rp_dict.csv_manager.batch_update([
        {"item_id": "T03_1V_00", "value": round(v1_wib, 3), "status": v1_status},
        {"item_id": "T03_1V_01", "value": round(c1_wib, 3), "status": c1_status},
        {"item_id": "T03_1V_02", "value": round(v2_wib, 3), "status": v2_status},
        {"item_id": "T03_1V_03", "value": round(c2_wib, 3), "status": c2_status}
    ])

time.sleep(1)

print("Waiting for WIB boot...")
time.sleep(30) # wait for boot
print(f"WIB booted. Ch1 current: {c1_wib:.3f}A, Ch2 current: {c2_wib:.3f}A")
# Internet Connection
# TCP/IP 192.168.121.1
ping_host(ip_address="192.168.121.1", count=4)
ping_host(ip_address="192.168.121.2", count=4)

time.sleep(1)
# in the test, we use putty to run the script in WIB
# in the real program, we will send message to enable the script
import component.temp as initial
time.sleep(1)
# open putty
tcp = TCP_CFG()
udp = CLS_UDP()
conv = RAW_CONV()
now = datetime.now()

# Check power info at WIB side
# 1 get firmware version
a=tcp.tcp_cmd_io(0, 0, addr = 0x0, data = 0x0)
print(a)
set_v = 1

# 2 set FEMB Voltage
rp_dict.log03_femb_slot0['v_fe'] = '{}'.format(set_v)
rp_dict.log03_femb_slot0['v_cd'] = '{}'.format(set_v)
rp_dict.log03_femb_slot0['v_adc'] = '{}'.format(set_v)
rp_dict.log03_femb_slot0['v_idle'] = '{}'.format(set_v)
rp_dict.log03_femb_slot0['v_bias'] = '5'
rp_dict.log03_femb_slot1['v_fe'] = '{}'.format(set_v)
rp_dict.log03_femb_slot1['v_cd'] = '{}'.format(set_v)
rp_dict.log03_femb_slot1['v_adc'] = '{}'.format(set_v)
rp_dict.log03_femb_slot1['v_idle'] = '{}'.format(set_v)
rp_dict.log03_femb_slot1['v_bias'] = '5'
rp_dict.log03_femb_slot2['v_fe'] = '{}'.format(set_v)
rp_dict.log03_femb_slot2['v_cd'] = '{}'.format(set_v)
rp_dict.log03_femb_slot2['v_adc'] = '{}'.format(set_v)
rp_dict.log03_femb_slot2['v_idle'] = '{}'.format(set_v)
rp_dict.log03_femb_slot2['v_bias'] = '5'
rp_dict.log03_femb_slot3['v_fe'] = '{}'.format(set_v)
rp_dict.log03_femb_slot3['v_cd'] = '{}'.format(set_v)
rp_dict.log03_femb_slot3['v_adc'] = '{}'.format(set_v)
rp_dict.log03_femb_slot3['v_idle'] = '{}'.format(set_v)
rp_dict.log03_femb_slot3['v_bias'] = '5'

for i in range(4):
    femb = i
    tcp.femb_pwr_set(femb=femb, pwr_on=1, v_fe=set_v, v_cd=set_v, v_adc=set_v, v_N=set_v)

    time.sleep(1)
    print('debug')
    pwr_info = tcp.femb_pwr_rd(femb=femb)
    # pwr_info = tcp.wib_pwr_rd()
    print('Power Consumption on SLOT: {}'.format(femb))
    print(pwr_info)
    print(pwr_info[0])
    print(pwr_info[1])
    print(pwr_info[2])
    print(pwr_info[3])



    if i == 0:
        rp_dict.log03_femb_slot0['V_fe_meas'] = pwr_info[0][0]
        rp_dict.log03_femb_slot0['V_cd_meas'] = pwr_info[2][0]
        rp_dict.log03_femb_slot0['V_adc_meas'] = pwr_info[1][0]
        rp_dict.log03_femb_slot0['V_idle_meas'] = pwr_info[3][0]
        rp_dict.log03_femb_slot0['V_bias_meas'] = pwr_info[4][0]
        rp_dict.log03_femb_slot0['I_fe_meas'] = pwr_info[0][1]
        rp_dict.log03_femb_slot0['I_cd_meas'] = pwr_info[2][1]
        rp_dict.log03_femb_slot0['I_adc_meas'] = pwr_info[1][1]
        rp_dict.log03_femb_slot0['I_idle_meas'] = pwr_info[3][1]
        rp_dict.log03_femb_slot0['I_bias_meas'] = pwr_info[4][1]
    elif i == 1:
        rp_dict.log03_femb_slot1['V_fe_meas'] = pwr_info[0][0]
        rp_dict.log03_femb_slot1['V_cd_meas'] = pwr_info[2][0]
        rp_dict.log03_femb_slot1['V_adc_meas'] = pwr_info[1][0]
        rp_dict.log03_femb_slot1['V_idle_meas'] = pwr_info[3][0]
        rp_dict.log03_femb_slot1['V_bias_meas'] = pwr_info[4][0]
        rp_dict.log03_femb_slot1['I_fe_meas'] = pwr_info[0][1]
        rp_dict.log03_femb_slot1['I_cd_meas'] = pwr_info[2][1]
        rp_dict.log03_femb_slot1['I_adc_meas'] = pwr_info[1][1]
        rp_dict.log03_femb_slot1['I_idle_meas'] = pwr_info[3][1]
        rp_dict.log03_femb_slot1['I_bias_meas'] = pwr_info[4][1]
    elif i == 2:
        rp_dict.log03_femb_slot2['V_fe_meas'] = pwr_info[0][0]
        rp_dict.log03_femb_slot2['V_cd_meas'] = pwr_info[2][0]
        rp_dict.log03_femb_slot2['V_adc_meas'] = pwr_info[1][0]
        rp_dict.log03_femb_slot2['V_idle_meas'] = pwr_info[3][0]
        rp_dict.log03_femb_slot2['V_bias_meas'] = pwr_info[4][0]
        rp_dict.log03_femb_slot2['I_fe_meas'] = pwr_info[0][1]
        rp_dict.log03_femb_slot2['I_cd_meas'] = pwr_info[2][1]
        rp_dict.log03_femb_slot2['I_adc_meas'] = pwr_info[1][1]
        rp_dict.log03_femb_slot2['I_idle_meas'] = pwr_info[3][1]
        rp_dict.log03_femb_slot2['I_bias_meas'] = pwr_info[4][1]
    elif i == 3:
        rp_dict.log03_femb_slot3['V_fe_meas'] = pwr_info[0][0]
        rp_dict.log03_femb_slot3['V_cd_meas'] = pwr_info[2][0]
        rp_dict.log03_femb_slot3['V_adc_meas'] = pwr_info[1][0]
        rp_dict.log03_femb_slot3['V_idle_meas'] = pwr_info[3][0]
        rp_dict.log03_femb_slot3['V_bias_meas'] = pwr_info[4][0]
        rp_dict.log03_femb_slot3['I_fe_meas'] = pwr_info[0][1]
        rp_dict.log03_femb_slot3['I_cd_meas'] = pwr_info[2][1]
        rp_dict.log03_femb_slot3['I_adc_meas'] = pwr_info[1][1]
        rp_dict.log03_femb_slot3['I_idle_meas'] = pwr_info[3][1]
        rp_dict.log03_femb_slot3['I_bias_meas'] = pwr_info[4][1]
    else:
        print('No FEMB Power Rail Measured! Please Check Connection!')
    tcp.femb_pwr_reset(femb=i)

print(rp_dict.log03_femb_slot0)
print(rp_dict.log03_femb_slot1)
print(rp_dict.log03_femb_slot2)
print(rp_dict.log03_femb_slot3)

# Update CSV with FEMB power rail measurements
if rp_dict.csv_manager:
    VOLTAGE_TOLERANCE = 0.15
    updates = []

    # Process all 4 slots
    slot_dicts = [
        (0, rp_dict.log03_femb_slot0),
        (1, rp_dict.log03_femb_slot1),
        (2, rp_dict.log03_femb_slot2),
        (3, rp_dict.log03_femb_slot3)
    ]

    for slot, slot_dict in slot_dicts:
        # Process all 5 rails (FE, CD, ADC, IDLE, BIAS)
        rails = ['fe', 'cd', 'adc', 'idle', 'bias']
        rail_names = ['FE', 'CD', 'ADC', 'IDLE', 'BIAS']

        for rail, rail_name in zip(rails, rail_names):
            v_set = float(slot_dict.get(f'v_{rail}', set_v))
            v_meas = float(slot_dict.get(f'V_{rail}_meas', 0))
            i_meas = float(slot_dict.get(f'I_{rail}_meas', 0))

            # Check voltage within tolerance
            v_status = "PASS" if abs(v_meas - v_set) <= VOLTAGE_TOLERANCE else "FAIL"

            updates.append({
                "item_id": f"T03_1V_{slot}{rail_name}_V",
                "value": round(v_meas, 3),
                "status": v_status
            })
            updates.append({
                "item_id": f"T03_1V_{slot}{rail_name}_I",
                "value": round(i_meas, 3),
                "status": "PASS"
            })

    rp_dict.csv_manager.batch_update(updates)
# tcp.tcp_poke(addr=0x01, data=0x07)
pwr_info = tcp.wib_pwr_rd()
# pwr_info = tcp.wib_pwr_rd()
print('Power Consumption on SLOT: {}'.format(femb))
print(pwr_info)
print(pwr_info[0])
print(pwr_info[1])
print(pwr_info[2])
print(pwr_info[3])



for i in range(4):
    tcp.femb_pwr_reset(femb=i)

# Calculate test duration
t2 = time.time()
test_duration = round(t2 - t1, 2)
print(f"\n\033[32mTest completed in {test_duration} seconds\033[0m\n")

# Record test duration
rp_dict.log03_femb_slot0['test_duration'] = test_duration

# Update CSV with test duration
if rp_dict.csv_manager:
    rp_dict.csv_manager.update_item("T03_1V_99", test_duration, status="COMPLETE")

import os

# === Setup relative path to ../report/WIB_03_1V_power_report.html ===
base_dir = os.path.dirname(os.path.abspath(__file__))
target_file_path = os.path.join(base_dir, "..", "report", "WIB_03_1V_power_report.html")

# Ensure target directory exists
os.makedirs(os.path.dirname(target_file_path), exist_ok=True)

# Define power rail thresholds for validation
VOLTAGE_TOLERANCE = 0.15  # ±0.15V from set value
RAIL_THRESHOLDS = {
    "FE": {"I_min": 0.0, "I_max": 1.5},
    "CD": {"I_min": 0.0, "I_max": 0.5},
    "ADC": {"I_min": 0.0, "I_max": 2.5},
    "IDLE": {"I_min": 0.0, "I_max": 0.3},
    "BIAS": {"I_min": 0.0, "I_max": 0.2}
}

# Validate all measurements
all_passed = True
slot_data = [
    ("SLOT0", rp_dict.log03_femb_slot0),
    ("SLOT1", rp_dict.log03_femb_slot1),
    ("SLOT2", rp_dict.log03_femb_slot2),
    ("SLOT3", rp_dict.log03_femb_slot3)
]

for slot_name, slot_dict in slot_data:
    for rail in ['fe', 'cd', 'adc', 'idle', 'bias']:
        v_set = float(slot_dict.get(f'v_{rail}', 0))
        v_meas = float(slot_dict.get(f'V_{rail}_meas', 0))
        i_meas = float(slot_dict.get(f'I_{rail}_meas', 0))

        # Voltage check
        if abs(v_meas - v_set) > VOLTAGE_TOLERANCE:
            all_passed = False

        # Current check
        rail_upper = rail.upper() if rail != 'idle' else 'IDLE'
        if rail_upper in RAIL_THRESHOLDS:
            thresholds = RAIL_THRESHOLDS[rail_upper]
            if not (thresholds["I_min"] <= i_meas <= thresholds["I_max"]):
                all_passed = False

overall_status = "PASS" if all_passed else "FAIL"
overall_status_class = "pass" if all_passed else "fail"

# Generate professional HTML report (Clean & Simple Style)
html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>WIB FEMB Power Rail Test Report</title>
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
            max-width: 1000px;
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

        /* Section */
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
            text-align: center;
            padding: 12px;
            border: 1px solid #000000;
        }}
        td {{
            padding: 10px;
            border: 1px solid #d1d5db;
            text-align: center;
        }}
        tr:nth-child(even) {{
            background-color: #f9fafb;
        }}
        .status-cell {{
            font-weight: bold;
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
        .rail-label {{
            text-align: left;
            font-weight: bold;
            padding-left: 15px;
        }}

        /* Test Description */
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
            <div class="subtitle">FEMB Power Rail Test Report (Test03 - 1V)</div>
            <div class="status-badge {overall_status_class}">Overall Status: {overall_status}</div>
        </div>

        <!-- Test Information -->
        <div class="info-section">
            <div class="info-row">
                <div class="info-label">Test Date:</div>
                <div class="info-value">{datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")}</div>
            </div>
            <div class="info-row">
                <div class="info-label">Total Test Time:</div>
                <div class="info-value">{test_duration} seconds</div>
            </div>
            <div class="info-row">
                <div class="info-label">Test Configuration:</div>
                <div class="info-value">4 FEMB Slots, 5 Power Rails each (1V test voltage)</div>
            </div>
        </div>

        <!-- WIB Power Supply -->
        <div class="section">
            <div class="section-title">WIB Power Supply Measurements</div>
            <table>
                <thead>
                    <tr>
                        <th style="width: 25%;">Channel</th>
                        <th style="width: 25%;">Voltage (V)</th>
                        <th style="width: 25%;">Current (A)</th>
                        <th style="width: 25%;">Power (W)</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><strong>Channel 1</strong></td>
                        <td>{rp_dict.log03_femb_slot0.get('wib_v1', 0):.3f} V</td>
                        <td>{rp_dict.log03_femb_slot0.get('wib_c1', 0):.3f} A</td>
                        <td>{(rp_dict.log03_femb_slot0.get('wib_v1', 0) * rp_dict.log03_femb_slot0.get('wib_c1', 0)):.3f} W</td>
                    </tr>
                    <tr>
                        <td><strong>Channel 2</strong></td>
                        <td>{rp_dict.log03_femb_slot0.get('wib_v2', 0):.3f} V</td>
                        <td>{rp_dict.log03_femb_slot0.get('wib_c2', 0):.3f} A</td>
                        <td>{(rp_dict.log03_femb_slot0.get('wib_v2', 0) * rp_dict.log03_femb_slot0.get('wib_c2', 0)):.3f} W</td>
                    </tr>
                    <tr style="background-color: #f3f4f6; font-weight: bold;">
                        <td><strong>TOTAL</strong></td>
                        <td></td>
                        <td></td>
                        <td>{((rp_dict.log03_femb_slot0.get('wib_v1', 0) * rp_dict.log03_femb_slot0.get('wib_c1', 0)) + (rp_dict.log03_femb_slot0.get('wib_v2', 0) * rp_dict.log03_femb_slot0.get('wib_c2', 0))):.3f} W</td>
                    </tr>
                </tbody>
            </table>
        </div>
"""

# Generate table for each FEMB slot
for slot_idx, (slot_name, slot_dict) in enumerate(slot_data):
    html_content += f"""
        <div class="section">
            <div class="section-title">FEMB SLOT {slot_idx} Power Rail Measurements</div>
            <div class="test-description">
                <strong>Test Configuration:</strong> Set voltage = 1V for FE/CD/ADC/IDLE, 5V for BIAS
            </div>
            <table>
                <thead>
                    <tr>
                        <th style="width: 20%;">Rail</th>
                        <th style="width: 16%;">Set V (V)</th>
                        <th style="width: 16%;">Meas V (V)</th>
                        <th style="width: 16%;">Meas I (A)</th>
                        <th style="width: 16%;">Power (W)</th>
                        <th style="width: 16%;">Status</th>
                    </tr>
                </thead>
                <tbody>"""

    rails_info = [
        ('FE', 'fe', 'LArASIC'),
        ('ADC', 'adc', 'ColdADC'),
        ('CD', 'cd', 'COLDATA'),
        ('IDLE', 'idle', 'IDLE'),
        ('BIAS', 'bias', 'BIAS')
    ]

    for rail_name, rail_key, rail_desc in rails_info:
        v_set = float(slot_dict.get(f'v_{rail_key}', 0))
        v_meas = float(slot_dict.get(f'V_{rail_key}_meas', 0))
        i_meas = float(slot_dict.get(f'I_{rail_key}_meas', 0))
        p_meas = v_meas * i_meas

        # Voltage validation
        v_error = abs(v_meas - v_set) > VOLTAGE_TOLERANCE

        # Current validation
        i_error = False
        if rail_name in RAIL_THRESHOLDS:
            thresholds = RAIL_THRESHOLDS[rail_name]
            i_error = not (thresholds["I_min"] <= i_meas <= thresholds["I_max"])

        status = "FAIL" if (v_error or i_error) else "PASS"
        status_class = "status-fail" if (v_error or i_error) else "status-pass"
        v_error_class = ' class="error-cell"' if v_error else ''
        i_error_class = ' class="error-cell"' if i_error else ''

        html_content += f"""
                    <tr>
                        <td class="rail-label"><strong>{rail_name}</strong> ({rail_desc})</td>
                        <td>{v_set:.2f}</td>
                        <td{v_error_class}>{v_meas:.3f}</td>
                        <td{i_error_class}>{i_meas:.3f}</td>
                        <td>{p_meas:.3f}</td>
                        <td class="status-cell {status_class}">{status}</td>
                    </tr>"""

    html_content += """
                </tbody>
            </table>
        </div>"""

html_content += f"""
        <!-- Footer -->
        <div class="footer">
            <p>DUNE WIB Quality Control System - Test03 FEMB Power Rail Test</p>
            <p>Report generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")}</p>
        </div>
    </div>
</body>
</html>
"""

# Write HTML file
with open(target_file_path, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"\n\033[32mHTML report saved to: {target_file_path}\033[0m\n")

# Safe power off and cleanup
time.sleep(0.5)
print("Turning off power supply...")
psu.safe_power_off()
psu.close()
print("\033[32mTest03 completed successfully!\033[0m")