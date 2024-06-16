############################################################################################
#   created on 6/11/2024 @ 18:49
#   email: radofanantenan.razakamiandra@stonybrook.edu
#   Analyze the data in QC_RMS.bin
############################################################################################

import os, sys, pickle
import numpy as np
from utils import dumpJson, createDirs, decodeRawData, printItem, LArASIC_ana
import matplotlib.pyplot as plt

class RMS:
    def __init__(self, root_path: str, data_dir: str, output_path: str):
        self.tms = 5
        printItem("FE noise measurement")
        with open('/'.join([root_path, data_dir, 'QC_RMS.bin']), 'rb') as fn:
            self.raw_data = pickle.load(fn)
        self.logs_dict = self.raw_data['logs']
        createDirs(logs_dict=self.logs_dict, output_dir=output_path)
        FE_outputDIRs = ['/'.join([output_path, self.logs_dict['FE{}'.format(ichip)]]) for ichip in range(8)]
        self.RMS_dirs = {self.logs_dict['FE{}'.format(ichip)]: '/'.join([FE_outputDIRs[ichip], 'RMS']) for ichip in range(8)}
        for key, val in self.RMS_dirs.items():
            try:
                os.mkdir(val)
            except OSError:
                pass
        self.config_keys = [key for key in self.raw_data.keys() if key!='logs']
        self.CFG_datasheet = self.getCFGs()
    
    def decodeCFG(self, config: str):
        cfg_split = config.split('_')
        cfg_datasheet = dict()
        sdd, sdf, slkh, slk, snc, sts, st, sgp, sg = '', '', '', '', '', '', '', '', ''
        if len(cfg_split)==10:
            [chk, sdd, sdf, slkh, slk, snc, sts, st, sgp, sg] = cfg_split
        elif len(cfg_split)==11:
            [chk, k, sdd, sdf, slkh, slk, snc, sts, st, sgp, sg] = cfg_split
            cfg_datasheet['param_chk'] = k
        cfg_datasheet['SDD'] = sdd[-1]
        cfg_datasheet['SDF'] = sdf[-1]
        cfg_datasheet['SLKH'] = slkh[-1]
        cfg_datasheet['SLK'] = slk[-2:]
        cfg_datasheet['SNC'] = snc[-1]
        cfg_datasheet['STS'] = sts[-1]
        cfg_datasheet['ST'] = st[-2:]
        cfg_datasheet['SGP'] = sgp[-1]
        cfg_datasheet['SG'] = sg[-2:]
        return {config: cfg_datasheet}

    def getCFGs(self):
        cfg_dict = dict()
        # cfg_list = [l for l in list(self.raw_data.keys()) if (l!='logs')]
        # for config in cfg_list:
        for config in self.config_keys:
            tmp_cfg = self.decodeCFG(config=config)
            cfg_dict[config]  = tmp_cfg[config]
        return cfg_dict

    def decode_oneRMS(self, config: str):
        fembs = self.raw_data[config][0]
        raw_data = self.raw_data[config][1]
        cfg_info = self.raw_data[config][2]
        decodedRMS = decodeRawData(fembs=fembs, rawdata=raw_data)
        out_dict = {self.logs_dict['FE{}'.format(ichip)]: dict() for ichip in range(8)}
        for ichip in range(8):
            FE_ID = self.logs_dict['FE{}'.format(ichip)]
            larasic = LArASIC_ana(dataASIC=decodedRMS[ichip], output_dir=self.RMS_dirs[FE_ID], chipID=FE_ID, tms=self.tms, param=config, generatePlots=False, generateQCresult=False)
            pedrms = larasic.runAnalysis(getPulseResponse=False, isRMSNoise=True)
            out_dict[FE_ID][config] = {
                'pedestal': pedrms['pedrms']['pedestal']['data'],
                'rms': pedrms['pedrms']['rms']['data']
            }
        return out_dict

    def decodeRMS(self):
        out_dict = {self.logs_dict['FE{}'.format(ichip)]: dict() for ichip in range(8)}
        for config in self.config_keys:
            print("configuration : {}".format(config))
            tmp = self.decode_oneRMS(config=config) 
            for ichip in range(8):
                FE_ID = self.logs_dict['FE{}'.format(ichip)]
                out_dict[FE_ID][config] = tmp[FE_ID][config]
        logs = {
            "date": self.logs_dict['date'],
            "testsite": self.logs_dict['testsite'],
            "env": self.logs_dict['env'],
            "note": self.logs_dict['note'],
            "DAT_SN": self.logs_dict['DAT_SN'],
            "WIB_slot": self.logs_dict['DAT_on_WIB_slot']
        }
        for ichip in range(8):
            pedrms_dict = {"logs": logs}
            FE_ID = self.logs_dict['FE{}'.format(ichip)]
            for config in self.config_keys:
                # pedrms_dict[FE_ID][config] = dict()
                pedrms_dict[config] = dict()
                pedrms_dict[config]['CFG'] = self.CFG_datasheet[config]
                for key in out_dict[FE_ID][config].keys():
                    pedrms_dict[config][key] = out_dict[FE_ID][config][key]
            dumpJson(output_path=self.RMS_dirs[FE_ID], output_name='RMS_Noise', data_to_dump=pedrms_dict)

if __name__ == '__main__':
    root_path = '../../Data_BNL_CE_WIB_SW_QC'
    output_path = '../../Analyzed_BNL_CE_WIB_SW_QC'
    list_data_dir = [dir for dir in os.listdir(root_path) if '.zip' not in dir]
    for i, data_dir in enumerate(list_data_dir):
        rms = RMS(root_path=root_path, data_dir=data_dir, output_path=output_path)
        rms.decodeRMS()