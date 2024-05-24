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
        self.get_logs()
        self.FE_IDs = [self.logs_dict['FE{}'.format(i)] for i in range(8)]
        ##----- Create Folders for the outputs -----
        createDirs(FE_IDs=self.FE_IDs, output_dir=output_dir)
        self.FE_output_DIRs = ['/'.join([output_dir, FE_ID]) for FE_ID in self.FE_IDs]
        ## --- OUTPUT DICTIONARY
        self.out_dict = dict()
        for FE_ID in self.FE_IDs:
            self.out_dict[FE_ID] = dict()
            for param in self.items_to_check:
                if param!='logs':
                    self.out_dict[FE_ID][param] = dict()

    def get_logs(self):
        logs = self.raw_data['logs']
        # FE IDs
        FE_ID_dict = dict()
        for k, elt in logs.items():
            if 'FE' in k:
                FE_ID_dict[k] = elt
        self.logs_dict = {'date': logs['date'], 'env': logs['env'], 'testsite': logs['testsite']}
        for k, fe in FE_ID_dict.items():
            self.logs_dict[k] = fe

    def WIB_PWR(self):
        pass

    def WIB_LINK(self):
        pass

    def FE_PWRON(self):
        pass

    def ADC_PWRON(self):
        pass

    def QC_CHK(self, range_peds=[300,3000], range_rms=[5,25], range_pulseAmp=[7000,10000], isPosPeak=True, param='ASICDAC_CALI_CHK'):
        # param = 'ASICDAC_CALI_CHK'
        fembs = self.raw_data[param][0]
        rawdata = self.raw_data[param][1]
        wibdata = decodeRawData(fembs=fembs, rawdata=rawdata)
        # out_list = []
        out_dict = dict()
        for ichip in range(8):
            chipID = self.FE_IDs[ichip]
            output_FE = self.FE_output_DIRs[ichip]
            asic = LArASIC_ana(dataASIC=wibdata[ichip], output_dir=output_FE, chipID=chipID, param=param)
            data_asic = asic.runAnalysis(range_peds=range_peds, range_rms=range_rms, range_pulseAmp=range_pulseAmp, isPosPeak=isPosPeak)
            # out_list.append(data_asic)
            out_dict[chipID] = data_asic
        # return {param: out_list}
        return {param: out_dict}

    def DIRECT_PLS_CHK(self, range_peds=[300,3000], range_rms=[5,25], range_pulseAmp=[9000,16000], isPosPeak=True):
        param = 'DIRECT_PLS_CHK'
        fembs = self.raw_data[param][0]
        rawdata = self.raw_data[param][1]
        wibdata = decodeRawData(fembs=fembs, rawdata=rawdata)
        self.direct_pls_chk_list = []
        for ichip in range(8):
            # ichip = 0 # will be used in a loop
            # output_dir = '/'.join([self.output_dir, self.logs_dict['FE{}'.format(ichip)]])
            chipID = self.FE_IDs[ichip]
            output_dir = self.FE_output_DIRs[ichip]
            asic = LArASIC_ana(dataASIC=wibdata[ichip], output_dir=output_dir, chipID=chipID, param=param)
            data_asic = asic.runAnalysis(range_peds=range_peds, range_rms=range_rms, range_pulseAmp=range_pulseAmp, isPosPeak=isPosPeak)
            self.direct_pls_chk_list.append(data_asic)
    
    def runAnalysis(self, in_params={}):
        '''
        input: in_params = {param0: {'pedestal': [], 'rms': [], 'pulseAmp': []},
                            param1: {'pedestal': [], 'rms': [], 'pulseAmp': []},
                            'isPosPeak': True/False
                            }
        '''
        params = ['ASICDAC_CALI_CHK', 'DIRECT_PLS_CHK']
        
        for param in params:
            range_peds = in_params[param]['pedestal']
            range_rms = in_params[param]['rms']
            range_pulseAmp = in_params[param]['pulseAmp']
            data_asic_forparam = self.QC_CHK(range_peds=range_peds, range_rms=range_rms, range_pulseAmp=range_pulseAmp, isPosPeak=in_params['isPosPeak'], param=param)
            for FE_ID in self.FE_IDs:
                self.out_dict[FE_ID][param]['pedestal'] = data_asic_forparam[param][FE_ID]['pedrms']['pedestal']
                self.out_dict[FE_ID][param]['rms'] = data_asic_forparam[param][FE_ID]['pedrms']['rms']
                self.out_dict[FE_ID][param]['pulseResponse'] = data_asic_forparam[param][FE_ID]['pulseResponse']
        
        ## ----- INCLUDE THE ANALYSIS OF OTHER PARAMETERS HERE -----------

        ## --- THIS BLOCK SHOULD BE THE LAST PART OF THE METHOD runAnalysis
        for i in range(8):
            dumpJson(output_path=self.FE_output_DIRs[i], output_name='QC_CHK_INIT', data_to_dump=self.out_dict[self.FE_IDs[i]])

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
