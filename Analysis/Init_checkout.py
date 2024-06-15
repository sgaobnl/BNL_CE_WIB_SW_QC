############################################################################################
#   created on 5/3/2024 @ 15:38
#   email: radofanantenan.razakamiandra@stonybrook.edu
#   Analyze the data in QC_INIT_CHK.bin
############################################################################################
import os, sys
import numpy as np
import pickle, json
from utils import printItem
from utils import decodeRawData, LArASIC_ana, createDirs, dumpJson
import matplotlib.pyplot as plt

class QC_INIT_CHECK:
    '''
        Data file: 
            QC_INIT_CHK.bin
        Items to check:
            WIB_PWR, WIB_LINK, FE_PWRON, ADC_PWRON, CD_PWRON, ASICDAC_CALI_CHK, DIRECT_PLS_CHK, logs
        output:
            self.out_dict = {'FE_ID0': {
                                    param0: {
                                        'pedestal' : {'data': [], 'result_qc': [], 'link_to_img': ''},
                                        'rms': {'data': [], 'result_qc': [], 'link_to_img': ''},
                                        'pulseResponse': {'pospeak': {}, 'negpeak': {}, 'link_to_img': ''}
                                    },
                                    param1 : { same as param0 },
                                    param2 : { TO BE DEFINED }
                                    .... TO BE DEFINED
                                  },
                        'FE_ID1': { same as FE_ID0 },
                        ...
                        }
    '''
    def __init__(self, root_path: str, data_dir: str, output_dir: str):
        self.tms = 0
        self.item_to_analyze = "Initialization checkout"
        printItem(self.item_to_analyze)
        self.init_chk_filename = 'QC_INIT_CHK.bin'
        # self.root_path = root_path
        # self.data_dir = data_dir
        self.items_to_check = ['WIB_PWR', 'WIB_LINK', 'FE_PWRON', 'ADC_PWRON', 'ASICDAC_CALI_CHK', 'DIRECT_PLS_CHK', 'logs']
        # load data to a dictionary
        with open('/'.join([root_path, data_dir, self.init_chk_filename]), 'rb') as fn:
            self.raw_data = pickle.load(fn)
        ## get the logs
        self.logs_dict = self.raw_data['logs']
        ##----- Create Folders for the outputs -----
        createDirs(logs_dict=self.logs_dict, output_dir=output_dir)
        FE_outputDIRs = ['/'.join([output_dir, self.logs_dict['FE{}'.format(ichip)]]) for ichip in range(8)]
        self.INIT_CHECK_dirs = ['/'.join([DIR, 'INIT_CHECK']) for DIR in FE_outputDIRs]
        for d in self.INIT_CHECK_dirs:
            try:
                os.mkdir(d)
            except OSError:
                pass
        ## --- OUTPUT DICTIONARY
        self.out_dict = dict()
        for ichip in range(8):
            FE_ID = self.logs_dict['FE{}'.format(ichip)]
            self.out_dict[FE_ID] = {
                "logs":{
                    "date": self.logs_dict['date'],
                    "testsite": self.logs_dict['testsite'],
                    "env": self.logs_dict['env'],
                    "note": self.logs_dict['note'],
                    "DAT_SN": self.logs_dict['DAT_SN'],
                    "WIB_slot": self.logs_dict['DAT_on_WIB_slot']
                }
            }
            for param in self.items_to_check:
                if param!='logs':
                    self.out_dict[FE_ID][param] = dict()

    def WIB_PWR(self):
        pass

    def WIB_LINK(self):
        link_mask = self.raw_data['WIB_LINK']
        return link_mask

    def FE_PWRON(self, range_V=[1.8, 1.82], generateQCresult=True):
        # printItem(item="FE_PWRON")
        print("Item: FE_PWRON")
        FE_PWRON_data = self.raw_data['FE_PWRON']
        voltage_params = ['VDDA', 'VDDO', 'VDDP']
        # organize the data
        out_dict = {self.logs_dict['FE{}'.format(ichip)]:{} for ichip in range(8)}
        for ichip in range(8):
            VDDA_V = np.round(FE_PWRON_data['FE{}_VDDA'.format(ichip)][0], 4)
            VDDA_I = np.round(FE_PWRON_data['FE{}_VDDA'.format(ichip)][1], 4)
            VDDA_P = np.round(FE_PWRON_data['FE{}_VDDA'.format(ichip)] [2], 4)
            VDDO_V = np.round(FE_PWRON_data['FE{}_VDDO'.format(ichip)][0], 4)
            VDDO_I = np.round(FE_PWRON_data['FE{}_VDDO'.format(ichip)][1], 4)
            VDDO_P = np.round(FE_PWRON_data['FE{}_VDDO'.format(ichip)] [2], 4)
            VDDP_V = np.round(FE_PWRON_data['FE{}_VPPP'.format(ichip)][0], 4)
            VDDP_I = np.round(FE_PWRON_data['FE{}_VPPP'.format(ichip)][1], 4)
            VDDP_P = np.round(FE_PWRON_data['FE{}_VPPP'.format(ichip)] [2], 4)
            qc_Voltage = [True, True, True]
            if generateQCresult:
                if (VDDA_V>=range_V[0]) & (VDDA_V<range_V[1]):
                    qc_Voltage[0] = True
                else:
                    qc_Voltage[0] = False
                if (VDDO_V>=range_V[0]) & (VDDO_V<range_V[1]):
                    qc_Voltage[1] = True
                else:
                    qc_Voltage[1] = False
                if (VDDP_V>=range_V[0]) & (VDDP_V<range_V[1]):
                    qc_Voltage[2] = True
                else:
                    qc_Voltage[2] = False
                Vpassed = True
                if False in qc_Voltage:
                    Vpassed = False

            oneChip_data =  {
                                'V' : {"data": {'VDDA': VDDA_V, 'VDDO': VDDO_V, 'VDDP': VDDP_V}, "unit": "V"},
                                'I': {"data" : {'VDDA': VDDA_I, 'VDDO': VDDO_I, 'VDDP': VDDP_I}, "unit": "mA"},
                                'P': {"data": {'VDDA': VDDA_P, 'VDDO': VDDO_P, 'VDDP': VDDP_P}, "unit": "mW"},
                            }
            if generateQCresult:
                oneChip_data['V']['result_qc'] = [Vpassed]
                oneChip_data['I']['result_qc'] = []
                oneChip_data['P']['result_qc'] = []
            out_dict[self.logs_dict['FE{}'.format(ichip)]] = oneChip_data
        return {'FE_PWRON': out_dict}

    def ADC_PWRON(self):
        pass

    def QC_CHK(self, range_peds=[300,3000], range_rms=[5,25], range_pulseAmp=[7000,10000], isPosPeak=True, param='ASICDAC_CALI_CHK', generateQCresult=False, generatePlots=False):
        # printItem(item=param)
        print("Item : {}".format(param))
        fembs = self.raw_data[param][0]
        rawdata = self.raw_data[param][1]
        wibdata = decodeRawData(fembs=fembs, rawdata=rawdata)
        # out_list = []
        out_dict = dict()
        for ichip in range(8):
            chipID = self.logs_dict['FE{}'.format(ichip)]
            output_FE = self.INIT_CHECK_dirs[ichip]
            asic = LArASIC_ana(dataASIC=wibdata[ichip], output_dir=output_FE, chipID=chipID, param=param, tms=self.tms, generateQCresult=generateQCresult, generatePlots=generatePlots)
            data_asic = asic.runAnalysis(range_peds=range_peds, range_rms=range_rms, range_pulseAmp=range_pulseAmp, isPosPeak=isPosPeak)
            out_dict[chipID] = data_asic
        return {param: out_dict}
    
    def decode_INIT_CHK(self, in_params={}, generateQCresult=False, generatePlots=False):
        '''
        input: in_params = {param0: {'pedestal': [], 'rms': [], 'pulseAmp': []},
                            param1: {'pedestal': [], 'rms': [], 'pulseAmp': []},
                            'isPosPeak': True/False
                            }
        '''
        params = ['ASICDAC_CALI_CHK', 'DIRECT_PLS_CHK', 'FE_PWRON']
        range_peds, range_rms, range_pulseAmp, range_V = [], [], [], []
        for param in params:
            if param=="FE_PWRON":
                if generateQCresult:
                    range_V = in_params[param]['V']
                FE_pwr_dict = self.FE_PWRON(range_V=range_V, generateQCresult=generateQCresult)
                for ichip in range(8):
                    FE_ID = self.logs_dict['FE{}'.format(ichip)]
                    self.out_dict[FE_ID][param] = FE_pwr_dict[param][FE_ID]
            elif (param=='ASICDAC_CALI_CHK') or (param=='DIRECT_PLS_CHK'):
                if generateQCresult:
                    range_peds = in_params[param]['pedestal']
                    range_rms = in_params[param]['rms']
                    range_pulseAmp = in_params[param]['pulseAmp']
                data_asic_forparam = self.QC_CHK(range_peds=range_peds, range_rms=range_rms, range_pulseAmp=range_pulseAmp, param=param, generateQCresult=generateQCresult, generatePlots=generatePlots)
                for ichip in range(8):
                    FE_ID = self.logs_dict['FE{}'.format(ichip)]
                    self.out_dict[FE_ID][param]["CFG_info"] = [] # to be added by Shanshan or Me later
                    self.out_dict[FE_ID][param]['pedestal'] = data_asic_forparam[param][FE_ID]['pedrms']['pedestal']['data']
                    self.out_dict[FE_ID][param]['rms'] = data_asic_forparam[param][FE_ID]['pedrms']['rms']['data']
                    # self.out_dict[FE_ID][param]['pulseResponse'] = data_asic_forparam[param][FE_ID]['pulseResponse']
                    self.out_dict[FE_ID][param]['pospeak'] = data_asic_forparam[param][FE_ID]['pulseResponse']['pospeak']['data']
                    self.out_dict[FE_ID][param]['negpeak'] = data_asic_forparam[param][FE_ID]['pulseResponse']['negpeak']['data']
        
        ## ----- INCLUDE THE ANALYSIS OF OTHER PARAMETERS HERE -----------

        ## --- THIS BLOCK SHOULD BE THE LAST PART OF THE METHOD runAnalysis
        for ichip in range(8):
            FE_ID = self.logs_dict['FE{}'.format(ichip)]
            dumpJson(output_path=self.INIT_CHECK_dirs[ichip], output_name='QC_CHK_INIT', data_to_dump=self.out_dict[FE_ID])

if __name__ == '__main__':
    root_path = '../../Data_BNL_CE_WIB_SW_QC'
    output_path = '../../Analyzed_BNL_CE_WIB_SW_QC'
    # root_path = 'D:/DAT_LArASIC_QC/Tested'

    qc_selection = json.load(open("qc_selection.json"))
    print(qc_selection)
    list_data_dir = [dir for dir in os.listdir(root_path) if '.zip' not in dir]
    for data_dir in list_data_dir:
        init_chk = QC_INIT_CHECK(root_path=root_path, data_dir=data_dir, output_dir=output_path)
        init_chk.decode_INIT_CHK(in_params=qc_selection['QC_INIT_CHK'], generateQCresult=False, generatePlots=True)
