from collections import defaultdict

log_fn_rp = defaultdict(dict)

# 00
# Initial Information
Test_site_d = defaultdict(dict)
Test_name_d = defaultdict(dict)
Test_WIB_ID_d = defaultdict(dict)
wib_info = defaultdict(dict)

# Global CSV Manager instance (initialized in Test00)
csv_manager = None




# 01 Checkout Test
log01_wib = defaultdict(dict)

# 02 Communication
log02_wib = defaultdict(dict)








# 03    Power Rail Test
log03_femb_slot0 = defaultdict(dict)
log03_femb_slot1 = defaultdict(dict)
log03_femb_slot2 = defaultdict(dict)
log03_femb_slot3 = defaultdict(dict)

# 04 wib power rail
log04_wib = defaultdict(dict)

# 05    calibration
log05_Cal = defaultdict(dict)

# 06    PTB Interface I2C Test
log06_PTB = defaultdict(dict)

# 07    IBERT
log07_ibert = defaultdict(dict)

# Report paths for final report integration
# These will be set by each test module when they complete
report_paths = defaultdict(dict)
# Initialize with default relative paths (will be in report/ folder)
report_paths['item01'] = 'WIB_01_communication_report_01.html'
report_paths['item02'] = 'WIB_02_Calibration_report_02.html'
report_paths['item031'] = 'WIB_03_1V_power_report.html'
report_paths['item032'] = 'WIB_03_2V_power_report.html'
report_paths['item033'] = 'WIB_03_3V_power_report.html'
report_paths['item034'] = 'WIB_03_4V_power_report.html'
report_paths['item041'] = ''  # Will be set by Test0400
report_paths['item042'] = ''  # Will be set by Test0401
report_paths['item043'] = ''  # Will be set by Test0402
report_paths['item044'] = ''  # Will be set by Test0403
report_paths['item051'] = 'WIB_05_I2C_Device_report_051.html'
report_paths['item052'] = 'WIB_052_I2C_Sensor_Info.html'
report_paths['item06'] = 'WIB_06_PTB_Interface.html'
report_paths['item07'] = 'WIB_07_WIB_IBERT.html'

def set_report_path(item_key, path):
    """Set the report path for a test item. Path should be relative to report/ folder."""
    report_paths[item_key] = path

