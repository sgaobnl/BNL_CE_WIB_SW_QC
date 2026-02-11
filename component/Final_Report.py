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

# === Setup relative path to ../file/power_report.md ===
base_dir = os.path.dirname(os.path.abspath(__file__))
target_file_path = os.path.join(base_dir, "..", "file", "final_report.md")
rp_dict.log01_wib['date01'] = datetime.now(timezone.utc)
rp_dict.log01_wib['WIB QR ID'] = '1750-1F-000016'
rp_dict.log01_wib['Tester Name'] = 'lke'
# Ensure target directory exists
os.makedirs(os.path.dirname(target_file_path), exist_ok=True)
# Always create new file (overwrite if exists)
with open(target_file_path, "w") as f:
    f.write('## Warm Interface Board QC Test' + '\n\n')
    f.write('#### WIB QR ID:&nbsp;&nbsp;&nbsp;&nbsp;' + rp_dict.log01_wib['WIB QR ID'].__str__() + '\n\n')
    f.write('#### Tester Name:&nbsp;&nbsp;&nbsp;&nbsp;' + rp_dict.log01_wib['Tester Name'].__str__() + '\n\n')
    f.write('#### Date:&nbsp;&nbsp;&nbsp;&nbsp;' + rp_dict.log01_wib['date01'].__str__() + '\n\n')
    f.write('### {}'.format(rp_dict.log_fn_rp['item01']) + ' [detail](WIB_01_communication_report_01.html)' + '\n\n')
    f.write('### {}'.format(rp_dict.log_fn_rp['item02']) + ' [detail](WIB_02_Calibration_report_02.html)' + '\n\n')
    f.write('### {}'.format(rp_dict.log_fn_rp['item031']) + ' [detail](WIB_03_1V_power_report.html)' + '\n\n')
    f.write('### {}'.format(rp_dict.log_fn_rp['item032']) + ' [detail](WIB_03_2V_power_report.html)' + '\n\n')
    f.write('### {}'.format(rp_dict.log_fn_rp['item033']) + ' [detail](WIB_03_3V_power_report.html)' + '\n\n')
    f.write('### {}'.format(rp_dict.log_fn_rp['item034']) + ' [detail](WIB_03_4V_power_report.html)' + '\n\n')
    f.write('### {}'.format(rp_dict.log_fn_rp['item041']) + ' [detail](D:/WIB_QC/DUNE_WIB_QC_Script/report/WIB_to_FEMB_slot_00_power_reportFEMB0_RT_0pF/result.pdf)' + '\n\n')
    f.write('### {}'.format(rp_dict.log_fn_rp['item042']) + ' [detail](D:/WIB_QC/DUNE_WIB_QC_Script/report/WIB_to_FEMB_slot_01_power_reportFEMB1_RT_0pF/result.pdf)' + '\n\n')
    f.write('### {}'.format(rp_dict.log_fn_rp['item043']) + ' [detail](D:/WIB_QC/DUNE_WIB_QC_Script/report/WIB_to_FEMB_slot_02_power_reportFEMB2_RT_0pF/result.pdf)' + '\n\n')
    f.write('### {}'.format(rp_dict.log_fn_rp['item044']) + ' [detail](D:/WIB_QC/DUNE_WIB_QC_Script/report/WIB_to_FEMB_slot_03_power_reportFEMB3_RT_0pF/result.pdf)' + '\n\n')
    f.write('### {}'.format(rp_dict.log_fn_rp['item051']) + ' [detail](WIB_05_I2C_Device_report_051.html)' + '\n\n')
    f.write('### {}'.format(rp_dict.log_fn_rp['item052']) + ' [detail](WIB_052_WIB_Power_report_052.html)' + '\n\n')
    f.write('### {}'.format(rp_dict.log_fn_rp['item06']) + ' [detail](WIB_06_PTB_Interface.html)' + '\n\n')
    f.write('### {}'.format(rp_dict.log_fn_rp['item07']) + ' [detail](WIB_07_WIB_IBERT.html)' + '\n\n')


print(f"Markdown table saved (new file) to {target_file_path}")