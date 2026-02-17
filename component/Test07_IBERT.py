import sys
import os
# import path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# from function.rigol_dp832_ps import RIGOL_PS_CTL
from function.ping_host import ping_host
from datetime import datetime
import subprocess




import file.report_dict as rp_dict
import time
import path
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LogNorm

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import function.Rigol_DP800 as rigol

t1 = time.time()
psu = rigol.RigolDP800()
# fm_ps = RIGOL_PS_CTL()
psu.safe_power_off()
time.sleep(0.5)
print("Turn FM on")
psu.set_channel(1, 12.0, 3.0, on=True)
psu.set_channel(2, 12.0, 3.0, on=True)
time.sleep(10)
v1, c1 = psu.measure(1)
v2, c2 = psu.measure(1)
# fm_ps.ps_init()
# fm_ps.off([1, 2, 3])
# time.sleep(2)
# fm_ps.set_channel(channel=1, voltage=11.9, v_limit=12.1, c_limit=3)
#
# fm_ps.set_channel(channel=2, voltage=12, v_limit=12.1, c_limit=3)
# fm_ps.on([1, 2])
# time.sleep(1)
# c1 = fm_ps.measure_params(channel = 1)
# c2 = fm_ps.measure_params(channel = 2)
print(c1)
print(c2)
time.sleep(1) # wait for boot

project_dir = "/home/dune/Documents/DUNE_WIB_QC_Script"
# # from ../file import example_ibert_ultrascale_gth_0.bit
#
# # Path to Vivado executable (adjust this based on your system)
vivado_path = path.xilinx_path
#
# # Run Vivado in batch mode with the Tcl script
command = [vivado_path, "-mode", "batch", "-source", "./file/Test07_vivado_tcl_command.tcl"]
#
# # Execute the command
process = subprocess.run(command, capture_output=True, text=True, cwd = project_dir)
#
# # Print the output and errors (if any)
print(process.stdout)
print(process.stderr)

# command = [vivado_path, "-mode", "batch", "-source", "../file/Test07_vivado_tcl_command.tcl"]
#
# import subprocess

# Path to Vivado executable (adjust this based on your system)
# vivado_path = "D:/Xilinx/Vivado/2023.2/bin/vivado.bat"
# time.sleep(1000)


# time to test
# the time used to test gtx ber *** import item IBERT BER
time.sleep(1000)
print('Measure the BER Result of GTX')
command = [vivado_path, "-mode", "batch", "-source", "file/tcl_02.tcl"]
# # Execute the command
process = subprocess.run(command, capture_output=True, text=True, cwd = project_dir)

print(process.stdout)

log_text = process.stdout
for line in log_text.splitlines():
    line = line.strip()
    print(line)
    # Match X0Y4 channel (using MGT_X0Y4/RX pattern which is consistent)
    if 'MGT_X0Y4/RX Total_BER:' in line:
        print(2)
        rp_dict.log07_ibert["X0Y4_Total_BER"] = line.split("Total_BER:")[-1].strip()
    elif 'MGT_X0Y4/RX Total_ERROR_count:' in line:
        print(3)
        rp_dict.log07_ibert['X0Y4_Total_ERROR_count'] = line.split("Total_ERROR_count:")[-1].strip()
    elif 'MGT_X0Y4/RX Total_BIT_count:' in line:
        print(4)
        rp_dict.log07_ibert["X0Y4_Total_BIT_count"] = line.split("Total_BIT_count:")[-1].strip()
    # Match X0Y5 channel
    elif 'MGT_X0Y5/RX Total_BER:' in line:
        print(5)
        rp_dict.log07_ibert['X0Y5_Total_BER'] = line.split("Total_BER:")[-1].strip()
    elif 'MGT_X0Y5/RX Total_ERROR_count:' in line:
        print(6)
        rp_dict.log07_ibert["X0Y5_Total_ERROR_count"] = line.split("Total_ERROR_count:")[-1].strip()
    elif 'MGT_X0Y5/RX Total_BIT_count:' in line:
        rp_dict.log07_ibert['X0Y5_Total_BIT_count'] = line.split("Total_BIT_count:")[-1].strip()
print(rp_dict)
# === Evaluate Test Result: Total_ERROR_count should be 0 ===
# Error counts are in hexadecimal format (e.g., 000000000000)
x0y4_error_str = rp_dict.log07_ibert.get('X0Y4_Total_ERROR_count', '-1')
x0y5_error_str = rp_dict.log07_ibert.get('X0Y5_Total_ERROR_count', '-1')

time.sleep(10)
command = [vivado_path, "-mode", "batch", "-source", "file/eyeScan.tcl"]
# # Execute the command
process = subprocess.run(command, capture_output=True, text=True, cwd = project_dir)
print(process.stdout)
# Parse hex values (handle both hex string and decimal)
try:
    x0y4_error_count = int(x0y4_error_str, 16)  # Parse as hexadecimal
except ValueError:
    x0y4_error_count = int(x0y4_error_str) if x0y4_error_str != '-1' else -1

try:
    x0y5_error_count = int(x0y5_error_str, 16)  # Parse as hexadecimal
except ValueError:
    x0y5_error_count = int(x0y5_error_str) if x0y5_error_str != '-1' else -1

# Determine pass/fail for each channel with result and decision
x0y4_decision = "PASS" if x0y4_error_count == 0 else "FAIL"
x0y5_decision = "PASS" if x0y5_error_count == 0 else "FAIL"

# rp_dict.log07_ibert['X0Y4_Total_ERROR_count_Result'] = x0y4_error_count
rp_dict.log07_ibert['X0Y4_Total_ERROR_count_Decision'] = x0y4_decision
# rp_dict.log07_ibert['X0Y5_Total_ERROR_count_Result'] = x0y5_error_count
rp_dict.log07_ibert['X0Y5_Total_ERROR_count_Decision'] = x0y5_decision

# Overall test status: PASS only if both channels have 0 errors
if x0y4_error_count == 0 and x0y5_error_count == 0:
    rp_dict.log07_ibert['Overall_Test_Status'] = "PASS"
    print("\033[32m" + "IBERT Test PASSED: Total_ERROR_count is 0 for both channels" + "\033[0m")
else:
    rp_dict.log07_ibert['Overall_Test_Status'] = "FAIL"
    print("\033[31m" + f"IBERT Test FAILED: X0Y4 Total_ERROR_count={x0y4_error_count} ({x0y4_decision}), X0Y5 Total_ERROR_count={x0y5_error_count} ({x0y5_decision})" + "\033[0m")

print(rp_dict.log07_ibert)

t2 = time.time()
print(t2 - t1)

print("Turn Power Supply off")
time.sleep(0.5)
psu.safe_power_off()
psu.close()
# fm_ps.off([1, 2, 3])




# === Setup Output Directory Structure ===
base_dir = os.path.dirname(os.path.abspath(__file__))
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# Get WIB board ID from rp_dict if available, otherwise use default
try:
    wib_id = rp_dict.wib_info.get('WIB_ID', 'UNKNOWN')
except:
    wib_id = 'UNKNOWN'

# Create output directory: report/WIB_07_IBERT_<WIB_ID>_<timestamp>/
output_dir_name = f"WIB_07_IBERT_{wib_id}_{timestamp}"
output_dir = os.path.join(base_dir, "..", "report", output_dir_name)
os.makedirs(output_dir, exist_ok=True)

print(f"\n{'=' * 60}")
print(f"Output Directory: {output_dir}")
print(f"{'=' * 60}\n")

# Store output directory in rp_dict for reference
rp_dict.log07_ibert['Output_Directory'] = output_dir_name

# Copy scan CSV files to output directory
import shutil
scan00_src = os.path.join(base_dir, "..", "scan00.csv")
scan01_src = os.path.join(base_dir, "..", "scan01.csv")
scan00_dst = os.path.join(output_dir, "scan00_X0Y4.csv")
scan01_dst = os.path.join(output_dir, "scan01_X0Y5.csv")

try:
    if os.path.exists(scan00_src):
        shutil.copy2(scan00_src, scan00_dst)
        print(f"Copied: scan00.csv -> {scan00_dst}")
except Exception as e:
    print(f"Warning: Could not copy scan00.csv: {e}")

try:
    if os.path.exists(scan01_src):
        shutil.copy2(scan01_src, scan01_dst)
        print(f"Copied: scan01.csv -> {scan01_dst}")
except Exception as e:
    print(f"Warning: Could not copy scan01.csv: {e}")

# === Step 1: Load specific region from CSV ===
filename = os.path.join(base_dir, "..", "scan00.csv")
eye_data = pd.read_csv(filename, skiprows=22, nrows=30, header=None, usecols=range(1, 10))
eye_matrix = eye_data.apply(pd.to_numeric, errors='coerce').dropna(how='any').values

# === Step 2: Replace zeros to avoid log scale crash ===
eye_matrix[eye_matrix == 0] = 1e-12  # Replace 0 with tiny value for log scale

# === Step 3: Plot with vivid color layering and log scale ===
plt.figure(figsize=(10, 6))

img = plt.imshow(
    eye_matrix,
    aspect='auto',
    cmap='jet',
    origin='lower',
    norm=LogNorm(vmin=1e-10, vmax=1e-0)  # Covers BER range from 1e-12 (blue) to 1e-3 (red)
)

# Add colorbar with log ticks
cbar = plt.colorbar(img)
cbar.set_label('Bit Error Rate (log scale)')
cbar.set_ticks([1e-10, 1e-9, 1e-8, 1e-7, 1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1, 1e-0])
cbar.ax.set_yticklabels(['1e-10', '1e-9', '1e-8', '1e-7', '1e-6', '1e-5', '1e-4', '1e-3', '1e-2', '1e-1', '1e-0'])

# Add labels and layout
plt.title('Eye Scan for X0Y4 (Log BER Heatmap)')
plt.xlabel('Horizontal Offset (UI)')
plt.ylabel('Vertical Offset (Codes)')
plt.tight_layout()
target_file_path1 = os.path.join(output_dir, "eye_scan_X0Y4.png")
plt.savefig(target_file_path1, dpi=300, bbox_inches='tight')
print(f"Saved: {target_file_path1}")

# === Step 1: Load specific region from CSV ===
filename = os.path.join(base_dir, "..", "scan01.csv")  # X0Y5 eye scan CSV
eye_data = pd.read_csv(filename, skiprows=22, nrows=30, header=None, usecols=range(1, 10))
eye_matrix = eye_data.apply(pd.to_numeric, errors='coerce').dropna(how='any').values

# === Step 2: Replace zeros to avoid log scale crash ===
eye_matrix[eye_matrix == 0] = 1e-12  # Replace 0 with tiny value for log scale

# === Step 3: Plot with vivid color layering and log scale ===
plt.figure(figsize=(10, 6))

img = plt.imshow(
    eye_matrix,
    aspect='auto',
    cmap='jet',
    origin='lower',
    norm=LogNorm(vmin=1e-10, vmax=1e-0)  # Covers BER range from 1e-12 (blue) to 1e-3 (red)
)

# Add colorbar with log ticks
cbar = plt.colorbar(img)
cbar.set_label('Bit Error Rate (log scale)')
cbar.set_ticks([1e-10, 1e-9, 1e-8, 1e-7, 1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1, 1e-0])
cbar.ax.set_yticklabels(['1e-10', '1e-9', '1e-8', '1e-7', '1e-6', '1e-5', '1e-4', '1e-3', '1e-2', '1e-1', '1e-0'])




# Add labels and layout
plt.title('Eye Scan for X0Y5 (Log BER Heatmap)')
plt.xlabel('Horizontal Offset (UI)')
plt.ylabel('Vertical Offset (Codes)')
plt.tight_layout()
target_file_path2 = os.path.join(output_dir, "eye_scan_X0Y5.png")
plt.savefig(target_file_path2, dpi=300, bbox_inches='tight')
print(f"Saved: {target_file_path2}")

# === Setup HTML report path in output directory ===
target_file_path = os.path.join(output_dir, "WIB_07_IBERT_report.html")
print(f"HTML Report: {target_file_path}")

# Print rp_dict.log07_ibert contents for verification
# print("\n" + "=" * 60)
# print("rp_dict.log07_ibert contents:")
# print("=" * 60)
# for key, value in rp_dict.log07_ibert.items():
#     print(f"  {key}: {value}")
# print("=" * 60 + "\n")

# Build table rows with status highlighting
rows = ""
if len(rp_dict.log07_ibert) == 0:
    rows = '<tr><td colspan="2" style="text-align: center; color: red;">No data captured - rp_dict.log07_ibert is empty</td></tr>\n'
else:
    for key, value in rp_dict.log07_ibert.items():
        # Add color styling for Decision and Status fields
        if 'Decision' in key or 'Status' in key:
            if value == "PASS":
                value_html = f'<span style="color: green; font-weight: bold;">{value}</span>'
            else:
                value_html = f'<span style="color: red; font-weight: bold;">{value}</span>'
        elif 'ERROR_count_Result' in key:
            # Highlight error count results - red if not 0, green if 0
            try:
                if int(value) != 0:
                    value_html = f'<span style="color: red; font-weight: bold;">{value}</span>'
                else:
                    value_html = f'<span style="color: green; font-weight: bold;">{value}</span>'
            except:
                value_html = str(value)
        else:
            value_html = str(value)
        rows += f"<tr><td>{key}</td><td>{value}</td></tr>\n"

# Determine overall status for header styling
overall_status = rp_dict.log07_ibert.get('Overall_Test_Status', 'UNKNOWN')
status_color = "#28a745" if overall_status == "PASS" else "#dc3545"
status_bg = "#d4edda" if overall_status == "PASS" else "#f8d7da"

# HTML content with styling
html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>WIB_07 WIB IBERT</title>
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
        .status-banner {{
            text-align: center;
            padding: 15px;
            margin: 20px auto;
            width: 60%;
            border-radius: 8px;
            font-size: 1.2em;
            font-weight: bold;
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
        .images {{
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-top: 30px;
        }}
        .images img {{
            max-width: 48%;
            border-radius: 6px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.15);
        }}
    </style>
</head>
<body>
    <h2>WIB IBERT Report</h2>
    <div class="status-banner" style="background-color: {status_bg}; color: {status_color}; border: 2px solid {status_color};">
        Overall Test Status: {overall_status}
    </div>

    <h3 style="text-align: center; margin-top: 30px;">IBERT (Integrated Bit Error Ratio Tester) serial analyzer</h3>
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

    <h3 style="text-align: center; margin-top: 30px;">Eye Scan Results</h3>
    <div class="images">
        <img src="./eye_scan_X0Y4.png" alt="Eye Scan X0Y4">
        <img src="./eye_scan_X0Y5.png" alt="Eye Scan X0Y5">
    </div>
</body>
</html>
"""

# Always create new file (overwrite if exists)
with open(target_file_path, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"HTML report saved to {target_file_path}")

# === Export test data to CSV ===
csv_file_path = os.path.join(output_dir, "IBERT_test_results.csv")
try:
    with open(csv_file_path, "w", encoding="utf-8") as csv_file:
        csv_file.write("Item,Value\n")
        for key, value in rp_dict.log07_ibert.items():
            csv_file.write(f"{key},{value}\n")
    print(f"CSV report saved to {csv_file_path}")
except Exception as e:
    print(f"Warning: Could not save CSV: {e}")

# === Print Output Directory Summary ===
print("\n" + "=" * 60)
print("TEST 07 IBERT - OUTPUT FILES SUMMARY")
print("=" * 60)
print(f"Output Directory: {output_dir}")
print("-" * 60)
print("Files generated:")
for f in os.listdir(output_dir):
    file_path = os.path.join(output_dir, f)
    file_size = os.path.getsize(file_path)
    print(f"  - {f} ({file_size} bytes)")
print("=" * 60)
print(f"\nAll files saved to: {output_dir}")
print("Ready for network drive copy.")

