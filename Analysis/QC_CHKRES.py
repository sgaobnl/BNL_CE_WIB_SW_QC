############################################################################################
#   created on 6/5/2024 @ 13:43
#   email: radofanantenan.razakamiandra@stonybrook.edu
#   Analyze the data in QC_CHKRES.bin
############################################################################################

# from datetime import datetime
import os, sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statistics
from scipy.stats import norm
from utils import printItem, dumpJson, decodeRawData, LArASIC_ana, BaseClass
from utils import BaseClass_Ana

class QC_CHKRES(BaseClass):
    def __init__(self, root_path: str, data_dir: str, output_dir: str):
        printItem("FE response measurement")
        super().__init__(root_path=root_path, data_dir=data_dir, output_path=output_dir, tms=2, QC_filename='QC_CHKRES.bin')
        if self.ERROR:
            return
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
        if self.ERROR:
            return
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
    
    def ChResp_ana(self, item_to_plot: str, group: str, returnData=False):
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
        # plt.figure(figsize=(8, 8))
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
                plt.figure(figsize=(8, 8))
                range_to_scan = []
                if item_to_plot=='negpeak':
                    range_to_scan = [1] # select 900mV only
                else:
                    range_to_scan = [0, 1]
                for i in range_to_scan:
                    # plt.figure(figsize=(8, 8))
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
                plt.figure(figsize=(8, 8))
                plt.errorbar(x=configs, y=meanValues, yerr=stdValues, capsize=4, label='Mean of {}'.format(item_to_plot), elinewidth=1.5)
                # plt.scatter(x=configs, y=meanValues, color='b', marker='.', s=100)
                plt.scatter(x=configs, y=minValues, color='r', marker='.', s=100)
                plt.scatter(x=configs, y=maxValues, color='r', marker='.', s=100)
                plt.xticks(list(configs))
        # plt.figure(figsize=(8, 8))
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
        if self.ERROR:
            return
        items_to_plot = ['pedestal', 'rms', 'pospeak', 'negpeak']
        groups = ['GAINs', 'OUTPUT', 'BL', 'TP', 'SLKS']
        for item_to_plot in items_to_plot:
            for group in groups:
                self.ChResp_ana(item_to_plot=item_to_plot, group=group)

    def extractData(self):
        items = ['pedestal', 'rms', 'pospeak', 'negpeak']
        groups = ['GAINs', 'OUTPUT', 'BL', 'TP', 'SLKS']
        out_dict = dict()
        for group in groups:
            out_dict[group] = {item: dict() for item in items}
        # print(out_dict)
        for item in items:
            for group in groups:
                configs, means, stds, mins, maxs = self.ChResp_ana(item_to_plot=item, group=group, returnData=True)
                out_dict[group][item] = {c: dict() for c in configs}
                
                if group=='GAINs':
                    for i, c in enumerate(configs):
                        out_dict[group][item][c]['mean'] = {'200mV': means[0][i], '900mV': means[1][i]}
                        out_dict[group][item][c]['min'] = {'200mV': mins[0][i], '900mV': mins[1][i]}
                        out_dict[group][item][c]['max'] = {'200mV': maxs[0][i], '900mV': maxs[1][i]}
                else:
                    for i, c in enumerate(configs):
                        out_dict[group][item][c]['mean'] = means[i]
                        out_dict[group][item][c]['min'] = mins[i]
                        out_dict[group][item][c]['max'] = maxs[i]
        # print(out_dict)
        return out_dict


class QC_CHKRES_StatAna():
    def __init__(self, root_path: str, output_path: str):
        self.root_path = root_path
        self.output_path = output_path
        self.output_fig = '/'.join([output_path, 'fig'])
        try:
            os.mkdir(self.output_fig)
        except:
            pass
        # THIS LINE NEEDS TO BE MODIFIED --> Find a better way to get the structure of the json file automatically
        self.chkdata_toy = {'GAINs': {'pedestal': {'4.7': {'mean': {'200mV': 920.0535, '900mV': 8723.2227}, 'min': {'200mV': 761.4332, '900mV': 8617.5559}, 'max': {'200mV': 1108.3855, '900mV': 8826.7037}}, '7.8': {'mean': {'200mV': 984.7076, '900mV': 8791.0025}, 'min': {'200mV': 826.057, '900mV': 8685.8425}, 'max': {'200mV': 1171.1404, '900mV': 8897.9679}}, '14': {'mean': {'200mV': 1116.7686, '900mV': 8931.4033}, 'min': {'200mV': 961.4979, '900mV': 8824.759}, 'max': {'200mV': 1300.3047, '900mV': 9043.0753}}, '25': {'mean': {'200mV': 1340.1492, '900mV': 9166.9446}, 'min': {'200mV': 1185.6007, '900mV': 9057.4761}, 'max': {'200mV': 1514.5733, '900mV': 9281.407}}}, 'rms': {'4.7': {'mean': {'200mV': 4.6696, '900mV': 4.7128}, 'min': {'200mV': 4.2797, '900mV': 4.2253}, 'max': {'200mV': 5.0279, '900mV': 5.2124}}, '7.8': {'mean': {'200mV': 7.3023, '900mV': 7.2306}, 'min': {'200mV': 6.6742, '900mV': 6.456}, 'max': {'200mV': 8.1935, '900mV': 7.963}}, '14': {'mean': {'200mV': 12.6979, '900mV': 12.9429}, 'min': {'200mV': 11.3092, '900mV': 11.7697}, 'max': {'200mV': 14.1517, '900mV': 14.4354}}, '25': {'mean': {'200mV': 22.7148, '900mV': 22.6192}, 'min': {'200mV': 18.8299, '900mV': 19.1871}, 'max': {'200mV': 26.8888, '900mV': 26.4137}}}, 'pospeak': {'4.7': {'mean': {'200mV': 3193.134, '900mV': 3274.3554}, 'min': {'200mV': 2761.7161, '900mV': 3186.8646}, 'max': {'200mV': 3253.5668, '900mV': 3312.3322}}, '7.8': {'mean': {'200mV': 4148.7768, '900mV': 4228.06}, 'min': {'200mV': 3779.7961, '900mV': 4120.1223}, 'max': {'200mV': 4210.443, '900mV': 4269.8196}}, '14': {'mean': {'200mV': 4203.2939, '900mV': 4275.0967}, 'min': {'200mV': 3956.6253, '900mV': 4172.9517}, 'max': {'200mV': 4259.7521, '900mV': 4330.0932}}, '25': {'mean': {'200mV': 4276.1008, '900mV': 4353.0346}, 'min': {'200mV': 4106.7747, '900mV': 4243.2496}, 'max': {'200mV': 4333.6218, '900mV': 4409.7394}}}, 'negpeak': {'4.7': {'mean': {'200mV': 920.0535, '900mV': 3264.254}, 'min': {'200mV': 761.4332, '900mV': 3026.6354}, 'max': {'200mV': 1108.3855, '900mV': 3307.9178}}, '7.8': {'mean': {'200mV': 984.7076, '900mV': 4224.815}, 'min': {'200mV': 826.057, '900mV': 4026.5444}, 'max': {'200mV': 1171.1404, '900mV': 4277.6942}}, '14': {'mean': {'200mV': 1116.7686, '900mV': 4277.4971}, 'min': {'200mV': 961.4979, '900mV': 4140.7983}, 'max': {'200mV': 1300.3047, '900mV': 4334.1568}}, '25': {'mean': {'200mV': 1340.1492, '900mV': 4362.1946}, 'min': {'200mV': 1185.6007, '900mV': 4259.4706}, 'max': {'200mV': 1514.5733, '900mV': 4422.9604}}}}, 'OUTPUT': {'pedestal': {'900 mV\nSEDC OFF\nBuff OFF': {'mean': 8917.833, 'min': 8811.4033, 'max': 9026.0783}, '900 mV\nSEDC OFF\nBuff ON': {'mean': 8765.595, 'min': 8647.3767, 'max': 8858.0942}, '900 mV\nSEDC ON\nBuff OFF': {'mean': 8783.0081, 'min': 8687.8206, 'max': 8875.1222}}, 'rms': {'900 mV\nSEDC OFF\nBuff OFF': {'mean': 12.9223, 'min': 11.5787, 'max': 14.929}, '900 mV\nSEDC OFF\nBuff ON': {'mean': 13.2322, 'min': 11.6834, 'max': 14.8552}, '900 mV\nSEDC ON\nBuff OFF': {'mean': 12.7703, 'min': 11.6407, 'max': 15.3885}}, 'pospeak': {'900 mV\nSEDC OFF\nBuff OFF': {'mean': 4279.1045, 'min': 4162.4816, 'max': 4326.8397}, '900 mV\nSEDC OFF\nBuff ON': {'mean': 4385.2487, 'min': 4292.1999, 'max': 4425.2744}, '900 mV\nSEDC ON\nBuff OFF': {'mean': 4328.32, 'min': 4295.3213, 'max': 4367.7248}}, 'negpeak': {'900 mV\nSEDC OFF\nBuff OFF': {'mean': 4285.083, 'min': 4131.8517, 'max': 4334.2154}, '900 mV\nSEDC OFF\nBuff ON': {'mean': 4399.2044, 'min': 4277.0102, 'max': 4446.4614}, '900 mV\nSEDC ON\nBuff OFF': {'mean': 4464.68, 'min': 4418.1787, 'max': 4526.5252}}}, 'BL': {'pedestal': {'900 mV\nSEDC OFF_Buff OFF': {'mean': 8925.9726, 'min': 8820.9019, 'max': 9034.7863}, '200 mV\nSEDC OFF_Buff OFF': {'mean': 1112.1438, 'min': 956.8159, 'max': 1296.2411}}, 'rms': {'900 mV\nSEDC OFF_Buff OFF': {'mean': 12.7781, 'min': 11.4768, 'max': 14.1009}, '200 mV\nSEDC OFF_Buff OFF': {'mean': 12.4046, 'min': 11.4699, 'max': 14.5145}}, 'pospeak': {'900 mV\nSEDC OFF_Buff OFF': {'mean': 4277.2774, 'min': 4169.3895, 'max': 4322.2863}, '200 mV\nSEDC OFF_Buff OFF': {'mean': 4203.0749, 'min': 3956.9595, 'max': 4263.4341}}, 'negpeak': {'900 mV\nSEDC OFF_Buff OFF': {'mean': 4279.5039, 'min': 4129.8605, 'max': 4335.1366}, '200 mV\nSEDC OFF_Buff OFF': {'mean': 1112.1438, 'min': 956.8159, 'max': 1296.2411}}}, 'TP': {'pedestal': {0.5: {'mean': 8694.7244, 'min': 8590.512, 'max': 8796.9825}, 1.0: {'mean': 8769.0665, 'min': 8663.2963, 'max': 8873.2017}, 2: {'mean': 8913.0714, 'min': 8807.7834, 'max': 9020.7699}, 3: {'mean': 9058.2681, 'min': 8953.8225, 'max': 9169.9924}}, 'rms': {0.5: {'mean': 11.6278, 'min': 11.0525, 'max': 12.5184}, 1.0: {'mean': 11.7596, 'min': 10.8947, 'max': 12.6109}, 2: {'mean': 12.3655, 'min': 11.2181, 'max': 13.2762}, 3: {'mean': 14.2321, 'min': 12.5532, 'max': 17.3397}}, 'pospeak': {0.5: {'mean': 3474.0673, 'min': 3367.489, 'max': 3521.4585}, 1.0: {'mean': 4130.6679, 'min': 4002.3059, 'max': 4178.7866}, 2: {'mean': 4278.6786, 'min': 4170.2014, 'max': 4327.7293}, 3: {'mean': 4289.2631, 'min': 4172.703, 'max': 4336.5276}}, 'negpeak': {0.5: {'mean': 3333.0577, 'min': 3152.8444, 'max': 3379.9383}, 1.0: {'mean': 4106.2071, 'min': 3929.6941, 'max': 4171.4634}, 2: {'mean': 4280.3839, 'min': 4128.4653, 'max': 4335.1151}, 3: {'mean': 4295.2994, 'min': 4183.297, 'max': 4336.7003}}}, 'SLKS': {'pedestal': {100: {'mean': 8740.8038, 'min': 8636.862, 'max': 8843.2177}, 500: {'mean': 8916.2093, 'min': 8808.6837, 'max': 9027.261}, 1000: {'mean': 9088.254, 'min': 8983.9484, 'max': 9202.2339}, 5000: {'mean': 11032.9986, 'min': 10929.6243, 'max': 11220.9052}}, 'rms': {100: {'mean': 12.5143, 'min': 11.1642, 'max': 14.5457}, 500: {'mean': 12.8407, 'min': 11.6557, 'max': 15.4567}, 1000: {'mean': 12.8509, 'min': 11.9001, 'max': 14.1173}, 5000: {'mean': 15.7395, 'min': 13.7845, 'max': 18.2684}}, 'pospeak': {100: {'mean': 4269.6962, 'min': 4037.5465, 'max': 4332.5828}, 500: {'mean': 4275.0876, 'min': 4169.616, 'max': 4327.9026}, 1000: {'mean': 4266.9752, 'min': 3997.7634, 'max': 4327.8913}, 5000: {'mean': 4248.5014, 'min': 3944.4107, 'max': 4317.3849}}, 'negpeak': {100: {'mean': 4265.8819, 'min': 3963.4535, 'max': 4330.6672}, 500: {'mean': 4277.2405, 'min': 4132.884, 'max': 4333.0974}, 1000: {'mean': 4280.3998, 'min': 4058.57, 'max': 4332.7753}, 5000: {'mean': 4277.3944, 'min': 3938.256, 'max': 4341.4135}}}}
    
    def getItems(self):
        list_chipID = os.listdir(self.root_path)
        # chipID_toy = list_chipID[0]
        # chkres_toy = QC_CHKRES_Ana(root_path=self.root_path, chipID=chipID_toy, output_path='')
        # # if chkres_toy.ERROR==True:
        # #     return dict()
        # chkdata_toy = chkres_toy.extractData()
        # print(chkdata_toy)
        # sys.exit()
        # Get data structure
        testItems = list(self.chkdata_toy.keys())
        groups = list(self.chkdata_toy[testItems[0]].keys())
        # Test item specific configurations
        ## Gains
        gains = list(self.chkdata_toy[testItems[0]][groups[0]].keys())
        ## OUTPUT
        outputs = list(self.chkdata_toy[testItems[1]][groups[0]].keys())
        ## BL
        Baselines = list(self.chkdata_toy[testItems[2]][groups[0]].keys())
        ## Peaking time
        TPs = list(self.chkdata_toy[testItems[3]][groups[0]].keys())
        ## SLKS
        slks = list(self.chkdata_toy[testItems[4]][groups[0]].keys())
        # print(chkdata_toy[testItems[1]][groups[0]].keys())

        # Format of the output dictionary
        ## We will only save the mean values. Note: saving the min, max, or std is also possible if needed --> Changing the format of the output is required
        out_dict = {key: dict() for key in testItems}
        for key in testItems:
            subdict = {g: dict() for g in groups}
            for g in groups:
                if key=='GAINs':
                    subdict[g] = {gain: {'200mV': [], '900mV': []} for gain in gains}
                elif key=='OUTPUT':
                    subdict[g] = {output: [] for output in outputs}
                elif key=='BL':
                    subdict[g] = {bl: [] for bl in Baselines}
                elif key=='TP':
                    subdict[g] = {tp: [] for tp in TPs}
                elif key=='SLKS':
                    subdict[g] = {s: [] for s in slks}
            out_dict[key] = subdict

        for chipID in list_chipID:
            chkres = QC_CHKRES_Ana(root_path=self.root_path, chipID=chipID, output_path='')
            if chkres.ERROR==True:
                continue
            chkres_data = chkres.extractData()
            # print(chkres_data.keys())
            # groups = chkres_data.keys()
            for testItem in testItems:
                subgroups = chkres_data[testItem].keys()
                # print(subgroups)
                for subgroup in subgroups:
                    ssubgroups = chkres_data[testItem][subgroup].keys()
                    # print(ssubgroups)
                    for ss in ssubgroups:
                        # print(chkres_data[testItem][subgroup][ss].keys())
                        if testItem=='GAINs':
                            out_dict[testItem][subgroup][ss]['200mV'].append(chkres_data[testItem][subgroup][ss]['mean']['200mV'])
                            out_dict[testItem][subgroup][ss]['900mV'].append(chkres_data[testItem][subgroup][ss]['mean']['900mV'])
                        else:
                            out_dict[testItem][subgroup][ss].append(chkres_data[testItem][subgroup][ss]['mean'])
                # break
            # print(chkres_data)
            # break
        # print(out_dict)
        # # TEST DISTRIBUTION
        # plt.figure()
        # plt.hist(out_dict['GAINs']['pedestal']['4.7']['900mV'])
        # plt.show()
        return out_dict

    def run_Ana(self):
        OUTPUT_DF = pd.DataFrame()
        #******************************
        data_dict = self.getItems()
        testItems = list(data_dict.keys())
        # The analysis of GAINs and the other items are different
        ## GAIN ANALYSIS
        gainData = data_dict['GAINs']
        groups = list(gainData.keys())
        ASIC_gains = list(gainData[groups[0]].keys())
        BLs = list(gainData[groups[0]][ASIC_gains[0]].keys())
        ##---- Lists for the dataframe
        testItem_list, group_list, asicgain_list, bl_list = [], [], [], []
        mean_list, std_list = [], []
        for group in groups:
            for asicGain in ASIC_gains:
                for BL in BLs:
                    filename = '_'.join(['QC_CHKRES', 'GAIN', group, asicGain, BL])
                    tmpdata = gainData[group][asicGain][BL]
                    Nbins = int(len(tmpdata)/2)
                    xmin, xmax = np.min(tmpdata), np.max(tmpdata)
                    mean, std = statistics.mean(tmpdata), statistics.stdev(tmpdata)
                    for _ in range(10):
                        if xmin < mean-3*std:
                            posMin = np.where(tmpdata==xmin)[0][0]
                            del tmpdata[posMin]
                        if xmax > mean+3*std:
                            posMax = np.where(tmpdata==xmax)[0][0]
                            del tmpdata[posMax]
                        xmin, xmax = np.min(tmpdata), np.max(tmpdata)
                        mean, std = statistics.mean(tmpdata), statistics.stdev(tmpdata)
                    mean, std = np.round(mean, 4), np.round(std, 4)
                    # fill the lists
                    testItem_list.append('GAIN')
                    group_list.append(group)
                    asicgain_list.append(asicGain)
                    bl_list.append(BL)
                    mean_list.append(mean)
                    std_list.append(std)
                    #
                    x = np.linspace(xmin, xmax, len(tmpdata))
                    p = norm.pdf(x, mean, std)
                    plt.figure()
                    plt.hist(tmpdata, bins=Nbins, density=True)
                    plt.plot(x, p, 'r', label='mean = {}, std = {}'.format(mean, std))
                    plt.xlabel(group);plt.ylabel('#')
                    # plt.show()
                    plt.legend()
                    plt.savefig('/'.join([self.output_fig, filename + '.png']))
                    plt.close()
        Gain_df = pd.DataFrame({'testItem': testItem_list, 'feature': group_list, 'cfg': asicgain_list, 'BL': bl_list, 'mean': mean_list, 'std': std_list})
        OUTPUT_DF = pd.concat([OUTPUT_DF, Gain_df], axis=0, ignore_index=True) #*******************
        ## OTHER THAN GAIN
        for item in testItems:
            if item!='GAINs':
                ## GAIN ANALYSIS
                ItemData = data_dict[item]
                groups = list(ItemData.keys())
                ASIC_Items = list(ItemData[groups[0]].keys())
                # BLs = list(ItemData[groups[0]][ASIC_Items[0]].keys())
                ##---- Lists for the dataframe
                testItem_list, group_list, asicItem_list, bl_list = [], [], [], []
                mean_list, std_list = [], []
                for group in groups:
                    for asicItem in ASIC_Items:
                        # for BL in BLs:
                        BL = ''
                        filename = '_'.join(['QC_CHKRES', '{}_{}_{}'.format(item, group, asicItem)])
                        if '\n' in filename:
                            # print(asicItem)
                            # print(filename)
                            # sys.exit()
                            tmpASICitem = '_'.join(asicItem.split('\n'))
                            BL = group.split('\n')[0]
                            filename = '_'.join(['QC_CHKRES', item, group, tmpASICitem])

                        tmpdata = ItemData[group][asicItem]
                        Nbins = int(len(tmpdata)/2)
                        xmin, xmax = np.min(tmpdata), np.max(tmpdata)
                        mean, std = statistics.mean(tmpdata), statistics.stdev(tmpdata)
                        for _ in range(10):
                            if xmin < mean-3*std:
                                posMin = np.where(tmpdata==xmin)[0][0]
                                del tmpdata[posMin]
                            if xmax > mean+3*std:
                                posMax = np.where(tmpdata==xmax)[0][0]
                                del tmpdata[posMax]
                            xmin, xmax = np.min(tmpdata), np.max(tmpdata)
                            mean, std = statistics.mean(tmpdata), statistics.stdev(tmpdata)
                        mean, std = np.round(mean, 4), np.round(std, 4)
                        # fill the lists
                        testItem_list.append(item)
                        group_list.append(group)
                        asicItem_list.append(asicItem)
                        bl_list.append(BL)
                        mean_list.append(mean)
                        std_list.append(std)
                        #
                        x = np.linspace(xmin, xmax, len(tmpdata))
                        p = norm.pdf(x, mean, std)
                        plt.figure()
                        plt.hist(tmpdata, bins=Nbins, density=True)
                        plt.plot(x, p, 'r', label='mean = {}, std = {}'.format(mean, std))
                        plt.xlabel(group);plt.ylabel('#')
                        # plt.show()
                        plt.legend()
                        plt.savefig('/'.join([self.output_fig, filename + '.png']))
                        plt.close()
                Item_df = pd.DataFrame({'testItem': testItem_list, 'feature': group_list, 'cfg': asicItem_list, 'BL': bl_list, 'mean': mean_list, 'std': std_list})
                OUTPUT_DF = pd.concat([OUTPUT_DF, Item_df], axis=0, ignore_index=True)
        OUTPUT_DF.sort_values(by=['testItem'], axis=0, inplace=True, ignore_index=True)
        OUTPUT_DF.to_csv('/'.join([self.output_path, 'StatAna_CHKRES.csv']), index=False)

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
    #     # chk_res.extractData()
    # #     break
    # chkres_stat = QC_CHKRES_StatAna(root_path=root_path, output_path=output_path)
    # chkres_stat.run_Ana()