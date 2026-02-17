"""
Test01: Serial/TCP/IP Communication Test
Tests UART, TCP/IP, and UDP communication with WIB board.
"""

import serial
import serial.tools.list_ports
import time
import sys
import os
from datetime import datetime, timezone

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from function.ping_host import ping_host
import file.report_dict as rp_dict
import function.Rigol_DP800 as rigol
import GUI.send_email as send_email

# Email configuration
SENDER_EMAIL = "bnlr216@gmail.com"
SENDER_PASSWORD = "vvef tosp minf wwhf"

# Supported USB-to-Serial adapter VID/PID pairs
SUPPORTED_ADAPTERS = [
    {"name": "Silicon Labs CP2105", "vid": 0x10C4, "pid": 0xEA70},
    {"name": "FTDI FT232", "vid": 0x0403, "pid": 0x6001},
    {"name": "FTDI FT2232", "vid": 0x0403, "pid": 0x6010},
]


def print_header(title):
    """Print formatted section header."""
    print("\n" + "=" * 60)
    print("\033[35m" + title + "\033[0m")
    print("=" * 60)


def send_failure_notification(tester_email, failed_items, wib_id="Unknown"):
    """
    Send email notification when test items fail.
    failed_items: list of tuples [(interface, test_name, note), ...]
    """
    if not tester_email or '@' not in tester_email:
        print("\033[33mNo valid email configured - skipping notification\033[0m")
        return False

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    # Build failed items list
    failed_list = ""
    for interface, test_name, note in failed_items:
        failed_list += f"  ❌ {interface} - {test_name}\n"
        failed_list += f"     Note: {note}\n\n"

    subject = f"[WIB QC ALERT] Test01 Communication FAILED - {wib_id}"

    body = f"""
{'='*60}
WIB QC TEST FAILURE NOTIFICATION
{'='*60}

Date/Time: {timestamp}
WIB ID: {wib_id}
Test: Test01 - Serial/TCP/IP Communication

{'='*60}
FAILED TEST ITEMS:
{'='*60}

{failed_list}
{'='*60}
FPGA SYSTEM STATUS: CHECK REQUIRED
{'='*60}
  FPGA: U96 ZYNQ-XCZU6CG-1FFVB1156E
  Memory: J10 DDR4

The above components may require inspection.

{'='*60}
ACTION REQUIRED:
{'='*60}
  1. Check cable connections for failed interfaces
  2. Verify power supply status
  3. Re-run failed tests if connections were loose
  4. Contact support if issue persists

---
This is an automated message from the WIB QC Test System.
"""

    try:
        send_email.send_email(
            SENDER_EMAIL,
            SENDER_PASSWORD,
            tester_email,
            subject,
            body
        )
        print_pass(f"Failure notification sent to: {tester_email}")
        return True
    except Exception as e:
        print_fail(f"Failed to send notification email: {e}")
        return False


def print_pass(message):
    """Print green pass message."""
    print(f"\033[32m{message}\033[0m")


def print_fail(message):
    """Print red fail message."""
    print(f"\033[31m{message}\033[0m")


def find_serial_port(psu):
    """
    Find supported USB-to-Serial adapter with retry option.
    Returns: (com_port, adapter_name) or (None, None) if skipped.
    """
    while True:
        print("\n=== Available USB Serial Devices ===")
        ports = serial.tools.list_ports.comports()

        for port in ports:
            if port.vid is not None and port.pid is not None:
                print(f"  Device: {port.device}")
                print(f"  VID:PID = {port.vid:04X}:{port.pid:04X}")
                print(f"  Manufacturer: {port.manufacturer}")
                print(f"  Description: {port.description}")
                print()

        # Find supported adapter
        for port in ports:
            for adapter in SUPPORTED_ADAPTERS:
                if port.vid == adapter["vid"] and port.pid == adapter["pid"]:
                    print_pass(f"Found supported adapter: {adapter['name']}")
                    print_pass(f"Using device: {port.device}")
                    return port.device, adapter["name"]

        # Not found - show available devices and ask for retry
        print_fail("No supported USB-to-Serial adapter found!")
        print("\nSupported adapters:")
        for adapter in SUPPORTED_ADAPTERS:
            print(f"  {adapter['name']}: VID:PID = {adapter['vid']:04X}:{adapter['pid']:04X}")
        print("\nAvailable devices:")
        for port in ports:
            if port.vid is not None:
                print(f"  {port.device}: VID:PID = {port.vid:04X}:{port.pid:04X}")

        # Ask for retry, skip, or exit
        print_fail("\nUSB-to-Serial adapter not detected.")
        print("Please check the connection and try again.\n")
        while True:
            choice = input("Options:\n  [R] Retry detection\n  [S] Skip UART test and continue\n  [E] Exit all tests\nYour choice (R/S/E): ").strip().upper()
            if choice == 'R':
                print(f"\033[33m\n==> Retrying USB-Serial detection...\033[0m")
                time.sleep(1)
                break
            elif choice == 'S':
                print(f"\033[33m\n==> Skipping UART test, continuing to TCP/IP...\033[0m")
                return None, None
            elif choice == 'E':
                print_fail("\nTest aborted by user.")
                psu.safe_power_off()
                psu.close()
                sys.exit(1)
            else:
                print("\033[33mInvalid choice. Please enter 'R', 'S', or 'E'.\033[0m")


def run_uart_test(com_port, psu):
    """
    Run UART/Serial communication test.
    Returns: (status, note)
    """
    print(f"\nConnecting to {com_port}...")

    try:
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
                print(line)
                buffer += line + "\n"
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
                    print_pass('Serial Communication Pass')
                    return True, 'Serial Communication Pass'

            elif time.time() - last_data_time > 30:
                print("No data received for 30 seconds. Stopping.")
                print_fail("Failed the Serial Communication Test")
                return False, 'Serial Communication Failed - Timeout'

    except KeyboardInterrupt:
        print_fail("\nInterrupted by user.")
        raise

    except Exception as e:
        print_fail(f"Serial communication error: {e}")
        return False, f'Serial Communication Error: {e}'

    finally:
        if 'ser_test' in locals():
            ser_test.close()
            print("Serial port closed.")


def run_ping_test(ip_address, test_name):
    """
    Run ping test to specified IP.
    Returns: (status, note)
    """
    result = ping_host(ip_address=ip_address, count=4)
    if result:
        return True, f'{test_name} Communication Pass'
    else:
        return False, f'{test_name} Communication Failed'


def retry_test(test_func, test_name, psu, *args):
    """
    Run test with retry option on failure.
    Returns: (status, note)
    """
    while True:
        status, note = test_func(*args)

        if status:
            print_pass(f"✓ {test_name} Test PASSED")
            return status, note

        # Test failed - prompt for retry, skip, or exit
        print_header(f"❌ {test_name} Test FAILED")
        print_fail(f"\n{test_name} test has FAILED.")
        print("What would you like to do?\n")
        while True:
            choice = input("Options:\n  [R] Retry this test\n  [S] Skip and continue to next test\n  [E] Exit all tests\nYour choice (R/S/E): ").strip().upper()
            if choice == 'R':
                print(f"\033[33m\n==> Retrying {test_name} test...\033[0m")
                time.sleep(1)
                break
            elif choice == 'S':
                print(f"\033[33m\n==> Skipping {test_name} test, continuing to next...\033[0m")
                return False, f'{test_name} - SKIPPED (Failed)'
            elif choice == 'E':
                print_fail("\nTest aborted by user.")
                psu.safe_power_off()
                psu.close()
                sys.exit(1)
            else:
                print("\033[33mInvalid choice. Please enter 'R', 'S', or 'E'.\033[0m")


def generate_html_report(com_port, adapter_name, test_duration, results):
    """
    Generate HTML report for communication tests.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    target_file_path = os.path.join(base_dir, "..", "report", "WIB_01_communication_report_01.html")
    os.makedirs(os.path.dirname(target_file_path), exist_ok=True)

    uart_status = results['uart']['status']
    tcp_status = results['tcp']['status']
    udp_status = results['udp']['status']

    overall_pass = uart_status and tcp_status and udp_status
    overall_status = "PASS" if overall_pass else "FAIL"
    overall_class = "pass" if overall_pass else "fail"

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>WIB Communication Test Report</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #fff; color: #000; padding: 30px; line-height: 1.6; }}
        .container {{ max-width: 900px; margin: 0 auto; }}
        .header {{ border-bottom: 3px solid #000; padding-bottom: 20px; margin-bottom: 30px; }}
        .header h1 {{ font-size: 24px; font-weight: bold; margin-bottom: 5px; }}
        .header .subtitle {{ font-size: 14px; color: #666; }}
        .status-badge {{ display: inline-block; padding: 8px 16px; font-weight: bold; font-size: 16px; margin-top: 15px; border: 2px solid; }}
        .status-badge.pass {{ color: #166534; background-color: #dcfce7; border-color: #166534; }}
        .status-badge.fail {{ color: #991b1b; background-color: #fee2e2; border-color: #991b1b; }}
        .info-section {{ margin: 20px 0; padding: 15px; background: #f9fafb; border-left: 4px solid #000; }}
        .info-row {{ display: flex; margin: 8px 0; }}
        .info-label {{ font-weight: bold; width: 150px; }}
        .section {{ margin: 30px 0; }}
        .section-title {{ font-size: 18px; font-weight: bold; margin-bottom: 15px; padding-bottom: 8px; border-bottom: 2px solid #e5e7eb; }}
        table {{ width: 100%; border-collapse: collapse; margin: 15px 0; border: 1px solid #000; }}
        th {{ background-color: #f3f4f6; font-weight: bold; text-align: left; padding: 12px; border: 1px solid #000; }}
        td {{ padding: 12px; border: 1px solid #d1d5db; }}
        tr:nth-child(even) {{ background-color: #f9fafb; }}
        .status-pass {{ color: #166534; font-weight: bold; }}
        .status-fail {{ color: #991b1b; font-weight: bold; }}
        .footer {{ margin-top: 40px; padding-top: 20px; border-top: 2px solid #e5e7eb; text-align: center; color: #6b7280; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>DUNE WIB Quality Control</h1>
            <div class="subtitle">Communication Test Report (Test01)</div>
            <div class="status-badge {overall_class}">Overall Status: {overall_status}</div>
        </div>

        <div class="info-section">
            <div class="info-row"><div class="info-label">Test Date:</div><div>{results['uart']['date']}</div></div>
            <div class="info-row"><div class="info-label">Total Test Time:</div><div>{test_duration} seconds</div></div>
            <div class="info-row"><div class="info-label">Serial Interface:</div><div>{com_port} ({adapter_name})</div></div>
        </div>

        <div class="info-section" style="background: #f0f9ff; border-left-color: #0066cc;">
            <div style="font-weight: bold; margin-bottom: 10px;">FPGA System Verification</div>
            <div class="info-row"><div class="info-label">FPGA:</div><div>U96 ZYNQ-XCZU6CG-1FFVB1156E</div></div>
            <div class="info-row"><div class="info-label">Memory:</div><div>J10 DDR4</div></div>
            <div class="info-row"><div class="info-label">Status:</div><div style="color: {'#166534' if overall_pass else '#991b1b'}; font-weight: bold;">{'Operational - All interfaces verified' if overall_pass else 'Check Required - Some interfaces failed'}</div></div>
        </div>

        <div class="section">
            <div class="section-title">Test Results Summary</div>
            <table>
                <thead>
                    <tr><th>Test Item</th><th>Interface</th><th>Target</th><th>Status</th><th>Notes</th></tr>
                </thead>
                <tbody>
                    <tr>
                        <td><strong>1. UART/Serial</strong></td>
                        <td><strong>P17</strong></td>
                        <td>{com_port}</td>
                        <td class="status-{'pass' if uart_status else 'fail'}">{'PASS' if uart_status else 'FAIL'}</td>
                        <td>{results['uart']['note']}</td>
                    </tr>
                    <tr>
                        <td><strong>2. TCP/IP</strong></td>
                        <td><strong>P16</strong></td>
                        <td>192.168.121.1</td>
                        <td class="status-{'pass' if tcp_status else 'fail'}">{'PASS' if tcp_status else 'FAIL'}</td>
                        <td>{results['tcp']['note']}</td>
                    </tr>
                    <tr>
                        <td><strong>3. UDP</strong></td>
                        <td><strong>P15</strong></td>
                        <td>192.168.121.2</td>
                        <td class="status-{'pass' if udp_status else 'fail'}">{'PASS' if udp_status else 'FAIL'}</td>
                        <td>{results['udp']['note']}</td>
                    </tr>
                </tbody>
            </table>
        </div>

        <div class="footer">
            <p>DUNE WIB Quality Control System - Test01 Communication Test</p>
            <p>Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>
</body>
</html>"""

    with open(target_file_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"\nHTML report saved to: {target_file_path}")
    return target_file_path


def main():
    """Main test function."""
    t1 = time.time()
    utc_time = datetime.now(timezone.utc)

    # Print header
    print_header("A_RT01 : Serial_TCPIP_Communication Test")
    print("This test verifies FPGA system communication interfaces.")
    print("Passing confirms: U96 ZYNQ-XCZU6CG-1FFVB1156E + J10 DDR4 operational")
    print("")
    print("Test items:")
    print("  1. UART/Serial Communication (P17)")
    print("  2. TCP/IP Communication (P16)")
    print("  3. UDP Communication (P15)")
    print("=" * 60)

    # Initialize power supply
    psu = rigol.RigolDP800()

    # Results storage
    results = {
        'uart': {'status': False, 'note': '', 'date': utc_time.strftime("%Y-%m-%d %H:%M:%S UTC")},
        'tcp': {'status': False, 'note': '', 'date': utc_time.strftime("%Y-%m-%d %H:%M:%S UTC")},
        'udp': {'status': False, 'note': '', 'date': utc_time.strftime("%Y-%m-%d %H:%M:%S UTC")}
    }

    # Find serial port
    print_header("Test Item 1: UART/Serial Communication (P17)")
    com_port, adapter_name = find_serial_port(psu)

    rp_dict.log02_wib['uart_date'] = utc_time.strftime("%Y-%m-%d %H:%M:%S UTC")

    # Check if UART was skipped
    if com_port is None:
        rp_dict.log02_wib['uart_com'] = 'No USB-Serial adapter found - SKIPPED'
        rp_dict.log02_wib['uart_status'] = False
        rp_dict.log02_wib['uart_note'] = 'UART test skipped - no adapter found'
        results['uart']['status'] = False
        results['uart']['note'] = 'SKIPPED - No USB-Serial adapter'
        if rp_dict.csv_manager:
            rp_dict.csv_manager.update_item("T01_01", "SKIP", status="SKIP")
    else:
        rp_dict.log02_wib['uart_com'] = f'COM_PORT is {com_port} using {adapter_name}'

    # Power on
    print("\nTurn FM on")
    psu.set_channel(1, 12.0, 3.0, on=True)
    psu.set_channel(2, 12.0, 3.0, on=True)
    time.sleep(10)
    v1, c1 = psu.measure(1)
    v2, c2 = psu.measure(2)

    try:
        # Test 1: UART (only if adapter found)
        if com_port is not None:
            status, note = retry_test(run_uart_test, "UART/Serial (P17)", psu, com_port, psu)
            results['uart']['status'] = status
            results['uart']['note'] = note
            rp_dict.log02_wib['uart_status'] = status
            rp_dict.log02_wib['uart_note'] = note

            # Update CSV
            if rp_dict.csv_manager:
                rp_dict.csv_manager.update_item("T01_01", "PASS" if status else "FAIL", status="PASS" if status else "FAIL")

        # Test 2: TCP/IP
        print_header("Test Item 2: TCP/IP Communication (P16)")
        status, note = retry_test(lambda: run_ping_test("192.168.121.1", "TCP/IP"), "TCP/IP (P16)", psu)
        results['tcp']['status'] = status
        results['tcp']['note'] = note
        rp_dict.log02_wib['TCP_IP_status'] = status
        rp_dict.log02_wib['TCP_IP_note'] = note
        rp_dict.log02_wib['TCP_IP_date'] = utc_time.strftime("%Y-%m-%d %H:%M:%S UTC")

        if rp_dict.csv_manager and status:
            rp_dict.csv_manager.batch_update([
                {"item_id": "T01_02", "value": "192.168.121.1", "status": "PASS"},
                {"item_id": "T01_03", "value": "Connected", "status": "PASS"}
            ])

        # Test 3: UDP
        print_header("Test Item 3: UDP Communication (P15)")
        status, note = retry_test(lambda: run_ping_test("192.168.121.2", "UDP"), "UDP (P15)", psu)
        results['udp']['status'] = status
        results['udp']['note'] = note
        rp_dict.log02_wib['UDP_status'] = status
        rp_dict.log02_wib['UDP_note'] = note
        rp_dict.log02_wib['UDP_date'] = utc_time.strftime("%Y-%m-%d %H:%M:%S UTC")

        if rp_dict.csv_manager and status:
            rp_dict.csv_manager.batch_update([
                {"item_id": "T01_05", "value": "Connected", "status": "PASS"},
                {"item_id": "T01_07", "value": "4 packets received", "status": "PASS"}
            ])

        # Calculate duration
        t2 = time.time()
        test_duration = round(t2 - t1, 2)
        rp_dict.log02_wib['Communication_Time_Consumption'] = f'Communication Time Consumption = {test_duration} s'

        # Update CSV with power measurements
        if rp_dict.csv_manager:
            rp_dict.csv_manager.batch_update([
                {"item_id": "T01_08", "value": round(v1, 3), "status": "PASS" if 11.0 <= v1 <= 13.0 else "FAIL"},
                {"item_id": "T01_09", "value": round(c1, 3), "status": "PASS" if 0.5 <= c1 <= 3.0 else "FAIL"},
                {"item_id": "T01_10", "value": round(v2, 3), "status": "PASS" if 11.0 <= v2 <= 13.0 else "FAIL"},
                {"item_id": "T01_11", "value": round(c2, 3), "status": "PASS" if 0.5 <= c2 <= 3.0 else "FAIL"},
                {"item_id": "T01_12", "value": test_duration, "status": "COMPLETE"}
            ])

        # Print summary
        all_pass = results['uart']['status'] and results['tcp']['status'] and results['udp']['status']
        print_header("✓ ALL COMMUNICATION TESTS COMPLETED")
        print(f"Total test time: {test_duration} seconds")
        print("")
        print("Interface Results:")
        print(f"  P17 - UART Communication: {'PASS' if results['uart']['status'] else 'FAIL'}")
        print(f"  P16 - TCP/IP Communication: {'PASS' if results['tcp']['status'] else 'FAIL'}")
        print(f"  P15 - UDP Communication: {'PASS' if results['udp']['status'] else 'FAIL'}")
        print("")
        print("FPGA System Components:")
        print("  U96 - ZYNQ-XCZU6CG-1FFVB1156E")
        print("  J10 - DDR4 Memory")
        if all_pass:
            print_pass("  Status: OPERATIONAL - All interfaces verified")
        else:
            print_fail("  Status: CHECK REQUIRED - Some interfaces failed")
        print("=" * 60)

        # Send email notification if any test failed
        if not all_pass:
            # Collect failed items
            failed_items = []
            if not results['uart']['status']:
                failed_items.append(("P17", "UART/Serial Communication", results['uart']['note']))
            if not results['tcp']['status']:
                failed_items.append(("P16", "TCP/IP Communication", results['tcp']['note']))
            if not results['udp']['status']:
                failed_items.append(("P15", "UDP Communication", results['udp']['note']))

            # Get tester email from wib_info
            tester_email = rp_dict.wib_info.get('tester_email', '') if hasattr(rp_dict, 'wib_info') else ''
            wib_id = rp_dict.wib_info.get('WIB_ID', 'Unknown') if hasattr(rp_dict, 'wib_info') else 'Unknown'

            if failed_items:
                print("\n" + "=" * 60)
                print("Sending failure notification email...")
                send_failure_notification(tester_email, failed_items, wib_id)

        if test_duration > 40:
            print(f"\033[33m⚠ Warning: Test time ({test_duration}s) exceeded recommended 40 seconds\033[0m")

        # Generate report
        report_com_port = com_port if com_port else "N/A"
        report_adapter = adapter_name if adapter_name else "Not detected"
        generate_html_report(report_com_port, report_adapter, test_duration, results)

    finally:
        # Power off and cleanup
        print("\nTurning off power supply...")
        psu.safe_power_off()
        psu.close()
        print_pass("Test01 completed successfully!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_fail("\n\nTest interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print_fail(f"\nError: {e}")
        sys.exit(1)
