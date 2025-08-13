import pickle 
import os
import sys

def qc_files_status( rootdir, duttype="FE"):
    if "FE" in duttype:
        files_in_done = ['QC_CALI_DATDAC.bin', 'QC_CALI_ASICDAC.bin', 'QC_RMS.bin', 'QC_Cap_Meas.bin', 'QC_PWR.bin', 'QC_PWR_CYCLE.bin', 'QC_MON.bin', 'QC_INIT_CHK.bin', 'QC_DLY_RUN.bin', 'QC.log', 'QC_CALI_ASICDAC_47.bin', 'QC_CHKRES.bin', 'QC_CALI_DIRECT.bin']
        for fn in files_in_done:
            fp =  "/".join([rootdir , fn])
            if not os.path.isfile(fp):  #
                print ("incompleted QC files  under this folder")
                return False #QC test is incompleted



        log_fp = "/".join([rootdir , "QC.log"])

        if os.path.isfile(log_fp):  #
            with open(log_fp, 'rb') as fn:
                logd  = pickle.load( fn)

        keys_in_done = ['QC_TestItemID_000_SCP' ,'QC_TestItemID_000_Save'
                    ,'QC_TestItemID_001' ,'QC_TestItemID_001_SCP' ,'QC_TestItemID_001_Save'
                    ,'QC_TestItemID_002' ,'QC_TestItemID_002_SCP' ,'QC_TestItemID_002_Save'
                    ,'QC_TestItemID_003' ,'QC_TestItemID_003_SCP' ,'QC_TestItemID_003_Save'
                    ,'QC_TestItemID_004' ,'QC_TestItemID_004_SCP' ,'QC_TestItemID_004_Save'
                    ,'QC_TestItemID_005' ,'QC_TestItemID_005_SCP' ,'QC_TestItemID_005_Save'
                    ,'QC_TestItemID_061' ,'QC_TestItemID_061_SCP' ,'QC_TestItemID_061_Save'
                    ,'QC_TestItemID_062' ,'QC_TestItemID_062_SCP' ,'QC_TestItemID_062_Save'
                    ,'QC_TestItemID_063' ,'QC_TestItemID_063_SCP' ,'QC_TestItemID_063_Save'
                    ,'QC_TestItemID_064' ,'QC_TestItemID_064_SCP' ,'QC_TestItemID_064_Save'
                    ,'QC_TestItemID_007' ,'QC_TestItemID_007_SCP' ,'QC_TestItemID_007_Save'
                    ,'QC_TestItemID_008' ,'QC_TestItemID_008_SCP' ,'QC_TestItemID_008_Save'
                    ,'QC_TestItemID_009']

        for key in keys_in_done:
            if key not in logd.keys():
                print ("QC test is incompleted under this folder")
                return False #QC test is incompleted

        return True
    if "ADC" in duttype:
        print ("ADC files check to be added")
        return False
    if "CD" in duttype:
        print ("CD files check to be added")
        return False
    
if __name__ =="__main__":
    rootdir ='S:\RTS_DAT_LArASIC_QC\B009T0010\Time_20250808163429_DUT_0000_1001_2002_3003_4004_5010_6011_7012\RT_FE_009006120_009004885_009006583_009006354_009006413_009002743_009002744_009002704/'
    rootdir = r'S:\RTS_DAT_LArASIC_QC\B009T0010\Time_20250812151740_DUT_0071_1072_2073_3074_4075_5076_6077_7078\LN_FE_009002722_009002725_009002721_009002830_009002393_009002324_009002323_009002322/'
    flg = qc_files_status( rootdir, duttype="FE")
    print (flg)
