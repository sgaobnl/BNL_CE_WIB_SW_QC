############################################################################################
#   created on 5/3/2024 @ 14:38
#   emails: radofanantenan.razakamiandra@stonybrook.edu
#
############################################################################################

import os, sys, pickle
import numpy as np
# import csv
import json
import matplotlib.pyplot as plt
# from spymemory_decode_copy import wib_dec
import math

from dunedaq_decode import wib_dec

sys.path.append('Analysis/')
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

def dumpJson(output_path: str, output_name: str, data_to_dump: dict):
    '''
        Save data to json.
        inputs:
            output_path: path to the output
            output_name: filename WITHOUT the extension .json
            data_to_dump: a dictionary of the data to save
    '''
    with open('/'.join([output_path, output_name + '.json']), 'w+') as fn:
        json.dump(data_to_dump, fn)
        ## ------- MODIFIY THE WAY TO WRITE THE DATA ON THE FILE
        ## ==> ORGANIZE THE DATA BY WRITING EACH key: value ON A NEW LINE

def linear_fit(x: list, y: list):
    '''
        Perform a linear fit on y = f(x) using numpy.polyfit degree 1.
        inputs: x and y
        outputs: slope, yintercept, peakinl
    '''
    fit = np.polyfit(x, y, 1)
    slope, yintercept = fit[0], fit[1]
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
    

def decodeRawData(fembs, rawdata):
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

def getMaxAmpIndices(oneCHdata: list):
    index_list = []
    imax_np = np.where(np.array(oneCHdata) >= 0.8*np.max(np.array(oneCHdata)))[0]
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

def getpedestal_rms(oneCHdata: list):
    '''
    pktime : 2us
    sampling: every 500ns (clock) --> 1 bin (time) = 500ns
    --> number of samples (point) from the pedestal to the peak : 4 samples
    ===> take data 10 samples before the peak (5 + some ~margins)
    '''
    data = np.array(oneCHdata)
    imax = getMaxAmpIndices(data)
    # find peak
    ilastped = imax[0] - 20
    istart = ilastped-100
    if istart<0:
        istart=0
    baseline = data[istart:ilastped]
    ped = np.round(np.mean(baseline), 4)
    # if math.isnan(ped):
    #     print(baseline, ilastped)
    rms = np.round(np.std(baseline), 4)
    return [ped, rms]

def getpulse(oneCHdata: list):
    data = np.array(oneCHdata)
    # imax = np.where(data>=0.95*np.max(data))[0] # only peaks >= 0.95*maximum are selected for the averaging
    imax = getMaxAmpIndices(oneCHdata=data)
    iimax = 0
    pulserange = np.array([])
    for i in range(len(imax)):
        if len(data[imax[i]-120 : imax[i]+200])!=0:
            pulserange = data[imax[i]-120 : imax[i]+200]
            iimax = i
            break
    Npulses = 1
    for i in range(iimax, len(imax)):
        tmprange = data[imax[i]-120 : imax[i]+200]
        if len(tmprange)!=len(pulserange):
            pass
        else:
            Npulses += 1
            pulserange += tmprange
    pulserange = pulserange / Npulses
    return pulserange

# Analyze one LArASIC
class LArASIC_ana:
    def __init__(self, dataASIC: list, output_dir: str, chipID: str, tms=0, param='ASICDAC_CALI_CHK'):
        ## chipID : from the logs
        self.data = dataASIC
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

    def PedestalRMS(self, range_peds=[300, 3000], range_rms=[5,25]):
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
            bool_ped = True
            bool_rms = True
            [tmpped, tmprms] = getpedestal_rms(oneCHdata=self.data[ich])
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

        out_dict = {'pedestal': {'data': pedestals, 'result_qc': result_qc_ped},
                    'rms': {'data': rms, 'result_qc': result_qc_rms}
                    }
        
        # plot of pedestal
        plt.figure()
        plt.plot(pedestals, label='Pedestal')
        plt.xlabel('Channels')
        plt.ylabel('ADC bit')
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
        plt.ylim([range_rms[0], range_rms[1]])
        plt.title('RMS')
        plt.legend(loc="upper right")
        plt.grid()
        plt.savefig('/'.join([self.output_dir, '{}_rms_{}.png'.format(self.Items[self.tms], self.param)]))
        plt.close()
        
        out_dict['pedestal']['link_to_img'] = '/'.join([self.output_dir, '{}_pedestal_{}.png'.format(self.Items[self.tms], self.param)])
        out_dict['rms']['link_to_img'] = '/'.join([self.output_dir, '{}_rms_{}.png'.format(self.Items[self.tms], self.param)])
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
            pulseData = getpulse(oneCHdata=self.data[ich])
            pospeak = np.round(np.max(pulseData) - pedestals[ich], 4)
            negpeak = np.round(pedestals[ich] - np.min(pulseData), 4)
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

        out_dict = {'pospeak': {'data': ppeaks, 'result_qc': result_qc_ppeak},
                    'negpeak': {'data': npeaks, 'result_qc': result_qc_npeak}}
        
        # pulse response - averaged waveform
        plt.figure()
        for ich in range(16):
            avg_pulse = getpulse(oneCHdata=self.data[ich])
            plt.plot(avg_pulse, label='CH{}'.format(ich))
        plt.xlabel('Time')
        plt.ylabel('ADC bit')
        plt.title('Averaged Waveform')
        plt.legend(loc="upper right")
        plt.grid()
        plt.savefig('/'.join([self.output_dir, '{}_pulseResponse_{}.png'.format(self.Items[self.tms], self.param)]))
        plt.close()
        out_dict['waveform_img'] = '/'.join([self.output_dir, '{}_pulseResponse_{}.png'.format(self.Items[self.tms], self.param)])

        # pulse amplitude
        plt.figure()
        if isPosPeak:
            plt.plot(ppeaks, label='Positive peaks')
        else:
            plt.plot(npeaks, label='Negative peaks')
        plt.ylim([range_pulseAmp[0], range_pulseAmp[1]])
        plt.xlabel('Channels')
        plt.ylabel('ADC bit')
        plt.title('Pulse amplitude')
        plt.legend(loc="upper right")
        plt.grid()
        plt.savefig('/'.join([self.output_dir, '{}_pulseAmplitude_{}.png'.format(self.Items[self.tms], self.param)]))
        plt.close()
        if isPosPeak:
            out_dict['pospeak']['link_to_img'] = '/'.join([self.output_dir, '{}_pulseAmplitude_{}.png'.format(self.Items[self.tms], self.param)])
            out_dict['negpeak']['link_to_img'] = ''
        else:
            out_dict['pospeak']['link_to_img'] = ''
            out_dict['negpeak']['link_to_img'] = '/'.join([self.output_dir, '{}_pulseAmplitude_{}.png'.format(self.Items[self.tms], self.param)])
        return out_dict
    
    def runAnalysis(self, range_peds=[300, 3000], range_rms=[5,25], range_pulseAmp=[9000,16000], isPosPeak=True):
        '''
            inputs:
                ** range_peds: range pedestal
                ** range_rms: range rms
                ** range_pulseAmp: range pulse amplitude
            return: {"pedrms": pedrms, "pulseResponse": pulseResponse}
        '''
        pedrms = self.PedestalRMS(range_peds=range_peds, range_rms=range_rms)
        pulseResponse = self.PulseResponse(pedestals=pedrms['pedestal']['data'], isPosPeak=isPosPeak, range_pulseAmp=range_pulseAmp)
        return {"pedrms": pedrms, "pulseResponse": pulseResponse}
    
if __name__ == '__main__':
    root_path = '../../Data_BNL_CE_WIB_SW_QC'
    output_path = '../../Analyzed_BNL_CE_WIB_SW_QC'