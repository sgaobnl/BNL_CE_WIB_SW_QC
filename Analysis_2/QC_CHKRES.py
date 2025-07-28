############################################################################################
#   created on 6/5/2024 @ 13:43
#   email: radofanantenan.razakamiandra@stonybrook.edu
#   Analyze the data in QC_CHKRES.bin
############################################################################################

# from datetime import datetime
import os, sys, csv
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statistics
from scipy.stats import norm
from utils import printItem, dumpJson, decodeRawData, LArASIC_ana, BaseClass
from utils import BaseClass_Ana

class QC_CHKRES(BaseClass):
    def __init__(self, root_path: str, data_dir: str, output_dir: str, env='RT'):
        printItem("FE response measurement")
        super().__init__(root_path=root_path, data_dir=data_dir, output_path=output_dir, tms=2, QC_filename='QC_CHKRES.bin', env=env)
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
        FE_IDs = []
        for ichip in range(8):
            ASIC_ID = self.logs_dict['FE{}'.format(ichip)]
            FE_IDs.append(ASIC_ID)
            allchip_data[ASIC_ID] = {
#                "logs":{
#                    "date": self.logs_dict['date'],
#                    "testsite": self.logs_dict['testsite'],
#                    "env": self.logs_dict['env'],
#                    "note": self.logs_dict['note'],
#                    "DAT_SN": self.logs_dict['DAT_SN'],
#                    "WIB_slot": self.logs_dict['DAT_on_WIB_slot']
#                }
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
        return FE_IDs

class QC_CHKRES_Ana(BaseClass_Ana):
    def __init__(self, root_path: str, chipID: str, output_path: str):
        self.item = 'QC_CHKRES'
        self.tms = '02'
        super().__init__(root_path=root_path, chipID=chipID, output_path=output_path, item=self.item)
        self.root_path = root_path
        self.output_path = output_path
        #self.output_dir = '/'.join([self.output_dir, self.item])
        #print(self.output_dir)
        #try:
        #    os.mkdir(self.output_dir)
        #except OSError:
        #    pass

    def makePlots(self):
        if self.ERROR:
            return
        items_to_plot = ['pedestal', 'rms', 'pospeak', 'negpeak']
        groups = ['GAINs', 'OUTPUT', 'BL', 'TP', 'SLKS']
        for item_to_plot in items_to_plot:
            for group in groups:
                self.ChResp_ana(item_to_plot=item_to_plot, group=group)

    def extractData_forStat(self):
        items = ['pedestal', 'rms', 'pospeak', 'negpeak']
        groups = ['GAINs', 'OUTPUT', 'BL', 'TP', 'SLKS']
        out_dict = dict()
        for group in groups:
            out_dict[group] = {item: dict() for item in items}
        # print(out_dict)
        for item in items:
            for group in groups:
                configs, means, stds, mins, maxs, cfgs_dict = self.ChResp_ana(item_to_plot=item, group=group, returnData=True)
                out_dict[group][item] = {c: dict() for c in configs}

                if group=='GAINs':
                    for i, c in enumerate(configs):
                        out_dict[group][item][c]['mean'] = {'200mV': means[0][i], '900mV': means[1][i]}
                        out_dict[group][item][c]['min'] = {'200mV': mins[0][i], '900mV': mins[1][i]}
                        out_dict[group][item][c]['max'] = {'200mV': maxs[0][i], '900mV': maxs[1][i]}
                        out_dict[group][item][c]['cfgs_dict'] = {'200mV': cfgs_dict[0][i], '900mV': cfgs_dict[1][i]}
                else:
                    for i, c in enumerate(configs):
                        out_dict[group][item][c]['mean'] = means[i]
                        out_dict[group][item][c]['min'] = mins[i]
                        out_dict[group][item][c]['max'] = maxs[i]
                        out_dict[group][item][c]['cfgs_dict'] = cfgs_dict[i]

        return out_dict
    
    def extractData(self):
        data_dict = {'testItem': [], 'cfg': [], 'feature': [], 'CH': [], 'data': []}
        mapping_params = {}
        for param in self.params:
            param_data = self.getoneConfigData(config=param)
            mapping_params[param] = param_data['CFG_info']
            param_splitted = param.split('_')
            testItem = param_splitted[1]
            config = '_'.join(param_splitted[2:])
            # print(testItem, config)
            # print(param_data)
            # print(mapping_params)
            features = [f for f in param_data.keys() if f!='CFG_info']
            # print(features)
            for feature in features:
                feature_data = param_data[feature]
                for ich, d in enumerate(feature_data):
                    data_dict['testItem'].append(testItem)
                    data_dict['cfg'].append(config)
                    data_dict['feature'].append(feature)
                    data_dict['CH'].append(ich)
                    data_dict['data'].append(d)
        # print(mapping_params)
        # sys.exit()
        return pd.DataFrame(data_dict), mapping_params

    def run_Ana(self, path_to_stat=None):
        """
        Analyze test data and optionally compare with statistical thresholds.
        
        Args:
            path_to_stat (str, optional): Path to CSV file with statistical thresholds.
                                        If None, only raw data analysis is performed.
        
        Returns:
            list: List of result rows containing test data and analysis results
        """
        if self.ERROR:
            return None

        data_df, mapping_params = self.extractData()
        #dumpJson(output_path=self.output_path, output_name=self.chipID+'_mapping', data_to_dump=mapping_params)

        # Load statistical data if provided
        stat_df = None
        if path_to_stat:
            stat_df = pd.read_csv(path_to_stat)

        testItems = data_df['testItem'].unique()
        full_result_rows = []

        for testItem in testItems:
            item_data = data_df[data_df['testItem']==testItem].copy()
            stat_item = stat_df[stat_df['testItem']==testItem].copy() if stat_df is not None else None
            
            for cfg in item_data['cfg'].unique():
                cfg_data = item_data[item_data['cfg']==cfg].copy()
                stat_cfg = stat_item[stat_item['cfg']==cfg].copy() if stat_df is not None else None
                
                for feature in cfg_data['feature'].unique():
                    feature_data = cfg_data[cfg_data['feature']==feature].copy()
                    
                    # Apply statistical analysis if data available
                    result = None
                    if stat_df is not None:
                        stat_feature = stat_cfg[stat_cfg['feature']==feature].copy()
                        feature_data['mean'] = [stat_feature.iloc[0]['mean'] for _ in range(16)]
                        feature_data['std'] = [stat_feature.iloc[0]['std'] for _ in range(16)]
                        feature_data[f'QC_result_{testItem}'] = (
                            (feature_data['data'] >= (feature_data['mean']-3*feature_data['std'])) & 
                            (feature_data['data'] <= (feature_data['mean']+3*feature_data['std']))
                        )
                        result = 'FAILED' if False in feature_data[f'QC_result_{testItem}'] else 'PASSED'
                        feature_data.drop(['mean', 'std', f'QC_result_{testItem}'], axis=1, inplace=True)

                    if result is not None:
                        # Create result row
                        feature_result_row = [
                            f'Test_{self.tms}_{self.item}',
                            f'{cfg}_{feature}',
                            result
                        ]
                    else:
                        # Create result row
                        feature_result_row = [
                            f'Test_{self.tms}_{self.item}',
                            f'{cfg}_{feature}'
                        ]

                    # Add channel data
                    for ch in feature_data['CH']:
                        chdata = f'CH{ch}={feature_data.iloc[ch]["data"]}'
                        feature_result_row.append(chdata)

                    # Optional debug output
                    if stat_df is not None and stat_feature is not None:
                        print(result, feature_data)
                        print(stat_feature)

                    full_result_rows.append(feature_result_row)
        if len(full_result_rows)!=0:
            with open('/'.join([self.output_path, self.chipID, '{}.csv'.format(self.item)]), 'w') as csvfile:
                csv.writer(csvfile, delimiter=',').writerows(full_result_rows)
        return full_result_rows
    # def run_Ana(self, path_to_stat=''):
    #     if self.ERROR:
    #         return None
    #     stat_ana_df = pd.read_csv(path_to_stat)
    #     #
    #     data_df, mapping_params = self.extractData()
    #     # print(mapping_params)
    #     dumpJson(output_path=self.output_dir, output_name=self.chipID+'_mapping', data_to_dump=mapping_params)
    #     #
    #     testItems = data_df['testItem'].unique()
    #     full_result_rows = []
    #     for testItem in testItems:
    #         item_result_rows = []
    #         itemData = data_df[data_df['testItem']==testItem].copy()
    #         stat_ana_item = stat_ana_df[stat_ana_df['testItem']==testItem].copy()
    #         configurations = itemData['cfg'].unique()
    #         for cfg in configurations:
    #             cfg_result_rows = []
    #             cfg_data = itemData[itemData['cfg']==cfg].copy()
    #             stat_ana_cfg = stat_ana_item[stat_ana_item['cfg']==cfg].copy()
    #             features = cfg_data['feature'].unique()
    #             for feature in features:
    #                 feature_data = cfg_data[cfg_data['feature']==feature].copy()
    #                 stat_ana_feature = stat_ana_cfg[stat_ana_cfg['feature']==feature].copy()
    #                 feature_data['mean'] = [stat_ana_feature.iloc[0]['mean'] for _ in range(16)]
    #                 feature_data['std'] = [stat_ana_feature.iloc[0]['std'] for _ in range(16)]
    #                 feature_data['QC_result_{}'.format(testItem)]= (feature_data['data']>= (feature_data['mean']-3*feature_data['std'])) & (feature_data['data'] <= (feature_data['mean']+3*feature_data['std']))
    #                 result = 'PASSED'
    #                 if False in feature_data['QC_result_{}'.format(testItem)]:
    #                     result = 'FAILED'
    #                 feature_data.drop(['mean', 'std', 'QC_result_{}'.format(testItem)], axis=1, inplace=True)
    #                 feature_result_row = ['Test_{}_{}'.format(self.tms, self.item), cfg+'_'+feature, result]
    #                 for ch in feature_data['CH']:
    #                     chdata = 'CH{}={}'.format(ch, feature_data.iloc[ch]['data'])
    #                     feature_result_row.append(chdata)
    #                 cfg_result_rows.append(feature_result_row)
    #             item_result_rows += cfg_result_rows
    #         full_result_rows += item_result_rows
    #     return full_result_rows

#---------------------------
# Class for statistical analysis
#--------------------------
class QC_CHKRES_StatAna():
    def __init__(self, root_path: str, output_path: str):
        self.root_path = root_path
        self.output_path = output_path
        self.output_fig = '/'.join([output_path, 'fig'])
        try:
            os.mkdir(self.output_fig)
        except:
            pass

    def get_mean_std(self, tmpdata):
        median = statistics.median(tmpdata)
        std = statistics.stdev(tmpdata)
        xmin, xmax = np.min(tmpdata), np.max(tmpdata)

        for _ in range(100):
            if xmin < median-3*std:
                posMin = np.where(tmpdata==xmin)[0]
                # del tmpdata[posMin]
                tmpdata = np.delete(np.array(tmpdata), posMin)
            if xmax > median+3*std:
                posMax = np.where(tmpdata==xmax)[0]
                # del tmpdata[posMax]
                tmpdata = np.delete(np.array(tmpdata), posMax)

            xmin, xmax = np.min(tmpdata), np.max(tmpdata)
            median, std = statistics.median(tmpdata), statistics.stdev(tmpdata)
        median, std = np.round(median, 4), np.round(std, 4)
        return median, std
    
    def getItems(self):
        data_df = pd.DataFrame()
        FirstData = True
        list_chipID = os.listdir(self.root_path)
        for chipID in list_chipID:
            chkres = QC_CHKRES_Ana(root_path=self.root_path, chipID=chipID, output_path='')
            if chkres.ERROR==True:
                continue
            chkres_data, mapping_parms = chkres.extractData()
            # print(chkres_data)
            if FirstData:
                data_df = chkres_data.copy()
                FirstData = False
            else:
                data_df = pd.concat([data_df, chkres_data.copy()], axis=0, ignore_index=True)
                # break # comment this in real analysis
        return data_df
    
    def run_Ana(self):
        stat_ana_df = {'testItem': [], 'cfg': [], 'feature': [], 'mean': [], 'std': []}
        data_df = self.getItems()
        testItems = data_df['testItem'].unique()
        # configurations = data_df['cfg'].unique()
        # features = data_df['feature'].unique()
        for testItem in testItems:
            testItem_data = data_df[data_df['testItem']==testItem].copy()
            configurations = testItem_data['cfg'].unique()
            for cfg in configurations:
                cfg_data = testItem_data[testItem_data['cfg']==cfg].copy()
                features = cfg_data['feature'].unique()
                for feature in features:
                    feature_data = cfg_data[cfg_data['feature']==feature].copy()
                    mean, std = self.get_mean_std(tmpdata=np.array(feature_data['data']))
                    stat_ana_df['testItem'].append(testItem)
                    stat_ana_df['cfg'].append(cfg)
                    stat_ana_df['feature'].append(feature)
                    stat_ana_df['mean'].append(mean)
                    stat_ana_df['std'].append(std)
        stat_ana_df = pd.DataFrame(stat_ana_df).sort_values(by='testItem', ascending=True)
        stat_ana_df.to_csv('/'.join([self.output_path, 'StatAna_CHKRES.csv']), index=False)


if __name__ == "__main__":
    root_path = "E:/B009T0008/"
    output_path = root_path + "Ana"
    data_dir = "Time_20250527114445_DUT_0000_1001_2002_3003_4004_5005_6006_7007"
    env = 'RT'
    qc_checkres = QC_CHKRES(root_path=root_path, data_dir=data_dir, output_dir=output_path, env=env)
    qc_checkres.decode_CHKRES()
    
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
    # root_path = '../../Analyzed_BNL_CE_WIB_SW_QC'
    # output_path = '../../Analysis'
    #root_path = '../../out_B010T0004_'
    #output_path = '../../analyzed_B010T0004_'
    # list_chipID = os.listdir(root_path)
    # for chipID in list_chipID:
    #     chk_res = QC_CHKRES_Ana(root_path=root_path, chipID=chipID, output_path=output_path)
    #     chk_res.run_Ana(path_to_stat='/'.join([output_path, 'StatAna_CHKRES.csv']))
    #     sys.exit()
    #     chk_res.makePlots()
    #     # chk_res.extractData()
    # #     break
    #chkres_stat = QC_CHKRES_StatAna(root_path=root_path, output_path=output_path)
    #chkres_stat.run_Ana()
