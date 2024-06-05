############################################################################################
#   created on 6/5/2024 @ 13:43
#   emails: radofanantenan.razakamiandra@stonybrook.edu
#   Analyze the data in QC_CHKRES.bin
############################################################################################

from datetime import datetime
import os, sys
import numpy as np
import matplotlib.pyplot as plt
import json, pickle
from utils import printItem, createDirs, dumpJson, decodeRawData, LArASIC_ana

class QC_CHKRES:
    def __init__(self, root_path: str, data_dir: str, output_dir: str):
        self.tms = 2
        self.qc_chres_filename = "QC_CHKRES.bin"
        self.qc_item_to_analyze = "FE response measurement checkout"
        printItem(self.qc_item_to_analyze)
        # open the raw data
        with open('/'.join([root_path, data_dir, 'QC_CHKRES.bin']), 'rb') as f:
            self.raw_data = pickle.load(f)
        self.logs_dict = self.raw_data['logs']
        self.pulseResp_params = [param for param in self.raw_data.keys() if param!='logs']
        # tmp_params = [p.split('_')[1] for p in self.pulseResp_params]
        self.__getConfig(self.pulseResp_params)

    def __getConfig(self, list_params: list):
        elts_to_check = []
        tmp_elts_to_check = [p.split('_')[1] for p in list_params]
        for x in tmp_elts_to_check:
            if x not in elts_to_check:
                elts_to_check.append(x)
        configs = {c: [] for c in elts_to_check}
        for KEY in configs.keys():
            for param in list_params:
                if KEY==param.split('_')[1]:
                    configs[KEY].append(param)
        print(configs.keys())
        print(configs['TP'][0].split('_')[2:])
    
    def __splitConfig(self, config_dict: dict, KEY: str):
        config_list = config_dict[KEY]
        config_key_letters = {
            'GAINs': 'SG',
            'TP': 'ST',
            'SLKS': 'SLK',
            'BL': 'SNC',
            'OUTPUT': ['SDD', 'SDF']
        }

if __name__ == "__main__":
    root_path = '../../Data_BNL_CE_WIB_SW_QC'
    output_path = '../../Analyzed_BNL_CE_WIB_SW_QC'
    list_data_dir = os.listdir(root_path)
    for data_dir in list_data_dir:
        qc_checkres = QC_CHKRES(root_path=root_path, data_dir=data_dir, output_dir=output_path)
        sys.exit()
