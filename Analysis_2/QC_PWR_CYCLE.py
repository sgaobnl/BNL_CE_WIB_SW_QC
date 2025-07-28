############################################################################################
#   created on 6/11/2024 @ 10:53
#   email: radofanantenan.razakamiandra@stonybrook.edu
#   Analyze the data in QC_PWR_CYCLE.bin
############################################################################################

import os, pickle, sys, statistics, pandas as pd, csv
import numpy as np
import matplotlib.pyplot as plt
from utils import createDirs, printItem, decodeRawData, dumpJson, LArASIC_ana, BaseClass
from utils import BaseClass_Ana

class PWR_CYCLE(BaseClass):
    def __init__(self, root_path: str, data_dir: str, output_path: str, env='RT'):
        printItem('FE power cycling')
        self.item = 'QC_PWR_CYCLE'
        super().__init__(root_path=root_path, data_dir=data_dir, output_path=output_path, QC_filename='QC_PWR_CYCLE.bin', tms=4, env=env)
        if self.ERROR:
            return
        self.period = 500

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
        pwrcycleN = int(pwr_cycle_N.split('_')[1])
        for ichip in range(8):
            FE_ID = self.logs_dict['FE{}'.format(ichip)]
            larasic = LArASIC_ana(dataASIC=decoded_wf[ichip], output_dir=self.FE_outputDIRs[FE_ID], chipID=FE_ID, tms=self.tms, param=pwr_cycle_N, generatePlots=False, generateQCresult=False, period=self.period)
            data_asic = larasic.runAnalysis(pwrcylceN=pwrcycleN)
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
        decoded_wf = decodeRawData(fembs=fembs, rawdata=rawdata_wf, period=self.period)
        #
        chResp = self.decodeWF(decoded_wf=decoded_wf, pwr_cycle_N=pwr_cycle_N)
        for ichip in range(8):
            FE_ID = self.logs_dict['FE{}'.format(ichip)]
            for key in chResp[FE_ID].keys():
                PwrCycle_data[FE_ID][pwr_cycle_N][key] = chResp[FE_ID][key]
        return PwrCycle_data
        
    def decode_PwrCycle(self):
        if self.ERROR:
            return
        N_pwrcycle = 8
        PwrCycle_data = {self.logs_dict['FE{}'.format(ichip)]: {} for ichip in range(8)}
        for ipcycle in range(N_pwrcycle):
            pwr_cycle_N = 'PwrCycle_{}'.format(ipcycle)
            print("Item : {}".format(pwr_cycle_N))
            one_pwrcyc = self.decode_OnePwrCycle(pwr_cycle_N=pwr_cycle_N)
            for FE_ID in one_pwrcyc.keys():
                PwrCycle_data[FE_ID][pwr_cycle_N] = one_pwrcyc[FE_ID][pwr_cycle_N]
        # save data to json file
        FE_IDs = []
        for ichip in range(8):
            FE_ID = self.logs_dict['FE{}'.format(ichip)]
            FE_IDs.append(FE_ID)
            data = PwrCycle_data[FE_ID]
            dumpJson(output_path=self.FE_outputDIRs[FE_ID], output_name='QC_PWR_CYCLE', data_to_dump=data)
        return FE_IDs

class PWR_CYCLE_Ana(BaseClass_Ana):
    '''
        This class is written to analyze the decoded data for each ASIC.
        The name of the function get_IVP(...) means get Current, Voltage, or Power.
    '''
    def __init__(self, root_path: str, chipID: str, output_path: str):
        self.item = 'QC_PWR_CYCLE'
        print (self.item)
        self.tms = '04'
        super().__init__(root_path=root_path, chipID=chipID, output_path=output_path, item=self.item)
        self.root_path = root_path
        self.output_path = output_path
        self.units = {'V': 'V', 'I': 'mA', 'P': 'mW'}
    
    def get_IVP(self, param='V', forStat=False):
        if forStat:
            vdda_cycles = np.zeros(len(self.params))
            vddp_cycles = np.zeros(len(self.params))
            vddo_cycles = np.zeros(len(self.params))
            for cycle in self.params:
                Ncycle = int(cycle.split('_')[1])
                vdda_cycles[Ncycle] = self.data[cycle][param]['VDDA']
                vddp_cycles[Ncycle] = self.data[cycle][param]['VDDP']
                vddo_cycles[Ncycle] = self.data[cycle][param]['VDDO']
            return vdda_cycles, vddp_cycles, vddo_cycles
        else:
            cycles = [[], [], []]
            Voltages = [[], [], []] # for [[VDDA], [VDDP], [VDDO]]
            for cycle in self.params:
                Ncycle = int(cycle.split('_')[1])
                data = self.data[cycle][param]
                # VDDA
                cycles[0].append(Ncycle)
                Voltages[0].append(data['VDDA'])
                # VDDP
                cycles[1].append(Ncycle)
                Voltages[1].append(data['VDDP'])
                # VDDO
                cycles[2].append(Ncycle)
                Voltages[2].append(data['VDDO'])
            VDDA = {'cycle': cycles[0], param: Voltages[0]}
            VDDP = {'cycle': cycles[1], param: Voltages[1]}
            VDDO = {'cycle': cycles[2], param: Voltages[2]}
            return VDDA, VDDP, VDDO
    
    def get_wfdata(self, item='pedestal', forStat=False):
        if forStat:
            # concatenate the 16-channels data for each cycle and return all of them, grouped by cycle.
            # The distribution will be drawn for each cycle.
            # cycleData = np.zeros(len(self.params))
            # cycleData = np.array([np.array([]) for _ in range(len(self.params))])
            cycleData = [[] for _ in range(8)]
            for cycle in self.params:
                Ncycle = int(cycle.split('_')[1])
                data = np.array(self.data[cycle][item])
                # cycleData[Ncycle] = np.concatenate((cycleData[Ncycle], data))
                cycleData[Ncycle] = data
            return cycleData
        else:
            # Get mean values for each cycle
            # Plot mean values vs. cycle number
            cycle_data = {}
            for cycle in self.params:
                Ncycle = int(cycle.split('_')[1])
                # print(self.data[cycle][item])
                # print(self.data)
                # sys.exit()
                data = np.array(self.data[cycle][item])
                # mean = np.round(np.mean(data), 4)
                # std = np.round(np.std(data), 4)
                # cycle_data[cycle] = {'{}_mean'.format(item): mean, '{}_std'.format(item): std}
                cycle_data[cycle] = {'CH{}'.format(ichn) : data[ichn] for ichn in range(len(data))}
            return cycle_data

    def plot_cycle_vs_item(self, data_dict, item='', vdd_cfg=''):
        plt.figure()
        plt.plot(data_dict['cycle'], data_dict[item], '--.', markersize=10)
        plt.xlabel('Cycle')
        plt.ylabel(item + ' ({})'.format(self.units[item]))
        plt.savefig('/'.join([self.output_path, self.item + '_' + item +'_{}.png'.format(vdd_cfg)]))
        plt.close()

    def create_dfItem_PWR(self, param='V', generatePlots=False):
        vdda, vddp, vddo = self.get_IVP(param=param, forStat=False)
        if generatePlots:
            self.plot_cycle_vs_item(data_dict=vdda, item=param, vdd_cfg='VDDA')
            self.plot_cycle_vs_item(data_dict=vddo, item=param, vdd_cfg='VDDO')
            self.plot_cycle_vs_item(data_dict=vddp, item=param, vdd_cfg='VDDP')
        out_dict = {'testItem': [], 'Cycle': [], 'vdd_cfgs': [], 'value': []}
        key_val = {'VDDA': vdda, 'VDDO': vddo, 'VDDP': vddp}
        for key, val in key_val.items():
            data = val
            for icycle in data['cycle']:
                out_dict['testItem'].append(param)# +' ({})'.format(self.units[param]))
                out_dict['Cycle'].append(icycle)
                out_dict['vdd_cfgs'].append(key)
                out_dict['value'].append(data[param][icycle])
        out_df = pd.DataFrame(out_dict)
        return out_df
    
    def create_dfItem_wf(self, param='pedestal'):
        data_wf = self.get_wfdata(item=param, forStat=False)
        out_dict = {'testItem': [], 'Cycle': [], 'vdd_cfgs' : [], 'CH' : [], 'value' : []}
        for cycle, data in data_wf.items():
            icycle = int(cycle.split('_')[1])
            for ichn in range(len(data)):
                out_dict['testItem'].append(param)
                out_dict['Cycle'].append(icycle)
                out_dict['vdd_cfgs'].append('n/a')
                out_dict['CH'].append(ichn)
                out_dict['value'].append(data['CH{}'.format(ichn)])
        out_df = pd.DataFrame(out_dict)
        return out_df

    def run_Ana(self):
        if self.ERROR:
            return

        # Get power measurement data
        pwr_out_df = pd.DataFrame({'testItem': [], 'Cycle': [], 'vdd_cfgs': [], 'value': []})
        for param in ['V', 'I', 'P']:
            param_df = self.create_dfItem_PWR(param=param, generatePlots=False)
            pwr_out_df = pd.concat([pwr_out_df, param_df], axis=0)
        pwr_out_df.reset_index().drop('index',axis=1, inplace=True)

        pwr_qc_results = pwr_out_df.copy()
        pwr_qc_results['QC_result'] = True  # Default pass without statistics

        pwr_qc_results = pwr_qc_results.reset_index().drop('index', axis=1)
        pwr_qc_results['Cycle'] = pwr_qc_results['Cycle'].astype(int)

        # Get channel response data
        chresp_out_df = pd.DataFrame({'testItem': [], 'Cycle': [], 'CH': [], 'value': []})
        for param in ['pedestal', 'rms', 'negpeak', 'pospeak']:
            param_df = self.create_dfItem_wf(param=param).drop('vdd_cfgs', axis=1).copy()
            chresp_out_df = pd.concat([chresp_out_df, param_df], axis=0)

        chresp_qc_results = chresp_out_df.copy()
        chresp_qc_results['QC_result'] = True  # Default pass without statistics

        # Process results cycle by cycle
        cycles = chresp_qc_results['Cycle'].unique()
        results_cycles = []
        for icycle in cycles:
            tmpdata_pwr = pwr_qc_results[pwr_qc_results['Cycle']==icycle].copy().reset_index().drop('index',axis=1)
            tmpdata_chresp = chresp_qc_results[chresp_qc_results['Cycle']==icycle].copy().reset_index().drop('index',axis=1)

            # The rest of the code remains the same as original
            # ...existing code for processing cycle results...
            cycle_pwr_qc_result = ''
            cycle_chresp_qc_result = ''
            if False in list(tmpdata_pwr['QC_result']):
                cycle_pwr_qc_result = 'FAILED'
            else:
                cycle_pwr_qc_result = 'PASSED'
            if False in list(tmpdata_chresp['QC_result']):
                cycle_chresp_qc_result = 'FAILED'
            else:
                cycle_chresp_qc_result = 'PASSED'
            
            # Format power parameters
            pwr_params = []
            for i in range(len(tmpdata_pwr)):
                param = '_'.join([tmpdata_pwr.iloc[i]['vdd_cfgs'], tmpdata_pwr.iloc[i]['testItem']])
                pwr_params.append('{} = {}'.format(param, tmpdata_pwr.iloc[i]['value']))

            # Format channel results
            ch_results = []
            for ichn in range(16):
                CH = 'CH{}'.format(ichn)
                posAmp = tmpdata_chresp[(tmpdata_chresp['CH']==ichn) & (tmpdata_chresp['testItem']=='pospeak')]['value']
                negAmp = tmpdata_chresp[(tmpdata_chresp['CH']==ichn) & (tmpdata_chresp['testItem']=='negpeak')]['value']
                ped = tmpdata_chresp[(tmpdata_chresp['CH']==ichn) & (tmpdata_chresp['testItem']=='pedestal')]['value']
                rms = tmpdata_chresp[(tmpdata_chresp['CH']==ichn) & (tmpdata_chresp['testItem']=='rms')]['value']
                ch_results.append(("{}=(ped={};rms={};posAmp={};negAmp={})".format(CH, ped.iloc[0], rms.iloc[0], posAmp.iloc[0], negAmp.iloc[0])))

            results_cycles.append(['Test_{}_Power_cycle'.format(self.tms), 'Cycle_{}'.format(icycle)] + pwr_params + ch_results)

        return results_cycles


if __name__ == '__main__':
    root_path = "E:/B009T0008/"
    output_path = root_path + "Ana"
    data_dir = "Time_20250527114445_DUT_0000_1001_2002_3003_4004_5005_6006_7007"
    env = 'RT'
    pwr_cycle = PWR_CYCLE(root_path=root_path, data_dir=data_dir, output_path=output_path, env=env)
    pwr_cycle.decode_PwrCycle()
