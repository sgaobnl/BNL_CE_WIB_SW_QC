############################################################################################
#   created on 5/3/2024 @ 15:38
#   email: radofanantenan.razakamiandra@stonybrook.edu
#   Analyze the data in QC_INIT_CHK.bin
############################################################################################
import os, sys
import numpy as np
import pickle, json
from datetime import datetime
from utils import printItem
from utils import decodeRawData, LArASIC_ana, createDirs, dumpJson, BaseClass
import matplotlib.pyplot as plt

class QC_INIT_CHECK(BaseClass):
    def __init__(self, root_path: str, data_dir: str, output_dir: str):
        printItem('Initialization checkout')
        super().__init__(root_path=root_path, data_dir=data_dir, output_path=output_dir, tms=0, QC_filename='QC_INIT_CHK.bin')
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
            for param in self.params:
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
        period = 500
        if 'ASICDAC' in param:
            period = 500
        elif 'DIRECT' in param:
            period = 512
        print("Item : {}".format(param))
        fembs = self.raw_data[param][0]
        rawdata = self.raw_data[param][1]
        wibdata = decodeRawData(fembs=fembs, rawdata=rawdata, period=period)
        # out_list = []
        out_dict = dict()
        for ichip in range(8):
            chipID = self.logs_dict['FE{}'.format(ichip)]
            output_FE = self.FE_outputDIRs[chipID]
            asic = LArASIC_ana(dataASIC=wibdata[ichip], output_dir=output_FE, chipID=chipID, param=param, tms=self.tms, generateQCresult=generateQCresult, generatePlots=generatePlots, period=period)
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
        range_peds, range_rms, range_pulseAmp, range_V = [], [], [], []
        for param in self.params:
            if param=="FE_PWRON":
                if generateQCresult:
                    range_V = in_params[param]['V']
                FE_pwr_dict = self.FE_PWRON(range_V=range_V, generateQCresult=generateQCresult)
                for ichip in range(8):
                    FE_ID = self.logs_dict['FE{}'.format(ichip)]
                    self.out_dict[FE_ID][param] = FE_pwr_dict[param][FE_ID]
            # elif (param=='ASICDAC_CALI_CHK') or (param=='DIRECT_PLS_CHK'):
            elif ('ASIC' in param) or ('DIRECT' in param):
            # elif param=='DIRECT_PLS_CHK':
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
                    self.out_dict[FE_ID][param]['pospeak'] = data_asic_forparam[param][FE_ID]['pulseResponse']['pospeak']['data']
                    self.out_dict[FE_ID][param]['negpeak'] = data_asic_forparam[param][FE_ID]['pulseResponse']['negpeak']['data']

        ## --- THIS BLOCK SHOULD BE THE LAST PART OF THE METHOD runAnalysis
        for ichip in range(8):
            FE_ID = self.logs_dict['FE{}'.format(ichip)]
            dumpJson(output_path=self.FE_outputDIRs[FE_ID], output_name='QC_CHK_INIT', data_to_dump=self.out_dict[FE_ID])


if __name__ == '__main__':
    # root_path = '../../Data_BNL_CE_WIB_SW_QC'
    # root_path = '../../B010T0004/Time_20240703122319_DUT_0000_1001_2002_3003_4004_5005_6006_7007'
    root_path = '../../B010T0004'
    output_path = '../../Analyzed_BNL_CE_WIB_SW_QC'
    # root_path = 'D:/DAT_LArASIC_QC/Tested'

    qc_selection = json.load(open("qc_selection.json"))
    # print(qc_selection)

    list_data_dir = [dir for dir in os.listdir(root_path) if (os.path.isdir('/'.join([root_path, dir]))) and (dir!='images')] ### USE THIS LINE FOR OTHER TEST ITEMS AS WELL
    for i, data_dir in enumerate(list_data_dir):
        printItem(data_dir)
        #----------------------------
        t0 = datetime.now()
        init_chk = QC_INIT_CHECK(root_path=root_path, data_dir=data_dir, output_dir=output_path)
        init_chk.decode_INIT_CHK(in_params=qc_selection['QC_INIT_CHK'], generateQCresult=False, generatePlots=True)
        #----------------------------
        tf = datetime.now()
        print('end time : {}'.format(tf))
        deltaT = (tf - t0).total_seconds()
        print("Decoding time : {} seconds".format(deltaT))
        print("=xx="*20)
