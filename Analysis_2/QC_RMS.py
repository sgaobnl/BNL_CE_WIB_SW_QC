############################################################################################
#   created on 6/11/2024 @ 18:49
#   email: radofanantenan.razakamiandra@stonybrook.edu
#   Analyze the data in QC_RMS.bin
############################################################################################

import os, sys, pickle, json, statistics, csv
from scipy.stats import norm
import numpy as np
from utils import dumpJson, createDirs, decodeRawData, printItem, LArASIC_ana, BaseClass, BaseClass_Ana
import matplotlib.pyplot as plt
import pandas as pd

class RMS(BaseClass):
    def __init__(self, root_path: str, data_dir: str, output_path: str, env='RT'):
        printItem("FE noise measurement")
        super().__init__(root_path=root_path, data_dir=data_dir, output_path=output_path, QC_filename='QC_RMS.bin', tms=5, env=env)
        if self.ERROR:
            return
        self.CFG_datasheet = self.getCFGs()
        self.period = 500
    
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
        for config in self.params:
            tmp_cfg = self.decodeCFG(config=config)
            cfg_dict[config]  = tmp_cfg[config]
        return cfg_dict

    def decode_oneRMS(self, config: str):
        fembs = self.raw_data[config][0]
        raw_data = self.raw_data[config][1]
        cfg_info = self.raw_data[config][2]
        decodedRMS = decodeRawData(fembs=fembs, rawdata=raw_data, period=self.period)
        out_dict = {self.logs_dict['FE{}'.format(ichip)]: dict() for ichip in range(8)}
        for ichip in range(8):
            FE_ID = self.logs_dict['FE{}'.format(ichip)]
            larasic = LArASIC_ana(dataASIC=decodedRMS[ichip], output_dir=self.FE_outputDIRs[FE_ID], chipID=FE_ID, tms=self.tms, param=config, generatePlots=False, generateQCresult=False, period=self.period)
            pedrms = larasic.runAnalysis(getPulseResponse=True, isRMSNoise=True)
            out_dict[FE_ID][config] = {
                'pedestal': pedrms['pedrms']['pedestal']['data'],
                'rms': pedrms['pedrms']['rms']['data']
            }
        return out_dict

    def decodeRMS(self):
        if self.ERROR:
            return
        out_dict = {self.logs_dict['FE{}'.format(ichip)]: dict() for ichip in range(8)}
        for config in self.params:
            print("configuration : {}".format(config))
            tmp = self.decode_oneRMS(config=config) 
            for ichip in range(8):
                FE_ID = self.logs_dict['FE{}'.format(ichip)]
                out_dict[FE_ID][config] = tmp[FE_ID][config]
        #logs = {
        #    "date": self.logs_dict['date'],
        #    "testsite": self.logs_dict['testsite'],
        #    "env": self.logs_dict['env'],
        #    "note": self.logs_dict['note'],
        #    "DAT_SN": self.logs_dict['DAT_SN'],
        #    "WIB_slot": self.logs_dict['DAT_on_WIB_slot']
        #}
        FE_IDs = []
        for ichip in range(8):
        #    pedrms_dict = {"logs": logs}
            pedrms_dict = {}
            FE_ID = self.logs_dict['FE{}'.format(ichip)]
            FE_IDs.append(FE_ID)
            for config in self.params:
                pedrms_dict[config] = dict()
                pedrms_dict[config]['CFG'] = self.CFG_datasheet[config]
                for key in out_dict[FE_ID][config].keys():
                    pedrms_dict[config][key] = out_dict[FE_ID][config][key]
            dumpJson(output_path=self.FE_outputDIRs[FE_ID], output_name='QC_RMS', data_to_dump=pedrms_dict)
        return FE_IDs

class RMS_Ana(BaseClass_Ana):
    def __init__(self, root_path: str, output_path: str, chipID: str):
        self.item = 'QC_RMS'
        print (self.item)
        self.tms = 5
        super().__init__(root_path=root_path, chipID=chipID, output_path=output_path, item=self.item)
        self.root_path = root_path
        self.output_path = output_path
        #self.output_dir = '/'.join([self.output_dir, self.item])
        #try:
        #    os.mkdir(self.output_dir)
        #except OSError:
        #    pass
        #print(self.output_dir)
        ## sys.exit()
    
    def _FileExist(self):
        chipDir = '/'.join([self.output_path, self.chipID])
        chipDirExist = os.path.isdir(chipDir)
        #qcMondirExist = os.path.isdir('/'.join([chipDir, 'QC_RMS']))
        feMonFileExist = os.path.isfile('/'.join([chipDir, 'QC_RMS.json']))
        return  feMonFileExist

    def getItem(self,config=''):
        data = self.data[config]
        return data, config

    def plot_rms_data(self, dict_data, config):
        decodedConfig = dict_data['CFG']
        ped = dict_data['pedestal']
        rms = dict_data['rms']
        # plot of pedestal vs CH
        fig, ax = plt.subplots(1,2,figsize=(5*2,5))
        ax[0].plot(np.arange(16), ped, '.-')
        ax[0].set_xlabel('CH')
        ax[0].set_ylabel('Pedestal')
        # plot of RMS vs CH
        ax[1].plot(np.arange(16), rms, '.-')
        ax[1].set_xlabel('CH')
        ax[1].set_ylabel('RMS')
        plt.savefig('/'.join([self.output_path, config + '.png']))
        plt.close()

    def run_Ana(self, path_to_statAna=None, generatePlots=False):
        """
        Analyze RMS test data and optionally compare with statistical thresholds.
        
        Args:
            path_to_statAna (str, optional): Path to CSV file with statistical thresholds.
                                            If None, only raw data analysis is performed.
            generatePlots (bool): Whether to generate plots for each configuration.
        
        Returns:
            list: List of result rows containing test data and analysis results
        """
        if not self._FileExist():
            return None

        data_df = pd.DataFrame({'cfg': []})
        result_table = []

        # Load statistical data if provided
        stat_df = None
        if path_to_statAna:
            stat_df = pd.read_csv(path_to_statAna)

        for config in self.params:
            data, cfg = self.getItem(config=config)
            
            if generatePlots:
                self.plot_rms_data(dict_data=data, config=cfg)

            # Create basic dataframe with measurements
            df = pd.DataFrame({
                'cfg': [cfg for _ in range(len(data['pedestal']))],
                'CH': [chn for chn in range(16)],
                'pedestal': data['pedestal'],
                'rms': data['rms']
            })

            # Apply statistical analysis if data available
            qc_result = None
            if stat_df is not None:
                stat_config_row = stat_df[stat_df['cfg']==config].copy().reset_index().drop('index', axis=1)
                
                # Add statistical data
                stat_dict = {
                    'mean_pedestal': [stat_config_row['mean_pedestal'][0] for _ in range(16)],
                    'mean_rms': [stat_config_row['mean_rms'][0] for _ in range(16)],
                    'std_pedestal': [stat_config_row['std_pedestal'][0] for _ in range(16)],
                    'std_rms': [stat_config_row['std_rms'][0] for _ in range(16)]
                }
                
                for key, val in stat_dict.items():
                    df[key] = val

                # Perform QC checks
                df['QC_result_pedestal'] = (
                    (df['pedestal'] >= (df['mean_pedestal']-3*df['std_pedestal'])) & 
                    (df['pedestal'] <= (df['mean_pedestal']+3*df['std_pedestal']))
                )
                df['QC_result_rms'] = (
                    (df['rms'] >= (df['mean_rms']-3*df['std_rms'])) & 
                    (df['rms'] <= (df['mean_rms']+3*df['std_rms']))
                )

                # Determine overall result
                qc_res_ped = 'FAILED' if False in df['QC_result_pedestal'] else 'PASSED'
                qc_res_rms = 'FAILED' if False in df['QC_result_rms'] else 'PASSED'
                qc_result = 'FAILED' if 'FAILED' in [qc_res_ped, qc_res_rms] else 'PASSED'

                # Clean up statistical columns
                for key in stat_dict.keys():
                    df.drop(key, axis=1, inplace=True)

            # Build result row
            row_table = []
            if qc_result is not None:
                row_table = [f'Test_0{self.tms}_RMS', config, qc_result]
            else:
                row_table = [f'Test_0{self.tms}_RMS', config]
            for chn in range(len(df['CH'])):
                ped = df.iloc[chn]['pedestal']
                rms = df.iloc[chn]['rms']
                row_table.append(f"CH{chn}=(pedestal={ped};rms={rms})")
            result_table.append(row_table)

            # Concatenate to main dataframe
            data_df = df if data_df.empty else pd.concat([data_df, df], axis=0).reset_index().drop('index', axis=1)

        # Save results
        #if not data_df.empty:
        #    data_df.to_csv(f'{self.output_path}/{self.chipID}/{self.item}.csv', index=False)
        #with open('/'.join([self.output_path, self.chipID, '{}.csv'.format(self.item)]), 'w') as csvfile:
        #    csv.writer(csvfile, delimiter=',').writerows(result_table)    

        return result_table

    # def run_Ana(self, path_to_statAna='', generatePlots=False):
    #     if self._FileExist():
    #         stat_csv = pd.read_csv(path_to_statAna)
                        
    #         result_df = pd.DataFrame({'cfg': []})
    #         for icfg, config in enumerate(self.params):
    #             data ,cfg = self.getItem(config=config)
    #             # stat_config_df = new_stat_csv[new_stat_csv['cfg']==cfg].copy().reset_index().drop('index', axis=1).copy()
    #             stat_config_row = stat_csv[stat_csv['cfg']==config].copy().reset_index().drop('index', axis=1)
    #             stat_dict = {
    #                 'mean_pedestal': [stat_config_row['mean_pedestal'][0] for _ in range(16)],
    #                 'mean_rms': [stat_config_row['mean_rms'][0] for _ in range(16)],
    #                 'std_pedestal': [stat_config_row['std_pedestal'][0] for _ in range(16)],
    #                 'std_rms': [stat_config_row['std_rms'][0] for _ in range(16)]
    #             }

    #             # print(stat_config_row.columns)
    #             # sys.exit()
    #             # print(data, config)
    #             if generatePlots:
    #                 self.plot_rms_data(dict_data=data, config=cfg)
    #             # print(self.chipID)
    #             df = pd.DataFrame({'cfg': [cfg for _ in range(len(data['pedestal']))], 'CH': [chn for chn in range(16)], 'pedestal': data['pedestal'], 'rms': data['rms']})
    #             for key, val in stat_dict.items():
    #                 df[key] = val
    #             df['QC_result_pedestal']= (df['pedestal']>= (df['mean_pedestal']-3*df['std_pedestal'])) & (df['pedestal'] <= (df['mean_pedestal']+3*df['std_pedestal']))
    #             df['QC_result_rms']= (df['rms']>= (df['mean_rms']-3*df['std_rms'])) & (df['rms'] <= (df['mean_rms']+3*df['std_rms']))
    #             # print(df.shape)
    #             # print(df)
    #             # print(df.columns)
    #             for key in stat_dict.keys():
    #                 df.drop(key, axis=1, inplace=True)
    #             # print(df.columns)
    #             if icfg==0:
    #                 result_df = df.copy()
    #             else:
    #                 result_df = pd.concat([result_df, df], axis=0).reset_index().drop('index', axis=1)
    #         # save dataframe to csv
    #         result_df.to_csv('/'.join([self.output_dir, self.item+'.csv']), index=False)
    #         # convert dataframe to an array of arrays
    #         result_table = []
    #         for config in self.params:
    #             qc_res_ped = 'PASSED'
    #             qc_res_rms = 'PASSED'
    #             tmp_df = result_df[result_df['cfg']==config].copy().reset_index().drop('index', axis=1)
    #             if False in tmp_df['QC_result_pedestal']:
    #                 qc_res_ped = 'FAILED'
    #             if False in tmp_df['QC_result_rms']:
    #                 qc_res_rms = 'FAILED'
    #             qc_result = 'PASSED'
    #             if 'FAILED' in [qc_res_ped, qc_res_rms]:
    #                 qc_result = 'FAILED'
    #             row_table = ['Test_0{}_RMS'.format(self.tms), config, qc_result]
    #             for chn in range(len(tmp_df['CH'])):
    #                 ped = tmp_df.iloc[chn]['pedestal']
    #                 rms = tmp_df.iloc[chn]['rms']
    #                 row_table.append("CH{}=(pedestal={};rms={})".format( chn, ped, rms ))
    #             result_table.append(row_table)
    #         return result_table
    #     else:
    #         return

class RMS_StatAna():
    def __init__(self, root_path: str, output_path: str):
        self.root_path = root_path
        self.output_path = output_path
        self.output_fig = '/'.join([output_path, 'fig'])
        try:
            os.mkdir(self.output_fig)
        except:
            pass
        
    def _FileExist(self, chipDir:str):
        chipDirExist = os.path.isdir(chipDir)
        qcMondirExist = os.path.isdir('/'.join([chipDir, 'QC_RMS']))
        feMonFileExist = os.path.isfile('/'.join([chipDir, 'QC_RMS/RMS_Noise.json']))
        return chipDirExist and qcMondirExist and feMonFileExist
    
    def getItems(self):
        list_chipID = os.listdir(self.root_path)
        cfg_map = dict()
        i = 0
        out_dict = dict()
        keys = []
        for chipID in list_chipID:
            path_to_chip = '/'.join([self.root_path, chipID])
            if not self._FileExist(chipDir=path_to_chip):
                continue
            path_to_file = '/'.join([path_to_chip, 'QC_RMS/RMS_Noise.json'])
            data = json.load(open(path_to_file))
            if i==0:
                keys = [k for k in data.keys() if k!='logs']
                # get configurations
                for key in keys:
                    cfg_map[key] = data[key]['CFG']
                    out_dict[key] = {'pedestal': np.array([]), 'rms': np.array([])}
            for key in keys:
                out_dict[key]['pedestal'] = np.append(out_dict[key]['pedestal'], data[key]['pedestal'])
                out_dict[key]['rms'] = np.append(out_dict[key]['rms'], data[key]['rms'])
            i += 1
        return out_dict, cfg_map

    def run_Ana(self):
        ######################################
        print("QC RMS statistical analysis....")
        ######################################
        data, configurations = self.getItems()
        cfg_list = []
        mean_ped, std_ped = [], []
        mean_rms, std_rms = [], []
        for cfg in configurations.keys():
            print('CFG = {}...'.format(cfg))
            # Pedestal
            tmpdata = data[cfg]['pedestal']
            median, std = statistics.median(tmpdata), statistics.stdev(tmpdata)
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

            # cfg_list.append(cfg)
            mean_ped.append(median)
            std_ped.append(std)
            # print(median, std)

            x = np.linspace(xmin, xmax, len(tmpdata))
            p = norm.pdf(x, median, std)
            plt.figure()
            plt.hist(tmpdata, bins=len(tmpdata)//128, density=True)
            plt.plot(x, p, 'r', label='mean = {}, std = {}'.format(median, std))
            plt.xlabel('-'.join(['Pedestal', cfg]));plt.ylabel('#')
            plt.legend()
            plt.savefig('/'.join([self.output_fig, 'QC_RMS_Pedestal_{}.png'.format(cfg)]))
            plt.close()
            # sys.exit()
            #
            # RMS
            tmpdata = data[cfg]['rms']
            median, std = statistics.median(tmpdata), statistics.stdev(tmpdata)
            xmin, xmax = np.min(tmpdata), np.max(tmpdata)
            for _ in range(350):
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

            cfg_list.append(cfg)
            mean_rms.append(median)
            std_rms.append(std)
            
            x = np.linspace(xmin, xmax, len(tmpdata))
            p = norm.pdf(x, median, std)
            plt.figure()
            plt.hist(tmpdata, bins=len(tmpdata)//128, density=True)
            plt.plot(x, p, 'r', label='mean = {}, std = {}'.format(median, std))
            plt.xlabel('-'.join(['RMS', cfg]));plt.ylabel('#')
            plt.legend()
            plt.savefig('/'.join([self.output_fig, 'QC_RMS_RMS_{}.png'.format(cfg)]))
            plt.close()

        OUTPUT_DF = pd.DataFrame({'cfg': cfg_list, 'mean_pedestal': mean_ped, 'std_pedestal': std_ped, 'mean_rms': mean_rms, 'std_rms': std_rms})
        OUTPUT_DF.to_csv('/'.join([self.output_path, 'StatAna_RMS.csv']), index=False)
        pd.DataFrame(configurations).to_csv('/'.join([self.output_path, 'QC_RMS_CONFIG_MAP.csv']))

if __name__ == '__main__':
    root_path = "E:/B009T0008/"
    output_path = root_path + "Ana"
    data_dir = "Time_20250527114445_DUT_0000_1001_2002_3003_4004_5005_6006_7007"
    env = 'RT'
    rms = RMS(root_path=root_path, data_dir=data_dir, output_path=output_path, env=env)
    rms.decodeRMS()
    # root_path = '../../Data_BNL_CE_WIB_SW_QC'
    # output_path = '../../Analyzed_BNL_CE_WIB_SW_QC'
    # # list_data_dir = [dir for dir in os.listdir(root_path) if '.zip' not in dir]
    # root_path = '../../B010T0004'
    # list_data_dir = [dir for dir in os.listdir(root_path) if (os.path.isdir('/'.join([root_path, dir]))) and (dir!='images')]
    # for i, data_dir in enumerate(list_data_dir):
    #     rms = RMS(root_path=root_path, data_dir=data_dir, output_path=output_path)
    #     rms.decodeRMS()
    # root_path = '../../Analyzed_BNL_CE_WIB_SW_QC'
    # output_path = '../../Analysis'
    #root_path = '../../out_B010T0004_'
    #output_path = '../../analyzed_B010T0004_'
    #rms_stat = RMS_StatAna(root_path=root_path, output_path=output_path)
    #rms_stat.run_Ana()
    ##
    ##
    # root_path = '../../Analyzed_BNL_CE_WIB_SW_QC'
    # output_path = '../../Analysis'
    # list_chipID = os.listdir(root_path)
    # for chipID in list_chipID:
    #     rms_ana = RMS_Ana(root_path=root_path, output_path=output_path, chipID=chipID)
    #     rms_ana.run_Ana(path_to_statAna='/'.join([output_path, 'StatAna_RMS.csv']), generatePlots=False)
