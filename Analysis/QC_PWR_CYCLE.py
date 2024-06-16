############################################################################################
#   created on 6/11/2024 @ 10:53
#   email: radofanantenan.razakamiandra@stonybrook.edu
#   Analyze the data in QC_PWR_CYCLE.bin
############################################################################################

import os, pickle
import numpy as np
from utils import createDirs, printItem, decodeRawData, dumpJson, LArASIC_ana, BaseClass

class PWR_CYCLE(BaseClass):
    def __init__(self, root_path: str, data_dir: str, output_path: str):
        printItem('FE power cycling')
        super().__init__(root_path=root_path, data_dir=data_dir, output_path=output_path, QC_filename='QC_PWR_CYCLE.bin', tms=4)

    def decode_pwrCons(self, pwrCons_data: dict):
        out_dict = {self.logs_dict['FE{}'.format(ichip)]: dict() for ichip in range(8)}
        for ichip in range(8):
            FE_ID = self.logs_dict['FE{}'.format(ichip)]
            pwr_rails = ['VDDA', 'VDDO', 'VPPP']
            tmp_out = {'V': dict(), 'I': dict(), 'P': dict()}
            for pwr_rail in pwr_rails:
                key = 'FE{}_{}'.format(ichip, pwr_rail)
                V = np.round(pwrCons_data[key][0], 4)
                I = np.round(pwrCons_data[key][1], 4)
                P = np.round(pwrCons_data[key][2], 4)
                key = pwr_rail
                if pwr_rail=='VPPP':
                    key = 'VDDP'
                tmp_out['V'][key] = V
                tmp_out['I'][key] = I
                tmp_out['P'][key] = P
            out_dict[FE_ID] = tmp_out
        return out_dict

    def decodeWF(self, decoded_wf: list, pwr_cycle_N: str):
        out_dict = {self.logs_dict['FE{}'.format(ichip)]: dict() for ichip in range(8)}
        for ichip in range(8):
            FE_ID = self.logs_dict['FE{}'.format(ichip)]
            larasic = LArASIC_ana(dataASIC=decoded_wf[ichip], output_dir=self.FE_outputDIRs[FE_ID], chipID=FE_ID, tms=self.tms, param=pwr_cycle_N, generatePlots=False, generateQCresult=False)
            data_asic = larasic.runAnalysis()
            tmp_out = {
                'pedestal': data_asic['pedrms']['pedestal']['data'],
                'rms': data_asic['pedrms']['rms']['data'],
                'pospeak': data_asic['pulseResponse']['pospeak']['data'],
                'negpeak': data_asic['pulseResponse']['negpeak']['data']
            }
            out_dict[FE_ID] = tmp_out
        return out_dict
    
    def decode_OnePwrCycle(self, pwr_cycle_N: str):
        # OUTPUT DATA
        PwrCycle_data = {self.logs_dict['FE{}'.format(ichip)]: {pwr_cycle_N: dict()} for ichip in range(8)}
        raw_data = self.raw_data[pwr_cycle_N]
        #
        fembs = raw_data[0] # FEMB list : we use the first slot of WIB only
        rawdata_wf = raw_data[1] # raw data waveform
        config_data = raw_data[2] # configuration : HOW DO WE USE THIS INFORMATION ?
        pwrCons_data = raw_data[3] # power consumption
        #
        pwr = self.decode_pwrCons(pwrCons_data=pwrCons_data)
        for ichip in range(8):
            FE_ID = self.logs_dict['FE{}'.format(ichip)]
            for key in pwr[FE_ID].keys():
                PwrCycle_data[FE_ID][pwr_cycle_N][key] = pwr[FE_ID][key]
        # decoding waveform
        decoded_wf = decodeRawData(fembs=fembs, rawdata=rawdata_wf)
        #
        chResp = self.decodeWF(decoded_wf=decoded_wf, pwr_cycle_N=pwr_cycle_N)
        for ichip in range(8):
            FE_ID = self.logs_dict['FE{}'.format(ichip)]
            for key in chResp[FE_ID].keys():
                PwrCycle_data[FE_ID][pwr_cycle_N][key] = chResp[FE_ID][key]
        return PwrCycle_data
        
    def decode_PwrCycle(self):
        N_pwrcycle = 8
        logs = {
            "date": self.logs_dict['date'],
            "testsite": self.logs_dict['testsite'],
            "env": self.logs_dict['env'],
            "note": self.logs_dict['note'],
            "WIB_slot": self.logs_dict['DAT_on_WIB_slot']
        }
        PwrCycle_data = {self.logs_dict['FE{}'.format(ichip)]: {"logs": logs} for ichip in range(8)}
        for ipcycle in range(N_pwrcycle):
            pwr_cycle_N = 'PwrCycle_{}'.format(ipcycle)
            print("Item : {}".format(pwr_cycle_N))
            one_pwrcyc = self.decode_OnePwrCycle(pwr_cycle_N=pwr_cycle_N)
            for FE_ID in one_pwrcyc.keys():
                PwrCycle_data[FE_ID][pwr_cycle_N] = one_pwrcyc[FE_ID][pwr_cycle_N]
        # save data to json file
        for ichip in range(8):
            FE_ID = self.logs_dict['FE{}'.format(ichip)]
            data = PwrCycle_data[FE_ID]
            dumpJson(output_path=self.FE_outputDIRs[FE_ID], output_name='PWR_CYCLE', data_to_dump=data)


if __name__ == '__main__':
    root_path = '../../Data_BNL_CE_WIB_SW_QC'
    output_path = '../../Analyzed_BNL_CE_WIB_SW_QC'
    list_data_dir = [dir for dir in os.listdir(root_path) if '.zip' not in dir]
    for i, data_dir in enumerate(list_data_dir):
        pwr_c = PWR_CYCLE(root_path=root_path, data_dir=data_dir, output_path=output_path)
        pwr_c.decode_PwrCycle()
