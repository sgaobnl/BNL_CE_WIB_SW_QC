############################################################################################
#   created on 6/12/2024 @ 11:32
#   email: radofanantenan.razakamiandra@stonybrook.edu
#   Analyze the calibration data: QC_CALI_ASICDAC.bin, QC_CALI_DATDAC.bin, and QC_CALI_DIRECT.bin
############################################################################################

import os, pickle, sys, statistics, pandas as pd, csv
import numpy as np
from utils import printItem, createDirs, dumpJson, linear_fit, LArASIC_ana, decodeRawData, BaseClass #, getPulse
from scipy.signal import find_peaks
from utils import BaseClass_Ana, gain_inl
from scipy.stats import norm

class QC_CALI(BaseClass):
#    '''
#        Using the 6-bit DAC embedded on the chip to perform the calibration;
#        LArASIC gain: 14mV/fC, peak time: 2$\mu$s
#        INFO from QC_top:
#            - cali_mode=2,
#            - asicdac=0,
#            - period = 512,
#            - width = 384
#            if snc==0: maxdac = 32
#            else: maxdac = 64
#            - num_samples = 5
#            - filename: QC_CALI_ASICDAC.bin
#    '''
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
        super().__init__(root_path=root_path, data_dir=data_dir, output_path=output_path, tms=tms, QC_filename=QC_filename, env=env)
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
        return cfg

    def avgWf(self, data: list, param='ASIC', getWaveforms=False):
        newdata = []
        for ichip in range(len(data)):
            ASIC_ID = self.logs_dict['FE{}'.format(ichip)]
            larasic = LArASIC_ana(dataASIC=data[ichip], output_dir=self.FE_outputDIRs[ASIC_ID], chipID=ASIC_ID, tms=self.tms, param=param, generateQCresult=False,  period=self.period)
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
            amplitudes[FE_ID] = {}
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
        FE_IDs = []
        for ichip in range(8):
            FE_ID = self.logs_dict['FE{}'.format(ichip)]
            FE_IDs.append(FE_ID)
            print('Save amplitudes of {} ...'.format(FE_ID))
            dumpJson(output_path=self.FE_outputDIRs[FE_ID], output_name='QC_CALI_{}'.format(self.suffixName), data_to_dump=amplitudes[FE_ID], indent=4)
        return FE_IDs
        

    def runASICDAC_cali(self, saveWfData=False):
        if self.ERROR:
            return
        organizedData = self.organizeData(saveWaveformData=saveWfData)
        FE_IDs = self.getAmplitudes(organizedData=organizedData)
        return FE_IDs

#@ Analysis of the decoded data
class QC_CALI_Ana(BaseClass_Ana):
    def __init__(self, root_path: str, output_path: str, chipID: str, CALI_item: str):
        self.item = CALI_item 
        print (self.item)
        super().__init__(root_path=root_path, chipID=chipID, output_path=output_path, item=CALI_item)
        self.root_path = root_path
        self.output_path = output_path
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
        
    def getINL(self, BL: str, item: str, returnGain=False):
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
                #print(self.item, '------------', item, BL)
                slope, yintercept, inl, linRange = gain_inl(y=chdf['DAC'], x=chdf['data'], item=self.item)

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
    
    def getItem_forStatAna(self):
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
                BL_INL_posAmp = self.getINL(BL=BL, item=item, returnGain=True)
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

    def run_Ana(self ):
        if self.ERROR:
            return

        items = ['posAmp', 'negAmp']
        BLs = ['SNC0', 'SNC1']
        BL_dict = {'SNC0': '900mV', 'SNC1' : '200mV'}
        out_dict = {'item': [], 'CFG': [], 'BL': [], 'ch': [], 'gain (fC/ADC bit)': [], 'worstINL (%)': [], 'linRange (fC)': []}

        # Original data processing code remains unchanged
        for item in items:
            for BL in BLs:
                isNegAmp_200BL = (item=='negAmp') & (BL=='SNC1')
                if not isNegAmp_200BL:
                    outINL = self.getINL(BL=BL, item=item, returnGain=True)
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

        final_df =  out_df

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
                    
                    # Just add configuration info without QC result
                    __BL = '900mV' if BL=='SNC0' else '200mV'
                    result_Amp_cfg.append('_'.join([__BL, item, cfg]))

                    for ich, ch in enumerate(cfg_df['ch']):
                        gain = cfg_df.iloc[ich]['gain (fC/ADC bit)']
                        worstINL = cfg_df.iloc[ich]['worstINL (%)']
                        linRange = cfg_df.iloc[ich]['linRange (fC)']
                        result_Amp_cfg.append("CH{}=(worstINL={};gain={};linRangeCharge={})".format(ch, worstINL, gain, linRange))
                    result_in_list.append(result_Amp_cfg)

        return result_in_list
    

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
