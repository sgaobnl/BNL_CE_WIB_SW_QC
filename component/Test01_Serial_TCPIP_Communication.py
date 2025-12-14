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
import sys

# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

print("\033[35m" + "A_RT01 : Serial_TCPIP_Communication Test" + "\033[0m")
utc_time = datetime.now(timezone.utc)
t1 = time.time()
# Find the correct port for "Silicon Labs Dual CP2105 USB to UART Bridge: Standard COM Port"
device_name = "Silicon Labs Dual CP2105 USB to UART Bridge: Standard COM Port"
fm_ps = RIGOL_PS_CTL()
ports = serial.tools.list_ports.comports()
com_port = None

for port in ports:
    if device_name in port.description:
        com_port = port.device
        break

rp_dict.log02_wib['uart_date'] = utc_time.strftime("%Y-%m-%d %H:%M:%S UTC")
if com_port is None:
    raise Exception("Device not found. Check the connection or device name.")
else:
    rp_dict.log02_wib['uart_com'] = 'COM_PORT is {}'.format(com_port)

# Configure the serial port
ser = serial.Serial(
    port=com_port,
    baudrate=115200,  # Speed: 115200
    bytesize=serial.EIGHTBITS,  # Data bits: 8
    parity=serial.PARITY_NONE,  # Parity: None
    stopbits=serial.STOPBITS_ONE,  # Stop bits: 1
    timeout=1,  # Read timeout
    rtscts=False,  # Flow control: None
    dsrdtr=False,
    xonxoff=False
)

print("Turn FM on")
fm_ps.ps_init()
fm_ps.off([1, 2, 3])
fm_ps.set_channel(channel=1, voltage=12, v_limit=12.1, c_limit=3)
fm_ps.set_channel(channel=2, voltage=12, v_limit=12.1, c_limit=3)
fm_ps.on([1, 2])
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


