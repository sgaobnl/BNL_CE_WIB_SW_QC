############################################################################################
#   created on 6/12/2024 @ 11:32
#   email: radofanantenan.razakamiandra@stonybrook.edu
#   Analyze the calibration data: QC_CALI_ASICDAC.bin, QC_CALI_DATDAC.bin, and QC_CALI_DIRECT.bin
############################################################################################

import os, sys, pickle
import numpy as np
from utils import printItem, createDirs, dumpJson, linear_fit, LArASIC_ana, decodeRawData, getpulse, BaseClass
import matplotlib.pyplot as plt

class ASICDAC_CALI(BaseClass):
    '''
        Using the 6-bit DAC embedded on the chip to perform the calibration;
        LArASIC gain: 14mV/fC, peak time: 2$\mu$s
    '''
    def __init__(self, root_path: str, data_dir: str, output_path: str, tms: int, QC_filename: str, generateWf=False):
        printItem('ASICDAC Calibration')
        self.generateWf = generateWf
        super().__init__(root_path=root_path, data_dir=data_dir, output_path=output_path, tms=tms, QC_filename=QC_filename, generateWaveForm=self.generateWf)

    def getDAC_values(self):
        params_DAC = dict()
        unique_BL = []
        for p in self.params:
            tmp = p.split('_')
            if tmp[1] not in unique_BL:
                unique_BL.append(tmp[1])
        for SNC in unique_BL:
            params_DAC[SNC] = []
            for param in self.params:
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
            format of decodedData_oneBL:
            [[[],[],[], ...],[[],[],[], ...],....] => 8 chips [16 channels]
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
        for ichip in range(8):
            FE_ID = self.logs_dict['FE{}'.format(ichip)]
            all_ppeaks[FE_ID] = dict()
            for BL in decodedData.keys():
                all_ppeaks[FE_ID][BL] = dict()
                for chn in range(16):
                    all_ppeaks[FE_ID][BL]['CH{}'.format(chn)] = [[], []]
        # get positive peaks by using the class LArASIC_ana
        for BL in decodedData.keys():
            for dac, data in decodedData[BL]:
                for ichip in range(8):
                    FE_ID = self.logs_dict['FE{}'.format(ichip)]
                    larasic = LArASIC_ana(dataASIC=data[ichip], output_dir=self.FE_outputPlots_DIRs[FE_ID], chipID=FE_ID, tms=self.tms, param='ASICDAC_{}'.format(BL), generatePlots=False, generateQCresult=False)
                    larasic_data = larasic.runAnalysis(getPulseResponse=True, isRMSNoise=False)['pulseResponse']['pospeak']['data']
                    for chn in range(16):
                        all_ppeaks[FE_ID][BL]['CH{}'.format(chn)][0].append(dac)
                        all_ppeaks[FE_ID][BL]['CH{}'.format(chn)][1].append(larasic_data[chn])
        # save data to json
        for ichip in range(8):
            FE_ID = self.logs_dict['FE{}'.format(ichip)]
            logs = {
                "date": self.logs_dict['date'],
                "testsite": self.logs_dict['testsite'],
                "env": self.logs_dict['env'],
                "note": self.logs_dict['note'],
                "DAT_SN": self.logs_dict['DAT_SN'],
                "WIB_slot": self.logs_dict['DAT_on_WIB_slot']
            }
            data = {"logs": logs}
            for key in all_ppeaks[FE_ID].keys():
                data[key] = all_ppeaks[FE_ID][key]
            dumpJson(output_path=self.FE_outputDIRs[FE_ID], output_name='QC_CALI_{}'.format(self.suffixName), data_to_dump=data)

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
        plt.savefig('/'.join([self.FE_outputPlots_DIRs[chipID], 'Cali_ASICDAC_wf_{}_ch{}.png'.format(BL, chn)]))
        plt.close()
    #--------------------------------------------

    def runScript(self):
        params = self.getDAC_values()
        decodedData = self.decode(params_DAC=params)
        if self.generateWf:
            all_wf = self.organizeData_wf(decodedData=decodedData)
            for FE_ID in all_wf.keys():
                for BL in ['SNC0', 'SNC1']:
                    for chn in range(16):
                        self.plot_waveform(all_wf_data=all_wf, chipID=FE_ID, BL=BL, chn=chn)
        self.getPosPeak(decodedData=decodedData)

class DATDAC_CALI(BaseClass):
    '''
        Calibration using the DAC on the DAT board;
        LArASIC gain: 14mV/fC; peak time : 2$\mu$s
    '''
    def __init__(self, root_path: str, data_dir: str, output_path: str, tms:int):
        printItem("DAT-DAC calibration")
        super().__init__(root_path=root_path, data_dir=data_dir, output_path=output_path, tms=tms, QC_filename='QC_CALI_DATDAC.bin')

# class Calibration:
#     def __init__(self, root_path: str, data_dir: str, output_path: str, tms: int):
#         self.tms = tms
#         self.tms_val = {
#             61: ["QC_CALI_ASICDAC.bin", "ASICDAC calibration"],
#             62: ["QC_CALI_DATDAC.bin", "DATDAC calibration"],
#             63: ["QC_CALI_DIRECT.bin", "DIRECT input calibration"]

# x-x---------------------------------------------------------------x-x
def runCalibrations(root_path: str, data_dir: str, output_path: str):
    # all_tms = [61, 62, 63]
    # all_tms = [61]
    # for tms in all_tms:
    #     # calib = Calibration(root_path=root_path, data_dir=data_dir, output_path=output_path, tms=tms)
    #     # calib.ASICDAC_cali()

    asicdac = ASICDAC_CALI(root_path=root_path, data_dir=data_dir, output_path=output_path, tms=64, QC_filename='QC_CALI_ASICDAC_47.bin')
    asicdac.runScript(generateWf=True)
    # datdac = DATDAC_CALI(root_path=root_path, data_dir=data_dir, output_path=output_path, tms=tms)
    sys.exit()

if __name__ == '__main__':
    root_path = '../../Data_BNL_CE_WIB_SW_QC'
    output_path = '../../Analyzed_BNL_CE_WIB_SW_QC'

    list_data_dir = [dir for dir in os.listdir(root_path) if '.zip' not in dir]
    for i, data_dir in enumerate(list_data_dir):
        if i==2:
            runCalibrations(root_path=root_path, data_dir=data_dir, output_path=output_path)
        # sys.exit()