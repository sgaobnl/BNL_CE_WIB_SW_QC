############################################################################################
#   created on 6/9/2024 @ 16:16
#   email: radofanantenan.razakamiandra@stonybrook.edu
#   Run all decoding scripts
############################################################################################

import os
from datetime import datetime
from Init_checkout import QC_INIT_CHECK
from QC_PWR import QC_PWR
from QC_CHKRES import QC_CHKRES
from QC_FE_MON import FE_MON
from QC_PWR_CYCLE import PWR_CYCLE
from QC_RMS import RMS
from QC_CALIBRATION import QC_CALI
from QC_DLY_RUN import QC_DLY_RUN
from QC_Cap_Meas import QC_Cap_Meas

if __name__ == '__main__':
    # root_path = '../../Data_BNL_CE_WIB_SW_QC'
    # root_path = '../../B010T0004'
    # output_path = '../../Analyzed_BNL_CE_WIB_SW_QC'

    # # list_data_dir = [dir for dir in os.listdir(root_path) if '.zip' not in dir]
    # list_data_dir = [dir for dir in os.listdir(root_path) if (os.path.isdir('/'.join([root_path, dir]))) and (dir!='images')]
    # for data_dir in list_data_dir:
    #     print(data_dir)
    #     t0 = datetime.now()
    #     print('start time : {}'.format(t0))
    #     #-----------------------------
    #     # Initialization checkout
    #     # init_chk = QC_INIT_CHECK(root_path=root_path, data_dir=data_dir, output_dir=output_path)
    #     # init_chk.decode_INIT_CHK(generateQCresult=False, generatePlots=False)
    #     # # Power consumption measurement
    #     # qc_pwr = QC_PWR(root_path=root_path, data_dir=data_dir, output_dir=output_path)
    #     # qc_pwr.decode_FE_PWR()
    #     # Channel response checkout
    #     # qc_checkres = QC_CHKRES(root_path=root_path, data_dir=data_dir, output_dir=output_path)
    #     # qc_checkres.decode_CHKRES()
    #     # FE monitoring
    #     # fe_mon = FE_MON(root_path=root_path, data_dir=data_dir, output_path=output_path)
    #     # fe_mon.decodeFE_MON()
    #     # # Power cycling
    #     # pwr_cycle = PWR_CYCLE(root_path=root_path, data_dir=data_dir, output_path=output_path)
    #     # pwr_cycle.decode_PwrCycle()
    #     # # RMS noise
    #     # rms = RMS(root_path=root_path, data_dir=data_dir, output_path=output_path)
    #     # rms.decodeRMS()
    #     # # ASICDAC Calibration
    #     # asicdac = QC_CALI(root_path=root_path, data_dir=data_dir, output_path=output_path, tms=61, QC_filename='QC_CALI_ASICDAC.bin', generateWf=True)
    #     # asicdac.runASICDAC_cali(saveWfData=False)
    #     tmpdir = os.listdir('/'.join([root_path, data_dir]))[0]
    #     if 'QC_CALI_ASICDAC_47.bin' in os.listdir('/'.join([root_path, data_dir, tmpdir])):
    #         asic47dac = QC_CALI(root_path=root_path, data_dir=data_dir, output_path=output_path, tms=64, QC_filename='QC_CALI_ASICDAC_47.bin', generateWf=True)
    #         asic47dac.runASICDAC_cali(saveWfData=False)
    #     # datdac = QC_CALI(root_path=root_path, data_dir=data_dir, output_path=output_path, tms=62, QC_filename='QC_CALI_DATDAC.bin', generateWf=True)
    #     # datdac.runASICDAC_cali(saveWfData=False)
    #     # direct_cali = QC_CALI(root_path=root_path, data_dir=data_dir, output_path=output_path, tms=63, QC_filename='QC_CALI_DIRECT.bin', generateWf=True)
    #     # direct_cali.runASICDAC_cali(saveWfData=False)
    #     #
    #     # DELAY RUN
    #     # dly_run = QC_DLY_RUN(root_path=root_path, data_dir=data_dir, output_path=output_path, generateWf=False)
    #     # dly_run.run_DLY_RUN()
    #     #
    #     # Capacitance measurement
    #     # cap = QC_Cap_Meas(root_path=root_path, data_dir=data_dir, output_path=output_path, generateWf=False)
    #     # decodedData = cap.decode()
    #     # cap.saveData(decodedData=decodedData)
    #     #----------------------------
    #     tf = datetime.now()
    #     print('end time : {}'.format(tf))
    #     deltaT = (tf - t0).total_seconds()
    #     print("Decoding time : {} seconds".format(deltaT))
    #     print("=xx="*20)

    mainPath = "/media/rado/New Volume/"
    output_path = '../../Analyzed_BNL_CE_WIB_SW_QC'
    for folder in os.listdir(mainPath):
        if folder[:2]=='B0' and '_' not in folder:
            root_path = '/'.join([mainPath, folder])
            list_data_dir = [dir for dir in os.listdir(root_path) if (os.path.isdir('/'.join([root_path, dir]))) and (dir!='images')]
            for data_dir in list_data_dir:
                # # Power consumption measurement
                qc_pwr = QC_PWR(root_path=root_path, data_dir=data_dir, output_dir=output_path)
                qc_pwr.decode_FE_PWR()
                # # Channel response checkout
                qc_checkres = QC_CHKRES(root_path=root_path, data_dir=data_dir, output_dir=output_path)
                qc_checkres.decode_CHKRES()
                # # FE monitoring
                fe_mon = FE_MON(root_path=root_path, data_dir=data_dir, output_path=output_path)
                fe_mon.decodeFE_MON()