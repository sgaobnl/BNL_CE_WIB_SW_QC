############################################################################################
#   created on 5/3/2024 @ 15:38
#   emails: radofanantenan.razakamiandra@stonybrook.edu
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
            self.out_dict[FE_ID] = dict()
            for param in self.items_to_check:
                if param!='logs':
                    self.out_dict[FE_ID][param] = dict()

    def WIB_PWR(self):
        pass

    def WIB_LINK(self):
        link_mask = self.raw_data['WIB_LINK']
        return link_mask

    def FE_PWRON(self, range_V=[1.8, 1.82], generateQCresult=True):
        '''
            Voltages: VDDA, VDDO, and VDDP
            raw data format:
            {
                'FE0_VDDA': [voltage(V), current(mA), power(mW)],
                'FE0_VDDO': [voltage(V), current(mA), power(mW)],
                'FE0_VDDP': [voltage(V), current(mA), power(mW)],
                'FE1_VDDA': [V, I, P],
                'FE1_VDDO': [V, I, P],
                'FE1_VDDP': [V, I, P],
                ...
            }
            output data format:
            {
                'FE_PWRON': {
                    'chipID_0': {
                        'V': {'data': [VDDA_V, VDDO_V, VDDP_V], 'result_qc': []},
                        'I': {'data': [VDDA_I, VDDO_I, VDDP_I], 'result_qc': []},
                        'P': {'data': [VDDA_P, VDDO_P, VDDP_P], 'result_qc': []},
                        'units': ['V', 'mA', 'mW']
                    },
                    'chipID_1': {....},
                    ...
                }
            }
            Note: FE{}_VPPP in the code refers to VDDP
            - If generateQCresult==True: the "result_qc" is saved in the output data
        '''
        printItem(item="FE_PWRON")
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
            # oneChip_data =  {
            #                     'V' : {"data": [VDDA_V, VDDO_V, VDDP_V], "result_qc": [Vpassed]},
            #                     'I': {"data" : [VDDA_I, VDDO_I, VDDP_I], "result_qc": []},
            #                     'P': {"data": [VDDA_P, VDDO_P, VDDP_P], "result_qc" : []},
            #                     'units': ['V', 'mA', 'mW']
            #                 }
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

    def QC_CHK(self, range_peds=[300,3000], range_rms=[5,25], range_pulseAmp=[7000,10000], isPosPeak=True, param='ASICDAC_CALI_CHK', generateQCresult=False):
        printItem(item=param)
        fembs = self.raw_data[param][0]
        rawdata = self.raw_data[param][1]
        wibdata = decodeRawData(fembs=fembs, rawdata=rawdata)
        # out_list = []
        out_dict = dict()
        for ichip in range(8):
            chipID = self.logs_dict['FE{}'.format(ichip)]
            output_FE = self.INIT_CHECK_dirs[ichip]
            asic = LArASIC_ana(dataASIC=wibdata[ichip], output_dir=output_FE, chipID=chipID, param=param, tms=self.tms, generateQCresult=generateQCresult, generatePlots=False)
            data_asic = asic.runAnalysis(range_peds=range_peds, range_rms=range_rms, range_pulseAmp=range_pulseAmp, isPosPeak=isPosPeak)
            out_dict[chipID] = data_asic
        return {param: out_dict}
    
    def runAnalysis(self, in_params={}, generateQCresult=False):
        '''
        input: in_params = {param0: {'pedestal': [], 'rms': [], 'pulseAmp': []},
                            param1: {'pedestal': [], 'rms': [], 'pulseAmp': []},
                            'isPosPeak': True/False
                            }
        '''
        params = ['ASICDAC_CALI_CHK', 'DIRECT_PLS_CHK', 'FE_PWRON']
        
        for param in params:
            if param=="FE_PWRON":
                range_V = in_params[param]['V']
                FE_pwr_dict = self.FE_PWRON(range_V=range_V, generateQCresult=generateQCresult)
                for ichip in range(8):
                    FE_ID = self.logs_dict['FE{}'.format(ichip)]
                    self.out_dict[FE_ID][param] = FE_pwr_dict[param][FE_ID]
            elif (param=='ASICDAC_CALI_CHK') or (param=='DIRECT_PLS_CHK'):
                range_peds = in_params[param]['pedestal']
                range_rms = in_params[param]['rms']
                range_pulseAmp = in_params[param]['pulseAmp']
                data_asic_forparam = self.QC_CHK(range_peds=range_peds, range_rms=range_rms, range_pulseAmp=range_pulseAmp, isPosPeak=in_params['isPosPeak'], param=param, generateQCresult=generateQCresult)
                for ichip in range(8):
                    FE_ID = self.logs_dict['FE{}'.format(ichip)]
                    self.out_dict[FE_ID][param]["CFG_info"] = [] # to be added by Shanshan or Me later
                    self.out_dict[FE_ID][param]['pedestal'] = data_asic_forparam[param][FE_ID]['pedrms']['pedestal']
                    self.out_dict[FE_ID][param]['rms'] = data_asic_forparam[param][FE_ID]['pedrms']['rms']
                    self.out_dict[FE_ID][param]['pulseResponse'] = data_asic_forparam[param][FE_ID]['pulseResponse']
        
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
    list_data_dir = os.listdir(root_path)
    for data_dir in list_data_dir:
        # data_dir = 'FE_004003138_004003139_004003140_004003145_004003157_004003146_004003147_004003148'
        # data_dir = 'FE_002006204_002006209_002006210_002006211_002006212_002006217_002006218_002006219'
        init_chk = QC_INIT_CHECK(root_path=root_path, data_dir=data_dir, output_dir=output_path)
        init_chk.runAnalysis(in_params=qc_selection['QC_INIT_CHK'], generateQCresult=False)
