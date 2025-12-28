from llc import LLC
from fe_asic_reg_mapping import FE_ASIC_REG_MAPPING
from wib_cfgs import WIB_CFGS
from spymemory_decode import wib_spy_dec_syn
from spymemory_decode import wib_dec
import time
import sys
import numpy as np
import pickle
import copy
import time, datetime, random, statistics   
import ctypes 
import pyvisa  
import struct


class DAT_CFGS(WIB_CFGS):
    def __init__(self):
        super().__init__()
        self.cd_sel = 0
        self.dat_on_wibslot = 0
        self.fembs = [self.dat_on_wibslot]
        self.data_align_flg = False
        self.data_align_pwron_flg = True

        #MUX (SN74LV405AD)
        self.mon_fe_cs = ["GND", "Ext_Test", "DAC", "FE_COMMON_DAC", "VBGR", "DNI[To_AmpADC]", "GND", "AUX_VOLTAGE_MUX"]
        self.mon_fe_cmn_cs = ["GND", "DAC_OUT", "TST_PULSE_AMON", "Ext_TEST", "DAC_OUT_WIB_SWTCH", "P1.8V"]
        self.mon_adc_cs = ["VOLTAGE_MONITOR_MUX", "CURRENT_MONITOR_MUX", "VREFP", "VREFN", "VCMI", "VCMO", "AUX_ISINK_MUX", "AUX_ISOURCE_MUX"]
        self.adc_imon_sel = ["ICMOS_REF", "ISHA0", "IADC0", "ISHA1", "IADC1", "IBUFF(CMOS)", "IREF", "IREFBUFFER0"]
        self.mon_AD_REF = 2.564 #need to update accoring to board
        self.AD_LSB = 2564/4096 #mV/bit #need to update accoring to board
        self.imon_R = 5#5kOhm resistor for DAT current monitor
        self.monadc_avg = 1
        self.fedly= 1
        self.sddflg = 0 
        self.ADCVREF = 2.5
        self.gen_rm = 'TCPIP0::192.168.121.201::inst0::INSTR'
        self.rev = 1 #0 old revison, 1 new revision
        self.fe_cali_vref = 1.090 

    def wib_pwr_on_dat(self):
        print ("Initilization checkout")
        self.wib_fw()
        print ("Turn off all power rails for FEMBs")
        self.femb_cd_rst()
        self.femb_powering([])
        self.data_align_flg = False
        self.data_align_pwron_flg = True
        time.sleep(2)
        
        #set FEMB voltages
        self.fembs_vol_set(vfe=4.0, vcd=4.0, vadc=4.0)
        #power on FEMBs
        self.femb_powering(self.fembs)
        self.data_align_flg = False
        self.data_align_pwron_flg = True

        #pwr_ongoing_f = True
        for i in range(30):
            pwr_ongoing_f = True
            for femb_id in self.fembs:
                ver_id = self.cdpeek(femb_id, 0xC, 0, 0xF4) 
                year_l = self.cdpeek(femb_id, 0xC, 0, 0xF9) 
                year_h = self.cdpeek(femb_id, 0xC, 0, 0xFA)
                print ("DAT", hex(ver_id), hex(year_h), hex(year_l))
                if (ver_id == 0x2B) and (year_h == 0x20) and (year_l == 0x24):
                    pwr_ongoing_f = False
            if (not pwr_ongoing_f) and i > 20:
                init_f = True
            else:
                init_f = False
                break
            time.sleep(1)

        pwr_meas = None
        link_mask = None

        if not init_f:
            init_f = not self.dat_fpga_reset()

        if not init_f: 
            self.cdpoke(0, 0xC, 0, self.DAT_CD_AMON_SEL, self.cd_sel)    
            self.femb_cd_rst()
            for femb_id in self.fembs:
               self.femb_cd_fc_act(femb_id, act_cmd="rst_adcs")
               self.femb_cd_fc_act(femb_id, act_cmd="rst_larasics")
               self.femb_cd_fc_act(femb_id, act_cmd="rst_larasic_spi")
            pwr_meas, init_f = self.wib_pwr_on_dat_chk()

            link_mask=self.wib_femb_link_en(self.fembs)
            for femb_no in self.fembs:
                if (0xf<<(femb_no*4))&link_mask == 0:
                    print ("HS links are good")
                    self.data_align_flg = False
                    self.data_align_pwron_flg = True
                    self.femb_cd_fc_act(femb_no, act_cmd="rst_adcs")
                    self.femb_cd_fc_act(femb_no, act_cmd="rst_larasics")
                    self.femb_cd_fc_act(femb_no, act_cmd="rst_larasic_spi")
                else:
                    init_f = True
                    print ("\033[91m" + "FEMB%d, HS links are broken, 0x%H"%(femb_no, link_mask)+ "\033[0m")
                    print ("\033[91m" + "Turn DAT off!"+ "\033[0m")
                    self.femb_powering([])
                    self.data_align_flg = False
                    self.data_align_pwron_flg = True
        return pwr_meas, link_mask, init_f

    def wib_pwr_on_dat_chk(self, fullon_chk=True):
        pwr_meas = self.get_sensors()
        for key in pwr_meas:
            if "FEMB%d"%self.dat_on_wibslot in key:
                init_f = False
                if fullon_chk:
                    print (key, ":", pwr_meas[key])
                    if "BIAS_V" in key:
                        if pwr_meas[key] < 4.5:
                            init_f = True
                    if "DC2DC0_V" in key:
                        if pwr_meas[key] < 3.5:
                            init_f = True
                    if "DC2DC1_V" in key:
                        if pwr_meas[key] < 3.5:
                            init_f = True
                    if "DC2DC2_V" in key:
                        if pwr_meas[key] < 3.5:
                            init_f = True
#                   if "DC3DC3_V" in key: #not use
#                       if pwr_meas[key] < 3.5:
#                           init_f = True
        
                    if "BIAS_I" in key:
                        if pwr_meas[key] > 0.1:
                            init_f = True
                    if "DC2DC0_I" in key:
                        if (pwr_meas[key] < 0.2) or (pwr_meas[key] > 1.0) :
                            init_f = True
                    if "DC2DC1_I" in key:
                        if (pwr_meas[key] < 0.2) or (pwr_meas[key] > 1.0) :
                            init_f = True
                    if "DC2DC2_I" in key:
                        if (pwr_meas[key] < 1) or (pwr_meas[key] > 2.5) :
                            init_f = True
#                    if "DC3DC3_I" in key: #not use
#                        if pwr_meas[key] > 1:
#                        init_f = True
                else:
                    if "BIAS_I" in key:
                        if pwr_meas[key] > 0.1:
                            init_f = True
                    if "DC2DC0_I" in key:
                        if  pwr_meas[key] > 0.6 :
                            init_f = True
                    if "DC2DC1_I" in key:
                        if pwr_meas[key] > 1.0 :
                            init_f = True
                    if "DC2DC2_I" in key:
                        if pwr_meas[key] > 2.5 :
                            print (key, pwr_meas[key] )
                            init_f = True
#                    if "DC3DC3_I" in key: #not use
#                        if pwr_meas[key] > 1:
#                        init_f = True

                if init_f:
                    print ("\033[91m" + "DAT power consumption @ (power on) is not right, please contact tech coordinator!"+ "\033[0m")
                    print ("\033[91m" + "Turn DAT off!"+ "\033[0m")
                    self.femb_powering([])
                    self.data_align_flg = False
                    self.data_align_pwron_flg = True
                    return pwr_meas, init_f
        return pwr_meas, init_f


    def dat_pwroff_chk(self, env='RT'):
        self.femb_powering([])
        while True:
            init_f = False
            pwr_meas = self.get_sensors()
            time.sleep(0.1)
            pwr_meas = self.get_sensors()
            for key in pwr_meas:
                if "FEMB%d"%self.dat_on_wibslot in key:
                    if "BIAS_V" in key:
                        if pwr_meas[key] > 2.0:
                            init_f = True
                            print (key, ":", pwr_meas[key])
                    if "DC2DC0_V" in key:
                        if pwr_meas[key] > 0.5:
                            init_f = True
                            print (key, ":", pwr_meas[key])
                    if "DC2DC1_V" in key:
                        if pwr_meas[key] > 0.5:
                            init_f = True
                            print (key, ":", pwr_meas[key])
                    if "DC2DC2_V" in key:
                        if pwr_meas[key] > 0.5:
                            init_f = True
                            print (key, ":", pwr_meas[key])
#                    if "DC3DC3_V" in key:
#                        if pwr_meas[key] > 0.5:
#                            init_f = True
            
                    if "BIAS_I" in key:
                        if pwr_meas[key] > 0.05:
                            init_f = True
                            print (key, ":", pwr_meas[key])
                    if "DC2DC0_I" in key:
                        if (pwr_meas[key] > 0.05) :
                            init_f = True
                            print (key, ":", pwr_meas[key])
                    if "DC2DC1_I" in key:
                        if (pwr_meas[key] > 0.05) :
                            init_f = True
                            print (key, ":", pwr_meas[key])
                    if "DC2DC2_I" in key:
                        if (pwr_meas[key] > 0.05) :
                            init_f = True
                            print (key, ":", pwr_meas[key])
#                    if "DC3DC3_I" in key:
#                        if (pwr_meas[key] > 0.05) :
#                            init_f = True
                    if 'RT' in env or 'rt' in env:
                        init_f = False
            if init_f:
                print ("Wait 2 seconds, not yet completely shut down...")
                time.sleep(2)
            if not init_f:
                print ("DAT is off...")
                break
        
    def feadc_pwr_info(self,asic_list, dat_addrs, pwrrails):
        asics_pwr_info = {}
        for asic in range(8):
            for i in range(len(dat_addrs)):
                addr = dat_addrs[i]
                current = self.datpower_getcurrent(addr, fe=asic) #fe keyword arg is for fe OR adc power monitors
                bus_voltage = self.datpower_getvoltage(addr, fe=asic)
                #c0 = self.datpower_getcurrent(addr, fe=asic)
                #v0 = self.datpower_getvoltage(addr, fe=asic)
                #c1 = self.datpower_getcurrent(addr, fe=asic)
                #v1 = self.datpower_getvoltage(addr, fe=asic)
                #c2 = self.datpower_getcurrent(addr, fe=asic)
                #v2 = self.datpower_getvoltage(addr, fe=asic)
                #c = [c0,c1,c2]
                #c.sort()
                #current = c[1]
                #v = [v0,v1,v2]
                #v.sort()
                #bus_voltage = v[1]
                asics_pwr_info[asic_list[asic] + "_" + pwrrails[i]] = [bus_voltage, current*1e+3, bus_voltage*current*1e+3]
        return asics_pwr_info

    def cd_pwr_info(self,asic_list, dat_addrs, pwrrails):
        asics_pwr_info = {}
        for asic in range(2):
            for i in range(len(dat_addrs)):
                addr = dat_addrs[i]
                current = self.datpower_getcurrent(addr, cd=asic)
                #print (hex(current))
                bus_voltage = self.datpower_getvoltage(addr, cd=asic)
                #c0 = self.datpower_getcurrent(addr, cd=asic)
                #v0 = self.datpower_getvoltage(addr, cd=asic)
                #c1 = self.datpower_getcurrent(addr, cd=asic)
                #v1 = self.datpower_getvoltage(addr, cd=asic)
                #c2 = self.datpower_getcurrent(addr, cd=asic)
                #v2 = self.datpower_getvoltage(addr, cd=asic)
                #c = [c0,c1,c2]
                #c.sort()
                #current = c[1]
                #v = [v0,v1,v2]
                #v.sort()
                #bus_voltage = v[1]
                asics_pwr_info[asic_list[asic] + "_" + pwrrails[i]] = [bus_voltage, current*1e+3, bus_voltage*current*1e+3]
        return asics_pwr_info


    def fe_pwr_meas(self,):
        fe_list = ["FE0", "FE1", "FE2", "FE3", "FE4", "FE5", "FE6", "FE7"]
        addrs = [0x40, 0x41, 0x42]
        pwrrails = ["VDDA", "VDDO", "VPPP"]
        fes_pwr_info = self.feadc_pwr_info(asic_list=fe_list, dat_addrs=addrs, pwrrails=pwrrails)
        return fes_pwr_info

    def adc_pwr_meas(self):
        adc_list = ["ADC0-0x8", "ADC1-0x9", "ADC2-0xA", "ADC3-0xB", "ADC4-0x4", "ADC5-0x5", "ADC6-0x6", "ADC7-0x7"]
        addrs = [0x43, 0x44, 0x45, 0x46]
        pwrrails = ["VDDA2P5", "VDDD1P2", "VDDIO", "VDDD2P5"]
        adcs_pwr_info = self.feadc_pwr_info(asic_list=adc_list, dat_addrs=addrs, pwrrails=pwrrails)
        return adcs_pwr_info

    def dat_cd_pwr_meas(self):
        cd_list = ["CD0-0x3", "CD1-0x2"]
        if self.rev == 1:
            addrs = [0x40, 0x41, 0x42, 0x45, 0x44] 
        else:
            addrs = [0x40, 0x41, 0x43, 0x45, 0x44] 
        pwrrails = ["CD_VDDA", "FE_VDDA", "CD_VDDCORE", "CD_VDDD", "CD_VDDIO"]
        cds_pwr_info = self.cd_pwr_info(asic_list=cd_list, dat_addrs=addrs, pwrrails=pwrrails)
        return cds_pwr_info

    def dat_cd_hard_reset(self, femb_id):
        rdv = self.cdpeek(femb_id, 0xC, 0, self.DAT_CD_CONFIG) 
        self.femb_i2c_wrchk(femb_id, 0xC, 0, self.DAT_CD_CONFIG, 0x30|rdv) #CD0
        time.sleep(0.001)
        self.femb_i2c_wrchk(femb_id, 0xC, 0, self.DAT_CD_CONFIG, 0xCF&rdv) #CD0
        time.sleep(0.01)

    def dat_cd_gpio_chk(self, femb_id):
        #set GPIO as output
        self.femb_i2c_wrchk(femb_id, chip_addr=3, reg_page=0, reg_addr=0x27, wrdata=0x1f) #CD0
        self.femb_i2c_wrchk(femb_id, chip_addr=2, reg_page=0, reg_addr=0x27, wrdata=0x1f) #CD1
        datad = {}
        cd0 = []
        cd1 = []
        for wrv in range(32):
            wrv0 = wrv&0x1f
            wrv1 = (wrv+1)&0x1f
            self.femb_i2c_wrchk(femb_id, chip_addr=3, reg_page=0, reg_addr=0x26, wrdata=wrv0)
            self.femb_i2c_wrchk(femb_id, chip_addr=2, reg_page=0, reg_addr=0x26, wrdata=wrv1)
            cd0rdv = self.cdpeek(femb_id, 0xC, 0, 0x3) 
            cd1rdv = self.cdpeek(femb_id, 0xC, 0, 0x2) 
            if (wrv0 != cd0rdv):
                cd0.append([wrv0 ,cd0rdv])
                #print ("Error0", wrv0 ,cd0rdv)
            if (wrv1 != cd1rdv):
                cd1.append([wrv1 ,cd1rdv])
                #print ("Error1", wrv1 ,cd1rdv)
        if (len(cd0) == 0):
            print ("COLDATA with Addr0x03 pass GPIO check")
            datad["CD0_Addr3_GPIO"] = [femb_id,  "PASS"]
        else:
            datad["CD0_Addr2_GPIO"] = [femb_id,  "FAIL", cd0]
        if (len(cd1) == 0):
            print ("COLDATA with Addr0x02 pass GPIO check")
            datad["CD1_Addr2_GPIO"] = [femb_id,  "PASS"]
        else:
            datad["CD1_Addr2_GPIO"] = [femb_id,  "FAIL", cd1]
        return datad

    def dat_cd_order_swap(self, femb_id):
        #U1 (left) as primary
        self.femb_i2c_wrchk(femb_id, 0xC, 0, self.DAT_CD_CONFIG, 0x00)
#perform FEMB configuration, check ADC pattern data

        #U2 (right) as primary
        self.femb_i2c_wrchk(femb_id, 0xC, 0, self.DAT_CD_CONFIG, 0x01) 
#perform FEMB configuration, check ADC pattern data

    def asic_init_pwrchk(self, fes_pwr_info, adcs_pwr_info, cds_pwr_info):
        febads = []
        adcbads = []
        cdbads = []
        warn_flg = False
        kl = list(fes_pwr_info.keys())
        for onekey in kl:
            if "VDDA" in onekey:
                if  (fes_pwr_info[onekey][0] > 1.75) & (fes_pwr_info[onekey][0] < 1.95) & (fes_pwr_info[onekey][1] > 15  ) & (fes_pwr_info[onekey][1] < 25  ) :
                    pass
                else:
                    print ("Warning: {} is out of range {}".format(onekey, fes_pwr_info[onekey]))
                    fe_no = int(onekey[2])
                    if fe_no not in febads:
                        febads.append(fe_no)
                    warn_flg = True
            if "VDDO" in onekey:
                if  (fes_pwr_info[onekey][0] > 1.75) & (fes_pwr_info[onekey][0] < 1.95) & (fes_pwr_info[onekey][1] > -0.1  ) & (fes_pwr_info[onekey][1] < 3  ) :
                    pass
                else:
                    print ("Warning: {} is out of range {}".format(onekey, fes_pwr_info[onekey]))
                    fe_no = int(onekey[2])
                    if fe_no not in febads:
                        febads.append(fe_no)
                    warn_flg = True
            if "VDDP" in onekey:
                if  (fes_pwr_info[onekey][0] > 1.75) & (fes_pwr_info[onekey][0] < 1.95) & (fes_pwr_info[onekey][1] > 28  ) & (fes_pwr_info[onekey][1] < 37  ) :
                    pass
                else:
                    print ("Warning: {} is out of range {}".format(onekey, fes_pwr_info[onekey]))
                    fe_no = int(onekey[2])
                    if fe_no not in febads:
                        febads.append(fe_no)
                    warn_flg = True

        kl = list(adcs_pwr_info.keys())
        for onekey in kl:
            if "VDDA2P5" in onekey:
                if  (adcs_pwr_info[onekey][0] > 2.10) & (adcs_pwr_info[onekey][0] < 2.40) & (adcs_pwr_info[onekey][1] > 100  ) & (adcs_pwr_info[onekey][1] < 200  ) :
                    pass
                else:
                    print ("Warning: {} is out of range {}".format(onekey, adcs_pwr_info[onekey]))
                    adc_no = int(onekey[3])
                    if adc_no not in adcbads:
                        adcbads.append(adc_no)
                    warn_flg = True

            if "VDDD2P5" in onekey:
                if  (adcs_pwr_info[onekey][0] > 2.10) & (adcs_pwr_info[onekey][0] < 2.40) & (adcs_pwr_info[onekey][1] > 10  ) & (adcs_pwr_info[onekey][1] < 40  ) :
                    pass
                else:
                    print ("Warning: {} is out of range {}".format(onekey, adcs_pwr_info[onekey]))
                    adc_no = int(onekey[3])
                    if adc_no not in adcbads:
                        adcbads.append(adc_no)
                    warn_flg = True

            if "VDDIO" in onekey:
                if  (adcs_pwr_info[onekey][0] > 2.10) & (adcs_pwr_info[onekey][0] < 2.40) & (adcs_pwr_info[onekey][1] > 3  ) & (adcs_pwr_info[onekey][1] < 8  ) :
                    pass
                else:
                    print ("Warning: {} is out of range {}".format(onekey, adcs_pwr_info[onekey]))
                    adc_no = int(onekey[3])
                    if adc_no not in adcbads:
                        adcbads.append(adc_no)
                    warn_flg = True

            if "VDDD1P2" in onekey:
                if  (adcs_pwr_info[onekey][0] > 1.05) & (adcs_pwr_info[onekey][0] < 1.15) & (adcs_pwr_info[onekey][1] > 1  ) & (adcs_pwr_info[onekey][1] < 3  ) :
                    pass
                else:
                    print ("Warning: {} is out of range {}".format(onekey, adcs_pwr_info[onekey]))
                    adc_no = int(onekey[3])
                    if adc_no not in adcbads:
                        adcbads.append(adc_no)
                    warn_flg = True

        for onekey in kl:
            if "CD_VDDA" in onekey:
                if  (cds_pwr_info[onekey][0] > 1.15) & (cds_pwr_info[onekey][0] < 1.25) & (cds_pwr_info[onekey][1] > 5   ) & (cds_pwr_info[onekey][1] < 10  ) :
                    pass
                else:
                    print ("Warning: {} is out of range {}".format(onekey, cds_pwr_info[onekey]))
                    cd_no = int(onekey[2])
                    if cd_no not in cdbads:
                        cdbads.append(cd_no)
                    warn_flg = True

            if "FE_VDDA" in onekey:
                if  (cds_pwr_info[onekey][0] > 1.70) & (cds_pwr_info[onekey][0] < 1.90) & (cds_pwr_info[onekey][1] > -0.1  ) & (cds_pwr_info[onekey][1] < 3  ) :
                    pass
                else:
                    print ("Warning: {} is out of range {}".format(onekey, cds_pwr_info[onekey]))
                    cd_no = int(onekey[2])
                    if cd_no not in cdbads:
                        cdbads.append(cd_no)
                    warn_flg = True

            if "CD_VDDCORE" in onekey:
                if  (cds_pwr_info[onekey][0] > 1.15) & (cds_pwr_info[onekey][0] < 1.25) & (cds_pwr_info[onekey][1] > 7  ) & (cds_pwr_info[onekey][1] < 12  ) :
                    pass
                else:
                    print ("Warning: {} is out of range {}".format(onekey, cds_pwr_info[onekey]))
                    cd_no = int(onekey[2])
                    if cd_no not in cdbads:
                        cdbads.append(cd_no)
                    warn_flg = True
            if "CD_VDDD" in onekey: 
                if  (cds_pwr_info[onekey][0] > 1.15) & (cds_pwr_info[onekey][0] < 1.25) & (cds_pwr_info[onekey][1] > 15  ) & (cds_pwr_info[onekey][1] < 25  ) :
                    pass
                else:
                    print ("Warning: {} is out of range {}".format(onekey, cds_pwr_info[onekey]))
                    cd_no = int(onekey[2])
                    if cd_no not in cdbads:
                        cdbads.append(cd_no)
                    warn_flg = True

            if "CD_VDDIO" in onekey:
                if  (cds_pwr_info[onekey][0] > 2.20) & (cds_pwr_info[onekey][0] < 2.35) & (cds_pwr_info[onekey][1] > 40  ) & (cds_pwr_info[onekey][1] < 55  ) :
                    pass
                else:
                    print ("Warning: {} is out of range {}".format(onekey, cds_pwr_info[onekey]))
                    cd_no = int(onekey[2])
                    if cd_no not in cdbads:
                        cdbads.append(cd_no)
                    warn_flg = True

        if warn_flg:
            print ("\033[91m" + "please check before restart"+ "\033[0m")
            self.femb_powering([])
            self.data_align_flg = False
        return warn_flg, febads, adcbads, cdbads

    def asic_init_por(self, duts=["FE", "ADC", "CD"]): #check status after power on
        warn_flg = False
        self.dat_fpga_reset()
        febads = []
        adcbads = []
        cdbads = []
        if "FE" in duts:
            vbgr = self.dat_fe_vbgrs()
            for fe in range(8):
                vtmp = vbgr['VBGR'][1][fe]
                if (vtmp > 1100) and (vtmp < 1300) :
                    pass
                else:
                    warn_flg = True
                    print ("Warning: VBGR of FE{} is out of range {}mV (typical 1.2V)".format(fe, vtmp))
                    febads.append(fe)

        if "ADC" in duts:
            print ("To be developped")
            datad_mons = self.dat_adc_mons(femb_id = 0, mon_type=0x3c)  
            warn_flg, adcbads = self.adc_refv_chk(datad_mons)

            if not warn_flg:
                warn_flg, adcbads = self.femb_adc_chkreg(self.dat_on_wibslot)

        if "CD" in duts:
            print ("To be developped")
            #warn_flg, adcbads

        if warn_flg:
            print ("\033[91m" + "please check before restart"+ "\033[0m")
            self.femb_powering([])
            self.data_align_flg = False
        return warn_flg, febads, adcbads, cdbads

    def dat_adc_qc_cfg(self,data_fmt=0x08, sha_cs=0, ibuf_cs=0, vrefp=0xDF, vrefn=0x33, vcmo=0x89, vcmi=0x67, autocali=1, adac_pls_en=0):
        self.femb_cd_rst()
        cfg_paras_rec = []
        for femb_id in self.fembs:
            self.adcs_paras = [ # c_id, data_fmt(0x89), sha_cs(0x84), ibuf_cs(0x80), vrefp, vrefn, vcmo, vcmi, autocali
                                [0x4, data_fmt, sha_cs, ibuf_cs, vrefp, vrefn, vcmo, vcmi, autocali],
                                [0x5, data_fmt, sha_cs, ibuf_cs, vrefp, vrefn, vcmo, vcmi, autocali],
                                [0x6, data_fmt, sha_cs, ibuf_cs, vrefp, vrefn, vcmo, vcmi, autocali],
                                [0x7, data_fmt, sha_cs, ibuf_cs, vrefp, vrefn, vcmo, vcmi, autocali],
                                [0x8, data_fmt, sha_cs, ibuf_cs, vrefp, vrefn, vcmo, vcmi, autocali],
                                [0x9, data_fmt, sha_cs, ibuf_cs, vrefp, vrefn, vcmo, vcmi, autocali],
                                [0xA, data_fmt, sha_cs, ibuf_cs, vrefp, vrefn, vcmo, vcmi, autocali],
                                [0xB, data_fmt, sha_cs, ibuf_cs, vrefp, vrefn, vcmo, vcmi, autocali],
                              ]
            self.set_fe_reset()
            self.set_fe_board(dac=1) # to aviod all 0 in FE register
            self.set_fe_sync()
            #adac_pls_en = 0 #enable LArASIC interal calibraiton pulser
            cfg_paras_rec.append( (femb_id, copy.deepcopy(self.adcs_paras), copy.deepcopy(self.regs_int8), adac_pls_en, self.cd_sel) )
            if not self.femb_cfg(femb_id, adac_pls_en ):
                return False
        if self.data_align_pwron_flg == True:
            self.data_align(self.fembs)
            self.data_align_pwron_flg = False
            time.sleep(0.1)
        if self.data_align_flg != True:
            self.data_align(self.fembs)
            self.data_align_flg = False
        return cfg_paras_rec

    def dat_adc_qc_refdacs(self, femb_id=0 ):
        refv_dacs = []
        # #Scan the DAC (8bit) for each ref voltages
        # for dac in range(0,0x100,0x10): #do we need every value? add a step?
            # cfg_info = dat.dat_adc_qc_cfg(vrefp=dac, vrefn=dac, vcmo=dac, vcmi=dac)
            # refv_dacs.append(dat.dat_adc_mons(mon_type=0x3c))
            # #data.update(dat.dat_adc_mons(mon_type=0x3c))
            
        #Using https://www.analog.com/media/en/training-seminars/design-handbooks/Data-Conversion-Handbook/Chapter5.pdf pg 10
        #1. measure all 0's and all 1's to get LSB
        # dac = 0xFF
        # cfg_info = dat.dat_adc_qc_cfg(vrefp=dac, vrefn=dac, vcmo=dac, vcmi=dac)
        # refv_dacs[dac] = dat.dat_adc_mons(mon_type=0x3c) 
        
        #2. measure one-hot codes
        #3. measure "major carry points": 0000 to 0001, 0001 to 0010, 0011 to 0100, and 0111 to 1000    [i.e. one-hot minus 1]
        # indiv_sums = {}
        # indiv_sums['MON_VREFP'] = np.array([0,0,0,0,0,0,0,0])
        # indiv_sums['MON_VREFN'] = np.array([0,0,0,0,0,0,0,0])
        # indiv_sums['MON_VCMI'] = np.array([0,0,0,0,0,0,0,0])
        # indiv_sums['MON_VCMO'] = np.array([0,0,0,0,0,0,0,0])
        
        #dac levels to sample:
            #one hots and major carries for dnl/inl and a few others for plotting
        dacs = [0, 0b1, 0b10, 0b11, 0b100, 0b111, 0b1000, 0b1111, 0b10000, 0b11111, 0b100000, 0b110000, 0b111111, 
            0b1000000, 0b1010000, 0b1100000, 0b1110000, 0b1111111, 
            0b10000000, 0b10010000, 0b10100000, 0b10110000, 0b11000000, 0b11010000, 0b11100000, 0b11110000, 0b11111111]
        
        # for shift in range(8):
        for dac in dacs:
            ###one-hot
            # dac = 0x1 << shift
            # refv_dacs[dac] = dat.dat_adc_mons(mon_type=0x3c)
            for adc_no in range(8):
                self.adcs_paras[adc_no][4] = dac
                self.adcs_paras[adc_no][5] = dac
                self.adcs_paras[adc_no][6] = dac
                self.adcs_paras[adc_no][7] = dac
                self.adcs_paras[adc_no][8] = 0 # disable autocali
            self.femb_adc_cfg(femb_id)
            time.sleep(0.2)

            refv_dacs.append(self.dat_adc_mons(femb_id=femb_id, mon_type=0x3c))
            #print (refv_dacs[-1])
            # for key in ['MON_VREFP','MON_VREFN','MON_VCMI','MON_VCMO']:
                # indiv_sums[key] = indiv_sums[key] + refv_dacs[dac][key][1] #for verification
            # print("\nadding",bin(dac),"\n")
            ###major carry point
            # if dac != 0x2: #because 0b10 was already covered by 0x1 << 0
                # dac = dac - 1
                # cfg_info = dat.dat_adc_qc_cfg(vrefp=dac, vrefn=dac, vcmo=dac, vcmi=dac)
                # refv_dacs[dac] = dat.dat_adc_mons(mon_type=0x3c)                
        # one_lsb = {}
        # for key in ['MON_VREFP','MON_VREFN','MON_VCMI','MON_VCMO']:    
            # one_lsb[key] = (refv_dacs[0xFF][key][1] - refv_dacs[0x00][key][1]) / 255 #8 bits
        # print("adding 0")
        #[4bit version]: The all "1"s code, 1111, previously measured should equal the sum of the individual bit voltages: 0000, 0001,
        #0010, 0100, and 1000. This is a good test to verify that superposition holds.
        # for key in ['MON_VREFP','MON_VREFN','MON_VCMI','MON_VCMO']:
            # indiv_sums[key] = indiv_sums[key] + refv_dacs[0x00][key][1] #for verification
        # print("individual sums:",indiv_sums)
        # print("all 1's:",refv_dacs[0xFF])
        
        # vrefp00_sum = 0
        # for dac in [0b0,0b1,0b10,0b100,0b1000,0b10000,0b100000,0b1000000,0b10000000]:
            # print(bin(dac))
            # vrefp00_sum = vrefp00_sum + refv_dacs[dac]['MON_VREFP'][1][0]
        
        # for key in ['MON_VREFP','MON_VREFN','MON_VCMI','MON_VCMO']:
            # print('vrefp0 sum',key,":",vrefp00_sum[key][1])
        # print('vrefp ff:',refv_dacs[0xFF]['MON_VREFP'][1][0])

        #return voltages to normal
        self.dat_adc_qc_cfg()
        return refv_dacs

    def dat_adc_qc_imons(self, femb_id=0 ):
        #Check the current monitors
        imons = {}
        for imon_select in range(0x8):
            adcs_addr=[0x08,0x09,0x0A,0x0B,0x04,0x05,0x06,0x07]  
            #turn on and select current monitor
            for chip in range(0x8):
                self.femb_i2c_wrchk(femb_id=self.dat_on_wibslot, chip_addr=adcs_addr[chip], reg_page=1, reg_addr=0xaf, wrdata=(imon_select<<5)|0x02)
            imon_datas = self.dat_adc_mons(mon_type=0x2)["MON_Imon"]
            #Add current (mA) calculation to dict
            imon_datas.append(np.array(imon_datas[1])/self.imon_R)
            imons[self.adc_imon_sel[imon_select]] = imon_datas        

        #return to normal
        self.dat_adc_qc_cfg()
        return imons

    def dat_adc_qc_oscfreq(self, femb_id=0 ):
        chipfreqs = []

        adcs_addr=[0x08,0x09,0x0A,0x0B,0x04,0x05,0x06,0x07] 
        for chip in range(8): #turn ring osc output on
            self.femb_i2c_wrchk(femb_id, adcs_addr[chip], 1, 0xAA, 0x1)
        freqs = []
        for seconds in range(10):    
            print(seconds+1,"seconds:")
            freq_1s = []
            time.sleep(1) #Allow DAT ro counters to count number of pulses in 1 second
            for chip in range(8):       
                self.cdpoke(femb_id, 0xC, 0, self.DAT_SOCKET_SEL, chip)
                byte3 = self.cdpeek(femb_id, 0xC, 0, self.DAT_ADC_RING_OSC_COUNT_B3)
                byte2 = self.cdpeek(femb_id, 0xC, 0, self.DAT_ADC_RING_OSC_COUNT_B2)
                byte1 = self.cdpeek(femb_id, 0xC, 0, self.DAT_ADC_RING_OSC_COUNT_B1)
                byte0 = self.cdpeek(femb_id, 0xC, 0, self.DAT_ADC_RING_OSC_COUNT_B0)
                freq = (byte3 << 8*3) | (byte2 << 8*2) | (byte1 << 8*1) | byte0
                if seconds == 0:
                    pass
                else:
                    freq_1s.append(freq)
            if seconds != 0:
                freqs.append(freq_1s)
        ks = zip(*freqs)
        for k in ks:
            chipfreqs.append(np.mean(k)) 

        return chipfreqs

    def dat_adc_qc_auto_weithts(self):
        ws = []
        adcs_addr=[0x08,0x09,0x0A,0x0B,0x04,0x05,0x06,0x07]
        for chip in range(8):
            chip_weights = []
            for adc in range(2): #ADC0 or ADC1
                adc_weights = []
                for weight in range(2): #W0 or W2
                    stage_weights = []
                    for stage_num in range(16):                     
                        #calculated using ColdADC datasheet, section "Configuration Memory", Table 10: Configuration Memory Address
                        weight_lsb_addr = (adc << 6) | (weight << 5) | (stage_num << 1)
                        weight_msb_addr = weight_lsb_addr | 0x1
                        weight_lsb = self.femb_i2c_rd(self.dat_on_wibslot, adcs_addr[chip], 0x1, weight_lsb_addr)
                        weight_msb = self.femb_i2c_rd(self.dat_on_wibslot, adcs_addr[chip], 0x1, weight_msb_addr)
                        weight_16b = (weight_msb << 8) | weight_lsb
                        stage_weights.append(weight_16b)
                    adc_weights.append(stage_weights)
                chip_weights.append(adc_weights)
            ws.append(chip_weights)
        return ws 



    def dat_fe_qc_cfg(self, adac_pls_en=0, sts=1, snc=0,sg0=0, sg1=0, st0=1, st1=1, swdac=0, sdd=0, sdf=0, dac=0x00, sgp=0, slk0=0, slk1=0, chn=128):
        self.femb_cd_rst()
        cfg_paras_rec = []
        for femb_id in self.fembs:
#            self.adcs_paras = [ # c_id, data_fmt(0x89), sha_cs(0x84), ibuf_cs(0x80), vrefp, vrefn, vcmo, vcmi, autocali
#                                [0x4, 0x08, sdd, 0, 0xDF, 0x33, 0x89, 0x67, 0],
#                                [0x5, 0x08, sdd, 0, 0xDF, 0x33, 0x89, 0x67, 0],
#                                [0x6, 0x08, sdd, 0, 0xDF, 0x33, 0x89, 0x67, 0],
#                                [0x7, 0x08, sdd, 0, 0xDF, 0x33, 0x89, 0x67, 0],
#                                [0x8, 0x08, sdd, 0, 0xDF, 0x33, 0x89, 0x67, 0],
#                                [0x9, 0x08, sdd, 0, 0xDF, 0x33, 0x89, 0x67, 0],
#                                [0xA, 0x08, sdd, 0, 0xDF, 0x33, 0x89, 0x67, 0],
#                                [0xB, 0x08, sdd, 0, 0xDF, 0x33, 0x89, 0x67, 0],
#                              ]
            for i in range(8):
                self.adcs_paras[i][2] = sdd

            self.set_fe_reset()
            if chn >=128: #configurate all channels
                self.set_fe_board(sts=sts, snc=snc,sg0=sg0, sg1=sg1, st0=st0, st1=st1, swdac=swdac, sdd=sdd, sdf=sdf, dac=dac, sgp=sgp, slk0=slk0, slk1=slk1 )
            else:
                ch = chn%16 #only enable one chanel per FE chip
                for fe in range(8):
                    self.set_fechn_reg(chip=fe&0x07, chn=ch, sts=sts, snc=snc,sg0=sg0, sg1=sg1, st0=st0, st1=st1, sdf=sdf)
                    self.set_fechip_global(chip=fe&0x07, swdac=swdac, sdd=sdd, dac=dac, sgp=sgp, slk0=slk0, slk1=slk1)
                self.set_fe_sync()
            adac_pls_en = adac_pls_en #enable LArASIC interal calibraiton pulser
            cfg_paras_rec.append( (femb_id, copy.deepcopy(self.adcs_paras), copy.deepcopy(self.regs_int8), adac_pls_en, self.cd_sel) )
            if not self.femb_cfg(femb_id, adac_pls_en ):
                return False

            self.sddflg=sdd
        if self.data_align_pwron_flg == True:
            self.data_align(self.fembs)
            self.data_align_pwron_flg = False
            time.sleep(0.1)
        if self.data_align_flg != True:
            self.data_align(self.fembs)
            self.data_align_flg = False

        print ("Wait %d seconds for FEMB configruation is stable..."%self.fedly)
        time.sleep(self.fedly)
        return cfg_paras_rec

    def dat_adc_qc_acq(self, num_samples = 1):
        rawdata = self.spybuf_trig(fembs=self.fembs, num_samples=num_samples, trig_cmd=0, fastchk=False) #returns list of size 1
        #wibdata = wib_dec(rawdata,fembs=self.fembs, spy_num=1)[0][self.fembs[0]]
        return rawdata 


    def dat_fe_only_cfg(self, sts=0, snc=0,sg0=0, sg1=0, st0=1, st1=1, swdac=0, sdd=0, sdf=0, dac=0x00, sgp=0, slk0=0, slk1=0, chn=128):
        cfg_paras_rec = []
        for femb_id in self.fembs:
            self.set_fe_reset()
            if chn >=128: #configurate all channels
                self.set_fe_board(sts=sts, snc=snc,sg0=sg0, sg1=sg1, st0=st0, st1=st1, swdac=swdac, sdd=sdd, sdf=sdf, dac=dac, sgp=sgp, slk0=slk0, slk1=slk1 )
            else:
                ch = chn%16 #only enable one chanel per FE chip
                for fe in range(8):
                    self.set_fechn_reg(chip=fe&0x07, chn=ch, sts=sts, snc=snc,sg0=sg0, sg1=sg1, st0=st0, st1=st1, sdf=sdf)
                    self.set_fechip_global(chip=fe&0x07, swdac=swdac, sdd=sdd, dac=dac, sgp=sgp, slk0=slk0, slk1=slk1)
                self.set_fe_sync()
            self.femb_fe_cfg(femb_id=femb_id)
            if self.sddflg != sdd :
                for i in range(8):
                    self.adcs_paras[i][2] = sdd
#            self.adcs_paras = [ # c_id, data_fmt(0x89), sha_cs(0x84), ibuf_cs(0x80), vrefp, vrefn, vcmo, vcmi, autocali
#                                    [0x4, 0x08, sdd, 0, 0xDF, 0x33, 0x89, 0x67, 0],
#                                    [0x5, 0x08, sdd, 0, 0xDF, 0x33, 0x89, 0x67, 0],
#                                    [0x6, 0x08, sdd, 0, 0xDF, 0x33, 0x89, 0x67, 0],
#                                    [0x7, 0x08, sdd, 0, 0xDF, 0x33, 0x89, 0x67, 0],
#                                    [0x8, 0x08, sdd, 0, 0xDF, 0x33, 0x89, 0x67, 0],
#                                    [0x9, 0x08, sdd, 0, 0xDF, 0x33, 0x89, 0x67, 0],
#                                    [0xA, 0x08, sdd, 0, 0xDF, 0x33, 0x89, 0x67, 0],
#                                    [0xB, 0x08, sdd, 0, 0xDF, 0x33, 0x89, 0x67, 0],
#                                  ]

                self.femb_adc_cfg(femb_id=femb_id)
                self.sddflg = sdd 
            cfg_paras_rec.append( (femb_id, copy.deepcopy(self.adcs_paras), copy.deepcopy(self.regs_int8)) )
        print ("Wait %d seconds for FEMB configruatio (FE) is stable..."%self.fedly)
        time.sleep(self.fedly)
        return cfg_paras_rec

    def dat_fe_qc_acq(self, num_samples = 1):
        #time.sleep(1)
        rawdata = self.spybuf_trig(fembs=self.fembs, num_samples=num_samples, trig_cmd=0) #returns list of size 1
        return rawdata

    def dat_fe_qc_rst(self, num_samples = 1):
        self.femb_cd_rst()
        for femb_id in self.fembs:
            self.femb_cd_fc_act(femb_id, act_cmd="rst_adcs")
            self.femb_cd_fc_act(femb_id, act_cmd="rst_larasics")
            self.femb_cd_fc_act(femb_id, act_cmd="rst_larasic_spi")

    def dat_fe_qc(self, num_samples=1, adac_pls_en=0, sts=0, snc=0,sg0=0, sg1=0, st0=1, st1=1, swdac=0, sdd=0, sdf=0, dac=0x00, sgp=0, slk0=0, slk1=0, chn=128):
        cfg_info = self.dat_fe_qc_cfg(adac_pls_en=adac_pls_en, sts=sts, snc=snc,sg0=sg0, sg1=sg1, st0=st0, st1=st1, swdac=swdac, sdd=sdd, sdf=sdf, dac=dac, sgp=sgp, slk0=slk0, slk1=slk1 )
        if cfg_info == False:
            return False
        data =  self.dat_fe_qc_acq(num_samples)
        #self.dat_fe_qc_rst()
        return data, cfg_info

    def dat_cali_source(self, cali_mode=3, val=1.090, period=0x200, width=0x180, asicdac=0x10, chips=0xff):
        #cali_mode: 0 = direct input, 1 = DAT DAC, 2 = ASIC DAC, 3 or larger: disable cali
        if cali_mode <0 or cali_mode >3:
            cali_mode=3
            #print ("\033[91m" + "Wrong value for cali_mode"+ "\033[0m")
            #print ("\033[91m" + "cali_mode: 0 = direct input, 1 = DAT DAC, 2 = ASIC DAC, 3 =disable cali" + "\033[0m" )
            #print ("\033[91m" + "Exit anyway!"+ "\033[0m")
            #self.femb_powering([])
            #self.data_align_flg = False
            #exit()

        self.dat_fpga_reset()
        if cali_mode < 2:
            valint = int(val*65536/self.ADCVREF)
            self.dat_set_dac(val=valint, fe_cal=0)
            if self.rev == 0:
                self.cdpoke(0, 0xC, 0, self.DAT_FE_CMN_SEL, 4)    
            else:
                self.cdpoke(0, 0xC, 0, self.DAT_FE_CMN_SEL, 1)    
            width = width&0xfff # width = duty, it must be less than (perod-2)
            period = period&0xfff #period = ADC samples between uplses
            if width >= period - 2:
                width = period - 2
            self.cdpoke(0, 0xC, 0, self.DAT_TEST_PULSE_WIDTH_MSB, ((width*32)>>8)&0xff)
            self.cdpoke(0, 0xC, 0, self.DAT_TEST_PULSE_WIDTH_LSB, (width*32)&0xff)  
            self.cdpoke(0, 0xC, 0, self.DAT_TEST_PULSE_PERIOD_MSB, period>>8)  
            self.cdpoke(0, 0xC, 0, self.DAT_TEST_PULSE_PERIOD_LSB, period&0xff)  
            self.cdpoke(0, 0xC, 0, self.DAT_TEST_PULSE_EN, 0x4)  
            self.cdpoke(0, 0xC, 0, self.DAT_EXT_PULSE_CNTL, 1)    

            chncs = 0xffff
            if self.rev == 0:
                skt_en = 0xff
            elif self.rev == 1:
                skt_en = chips 
            self.cdpoke(0, 0xC, 0, self.DAT_ADC_FE_TEST_SEL, 3<<4)    
            self.cdpoke(0, 0xC, 0, self.DAT_FE_TEST_SEL_INHIBIT, 0x00)   
            if cali_mode == 0:
                self.cdpoke(0, 0xC, 0, self.DAT_FE_CALI_CS, ~skt_en)  #direct input
                self.cdpoke(0, 0xC, 0, self.DAT_TEST_PULSE_SOCKET_EN, skt_en)  #direct input
                self.cdpoke(0, 0xC, 0, self.DAT_FE_IN_TST_SEL_MSB, (chncs>>8)&0xff)   #direct input
                self.cdpoke(0, 0xC, 0, self.DAT_FE_IN_TST_SEL_LSB, chncs&0xff)   #direct input
                adac_pls_en = 0
                sts = 0
                swdac = 0
                dac = 0
            if cali_mode == 1:
                self.cdpoke(0, 0xC, 0, self.DAT_FE_CALI_CS, skt_en)  #DAT DAC
                self.cdpoke(0, 0xC, 0, self.DAT_TEST_PULSE_SOCKET_EN, ~skt_en)  #direct input disabled
                self.cdpoke(0, 0xC, 0, self.DAT_FE_IN_TST_SEL_MSB, (chncs>>8)&0xff)   #direct input
                self.cdpoke(0, 0xC, 0, self.DAT_FE_IN_TST_SEL_LSB, chncs&0xff)   #direct input
                adac_pls_en = 0
                sts = 1
                swdac = 2
                dac = 0

        if cali_mode == 2:
            adac_pls_en = 1
            sts = 1
            swdac = 1
            dac = asicdac
        if cali_mode == 3:
            adac_pls_en = 0
            sts = 0
            swdac = 0
            dac = 0
        time.sleep(0.1)
        return adac_pls_en, sts, swdac, dac


    def dat_asic_chk(self):
        datad = {}

        self.fedly = 1
        adac_pls_en, sts, swdac, dac = self.dat_cali_source(cali_mode=2,asicdac=0x20)
        rawdata = self.dat_fe_qc(num_samples=5, adac_pls_en=adac_pls_en, sts=sts, swdac=swdac, dac=dac,snc=1,sg0=1, sg1=1, sdd=0)
        if rawdata == False:
            return False
        #wibdata = wib_dec(rawdata[0], fembs=self.fembs, spy_num=1)[0]
        fes_pwr_info =  self.fe_pwr_meas()
        datad["ASICDAC_47mV_CHK"] = (self.fembs, rawdata[0], rawdata[1], fes_pwr_info)

        adac_pls_en, sts, swdac, dac = self.dat_cali_source(cali_mode=2,asicdac=0x10)
        rawdata = self.dat_fe_qc(num_samples=5, adac_pls_en=adac_pls_en, sts=sts, swdac=swdac, dac=dac,snc=1,sg0=1, sg1=1, sdd=0)
        if rawdata == False:
            return False
        #wibdata = wib_dec(rawdata[0], fembs=self.fembs, spy_num=1)[0]
        fes_pwr_info =  self.fe_pwr_meas()
        datad["ASICDAC_47mV_CHK_x10"] = (self.fembs, rawdata[0], rawdata[1], fes_pwr_info)

        adac_pls_en, sts, swdac, dac = self.dat_cali_source(cali_mode=2,asicdac=0x18)
        rawdata = self.dat_fe_qc(num_samples=5, adac_pls_en=adac_pls_en, sts=sts, swdac=swdac, dac=dac,snc=1,sg0=1, sg1=1, sdd=0)
        if rawdata == False:
            return False
        #wibdata = wib_dec(rawdata[0], fembs=self.fembs, spy_num=1)[0]
        fes_pwr_info =  self.fe_pwr_meas()
        datad["ASICDAC_47mV_CHK_x18"] = (self.fembs, rawdata[0], rawdata[1], fes_pwr_info)

        adac_pls_en, sts, swdac, dac = self.dat_cali_source(cali_mode=3)
        rawdata = self.dat_fe_qc(num_samples=5, adac_pls_en=adac_pls_en, snc=1,sg0=1, sg1=1, sdd=0)
        if rawdata == False:
            return False
        #wibdata = wib_dec(rawdata[0], fembs=self.fembs, spy_num=1)[0]
        fes_pwr_info =  self.fe_pwr_meas()
        datad["ASICDAC_47mV_RMS"] = (self.fembs, rawdata[0], rawdata[1], fes_pwr_info)


        self.fedly = 1
        adac_pls_en, sts, swdac, dac = self.dat_cali_source(cali_mode=0, val=self.fe_cali_vref-0.05, period=0x200, width=0x180, asicdac=0x10)
        rawdata = self.dat_fe_qc(num_samples=5, adac_pls_en=adac_pls_en, sts=sts, swdac=swdac, dac=dac, snc=1) #direct FE input
        if rawdata == False:
            return False
        #wibdata = wib_dec(rawdata[0], fembs=self.fembs, spy_num=1)[0]
        fes_pwr_info =  self.fe_pwr_meas()
        datad["DIRECT_PLS_CHK"] = (self.fembs, rawdata[0], rawdata[1], fes_pwr_info)

        adac_pls_en, sts, swdac, dac = self.dat_cali_source(cali_mode=3)
        rawdata = self.dat_fe_qc(num_samples=5, adac_pls_en=adac_pls_en,  snc=1) #direct FE input
        if rawdata == False:
            return False
        #wibdata = wib_dec(rawdata[0], fembs=self.fembs, spy_num=1)[0]
        fes_pwr_info =  self.fe_pwr_meas()
        datad["DIRECT_PLS_RMS"] = (self.fembs, rawdata[0], rawdata[1], fes_pwr_info)

        self.fedly = 3
        adac_pls_en, sts, swdac, dac = self.dat_cali_source(cali_mode=2,asicdac=0x20)
        rawdata = self.dat_fe_qc(num_samples=5, adac_pls_en=adac_pls_en, sts=sts, swdac=swdac, dac=dac,snc=1,sg0=0, sg1=0, sdd=1)
        if rawdata == False:
            return False
        #wibdata = wib_dec(rawdata[0], fembs=self.fembs, spy_num=1)[0]
        fes_pwr_info =  self.fe_pwr_meas()
        datad["ASICDAC_CALI_CHK"] = (self.fembs, rawdata[0], rawdata[1], fes_pwr_info)

        adac_pls_en, sts, swdac, dac = self.dat_cali_source(cali_mode=3)
        rawdata = self.dat_fe_qc(num_samples=5, adac_pls_en=adac_pls_en, snc=1,sg0=0, sg1=0, sdd=1)
        if rawdata == False:
            return False
        #wibdata = wib_dec(rawdata[0], fembs=self.fembs, spy_num=1)[0]
        fes_pwr_info =  self.fe_pwr_meas()
        datad["ASICDAC_CALI_RMS"] = (self.fembs, rawdata[0], rawdata[1], fes_pwr_info)

        self.fedly = 1
        return datad


    def dat_coldadc_input_cs(self,  mode="DACSE", SHAorADC = "SHA", chsenl=0x0000):
        #disable FE feeding
        self.cdpoke(0, 0xC, 0, 0x62, 0x0f) #FE_CMS_INH, CSC, CSB, CSA

        if "P6DIFF" in mode:
            self.cdpoke(0, 0xC, 0, self.DAT_ADC_PN_TST_SEL, 0x22)
        elif "P6SE" in mode:
            self.cdpoke(0, 0xC, 0, self.DAT_ADC_PN_TST_SEL, 0x02)
        elif "WIBDIFF" in mode: #new DAT
            print ("Only on new DAT")
            self.cdpoke(0, 0xC, 0, self.DAT_ADC_PN_TST_SEL, 0x11)
        elif "WIBSE" in mode:
            self.cdpoke(0, 0xC, 0, self.DAT_ADC_PN_TST_SEL, 0x01)
        elif "DACDIFF" in mode:
            self.cdpoke(0, 0xC, 0, self.DAT_ADC_PN_TST_SEL, 0x33)
        elif "DACSE" in mode:
            self.cdpoke(0, 0xC, 0, self.DAT_ADC_PN_TST_SEL, 0x03)
        elif "OPEN" in mode:
            self.cdpoke(0, 0xC, 0, self.DAT_ADC_PN_TST_SEL, 0x66)
        elif "V2P6_SE2DIFF" in mode:
            self.cdpoke(0, 0xC, 0, self.DAT_ADC_PN_TST_SEL, 0x66)
        elif "V2WIB_SE2DIFF" in mode:
            self.cdpoke(0, 0xC, 0, self.DAT_ADC_PN_TST_SEL, 0x77)

        if "ADC" in SHAorADC: #to ADC input directly 
            self.cdpoke(0, 0xC, 0, self.DAT_ADC_TEST_IN_SEL, 1)
        else:
            self.cdpoke(0, 0xC, 0, self.DAT_ADC_TEST_IN_SEL, 0)

        self.cdpoke(0, 0xC, 0, self.DAT_ADC_SRC_CS_P_LSB, chsenl&0xFF)
        self.cdpoke(0, 0xC, 0, self.DAT_ADC_SRC_CS_P_MSB, (chsenl>>8)&0xFF)


    def dat_coldadc_cali_cs(self,  mode="SE", chsenl=0x0000):
        if "DIFF" in mode:
            self.cdpoke(0, 0xC, 0, self.DAT_ADC_PN_TST_SEL, 0x33)
        else:
            self.cdpoke(0, 0xC, 0, self.DAT_ADC_PN_TST_SEL, 0x03)

        self.cdpoke(0, 0xC, 0, self.DAT_ADC_TEST_IN_SEL, 0)
        # ##Set ADC_SRC_CS_P to 0x0000 (ADC_SRC_CS_P_MSB, ADC_SRC_CS_P_LSB)

        self.cdpoke(0, 0xC, 0, self.DAT_ADC_SRC_CS_P_LSB, chsenl&0xFF)
        self.cdpoke(0, 0xC, 0, self.DAT_ADC_SRC_CS_P_MSB, (chsenl>>8)&0xFF)

    def dat_coldadc_ext(self, ext_source="DAT_P6", chsenl=0x0000):
        ##DAC ADC N to 0V
        ##make sure ADCs are hooked to P6/P7
        ## ##Set ADC_P_TST_CSABC to 2, set ADC_N_TST_CSABC to 0  [Set ADC_P_TST_SEL to 0 | (0 << 4)]

        if "P6" in ext_source:
            self.cdpoke(0, 0xC, 0, self.DAT_ADC_PN_TST_SEL, 0x02) #N tie to GND #SE
            #self.cdpoke(0, 0xC, 0, self.DAT_ADC_PN_TST_SEL, 0x22) #N tie to GND #DIFF
        elif "WIB" in ext_source:
            self.cdpoke(0, 0xC, 0, self.DAT_ADC_PN_TST_SEL, 0x01) #N tie to GND

        # ##Set ADC_TEST_IN_SEL to 0, direct input to ADC x16 inputs
        self.cdpoke(0, 0xC, 0, self.DAT_ADC_TEST_IN_SEL, 0)

        # ##Set ADC_SRC_CS_P to 0x0000 (ADC_SRC_CS_P_MSB, ADC_SRC_CS_P_LSB)
        #high(default) connects ADC to FE, low connects ADC to other sources
        self.cdpoke(0, 0xC, 0, self.DAT_ADC_SRC_CS_P_LSB, chsenl&0xFF)
        self.cdpoke(0, 0xC, 0, self.DAT_ADC_SRC_CS_P_MSB, (chsenl>>8)&0xFF)


        #self.cdpoke(0, 0xC, 0, self.DAT_ADC_PN_TST_SEL, 0x00) #N tie to GND #SE
        #self.cdpoke(0, 0xC, 0, self.DAT_ADC_TEST_IN_SEL, 1)

        ## ##Set ADC_SRC_CS_P to 0x0000 (ADC_SRC_CS_P_MSB, ADC_SRC_CS_P_LSB)
        #self.cdpoke(0, 0xC, 0, self.DAT_ADC_SRC_CS_P_LSB, 0xFE)
        #self.cdpoke(0, 0xC, 0, self.DAT_ADC_SRC_CS_P_MSB, 0xff)

    def dat_coldata_efuse_prm(self, femb_id=0, chip_addr=0x0C, efuseid=0):
        if (efuseid < 0) :
            print ("Error, EFUSE ID must be >=0")
            input ("Pause...")
        elif (efuseid > 0x80000000) :
            print ("Error, EFUSE ID must be <0x80000000")
            input ("Pause...")
        efusevalue=(efuseid<<1)&0xFFFFFFFF
        efuse_enable_regadr =  62
        efuse_start_regadr = 67
        efuse_data07adr =88 
        efuse_data0fadr =89 
        efuse_data17adr =90 
        efuse_data1fadr =91 

        while True:
            self.femb_cd_rst()
            time.sleep(0.1)
            self.femb_i2c_wrchk(femb_id=femb_id, chip_addr=chip_addr, reg_page=0, reg_addr=efuse_enable_regadr, wrdata= 0x8)
            self.femb_i2c_wrchk(femb_id=femb_id, chip_addr=chip_addr, reg_page=0, reg_addr=efuse_start_regadr, wrdata= 0)
            self.femb_i2c_wrchk(femb_id=femb_id, chip_addr=chip_addr, reg_page=0, reg_addr=efuse_data07adr,  wrdata=efusevalue&0xff      )
            self.femb_i2c_wrchk(femb_id=femb_id, chip_addr=chip_addr, reg_page=0, reg_addr=efuse_data0fadr, wrdata=(efusevalue>>8)&0xff )
            self.femb_i2c_wrchk(femb_id=femb_id, chip_addr=chip_addr, reg_page=0, reg_addr=efuse_data17adr, wrdata=(efusevalue>>16)&0xff)
            self.femb_i2c_wrchk(femb_id=femb_id, chip_addr=chip_addr, reg_page=0, reg_addr=efuse_data1fadr, wrdata=(efusevalue>>24)&0xff)
            self.femb_i2c_wrchk(femb_id=femb_id, chip_addr=chip_addr, reg_page=0, reg_addr=efuse_start_regadr, wrdata= 1)
            time.sleep(0.1)
            self.femb_i2c_wrchk(femb_id=femb_id, chip_addr=chip_addr, reg_page=0, reg_addr=efuse_start_regadr, wrdata= 0)
            self.femb_cd_rst()
            self.femb_i2c_wrchk(femb_id=femb_id, chip_addr=chip_addr, reg_page=0, reg_addr=efuse_enable_regadr, wrdata= 0x0)

            self.femb_i2c_wrchk(0, 0x3, 0, 0x1f,1)
            time.sleep(0.01)
            efusev18 = self.cdpeek(0, 0x3, 0, 0x18)
            efusev19 = self.cdpeek(0, 0x3, 0, 0x19)
            efusev1A = self.cdpeek(0, 0x3, 0, 0x1A)
            efusev1B = self.cdpeek(0, 0x3, 0, 0x1B)
            efusev = efusev18 + (efusev19<<8) + (efusev1A<<16) +(efusev1B<<24)
            if (efuseid&efusev) == efuseid :
                print ("Efuse was programmed, readback value is 0x%x"%efusev)
                break
            else:
                print ("Not all bits were programmed, re-program...")
                print ("WriteEfuse=0x%x, ReadEfuse=0x%x"%(efuseid, efusev))
                break

    def dat_fpga_reset(self):
        tmpi = 0
        while True:
            tmpi = tmpi + 1
            wrv = 0x03
            self.cdpoke(0, 0xC, 0, self.DAT_FPGA_RST, 0x3)  
            time.sleep(0.2)
            rdv = self.cdpeek(0, 0xC, 0, self.DAT_FPGA_RST)  
            if rdv == 0x00:
                print ("DAT FPGA is reset")
                self.data_align_flg = False
                return True
            else:
                time.sleep(1)
                if tmpi < 30:
                    print ("Try to reset DAT FPGA...")
                    pass
                else:
                    print ("Can't reset DAT FPGA, please check data cable connection")
                    self.femb_powering([])
                    return False


    def dat_monadcs(self, mode="fe"):
        if mode != "fe" and mode != "adc":
            print("dat_monadcs: mode can be 'fe' or 'adc'")
            return
        avg_datas = [[],[],[],[],[],[],[],[]]
        avg = self.monadc_avg
        for avgi in range(avg):            
            self.dat_monadc_trig() #get rid of previous result    
            self.dat_monadc_trig() #get rid of previous result   
            for chip in range(8):
                for check in range(10):
                    if mode == "fe":
                        if not self.dat_monadc_busy(fe=chip):
                            break;
                    elif mode == "adc":
                        if not self.dat_monadc_busy(adc=chip):
                            break;                        
                    if check is 9:
                        print("Timed out while waiting for AD7274 controller to finish")
                if mode == "fe":
                    data = self.dat_monadc_getdata(fe=chip)
                elif mode == "adc":
                    data = self.dat_monadc_getdata(adc=chip)
                avg_datas[chip].append(data)
        datas = []
        datas_std = []
        for chip in range(8):
            if avg == 1:
                datas.append(avg_datas[chip][0])
                datas_std.append(0)
            else:
                datas.append(int(np.mean(avg_datas[chip])))
                datas_std.append(np.std(avg_datas[chip]))
        return datas, datas_std

    def dat_fe_vbgrs(self):
        #measure VBGR through VBGR pin
        print ("measure VBGR through VBGR pin")
        mon_datas = {} 
        mux_cs = 4
        mux_name = self.mon_fe_cs[mux_cs]
        self.cdpoke(0, 0xC, 0, self.DAT_FE_CALI_CS, 0x00)    
        self.cdpoke(0, 0xC, 0, self.DAT_TEST_PULSE_EN, 0x00) #disable pin4 of U230 (FE_INS_PLS_CS)   
        self.cdpoke(0, 0xC, 0, self.DAT_TEST_PULSE_SOCKET_EN, 0x00) #disable pin4 of U230 (FE_INS_PLS_CS = 1)   
        self.cdpoke(0, 0xC, 0, self.DAT_FE_IN_TST_SEL_LSB, 0x00)    
        self.cdpoke(0, 0xC, 0, self.DAT_FE_IN_TST_SEL_MSB, 0x00)    
        self.cdpoke(0, 0xC, 0, self.DAT_ADC_FE_TEST_SEL, mux_cs<<4)    
        self.cdpoke(0, 0xC, 0, self.DAT_FE_TEST_SEL_INHIBIT, 0x00)    
        time.sleep(0.2)
        datas = self.dat_monadcs()[0]
        datas_v = np.array(datas)*self.AD_LSB
        mon_datas["VBGR"] = [datas, datas_v]
        return mon_datas


    def dat_fe_mons(self, mon_type=0x1f ):
        #measure VBGR/Temperature through Monitoring pin
        femb_id = self.fembs[0]

        for i in range(8):
            self.adcs_paras[i][8] = 0 # disable autocali 
#            self.adcs_paras = [ # c_id, data_fmt(0x89), sha_cs(0x84), ibuf_cs(0x80), vrefp, vrefn, vcmo, vcmi, autocali
#                            [0x4, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 0],
#                            [0x5, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 0],
#                            [0x6, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 0],
#                            [0x7, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 0],
#                            [0x8, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 0],
#                            [0x9, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 0],
#                            [0xA, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 0],
#                            [0xB, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 0],
#                          ]

        mux_cs=5
        mux_name = self.mon_fe_cs[mux_cs]
        self.cdpoke(femb_id, 0xC, 0, self.DAT_FE_CALI_CS, 0xFF)    
        self.cdpoke(femb_id, 0xC, 0, self.DAT_TEST_PULSE_EN, 0x00) #disable pin4 of U230 (FE_INS_PLS_CS)   
        self.cdpoke(femb_id, 0xC, 0, self.DAT_TEST_PULSE_SOCKET_EN, 0x00) #disable pin4 of U230 (FE_INS_PLS_CS = 1)   
        self.cdpoke(femb_id, 0xC, 0, self.DAT_FE_IN_TST_SEL_LSB, 0x00)    
        self.cdpoke(femb_id, 0xC, 0, self.DAT_FE_IN_TST_SEL_MSB, 0x00)    
        self.cdpoke(femb_id, 0xC, 0, self.DAT_ADC_FE_TEST_SEL, mux_cs<<4)    
        self.cdpoke(femb_id, 0xC, 0, self.DAT_FE_TEST_SEL_INHIBIT, 0xff)    

        mon_datas = {} 

        #mon_type = 0x01: Temperature
        if mon_type&0x01:
            print ("measure Temperatue through Monitoring pin")
            self.set_fe_reset()
            chn = 0
            stb0=1
            stb1=0
 
            for fe in range(8):
                self.set_fechn_reg(chip=fe&0x07, chn=chn, smn=1, sdf=1) 
                self.set_fechip_global(chip=fe&0x07, stb1=stb1, stb=stb0)
            self.set_fe_sync()
            self.femb_fe_cfg(femb_id=femb_id)
            time.sleep(0.2)
            datas = self.dat_monadcs()[0]
            datas_v = np.array(datas)*self.AD_LSB
            mon_datas["MON_Temper"] = [datas, datas_v]

        #mon_type = 0x2: VBGR
        if mon_type&0x02:
            print ("measure VBGR through Monitoring pin")
            self.set_fe_reset()
            chn = 0
            stb1=1
            stb0=1
            for fe in range(8):
                self.set_fechn_reg(chip=fe&0x07, chn=chn, smn=1, sdf=1) 
                self.set_fechip_global(chip=fe&0x07, stb1=stb1, stb=stb0)
            self.set_fe_sync()
            self.femb_fe_cfg(femb_id=femb_id)
            time.sleep(0.2)
            datas = self.dat_monadcs()[0]
            datas_v = np.array(datas)*self.AD_LSB
            mon_datas["MON_VBGR"] = [datas, datas_v]

        #mon_type = 0x4: DAC
        if mon_type&0x04:
            print ("measure LArASIC DAC through Monitoring pin, wait 2-3 minutes")
            self.set_fe_reset()
            chn = 0
            sg0=0
            sg1=0
            sgp=1
 
            self.set_fe_board(sg0=sg0, sg1=sg1)
            datas_dac =[]
            for dac in range(0,64, 1):
                for fe in range(8):
                    self.set_fechip_global(chip=fe&0x07, swdac=3, dac=dac, sgp=sgp)
                self.set_fe_sync()
                self.femb_fe_cfg(femb_id=femb_id)
                time.sleep(0.1)
                datas = self.dat_monadcs()[0]
                datas_dac.append([dac, datas])
                #print ([sgp, dac, datas])
            mon_datas["MON_DAC_SGP1"] = datas_dac

            sgp=0
            for sg0 in [0,1]:
                for sg1 in [0,1]:
                    datas_dac =[]
                    for dac in range(0,64, 1):
                        for fe in range(8):
                            self.set_fechip(chip=fe&0x07, swdac=3, sg0=sg0, sg1=sg1, dac=dac, sgp=sgp)
                        self.set_fe_sync()
                        self.femb_fe_cfg(femb_id=femb_id)
                        time.sleep(0.1)
                        datas = self.dat_monadcs()[0]
                        datas_dac.append([dac, datas])
                        #print ([sg0, sg1, sgp, dac, datas])
                    mon_datas["MON_DAC_SG0_%d_SG1_%d"%(sg0, sg1)] = datas_dac

        #if mon_type == 0x08: 200mV BL
        if mon_type&0x08:
            stb0=0
            stb1=0
            print ("measure LArASIC 200mV BL through Monitoring pin")
            datas_chs = []
            for chn in range(16):
                self.set_fe_reset()
                for fe in range(8):
                    self.set_fechn_reg(chip=fe&0x07, chn=chn, snc=1, smn=1,st0=1, st1=1, sdf=1) 
                self.set_fe_sync()
                self.femb_fe_cfg(femb_id=femb_id)
                time.sleep(0.1)
                datas=self.dat_monadcs()[0]
                datas_chs.append([chn, datas])
            mon_datas["MON_200BL"] = datas_chs

        #if mon_type == 0x10: 900mV BL
        if mon_type&0x10:
            stb0=0
            stb1=0
            print ("measure LArASIC 900mV BL through Monitoring pin")
            datas_chs = []
            for chn in range(16):
                self.set_fe_reset()
                for fe in range(8):
                    self.set_fechn_reg(chip=fe&0x07, chn=chn, snc=0, smn=1,st0=1, st1=1, sdf=1) 
                self.set_fe_sync()
                self.femb_fe_cfg(femb_id=femb_id)
                time.sleep(0.1)
                datas=self.dat_monadcs()[0]
                datas_chs.append([chn, datas])
            mon_datas["MON_900BL"] = datas_chs

        if True: #disable monitoring
            self.set_fe_reset()
            self.set_fe_sync()
            self.femb_fe_cfg(femb_id=femb_id)
            mux_cs=0
            mux_name = self.mon_fe_cs[mux_cs]
            self.cdpoke(femb_id, 0xC, 0, self.DAT_FE_CALI_CS, 0x00)    
            self.cdpoke(femb_id, 0xC, 0, self.DAT_TEST_PULSE_EN, 0x00) #disable pin4 of U230 (FE_INS_PLS_CS = 1)   
            self.cdpoke(femb_id, 0xC, 0, self.DAT_TEST_PULSE_SOCKET_EN, 0x00) #disable pin4 of U230 (FE_INS_PLS_CS = 1)   
            self.cdpoke(femb_id, 0xC, 0, self.DAT_ADC_FE_TEST_SEL, mux_cs<<4)    
            self.cdpoke(femb_id, 0xC, 0, self.DAT_FE_TEST_SEL_INHIBIT, 0xFF)    
        return mon_datas

    def dat_adc_mons(self,femb_id=0, mon_type=0xff):
        #femb_id = self.fembs[0]
        
        mon_datas = {} 
        
        #mon_type = 0x01: VOLTAGE_MONITOR_MUX
        if mon_type&0x01:
            mux_cs = 0
            mux_name = self.mon_adc_cs[mux_cs]
            self.cdpoke(femb_id, 0xC, 0, self.DAT_ADC_FE_TEST_SEL, mux_cs)   
            time.sleep(0.1) #delay 200 ms to allow voltage to settle
            datas = self.dat_monadcs(mode="adc")[0]
            datas_v = np.array(datas)*self.AD_LSB
            mon_datas["MON_Vmon"] = [datas, datas_v]    
            
        #mon_type = 0x2: CURRENT_MONITOR_MUX
        if mon_type&0x02:
            mux_cs = 1
            mux_name = self.mon_adc_cs[mux_cs]
            self.cdpoke(femb_id, 0xC, 0, self.DAT_ADC_FE_TEST_SEL, mux_cs)    
            time.sleep(0.1) #delay 200 ms to allow voltage to settle
            datas = self.dat_monadcs(mode="adc")[0]
            datas_v = np.array(datas)*self.AD_LSB
            mon_datas["MON_Imon"] = [datas, datas_v]     
        
        #mon_type = 0x4: VREFP
        if mon_type&0x04:
            mux_cs = 2
            mux_name = self.mon_adc_cs[mux_cs]
            self.cdpoke(femb_id, 0xC, 0, self.DAT_ADC_FE_TEST_SEL, mux_cs) 
            time.sleep(0.1) #delay 200 ms to allow voltage to settle            
            datas = self.dat_monadcs(mode="adc")[0]
            datas_v = np.array(datas)*self.AD_LSB
            mon_datas["MON_VREFP"] = [datas, datas_v]     

        #mon_type = 0x8: VREFN
        if mon_type&0x08:
            mux_cs = 3
            mux_name = self.mon_adc_cs[mux_cs]
            self.cdpoke(femb_id, 0xC, 0, self.DAT_ADC_FE_TEST_SEL, mux_cs)  
            time.sleep(0.1) #delay 200 ms to allow voltage to settle
            datas = self.dat_monadcs(mode="adc")[0]
            datas_v = np.array(datas)*self.AD_LSB
            mon_datas["MON_VREFN"] = [datas, datas_v]  

        #mon_type = 0x10: VCMI
        if mon_type&0x10:
            mux_cs = 4
            mux_name = self.mon_adc_cs[mux_cs]
            self.cdpoke(femb_id, 0xC, 0, self.DAT_ADC_FE_TEST_SEL, mux_cs)  
            time.sleep(0.1) #delay 200 ms to allow voltage to settle
            datas = self.dat_monadcs(mode="adc")[0]
            datas_v = np.array(datas)*self.AD_LSB
            mon_datas["MON_VCMI"] = [datas, datas_v]

        #mon_type = 0x20: VCMO
        if mon_type&0x20:
            mux_cs = 5
            mux_name = self.mon_adc_cs[mux_cs]
            self.cdpoke(femb_id, 0xC, 0, self.DAT_ADC_FE_TEST_SEL, mux_cs)    
            time.sleep(0.1) #delay 200 ms to allow voltage to settle
            datas = self.dat_monadcs(mode="adc")[0]
            datas_v = np.array(datas)*self.AD_LSB
            mon_datas["MON_VCMO"] = [datas, datas_v]

        #mon_type = 0x40: AUX_ISINK_MUX
        if mon_type&0x40:
            mux_cs = 6
            mux_name = self.mon_adc_cs[mux_cs]
            self.cdpoke(femb_id, 0xC, 0, self.DAT_ADC_FE_TEST_SEL, mux_cs) 
            time.sleep(0.2) #delay 200 ms to allow voltage to settle            
            datas = self.dat_monadcs(mode="adc")[0]
            datas_v = np.array(datas)*self.AD_LSB
            mon_datas["MON_Isink"] = [datas, datas_v]

        #mon_type = 0x80: AUX_ISOURCE_MUX
        if mon_type&0x80:
            mux_cs = 7
            mux_name = self.mon_adc_cs[mux_cs]
            self.cdpoke(femb_id, 0xC, 0, self.DAT_ADC_FE_TEST_SEL, mux_cs)
            time.sleep(0.2) #delay 200 ms to allow voltage to settle
            datas = self.dat_monadcs(mode="adc")[0]
            datas_v = np.array(datas)*self.AD_LSB
            mon_datas["MON_Isrc"] = [datas, datas_v]
            
        return mon_datas
    
    def adc_histbuf(self): #adapted from llc.spybuf()
        HIST_MEM_SIZE = 0x8000 #rom A00C8000 to A00CFFFF
        buf = (ctypes.c_char*HIST_MEM_SIZE)()
        buf_bytes = bytearray(HIST_MEM_SIZE)
        

        self.wib.bufread(buf,8) #read from histogram memory
        byte_ptr = (ctypes.c_char*HIST_MEM_SIZE).from_buffer(buf_bytes)            
        if not ctypes.memmove(byte_ptr, buf, HIST_MEM_SIZE):
            print('memmove failed')
            return None
                    
        return buf_bytes     
    
    def dat_adc_histbuf_trig(self, num_samples=1639000, waveform='ramp'):
        #set samples to take
        self.poke(0xA00C007C, num_samples)

        hist_data = []

        chs = []
        for femb in self.fembs:
            for ch in range(128):
                chs.append(femb*128+ch)

        start = time.time()
        for ch in chs:    
            self.dat_adc_ch_cs(ch=ch)
            #indicate which channel is to be analyzed
            # self.poke(0xA00C0078, ch | (0x1<<9)) #extra bit is to make sure trigger is output over P12 LEMO
            self.poke(0xA00C0078, ch)
            
            if waveform == 'RAMP':                
                while True:
                # while self.peek(0xA00C00F0) & ~(0x3ff) != 0x000: #wait till monitor output = 0x000
                    peek = self.peek(0xA00C00F0) >> 10
                    if peek < 500:
                        break
                    pass
            
            #trigger histogram
            self.poke(0xA00C0074, 0x1)
            self.poke(0xA00C0074, 0x0)
            
            tries = 0
            while self.peek(0xA00C00F0) & (0x1<<9) == 0: #while hist not done
                pass
            ch_hist_data = self.adc_histbuf()
                
            print("Hist of Ch%d is done"%ch) 

            hist_data.append(ch_hist_data)

        print("Connecting ADC back to ASIC channels")
        self.cdpoke(0, 0xC, 0, self.DAT_ADC_SRC_CS_P_LSB, 0xFF)
        self.cdpoke(0, 0xC, 0, self.DAT_ADC_SRC_CS_P_MSB, 0xFF)
        
        return hist_data    
        
    def dat_enob_acq(self, sineflg=True):
        #print("WIB ENOB 16,384 samples test")  
        #print("before running this script: configure the FEMB chips and trigger")  
        ch_data = []
        for ch in range(512):
            if (ch // 128) not in self.fembs:
               ch_data.append(None)
               continue

            while True:
                self.poke(0xa00c0078, ch)
                #trigger capture
                self.poke(0xa00c0074, 0x3)
                self.poke(0xa00c0074, 0x2)
                #wait till capture done
                tries = 0
                while (self.peek(0xa00c00f0) & 0x100) == 0:            
                    pass
                    tries = tries + 1
                    if tries == 20000:
                        print("ENOB waveform acquisition failed for channel",ch)
                        print("Aborting acquisition")
                        return ch_data
                self.poke(0xa00c0074, 0x0)
                data = self.adc_histbuf() #block read
                if sineflg:
                    if self.enobdata_check(ch, data): #check if data is good
                        break
                else:
                    break
            
            ch_data.append(data)
        return ch_data        

    def dat_enob_acq_2 (self, sineflg=True):
        ch_data = []
        for ch in range(512):
        #for ch in [0]:
            if (ch // 128) not in self.fembs:
               ch_data.append(None)
               continue
            data = self.dat_enob_acq_ch(ch=ch)
            ch_data.append(data)
        return ch_data        

    def dat_adc_ch_cs(self, ch=0):
        #select chip
        chipno = ch//16
        self.cdpoke(0, 0xC, 0, self.DAT_ADC_TST_SEL, ((1<<chipno)^0xFF)&0xFF)

        #select chnnel, chsenl is low active 
        chperchip = ch%16
        if self.rev == 0:
            if (chperchip == 4 ) :
                chsenl = 0xFFFF ^ (1<<5)
            elif  (chperchip == 6):
                chsenl = 0xFFFF ^ (1<<7)
            else:
                chsenl = 0xFFFF ^ (1<<chperchip)
        else:
            chsenl = 0xFFFF ^ (1<<chperchip)
        self.cdpoke(0, 0xC, 0, self.DAT_ADC_SRC_CS_P_LSB, chsenl&0xFF)
        self.cdpoke(0, 0xC, 0, self.DAT_ADC_SRC_CS_P_MSB, (chsenl>>8)&0xFF)
        time.sleep(0.05)

    def dat_enob_acq_ch(self, ch=0, sineflg=True):
        self.dat_adc_ch_cs(ch=ch)
        #print("WIB ENOB 16,384 samples test")  
        #print("before running this script: configure the FEMB chips and trigger")  
        while True:
            self.poke(0xa00c0078, ch)
            #trigger capture
            self.poke(0xa00c0074, 0x3)
            self.poke(0xa00c0074, 0x2)
            #wait till capture done
            tries = 0
            while (self.peek(0xa00c00f0) & 0x100) == 0:            
                pass
                tries = tries + 1
                if tries == 20000:
                    print("ENOB waveform acquisition failed for channel",ch)
                    print("Aborting acquisition")
                    return None
            self.poke(0xa00c0074, 0x0)
            data = self.adc_histbuf() #block read
            if sineflg:
                if self.enobdata_check(ch, data): #check if data is good
                   # input ("aaa")
                    break
                else:
                   # input ("aaa")
                    pass
                    #break
            else:
                break
        return data        

    
    def enobdata_check(self, ch, data): 
        num_16bwords = 0x8000 / 2
        words16b = list(struct.unpack_from("<%dH"%(num_16bwords),data))
        if 0 in words16b or 0x3fff in words16b:
            print ("data on ch%d has glitch, retake data"%ch)
            return False
        data0 = np.array(words16b[0:-1])
        data1 = np.array(words16b[1:])
        deltas = data0 - data1
        dstd = np.std(deltas)
        dmean = np.mean(deltas)
        if np.max(deltas) > (dmean + 5*dstd) or np.min(deltas) < (dmean - 5*dstd):
            print ("data on ch%d has glitch, retake data"%ch)
            return False
        else:
            return True

    def adc_refv_chk(self,datad):
        adcbads = []
        dkeys = list(datad.keys())
        err_high = 1.15
        err_low = 0.85
        
        vrefp_nom = 1950 #mV
        vrefn_nom = 450 
        vcmi_nom = 900 
        vcmo_nom = 1200
        
        warn_flg = False
        for onekey in dkeys:
            if "MON_VREFP" in onekey:
                vnom = vrefp_nom
            elif "MON_VREFN" in onekey:
                vnom = vrefn_nom
            elif "MON_VCMI" in onekey:
                vnom = vcmi_nom
            elif "MON_VCMO" in onekey:
                vnom = vcmo_nom            

            for chipno in range(8):
                data = datad[onekey][1][chipno]
                if (vnom*err_low < data) and (data < vnom*err_high):
                    pass
                else:
                    print ("Warning: {} is out of range of {} mV: {}".format(onekey, vnom, data))
                    if chipno not in adcbads:
                        adcbads.append(chipno)
                    warn_flg = True
        return warn_flg, adcbads
            
    def sig_gen_config(self, waveform = None, freq = 1000, vlow = 0, vhigh = 2.5):        
        
        if waveform == None: #turn off output
            pass
        elif  waveform == "TRI" or waveform == "RAMP" or waveform == "DC": #DC will use vhigh argument
            pass
        elif waveform == "SINE":
            waveform = "SIN" 
        else:
            print("sig_gen_config: Unrecognized waveform argument. Options are TRIG, RAMP, SINE, DC")
            waveform = "error"
        
        if vlow >= 0:
            lowsign = "+"
        else:
            lowsign = ""
        if vhigh >= 0:
            highsign = "+"
        else:
            highsign = ""     
            
        rm = pyvisa.ResourceManager()
        sigconfig_done = False
        while not sigconfig_done:
            try:
                sig_gen = rm.open_resource(self.gen_rm)
                print(sig_gen.query("*IDN?"),end='')
                if waveform == None or waveform == "error": #turn off output
                    sig_gen.write("OUTPUT OFF")  
                else:
                    if waveform == 'DC':
                        sig_gen.write("FUNCTION DC")
                        sig_gen.write("VOLTAGE:OFFSET "+highsign+str(vhigh))
                    elif waveform == 'RAMP' or waveform == 'SIN' or waveform == 'TRI':
                        sig_gen.write("FUNCTION "+str(waveform))
                        if waveform == 'RAMP':
                            sig_gen.write("FUNC:RAMP:SYMM 100")
                        sig_gen.write("FREQ "+str(freq))
                    
                        sig_gen.write("VOLTAGE:LOW "+lowsign+str(vlow))
                        sig_gen.write("VOLTAGE:HIGH "+highsign+str(vhigh))
                    
                    sig_gen.write("OUTPUT:LOAD INF") #HiZ impedance
                    sig_gen.write("OUTPUT ON")
                sigconfig_done = True 
                print("Signal generator configured")               
                sig_gen.close() 
            except Exception as e:
                print(e)
                print("Error configuring signal generator. Trying again...")
                #err = sig_gen.query("SYSTEM:ERROR?")
                #print("Signal generator status:",err,end='')
    
    # def dat_adc_imons(self, mon_type=0xff):
        # femb_id = self.fembs[0]
        
        # mon_datas = {}     

        # #mon_type = 0x01: VBGR
        # if mon_type&0x01:   
            # imon_select = 0x0
            
            # vbgr_imons = 

    
#    def asic_off_pwrchk(self):
#        while True:
#            fes_pwr_info =  self.fe_pwr_meas()
#            adcs_pwr_info = self.adc_pwr_meas()
#            cds_pwr_info =  self.cd_pwr_meas()
#
#            warn_flg = False
#            kl = list(fes_pwr_info.keys())
#            for onekey in kl:
#                if "VDDA" in onekey:
#                    if fes_pwr_info[onekey][0] < 0.30) & (fes_pwr_info[onekey][0]< 2  ) :
#                        pass
#                    else:
#                        warn_flg = True
#                if "VDDO" in onekey:
#                    if (fes_pwr_info[onekey][0] < 0.30) & (fes_pwr_info[onekey][0]< 2 ) :
#                        pass
#                    else:
#                        warn_flg = True
#                if "VDDP" in onekey:
#                    if (fes_pwr_info[onekey][0] < 0.30) & (fes_pwr_info[onekey][0]< 2  ) :
#                        pass
#                    else:
#                        warn_flg = True
#
#            kl = list(adcs_pwr_info.keys())
#            for onekey in kl:
#                if "VDDA2P5" in onekey:
#                    if (adcs_pwr_info[onekey][0] < 0.30) & (adcs_pwr_info[onekey][0] < 2  ) :
#                        pass
#                    else:
#                        warn_flg = True
#                if "VDDD2P5" in onekey:
#                    if (adcs_pwr_info[onekey][0] < 0.30) & (adcs_pwr_info[onekey][0] < 2  ) :
#                        pass
#                    else:
#                        warn_flg = True
#
#                if "VDDIO" in onekey:
#                    if (adcs_pwr_info[onekey][0] < 0.30) & (adcs_pwr_info[onekey][0] < 2  ) :
#                        pass
#                    else:
#                        warn_flg = True
#                if "VDDD1P2" in onekey:
#                    if (adcs_pwr_info[onekey][0] < 0.30) & (adcs_pwr_info[onekey][0] < 2  ) :
#                        pass
#                    else:
#                        warn_flg = True
#
#            kl = list(cds_pwr_info.keys())
#            for onekey in kl:
#                if "CD_VDDA" in onekey:
#                    if (cds_pwr_info[onekey][0] < 0.3)  & (cds_pwr_info[onekey][0] < 2  ) :
#                        pass
#                    else:
#                        warn_flg = True
#                if "FE_VDDA" in onekey:
#                    if (cds_pwr_info[onekey][0] < 0.3)  & (cds_pwr_info[onekey][0] < 2  ) :
#                        pass
#                    else:
#                        warn_flg = True
#
#                if "CD_VDDCORE" in onekey:
#                    if (cds_pwr_info[onekey][0] < 0.3)  & (cds_pwr_info[onekey][0] < 2  ) :
#                        pass
#                    else:
#                        warn_flg = True
#                if "CD_VDDD" in onekey: 
#                    if (cds_pwr_info[onekey][0] < 0.3)  & (cds_pwr_info[onekey][0] < 2  ) :
#                        pass
#                    else:
#                        warn_flg = True
#                if "CD_VDDIO" in onekey:
#                    if (cds_pwr_info[onekey][0] < 0.3)  & (cds_pwr_info[onekey][0] < 2  ) :
#                        pass
#                    else:
#                        print ("Warning: {} is out of range {}".format(onekey, cds_pwr_info[onekey]))
#                        warn_flg = True
#            if warn_flg:
#                print ("Wait 2 second, not yet completely shut down...")
#                time.sleep(2)
#            else:
#                print ("All DUTs power rails are off!")


