############################################################################################
#   created on 6/5/2024 @ 13:43
#   email: radofanantenan.razakamiandra@stonybrook.edu
#   Analyze the data in QC_CHKRES.bin
############################################################################################

# from datetime import datetime
import os, sys
# import numpy as np
import matplotlib.pyplot as plt
# import json, pickle
from utils import printItem, dumpJson, decodeRawData, LArASIC_ana, BaseClass
from utils import BaseClass_Ana

class QC_CHKRES(BaseClass):
    def __init__(self, root_path: str, data_dir: str, output_dir: str):
        printItem("FE response measurement")
        super().__init__(root_path=root_path, data_dir=data_dir, output_path=output_dir, tms=2, QC_filename='QC_CHKRES.bin')
        self.period = 500

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
        sdd_dict = {
            "0" : "SEDC OFF",
            "1" : "SEDC ON"
        }
        sdf_dict = {
            "0" : "Buff OFF",
            "1" : "Buff ON"
        }
        slkh_dict = {
            # "0" : "RQI x10 OFF",
            # "1" : "RQI x10 ON"
            "0" : 1,
            "1": 10
        }
        slk_dict = {
            # "0" : "500 pA RQI",
            # "1" : "100 pA RQI"
            "0": 500, # pA RQI
            "1": 100 # pA RQI
        }
        snc_dict = {
            "0" : "900 mV",
            "1" : "200 mV"
        }
        sts_dict = {
            "0" : "test cap OFF",
            "1" : "test cap ON"
        }
        st_dict = {
            # "00" : "1.0 $\mu s$",
            # "10" : "0.5 $\mu s$",
            # "01" : "3 $\mu s$",
            # "11" : "2 $\mu s$"
            "00" : 1.0,
            "10" : 0.5,
            "01" : 3,
            "11" : 2
        }
        sgp_dict = {
            "0": "Gbit=0",
            "1": "Gbit=1"
        }
        sg_dict = {
            # "00" : "14mV/fC",
            # "10" : "25mV/fC",
            # "01" : "7.8mV/fC",
            # "11" : "4.7mV/fC"
            "00": 14,
            "10": 25,
            "01": 7.8,
            "11": 4.7
        }
        config_datasheet = dict()
        # for KEY, config_list in config_dict.items():
        config_datasheet = {}
        for VAL in config_list:
            [chk, k, sdd, sdf, slk, slkh, snc, st0, st1, sg0, sg1] = VAL.split('_')
            sdd_val = sdd[-1]
            sdf_val = sdf[-1]
            slkh_val = slkh[-1]
            slk_val = slk[-1:]
            snc_val = snc[-1]
            st_val = st0[-1]+ st1[-1]
            sgp_val = "0"
            sg_val = sg0[-1] + sg1[-1]
            config_datasheet[VAL] = {
                "param_chk": k,
                "SDD": sdd_dict[sdd_val],
                "SDF": sdf_dict[sdf_val],
                "SLKH": slkh_dict[slkh_val],
                "SLK": slk_dict[slk_val],
                "SNC": snc_dict[snc_val],
                # "STS": sts_dict[sts_val],
                "ST": st_dict[st_val],
                "SGP": sgp_dict[sgp_val],
                "SG": sg_dict[sg_val]
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
        wibdata = decodeRawData(fembs=fembs, rawdata=rawdata, period=self.period)
        # wibdata = decodedData['wf']
        # avg_wibdata = decodedData['avg_wf']
        for ichip in range(8):
            ASIC_ID = self.logs_dict['FE{}'.format(ichip)]
            out_dict[ASIC_ID] = dict()
            larasic = LArASIC_ana(dataASIC=wibdata[ichip], output_dir=self.FE_outputDIRs[ASIC_ID], chipID=ASIC_ID, tms=self.tms, param=config, generateQCresult=False, generatePlots=False, period=self.period)
            data_asic = larasic.runAnalysis()
            out_dict[ASIC_ID]['pedestal'] = data_asic['pedrms']['pedestal']['data']
            out_dict[ASIC_ID]['rms'] = data_asic['pedrms']['rms']['data']
            out_dict[ASIC_ID]['pospeak'] = data_asic['pulseResponse']['pospeak']['data']
            out_dict[ASIC_ID]['negpeak'] = data_asic['pulseResponse']['negpeak']['data']
        return (config, out_dict)
    
    def decode_CHKRES(self):
        # get CONFIGURATIONs
        datasheetCFG = self.cfgData2cfgDatasheet(config_list=self.params)

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

        for param_cfg in self.params:
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
            dumpJson(output_path=self.FE_outputDIRs[ASIC_ID], output_name='QC_CHKRES', data_to_dump=allchip_data[ASIC_ID])

class QC_CHKRES_Ana(BaseClass_Ana):
    def __init__(self, root_path: str, chipID: str, output_path: str):
        self.item = 'QC_CHKRES'
        super().__init__(root_path=root_path, chipID=chipID, output_path=output_path, item=self.item)
        self.output_dir = '/'.join([self.output_dir, self.item])
        try:
            os.mkdir(self.output_dir)
        except OSError:
            pass
        # print(self.params)
        # self.makePlots()
        # sys.exit()
    
    def ChResp_ana(self, item_to_plot: str, group: str, returnData: False):
        chipData = {}
        for param in self.params:
            data = self.getoneConfigData(config=param)
            # meanValue, stdValue, minValue, maxValue = self.getCHresp_info(oneChipData=data[item_to_plot])
            meanValue, stdValue, minValue, maxValue = 0., 0., 0., 0.
            if data['CFG_info']['param_chk'] == group:
                meanValue, stdValue, minValue, maxValue = self.getCHresp_info(oneChipData=data[item_to_plot])
                cfg_info = data['CFG_info']
                config = ''
                if group=='GAINs':
                    # config = '\n'.join([cfg_info['SNC'], cfg_info['SGP'], str(cfg_info['SG'])])
                    config = '_'.join([cfg_info['SNC'], str(cfg_info['SG'])])
                elif group=='OUTPUT':
                    # config = '\n'.join(['_'.join([cfg_info['SNC'], cfg_info['SG']]), cfg_info['SDD'], cfg_info['SDF']])
                    config = '\n'.join([cfg_info['SNC'], cfg_info['SDD'], cfg_info['SDF']])
                elif group=='BL':
                    config = '\n'.join([cfg_info['SNC'], '_'.join([cfg_info['SDD'], cfg_info['SDF']])])
                elif group=='TP':
                    # config = '\n'.join([cfg_info['ST'], cfg_info['SLK'], cfg_info['SLKH']])
                    config = cfg_info['ST']
                elif group=='SLKS':
                    # config = '\n'.join([cfg_info['SNC'], cfg_info['SLKH'], cfg_info['SLK']])
                    config = cfg_info['SLKH'] * cfg_info['SLK']
                chipData[config] = {'mean': meanValue, 'std': stdValue, 'min': minValue, 'max': maxValue}
        configs = chipData.keys()
        meanValues = [d['mean'] for key, d in chipData.items()]
        stdValues = [d['std'] for key, d in chipData.items()]
        minValues = [d['min'] for key, d in chipData.items()]
        maxValues = [d['max'] for key, d in chipData.items()]
        plt.figure(figsize=(8, 8))
        if group=='GAINs':
            # print(configs)
            BL200mV_configs = [c for c in list(configs) if '200 mV' in c]
            BL900mV_configs = [c for c in list(configs) if '900 mV' in c]
            # xticks = ['\n'.join(c.split('\n')[1:]) for c in BL200mV_configs]
            xticks = [float(c.split('_')[1]) for c in BL200mV_configs]
            bl200_xticks = xticks.copy()
            bl900_xticks = xticks.copy()
            bl200_xticks, BL200mV_configs = (list(t) for t in zip(*sorted(zip(bl200_xticks, BL200mV_configs))))
            bl900_xticks, BL900mV_configs = (list(t)for t in zip(*sorted(zip(bl900_xticks, BL900mV_configs))))
            xticks = [c.split('_')[1] for c in BL200mV_configs]
            tmpdata200 = {key: chipData[key] for key in BL200mV_configs}
            tmpdata900 = {key: chipData[key] for key in BL900mV_configs}
            mean200 = [d['mean'] for key, d, in tmpdata200.items()]
            std200 = [d['std'] for key, d in tmpdata200.items()]
            min200 = [d['min'] for key, d in tmpdata200.items()]
            max200 = [d['max'] for key, d in tmpdata200.items()]
            mean900 = [d['mean'] for key, d, in tmpdata900.items()]
            std900 = [d['std'] for key, d in tmpdata900.items()]
            min900 = [d['min'] for key, d in tmpdata900.items()]
            max900 = [d['max'] for key, d in tmpdata900.items()]
            datas = [tmpdata200, tmpdata900]
            BL = ['200mV', '900mV']
            colors=['r', 'b']
            means = [mean200, mean900]
            stds = [std200, std900]
            mins = [min200, min900]
            maxs = [max200, max900]
            #______ return the data if returnData==True______
            if returnData:
                return xticks, means, stds, mins, maxs
            else:
                range_to_scan = []
                if item_to_plot=='negpeak':
                    range_to_scan = [1] # select 900mV only
                else:
                    range_to_scan = [0, 1]
                for i in range_to_scan:
                    plt.errorbar(x=xticks, y=means[i], yerr=stds[i], capsize=4, color=colors[i], ecolor=colors[i], label='Mean of {}, {} BL'.format(item_to_plot, BL[i]), elinewidth=1.5)
                    # plt.scatter(x=xticks, y=means[i], color='g', marker='.', s=10)
                    plt.scatter(x=xticks, y=mins[i], color=colors[i], marker='.', s=100)
                    plt.scatter(x=xticks, y=maxs[i], color=colors[i], marker='.', s=100)
                    plt.xticks(xticks)
        else:
            if type(list(configs)[0]) in [float, int]:
                tmp = list(configs).copy()
                _, meanValues = (list(t) for t in zip(*sorted(zip(list(configs).copy(), meanValues))))
                _, stdValues = (list(t) for t in zip(*sorted(zip(list(configs).copy(), stdValues))))
                _, minValues = (list(t) for t in zip(*sorted(zip(list(configs).copy(), minValues))))
                _, maxValues = (list(t) for t in zip(*sorted(zip(list(configs).copy(), maxValues))))
                configs = sorted(list(configs))
            #______ return the data if returnData==True______
            if returnData:
                return configs, meanValues, stdValue, minValues, maxValues
            else:
                plt.errorbar(x=configs, y=meanValues, yerr=stdValues, capsize=4, label='Mean of {}'.format(item_to_plot), elinewidth=1.5)
                # plt.scatter(x=configs, y=meanValues, color='b', marker='.', s=100)
                plt.scatter(x=configs, y=minValues, color='r', marker='.', s=100)
                plt.scatter(x=configs, y=maxValues, color='r', marker='.', s=100)
                plt.xticks(list(configs))
        unitx = ''
        if group=='GAINs':
            unitx = '(mV/fC)'
        elif group=='TP':
            unitx = '($\\mu s$)'
        elif group=='SLKS':
            unitx = '(pA RQI)'
        
        ylim = []
        if item_to_plot=='pedestal':
            minped = 500
            maxped = 10000
            if group=='SLKS':
                minped = 8000
                maxped = 12000
            ylim = [minped, maxped]
        elif item_to_plot=='rms':
            ylim = [0, 25]
        elif item_to_plot=='pospeak':
            ylim = [3000, 5000]
        elif item_to_plot=='negpeak':
            ylim = [3000, 5000]
        if len(ylim)!=0:
            plt.ylim(ylim)
        plt.xlabel('Configurations {}'.format(unitx), fontdict={'weight': 'bold'}, loc='right')
        plt.ylabel('{} (ADC bit)'.format(item_to_plot), fontdict={'weight': 'bold'}, loc='top')
        plt.title(item_to_plot)
        plt.legend()
        plt.grid(True)
        plt.savefig('/'.join([self.output_dir, '_'.join([self.item, item_to_plot, group]) + '.png']))
        plt.close()
        # sys.exit()

    def makePlots(self):
        items_to_plot = ['pedestal', 'rms', 'pospeak', 'negpeak']
        groups = ['GAINs', 'OUTPUT', 'BL', 'TP', 'SLKS']
        for item_to_plot in items_to_plot:
            for group in groups:
                self.ChResp_ana(item_to_plot=item_to_plot, group=group)

if __name__ == "__main__":
    # root_path = '../../Data_BNL_CE_WIB_SW_QC'
    # output_path = '../../Analyzed_BNL_CE_WIB_SW_QC'
    # # list_data_dir = [dir for dir in os.listdir(root_path) if '.zip' not in dir]
    # root_path = '../../B010T0004'
    # list_data_dir = [dir for dir in os.listdir(root_path) if (os.path.isdir('/'.join([root_path, dir]))) and (dir!='images')]
    # for i, data_dir in enumerate(list_data_dir):
    #     # if i==2:
    #         qc_checkres = QC_CHKRES(root_path=root_path, data_dir=data_dir, output_dir=output_path)
    #         qc_checkres.decode_CHKRES()
    #********************************************************
    root_path = '../../Analyzed_BNL_CE_WIB_SW_QC'
    output_path = '../../Analysis'
    list_chipID = os.listdir(root_path)
    for chipID in list_chipID:
        chk_res = QC_CHKRES_Ana(root_path=root_path, chipID=chipID, output_path=output_path)
        chk_res.makePlots()
