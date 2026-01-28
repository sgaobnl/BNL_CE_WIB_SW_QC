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
# the time used to test gtx ber
time.sleep(20)
print('Measure the BER Result of GTX')
command = [vivado_path, "-mode", "batch", "-source", "file/tcl_02.tcl"]
# # Execute the command
process = subprocess.run(command, capture_output=True, text=True, cwd = project_dir)

print(process.stdout)

time.sleep(10)
command = [vivado_path, "-mode", "batch", "-source", "file/eyeScan.tcl"]
# # Execute the command
process = subprocess.run(command, capture_output=True, text=True, cwd = project_dir)
print(process.stdout)

log_text = process.stdout
for line in log_text.splitlines():
    line = line.strip()
    if 'IBERT/Quad_128/MGT_X0Y4/RX Total_BER:' in line:
        rp_dict.log07_ibert["X0Y4_BIT_Error_Rate"] = line.split("Total_BER:")[-1].strip()
    elif 'IBERT/Quad_128/MGT_X0Y4/RX Total_ERROR_count:' in line:
        rp_dict.log07_ibert['X0Y4_ERROR_count'] = line.split("Total_ERROR_count:")[-1].strip()
    elif 'IBERT/Quad_128/MGT_X0Y4/RX Total_BIT_count:' in line:
        rp_dict.log07_ibert["X0Y4_BIT_count"] = line.split("Total_BIT_count:")[-1].strip()
    elif 'IBERT/Quad_128/MGT_X0Y5/RX Total_BER:' in line:
        rp_dict.log07_ibert['X0Y5_BIT_Error_Rate'] = line.split("Total_BER:")[-1].strip()
    elif 'IBERT/Quad_128/MGT_X0Y5/RX Total_ERROR_count:' in line:
        rp_dict.log07_ibert["X0Y5_ERROR_Number"] = line.split("Total_ERROR_count:")[-1].strip()
    elif 'IBERT/Quad_128/MGT_X0Y5/RX Total_BIT_count:' in line:
        rp_dict.log07_ibert['X0Y5_BIT_Number'] = line.split("Total_BIT_count:")[-1].strip()

print(rp_dict.log07_ibert)

t2 = time.time()
print(t2 - t1)

time.sleep(2)
psu.close()
# fm_ps.off([1, 2, 3])




# === Step 1: Load specific region from CSV ===
base_dir = os.path.dirname(os.path.abspath(__file__))
# target_file_path = os.path.join(base_dir, "..", "report", "scan00.csv")

filename = '../scan00.csv'
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
target_file_path1 = os.path.join(base_dir, "..", "report", "eye_scan_X0Y4.png")
plt.savefig(target_file_path1, dpi=300, bbox_inches='tight')

# === Step 1: Load specific region from CSV ===
filename = '../scan01.csv'  # your CSV
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
target_file_path2 = os.path.join(base_dir, "..", "report", "eye_scan_X0Y5.png")
plt.savefig(target_file_path2, dpi=300, bbox_inches='tight')

import os

# === Setup relative path to ../report/WIB_IBERT_07.html ===
target_file_path = os.path.join(base_dir, "..", "report", "WIB_07_WIB_IBERT.html")
print(target_file_path)

# Ensure target directory exists
os.makedirs(os.path.dirname(target_file_path), exist_ok=True)

# Build table rows
rows = ""
for key, value in rp_dict.log07_ibert.items():
    rows += f"<tr><td>{key}</td><td>{value}</td></tr>\n"

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

print(f"HTML report saved (new file) to {target_file_path}")

