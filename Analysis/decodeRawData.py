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

if __name__ == '__main__':
    root_path = '../../Data_BNL_CE_WIB_SW_QC'
    output_path = '../../Analyzed_BNL_CE_WIB_SW_QC'

    list_data_dir = [dir for dir in os.listdir(root_path) if '.zip' not in dir]
    for data_dir in list_data_dir:
        t0 = datetime.now()
        print('start time : {}'.format(t0))
        #-----------------------------
        # Initialization checkout
        init_chk = QC_INIT_CHECK(root_path=root_path, data_dir=data_dir, output_dir=output_path)
        init_chk.decode_INIT_CHK(generateQCresult=False)
        # Power consumption measurement
        qc_pwr = QC_PWR(root_path=root_path, data_dir=data_dir, output_dir=output_path)
        qc_pwr.decode_FE_PWR()
        # Channel response checkout
        qc_checkres = QC_CHKRES(root_path=root_path, data_dir=data_dir, output_dir=output_path)
        qc_checkres.decode_CHKRES()
        # FE monitoring
        fe_mon = FE_MON(root_path=root_path, data_dir=data_dir, output_path=output_path)
        fe_mon.decodeFE_MON()
        # Power cycling
        pwr_cycle = PWR_CYCLE(root_path=root_path, data_dir=data_dir, output_path=output_path)
        pwr_cycle.decode_PwrCycle()
        # RMS noise
        rms = RMS(root_path=root_path, data_dir=data_dir, output_path=output_path)
        rms.decodeRMS()
        #----------------------------
        tf = datetime.now()
        print('end time : {}'.format(tf))
        deltaT = (tf - t0).total_seconds()
        print("Decoding time : {} seconds".format(deltaT))
        print("=xx="*20)
