############################################################################################
#   created on 5/3/2024 @ 15:38
#   emails: radofanantenan.razakamiandra@stonybrook.edu
#   Analyze the data in QC_INIT_CHK.bin
############################################################################################
import os, sys
import pickle, json
from utils import printItem
from utils import decodeRawData, LArASIC_ana, createDirs, dumpJson

class ANALYSIS:
    '''
    One run on the DUNE ASIC Test board ---> 8 LArASICs
    '''
    def __init__(self, root_path: str, data_dir: str, main_output_dir: str):
        self.main_output_dir = main_output_dir
        self.input_dir = '/'.join([root_path, data_dir])
        self.logs = self.get_logs()
        self.FE_IDs = [self.logs['FE{}'.format(i)] for i in range(8)]
        ##----- Create Folders for the outputs -----
        createDirs(FE_IDs=self.FE_IDs, output_dir=main_output_dir)
        self.FE_output_DIRs = ['/'.join([self.main_output_dir, FE_ID]) for FE_ID in self.FE_IDs]
        ##------
        self.ItemsFilename_dict = {
                                        0: 'QC_INIT_CHK.bin',
                                        1: 'QC_PWR.bin',
                                        2: 'QC_CHKRES.bin',
                                        3: 'QC_MON.bin',
                                        4: 'QC_PWR_CYCLE.bin',
                                        5: 'QC_RMS.bin',
                                        61: 'QC_CALI_ASICDAC.bin',
                                        62: 'QC_CALI_DATDAC.bin',
                                        63: 'QC_CALI_DIRECT.bin',
                                        7: 'QC_DLY_RUN.bin',
                                        8: 'QC_Cap_Meas.bin'
                                }
        self.testItems_dict = {
                                0: "Initialization checkout",
                                 1: "FE power consumption measurement",
                                 2: "FE response measurement checkout",
                                 3: "FE monitoring measurement",
                                 4: "FE power cycling measurement",
                                 5: "FE noise measurement",
                                 61: "FE calibration measurement (ASIC-DAC)",
                                 62: "FE calibration measurement (DAT-DAC)",
                                 63: "FE calibration measurement (Direct-Input)",
                                 7: "FE delay run",
                                 8: "FE cali-cap measurement"
                                }
    
    def get_logs(self):
        with open('/'.join([self.input_dir, 'QC_INIT_CHK.bin']), 'rb') as fn:
            logs = pickle.load(fn)['logs']
        return logs
    
    def INIT_CHK(self):
        tms = 0
        pass

    def PWR(self):
        tms = 1
        pass

    def CHKRES(self):
        tms = 2
        pass

    def MON(self):
        tms = 3
        pass

    def PWR_CYCLE(self):
        tms = 4
        pass

    def RMS(self):
        tms = 5
        pass

    def CALI_ASICDAC(self):
        tms = 61
        pass

    def CALI_DATDAC(self):
        tms = 62
        pass

    def CALI_DIRECT(self):
        tms = 63
        pass

    def DELAY_RUN(self):
        tms = 7
        pass

    def CALI_CAP(self):
        tms = 8
        pass

class INIT_CHECK:
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
        self.root_path = root_path
        self.data_dir = data_dir
        self.items_to_check = ['WIB_PWR', 'WIB_LINK', 'FE_PWRON', 'ADC_PWRON', 'ASICDAC_CALI_CHK', 'DIRECT_PLS_CHK', 'logs']
        # load data to a dictionary
        with open('/'.join([self.root_path, self.data_dir, self.init_chk_filename]), 'rb') as fn:
            self.raw_data = pickle.load(fn)
        ## get the logs
        self.logs_dict = self.raw_data['logs']
        ##----- Create Folders for the outputs -----
        createDirs(logs_dict=self.logs_dict, output_dir=output_dir)
        self.FE_output_DIRs = ['/'.join([output_dir, self.logs_dict['FE{}'.format(ichip)]]) for ichip in range(8)]
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
        pass

    def FE_PWRON(self, range_V=[1.8, 1.82]):
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
                        'V': [VDDA_V, VDDO_V, VDDP_V],
                        'I': [VDDA_I, VDDO_I, VDDP_I],
                        'P': [VDDA_P, VDDO_P, VDDP_P],
                        'units': ['V', 'mA', 'mW']
                    },
                    'chipID_1': {....},
                    ...
                }
            }
            Note: FE{}_VPPP in the code refers to VDDP
        '''
        printItem(item="FE_PWRON")
        FE_PWRON_data = self.raw_data['FE_PWRON']
        voltage_params = ['VDDA', 'VDDO', 'VDDP']
        # organize the data
        out_dict = {self.logs_dict['FE{}'.format(ichip)]:{} for ichip in range(8)}
        for ichip in range(8):
            VDDA_V = FE_PWRON_data['FE{}_VDDA'.format(ichip)][0]
            VDDA_I = FE_PWRON_data['FE{}_VDDA'.format(ichip)][1]
            VDDA_P = FE_PWRON_data['FE{}_VDDA'.format(ichip)] [2]
            VDDO_V = FE_PWRON_data['FE{}_VDDO'.format(ichip)][0]
            VDDO_I = FE_PWRON_data['FE{}_VDDO'.format(ichip)][1]
            VDDO_P = FE_PWRON_data['FE{}_VDDO'.format(ichip)] [2]
            VDDP_V = FE_PWRON_data['FE{}_VPPP'.format(ichip)][0]
            VDDP_I = FE_PWRON_data['FE{}_VPPP'.format(ichip)][1]
            VDDP_P = FE_PWRON_data['FE{}_VPPP'.format(ichip)] [2]
            qc_Voltage = [True, True, True]
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
            oneChip_data =  {
                                'V' : {"data": [VDDA_V, VDDO_V, VDDP_V], "result_qc": qc_Voltage},
                                'I': [VDDA_I, VDDO_I, VDDP_I],
                                'P': [VDDA_P, VDDO_P, VDDP_P],
                                'units': ['V', 'mA', 'mW']
                            }
            out_dict[self.logs_dict['FE{}'.format(ichip)]] = oneChip_data
        return {'FE_PWRON': out_dict}

    def ADC_PWRON(self):
        pass

    def QC_CHK(self, range_peds=[300,3000], range_rms=[5,25], range_pulseAmp=[7000,10000], isPosPeak=True, param='ASICDAC_CALI_CHK'):
        printItem(item=param)
        fembs = self.raw_data[param][0]
        rawdata = self.raw_data[param][1]
        wibdata = decodeRawData(fembs=fembs, rawdata=rawdata)
        # out_list = []
        out_dict = dict()
        for ichip in range(8):
            chipID = self.logs_dict['FE{}'.format(ichip)]
            output_FE = self.FE_output_DIRs[ichip]
            asic = LArASIC_ana(dataASIC=wibdata[ichip], output_dir=output_FE, chipID=chipID, param=param)
            data_asic = asic.runAnalysis(range_peds=range_peds, range_rms=range_rms, range_pulseAmp=range_pulseAmp, isPosPeak=isPosPeak)
            out_dict[chipID] = data_asic
        return {param: out_dict}
    
    def runAnalysis(self, in_params={}):
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
                FE_pwr_dict = self.FE_PWRON(range_V=range_V)
                for ichip in range(8):
                    FE_ID = self.logs_dict['FE{}'.format(ichip)]
                    self.out_dict[FE_ID][param] = FE_pwr_dict[param][FE_ID]
            elif (param=='ASICDAC_CALI_CHK') or (param=='DIRECT_PLS_CHK'):
                range_peds = in_params[param]['pedestal']
                range_rms = in_params[param]['rms']
                range_pulseAmp = in_params[param]['pulseAmp']
                data_asic_forparam = self.QC_CHK(range_peds=range_peds, range_rms=range_rms, range_pulseAmp=range_pulseAmp, isPosPeak=in_params['isPosPeak'], param=param)
                for ichip in range(8):
                    FE_ID = self.logs_dict['FE{}'.format(ichip)]
                    self.out_dict[FE_ID][param]['pedestal'] = data_asic_forparam[param][FE_ID]['pedrms']['pedestal']
                    self.out_dict[FE_ID][param]['rms'] = data_asic_forparam[param][FE_ID]['pedrms']['rms']
                    self.out_dict[FE_ID][param]['pulseResponse'] = data_asic_forparam[param][FE_ID]['pulseResponse']
        
        ## ----- INCLUDE THE ANALYSIS OF OTHER PARAMETERS HERE -----------

        ## --- THIS BLOCK SHOULD BE THE LAST PART OF THE METHOD runAnalysis
        for ichip in range(8):
            FE_ID = self.logs_dict['FE{}'.format(ichip)]
            dumpJson(output_path=self.FE_output_DIRs[ichip], output_name='QC_CHK_INIT', data_to_dump=self.out_dict[FE_ID])

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
        init_chk = INIT_CHECK(root_path=root_path, data_dir=data_dir, output_dir=output_path)
        init_chk.runAnalysis(in_params=qc_selection['QC_INIT_CHK'])
        sys.exit()