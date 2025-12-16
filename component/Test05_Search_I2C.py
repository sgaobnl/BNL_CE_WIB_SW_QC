import socket
import time
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# from function.rigol_dp832_ps import RIGOL_PS_CTL
import function.Rigol_DP800 as rigol
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
v2, c2 = psu.measure(1)
time.sleep(1)
print(c1)
print(c2)

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
psu.safe_power_off()
psu.close()
t2 = time.time()
print('time consumption = {}'.format(t2-t1))



import os

# === Setup relative path to ../report/I2C_Device_report_051.html ===
base_dir = os.path.dirname(os.path.abspath(__file__))
target_file_path = os.path.join(base_dir, "..", "report", "WIB_05_I2C_Device_report_051.html")
print(target_file_path)

# Ensure target directory exists
os.makedirs(os.path.dirname(target_file_path), exist_ok=True)

# Collect key-value pairs
rows = ""
for key, value in rp_dict.log06_PTB.items():
    rows += f"<tr><td>{key}</td><td>{value}</td></tr>\n"

# HTML content with CSS styling
html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>WIB_05 I2C Device Report</title>
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
        table {{
            width: 60%;
            margin: 20px auto;
            border-collapse: collapse;
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
            background: #fff;
            border-radius: 8px;
            overflow: hidden;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 10px 15px;
            text-align: left;
        }}
        th {{
            background-color: #f0f0f0;
            font-weight: bold;
            text-align: center;
        }}
        tr:nth-child(even) td {{
            background-color: #fafafa;
        }}
    </style>
</head>
<body>
    <h2>I2C Device Report</h2>
    <table>
        <thead>
            <tr>
                <th>Item</th>
                <th>Value</th>
            </tr>
        </thead>
        <tbody>
            {rows}
        </tbody>
    </table>
</body>
</html>
"""

# Always create new file (overwrite if exists)
with open(target_file_path, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"HTML report saved (new file) to {target_file_path}")















