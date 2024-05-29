############################################################################################
#   created on 5/28/2024 @ 15:38
#   emails: radofanantenan.razakamiandra@stonybrook.edu
#   Analyze the data in QC_PWR.bin
############################################################################################

import os, sys
import numpy as np
import matplotlib.pyplot as plt
import json, pickle
from utils import printItem, decodeRawData, createDirs, dumpJson

class QC_PWR:
    def __init__(self, root_path: str, data_dir: str, output_dir: str):
        self.tms = 1
        self.qc_pwr_filename = 'QC_PWR.bin'
        self.item_to_analyze = "FE power consumption measurement"
        printItem(self.item_to_analyze)
        with open('/'.join([root_path, data_dir, self.qc_pwr_filename]), 'rb') as f:
            self.raw_data = pickle.load(f)
        self.logs_dict = self.raw_data['logs']
        ##----- Create Folders for the outputs -----
        createDirs(logs_dict=self.logs_dict, output_dir=output_dir)
        self.FE_output_DIRs = ['/'.join([output_dir, self.logs_dict['FE{}'.format(ichip)]]) for ichip in range(8)]

    def FE_PWR(self):
        param_meanings = {
            'SDF0': 'BufferOFF',
            'SDF1': 'BufferON',
            'SNC0': '900mV',
            'SNC1': '200mV',
            'SDD0': 'SEDC_off',
            'SDD1': 'SEDC_on'
        }
        pwr_params = [key for key in list(self.raw_data.keys()) if key!='logs']
        data_by_config = dict()
        for ichip in range(8):
            FE_ID = self.logs_dict['FE{}'.format(ichip)]
            data_by_config[FE_ID] = dict()
            ## ---- NEED TO ORGARNIZE THIS PART
            ## ---- The parameters in the raw data correspond to different configurations of the LArASIC --> Need datasheet
            for param in pwr_params:
                data_oneconfig = self.raw_data[param][3]
                data_by_config[FE_ID][param] = dict()
                for val in data_oneconfig.keys():
                    if 'FE{}'.format(ichip) in val:
                        keyname = val.split('_')[1]
                        if keyname=="VPPP":
                            keyname = "VDDP"
                        data_by_config[FE_ID][param][keyname] = data_oneconfig[val]
        print(data_by_config['002-06204'])
        print('==='*20)
        pwr_all_chips = dict()
        for ichip in range(8):
            oneChip_data = {'VDDA': {'900mV': {}, '200mV': {}}, 'VDDO': {'900mV': {}, '200mV': {}}, 'VDDP': {'900mV': {}, '200mV': {}}}
            FE_ID = self.logs_dict['FE{}'.format(ichip)]
            for param in pwr_params:
                configs = [conf for conf in param.split('_') if conf!='PWR']
                for pwr_rail in ['VDDA', 'VDDO', 'VDDP']:
                    oneChip_data[pwr_rail][param_meanings[configs[2]]]['_'.join([configs[0], configs[1]])] = data_by_config[FE_ID][param][pwr_rail]
            pwr_all_chips[FE_ID] = oneChip_data
        print(pwr_all_chips['002-06204'])
        print('==='*20)
        # Making plots
        Baselines = ['200mV', '900mV']
        pwr_rails = ['VDDA', 'VDDO', 'VDDP']
        for pwr_rail in pwr_rails:
            for ichip, chip_id in enumerate(pwr_all_chips.keys()):
                fig1, ax1 = plt.subplots()
                fig2, ax2 = plt.subplots()
                fig3, ax3 = plt.subplots()
                for BL in Baselines:
                    data_to_plot = pwr_all_chips[chip_id][pwr_rail][BL]
                    configs = list(data_to_plot.keys())
                    voltage, current, power = [], [], []
                    xticks_titles = []
                    for config in configs:
                        tmp = config.split('_')
                        tmptmp = '\n'.join([param_meanings[tmp[0]], param_meanings[tmp[1]]])
                        xticks_titles.append(tmptmp)
                        voltage.append(data_to_plot[config][0])
                        current.append(data_to_plot[config][1])
                        power.append(data_to_plot[config][2])
                    
                    # voltage
                    ax1.plot(voltage, label=BL, marker='.', markersize=12)
                    ax1.set_xticks([0, 1, 2], xticks_titles)
                    ax1.set_ylabel('Voltage (V)')
                    # current
                    ax2.plot(current, label=BL, marker='.', markersize=12)
                    ax2.set_xticks([0, 1, 2], xticks_titles)
                    ax2.set_ylabel('Current (mA)')
                # voltage
                ax1.set_title('{} - Voltage'.format(pwr_rail))
                ax1.legend()
                fig1.savefig('/'.join([self.FE_output_DIRs[ichip], '{}_voltage.png'.format(pwr_rail)]))
                # current
                ax2.set_title('{} - Current'.format(pwr_rail))
                ax2.legend()
                fig2.savefig('/'.join([self.FE_output_DIRs[ichip], '{}_current.png'.format(pwr_rail)]))
                plt.close()
        sys.exit()
                

if __name__ =='__main__':
    root_path = '../../Data_BNL_CE_WIB_SW_QC'
    output_path = '../../Analyzed_BNL_CE_WIB_SW_QC'
    list_data_dir = os.listdir(root_path)
    for data_dir in list_data_dir:
        qc_pwr = QC_PWR(root_path=root_path, data_dir=data_dir, output_dir=output_path)
        qc_pwr.FE_PWR()
        sys.exit()
