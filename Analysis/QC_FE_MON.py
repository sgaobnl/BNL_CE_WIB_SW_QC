############################################################################################
#   created on 6/9/2024 @ 17:13
#   emails: radofanantenan.razakamiandra@stonybrook.edu
#   Decode QC_MON.bin
############################################################################################

import os, sys, pickle
from utils import printItem, createDirs, dumpJson

class FE_MON:
    def __init__(self, root_path: str, data_dir: str, output_path: str):
        self.tms = 3
        self.qc_filename = "QC_MON.bin"
        printItem(item="FE monitoring")
        # read raw data
        with open('/'.join([root_path, data_dir, self.qc_filename]), 'rb') as f:
            self.raw_data = pickle.load(f)
        # get parameters (keys in the raw_data)
        self.mon_params = [key for key in self.raw_data.keys() if key!='logs']
        # get logs
        self.logs_dict = self.raw_data['logs']
        createDirs(logs_dict=self.logs_dict, output_dir=output_path)
        self.FE_outputDIRs = ['/'.join([output_path, self.logs_dict['FE{}'.format(ichip)], 'QC_FE_MON']) for ichip in range(8)]
        print(self.mon_params)

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
            tmp_data = self.raw_data[param][unitChoice[unitOutput]]
            for ichip in range(8):
                FE_ID = self.logs_dict['FE{}'.format(ichip)]
                out_dict[FE_ID][param] = tmp_data[ichip]
        return out_dict

    def mon_dac(self):
        params = [param for param in self.mon_params if 'DAC' in param]
        for param in params:
            data = self.raw_data[param]
            for idac in range(64):
                dac_val = data[idac][0]
                chips_data = data[idac][1]
                
                sys.exit()

if __name__ == '__main__':
    root_path = '../../Data_BNL_CE_WIB_SW_QC'
    output_path = '../../Analyzed_BNL_CE_WIB_SW_QC'

    list_data_dir = [dir for dir in os.listdir(root_path) if '.zip' not in dir]
    for data_dir in list_data_dir:
        fe_Mon = FE_MON(root_path=root_path, data_dir=data_dir, output_path=output_path)
        fe_Mon.mon_dac()
        sys.exit()