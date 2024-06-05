############################################################################################
#   created on 5/28/2024 @ 15:38
#   emails: radofanantenan.razakamiandra@stonybrook.edu
#   Analyze the data in QC_PWR.bin
############################################################################################

import datetime
import os, sys
import numpy as np
import matplotlib.pyplot as plt
import json, pickle
from utils import printItem, createDirs, dumpJson, decodeRawData, LArASIC_ana

class QC_PWR:
    '''
        Raw data ("QC_PWR.bin") from one DAT board -> 8x decoded data for each LArASIC
    '''
    def __init__(self, root_path: str, data_dir: str, output_dir: str):
        self.tms = 1
        self.qc_pwr_filename = 'QC_PWR.bin'
        self.item_to_analyze = "FE power consumption measurement"
        printItem(self.item_to_analyze)
        with open('/'.join([root_path, data_dir, self.qc_pwr_filename]), 'rb') as f:
            self.raw_data = pickle.load(f)
        self.logs_dict = self.raw_data['logs']
        self.pwr_params = [key for key in list(self.raw_data.keys()) if key!='logs']
        ##----- Create Folders for the outputs -----
        createDirs(logs_dict=self.logs_dict, output_dir=output_dir)
        FEoutputDIR = ['/'.join([output_dir, self.logs_dict['FE{}'.format(ichip)]]) for ichip in range(8)]
        self.pwr_outputDIR = ['/'.join([outDIR, 'QC_PWR']) for outDIR in FEoutputDIR]
        self.__createPWRfolders()
        #
        self.param_meanings = {
            'SDF0': 'seBuffOFF',
            'SDF1': 'seBuffON',
            'SNC0': '900mV',
            'SNC1': '200mV',
            'SDD0': 'sedcBufOFF',
            'SDD1': 'sedcBufON'
        }

    def __createPWRfolders(self):
        for pathtofolder in self.pwr_outputDIR:
            try:
                os.mkdir(pathtofolder)
            except OSError:
                pass

    def isParamInRange(self, paramVal=0, rangeParam=[0, 0]):
        flag = True
        if (paramVal>rangeParam[0]) & (paramVal<rangeParam[1]):
            flag = True
        else:
            flag = False
        return flag

    def getPowerConsumption(self):
        data_by_config = {self.logs_dict['FE{}'.format(ichip)]: {} for ichip in range(8)}
        for param in self.pwr_params:
            for KEY_feid in data_by_config.keys():
                data_by_config[KEY_feid][param] = dict()
        
        for param in self.pwr_params:
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

    def FE_PWR(self, selectionCriteria: dict):
        print('----> Power consumption')
        data_by_config = self.getPowerConsumption()

        pwr_all_chips = dict()
        for ichip in range(8):
            oneChip_data = {'900mV': {}, '200mV': {}, 'units': ['V', 'mA', 'mW']}
            FE_ID = self.logs_dict['FE{}'.format(ichip)]
            for param in self.pwr_params:
                configs = [conf for conf in param.split('_') if conf!='PWR']
                v_i_pwr = np.array([0,0,0])
                v_i_pwr_params = ['V', 'I', 'P']
                for pwr_rail in ['VDDA', 'VDDO', 'VDDP']:
                    v_i_pwr = v_i_pwr + np.array(data_by_config[FE_ID][param][pwr_rail])
                oneChip_data[self.param_meanings[configs[2]]]['_'.join([configs[0], configs[1]])] = {v_i_pwr_params[i]: np.around(v_i_pwr[i], 4) for i in range(3)}
            pwr_all_chips[FE_ID] = oneChip_data
        # Making plots
        plt.rcParams['font.size'] = 13
        Baselines = ['200mV', '900mV']
        for ichip, chip_id in enumerate(pwr_all_chips.keys()):
            fig_v, ax_v = plt.subplots()
            fig_i, ax_i = plt.subplots()
            fig_p, ax_p = plt.subplots()
            for BL in Baselines:
                data_to_plot = pwr_all_chips[chip_id][BL]
                # configs = list(data_to_plot.keys())
                voltage, current, power = [], [], []
                xticks_labels = []
                configs = ['SDD0_SDF0', 'SDD0_SDF1', 'SDD1_SDF0']
                for config in configs:
                    tmp = config.split('_')
                    xticks_labels.append('\n'.join([self.param_meanings[tmp[0]], self.param_meanings[tmp[1]]]))
                    voltage.append(data_to_plot[config]['V'])
                    current.append(data_to_plot[config]['I'])
                    power.append(data_to_plot[config]['P'])
                # voltage
                ax_v.plot(voltage, label=BL, marker='.', markersize=12)
                ax_v.set_xticks([0, 1, 2], xticks_labels)
                # current
                ax_i.plot(current, label=BL, marker='.', markersize=12)
                ax_i.set_xticks([0, 1, 2], xticks_labels)
                # power
                ax_p.plot(power, label=BL, marker='.', markersize=12)
                ax_p.set_xticks([0, 1, 2], xticks_labels)
                
            # voltage
            ax_v.set_ylabel('Voltage ({})'.format(pwr_all_chips[chip_id]['units'][0]))
            ax_v.legend()
            fig_v.savefig('/'.join([self.pwr_outputDIR[ichip], '{}_Voltage.png'.format(self.qc_pwr_filename.split('.')[0])]))
            plt.close(fig=fig_v)
            # current
            ax_i.set_ylabel('Current ({})'.format(pwr_all_chips[chip_id]['units'][1]))
            ax_i.legend()
            fig_i.savefig('/'.join([self.pwr_outputDIR[ichip], '{}_Current.png'.format(self.qc_pwr_filename.split('.')[0])]))
            plt.close(fig=fig_i)
            # power
            ax_p.set_ylabel('Power ({})'.format(pwr_all_chips[chip_id]['units'][2]))
            ax_p.legend()
            fig_p.savefig('/'.join([self.pwr_outputDIR[ichip], '{}_PowerConsumption.png'.format(self.qc_pwr_filename.split('.')[0])]))
            plt.close(fig=fig_p)

        # update data with the link to the plots and save everything in a json file
        chResponseAllChips = self.analyzeChResponse()
        for ichip, chip_id in enumerate(pwr_all_chips.keys()):
            FE_output_dir = self.pwr_outputDIR[ichip]
            # oneChip_data = {
            #                 'V': {'200mV': {}, '900mV': {}, 'unit': 'V', 'result_qc': '', 'link_to_img': ''},
            #                 'I': {'200mV': {}, '900mV': {}, 'unit': 'mA', 'result_qc': '', 'link_to_img': {}},
            #                 'P': {'200mV': {}, '900mV': {}, 'unit': 'mW', 'result_qc': '', 'link_to_img': {}}              
            #                 }
            ## Do not include any selection criteria or qc result in this part of the script
            oneChip_data = {
                            'V': {'200mV': {}, '900mV': {}, 'unit': 'V', 'link_to_img': ''},
                            'I': {'200mV': {}, '900mV': {}, 'unit': 'mA', 'link_to_img': {}},
                            'P': {'200mV': {}, '900mV': {}, 'unit': 'mW', 'link_to_img': {}},
                            'ChannelResponse': {}          
                            }
            Baselines = ['200mV', '900mV']
            configs = ['SDD0_SDF0', 'SDD0_SDF1', 'SDD1_SDF0']
            # V_result, I_result, P_result = [], [], []
            tmpdata_onechip = pwr_all_chips[chip_id]
            for BL in Baselines:
                # result_qc_V = []
                # result_qc_I = []
                # result_qc_P = []
                for config in configs:
                    voltage = tmpdata_onechip[BL][config]['V']
                    current = tmpdata_onechip[BL][config]['I']
                    pwrconsumption = tmpdata_onechip[BL][config]['P']
                    # get the accepted ranges for the voltage, current, and power consumption
                    # rangeV = selectionCriteria[BL]['V'][config]
                    # rangeI = selectionCriteria[BL]['I'][config]
                    # rangeP = selectionCriteria[BL]['P'][config]
                    # flagV = self.isParamInRange(paramVal=voltage, rangeParam=rangeV)
                    # flagI = self.isParamInRange(paramVal=current, rangeParam=rangeI)
                    # flagP = self.isParamInRange(paramVal=pwrconsumption, rangeParam=rangeP)

                    oneChip_data['V'][BL][config] = voltage
                    oneChip_data['I'][BL][config] = current
                    oneChip_data['P'][BL][config] = pwrconsumption
                    # result_qc_V.append(flagV)
                    # result_qc_I.append(flagI)
                    # result_qc_P.append(flagP)
                # V_passed, I_passed, P_passed = True, True, True
                # if False in result_qc_V:
                #     V_passed = False
                # if False in result_qc_I:
                #     I_passed = False
                # if False in result_qc_P:
                #     P_passed = False
                # V_result.append(V_passed)
                # I_result.append(I_result)
                # P_result.append(P_passed)
            # v_qc = ""
            # if False in V_result:
            #     v_qc = "Failed"
            # else:
            #     v_qc = "Passed"
            # i_qc = ""
            # if False in I_result:
            #     i_qc = "Failed"
            # else:
            #     i_qc = "Passed"
            # p_qc = ""
            # if False in P_result:
            #     p_qc = "Failed"
            # else:
            #     p_qc = "Passed"
            # oneChip_data['V']['result_qc'] = v_qc
            # oneChip_data['I']['result_qc'] = i_qc
            # oneChip_data['P']['result_qc'] = p_qc
            oneChip_data['V']['link_to_img'] = './{}_Voltage.png'.format(self.qc_pwr_filename.split('.')[0])
            oneChip_data['I']['link_to_img'] = './{}_Current.png'.format(self.qc_pwr_filename.split('.')[0])
            oneChip_data['P']['link_to_img'] = './{}_PowerConsumption.png'.format(self.qc_pwr_filename.split('.')[0])
            #
            oneChip_data['ChannelResponse'] = chResponseAllChips[chip_id]

            dumpJson(output_path=FE_output_dir, output_name="QC_PWR_data", data_to_dump=oneChip_data)

    def analyzeChResponse(self):
        '''
            For each configuration corresponds a raw data of the channel response. 
            This method aims to analyze the channel response during the power measuremet
        '''
        print('---> Channel Response')
        outdata = {self.logs_dict['FE{}'.format(ichip)]: {} for ichip in range(8)}
        for param in self.pwr_params:
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
                chipID = self.logs_dict['FE{}'.format(ichip)]
                larasic = LArASIC_ana(dataASIC=decodedData[ichip], output_dir=self.pwr_outputDIR[ichip], chipID=chipID, tms=1, param=suffixFilename, generateQCresult=False)
                data_asic = larasic.runAnalysis()
                outdata[chipID][suffixFilename] = data_asic
        return outdata

if __name__ =='__main__':
    t0 = datetime.datetime.now()
    print('start time : {}'.format(t0))
    root_path = '../../Data_BNL_CE_WIB_SW_QC'
    output_path = '../../Analyzed_BNL_CE_WIB_SW_QC'
    list_data_dir = os.listdir(root_path)
    qc_selection = json.load(open("qc_selection.json"))
    for data_dir in list_data_dir:
        qc_pwr = QC_PWR(root_path=root_path, data_dir=data_dir, output_dir=output_path)
        qc_pwr.FE_PWR(selectionCriteria=qc_selection['QC_PWR'])
        # qc_pwr.analyzeChResponse()
        tf = datetime.datetime.now()
        print('end time : {}'.format(tf))
        deltaT = (tf - t0).total_seconds()
        print("Analysis duration : {} seconds".format(deltaT))
        sys.exit()