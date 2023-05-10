#This script test power measurement test and pulse response test 
#for each chip, each FEMB configuration.
#This makes 2 raw data files, rawDataCurrent.bin, 
#rawDataPulse.bin, for the measurement and pulse response test respectively.
#The output files are generated under the directory ./tmp_data/
from wib_cfgs import WIB_CFGS
import time
import sys
import numpy as np
import pickle
import copy
import time, datetime, random, statistics    
from spymemory_decode import wib_spy_dec_syn

switch = ["OFF", "ON"]
BL = ["900", "200"]

chk = WIB_CFGS()
chk.wib_fw()
#step 1
#reset all FEMBs on WIB
fembs=[0]
chk.wib_femb_link_en(fembs)

#turn this on to pause and waiting for user input when test fails
WAITING_USER_INPUT = False

rawDataCurrent = [[],[],[],[],[],[],[],[]]
rawDataPulse = [[],[],[],[],[],[],[],[]]


print("FE INA226")
fe_name = ["FE0", "FE1", "FE2", "FE3", "FE4", "FE5", "FE6", "FE7"]
addrs = [0x40, 0x41, 0x42]
pwrrails = ["VDD", "VDDO", "VPPP"]
V_LSB = 1.25e-3
I_LSB = 0.01e-3 #amps
R = 0.1 #ohms
#cal = 0.00512/(I_LSB*R)
#print("cal is",hex(int(cal)))
VPPPLowerLimit = 20
VPPPUpperLimit = 35
VDDLowerLimit = 10
VDDUpperLimit = 25
VDDOLowerLimit = -2
VDDOUpperLimit = 5

####################FEMBs Configuration################################
def pwr_femb_cfg(sdf, sdd, snc):
    if (sdf ==1) and (sdd ==1):
        print ("error! sdf and sdd can't be on at the same time")
        exit()
    chk.femb_cd_rst()
    cfg_paras_rec = []
    for femb_id in fembs:
        chk.adcs_paras = [ # c_id, data_fmt(0x89), diff_en(0x84), sdf_en(0x80), vrefp, vrefn, vcmo, vcmi, autocali
                            [0x4, 0x08, 0, sdd, 0xDF, 0x33, 0x89, 0x67, 0],
                            [0x5, 0x08, 0, sdd, 0xDF, 0x33, 0x89, 0x67, 0],
                            [0x6, 0x08, 0, sdd, 0xDF, 0x33, 0x89, 0x67, 0],
                            [0x7, 0x08, 0, sdd, 0xDF, 0x33, 0x89, 0x67, 0],
                            [0x8, 0x08, 0, sdd, 0xDF, 0x33, 0x89, 0x67, 0],
                            [0x9, 0x08, 0, sdd, 0xDF, 0x33, 0x89, 0x67, 0],
                            [0xA, 0x08, 0, sdd, 0xDF, 0x33, 0x89, 0x67, 0],
                            [0xB, 0x08, 0, sdd, 0xDF, 0x33, 0x89, 0x67, 0],
                          ]
        chk.set_fe_board(sts=0, snc=snc,sg0=0, sg1=0, st0=0, st1=0, swdac=0, sdd=sdd, sdf=sdf, dac=0x00 )
        adac_pls_en = 0 #enable LArASIC interal calibraiton pulser
        cfg_paras_rec.append( (femb_id, copy.deepcopy(chk.adcs_paras), copy.deepcopy(chk.regs_int8), adac_pls_en) )
        chk.femb_cfg(femb_id, adac_pls_en )
    print ("sleep 5 secs...")
    time.sleep(5)

def pwr_info(FE):
    fes_pwr_info = {}
    for i in range(3):
        addr = addrs[i]
        bus_voltage = chk.datpower_getvoltage(addr, fe=FE)
        current = chk.datpower_getcurrent(addr, fe=FE)
        fes_pwr_info[fe_name[FE] + "_" + pwrrails[i]] = [bus_voltage, current*1e+3, bus_voltage*current*1e+3]
    return fes_pwr_info

def CheckTheCurrent(pwr_info, FE):
    isPassed = True
    tempMeasurement = [];
    #geting current values
    VPPP = pwr_info[fe_name[FE] + "_VPPP"][1]
    tempMeasurement.append(VPPP);
    VDD = pwr_info[fe_name[FE] + "_VDD"][1]
    tempMeasurement.append(VDD);
    VDDO = pwr_info[fe_name[FE] + "_VDDO"][1]
    tempMeasurement.append(VDDO);

    if (VPPP < VPPPLowerLimit) or (VPPP > VPPPUpperLimit):
        print (" |-" + fe_name[FE] + "_VPPP: " + str(round(VPPP, 2)) + "\033[91m" + " is out of range" + "\033[0m" + "(" + str(VPPPLowerLimit) + " ~ " + str(VPPPUpperLimit) + ")")
        isPassed = False
        if WAITING_USER_INPUT : input ("\033[91m" + '  |-waiting user input...' + "\033[0m")
    else:
        print (" |-" + fe_name[FE] + "_VPPP: " + str(round(VPPP, 2)) + " is in the range (" + str(VPPPLowerLimit) + " ~ " + str(VPPPUpperLimit) + ")")
    if (VDD < VDDLowerLimit) or (VDD > VDDUpperLimit):
        print (" |-" + fe_name[FE] + "_VDD: " + str(round(VDD, 2)) + "\033[91m" + " is out of range" + "\033[0m" + " (" + str(VDDLowerLimit) + " ~ " + str(VDDUpperLimit) + ")")
        isPassed = False
        if WAITING_USER_INPUT : input ("\033[91m" + '  |-waiting user input...' + "\033[0m")
    else:
        print (" |-" + fe_name[FE] + "_VDD: " + str(round(VDD, 2)) + " is in the range (" + str(VDDLowerLimit) + " ~ " + str(VDDUpperLimit) + ")")
    if (VDDO < VDDOLowerLimit) or (VDDO > VDDOUpperLimit):
        print (" |-" + fe_name[FE] + "_VDDO: " + str(round(VDDO, 2)) + "\033[91m" + " is out of range" + "\033[0m" + " (" + str(VDDOLowerLimit) + " ~ " + str(VDDOUpperLimit) + ")")
        isPassed = False
        if WAITING_USER_INPUT : input ("\033[91m" + '  |-waiting user input...' + "\033[0m")
    else:
        print (" |-" + fe_name[FE] + "_VDDO: " + str(round(VDDO, 2)) + " is in the range (" + str(VDDOLowerLimit) + " ~ " + str(VDDOUpperLimit) + ")")

    #if (isPassed) :
    #    print ("\033[93m" + "FE" + str(FE) + " current check passed" + "\033[0m")
    #else :
    #    print ("\033[91m" + "FE" + str(FE) + " current check failed" + "\033[0m")

    return isPassed, tempMeasurement

def CheckPulseResponse(sdf, sdd, snc):
    chk.femb_cd_rst()

    cfg_paras_rec = []
    #for femb_id in fembs:
    femb_id = fembs[0]
    #step 2
    #Configur Coldata, ColdADC, and LArASIC parameters. 
    #Here Coldata uses default setting in the script (not the ASIC default register values)
    #ColdADC configuraiton
    chk.adcs_paras = [ # c_id, data_fmt(0x89), diff_en(0x84), sdf_en(0x80), vrefp, vrefn, vcmo, vcmi, autocali
                        [0x4, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 0],
                        [0x5, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 0],
                        [0x6, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 0],
                        [0x7, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 0],
                        [0x8, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 0],
                        [0x9, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 0],
                        [0xA, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 0],
                        [0xB, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 0],
                      ]
    if sdd == 1:
        for i in range(8):
            chk.adcs_paras[i][2] = 1
    else:
        for i in range(8):
            chk.adcs_paras[i][2] = 0

    #LArASIC register configuration
    chk.set_fe_board(sts=1, snc=snc,sg0=0, sg1=0, st0=0, st1=0, swdac=1, sdf=sdf, sdd=sdd, dac=0x10 )
    adac_pls_en = 1 #enable LArASIC interal calibraiton pulser
#    adac_pls_en = 1 #enable LArASIC interal calibraiton pulser
    cfg_paras_rec.append( (femb_id, copy.deepcopy(chk.adcs_paras), copy.deepcopy(chk.regs_int8), adac_pls_en) )
    #step 3
    chk.femb_cfg(femb_id, adac_pls_en )

    chk.data_align(fembs)

    time.sleep(0.5)

    ####################FEMBs Data taking################################
    sample_N = 1
    rawdata = chk.spybuf_trig(fembs=fembs, num_samples=sample_N, trig_cmd=0) #returns list of size 1

    pwr_meas = chk.get_sensors()

    runi = 0

    buf0 = rawdata[runi][0][0]
    buf1 = rawdata[runi][0][1]
    buf_end_addr = rawdata[runi][1] 
    trigger_rec_ticks = rawdata[runi][2]
    if rawdata[runi][3] != 0:
        trigmode = 'HW'; 
    else:
        trigmode = 'SW'; 

    femb = 0
    dec_data = wib_spy_dec_syn(buf0, buf1, trigmode, buf_end_addr, trigger_rec_ticks, [femb])

    if femb<=1:
        link = 0
    else:
        link = 1

    flen = len(dec_data[link])

    tmts = []
    sfs0 = []
    sfs1 = []
    cdts_l0 = []
    cdts_l1 = []
    femb0 = []
    femb1 = []
    femb2 = []
    femb3 = []
    for i in range(flen):
        tmts.append(dec_data[link][i]["TMTS"])  # timestampe(64bit) * 512ns  = real time in ns (UTS)
        sfs0.append(dec_data[link][i]["FEMB_SF"])
        cdts_l0.append(dec_data[link][i]["FEMB_CDTS"])
        femb0.append(dec_data[link][i]["FEMB0_2"])
        femb1.append(dec_data[link][i]["FEMB1_3"])
        #sfs1.append(dec_data[1][i]["FEMB_SF"])
        #cdts_l1.append(dec_data[1][i]["FEMB_CDTS"])
        #femb2.append(dec_data[1][i]["FEMB0_2"])
        #femb3.append(dec_data[1][i]["FEMB1_3"])
    

    femb0 = list(zip(*femb0))
    femb1 = list(zip(*femb1))
    femb2 = list(zip(*femb2))
    femb3 = list(zip(*femb3))
        
    wibs = [femb0, femb1, femb2, femb3]

    isPulsePassed = [True, True, True, True, True, True, True, True] 

    for fembi in [femb]:
        for FE in range(8):
            tempPulseMeasurement = [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
            print ("------------------------------------------------")
            print ("FE" + str(FE) + " pulse response")
            for chn in range(16):
                tempMax = np.max(wibs[fembi][FE * 16 + chn][0:1500])
                tempMin = np.min(wibs[fembi][FE * 16 + chn][0:1500])
                maxpos = np.where(wibs[fembi][FE * 16 + chn][0:1500] == np.max(wibs[fembi][FE * 16 + chn][0:1500]))[0][0]
                tempPad = wibs[fembi][FE * 16 + chn][maxpos - 50]
                tempPulseMeasurement[chn] = [tempMax, tempPad]
                if (snc == 0):
                    if (tempMax - tempPad) < 3000 or (tempPad - tempMin) < 3000:
                        isPulsePassed[FE] = False;
                        print ("\033[91m" + "channel: " + str(chn) + "\033[0m")
                        print ("\033[91m" + " |-max: " + str(tempMax) + "\033[0m")
                        print ("\033[91m" + " |-pad: " + str(tempPad) + "\033[0m")
                        print ("\033[91m" + " |-min: " + str(tempMin) + "\033[0m")
                    else :
                        print ("channel: " + str(chn))
                        print (" |-max: " + str(tempMax))
                        print (" |-pad: " + str(tempPad))
                        print (" |-min: " + str(tempMin) + "\033[0m")
                if (snc == 1):
                    if (tempMax - tempPad) < 3000:
                        isPulsePassed[FE] = False;
                        print ("\033[91m" + "channel: " + str(chn) + "\033[0m")
                        print ("\033[91m" + " |-max: " + str(tempMax) + "\033[0m")
                        print ("\033[91m" + " |-pad: " + str(tempPad) + "\033[0m")
                    else :
                        print ("channel: " + str(chn))
                        print (" |-max: " + str(tempMax))
                        print (" |-pad: " + str(tempPad))
            rawDataPulse[FE].append(tempPulseMeasurement)

    print ("------------------------------------------------")
    print ("current configuration:" + "\033[96m"  + "SE=" + switch[sdf] + ", SEDC=" + switch[sdd] + ", BL=" + BL[snc] +"mV" + "\033[0m")
    for FE in range(8):
        if (isPulsePassed[FE]) :
            print ("|-FE" + str(FE) + " pulse response check:\033[93m passed" + "\033[0m")
        else :
            print ("|-FE" + str(FE) + " pulse response check:\033[91m failed" + "\033[0m")
            if WAITING_USER_INPUT : input ("\033[91m" + '  |-waiting user input...' + "\033[0m")
    print ("------------------------------------------------")

    return isPulsePassed

def TestEachConfiguration(sdf, sdd, snc):
    #0: OFF/900, 1: ON/200 
    isPassed = [True, True, True, True, True, True, True, True] 

    #############changing configuration###########
    print ("changing configuration... " + "\033[96m"  + "SE=" + switch[sdf] + ", SEDC=" + switch[sdd] + ", BL=" + BL[snc] +"mV" + "\033[0m")
    pwr_femb_cfg(sdf=sdf, sdd=sdd, snc=snc)   #0: OFF/900, 1: ON/200 
    print ("------------------------------------------------")
    print ("current configuration: " + "\033[96m"  + "SE=" + switch[sdf] + ", SEDC=" + switch[sdd] + ", BL=" + BL[snc] +"mV" + "\033[0m")

    #############check current###########
    for FE in range(8):
        temp_fe_pwr_info = pwr_info(FE)
        rawDataCurrent[FE].append(temp_fe_pwr_info)
        print ("FE" + str(FE) + ", checking the measured current range...")
        if (CheckTheCurrent(temp_fe_pwr_info, FE)[0] == False):
            isPassed[FE] = False

    print ("------------------------------------------------")
    print ("current configuration: " + "\033[96m"  + "SE=" + switch[sdf] + ", SEDC=" + switch[sdd] + ", BL=" + BL[snc] +"mV" + "\033[0m")
    for FE in range(8):
        if (isPassed[FE]) :
            print ("|-FE" + str(FE) + " current check:\033[93m passed" + "\033[0m")
        else :
            print ("|-FE" + str(FE) + " current check:\033[91m failed" + "\033[0m")
    print ("------------------------------------------------")

    #############pulse response###########
    chk.set_fe_board(sts=1, snc=snc,sg0=0, sg1=0, st0=0, st1=0, swdac=1, sdf=sdf, sdd=sdd, dac=0x10 )
    print ("checking the pulse range...")
    CheckPulseResponse(sdf=sdf, sdd=sdd, snc=snc)

    return isPassed

def DoTest():
    isPassed = [True,True,True,True,True,True,True,True]
    print ("------------------------------------------------")
    #print ("testing FE" + str(FE) + "...")
    #default configuration
    print ("default configuration")
    for FE in range(8):
        print ("FE" + str(FE) + ", checking the measured current range...")
        temp_fe_pwr_info = pwr_info(FE)
        rawDataCurrent[FE].append(temp_fe_pwr_info)
        rawDataPulse[FE].append([])
        if (CheckTheCurrent(temp_fe_pwr_info, FE)[0] == False):
            isPassed[FE] = False

    print ("------------------------------------------------")
    print ("current configuration: default")
    for FE in range(8):
        if (isPassed[FE]):
            print ("|-FE" + str(FE) + " current check:\033[93m passed" + "\033[0m")
        else :
            print ("|-FE" + str(FE) + " current check:\033[91m failed" + "\033[0m")
    print ("------------------------------------------------")

    TestEachConfiguration(sdf=0, sdd=0, snc=0)
    TestEachConfiguration(sdf=1, sdd=0, snc=0)
    TestEachConfiguration(sdf=0, sdd=1, snc=0)
    TestEachConfiguration(sdf=0, sdd=0, snc=1)
    TestEachConfiguration(sdf=1, sdd=0, snc=1)
    TestEachConfiguration(sdf=0, sdd=1, snc=1)

    outputFile = "./tmp_data/rawDataCurrent.bin"
    with open(outputFile, 'wb') as f:
        pickle.dump(rawDataCurrent, f)
    outputFile = "./tmp_data/rawDataPulse.bin"
    with open(outputFile, 'wb') as f:
        pickle.dump(rawDataPulse, f)

DoTest()
