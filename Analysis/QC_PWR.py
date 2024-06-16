############################################################################################
#   created on 5/28/2024 @ 15:38
#   email: radofanantenan.razakamiandra@stonybrook.edu
#   Analyze the data in QC_PWR.bin
############################################################################################

import datetime
import os, sys
import numpy as np
import matplotlib.pyplot as plt
import json, pickle
from utils import printItem, createDirs, dumpJson, decodeRawData, LArASIC_ana, BaseClass

class QC_PWR(BaseClass):
    '''
        Raw data ("QC_PWR.bin") from one DAT board -> 8x decoded data for each LArASIC
    '''
    def __init__(self, root_path: str, data_dir: str, output_dir: str):
        printItem('FE power consumption measurement')
        super().__init__(root_path=root_path, data_dir=data_dir, output_path=output_dir, tms=1, QC_filename='QC_PWR.bin')
        #
        self.param_meanings = {
            'SDF0': 'seBuffOFF',
            'SDF1': 'seBuffON',
            'SNC0': '900mV',
            'SNC1': '200mV',
            'SDD0': 'sedcBufOFF',
            'SDD1': 'sedcBufON'
        }

    def isParamInRange(self, paramVal=0, rangeParam=[0, 0]):
        flag = True
        if (paramVal>rangeParam[0]) & (paramVal<rangeParam[1]):
            flag = True
        else:
            flag = False
        return flag

    def getPowerConsumption(self):
        data_by_config = {self.logs_dict['FE{}'.format(ichip)]: {} for ichip in range(8)}
        for param in self.params:
            for KEY_feid in data_by_config.keys():
                data_by_config[KEY_feid][param] = dict()
        
        for param in self.params:
            print('configuration : {}'.format(param))
            data_oneconfig = self.raw_data[param][3]
            for ichip in range(8):
                FE_ID = self.logs_dict['FE{}'.format(ichip)]
                for val in data_oneconfig.keys():
                    if 'FE{}'.format(ichip) in val:
                        keyname = val.split('_')[1]
                        if keyname=="VPPP":
                            keyname = "VDDP"
                        data_by_config[FE_ID][param][keyname] = data_oneconfig[val]
        return data_by_config

    def decode_FE_PWR(self):
        print('----> Power consumption')
        data_by_config = self.getPowerConsumption()

        pwr_all_chips = dict()
        for ichip in range(8):
            oneChip_data = {
                "V": {"900mV": {}, "200mV": {}, "unit": "V"},
                "I": {"900mV": {}, "200mV": {}, "unit": "mA"},
                "P": {"900mV": {}, "200mV": {}, "unit": "mW"}
            }
            FE_ID = self.logs_dict['FE{}'.format(ichip)]
            for param in self.params:
                configs = [conf for conf in param.split('_') if conf!='PWR']
                BL = self.param_meanings[configs[2]]
                outputConfig = '_'.join([self.param_meanings[configs[0]], self.param_meanings[configs[1]]])
                data_config = data_by_config[FE_ID][param]
                V = {}
                I = {}
                P = {}
                for pwr_rail in ['VDDA', 'VDDO', 'VDDP']:
                    V[pwr_rail] = np.round(data_config[pwr_rail][0], 4)
                    I[pwr_rail] = np.round(data_config[pwr_rail][1], 4)
                    P[pwr_rail] = np.round(data_config[pwr_rail][2], 4)
                oneChip_data["V"][self.param_meanings[configs[2]]][outputConfig] = V
                oneChip_data["I"][self.param_meanings[configs[2]]][outputConfig] = I
                oneChip_data["P"][self.param_meanings[configs[2]]][outputConfig] = P

            pwr_all_chips[FE_ID] = oneChip_data

        # update data with the link to the plots and save everything in a json file
        chResponseAllChips = self.analyzeChResponse()
        for ichip, chip_id in enumerate(pwr_all_chips.keys()):
            FE_output_dir = self.FE_outputDIRs[chip_id]
           
            tmpdata_onechip = pwr_all_chips[chip_id]
  
            oneChip_data = {
                "logs":{
                    "date": self.logs_dict['date'],
                    "testsite": self.logs_dict['testsite'],
                    "env": self.logs_dict['env'],
                    "note": self.logs_dict['note'],
                    "DAT_SN": self.logs_dict['DAT_SN'],
                    "WIB_slot": self.logs_dict['DAT_on_WIB_slot']
                }
            }
            Baselines = ['200mV', '900mV']
            params = ['V', 'I', 'P']
            params_units = {'V': 'V', 'I': 'mA', 'P': 'mW'}
            configs_out = tmpdata_onechip['V']['900mV'].keys()
            for BL in Baselines:
                for config in configs_out:
                    tmpconfig = '_'.join([BL, config])
                    oneChip_data[tmpconfig] = {}
        
            for BL in Baselines:
                for config in configs_out:
                    tmpconfig = '_'.join([BL, config])
                    oneChip_data[tmpconfig]['CFG_info'] = {}
                    for param in params:
                        oneChip_data[tmpconfig][param] = tmpdata_onechip[param][BL][config]
                    oneChip_data[tmpconfig]['unitPWR'] = params_units
                    oneChip_data[tmpconfig]['pedestal'] = chResponseAllChips[chip_id][tmpconfig]["pedrms"]['pedestal']['data']
                    oneChip_data[tmpconfig]['rms'] = chResponseAllChips[chip_id][tmpconfig]['pedrms']['rms']['data']
                    oneChip_data[tmpconfig]['pospeak'] = chResponseAllChips[chip_id][tmpconfig]['pulseResponse']['pospeak']['data']
                    oneChip_data[tmpconfig]['negpeak'] = chResponseAllChips[chip_id][tmpconfig]['pulseResponse']['negpeak']['data']
            dumpJson(output_path=FE_output_dir, output_name="QC_PWR_data", data_to_dump=oneChip_data)

    def analyzeChResponse(self):
        '''
            For each configuration corresponds a raw data of the channel response. 
            This method aims to analyze the channel response during the power measuremet
        '''
        print('---> Channel Response')
        outdata = {self.logs_dict['FE{}'.format(ichip)]: {} for ichip in range(8)}
        for param in self.params:
            print('configuration : {}'.format(param))
            fembs = self.raw_data[param][0]
            raw_data = self.raw_data[param][1]
            decodedData = decodeRawData(fembs=fembs, rawdata=raw_data)
            ## decodedData is the decoded data for 8 chips
            ## One can use it if a further analysis on the channel response is needed during the power measurement
            for ichip in range(8):
                tmp_config = [c for c in param.split('_') if c!='PWR']
                config = {'SNC': tmp_config[2], "SDD": tmp_config[0], 'SDF': tmp_config[1]} # SNC : baseline 200mV or 900mV
                suffixFilename = '_'.join([self.param_meanings[config['SNC']], self.param_meanings[config['SDD']], self.param_meanings[config['SDF']]])
                # suffixFilename = '_'.join(tmp_config)
                chipID = self.logs_dict['FE{}'.format(ichip)]
                larasic = LArASIC_ana(dataASIC=decodedData[ichip], output_dir=self.FE_outputDIRs[chipID], chipID=chipID, tms=1, param=suffixFilename, generateQCresult=False, generatePlots=False)
                data_asic = larasic.runAnalysis()
                outdata[chipID][suffixFilename] = data_asic
        return outdata

if __name__ =='__main__':
    root_path = '../../Data_BNL_CE_WIB_SW_QC'
    output_path = '../../Analyzed_BNL_CE_WIB_SW_QC'
    list_data_dir = [dir for dir in os.listdir(root_path) if '.zip' not in dir]
    qc_selection = json.load(open("qc_selection.json"))
    for data_dir in list_data_dir:
        t0 = datetime.datetime.now()
        print('start time : {}'.format(t0))
        qc_pwr = QC_PWR(root_path=root_path, data_dir=data_dir, output_dir=output_path)
        qc_pwr.decode_FE_PWR()
        tf = datetime.datetime.now()
        print('end time : {}'.format(tf))
        deltaT = (tf - t0).total_seconds()
        print("Decoding time : {} seconds".format(deltaT))