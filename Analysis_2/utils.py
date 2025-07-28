############################################################################################
#   created on 5/3/2024 @ 14:38
#   email: radofanantenan.razakamiandra@stonybrook.edu
#   Utility functions and classes needed for the decoding and analysis
############################################################################################

import os, sys, json, platform, pickle
import numpy as np
import markdown
# import csv
import json
import matplotlib.pyplot as plt
import statsmodels.api as sm
from scipy.signal import find_peaks
from scipy import stats

##
from sklearn.cluster import DBSCAN
##
# sys.path.append('../')
# from spymemory_decode import wib_dec
# sys.path.append('./Analysis')
#_________Import the CPP module_____________
system_info = platform.system()
print("Operating system: ", system_info)
if system_info=='Linux':
    # print('IN')
    sys.path.append('./decode')
    from dunedaq_decode import wib_dec
    sys.path.append('../')
elif system_info=='Windows':
    sys.path.append('../')
    from spymemory_decode import wib_dec
#     sys.path.append('../build')
#     from dunedaq_decode import wib_dec
#     sys.path.append('../Analysis')
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
        

def linear_fit(x: list, y: list):
    '''
        Perform a linear fit on y = f(x) using numpy.polyfit degree 1.
        inputs: x and y
        outputs: slope, yintercept, peakinl
    '''

    slope, yintercept = np.polyfit(x, y, 1)
    y_fit = np.array(x) * slope + yintercept
    delta_y = np.abs(np.array(y) - y_fit)
    inl = delta_y / (np.max(y) - np.min(y))
    peakinl = np.max(inl)
    return slope, yintercept, peakinl


def gain_inl(x: list, y: list, item='', returnDNL=False):
    x = np.array(x)
    y = np.array(y)
    
    # # Initial fit on all points
    # slope, yintercept = np.polyfit(x, y, 1)
    # ypred = slope * x + yintercept
    
    # # Calculate INL for all points
    # inl_points = []
    # for i in range(1, len(x)):
    #     dy = np.abs(y[i] - ypred[i])
    #     inl = (dy / np.abs(y[i] - y[0])) * 100
    #     if inl <= 1:
    #         inl_points.append(i)
    
    # # Find longest continuous sequence
    # sequences = []
    # current_seq = [inl_points[0]]
    
    # for i in range(1, len(inl_points)):
    #     if inl_points[i] == inl_points[i-1] + 1:
    #         current_seq.append(inl_points[i])
    #     else:
    #         sequences.append(current_seq)
    #         current_seq = [inl_points[i]]
    # sequences.append(current_seq)
    
    # # Get longest sequence
    # best_seq = max(sequences, key=len)
    # print('sequences : ', best_seq)
    # i0 = best_seq[0]
    # i1 = best_seq[-1] + 1
    
    # # Final calculations for best range
    # slope, yintercept = np.polyfit(x[i0:i1], y[i0:i1], 1)
    # ypred = slope * x + yintercept

    slope, yintercept = np.polyfit(x, y, 1)
    y_fit = np.array(x) * slope + yintercept
    delta_y = np.abs(np.array(y) - y_fit)
    inl = delta_y / (np.max(y) - np.min(y))

    i0 = 0
    i1 = -1

    # for i1, ii in enumerate(inl):
    #     if ii > 0.01:
    #         break
    posINL = np.where(inl > 0.01)[0]
    if len(posINL)==0:
        # if 'ASICDAC' in item:
        #     i1 = -1
        # else:
        #     i1 = 0
        #     i0 = -1
        i1 = -1
    else:
        i1 = posINL[0]
        if i1==0:
            i0 = -1
    
    # delta_y = np.abs(y[i0:i1] - ypred[i0:i1])
    # inl = delta_y / (np.max(y[i0:i1]) - np.min(y[i0:i1]))
    # peakinl = np.max(inl)
    peakinl = np.max(inl)
    # linRange = [y[i0], y[i1-1]] if 'ASICDAC' in item else [y[i1-1], y[i0]]
    linRange = [y[i0], y[i1]]
    # print('-----------', item, len(linRange))
    # if np.abs(linRange[1]-linRange[0]) < 37:
    #     print(np.abs(linRange[1]-linRange[0]))
    #     plt.figure()
    #     plt.scatter(y, x)
    #     plt.plot(y_fit, x)
    #     plt.show()
    #     sys.exit()
    
    if returnDNL:
        dnl_list = []
        try:
            lsb = np.abs((np.max(y[i0:i1]) - np.min(y[i0:i1])) / (np.max(x[i0:i1]) - np.min(x[i0:i1])))
        except:
            print(i0, i1)
            sys.exit()
        dnl_list.append(np.abs(((np.abs(y[i0+1] - y[i0])/np.abs(x[i0+1] - x[i0]))-lsb)/lsb))
        
        for i in range(i0+1, i1):
            dnl_list.append(np.abs(((np.abs(y[i]-y[i-1])/np.abs(x[i]-x[i-1])) - lsb)/lsb))
            
        y_FSR = (np.max(y[i0:i1]) - np.min(y[i0:i1]))
        dnl_normalized_to_y_FSR = ((np.array(dnl_list)*lsb/y_FSR))
        
        return slope, yintercept, peakinl, linRange, np.max(dnl_normalized_to_y_FSR)
    
    return slope, yintercept, peakinl, linRange

def createDirs(logs_dict: dict, output_dir: str):
    for ife in range(8):
        FE = logs_dict['FE{}'.format(ife)]
        try:
            os.makedirs('/'.join([output_dir, FE]))
        except OSError:
            pass
    

def decodeRawData_(fembs, rawdata, needTimeStamps=False):
    wibdata = wib_dec(rawdata, fembs, spy_num=1, cd0cd1sync=False)[0]
    tmpdata = [wibdata[fembs[0]]][0] # data of the 128 channels for the 8 chips
    # print(len(wibdata))
    # tmpdata = wibdata[1][0]
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
    if needTimeStamps:
        tmstamps = wibdata[4][0]
        cd_tmstamps = wibdata[5][0]
        return data, tmstamps, cd_tmstamps
    else:
        return data

def organizeWibdata(wibdata: list):
    ## 1 ASIC: 16 channels
    data = []
    iichn = 0
    for nchip in range(8):
        onechipData = []
        for ichn in range(16):
            onechipData.append(list(wibdata[0][iichn]))
            iichn += 1
        data.append(onechipData)
    return data

def decodeRawData(fembs, rawdata, needTimeStamps=False, period=500):
    tmpwibdata = wib_dec(rawdata, fembs, spy_num=5, cd0cd1sync=False)
    #-----------------------------------------------------------------------------
    dat_tmts_l = []
    dat_tmts_h = []
    for wibdata in tmpwibdata:
        if system_info=='Linux':
            dat_tmts_l.append(wibdata[5][fembs[0]*2][0]) #LSB of timestamp = 16ns
            dat_tmts_h.append(wibdata[5][fembs[0]*2+1][0])
        elif system_info=='Windows':
            dat_tmts_l.append(wibdata[5][fembs[0]*2][0]) #LSB of timestamp = 16ns
            dat_tmts_h.append(wibdata[5][fembs[0]*2+1][0])

    # period = 500
    dat_tmtsl_oft = (np.array(dat_tmts_l)//32)%period #ADC sample rate = 16ns*32 = 512ns
    dat_tmtsh_oft = (np.array(dat_tmts_h)//32)%period #ADC sample rate = 16ns*32 = 512ns

    #for achn in range(len(datd)):
    all_data = []
    # print ("concatenate spy buffers according to timestamp")
    for achn in range(128):
        conchndata = np.array([])

        for i in range(len(tmpwibdata)):
            if achn<64:
                oft = dat_tmtsl_oft[i]
            else:
                oft = dat_tmtsh_oft[i]

            wibdata = tmpwibdata[i]
            datd = [wibdata[0], wibdata[1],wibdata[2],wibdata[3]][fembs[0]]
            # print('number of chn = ', len(datd))
            chndata = np.array(datd[achn] , dtype=np.uint32)
            lench = len(chndata)
            tmp = int(period-oft)
            # conchndata = conchndata + list(chndata[tmp : ((lench-tmp)//period)*period + tmp])
            # print(tmp, ' ---- ', ((lench-tmp)//period)*period + tmp)
            conchndata = np.concatenate((conchndata, chndata[tmp : ((lench-tmp)//period)*period + tmp]))
        all_data.append(conchndata)

    data = []
    iichn = 0
    for nchip in range(8):
        onechipData = []
        for ichn in range(16):
            onechipData.append(list(all_data[iichn]))
            iichn += 1
        data.append(onechipData)
    return data

def getMaxAmpIndices(oneCHdata: list):
    index_list = []
    imax_np = np.where(np.array(oneCHdata) >= 0.9*np.max(np.array(oneCHdata)))[0]
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

def getMinAmpIndices(data: list):
    index_list = []
    mindata = np.min(data)
    imin_np = np.where(np.array(data) <= (mindata+0.2*mindata))[0]
    new_list = [False]
    for ii in range(1, len(imin_np)):
        if imin_np[ii]==imin_np[ii-1]+1:
            new_list.append(True)
        else:
            new_list.append(False)
    # print(imin_np)
    # print(new_list)
    diff = np.where(np.array(new_list)==False)[0]
    s = []
    for i in range(len(diff)-1):
        s.append(new_list[diff[i]: diff[i+1]])
    s.append(new_list[diff[-1]:])
    indices = []
    for i in range(len(diff)):
        indices.append([])
        for ii in range(len(s[i])):
            if ii==0:
                indices[i].append(diff[i])
            else:
                indices[i].append(indices[i][ii-1]+1)
    # print(indices)
    imin_list = []
    for i in range(len(indices)):
        tmp = data[indices[i][0] : indices[i][-1]]
        # print(np.min(tmp))
        imin = np.where(tmp==np.min(tmp))[0][0]
        # print(imin)
        # print('--')
        imin_list.append(imin_np[indices[i][imin]])
    # print(imin_list)
    return imin_list

def getpedestal_rms(oneCHdata: list, pureNoise=False, period=500):
    '''
    pktime : 2us
    sampling: every 500ns (clock) --> 1 bin (time) = 500ns
    --> number of samples (point) from the pedestal to the peak : 4 samples
    ===> take data 10 samples before the peak (5 + some ~margins)
    '''
    ped, rms = 0.0, 0.0
    if pureNoise:
        ped = np.round(np.mean(oneCHdata), 4)
        rms = np.round(np.std(oneCHdata), 4)
    else:
        # posmax, pheights = find_peaks(x=oneCHdata, height=0.85*np.max(oneCHdata)) ### use argmax corresponding to each period instead of find_peaks 
        # N_pulses = len(posmax)
        # if N_pulses>20: # the data does not have any pulse because we sent 20 pulses at max (5 spy buffers)
        #     ped = np.round(np.mean(oneCHdata), 4)
        #     rms = np.round(np.std(oneCHdata), 4)
        # else:
        #     data = np.array([])
        #     # for i in range(N_pulses):
        #     #     istart = i*period
        #     #     iend = posmax[i]-10
        #     #     if (iend-istart) > 0:
        #     #         data = np.concatenate((data, oneCHdata[istart : iend]))
        #     # ped = np.round(np.mean(data), 4)
        #     # rms = np.round(np.std(data), 4)
        #     N_periods = len(oneCHdata)//period
        data = np.array([])
        N_periods = len(oneCHdata) // period
        for i in range(N_periods):
            chunkdata = oneCHdata[i*period : (i+1)*period]
            pmax = np.argmax(chunkdata)
            pmin = np.argmin(chunkdata)
            istart = 0
            iend = 0
            if (pmax < pmin) and (pmax-50 < 0):
                istart = pmin+20
                iend = -50
            elif (pmax < pmin) and (period-pmin < pmax):
                istart = 20
                iend = pmax - 20
            else:
                front = chunkdata[pmax - 20 : ]
                back = chunkdata[ : pmax - 20]
                chunkdata = np.concatenate((front, back))
                pmax = np.argmax(chunkdata)
                pmin = np.argmin(chunkdata)
                istart = pmin + 20
                iend = -50
            data = np.concatenate((data, chunkdata[istart : iend]))
        ped = np.round(np.mean(data), 4)
        rms = np.round(np.std(data), 4)

    return [ped, rms]

#_______BASE_CLASS________________
class BaseClass:
    def __init__(self, root_path: str, data_dir: str, output_path: str, tms: int, QC_filename: str, env='RT'):
        self.tms = tms
        # self.input_dir = '/'.join([root_path, data_dir])
        tmpdata_dir = [f for f in os.listdir('/'.join([root_path, data_dir])) if env in f][0]
        output_path = f'{output_path}_{env}'
        self.input_dir = '/'.join([root_path, data_dir, tmpdata_dir])
        self.filename = QC_filename
        self.ERROR = False
        # does self.filename exist in the folder??
        if self.filename in os.listdir(self.input_dir):
            pass
        else:
            self.ERROR = True
            return
        splitted_filename = self.filename.split('_')
        if '47.bin' in splitted_filename:
            self.suffixName = splitted_filename[-2] + '_47'
        else:
            self.suffixName = splitted_filename[-1].split('.')[0]
        
        #self.foldername = self.filename.split('.')[0]
        # with open('/'.join([root_path, data_dir, self.filename]), 'rb') as fn:
        with open('/'.join([self.input_dir, self.filename]), 'rb') as fn:
            self.raw_data = pickle.load(fn)
        # self.raw_data = raw_data
        self.logs_dict = self.raw_data['logs']
        #print (self.logs_dict)
        self.logs_dict['position'] = {'on Tray': dict(),
                                      'on DAT' : dict()
                                      }
        self.params = [key for key in self.raw_data.keys() if key!='logs']
        self.__openLog__()
        createDirs(logs_dict=self.logs_dict, output_dir=output_path)
        self.FE_outputDIRs = {self.logs_dict['FE{}'.format(ichip)] :'/'.join([output_path, self.logs_dict['FE{}'.format(ichip)]]) for ichip in range(8)}
        #self.FE_outputDIRs = {self.logs_dict['FE{}'.format(ichip)] :'/'.join([output_path, self.logs_dict['FE{}'.format(ichip)], self.foldername]) for ichip in range(8)}
        for FE_ID, dir in self.FE_outputDIRs.items():
            try:
                os.mkdir(dir)
            except OSError:
                pass

    def __openLog__(self):
        # Update the internal logs of each test item -> Use the timestamp as an ID for each FE ASIC
        if 'QC.log' not in os.listdir(self.input_dir):
            self.ERROR = True
            return
        with open('/'.join([self.input_dir, 'QC.log']), 'rb') as f:
            logs = pickle.load(f)
        RTS_IDs = logs['RTS_IDs']
        for tmts, place in RTS_IDs.items():
            FE = 'FE{}'.format(place[1])
            self.logs_dict[FE] = tmts
            #self.logs_dict['ADC{}'.format(place[1])] = tmts
            self.logs_dict['FE{}'.format(place[1])] = tmts
            self.logs_dict['position']['on Tray'][FE] = place[0]
            self.logs_dict['position']['on DAT'][FE] = place[1]

    # def get_Info_logs(self):
    #     logs = {
    #                 # "item_name" : self.item,
    #                 "RTS_timestamp" : [self.logs_dict['FE{}'.format(ichip)] for ichip in range(8)],
    #                 'Test Site' : self.logs_dict['testsite'],
    #                 'RTS_Property_ID' : 'BNL',
    #                 'RTS chamber' : 1,
    #                 'DAT_ID' : self.logs_dict['DAT_SN'],
    #                 'DAT rev' : self.logs_dict['DAT_Revision'],
    #                 'Tester' : self.logs_dict['tester'],
    #                 'DUT' : self.logs_dict['DUT'],
    #                 'Tray ID' : self.logs_dict['TrayID'],
    #                 'SN' : '',
    #                 'DUT_location_on_tray' : self.logs_dict['position']['on Tray'],
    #                 'DUT_location_on_DAT' : self.logs_dict['position']['on DAT'],
    #                 'Chip_Mezzanine_1_in_use' : 'ADC_XXX_XXX',
    #                 'Chip_Mezzanine_2_in_use' : 'CD_XXXX_XXXX',
    #                 "date": self.logs_dict['date'],
    #                 "env": self.logs_dict['env'],
    #                 "note": self.logs_dict['note'],
    #                 "DAT_SN": self.logs_dict['DAT_SN'],
    #                 "WIB_slot": self.logs_dict['DAT_on_WIB_slot']
    #             }
    #     return logs

#_______BASE_CLASS_for_ANALYSIS_of_the_decoded_data________________
class BaseClass_Ana:
    def __init__(self, root_path: str, chipID: str, item: str, output_path: str):
        '''
            root_path : path to the main folder of the decoded data => path to the chip ID (timestamp);
            item : item to analyze. For example: QC_INIT_CHK, QC_PWR, QC_PWR_CYCLE, etc.
        '''
        self.root_path = root_path
        self.chipID = chipID
        self.output_path = output_path
        # self.output_dir = '/'.join([self.root_path, self.chipID, 'Analysis'])
        #try:
        #    os.mkdir(output_path)
        #except:
        #    pass
        #self.output_dir = '/'.join([output_path, chipID])
        #try:
        #    os.mkdir(self.output_dir)
        #except OSError:
        #    # print("Folder already exists...")
        #    pass
        self.ERROR = False # to check if the json file exists    
        self.item_to_ana = item
        try:
            self.filename = [f for f in os.listdir('/'.join([self.output_path, self.chipID])) if ((f'{self.item_to_ana}.json' in f) and ('json' in f[-4:])) ][0]
            self.data, self.params = self.read_json()
        except:
            print('Error: {}.json not exist for chip = {}'.format(self.item_to_ana,chipID))
            self.ERROR = True

    def read_json(self):
        #path_to_file = '/'.join([self.root_path, self.chipID, self.item_to_ana, self.filename])
        path_to_file = '/'.join([self.output_path, self.chipID,  self.filename])
        data = json.load(open(path_to_file))
        params = [param for param in data.keys() if param != 'logs']
        return data, params

    def getoneConfigData(self, config: str):
        data = self.data[config]
        return data

    def getCHresp_info(self, oneChipData: list):
        '''
            This method can be used if the input data has the channel responses like pedestal, rms, pospeak (or posAmp), and negpeak (or negAmp)
        '''
        meanValue = np.round(np.mean(oneChipData), 4)
        stdValue = np.round(np.std(oneChipData) / np.sqrt(16), 4) # standard error of the mean      
        minValue = np.round(np.min(oneChipData), 4) # the positive value was obtained by subtracting the pedestal by the minValue (the actual one)
        maxValue = np.round(np.max(oneChipData), 4)
        return meanValue, stdValue, minValue, maxValue
    
    def ChResp_ana(self, item_to_plot: str):
        '''
            This method will be overwritten in some of the analysis classes in order to get the required analysis for each QC item. That's completely fine.
            item_to_plot could be 'pedestal', 'rms', 'pospeak', or 'negpeak'
        '''
        chipData = dict()
        for param in self.params:
            data = self.getoneConfigData(config=param)
            meanValue, stdValue, minValue, maxValue = self.getCHresp_info(oneChipData=data[item_to_plot])
            # config = '\n'.join(param.split('_'))
            config = ''
            cfg_splitted = param.split('_')
            config ='\n'.join(cfg_splitted)
            chipData[config] = {'mean': meanValue, 'std': stdValue, 'min': minValue, 'max': maxValue}
        configs = list(chipData.keys())
        plt.figure(figsize=(15, 12))
        for cfg in configs:
            cfg_split = cfg.split('_')
            xlabel = cfg
            # mean and std
            plt.errorbar(x=xlabel, y=chipData[cfg]['mean'], yerr=chipData[cfg]['std'], color='b', fmt='.', capsize=4)
            # min value
            plt.scatter(x=xlabel, y=chipData[cfg]['min'], color='r', marker='.', s=100)
            # max value
            plt.scatter(x=xlabel, y=chipData[cfg]['max'], color='r', marker='.', s=100)
        plt.title('{}'.format(item_to_plot))
        plt.grid(True)
        plt.savefig('/'.join([self.output_dir, '{}_'.format(self.item_to_ana) + item_to_plot + '.png']))
        plt.close()
#________________________________________xx___________________________________________________________________________

# Analyze one LArASIC --Decoding
class LArASIC_ana:
    def __init__(self, dataASIC: list, output_dir: str, chipID: str, tms=0, param='ASICDAC_CALI_CHK', generateQCresult=True, generatePlots=False, period=500):
        self.generateQCresult = generateQCresult
        self.generatePlots = generatePlots
        ## chipID : from the logs
        self.data = dataASIC
        self.chipID = chipID
        self.param = param
        self.output_dir = output_dir
        self.tms = tms # use this info
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
                    64: 'CALI_ASICDAC_47',
                    7: 'DLY_RUN',
                    8: 'Cap_Meas'
                    }
        self.period = period

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
            [tmpped, tmprms] = getpedestal_rms(oneCHdata=self.data[ich], pureNoise=isRMSNoise, period=self.period)
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
            
            # out_dict['pedestal']['link_to_img'] = '/'.join(['.', '{}_pedestal_{}.png'.format(self.Items[self.tms], self.param)])
            # out_dict['rms']['link_to_img'] = '/'.join(['.', '{}_rms_{}.png'.format(self.Items[self.tms], self.param)])
        return out_dict
    
    def getpulse(self, pwrcycleN=-1):
        '''
            This method is not a generalized algorithm to get the average pulses. It is tms depedent, based on what we see when plotting the waveforms.
        '''
        chipWF = []
        for ich in range(16):
            # if self.tms in [0, 1, 2, 4, 61, 64]:
            chdata = []
            N_pulses = len(self.data[ich])//self.period
            for i in range(N_pulses):
            # for i in range(4):
                istart = i*self.period
                iend = istart + self.period
                chunkdata = self.data[ich][istart : iend]
                chdata.append(chunkdata)
            chdata = np.array(chdata)
            avg_wf = np.average(np.transpose(chdata), axis=1, keepdims=False)
            # posmax = np.argmax(avg_wf)
            # if posmax+10 > self.period:
            #     front = avg_wf[posmax-50 : ]
            #     back = avg_wf[ : posmax-50]
            #     avg_wf = np.concatenate((front, back), axis=0)
            # elif posmax-10 < 0:
            #     front = avg_wf[-50 : ]
            #     back = avg_wf[ : -50]
            #     avg_wf = np.concatenate((front, back), axis=0)
            pmax = np.argmax(avg_wf)
            pmin = np.argmin(avg_wf)
            if pmax > pmin:
                front = avg_wf[pmax - 50 : ]
                back = avg_wf[ : pmax - 50]
                avg_wf = np.concatenate((front, back))
            elif (pmax < pmin) and (pmax-50 < 0):
                front = avg_wf[-50 : ]
                back = avg_wf[ : -50]
                avg_wf = np.concatenate((front, back))

            chipWF.append(avg_wf)
        return chipWF

    def PulseResponse(self, pedestals: list, range_pulseAmp=[9000,16000], isPosPeak=True, pwrcycleN=-1, getWaveform=False):
        ppeaks, result_qc_ppeak = [], []
        npeaks, result_qc_npeak = [], []
        pulseData = self.getpulse(pwrcycleN=pwrcycleN) # get pulses of all channels
        for ich in range(16):
            pospeak = np.round(np.max(pulseData[ich]) - pedestals[ich], 4)
            negpeak = np.round(pedestals[ich] - np.min(pulseData[ich]), 4)
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
        if getWaveform:
            out_dict['waveforms'] = pulseData
            
        if self.generateQCresult:
            out_dict['pospeak']['result_qc'] = result_qc_ppeak
            out_dict['negpeak']['result_qc'] = result_qc_npeak
        
        if self.generatePlots:
            # pulse response - averaged waveform
            plt.figure()
            BLref = pulseData[0][0]
            for ich in range(16):
                # BL_ich = pulseData[ich][0]
                # diff = BL_ich - BLref
                # if diff < 0:
                #     pulseData[ich] = pulseData[ich] + np.abs(diff)
                # else:
                #     pulseData[ich] = pulseData[ich] - np.abs(diff)
                plt.plot(pulseData[ich], label='CH{}'.format(ich))
            plt.xlabel('Time')
            plt.ylabel('ADC bit')
            plt.title('Averaged Waveform')
            plt.legend(loc="upper right")
            plt.grid()
            plt.savefig('/'.join([self.output_dir, '{}_pulseResponse_{}.png'.format(self.Items[self.tms], self.param)]))
            plt.close()
            # out_dict['waveform_img'] = '/'.join(['.', '{}_pulseResponse_{}.png'.format(self.Items[self.tms], self.param)])

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

        return out_dict
    
    def runAnalysis(self, range_peds=[300, 3000], range_rms=[5,25], range_pulseAmp=[9000,16000], isPosPeak=True, getPulseResponse=True, isRMSNoise=False, pwrcylceN=-1, getWaveforms=False):
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
            pulseResponse = self.PulseResponse(pedestals=pedrms['pedestal']['data'], isPosPeak=isPosPeak, range_pulseAmp=range_pulseAmp, pwrcycleN=pwrcylceN, getWaveform=getWaveforms)
            out_dict['pulseResponse'] = pulseResponse
        # return {"pedrms": pedrms, "pulseResponse": pulseResponse}
        return out_dict

##++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
##************************* STATISTICAL ANALYSIS ***************************************************************
def stat_ana(root_path: str, testItem: str):
    file_list = ['/'.join([root_path, dir, testItem+'.json']) for dir in os.listdir(root_path) if testItem+'.json' in os.listdir('/'.join([root_path, dir]))]
    ## power analysis

    ## pedestal analysis

    ## rms analysis

    ## pospeak analysis

    ## negpeak analysis
    print(file_list)
##++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# # Generate report for one LArASIC
# # --> All parameters for the QC
# class QC_REPORT:
#     def __init__(self, root_path: str, chipID: str):
#         self.input_path = '/'.join([root_path, chipID])
#         self.output_path = '/'.join([root_path, chipID])
#         self.chipID = chipID
#         self.reportName = '{}_report.md'.format(chipID)
#         self.mdfile = self.openMD(reportName=self.reportName)

#     def openMD(self, reportName: str):
#         mdfile = open('/'.join([self.output_path, reportName]), 'w', encoding="utf-8")
#         return mdfile

#     def QC_PWR_report(self):
        
#         pwr_report = "| <h3 style='text-align:center'>Power Consumption</h3> |\n|---|"
#         list_plots = ['/'.join(['.', f]) for f in os.listdir(self.input_path) if 'PWR' in f]
#         keys_pwr = ["Voltage", "Current", "Power"]
#         BLs = ["200mV", "900mV"]
#         ## --- Pulse Response
#         row_pulseResp = "|<div style='display:flex; align-items: center;justify-content: center;'>\
#             <table style='margin-left:auto'>"
#         row_pulseResp += "<tr>"
#         for BL in BLs:
#             plotname = "./QC_PWR_{}_pulseResp.png".format(BL)
#             row_pulseResp += "<td> ![{}Baseline]({}) </td>".format(BL, plotname)
#         print(row_pulseResp)
#         row_pulseResp += "</tr></table></div>|\n"
#         pwr_report = '\n'.join([pwr_report, row_pulseResp])
        
#         self.mdfile.write(pwr_report)
        
    
if __name__ == '__main__':
    # root_path = '../../Data_BNL_CE_WIB_SW_QC'
    # root_path = '../../Analyzed_BNL_CE_WIB_SW_QC/002-06204'
    # qc_report = QC_REPORT(input_path=root_path, output_path=root_path)
    # pwr_qc_dict = qc_report.QC_PWR_report()
    # print(pwr_qc_dict)
    # root_path = '../../Analyzed_BNL_CE_WIB_SW_QC'
    # # stat_ana(root_path=root_path, testItem='QC_CHK_INIT')
    # list_chipID = os.listdir(root_path)
    # for chipID in list_chipID:
    #     bc_ana = BaseClass_Ana(root_path=root_path, chipID=chipID, item='QC_PWR')
    #     sys.exit()
    root_path = '../../Analysis'
    listChips = os.listdir(root_path)
    for chipID in listChips:
        report = QC_REPORT(root_path=root_path, chipID=chipID)
        report.QC_PWR_report()
        sys.exit()
