############################################################################################
#   created on 7/2/2024 @ 13:52
#   email: radofanantenan.razakamiandra@stonybrook.edu
#   Analyze the calibration data: QC_Cap_Meas.bin
############################################################################################

import os, sys, csv
import numpy as np
import pandas as pd
from utils import printItem, createDirs, dumpJson, linear_fit, LArASIC_ana, decodeRawData, BaseClass #, getMaxAmpIndices, getMinAmpIndices, getPulse
import matplotlib.pyplot as plt
from utils import BaseClass_Ana
from scipy.stats import norm

class QC_Cap_Meas(BaseClass):
    def __init__(self, root_path: str, data_dir: str, output_path: str, generateWf_plot=False, env='RT'):
        printItem("Capacitance measurement")
        self.generateWf_plot = generateWf_plot
        super().__init__(root_path=root_path, data_dir=data_dir, output_path=output_path, tms=8, QC_filename="QC_Cap_Meas.bin", generateWaveForm=self.generateWf_plot, env=env)
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
                        if self.generateWf_plot:
                            self.saveWaveform(wf_data=wf, FE_ID=FE_ID, chn=fechn, V=bl, cali_input=c)
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
            # ratio = Cref/Ccali
            # print(ratio)
            # print(chn_cali)
            # sys.exit()
            # print(np.argmax(vref), vref[np.argmax(vref)])
            ##
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
    
    def plotRatioCap(self):
        plt.figure()
        plt.plot(self.ratioCap, '--.', markersize=12)
        plt.xlabel('CH')
        plt.ylabel('Capacitance (pF)')
        plt.ylim([0.0, 1.5])
        plt.grid(True)
        # plt.show()
        # sys.exit()
        plt.savefig('/'.join([self.output_path, self.item + '_' + self.chipID + '.png']))
        plt.close()

    def run_Ana(self, path_to_stat=None, generatePlots=False):
        if generatePlots:
            self.plotRatioCap()

        stat_ana_df = None
        if path_to_stat is not None:
            stat_ana_df = pd.read_csv(path_to_stat)
            # print(stat_ana_df['gain'])
            # print(stat_ana_df.columns)

        Cap_df = self.getRatioCapacitance(returnDF=True)
        combined_df = pd.DataFrame({
            'item': [stat_ana_df.iloc[0]['item'] if stat_ana_df is not None else None for _ in range(16)],
            'BL': [stat_ana_df.iloc[0]['BL'] if stat_ana_df is not None else Cap_df.iloc[0]['BL'] for _ in range(16)],
            'peakTime': [stat_ana_df.iloc[0]['peakTime'] if stat_ana_df is not None else Cap_df.iloc[0]['peakTime'] for _ in range(16)],
            'gain': [stat_ana_df.iloc[0]['gain'] if stat_ana_df is not None else Cap_df.iloc[0]['gain'] for _ in range(16)],
            'meanCap (pF)': [stat_ana_df.iloc[0]['meanCap (pF)'] if stat_ana_df is not None else None for _ in range(16)],
            'stdCap (pF)': [stat_ana_df.iloc[0]['stdCap (pF)'] if stat_ana_df is not None else None for _ in range(16)],
            'Cap (pF)': Cap_df['Cap'],
            'CH': Cap_df['CH']
        })
        # print(Cap_df)
        # print(combined_df)
        # print(combined_df.columns)

        if stat_ana_df is not None:
            combined_df['QC_result'] = (
                (combined_df['Cap (pF)'] >= (combined_df['meanCap (pF)'] - 3 * combined_df['stdCap (pF)'])) &
                (combined_df['Cap (pF)'] <= (combined_df['meanCap (pF)'] + 3 * combined_df['stdCap (pF)']))
            )
        else:
            combined_df['QC_result'] = None

        # print(combined_df)
        combined_df.drop(['meanCap (pF)', 'stdCap (pF)'], axis=1, inplace=True, errors='ignore')
        # print(combined_df)
        #combined_df.to_csv('/'.join([self.output_path, self.chipID,self.item + '.csv']), index=False)

        # combined_df, which is the result of the QC, row
        qc_result = None
        # if (stat_ana_df is not None) and (False in combined_df['QC_result']):
        #     qc_result = 'FAILED'
        # else:
        #     qc_result = 'PASSED'
        if stat_ana_df is not None:
            qc_result = 'FAILED' if False in combined_df[f'QC_result'] else 'PASSED'

        # print(combined_df.iloc[0][['BL', 'peakTime', 'gain']])
        cfg = '_'.join(combined_df.iloc[0][['BL', 'peakTime', 'gain']].dropna())
        #if qc_result is not None:
        #    row_data = ['Test_{}_Capacitance'.format(self.tms), cfg, qc_result]
        #else:
        row_data = ['Test_{}_Capacitance'.format(self.tms), cfg]
        for chn in combined_df['CH']:
            row_data.append('CH{}=(Cap (pF)={})'.format(chn, combined_df.iloc[chn]['Cap (pF)']))

        #return row_data
        row_data = [row_data]
        with open('/'.join([self.output_path, self.chipID, '{}.csv'.format(self.item)]), 'w') as csvfile:
            csv.writer(csvfile, delimiter=',').writerows(row_data)    

    
    def run_Ana_withStat(self, path_to_stat='', generatePlots=False):
        if generatePlots:
            self.plotRatioCap
        stat_ana_df = pd.read_csv(path_to_stat)
        print(stat_ana_df['gain'])
        print(stat_ana_df.columns)
        
        Cap_df = self.getRatioCapacitance(returnDF=True)
        combined_df = pd.DataFrame({
            'item': [stat_ana_df.iloc[0]['item'] for _ in range(16)],
            'BL' : [stat_ana_df.iloc[0]['BL'] for _ in range(16)],
            'peakTime': [stat_ana_df.iloc[0]['peakTime'] for _ in range(16)],
            'gain' : [stat_ana_df.iloc[0]['gain'] for _ in range(16)],
            'meanCap (pF)': [stat_ana_df.iloc[0]['meanCap (pF)'] for _ in range(16)],
            'stdCap (pF)': [stat_ana_df.iloc[0]['stdCap (pF)'] for _ in range(16)],
            'Cap (pF)': Cap_df['Cap'],
            'CH': Cap_df['CH']
        })
        print(combined_df)
        print(combined_df.columns)
        combined_df['QC_result']= (combined_df['Cap (pF)']>= (combined_df['meanCap (pF)']-3*combined_df['stdCap (pF)'])) & (combined_df['Cap (pF)'] <= (combined_df['meanCap (pF)']+3*combined_df['stdCap (pF)']))
        print(combined_df)
        combined_df.drop(['meanCap (pF)', 'stdCap (pF)'], axis=1, inplace=True)
        print(combined_df)
        combined_df.to_csv('/'.join([self.output_path, self.item+'.csv']),index=False)
        #
        # combined_df, which is the result of the QC, row
        qc_result = 'PASSED'
        if False in combined_df['QC_result']:
            qc_result = 'FAILED'
        cfg = '_'.join(combined_df.iloc[0][['BL', 'peakTime','gain']])
        row_data = ['Test_{}_Capacitance'.format(self.tms), cfg, qc_result]
        for chn in combined_df['CH']:
            row_data.append('CH{}=(Cap (pF)={})'.format(chn, combined_df.iloc[chn]['Cap (pF)']))
        print(row_data)
        return row_data
        
def Cap_stat_ana(root_path: str, list_chipID: list, output_path: str, savefig=False):
    ############################# QUESTION RELATED TO THIS #####################
    # Do we want to save the mean, std in a separate csv file ?
    # as far as I know, we only have one configuration for this measurement so
    # so the csv file will be extremely small in size
    # --> Probably the answer to this is yes, we want to save these information 
    # in a csv file no matter the size
    ############################################################################
    ratio_caps = np.array([])
    config = dict()
    firstData = True
    for chipID in list_chipID:
        cap = QC_Cap_Meas_Ana(root_path=root_path, output_path=output_path, chipID=chipID)
        if cap.ERROR:
            continue
        tmpratiocap = cap.getRatioCapacitance()
        if savefig:
            cap.plotRatioCap()
        if firstData:
            ratio_caps = tmpratiocap
            config = cap.config
            firstData = False
        else:
            ratio_caps = np.concatenate((ratio_caps, tmpratiocap))
        # cap.plotRatioCap()
    x = np.linspace(np.min(ratio_caps), np.max(ratio_caps), len(ratio_caps))
    mean, std = np.median(ratio_caps), np.std(ratio_caps)
    p = norm.pdf(x, mean, std)
    plt.figure()
    plt.hist(ratio_caps, bins=100, density=True, label='mean = {}, std = {}'.format(np.round(mean,4), np.round(std,4)))
    plt.plot(x, p)
    plt.xlabel('Capacitance (pF)');plt.ylabel('#')
    plt.legend()
    # plt.show()
    plt.savefig('/'.join([output_path, 'fig', 'QC_Cap_Meas.png']))
    plt.close()
    #
    # save Config, Mean, and std in csv file
    config['meanCap'] = np.round(mean, 4)
    config['stdCap'] = np.round(std, 4)
    # print(config)
    df = pd.DataFrame({'item': ['Capacitance'], 'BL': [config['BL']], 'peakTime': [config['peakTime']], 'gain': [config['gain']],
                 'meanCap (pF)': [config['meanCap']], 'stdCap (pF)': [config['stdCap']]})
    df.to_csv('/'.join([output_path, 'QC_Cap_Meas.csv']), index=False)
    # print(ratio_caps)

if __name__ == '__main__':
    # root_path = '../../Data_BNL_CE_WIB_SW_QC'
    # root_path = '../../B010T0004/Time_20240703122319_DUT_0000_1001_2002_3003_4004_5005_6006_7007/'
    # output_path = '../../Analyzed_BNL_CE_WIB_SW_QC'
    # output_path = '../../Analyzed_for_capmeas'
    # root_path = '../../B010T0004'
    # list_data_dir = [dir for dir in os.listdir(root_path) if (os.path.isdir('/'.join([root_path, dir]))) and (dir!='images')]
    # # list_data_dir = [dir for dir in os.listdir(root_path) if '.zip' not in dir]
    # for i, data_dir in enumerate(list_data_dir):
    #     # if i==1:
    #         print(data_dir)
    #         cap = QC_Cap_Meas(root_path=root_path, data_dir=data_dir, output_path=output_path, generateWf_plot=True)
    #         decodedData = cap.decode()
    #         cap.saveData(decodedData=decodedData)
    #         # sys.exit()
    # root_path = '../../Analyzed_BNL_CE_WIB_SW_QC'
    # output_path = '../../Analysis'
    #root_path = '../../out_B010T0004_'
    #output_path = '../../analyzed_B010T0004_'
    #list_chipID = os.listdir(root_path)
    root_path = "E:/B009T0008/"
    output_path = root_path + "Ana"
    data_dir = "Time_20250527114445_DUT_0000_1001_2002_3003_4004_5005_6006_7007"
    env = 'RT'
    # for chipID in list_chipID:
    #     m = QC_Cap_Meas_Ana(root_path=root_path, output_path=output_path, chipID=chipID)
    #     m.run_Ana(path_to_stat='/'.join([output_path, 'QC_Cap_Meas.csv']))
    #     sys.exit()
    #Cap_stat_ana(root_path=root_path, output_path=output_path, list_chipID=list_chipID)
    cap = QC_Cap_Meas(root_path=root_path, data_dir=data_dir, output_path=output_path, env=env, generateWf_plot=False)
    cap.decode_CapMeas()
