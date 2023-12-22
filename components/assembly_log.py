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

report_log01 = defaultdict(dict)
report_log02 = defaultdict(dict)
report_log03 = defaultdict(dict)
report_log04 = defaultdict(dict)
report_log05 = defaultdict(dict)
report_log06 = defaultdict(dict)
report_log07 = defaultdict(dict)
report_log08 = defaultdict(dict)
report_log09 = defaultdict(dict)
report_log10 = defaultdict(dict)

final_status = defaultdict(dict)
