############################################################################################
#   created on 7/2/2024 @ 13:52
#   email: radofanantenan.razakamiandra@stonybrook.edu
#   Analyze the calibration data: QC_Cap_Meas.bin
############################################################################################

import os, sys
import numpy as np
from utils import printItem, createDirs, dumpJson, linear_fit, LArASIC_ana, decodeRawData, BaseClass #, getMaxAmpIndices, getMinAmpIndices, getPulse
import matplotlib.pyplot as plt

class QC_Cap_Meas(BaseClass):
    def __init__(self, root_path: str, data_dir: str, output_path: str, generateWf=False):
        printItem("Capacitance measurement")
        self.generateWf = generateWf
        super().__init__(root_path=root_path, data_dir=data_dir, output_path=output_path, tms=8, QC_filename="QC_Cap_Meas.bin", generateWaveForm=self.generateWf)
        self.suffixName = "Cap_Meas"
        # print(self.params)
        self.period = 1000

    def getCFG(self):
        CFG = {}
        tmpOptions = []
        for param in self.params:
            s = param.split('_')
            tmpOptions.append(s[-1])
        options = []
        for o in tmpOptions:
            if o not in options:
                options.append(o)
        for opt in options:
            CFG[opt] = []
            for param in self.params:
                if opt in param:
                    s = param.split('_')
                    CFG[opt].append((param, s[0], s[1]))
        return CFG

    def decode(self):
        '''
            output:
            {
                'CALI': {
                    FECHN00 : {
                        BL0:{
                            FE_ID0 : {'waveform': [], 'ppeak': [], 'npeak': [], 'pedestal': [], 'rms': []},
                            FE_ID1 : {'waveform': [], 'ppeak': [], 'npeak': [], 'pedestal': [], 'rms': []},
                            ...
                        },
                        BL1:{
                            FE_ID0 : {'waveform': [], 'ppeak': [], 'npeak': [], 'pedestal': [], 'rms': []},
                            FE_ID1 : {'waveform': [], 'ppeak': [], 'npeak': [], 'pedestal': [], 'rms': []},
                            ...
                        },
                    },
                    FECHN001 : {
                        BL0:{
                            FE_ID0 : {'waveform': [], 'ppeak': [], 'npeak': [], 'pedestal': [], 'rms': []},
                            FE_ID1 : {'waveform': [], 'ppeak': [], 'npeak': [], 'pedestal': [], 'rms': []},
                            ...
                        },
                        BL1:{
                            FE_ID0 : {'waveform': [], 'ppeak': [], 'npeak': [], 'pedestal': [], 'rms': []},
                            FE_ID1 : {'waveform': [], 'ppeak': [], 'npeak': [], 'pedestal': [], 'rms': []},
                            ...
                        },
                    },
                    ....
                },
                'INPUT': {
                ...
                }
            }
        '''
        decodedData = dict()
        CFG = self.getCFG()
        # self.decode_CALI(CFG=CFG['CALI'])
        for c in ['CALI', 'INPUT']:
            tmpCFG = CFG[c]
            tmpDecoded = dict()
            for p, FECHN, V in tmpCFG:
                tmpDecoded[FECHN] = dict()

            for param, FECHN, V in tmpCFG:
                _fembs = self.raw_data[param][0]
                _rawdata = self.raw_data[param][1]
                chn = self.raw_data[param][2]
                val = self.raw_data[param][3]
                period = self.raw_data[param][4]
                width = self.raw_data[param][5]
                cali_fe_info = self.raw_data[param][6]
                cfg_info = self.raw_data[param][7]
                tmp = decodeRawData(fembs=_fembs, rawdata=_rawdata, needTimeStamps=False, period=period)
                tmpDecoded[FECHN][V] = dict()
                for ichip in range(8):
                    FE_ID = self.logs_dict['FE{}'.format(ichip)]
                    larasic = LArASIC_ana(dataASIC=tmp[ichip], output_dir=self.FE_outputDIRs[FE_ID], chipID=FE_ID, tms=self.tms, param='', generatePlots=False, generateQCresult=False, period=period)
                    tmpdata = larasic.runAnalysis(getPulseResponse=True, isRMSNoise=False, getWaveforms=True)
                    # wf, ppeak, npeak, ped, rms = self.avgWf(data=tmp[ichip][chn], period=period)
                    wf = tmpdata['pulseResponse']['waveforms'][chn]
                    ppeak = tmpdata['pulseResponse']['pospeak']['data'][chn]
                    npeak = tmpdata['pulseResponse']['negpeak']['data'][chn]
                    ped = tmpdata['pedrms']['pedestal']['data'][chn]
                    rms = tmpdata['pedrms']['rms']['data'][chn]

                    tmpDecoded[FECHN][V][FE_ID] = {'waveform': wf, 'ppeak': ppeak, 'npeak': npeak, 'pedestal': ped, 'rms': rms}
                    # wf = self.avgWf(data=tmp[ichip][chn])
            # sys.exit()
            decodedData[c] = tmpDecoded
        return decodedData
    
    def saveWaveform(self, wf_data: list, FE_ID: str, chn: str, V: str, cali_input: str):
        plt.figure()
        plt.plot(wf_data)
        plt.savefig('/'.join([self.FE_outputPlots_DIRs[FE_ID], '{}_{}_{}.png'.format(cali_input, V, chn)]))
        plt.close()

    def saveData(self, decodedData: dict):
        # d[cali][fechn][bl][feid]
        # arrange the data - chip per chip
        arranged_data = dict()
        for ichip in range(8):
            FE_ID = self.logs_dict['FE{}'.format(ichip)]
            arranged_data[FE_ID] = dict()
            for c in decodedData.keys():
                arranged_data[FE_ID][c] = dict()
                for fechn in decodedData[c].keys():
                    arranged_data[FE_ID][c][fechn] = dict()
                    for bl in decodedData[c][fechn].keys():
                        arranged_data[FE_ID][c][fechn][bl] = decodedData[c][fechn][bl][FE_ID]
        # print(arranged_data)
        FE_IDs = list(arranged_data.keys())
        c = list(arranged_data[FE_IDs[0]].keys())
        fechn = list(arranged_data[FE_IDs[0]][c[0]].keys())
        bl = list(arranged_data[FE_IDs[0]][c[0]][fechn[0]])
        # print(FE_IDs, c, fechn, bl)
        # save data to json file
        for ichip in range(8):
            FE_ID = self.logs_dict['FE{}'.format(ichip)]
            print('----{}---'.format(FE_ID))
            chipdata = dict()
            chipdata['logs'] = {
                    "date": self.logs_dict['date'],
                    "testsite": self.logs_dict['testsite'],
                    "env": self.logs_dict['env'],
                    "note": self.logs_dict['note'],
                    "DAT_SN": self.logs_dict['DAT_SN'],
                    "WIB_slot": self.logs_dict['DAT_on_WIB_slot']
                }
            for c in arranged_data[FE_ID].keys():
                chipdata[c] = dict()
                for fechn in arranged_data[FE_ID][c].keys():
                    chipdata[c][fechn] = dict()
                    for bl in arranged_data[FE_ID][c][fechn].keys():
                        tmp = arranged_data[FE_ID][c][fechn][bl]
                        wf = tmp['waveform']
                        chipdata[c][fechn][bl] = {'ppeak': tmp['ppeak'], 'npeak': tmp['npeak'], 'pedestal': tmp['pedestal'], 'rms': tmp['rms']}
                        if self.generateWf:
                            self.saveWaveform(wf_data=wf, FE_ID=FE_ID, chn=fechn, V=bl, cali_input=c)
            dumpJson(output_path=self.FE_outputDIRs[FE_ID], output_name=self.suffixName, data_to_dump=chipdata, indent=4)
        # sys.exit()
                        # chipdata[c][fechn][bl] = 
        # add option to plot waveform


if __name__ == '__main__':
    # root_path = '../../Data_BNL_CE_WIB_SW_QC'
    # root_path = '../../B010T0004/Time_20240703122319_DUT_0000_1001_2002_3003_4004_5005_6006_7007/'
    output_path = '../../Analyzed_BNL_CE_WIB_SW_QC'
    root_path = '../../B010T0004'
    list_data_dir = [dir for dir in os.listdir(root_path) if (os.path.isdir('/'.join([root_path, dir]))) and (dir!='images')]
    # list_data_dir = [dir for dir in os.listdir(root_path) if '.zip' not in dir]
    for i, data_dir in enumerate(list_data_dir):
        # if i==1:
            print(data_dir)
            cap = QC_Cap_Meas(root_path=root_path, data_dir=data_dir, output_path=output_path, generateWf=False)
            decodedData = cap.decode()
            cap.saveData(decodedData=decodedData)
            # sys.exit()
