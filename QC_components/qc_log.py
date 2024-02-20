from collections import defaultdict

report_log00 = defaultdict(dict)    # input information
test_label = []
#   01  Power Consumption
report_log01 = defaultdict(dict)    # input information
check_log01 = defaultdict(dict)    # input information
#   SE OFF
report_log01_11 = defaultdict(dict)
report_log01_12 = defaultdict(dict)
report_log01_13 = defaultdict(dict)
check_log01_11 = defaultdict(dict)
check_log01_12 = defaultdict(dict)
check_log01_13 = defaultdict(dict)
#   SE ON
report_log01_21 = defaultdict(dict)
report_log01_22 = defaultdict(dict)
report_log01_23 = defaultdict(dict)
check_log01_21 = defaultdict(dict)
check_log01_22 = defaultdict(dict)
check_log01_23 = defaultdict(dict)
#   DIFF (SEDC)
report_log01_31 = defaultdict(dict)
report_log01_32 = defaultdict(dict)
report_log01_33 = defaultdict(dict)
check_log01_31 = defaultdict(dict)
check_log01_32 = defaultdict(dict)
check_log01_33 = defaultdict(dict)

# 03
item3 = "Leakage_Current"
report_log03_01 = defaultdict(dict)    # input information
report_log03_02 = defaultdict(dict)    # input information
report_log03_03 = defaultdict(dict)    # input information
report_log03_04 = defaultdict(dict)    # input information
check_log03_01 = defaultdict(dict)    # input information
check_log03_02 = defaultdict(dict)    # input information
check_log03_03 = defaultdict(dict)    # input information
check_log03_04 = defaultdict(dict)    # input information

check_log03_table_01 = defaultdict(dict)    # input information
report_log3 = [report_log03_01, report_log03_02, report_log03_03, report_log03_04]

# 04
item04 = "CHK"
report_log04_01 = defaultdict(dict)    # input information
report_log04_02 = defaultdict(dict)    # input information
report_log04_03 = defaultdict(dict)    # input information
report_log04_04 = defaultdict(dict)    # input information
report_log04_05 = defaultdict(dict)    # input information
report_log04_06 = defaultdict(dict)    # input information
check_log04_01 = defaultdict(dict)    # input information
check_log04_02 = defaultdict(dict)    # input information
check_log04_03 = defaultdict(dict)    # input information
check_log04_04 = defaultdict(dict)    # input information
check_log04_05 = defaultdict(dict)    # input information
check_log04_06 = defaultdict(dict)    # input information

check_log04_table_01 = defaultdict(dict)
check_log04_table_02 = defaultdict(dict)
check_log04_table_03 = defaultdict(dict)
check_log04_table_04 = defaultdict(dict)
check_log04_table_05 = defaultdict(dict)
check_log04_table_06 = defaultdict(dict)

report_log04_07 = defaultdict(dict)    # input information
report_log04_08 = defaultdict(dict)    # input information
report_log04_09 = defaultdict(dict)    # input information
report_log04_10 = defaultdict(dict)    # input information
report_log04_11 = defaultdict(dict)    # input information
report_log04_12 = defaultdict(dict)    # input information
report_log04_13 = defaultdict(dict)    # input information
report_log04_14 = defaultdict(dict)    # input information
report_log04_15 = defaultdict(dict)    # input information
report_log04_16 = defaultdict(dict)    # input information
report_log4 = [report_log04_01, report_log04_02, report_log04_03, report_log04_04, report_log04_05, report_log04_06]

# 05
item05 = "RMS"
report_log05_result = defaultdict(dict)
report_log05_fin_result = False
report_log05_tablecell = defaultdict(dict)
report_log05_table = defaultdict(dict)
report_log05_table2 = defaultdict(dict)
report_log051_pulse = defaultdict(dict)
report_log052_pedestal = defaultdict(dict)
report_log054_pedestal_issue = defaultdict(dict)
report_log053_rms = defaultdict(dict)
report_log055_rms_issue = defaultdict(dict)
report_log059_rms_table_log = defaultdict(dict)

# 06
report_log06 = defaultdict(dict)    # input information
item061 = "CALI1"
item062 = "CALI1_DIFF"

# 07
report_log07 = defaultdict(dict)    # input information
item071 = "CALI2"
item072 = "CALI2_DIFF"

# 10
item10 = "MON_FE"
report_log10_01 = defaultdict(dict)
report_log10_02 = defaultdict(dict)
report_log10_03 = defaultdict(dict)
report_log10_04 = defaultdict(dict)
report_log10_05 = defaultdict(dict)
report_log10_06 = defaultdict(dict)

mon_pulse = defaultdict(dict)

# 11
item11 = "MON_FE"
report_log11_01 = defaultdict(dict)

# 12
item12 = "MON_ADC"
ADCMON_table_cell = defaultdict(dict)
ADCMON_table = defaultdict(dict)

# 15
item15 = "ADC_SYNC_PAT"
# ADCMON_table_cell = defaultdict(dict)
# ADCMON_table = defaultdict(dict)

chkflag = defaultdict(dict)    # input information
badlist = defaultdict(dict)    # input information
tmp_log = defaultdict(dict)
check_log = defaultdict(dict)
tmp_pulse = defaultdict(dict)



# 06 calibration
channel0_pulse = defaultdict(dict)

