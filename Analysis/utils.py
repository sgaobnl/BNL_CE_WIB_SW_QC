############################################################################################
#   created on 5/3/2024 @ 14:38
#   emails: radofanantenan.razakamiandra@stonybrook.edu
#
############################################################################################

import os
import numpy as np
# import csv
import json
import matplotlib.pyplot as plt
from spymemory_decode_copy import wib_dec

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
    print('*\t{}\t\t*'.format(item))
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

def decodeRawData(fembs, rawdata, rms_flg=False):
    wibdata = wib_dec(rawdata, fembs, spy_num=1, cd0cd1sync=False)[0]
    # data = [wibdata[0]][fembs[0]]#, wibdata[1],wibdata[2],wibdata[3]][fembs[0]]
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

def getpedestal_rms(oneCHdata: list):
    '''
    pktime : 2us
    sampling: every 500ns (clock)
    --> number of samples from the pedestal to the peak : 4 samples
    ===> take data 10 samples before the peak (5 + some ~margins)
    '''
    data = np.array(oneCHdata)
    # find peak
    imax = np.where(data==np.max(data))[0][0]
    ilastped = imax - 20
    inextped = imax + 150
    baseline = np.concatenate([data[ilastped-100:ilastped], data[inextped : inextped + 100]])
    # baseline = data[ilastped-100:ilastped]
    ped = np.mean(baseline)
    rms = np.std(baseline)
    return [ped, rms]

def getpulse(oneCHdata: list):
    data = np.array(oneCHdata)
    imax = np.where(data==np.max(data))[0][0]
    pulserange = data[imax-50 : imax+100]
    return pulserange

# Analyze one LArASIC
class ASIC_ana:
    def __init__(self, dataASIC: list, output_dir: str, chipID: str):
        ## one can get the chipID from the logs
        ##
        self.data = dataASIC
        self.chipID = chipID
        self.output_dir = output_dir
        # self.getPedestal_RMS()
        # self.getwaveforms()

    def getPedestal_RMS(self, makePlot=False):
        ## return [pedestal, rms]
        peds = []
        rms = []
        Nch = len(self.data)
        for ich in range(Nch):
            [tmpped, tmprms] = getpedestal_rms(oneCHdata=self.data[ich])
            peds.append(tmpped)
            rms.append(tmprms)

        if makePlot:
            # Pedestal
            plt.figure()
            plt.plot(peds, label='Pedestal')
            meanped = np.mean(peds)
            plt.xlim([-0.5,16])
            plt.ylim([meanped-500 , meanped+500])
            plt.xlabel('CH number')
            plt.ylabel('ADC count')
            plt.title('Pedestal')
            plt.legend()
            plt.grid()
            plt.savefig('/'.join([self.output_dir, 'pedestal_{}.png'.format(self.chipID)]))

            # RMS
            plt.figure()
            plt.plot(rms, label='RMS')
            plt.ylim([0, 50])
            plt.xlabel('CH number')
            plt.ylabel('ADC count')
            plt.title('RMS')
            plt.legend()
            plt.grid()
            plt.savefig('/'.join([self.output_dir, 'rms_{}.png'.format(self.chipID)]))

        # selection
        #
        out = {'pedestal': peds, 'rms': rms, 'pedestal_passed': True, 'rms_passed': True}
        return out

    def getwaveforms(self, makePlot=False):
        rangepulses = []
        for ich in range(len(self.data)):
            tmppulserange = getpulse(oneCHdata=self.data[ich])
            rangepulses.append(tmppulserange)
        
        if makePlot:
            plt.figure()
            for ich in range(16):
                plt.plot(rangepulses[ich], label='CH{}'.format(ich))
            plt.xlabel('Time (ns)')
            plt.ylabel('ADC count')
            plt.title('Wave forms')
            plt.legend()
            plt.grid()
            plt.savefig('/'.join([self.output_dir, 'waveforms_{}.png'.format(self.chipID)]))

        return rangepulses

    def get_ppeak(self, waveforms: list, pedestals: list):
        positive_peaks = []
        for ich in range(16):
            ppeak = np.max(waveforms[ich]) - pedestals[ich]
            positive_peaks.append(ppeak)
        # selection
        #
        out = {'positive_peaks': positive_peaks, 'ppeak_passed': True}
        return out
    
    def runAll(self, defCriteria=True):
        '''
            defCriteria==True: we need the data (list of numbers) in order to make distributions of each parameter and define the selection criteria (range)
        '''
        if defCriteria:
            ped_rms = self.getPedestal_RMS(makePlot=False)
            pedestals = ped_rms['pedestal']
            rms = ped_rms['rms']
            waveforms = self.getwaveforms(makePlot=False)
            ppeaks = self.get_ppeak(waveforms=waveforms, pedestals=pedestals)['positive_peaks']
            return [pedestals, rms, ppeaks]
        else:
            # make plots
            # save results in files
            pass