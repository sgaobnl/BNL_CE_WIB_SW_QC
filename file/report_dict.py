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

