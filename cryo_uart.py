# -*- coding: utf-8 -*-
"""
Created on Mon Sep  9 11:00:21 2019

"""

import os
import sys
import time
import os.path
import serial

from colorama import just_fix_windows_console
just_fix_windows_console()

####### Input test information #######
#Red = '\033[91m'
#Green = '\033[92m'
#Blue = '\033[94m'
#Cyan = '\033[96m'
#White = '\033[97m'
#Yellow = '\033[93m'
#Magenta = '\033[95m'
#Grey = '\033[90m'
#Black = '\033[90m'
#Default = '\033[99m'

class cryobox:
    def __init__(self):
        self.cmd_dict={}
        self.cmd_dict[b'0'] = b'Setting STATE to 0 (AutoFill)'
        self.cmd_dict[b'1'] = b'Setting STATE to 1 (IDLE)'
        self.cmd_dict[b'2'] = b'Setting STATE to 2 (TC Warming)'
        self.cmd_dict[b'3'] = b'Setting STATE to 3 (TC LN2 Puddle)'
        self.cmd_dict[b'4'] = b'Setting STATE to 4 (TC LN2 Immersion)'

    def cryo_create(self):
        self.ser = serial.Serial('COM4', 9600, timeout=0, parity=serial.PARITY_NONE)
        print ("cryogenic box is connected")

    def cryo_close(self):
        self.ser.close()
        print ("cryogenic box is disconnected")

    def cryo_cmd(self, mode=b'1'):
        rd = b''
        while True:
            self.ser.write(mode)
            for i in range(2):
                time.sleep(1)
                rd = rd + self.ser.read(4096)
            if self.cmd_dict[mode] in rd:
                print ("\033[92m", self.cmd_dict[mode], "\033[0m")
                if mode!=b'0': #readback status
                    self.ser.write(b'm')
                    for i in range(2):
                        time.sleep(1)
                        rd = rd + self.ser.read(4096)
                    if b'State= ' + mode in rd:
                        print (rd)
                        break
                    else:
                        pass
                else:
                    break
        return rd

    def cryo_fill(self):
        self.cryo_create()
        fill_flg = True
        while fill_flg:
            try:
                print ("Start fill 50L dewar...")
                print ("\033[93m If 22psi dewar is empty, please \033[91m Ctrl + C (only once) \033[0m")
                #while True: #to be decided later if needed
                #    yorn = input("Please open value of 22psi dewar : ")
                #    if "Y" in yorn or "y" in yorn:
                #        break
                rd = self.cryo_cmd(mode=b'0')
                while True:
                    time.sleep(1)
                    tmp = self.ser.read(4096)
                    if tmp!=b'':
                        print (tmp)
                        rd = rd + tmp
                    if b'AutoFill ended. Setting State 2 (Warm/Purge)' in rd:
                        fill_flg = False
                        #while True: #to be decided later if needed
                        #    yorn = input("Please close value of 22psi dewar : ")
                        #    if "Y" in yorn or "y" in yorn:
                        #        break
                        break
                rd += self.cryo_cmd(mode=b'1')
            except KeyboardInterrupt:
                fill_flg = True
                rd += self.cryo_cmd(mode=b'1')
                print ("Please shut down valve of 22psi dewar")
                while True:
                    yorn = input("Is 22pis Dewar \033[91m value CLOSE \033[0m completely?(y or n) : ")
                    if "Y" in yorn or "y" in yorn:
                        while True:
                            confirmed = input("Double confirmed?(Type in exactly: \033[91m confirmed \033[0m) : ")
                            if confirmed == 'confirmed':
                                print ("Please replace the dewar with a full one")
                                while True:
                                    yorn = input("New full dewar in position and hose tighted?(y or n) : ")
                                    if "Y" in yorn or "y" in yorn:
                                        print ("Please open the valve of 22psi dewar")
                                        break
                                break
                        break
                    else:
                        pass
#                raise
        self.cryo_close()

        return rd

    def cryo_warmup(self, waitminutes = 20):
        self.cryo_create()
        rd = self.cryo_cmd(mode=b'2')
        self.cryo_close()
        print ("Please wait %d minutes..."%waitminutes)
        time.sleep(waitminutes*60)
        self.cryo_create()
        rd = self.cryo_cmd(mode=b'1')
        self.cryo_close()
        return rd

    def cryo_lowlevel(self, waitminutes = 10):
        self.cryo_create()
        rd = self.cryo_cmd(mode=b'3')
        self.cryo_close()
        print ("Please wait %d minutes..."%waitminutes)
        time.sleep(waitminutes*60)

    def cryo_highlevel(self, waitminutes = 5):
        self.cryo_create()
        rd = self.cryo_cmd(mode=b'4')
        self.cryo_close()
        print ("Please wait %d minutes..."%waitminutes)
        time.sleep(waitminutes*60)
                   
                    
if __name__=="__main__":
    cryo=cryobox()
    #cryo.cryo_fill()
    #cryo.cryo_lowlevel(waitminutes=10)
    #cryo.cryo_highlevel(waitminutes=5)
    #cryo.cryo_highlevel(waitminutes=60)
#    input ("Wait...")
    cryo.cryo_warmup(waitminutes=0.1)
    #cryo.cryo_close()

