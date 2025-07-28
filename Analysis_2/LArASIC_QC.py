import os, sys
from datetime import datetime
import pandas as pd
#
#from QC_Report import QC_Report
#
# Import classes needed to generate statistical analysis

def DecodeRawData_func(root_path, data_dir, env, tms):
    output_path = root_path + "Ana"
        
    if tms == 0:
        # # Initialization checkout
        from QC_INIT_CHK import QC_INIT_CHK, QC_INIT_CHKAna
        init_chk = QC_INIT_CHK(root_path=root_path, data_dir=data_dir, output_dir=output_path, env=env)
        FE_IDs = init_chk.decode_FE_PWR()
        #FE_IDs = ['20250527114445', '20250527114539', '20250527114632', '20250527114726', '20250527114820', '20250527114916', '20250527115012', '20250527115109']
        for FE_ID in FE_IDs:
            init_chk_ana = QC_INIT_CHKAna(root_path=root_path, output_path=output_path + "_" + env, chipID=FE_ID)
            init_chk_ana.run_Ana()

    if tms == 1:
        # # Power consumption measurement
        from QC_PWR import QC_PWR, QC_PWR_analysis
        qc_pwr = QC_PWR(root_path=root_path, data_dir=data_dir, output_dir=output_path, env=env)
        FE_IDs = qc_pwr.decode_FE_PWR()
        for FE_ID in FE_IDs:
            pwr_ana = QC_PWR_analysis(root_path=root_path, chipID=FE_ID, output_path=output_path + "_" + env)
            pwr_ana.run_Ana(path_to_statAna='')

    if tms == 2:
        # # Channel response checkout
        from QC_CHKRES import QC_CHKRES, QC_CHKRES_Ana
        qc_checkres = QC_CHKRES(root_path=root_path, data_dir=data_dir, output_dir=output_path, env=env)
        FE_IDs = qc_checkres.decode_CHKRES()
        for FE_ID in FE_IDs:
            ana_femon =  QC_CHKRES_Ana(root_path=root_path, chipID=FE_ID, output_path=output_path + "_" + env)
            ana_femon.run_Ana()

    if tms == 3:
        # FE monitoring
        from QC_FE_MON import FE_MON, QC_FE_MON_Ana
        fe_mon = FE_MON(root_path=root_path, data_dir=data_dir, output_path=output_path, env=env)
        FE_IDs = fe_mon.decodeFE_MON()
        print (FE_IDs)
        exit()
        for FE_ID in FE_IDs:
            ana_femon =  QC_FE_MON_Ana(root_path=root_path, chipID=FE_ID, output_path=output_path + "_" + env)
            ana_femon.run_Ana()

    if tms == 4:
        # Power cycling
        from QC_PWR_CYCLE import PWR_CYCLE, PWR_CYCLE_Ana
        pwr_cycle = PWR_CYCLE(root_path=root_path, data_dir=data_dir, output_path=output_path, env=env)
        FE_IDs = pwr_cycle.decode_PwrCycle()
        for FE_ID in FE_IDs:
            ana_pca =  PWR_CYCLE_Ana(root_path=root_path, chipID=FE_ID, output_path=output_path + "_" + env)
            ana_pca.run_Ana()

    if tms == 5:
        # # RMS noise
        from QC_RMS import RMS, RMS_Ana
        rms = RMS(root_path=root_path, data_dir=data_dir, output_path=output_path, env=env)
        FE_IDs = rms.decodeRMS()
        #FE_IDs = ['20250527114445', '20250527114539', '20250527114632', '20250527114726', '20250527114820', '20250527114916', '20250527115012', '20250527115109']
        for FE_ID in FE_IDs:
            ana_rms = RMS_Ana(root_path=root_path, chipID=FE_ID, output_path=output_path + "_" + env)
            ana_rms.run_Ana()

    if tms == 61:
        # # ASICDAC Calibration
        from QC_CALIBRATION import QC_CALI, QC_CALI_Ana
        asicdac = QC_CALI(root_path=root_path, data_dir=data_dir, output_path=output_path, env=env, tms=tms, QC_filename='QC_CALI_ASICDAC.bin', generateWf=False)
        FE_IDs =asicdac.runASICDAC_cali(saveWfData=False)
        #FE_IDs = ['20250527114445', '20250527114539', '20250527114632', '20250527114726', '20250527114820', '20250527114916', '20250527115012', '20250527115109']
        for FE_ID in FE_IDs:
            ana_cali = QC_CALI_Ana(root_path=root_path, chipID=FE_ID, output_path=output_path + "_" + env, CALI_item="QC_CALI_ASICDAC")
            ana_cali.run_Ana()

    if tms == 64:
        from QC_CALIBRATION import QC_CALI, QC_CALI_Ana
        tmpdir = os.listdir('/'.join([root_path, data_dir]))[0]
        if 'QC_CALI_ASICDAC_47.bin' in os.listdir('/'.join([root_path, data_dir, tmpdir])):
            asic47dac = QC_CALI(root_path=root_path, data_dir=data_dir, output_path=output_path, env=env, tms=tms, QC_filename='QC_CALI_ASICDAC_47.bin', generateWf=False)
            FE_IDs = asic47dac.runASICDAC_cali(saveWfData=False)
            #FE_IDs = ['20250527114445', '20250527114539', '20250527114632', '20250527114726', '20250527114820', '20250527114916', '20250527115012', '20250527115109']
            for FE_ID in FE_IDs:
                ana_cali = QC_CALI_Ana(root_path=root_path, chipID=FE_ID, output_path=output_path + "_" + env, CALI_item="QC_CALI_ASICDAC_47")
                ana_cali.run_Ana()

    if tms == 62:
        from QC_CALIBRATION import QC_CALI, QC_CALI_Ana
        datdac = QC_CALI(root_path=root_path, data_dir=data_dir, output_path=output_path, env=env, tms=tms, QC_filename='QC_CALI_DATDAC.bin', generateWf=False)
        FE_IDs = datdac.runASICDAC_cali(saveWfData=False)
        #FE_IDs = ['20250527114445', '20250527114539', '20250527114632', '20250527114726', '20250527114820', '20250527114916', '20250527115012', '20250527115109']
        for FE_ID in FE_IDs:
            ana_cali = QC_CALI_Ana(root_path=root_path, chipID=FE_ID, output_path=output_path + "_" + env, CALI_item="QC_CALI_DATDAC")
            ana_cali.run_Ana()

    if tms == 63:
        from QC_CALIBRATION import QC_CALI, QC_CALI_Ana
        direct_cali = QC_CALI(root_path=root_path, data_dir=data_dir, output_path=output_path, env=env, tms=tms, QC_filename='QC_CALI_DIRECT.bin', generateWf=False)
        FE_IDs = direct_cali.runASICDAC_cali(saveWfData=False)
        #FE_IDs = ['20250527114445', '20250527114539', '20250527114632', '20250527114726', '20250527114820', '20250527114916', '20250527115012', '20250527115109']
        for FE_ID in FE_IDs:
            ana_cali = QC_CALI_Ana(root_path=root_path, chipID=FE_ID, output_path=output_path + "_" + env, CALI_item="QC_CALI_DIRECT")
            ana_cali.run_Ana()

    if tms == 8:
        from QC_Cap_Meas import QC_Cap_Meas, QC_Cap_Meas_Ana
        ## Calibration capacitor measurement
        cap = QC_Cap_Meas(root_path=root_path, data_dir=data_dir, output_path=output_path, env=env, generateWf_plot=False)
        FE_IDs = cap.decode_CapMeas()
        #FE_IDs = ['20250527114445', '20250527114539', '20250527114632', '20250527114726', '20250527114820', '20250527114916', '20250527115012', '20250527115109']
        for FE_ID in FE_IDs:
            ana_cap = QC_Cap_Meas_Ana(root_path=root_path, chipID=FE_ID, output_path=output_path + "_" + env)
            ana_cap.run_Ana()
    

if __name__ =="__main__":
    root_path = "D:/B009T0008/"
    data_dir = "Time_20250527114445_DUT_0000_1001_2002_3003_4004_5005_6006_7007"
    env = 'RT'
    DecodeRawData_func(root_path=root_path, data_dir=data_dir, env=env, tms=0)
#    DecodeRawData_func(root_path=root_path, data_dir=data_dir, env=env, tms=1)
#    DecodeRawData_func(root_path=root_path, data_dir=data_dir, env=env, tms=2)
#    DecodeRawData_func(root_path=root_path, data_dir=data_dir, env=env, tms=3)
#    DecodeRawData_func(root_path=root_path, data_dir=data_dir, env=env, tms=4)
#    DecodeRawData_func(root_path=root_path, data_dir=data_dir, env=env, tms=5)
#    DecodeRawData_func(root_path=root_path, data_dir=data_dir, env=env, tms=61)
#    DecodeRawData_func(root_path=root_path, data_dir=data_dir, env=env, tms=62)
#    DecodeRawData_func(root_path=root_path, data_dir=data_dir, env=env, tms=63)
#    DecodeRawData_func(root_path=root_path, data_dir=data_dir, env=env, tms=64)
#    DecodeRawData_func(root_path=root_path, data_dir=data_dir, env=env, tms=8)


#    AnalyzeDecodedData_func(root_path=root_path, env=env)    

