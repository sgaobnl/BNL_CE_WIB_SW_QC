# -*- coding: utf-8 -*-
import os, sys, csv
from datetime import datetime
import pandas as pd
from qc_files_status import qc_files_status 
#
#from QC_Report import QC_Report
#
# Import classes needed to generate statistical analysis

def DecodeRawData_func(root_path, data_dir, env, tms):
    output_path = root_path + "/Ana"
        
    if tms == 0:
        # # Initialization checkout
        from QC_INIT_CHK import QC_INIT_CHK
        init_chk = QC_INIT_CHK(root_path=root_path, data_dir=data_dir, output_path=output_path, env=env)
        FE_IDs = init_chk.decode_FE_PWR()

    if tms == 1:
        # # Power consumption measurement
        from QC_PWR import QC_PWR, QC_PWR_analysis
        qc_pwr = QC_PWR(root_path=root_path, data_dir=data_dir, output_path=output_path, env=env)
        FE_IDs = qc_pwr.decode_FE_PWR()

    if tms == 2:
        # # Channel response checkout
        from QC_CHKRES import QC_CHKRES
        qc_checkres = QC_CHKRES(root_path=root_path, data_dir=data_dir, output_path=output_path, env=env)
        FE_IDs = qc_checkres.decode_CHKRES()

    if tms == 3:
        # FE monitoring
        from QC_FE_MON import FE_MON
        fe_mon = FE_MON(root_path=root_path, data_dir=data_dir, output_path=output_path, env=env)
        FE_IDs = fe_mon.decodeFE_MON()

    if tms == 4:
        # Power cycling
        from QC_PWR_CYCLE import PWR_CYCLE 
        pwr_cycle = PWR_CYCLE(root_path=root_path, data_dir=data_dir, output_path=output_path, env=env)
        FE_IDs = pwr_cycle.decode_PwrCycle()

    if tms == 5:
        # # RMS noise
        from QC_RMS import RMS
        rms = RMS(root_path=root_path, data_dir=data_dir, output_path=output_path, env=env)
        FE_IDs = rms.decodeRMS()

    if tms == 61:
        # # ASICDAC Calibration
        from QC_CALIBRATION import QC_CALI
        asicdac = QC_CALI(root_path=root_path, data_dir=data_dir, output_path=output_path, env=env, tms=tms, QC_filename='QC_CALI_ASICDAC.bin')
        FE_IDs =asicdac.runASICDAC_cali(saveWfData=False)

    if tms == 64:
        from QC_CALIBRATION import QC_CALI
        tmpdirs = os.listdir('/'.join([root_path, data_dir]))
        for tmpdir in tmpdirs:
            if env in tmpdir[0:3]:
                break
        if 'QC_CALI_ASICDAC_47.bin' in os.listdir('/'.join([root_path, data_dir, tmpdir])):
            asic47dac = QC_CALI(root_path=root_path, data_dir=data_dir, output_path=output_path, env=env, tms=tms, QC_filename='QC_CALI_ASICDAC_47.bin')
            FE_IDs = asic47dac.runASICDAC_cali(saveWfData=False)

    if tms == 62:
        from QC_CALIBRATION import QC_CALI
        datdac = QC_CALI(root_path=root_path, data_dir=data_dir, output_path=output_path, env=env, tms=tms, QC_filename='QC_CALI_DATDAC.bin')
        FE_IDs = datdac.runASICDAC_cali(saveWfData=False)

    if tms == 63:
        from QC_CALIBRATION import QC_CALI
        direct_cali = QC_CALI(root_path=root_path, data_dir=data_dir, output_path=output_path, env=env, tms=tms, QC_filename='QC_CALI_DIRECT.bin')
        FE_IDs = direct_cali.runASICDAC_cali(saveWfData=False)

    if tms == 8:
        from QC_Cap_Meas import QC_Cap_Meas
        ## Calibration capacitor measurement
        cap = QC_Cap_Meas(root_path=root_path, data_dir=data_dir, output_path=output_path, env=env)
        FE_IDs = cap.decode_CapMeas()

    for FE_ID in FE_IDs:
        chip_path = '/'.join([root_path + "Ana"+ "_" + env, FE_ID])
        jfs = ["QC_INIT_CHK.json", "QC_PWR.json", "QC_PWR_CYCLE.json", "QC_CHKRES.json", "QC_CALI_ASICDAC.json", 
               "QC_CALI_ASICDAC_47.json", "QC_CALI_DATDAC.json", "QC_CALI_DIRECT.json", "QC_RMS.json", "QC_FE_MON.json", 'QC_Cap_Meas.json'  ]
        for fn in jfs:
            if not os.path.isfile('/'.join([chip_path, fn])):
                return None
        DecodeJson2csv(root_path, FE_ID, env)
    
def DecodeJson2csv(root_path, FE_ID, env):
    output_path = root_path + "Ana"+ "_" + env
    results_path = root_path + "results"
    if os.path.isdir(results_path):
        pass
    else:
        try:
            os.mkdir(results_path)
        except:
            print (f"Error: {results_path} can be created")
            return None

    csv_results = []
    #json_fs = [f for f in os.listdir(output_path + "_" + env) if ".json" in f]
    

    from QC_INIT_CHK import QC_INIT_CHKAna
    init_chk_ana = QC_INIT_CHKAna(root_path=root_path,chipID=FE_ID, output_path=output_path )
    tmp = init_chk_ana.run_Ana()
    if type(tmp) == list:
        csv_results += tmp

    from QC_PWR import  QC_PWR_analysis
    pwr_ana = QC_PWR_analysis(root_path=root_path, chipID=FE_ID, output_path=output_path)
    tmp = pwr_ana.run_Ana(path_to_statAna='')
    if type(tmp) == list:
        csv_results += tmp


    from QC_CHKRES import QC_CHKRES_Ana
    ana_femon =  QC_CHKRES_Ana(root_path=root_path, chipID=FE_ID, output_path=output_path)
    tmp = ana_femon.run_Ana()
    if type(tmp) == list:
        csv_results += tmp

    from QC_FE_MON import QC_FE_MON_Ana
    ana_femon =  QC_FE_MON_Ana(root_path=root_path, chipID=FE_ID, output_path=output_path)
    tmp = ana_femon.run_Ana()
    if type(tmp) == list:
        csv_results += tmp

    from QC_PWR_CYCLE import PWR_CYCLE_Ana
    ana_pca =  PWR_CYCLE_Ana(root_path=root_path, chipID=FE_ID, output_path=output_path)
    tmp = ana_pca.run_Ana()
    if type(tmp) == list:
        csv_results += tmp

    from QC_RMS import RMS_Ana
    ana_rms = RMS_Ana(root_path=root_path, chipID=FE_ID, output_path=output_path)
    tmp = ana_rms.run_Ana()
    if type(tmp) == list:
        csv_results += tmp

    from QC_CALIBRATION import QC_CALI_Ana
    ana_cali = QC_CALI_Ana(root_path=root_path, chipID=FE_ID, output_path=output_path, CALI_item="QC_CALI_ASICDAC")
    tmp = ana_cali.run_Ana()
    if type(tmp) == list:
        csv_results += tmp

    ana_cali = QC_CALI_Ana(root_path=root_path, chipID=FE_ID, output_path=output_path, CALI_item="QC_CALI_ASICDAC_47")
    tmp = ana_cali.run_Ana()
    if type(tmp) == list:
        csv_results += tmp

    ana_cali = QC_CALI_Ana(root_path=root_path, chipID=FE_ID, output_path=output_path, CALI_item="QC_CALI_DIRECT")
    tmp = ana_cali.run_Ana()
    if type(tmp) == list:
        csv_results += tmp

    ana_cali = QC_CALI_Ana(root_path=root_path, chipID=FE_ID, output_path=output_path, CALI_item="QC_CALI_DATDAC")
    tmp= ana_cali.run_Ana()
    if type(tmp) == list:
        csv_results += tmp

    from QC_Cap_Meas import QC_Cap_Meas_Ana
    ana_cap = QC_Cap_Meas_Ana(root_path=root_path, chipID=FE_ID, output_path=output_path)
    tmp = ana_cap.run_Ana()
    if type(tmp) == list:
        csv_results += tmp

    with open('/'.join([results_path, '{}_{}.csv'.format(FE_ID, env)]), 'w') as f:
        csvwriter = csv.writer(f, delimiter=',', dialect="unix")
        csvwriter.writerows(csv_results)


if __name__ =="__main__":
    root_path = '''S:/RTS_DAT_LArASIC_QC/B002T0001/'''
    #root_path = "E:/RTS_DAT_LArASIC_QC/B009T0008/"
    #root_path = "Time_20250529153639_DUT_0047_1048_2049_3066_4067_5068_6069_7082"""
    #data_dir = "Time_20250527114445_DUT_0000_1001_2002_3003_4004_5005_6006_7007"

    for root, dirs, files in os.walk(root_path):
        break
    data_dir = 'Time_20250813122458_DUT_0008_1009_2010_3011_4012_5013_6014_7015'
    dirs = [data_dir]

    for data_dir in dirs:
        if ("Time_" in data_dir[0:5]) and ("_DUT_" in data_dir):
            for subdir in os.listdir("/".join([root_path, data_dir])):
                if os.path.isdir("/".join([root_path, data_dir, subdir])):
                    env=subdir[0:2]
                    fdp = "/".join([root_path, data_dir, subdir])
                    if "_FE_" in subdir:
                        qcdone_flg = qc_files_status(rootdir=fdp, duttype = 'FE')
                        if not qcdone_flg:
                            print ("Warning: Folder with incompleted QC data, ignore!", "/".join([root_path, data_dir, subdir]), )
                            continue
                    if ("RT" in env) or ("LN" in env):
                        print ("www")
                        print ("/".join([root_path, data_dir, subdir]))
 #                       DecodeRawData_func(root_path=root_path, data_dir=data_dir, env=env, tms=0)
 #                       DecodeRawData_func(root_path=root_path, data_dir=data_dir, env=env, tms=1)
 #                       DecodeRawData_func(root_path=root_path, data_dir=data_dir, env=env, tms=2)
 #                       DecodeRawData_func(root_path=root_path, data_dir=data_dir, env=env, tms=3)
 #                       DecodeRawData_func(root_path=root_path, data_dir=data_dir, env=env, tms=4)
 #                       DecodeRawData_func(root_path=root_path, data_dir=data_dir, env=env, tms=5)
 #                       DecodeRawData_func(root_path=root_path, data_dir=data_dir, env=env, tms=61)
 #                       DecodeRawData_func(root_path=root_path, data_dir=data_dir, env=env, tms=62)
 #                       DecodeRawData_func(root_path=root_path, data_dir=data_dir, env=env, tms=63)
                        DecodeRawData_func(root_path=root_path, data_dir=data_dir, env=env, tms=64)
 #                       DecodeRawData_func(root_path=root_path, data_dir=data_dir, env=env, tms=8)

#    Bdirs = [] 
#    for onedir in dirs:
#        if ("B" in onedir[0:1]) and ("T0" in  onedir):
#            Bdirs.append(onedir)
#
#    for bdir in Bdirs:
#        bpath = "/".join([root_path, bdir])
#        for broot, bsubdirs, files in os.walk(bpath):
#            break
#        #print (bsubdirs)
#        for data_dir in bsubdirs:
#            if ("Time_" in data_dir[0:5]) and ("_DUT_" in data_dir):
#                for subdir in os.listdir("/".join([bpath, data_dir])):
#                    if os.path.isdir("/".join([bpath, data_dir, subdir])):
#                        env=subdir[0:2]
#                        fdp = "/".join([bpath, data_dir, subdir])
#                        if "_FE_" in subdir:
#                            qcdone_flg = qc_files_status(rootdir=fdp, duttype = 'FE')
#                            if not qcdone_flg:
#                                print ("Warning: Folder with incompleted QC data, ignore!", "/".join([bpath, data_dir, subdir]), )
#                                continue
#                        if ("RT" in env) or ("LN" in env):
#                            print ("/".join([bpath, data_dir, subdir]))
#                            DecodeRawData_func(root_path=bpath, data_dir=data_dir, env=env, tms=0)
#                            DecodeRawData_func(root_path=bpath, data_dir=data_dir, env=env, tms=1)
#                            DecodeRawData_func(root_path=bpath, data_dir=data_dir, env=env, tms=2)
#                            DecodeRawData_func(root_path=bpath, data_dir=data_dir, env=env, tms=3)
#                            DecodeRawData_func(root_path=bpath, data_dir=data_dir, env=env, tms=4)
#                            DecodeRawData_func(root_path=bpath, data_dir=data_dir, env=env, tms=5)
#                            DecodeRawData_func(root_path=bpath, data_dir=data_dir, env=env, tms=61)
#                            DecodeRawData_func(root_path=bpath, data_dir=data_dir, env=env, tms=62)
#                            DecodeRawData_func(root_path=bpath, data_dir=data_dir, env=env, tms=63)
#                            DecodeRawData_func(root_path=bpath, data_dir=data_dir, env=env, tms=64)
#                            DecodeRawData_func(root_path=bpath, data_dir=data_dir, env=env, tms=8)
#


#    FE_ID = "001_00001_20250529153639_Tray47_SKT0"
#    env="LN"
#    output_path = root_path + "Ana"+ "_" + env
#    from QC_CALIBRATION import QC_CALI_Ana
#    ana_cali = QC_CALI_Ana(root_path=root_path, chipID=FE_ID, output_path=output_path, CALI_item="QC_CALI_ASICDAC")
#    tmp = ana_cali.run_Ana()
#    print (tmp)
#    print (tmp[0])
#    print (tmp[0][0])

#    import shutil
#    FE_ID = "20250529153639" #009-3495
#    chipid = "009_3525"
#    chipid, FE_ID = ["009_3518", "20250528112559"]
    
    
    
#    env = "RT"
#    DecodeJson2csv(root_path, FE_ID, env)
#    env = "LN"
#    DecodeJson2csv(root_path, FE_ID, env)

#    src = "/".join([root_path, "Ana_RT", FE_ID])
#    des = "/".join(["E:/RTS_DAT_LArASIC_QC/B009T0008/BRD31/",  chipid + "_" + FE_ID + "_" + env])
#    #os.makedirs(des, exist_ok=True)
#    shutil.copytree(src, des)
#    srcf = "E:/RTS_DAT_LArASIC_QC/B009T0008/results/" + FE_ID + "_" + env + ".csv"
#    dstf = "/".join(["E:/RTS_DAT_LArASIC_QC/B009T0008/BRD31/",  chipid + "_" + FE_ID + "_" + env + ".csv"])
#    shutil.copy(srcf, dstf)
#
#    exit()
#
#    src = "/".join([root_path, "Ana_LN", FE_ID])
#    des = "/".join(["E:/RTS_DAT_LArASIC_QC/B009T0008/BRD31/",  chipid + "_" + FE_ID + "_" + env])
#    #os.makedirs(des, exist_ok=True)
#    shutil.copytree(src, des)
#    srcf = "E:/RTS_DAT_LArASIC_QC/B009T0008/results/" + FE_ID + "_" + env + ".csv"
#    dstf = "/".join(["E:/RTS_DAT_LArASIC_QC/B009T0008/BRD31/",  chipid + "_" + FE_ID + "_" + env + ".csv"])
#    shutil.copy(srcf, dstf)
#
##    AnalyzeDecodedData_func(root_path=root_path, env=env)    
#
