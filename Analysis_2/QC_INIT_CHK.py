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

class QC_INIT_CHK(BaseClass):
    '''
        Raw data ("QC_PWR.bin") from one DAT board -> 8x decoded data for each LArASIC
    '''
    def __init__(self, root_path: str, data_dir: str, output_path: str, env='RT'):
        printItem('Initialization checkout')
        self.item = "QC_INIT_CHK"
        super().__init__(root_path=root_path, data_dir=data_dir, output_path=output_path, tms=1, QC_filename='QC_INIT_CHK.bin', env=env)
        if self.ERROR:
            return
        tmps = root_path.split("/")
        for tmp in tmps:
            if "B" in tmp[0] and "T" in tmp[4]:
                self.tray_id = tmp
                break

        self.param_meanings = [
            'ASICDAC_47mV_CHK',
            'ASICDAC_47mV_CHK_x10',
            'ASICDAC_47mV_CHK_x18',
            'ASICDAC_47mV_RMS',
            'DIRECT_PLS_CHK',
            'DIRECT_PLS_RMS',
            'ASICDAC_CALI_CHK',
            'ASICDAC_CALI_RMS'
        ]
        self.period = 500

    def getPowerConsumption(self):
        data_by_config = {self.logs_dict['FE{}'.format(ichip)]: {} for ichip in range(8)}
        for param in self.params:
            if param not in self.param_meanings:
                continue
            for KEY_feid in data_by_config.keys():
                data_by_config[KEY_feid][param] = dict()
        
        for param in self.params:
            if param not in self.param_meanings:
                continue
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

    def decode_FE_PWR(self, getWaveforms=False):
        if self.ERROR:
            return
        print('----> Power consumption')
        data_by_config = self.getPowerConsumption()

        pwr_all_chips = dict()
        FE_IDs = []
        ADC_IDs = []
        CD_IDs = []
        for ichip in range(8):
            oneChip_data = { } 
            for param in self.param_meanings:
                oneChip_data[param] = {} 

            FE_ID = self.logs_dict['FE{}'.format(ichip)]
            FE_IDs.append(FE_ID)
            ADC_ID = self.logs_dict['ADC{}'.format(ichip)]
            ADC_IDs.append(ADC_ID)
            CD_ID = self.logs_dict['CD{}'.format(int(ichip//4))]
            CD_IDs.append(CD_ID)

            for param in self.params:
                if param not in self.param_meanings:
                    continue
                configs = [conf for conf in param.split('_') if conf!='PWR']
                data_config = data_by_config[FE_ID][param]
                V = {}
                I = {}
                P = {}
                for pwr_rail in ['VDDA', 'VDDO', 'VDDP']:
                    V[pwr_rail] = np.round(data_config[pwr_rail][0], 4)
                    I[pwr_rail] = np.round(data_config[pwr_rail][1], 4)
                    P[pwr_rail] = np.round(data_config[pwr_rail][2], 4)
                oneChip_data[param]["V"] = V
                oneChip_data[param]["I"] = I
                oneChip_data[param]["P"] = P

            pwr_all_chips[FE_ID] = oneChip_data

        # update data with the link to the plots and save everything in a json file
        chResponseAllChips = self.analyzeChResponse(getWaveforms=True)
        for ichip, chip_id in enumerate(pwr_all_chips.keys()):
            FE_output_dir = self.FE_outputDIRs[chip_id]
           
            tmpdata_onechip = pwr_all_chips[chip_id]
  
            oneChip_data = {
                'logs' : {
                    "item_name" : self.item,
                    "RTS_timestamp" : self.logs_dict['FE{}'.format(ichip)],
                    'RTS_Property_ID' : 'BNL001',
#                    'RTS chamber' : 1,
                    "date": self.logs_dict['date'],
                    "FE_ID":FE_IDs[ichip],
                    "tester": self.logs_dict['tester'],
                    "testsite": self.logs_dict['testsite'],
                    "env": self.logs_dict['env'],
                    "note": self.logs_dict['note'],
                    "DAT_Rev": self.logs_dict['DAT_Revision'],
                    "DAT_SN": self.logs_dict['DAT_SN'],
                    "WIB_slot": self.logs_dict['DAT_on_WIB_slot'],
                    "Tray_ID":self.tray_id,
                    "CD_on_DAT":CD_IDs[ichip],
                    "ADC_on_DAT":ADC_IDs[ichip],

                }
            }
            pwr_params = ['V', 'I', 'P']
            params_units = {'V': 'V', 'I': 'mA', 'P': 'mW'}
            for param in self.param_meanings:
                oneChip_data[param] = {} 
            for param in self.param_meanings:
                if True:
                    tmpconfig = param
                    oneChip_data[tmpconfig]['CFG_info'] = {}
                    for pwr_param in pwr_params:
                        oneChip_data[tmpconfig][pwr_param] = tmpdata_onechip[tmpconfig][pwr_param]
                    oneChip_data[tmpconfig]['unitPWR'] = params_units
                    oneChip_data[tmpconfig]['pedestal'] = chResponseAllChips[chip_id][tmpconfig]["pedrms"]['pedestal']['data']
                    oneChip_data[tmpconfig]['rms'] = chResponseAllChips[chip_id][tmpconfig]['pedrms']['rms']['data']
                    oneChip_data[tmpconfig]['pospeak'] = chResponseAllChips[chip_id][tmpconfig]['pulseResponse']['pospeak']['data']
                    oneChip_data[tmpconfig]['negpeak'] = chResponseAllChips[chip_id][tmpconfig]['pulseResponse']['negpeak']['data']
            dumpJson(output_path=FE_output_dir, output_name="QC_INIT_CHK", data_to_dump=oneChip_data)
        return FE_IDs

    def analyzeChResponse(self, getWaveforms=True):
        '''
            For each configuration corresponds a raw data of the channel response. 
            This method aims to analyze the channel response during the power measuremet
        '''
        print('---> Channel Response')
        outdata = {self.logs_dict['FE{}'.format(ichip)]: {} for ichip in range(8)}
        for param in self.params:
            if param not in self.param_meanings:
                continue
            print('configuration : {}'.format(param))
            fembs = self.raw_data[param][0]
            raw_data = self.raw_data[param][1]
            decodedData = decodeRawData(fembs=fembs, rawdata=raw_data, period=self.period)
            for ichip in range(8):
                tmp_config = [param]
                suffixFilename = param
                chipID = self.logs_dict['FE{}'.format(ichip)]
                larasic = LArASIC_ana(dataASIC=decodedData[ichip], output_dir=self.FE_outputDIRs[chipID], chipID=chipID, tms=1, param=suffixFilename, generateQCresult=False, generatePlots=False, period=self.period)
                data_asic = larasic.runAnalysis(getWaveforms=getWaveforms, getPulseResponse=True)
                outdata[chipID][suffixFilename] = data_asic
        return outdata

class QC_INIT_CHKAna(BaseClass_Ana):
    '''
        This class is written to analyze the decoded data for each ASIC.
    '''
    def __init__(self, root_path: str, chipID: str, output_path: str):
        self.item = 'QC_INIT_CHK'
        self.tms = '00'
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
    
    def run_Ana(self):
        if self.ERROR:
            print ("error")
            return None

        results_CFGs = []
        for onekey in self.data["logs"].keys():
            if 'item_name' not in onekey:
                results_CFGs.append([onekey,self.data["logs"][onekey]])
        print (self.data["logs"]['item_name'])
        # Get raw measurements
        pwr_df, chresp_df = self.PWR_consumption_ana()

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

                results_CFGs.append([f'Test_{self.tms}_QC_INIT_CHK', cfg] + pwr_params + ch_results)
        return results_CFGs


if __name__ =='__main__':
    root_path = "E:/B009T0008/"
    output_path = root_path + "Ana"
    data_dir = "Time_20250527114445_DUT_0000_1001_2002_3003_4004_5005_6006_7007"
    env = 'RT'
    #qc_selection = json.load(open("./qc_selection.json"))
    qc_pwr = QC_PWR(root_path=root_path, data_dir=data_dir, output_dir=output_path, env=env)
    qc_pwr.decode_FE_PWR(getWaveforms=True)

