import serial
import serial.tools.list_ports
import time
import sys
import os

# Add the parent directory to sys.path so 'function' can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Now it's safe to import from 'function'
from function.rigol_dp832_ps import RIGOL_PS_CTL
# Other imports...

from function.ping_host import ping_host
import subprocess
import file.report_dict as rp_dict
import os
import datetime
from datetime import datetime, timezone
import function.Rigol_DP800 as rigol

psu = rigol.RigolDP800()
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
print("Turn FM on")


import serial
import serial.tools.list_ports
from datetime import datetime, timezone
import time












# 寻找串口
print("\033[35m" + "A_RT01 : Serial_TCPIP_Communication Test" + "\033[0m")
utc_time = datetime.now(timezone.utc)
t1 = time.time()

# Silicon Labs CP2105 的 VID 和 PID
VID = 0x10C4  # Silicon Labs
PID = 0xEA70  # CP2105 Dual UART Bridge

# 列出所有串口设备（类似 lsusb）
print("\n=== Available USB Serial Devices ===")
ports = serial.tools.list_ports.comports()
for port in ports:
    if port.vid is not None and port.pid is not None:
        print(f"  VID:PID = {port.vid:04X}:{port.pid:04X}")
    print(f"  Manufacturer: {port.manufacturer}")
    print(f"  Serial Number: {port.serial_number}")

# 通过 VID/PID 查找设备
com_port = None
for port in ports:
    if port.vid == VID and port.pid == PID:
        com_port = port.device
        print(f"\033[32mFound device: {port.device}\033[0m")
        print(f"  Description: {port.description}")
        print(f"  Serial Number: {port.serial_number}")
        break

rp_dict.log02_wib['uart_date'] = utc_time.strftime("%Y-%m-%d %H:%M:%S UTC")

if com_port is None:
    # 如果找不到，打印当前所有设备的VID/PID供参考
    print("\n\033[31mDevice not found!\033[0m")
    print(f"Looking for VID:PID = {VID:04X}:{PID:04X}")
    print("\nAvailable devices:")
    for port in ports:
        if port.vid is not None:
            print(f"  {port.device}: VID:PID = {port.vid:04X}:{port.pid:04X}")
    raise Exception("Device not found. Check the connection or VID/PID.")
else:
    rp_dict.log02_wib['uart_com'] = f'COM_PORT is {com_port}'

# Configure the serial port
ser = serial.Serial(
    port=com_port,
    baudrate=115200,
    bytesize=serial.EIGHTBITS,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    timeout=1,
    rtscts=False,
    dsrdtr=False,
    xonxoff=False
)

print(f"\n\033[32mSerial port {com_port} opened successfully\033[0m")




















print("Turn FM on")
print("Turn FM on")
psu.set_channel(1, 12.0, 3.0, on=True)
psu.set_channel(2, 12.0, 3.0, on=True)
time.sleep(10)
v1, c1 = psu.measure(1)
v2, c2 = psu.measure(1)
print(f"Connected to {com_port}")
uart_status = False
uart_note = ''
try:
    buffer = ""
    login_detected = False
    last_data_time = time.time()

    while True:
        line = ser.readline().decode('utf-8', errors='ignore').strip()

        if line:
            print(line)  # Print received data
            buffer += line + "\n"  # Store received data
            last_data_time = time.time()

            if line == "WIB_Petalinux login:" and not login_detected:
                print("Detected login prompt, sending 'root'...")
                ser.write(b'root\n')
                login_detected = True

            elif "Password:" in line and login_detected:
                print("Detected password prompt, sending 'root'...")
                ser.write(b'root\n')

            elif "root@WIB_Petalinux:" in line and login_detected:
                print("Detected Linux, sending 'root'...")
                ser.write(b'cat /etc/issue\n')

            elif 'PetaLinux 2019.1' in line and login_detected:
                ser.write(b'\n')
                print('Serial Communication Pass')
                uart_status = True
                uart_note = 'Serial Communication Pass'
                break

        elif time.time() - last_data_time > 10:
            print("No data received for 10 seconds. Stopping.")
            print("Failed the Serial Communication Test")
            uart_status = False
            uart_note = 'Serial Communication Failed Test'
            break



except KeyboardInterrupt:
    print("\nInterrupted by user.")

finally:
    ser.close()
    print("Serial port closed.")

rp_dict.log02_wib['uart_status'] = uart_status
rp_dict.log02_wib['uart_note'] = uart_note

tcpip_rd = ping_host(ip_address="192.168.121.1", count=4)
rp_dict.log02_wib['TCP_IP_date'] = utc_time.strftime("%Y-%m-%d %H:%M:%S UTC")

rp_dict.log02_wib['TCP_IP_status'] = tcpip_rd
if tcpip_rd:
    rp_dict.log02_wib['TCP_IP_note'] = 'TCP/IP Communication Pass'
else:
    rp_dict.log02_wib['TCP_IP_note'] = 'TCP/IP Communication Failed Test'

udp_rd = ping_host(ip_address="192.168.121.2", count=4)
rp_dict.log02_wib['UDP_date'] = utc_time.strftime("%Y-%m-%d %H:%M:%S UTC")
rp_dict.log02_wib['UDP_status'] = tcpip_rd
if tcpip_rd:
    rp_dict.log02_wib['UDP_note'] = 'TCP/IP Communication Pass'
else:
    rp_dict.log02_wib['UDP_note'] = 'TCP/IP Communication Failed Test'



t2 = time.time()
rp_dict.log02_wib['Communication_Time_Consumption'] = 'Communication Time Consumption = {} s'.format(round(t2-t1, 2))
# time < 40 seconds



import os

# === Setup relative path to ../file/communication_report_01.html ===
base_dir = os.path.dirname(os.path.abspath(__file__))
target_file_path = os.path.join(base_dir, "..", "report", "WIB_01_communication_report_01.html")

# Ensure target directory exists
os.makedirs(os.path.dirname(target_file_path), exist_ok=True)

# Collect report values from rp_dict
uart_date = rp_dict.log02_wib['uart_date']
uart_com = rp_dict.log02_wib['uart_com']
uart_status = str(rp_dict.log02_wib['uart_status'])
uart_note = rp_dict.log02_wib['uart_note']

tcp_date = rp_dict.log02_wib['TCP_IP_date']
tcp_status = str(rp_dict.log02_wib['TCP_IP_status'])
tcp_note = rp_dict.log02_wib['TCP_IP_note']

udp_date = rp_dict.log02_wib['UDP_date']
udp_status = str(rp_dict.log02_wib['UDP_status'])
udp_note = rp_dict.log02_wib['UDP_note']

# HTML content with CSS styling
html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>WIB_01 Communication Test Report</title>
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
        .item {{
            margin: 8px 0;
        }}
        .label {{
            font-weight: bold;
            color: #555;
        }}
        .value {{
            margin-left: 10px;
        }}
    </style>
</head>
<body>
    <h2>Communication Test Report</h2>

    <div class="section">
        <h3>UART Communication</h3>
        <div class="item"><span class="label">Date:</span><span class="value">{uart_date}</span></div>
        <div class="item"><span class="label">COM:</span><span class="value">{uart_com}</span></div>
        <div class="item"><span class="label">Status:</span><span class="value">{uart_status}</span></div>
        <div class="item"><span class="label">Note:</span><span class="value">{uart_note}</span></div>
    </div>

    <div class="section">
        <h3>TCP/IP Communication</h3>
        <div class="item"><span class="label">Date:</span><span class="value">{tcp_date}</span></div>
        <div class="item"><span class="label">Status:</span><span class="value">{tcp_status}</span></div>
        <div class="item"><span class="label">Note:</span><span class="value">{tcp_note}</span></div>
    </div>

    <div class="section">
        <h3>UDP Communication</h3>
        <div class="item"><span class="label">Date:</span><span class="value">{udp_date}</span></div>
        <div class="item"><span class="label">Status:</span><span class="value">{udp_status}</span></div>
        <div class="item"><span class="label">Note:</span><span class="value">{udp_note}</span></div>
    </div>
</body>
</html>
"""

# Always create new file (overwrite if exists)
with open(target_file_path, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"HTML report saved (new file) to {target_file_path}")


