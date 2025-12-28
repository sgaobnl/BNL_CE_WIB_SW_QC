# -*- coding: utf-8 -*-
"""
Created on Mon Sep  9 19:28:25 2019

@author: Edoardo Lopriore
"""
import struct
import sys
import string
import time
import copy

#import visa
import pyvisa as visa
#from visa import VisaIOError

class RIGOL_PS_CTL:
    def ps_init(self):
        rm = visa.ResourceManager()
        rm_list = rm.list_resources()
        try:
            rm_list.index(self.ADDR)
            print ("RigolDP832 generator (%s) is locacted"%self.ADDR)
        except ValueError:
            print ("RigolDP832 generator (%s) is not found, Please check!"%self.ADDR)
            print ("Exit anyway!")
            sys.exit()
        try:
            ps = rm.open_resource(self.ADDR)
        #except VisaIOError:
        except :
            print ("RigolDP832 Initialize--> Exact system name not found")
            print ("Exit anyway!")
            sys.exit()
        self.powerSupplyDevice = ps

    def on(self, channels = [1,2,3]):
        if type(channels) is not list:
            if ((int(channels) < 1) or (int(channels) > 3)):
                print("RigolDP832 Error --> Channel needs to be 1, 2, or 3!  {} was given!".format(channels))
                return
            self.powerSupplyDevice.write(":OUTP CH{}, ON".format(channels))
            if (self.get_on_off(channels) != True):
                print("RigolDP832 Error --> Tried to turn on Channel {} of the Rigol DP832, but it didn't turn on".format(channels))

        else:
            for i in channels:
                if ((int(i) < 1) or (int(i) > 3)):
                    print("RigolDP832 Error --> Channel needs to be 1, 2, or 3!  {} was given!".format(i))
                    return

            for i in channels:
               self.powerSupplyDevice.write(":OUTP CH{}, ON".format(i))
               if (self.get_on_off(i) != True):
                   print("RigolDP832 Error --> Tried to turn on Channel {} of the Rigol DP832, but it didn't turn on".format(i))

        return True

    def off(self, channels = [1,2,3]):
        if type(channels) is not list:
            if ((int(channels) < 1) or (int(channels) > 3)):
                print("RigolDP832 Error --> Channel needs to be 1, 2, or 3!  {} was given!".format(channels))
                return
            self.powerSupplyDevice.write(":OUTP CH{}, OFF".format(channels))
            if (self.get_on_off(channels) != False):
                   print("RigolDP832 Error --> Tried to turn off Channel {} of the Rigol DP832, but it didn't turn off".format(channels))

        else:
            for i in channels:
                if ((int(i) < 1) or (int(i) > 3)):
                    print("RigolDP832 Error --> Channel needs to be 1, 2, or 3!  {} was given!".format(i))
                    return

            for i in channels:
               self.powerSupplyDevice.write(":OUTP CH{}, OFF".format(i))
               if (self.get_on_off(i) != False):
                   print("RigolDP832 Error --> Tried to turn off Channel {} of the Rigol DP832, but it didn't turn off".format(i))

    def get_on_off(self, channel):
        self.powerSupplyDevice.write(":OUTP? CH{}".format(channel))
        #resp = self.powerSupplyDevice.read().strip().decode()
        resp = self.powerSupplyDevice.read().strip()
        status = None
        if (resp == "ON"):
            status = True
        elif (resp == "OFF"):
            status = False
        return (status)

    #Set all useful parameters of a channel.  Will ignore setting parameters that were not explicitly passed as arguments.
    def set_channel(self, channel, voltage = None, current = None, v_limit = None, c_limit = None, vp = None, cp = None):
        if (voltage and current):
            print("RigolDP832 Error --> Can't set both voltage and current for Channel {}".format(channel))

        if (voltage):
            if ((voltage > 0) and (voltage < 30)):
                self.powerSupplyDevice.write(":SOUR{}:VOLT {}".format(channel,voltage))
                self.powerSupplyDevice.write(":SOUR{}:VOLT?".format(channel))
                #response = float(self.powerSupplyDevice.read().strip().decode())
                response = float(self.powerSupplyDevice.read().strip())
                if (response != voltage):
                    print("RigolDP832 Error --> Voltage was set to {}, but response is {}".format(voltage, response))
            else:
                print("RigolDP832 Error --> Voltage must be between 0 and 30 Volts, was {}".format(voltage))

        if (current):
            if ((current > 0) and (current < 3)):
                self.powerSupplyDevice.write(":SOUR{}:CURR {}".format(channel,current))
                self.powerSupplyDevice.write(":SOUR{}:CURR?".format(channel))
                #response = float(self.powerSupplyDevice.read().strip().decode())
                response = float(self.powerSupplyDevice.read().strip())
                if (response != current):
                    print("RigolDP832 Error --> Current was set to {}, but response is {}".format(current, response))
            else:
                print("RigolDP832 Error --> Current must be between 0 and 3 Amps, was {}".format(current))

        if (v_limit):
            if ((v_limit > 0.01) and (v_limit < 33)):
                self.powerSupplyDevice.write(":SOUR{}:VOLT:PROT {}".format(channel,v_limit))
                self.powerSupplyDevice.write(":SOUR{}:VOLT:PROT?".format(channel))
                #response = float(self.powerSupplyDevice.read().strip().decode())
                response = float(self.powerSupplyDevice.read().strip())
                if (response != v_limit):
                    print("RigolDP832 Error --> Voltage protection was set to {}, but response is {}".format(v_limit, response))
            else:
                print("RigolDP832 Error --> OverVoltage protection must be between 0.01 and 30 Volts, was {}".format(v_limit))

        if (c_limit):
            if ((c_limit > 0.001) and (c_limit < 3.3)):
                self.powerSupplyDevice.write(":SOUR{}:CURR:PROT {}".format(channel,c_limit))
                self.powerSupplyDevice.write(":SOUR{}:CURR:PROT?".format(channel))
                #response = float(self.powerSupplyDevice.read().strip().decode())
                response = float(self.powerSupplyDevice.read().strip())
                if (response != c_limit):
                    print("RigolDP832 Error --> Current protection was set to {}, but response is {}".format(c_limit, response))
            else:
                print("RigolDP832 Error --> OverCurrent protection must be between 0.001 and 3.3 Amps, was {}".format(c_limit))

        if (vp):
            if ((vp == "ON") or (vp == "OFF")):
                self.powerSupplyDevice.write(":SOUR{}:VOLT:PROT:STATE {}".format(channel,vp))
                self.powerSupplyDevice.write(":SOUR{}:VOLT:PROT:STATE?".format(channel))
                #response = self.powerSupplyDevice.read().strip().decode()
                response = self.powerSupplyDevice.read().strip()
                if (response != vp):
                    print("RigolDP832 Error --> OverVoltage was set to {}, but response is {}".format(vp, response))
            else:
                print("RigolDP832 Error --> OverVoltage protection must be 'ON' or 'OFF', was {}".format(vp))

        if (cp):
            if ((cp == "ON") or (cp == "OFF")):
                self.powerSupplyDevice.write(":SOUR{}:CURR:PROT:STATE {}".format(channel,cp))
                self.powerSupplyDevice.write(":SOUR{}:CURR:PROT:STATE?".format(channel))
                #response = self.powerSupplyDevice.read().strip().decode()
                response = self.powerSupplyDevice.read().strip()
                if (response != cp):
                    print("RigolDP832 Error --> OverCurrent was set to {}, but response is {}".format(cp, response))
            else:
                print("RigolDP832 Error --> OverCurrent protection must be 'ON' or 'OFF', was {}".format(cp))

    #Returns array of 3 numbers: Voltage, Current and Power
    def measure_params(self,channel):
        if ((int(channel) < 1) or (int(channel) > 3)):
            print("RigolDP832 Error --> Channel needs to be 1, 2, or 3!  {} was given!".format(channel))
            return

        self.powerSupplyDevice.write(":MEAS:ALL? CH{}".format(channel))
        response = (self.powerSupplyDevice.read().strip().split(","))
        for i in range(len(response)):
            response[i] = float(response[i])
        return response

    def beep(self):
        self.powerSupplyDevice.write(":SYSTem:BEEPer:IMMediate")
        return True


    #__INIT__#
    def __init__(self):
        self.ADDR = u'USB0::0x1AB1::0x0E11::DP8C184550811::INSTR'
        self.gen = None

if __name__ == '__main__':
    ps = RIGOL_PS_CTL()
    ps.ps_init()
    ps.set_channel(1,voltage=12, v_limit=14, c_limit=2)
    ps.set_channel(2,voltage=12, v_limit=14, c_limit=2)
    ps.beep()
    ps.on(channels=[1,2])
    #ps.off(channels=[1,2])
