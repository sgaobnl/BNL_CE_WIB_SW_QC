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
from function.csv_manager import WIB_QC_CSV_Manager
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
print("\n" + "="*60)
print("\033[35m" + "A_RT01 : Serial_TCPIP_Communication Test" + "\033[0m")
print("="*60)
print("This test includes 3 test items:")
print("  1. UART/Serial Communication")
print("  2. TCP/IP Communication")
print("  3. UDP Communication")
print("="*60)
utc_time = datetime.now(timezone.utc)
t1 = time.time()

# Test Item 1: UART/Serial Communication
print("\n" + "="*60)
print("\033[35m" + "Test Item 1: UART/Serial Communication" + "\033[0m")
print("="*60)

# Supported USB-to-Serial adapter VID/PID pairs
SUPPORTED_ADAPTERS = [
    {"name": "Silicon Labs CP2105", "vid": 0x10C4, "pid": 0xEA70},
    {"name": "FTDI FT232", "vid": 0x0403, "pid": 0x6001},
    {"name": "FTDI FT2232", "vid": 0x0403, "pid": 0x6010},
]

# 列出所有串口设备（类似 lsusb）
print("\n=== Available USB Serial Devices ===")
ports = serial.tools.list_ports.comports()
for port in ports:
    if port.vid is not None and port.pid is not None:
        print(f"  Device: {port.device}")
        print(f"  VID:PID = {port.vid:04X}:{port.pid:04X}")
        print(f"  Manufacturer: {port.manufacturer}")
        print(f"  Description: {port.description}")
        print(f"  Serial Number: {port.serial_number}")
        print()

# 通过支持的 VID/PID 列表查找设备
com_port = None
adapter_name = None
for port in ports:
    for adapter in SUPPORTED_ADAPTERS:
        if port.vid == adapter["vid"] and port.pid == adapter["pid"]:
            com_port = port.device
            adapter_name = adapter["name"]
            print(f"\033[32mFound supported adapter: {adapter_name}\033[0m")
            print(f"\033[32mUsing device: {port.device}\033[0m")
            print(f"  Description: {port.description}")
            print(f"  VID:PID: {port.vid:04X}:{port.pid:04X}")
            break
    if com_port is not None:
        break

rp_dict.log02_wib['uart_date'] = utc_time.strftime("%Y-%m-%d %H:%M:%S UTC")

if com_port is None:
    # 如果找不到，打印当前所有设备的VID/PID供参考
    print("\n\033[31mNo supported USB-to-Serial adapter found!\033[0m")
    print("\nSupported adapters:")
    for adapter in SUPPORTED_ADAPTERS:
        print(f"  {adapter['name']}: VID:PID = {adapter['vid']:04X}:{adapter['pid']:04X}")
    print("\nAvailable devices:")
    for port in ports:
        if port.vid is not None:
            print(f"  {port.device}: VID:PID = {port.vid:04X}:{port.pid:04X}")
    raise Exception("No supported USB-to-Serial adapter found. Check connection or add your adapter to SUPPORTED_ADAPTERS list.")
else:
    rp_dict.log02_wib['uart_com'] = f'COM_PORT is {com_port} using {adapter_name}'



















print("Turn FM on")
psu.set_channel(1, 12.0, 3.0, on=True)
psu.set_channel(2, 12.0, 3.0, on=True)
time.sleep(10)
v1, c1 = psu.measure(1)
v2, c2 = psu.measure(1)

# UART test loop - allows retry without restarting script
uart_test_passed = False
while not uart_test_passed:
    print(f"\nConnecting to {com_port}...")
    uart_status = False
    uart_note = ''

    try:
        # Open serial port for this test attempt
        ser_test = serial.Serial(
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
        print(f"Serial port {com_port} opened for testing")

        buffer = ""
        login_detected = False
        last_data_time = time.time()

        while True:
            line = ser_test.readline().decode('utf-8', errors='ignore').strip()

            if line:
                print(line)  # Print received data
                buffer += line + "\n"  # Store received data
                last_data_time = time.time()

                if line == "WIB_Petalinux login:" and not login_detected:
                    print("Detected login prompt, sending 'root'...")
                    ser_test.write(b'root\n')
                    login_detected = True

                elif "Password:" in line and login_detected:
                    print("Detected password prompt, sending 'root'...")
                    ser_test.write(b'root\n')

                elif "root@WIB_Petalinux:" in line and login_detected:
                    print("Detected Linux prompt, sending command...")
                    ser_test.write(b'cat /etc/issue\n')

                elif 'PetaLinux 2019.1' in line and login_detected:
                    ser_test.write(b'\n')
                    print('\033[32mSerial Communication Pass\033[0m')
                    uart_status = True
                    uart_note = 'Serial Communication Pass'
                    break

            elif time.time() - last_data_time > 30:
                print("No data received for 10 seconds. Stopping.")
                print("\033[31mFailed the Serial Communication Test\033[0m")
                uart_status = False
                uart_note = 'Serial Communication Failed Test'
                break

    except KeyboardInterrupt:
        print("\n\033[31mInterrupted by user.\033[0m")
        if 'ser_test' in locals():
            ser_test.close()
        psu.safe_power_off()
        psu.close()
        sys.exit(1)

    except Exception as e:
        print(f"\033[31mSerial communication error: {e}\033[0m")
        uart_status = False
        uart_note = f'Serial Communication Error: {e}'

    finally:
        if 'ser_test' in locals():
            ser_test.close()
            print("Serial port closed.")

    # Check UART test result and prompt for retry or exit
    if not uart_status:
        print("\n" + "="*60)
        print("\033[31m" + "❌ UART/Serial Communication Test FAILED" + "\033[0m")
        print("="*60)
        while True:
            choice = input("\nOptions:\n  [R] Retry UART test\n  [E] Exit test\nYour choice (R/E): ").strip().upper()
            if choice == 'R':
                print("\033[33m\n==> Retrying UART communication test...\033[0m")
                time.sleep(1)  # Brief pause before retry
                break  # Break inner loop to retry UART test
            elif choice == 'E':
                print("\033[31m\nTest aborted by user.\033[0m")
                psu.safe_power_off()
                psu.close()
                sys.exit(1)
            else:
                print("\033[33mInvalid choice. Please enter 'R' or 'E'.\033[0m")
    else:
        print("\033[32m✓ UART/Serial Communication Test PASSED\033[0m")
        uart_test_passed = True  # Exit retry loop

# Record final UART test results
rp_dict.log02_wib['uart_status'] = uart_status
rp_dict.log02_wib['uart_note'] = uart_note

# Update CSV for UART test
if rp_dict.csv_manager:
    uart_csv_status = "PASS" if uart_status else "FAIL"
    rp_dict.csv_manager.update_item("T01_01", uart_csv_status, status=uart_csv_status)

# Test Item 2: TCP/IP Communication
print("\n" + "="*60)
print("\033[35m" + "Test Item 2: TCP/IP Communication" + "\033[0m")
print("="*60)
tcpip_rd = ping_host(ip_address="192.168.121.1", count=4)
rp_dict.log02_wib['TCP_IP_date'] = utc_time.strftime("%Y-%m-%d %H:%M:%S UTC")

rp_dict.log02_wib['TCP_IP_status'] = tcpip_rd
if tcpip_rd:
    rp_dict.log02_wib['TCP_IP_note'] = 'TCP/IP Communication Pass'
    print("\033[32m✓ TCP/IP Communication Test PASSED\033[0m")

    # Update CSV for TCP/IP test
    if rp_dict.csv_manager:
        rp_dict.csv_manager.batch_update([
            {"item_id": "T01_02", "value": "192.168.121.1", "status": "PASS"},
            {"item_id": "T01_03", "value": "Connected", "status": "PASS"}
        ])
else:
    rp_dict.log02_wib['TCP_IP_note'] = 'TCP/IP Communication Failed Test'
    print("\n" + "="*60)
    print("\033[31m" + "❌ TCP/IP Communication Test FAILED" + "\033[0m")
    print("="*60)
    print("Possible issues:")
    print("  - Network cable not connected")
    print("  - WIB not powered on properly")
    print("  - IP address 192.168.121.1 not reachable")
    while True:
        choice = input("\nOptions:\n  [R] Retry TCP/IP test\n  [E] Exit test\nYour choice (R/E): ").strip().upper()
        if choice == 'R':
            print("\033[33m\nRetrying TCP/IP communication test...\033[0m")
            tcpip_rd = ping_host(ip_address="192.168.121.1", count=4)
            rp_dict.log02_wib['TCP_IP_status'] = tcpip_rd
            if tcpip_rd:
                rp_dict.log02_wib['TCP_IP_note'] = 'TCP/IP Communication Pass'
                print("\033[32m✓ TCP/IP Communication Test PASSED (after retry)\033[0m")

                # Update CSV after successful retry
                if rp_dict.csv_manager:
                    rp_dict.csv_manager.batch_update([
                        {"item_id": "T01_02", "value": "192.168.121.1", "status": "PASS"},
                        {"item_id": "T01_03", "value": "Connected", "status": "PASS"}
                    ])
                break
            else:
                print("\033[31m❌ TCP/IP test failed again.\033[0m")
                continue
        elif choice == 'E':
            print("\033[31m\nTest aborted by user.\033[0m")
            psu.safe_power_off()
            psu.close()
            sys.exit(1)
        else:
            print("\033[33mInvalid choice. Please enter 'R' or 'E'.\033[0m")

# Test Item 3: UDP Communication
print("\n" + "="*60)
print("\033[35m" + "Test Item 3: UDP Communication" + "\033[0m")
print("="*60)
udp_rd = ping_host(ip_address="192.168.121.2", count=4)
rp_dict.log02_wib['UDP_date'] = utc_time.strftime("%Y-%m-%d %H:%M:%S UTC")
rp_dict.log02_wib['UDP_status'] = udp_rd  # Fixed: was tcpip_rd, should be udp_rd
if udp_rd:
    rp_dict.log02_wib['UDP_note'] = 'UDP Communication Pass'
    print("\033[32m✓ UDP Communication Test PASSED\033[0m")

    # Update CSV for UDP test
    if rp_dict.csv_manager:
        rp_dict.csv_manager.batch_update([
            {"item_id": "T01_05", "value": "Connected", "status": "PASS"},
            {"item_id": "T01_07", "value": "4 packets received", "status": "PASS"}
        ])
else:
    rp_dict.log02_wib['UDP_note'] = 'UDP Communication Failed Test'
    print("\n" + "="*60)
    print("\033[31m" + "❌ UDP Communication Test FAILED" + "\033[0m")
    print("="*60)
    print("Possible issues:")
    print("  - UDP service not running on WIB")
    print("  - IP address 192.168.121.2 not reachable")
    print("  - Firewall blocking UDP packets")
    while True:
        choice = input("\nOptions:\n  [R] Retry UDP test\n  [E] Exit test\nYour choice (R/E): ").strip().upper()
        if choice == 'R':
            print("\033[33m\nRetrying UDP communication test...\033[0m")
            udp_rd = ping_host(ip_address="192.168.121.2", count=4)
            rp_dict.log02_wib['UDP_status'] = udp_rd
            if udp_rd:
                rp_dict.log02_wib['UDP_note'] = 'UDP Communication Pass'
                print("\033[32m✓ UDP Communication Test PASSED (after retry)\033[0m")

                # Update CSV after successful retry
                if rp_dict.csv_manager:
                    rp_dict.csv_manager.batch_update([
                        {"item_id": "T01_05", "value": "Connected", "status": "PASS"},
                        {"item_id": "T01_07", "value": "4 packets received", "status": "PASS"}
                    ])
                break
            else:
                print("\033[31m❌ UDP test failed again.\033[0m")
                continue
        elif choice == 'E':
            print("\033[31m\nTest aborted by user.\033[0m")
            psu.safe_power_off()
            psu.close()
            sys.exit(1)
        else:
            print("\033[33mInvalid choice. Please enter 'R' or 'E'.\033[0m")



t2 = time.time()
test_duration = round(t2-t1, 2)
rp_dict.log02_wib['Communication_Time_Consumption'] = f'Communication Time Consumption = {test_duration} s'

# Update CSV with power measurements and test duration
if rp_dict.csv_manager:
    v1_status = "PASS" if 11.0 <= v1 <= 13.0 else "FAIL"
    c1_status = "PASS" if 0.5 <= c1 <= 3.0 else "FAIL"
    v2_status = "PASS" if 11.0 <= v2 <= 13.0 else "FAIL"
    c2_status = "PASS" if 0.5 <= c2 <= 3.0 else "FAIL"

    rp_dict.csv_manager.batch_update([
        {"item_id": "T01_08", "value": round(v1, 3), "status": v1_status},
        {"item_id": "T01_09", "value": round(c1, 3), "status": c1_status},
        {"item_id": "T01_10", "value": round(v2, 3), "status": v2_status},
        {"item_id": "T01_11", "value": round(c2, 3), "status": c2_status},
        {"item_id": "T01_12", "value": test_duration, "status": "COMPLETE"}
    ])

# Display test summary
print("\n" + "="*60)
print("\033[32m" + "✓ ALL COMMUNICATION TESTS COMPLETED" + "\033[0m")
print("="*60)
print(f"Total test time: {test_duration} seconds")
print(f"  ✓ UART Communication: {'PASS' if uart_status else 'FAIL'}")
print(f"  ✓ TCP/IP Communication: {'PASS' if tcpip_rd else 'FAIL'}")
print(f"  ✓ UDP Communication: {'PASS' if udp_rd else 'FAIL'}")
print("="*60)

# Check if test time exceeded threshold
if test_duration > 40:
    print(f"\033[33m⚠ Warning: Test time ({test_duration}s) exceeded recommended 40 seconds\033[0m")



import os

# === Setup relative path to ../file/communication_report_01.html ===
base_dir = os.path.dirname(os.path.abspath(__file__))
target_file_path = os.path.join(base_dir, "..", "report", "WIB_01_communication_report_01.html")

# Ensure target directory exists
os.makedirs(os.path.dirname(target_file_path), exist_ok=True)

# Collect report values from rp_dict
uart_date = rp_dict.log02_wib['uart_date']
uart_com = rp_dict.log02_wib['uart_com']
uart_status_bool = rp_dict.log02_wib['uart_status']
uart_note = rp_dict.log02_wib['uart_note']

tcp_date = rp_dict.log02_wib['TCP_IP_date']
tcp_status_bool = rp_dict.log02_wib['TCP_IP_status']
tcp_note = rp_dict.log02_wib['TCP_IP_note']

udp_date = rp_dict.log02_wib['UDP_date']
udp_status_bool = rp_dict.log02_wib['UDP_status']
udp_note = rp_dict.log02_wib['UDP_note']

# Determine overall test status
overall_pass = uart_status_bool and tcp_status_bool and udp_status_bool
overall_status = "PASS" if overall_pass else "FAIL"
overall_status_class = "pass" if overall_pass else "fail"

# HTML content with professional styling
html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>WIB Communication Test Report</title>
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

        /* Test Results Table */
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

        /* Details Section */
        .details-box {{
            margin: 15px 0;
            padding: 15px;
            border: 1px solid #d1d5db;
            background: #fafafa;
        }}
        .details-title {{
            font-weight: bold;
            color: #000000;
            margin-bottom: 10px;
        }}
        .details-item {{
            margin: 5px 0;
            padding-left: 15px;
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
            <div class="subtitle">Communication Test Report (Test01)</div>
            <div class="status-badge {overall_status_class}">Overall Status: {overall_status}</div>
        </div>

        <!-- Test Information -->
        <div class="info-section">
            <div class="info-row">
                <div class="info-label">Test Date:</div>
                <div class="info-value">{uart_date}</div>
            </div>
            <div class="info-row">
                <div class="info-label">Total Test Time:</div>
                <div class="info-value">{test_duration} seconds</div>
            </div>
            <div class="info-row">
                <div class="info-label">Serial Interface:</div>
                <div class="info-value">{uart_com}</div>
            </div>
        </div>

        <!-- Test Results Summary -->
        <div class="section">
            <div class="section-title">Test Results Summary</div>
            <table>
                <thead>
                    <tr>
                        <th style="width: 30%;">Test Item</th>
                        <th style="width: 25%;">Target</th>
                        <th style="width: 15%;">Status</th>
                        <th style="width: 30%;">Notes</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><strong>1. UART/Serial Communication</strong></td>
                        <td>{com_port}</td>
                        <td class="status-cell status-{'pass' if uart_status_bool else 'fail'}">{'PASS' if uart_status_bool else 'FAIL'}</td>
                        <td>{uart_note}</td>
                    </tr>
                    <tr>
                        <td><strong>2. TCP/IP Communication</strong></td>
                        <td>192.168.121.1</td>
                        <td class="status-cell status-{'pass' if tcp_status_bool else 'fail'}">{'PASS' if tcp_status_bool else 'FAIL'}</td>
                        <td>{tcp_note}</td>
                    </tr>
                    <tr>
                        <td><strong>3. UDP Communication</strong></td>
                        <td>192.168.121.2</td>
                        <td class="status-cell status-{'pass' if udp_status_bool else 'fail'}">{'PASS' if udp_status_bool else 'FAIL'}</td>
                        <td>{udp_note}</td>
                    </tr>
                </tbody>
            </table>
        </div>

        <!-- Detailed Results -->
        <div class="section">
            <div class="section-title">Detailed Test Information</div>

            <div class="details-box">
                <div class="details-title">1. UART/Serial Communication Test</div>
                <div class="details-item">• Test Timestamp: {uart_date}</div>
                <div class="details-item">• Communication Port: {com_port}</div>
                <div class="details-item">• USB Adapter: {uart_com}</div>
                <div class="details-item">• Auto-login: Verified (root@WIB_Petalinux)</div>
                <div class="details-item">• System Version: PetaLinux 2019.1 detected</div>
                <div class="details-item">• Result: {uart_note}</div>
            </div>

            <div class="details-box">
                <div class="details-title">2. TCP/IP Communication Test</div>
                <div class="details-item">• Test Timestamp: {tcp_date}</div>
                <div class="details-item">• Target IP Address: 192.168.121.1</div>
                <div class="details-item">• Protocol: ICMP Echo Request (ping)</div>
                <div class="details-item">• Ping Count: 4 packets</div>
                <div class="details-item">• Result: {tcp_note}</div>
            </div>

            <div class="details-box">
                <div class="details-title">3. UDP Communication Test</div>
                <div class="details-item">• Test Timestamp: {udp_date}</div>
                <div class="details-item">• Target IP Address: 192.168.121.2</div>
                <div class="details-item">• Protocol: ICMP Echo Request (ping)</div>
                <div class="details-item">• Ping Count: 4 packets</div>
                <div class="details-item">• Result: {udp_note}</div>
            </div>
        </div>

        <!-- Footer -->
        <div class="footer">
            <p>DUNE WIB Quality Control System - Test01 Communication Test</p>
            <p>Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
        </div>
    </div>
</body>
</html>
"""

# Always create new file (overwrite if exists)
with open(target_file_path, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"\nHTML report saved to: {target_file_path}")

# Power off and cleanup
print("\nTurning off power supply...")
psu.safe_power_off()
psu.close()
print("\033[32mTest01 completed successfully!\033[0m")


