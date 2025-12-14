
import sys
import os

# Add the parent directory to sys.path so 'function' can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from function.rigol_dp832_ps import RIGOL_PS_CTL
from function.ping_host import ping_host
from datetime import datetime
from function.cls_udp import CLS_UDP
from function.tcp_cfg import TCP_CFG
import function.tcp as tcp_con
from function.raw_convertor import RAW_CONV
import time
import file.report_dict as rp_dict

print("\033[35m" + "A_RT03_03 : Power Rail" + "\033[0m")
t1 = time.time()
fm_ps = RIGOL_PS_CTL()
print("Turn FM on")
fm_ps.ps_init()
fm_ps.off([1, 2, 3])
time.sleep(2)

fm_ps.set_channel(channel=1, voltage=11.9, v_limit=12, c_limit=3)
fm_ps.set_channel(channel=2, voltage=11.95, v_limit=12, c_limit=3)
fm_ps.on([1, 2])
time.sleep(1)

time.sleep(30) # wait for boot
c1 = fm_ps.measure_params(channel = 1)
c2 = fm_ps.measure_params(channel = 2)
print(c1)
print(c2)
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
set_v = 3

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


import os

# === Setup relative path to ../report/power_report_03.html ===
base_dir = os.path.dirname(os.path.abspath(__file__))
target_file_path = os.path.join(base_dir, "..", "report", "WIB_03_3V_power_report.html")
print(target_file_path)

# Ensure target directory exists
os.makedirs(os.path.dirname(target_file_path), exist_ok=True)

# Define function to build slot tables
def build_table(slot_name, data):
    rails = ['FE', 'CD', 'ADC', 'IDLE', 'BIAS']
    set_voltage_row = "".join(f"<td>{data.get(f'v_{r.lower()}', '')}</td>" for r in rails)
    meas_voltage_row = "".join(f"<td>{data.get(f'V_{r.lower()}_meas', 0):.3f}</td>" for r in rails)
    meas_current_row = "".join(f"<td>{data.get(f'I_{r.lower()}_meas', 0):.3f}</td>" for r in rails)

    return f"""
    <div class="section">
        <h3>WIB_03_3V Power Rail in FEMB {slot_name}</h3>
        <table>
            <thead>
                <tr>
                    <th>Rail</th>
                    {''.join(f'<th>{r}</th>' for r in rails)}
                </tr>
            </thead>
            <tbody>
                <tr><td>Set Voltage (V)</td>{set_voltage_row}</tr>
                <tr><td>Measured Voltage (V)</td>{meas_voltage_row}</tr>
                <tr><td>Measured Current (A)</td>{meas_current_row}</tr>
            </tbody>
        </table>
    </div>
    """

# Collect slot reports
slot0 = build_table("SLOT 0", rp_dict.log03_femb_slot0)
slot1 = build_table("SLOT 1", rp_dict.log03_femb_slot1)
slot2 = build_table("SLOT 2", rp_dict.log03_femb_slot2)
slot3 = build_table("SLOT 3", rp_dict.log03_femb_slot3)

# HTML content with CSS styling
html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Power Report</title>
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
            margin: 30px 0;
            padding: 20px;
            border-radius: 10px;
            background: #fff;
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        }}
        h3 {{
            margin-bottom: 10px;
            color: #2c3e50;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: center;
        }}
        th {{
            background-color: #f0f0f0;
            font-weight: bold;
        }}
        tr:nth-child(even) td {{
            background-color: #fafafa;
        }}
    </style>
</head>
<body>
    <h2>Power Rail Report</h2>
    {slot0}
    {slot1}
    {slot2}
    {slot3}
</body>
</html>
"""

# Always create new file (overwrite if exists)
with open(target_file_path, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"HTML report saved (new file) to {target_file_path}")


#
time.sleep(3)
fm_ps.ps_init()
fm_ps.off([1, 2, 3])