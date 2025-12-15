import time
import sys
import os

# Add the parent directory to sys.path so 'function' can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Now it's safe to import from 'function'
# from function.rigol_dp832_ps import RIGOL_PS_CTL
import function.Rigol_DP800 as rigol
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
utc_time = datetime.now(timezone.utc)
rp_dict.log01_wib['WIB QR ID'] = Test_WIB_ID_d
rp_dict.log01_wib['Tester Name'] = Test_name_d
rp_dict.log01_wib['date01'] = utc_time.strftime("%Y-%m-%d %H:%M:%S UTC")



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
else:
    rp_dict.log01_wib['Component Inspection'] = 'Passed'
utc_time = datetime.now(timezone.utc)
rp_dict.log01_wib['item1_date'] = utc_time.strftime("%Y-%m-%d %H:%M:%S UTC")

# print('Insert SD card')
item2 = input('Use LTpowerPlay configure the Power Rail')
if item2 == 'n' or item2 == 'N':
    rp_dict.log01_wib['LTpowerPlay'] = 'Failed'
else:
    rp_dict.log01_wib['LTpowerPlay'] = 'Passed'
utc_time = datetime.now(timezone.utc)
rp_dict.log01_wib['item2_date'] = utc_time.strftime("%Y-%m-%d %H:%M:%S UTC")

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
v2, c2 = psu.measure(1)
# v2, i2 = psu.measure(2)

# c1 = fm_ps.measure_params(channel = 1)
# c2 = fm_ps.measure_params(channel = 2)
print(v1, c1)
print(v2, c2)
time.sleep(3)
psu.close()

rp_dict.log01_wib['Power Check channel 1'] = c1
rp_dict.log01_wib['Power Check channel 2'] = c2
utc_time = datetime.now(timezone.utc)
rp_dict.log01_wib['Power Check Date'] = utc_time.strftime("%Y-%m-%d %H:%M:%S UTC")


item3 = input('Install Front Panel')
if item3 == 'n' or item3 == 'N':
    rp_dict.log01_wib['Front_Panel'] = 'Failed'
else:
    rp_dict.log01_wib['Front_Panel'] = 'Passed'
utc_time = datetime.now(timezone.utc)
rp_dict.log01_wib['item3_date'] = utc_time.strftime("%Y-%m-%d %H:%M:%S UTC")

t2 = time.time()

rp_dict.log01_wib['Time_Consumption'] = round((t2-t1), 2)

















# === Setup relative path to ../file/power_report.md ===
import os

# Define the path to the output HTML file
base_dir = os.path.dirname(os.path.abspath(__file__))
target_file_path = os.path.join(base_dir, "..", "report", "Reception_Checkout_Traveler_00.html")

# Ensure the target directory exists
os.makedirs(os.path.dirname(target_file_path), exist_ok=True)

# Start writing the HTML file (overwrite if exists)
with open(target_file_path, "w") as f:
    f.write('<!DOCTYPE html>\n')
    f.write('<html lang="en">\n')
    f.write('<head>\n')
    f.write('    <meta charset="UTF-8">\n')
    f.write('    <title>WIB Reception Checkout</title>\n')
    f.write('    <style>\n')
    f.write('        body { font-family: Arial, sans-serif; line-height: 1.6; margin: 40px; }\n')
    f.write('        h2, h3, h4 { margin-bottom: 0.3em; }\n')
    f.write('        .section { margin-bottom: 30px; }\n')
    f.write('        .label { font-weight: bold; }\n')
    f.write('        .value { margin-left: 20px; }\n')
    f.write('    </style>\n')
    f.write('</head>\n')
    f.write('<body>\n\n')

    f.write('<h2>WIB Reception Checkout</h2>\n\n')

    f.write('<div class="section">\n')
    f.write(f'    <h4><span class="label">WIB QR ID:</span> <span class="value">{rp_dict.log01_wib["WIB QR ID"]}</span></h4>\n')
    f.write(f'    <h4><span class="label">Tester Name:</span> <span class="value">{rp_dict.log01_wib["Tester Name"]}</span></h4>\n')
    f.write(f'    <h4><span class="label">Date:</span> <span class="value">{rp_dict.log01_wib["date01"]}</span></h4>\n')
    f.write('</div>\n\n')

    f.write('<div class="section">\n')
    f.write('    <h3>Component Inspection</h3>\n')
    f.write(f'    <h4><span class="label">Check Jumper, SW4, DDR4:</span> <span class="value">{rp_dict.log01_wib["Component Inspection"]}</span></h4>\n')
    f.write(f'    <h4><span class="label">Date:</span> <span class="value">{rp_dict.log01_wib["item1_date"]}</span></h4>\n')
    f.write('</div>\n\n')

    f.write('<div class="section">\n')
    f.write('    <h3>LTpowerPlay Power Configure</h3>\n')
    f.write(f'    <h4><span class="label">LTpowerPlay Config:</span> <span class="value">{rp_dict.log01_wib["LTpowerPlay"]}</span></h4>\n')
    f.write(f'    <h4><span class="label">Date:</span> <span class="value">{rp_dict.log01_wib["item2_date"]}</span></h4>\n')
    f.write('</div>\n\n')

    f.write('<div class="section">\n')
    f.write('    <h3>Initial Power Check</h3>\n')
    f.write(f'    <h4><span class="label">Power Check:</span> <span class="value">{rp_dict.log01_wib["Power Check channel 1"]}</span></h4>\n')
    f.write(f'    <h4><span class="label">Power Check:</span> <span class="value">{rp_dict.log01_wib["Power Check channel 2"]}</span></h4>\n')
    f.write(f'    <h4><span class="label">Date:</span> <span class="value">{rp_dict.log01_wib["Power Check Date"]}</span></h4>\n')
    f.write('</div>\n\n')

    f.write('<div class="section">\n')
    f.write('    <h3>Install Front Panel</h3>\n')
    f.write(f'    <h4><span class="label">Front Panel:</span> <span class="value">{rp_dict.log01_wib["Front_Panel"]}</span></h4>\n')
    f.write(f'    <h4><span class="label">Date:</span> <span class="value">{rp_dict.log01_wib["item3_date"]}</span></h4>\n')
    f.write('</div>\n\n')

    f.write('<div class="section">\n')
    f.write('    <h3>Time Consumption</h3>\n')
    f.write(f'    <h4><span class="value">{rp_dict.log01_wib["Time_Consumption"]} s</span></h4>\n')
    f.write('</div>\n\n')

    f.write('</body>\n</html>\n')

print(f"HTML file saved (new file) to {target_file_path}")
