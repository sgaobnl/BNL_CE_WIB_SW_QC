############################################################################################
#   created on 5/28/2024 @ 15:38
#   email: radofanantenan.razakamiandra@stonybrook.edu
#   Analyze the data in QC_PWR.bin
############################################################################################

import datetime
import os, sys, csv
import numpy as np
import pandas as pd
import json, pickle
from utils import printItem, createDirs, dumpJson, decodeRawData, LArASIC_ana, BaseClass
from utils import BaseClass_Ana

class QC_PWR(BaseClass):
    '''
        Raw data ("QC_PWR.bin") from one DAT board -> 8x decoded data for each LArASIC
    '''
    def __init__(self, root_path: str, data_dir: str, output_path: str, env='RT'):
        printItem('FE power consumption measurement')
        self.item = "QC_PWR"
        super().__init__(root_path=root_path, data_dir=data_dir, output_path=output_path, tms=1, QC_filename='QC_PWR.bin', env=env)
        if self.ERROR:
            return
        self.param_meanings = {
            'SDF0': 'seBuffOFF',
            'SDF1': 'seBuffON',
            'SNC0': '900mV',
            'SNC1': '200mV',
            'SDD0': 'sedcBufOFF',
            'SDD1': 'sedcBufON'
        }
        self.period = 500

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

    def decode_FE_PWR(self, getWaveforms=True):
        if self.ERROR:
            return
        print('----> Power consumption')
        data_by_config = self.getPowerConsumption()

        pwr_all_chips = dict()
        FE_IDs = []
        for ichip in range(8):
            oneChip_data = {
                "V": {"900mV": {}, "200mV": {}, "unit": "V"},
                "I": {"900mV": {}, "200mV": {}, "unit": "mA"},
                "P": {"900mV": {}, "200mV": {}, "unit": "mW"}
            }
            FE_ID = self.logs_dict['FE{}'.format(ichip)]
            FE_IDs.append(FE_ID)
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
        chResponseAllChips = self.analyzeChResponse(getWaveforms=getWaveforms)
        for ichip, chip_id in enumerate(pwr_all_chips.keys()):
            FE_output_dir = self.FE_outputDIRs[chip_id]
           
            tmpdata_onechip = pwr_all_chips[chip_id]
  
            oneChip_data = { }
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
            dumpJson(output_path=FE_output_dir, output_name="QC_PWR", data_to_dump=oneChip_data)
        return FE_IDs

    def analyzeChResponse(self, getWaveforms=True):
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
            decodedData = decodeRawData(fembs=fembs, rawdata=raw_data, period=self.period)
            ## decodedData is the decoded data for 8 chips
            ## One can use it if a further analysis on the channel response is needed during the power measurement
            for ichip in range(8):
                tmp_config = [c for c in param.split('_') if c!='PWR']
                config = {'SNC': tmp_config[2], "SDD": tmp_config[0], 'SDF': tmp_config[1]} # SNC : baseline 200mV or 900mV
                suffixFilename = '_'.join([self.param_meanings[config['SNC']], self.param_meanings[config['SDD']], self.param_meanings[config['SDF']]])
                # suffixFilename = '_'.join(tmp_config)
                chipID = self.logs_dict['FE{}'.format(ichip)]
                larasic = LArASIC_ana(dataASIC=decodedData[ichip], output_dir=self.FE_outputDIRs[chipID], chipID=chipID, tms=1, param=suffixFilename, generateQCresult=False, generatePlots=False, period=self.period)
                data_asic = larasic.runAnalysis(getWaveforms=getWaveforms, getPulseResponse=True)
                outdata[chipID][suffixFilename] = data_asic
        return outdata

class QC_PWR_analysis(BaseClass_Ana):
    '''
        This class is written to analyze the decoded data for each ASIC.
    '''
    def __init__(self, root_path: str, chipID: str, output_path: str):
        self.item = 'QC_PWR'
        self.tms = '01'
        print (self.item)
        super().__init__(root_path=root_path, chipID=chipID, item=self.item, output_path=output_path)
        self.root_path = root_path
        self.output_path = output_path

    def get_cfg(self, config: str, separateBL=False):
        splitted = config.split('_')
        if separateBL:
            BL = splitted[0]
            cfg = '\n'.join(splitted[1:])
            return BL, cfg
        else:
            cfg = ''
            if 'mV' in splitted[0]:
                cfg = '\n'.join(splitted[1:])
            else:
                cfg = '\n'.join(splitted)
            return cfg
    
    def get_V(self):
        v_vdda_dict = {'data': {}, 'unit': 'V'}
        v_vddo_dict = {'data': {}, 'unit': 'V'}
        v_vddp_dict = {'data': {}, 'unit': 'V'}
        for param in self.params:
            data = self.getoneConfigData(config=param)
            vdda = data['V']['VDDA']
            vddo = data['V']['VDDO']
            vddp = data['V']['VDDP']
            unitV = data['unitPWR']['V']
            v_vdda_dict['data'][param] = vdda
            v_vddo_dict['data'][param] = vddo
            v_vddp_dict['data'][param] = vddp
        return v_vdda_dict, v_vddo_dict, v_vddp_dict

    def get_I(self):
        I_vdda_dict = {'data': {}, 'unit': 'mA'}
        I_vddo_dict = {'data': {}, 'unit': 'mA'}
        I_vddp_dict = {'data': {}, 'unit': 'mA'}
        for param in self.params:
            data = self.getoneConfigData(config=param)
            vdda = data['I']['VDDA']
            vddo = data['I']['VDDO']
            vddp = data['I']['VDDP']
            # print(vddo, vddp)
            unitI = data['unitPWR']['I']
            I_vdda_dict['data'][param] = vdda
            I_vddo_dict['data'][param] = vddo
            I_vddp_dict['data'][param] = vddp
        return I_vdda_dict, I_vddo_dict, I_vddp_dict
    
    def get_P(self):
        P_vdda_dict = {'data': {}, 'unit': 'mW'}
        P_vddo_dict = {'data': {}, 'unit': 'mW'}
        P_vddp_dict = {'data': {}, 'unit': 'mW'}
        P_total_dict = {'data': {}, 'unit': 'mW'}
        for param in self.params:
            data = self.getoneConfigData(config=param)
            vdda = data['P']['VDDA']
            vddo = data['P']['VDDO']
            vddp = data['P']['VDDP']
            unitP = data['unitPWR']['P']
            P_vdda_dict['data'][param] = vdda
            P_vddo_dict['data'][param] = vddo
            P_vddp_dict['data'][param] = vddp
            P_total_dict['data'][param] = vdda + vddo + vddp
        return P_vdda_dict, P_vddo_dict, P_vddp_dict, P_total_dict

    def PWR_consumption_ana(self):
        V_vdda, V_vddo, V_vddp = self.get_V()
        I_vdda, I_vddo, I_vddp = self.get_I()
        P_vdda, P_vddo, P_vddp, P_total = self.get_P()
        V_list = [('vdda', V_vdda), ('vddo', V_vddo), ('vddp', V_vddp)]
        I_list = [('vdda', I_vdda), ('vddo', I_vddo), ('vddp', I_vddp)]
        P_list = [('vdda', P_vdda), ('vddo', P_vddo), ('vddp', P_vddp), ('Total Power', P_total)]
        outdata = {'testItem': [], 'cfgs': [], 'cfg_item': [], 'value': []}
        for i in range(len(V_list)):
            Vvdd_cfg = V_list[i][0]
            v_item = 'V (V/LArASIC)'
            Vvdd_meas = V_list[i][1]['data']
            for key, val in Vvdd_meas.items():
                outdata['testItem'].append(v_item)
                outdata['cfgs'].append(key)
                outdata['cfg_item'].append(Vvdd_cfg)
                outdata['value'].append(val)
            #
            Pvdd_cfg = P_list[i][0]
            P_item = 'P (mW/LArASIC)'
            Pvdd_meas = P_list[i][1]['data']
            for key, val in Pvdd_meas.items():
                outdata['testItem'].append(P_item)
                outdata['cfgs'].append(key)
                outdata['cfg_item'].append(Pvdd_cfg)
                outdata['value'].append(val)
            #
            Ivdd_cfg = I_list[i][0]
            I_item = 'I (mA/LArASIC)'
            Ivdd_meas = I_list[i][1]['data']
            for key, val in Ivdd_meas.items():
                outdata['testItem'].append(I_item)
                outdata['cfgs'].append(key)
                outdata['cfg_item'].append(Ivdd_cfg)
                outdata['value'].append(val)
        chresp_dict = {'testItem': [], 'cfgs': [], 'cfg_item': [], 'chn': [], 'value': []}
        for item in ['rms', 'pedestal', 'pospeak', 'negpeak']:
            chres_data = self.ChResp_ana(item=item)
            for config, listval in chres_data.items():
                testItems = ['ChResp' for _ in range(len(listval))]
                cfgs = [config for _ in range(len(listval))]
                cfg_item = [item for _ in range(len(listval))]
                chns = [i for i in range(len(listval))]
                values = listval
                # chresp_dict = {'testItem': testItems, 'cfgs': cfgs, 'cfg_item': cfg_item, 'chn': chns, 'value': values}
                chresp_dict['testItem'] += testItems
                chresp_dict['cfgs'] += cfgs
                chresp_dict['cfg_item'] += cfg_item
                chresp_dict['chn'] += chns
                chresp_dict['value'] += values
        
        chresp_df = pd.DataFrame(chresp_dict)
        pwr_cons_df = pd.DataFrame(outdata)
        return pwr_cons_df, chresp_df
    
    def ChResp_ana(self, item='rms'):
        '''
            item could be 'pedestal', 'rms'
        '''
        chipData = {'200mV': {}, '900mV': {}}
        colors = ['r', 'b']
        ylim = []
        if item=='rms':
            ylim = [0, 25]
        elif item=='pedestal':
            ylim = [500, 10000]
        itemData = dict()
        for param in self.params:
            BL, cfg = self.get_cfg(config=param, separateBL=True)
            data = self.getoneConfigData(config=param)
            itemData[param] = data[item]
        return itemData

    
    def run_Ana(self, path_to_statAna=""):
        if self.ERROR:
            print ("error")
            return None

        # Get raw measurements
        pwr_df, chresp_df = self.PWR_consumption_ana()
        results_CFGs = []

        if True:
            unique_cfgs = pwr_df['cfgs'].unique()
            for cfg in unique_cfgs:
                # Get power data
                cfg_pwr_data = pwr_df[pwr_df['cfgs']==cfg].copy()
                
                # Get channel response data  
                cfg_chresp_data = chresp_df[chresp_df['cfgs']==cfg].copy()

                # Build power parameters string
                pwr_params = []
                for _, row in cfg_pwr_data.iterrows():
                    param = '_'.join([row['cfg_item'], row['testItem'].split(' ')[0]])
                    pwr_params.append('{} = {}'.format(param, row['value']))

                # Build channel response strings
                ch_results = []
                for ichn in range(16):
                    ch_data = cfg_chresp_data[cfg_chresp_data['chn']==ichn]
                    posAmp = float(ch_data[ch_data['cfg_item']=='pospeak']['value'].iloc[0])
                    negAmp = float(ch_data[ch_data['cfg_item']=='negpeak']['value'].iloc[0])
                    ped = float(ch_data[ch_data['cfg_item']=='pedestal']['value'].iloc[0])
                    rms = float(ch_data[ch_data['cfg_item']=='rms']['value'].iloc[0])
                    ch_results.append(f"CH{ichn}=(ped={ped};rms={rms};posAmp={posAmp};negAmp={negAmp})")

                results_CFGs.append([f'Test_{self.tms}_Power_Consumption', cfg] + pwr_params + ch_results)

        return results_CFGs
    

if __name__ =='__main__':
    root_path = "E:/B009T0008/"
    output_path = root_path + "Ana"
    data_dir = "Time_20250527114445_DUT_0000_1001_2002_3003_4004_5005_6006_7007"
    env = 'RT'
    qc_pwr = QC_PWR(root_path=root_path, data_dir=data_dir, output_dir=output_path, env=env)
    qc_pwr.decode_FE_PWR(getWaveforms=True)


