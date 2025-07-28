############################################################################################
#   created on 7/2/2024 @ 13:52
#   email: radofanantenan.razakamiandra@stonybrook.edu
#   Analyze the calibration data: QC_Cap_Meas.bin
############################################################################################

import os, sys, csv
import numpy as np
import pandas as pd
from utils import printItem, createDirs, dumpJson, linear_fit, LArASIC_ana, decodeRawData, BaseClass #, getMaxAmpIndices, getMinAmpIndices, getPulse
from utils import BaseClass_Ana
from scipy.stats import norm

class QC_Cap_Meas(BaseClass):
    def __init__(self, root_path: str, data_dir: str, output_path: str, env='RT'):
        printItem("Capacitance measurement")
        super().__init__(root_path=root_path, data_dir=data_dir, output_path=output_path, tms=8, QC_filename="QC_Cap_Meas.bin",  env=env)
        #self.suffixName = "Cap_Meas"
        # print(self.params)
        self.period = 1000

    def getCFG(self):
        CFG = {}
        tmpOptions = []
        # print(self.params)
        # print('\n\n')
        for param in self.params:
            s = param.split('_')
            tmpOptions.append(s[-1])
        # print(tmpOptions,'\n\n')
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
            #print('----{}---'.format(FE_ID))
            chipdata = dict()
            #chipdata['logs'] = {
            #        "date": self.logs_dict['date'],
            #        "testsite": self.logs_dict['testsite'],
            #        "env": self.logs_dict['env'],
            #        "note": self.logs_dict['note'],
            #        "DAT_SN": self.logs_dict['DAT_SN'],
            #        "WIB_slot": self.logs_dict['DAT_on_WIB_slot']
            #    }
            for c in arranged_data[FE_ID].keys():
                chipdata[c] = dict()
                for fechn in arranged_data[FE_ID][c].keys():
                    chipdata[c][fechn] = dict()
                    for bl in arranged_data[FE_ID][c][fechn].keys():
                        tmp = arranged_data[FE_ID][c][fechn][bl]
                        wf = tmp['waveform']
                        chipdata[c][fechn][bl] = {'ppeak': tmp['ppeak'], 'npeak': tmp['npeak'], 'pedestal': tmp['pedestal'], 'rms': tmp['rms']}
            #dumpJson(output_path=self.FE_outputDIRs[FE_ID], output_name=self.suffixName, data_to_dump=chipdata, indent=4)
            dumpJson(output_path=self.FE_outputDIRs[FE_ID], output_name="QC_Cap_Meas", data_to_dump=chipdata, indent=4)
        # sys.exit()
                        # chipdata[c][fechn][bl] = 
        # add option to plot waveform
    
    def decode_CapMeas(self):
        if self.ERROR:
            return
        decodedData = self.decode()
        self.saveData(decodedData=decodedData)

class QC_Cap_Meas_Ana(BaseClass_Ana):
    def __init__(self, root_path: str, output_path: str, chipID: str):
        self.item = 'QC_Cap_Meas'
        print (self.item)
        self.tms = '08'
        super().__init__(root_path=root_path, chipID=chipID, output_path=output_path, item=self.item)
        self.root_path = root_path
        self.output_path = output_path
        #self.output_dir = '/'.join([output_path, chipID, self.item])
        #print(self.output_dir)
        #try:
        #    os.mkdir('/'.join([output_path, chipID]))
        #except OSError:
        #    pass
        #try:
        #    os.mkdir(self.output_dir)
        #except OSError:
        #    pass
        self.ratioCap = []
        # this is hard coded because the keys and filename do not have them
        config = {
            'BL': '200mV',
            'peakTime': '3us',
            'gain': '4.7mV/fC'
        }
        self.config = dict(config)

    def getRatioCapacitance(self, returnDF=False):
        chn_list = list(self.data['INPUT'].keys())
        # print(chn_list)
        ratioC = []
        for chn in chn_list:
            chn_ref = self.data['INPUT'][chn]
            chn_cali = self.data['CALI'][chn]
            # reference
            vref = [float(v.split('m')[0]) for v in chn_ref.keys()]
            imin_vref, imax_vref = np.argmin(vref), np.argmax(vref)
            delta_vref = vref[imax_vref] - vref[imin_vref]
            refmax = str(int(vref[imax_vref])) + 'mV'
            refmin = str(int(vref[imin_vref])) + 'mV'
            Aref = chn_ref[refmax]['ppeak'] - chn_ref[refmin]['ppeak']
            Cref = (Aref/delta_vref)*0.185

            # cali
            vcali = [float(v.split('m')[0]) for v in chn_cali.keys()]
            imin_vcali, imax_vcali = np.argmin(vcali), np.argmax(vcali)
            delta_vcali = vcali[imax_vcali] - vcali[imin_vcali]
            icalimax, icalimin = '0'+str(int(vcali[imax_vcali])) + 'mV', '0'+str(int(vcali[imin_vcali])) + 'mV'
            Acali = chn_cali[icalimax]['ppeak'] - chn_cali[icalimin]['ppeak']
            Ccali = (Acali/delta_vcali)
            
            ratio = Ccali/Cref
            ## NOTE ABOUT THIS IS ON MY IPAD : notes from the chat with Shanshan
            ratioC.append(ratio)
        self.ratioCap = ratioC
        if returnDF:
            CH_list = [int(ch.split('N')[1]) for ch in chn_list]
            return pd.DataFrame({'CH': CH_list, 'BL': [self.config['BL'] for _ in CH_list], 
                    'peakTime': [self.config['peakTime'] for _ in CH_list], 
                    'gain': [self.config['gain'] for _ in CH_list], 
                    'Cap': np.array(ratioC)})
        else:
            return np.array(ratioC)
    

    def run_Ana(self):
        Cap_df = self.getRatioCapacitance(returnDF=True)
        combined_df = pd.DataFrame({
#            'item': [ None for _ in range(16)],
            'BL': [Cap_df.iloc[0]['BL'] for _ in range(16)],
            'peakTime': [ Cap_df.iloc[0]['peakTime'] for _ in range(16)],
            'gain': [Cap_df.iloc[0]['gain'] for _ in range(16)],
#            'meanCap (pF)': [ None for _ in range(16)],
#            'stdCap (pF)': [None for _ in range(16)],
            'Cap (pF)': Cap_df['Cap'],
            'CH': Cap_df['CH']
        })
        combined_df['QC_result'] = None

        #combined_df.drop(['meanCap (pF)', 'stdCap (pF)'], axis=1, inplace=True, errors='ignore')

        cfg = '_'.join(combined_df.iloc[0][['BL', 'peakTime', 'gain']].dropna())
        row_data = ['Test_{}_Capacitance'.format(self.tms), cfg]
        for chn in combined_df['CH']:
            row_data.append('CH{}=(Cap (pF)={})'.format(chn, combined_df.iloc[chn]['Cap (pF)']))

        row_data = [row_data]
        #with open('/'.join([self.output_path, self.chipID, '{}.csv'.format(self.item)]), 'w') as csvfile:
        #    csv.writer(csvfile, delimiter=',').writerows(row_data)    
        return row_data 


if __name__ == '__main__':
    root_path = "E:/B009T0008/"
    output_path = root_path + "Ana"
    data_dir = "Time_20250527114445_DUT_0000_1001_2002_3003_4004_5005_6006_7007"
    env = 'RT'
    cap = QC_Cap_Meas(root_path=root_path, data_dir=data_dir, output_path=output_path, env=env)
    cap.decode_CapMeas()
