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
from utils import BaseClass_Ana

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
        self.period = 500

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

    def decode_FE_PWR(self, getWaveforms=True):
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
        chResponseAllChips = self.analyzeChResponse(getWaveforms=getWaveforms)
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
                larasic = LArASIC_ana(dataASIC=decodedData[ichip], output_dir=self.FE_outputDIRs[chipID], chipID=chipID, tms=1, param=suffixFilename, generateQCresult=False, generatePlots=True, period=self.period)
                data_asic = larasic.runAnalysis(getWaveforms=getWaveforms, getPulseResponse=True)
                outdata[chipID][suffixFilename] = data_asic
        return outdata

class QC_PWR_analysis(BaseClass_Ana):
    def __init__(self, root_path: str, chipID: str, output_path: str):
        self.item = 'QC_PWR'
        super().__init__(root_path=root_path, chipID=chipID, item=self.item, output_path=output_path)
        # print(self.params)

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

    def plot_PWR(self, data_dict_list: list, xlabel: str, ylabel: str, item_to_plot: str):
        colors = [('r', 'm'), ('b', 'black'), ('g', 'y'), ('r', 'gray')]
        plt.figure(figsize=(10, 8))
        i = 0
        for item, data_dict in data_dict_list:
            # print(data_dict['data'].keys())
            # config_list = [self.get_cfg(config=c) for c in list(data_dict['data'].keys())]
            # data = list(data_dict['data'].values())
            # plt.plot(config_list, data, marker='.', markersize=15, label=item)
            BL_200mV = [c for c in data_dict['data'].keys() if '200mV' in c]
            cfg200mV = [self.get_cfg(config=c) for c in BL_200mV]
            BL_900mV = [c for c in data_dict['data'].keys() if '900mV' in c]
            cfg900mV = [self.get_cfg(config=c) for c in BL_900mV]
            data200mV = {c : data_dict['data'][c] for c in BL_200mV}
            data900mV = {c : data_dict['data'][c] for c in BL_900mV}
            plt.plot(cfg200mV, list(data200mV.values()), marker='.', markersize=15, label='{} : BL 200mV'.format(item), color=colors[i][0])
            plt.plot(cfg900mV, list(data900mV.values()), marker='*', markersize=7, label='{} : BL 900mV'.format(item), color=colors[i][1])
            i += 1
        plt.xlabel(xlabel, fontdict={'weight': 'bold'}, loc='right')
        plt.ylabel(ylabel, fontdict={'weight': 'bold'}, loc='top')
        plt.title(item_to_plot)
        plt.legend()
        plt.grid(True)
        plt.savefig('/'.join([self.output_dir, 'PWR_' + item_to_plot + '.png']))
        plt.close()
        # sys.exit()

    def PWR_consumption_ana(self):
        V_vdda, V_vddo, V_vddp = self.get_V()
        I_vdda, I_vddo, I_vddp = self.get_I()
        P_vdda, P_vddo, P_vddp, P_total = self.get_P()
        V_list = [('VDDA', V_vdda), ('VDDO', V_vddo), ('VDDP', V_vddp)]
        I_list = [('VDDA', I_vdda), ('VDDO', I_vddo), ('VDDP', I_vddp)]
        P_list = [('VDDA', P_vdda), ('VDDO', P_vddo), ('VDDP', P_vddp), ('Total Power', P_total)]
        self.plot_PWR(data_dict_list=V_list, xlabel='Configurations', ylabel='Voltage ({}/LArASIC)'.format(V_vdda['unit']), item_to_plot='Voltage')
        self.plot_PWR(data_dict_list=I_list, xlabel='Configurations', ylabel='Current ({}/LArASIC)'.format(I_vdda['unit']), item_to_plot='Current')
        self.plot_PWR(data_dict_list=P_list, xlabel='Configurations', ylabel='Power ({}/LArASIC)'.format(P_vdda['unit']), item_to_plot='Power')
        # self.plot_PWR(data_dict_list=[('Total power consumption', P_total)], xlabel='Configurations', ylabel='Total power ({})'.format(P_total['unit']), item_to_plot='Total_power_cons')
    
    def ChResp_ana(self, item_to_plot: str):
        '''
            item_to_plot could be 'pedestal', 'rms', 'pospeak', or 'negpeak'
        '''
        chipData = {'200mV': {}, '900mV': {}}
        for param in self.params:
            BL, cfg = self.get_cfg(config=param, separateBL=True)
            data = self.getoneConfigData(config=param)
            meanValue, stdValue, minValue, maxValue = self.getCHresp_info(oneChipData=data[item_to_plot])
            chipData[BL][cfg] = {'mean': meanValue, 'std': stdValue, 'min': minValue, 'max': maxValue}
        for BL in ['200mV', '900mV']:
            plt.figure(figsize=(8,7))
            configs = list(chipData[BL].keys())
            for cfg in configs:
                # mean and std
                plt.errorbar(x=cfg, y=chipData[BL][cfg]['mean'], yerr=chipData[BL][cfg]['std'], color='b', fmt='.', capsize=4)
                plt.scatter(x=cfg, y=chipData[BL][cfg]['mean'], color='b', marker='.', s=100)
                if item_to_plot=='negpeak' and BL=='900mV':
                    # min value
                    plt.scatter(x=cfg, y=chipData[BL][cfg]['min'], color='r', marker='.', s=100)
                # max value
                plt.scatter(x=cfg, y=chipData[BL][cfg]['max'], color='r', marker='.', s=100)
            meanvalues = [chipData[BL][cfg]['mean'] for cfg in configs]
            plt.plot(configs, meanvalues, color='black')
            plt.xlabel('Configurations', loc='right', fontdict={'weight': 'bold'})
            plt.ylabel('{} (ADC bit)'.format(item_to_plot), loc='top', fontdict={'weight': 'bold'})
            plt.title('{} {}'.format(item_to_plot, BL))
            plt.grid(True)
            plt.savefig('/'.join([self.output_dir, 'PWR_{}_{}.png'.format(item_to_plot, BL)]))
            plt.close()

    def Mean_ChResp_ana(self, BL: str):
        configs = []
        pedestals = []
        pospeaks = []
        negpeaks = []
        stdppeaks, stdnpeaks = [], []
        for param in self.params:
            _BL, cfg = self.get_cfg(config=param, separateBL=True)
            if _BL==BL:
                data = self.getoneConfigData(config=param)
                # items_in_data = ['pedestal', 'rms', 'pospeak', 'negpeak']
                items_in_data = ['pospeak', 'negpeak']
                meanppeak, stdppeak, minppeak, maxppeak = self.getCHresp_info(oneChipData=data['pospeak'])
                meannpeak, stdnpeak, minnpeak, maxnpeak = self.getCHresp_info(oneChipData=data['negpeak'])
                meanpedestal, stdpedestal, minpedestal, maxpedestal = self.getCHresp_info(oneChipData=data['pedestal'])
                configs.append('\n'.join([_BL, cfg]))
                pedestals.append(meanpedestal)
                pospeaks.append(meanppeak)
                negpeaks.append(-meannpeak)
                stdppeaks.append(stdppeak)
                stdnpeaks.append(stdnpeak)

        if BL=='200mV':
            plt.figure(figsize=(8,8))
            # plt.plot(configs, pedestals, 'b.-', label='Pedestal')
            plt.plot(configs, pospeaks, 'r.-', markersize=15, label="Positive peaks")
            plt.ylim([np.mean(pedestals)*2, np.max(pospeaks)+np.mean(pedestals)])
            plt.xlabel("Configurations", loc='right', fontdict={'weight':'bold'})
            plt.ylabel("Amplitude (ADC bit)", loc='top', fontdict={'weight': 'bold'})
            plt.legend()
            plt.title('Pulse Response: Baseline = {}'.format(BL))
            plt.grid(True)
            plt.savefig('/'.join([self.output_dir, '{}_{}_pulseResp.png'.format(self.item_to_ana, BL)]))
            plt.close()
            # sys.exit()
        elif BL=='900mV':
            plt.figure(figsize=(8,8))
            # plt.plot(configs, pedestals, 'b.-', label="Pedestal")
            plt.errorbar(x=configs, y=pospeaks, yerr=stdppeaks, color='r', fmt='.', markersize=5, label='Positive peaks', capsize=4)
            plt.plot(configs, pospeaks, color='black')
            plt.errorbar(x=configs, y=negpeaks, yerr=stdnpeaks, color='g', fmt='.', markersize=5, label='Negative peaks', capsize=4)
            plt.plot(configs, negpeaks)
            plt.axline((0,0), (1,1), color='black', linestyle='--')
            plt.xlabel("Configurations", loc='right', fontdict={'weight':'bold'})
            plt.ylabel("Amplitude (ADC bit)", loc='top', fontdict={'weight': 'bold'})
            plt.legend(loc='right')
            plt.title('Pulse Response : Baseline = {}'.format(BL))
            plt.grid(True)
            plt.savefig('/'.join([self.output_dir, '{}_{}_pulseResp.png'.format(self.item_to_ana, BL)]))
            plt.close()
            # sys.exit()

    def runAnalysis(self):
        self.PWR_consumption_ana()
        chresp_items = ['pedestal', 'rms']
        for item_to_plot in chresp_items:
            self.ChResp_ana(item_to_plot=item_to_plot)
        for BL in ['200mV', '900mV']:
            self.Mean_ChResp_ana(BL=BL)

if __name__ =='__main__':
    # root_path = '../../Data_BNL_CE_WIB_SW_QC'
    # root_path = '../../B010T0004'
    # output_path = '../../Analyzed_BNL_CE_WIB_SW_QC'
    # # list_data_dir = [dir for dir in os.listdir(root_path) if '.zip' not in dir]
    # list_data_dir = [dir for dir in os.listdir(root_path) if (os.path.isdir('/'.join([root_path, dir]))) and (dir!='images')]
    # # qc_selection = json.load(open("qc_selection.json"))
    # for data_dir in list_data_dir:
    #     t0 = datetime.datetime.now()
    #     print('start time : {}'.format(t0))
    #     qc_pwr = QC_PWR(root_path=root_path, data_dir=data_dir, output_dir=output_path)
    #     qc_pwr.decode_FE_PWR()
    #     tf = datetime.datetime.now()
    #     print('end time : {}'.format(tf))
    #     deltaT = (tf - t0).total_seconds()
    #     print("Decoding time : {} seconds".format(deltaT))
    #     sys.exit()
    root_path = '../../Analyzed_BNL_CE_WIB_SW_QC'
    output_path = '../../Analysis'
    list_chipID = os.listdir(root_path)
    for chipID in list_chipID:
        pwr_ana = QC_PWR_analysis(root_path=root_path, chipID=chipID, output_path=output_path)
        pwr_ana.runAnalysis()
        # pwr_ana.Mean_ChResp_ana(BL='900mV')
        # sys.exit()