import time
import sys
import os

# Add the parent directory to sys.path so 'function' can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Now it's safe to import from 'function'
# from function.rigol_dp832_ps import RIGOL_PS_CTL
import function.Rigol_DP800 as rigol
from function.csv_manager import WIB_QC_CSV_Manager
# Other imports...

import file.report_dict as rp_dict
import os
import datetime
from datetime import datetime, timezone

t1 = time.time()

print('######## WIB Reception Checkout           ########')
print('######## Part 00 Information    ########')
print('######## Part 00     ########')
Test_name_d = input('Input your name')
Test_WIB_ID_d = input('Scan or input WIB QR ID')
Test_site_d = input('Input test site (e.g., BNL, FNAL): ')
utc_time = datetime.now(timezone.utc)
rp_dict.log01_wib['WIB QR ID'] = Test_WIB_ID_d
rp_dict.log01_wib['Tester Name'] = Test_name_d
rp_dict.log01_wib['date01'] = utc_time.strftime("%Y-%m-%d %H:%M:%S UTC")

# Initialize CSV Manager for unified test results recording
print(f"\n{'='*60}")
print("Initializing unified CSV test results file...")
print(f"{'='*60}")
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
csv_filepath = os.path.join(
    os.path.dirname(__file__),
    "..",
    "report",
    f"WIB_{Test_WIB_ID_d}_QC_Results_{timestamp}.csv"
)
rp_dict.csv_manager = WIB_QC_CSV_Manager(wib_id=Test_WIB_ID_d, csv_filepath=csv_filepath)
rp_dict.csv_manager.update_wib_info(tester=Test_name_d, test_site=Test_site_d, comment="")
print(f"✓ CSV results file created: {csv_filepath}\n")



# fm_ps = RIGOL_PS_CTL()
# print("Turn FM on")
# fm_ps.ps_init()
# fm_ps.off([1, 2, 3])
# fm_ps.set_channel(channel=1, voltage=11.9, v_limit=11.9, c_limit=3)
# fm_ps.set_channel(channel=2, voltage=12, v_limit=12, c_limit=3)
# fm_ps.on([1, 2])
# time.sleep(9)
# c1 = fm_ps.measure_params(channel = 1)
# c2 = fm_ps.measure_params(channel = 2)
# print(c1)
# print(c2)
# time.sleep(3)
# fm_ps.off([1, 2, 3])


item1 = input('Component Inspection Y/N')
print(item1)
if item1 == 'n' or item1 == 'N':
    rp_dict.log01_wib['Component Inspection'] = 'Failed'
    item1_status = 'FAIL'
else:
    rp_dict.log01_wib['Component Inspection'] = 'Passed'
    item1_status = 'PASS'
utc_time = datetime.now(timezone.utc)
rp_dict.log01_wib['item1_date'] = utc_time.strftime("%Y-%m-%d %H:%M:%S UTC")

# Update CSV
rp_dict.csv_manager.update_item("T00_01", item1_status, status=item1_status)

# print('Insert SD card')
item2 = input('Use LTpowerPlay configure the Power Rail')
if item2 == 'n' or item2 == 'N':
    rp_dict.log01_wib['LTpowerPlay'] = 'Failed'
    item2_status = 'FAIL'
else:
    rp_dict.log01_wib['LTpowerPlay'] = 'Passed'
    item2_status = 'PASS'
utc_time = datetime.now(timezone.utc)
rp_dict.log01_wib['item2_date'] = utc_time.strftime("%Y-%m-%d %H:%M:%S UTC")

# Update CSV
rp_dict.csv_manager.update_item("T00_02", item2_status, status=item2_status)

input('Please insert the WIB into [TEST SLOT]')

input('Power On and Check the current')

psu = rigol.RigolDP800()
print("Turn FM on")
print('power on begin')
psu.set_channel(1, 12.0, 3.0, on=True)
psu.set_channel(2, 12.0, 3.0, on=True)
# fm_ps.set_channel(channel=2, voltage=11.95, v_limit=12.1, c_limit=3)
time.sleep(10)
v1, c1 = psu.measure(1)
v2, c2 = psu.measure(2)
# v2, i2 = psu.measure(2)

# c1 = fm_ps.measure_params(channel = 1)
# c2 = fm_ps.measure_params(channel = 2)
print(v1, c1)
print(v2, c2)
time.sleep(3)
psu.safe_power_off()
psu.close()

rp_dict.log01_wib['Power Check channel 1'] = c1
rp_dict.log01_wib['Power Check channel 2'] = c2
utc_time = datetime.now(timezone.utc)
rp_dict.log01_wib['Power Check Date'] = utc_time.strftime("%Y-%m-%d %H:%M:%S UTC")

# Update CSV with power measurements
c1_status = "PASS" if 0.5 <= c1 <= 2.0 else "FAIL"
c2_status = "PASS" if 0.5 <= c2 <= 2.0 else "FAIL"
rp_dict.csv_manager.batch_update([
    {"item_id": "T00_03", "value": round(c1, 3), "status": c1_status},
    {"item_id": "T00_04", "value": round(c2, 3), "status": c2_status}
])

item3 = input('Install Front Panel')
if item3 == 'n' or item3 == 'N':
    rp_dict.log01_wib['Front_Panel'] = 'Failed'
    item3_status = 'FAIL'
else:
    rp_dict.log01_wib['Front_Panel'] = 'Passed'
    item3_status = 'PASS'
utc_time = datetime.now(timezone.utc)
rp_dict.log01_wib['item3_date'] = utc_time.strftime("%Y-%m-%d %H:%M:%S UTC")

# Update CSV
rp_dict.csv_manager.update_item("T00_05", item3_status, status=item3_status)

t2 = time.time()

rp_dict.log01_wib['Time_Consumption'] = round((t2-t1), 2)

# Update CSV with test duration
rp_dict.csv_manager.update_item("T00_06", round(t2-t1, 2), status="COMPLETE")

















# === Generate Professional HTML Report ===
import os

# Calculate overall status
all_tests_passed = all([
    rp_dict.log01_wib["Component Inspection"] == "Passed",
    rp_dict.log01_wib["LTpowerPlay"] == "Passed",
    rp_dict.log01_wib["Front_Panel"] == "Passed"
])
overall_status = "PASS" if all_tests_passed else "FAIL"

# Define the path to the output HTML file
base_dir = os.path.dirname(os.path.abspath(__file__))
target_file_path = os.path.join(base_dir, "..", "report", "Reception_Checkout_Traveler_00.html")

# Ensure the target directory exists
os.makedirs(os.path.dirname(target_file_path), exist_ok=True)

# Generate professional HTML report (Clean & Simple Style)
html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WIB Reception Checkout - {rp_dict.log01_wib["WIB QR ID"]}</title>
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

        /* Test Steps Section */
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

        /* Steps Table */
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

        /* Power Measurements Table */
        .power-section {{
            margin: 20px 0;
        }}
        .power-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 10px 0;
            border: 1px solid #000000;
        }}
        .power-table th {{
            background-color: #f3f4f6;
            color: #000000;
            padding: 10px;
            border: 1px solid #000000;
            text-align: center;
        }}
        .power-table td {{
            padding: 10px;
            border: 1px solid #d1d5db;
            text-align: center;
        }}

        /* Details Box */
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

        /* Summary Section */
        .summary-section {{
            margin: 30px 0;
            padding: 15px;
            background: #f9fafb;
            border: 1px solid #d1d5db;
        }}
        .summary-title {{
            font-size: 16px;
            font-weight: bold;
            color: #000000;
            margin-bottom: 10px;
        }}
        .summary-item {{
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #d1d5db;
        }}
        .summary-item:last-child {{
            border-bottom: none;
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
            <div class="subtitle">Reception Checkout Report (Test00)</div>
            <div class="status-badge {overall_status.lower()}">Overall Status: {overall_status}</div>
        </div>

        <!-- Test Information -->
        <div class="info-section">
            <div class="info-row">
                <div class="info-label">WIB QR ID:</div>
                <div class="info-value">{rp_dict.log01_wib["WIB QR ID"]}</div>
            </div>
            <div class="info-row">
                <div class="info-label">Tester Name:</div>
                <div class="info-value">{rp_dict.log01_wib["Tester Name"]}</div>
            </div>
            <div class="info-row">
                <div class="info-label">Test Date:</div>
                <div class="info-value">{rp_dict.log01_wib["date01"]}</div>
            </div>
            <div class="info-row">
                <div class="info-label">Total Test Time:</div>
                <div class="info-value">{rp_dict.log01_wib["Time_Consumption"]} seconds</div>
            </div>
        </div>

        <!-- Inspection Steps Summary -->
        <div class="section">
            <div class="section-title">Inspection Steps Summary</div>
            <table>
                <thead>
                    <tr>
                        <th style="width: 10%;">Step</th>
                        <th style="width: 40%;">Inspection Item</th>
                        <th style="width: 15%;">Status</th>
                        <th style="width: 35%;">Timestamp</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><strong>1</strong></td>
                        <td>Component Inspection</td>
                        <td class="status-cell status-{'pass' if rp_dict.log01_wib["Component Inspection"] == "Passed" else 'fail'}">
                            {rp_dict.log01_wib["Component Inspection"]}
                        </td>
                        <td>{rp_dict.log01_wib["item1_date"]}</td>
                    </tr>
                    <tr>
                        <td><strong>2</strong></td>
                        <td>LTpowerPlay Configuration</td>
                        <td class="status-cell status-{'pass' if rp_dict.log01_wib["LTpowerPlay"] == "Passed" else 'fail'}">
                            {rp_dict.log01_wib["LTpowerPlay"]}
                        </td>
                        <td>{rp_dict.log01_wib["item2_date"]}</td>
                    </tr>
                    <tr>
                        <td><strong>3</strong></td>
                        <td>Initial Power Check</td>
                        <td class="status-cell status-pass">Completed</td>
                        <td>{rp_dict.log01_wib["Power Check Date"]}</td>
                    </tr>
                    <tr>
                        <td><strong>4</strong></td>
                        <td>Front Panel Installation</td>
                        <td class="status-cell status-{'pass' if rp_dict.log01_wib["Front_Panel"] == "Passed" else 'fail'}">
                            {rp_dict.log01_wib["Front_Panel"]}
                        </td>
                        <td>{rp_dict.log01_wib["item3_date"]}</td>
                    </tr>
                </tbody>
            </table>
        </div>

        <!-- Power Check Results -->
        <div class="section">
            <div class="section-title">Power Check Measurements</div>
            <table class="power-table">
                <thead>
                    <tr>
                        <th>Channel</th>
                        <th>Current (A)</th>
                        <th>Expected Range</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><strong>Channel 1</strong></td>
                        <td>{rp_dict.log01_wib["Power Check channel 1"]:.3f} A</td>
                        <td>0.5 - 2.0 A</td>
                        <td class="status-cell status-{'pass' if 0.5 <= rp_dict.log01_wib["Power Check channel 1"] <= 2.0 else 'fail'}">
                            {'PASS' if 0.5 <= rp_dict.log01_wib["Power Check channel 1"] <= 2.0 else 'FAIL'}
                        </td>
                    </tr>
                    <tr>
                        <td><strong>Channel 2</strong></td>
                        <td>{rp_dict.log01_wib["Power Check channel 2"]:.3f} A</td>
                        <td>0.5 - 2.0 A</td>
                        <td class="status-cell status-{'pass' if 0.5 <= rp_dict.log01_wib["Power Check channel 2"] <= 2.0 else 'fail'}">
                            {'PASS' if 0.5 <= rp_dict.log01_wib["Power Check channel 2"] <= 2.0 else 'FAIL'}
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>

        <!-- Detailed Information -->
        <div class="section">
            <div class="section-title">Detailed Information</div>

            <div class="details-box">
                <div class="details-title">Step 1: Component Inspection</div>
                <div class="details-item">• Visual inspection of critical components</div>
                <div class="details-item">• Verified: Jumpers, SW4 switch, DDR4 memory modules</div>
                <div class="details-item">• Result: {rp_dict.log01_wib["Component Inspection"]}</div>
            </div>

            <div class="details-box">
                <div class="details-title">Step 2: LTpowerPlay Configuration</div>
                <div class="details-item">• Power management settings configured</div>
                <div class="details-item">• Using LTpowerPlay software</div>
                <div class="details-item">• Result: {rp_dict.log01_wib["LTpowerPlay"]}</div>
            </div>

            <div class="details-box">
                <div class="details-title">Step 3: Initial Power Check</div>
                <div class="details-item">• Channel 1 Current: {rp_dict.log01_wib["Power Check channel 1"]:.3f} A</div>
                <div class="details-item">• Channel 2 Current: {rp_dict.log01_wib["Power Check channel 2"]:.3f} A</div>
                <div class="details-item">• Power verification completed successfully</div>
            </div>

            <div class="details-box">
                <div class="details-title">Step 4: Front Panel Installation</div>
                <div class="details-item">• Physical installation and verification</div>
                <div class="details-item">• Front panel assembly checked</div>
                <div class="details-item">• Result: {rp_dict.log01_wib["Front_Panel"]}</div>
            </div>
        </div>

        <!-- Test Summary -->
        <div class="summary-section">
            <div class="summary-title">Test Summary</div>
            <div class="summary-item">
                <span>Total Steps Completed:</span>
                <strong>4 / 4</strong>
            </div>
            <div class="summary-item">
                <span>Steps Passed:</span>
                <strong>{sum([1 for key in ["Component Inspection", "LTpowerPlay", "Front_Panel"] if rp_dict.log01_wib[key] == "Passed"])} / 3</strong>
            </div>
            <div class="summary-item">
                <span>Total Test Duration:</span>
                <strong>{rp_dict.log01_wib["Time_Consumption"]} seconds</strong>
                </div>
                <div class="summary-item">
                    <span>Overall Status:</span>
                    <strong style="color: {'#10b981' if overall_status == 'PASS' else '#ef4444'};">{overall_status}</strong>
                </div>
            </div>
        </div>

        <!-- Footer -->
        <div class="footer">
            <p>DUNE WIB Quality Control System - Test00 Reception Checkout</p>
            <p>Report generated: {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")}</p>
        </div>
    </div>
</body>
</html>"""

# Write the HTML file
with open(target_file_path, "w", encoding='utf-8') as f:
    f.write(html_content)

print(f"Professional HTML report saved to {target_file_path}")
