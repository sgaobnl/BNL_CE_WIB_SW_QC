import sys
import os

# Add the parent directory to sys.path so 'file' can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import file.report_dict as rp_dict
import datetime
from datetime import datetime, timezone

def fin_rep(item = 1, status = True):
    if item == 1:
        if status:
            rp_dict.log_fn_rp['item01'] = 'Item_01 Serial_TCP/IP_Communication Pass QC'
        else:
            rp_dict.log_fn_rp['item01'] = 'Item_01 Serial_TCP/IP_Communication QC Failed'

    if item == 2:
        if status:
            rp_dict.log_fn_rp['item02'] = 'Item_02 Calibration Path Control Pass QC'
        else:
            rp_dict.log_fn_rp['item02'] = 'Item_02 Calibration Path Control QC Failed'

    if item == 31:
        if status:
            rp_dict.log_fn_rp['item031'] = 'Item_0301 Power Rail Pass QC'
        else:
            rp_dict.log_fn_rp['item031'] = 'Item_0301 Power Rail QC Failed'

    if item == 32:
        if status:
            rp_dict.log_fn_rp['item032'] = 'Item_0302 Power Rail Pass QC'
        else:
            rp_dict.log_fn_rp['item032'] = 'Item_0302 Power Rail QC Failed'
    if item == 33:
        if status:
            rp_dict.log_fn_rp['item033'] = 'Item_0303 Power Rail Pass QC'
        else:
            rp_dict.log_fn_rp['item033'] = 'Item_0303 Power Rail QC Failed'
    if item == 34:
        if status:
            rp_dict.log_fn_rp['item034'] = 'Item_0304 Power Rail Pass QC'
        else:
            rp_dict.log_fn_rp['item034'] = 'Item_0304 Power Rail QC Failed'

    if item == 41:
        if status:
            rp_dict.log_fn_rp['item041'] = 'Item_041 WIB FEMB Pulse Pass QC'
        else:
            rp_dict.log_fn_rp['item041'] = 'Item_041 WIB FEMB Pulse QC Failed'
    if item == 42:
        if status:
            rp_dict.log_fn_rp['item042'] = 'Item_042 WIB FEMB Pulse Pass QC'
        else:
            rp_dict.log_fn_rp['item042'] = 'Item_042 WIB FEMB Pulse QC Failed'
    if item == 43:
        if status:
            rp_dict.log_fn_rp['item043'] = 'Item_043 WIB FEMB Pulse Pass QC'
        else:
            rp_dict.log_fn_rp['item043'] = 'Item_043 WIB FEMB Pulse QC Failed'
    if item == 44:
        if status:
            rp_dict.log_fn_rp['item044'] = 'Item_044 WIB FEMB Pulse Pass QC'
        else:
            rp_dict.log_fn_rp['item044'] = 'Item_044 WIB FEMB Pulse QC Failed'

    if item == 51:
        if status:
            rp_dict.log_fn_rp['item051'] = 'Item_05 I2C Device Access Pass QC'
        else:
            rp_dict.log_fn_rp['item051'] = 'Item_05 I2C Device Access QC Failed'
    if item == 52:
        if status:
            rp_dict.log_fn_rp['item052'] = 'Item_05 I2C Device Access Pass QC'
        else:
            rp_dict.log_fn_rp['item052'] = 'Item_05 I2C Device Access QC Failed'

    if item == 6:
        if status:
            rp_dict.log_fn_rp['item06'] = 'Item_06 PTB Interface Pass QC'
        else:
            rp_dict.log_fn_rp['item06'] = 'Item_06 PTB Interface QC Failed'

    if item == 7:
        if status:
            rp_dict.log_fn_rp['item07'] = 'Item_07 IBERT Pass QC'
        else:
            rp_dict.log_fn_rp['item07'] = 'Item_07 IBERT QC Failed'

fin_rep(item=1, status=True)
fin_rep(item=2, status=True)
fin_rep(item=31, status=True)
fin_rep(item=32, status=True)
fin_rep(item=33, status=True)
fin_rep(item=34, status=True)
fin_rep(item=41, status=True)
fin_rep(item=42, status=True)
fin_rep(item=43, status=True)
fin_rep(item=44, status=True)
fin_rep(item=51, status=True)
fin_rep(item=52, status=True)
fin_rep(item=6, status=True)
fin_rep(item=7, status=True)

# === Setup relative path to ../report/final_report.html ===
base_dir = os.path.dirname(os.path.abspath(__file__))
target_file_path = os.path.join(base_dir, "..", "report", "final_report.html")
rp_dict.log01_wib['date01'] = datetime.now(timezone.utc)
rp_dict.log01_wib['WIB QR ID'] = '1750-1F-000016'
rp_dict.log01_wib['Tester Name'] = 'lke'
# Ensure target directory exists
os.makedirs(os.path.dirname(target_file_path), exist_ok=True)
# Always create new file (overwrite if exists)
with open(target_file_path, "w") as f:
    f.write('<!DOCTYPE html>\n')
    f.write('<html lang="en">\n')
    f.write('<head>\n')
    f.write('    <meta charset="UTF-8">\n')
    f.write('    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n')
    f.write('    <title>WIB QC Test Report</title>\n')
    f.write('    <style>\n')
    f.write('        body { font-family: Arial, sans-serif; margin: 40px; }\n')
    f.write('        h2 { color: #333; }\n')
    f.write('        h4 { color: #555; margin: 10px 0; }\n')
    f.write('        h3 { margin: 15px 0; }\n')
    f.write('        a { color: #0066cc; text-decoration: none; }\n')
    f.write('        a:hover { text-decoration: underline; }\n')
    f.write('        .pass { color: green; }\n')
    f.write('        .fail { color: red; }\n')
    f.write('    </style>\n')
    f.write('</head>\n')
    f.write('<body>\n')
    f.write('    <h2>Warm Interface Board QC Test</h2>\n')
    f.write('    <h4>WIB QR ID:&nbsp;&nbsp;&nbsp;&nbsp;' + str(rp_dict.log01_wib['WIB QR ID']) + '</h4>\n')
    f.write('    <h4>Tester Name:&nbsp;&nbsp;&nbsp;&nbsp;' + str(rp_dict.log01_wib['Tester Name']) + '</h4>\n')
    f.write('    <h4>Date:&nbsp;&nbsp;&nbsp;&nbsp;' + str(rp_dict.log01_wib['date01']) + '</h4>\n')
    f.write('    <h3>{} <a href="{}">[detail]</a></h3>\n'.format(rp_dict.log_fn_rp['item01'], rp_dict.report_paths['item01']))
    f.write('    <h3>{} <a href="{}">[detail]</a></h3>\n'.format(rp_dict.log_fn_rp['item02'], rp_dict.report_paths['item02']))
    f.write('    <h3>{} <a href="{}">[detail]</a></h3>\n'.format(rp_dict.log_fn_rp['item031'], rp_dict.report_paths['item031']))
    f.write('    <h3>{} <a href="{}">[detail]</a></h3>\n'.format(rp_dict.log_fn_rp['item032'], rp_dict.report_paths['item032']))
    f.write('    <h3>{} <a href="{}">[detail]</a></h3>\n'.format(rp_dict.log_fn_rp['item033'], rp_dict.report_paths['item033']))
    f.write('    <h3>{} <a href="{}">[detail]</a></h3>\n'.format(rp_dict.log_fn_rp['item034'], rp_dict.report_paths['item034']))
    f.write('    <h3>{} <a href="{}">[detail]</a></h3>\n'.format(rp_dict.log_fn_rp['item041'], rp_dict.report_paths['item041']))
    f.write('    <h3>{} <a href="{}">[detail]</a></h3>\n'.format(rp_dict.log_fn_rp['item042'], rp_dict.report_paths['item042']))
    f.write('    <h3>{} <a href="{}">[detail]</a></h3>\n'.format(rp_dict.log_fn_rp['item043'], rp_dict.report_paths['item043']))
    f.write('    <h3>{} <a href="{}">[detail]</a></h3>\n'.format(rp_dict.log_fn_rp['item044'], rp_dict.report_paths['item044']))
    f.write('    <h3>{} <a href="{}">[detail]</a></h3>\n'.format(rp_dict.log_fn_rp['item051'], rp_dict.report_paths['item051']))
    f.write('    <h3>{} <a href="{}">[detail]</a></h3>\n'.format(rp_dict.log_fn_rp['item052'], rp_dict.report_paths['item052']))
    f.write('    <h3>{} <a href="{}">[detail]</a></h3>\n'.format(rp_dict.log_fn_rp['item06'], rp_dict.report_paths['item06']))
    f.write('    <h3>{} <a href="{}">[detail]</a></h3>\n'.format(rp_dict.log_fn_rp['item07'], rp_dict.report_paths['item07']))
    f.write('</body>\n')
    f.write('</html>\n')


print(f"HTML report saved to {target_file_path}")