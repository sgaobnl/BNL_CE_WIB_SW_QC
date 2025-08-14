'''
    Description:
        This script is used to convert the binary data (.bin) to hdf5 format. One output file will
        have the data for 8 ASICs.
        The goal is to only convert the binary file, not decoding it.
    Input:
        - Binary file from the LArASIC QC.
    Output:
        - HDF5 format version of the binary file.
'''

import os, sys
import h5py, pickle
import numpy as np
import re
# import matplotlib.pyplot as plt

# from utils import decodeRawData # can be ignored, only used for test

def read_bin(filename, path_to_file):
    with open('/'.join([path_to_file, filename]), 'rb') as f:
        data = pickle.load(f)
        return data
    
def write_hdf5(f, data, group_name='/'):
    if group_name!='/':
        grp = f.create_group(group_name)
    else:
        grp = f
    for key,val in data.items():
        if isinstance(val, dict):
            if 'attrs' in key:
                for k, v in val.items():
                    grp.attrs[k] = v
            else:
                write_hdf5(f, val, group_name=f'{group_name}/{key}')
        else:
            grp.create_dataset(key,data=val)

def get_allKeys(data):
    '''
        This function extracts the keys that are specific to the item being tested during the QC.
    '''
    SpecificKeys_inBin = []
    GeneralKeys_inBin = []
    for key in data.keys():
        if isinstance(data[key], tuple) | isinstance(data[key], list):
        # if (key not in GeneralKeys_inBin) & (key != LogKey) & (key != 'QCstatus'):
            SpecificKeys_inBin.append(key)
        else:
            GeneralKeys_inBin.append(key)
    return SpecificKeys_inBin, GeneralKeys_inBin

def specKeyData2Dict(data, specKeys_list):
    # Attributes should be added to the dictionary of the spy buffer data (all_spybuff) and assigned to the key 'attrs'
    # Use a dictionary to store all the attributes you want to include in the hdf5 file
    all_data_dict = dict()
    for i, speckey in enumerate(specKeys_list):
        speckeyData = data[speckey]
        fembs = speckeyData[0]
        # converting the fembs list to numpy array
        fembs_np = np.array(tuple(fembs), dtype=int)

        rawdata = speckeyData[1]
        # converting the rawdata (hex) list to a numpy array where each element is an object type
        all_spybuff = dict()
        N_spybuff = len(rawdata)
        for ispy_buff in range(N_spybuff):
            rawdata_dict = rawdata2numpy_dict(rawdata=rawdata, spy_buff=ispy_buff)
            all_spybuff[f'trigger{ispy_buff}'] = rawdata_dict

        config = speckeyData[2]
        if isinstance(config, list):
            # converting configurations list (one element) to dictionary
            config_dict = config2dict(config_data=config)

        # Adding attributes
        N_triggers = len(list(all_spybuff.keys()))
        all_spybuff['attrs'] = {'N_trigger': N_triggers}

        pwrcons = speckeyData[3]
        if isinstance(pwrcons, dict):
            # converting the power consumptions to numpy array with custom dtype
            new_pwrcons_dict  = {}
            for key, val in pwrcons.items():
                val_np = np.array(tuple(val), dtype=np.dtype([('V', np.float32), ('I', np.float32), ('P', np.float32)]))
                # val_dict = {
                #     'V' : val[0],
                #     'I' : val[1],
                #     'P' : val[2] 
                # }
                new_pwrcons_dict[key] = val_np
            new_pwrcons_dict['attrs'] = {'Info': 'Power consumption for each ASIC for each power rail',
                                         'unit_V': 'V',
                                         'unit_I': 'mA',
                                         'unit_P': 'mW'}
            speckeyData_dict = {'fembs': fembs_np, 'pwrcons': new_pwrcons_dict, 'rawdata': all_spybuff}
            speckeyData_dict['attrs'] = {'fembs': 'FEMBs used (tuple)',
                                         'pwrcons': 'Power consumption in the format np.array([V, I, P])',
                                         'rawdata': 'Spy buffer'}
        else:
            speckeyData_dict = {'fembs': fembs_np, 'rawdata': all_spybuff}
            speckeyData_dict['attrs'] = {'fembs': 'FEMBs used (tuple)',
                                         'rawdata': 'Spy buffer'}
        if isinstance(config, list):
            speckeyData_dict['config'] = config_dict
        
        all_data_dict[speckey] = speckeyData_dict
    return all_data_dict

def config2dict(config_data):
    # to maintain the same format as the original data, the output should be a list with just one element which is a tuple with one element
    # cfg_paras_rec.append( (femb_id, copy.deepcopy(self.adcs_paras), copy.deepcopy(self.regs_int8), adac_pls_en, self.cd_sel) )
    # femb_id
    femb_id = config_data[0][0]
    # print(femb_id)
    # adcs_paras
    adcs_paras = config_data[0][1]
    # regs_int8
    regs_int8 = config_data[0][2]
    # adac_pls_en
    adac_pls_en = config_data[0][3]
    # cd_sel
    cd_sel = config_data[0][4]

    out_dict = {'femb_id': femb_id,
                'adc_paras': adcs_paras,
                'regs_int8': regs_int8,
                'adac_pls_en': adac_pls_en,
                'cd_sel': cd_sel}
    return out_dict

def rawdata2numpy_dict(rawdata, spy_buff=0):
    spy_buff_data = rawdata[spy_buff]
    # Structure of the spy_buff_data
    '''
        It is a tuple with 4 elements:
            a. 1st element: [bytearray, None, None, None, None, None, None]
            b. 2nd, 3rd, 4th elements: 0, 32767, 0 ==> (data0 = (rawdata, buf_end_addrs[fembs[0]*2], spy_rec_ticks, trig_cmd))
        Conversion steps:
            1. Convert the 1st element to a numpy array where 1st element is 
    '''
    out_spy_buff_data = {'femb_data': {}, 'buf_end_addrs': 0, 'spy_rec_ticks': 0, 'trig_cmd': 0}
    params = {1: 'buf_end_addrs', 2: 'spy_rec_ticks', 3: 'trig_cmd'}
    for i_tmp, tmpdata in enumerate(spy_buff_data):
        if type(tmpdata)==list:
            data = tmpdata
            # out_data = []
            out_data = {}
            ifemb = 0
            for i, d in enumerate(data):
                if i%2 ==0:
                    if d==None:
                        # out_data[f'femb{ifemb}'] = {f'buff{i%2}': np.nan}
                        pass
                    else:     
                        # out_data[f'femb{ifemb}'] = {f'buff{i%2}': np.frombuffer(d, dtype=np.uint8)}
                        out_data = {f'buff{i%2}': np.frombuffer(d, dtype=np.uint8)}
                else:
                    if d==None:
                        # out_data[f'femb{ifemb}'][f'buff{i%2}'] = np.nan
                        pass
                    else:
                        # out_data[f'femb{ifemb}'][f'buff{i%2}'] = np.frombuffer(d, dtype=np.uint8)
                        out_data[f'buff{i%2}'] = np.frombuffer(d, dtype=np.uint8)
                    ifemb += 1

            # out_spy_buff_data['femb_data'] = out_data
            out_spy_buff_data = out_data
        else:
            out_spy_buff_data[params[i_tmp]] = tmpdata
        # out_spy_buff_data['attrs'] = {'N_fembs': 'Number of FEMBs used'}
    return out_spy_buff_data

################# Conversion back to HEX #############################################################
# def hdf5_oneSpyBuff2HEX(hdf5_spy_buffData):
#     '''
#         We need to convert back to bytearray in order to be able to use the script wib_dec developed before.
#     '''
#     spy_buff_data = hdf5_spy_buffData
#     grp = spy_buff_data
#     arrays = grp['data_arrays'][:]
#     mask = grp['data_mask'][:]
#     array_list = [bytearray(arrays[i].tobytes()) if mask[i] else None for i in range(len(arrays))]
#     values = grp['values'][:]
#     spy_buff_HEX = (array_list,) + tuple(values)
#     return spy_buff_HEX

# def hdf5Rawdata2HEX(wholeHDF5data, specKey):
#     '''
#         Convert the hdf5 data (spy_buffer) to hex
#     '''
#     hdf5Rawdata = wholeHDF5data[specKey]['rawdata']
#     hdf5Rawdata_inHEX = []
#     for spy_buff_i, spy_buff_data in hdf5Rawdata.items():
#         spy_buff_HEX = hdf5_oneSpyBuff2HEX(hdf5_spy_buffData=spy_buff_data)
#         hdf5Rawdata_inHEX.append(spy_buff_HEX)
#     return hdf5Rawdata_inHEX
###############################################################################################


def PWRON(pwron_data):
    out_pwron = dict()
    for key, val in pwron_data.items():
        pwrdtype = np.dtype([('V', np.float32), ('I', np.float32), ('P', np.float32)])
        out_pwron[key] = np.array(tuple(val), dtype=pwrdtype)
    out_pwron['attrs'] = {'Info': 'The power consumption is in the format (V, I, P)'}
    return out_pwron

def binWithoutRAW2dict(data, FileName='QC_MON.bin'):
    '''
        This function is used to convert the data from the binary files without raw data to dictionary format.
        Input:
            data from the binary file, output of the read_bin function.
        Output:
            dictionary format of the input data.
    '''
    speckey_list, GeneralKeys_inBin = get_allKeys(data=data)
    # print(speckey_list)
    # print(GeneralKeys_inBin)
    out_data = dict()
    if 'MON' in FileName:
        # print(data['logs'])
        custom_dtype = np.dtype([(f'FE{ichip}', np.float32) for ichip in range(8)])
        for speckey in speckey_list:
            if speckey in ['VBGR', 'MON_Temper', 'MON_VBGR']:
                # custom_dtype = np.dtype([(f'FE{ichip}', np.float32) for ichip in range(8)])
                tmp_dict = {
                    'datas' : np.array(tuple(data[speckey][0]), dtype=custom_dtype), # ADC bit
                    'data_v': np.array(tuple(data[speckey][1]), dtype=custom_dtype) # in the unit of AD_LSB : datas*AD_LSB
                }
                out_data[speckey] = tmp_dict
            elif speckey in ['MON_200BL', 'MON_900BL']:
                # custom_dtype = np.dtype([(f'FE{ichip}', np.float32) for ichip in range(8)])
                tmp_dict = {f'CHN_{data[speckey][ichn][0]}' : np.array(tuple(data[speckey][ichn][1]), dtype=custom_dtype) for ichn in range(16)}
                out_data[speckey] = tmp_dict
            else:
                tmp_dict = {f'DAC_{data[speckey][idac][0]}' : np.array(tuple(data[speckey][idac][1]), dtype=custom_dtype) for idac in range(len(data[speckey]))}
                out_data[speckey] = tmp_dict
        for key in GeneralKeys_inBin:
            out_data[key] = data[key]
    else:
        # print(data['WIB_UTC_Date_Time'])
        # keys_for_report = [key for key in GeneralKeys_inBin if ('QC' not in key) & ('WIB' not in key) & ('PC' not in key) & ('tms' not in key) & ('pc' not in key)]
        keys_for_report = [key for key in GeneralKeys_inBin if ('QC' not in key) & ('WIB' not in key) & ('PC' not in key) & ('tms' not in key)]
        # print(keys_for_report)
        for key in keys_for_report:
            # if key=='tms_items':
            #     tmp_dict = dict()

            #     for key1, val1 in data[key].items():
            #         val1 = val1.replace('\x1b[96m ', '').replace('\x1b[0m', '')
            #         tmp_dict[key1] = val1
            #     print(tmp_dict)
            #     out_data[key] = tmp_dict
            # else:
                out_data[key] = data[key]
    return out_data

def bin2dict(data): # for binary files except QC.log and QC_MON.bin
    speckey_list, GeneralKeys_inBin = get_allKeys(data=data)
    out_data = dict()
    for key in GeneralKeys_inBin:
        if 'PWRON' in key:
            out_data[key] = PWRON(pwron_data=data[key])
        elif 'status' in key:
            pass
        else:
            out_data[key] = data[key]
    data = specKeyData2Dict(data=data, specKeys_list=speckey_list)
    for key, val in data.items():
        out_data[key] = val
    return out_data
    

if __name__ == '__main__':
    # root_path = 'D:/RTS_tmp/B010T0001/Time_20240701171351_DUT_0000_1001_2002_3003_4004_5005_6006_7007/RT_FE_002010000_002020000_002030000_002040000_002050000_002060000_002070000_002080000'
    root_path = 'E:/B009T0008/Time_20250527114445_DUT_0000_1001_2002_3003_4004_5005_6006_7007/RT_FE_001000001_001000002_001000003_001000004_001000005_001000006_001000007_001000008/'
    output_path = 'tmp'
    try:
        os.makedirs(output_path)
    except:
        pass
    # binFileName = 'QC_MON.bin'
    list_bin_files = os.listdir(root_path)
    # print(list_bin_files)
    # sys.exit()
    for binFileName in list_bin_files:
        hdf5_name = binFileName.split('.')[0] + '.hdf5'
        # with h5py.File('/'.join(['D:/RTS_tmp/B010T0001/Time_20240701171351_DUT_0000_1001_2002_3003_4004_5005_6006_7007/RT_FE_002010000_002020000_002030000_002040000_002050000_002060000_002070000_002080000', hdf5_name]), 'w') as f:
        with h5py.File('/'.join([output_path, hdf5_name]), 'w') as f:
            data = read_bin(filename=binFileName, path_to_file=root_path)
            try:    
                data0 = bin2dict(data=data)
                print(hdf5_name)
                write_hdf5(f=f, data=data0)
            except:
                data1 = binWithoutRAW2dict(data=data, FileName=binFileName)
                write_hdf5(f=f, data=data1)
