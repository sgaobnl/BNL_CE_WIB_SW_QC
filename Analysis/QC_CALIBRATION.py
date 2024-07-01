############################################################################################
#   created on 6/12/2024 @ 11:32
#   email: radofanantenan.razakamiandra@stonybrook.edu
#   Analyze the calibration data: QC_CALI_ASICDAC.bin, QC_CALI_DATDAC.bin, and QC_CALI_DIRECT.bin
############################################################################################

import os, sys
import numpy as np
from utils import printItem, createDirs, dumpJson, linear_fit, LArASIC_ana, decodeRawData, BaseClass, getMaxAmpIndices
import matplotlib.pyplot as plt

class ASICDAC_CALI(BaseClass):
    '''
        Using the 6-bit DAC embedded on the chip to perform the calibration;
        LArASIC gain: 14mV/fC, peak time: 2$\mu$s
        INFO from QC_top:
            - cali_mode=2,
            - asicdac=0,
            - period = 512,
            - width = 384
            if snc==0: maxdac = 32
            else: maxdac = 64
            - num_samples = 5
            - filename: QC_CALI_ASICDAC.bin
    '''
    def __init__(self, root_path: str, data_dir: str, output_path: str, tms: int, QC_filename: str, generateWf=False):
        printItem('ASICDAC Calibration')
        self.generateWf = generateWf
        super().__init__(root_path=root_path, data_dir=data_dir, output_path=output_path, tms=tms, QC_filename=QC_filename, generateWaveForm=self.generateWf)

    def getCFG(self):
        '''
        return:
            {
                'SNC0': [(DAC, param), (DAC, param), ...., (DAC, param)],
                'SCN1': [(DAC, param), (DAC, param), ...., (DAC, param)]
            }
        '''
        cfg = {'SNC0': [], 'SNC1': []}
        for param in self.params:
            splitted = param.split('_')
            BL = splitted[1]
            DAC = int(splitted[-1].split('ASICDAC')[-1])
            cfg[BL].append((DAC, param))
        return cfg

    def avgWf(self, data: list, dac: int):
        newdata = []
        for ichip in range(8):
            onechipdata = data[ichip]
            newchipdata = []
            width = 500
            for chn in range(16):
                chdata = np.array(onechipdata[chn])
                period = 500
                newchdata = []
                num_samples = 5
                for i in range(num_samples):
                    istart = i*period
                    iend = istart + period
                    chunkdata = chdata[istart : iend]
                    maxpos = int((iend-istart)/2)
                    if dac!=0:
                        maxpos = np.where(chunkdata==np.max(chunkdata))[0][0]
                    istart = maxpos-10
                    iend = maxpos+100
                    if istart < 0:
                        istart = 0
                    wf = chunkdata[istart : iend]
                    # chdata.append(np.array(wf))
                    newchdata.append(wf)
                L = [len(d) for d in newchdata]
                # print(L)
                imax = np.where(L==np.median(L))[0][0]
                if imax!=0:
                    newchdata[imax].pop(-1)
                sameLength = False
                while not sameLength:
                    pos = [i for i in range(len(L)) if L[i]!=L[imax]]

                    for k in pos:
                        if k==len(newchdata):
                            newchdata.pop(-1)
                        else:
                            newchdata.pop(k)
                    LL = [len(d) for d in newchdata]
                    # print(LL)
                    pos = [i for i in range(len(LL)) if LL[i]!=LL[imax]]
                    if len(pos)==0:
                        sameLength = True
                newchdata = np.array(newchdata)
                avg_wf = np.average(np.transpose(newchdata), axis=1, keepdims=False)
                newchipdata.append(avg_wf)
            newdata.append(newchipdata)
        return newdata

    def decode(self):
        '''
            Decode the raw data and get timestamps and data
        '''
        cfg = self.getCFG()
        BLs = cfg.keys()
        decoded_data = {BL: dict() for BL in BLs}
        for BL in BLs:
            DAC_param = cfg[BL] # [(DAC, param), (DAC, param), ...., (DAC, param)]
            for DAC, param in DAC_param:
                fembs = self.raw_data[param][0]
                rawdata = self.raw_data[param][1]
                data, tmstamps, cd_tmstamps = decodeRawData(fembs=fembs, rawdata=rawdata, needTimeStamps=True)
                # if DAC==4:
                decoded_data[BL][DAC] = self.avgWf(data=data, dac=DAC) # already averaged
        return decoded_data

    def organizeData(self, saveWaveformData=False):
        organized_data = dict()
        for ichip in range(8):
            FE_ID = self.logs_dict['FE{}'.format(ichip)]
            organized_data[FE_ID] = dict()
            for BL in ['SNC0', 'SNC1']:
                organized_data[FE_ID][BL] = dict()
                for chn in range(16):
                    organized_data[FE_ID][BL]['CH{}'.format(chn)] = {'DAC': [], 'CH': []} # [DAC_list, [ch_list. ch_list, ....]]
        
        # organize the data
        decodedData = self.decode()
        for ichip in range(8):
            FE_ID = self.logs_dict['FE{}'.format(ichip)]            
            for BL in decodedData.keys():
                for chn in range(16):
                    for DAC in decodedData[BL].keys():
                        dac_data = decodedData[BL][DAC][ichip][chn]
                        organized_data[FE_ID][BL]['CH{}'.format(chn)]['DAC'].append(DAC)
                        organized_data[FE_ID][BL]['CH{}'.format(chn)]['CH'].append(list(dac_data))

        if saveWaveformData:
            #@ save the organized data to json files
            for ichip in range(8):
                FE_ID = self.logs_dict['FE{}'.format(ichip)]
                dumpJson(output_path=self.FE_outputDIRs[FE_ID], output_name='CALI_{}'.format(self.suffixName), data_to_dump=organized_data[FE_ID], indent=4)
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
        
        # Pedestal
        pedestals = dict()
        for ichip in range(8):
            FE_ID = self.logs_dict['FE{}'.format(ichip)]
            pedestals[FE_ID] = dict()
            for BL in ['SNC0', 'SNC1']:
                pedestals[FE_ID][BL] = dict()
                for chn in range(16):
                    DAC = 0 # pedestal without pulse
                    CH = 'CH{}'.format(chn)
                    ped = np.round(np.mean(organizedData[FE_ID][BL][CH]['CH'][0]), 4)
                    std = np.round(np.std(organizedData[FE_ID][BL][CH]['CH'][0]), 4)
                    pedestals[FE_ID][BL][CH] = {'pedestal': ped, 'std': std}
        
        # Positive and negative Peaks
        amplitudes = dict()
        for ichip in range(8):
            FE_ID = self.logs_dict['FE{}'.format(ichip)]
            amplitudes[FE_ID] = {'logs': logs}
            for BL in ['SNC0', 'SNC1']:
                amplitudes[FE_ID][BL] = dict()
                for chn in range(16):
                    amplitudes[FE_ID][BL]['CH{}'.format(chn)] = []
                    ped = pedestals[FE_ID][BL]['CH{}'.format(chn)]['pedestal']
                    std = pedestals[FE_ID][BL]['CH{}'.format(chn)]['std']
                    for idac, dac in enumerate(organizedData[FE_ID][BL]['CH{}'.format(chn)]['DAC']):
                        dacdata = organizedData[FE_ID][BL]['CH{}'.format(chn)]['CH'][idac]
                        ppeak, npeak = 0, 0
                        if dac==0:
                            ppeak = ped
                            npeak = ped
                        else:
                            ippeak = np.where(dacdata==np.max(dacdata))[0][0]
                            ppeak = dacdata[ippeak]
                            inpeak = np.where(dacdata==np.min(dacdata))[0][0]
                            npeak = dacdata[inpeak]
                        posAmp = np.round(ppeak - ped, 4)
                        negAmp = np.round(ped - npeak, 4)
                        amplitudes[FE_ID][BL]['CH{}'.format(chn)].append({'DAC': dac, 'pedestal': ped, 'std': std,'posAmp': posAmp, 'negAmp': negAmp})
        
        # save data
        for ichip in range(8):
            FE_ID = self.logs_dict['FE{}'.format(ichip)]
            print('Save amplitudes of {} ...'.format(FE_ID))
            dumpJson(output_path=self.FE_outputDIRs[FE_ID], output_name='CALI_{}_Amp'.format(self.suffixName), data_to_dump=amplitudes[FE_ID], indent=4)

    def plotWaveForms(self, organizedData: dict):
        for ichip in range(8):
            FE_ID = self.logs_dict['FE{}'.format(ichip)]
            onechipData = organizedData[FE_ID]
            for BL in onechipData.keys():
                print(FE_ID, BL)
                for chn in range(16):
                    # print(onechipData[BL]['CH{}'.format(chn)].keys())
                    plt.figure()
                    for idac, DAC in enumerate(onechipData[BL]['CH{}'.format(chn)]['DAC']):
                        plt.plot(onechipData[BL]['CH{}'.format(chn)]['CH'][idac], label='DAC {}'.format(DAC))
                    plt.legend()
                    plt.savefig('/'.join([self.FE_outputPlots_DIRs[FE_ID], 'CALI_{}_wf_{}_chn{}.png'.format(self.suffixName, BL, chn)]))
                    plt.close()
                    # sys.exit()

    def runASICDAC_cali(self, saveWfData=False):
        organizedData = self.organizeData(saveWaveformData=saveWfData)
        if self.generateWf:
            self.plotWaveForms(organizedData=organizedData)
        self.getAmplitudes(organizedData=organizedData)

# DATDAC calibration
# class DATDAC_CALI(BaseClass):
#     def __init__(self, root_path: str, data_dir: str, output_path: str, tms: int, QC_filename: str, generateWf=False):
#         printItem("DATDAC Calibration")
#         self.generateWf = generateWf
#         super().__init__(root_path=root_path, data_dir=data_dir, output_path=output_path, tms=62, QC_filename='QC_CALI_DATDAC.bin', generateWaveForm=self.generateWf)
    
#     def getCFG(self):
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
class DATDAC_CALI(BaseClass):
    def __init__(self, root_path: str, data_dir: str, output_path: str, tms: int, QC_filename: str, generateWf=False, CALI_ITEM='DATDAC'):
        self.generateWf = generateWf
        self.CALI_ITEM = CALI_ITEM
        printItem('{} Calibration'.format(self.CALI_ITEM))
        super().__init__(root_path=root_path, data_dir=data_dir, output_path=output_path, tms=tms, QC_filename=QC_filename, generateWaveForm=self.generateWf)

    def getCFG(self):
        '''
        return:
            {
                'SNC0': [(DAC, param), (DAC, param), ...., (DAC, param)],
                'SCN1': [(DAC, param), (DAC, param), ...., (DAC, param)]
            }
        '''
        cfg = {'SNC0': [], 'SNC1': []}
        for param in self.params:
            splitted = param.split('_')
            # print(splitted)
            # BL = splitted[1]
            # DAC = int(splitted[-1].split('DATDAC')[-1])
            if self.CALI_ITEM=='DATDAC':
                BL = splitted[-1]
                DAC = splitted[2]
            elif self.CALI_ITEM=='DIRECT':
                DAC = param.split('_')[-1]
                BL = param.split('_')[1]
            cfg[BL].append((DAC, param))
        return cfg

    def avgWf(self, data: list, dac: int):
        newdata = []
        for ichip in range(8):
            onechipdata = data[ichip]
            newchipdata = []
            width = 500
            for chn in range(16):
                chdata = np.array(onechipdata[chn])
                period = 1000
                newchdata = []
                num_samples = 3
                for i in range(num_samples):
                    istart = i*period+100
                    iend = istart + period
                    chunkdata = chdata[istart : iend]
                    maxpos = int((iend-istart)/2 - 50)
                    # if dac!='4':
                        # print(np.max(chunkdata))
                    maxpos = np.where(chunkdata==np.max(chunkdata))[0][0]
                    istart = maxpos-10
                    iend = maxpos+300
                    if istart < 0:
                        istart = 0
                    wf = chunkdata[istart : iend]
                    if len(wf)!=0:
                        newchdata.append(list(wf))
                L = [len(d) for d in newchdata]
                # print(L)
                imax = np.where(L==np.median(L))[0][0]
                if imax!=0:
                    newchdata[imax].pop(-1)
                sameLength = False
                while not sameLength:
                    pos = [i for i in range(len(L)) if L[i]!=L[imax]]

                    for k in pos:
                        if k==len(newchdata):
                            newchdata.pop(-1)
                        else:
                            newchdata.pop(k)
                    LL = [len(d) for d in newchdata]
                    # print(LL)
                    if len(LL)==1:
                        sameLength = True
                    else:
                        pos = [i for i in range(len(LL)) if LL[i]!=LL[imax]]
                        if len(pos)==0:
                            sameLength = True
                newchdata = np.array(newchdata)
                avg_wf = np.average(np.transpose(newchdata), axis=1, keepdims=False)
                newchipdata.append(avg_wf)
            newdata.append(newchipdata)
        return newdata

    def decode(self):
        '''
            Decode the raw data and get timestamps and data
        '''
        cfg = self.getCFG()
        BLs = cfg.keys()
        decoded_data = {BL: dict() for BL in BLs}
        for BL in BLs:
            DAC_param = cfg[BL] # [(DAC, param), (DAC, param), ...., (DAC, param)]
            for DAC, param in DAC_param:
                fembs = self.raw_data[param][0]
                rawdata = self.raw_data[param][1]
                data, tmstamps, cd_tmstamps = decodeRawData(fembs=fembs, rawdata=rawdata, needTimeStamps=True)
                decoded_data[BL][DAC] = self.avgWf(data=data, dac=DAC) # already averaged
        return decoded_data

    def organizeData(self, saveWaveformData=False):
        organized_data = dict()
        for ichip in range(8):
            FE_ID = self.logs_dict['FE{}'.format(ichip)]
            organized_data[FE_ID] = dict()
            for BL in ['SNC0', 'SNC1']:
                organized_data[FE_ID][BL] = dict()
                for chn in range(16):
                    organized_data[FE_ID][BL]['CH{}'.format(chn)] = {'DAC': [], 'CH': []} # [DAC_list, [ch_list. ch_list, ....]]
        
        # organize the data
        decodedData = self.decode()
        for ichip in range(8):
            FE_ID = self.logs_dict['FE{}'.format(ichip)]            
            for BL in decodedData.keys():
                for chn in range(16):
                    for DAC in decodedData[BL].keys():
                        dac_data = decodedData[BL][DAC][ichip][chn]
                        organized_data[FE_ID][BL]['CH{}'.format(chn)]['DAC'].append(DAC)
                        organized_data[FE_ID][BL]['CH{}'.format(chn)]['CH'].append(list(dac_data))

        if saveWaveformData:
            #@ save the organized data to json files
            for ichip in range(8):
                FE_ID = self.logs_dict['FE{}'.format(ichip)]
                dumpJson(output_path=self.FE_outputDIRs[FE_ID], output_name='CALI_{}'.format(self.suffixName), data_to_dump=organized_data[FE_ID], indent=4)
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
        
        # Pedestal
        pedestals = dict()
        for ichip in range(8):
            FE_ID = self.logs_dict['FE{}'.format(ichip)]
            pedestals[FE_ID] = dict()
            for BL in ['SNC0', 'SNC1']:
                pedestals[FE_ID][BL] = dict()
                for chn in range(16):
                    DAC = 0 # pedestal without pulse
                    CH = 'CH{}'.format(chn)
                    ped = np.round(np.mean(organizedData[FE_ID][BL][CH]['CH'][0]), 4)
                    std = np.round(np.std(organizedData[FE_ID][BL][CH]['CH'][0]), 4)
                    pedestals[FE_ID][BL][CH] = {'pedestal': ped, 'std': std}
        
        # Positive and negative Peaks
        amplitudes = dict()
        for ichip in range(8):
            FE_ID = self.logs_dict['FE{}'.format(ichip)]
            amplitudes[FE_ID] = {'logs': logs}
            for BL in ['SNC0', 'SNC1']:
                amplitudes[FE_ID][BL] = dict()
                for chn in range(16):
                    amplitudes[FE_ID][BL]['CH{}'.format(chn)] = []
                    ped = pedestals[FE_ID][BL]['CH{}'.format(chn)]['pedestal']
                    std = pedestals[FE_ID][BL]['CH{}'.format(chn)]['std']
                    for idac, dac in enumerate(organizedData[FE_ID][BL]['CH{}'.format(chn)]['DAC']):
                        dacdata = organizedData[FE_ID][BL]['CH{}'.format(chn)]['CH'][idac]
                        ppeak, npeak = 0, 0
                        if dac==0:
                            ppeak = ped
                            npeak = ped
                        else:
                            ippeak = np.where(dacdata==np.max(dacdata))[0][0]
                            ppeak = dacdata[ippeak]
                            inpeak = np.where(dacdata==np.min(dacdata))[0][0]
                            npeak = dacdata[inpeak]
                        posAmp = np.round(ppeak - ped, 4)
                        negAmp = np.round(ped - npeak, 4)
                        amplitudes[FE_ID][BL]['CH{}'.format(chn)].append({'DAC': dac, 'pedestal': ped, 'std': std,'posAmp': posAmp, 'negAmp': negAmp})
        
        # save data
        for ichip in range(8):
            FE_ID = self.logs_dict['FE{}'.format(ichip)]
            print('Save amplitudes of {} ...'.format(FE_ID))
            dumpJson(output_path=self.FE_outputDIRs[FE_ID], output_name='CALI_{}_Amp'.format(self.suffixName), data_to_dump=amplitudes[FE_ID], indent=4)

    def plotWaveForms(self, organizedData: dict):
        for ichip in range(8):
            FE_ID = self.logs_dict['FE{}'.format(ichip)]
            onechipData = organizedData[FE_ID]
            for BL in onechipData.keys():
                print(FE_ID, BL)
                for chn in range(16):
                    # print(onechipData[BL]['CH{}'.format(chn)].keys())
                    plt.figure(figsize=(6, 6))
                    for idac, DAC in enumerate(onechipData[BL]['CH{}'.format(chn)]['DAC']):
                        plt.plot(onechipData[BL]['CH{}'.format(chn)]['CH'][idac], label='DAC {}'.format(DAC))
                    plt.legend()
                    plt.savefig('/'.join([self.FE_outputPlots_DIRs[FE_ID], 'CALI_{}_wf_{}_chn{}.png'.format(self.suffixName, BL, chn)]))
                    plt.close()
                    # sys.exit()

    def runDATDAC_cali(self, saveWfData=False):
        organizedData = self.organizeData(saveWaveformData=saveWfData)
        if self.generateWf:
            self.plotWaveForms(organizedData=organizedData)
        self.getAmplitudes(organizedData=organizedData)

if __name__ == '__main__':
    root_path = '../../Data_BNL_CE_WIB_SW_QC'
    output_path = '../../Analyzed_BNL_CE_WIB_SW_QC'

    list_data_dir = [dir for dir in os.listdir(root_path) if '.zip' not in dir]
    for i, data_dir in enumerate(list_data_dir):
        # if i==2:
        asicdac = ASICDAC_CALI(root_path=root_path, data_dir=data_dir, output_path=output_path, tms=61, QC_filename='QC_CALI_ASICDAC.bin', generateWf=True)
        asicdac.runASICDAC_cali(saveWfData=False)
        if 'QC_CALI_ASICDAC_47.bin' in os.listdir('/'.join([root_path, data_dir])):
            asic47dac = ASICDAC_CALI(root_path=root_path, data_dir=data_dir, output_path=output_path, tms=64, QC_filename='QC_CALI_ASICDAC_47.bin', generateWf=True)
            asic47dac.runASICDAC_cali(saveWfData=False)
        datdac = DATDAC_CALI(root_path=root_path, data_dir=data_dir, output_path=output_path, tms=62, QC_filename='QC_CALI_DATDAC.bin', generateWf=True, CALI_ITEM='DATDAC')
        datdac.runDATDAC_cali(saveWfData=False)
        direct = DATDAC_CALI(root_path=root_path, data_dir=data_dir, output_path=output_path, tms=63, QC_filename='QC_CALI_DIRECT.bin', generateWf=True, CALI_ITEM='DIRECT')
        direct.runDATDAC_cali(saveWfData=False)
        # sys.exit()