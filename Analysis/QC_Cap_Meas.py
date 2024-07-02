############################################################################################
#   created on 7/2/2024 @ 13:52
#   email: radofanantenan.razakamiandra@stonybrook.edu
#   Analyze the calibration data: QC_Cap_Meas.bin
############################################################################################

import os, sys
import numpy as np
from utils import printItem, createDirs, dumpJson, linear_fit, LArASIC_ana, decodeRawData, BaseClass, getMaxAmpIndices
import matplotlib.pyplot as plt

class QC_Cap_Meas(BaseClass):
    def __init__(self, root_path: str, data_dir: str, output_path: str, generateWf=False):
        printItem("Capacitance measurement")
        self.generateWf = generateWf
        super().__init__(root_path=root_path, data_dir=data_dir, output_path=output_path, tms=8, QC_filename="QC_Cap_Meas.bin", generateWaveForm=self.generateWf)
        self.suffixName = "Cap_Meas"
        print(self.suffixName)
        print(self.params)


if __name__ == '__main__':
    root_path = '../../Data_BNL_CE_WIB_SW_QC'
    output_path = '../../Analyzed_BNL_CE_WIB_SW_QC'

    list_data_dir = [dir for dir in os.listdir(root_path) if '.zip' not in dir]
    for i, data_dir in enumerate(list_data_dir):
        cap = QC_Cap_Meas(root_path=root_path, data_dir=data_dir, output_path=output_path, generateWf=False)
        sys.exit()
