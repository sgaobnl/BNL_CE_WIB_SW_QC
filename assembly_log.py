###### load logs and create report folder ######
chkflag={"RMS":[],"BL":[],"Pulse_SE":{},"Pulse_DIFF":{},"PWR":[],"MON_T":[],"MON_BGP":[],"MON_ADC":{}}
chkflag["Pulse_SE"]={"PPK":[],"NPK":[],"BL":[]}
chkflag["Pulse_DIFF"]={"PPK":[],"NPK":[],"BL":[]}
chkflag["MON_ADC"]={"VCMI":[],"VCMO":[],"VREFP":[],"VREFN":[],"VSSA":[]}

badlist={"RMS":[],"BL":[],"Pulse_SE":{},"Pulse_DIFF":{},"PWR":[],"MON_T":[],"MON_BGP":[],"MON_ADC":{}}
badlist["Pulse_SE"]={"PPK":[],"NPK":[],"BL":[]}
badlist["Pulse_DIFF"]={"PPK":[],"NPK":[],"BL":[]}
badlist["MON_ADC"]={"VCMI":[],"VCMO":[],"VREFP":[],"VREFN":[],"VSSA":[]}

report_log01 = {}
report_log02 = {}
report_log03 = {}
report_log04 = {}
report_log05 = {}
report_log06 = {}
report_log07 = {}
report_log08 = {}

