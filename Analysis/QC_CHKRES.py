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
        # create directories
        createDirs(logs_dict=self.logs_dict, output_dir=output_dir)
        FE_outputDIRs = ['/'.join([output_dir, self.logs_dict['FE{}'.format(ichip)]]) for ichip in range(8)]
        self.CHKRES_dirs = {self.logs_dict['FE{}'.format(ichip)]: '/'.join([FE_outputDIRs[ichip], 'CHKRES']) for ichip in range(8)}
        for key, val in self.CHKRES_dirs.items():
            try:
                os.mkdir(val)
            except OSError:
                pass
        self.pulseResp_params = [param for param in self.raw_data.keys() if param!='logs']


    def __getConfig_dict(self, list_params: list):
        '''
        output:
            {
            'GAINs': [],
            'OUTPUT': [],
            'BL': [],
            'TP': []
            }
        '''
        elts_to_check = []
        tmp_elts_to_check = [p.split('_')[1] for p in list_params]
        for x in tmp_elts_to_check:
            if x not in elts_to_check:
                elts_to_check.append(x)
        configs_dict = {c: [] for c in elts_to_check}
        for KEY in configs_dict.keys():
            for param in list_params:
                if KEY==param.split('_')[1]:
                    configs_dict[KEY].append(param)
        return configs_dict
    
    def cfgData2cfgDatasheet(self, config_list: list): #config_dict: dict):
        config_datasheet = dict()
        # for KEY, config_list in config_dict.items():
        config_datasheet = {}
        for VAL in config_list:
            [chk, k, sdd, sdf, slkh, slk, snc, sts, st, sgp, sg] = VAL.split('_')
            sdd_val = sdd[-1]
            sdf_val = sdf[-1]
            slkh_val = slkh[-1]
            slk_val = slk[-2:]
            snc_val = snc[-1]
            sts_val = sts[-1]
            st_val = st[-2:]
            sgp_val = sgp[-1]
            sg_val = sg[-2:]
            config_datasheet[VAL] = {
                "param_chk": k,
                "SDD": sdd_val,
                "SDF": sdf_val,
                "SLKH": slkh_val,
                "SLK": slk_val,
                "SNC": snc_val,
                "STS": sts_val,
                "ST": st_val,
                "SGP": sgp_val,
                "SG": sg_val
            }
            # print(config_datasheet[KEY])
        return config_datasheet

    
    def decodeOneConfigData(self, config: str):
        '''
         config is of the form "CHK_GAINs_SDD0_SDF0_SLK00_SLK10_SNC0_ST01_ST11_SG00_SG10"
        '''
        # DATA TO DECODE
        fembs = self.raw_data[config][0]
        rawdata = self.raw_data[config][1]
        # DISCUSS WITH SHANSHAN ABOUT THESE TWO CONFIGURATIONS
        cfg = self.raw_data[config][2] 
        fe_cfg = self.raw_data[config][3]
        # OUTPUT DICTIONARY
        out_dict = dict()
        decodedData = decodeRawData(fembs=fembs, rawdata=rawdata)
        for ichip in range(8):
            ASIC_ID = self.logs_dict['FE{}'.format(ichip)]
            out_dict[ASIC_ID] = dict()
            larasic = LArASIC_ana(dataASIC=decodedData[ichip], output_dir=self.CHKRES_dirs[ASIC_ID], chipID=ASIC_ID, tms=self.tms, param=config, generateQCresult=False, generatePlots=False)
            data_asic = larasic.runAnalysis()
            out_dict[ASIC_ID]['pedestal'] = data_asic['pedrms']['pedestal']['data']
            out_dict[ASIC_ID]['rms'] = data_asic['pedrms']['rms']['data']
            out_dict[ASIC_ID]['pospeak'] = data_asic['pulseResponse']['pospeak']['data']
            out_dict[ASIC_ID]['negpeak'] = data_asic['pulseResponse']['negpeak']['data']
        return (config, out_dict)
    
    def decode_CHKRES(self):
        # get CONFIGURATIONs
        datasheetCFG = self.cfgData2cfgDatasheet(config_list=self.pulseResp_params)

        allchip_data = dict()
        for ichip in range(8):
            ASIC_ID = self.logs_dict['FE{}'.format(ichip)]
            allchip_data[ASIC_ID] = {
                "logs":{
                    "date": self.logs_dict['date'],
                    "testsite": self.logs_dict['testsite'],
                    "env": self.logs_dict['env'],
                    "note": self.logs_dict['note'],
                    "DAT_SN": self.logs_dict['DAT_SN'],
                    "WIB_slot": self.logs_dict['DAT_on_WIB_slot']
                }
            }

        for param_cfg in self.pulseResp_params:
            print("configuration: {}".format(param_cfg))
            (cfg, cfg_chResp) = self.decodeOneConfigData(config=param_cfg)
            cfg_info = datasheetCFG[param_cfg]
            for ichip in range(8):
                ASIC_ID = self.logs_dict['FE{}'.format(ichip)]
                allchip_data[ASIC_ID][param_cfg] = cfg_chResp[ASIC_ID]
                allchip_data[ASIC_ID][param_cfg]['CFG_info'] = cfg_info
        
        # SAVE DATA FOR EACH CHIP TO JSON FILE
        for ichip in range(8):
            ASIC_ID = self.logs_dict['FE{}'.format(ichip)]
            dumpJson(output_path=self.CHKRES_dirs[ASIC_ID], output_name='QC_CHKRES', data_to_dump=allchip_data[ASIC_ID])

if __name__ == "__main__":
    root_path = '../../Data_BNL_CE_WIB_SW_QC'
    output_path = '../../Analyzed_BNL_CE_WIB_SW_QC'
    list_data_dir = [dir for dir in os.listdir(root_path) if '.zip' not in dir]
    for data_dir in list_data_dir:
        qc_checkres = QC_CHKRES(root_path=root_path, data_dir=data_dir, output_dir=output_path)
        qc_checkres.decode_CHKRES()
        
