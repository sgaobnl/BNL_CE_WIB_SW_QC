import sys
import numpy as np
import copy
import time, datetime, random, statistics    
import os
import argparse

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


def dat_read_cfg(infile_mode = True, froot = "./tmp_data/" ):
    logs={}
    if infile_mode:
        logs={}
        logs['date']=datetime.datetime.now().strftime("%m_%d_%Y_%H_%M_%S")
        index_f = "./asic_info.csv"
        with open(index_f, 'r') as fp:
            for cl in fp:
                tmp = cl.split(",")
                tmp = tmp[:-1]
                logs[tmp[0]] = tmp[1]
        cd_id = {}
        for cd in range(2):
            dkey = "CD%d"%cd
            cdstr=logs[dkey]
            cd_id['CD{}'.format(cd)] = cdstr[0:4]+cdstr[4:]

        adc_id = {}
        for adc in range(8):
            dkey = "ADC%d"%adc
            adcstr=logs[dkey]
            adc_id['ADC{}'.format(adc)] = adcstr[0:4]+adcstr[5:]

        fe_id = {}
        for fe in range(8):
            dkey = "FE%d"%fe
            festr=logs[dkey]
            if festr[3] == ("1") :
                fe_id['FE{}'.format(fe)] = festr[0:3]+"1"+festr[4:]
            else:
                fe_id['FE{}'.format(fe)] = festr[0:3]+"0"+festr[4:]

    if "CD" in logs['DUT']:
        fsubdir = "CD_{}_{}".format(cd_id['CD0'],cd_id['CD1']) 
    elif "ADC" in logs['DUT']:
        fsubdir = "ADC_{}_{}_{}_{}_{}_{}_{}_{}".format(adc_id['ADC0'],adc_id['ADC1'], adc_id['ADC2'], adc_id['ADC3'], adc_id['ADC4'], adc_id['ADC5'], adc_id['ADC6'], adc_id['ADC7']) 
    elif "FE" in logs['DUT']:
        fsubdir = "FE_{}_{}_{}_{}_{}_{}_{}_{}".format(fe_id['FE0'],fe_id['FE1'], fe_id['FE2'], fe_id['FE3'], fe_id['FE4'], fe_id['FE5'], fe_id['FE6'], fe_id['FE7']) 
    fdir = froot + fsubdir + "/"
    return logs,  fdir
