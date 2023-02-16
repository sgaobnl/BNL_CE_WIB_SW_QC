from wib_cfgs import WIB_CFGS
import time
import sys
import numpy as np
import pickle
import copy
import time, datetime, random, statistics    
    
chk = WIB_CFGS()
 

print("FE Monitoring")

#AD7274 testing
#write 0x1, then 0x0 to reg 26

#then keep checking busy (reg 55 & 0x80) until it is 0
#busy_regs = [55, 3, 5, 7, 9, 11, 13, 15, 17]

print ("DAT#001")
AD_REF = 2.564 #for board 2.564V
AD_LSB = AD_REF/4096

fe_name = ["FE1", "FE2", "FE3", "FE4", "FE5", "FE6", "FE7", "FE8"]

#MUX (SN74LV405AD)
select_names_fe = ["GND", "Ext_Test", "DAC", "FE_COMMON_DAC", "VBGR", "DNI[To_AmpADC]", "GND", "AUX_VOLTAGE_MUX"]

def dat_monadcs(avg=1):
    #t0 = time.time_ns()
    chk.dat_monadc_trig() #get the previous result    
    avg_datas = [[],[],[],[],[],[],[],[]]
    for avgi in range(avg):
        chk.dat_monadc_trig()    
        for fe in range(8):
            for check in range(10):
                if not chk.dat_monadc_busy(fe=fe):
                    break;
                if check is 9:
                    print("Timed out while waiting for AD7274 controller to finish")
            data = chk.dat_monadc_getdata(fe=fe)
            avg_datas[fe].append(data)
    datas = []
    datas_std = []
    for fe in range(8):
        if avg == 1:
            datas.append(avg_datas[fe][0])
            datas_std.append(0)
        else:
            datas.append(int(np.mean(avg_datas[fe])))
            datas_std.append(np.std(avg_datas[fe]))
    #print (time.time_ns() - t0)
    return datas, datas_std


def dat_fe_vbgrs():
    #measure VBGR through VBGR pin
    print ("measure VBGR through VBGR pin")
    mux_cs = 4
    mux_name = select_names_fe[mux_cs]
    chk.cdpoke(0, 0xC, 0, chk.DAT_ADC_FE_TEST_SEL, mux_cs<<4)    
    datas = dat_monadcs()[0]
    print (datas)
    for fe in range(8):
        print("FE MonADC " + mux_name + " :",datas[fe]*AD_LSB,"V\t",hex(datas[fe]),"\t",format(datas[fe],'b').zfill(12))

#dat_fe_vbgrs()


def dat_fe_mons(mon_type=0, sg0=0, sg1=1, sgp=0):
    #mon_type = 0:  Analog
    #mon_type = 1: Temperature
    #mon_type = 2: VBGR
    #mon_type = 3: DAC
    #mon_type = 4: Baseline @ 200mV 
    #mon_type = 5: Baseline @ 200mV 

    #measure VBGR/Temperature through Monitoring pin
    chk.adcs_paras = [ # c_id, data_fmt(0x89), diff_en(0x84), sdc_en(0x80), vrefp, vrefn, vcmo, vcmi, autocali
                        [0x4, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 1],
                        [0x5, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 1],
                        [0x6, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 1],
                        [0x7, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 1],
                        [0x8, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 1],
                        [0x9, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 1],
                        [0xA, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 1],
                        [0xB, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 1],
                      ]
    chk.femb_cfg(femb_id=0)

    while True:
        a = int(input ("cmn--> "))
        chk.cdpoke(0, 0xC, 0, chk.DAT_FE_CMN_SEL, a)    
        time.sleep(1)
        b = int(input ("mon--> "))
        chk.cdpoke(0, 0xC, 0, chk.DAT_MISC_IO, b)    

    mux_cs=5
    mux_name = select_names_fe[mux_cs]
    chk.cdpoke(0, 0xC, 0, chk.DAT_ADC_FE_TEST_SEL, mux_cs<<4)    
    chk.cdpoke(0, 0xC, 0, chk.DAT_FE_CALI_CS, 0xff)    
    chk.cdpoke(0, 0xC, 0, chk.DAT_FE_TEST_SEL_INHIBIT, 0xff)    

    if mon_type == 1:
        chk.set_fe_reset()
        print ("measure Temperatue through Monitoring pin")
        chn = 0
        stb0=0
        stb1=1
 
        for fe in range(8):
            chk.set_fechn_reg(chip=fe&0x07, chn=chn, smn=1, sdf=1) 
            chk.set_fechip_global(chip=fe&0x07, stb1=stb1, stb=stb0)
        chk.set_fe_sync()
        chk.femb_fe_cfg(femb_id=0)

        datas = dat_monadcs()[0]
        for fe in range(8):
            print("FE MonADC " + mux_name + " :",datas[fe]*AD_LSB,"V\t",hex(datas[fe]),"\t",format(datas[fe],'b').zfill(12))

    if mon_type == 2:
        chk.set_fe_reset()
        print ("measure VBGR through Monitoring pin")
        chn = 0
        stb1=1
        stb0=1
        for fe in range(8):
            chk.set_fechn_reg(chip=fe&0x07, chn=chn, smn=1, sdf=1) 
            chk.set_fechip_global(chip=fe&0x07, stb1=stb1, stb=stb0)
        chk.set_fe_sync()
        chk.femb_fe_cfg(femb_id=0)
        
        datas = dat_monadcs()[0]
        for fe in range(8):
            print("FE MonADC " + mux_name + " :",datas[fe]*AD_LSB,"V\t",hex(datas[fe]),"\t",format(datas[fe],'b').zfill(12))

    if mon_type == 3:
        chk.set_fe_reset()
        print ("measure LArASIC DAC through Monitoring pin")
        chk.set_fe_board(sg0=sg0, sg1=sg1)
        chn = 0
        for dac in range(64):
            for fe in range(8):
                chk.set_fechip_global(chip=fe&0x07, swdac=3, dac=dac, sgp=sgp)
            chk.set_fe_sync()
            chk.femb_fe_cfg(femb_id=0)
            
            datas = dat_monadcs()[0]
            for fe in range(8):
                print(dac, "FE MonADC " + mux_name + " :",datas[fe]*AD_LSB,"V\t",hex(datas[fe]),"\t",format(datas[fe],'b').zfill(12))


    if mon_type == 0:
        print ("measure LArASIC 200mV BL through Monitoring pin")
        chn = 0
        stb0=0
        stb1=0
 
        for chn in range(16):
            chk.set_fe_reset()
            for fe in range(8):
                chk.set_fechn_reg(chip=fe&0x07, chn=chn, snc=0, smn=1,st0=1, st1=1, sdf=1) 
            chk.set_fe_sync()
            chk.femb_fe_cfg(femb_id=0)

            datas = dat_monadcs()[0]
            for fe in range(8):
                print("900mV, FE %d CHN %d "%(fe, chn) + " MonADC " + mux_name + " :",datas[fe]*AD_LSB,"V\t",hex(datas[fe]),"\t",format(datas[fe],'b').zfill(12))

 
        for chn in range(16):
            chk.set_fe_reset()
            for fe in range(8):
                chk.set_fechn_reg(chip=fe&0x07, chn=chn, snc=1, smn=1,st0=1, st1=1, sdf=1) 
            chk.set_fe_sync()
            chk.femb_fe_cfg(femb_id=0)

            datas = dat_monadcs()[0]
            for fe in range(8):
                print("200mV, FE %d CHN %d "%(fe, chn) + " MonADC " + mux_name + " :",datas[fe]*AD_LSB,"V\t",hex(datas[fe]),"\t",format(datas[fe],'b').zfill(12))



dat_fe_mons(mon_type=0)
#dat_fe_mons(mon_type=2)
#dat_fe_mons(mon_type=3)
