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

AD_REF = 2.5
AD_LSB = AD_REF/4096

fe_name = ["FE1", "FE2", "FE3", "FE4", "FE5", "FE6", "FE7", "FE8"]

#MUX (SN74LV405AD)
select_names_fe = ["GND", "Ext_Test", "DAC", "FE_COMMON_DAC", "VBGR", "DNI[To_AmpADC]", "GND", "AUX_VOLTAGE_MUX"]

def dat_monadcs():
    datas = []
    time.sleep(1e-6)
    chk.dat_monadc_trig()    
    for fe in range(8):
        for check in range(10):
            if not chk.dat_monadc_busy(fe=fe):
                break;
            if check is 9:
                print("Timed out while waiting for AD7274 controller to finish")
        data = chk.dat_monadc_getdata(fe=fe)
        datas.append(data)
    return datas


def dat_fe_vbgrs():
    #measure VBGR through VBGR pin
    print ("measure VBGR through VBGR pin")
    mux_cs = 4
    mux_name = select_names_fe[4]
    chk.cdpoke(0, 0xC, 0, chk.DAT_ADC_FE_TEST_SEL, mux_cs<<4)    
    datas = dat_monadcs()
    print (datas)
    for fe in range(8):
        print("FE MonADC " + mux_name + " :",datas[fe]*AD_LSB,"V\t",hex(datas[fe]),"\t",format(datas[fe],'b').zfill(12))

#dat_fe_vbgrs()


def dat_fe_mons(mon_type=0):
    #mon_type = 0:  Analog
    #mon_type = 1: Temperature
    #mon_type = 2: VBGR
    #mon_type = 3: Baseline @ 200mV 
    #mon_type = 4: Baseline @ 200mV 
    #mon_type = 5: DAC 

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
    chk.set_fe_reset()
    chk.femb_cfg(femb_id=0)
    if mon_type == 2:
        print ("measure VBGR through Monitoring pin")
        chn = 0
        stb1=1
        stb=1
        for fe in range(8):
            self.set_fechn_reg(chip=fe&0x07, chn=chn, smn=1, sdf=1) 
            self.set_fechip_global(chip=fe&0x07, stb1=stb1, stb=stb0)
        self.set_fe_sync()
        chk.femb_fe_cfg(femb_id=0)
        
        mux=5
        chk.cdpoke(0, 0xC, 0, chk.DAT_ADC_FE_TEST_SEL, fe<<mux_cs)    
        chk.cdpoke(0, 0xC, 0, chk.DAT_FE_CALI_CS, 1)    

        datas = dat_monadcs()
        for fe in range(8):
            print("FE MonADC:",data*AD_LSB,"V\t",hex(data),"\t",format(data,'b').zfill(12))

    if mon_type == 1:
        print ("measure Temperatue through Monitoring pin")
        chn = 0
        for fe in range(8):
            self.set_fechn_reg(chip=fe&0x07, chn=chn, smn=1, sdf=1) 
            self.set_fechip_global(chip=fe&0x07, stb1=stb1, stb=stb0)
        self.set_fe_sync()
        chk.femb_fe_cfg(femb_id=0)
        
        mux=5
        chk.cdpoke(0, 0xC, 0, chk.DAT_ADC_FE_TEST_SEL, fe<<mux_cs)    
        chk.cdpoke(0, 0xC, 0, chk.DAT_FE_CALI_CS, 1)    

        datas = dat_monadcs()
        for fe in range(8):
            print("FE MonADC:",data*AD_LSB,"V\t",hex(data),"\t",format(data,'b').zfill(12))


dat_fe_mons(mon_type=1):
