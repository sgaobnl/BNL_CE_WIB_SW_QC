import sys 
import os

def rootdir_cs (duttype = "FE"):
    if "FE" in duttype:
        rootdir = "D:/DAT_LArASIC_QC/Tested/"
        rootdir = "S:/RTS_DAT_LArASIC_QC/"
        rootdir = "C:/SGAO/ColdTest/Tested/DAT_LArASIC_QC/"
    elif "ADC" in duttype:
        rootdir = "D:/DAT_ColdADC_QC/Tested/"
        #rootdir = "S:/SGAO_DAT/Tested/DAT_ColdADC_QC/Tested/"
        rootdir = "S:/RTS_DAT_ColdADC_QC/"
        rootdir = "C:/SGAO/ColdTest/Tested/DAT_ColdADC_QC/"
    elif "CD" in duttype:
        rootdir = "D:/DAT_CD_QC/Tested/"
        #rootdir = "S:/SGAO_DAT/Tested/DAT_CD_QC/Tested/"
        rootdir = "S:/RTS_DAT_COLDATA_QC/"
        rootdir = "C:/SGAO/ColdTest/Tested/DAT_CD_QC/"
    else:
        print ("Wrong ASIC type, exit anyway")
        exit()
    return rootdir
