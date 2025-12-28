from collections import defaultdict
top_path = defaultdict(dict)
report_log00 = defaultdict(dict)    # input information
test_label = []
#   01  Power Consumption
report_log01 = defaultdict(dict)    # input information
check_log01 = defaultdict(dict)    # input information
power_meas={"BIAS_V":[],"LArASIC_V":[],"ColdADC_V":[],"COLDATA_V":[],"BIAS_I":[],"LArASIC_I":[],"ColdADC_I":[],"COLDATA_I":[]}

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

#   02  Power Cycle
check_log02_01 = defaultdict(dict)
check_log02_02 = defaultdict(dict)
check_log02_03 = defaultdict(dict)
check_log02_04 = defaultdict(dict)
check_log02_05 = defaultdict(dict)

tmp_log02_01 = defaultdict(dict)
tmp_log02_02 = defaultdict(dict)
tmp_log02_03 = defaultdict(dict)
tmp_log02_04 = defaultdict(dict)
tmp_log02_05 = defaultdict(dict)
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
report_log04_01_4705 = defaultdict(dict)    # input information
report_log04_01_4710 = defaultdict(dict)    # input information
report_log04_01_4720 = defaultdict(dict)    # input information
report_log04_01_4730 = defaultdict(dict)    # input information
report_log04_01_7805 = defaultdict(dict)    # input information
report_log04_01_7810 = defaultdict(dict)    # input information
report_log04_01_7820 = defaultdict(dict)    # input information
report_log04_01_7830 = defaultdict(dict)    # input information
report_log04_01_1405 = defaultdict(dict)    # input information
report_log04_01_1410 = defaultdict(dict)    # input information
report_log04_01_1420 = defaultdict(dict)    # input information
report_log04_01_1430 = defaultdict(dict)    # input information
report_log04_01_2505 = defaultdict(dict)    # input information
report_log04_01_2510 = defaultdict(dict)    # input information
report_log04_01_2520 = defaultdict(dict)    # input information
report_log04_01_2530 = defaultdict(dict)    # input information

check_log04_01 = defaultdict(dict)    # input information
check_log04_01_4705 = defaultdict(dict)    # input information
check_log04_01_4710 = defaultdict(dict)    # input information
check_log04_01_4720 = defaultdict(dict)    # input information
check_log04_01_4730 = defaultdict(dict)    # input information
check_log04_01_7805 = defaultdict(dict)    # input information
check_log04_01_7810 = defaultdict(dict)    # input information
check_log04_01_7820 = defaultdict(dict)    # input information
check_log04_01_7830 = defaultdict(dict)    # input information
check_log04_01_1405 = defaultdict(dict)    # input information
check_log04_01_1410 = defaultdict(dict)    # input information
check_log04_01_1420 = defaultdict(dict)    # input information
check_log04_01_1430 = defaultdict(dict)    # input information
check_log04_01_2505 = defaultdict(dict)    # input information
check_log04_01_2510 = defaultdict(dict)    # input information
check_log04_01_2520 = defaultdict(dict)    # input information
check_log04_01_2530 = defaultdict(dict)    # input information

report_log04_02_4705 = defaultdict(dict)    # input information
report_log04_02_4710 = defaultdict(dict)    # input information
report_log04_02_4720 = defaultdict(dict)    # input information
report_log04_02_4730 = defaultdict(dict)    # input information
report_log04_02_7805 = defaultdict(dict)    # input information
report_log04_02_7810 = defaultdict(dict)    # input information
report_log04_02_7820 = defaultdict(dict)    # input information
report_log04_02_7830 = defaultdict(dict)    # input information
report_log04_02_1405 = defaultdict(dict)    # input information
report_log04_02_1410 = defaultdict(dict)    # input information
report_log04_02_1420 = defaultdict(dict)    # input information
report_log04_02_1430 = defaultdict(dict)    # input information
report_log04_02_2505 = defaultdict(dict)    # input information
report_log04_02_2510 = defaultdict(dict)    # input information
report_log04_02_2520 = defaultdict(dict)    # input information
report_log04_02_2530 = defaultdict(dict)    # input information

check_log04_02_4705 = defaultdict(dict)    # input information
check_log04_02_4710 = defaultdict(dict)    # input information
check_log04_02_4720 = defaultdict(dict)    # input information
check_log04_02_4730 = defaultdict(dict)    # input information
check_log04_02_7805 = defaultdict(dict)    # input information
check_log04_02_7810 = defaultdict(dict)    # input information
check_log04_02_7820 = defaultdict(dict)    # input information
check_log04_02_7830 = defaultdict(dict)    # input information
check_log04_02_1405 = defaultdict(dict)    # input information
check_log04_02_1410 = defaultdict(dict)    # input information
check_log04_02_1420 = defaultdict(dict)    # input information
check_log04_02_1430 = defaultdict(dict)    # input information
check_log04_02_2505 = defaultdict(dict)    # input information
check_log04_02_2510 = defaultdict(dict)    # input information
check_log04_02_2520 = defaultdict(dict)    # input information
check_log04_02_2530 = defaultdict(dict)    # input information


report_log04_03_4720 = defaultdict(dict)
report_log04_03_7820 = defaultdict(dict)
report_log04_03_1420 = defaultdict(dict)
report_log04_03_2520 = defaultdict(dict)

check_log04_03_4720 = defaultdict(dict)
check_log04_03_7820 = defaultdict(dict)
check_log04_03_1420 = defaultdict(dict)
check_log04_03_2520 = defaultdict(dict)

report_log04_04_14201 = defaultdict(dict)
report_log04_04_14202 = defaultdict(dict)
report_log04_04_14203 = defaultdict(dict)
report_log04_04_14204 = defaultdict(dict)
report_log04_04_14205 = defaultdict(dict)
report_log04_04_14206 = defaultdict(dict)

report_log04_05_14201 = defaultdict(dict)
report_log04_05_14202 = defaultdict(dict)
report_log04_05_14203 = defaultdict(dict)

check_log04_04_14201 = defaultdict(dict)
check_log04_04_14202 = defaultdict(dict)
check_log04_04_14203 = defaultdict(dict)
check_log04_04_14204 = defaultdict(dict)
check_log04_04_14205 = defaultdict(dict)
check_log04_04_14206 = defaultdict(dict)


check_log04_05_14201 = defaultdict(dict)
check_log04_05_14202 = defaultdict(dict)
check_log04_05_14203 = defaultdict(dict)

report_log04_02 = defaultdict(dict)    # input information
report_log04_03 = defaultdict(dict)    # input information
report_log04_04 = defaultdict(dict)    # input information
report_log04_05 = defaultdict(dict)    # input information
report_log04_06 = defaultdict(dict)    # input information

check_log04_02 = defaultdict(dict)    # input information
check_log04_03 = defaultdict(dict)    # input information
check_log04_04 = defaultdict(dict)    # input information
check_log04_05 = defaultdict(dict)    # input information
check_log04_06 = defaultdict(dict)    # input information

report_log046_fembbbl = defaultdict(dict)
report_log047_fembbblstd = defaultdict(dict)

check_log04_table_01 = defaultdict(dict)
check_log04_table_02 = defaultdict(dict)
check_log04_table_03 = defaultdict(dict)
check_log04_table_04 = defaultdict(dict)
check_log04_table_05 = defaultdict(dict)
check_log04_table_06 = defaultdict(dict)

# 05
item05 = "RMS"
report_log0500 = defaultdict(dict)
report_log05_result = defaultdict(dict)
report_log05_fin_result = False
report_log05_tablecell = defaultdict(dict)
report_log05_table = defaultdict(dict)
report_log05_table2 = defaultdict(dict)
report_log051_pulse = defaultdict(dict)
report_log052_pedestal = defaultdict(dict)
report_log054_pedestal_issue = defaultdict(dict)
report_log053_rms = defaultdict(dict)
report_log057_rmsfemb = defaultdict(dict)
report_log055_rms_issue = defaultdict(dict)
report_log056_fembrms = defaultdict(dict)
report_log057_fembrmsmean = defaultdict(dict)
report_log057_fembrmsstd = defaultdict(dict)
report_log057_fembrmsmax = defaultdict(dict)
report_log057_fembrmsmin = defaultdict(dict)
report_log057_fembrms = defaultdict(dict)
report_log059_rms_table_log = defaultdict(dict)

# 06
report_log06 = defaultdict(dict)    # input information
item061 = "CALI1"
item062 = "CALI1_DIFF"

tmp_log = defaultdict(dict)
csv_log = defaultdict(dict)
report_log0601 = defaultdict(dict)  # SE 200 mV 4.7 mV INL
report_log0601csvgain = defaultdict(dict)  # SE 200 mV 4.7 mV INL
report_log0601csvinl = defaultdict(dict)  # SE 200 mV 4.7 mV INL
report_log0601csvlinerange = defaultdict(dict)  # SE 200 mV 4.7 mV INL
report_log0602 = defaultdict(dict)  # SE 200 mV 7.8 mV INL
report_log0602csvgain = defaultdict(dict)  # SE 200 mV 4.7 mV INL
report_log0602csvinl = defaultdict(dict)  # SE 200 mV 4.7 mV INL
report_log0602csvlinerange = defaultdict(dict)  # SE 200 mV 4.7 mV INL
report_log0603 = defaultdict(dict)  # SE 200 mV 14 mV INL
report_log0603csv = defaultdict(dict)  # SE 200 mV 14 mV INL
report_log0604 = defaultdict(dict)  # SE 200 mV 25 mV INL
report_log0604csvgain = defaultdict(dict)  # SE 200 mV 4.7 mV INL
report_log0604csvinl = defaultdict(dict)  # SE 200 mV 4.7 mV INL
report_log0604csvlinerange = defaultdict(dict)  # SE 200 mV 4.7 mV INL
report_log0605 = defaultdict(dict)  # DIFF 200 mV 25 mV INL

check_log0601 = defaultdict(dict)  # SE 200 mV 4.7 mV INL
check_log0602 = defaultdict(dict)  # SE 200 mV 7.8 mV INL
check_log0603 = defaultdict(dict)  # SE 200 mV 14 mV INL
report_log0603csvgain = defaultdict(dict)  # SE 200 mV 14 mV INL
report_log0603csvinl = defaultdict(dict)  # SE 200 mV 14 mV INL
report_log0603csvlinerange = defaultdict(dict)  # SE 200 mV 14 mV INL
check_log0604 = defaultdict(dict)  # SE 200 mV 25 mV INL
check_log0605 = defaultdict(dict)  # DIFF 200 mV 25 mV INL
# 07
report_log07 = defaultdict(dict)    # input information
item071 = "CALI2"
item072 = "CALI2_DIFF"

report_log0701 = defaultdict(dict)  # SE 200 mV 4.7 mV INL
report_log0702 = defaultdict(dict)  # SE 200 mV 7.8 mV INL

check_log0701 = defaultdict(dict)  # SE 200 mV 4.7 mV INL
report_log0701csvgain = defaultdict(dict)
report_log0701csvinl = defaultdict(dict)
report_log0701csvlinerange = defaultdict(dict)

check_log0702 = defaultdict(dict)  # SE 200 mV 7.8 mV INL

report_log07_fin_result = defaultdict(dict)

# 08
report_log08 = defaultdict(dict)    # input information
item081 = "CALI3"
item082 = "CALI3_DIFF"

report_log0801 = defaultdict(dict)  # SE 200 mV 4.7 mV INL
report_log0801csvgain = defaultdict(dict)
report_log0801csvinl = defaultdict(dict)
report_log0801csvlinerange = defaultdict(dict)
report_log0802 = defaultdict(dict)  # SE 200 mV 7.8 mV INL

check_log0801 = defaultdict(dict)  # SE 200 mV 4.7 mV INL
check_log0802 = defaultdict(dict)  # SE 200 mV 7.8 mV INL

report_log08_fin_result = defaultdict(dict)

# 09
report_log09 = defaultdict(dict)    # input information
report_log0901csvgain = defaultdict(dict)
report_log0901csvinl = defaultdict(dict)
report_log0901csvlinerange = defaultdict(dict)
item091 = "CALI4"
item092 = "CALI4_DIFF"

report_log0901 = defaultdict(dict)  # SE 200 mV 4.7 mV INL
report_log0902 = defaultdict(dict)  # SE 200 mV 7.8 mV INL

check_log0901 = defaultdict(dict)  # SE 200 mV 4.7 mV INL
check_log0902 = defaultdict(dict)  # SE 200 mV 7.8 mV INL

report_log09_fin_result = defaultdict(dict)

# 10
item10 = "MON_FE"
report_log10_01 = defaultdict(dict)
report_log10_02 = defaultdict(dict)
report_log10_03 = defaultdict(dict)
report_log10_04 = defaultdict(dict)
report_log10_05 = defaultdict(dict)
report_log10_06 = defaultdict(dict)

check_log1001 = defaultdict(dict)

mon_pulse = defaultdict(dict)

# 11
item11 = "MON_FE"
report_log11_01 = defaultdict(dict)
check_log1101 = defaultdict(dict)
report_log1101csv = defaultdict(dict)
report_log1102csv = defaultdict(dict)



# 12
item12 = "MON_ADC"
ADCMON_table_cell = defaultdict(dict)
ADCMON_table = defaultdict(dict)

check_log1201 = defaultdict(dict)
report_log1201csv = defaultdict(dict)
report_log1202csv = defaultdict(dict)

# 13
report_log13 = defaultdict(dict)    # input information
item13 = "CALI5"

report_log1301 = defaultdict(dict)  # SE 200 mV 4.7 mV INL
report_log1302 = defaultdict(dict)  # SE 200 mV 7.8 mV INL

check_log1301 = defaultdict(dict)  # SE 200 mV 4.7 mV INL
check_log1302 = defaultdict(dict)  # SE 200 mV 7.8 mV INL

report_log1301csvgain = defaultdict(dict)
report_log1301csvinl = defaultdict(dict)
report_log1301csvlinerange = defaultdict(dict)

report_log13_fin_result = defaultdict(dict)

# 14
report_log14 = defaultdict(dict)    # input information
item14 = "CALI6"

report_log1401 = defaultdict(dict)  # SE 200 mV 4.7 mV INL
report_log1402 = defaultdict(dict)  # SE 200 mV 7.8 mV INL

check_log1401 = defaultdict(dict)  # SE 200 mV 4.7 mV INL
check_log1402 = defaultdict(dict)  # SE 200 mV 7.8 mV INL

report_log14_fin_result = defaultdict(dict)

report_log1401csvgain = defaultdict(dict)
report_log1401csvinl = defaultdict(dict)
report_log1401csvlinerange = defaultdict(dict)

# 15
item15 = "ADC_SYNC_PAT"
# ADCMON_table_cell = defaultdict(dict)
# ADCMON_table = defaultdict(dict)
check_log1501 = defaultdict(dict)
check_log1502 = defaultdict(dict)
check_log1503 = defaultdict(dict)
check_log15csv = defaultdict(dict)

chkflag = defaultdict(dict)    # input information
badlist = defaultdict(dict)    # input information
# tmp_log = defaultdict(dict)
check_log = defaultdict(dict)
tmp_pulse = defaultdict(dict)

# 16

item16 = "PLL_PAT"
check_log1601 = defaultdict(dict)
report_log1601 = defaultdict(dict)
check_log16csv = defaultdict(dict)
# 06 calibration
channel0_pulse = defaultdict(dict)

