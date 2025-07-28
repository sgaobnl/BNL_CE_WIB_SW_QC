############################################################################################
    #stat.run_Ana()
#   created on 6/9/2024 @ 17:13
#   email: radofanantenan.razakamiandra@stonybrook.edu
#   Decode QC_MON.bin
############################################################################################

import numpy as np
import os, sys, csv
from utils import printItem, createDirs, dumpJson, linear_fit, BaseClass, gain_inl
import json, statistics
from scipy.stats import norm
import pandas as pd

class FE_MON(BaseClass):
    def __init__(self, root_path: str, data_dir: str, output_path: str, env='RT'):
        self.tms = 3
        printItem(item="FE monitoring")
        super().__init__(root_path=root_path, data_dir=data_dir, output_path=output_path, QC_filename='QC_MON.bin', tms=self.tms, env=env)
        if self.ERROR:
            return
        self.mon_params = self.params

    def getBaselines(self):
        '''
        OUTPUT:
        {
            "chipID0": {
                "200mV": [],
                "900mV": []
            },
            "chipID1": {
                "200mV": [],
                "900mV": []
            },
            ...
        }
        '''
        Baselines = ['MON_200BL', 'MON_900BL']
        bl_dict = {
            'MON_200BL': '200mV',
            'MON_900BL': '900mV'
        }
        out_dict = {self.logs_dict['FE{}'.format(ichip)]: dict() for ichip in range(8)}
        for BL in Baselines:
            print("Item : {}".format(BL))
            all_chips_BL = self.raw_data[BL]
            ## organize the raw_data
            ## ==> [[16channels], [16channels], ...] : each element corresponds to the data for each LArASIC
            tmp_data = [[] for _ in range(8)]
            for ich in range(16):
                chdata = all_chips_BL[ich][1]
                for ichip in range(8):
                    tmp_data[ichip].append(chdata[ichip])
            
            ## Save the LArASIC's data to out_dict
            for ichip in range(8):
                FE_ID = self.logs_dict['FE{}'.format(ichip)]
                out_dict[FE_ID][bl_dict[BL]] = tmp_data[ichip]
        return out_dict

    def getvgbr_temp(self, unitOutput='mV'):
        '''
            Structure of the raw data:
                [[8chips], np.array([8chips])]
                ==> 1st element: VBGR, Mon_Temperature, or Mon_VGBR of 8 chips in ADC bit
                ==> 2nd element: VBGR, Mon_Temperature, or Mon_VGBR of 8 chips in mV
            OUTPUT:
            {
                "chipID0": {
                    "unit": unitOutput,
                    "VBGR": val,
                    "MON_Temper": val,
                    "MON_VBGR": val
                },
                "chipID1": {
                    "unit": unitOutput,
                    "VBGR": val,
                    "MON_Temper": val,
                    "MON_VBGR": val
                },
                ...
            }
        '''
        params = ['VBGR', 'MON_Temper', 'MON_VBGR']
        unitChoice = {
            'mV': 1,
            'ADC_bit': 0
        }
        out_dict = {self.logs_dict['FE{}'.format(ichip)]: {'unit': unitOutput} for ichip in range(8)}
        for param in params:
            print("Item : {}".format(param))
            tmp_data = self.raw_data[param][unitChoice[unitOutput]]
            for ichip in range(8):
                FE_ID = self.logs_dict['FE{}'.format(ichip)]
                out_dict[FE_ID][param] = tmp_data[ichip]
        return out_dict

    def mon_dac(self):
        '''
            Output:
             {
                "chipID0":{
                    "config0": {
                        "DAC": [],
                        "data": []
                    },
                    "config1": {
                        "DAC": [],
                        "data": []
                    },
                    ...
                },
                "chipID1":{
                    "config0": {
                        "DAC": [],
                        "data": []
                    },
                    "config1": {
                        "DAC": [],
                        "data": []
                    },
                    ...
                },
                ...
             }
            where len(DAC) = 64
        '''
        # print(self.raw_data)
        tmpout_dict = dict()
        params = [param for param in self.mon_params if 'DAC' in param]
        for param in params:
            print("configuration : {}".format(param))
            data = self.raw_data[param]
            dac_values = []
            dacperchip = [[] for _ in range(8)]
            for idac in range(64):
                dac_val = data[idac][0]
                chipsperDAC = data[idac][1]
                dac_values.append(dac_val)
                for ichip in range(8):
                    dacperchip[ichip].append(chipsperDAC[ichip])
            config = '_'.join( [p for p in param.split('_') if p!='MON'] )    
            tmpout_dict[config] = {"dac_values": dac_values, "all_chipsdata": dacperchip}
        
        OUT_dict = {self.logs_dict['FE{}'.format(ichip)]: dict() for ichip in range(8)}
        for ichip in range(8):
            FE_ID = self.logs_dict['FE{}'.format(ichip)]
            for config in tmpout_dict.keys():
                OUT_dict[FE_ID][config] = {
                    "DAC": tmpout_dict[config]["dac_values"],
                    "data": tmpout_dict[config]["all_chipsdata"][ichip]
                }
        return OUT_dict
    
    def decodeFE_MON(self):
        if self.ERROR:
            return
        #logs = {
        #    "date": self.logs_dict['date'],
        #    "testsite": self.logs_dict['testsite'],
        #    "env": self.logs_dict['env'],
        #    "note": self.logs_dict['note'],
        #    "DAT_SN": self.logs_dict['DAT_SN'],
        #    "WIB_slot": self.logs_dict['DAT_on_WIB_slot']
        #}
        BL = self.getBaselines()
        vbgr_temp = self.getvgbr_temp(unitOutput='mV')
        dac_meas = self.mon_dac()
        FE_IDs = []
        for ichip in range(8):
            FE_ID = self.logs_dict['FE{}'.format(ichip)]
            FE_IDs.append(FE_ID)
            dac_meas_chip = dac_meas[FE_ID]
            for config in dac_meas_chip.keys():
                #### In case a linearity range is needed from the monitoring, refer to this line
                AD_LSB = 2564/4096 # LSB in mV / ADC bit
                GAIN, Yintercept, INL = linear_fit(x=dac_meas_chip[config]['DAC'], y=np.array(dac_meas_chip[config]['data'])*AD_LSB) # y here is in mV
                dac_meas_chip[config]['GAIN'] = np.round(GAIN,4)
                dac_meas_chip[config]['unit_of_gain'] = 'mV/bit' # mV / DAC bit
                dac_meas_chip[config]['INL'] = np.round(INL,4)*100
            oneChipData = {
                #"logs" : logs,
                "BL": BL[FE_ID],
                "VBGR_Temp": vbgr_temp[FE_ID],
                "DAC_meas": dac_meas_chip
            }

            dumpJson(output_path=self.FE_outputDIRs[FE_ID], output_name='QC_FE_MON', data_to_dump=oneChipData, indent=4)
        return FE_IDs

class QC_FE_MON_Ana():
    def __init__(self, root_path: str, output_path: str, chipID=''):
        self.item = 'FE_MON'
        print (self.item)
        self.tms = '03'
        self.chipID = chipID
        self.root_path = root_path
        self.output_path = output_path

    def _FileExist(self, chipdir: str):
        chipDirExist = os.path.isdir(chipdir)
        qcMondirExist = os.path.isdir('/'.join([chipdir, 'QC_MON']))
        feMonFileExist = os.path.isfile('/'.join([chipdir, 'QC_MON/FE_MON.json']))
        return chipDirExist and qcMondirExist and feMonFileExist
    
    def getItems(self):
        path_to_chipID = '/'.join([self.output_path, self.chipID])
        #if not self._FileExist(chipdir=path_to_chipID):
        #    return None
        try:
            path_to_file = '/'.join([path_to_chipID, 'QC_FE_MON.json'])
            data = json.load(open(path_to_file))
        except: 
            print('Error: QC_FE_MON.json not exist for chip = {}'.format(self.chipID))
            return None
        #logs = data['logs']
        BL_dict = data['BL']
        BL_dict['CH'] = [ich for ich in range(16)]
        BL_df = pd.DataFrame(BL_dict)

        DAC_meas_dict = data['DAC_meas']
        DAC_meas_df = pd.DataFrame()
        configs = [c for c in DAC_meas_dict.keys()]
        #GAIN_INL_DNL_RANGE = {'CFG': [], 'gain (mV/ADC bit)': [], 'INL (%)': [], 'DNL (%)': [], 'Range (0-X)':[]}
        GAIN_INL_DNL_RANGE = {'CFG': [], 'gain (mV/ADC bit)': [], 'INL (%)': [],  'Range (0-X)':[]}
        for icfg, cfg in enumerate(configs):
            tmp_df = {}
            # print(DAC_meas_dict[cfg])
            keys = [c for c in DAC_meas_dict[cfg].keys() if (c=='DAC') | (c=='data')]
            # print(keys)
            for key in keys:
                tmp_df[key] = DAC_meas_dict[cfg][key]
            tmp_df['CFG'] = [cfg for _ in range(len(tmp_df[keys[0]]))]
            tmp_df = pd.DataFrame(tmp_df)
            # print(tmp_df)
            if icfg==0:
                DAC_meas_df = tmp_df
            else:
                DAC_meas_df = pd.concat([DAC_meas_df, tmp_df], axis=0)
            DAC_list = tmp_df['DAC'] # DAC bit
            data_list = tmp_df['data'] # in mV
            if ("DAC_SGP1" in cfg) or ("DAC_SG0_1_SG1_1" in cfg):
                DAC_list = DAC_list.drop(labels=[62,63])
                data_list = data_list.drop(labels=[62,63])
            AD_LSB = 2564/4096 # 2564 mV / 2^12 ==> mV / ADC bit
            gain, yintercept, worstinl, linRange, worstdnl = gain_inl(y=DAC_list, x=data_list*AD_LSB, item='', returnDNL=True)

            GAIN_INL_DNL_RANGE['CFG'].append(cfg)
            GAIN_INL_DNL_RANGE['gain (mV/ADC bit)'].append(1/gain)
            GAIN_INL_DNL_RANGE['INL (%)'].append(worstinl*100)
            #GAIN_INL_DNL_RANGE['DNL (%)'].append(worstdnl*100)
            GAIN_INL_DNL_RANGE['Range (0-X)'].append(np.max(linRange))
            
        GAIN_INL_DNL_RANGE = pd.DataFrame(GAIN_INL_DNL_RANGE)
        
        VBGR_Temp_dict = data['VBGR_Temp']
        return {'BL': BL_df, 'VBGR_Temp': VBGR_Temp_dict, 'DAC_meas': GAIN_INL_DNL_RANGE}

    def run_Ana(self):
        """
        Analyze test data and optionally compare with statistical thresholds.
        
        Args:
            path_to_statAna (str, optional): Path to CSV file with statistical thresholds.
                                        If None, only raw data analysis is performed.
        """
        items = self.getItems()
        if items==None:
            return None

        # BL analysis
        BL_data = items['BL']
        baselines = ['200mV', '900mV']

        BL_data['CH'] = BL_data['CH'].apply(lambda x: 'CH{}'.format(x))

        # VBGR_Temp analysis
        VBGR_Temp_data = items['VBGR_Temp']
        VBGR_Temp_data_df = pd.DataFrame([VBGR_Temp_data])
        
        combined_vbgr_temp = VBGR_Temp_data_df

        # DAC_meas analysis
        DAC_meas_data = items['DAC_meas'].copy()
        merged_DAC_meas = DAC_meas_data

        ## Transform dataframes to data tables
        ## Baselines
        BL_tables = []
        for BL in baselines:
            cols = [c for c in BL_data.columns if (c=='CH') | (BL in c)]
            oneBL = list(BL_data['CH'].astype(str).str.cat(BL_data[BL].astype(str), sep='='))
            BL_tables.append(['Test_{}_{}'.format(self.tms,self.item), 'BL_{}'.format(BL)] + oneBL)
        
        # VBGR_Temp
        vbgr_temp_tables = []
        cols = ['VBGR', 'MON_Temper', 'MON_VBGR']
        for col in cols:
            combined_vbgr_temp[col] = combined_vbgr_temp[col].apply(lambda x: '{}={}'.format(col, x))
            tmp_result = ['Test_{}_{}'.format(self.tms, self.item), 'VBGR_Temp', combined_vbgr_temp.iloc[0][col]]
            vbgr_temp_tables.append(tmp_result)
        
        # DAC_meas
        DAC_meas_table = []
        configurations = merged_DAC_meas['CFG'].unique()
        for cfg in configurations:
            onecfg_data = merged_DAC_meas[merged_DAC_meas['CFG']==cfg].copy()
            features = [cc for cc in onecfg_data.columns if cc!='CFG']
            tmp_result = ['Test_{}_{}'.format(self.tms, self.item), cfg]
                
            for feature in features:
                tmp_result.append('{}={}'.format(feature, onecfg_data.iloc[0][feature]))
            DAC_meas_table.append(tmp_result)

        output_table = BL_tables + vbgr_temp_tables + DAC_meas_table
        return output_table


if __name__ == '__main__':
    root_path = "E:/B009T0008/"
    output_path = root_path + "Ana"
    data_dir = "Time_20250527114445_DUT_0000_1001_2002_3003_4004_5005_6006_7007"
    env = 'RT'
    fe_Mon = FE_MON(root_path=root_path, data_dir=data_dir, output_path=output_path, env=env)
    fe_Mon.decodeFE_MON()
