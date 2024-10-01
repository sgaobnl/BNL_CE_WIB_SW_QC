############################################################################################
#   created on 7/2/2024 @ 10:20
#   email: radofanantenan.razakamiandra@stonybrook.edu
#   Analyze the calibration data: QC_DLY_RUN.bin
############################################################################################

import os, sys
import numpy as np
from utils import printItem, dumpJson, decodeRawData, BaseClass, LArASIC_ana
import matplotlib.pyplot as plt

class QC_DLY_RUN(BaseClass):
    def __init__(self, root_path: str, data_dir: str, output_path: str, generateWf=False):
        printItem("DELAY RUN")
        self.generateWf = generateWf
        super().__init__(root_path=root_path, data_dir=data_dir, output_path=output_path, tms=7, QC_filename="QC_DLY_RUN.bin", generateWaveForm=self.generateWf)
        self.suffixName = "DLY_RUN"
        self.period = 1000
    
    def getPhase_Period(self):
        Phase_Period = dict()
        for param in self.params:
            data = self.raw_data[param]
            phase = data[3]
            period = data[4]
            Phase_Period[param] = {'phase': phase, 'period': period}
        # print(Phase_Period)
        return Phase_Period

    def avgWf(self, data_in: list):
        newdata = []
        for ichip in range(8):
            onechipdata = data_in[ichip]
            FE_ID = self.logs_dict['FE{}'.format(ichip)]
            larasic = LArASIC_ana(dataASIC=onechipdata, output_dir=self.FE_outputDIRs[FE_ID], chipID=FE_ID, tms=self.tms, param='', generatePlots=False, generateQCresult=False, period=self.period)
            tmpdata = larasic.runAnalysis(getPulseResponse=True, isRMSNoise=False, getWaveforms=True)
            newchipdata = {}
            for chn in range(16):
                newchipdata['CH{}'.format(chn)] = {
                                                    'wf': tmpdata['pulseResponse']['waveforms'][chn], 
                                                    'pedestal': tmpdata['pedrms']['pedestal']['data'][chn], 
                                                    'rms': tmpdata['pedrms']['rms']['data'][chn]
                                                }
            newdata.append(newchipdata)
        return newdata

    def decode(self):
        decodedData = dict()
        Phase_Period = self.getPhase_Period()

        for param in self.params:
            __rawdata = self.raw_data[param]
            fembs = __rawdata[0]
            rawdata = __rawdata[1]
            # decodedData = decodeRawData(fembs=fembs, rawdata=rawdata, needTimeStamps=False)
            data = self.avgWf(data_in=decodeRawData(fembs=fembs, rawdata=rawdata, needTimeStamps=False, period=self.period))
            decodedData[param] = {'data': data, 'phase': Phase_Period[param]['phase'], 'period': Phase_Period[param]['period']}
        return decodedData
    
    def organizeData(self, decodedData):
        organized_data = dict()
        for ichip in range(8):
            FE_ID = self.logs_dict['FE{}'.format(ichip)]
            organized_data[FE_ID] = dict()
            for param in self.params:
                organized_data[FE_ID][param] = dict()
                for chn in range(16):
                    organized_data[FE_ID][param]['CH{}'.format(chn)] = dict()
        for param in self.params:
            tmpdata = decodedData[param]
            phase = tmpdata['phase']
            period = tmpdata['period']
            for ichip in range(8):
                FE_ID = self.logs_dict['FE{}'.format(ichip)]
                organized_data[FE_ID][param]['phase'] = phase
                organized_data[FE_ID][param]['period'] = period
                chipdata = tmpdata['data'][ichip]
                for chn in range(16):
                    chdata = chipdata['CH{}'.format(chn)]['wf']
                    pedestal = chipdata['CH{}'.format(chn)]['pedestal']
                    rms = chipdata['CH{}'.format(chn)]['rms']
                    organized_data[FE_ID][param]['CH{}'.format(chn)] = {'data': chdata, 'pedestal': pedestal, 'rms': rms}
        newdata = dict()
        for ichip in range(8):
            FE_ID = self.logs_dict['FE{}'.format(ichip)]
            newdata[FE_ID] = dict()
            onechipdata = {'CH{}'.format(ich): [] for ich in range(16)}
            phases = organized_data[FE_ID].keys()
            # group data by channel
            for phase in phases:
                for ich in range(16):
                    CH = 'CH{}'.format(ich)
                    onechipdata[CH].append(organized_data[FE_ID][phase][CH])
            # merge phases for each channel
            for ich in range(16):
                # tmpd = np.array([np.array(d['data']) for ph, d in enumerate(onechipdata['CH{}'.format(ich)])])
                tmpd = np.array([np.array(onechipdata['CH{}'.format(ich)][i]['data']) for i in range(31, -1, -1)])
                print(tmpd.shape)
                transpose_tmpd = np.transpose(tmpd) # transpose the previous matrix
                # transpose_tmpd = tmpd
                print(transpose_tmpd.shape)
                print(len(transpose_tmpd[0, :]))
                print(transpose_tmpd[0, :])
                tmpresult = transpose_tmpd.flatten() # 2d array --> 1d vector
                print(len(tmpresult)==32*1000)
                CHnumber = 'CH{}'.format(ich)
                newdata[FE_ID][CHnumber] = tmpresult
                plt.figure()
                x = [i for i in range(len(newdata[FE_ID][CHnumber]))]
                # plt.scatter(x=x, y=newdata[FE_ID][CHnumber])
                plt.plot(newdata[FE_ID][CHnumber], marker='*')
                plt.show()
                sys.exit()
            print(onechipdata['CH0'][0].keys())
            sys.exit()
        return organized_data
    
    def getAmplitudes(self, organizedData: dict):
        # logs
        logs = {
                "date": self.logs_dict['date'],
                "testsite": self.logs_dict['testsite'],
                "env": self.logs_dict['env'],
                "note": self.logs_dict['note'],
                "DAT_SN": self.logs_dict['DAT_SN'],
                "WIB_slot": self.logs_dict['DAT_on_WIB_slot']
            }
        for ichip in range(8):
            FE_ID = self.logs_dict['FE{}'.format(ichip)]
            tmpchipData = organizedData[FE_ID]
            chipdata = {
                'logs': logs
            }
            for param in tmpchipData.keys():
                phase = tmpchipData[param]['phase']
                period = tmpchipData[param]['period']
                key = "Phase{}_Period{}".format(phase, period)
                chipdata[key] = {'phase': phase, 'period': period}
                for chn in range(16):
                    wf = tmpchipData[param]['CH{}'.format(chn)]['data']
                    pedestal = tmpchipData[param]['CH{}'.format(chn)]['pedestal']
                    rms = np.round(tmpchipData[param]['CH{}'.format(chn)]['rms'], 4)
                    #
                    ppeak = np.round(np.max(wf)-pedestal, 4)
                    npeak = np.round(pedestal - np.min(wf), 4)
                    chipdata[key]['CH{}'.format(chn)] = {'pospeak': ppeak, 'negpeak': npeak, 'pedestal': pedestal, 'rms': rms}
            
            # save data
            print("Save data for {}...".format(FE_ID))
            dumpJson(output_path=self.FE_outputDIRs[FE_ID], output_name=self.suffixName, data_to_dump=chipdata, indent=4)

    def plotWaveforms(self, organizedData: dict):
        for ichip in range(8):
            FE_ID = self.logs_dict['FE{}'.format(ichip)]
            chipdata = organizedData[FE_ID]
            for chn in range(16):
                CH = 'CH{}'.format(chn)
                plt.figure(figsize=(15,15))
                for param in chipdata.keys():
                    phase = chipdata[param]['phase']
                    period = chipdata[param]['period']
                    wf = chipdata[param][CH]['data']
                    plt.plot(wf, label="phase = {}, period = {}".format(phase, period))
                plt.legend(loc='upper right')
                print("save waveform for {}, {}...".format(FE_ID, CH))
                plt.savefig('/'.join([self.FE_outputPlots_DIRs[FE_ID], '{}_CH{}.png'.format(self.suffixName, chn)]))
                plt.close()

    def run_DLY_RUN(self):
        decodedData = self.decode()
        organizedData = self.organizeData(decodedData=decodedData)
        print(type(organizedData))
        print(organizedData.keys())
        print(type(organizedData['20240703122319']))
        print(organizedData['20240703122319'].keys())
        print(type(organizedData['20240703122319']['Phase0000_freq1000']))
        print(organizedData['20240703122319']['Phase0000_freq1000'].keys())
        sys.exit()
        self.getAmplitudes(organizedData=organizedData)
        if self.generateWf:
            self.plotWaveforms(organizedData=organizedData)

if __name__ == '__main__':
    # root_path = '../../Data_BNL_CE_WIB_SW_QC'
    output_path = '../../Analyzed_BNL_CE_WIB_SW_QC'
    # list_data_dir = [dir for dir in os.listdir(root_path) if '.zip' not in dir]
    root_path = '../../B010T0004'
    list_data_dir = [dir for dir in os.listdir(root_path) if (os.path.isdir('/'.join([root_path, dir]))) and (dir!='images')]
    for i, data_dir in enumerate(list_data_dir):
        dly_run = QC_DLY_RUN(root_path=root_path, data_dir=data_dir, output_path=output_path, generateWf=True)
        dly_run.run_DLY_RUN()
        # sys.exit()