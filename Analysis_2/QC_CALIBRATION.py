############################################################################################
#   created on 6/12/2024 @ 11:32
#   email: radofanantenan.razakamiandra@stonybrook.edu
#   Analyze the calibration data: QC_CALI_ASICDAC.bin, QC_CALI_DATDAC.bin, and QC_CALI_DIRECT.bin
############################################################################################

import os, pickle, sys, statistics, pandas as pd, csv
import numpy as np
from utils import printItem, createDirs, dumpJson, linear_fit, LArASIC_ana, decodeRawData, BaseClass #, getPulse
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from utils import BaseClass_Ana, gain_inl
from scipy.stats import norm

class QC_CALI(BaseClass):
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
    def __init__(self, root_path: str, data_dir: str, output_path: str, tms: int, QC_filename: str, generateWf=False, env='RT'):
        if tms in [61, 64]:
            printItem('ASICDAC Calibration')
            self.period = 500
        elif tms==62:
            printItem('DATDAC calibration')
            self.period = 1000
        elif tms==63:
            printItem('DIRECT calibration')
            self.period = 1000
        self.generateWf = generateWf
        super().__init__(root_path=root_path, data_dir=data_dir, output_path=output_path, tms=tms, QC_filename=QC_filename, generateWaveForm=self.generateWf, env=env)
        if self.ERROR:
            return
            

    def getCFG(self):
        '''
        return:
            {
                'SNC0': [(DAC, param), (DAC, param), ...., (DAC, param)],
                'SCN1': [(DAC, param), (DAC, param), ...., (DAC, param)]
            }
        '''
        cfg = {'SNC0': [], 'SNC1': []}
        if self.tms in [61, 64]:
            for param in self.params:
                splitted = param.split('_')
                BL = splitted[1]
                DAC = int(splitted[-1].split('ASICDAC')[-1])
                cfg[BL].append((DAC, param))
        elif self.tms in [62, 63]:
            cfg = {'SNC0': [], 'SNC1': []}
            for param in self.params:
                splitted = param.split('_')
                # if self.CALI_ITEM=='DATDAC':
                if self.tms==62:
                    BL = splitted[-1]
                    DAC = splitted[2]
                # elif self.CALI_ITEM=='DIRECT':
                if self.tms==63:
                    DAC = param.split('_')[-1]
                    BL = param.split('_')[1]

                if 'Vref' in BL:
                    continue
                if 'Ext' in BL:
                    continue
                cfg[BL].append((DAC, param))
        # print(cfg)
        # sys.exit()
        return cfg

    def avgWf(self, data: list, param='ASIC', getWaveforms=False):
        newdata = []
        for ichip in range(len(data)):
            ASIC_ID = self.logs_dict['FE{}'.format(ichip)]
            larasic = LArASIC_ana(dataASIC=data[ichip], output_dir=self.FE_outputDIRs[ASIC_ID], chipID=ASIC_ID, tms=self.tms, param=param, generateQCresult=False, generatePlots=False, period=self.period)
            data_asic = larasic.runAnalysis(getWaveforms=getWaveforms)
            chipdata = {'pedestal': data_asic['pedrms']['pedestal']['data'],
                        'rms': data_asic['pedrms']['rms']['data'],
                        'pospeak': data_asic['pulseResponse']['pospeak']['data'],
                        'negpeak': data_asic['pulseResponse']['negpeak']['data'],
                        }
            if getWaveforms:
                        chipdata['waveforms'] = data_asic['pulseResponse']['waveforms']
            newdata.append(chipdata)
        return newdata

    def decode(self, getWaveform_data=False):
        '''
            Decode the raw data and get timestamps and data
        '''
        cfg = self.getCFG()
        BLs = cfg.keys()
        decoded_data = {BL: dict() for BL in BLs}
        for BL in BLs:
            DAC_param = cfg[BL] # [(DAC, param), (DAC, param), ...., (DAC, param)]
            print('-- Start decoding BL {} --'.format(BL))
            for DAC, param in DAC_param:
                print('Decoding DAC {}...'.format(DAC))
                # print(param)
                fembs = self.raw_data[param][0]
                rawdata = self.raw_data[param][1]
                data = decodeRawData(fembs=fembs, rawdata=rawdata, period=self.period)
                if self.tms==62:
                    DAC_cfg = '_'.join(param.split('_')[2:-1])
                    decoded_data[BL][DAC_cfg] = self.avgWf(data=data, param=param, getWaveforms=getWaveform_data)
                else:
                    decoded_data[BL][DAC] = self.avgWf(data=data, param=param, getWaveforms=getWaveform_data) # already averaged
            print('-- End of decoding BL {} --'.format(BL))
            # print(decoded_data[BL].keys())
            # sys.exit()
        return decoded_data

    def organizeData(self, saveWaveformData=False):
        organized_data = dict()
        for ichip in range(8):
            FE_ID = self.logs_dict['FE{}'.format(ichip)]
            organized_data[FE_ID] = dict()
            for BL in ['SNC0', 'SNC1']:
                organized_data[FE_ID][BL] = dict()
                for chn in range(16):
                    organized_data[FE_ID][BL]['CH{}'.format(chn)] = {'DAC': [], 'CH': [], 'pedestal': [], 'rms': [], 'pospeak': [], 'negpeak': []} # [DAC_list, [ch_list. ch_list, ....]]

        # organize the data
        decodedData = self.decode(getWaveform_data=self.generateWf)
        # print(decodedData['SNC0'].keys())
        # sys.exit()
        for ichip in range(8):
            FE_ID = self.logs_dict['FE{}'.format(ichip)]            
            for BL in decodedData.keys():
                # print(BL)
                # print(decodedData[BL].keys())
                # sys.exit()
                for chn in range(16):
                    for DAC in decodedData[BL].keys():
                        pedestal = decodedData[BL][DAC][ichip]['pedestal'][chn]
                        rms = decodedData[BL][DAC][ichip]['rms'][chn]
                        pospeak = decodedData[BL][DAC][ichip]['pospeak'][chn]
                        negpeak = decodedData[BL][DAC][ichip]['negpeak'][chn]
                        organized_data[FE_ID][BL]['CH{}'.format(chn)]['DAC'].append(DAC)
                        if self.generateWf:
                            dac_data = decodedData[BL][DAC][ichip]['waveforms'][chn]
                            organized_data[FE_ID][BL]['CH{}'.format(chn)]['CH'].append(list(dac_data))
                        organized_data[FE_ID][BL]['CH{}'.format(chn)]['pedestal'].append(pedestal)
                        organized_data[FE_ID][BL]['CH{}'.format(chn)]['rms'].append(rms)
                        organized_data[FE_ID][BL]['CH{}'.format(chn)]['pospeak'].append(pospeak)
                        organized_data[FE_ID][BL]['CH{}'.format(chn)]['negpeak'].append(negpeak)

        if saveWaveformData:
            #@ save the organized data to json files
            for ichip in range(8):
                FE_ID = self.logs_dict['FE{}'.format(ichip)]
                dumpJson(output_path=self.FE_outputDIRs[FE_ID], output_name='CALI_{}'.format(self.suffixName), data_to_dump=organized_data[FE_ID], indent=4)
        return organized_data

    def getAmplitudes(self, organizedData: dict):
        # logs
        #logs = {
        #        "date": self.logs_dict['date'],
        #        "testsite": self.logs_dict['testsite'],
        #        "env": self.logs_dict['env'],
        #        "note": self.logs_dict['note'],
        #        "DAT_SN": self.logs_dict['DAT_SN'],
        #        "WIB_slot": self.logs_dict['DAT_on_WIB_slot']
        #    }
        
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
                    ped = organizedData[FE_ID][BL][CH]['pedestal'][DAC]
                    std = organizedData[FE_ID][BL][CH]['rms'][DAC]
                    pedestals[FE_ID][BL][CH] = {'pedestal': ped, 'std': std}
        
        # Positive and negative Peaks
        amplitudes = dict()
        for ichip in range(8):
            FE_ID = self.logs_dict['FE{}'.format(ichip)]
            #amplitudes[FE_ID] = {'logs': logs}
            for BL in ['SNC0', 'SNC1']:
                amplitudes[FE_ID][BL] = dict()
                for chn in range(16):
                    amplitudes[FE_ID][BL]['CH{}'.format(chn)] = []
                    ped = pedestals[FE_ID][BL]['CH{}'.format(chn)]['pedestal']
                    std = pedestals[FE_ID][BL]['CH{}'.format(chn)]['std']
                    for idac, dac in enumerate(organizedData[FE_ID][BL]['CH{}'.format(chn)]['DAC']):
                        posAmp = organizedData[FE_ID][BL]['CH{}'.format(chn)]['pospeak'][idac]
                        negAmp = organizedData[FE_ID][BL]['CH{}'.format(chn)]['negpeak'][idac]
                        amplitudes[FE_ID][BL]['CH{}'.format(chn)].append({'DAC': dac, 'pedestal': ped, 'std': std,'posAmp': posAmp, 'negAmp': negAmp})
        
        # save data
        for ichip in range(8):
            FE_ID = self.logs_dict['FE{}'.format(ichip)]
            print('Save amplitudes of {} ...'.format(FE_ID))
            dumpJson(output_path=self.FE_outputDIRs[FE_ID], output_name='QC_CALI_{}'.format(self.suffixName), data_to_dump=amplitudes[FE_ID], indent=4)
        

    def plotWaveForms(self, organizedData: dict):
        for ichip in range(8):
            FE_ID = self.logs_dict['FE{}'.format(ichip)]
            onechipData = organizedData[FE_ID]
            print('Saving waveform for {}'.format(FE_ID))
            for BL in onechipData.keys():
                # print(FE_ID, BL)
                for chn in range(16):
                    plt.figure()
                    for idac, DAC in enumerate(onechipData[BL]['CH{}'.format(chn)]['DAC']):
                        dacdata = onechipData[BL]['CH{}'.format(chn)]['CH'][idac]
                        # plt.plot(dacdata, label='DAC {}'.format(DAC))
                        width = 20
                        # pospeak, h = find_peaks(x=dacdata, height=np.max(dacdata))
                        pospeak = np.argmax(dacdata)
                        if pospeak-10 < 0:
                            front = dacdata[-100 : ]
                            back = dacdata[ : -100]
                            dacdata = np.concatenate((front, back))
                            plt.plot(dacdata[pospeak-6 : pospeak+width], label='DAC {}'.format(DAC))
                        else:
                            plt.plot(dacdata[pospeak-6 :pospeak+width], label='DAC {}'.format(DAC))
                    plt.legend()
                    plt.savefig('/'.join([self.FE_outputPlots_DIRs[FE_ID], 'CALI_{}_wf_{}_chn{}.png'.format(self.suffixName, BL, chn)]))
                    plt.close()

    def runASICDAC_cali(self, saveWfData=False):
        if self.ERROR:
            return
        organizedData = self.organizeData(saveWaveformData=saveWfData)
        if self.generateWf:
            self.plotWaveForms(organizedData=organizedData)
        self.getAmplitudes(organizedData=organizedData)

#@ Analysis of the decoded data
class QC_CALI_Ana(BaseClass_Ana):
    def __init__(self, root_path: str, output_path: str, chipID: str, CALI_item: str):
        self.item = CALI_item 
        super().__init__(root_path=root_path, chipID=chipID, output_path=output_path, item=CALI_item)
        self.root_path = root_path
        self.output_path = output_path
#        self.output_dir = '/'.join([self.output_dir, CALI_item])
#        try:
#            os.mkdir(self.output_dir)
#        except OSError:
#            pass
#        print(self.output_dir)

        # slk0=0
        # slk1=0
        # st0=1
        # st1=1
        # sg0=0
        # sg1=0
        # sdd=0
        # sdf=0
        self.setGain = '14mV/fC'
        if 'ASICDAC_47' in self.item:
            self.setGain = '4.7mV/fC'
        self.config = { # config for ASICDAC
            'RQI' : '500pA',
            'SLKH' : 'disabled',
            'peakTime' : '2us',
            'gain' : self.setGain,
            'output' : 'SE_SEDC'
        }
        # We got the following gains from the Monitoring with the commercial ADC
        self.Mon_Gain = {
            '4.7mV/fC': 19.111,
            '7.8mV/fC': 14.7436,
            '14mV/fC': 8.2996,
            '25mV/fC': 4.7272
        }
        self.unit_MonGain = 'mV/DAC bit'
        self.CalibCap = 185*1E-15 # the calibration capacitance with ASICDAC is 185 fF = 0.185 pF
        self.CalibCap_DATDAC = 1000*1E-15 # Need to confirm with Shanshan. Calibration capacitance for DATDAC and DIRECT is equal to 1E-12 F = 1pF
        self.tms = {'CALI_ASICDAC': 61,
                    'CALI_DATDAC': 62,
                    'CALI_DIRECT': 63,
                    'CALI_ASICDAC_47': 64}['_'.join(CALI_item.split('_')[1:])]
        
    def getINL(self, BL: str, item: str, returnGain=False, generatePlot=False):
        '''
            - For each channel number, get the DAC and item values.
            - Get the INL for each channel.
            - Return the INL for the 16 channels.
            We use the positive amplitude to get the linearity.
        '''
        data = self.data[BL]
        allDAC_cfg = []
        unique_DAC_cfg = []
        if self.tms==62:
            allDAC_cfg = ['_'.join(dac_cfg['DAC'].split('_')[1:]) for dac_cfg in data['CH0']]
            unique_DAC_cfg = list(dict.fromkeys(allDAC_cfg))
        else:
            unique_DAC_cfg = ['cfg']
        
        df = {'BL':[], 'outputCFG': [], 'CH': [], 'DAC': [], 'data': [], 'pedestal': []}
        # if self.tms==62:
        for DAC_cfg in unique_DAC_cfg:
            for chn in range(16):
                chdata = data['CH{}'.format(chn)]
                for d in chdata:
                    tmp_dac_cfg = d['DAC']
                    dac = 0
                    cfg = ''
                    if self.tms==62:
                        dac = float((tmp_dac_cfg.split('_')[0]).split('m')[0])
                        cfg = '_'.join(tmp_dac_cfg.split('_')[1:])
                    else:
                        dac = tmp_dac_cfg
                        if type(dac)==str:
                            dac = int(dac.split('m')[0])
                        cfg = DAC_cfg
                    if cfg==DAC_cfg:
                        df['pedestal'].append(d['pedestal'])
                        df['BL'].append(BL)
                        df['outputCFG'].append(cfg)
                        df['CH'].append(chn)
                        df['DAC'].append(dac)
                        df['data'].append(d[item])
        df = pd.DataFrame(df)
        
        # if self.tms==62:
        all_INLs = {}
        all_GAINs = {}
        all_linearity_range = {}
        for dac_cfg in unique_DAC_cfg:
            INLs = {}
            GAINs = {}
            linearity_range = {}
            dac_cfg_df = df[df['outputCFG']==dac_cfg].copy()
            for chn in range(16):
                chdf = dac_cfg_df[dac_cfg_df['CH']==chn].copy()
                chdf.sort_values(by='data', inplace=True)
                chdf = chdf.reset_index()
                # calib = self.Mon_Gain[self.config['gain']] * self.CalibCap / np.power(10., -15) # mV/DAC bit * C  * 1E15 = mV/DAC bit * fC
                # if self.tms==62 | self.tms==63:
                #     calib = self.CalibCap_DATDAC / np.power(10., -12)
                # # chdf['DAC'] = chdf['DAC'] * 1e-3 * self.CalibCap / np.power(10., -15) # unit of input charge : fC
                # chdf['DAC'] = chdf['DAC'] * 1e-3 * calib # DAC bit * 1E-3 * mV/DAC bit * fC = V * fC
                # calibcap = self.CalibCap
                # if self.tms==62 | self.tms==63:
                #     calibcap = self.CalibCap_DATDAC
                
                ##
                ## gain in mV / DAC bit
                ## DAC in DAC
                ## CalibCap in F
                ##
                ## select calibcap
                calibCap = self.CalibCap
                if self.tms==62 | self.tms==63:
                    calibCap = self.CalibCap_DATDAC
                ## DAC in V
                if 'ASICDAC' in self.item:
                    chdf['DAC'] = chdf['DAC'] * self.Mon_Gain[self.config['gain']] * 1E-3
                else:
                    chdf['DAC'] = chdf['DAC'] * 1E-3
                ## DAC in fC
                chdf['DAC'] = chdf['DAC'] * calibCap * 1E15
                ## DAC in e-
                # chdf['DAC'] = chdf['DAC'] * calibCap / (1.602*1E-19)
                # plt.figure()
                # plt.scatter(y=chdf['DAC'], x=chdf['data'])
                # plt.show()
                # sys.exit()
                #print(self.item, '------------', item, BL)
                slope, yintercept, inl, linRange = gain_inl(y=chdf['DAC'], x=chdf['data'], item=self.item)

                if generatePlot:
                    ypred = slope*chdf['data'] + yintercept
                    # print(slope, yintercept, inl, linRange)
                    label = 'gain = {} fC/ADC bit, worst inl = {}% \n minCharge = {} fC, maxCharge = {} fC'.format( np.round(slope,4), np.round(inl*100,4), np.round(linRange[0], 4), np.round(linRange[1], 4) )
                    plt.figure()
                    plt.scatter(chdf['data'], chdf['DAC'], label=label)
                    plt.plot(chdf['data'], ypred, 'r')
                    plt.xlabel('{} (ADC bit)'.format(item))
                    plt.ylabel('Charge (fC)')
                    plt.legend()
                    plt.savefig('/'.join([self.output_path, '{}_ChargeVSamplitude_{}_{}.png'.format(self.item, BL, item)]))
                    plt.close()
                INLs[chn] = inl # need to  multiply by 100  to get %
                GAINs[chn] = slope
                linearity_range[chn] = linRange
            all_INLs[dac_cfg] = INLs # INL*100 gives %
            all_GAINs[dac_cfg] = GAINs # in fC/ADC bit
            all_linearity_range[dac_cfg] = linearity_range # in fC
        if returnGain:
            # print(all_INLs)
            # sys.exit()
            return all_INLs, all_GAINs, all_linearity_range, df
        else:
            return all_INLs
    
    def getItem_forStatAna(self, generatePlot=False):
        '''
            Idea I want to implement in this function:
            - concatenate the data for the 16-channels corresponding to each DAC value
        '''
        BLs = ['SNC0', 'SNC1']
        outdf = pd.DataFrame()
        for ibl, BL in enumerate(BLs):
            BLdf = pd.DataFrame()
            for iitem, item in enumerate(['posAmp', 'negAmp']):
                isNegAmp_SNC1 = (BL=='SNC1') and (item=='negAmp')
                if isNegAmp_SNC1:
                    continue
                # BL_INL_pos/negAmp = [all_INLs, all_GAINs, all_linearity_range, df]
                # BL_INL_posAmp = self.getINL(BL=BL, item='posAmp', returnGain=True, generatePlot=generatePlot)
                BL_INL_posAmp = self.getINL(BL=BL, item=item, returnGain=True, generatePlot=generatePlot)
                # BL_INL_negAmp = self.getINL(BL=BL, item='negAmp', returnGain=True, generatePlot=generatePlot)
                # negAmp_df = BL_INL_negAmp[3]
                posAmp_df = BL_INL_posAmp[3]

                # For both dataframes, the configurations are the same
                list_configs = np.unique(posAmp_df['outputCFG'])
                DAC_list = np.unique(posAmp_df['DAC'])

                for icfg, CFG in enumerate(list_configs):
                    cfgdf = pd.DataFrame()
                    # cfgneg_df = negAmp_df[negAmp_df['outputCFG']==CFG].copy()
                    # cfgneg_df['item'] = ['negAmp' for _ in range(len(cfgneg_df['CH']))]
                    cfgpos_df = posAmp_df[posAmp_df['outputCFG']==CFG].copy()
                    # cfgpos_df['item'] = ['posAmp' for _ in range(len(cfgpos_df['CH']))]
                    cfgpos_df['item'] = [item for _ in range(len(cfgpos_df['CH']))]
                    for chn in range(16):
                        # units : inl to be multiplied by 100 to get %, gain in fC/ADC bit, linRange in fC
                        # negAmp
                        chn_pos_df = cfgpos_df[cfgpos_df['CH']==chn].copy()
                        chnINL_pos = BL_INL_posAmp[0][CFG][chn]
                        chnGAIN_pos = BL_INL_posAmp[1][CFG][chn]
                        chnLinRange_pos = np.round(BL_INL_posAmp[2][CFG][chn][1]-BL_INL_posAmp[2][CFG][chn][0], 2) # after discussion with Shanshan, only represent the maximum and set the minimum to zero
                        chn_pos_df['INL'] = [chnINL_pos for _ in range(len(chn_pos_df['DAC']))]
                        chn_pos_df['GAIN'] = [chnGAIN_pos for _ in range(len(chn_pos_df['DAC']))]
                        chn_pos_df['linRange'] = [chnLinRange_pos for _ in range(len(chn_pos_df['DAC']))]

                        chndf = chn_pos_df.copy()
                        # chndf = pd.concat([chn_neg_df, chn_pos_df], axis=0)
                        if chn==0:
                            cfgdf = chndf
                        else:
                            cfgdf = pd.concat([cfgdf, chndf], axis=0)
                    if (iitem==0) and (icfg==0):
                        BLdf = cfgdf
                    else:
                        BLdf = pd.concat([BLdf, cfgdf], axis=0)
            if ibl==0:
                outdf = BLdf
            else:
                outdf = pd.concat([outdf, BLdf], axis=0)
        outdf.reset_index(drop=True, inplace=True)
        return outdf

    def getDAClist(self, BL: str):
        data = self.data[BL]
        DAClist = []
        ch = 'CH0'
        for d in data[ch]:
            DAClist.append(d['DAC'])
        return DAClist


    def getDataperDAC(self, BL: str, item: str, DAC: int):
        data = self.data[BL]
        allchDACdata = []
        chns = list(range(16))
        for ich in range(16):
            CH = "CH{}".format(ich)
            # get dict with the corresponding DAC value
            dacdata = dict()
            for d in data[CH]:
                if d["DAC"] == DAC:
                    dacdata = d
            allchDACdata.append(dacdata[item])
        return DAC, chns, allchDACdata
    
    def getmeanData(self, BL: str, item: str):
        '''
            Get the average of the 16 channels value of "item" for each DAC. 
        '''
        data = self.data[BL]
        DAC_list = self.getDAClist(BL=BL)
        # for d in data["CH0"]:
        #     DAC_list.append(d["DAC"])
        DAC_list = sorted(DAC_list)

        meandata = []
        stddata = []
        for idac, dac in enumerate(DAC_list):
            onedac_data = []
            for ich in range(16):
                chn = "CH{}".format(ich)
                d = data[chn][idac]
                onedac_data.append(d[item])
            mean = np.round(np.mean(onedac_data), 4)
            std = np.round(np.std(onedac_data), 4)
            meandata.append(mean)
            stddata.append(std)
        
        return DAC_list, meandata, stddata

    
                    
        # else:
        #     all_INLs = {}
        #     all_GAINs = {}
        #     all_linearity_range = {}
        #     for cfg in unique_DAC_cfg:
        #         INLs = {}
        #         GAINs = {}
        #         linearity_range = {}
        #         for chn in range(16):
        #             # print("-DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD-")
        #             # print(df)
        #             # sys.exit()
        #             chdf = df[df['CH']==chn].copy()
        #             chdf.sort_values(by='data', inplace=True)
        #             chdf = chdf.reset_index()
        #             # double-check the gain and DAC values
        #             if ('ASICDAC' in self.item):
        #                 chdf['DAC'] = chdf['DAC'] * self.Mon_Gain[self.config['gain']] * 1e-3 * self.CalibCap / np.power(10., -15) # unit of input charge : fC
        #             else:
        #                 chdf['DAC'] = chdf['DAC'] * 1e-3 * self.CalibCap / np.power(10., -15) # unit of input charge : fC
        #             # check linearity and get INL
        #             # slope, yintercept, inl = linear_fit(x=DAC_list[1:-2], y=item_data[1:-2])
        #             # if 'ASICDAC' in self.item:
        #             # slope, yintercept, inl, linRange = gain_inl(x=chdf['DAC_list'], y=chdf['item_data'], item=self.item)
        #             slope, yintercept, inl, linRange = gain_inl(y=chdf['DAC'], x=chdf['data'], item=self.item)
        #             # # unit of slope (=gain) : fC / ADC bit
        #             # # unit of linRange : fC
        #             # # unit of yintercept : fC because the DAC value (charge) is on the y-axis
        #             # #
        #             #############################################################################

        #             if generatePlot:
        #                 # print(chdf)
        #                 ypred = slope*chdf['data'] + yintercept
        #                 # print(slope, yintercept, inl, linRange)
        #                 label = 'gain = {} fC/ADC bit, worst inl = {}% \n minCharge = {} fC, maxCharge = {} fC'.format( np.round(slope,4), np.round(inl*100,4), np.round(linRange[0], 4), np.round(linRange[1], 4) )
        #                 plt.figure()
        #                 plt.scatter(chdf['data'], chdf['DAC'], label=label)
        #                 plt.plot(chdf['data'], ypred, 'r')
        #                 plt.xlabel('{} (ADC bit)'.format(item))
        #                 plt.ylabel('Charge (fC)')
        #                 plt.legend()
        #                 plt.savefig('/'.join([self.output_dir, '{}_ChargeVSamplitude_{}_{}.png'.format(self.item, BL, item)]))
        #                 plt.close()
        #             # sys.exit()

        #             # slope, yintercept, inl = linear_fit(x=df['DAC_list'], y=df['item_data'])
        #             # print(inl)
        #             #---------------- Convert the unit of gain to e-/ADC bit ----------------
        #             # linRange = np.array(linRange)
        #             # gain = slope
        #             # if 'ASICDAC' in self.item:
        #             #     linRange = linRange * self.Mon_Gain[self.config['gain']] * 1E-3 # this is the DAC value, in Volt
        #             #     gain = gain * self.Mon_Gain[self.config['gain']] * 1E-3
        #             # else:
        #             #     linRange = linRange * 1E-3 # we just needed to convert to Volt
        #             #     gain = gain * 1E-3
        #             # # chargeLinRange = linRange * self.CalibCap / (1.602*np.power(10.,-19)) # charge with unit e-
        #             # chargeLinRange = linRange * self.CalibCap / np.power(10.,-12) # charge with unit Coulomb
        #             # gain = gain * self.CalibCap / np.power(10., -12)
        #             # print(chargeLinRange, gain)
        #             # sys.exit()
        #             INLs[chn] = inl # need to  multiply by 100  to get %
        #             GAINs[chn] = slope
        #             linearity_range[chn] = linRange
        #         all_INLs[cfg] = INLs
        #         all_GAINs[cfg] = GAINs
        #         all_linearity_range[cfg] = linearity_range
        #     if returnGain:
        #         # print(INLs, GAINs, linearity_range)
        #         # sys.exit()
        #         # return INLs, GAINs, linearity_range, df
        #         return all_INLs, all_GAINs, all_linearity_range, df
        #     else:
        #         return INLs
    
    def Amp_vs_CH(self):
        items = ['posAmp', 'negAmp']
        BLs = ['SNC0', 'SNC1']
        BL_dict = {'SNC0': '900mV', 'SNC1' : '200mV'}
        for BL in BLs:
            for item in items:
                DAClist = self.getDAClist(BL=BL)
                fig, ax = plt.subplots()
                for dac in DAClist:
                    DAC, chns, allchdacdata = self.getDataperDAC(BL=BL, item=item, DAC=dac)
                    ax.plot(chns, allchdacdata, label='{}'.format(DAC))
                ax.set_xlabel('CH');ax.set_ylabel('ADC bit')
                ax.set_title('{} : {}'.format(BL_dict[BL], item))
                ax.legend()
                fig.savefig('/'.join([self.output_path, '{}_ampch_{}_{}.png'.format(self.item, BL_dict[BL], item)]))
                plt.close()
    
    def Amp_vs_DAC(self):
        items = ['posAmp', 'negAmp']
        BLs = ['SNC0', 'SNC1']
        BL_dict = {'SNC0': '900mV', 'SNC1' : '200mV'}
        for item in items:
            for BL in BLs:
                daclist, meandata, stddata = self.getmeanData(BL=BL, item=item)
                fig, ax = plt.subplots()
                ax.errorbar(x=daclist, y=meandata, yerr=stddata)
                ax.set_xlabel('DAC');ax.set_ylabel('ADC bit')
                ax.set_title('{} : {}'.format(BL_dict[BL], item))
                plt.grid(True)
                fig.savefig('/'.join([self.output_path, '{}_ampdac_{}_{}.png'.format(self.item, BL_dict[BL], item)]))
                plt.close()
    
    def INL_vs_CH(self):
        items = ['posAmp', 'negAmp']
        BLs = ['SNC0', 'SNC1']
        BL_dict = {'SNC0': '900mV', 'SNC1' : '200mV'}
        for item in items:
            for BL in BLs:
                isNegAmp_200BL = (item=='negAmp') & (BL=='SNC1')
                if not isNegAmp_200BL:
                    inls = self.getINL(BL=BL, item=item, generatePlot=True)
                    fig, ax = plt.subplots()
                    ax.plot(inls.keys(), inls.values())
                    ax.set_xlabel('CH');ax.set_ylabel('INL')
                    ax.set_title('{} : {}'.format(BL_dict[BL], item))
                    fig.savefig('/'.join([self.output_path, '{}_inlCH_{}_{}.png'.format(self.item, BL_dict[BL], item)]))
                    plt.close()

    def makeplots(self):
        if self.ERROR:
            return
        self.Amp_vs_CH()
        # self.Amp_vs_DAC()
        self.INL_vs_CH()
        
    def run_Ana(self, generatePlots=False, path_to_statAna=None):
        """
        Analyze calibration data and optionally compare with statistical thresholds.
        
        Args:
            generatePlots (bool): Whether to generate analysis plots
            path_to_statAna (str, optional): Path to CSV file with statistical thresholds.
                                        If None, only raw data analysis is performed.
        """
        if self.ERROR:
            return

        if generatePlots:
            self.makeplots()

        items = ['posAmp', 'negAmp']
        BLs = ['SNC0', 'SNC1']
        BL_dict = {'SNC0': '900mV', 'SNC1' : '200mV'}
        out_dict = {'item': [], 'CFG': [], 'BL': [], 'ch': [], 'gain (fC/ADC bit)': [], 'worstINL (%)': [], 'linRange (fC)': []}

        # Original data processing code remains unchanged
        for item in items:
            for BL in BLs:
                isNegAmp_200BL = (item=='negAmp') & (BL=='SNC1')
                if not isNegAmp_200BL:
                    outINL = self.getINL(BL=BL, item=item, generatePlot=generatePlots, returnGain=True)
                    configurations = list(outINL[0].keys())
                    all_INLs = outINL[0]
                    all_GAINs = outINL[1]
                    all_linearity_range = outINL[2]
                    df = outINL[3]
                    for cfg in configurations:
                        cfg_INL_dict = all_INLs[cfg]
                        cfg_GAIN_dict = all_GAINs[cfg]
                        cfg_linRange_dict = all_linearity_range[cfg]
                        for ich in range(16):
                            out_dict['ch'].append(ich)
                            out_dict['item'].append(item)
                            out_dict['BL'].append(BL)
                            out_dict['CFG'].append(cfg)
                            out_dict['gain (fC/ADC bit)'].append(np.round(cfg_GAIN_dict[ich], 4))
                            out_dict['worstINL (%)'].append(np.round(cfg_INL_dict[ich]*100, 2))
                            out_dict['linRange (fC)'].append(np.round(cfg_linRange_dict[ich][1]-cfg_linRange_dict[ich][0], 2))

        out_df = pd.DataFrame(out_dict)

        # Statistical analysis is optional
        result_qc_df = pd.DataFrame()
        if path_to_statAna is not None:
            cali_statAna_df = pd.read_csv(path_to_statAna)
            measItems = cali_statAna_df['measItem'].unique()
            
            tmp_out_df = pd.DataFrame()
            for i in range(len(measItems)):
                tmp_df = cali_statAna_df[cali_statAna_df['measItem']==measItems[i]].copy().reset_index().drop('index', axis=1)
                if i==0:
                    tmp_out_df = tmp_df[['item', 'CFG', 'BL', 'mean', 'std']].copy()
                else:
                    tmp_out_df = pd.merge(tmp_out_df, tmp_df[['item', 'CFG', 'BL', 'mean', 'std']], on=['item', 'CFG', 'BL'], how='outer')
                tmp_out_df.rename(columns={'mean': 'mean_{}'.format(measItems[i]), 'std': 'std_{}'.format(measItems[i])}, inplace=True)

            # Rest of statistical analysis code remains unchanged
            cali_statAna_new_df = {key: [] for key in tmp_out_df.keys()}
            cali_statAna_new_df['ch'] = []
            for i, val in enumerate(tmp_out_df['item']):
                for ich in range(16):
                    for measItem in tmp_out_df.keys():
                        cali_statAna_new_df[measItem].append(tmp_out_df.iloc[i][measItem])
                    cali_statAna_new_df['ch'].append(ich)
            cali_statAna_new_df = pd.DataFrame(cali_statAna_new_df)

            combined_df = pd.merge(out_df, cali_statAna_new_df, on=['item', 'CFG', 'BL', 'ch'], how='outer')
            keys_combined = combined_df.keys()

            for i, measItem in enumerate(measItems):
                k = [key for key in keys_combined if measItem in key]
                tmp = combined_df[['item', 'CFG','BL', 'ch']+k].copy().reset_index().drop('index', axis=1)
                keyval = [t for t in k if ('mean' not in t) & ('std' not in t)]
                try:
                    keyval = keyval[0]
                except:
                    print('key val = ',keyval)
                    print('measItem = ', measItem)
                
                tmp.rename(columns={keyval: 'value', 'mean_{}'.format(measItem): 'mean', 'std_{}'.format(measItem): 'std'}, inplace=True)
                if measItem=='INL':
                    tmp['QC_result'] = (tmp['value'] < 1)
                else:
                    tmp['QC_result']= (tmp['value']>= (tmp['mean']-3*tmp['std'])) & (tmp['value'] <= (tmp['mean']+3*tmp['std']))
                tmp.drop(['mean', 'std'], axis=1, inplace=True)
                tmp.rename(columns={'value': keyval, 'QC_result': 'QC_result_{}'.format(measItem)}, inplace=True)
                if i==0:
                    result_qc_df = tmp.copy().reset_index().drop('index', axis=1)
                else:
                    result_qc_df = pd.merge(result_qc_df, tmp, on=['item', 'CFG','BL', 'ch'], how='outer')

        # Choose output based on whether statistical analysis was done
        final_df = result_qc_df if path_to_statAna is not None else out_df
        #final_df.to_csv('/'.join([self.output_path, self.chipID, self.item+'.csv']), index=False)

        # Generate summary with or without QC results
        if path_to_statAna is not None:
            # Original QC summary code with pass/fail
            qc_res_cols = [c for c in final_df.columns if 'QC_result' in c]
            overall_result = 'PASSED'
            for c in qc_res_cols:
                if False in final_df[c]:
                    overall_result = 'FAILED'
        
        # Rest of result formatting code remains unchanged...
        result_in_list = []
        for item in ['posAmp', 'negAmp']:
            tmp_df = pd.DataFrame()
            BLs = []
            if item=='posAmp':
                tmp_df = final_df[final_df['item']=='posAmp']
                BLs = ['SNC0', 'SNC1']
            elif item=='negAmp':
                tmp_df = final_df[final_df['item']=='negAmp']
                BLs = ['SNC0']
            for BL in BLs:
                configurations = tmp_df['CFG'].unique()
                bl_df = tmp_df[tmp_df['BL']==BL].copy().reset_index().drop('index', axis=1)
                for cfg in configurations:
                    cfg_df = bl_df[bl_df['CFG']==cfg].copy().reset_index().drop('index', axis=1)
                    result_Amp_cfg = []
                    result_Amp_cfg.append('Test_{}_{}'.format(self.tms, self.item))
                    
                    if path_to_statAna is not None:
                        # Add QC result if statistical analysis was done
                        item_cfg_result = 'PASSED'
                        for c in qc_res_cols:
                            if False in cfg_df[c]:
                                item_cfg_result = 'FAILED'
                                break
                        __BL = '900mV' if BL=='SNC0' else '200mV'
                        result_Amp_cfg.append('_'.join([__BL, item, cfg]))
                        result_Amp_cfg.append(item_cfg_result)
                    else:
                        # Just add configuration info without QC result
                        __BL = '900mV' if BL=='SNC0' else '200mV'
                        result_Amp_cfg.append('_'.join([__BL, item, cfg]))

                    for ich, ch in enumerate(cfg_df['ch']):
                        gain = cfg_df.iloc[ich]['gain (fC/ADC bit)']
                        worstINL = cfg_df.iloc[ich]['worstINL (%)']
                        linRange = cfg_df.iloc[ich]['linRange (fC)']
                        result_Amp_cfg.append("CH{}=(worstINL={};gain={};linRangeCharge={})".format(ch, worstINL, gain, linRange))
                    result_in_list.append(result_Amp_cfg)

        # Save results
        with open('/'.join([self.output_path, self.chipID, '{}.csv'.format(self.item)]), 'w') as csvfile:
            csv.writer(csvfile, delimiter=',').writerows(result_in_list)        


    def run_Ana_withStat(self, generatePlots=False, path_to_statAna=''):
        if self.ERROR:
            return
        if generatePlots:
            self.makeplots()
        items = ['posAmp', 'negAmp']
        BLs = ['SNC0', 'SNC1']
        BL_dict = {'SNC0': '900mV', 'SNC1' : '200mV'}
        # out_dict = {'item' : [], 'BL': [], 'CFG': [], 'ch': [], 'gain (fC/ADC bit)': [], 'worstINL (%)': [], 'minCharge (fC)': [], 'maxCharge (fC)': []}
        out_dict = {'item' : [], 'BL': [], 'CFG': [], 'ch': [], 'gain (fC/ADC bit)': [], 'worstINL (%)': [], 'linRange (fC)': []}
        for item in items:
            for BL in BLs:
                print("output of getINL")
                isNegAmp_200BL = (item=='negAmp') & (BL=='SNC1')
                if isNegAmp_200BL:
                    continue
                # format of the output of self.getINL : all_INLs, all_GAINs, all_linearity_range, df
                outINL = self.getINL(BL=BL, item=item, generatePlot=generatePlots, returnGain=True)
                configurations = list(outINL[0].keys())
                # print(outINL[0])
                # print('-----------------------')
                # print(outINL[1])
                # print('------------------------')
                # print(outINL[2])
                # print('-----------------------')
                # print(outINL[3])
                # print('-----------------------')
                # print(configurations)
                all_INLs = outINL[0]
                all_GAINs = outINL[1]
                all_linearity_range = outINL[2]
                df = outINL[3]
                for cfg in configurations:
                    cfg_INL_dict =all_INLs[cfg]
                    cfg_GAIN_dict = all_GAINs[cfg]
                    cfg_linRange_dict = all_linearity_range[cfg]
                    for ich in range(16):
                        out_dict['ch'].append(ich)
                        out_dict['item'].append(item)
                        out_dict['BL'].append(BL)
                        out_dict['CFG'].append(cfg)
                        out_dict['gain (fC/ADC bit)'].append(np.round(cfg_GAIN_dict[ich], 4))
                        out_dict['worstINL (%)'].append(np.round(cfg_INL_dict[ich]*100, 2)) # the worstINL is converted to %
                        out_dict['linRange (fC)'].append(np.round(cfg_linRange_dict[ich][1]-cfg_linRange_dict[ich][0], 2))
                        # out_dict['minCharge (fC)'].append(0)
                        # out_dict['maxCharge (fC)'].append(np.round(cfg_linRange_dict[ich][1]-cfg_linRange_dict[ich][0], 2))
                # print(out_dict)
                # sys.exit()
                # worstinls, gains, linRanges = self.getINL(BL=BL, item=item, generatePlot=generatePlots, returnGain=True)
                # for ich in range(16):
                #     out_dict['ch'].append(ich)
                #     out_dict['item'].append(item)
                #     out_dict['BL'].append(BL)
                #     out_dict['gain (fC/ADC bit)'].append(np.round(gains[ich], 4))
                #     out_dict['worstINL (%)'].append(np.round(worstinls[ich]*100, 4)) # the worstINL is converted to %
                #     out_dict['minCharge (fC)'].append(linRanges[ich][0])
                #     out_dict['maxCharge (fC)'].append(linRanges[ich][1])
        
        out_df = pd.DataFrame(out_dict)
        # print(out_df)
        print('---------------- After converting out_df ------------')
        # print(out_df)
        # sys.exit()
        # out_df.to_csv('/'.join([self.output_dir, self.item+'.csv']),index=False)
        #
        # get statistical analysis file
        cali_statAna_df = pd.read_csv(path_to_statAna)
        # print(cali_statAna_df)
        # print('------------ after reading statAna --------------')
        ## Append statAna to the result for one chip
        measItems = cali_statAna_df['measItem'].unique()
        
        # print(cali_statAna_df[cali_statAna_df['measItem']=='INL'])
        tmp_out_df = pd.DataFrame()
        for i in range(len(measItems)):
            tmp_df = cali_statAna_df[cali_statAna_df['measItem']==measItems[i]].copy().reset_index().drop('index', axis=1)
            # print(tmp_df)
            if i==0:
                tmp_out_df = tmp_df[['item', 'CFG', 'BL', 'mean', 'std']].copy()
            else:
                tmp_out_df = pd.merge(tmp_out_df, tmp_df[['item', 'CFG', 'BL', 'mean', 'std']], on=['item', 'CFG', 'BL'], how='outer')
            tmp_out_df.rename(columns={'mean': 'mean_{}'.format(measItems[i]), 'std': 'std_{}'.format(measItems[i])}, inplace=True)

        cali_statAna_new_df = {key: [] for key in tmp_out_df.keys()}
        cali_statAna_new_df['ch'] = []
        for i, val in enumerate(tmp_out_df['item']):
            for ich in range(16):
                for measItem in tmp_out_df.keys():
                        cali_statAna_new_df[measItem].append(tmp_out_df.iloc[i][measItem])
                cali_statAna_new_df['ch'].append(ich)
        cali_statAna_new_df = pd.DataFrame(cali_statAna_new_df)

        combined_df = pd.merge(out_df, cali_statAna_new_df, on=['item', 'CFG', 'BL', 'ch'], how='outer')
        # print('------ combined_df ----------')
        # print(combined_df)
        
        keys_combined = combined_df.keys()
        # print(keys_combined)
        # print(measItems)
        # sys.exit()
        result_qc_df = pd.DataFrame()
        for i, measItem in enumerate(measItems):
            k = [key for key in keys_combined if measItem in key] 
            tmp = combined_df[['item', 'CFG','BL', 'ch']+k].copy().reset_index().drop('index', axis=1)
            # print(tmp)
            # print(k)

            keyval = [t for t in k if ('mean' not in t) & ('std' not in t)]
            try:
                keyval = keyval[0]
                # print(keyval)
            except:
                print('key val = ',keyval)
                print('measItem = ', measItem)
            
            tmp.rename(columns={keyval: 'value', 'mean_{}'.format(measItem): 'mean', 'std_{}'.format(measItem): 'std'}, inplace=True)
            if measItem=='INL': # we accept ASIC with worstINL < 1% (double-check with Shanshan)
                tmp['QC_result'] = (tmp['value'] < 1)
            else:
                tmp['QC_result']= (tmp['value']>= (tmp['mean']-3*tmp['std'])) & (tmp['value'] <= (tmp['mean']+3*tmp['std']))
            tmp.drop(['mean', 'std'], axis=1, inplace=True)
            tmp.rename(columns={'value': keyval, 'QC_result': 'QC_result_{}'.format(measItem)}, inplace=True)
            if i==0:
                result_qc_df = tmp.copy().reset_index().drop('index', axis=1)
            else:
                result_qc_df = pd.merge(result_qc_df, tmp, on=['item', 'CFG','BL', 'ch'], how='outer')
        # print('------------ result_qc_df --------------')
        # print(result_qc_df)
        # sys.exit()
        # drop the case where item==negAmp and BL=SNC1. We expect a non-linear behavior when it comes to the negative amplitude of the baseline 200mV
        posAmp_df = result_qc_df[result_qc_df['item']=='posAmp'].copy().reset_index().drop('index', axis=1)
        negAmp_df = result_qc_df[result_qc_df['item']=='negAmp'].copy()
        SNC0_negAmp_df = negAmp_df[negAmp_df['BL']=='SNC0'].copy().reset_index().drop('index', axis=1)
        out_df = pd.concat([posAmp_df, SNC0_negAmp_df], axis=0).reset_index().drop('index', axis=1)
        out_df.to_csv('/'.join([self.output_dir, self.item+'.csv']),index=False)
        # print('------------ out_df ------------')
        # print(out_df)
        # sys.exit()
        ##
        ## Generate the summary of the QC
        qc_res_cols = [c for c in out_df.columns if 'QC_result' in c]
        overall_result = 'PASSED'
        for c in qc_res_cols:
            if False in out_df[c]:
                overall_result = 'FAILED'

        print("LENGTH out_df = ",len(out_df['item'])//16)
        posAmp_df = out_df[out_df['item']=='posAmp']
        negAmp_df = out_df[out_df['item']=='negAmp']
        result_in_list = []
        for item in ['posAmp', 'negAmp']:
            tmp_df = pd.DataFrame()
            BLs = []
            if item=='posAmp':
                tmp_df = out_df[out_df['item']=='posAmp']
                BLs = ['SNC0', 'SNC1']
            elif item=='negAmp':
                tmp_df = out_df[out_df['item']=='negAmp']
                BLs = ['SNC0']
            for BL in BLs:
                # print('------------------------')
                # print(tmp_df)
                # sys.exit()
                configurations = tmp_df['CFG'].unique()
                # print(configurations)
                # sys.exit()
                bl_df = tmp_df[tmp_df['BL']==BL].copy().reset_index().drop('index', axis=1)
                for cfg in configurations:
                    cfg_df = bl_df[bl_df['CFG']==cfg].copy().reset_index().drop('index', axis=1)
                    result_Amp_cfg = []
                    # bl_df = tmp_df[tmp_df['BL']==BL].copy().reset_index().drop('index', axis=1)
                    result_Amp_cfg.append('Test_{}_{}'.format(self.tms, self.item))
                    item_cfg_result = 'PASSED'
                    for c in qc_res_cols:
                        if False in cfg_df[c]:
                            item_cfg_result = 'FAILED'
                            break
                    __BL = ''
                    if BL=='SNC0':
                        __BL = '900mV'
                    elif BL=='SNC1':
                        __BL = '200mV'
                    result_Amp_cfg.append('_'.join([__BL, item, cfg]))
                    result_Amp_cfg.append(item_cfg_result)

                    for ich, ch in enumerate(cfg_df['ch']):
                        gain = cfg_df.iloc[ich]['gain (fC/ADC bit)']
                        worstINL = cfg_df.iloc[ich]['worstINL (%)']
                        # minCharge = cfg_df.iloc[ich]['minCharge (fC)']
                        # maxCharge = cfg_df.iloc[ich]['maxCharge (fC)']
                        # result_Amp_cfg.append("CH{}=(worstINL={};gain={};minCharge={};maxCharge={})".format(ch, worstINL, gain, minCharge, maxCharge))
                        linRange = cfg_df.iloc[ich]['linRange (fC)']
                        result_Amp_cfg.append("CH{}=(worstINL={};gain={};linRangeCharge={})".format(ch, worstINL, gain, linRange))
                    result_in_list.append(result_Amp_cfg)
                # print(result_in_list)
                # sys.exit()
        return result_in_list

    
def StatAna_cali(root_path: str, output_path: str, cali_item='QC_CALI_ASICDAC', saveDist=False):
    def plot_distribution(array, xtitle, output_path_fig, figname):
        xmin, xmax = np.min(array), np.max(array)
        mean, std = np.round(statistics.mean(array), 4), np.round(statistics.stdev(array), 4)
        x = np.linspace(xmin, xmax, len(array))
        p = norm.pdf(x, mean, std)
        Nbins = len(array)//32
        plt.figure()
        plt.hist(array, bins=Nbins, density=True)
        plt.plot(x, p, 'r', label='mean = {}, std = {}'.format(mean, std))
        plt.xlabel(xtitle);plt.ylabel('#')
        plt.legend()
        plt.savefig('/'.join([output_path_fig, figname + '.png']))
        plt.close()

    outdata = dict()
    # processed_data = {'SNC0': {'INL': [], 'GAIN': [], 'minCharge (fC)': [], 'maxCharge (fC)': []}, 'SNC1': {'INL': [], 'GAIN': [], 'minCharge (fC)': [], 'maxCharge (fC)' : []}} # to save the gain and inl
    # processed_data = {'posAmp' : {'SNC0': {'INL': [], 'GAIN': [], 'minCharge': [], 'maxCharge': []}, 'SNC1': {'INL': [], 'GAIN': [], 'minCharge': [], 'maxCharge' : []}},
    #                 'negAmp' : {'SNC0': {'INL': [], 'GAIN': [], 'minCharge': [], 'maxCharge': []}, 'SNC1': {'INL': [], 'GAIN': [], 'minCharge': [], 'maxCharge' : []}}
    #                 }
    processed_data_df = pd.DataFrame()
    output_path_fig = '/'.join([output_path, 'fig'])
    list_chipID = os.listdir(root_path)
    firstData = True
    BLs = []
    DACs = [[], []]
    for chipID in list_chipID:
        ana_cali = QC_CALI_Ana(root_path=root_path, output_path=output_path, chipID=chipID, CALI_item=cali_item)
        if ana_cali.ERROR:
            continue
        chipdata = ana_cali.getItem_forStatAna(generatePlot=False)
        # print('---------------- HERE ------------------')
        # print(chipdata[chipdata['BL']=='SNC1']['item'].unique())
        # sys.exit()
        if firstData:
            # outdata = chipdata
            # print(chipdata)
            # BLs = list(chipdata.keys())
            # for BL in BLs:
            #     outdata[BL] = {key: val for key, val in chipdata[BL]['data'].items()}
            #     for k in ['posAmp', 'negAmp']:
            #         key = k+'_INL'
            #         processed_data[k][BL]['INL'] = np.array([v for i, v in chipdata[BL][key]['inl'].items()])
            #         processed_data[k][BL]['GAIN'] = np.array([v for i, v in chipdata[BL][key]['gain'].items()])
            #         processed_data[k][BL]['minCharge'] = np.array([v[0] for i, v in chipdata[BL][key]['linRange'].items()])
            #         processed_data[k][BL]['maxCharge'] = np.array([v[1] for i, v in chipdata[BL][key]['linRange'].items()])
            # DACs = [list(outdata[bl]['DAC']) for bl in BLs]
            processed_data_df = chipdata.copy()
            firstData = False
        else:
            # for ibl, bl in enumerate(BLs):
            #     for k in ['posAmp', 'negAmp']:
            #         key = k+'_INL'
            #         inls = np.array([v for v in chipdata[bl][key]['inl'].values()])
            #         gains = np.array([v for v in chipdata[bl][key]['gain'].values()])
            #         maxCharges = np.array([v[1] for v in chipdata[bl][key]['linRange'].values()])
            #         minCharges = np.array([v[0] for v in chipdata[bl][key]['linRange'].values()])
            #         processed_data[k][bl]['INL'] = np.concatenate((processed_data[k][bl]['INL'], inls))
            #         processed_data[k][bl]['GAIN'] = np.concatenate((processed_data[k][bl]['GAIN'], gains))
            #         processed_data[k][bl]['minCharge'] = np.concatenate((processed_data[k][bl]['minCharge'], minCharges))
            #         processed_data[k][bl]['maxCharge'] = np.concatenate((processed_data[k][bl]['maxCharge'], maxCharges))
            #     for idac, dac in enumerate(DACs[ibl]):
            #         outdata[bl]['pedestal'][idac] = np.concatenate((outdata[bl]['pedestal'][idac], chipdata[bl]['data']['pedestal'][idac]))
            #         outdata[bl]['posAmp'][idac] = np.concatenate((outdata[bl]['posAmp'][idac], chipdata[bl]['data']['posAmp'][idac]))
            #         outdata[bl]['negAmp'][idac] = np.concatenate((outdata[bl]['negAmp'][idac], chipdata[bl]['data']['negAmp'][idac]))
            processed_data_df = pd.concat([processed_data_df, chipdata], axis=0)
            # break
    processed_data_df.reset_index(drop=True, inplace=True)
    # print(processed_data_df)
    # print(processed_data_df['item'].unique())
    # print(processed_data_df[processed_data_df['BL']=='SNC0']['item'].unique())
    # sys.exit()
    
    out_dict = {'testItem': [], 'CFG': [], 'BL': [], 'DAC': [], 'mean': [], 'std': []}
    BLs = ['SNC0', 'SNC1']
    # DACs = processed_data_df['DAC'].unique()
    # for ibl, bl in enumerate(outdata.keys()):
    for ibl, bl in enumerate(BLs):
        # bldata = outdata[bl]
        bldata = processed_data_df[processed_data_df['BL']==bl].copy().reset_index().drop('index', axis=1)
        CFGs = bldata['outputCFG'].unique()
        for cfg in CFGs:
            cfgdata = bldata[bldata['outputCFG']==cfg].copy().reset_index().drop('index', axis=1)
            DACs = cfgdata['DAC'].unique()
            # print(bldata.keys())
            # print(len(bldata['pedestal'][0]))
            # print(bldata['DAC'])
            # for idac, dac in enumerate(bldata['DAC']):
            for idac, dac in enumerate(DACs):
                dacdata = cfgdata[cfgdata['DAC']==dac].copy().reset_index().drop('index', axis=1)
                # print('-----------------DACDATA-----------------')
                pedestal = np.array(dacdata['pedestal'])
                posAmp = dacdata[dacdata['item']=='posAmp']['data']
                negAmp = []
                if bl=='SNC0':
                    negAmp = dacdata[dacdata['item']=='negAmp']['data']

                # pedestal
                pedmean = statistics.median(pedestal)
                pedstd = statistics.stdev(pedestal)
                pedmin, pedmax = pedmean-3*pedstd, pedmean+3*pedstd
                # posAmp
                posAmpmean = statistics.median(posAmp)
                posAmpstd = statistics.stdev(posAmp)
                posAmpmin, posAmpmax = posAmpmean-3*posAmpstd, posAmpmean+3*posAmpstd
                
                # negAmp
                negAmpmean, negAmpstd, negAmpstd, negAmpmin, negAmpmax = 0, 0, 0, 0, 0
                if bl=='SNC0':
                    if len(negAmp)==0:
                        print(dac, cfg)
                    negAmpmean = statistics.median(negAmp)
                    negAmpstd = statistics.stdev(negAmp)
                    negAmpmin, negAmpmax = negAmpmean-3*negAmpstd, negAmpmean+3*negAmpstd
                for _ in range(10):
                    # pedestal
                    posmin = np.where(pedestal < pedmin)[0]
                    posmax = np.where(pedestal > pedmax)[0]
                    pos = np.concatenate((posmin, posmax))
                    pedestal = np.delete(pedestal, pos)
                    pedmean = statistics.median(pedestal)
                    pedstd = statistics.stdev(pedestal)
                    pedmin, pedmax = pedmean-3*pedstd, pedmean+3*pedstd
                    # posAmp
                    posmin = np.where(posAmp < posAmpmin)[0]
                    posmax = np.where(posAmp > posAmpmax)[0]
                    pos = np.concatenate((posmin, posmax))
                    posAmp = np.delete(posAmp, pos)
                    posAmpmean = statistics.median(posAmp)
                    posAmpstd = statistics.stdev(posAmp)
                    posAmpmin, posAmpmax = posAmpmean-3*posAmpstd, posAmpmean+3*posAmpstd
                    # negAmp
                    if bl=='SNC0':
                        posmin = np.where(negAmp < negAmpmin)[0]
                        posmax = np.where(negAmp > negAmpmax)[0]
                        pos = np.concatenate((posmin, posmax))
                        negAmp = np.delete(negAmp, pos)
                        negAmpmean = statistics.median(negAmp)
                        negAmpstd = statistics.stdev(negAmp)
                        negAmpmin, negAmpmax = negAmpmean-3*negAmpstd, negAmpmean+3*negAmpstd
                if saveDist:
                    plot_distribution(array=pedestal, xtitle='pedestal', output_path_fig=output_path_fig, figname='_'.join([cali_item, 'pedestal', bl, str(dac)]))
                    plot_distribution(array=posAmp, xtitle='posAmp', output_path_fig=output_path_fig, figname='_'.join([cali_item, 'posAmp', bl, str(dac)]))
                    plot_distribution(array=negAmp, xtitle='negAmp', output_path_fig=output_path_fig, figname='_'.join([cali_item, 'negAmp', bl, str(dac)]))
                
                # pedestal
                out_dict['testItem'].append('pedestal')
                out_dict['CFG'].append(cfg)
                out_dict['BL'].append(bl)
                out_dict['DAC'].append(dac)
                out_dict['mean'].append(pedmean)
                out_dict['std'].append(pedstd)
                # posAmp
                out_dict['testItem'].append('posAmp')
                out_dict['CFG'].append(cfg)
                out_dict['BL'].append(bl)
                out_dict['DAC'].append(dac)
                out_dict['mean'].append(posAmpmean)
                out_dict['std'].append(posAmpstd)
                # negAmp
                out_dict['testItem'].append('negAmp')
                out_dict['CFG'].append(cfg)
                out_dict['BL'].append(bl)
                out_dict['DAC'].append(dac)
                out_dict['mean'].append(negAmpmean)
                out_dict['std'].append(negAmpstd)

    # for key in out_dict.keys():
    #     print(len(out_dict[key]))
    out_df = pd.DataFrame(out_dict).sort_values(by=['testItem', 'BL'])
    # print(out_df.head())
    out_df.to_csv('/'.join([output_path, cali_item + '.csv']))

    # Gain, INL, meangain, stdgain, meaninl, stdinl
    # testItems = []
    # BLs = []
    # means = []
    # stds = []
    # print(processed_data_df)
    # sys.exit()
    # processed_data = {'posAmp' : {'SNC0': {'INL': [], 'GAIN': [], 'minCharge (fC)': [], 'maxCharge (fC)': []}, 'SNC1': {'INL': [], 'GAIN': [], 'minCharge (fC)': [], 'maxCharge (fC)' : []}},
    #                 'negAmp' : {'SNC0': {'INL': [], 'GAIN': [], 'minCharge (fC)': [], 'maxCharge (fC)': []}, 'SNC1': {'INL': [], 'GAIN': [], 'minCharge (fC)': [], 'maxCharge (fC)' : []}}
    #                 }
    # processed_data_dict = {'BL': [], 'testItem': [], 'mean': [], 'std': []}
    # processed_data_dict = {'item': [], 'BL': [], 'gain (fC/ADC bit)': [], 'std gain (fC/ADC bit)': [], 'INL (%)': [], 'minCharge (fC)': [], 'maxCharge (fC)': []}
    processed_data_dict = {'item': [], 'CFG': [], 'BL': [], 'measItem': [], 'unit': [], 'mean': [], 'std' : []}
    # unit_gain = 'fC/ADC bit'
    unit = ''
    testItems = processed_data_df['item'].unique() # posAmp, negAmp
    # for keyItem in processed_data.keys():
    for keyItem in testItems:
        itemData = processed_data_df[processed_data_df['item']==keyItem].copy().reset_index().drop('index', axis=1)
        CFGs = itemData['outputCFG'].unique()
        for cfg in CFGs:
            cfgdata = itemData[itemData['outputCFG']==cfg].copy().reset_index().drop('index', axis=1)
            # itemData = processed_data[keyItem]
            BLs = cfgdata['BL'].unique() # SNC0, SNC1
            # for bl in itemData.keys():
            for bl in BLs:
                bldata = cfgdata[cfgdata['BL']==bl].copy().reset_index().drop('index', axis=1)
                # bldata = itemData[bl]
                item_to_process = ['INL', 'GAIN', 'linRange']
                # for key, val in bldata.items():
                for key in item_to_process:
                    val = bldata[key]
                    median, std = statistics.median(val), statistics.stdev(val)
                    xmin, xmax = median - 3*std, median+3*std
                    for _ in range(10):
                        posmin = np.where(val<xmin)[0]
                        posmax = np.where(val>xmax)[0]
                        pos = np.concatenate((posmin, posmax))
                        val = np.delete(val, pos)
                        median, std = statistics.median(val), statistics.stdev(val)
                        xmin, xmax = median - 3*std, median+3*std
                    if saveDist:
                        plot_distribution(array=d, xtitle='{} {} {}'.format(keyItem, bl, key), output_path_fig=output_path_fig, figname='_'.join([cali_item, keyItem, bl, key]))
                    outKEY = ''
                    processed_data_dict['item'].append(keyItem)
                    processed_data_dict['BL'].append(bl)
                    if key=='INL':
                        unit = '%'
                        outKEY = key
                        # processed_data_dict[outKEY].append(np.round(median*100, 4))
                    elif key=='GAIN':
                        outKEY = 'gain'
                        unit = 'fC/ADC bit'
                        # processed_data_dict[outKEY].append(np.round(median, 4))
                        # processed_data_dict['std {}'.format(outKEY)].append(np.round(std, 4))
                    else:
                        outKEY = key
                        unit = 'fC'
                        # processed_data_dict[outKEY].append(np.round(median, 4))
                    processed_data_dict['measItem'].append(outKEY)
                    processed_data_dict['CFG'].append(cfg)
                    if key=='INL':
                        processed_data_dict['mean'].append(np.round(median*100, 4))
                        processed_data_dict['std'].append(np.round(std, 4))
                        processed_data_dict['unit'].append(unit)
                    else:
                        processed_data_dict['mean'].append(np.round(median, 4))
                        processed_data_dict['std'].append(np.round(std, 4))
                        processed_data_dict['unit'].append(unit)

    processed_data_df = pd.DataFrame(processed_data_dict)
    processed_data_df.to_csv('/'.join([output_path, cali_item + '_GAIN_INL.csv']), index=False)

if __name__ == '__main__':
    root_path = "E:/B009T0008/"
    output_path = root_path + "Ana"
    data_dir = "Time_20250527114445_DUT_0000_1001_2002_3003_4004_5005_6006_7007"
    env = 'RT'

    asicdac = QC_CALI(root_path=root_path, data_dir=data_dir, output_path=output_path, env=env, tms=61, QC_filename='QC_CALI_ASICDAC.bin', generateWf=False)
    asicdac.runASICDAC_cali(saveWfData=False)
    tmpdir = os.listdir('/'.join([root_path, data_dir]))[0]
    if 'QC_CALI_ASICDAC_47.bin' in os.listdir('/'.join([root_path, data_dir, tmpdir])):
        asic47dac = QC_CALI(root_path=root_path, data_dir=data_dir, output_path=output_path, env=env, tms=64, QC_filename='QC_CALI_ASICDAC_47.bin', generateWf=False)
        asic47dac.runASICDAC_cali(saveWfData=False)
    datdac = QC_CALI(root_path=root_path, data_dir=data_dir, output_path=output_path, env=env, tms=62, QC_filename='QC_CALI_DATDAC.bin', generateWf=False)
    datdac.runASICDAC_cali(saveWfData=False)
    direct_cali = QC_CALI(root_path=root_path, data_dir=data_dir, output_path=output_path, env=env, tms=63, QC_filename='QC_CALI_DIRECT.bin', generateWf=False)
    direct_cali.runASICDAC_cali(saveWfData=False)
    # root_path = '../../Data_BNL_CE_WIB_SW_QC'
    # output_path = '../../Analyzed_BNL_CE_WIB_SW_QC'

    # # # list_data_dir = [dir for dir in os.listdir(root_path) if '.zip' not in dir]
    # root_path = '../../B010T0004'
    # list_data_dir = [dir for dir in os.listdir(root_path) if (os.path.isdir('/'.join([root_path, dir]))) and (dir!='images')]
    # for i, data_dir in enumerate(list_data_dir):
    #     # if '20240703163752' in data_dir:
    #         asicdac = QC_CALI(root_path=root_path, data_dir=data_dir, output_path=output_path, tms=61, QC_filename='QC_CALI_DATDAC.bin', generateWf=True)
    #         asicdac.runASICDAC_cali(saveWfData=False)
    #         subdir = os.listdir('/'.join([root_path, data_dir]))[0]
    #         if 'QC_CALI_ASICDAC_47.bin' in os.listdir('/'.join([root_path, data_dir, subdir])):
    #             asic47dac = QC_CALI(root_path=root_path, data_dir=data_dir, output_path=output_path, tms=64, QC_filename='QC_CALI_ASICDAC_47.bin', generateWf=True)
    #             asic47dac.runASICDAC_cali(saveWfData=False)
    #         datdac = QC_CALI(root_path=root_path, data_dir=data_dir, output_path=output_path, tms=62, QC_filename='QC_CALI_DATDAC.bin', generateWf=True)
    #         datdac.runASICDAC_cali(saveWfData=False)
    #         direct_cali = QC_CALI(root_path=root_path, data_dir=data_dir, output_path=output_path, tms=63, QC_filename='QC_CALI_DIRECT.bin', generateWf=True)
    #         direct_cali.runASICDAC_cali(saveWfData=False)
    # root_path = '../../Analyzed_BNL_CE_WIB_SW_QC'
    # output_path = '../../Analysis'
    #root_path = '../../out_B010T0004_'
    #output_path = '../../analyzed_B010T0004_'
    #list_chipID = os.listdir(root_path)
    ## calib_item = ['QC_CALI_ASICDAC', 'QC_CALI_ASICDAC_47', 'QC_CALI_DATDAC', 'QC_CALI_DIRECT'] #'QC_CALI_ASICDAC']#
    #calib_item = ['QC_CALI_ASICDAC']
    ## for chipID in list_chipID:
    ##     # calib_item = ['QC_CALI_ASICDAC', 'QC_CALI_ASICDAC_47', 'QC_CALI_DATDAC', 'QC_CALI_DIRECT']
    ##     for cali_item in calib_item:
    ##         ana_cali = QC_CALI_Ana(root_path=root_path, output_path=output_path, chipID=chipID, CALI_item=cali_item)
    ##         ana_cali.run_Ana(generatePlots=False, path_to_statAna='/'.join([output_path, '{}_GAIN_INL.csv'.format(cali_item)]))
    ##         sys.exit()
    #for cali_item in calib_item:
    #    StatAna_cali(root_path=root_path, output_path=output_path, cali_item=cali_item, saveDist=False)
