############################################################################################
#   created on 6/12/2024 @ 11:32
#   email: radofanantenan.razakamiandra@stonybrook.edu
#   Analyze the calibration data: QC_CALI_ASICDAC.bin, QC_CALI_DATDAC.bin, and QC_CALI_DIRECT.bin
############################################################################################

import os, sys, pickle
import numpy as np
from utils import printItem, createDirs, dumpJson, linear_fit, LArASIC_ana, decodeRawData, getpulse
import matplotlib.pyplot as plt

class ASICDAC_CALI:
    '''
        Using the 6-bit DAC embedded on the chip to perform the calibration
    '''
    def __init__(self, raw_data: dict, tms: int):
        self.tms = tms
        self.raw_data = raw_data
        self.logs_dict = self.raw_data['logs']
        self.cali_params = [key for key in self.raw_data.keys() if key!='logs']
        createDirs(logs_dict=self.logs_dict, output_dir=output_path)
        FE_outputDIRs = {self.logs_dict['FE{}'.format(ichip)] :'/'.join([output_path, self.logs_dict['FE{}'.format(ichip)], 'QC_CALI']) for ichip in range(8)}
        for FE_ID, dir in FE_outputDIRs.items():
            try:
                os.mkdir(dir)
            except OSError:
                pass
        self.FE_outputDIRs = {self.logs_dict['FE{}'.format(ichip)] :'/'.join([output_path, self.logs_dict['FE{}'.format(ichip)], 'QC_CALI', 'ASICDAC']) for ichip in range(8)}
        for FE_ID, dir in self.FE_outputDIRs.items():
            try:
                os.mkdir(dir)
            except OSError:
                pass

    def getDAC_values(self):
        params_DAC = dict()
        unique_BL = []
        for p in self.cali_params:
            tmp = p.split('_')
            if tmp[1] not in unique_BL:
                unique_BL.append(tmp[1])
        for SNC in unique_BL:
            params_DAC[SNC] = []
            for param in self.cali_params:
                if SNC in param:
                    dac = int(param.split('ASICDAC')[-1])
                    params_DAC[SNC].append((dac, param))
        return params_DAC
    
    def decode(self, params_DAC: dict):
        '''
            output:
            {
                SNC0: [(dac_val, decodedData_oneBL), (dac_val, decodedData_oneBL), ...],
                SNC1: [(dac_val, decodedData_oneBL), (dac_val, decodedData_oneBL), ...]
            }
        '''
        all_decodedData = dict()
        for BL in params_DAC.keys():
            all_decodedData[BL] = []
            for dac, param in params_DAC[BL]:
                fembs = self.raw_data[param][0]
                raw_data = self.raw_data[param][1]
                decodedData = decodeRawData(fembs=fembs, rawdata=raw_data)
                all_decodedData[BL].append((dac, decodedData))
        return all_decodedData
    
    def getPosPeak(self, decodedData: dict):
        all_ppeaks = dict()
        for BL in decodedData.keys():
            all_ppeaks[BL] = []
            for dac, data in decodedData[BL]:
                for ichip in range(8):
                    FE_ID = self.logs_dict['FE{}'.format(ichip)]
                    larasic = LArASIC_ana(dataASIC=data[ichip], output_dir=self.FE_outputDIRs[FE_ID], chipID=FE_ID, tms=self.tms, param='ASICDAC_{}'.format(BL), generatePlots=False, generateQCresult=False)
                    larasic_data = larasic.runAnalysis(getPulseResponse=True, isRMSNoise=False)['pulseResponse']['pospeak']['data']

    #--------------------------------------------
    def organizeData_wf(self, decodedData: dict):
        '''
            output:
            {
                chipID_i : {
                    "SNC0": {
                        chn: [(dac_val, chn_data), ....],
                        ...
                    },
                    "SNC1": {
                        chn: [(dac_val, chn_data), ....],
                        ...
                    }
                }
            }
        '''
        all_wf = dict()
        for ichip in range(8):
            FE_ID = self.logs_dict['FE{}'.format(ichip)]
            all_wf[FE_ID] = {BL: dict() for BL in decodedData.keys()}
            for BL in decodedData.keys():
                for chn in range(16):
                    all_wf[FE_ID][BL][chn] = []
        for BL in decodedData.keys():
            for dac, data in decodedData[BL]:
                for ichip in range(8):
                    FE_ID = self.logs_dict['FE{}'.format(ichip)]
                    for chn in range(16):
                        all_wf[FE_ID][BL][chn].append((dac, data[ichip][chn]))
        return all_wf

    def plot_waveform(self, all_wf_data: dict, chipID: str, BL: str,  chn: int):
        all_dac_chndata = all_wf_data[chipID][BL][chn]
        plt.figure()
        for dac, chn_data in all_dac_chndata:
            data = getpulse(oneCHdata=chn_data, averaged=True)
            posmax = np.where(data==np.max(data))[0]
            plt.plot(data[posmax[0]-5 : posmax[0]+100], label='DAC {}'.format(dac))
        plt.legend()
        # plt.show()
        plt.savefig('/'.join([self.FE_outputDIRs[chipID], 'Cali_ASICDAC_wf_{}_ch{}.png'.format(BL, chn)]))
        plt.close()
    #--------------------------------------------

    def runTest(self):
        params = self.getDAC_values()
        decodedData = self.decode(params_DAC=params)
        all_wf = self.organizeData_wf(decodedData=decodedData)
        for FE_ID in all_wf.keys():
            for BL in ['SNC0', 'SNC1']:
                for chn in range(16):
                    self.plot_waveform(all_wf_data=all_wf, chipID=FE_ID, BL=BL, chn=chn)

class Calibration:
    def __init__(self, root_path: str, data_dir: str, output_path: str, tms: int):
        self.tms = tms
        self.tms_val = {
            61: ["QC_CALI_ASICDAC.bin", "ASICDAC calibration"],
            62: ["QC_CALI_DATDAC.bin", "DATDAC calibration"],
            63: ["QC_CALI_DIRECT.bin", "DIRECT input calibration"]
        }
        self.filename = self.tms_val[tms][0]
        printItem(item=self.tms_val[tms][1])
        #
        with open('/'.join([root_path, data_dir, self.filename]), 'rb') as fn:
            self.raw_data = pickle.load(fn)
        self.logs_dict = self.raw_data['logs']
        createDirs(logs_dict=self.logs_dict, output_dir=output_path)
        self.FE_outputDIRs = {self.logs_dict['FE{}'.format(ichip)] :'/'.join([output_path, self.logs_dict['FE{}'.format(ichip)], 'QC_CALI']) for ichip in range(8)}
        for FE_ID, dir in self.FE_outputDIRs.items():
            try:
                os.mkdir(dir)
            except OSError:
                pass
        self.suffix_filename = self.filename.split('_')[-1].split('.')[0]
        # get parameters (keys in the raw_data)
        self.cali_params = [key for key in self.raw_data.keys() if key!='logs']
        print(self.cali_params)
        if self.suffix_filename=='ASICDAC':
            self.ASICDAC_cali()
            # asicdac = ASICDAC_CALI(raw_data=self.raw_data, tms=tms)
            # asicdac.runTest()
            # sys.exit()
        elif self.suffix_filename=='DATDAC':
            self.DATDAC_cali()

    def ASICDAC_cali(self):
        '''
            Using the 6-bit DAC embedded on the chip to perfrom the calibration;
            LArASIC gain: 14mV/fC, peak time: 2$\mu$s
        '''
        # get DAC values for both baselines ----
        params_DAC = {}
        unique_BL = []
        for p in self.cali_params:
            tmp = p.split('_')
            if tmp[1] not in unique_BL:
                unique_BL.append(tmp[1])
        for BL in unique_BL:
            params_DAC[BL] = {'DAC': [], 'params': []}
            for p in self.cali_params:
                if BL in p:
                    params_DAC[BL]['params'].append(p)
                    tmp = p.split('ASICDAC')
                    params_DAC[BL]['DAC'].append(int(tmp[-1]))
        # ---------x-x---------
        # DECODE the raw data
        BL_dict = dict()
        for BL in unique_BL: # SNC0 and SNC1
            dac_values = params_DAC[BL]['DAC']
            params = params_DAC[BL]['params']
            oneBL_dict = {self.logs_dict['FE{}'.format(ichip)]: dict() for ichip in range(8)}
            # print(BL)
            # print(params)
            for iparam, param in enumerate(params):
                fembs = self.raw_data[param][0]
                raw_data = self.raw_data[param][1]
                decodedData = decodeRawData(fembs=fembs, rawdata=raw_data)
                for ichip in range(8):
                    FE_ID = self.logs_dict['FE{}'.format(ichip)]
                    
                    larasic = LArASIC_ana(dataASIC=decodedData[ichip], output_dir=self.FE_outputDIRs[FE_ID], chipID=FE_ID, tms=self.tms, param=param, generatePlots=False, generateQCresult=False)
                    larasic_data = dict()
                    if iparam==0:
                        larasic_data = larasic.runAnalysis(getPulseResponse=True, isRMSNoise=False) # I think when the DAC value is zero, we get a signal without pulse => only a fluctuation of the baseline
                    else:
                        larasic_data = larasic.runAnalysis(getPulseResponse=True, isRMSNoise=False)
                    chip_data = {
                        # "pedestal": larasic_data['pedrms']['pedestal']['data'],
                        # "rms": larasic_data['pedrms']['rms']['data'],
                        "pospeak": larasic_data['pulseResponse']['pospeak']['data'],
                        # "negpeak": larasic_data['pulseResponse']['negpeak']['data']
                    }
                    oneBL_dict[FE_ID][dac_values[iparam]] = chip_data
            BL_dict[BL] = oneBL_dict
        calib_data = {self.logs_dict['FE{}'.format(ichip)]: dict() for ichip in range(8)}
        for BL in unique_BL:
            for ichip in range(8):
                 FE_ID = self.logs_dict['FE{}'.format(ichip)]
                 calib_data[FE_ID][BL] = dict()
        for ichip in range(8):
            FE_ID = self.logs_dict['FE{}'.format(ichip)]
            for BL in unique_BL:
                for ich in range(16):
                    DAC_val = []
                    pospeaks = []
                    for dac in BL_dict[BL][FE_ID].keys():
                        DAC_val.append(dac)
                        pospeaks.append(BL_dict[BL][FE_ID][dac]['pospeak'][ich])
                    calib_data[FE_ID][BL][ich] = [DAC_val, pospeaks]
        for FE_ID, fedata in calib_data.items():
            dumpJson(output_path=self.FE_outputDIRs[FE_ID], output_name="Calibration_{}".format(self.suffix_filename), data_to_dump=fedata, indent=-1)

    def DATDAC_cali(self):
        '''
            Using the DAT-DAC to perform the calibration;
            LArASIC gain : 14mV/fC, peak time: 2$\mu$s
        '''
        # get config from keys
        fe_configs = dict()
        for param in self.cali_params:
            tmp = param.split('_')[2:]
            fe_configs[param] = [tmp[0], '_'.join(tmp[1:])]
            # fe_configs.append((tmp[0], '_'.join(tmp[1:]), param))
        print(fe_configs)
        # configs = 

# x-x---------------------------------------------------------------x-x
def runCalibrations(root_path: str, data_dir: str, output_path: str):
    # all_tms = [61, 62, 63]
    all_tms = [62]
    for tms in all_tms:
        calib = Calibration(root_path=root_path, data_dir=data_dir, output_path=output_path, tms=tms)
        # calib.ASICDAC_cali()
        # sys.exit()

if __name__ == '__main__':
    root_path = '../../Data_BNL_CE_WIB_SW_QC'
    output_path = '../../Analyzed_BNL_CE_WIB_SW_QC'

    list_data_dir = [dir for dir in os.listdir(root_path) if '.zip' not in dir]
    for i, data_dir in enumerate(list_data_dir):
        # if i==1:
        runCalibrations(root_path=root_path, data_dir=data_dir, output_path=output_path)
        sys.exit()