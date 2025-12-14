# -*- coding: utf-8 -*-
"""
File Name: cls_udp.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 3/20/2019 4:52:43 PM
Last modified: 4/12/2022 11:52:26 AM
"""

# defaut setting for scientific caculation
# import numpy
# import scipy
# from numpy import *
# import numpy as np
# import scipy as sp
# import pylab as pl

import struct
import sys
import string
import socket
import time
import copy
from socket import AF_INET, SOCK_DGRAM
import codecs


class CLS_UDP:
    def write_reg(self, reg, data):
        regVal = int(reg)
        if (regVal < 0) or (regVal > self.MAX_REG_NUM):
            return None
        dataVal = int(data)
        if (dataVal < 0) or (dataVal > self.MAX_REG_VAL):
            return None

        # crazy packet structure require for UDP interface
        dataValMSB = ((dataVal >> 16) & 0xFFFF)
        dataValLSB = dataVal & 0xFFFF
        WRITE_MESSAGE = struct.pack('HHHHHHHHH', socket.htons(self.KEY1), socket.htons(self.KEY2), socket.htons(regVal),
                                    socket.htons(dataValMSB),
                                    socket.htons(dataValLSB), socket.htons(self.FOOTER), 0x0, 0x0, 0x0)

        # send packet to board, don't do any checks
        sock_write = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Internet, UDP
        sock_write.setblocking(0)
        sock_write.sendto(WRITE_MESSAGE, (self.UDP_IP, self.UDP_PORT_WREG))
        sock_write.close()

    def read_reg(self, reg):
        regVal = int(reg)
        if (regVal < 0) or (regVal > self.MAX_REG_NUM):
            return -1

        # set up listening socket, do before sending read request
        sock_readresp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Internet, UDP
        sock_readresp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock_readresp.bind(('', self.UDP_PORT_RREGRESP))
        sock_readresp.settimeout(1)

        # crazy packet structure require for UDP interface
        READ_MESSAGE = struct.pack('HHHHHHHHH', socket.htons(self.KEY1), socket.htons(self.KEY2), socket.htons(regVal),
                                   0, 0, socket.htons(self.FOOTER), 0, 0, 0)
        sock_read = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Internet, UDP
        sock_read.setblocking(0)
        sock_read.sendto(READ_MESSAGE, (self.UDP_IP, self.UDP_PORT_RREG))
        sock_read.close()

        # try to receive response packet from board, store in hex
        data = []
        try:
            data = sock_readresp.recv(4 * 1024)
        except socket.timeout:
            self.udp_timeout_cnt = self.udp_timeout_cnt + 1
            sock_readresp.close()
            return -2
            # dataHex = data.encode('hex')
        # dataHex = codecs.encode(bytes(data, 'utf-8'), 'hex')
        dataHex = codecs.encode(data, 'hex')
        sock_readresp.close()

        # extract register value from response
        if int(dataHex[0:4], 16) != regVal:
            return -3
        dataHexVal = int(dataHex[4:12], 16)
        return dataHexVal

    def write_reg_wib(self, reg, data):
        self.write_reg(reg, data)

    def read_reg_wib(self, reg):
        dataHex = self.read_reg(reg)
        return dataHex

    def write_reg_wib_checked(self, reg, data):
        i = 0
        while (i < 10):
            self.write_reg_wib(reg, data)
            self.wib_wr_cnt = self.wib_wr_cnt + 1
            rdata = self.read_reg_wib(reg)
            rdata = self.read_reg_wib(reg)
            if (data == rdata):
                break
            else:
                i = i + 1
                self.wib_wrerr_cnt = self.wib_wrerr_cnt + 1
                time.sleep(abs(i - 1 + 0.001))
        if i >= 10:
            print("readback value is different from written data, %d, %x, %x" % (reg, data, rdata))
            sys.exit()

    def get_rawdata(self):
        # set up listening socket
        sock_data = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Internet, UDP
        sock_data.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock_data.bind(('', self.UDP_PORT_HSDATA))
        sock_data.settimeout(1)
        # receive data, don't pause if no response
        try:
            # data = sock_data.recv(8*1024)
            data = sock_data.recv(9014)
        except socket.timeout:
            self.udp_hstimeout_cnt = self.udp_hstimeout_cnt + 1
            print("FEMB_UDP--> Error get_data: No data packet received from board, quitting")
            data = []
        sock_data.close()
        return data

    def get_rawdata_packets(self, val):
        numVal = int(val)
        if (numVal < 0):
            print("FEMB_UDP--> Error record_hs_data: Invalid number of data packets requested")
            return None
        timeout_cnt = 0
        # set up listening socket
        sock_data = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Internet, UDP
        sock_data.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock_data.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 8192000)
        sock_data.bind(('', self.UDP_PORT_HSDATA))
        sock_data.settimeout(1)
        rawdataPackets = []
        for packet in range(0, numVal, 1):
            data = None
            try:
                data = sock_data.recv(8192)
                # print(data)
                # input()
            except socket.timeout:
                print("ERROR: UDP timeout")
                self.udp_hstimeout_cnt = self.udp_hstimeout_cnt + 1
                sock_data.close()
                return None
            #                if (timeout_cnt == 5):
            #                    sock_data.close()
            #                    print ("ERROR: UDP timeout, Please check if there is any conflict (someone else try to control WIB at the same time), continue anyway")
            #                    return None
            #                else:
            #                    timeout_cnt = timeout_cnt + 1
            #                    self.write_reg_wib_checked (15, 0)
            #                    print ("ERROR: UDP timeout,  Please check if there is any conflict, Try again in 3 seconds")
            #                    continue
            if data != None:
                rawdataPackets.append(data)
        sock_data.close()

        if len(rawdataPackets) != 0:
            rawdata = b''.join(rawdataPackets)
        return rawdata

    ########################################################################################################
    # __INIT__#
    def __init__(self):
        self.UDP_IP = "192.168.121.2"
        self.KEY1 = 0xDEAD
        self.KEY2 = 0xBEEF
        self.FOOTER = 0xFFFF
        self.UDP_PORT_WREG = 32000
        self.UDP_PORT_RREG = 32001
        self.UDP_PORT_RREGRESP = 32002
        self.UDP_PORT_HSDATA = 32003
        self.MAX_REG_NUM = 0x666
        self.MAX_REG_VAL = 0xFFFFFFFF
        self.MAX_NUM_PACKETS = 1000000

        self.jumbo_flag = False
        self.wib_wr_cnt = 0
        self.wib_wrerr_cnt = 0
        self.udp_timeout_cnt = 0
        self.udp_hstimeout_cnt = 0

