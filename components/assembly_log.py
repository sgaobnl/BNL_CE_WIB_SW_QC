from collections import defaultdict
##### load logs and create report folder ######
chkflag={"RMS":[],"BL":[],"Pulse_SE":{},"Pulse_DIFF":{},"PWR":[],"MON_T":[],"MON_BGP":[],"MON_ADC":{}}
chkflag["Pulse_SE"]={"PPK":[],"NPK":[],"BL":[]}
chkflag["Pulse_DIFF"]={"PPK":[],"NPK":[],"BL":[]}
chkflag["MON_ADC"]={"VCMI":[],"VCMO":[],"VREFP":[],"VREFN":[],"VSSA":[]}

badlist={"RMS":[],"BL":[],"Pulse_SE":{},"Pulse_DIFF":{},"PWR":[],"MON_T":[],"MON_BGP":[],"MON_ADC":{}}
badlist["Pulse_SE"]={"PPK":[],"NPK":[],"BL":[]}
badlist["Pulse_DIFF"]={"PPK":[],"NPK":[],"BL":[]}
badlist["MON_ADC"]={"VCMI":[],"VCMO":[],"VREFP":[],"VREFN":[],"VSSA":[]}

report_log00 = defaultdict(dict)    # SN
report_log001 = defaultdict(dict)    # SN
report_log002 = defaultdict(dict)    # SN

report_log01 = defaultdict(dict)    # input information
report_log02 = defaultdict(dict)    # initial current measurement
report_log021 = defaultdict(dict)    # initial current result
report_log03 = defaultdict(dict)    # initial registers check
report_log04 = defaultdict(dict)    # SE mode: rms & ped
report_log04csv = defaultdict(dict)    # SE mode: rms & ped
rmsdata = defaultdict(dict)
peddata = defaultdict(dict)

report_log05 = defaultdict(dict)    # SE mode: current measurement
report_log051 = defaultdict(dict)    # SE mode: current result
report_log06 = defaultdict(dict)    # SE mode: power rail
report_log06csv = defaultdict(dict)    # SE mode: power rail
report_log061 = defaultdict(dict)    # SE mode: power rail
report_log07 = defaultdict(dict)    # SE mode: pulse response
report_log07csv = defaultdict(dict)    # SE mode: pulse response
report_log08 = defaultdict(dict)    # DIFF mode: pulse, rms, ped
report_log09 = defaultdict(dict)    # DIFF mode: power rail
report_log091 = defaultdict(dict)    # DIFF mode: power rail
report_log10 = defaultdict(dict)    # DIFF mode: current measurement
report_log10csv = defaultdict(dict)    # DIFF mode: current measurement
report_log101 = defaultdict(dict)    # DIFF mode: current measurement
report_log11 = defaultdict(dict)    # Monitor path
report_log111 = defaultdict(dict)    # Monitor path
tmp_log00 = defaultdict(dict)
ck_log00 = defaultdict(dict)
qc_log00 = defaultdict(dict)

final_status = defaultdict(dict)

power_rail_report_log = defaultdict(dict)
power_rail_report_csv = defaultdict(dict)


chkflag = defaultdict(dict)    # input information
badlist = defaultdict(dict)    # input information

tmp_log = defaultdict(dict)
check_log = defaultdict(dict)

channel0_pulse = defaultdict(dict)