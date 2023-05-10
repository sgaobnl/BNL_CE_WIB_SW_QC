#This script makes .pdf files from the outputs of LArASIC_test.py script.
#This makes 8 .pdf at ./output/ directory for each chip, which contains voltages tables, 
#plots for measured current, and pulse response plot for each FEMB configuration.
#

from wib_cfgs import WIB_CFGS
import time
import sys
import numpy as np
import pickle
import copy
import time, datetime, random, statistics    
import csv
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
from fpdf import FPDF
    
#inputFile = "./tmp_data/rawDataCurrent.bin"
inputFile = "./tmp_data/rawDataCurrent.bin"
inputPulseFile = "./tmp_data/rawDataPulse.bin"

bufferStatus = ['SE=OFF, SEDC=OFF, 900mV BL', 'SE=ON, SEDC=OFF, 900mV BL', 'SE=OFF, SEDC=ON, 900mV BL', 
        'SE=OFF, SEDC=OFF, 200mV BL', 'SE=ON, SEDC=OFF, 200mV BL', 'SE=OFF, SEDC=ON, 200mV BL']
channels = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]

#raw data for power measurement
with open(inputFile, 'rb') as f:
    rawDataCurrent = pickle.load(f)
#raw data for pulse response
with open(inputPulseFile, 'rb') as f:
    rawDataPulse = pickle.load(f)

def GetPulsePlot(feNumber, configurationIndex):
    fig, ax = plt.subplots()
    tempCurrentPointsMax = GetPulsePoints(feNumber,configurationIndex, 0)
    tempCurrentPointsPad = GetPulsePoints(feNumber,configurationIndex, 1)
    line1, = ax.plot(channels, tempCurrentPointsMax, label = "max", marker = 'o')
    line2, = ax.plot(channels, tempCurrentPointsPad, label = "pad", marker = 'o')
    ax.set_title('FE' + str(feNumber) + bufferStatus[configurationIndex - 1])
    plt.ylabel('Measured pulse')
    plt.xlabel('channels')
    ax.grid(True)
    return plt

def GetPulsePoints(feNumber, configurationIndex, max_or_pad): #0: max, 1: pad
    tempPoints = []
    for chn in range(16):
        tempPoints.append(rawDataPulse[feNumber][configurationIndex][chn][max_or_pad])
        print(rawDataPulse[feNumber][configurationIndex][chn][max_or_pad])
    return tempPoints

def GetCurrentPlot(feNumber, snc):
    fig, ax = plt.subplots()
    bufferStatus1 = ['SE=OFF, SEDC=OFF', 'SE=ON, SEDC=OFF', 'SE=OFF, SEDC=ON']
    bufferStatus2 = ['SE=OFF, SEDC=OFF', 'SE=ON, SEDC=OFF', 'SE=OFF, SEDC=ON']
    bufferStatus3 = ['SE=OFF, SEDC=OFF', 'SE=ON, SEDC=OFF', 'SE=OFF, SEDC=ON']
    tempCurrentPoints1 = GetCurrentPoints(feNumber,2,snc)
    tempCurrentPoints2 = GetCurrentPoints(feNumber,0,snc)
    tempCurrentPoints3 = GetCurrentPoints(feNumber,1,snc)
    line1, = ax.plot(bufferStatus1 , tempCurrentPoints1, label = "VPPP", marker = 'o')
    line2, = ax.plot(bufferStatus2 , tempCurrentPoints2, label = "VDD", marker = 'o')
    line3, = ax.plot(bufferStatus3 , tempCurrentPoints3, label = "VDDO", marker = 'o')
    if (snc == 0):
        ax.set_title('FE' + str(feNumber) + ', 900mV BL')
    if (snc == 1):
        ax.set_title('FE' + str(feNumber) + ', 200mV BL')
    ax.legend(handles=[line1, line2, line3])
    plt.ylabel('Measured Current (mA)')
    plt.xlabel('Buffer Status')
    for index in range(len(bufferStatus1)):
      ax.text(bufferStatus1[index], round(tempCurrentPoints1[index], 1), round(tempCurrentPoints1[index], 1), size=12)
      ax.text(bufferStatus2[index], round(tempCurrentPoints2[index], 1), round(tempCurrentPoints2[index], 1), size=12)
      ax.text(bufferStatus3[index], round(tempCurrentPoints3[index], 1), round(tempCurrentPoints3[index], 1), size=12)
    ax.grid(True)
    return plt

def GetCurrentPoints(feNumber, vIndex, snc) :   #vIndex: 0 = VDD, 1 = VDDO, 2 = VPPP snc: 0 = 900mV, 1 = 200mV
    tempPoints = []
    tempKey = 'FE' + str(feNumber) + '_'
    if (vIndex == 0): 
        tempKey += 'VDD'
    if (vIndex == 1): 
        tempKey += 'VDDO'
    if (vIndex == 2): 
        tempKey += 'VPPP'
    if (snc == 0):
        tempPoints.append(rawDataCurrent[feNumber][1][tempKey][1])
        tempPoints.append(rawDataCurrent[feNumber][2][tempKey][1])
        tempPoints.append(rawDataCurrent[feNumber][3][tempKey][1])
    if (snc == 1):
        tempPoints.append(rawDataCurrent[feNumber][4][tempKey][1])
        tempPoints.append(rawDataCurrent[feNumber][5][tempKey][1])
        tempPoints.append(rawDataCurrent[feNumber][6][tempKey][1])
    return tempPoints

def MakePDF(feNumber):
    print ('making result pdf for fe{}'.format(feNumber))
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Times', '', 24)
    pdf.cell(0, 20, 'Power Measurement', 0, 1, 'C')
    pdf.set_font('Times', '', 12)
    FE = 'FE' + str(feNumber) + '_'
    FE_VDD = FE + 'VDD'
    FE_VDDO = FE + 'VDDO'
    FE_VPPP = FE + 'VPPP'
    FE_V = [FE_VDD, FE_VDDO, FE_VPPP]
    #tempConfigurationIndex = 0
    for tempConfigurationIndex in range(6):
        if (tempConfigurationIndex == 0): 
            pdf.cell(60, 10, 'SE=OFF SEDC=OFF', 1, 0, 'C')
            pdf.cell(60, 10, '900mV (BL)', 1, 0, 'C')
        if (tempConfigurationIndex == 1): 
            pdf.cell(60, 10, 'SE=ON SEDC=OFF', 1, 0, 'C')
            pdf.cell(60, 10, '900mV (BL)', 1, 0, 'C')
        if (tempConfigurationIndex == 2): 
            pdf.cell(60, 10, 'SE=OFF SEDC=ON', 1, 0, 'C')
            pdf.cell(60, 10, '900mV (BL)', 1, 0, 'C')
        if (tempConfigurationIndex == 3): 
            pdf.cell(60, 10, 'SE=OFF SEDC=OFF', 1, 0, 'C')
            pdf.cell(60, 10, '200mV (BL)', 1, 0, 'C')
        if (tempConfigurationIndex == 4): 
            pdf.cell(60, 10, 'SE=ON SEDC=OFF', 1, 0, 'C')
            pdf.cell(60, 10, '200mV (BL)', 1, 0, 'C')
        if (tempConfigurationIndex == 5): 
            pdf.cell(60, 10, 'SE=OFF SEDC=ON', 1, 0, 'C')
            pdf.cell(60, 10, '200mV (BL)', 1, 0, 'C')
        #tempConfigurationIndex += 1
        pdf.cell(60, 10, '', 1, 1, 'C')
        pdf.cell(60, 10, 'Power Rail', 1, 0, 'C')
        pdf.cell(60, 10, 'Voltages (V)', 1, 0, 'C')
        pdf.cell(60, 10, 'Current (mA)', 1, 1, 'C')
        tempPower = 0
        tempIndex = 0;

        for v in FE_V:
            pdf.cell(60, 10, v, 1, 0, 'C')
            pdf.cell(60, 10, str(rawDataCurrent[feNumber][tempConfigurationIndex + 1][v][0]), 1, 0, 'C')
            pdf.cell(60, 10, str(rawDataCurrent[feNumber][tempConfigurationIndex + 1][v][1]), 1, 1, 'C')
            tempPower += rawDataCurrent[feNumber][tempConfigurationIndex + 1][v][2]
        pdf.cell(60, 10, 'Power (mW/Ch)', 1, 0, 'C')
        pdf.cell(60, 10, str(tempPower), 1, 0, 'C')
        pdf.cell(60, 10, '', 1, 1, 'C')
        pdf.cell(0, 10, '', 0, 1, 'C')

        tempPlot = GetPulsePlot(feNumber, tempConfigurationIndex + 1)
        tempPlot.savefig('./output/plots/FE{}_pulse_{}.png'.format(feNumber, tempConfigurationIndex + 1))

    tempPlot = GetCurrentPlot(feNumber,0)
    tempPlot.savefig('./output/plots/FE{}_900mV.png'.format(feNumber))
    tempPlot = GetCurrentPlot(feNumber,1)
    tempPlot.savefig('./output/plots/FE{}_200mV.png'.format(feNumber))
    pdf.image('./output/plots/FE{}_200mV.png'.format(feNumber), x = None, y = None, w = 150, h = 100, type = 'png', link = '')
    pdf.image('./output/plots/FE{}_900mV.png'.format(feNumber), x = None, y = None, w = 150, h = 100, type = 'png', link = '')
    for tempConfigurationIndex in range(6):
        pdf.image('./output/plots/FE{}_pulse_{}.png'.format(feNumber, tempConfigurationIndex + 1), x = None, y = None, w = 100, h = 66, type = 'png', link = '')

    pdf.output('./output/result_FE{}.pdf'.format(feNumber), 'F')


def MakePDFAll():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Times', '', 24)
    pdf.cell(0, 20, 'Power Measurement', 0, 1, 'C')
    pdf.set_font('Times', '', 12)
    #tempConfigurationIndex = 0
    for tempConfigurationIndex in range(6):
        if (tempConfigurationIndex == 0): 
            pdf.cell(60, 10, 'SE=OFF SEDC=OFF', 1, 0, 'C')
            pdf.cell(60, 10, '900mV (BL)', 1, 0, 'C')
        if (tempConfigurationIndex == 1): 
            pdf.cell(60, 10, 'SE=ON SEDC=OFF', 1, 0, 'C')
            pdf.cell(60, 10, '900mV (BL)', 1, 0, 'C')
        if (tempConfigurationIndex == 2): 
            pdf.cell(60, 10, 'SE=OFF SEDC=ON', 1, 0, 'C')
            pdf.cell(60, 10, '900mV (BL)', 1, 0, 'C')
        if (tempConfigurationIndex == 3): 
            pdf.cell(60, 10, 'SE=OFF SEDC=OFF', 1, 0, 'C')
            pdf.cell(60, 10, '200mV (BL)', 1, 0, 'C')
        if (tempConfigurationIndex == 4): 
            pdf.cell(60, 10, 'SE=ON SEDC=OFF', 1, 0, 'C')
            pdf.cell(60, 10, '200mV (BL)', 1, 0, 'C')
        if (tempConfigurationIndex == 5): 
            pdf.cell(60, 10, 'SE=OFF SEDC=ON', 1, 0, 'C')
            pdf.cell(60, 10, '200mV (BL)', 1, 0, 'C')
        #tempConfigurationIndex += 1
        pdf.cell(60, 10, '', 1, 1, 'C')
        pdf.cell(60, 10, 'Power Rail', 1, 0, 'C')
        pdf.cell(60, 10, 'Voltages (V)', 1, 0, 'C')
        pdf.cell(60, 10, 'Current (mA)', 1, 1, 'C')
        kl = list(d.keys())
        tempPower = 0
        tempIndex = 0;
        for onekey in kl:
            #print (onekey, d[onekey])
            pdf.cell(60, 10, onekey, 1, 0, 'C')
            pdf.cell(60, 10, str(d[onekey][0]), 1, 0, 'C')
            pdf.cell(60, 10, str(d[onekey][1]), 1, 1, 'C')
            tempPower += d[onekey][2]
            tempIndex += 1
            if (tempIndex%3 == 0):
                pdf.cell(60, 10, 'Power (mW/Ch)', 1, 0, 'C')
                pdf.cell(60, 10, str(tempPower), 1, 0, 'C')
                pdf.cell(60, 10, '', 1, 1, 'C')
                tempPower = 0
        pdf.cell(0, 10, '', 0, 1, 'C')

    for i in range(8):
        tempPlot = GetCurrentPlot(i+1,0)
        tempPlot.savefig('./output/plots/FE{}_900mV.png'.format(i+1))
        plt.close()
        tempPlot = GetCurrentPlot(i+1,1)
        tempPlot.savefig('./output/plots/FE{}_200mV.png'.format(i+1))
        plt.close()
        pdf.image('./output/plots/FE{}_200mV.png'.format(i+1), x = None, y = None, w = 150, h = 100, type = 'png', link = '')
        pdf.image('./output/plots/FE{}_900mV.png'.format(i+1), x = None, y = None, w = 150, h = 100, type = 'png', link = '')

    pdf.output('tuto1.pdf', 'F')

    MakePDF(1)


def GetAllFECurrentsForBufferStatus(cofigurationIndex):
    tempPointsVDD = []
    tempPointsVDDO = []
    tempPointsVPPP = []
    FEs = ['FE1','FE2','FE3','FE4','FE5','FE6','FE7','FE8']
    for feNumber in range(1, 9):
        tempKey = 'FE' + str(feNumber) + '_'
        tempKeyVDD = tempKey + 'VDD'
        tempKeyVDDO = tempKey + 'VDDO'
        tempKeyVPPP = tempKey + 'VPPP'
        tempPointsVDD.append(rawDataCurrent[cofigurationIndex][tempKeyVDD][1])
        tempPointsVDDO.append(rawDataCurrent[cofigurationIndex][tempKeyVDDO][1])
        tempPointsVPPP.append(rawDataCurrent[cofigurationIndex][tempKeyVPPP][1])
    fig, ax = plt.subplots()
    line1, = ax.plot(FEs, tempPointsVPPP, label = "VPPP", marker = 'o')
    line2, = ax.plot(FEs, tempPointsVDD, label = "VDD", marker = 'o')
    line3, = ax.plot(FEs, tempPointsVDDO, label = "VDDO", marker = 'o')
    if (cofigurationIndex == 0): 
        bufferStatusString = 'SE=OFF SEDC=OFF, 900mV (BL)'
    if (cofigurationIndex == 1): 
        bufferStatusString = 'SE=ON SEDC=OFF, 900mV (BL)'
    if (cofigurationIndex == 2): 
        bufferStatusString = 'SE=OFF SEDC=ON, 900mV (BL)'
    if (cofigurationIndex == 3): 
        bufferStatusString = 'SE=OFF SEDC=OFF, 200mV (BL)'
    if (cofigurationIndex == 4): 
        bufferStatusString = 'SE=ON SEDC=OFF, 200mV (BL)'
    if (cofigurationIndex == 5): 
        bufferStatusString = 'SE=OFF SEDC=ON, 200mV (BL)'
    ax.set_title(bufferStatusString)
    ax.legend(handles=[line1, line2, line3])
    plt.ylabel('Measured Current (mA)')
    for index in range(len(FEs)):
      ax.text(FEs[index], round(tempPointsVPPP[index], 1), round(tempPointsVPPP[index], 1), size=12)
      ax.text(FEs[index], round(tempPointsVDD[index], 1), round(tempPointsVDD[index], 1), size=12)
      ax.text(FEs[index], round(tempPointsVDDO[index], 1), round(tempPointsVDDO[index], 1), size=12)
    ax.grid(True)
    plt.savefig('./output/plots/' + bufferStatusString + '.png')
    plt.close()
    #plt.show()

for feNumber in range(8):
    MakePDF(feNumber)

#for configurationIndex in range(0, 6):
    #GetAllFECurrentsForBufferStatus(configurationIndex)
