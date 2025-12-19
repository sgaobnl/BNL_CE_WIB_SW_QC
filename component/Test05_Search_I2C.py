import socket
import time
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# from function.rigol_dp832_ps import RIGOL_PS_CTL
import function.Rigol_DP800 as rigol
from function.csv_manager import WIB_QC_CSV_Manager
from function.ping_host import ping_host
from datetime import datetime
from function.cls_udp import CLS_UDP
from function.tcp_cfg import TCP_CFG
from function.raw_convertor import RAW_CONV
import time
import file.report_dict as rp_dict
from datetime import datetime

SERVER_IP = "192.168.121.1"
PORT = 23  # Change if necessary (23 for Telnet, 22 for SSH)
USERNAME = "root"
PASSWORD = "root"
INITIAL_COMMAND = "i2cset -y 1 0x70 0xff 0xff"

t1 = time.time()

def receive_response(sock):
    """ Helper function to receive data from the socket """
    time.sleep(1)  # Give the server time to respond
    response = sock.recv(4096).decode(errors='ignore')
    print(response)  # Print the response for debugging
    return response

def connect_to_server():
    """ Establishes connection to the Zynq server and logs in """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((SERVER_IP, PORT))
        print("Connected to server.")

        # Read initial login prompt
        receive_response(s)

        # Send username and read response
        s.sendall((USERNAME + "\n").encode())
        receive_response(s)

        # Send password and read response
        s.sendall((PASSWORD + "\n").encode())
        receive_response(s)

        # Ensure login completion
        s.sendall(b"\n")
        receive_response(s)

        print("Login successful.")
        return s  # Keep the socket open for further commands

    except Exception as e:
        print("Connection error:", e)
        return None

def send_command(sock, command):
    """ Sends a command to the server and receives the response """
    try:
        sock.sendall((command + "\n").encode())
        response = receive_response(sock)
        return response
    except Exception as e:
        print("Error sending command:", e)
        return None




print("\033[35m" + "A_RT05_01 : Search I2C" + "\033[0m")

t1 = time.time()
psu = rigol.RigolDP800()

psu.set_channel(1, 12.0, 3.0, on=True)
psu.set_channel(2, 12.0, 3.0, on=True)
time.sleep(10)
v1, c1 = psu.measure(1)
v2, c2 = psu.measure(2)
print(f"WIB Power - Ch1: {v1:.3f}V {c1:.3f}A, Ch2: {v2:.3f}V {c2:.3f}A")

# Update CSV with WIB power measurements
if rp_dict.csv_manager:
    v1_status = "PASS" if 11.0 <= v1 <= 13.0 else "FAIL"
    c1_status = "PASS" if 0.5 <= c1 <= 3.0 else "FAIL"
    v2_status = "PASS" if 11.0 <= v2 <= 13.0 else "FAIL"
    c2_status = "PASS" if 0.5 <= c2 <= 3.0 else "FAIL"

    rp_dict.csv_manager.batch_update([
        {"item_id": "T05_00", "value": round(v1, 3), "status": v1_status},
        {"item_id": "T05_01", "value": round(c1, 3), "status": c1_status},
        {"item_id": "T05_02", "value": round(v2, 3), "status": v2_status},
        {"item_id": "T05_03", "value": round(c2, 3), "status": c2_status}
    ])

time.sleep(1)

time.sleep(27) # wait for boot
ping_host(ip_address="192.168.121.1", count=4)
ping_host(ip_address="192.168.121.2", count=4)
time.sleep(1)
import component.temp as initial
initial
tcp = TCP_CFG()
udp = CLS_UDP()
conv = RAW_CONV()
now = datetime.now()
# if __name__ == "__main__":
connection = connect_to_server()
if connection:
    # Send initial command
    tcp.tcp_poke(1, 0x00)
    send_command(connection, INITIAL_COMMAND)
    readback = send_command(connection, 'i2cdetect -r -y 0')
    print(readback)
    if '6b' in readback:
        print('I2C Device SI5342 has been found')
        rp_dict.log06_PTB['SI5342'] = 'Detected'
    else:
        print('Loss I2C Device [SI5342] ...')
        rp_dict.log06_PTB['SI5342'] = 'No ...'
    tcp.tcp_poke(1, 0x01)
    readback = send_command(connection, 'i2cdetect -r -y 0')
    print(readback)
    if '6b' in readback:
        print('I2C Device SI5344 has been found')
        rp_dict.log06_PTB['SI5344'] = 'Detected'
    else:
        print('Loss I2C Device [SI5344] ...')
        rp_dict.log06_PTB['SI5344'] = 'No ...'

    tcp.tcp_poke(1, 0x02)
    readback = send_command(connection, 'i2cdetect -r -y 0')
    print(readback)
    Device = 'TCA9546ADR';    Address = '70'
    if Address in readback:
        print('I2C Device {} has been found at 0x{}'.format(Device, Address))
        rp_dict.log06_PTB['{} 0x{}'.format(Device ,Address)] = 'Detected'
    else:
        print('Loss I2C Device [{}] at 0x{} ...'.format(Device, Address))
        rp_dict.log06_PTB['{} 0x{}'.format(Device ,Address)] = 'No'

    tcp.tcp_poke(1, 0x03)
    readback = send_command(connection, 'i2cdetect -r -y 0')
    print(readback)
    Device = 'LTC2991';    Address = '48'
    if Address in readback:
        print('I2C Device {} has been found at 0x{}'.format(Device, Address))
        rp_dict.log06_PTB['{} 0x{}'.format(Device, Address)] = 'Detected'
    else:
        print('Loss I2C Device [{}] at 0x{} ...'.format(Device, Address))
        rp_dict.log06_PTB['{} 0x{}'.format(Device, Address)] = 'No'
    Device = 'LTC2991';    Address = '49'
    if Address in readback:
        print('I2C Device {} has been found at 0x{}'.format(Device, Address))
        rp_dict.log06_PTB['{} 0x{}'.format(Device, Address)] = 'Detected'
    else:
        print('Loss I2C Device [{}] at 0x{} ...'.format(Device, Address))
        rp_dict.log06_PTB['{} 0x{}'.format(Device, Address)] = 'No'
    Device = 'LTC2991';    Address = '4a'
    if Address in readback:
        print('I2C Device {} has been found at 0x{}'.format(Device, Address))
        rp_dict.log06_PTB['{} 0x{}'.format(Device, Address)] = 'Detected'
    else:
        print('Loss I2C Device [{}] at 0x{} ...'.format(Device, Address))
        rp_dict.log06_PTB['{} 0x{}'.format(Device, Address)] = 'No'
    Device = 'LTC2991';    Address = '4b'
    if Address in readback:
        print('I2C Device {} has been found at 0x{}'.format(Device, Address))
        rp_dict.log06_PTB['{} 0x{}'.format(Device, Address)] = 'Detected'
    else:
        print('Loss I2C Device [{}] at 0x{} ...'.format(Device, Address))
        rp_dict.log06_PTB['{} 0x{}'.format(Device, Address)] = 'No'
    Device = 'LTC2990';    Address = '4e'
    if Address in readback:
        print('I2C Device {} has been found at 0x{}'.format(Device, Address))
        rp_dict.log06_PTB['{} 0x{}'.format(Device, Address)] = 'Detected'
    else:
        print('Loss I2C Device [{}] at 0x{} ...'.format(Device, Address))
        rp_dict.log06_PTB['{} 0x{}'.format(Device, Address)] = 'No'


    tcp.tcp_poke(1, 0x04)
    readback = send_command(connection, 'i2cdetect -r -y 2')
    print(readback)
    Device = 'TCA6424';    Address = '22'
    if Address in readback:
        print('I2C Device {} has been found at 0x{}'.format(Device, Address))
        rp_dict.log06_PTB['{} 0x{}'.format(Device, Address)] = 'Detected'
    else:
        print('Loss I2C Device [{}] at 0x{} ...'.format(Device, Address))
        rp_dict.log06_PTB['{} 0x{}'.format(Device, Address)] = 'No'
    Device = 'TCA642';    Address = '23'
    if Address in readback:
        print('I2C Device {} has been found at 0x{}'.format(Device, Address))
        rp_dict.log06_PTB['{} 0x{}'.format(Device, Address)] = 'Detected'
    else:
        print('Loss I2C Device [{}] at 0x{} ...'.format(Device, Address))
        rp_dict.log06_PTB['{} 0x{}'.format(Device, Address)] = 'No'

#######
    tcp.tcp_poke(1, 0x05)
    time.sleep(3)
    readback = send_command(connection, 'i2cdetect -r -y 1')
    print(readback)
    Device = 'LTC2499';    Address = '15'
    if Address in readback:
        print('I2C Device {} has been found at 0x{}'.format(Device, Address))
        rp_dict.log06_PTB['{} 0x{}'.format(Device, Address)] = 'Detected'
    else:
        print('Loss I2C Device [{}] at 0x{} ...'.format(Device, Address))
        rp_dict.log06_PTB['{} 0x{}'.format(Device, Address)] = 'No'

    Device = 'INA226';    Address = '46'
    if Address in readback:
        print('I2C Device {} has been found at 0x{}'.format(Device, Address))
        rp_dict.log06_PTB['{} 0x{}'.format(Device, Address)] = 'Detected'
    else:
        print('Loss I2C Device [{}] at 0x{} ...'.format(Device, Address))
        rp_dict.log06_PTB['{} 0x{}'.format(Device, Address)] = 'No'
    Device = 'AD7414A';      Address = '49'
    if Address in readback:
        print('I2C Device {} has been found at 0x{}'.format(Device, Address))
        rp_dict.log06_PTB['{} 0x{}'.format(Device, Address)] = 'Detected'
    else:
        print('Loss I2C Device [{}] at 0x{} ...'.format(Device, Address))
        rp_dict.log06_PTB['{} 0x{}'.format(Device, Address)] = 'No'

    Device = 'AD7414A';      Address = '4a'
    if Address in readback:
        print('I2C Device {} has been found at 0x{}'.format(Device, Address))
        rp_dict.log06_PTB['{} 0x{}'.format(Device, Address)] = 'Detected'
    else:
        print('Loss I2C Device [{}] at 0x{} ...'.format(Device, Address))
        rp_dict.log06_PTB['{} 0x{}'.format(Device, Address)] = 'No'

    Device = 'AD7414A'
    Address = '4d'
    if Address in readback:
        print('I2C Device {} has been found at 0x{}'.format(Device, Address))
        rp_dict.log06_PTB['{} 0x{}'.format(Device, Address)] = 'Detected'
    else:
        print('Loss I2C Device [{}] at 0x{} ...'.format(Device, Address))
        rp_dict.log06_PTB['{} 0x{}'.format(Device, Address)] = 'No'

    Device = 'SODIMM'
    Address = '51'
    if Address in readback:
        print('I2C Device {} has been found at 0x{}'.format(Device, Address))
        rp_dict.log06_PTB['{} 0x{}'.format(Device, Address)] = 'Detected'
    else:
        print('Loss I2C Device [{}] at 0x{} ...'.format(Device, Address))
        rp_dict.log06_PTB['{} 0x{}'.format(Device, Address)] = 'No'

    Device = 'LTC2991'
    Address = '48'
    if Address in readback:
        print('I2C Device {} has been found at 0x{}'.format(Device, Address))
        rp_dict.log06_PTB['{} 0x{}'.format(Device, Address)] = 'Detected'
    else:
        print('Loss I2C Device [{}] at 0x{} ...'.format(Device, Address))
        rp_dict.log06_PTB['{} 0x{}'.format(Device, Address)] = 'No'

    Device = 'LTC2991'
    Address = '4c'
    if Address in readback:
        print('I2C Device {} has been found at 0x{}'.format(Device, Address))
        rp_dict.log06_PTB['{} 0x{}'.format(Device, Address)] = 'Detected'
    else:
        print('Loss I2C Device [{}] at 0x{} ...'.format(Device, Address))
        rp_dict.log06_PTB['{} 0x{}'.format(Device, Address)] = 'No'

    Device = 'LTC2991'
    Address = '4e'
    if Address in readback:
        print('I2C Device {} has been found at 0x{}'.format(Device, Address))
        rp_dict.log06_PTB['{} 0x{}'.format(Device, Address)] = 'Detected'
    else:
        print('Loss I2C Device [{}] at 0x{} ...'.format(Device, Address))
        rp_dict.log06_PTB['{} 0x{}'.format(Device, Address)] = 'No'


#####
#######
    tcp.tcp_poke(1, 0x06)
    readback = send_command(connection, 'i2cdetect -r -y 0')
    print(readback)
    Device = 'DAC7574';    Address = '4c'
    if Address in readback:
        print('I2C Device {} has been found at 0x{}'.format(Device, Address))
        rp_dict.log06_PTB['{} 0x{}'.format(Device, Address)] = 'Detected'
    else:
        print('Loss I2C Device [{}] at 0x{} ...'.format(Device, Address))
        rp_dict.log06_PTB['{} 0x{}'.format(Device, Address)] = 'No'
    Device = 'DAC7574'
    Address = '4d'
    if Address in readback:
        print('I2C Device {} has been found at 0x{}'.format(Device, Address))
        rp_dict.log06_PTB['{} 0x{}'.format(Device, Address)] = 'Detected'
    else:
        print('Loss I2C Device [{}] at 0x{} ...'.format(Device, Address))
        rp_dict.log06_PTB['{} 0x{}'.format(Device, Address)] = 'No'
    Device = 'DAC7574'
    Address = '4e'
    if Address in readback:
        print('I2C Device {} has been found at 0x{}'.format(Device, Address))
        rp_dict.log06_PTB['{} 0x{}'.format(Device, Address)] = 'Detected'
    else:
        print('Loss I2C Device [{}] at 0x{} ...'.format(Device, Address))
        rp_dict.log06_PTB['{} 0x{}'.format(Device, Address)] = 'No'
    Device = 'DAC7574'
    Address = '4f'
    if Address in readback:
        print('I2C Device {} has been found at 0x{}'.format(Device, Address))
        rp_dict.log06_PTB['{} 0x{}'.format(Device, Address)] = 'Detected'
    else:
        print('Loss I2C Device [{}] at 0x{} ...'.format(Device, Address))
        rp_dict.log06_PTB['{} 0x{}'.format(Device, Address)] = 'No'

    #######
    tcp.tcp_poke(1, 0x07)
    readback = send_command(connection, 'i2cdetect -r -y 0')
    print(readback)
    Device = 'LTC2977'
    Address = '5c'
    if Address in readback:
        print('I2C Device {} has been found at 0x{}'.format(Device, Address))
        rp_dict.log06_PTB['{} 0x{}'.format(Device, Address)] = 'Detected'
    else:
        print('Loss I2C Device [{}] at 0x{} ...'.format(Device, Address))
        rp_dict.log06_PTB['{} 0x{}'.format(Device, Address)] = 'No'

#####
    tcp.tcp_poke(1, 0x08)
    readback = send_command(connection, 'i2cdetect -r -y 1')
    print(readback)
    Device = 'DAC7574'
    Address = '4c'
    if Address in readback:
        print('I2C Device {} has been found at 0x{}'.format(Device, Address))
        rp_dict.log06_PTB['{} 0x{}'.format(Device, Address)] = 'Detected'
    else:
        print('Loss I2C Device [{}] at 0x{} ...'.format(Device, Address))
        rp_dict.log06_PTB['{} 0x{}'.format(Device, Address)] = 'No'
    Device = 'DAC7574'
    Address = '4d'
    if Address in readback:
        print('I2C Device {} has been found at 0x{}'.format(Device, Address))
        rp_dict.log06_PTB['{} 0x{}'.format(Device, Address)] = 'Detected'
    else:
        print('Loss I2C Device [{}] at 0x{} ...'.format(Device, Address))
        rp_dict.log06_PTB['{} 0x{}'.format(Device, Address)] = 'No'

    #####
    tcp.tcp_poke(1, 0x09)
    readback = send_command(connection, 'i2cdetect -r -y 0')
    print(readback)
    Device = '24LC64SN'
    Address = '50'
    if Address in readback:
        print('I2C Device {} has been found at 0x{}'.format(Device, Address))
        rp_dict.log06_PTB['{} 0x{}'.format(Device, Address)] = 'Detected'
    else:
        print('Loss I2C Device [{}] at 0x{} ...'.format(Device, Address))
        rp_dict.log06_PTB['{} 0x{}'.format(Device, Address)] = 'No'

    #####
    tcp.tcp_poke(1, 0x0a)
    readback = send_command(connection, 'i2cdetect -y 0')
    print(readback)
    Device = 'ADN2814'
    Address = '40'
    if Address in readback:
        print('I2C Device {} has been found at 0x{}'.format(Device, Address))
        rp_dict.log06_PTB['{} 0x{}'.format(Device, Address)] = 'Detected'
    else:
        print('Loss I2C Device [{}] at 0x{} ...'.format(Device, Address))
        rp_dict.log06_PTB['{} 0x{}'.format(Device, Address)] = 'No'

        # Allow user to send further commands
        # while True:
        #     cmd = input("Enter command to send (or 'exit' to close): ")
        #     if cmd.lower() == "exit":
        #         print("Closing connection...")
        #         connection.close()
        #         break
        #     else:
        #         send_command(connection, cmd)
time.sleep(0.5)

# Update CSV with all I2C device detection results
if rp_dict.csv_manager:
    # Map device names to CSV item IDs
    device_mapping = {
        'SI5342': 'T05_10',
        'SI5344': 'T05_11',
        'TCA9546ADR 0x70': 'T05_12',
        'LTC2991 0x48': 'T05_13',
        'LTC2991 0x49': 'T05_14',
        'LTC2991 0x4a': 'T05_15',
        'LTC2991 0x4b': 'T05_16',
        'LTC2990 0x4e': 'T05_17',
        'TCA6424 0x22': 'T05_18',
        'TCA642 0x23': 'T05_19',
        'LTC2499 0x15': 'T05_20',
        'INA226 0x46': 'T05_21',
        'AD7414A 0x49': 'T05_22',
        'AD7414A 0x4a': 'T05_23',
        'AD7414A 0x4d': 'T05_24',
        'SODIMM 0x51': 'T05_25',
        'DAC7574 0x4c': 'T05_29',
        'DAC7574 0x4d': 'T05_30',
        'DAC7574 0x4e': 'T05_31',
        'DAC7574 0x4f': 'T05_32',
        'LTC2977 0x5c': 'T05_33',
        '24LC64SN 0x50': 'T05_36',
        'ADN2814 0x40': 'T05_37'
    }

    updates = []
    for device_name, item_id in device_mapping.items():
        device_status = rp_dict.log06_PTB.get(device_name, "Not Tested")
        csv_status = "PASS" if "Detected" in device_status else "FAIL"
        updates.append({
            "item_id": item_id,
            "value": device_status,
            "status": csv_status
        })

    rp_dict.csv_manager.batch_update(updates)

psu.safe_power_off()
psu.close()
t2 = time.time()
test_duration = round(t2-t1, 2)
print('time consumption = {}'.format(test_duration))

# Update CSV with test duration
if rp_dict.csv_manager:
    rp_dict.csv_manager.update_item("T05_99", test_duration, status="COMPLETE")



import os

# === Setup relative path to ../report/I2C_Device_report_051.html ===
base_dir = os.path.dirname(os.path.abspath(__file__))
target_file_path = os.path.join(base_dir, "..", "report", "WIB_05_I2C_Device_report_051.html")
print(target_file_path)

# Ensure target directory exists
os.makedirs(os.path.dirname(target_file_path), exist_ok=True)

# Determine overall status
all_devices_detected = all("Detected" in str(value) for value in rp_dict.log06_PTB.values())
overall_status = "PASS" if all_devices_detected else "FAIL"
overall_status_class = "status-pass" if all_devices_detected else "status-fail"

# Count detected devices
total_devices = len(rp_dict.log06_PTB)
detected_devices = sum(1 for value in rp_dict.log06_PTB.values() if "Detected" in str(value))

# Build device table rows
device_rows = ""
for key, value in rp_dict.log06_PTB.items():
    status_class = "status-pass" if "Detected" in value else "status-fail"
    status_text = "PASS" if "Detected" in value else "FAIL"
    device_rows += f"<tr><td>{key}</td><td>{value}</td><td class='{status_class}'>{status_text}</td></tr>\n"

# HTML content with professional clean styling
html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>WIB I2C Device Search Report - Test05</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 40px;
            background-color: #ffffff;
            color: #000000;
        }}
        .container {{
            max-width: 1000px;
            margin: 0 auto;
        }}
        .header {{
            border-bottom: 2px solid #000000;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }}
        .header h1 {{
            margin: 0;
            font-size: 24px;
            font-weight: bold;
        }}
        .subtitle {{
            font-size: 18px;
            color: #333333;
            margin-top: 5px;
        }}
        .status-badge {{
            display: inline-block;
            padding: 8px 16px;
            margin: 10px 0;
            font-weight: bold;
            border: 2px solid #000000;
        }}
        .status-pass {{
            background-color: #ffffff;
            color: #000000;
        }}
        .status-fail {{
            background-color: #fee2e2;
            color: #000000;
        }}
        .info-section {{
            margin: 20px 0;
            padding: 15px;
            background-color: #f5f5f5;
            border: 1px solid #cccccc;
        }}
        .info-row {{
            display: flex;
            padding: 5px 0;
        }}
        .info-label {{
            font-weight: bold;
            min-width: 200px;
        }}
        .info-value {{
            flex: 1;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background-color: #ffffff;
        }}
        th, td {{
            border: 1px solid #000000;
            padding: 10px;
            text-align: left;
        }}
        th {{
            background-color: #e5e5e5;
            font-weight: bold;
        }}
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        .footer {{
            margin-top: 30px;
            padding-top: 15px;
            border-top: 1px solid #cccccc;
            text-align: center;
            color: #666666;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>DUNE WIB Quality Control</h1>
            <div class="subtitle">I2C Device Search Report (Test05)</div>
            <div class="status-badge {overall_status_class}">Overall Status: {overall_status}</div>
        </div>

        <!-- Test Information -->
        <div class="info-section">
            <div class="info-row">
                <div class="info-label">Test Date:</div>
                <div class="info-value">{datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")}</div>
            </div>
            <div class="info-row">
                <div class="info-label">Test Duration:</div>
                <div class="info-value">{test_duration} seconds</div>
            </div>
            <div class="info-row">
                <div class="info-label">Devices Detected:</div>
                <div class="info-value">{detected_devices} / {total_devices}</div>
            </div>
            <div class="info-row">
                <div class="info-label">WIB IP Address:</div>
                <div class="info-value">192.168.121.1</div>
            </div>
        </div>

        <!-- Power Measurements -->
        <h2>WIB Power Supply</h2>
        <table>
            <thead>
                <tr>
                    <th>Channel</th>
                    <th>Voltage (V)</th>
                    <th>Current (A)</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Channel 1</td>
                    <td>{v1:.3f}</td>
                    <td>{c1:.3f}</td>
                    <td class="{'status-pass' if 11.0 <= v1 <= 13.0 and 0.5 <= c1 <= 3.0 else 'status-fail'}">{'PASS' if 11.0 <= v1 <= 13.0 and 0.5 <= c1 <= 3.0 else 'FAIL'}</td>
                </tr>
                <tr>
                    <td>Channel 2</td>
                    <td>{v2:.3f}</td>
                    <td>{c2:.3f}</td>
                    <td class="{'status-pass' if 11.0 <= v2 <= 13.0 and 0.5 <= c2 <= 3.0 else 'status-fail'}">{'PASS' if 11.0 <= v2 <= 13.0 and 0.5 <= c2 <= 3.0 else 'FAIL'}</td>
                </tr>
            </tbody>
        </table>

        <!-- I2C Device Detection Results -->
        <h2>I2C Device Detection Results</h2>
        <table>
            <thead>
                <tr>
                    <th>Device Name & Address</th>
                    <th>Detection Result</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                {device_rows}
            </tbody>
        </table>

        <!-- Footer -->
        <div class="footer">
            <p>Generated by DUNE WIB QC System - Test05: I2C Device Search</p>
            <p>Report generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        </div>
    </div>
</body>
</html>
"""

# Always create new file (overwrite if exists)
with open(target_file_path, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"HTML report saved (new file) to {target_file_path}")















