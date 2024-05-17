############################################################################################
#   created on 5/3/2024 @ 15:38
#   emails: radofanantenan.razakamiandra@stonybrook.edu
#   Analyze the data in QC_INIT_CHK.bin
############################################################################################
import os
import pickle
import numpy as np
import matplotlib.pyplot as plt
from utils import printItem, dumpJson
from utils import decodeRawData, getpedestal_rms, getpulse, ASIC_ana

class Init_checkout:
    '''
        Data file: 
            QC_INIT_CHK.bin
        Items to check:
            WIB_PWR, WIB_LINK, FE_PWRON, ADC_PWRON, CD_PWRON, ASICDAC_CALI_CHK, DIRECT_PLS_CHK, logs
    '''
    def __init__(self, root_path: str, data_dir: str, output_dir: str):
        self.item_to_analyze = "Initialization checkout"
        printItem(self.item_to_analyze)
        self.init_chk_filename = 'QC_INIT_CHK.bin'
        self.root_path = root_path
        self.data_dir = data_dir
        self.items_to_check = ['WIB_PWR', 'WIB_LINK', 'FE_PWRON', 'ADC_PWRON', 'ASICDAC_CALI_CHK', 'DIRECT_PLS_CHK', 'logs']
        # load data to a dictionary
        with open('/'.join([self.root_path, self.data_dir, self.init_chk_filename]), 'rb') as fn:
            self.raw_data = pickle.load(fn)
        # try to create output directory
        try:
            os.makedirs(output_dir)
        except OSError:
            print('Unable to create the folder {}.'.format(output_dir))
        newoutput_dir = '/'.join([output_dir, self.data_dir])
        try:
            os.makedirs(newoutput_dir)
        except OSError:
            print('Unable to create the folder {}.'.format(newoutput_dir))
        self.output_dir = '/'.join([newoutput_dir, 'INIT_CHK'])
        try:
            os.makedirs(self.output_dir)
        except OSError:
            print('Unable to create the folder {}.'.format(self.output_dir))
        ## get the logs
        self.get_logs()

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
        # dumpJson(output_path=self.output_dir, output_name='logs', data_to_dump=logs_dict)

    def WIB_PWR(self):
        pass

    def WIB_LINK(self):
        pass

    def FE_PWRON(self):
        pass

    def ADC_PWRON(self):
        pass

    def ASICDAC_CALI_CHK(self):
        fembs = self.raw_data['ASICDAC_CALI_CHK'][0]
        rawdata = self.raw_data['ASICDAC_CALI_CHK'][1]

    def DIRECT_PLS_CHK(self):
        rawdata = self.raw_data['DIRECT_PLS_CHK']
    
    def getData(self, param='ASICDAC_CALI_CHK'):
        fembs = self.raw_data[param][0]
        rawdata = self.raw_data[param][1]
        wibdata = decodeRawData(fembs=fembs, rawdata=rawdata)

        pedestals = np.array([])
        rms = np.array([])
        ppeaks = np.array([])
        for ichip in range(8):
            # ichip = 0 # will be used in a loop
            chipID = self.logs_dict['FE{}'.format(ichip)]
            asic = ASIC_ana(dataASIC=wibdata[7], output_dir=self.output_dir, chipID=chipID)
            [tmp_peds, tmp_rms, tmp_ppeaks] = asic.runAll(defCriteria=True)
            pedestals = np.concatenate([pedestals, np.array(tmp_peds)])
            rms = np.concatenate([rms, np.array(tmp_rms)])
            ppeaks = np.concatenate([ppeaks, np.array(tmp_ppeaks)])

        return [pedestals, rms, ppeaks]

###############################################################################################################
############################ MAKE DISTRIBUTION -- GET STD --> Range of values #################################
def DefineCriteria_initCHK(param='ASICDAC_CALI_CHK', root_path=''):
    list_data_dir = os.listdir(root_path)
    pedestals = np.array([])
    rms = np.array([])
    ppeaks = np.array([])
    for data_dir in list_data_dir:
        init_chk = Init_checkout(root_path=root_path, data_dir=data_dir, output_dir='')
        [tmp_peds, tmp_rms, tmp_ppeaks] = init_chk.getData(param=param)
        pedestals = np.concatenate([pedestals, tmp_peds])
        rms = np.concatenate([rms, tmp_rms])
        ppeaks = np.concatenate([ppeaks, tmp_ppeaks])
    
    print(len(pedestals))
    plt.figure()
    plt.hist(pedestals, bins=50)
    plt.show()

if __name__ == '__main__':
    root_path = '../../Data_BNL_CE_WIB_SW_QC'
    output_path = '../../Analyzed_BNL_CE_WIB_SW_QC'
    DefineCriteria_initCHK(root_path=root_path)
    # list_data_dir = os.listdir(root_path)
    # for data_dir in list_data_dir:
    #     # data_dir = 'FE_004003138_004003139_004003140_004003145_004003157_004003146_004003147_004003148'
    #     init_chk = Init_checkout(root_path=root_path, data_dir=data_dir, output_dir=output_path)
    #     # init_chk.get_logs()
    #     init_chk.ASICDAC_CALI_CHK()
