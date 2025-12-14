# -*- coding: utf-8 -*-
"""
File Name: init_femb.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description:
Created Time: 7/15/2016 11:47:39 AM
Last modified: 4/13/2022 4:00:49 PM
"""

#import scipy
#from numpy import *
#import numpy as np
#import scipy as sp
#import pylab as pl
import numpy as np
import struct
import os

class RAW_CONV():
    def raw_conv_feedloc(self, raw_data):
        smps = int(len(raw_data) //2)
        # print(raw_data);input()
        dataNtuple =struct.unpack_from(">%dH"%(smps),raw_data)
        # print(dataNtuple);input()
        # print(type(dataNtuple));input()
        if (self.jumbo_flag == True):
            pkg_len = int(0x1E06/2)
        else:
            pkg_len = int(0x406/2)

        feed_loc=[]
        pkg_index  = []
        datalength = int( (len(dataNtuple) // pkg_len) -3) * (pkg_len)
        data_rest = raw_data[(datalength + pkg_len)*2:]
        i = int(0)
        k = []
        j = int(0)
        smps_num = 0
        chn_data=[[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],]
        while (i <= datalength ):
            #print (''.join('{:04x} '.format(x) for x in dataNtuple[i:i+pkg_len]) )
            data_a =  ((dataNtuple[i+0]<<16)&0x00FFFFFFFF) + (dataNtuple[i+1]& 0x00FFFFFFFF) + 0x0000000001
            data_b =  ((dataNtuple[i+0+pkg_len]<<16)&0x00FFFFFFFF) + (dataNtuple[i+1+pkg_len]& 0x00FFFFFFFF)
            acc_flg = ( data_a  == data_b )
            face_flg = ((dataNtuple[i+2+6] == 0xface) or (dataNtuple[i+2+6] == 0xfeed))
            #exit()

            if (face_flg == True ) and ( acc_flg == True ) :
                pkg_index.append(i)
                pkg_start = i
                i = i + pkg_len
                onepkgdata = dataNtuple[pkg_start : pkg_start + pkg_len]
                j = 8
                peak_len = 100
                while j < len(onepkgdata) :
                    if (onepkgdata[j] == 0xface ) or (onepkgdata[j] == 0xfeed ):
                        if  (onepkgdata[j] == 0xfeed ):
                            trg_flg = 0x1000
                        else:
                            trg_flg = 0x0000
                        # print(onepkgdata)
                        # print(onepkgdata[j]); input(123)
                        # print(onepkgdata[j+1]); input(123)
                        # print(onepkgdata[j+2]); input(123)
                        # trg_flg = 0x0000
                        chn_data[0].append( trg_flg + ((onepkgdata[j+1] & 0XFFF0)>>4) )
                        chn_data[1].append( trg_flg + ((onepkgdata[j+1] & 0XF)<<8) + ((onepkgdata[j+2] & 0XFF00)>>8) )
                        chn_data[2].append( trg_flg + ((onepkgdata[j+2] & 0XFF)<<4) + ((onepkgdata[j+3] & 0XF000)>>12) )
                        chn_data[3].append( trg_flg + ((onepkgdata[j+3] & 0XFFF)) )

                        chn_data[4].append( trg_flg + ((onepkgdata[j+4] & 0XFFF0)>>4) )
                        chn_data[5].append( trg_flg + ((onepkgdata[j+4] & 0XF)<<8) + ((onepkgdata[j+5] & 0XFF00)>>8) )
                        chn_data[6].append( trg_flg + ((onepkgdata[j+5] & 0XFF)<<4) + ((onepkgdata[j+6] & 0XF000)>>12) )
                        chn_data[7].append( trg_flg + ((onepkgdata[j+6] & 0XFFF)) )

                        chn_data[8].append( trg_flg + ((onepkgdata[j+7] & 0XFFF0)>>4) )
                        chn_data[9].append( trg_flg + ((onepkgdata[j+7] & 0XF)<<8) + ((onepkgdata[j+8] & 0XFF00)>>8) )
                        chn_data[10].append( trg_flg + ((onepkgdata[j+8] & 0XFF)<<4) + ((onepkgdata[j+9] & 0XF000)>>12) )
                        chn_data[11].append( trg_flg + ((onepkgdata[j+9] & 0XFFF)) )

                        chn_data[12].append( trg_flg + ((onepkgdata[j+10] & 0XFFF0)>>4) )
                        chn_data[13].append( trg_flg + ((onepkgdata[j+10] & 0XF)<<8) + ((onepkgdata[j+11] & 0XFF00)>>8) )
                        chn_data[14].append( trg_flg + ((onepkgdata[j+11] & 0XFF)<<4) + ((onepkgdata[j+12] & 0XF000)>>12) )
                        chn_data[15].append( trg_flg + ((onepkgdata[j+12] & 0XFFF)) )

                        if (onepkgdata[j] == 0xfeed ):
                            feed_loc.append(smps_num)
                        smps_num = smps_num + 1
                    else:
                        pass
                    j = j + 13
            else:
                #pass
                i = i + 1
                print("Wrong data at addr = {}".format(i))
                return None

        return chn_data

    def __init__(self):
        self.jumbo_flag = False

