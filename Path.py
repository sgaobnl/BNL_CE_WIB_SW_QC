import os

Desk = "D:/A0-FEMB_07_"
Board_version_batch = "1T_Auto/"


##===================================
data_dir_GTCK = Desk + Board_version_batch + "T1_GTCK_tmp_data/"
#report_dir_GTCK = Desk + Board_version_batch + "Q1_GTCK_reports/"
report_dir_GTCK = data_dir_GTCK + "A_REPORTS_T1/"
##===================================
data_dir_RTCK = Desk + Board_version_batch + "T2_CK_General_TEST/"
report_dir_RTCK = data_dir_RTCK + "ACK_REPORTS_T2/"
#report_dir_RTCK = Desk + Board_version_batch + "Q2_CK_performance_reports____I/"
##===================================
data_dir_RTQC = Desk + Board_version_batch + "T3_QC_Performance_TEST/"
report_dir_RTQC = data_dir_RTQC + "AQC_REPORTS_T3/"
#report_dir_RTQC = Desk + Board_version_batch + "Q3_QC_performance_reports____I_I/"
##===================================
#report_dir_LNCK = Desk + Board_version_batch + "Q4_LNCK_reports____I_I_I/"
#data_dir_LNCK = Desk + Board_version_batch + "Q4_LNCK_tmp_data_I_I_I/"
##===================================
#report_dir_LNQC = Desk + Board_version_batch + "Q5_LNQC_reports____I_I_I_I/"
#data_dir_LNQC = Desk + Board_version_batch + "Q5_LNQC_tmp_data_I_I_I_I/"
##===================================
data_dir_SCHK = Desk + Board_version_batch + "T6_SCHK_tmp_data/"
report_dir_SCHK = data_dir_SCHK + "A_REPORTS_T6/"
#report_dir_SCHK = Desk + Board_version_batch + "Q6_SCHK_reports____I_I_I_I_I/"




##===================================
if os.path.exists(report_dir_GTCK):
    #print("report_dir_GTCK path\n")
    pass
else:
    os.makedirs(report_dir_GTCK)
    print("create report_dir_GTCK path")

if os.path.exists(data_dir_GTCK):
    pass
else:
    os.makedirs(data_dir_GTCK)
    print("create data_dir_GTCK path")

##===================================
if os.path.exists(report_dir_RTCK):
    pass
else:
    os.makedirs(report_dir_RTCK)
    print("create report_dir_RTCK path")
    
if os.path.exists(data_dir_RTCK):
    pass
else:
    os.makedirs(data_dir_RTCK)
    print("create data_dir_RTCK path")

##===================================
if os.path.exists(report_dir_RTQC):
    pass
else:
    os.makedirs(report_dir_RTQC)
    print("create report_dir_RTQC path")

if os.path.exists(data_dir_RTQC):
    pass
else:
    os.makedirs(data_dir_RTQC)
    print("create data_dir_RTQC path")

##===================================
# if os.path.exists(report_dir_LNCK):
#     print("report_dir_LNCK path\n")
# else:
#     os.makedirs(report_dir_LNCK)
#     print("create report_dir_LNK path")
#
# if os.path.exists(data_dir_LNCK):
#     print("data_dir_LNCK path\n")
# else:
#     os.makedirs(data_dir_LNCK)
#     print("create data_dir_LNCK path")
#
# ##===================================
# if os.path.exists(report_dir_LNQC):
#     print("report_dir_LNQC path\n")
# else:
#     os.makedirs(report_dir_LNQC)
#     print("create report_dir_LNQC path")
#
# if os.path.exists(data_dir_LNQC):
#     print("data_dir_LNQC path\n")
# else:
#     os.makedirs(data_dir_LNQC)
#     print("create data_dir_LNQC path")

##===================================
if os.path.exists(report_dir_SCHK):
    pass
else:
    os.makedirs(report_dir_SCHK)
    print("create report_dir_SCHK path")

if os.path.exists(data_dir_SCHK):
    pass
else:
    os.makedirs(data_dir_SCHK)
    print("create data_dir_SCHK path")