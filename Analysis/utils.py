############################################################################################
#   created on 5/3/2024 @ 14:38
#   email: radofanantenan.razakamiandra@stonybrook.edu
#   Utility functions and classes needed for the decoding and analysis
############################################################################################

import os, sys, json, platform, pickle
import numpy as np
# import csv
import json
import matplotlib.pyplot as plt
import statsmodels.api as sm

#_________Import the CPP module_____________
system_info = platform.system()
if system_info=='Linux':
    # print('IN')
    sys.path.append('./decode')
    from dunedaq_decode import wib_dec
    sys.path.append('../')
elif system_info=='Windows':
    sys.path.append('../build')
    from dunedaq_decode import wib_dec
    sys.path.append('../Analysis')
#______________xx______xx__________________

def printTestItems(testItems: dict):
    '''
        Print the list of items to analyze.
        Input: a dictionary of the form {i: item}
    '''
    for i, elt in testItems:
        print("{} : {}".format(i, elt))

def printItem(item: str):
    '''
        Print one item.
    '''
    print('--'*20)
    print('\t*',' '*2,'{}'.format(item),' '*2,'*')
    print('--'*20)

def dumpJson(output_path: str, output_name: str, data_to_dump: dict, indent=4):
    '''
        Save data to json.
        inputs:
            output_path: path to the output
            output_name: filename WITHOUT the extension .json
            data_to_dump: a dictionary of the data to save
    '''
    with open('/'.join([output_path, output_name + '.json']), 'w+', encoding='utf-8') as fn:
        if indent>=0:
            json.dump(data_to_dump, fn, indent=indent)
        else:
            json.dump(data_to_dump, fn)
        

def dumpMD(output_path: str, output_name: str, mdTable_to_dump: str):
    '''
        Save markdown table to *.md file.
        inputs:
            output_path: path to output,
            output_name: filename WITHOUT the extension .md,
            mdTable_to_dump: a string of the markdown table to save
    '''
    with open('/'.join([output_path, output_name + '.md']), 'w+') as mdfile:
        mdfile.write(mdTable_to_dump)

def linear_fit(x: list, y: list):
    '''
        Perform a linear fit on y = f(x) using numpy.polyfit degree 1.
        inputs: x and y
        outputs: slope, yintercept, peakinl
    '''
    # fit = np.polyfit(x, y, 1)
    # slope, yintercept = fit[0], fit[1]
    fit = sm.OLS(y, sm.add_constant(x)).fit()
    slope = fit.params[1]
    yintercept = fit.params[0]
    y_fit = np.array(x) * slope + yintercept
    delta_y = np.abs(np.array(y) - y_fit)
    inl = delta_y / (np.max(y) - np.min(y))
    peakinl = np.max(inl)
    return slope, yintercept, peakinl

def createDirs(logs_dict: dict, output_dir: str):
    for ife in range(8):
        FE = logs_dict['FE{}'.format(ife)]
        try:
            os.makedirs('/'.join([output_dir, FE]))
        except OSError:
            pass
    

def decodeRawData_before(fembs, rawdata):
    wibdata = wib_dec(rawdata, fembs, spy_num=1, cd0cd1sync=False)[0]
    tmpdata = [wibdata[fembs[0]]][0] # data of the 128 channels for the 8 chips
    # split data of the 8 chips:
    ## 1 ASIC: 16 channels
    data = []
    iichn = 0
    for nchip in range(8):
        onechipData = []
        for ichn in range(16):
            onechipData.append(list(tmpdata[iichn]))
            iichn += 1
        data.append(onechipData)
    return data

def decodeRawData(fembs, rawdata):
    '''
        - Decode the raw data;
        - Get the 128 data for all chips;
        - Get One period;
        - Take the average of all periods;
        - return data, one waveform, averaged waveform for each channel
    '''
    # decode the raw data using wib_dec
    wibdata = wib_dec(rawdata, fembs, spy_num=1, cd0cd1sync=False)[0]
    # get the data corresponding to the femb and timestamps
    tmpdata = wibdata[fembs[0]]
    tmstmps = wibdata[4][0] # 0-th element for 1st femb, 1st element for 2nd femb; We assume the femb is synchronized
    # find positions of waveforms
    firstCH_data = tmpdata[1]
    avg0, indices, L0 = getIndicesWF(data=firstCH_data, timestamps=tmstmps)
    avg_wf_allch = [avg0]
    for i in range(1, 128):
        onechdata = tmpdata[i]
        tmp_avg = np.zeros((1, L0))[0]
        for d in indices:
            tmp_avg = tmp_avg + onechdata[d[0] : d[1]]
        tmp_avg = tmp_avg / len(indices)
        avg_wf_allch.append(tmp_avg)

    # split data of the 8 chips:
    ## 1 ASIC: 16 channels
    # data = []
    data = {
        'wf' : [],
        'avg_wf': []
    }
    iichn = 0
    for nchip in range(8):
        onechipData = []
        onechip_avgWf = []
        for ichn in range(16):
            onechipData.append(list(tmpdata[iichn]))
            onechip_avgWf.append(list(avg_wf_allch[iichn]))
            iichn += 1
        # data.append(onechipData)
        data['wf'].append(onechipData)
        data['avg_wf'].append(onechip_avgWf)
    # print(len(data['wf']))
    # print(len(data['avg_wf']))
    # sys.exit()
    return data#, tmstmps

def getIndicesWF(data, timestamps):
    x = timestamps[:25]
    y = data[:25]
    fit = sm.OLS(y, sm.add_constant(x)).fit()
    y_fit = timestamps * fit.params[1] + fit.params[0]
    diff_y = np.abs(data - y_fit)
    M = np.mean(diff_y[:25])
    std = np.std(diff_y[:25])
    meandata = np.mean(y)
    data_copy = data.copy()
    modifiedPulses = diff_y.copy()
    indices_p = []
    for i in range(len(modifiedPulses)):
        if modifiedPulses[i] > (M+10*std):
            # indices_p.append(i)
            data_copy[i] = meandata
    meandata = np.mean(data_copy)
    std = np.std(data_copy)
    for i in range(len(data)):
        if (data[i] >= (meandata+10*std)) or (data[i]<=(meandata-10*std)):
            indices_p.append(i)
    i0 = indices_p[0]
    i1 = indices_p[-1]
    indices_p[0] = i0
    indices_p[-1] = i1
    # -- Need to ask this
    ## assuming the time between the positive and negative peaks is not bigger than 200 samples (200*500ns),
    ## let's find the blocks of indices
    pulse_indices = []
    pulse_indices.append(indices_p[0])
    for i in range(1, len(indices_p)):
        if (indices_p[i]-indices_p[i-1]) > 300:
            pulse_indices.append(indices_p[i-1])
            pulse_indices.append(indices_p[i])
    pulse_indices.append(indices_p[-1])
    # print(pulse_indices)
    #
    pairOfIndices = []
    for i in range(0, len(pulse_indices), 2):
        i0 = pulse_indices[i]-2
        i1 = pulse_indices[i+1]+4
        if (i0 <=2000) and (i1 <= 2000):
            pairOfIndices.append([i0, i1])
    # print(pairOfIndices)
    L0 = 0
    try:
        L0 = pairOfIndices[0][1]-pairOfIndices[0][0]
    except:
        print(indices_p)
        print(pulse_indices)
        print(pairOfIndices)
        plt.figure()
        plt.plot(data[52:387])
        plt.show()
        plt.close()
        sys.exit()
    for i in range(1, len(pairOfIndices)):
        d = pairOfIndices[i]
        diff = L0 - (d[1]-d[0])
        pairOfIndices[i][1] += diff
    # print(pairOfIndices)
    #
    avg_wf = np.zeros((1, L0))[0]
    for d in pairOfIndices:
        # print(len(avg_wf), len(data[d[0] : d[1]]))
        # print(d)
        avg_wf = avg_wf + data[d[0] : d[1]]
    avg_wf = avg_wf / len(pairOfIndices)
    return avg_wf, pairOfIndices, L0


def getMaxAmpIndices(oneCHdata: list):
    index_list = []
    imax_np = np.where(np.array(oneCHdata) >= 0.9*np.max(np.array(oneCHdata)))[0] # start from 0 if not calibration using ASICDAC
    #
    new_list = []
    for ii in range(1, len(imax_np)):
        if imax_np[ii]==imax_np[ii-1]+1:
            new_list.append(True)
        else:
            new_list.append(False)
    new_list.append(False)
    #
    diff_index = np.where(np.array(new_list) == False)[0]
    for i in range(len(diff_index)):
        range_index = []
        if i==0:
            range_index = [i, diff_index[i]]
        else:
            range_index = [diff_index[i-1]+1, diff_index[i]]
        # print(range_index)
        mean_imax = np.mean(imax_np[range_index[0] : range_index[1]+1])
        if oneCHdata[int(mean_imax)] < oneCHdata[int(mean_imax)+1]:
            index_list.append(int(mean_imax)+1)
        else:
            index_list.append(int(mean_imax))
    return index_list

def getpedestal_rms(oneCHdata: list, pureNoise=False):
    '''
    pktime : 2us
    sampling: every 500ns (clock) --> 1 bin (time) = 500ns
    --> number of samples (point) from the pedestal to the peak : 4 samples
    ===> take data 10 samples before the peak (5 + some ~margins)
    '''
    data = np.array(oneCHdata)
    ped, rms = 0., 0.
    if not pureNoise:
        imax = getMaxAmpIndices(data)
        # find peak
        ilastped = imax[0] - 20
        iimax = 0
        while ilastped<=50:
            ilastped = imax[iimax] - 20
            iimax += 1
        istart = ilastped-100
        if istart<0:
            istart=0
        baseline = data[istart:ilastped]
        ped = np.round(np.mean(baseline), 4)
        rms = np.round(np.std(baseline), 4)
    else:
        ped = np.round(np.mean(data), 4)
        rms = np.round(np.std(data), 4)
    return [ped, rms]

def getpulse(oneCHdata: list, averaged=True, timestamps=[]):
    indices = []
    istart = 0
    for i in range(5):
        ii = getIndicesWF(data=oneCHdata, timestamps=timestamps, istart=istart)
        indices.append(ii)
        istart = ii[1]
    print(indices)
    L = [d[1]-d[0] for d in indices]
    newIndices = []
    for i in range(len(L)):
        if L[i]>40:
            index = [indices[i][0], indices[i][0]+100]
            newIndices.append(index)

    imin = newIndices[0][0]
    imax = newIndices[0][1]
    avg_wf = np.array(oneCHdata[imin : imax])
    i = 0
    for i in range(1, len(newIndices)):
        imin = newIndices[i][0]
        imax = newIndices[i][1]
        avg_wf = avg_wf + np.array(oneCHdata[imin : imax])
    avg_wf = avg_wf / len(newIndices)
    return avg_wf


#_______BASE_CLASS________________
class BaseClass:
    def __init__(self, root_path: str, data_dir: str, output_path: str, tms: int, QC_filename: str, generateWaveForm=False):
        self.tms = tms
        self.filename = QC_filename
        splitted_filename = self.filename.split('_')
        if '47.bin' in splitted_filename:
            self.suffixName = splitted_filename[-2] + '_47'
        else:
            self.suffixName = splitted_filename[-1].split('.')[0]
        # self.foldername = '_'.join(self.filename.split('_')[:2])
        self.foldername = self.filename.split('.')[0]
        with open('/'.join([root_path, data_dir, self.filename]), 'rb') as fn:
            self.raw_data = pickle.load(fn)
        # self.raw_data = raw_data
        self.logs_dict = self.raw_data['logs']
        self.params = [key for key in self.raw_data.keys() if key!='logs']
        createDirs(logs_dict=self.logs_dict, output_dir=output_path)
        self.FE_outputDIRs = {self.logs_dict['FE{}'.format(ichip)] :'/'.join([output_path, self.logs_dict['FE{}'.format(ichip)], self.foldername]) for ichip in range(8)}
        for FE_ID, dir in self.FE_outputDIRs.items():
            try:
                os.mkdir(dir)
            except OSError:
                pass
        if generateWaveForm:
            self.FE_outputPlots_DIRs = {self.logs_dict['FE{}'.format(ichip)] :'/'.join([output_path, self.logs_dict['FE{}'.format(ichip)], self.foldername, self.suffixName]) for ichip in range(8)}
            for FE_ID, dir in self.FE_outputPlots_DIRs.items():
                try:
                    os.mkdir(dir)
                except OSError:
                    pass

# Analyze one LArASIC
class LArASIC_ana:
    def __init__(self, dataASIC: list, avgWaveforms: list, output_dir: str, chipID: str, tms=0, param='ASICDAC_CALI_CHK', generateQCresult=True, generatePlots=True):
        self.generateQCresult = generateQCresult
        self.generatePlots = generatePlots
        ## chipID : from the logs
        self.data = dataASIC
        self.avgData = avgWaveforms
        self.chipID = chipID
        self.param = param
        self.output_dir = output_dir
        self.tms = tms
        self.Items = {
                    0: 'INIT_CHK',
                    1: 'PWR',
                    2: 'CHKRES',
                    3: 'MON',
                    4: 'PWR_CYCLE',
                    5: 'RMS',
                    61: 'CALI_ASICDAC',
                    62: 'CALI_DATDAC',
                    63: 'CALI_DIRECT',
                    7: 'DLY_RUN',
                    8: 'Cap_Meas'
                    }

    def PedestalRMS(self, range_peds=[300, 3000], range_rms=[5,25], isRMSNoise=False):
        '''
            inputs: range of pedestal and range of rms
            output:
                return: {
                        'pedestal': {'data': [], 'result_qc': [], 'link_to_img': ''}, 
                        'rms': {'data': [], 'result_qc': [], 'link_to_img': ''}
                        }
                to be saved:
                    - plots of pedestal and rms --> .png
        '''
        pedestals, result_qc_ped = [], []
        rms, result_qc_rms = [], []
        for ich in range(16):
            [tmpped, tmprms] = getpedestal_rms(oneCHdata=self.data[ich], pureNoise=isRMSNoise)
            bool_ped = True
            bool_rms = True
            if self.generateQCresult:
                if (tmpped > range_peds[0]) & (tmpped < range_peds[1]):
                    bool_ped = True
                else:
                    bool_ped = False
                if (tmprms > range_rms[0]) & (tmprms < range_rms[1]):
                    bool_rms = True
                else:
                    bool_rms = False
                result_qc_ped.append(bool_ped)
                result_qc_rms.append(bool_rms)
            pedestals.append(tmpped)
            rms.append(tmprms)

        out_dict = {'pedestal': {'data': pedestals},
                    'rms': {'data': rms}
                    }
        if self.generateQCresult:
            out_dict['pedestal']['result_qc'] = result_qc_ped
            out_dict['rms']['result_qc'] = result_qc_rms
        if self.generatePlots:
            # plot of pedestal
            plt.figure()
            plt.plot(pedestals, label='Pedestal')
            plt.xlabel('Channels')
            plt.ylabel('ADC bit')
            if self.generateQCresult:
                plt.ylim([range_peds[0], range_peds[1]])
            plt.title('Pedestal')
            plt.legend(loc="upper right")
            plt.grid()
            plt.savefig('/'.join([self.output_dir, '{}_pedestal_{}.png'.format(self.Items[self.tms], self.param)]))
            plt.close()
            #
            # plot of rms
            plt.figure()
            plt.plot(rms, label='RMS')
            plt.xlabel('Channels')
            plt.ylabel('ADC bit')
            if self.generateQCresult:
                plt.ylim([range_rms[0], range_rms[1]])
            plt.title('RMS')
            plt.legend(loc="upper right")
            plt.grid()
            plt.savefig('/'.join([self.output_dir, '{}_rms_{}.png'.format(self.Items[self.tms], self.param)]))
            plt.close()
            
            out_dict['pedestal']['link_to_img'] = '/'.join(['.', '{}_pedestal_{}.png'.format(self.Items[self.tms], self.param)])
            out_dict['rms']['link_to_img'] = '/'.join(['.', '{}_rms_{}.png'.format(self.Items[self.tms], self.param)])
        return out_dict
    
    def PulseResponse(self, pedestals: list, range_pulseAmp=[9000,16000], isPosPeak=True):
        '''
            inputs:
                - range pulse amplitude
                - pedestals
            return: {
                    'pospeak': {'data': [], 'result_qc': [], 'link_to_img': ''},
                    'negpeak': {'data': [], 'result_qc': [], 'link_to_img': ''},
                    'waveform_img': ''
                    }
        '''
        ppeaks, result_qc_ppeak = [], []
        npeaks, result_qc_npeak = [], []
        for ich in range(16):
            # pulseData = getpulse(oneCHdata=self.data[ich], averaged=True)
            pulseData = self.avgData[ich]
            pospeak = np.round(np.max(pulseData) - pedestals[ich], 4)
            negpeak = np.round(pedestals[ich] - np.min(pulseData), 4)
            if self.generateQCresult:
                if isPosPeak:
                    bool_ppeak = True
                    if (pospeak > range_pulseAmp[0]) & (pospeak < range_pulseAmp[1]):
                        bool_ppeak = True
                    else:
                        bool_ppeak = False
                    result_qc_ppeak.append(bool_ppeak)
                else:
                    bool_npeak = True
                    if (negpeak > range_pulseAmp[0]) & (negpeak < range_pulseAmp[1]):
                        bool_npeak = True
                    else:
                        bool_npeak = False
                    result_qc_npeak.append(bool_npeak)
            ppeaks.append(pospeak)
            npeaks.append(negpeak)

        out_dict = {'pospeak': {'data': ppeaks},
                    'negpeak': {'data': npeaks}
                   }
        if self.generateQCresult:
            out_dict['pospeak']['result_qc'] = result_qc_ppeak
            out_dict['negpeak']['result_qc'] = result_qc_npeak
        
        if self.generatePlots:
            # pulse response - averaged waveform
            plt.figure()
            for ich in range(16):
                # avg_pulse = getpulse(oneCHdata=self.data[ich], averaged=True)
                avg_pulse = self.avgData[ich]
                plt.plot(avg_pulse, label='CH{}'.format(ich))
            plt.xlabel('Time')
            plt.ylabel('ADC bit')
            plt.title('Averaged Waveform')
            plt.legend(loc="upper right")
            plt.grid()
            plt.savefig('/'.join([self.output_dir, '{}_pulseResponse_{}.png'.format(self.Items[self.tms], self.param)]))
            plt.close()
            out_dict['waveform_img'] = '/'.join(['.', '{}_pulseResponse_{}.png'.format(self.Items[self.tms], self.param)])

            # pulse amplitude
            plt.figure()
            if isPosPeak:
                plt.plot(ppeaks, label='Positive peaks')
            else:
                plt.plot(npeaks, label='Negative peaks')
            if self.generateQCresult:
                plt.ylim([range_pulseAmp[0], range_pulseAmp[1]])
            plt.xlabel('Channels')
            plt.ylabel('ADC bit')
            plt.title('Pulse amplitude')
            plt.legend(loc="upper right")
            plt.grid()
            plt.savefig('/'.join([self.output_dir, '{}_pulseAmplitude_{}.png'.format(self.Items[self.tms], self.param)]))
            plt.close()
            if isPosPeak:
                out_dict['pospeak']['link_to_img'] = '/'.join(['.', '{}_pulseAmplitude_{}.png'.format(self.Items[self.tms], self.param)])
                out_dict['negpeak']['link_to_img'] = ''
            else:
                out_dict['pospeak']['link_to_img'] = ''
                out_dict['negpeak']['link_to_img'] = '/'.join(['.', '{}_pulseAmplitude_{}.png'.format(self.Items[self.tms], self.param)])
        return out_dict
    
    def runAnalysis(self, range_peds=[300, 3000], range_rms=[5,25], range_pulseAmp=[9000,16000], isPosPeak=True, getPulseResponse=True, isRMSNoise=False):
        '''
            inputs:
                ** range_peds: range pedestal
                ** range_rms: range rms
                ** range_pulseAmp: range pulse amplitude
            return: {"pedrms": pedrms, "pulseResponse": pulseResponse}
        '''
        out_dict = dict()
        pulseResponse = dict()
        pedrms = self.PedestalRMS(range_peds=range_peds, range_rms=range_rms, isRMSNoise=isRMSNoise)
        out_dict['pedrms'] = pedrms
        if getPulseResponse:
            pulseResponse = self.PulseResponse(pedestals=pedrms['pedestal']['data'], isPosPeak=isPosPeak, range_pulseAmp=range_pulseAmp)
            out_dict['pulseResponse'] = pulseResponse
        # return {"pedrms": pedrms, "pulseResponse": pulseResponse}
        return out_dict

# Generate report for one LArASIC
# --> All parameters for the QC
class QC_REPORT:
    def __init__(self, input_path: str, output_path: str):
        self.input_path = input_path
        self.output_path = output_path

    def QC_PWR_report(self):
        title_summary = "--- \n### POWER CONSUMPTION - SUMMARY"
        # read the json file
        data = json.load(open('/'.join([self.input_path, 'QC_PWR_data.json'])))
        KEY_names = {'V': "Voltage", 'I': 'Current', 'P': "Power Consumption"}
        KEY_units = {'V': 'V', 'I': 'mA', 'P': 'mW'}
        md = ""
        qc_results = []
        for KEY in data.keys():
            qc_result = data[KEY]['result_qc']
            qc_results.append(qc_results)
            link_to_img = data[KEY]['link_to_img']
            KEY_title = '**<u>' + KEY_names[KEY] + ' ({}):</u> {}**'.format(KEY_units[KEY], qc_result)
            KEY_plot = '![]({})'.format(link_to_img)
            KEY_md = "<span>{} \n {}</span>".format(KEY_title, KEY_plot)
            md += (KEY_md + '\n')
        md += "---"
        if False in qc_results:
            title_summary += ": Failed\n"
        else:
            title_summary += ": Passed\n"
        md = title_summary + md
        dumpMD(output_path=self.output_path, output_name='QC_PWR_md', mdTable_to_dump=md)

    
if __name__ == '__main__':
    # root_path = '../../Data_BNL_CE_WIB_SW_QC'
    root_path = '../../Analyzed_BNL_CE_WIB_SW_QC/002-06204'
    qc_report = QC_REPORT(input_path=root_path, output_path=root_path)
    pwr_qc_dict = qc_report.QC_PWR_report()
    print(pwr_qc_dict)