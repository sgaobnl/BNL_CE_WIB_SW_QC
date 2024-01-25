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



class DAT_CFGS(WIB_CFGS):
    def __init__(self):
        super().__init__()
        self.cd_sel = 0
        self.dat_on_wibslot = 0
#        if self.dat_on_wibslot  == 0:
#            self.Vref = 1.583
#        else:
#            self.Vref = 1.589
        self.fembs = [self.dat_on_wibslot]
        self.data_align_flg = False
        self.data_align_pwron_flg = True

        #MUX (SN74LV405AD)
        self.mon_fe_cs = ["GND", "Ext_Test", "DAC", "FE_COMMON_DAC", "VBGR", "DNI[To_AmpADC]", "GND", "AUX_VOLTAGE_MUX"]
        self.mon_AD_REF = 2.564 #need to update accoring to board
        self.AD_LSB = 2564/4096 #mV/bit #need to update accoring to board
        self.monadc_avg = 1
        self.fedly= 3
        self.sddflg = 0 
        self.ADCVREF = 2.5

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
        print ("Wait ~10 seconds ...")
        
        for i in range(5):
            self.wib_pwr_on_dat_chk(fullon_chk=False)
            time.sleep(0.1)
            print (i)
        self.dat_fpga_reset()
        self.cdpoke(0, 0xC, 0, self.DAT_CD_AMON_SEL, self.cd_sel)    
        self.femb_cd_rst()
        for femb_id in self.fembs:
           self.femb_cd_fc_act(femb_id, act_cmd="rst_adcs")
           self.femb_cd_fc_act(femb_id, act_cmd="rst_larasics")
           self.femb_cd_fc_act(femb_id, act_cmd="rst_larasic_spi")
        pwr_meas = self.wib_pwr_on_dat_chk()

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
                print ("\033[91m" + "FEMB%d, HS links are broken, 0x%H"%(femb_no, link_mask)+ "\033[0m")
                print ("\033[91m" + "Turn DAT off, exit anyway!"+ "\033[0m")
                self.femb_powering([])
                self.data_align_flg = False
                self.data_align_pwron_flg = True
                exit()

        return pwr_meas, link_mask

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
                        if (pwr_meas[key] < 0.2) or (pwr_meas[key] > 0.6) :
                            init_f = True
                    if "DC2DC1_I" in key:
                        if (pwr_meas[key] < 0.2) or (pwr_meas[key] > 0.6) :
                            init_f = True
                    if "DC2DC2_I" in key:
                        if (pwr_meas[key] < 1) or (pwr_meas[key] > 2.3) :
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
                        if pwr_meas[key] > 0.6 :
                            init_f = True
                    if "DC2DC2_I" in key:
                        if pwr_meas[key] > 2.0 :
                            init_f = True
#                    if "DC3DC3_I" in key: #not use
#                        if pwr_meas[key] > 1:
#                        init_f = True

                if init_f:
                    print ("\033[91m" + "DAT power consumption @ (power on) is not right, please contact tech coordinator!"+ "\033[0m")
                    print ("\033[91m" + "Turn DAT off, exit anyway!"+ "\033[0m")
                    self.femb_powering([])
                    self.data_align_flg = False
                    self.data_align_pwron_flg = True
                    time.sleep(1)
                    exit()
        return pwr_meas


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
                current = self.datpower_getcurrent(addr, fe=asic)
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
        print("Power Check for All power rails")
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
#        kl = list(adcs_pwr_info.keys())
#        for onekey in kl:
#            print (onekey, adcs_pwr_info[onekey])
        return adcs_pwr_info

    def dat_cd_pwr_meas(self):
        cd_list = ["CD0-0x3", "CD1-0x2"]
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

  #  def cd_dftreg_chk(self):

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
        self.dat_fpga_reset()
        warn_flg = False
        kl = list(fes_pwr_info.keys())
        for onekey in kl:
            if "VDDA" in onekey:
                if  (fes_pwr_info[onekey][0] > 1.75) & (fes_pwr_info[onekey][0] < 1.95) & (fes_pwr_info[onekey][1] > 15  ) & (fes_pwr_info[onekey][0] < 25  ) :
                    pass
                else:
                    print ("Warning: {} is out of range {}".format(onekey, fes_pwr_info[onekey]))
                    warn_flg = True
            if "VDDO" in onekey:
                if  (fes_pwr_info[onekey][0] > 1.75) & (fes_pwr_info[onekey][0] < 1.95) & (fes_pwr_info[onekey][1] > -0.1  ) & (fes_pwr_info[onekey][0] < 3  ) :
                    pass
                else:
                    print ("Warning: {} is out of range {}".format(onekey, fes_pwr_info[onekey]))
                    warn_flg = True
            if "VDDP" in onekey:
                if  (fes_pwr_info[onekey][0] > 1.75) & (fes_pwr_info[onekey][0] < 1.95) & (fes_pwr_info[onekey][1] > 28  ) & (fes_pwr_info[onekey][0] < 37  ) :
                    pass
                else:
                    print ("Warning: {} is out of range {}".format(onekey, fes_pwr_info[onekey]))
                    warn_flg = True

        kl = list(adcs_pwr_info.keys())
        for onekey in kl:
            if "VDDA2P5" in onekey:
                if  (adcs_pwr_info[onekey][0] > 2.10) & (adcs_pwr_info[onekey][0] < 2.30) & (adcs_pwr_info[onekey][1] > 100  ) & (adcs_pwr_info[onekey][0] < 140  ) :
                    pass
                else:
                    print ("Warning: {} is out of range {}".format(onekey, adcs_pwr_info[onekey]))
                    warn_flg = True
            if "VDDD2P5" in onekey:
                if  (adcs_pwr_info[onekey][0] > 2.10) & (adcs_pwr_info[onekey][0] < 2.30) & (adcs_pwr_info[onekey][1] > 15  ) & (adcs_pwr_info[onekey][0] < 25  ) :
                    pass
                else:
                    print ("Warning: {} is out of range {}".format(onekey, adcs_pwr_info[onekey]))
                    warn_flg = True

            if "VDDIO" in onekey:
                if  (adcs_pwr_info[onekey][0] > 2.10) & (adcs_pwr_info[onekey][0] < 2.30) & (adcs_pwr_info[onekey][1] > 3  ) & (adcs_pwr_info[onekey][0] < 8  ) :
                    pass
                else:
                    print ("Warning: {} is out of range {}".format(onekey, adcs_pwr_info[onekey]))
                    warn_flg = True
            if "VDDD1P2" in onekey:
                if  (adcs_pwr_info[onekey][0] > 1.05) & (adcs_pwr_info[onekey][0] < 1.15) & (adcs_pwr_info[onekey][1] > 1  ) & (adcs_pwr_info[onekey][0] < 3  ) :
                    pass
                else:
                    print ("Warning: {} is out of range {}".format(onekey, adcs_pwr_info[onekey]))
                    warn_flg = True

        kl = list(cds_pwr_info.keys())
        for onekey in kl:
            if "CD_VDDA" in onekey:
                if  (cds_pwr_info[onekey][0] > 1.15) & (cds_pwr_info[onekey][0] < 1.25) & (cds_pwr_info[onekey][1] > 5   ) & (cds_pwr_info[onekey][0] < 10  ) :
                    pass
                else:
                    print ("Warning: {} is out of range {}".format(onekey, cds_pwr_info[onekey]))
                    warn_flg = True
            if "FE_VDDA" in onekey:
                if  (cds_pwr_info[onekey][0] > 1.70) & (cds_pwr_info[onekey][0] < 1.90) & (cds_pwr_info[onekey][1] > -0.1  ) & (cds_pwr_info[onekey][0] < 3  ) :
                    pass
                else:
                    print ("Warning: {} is out of range {}".format(onekey, cds_pwr_info[onekey]))
                    warn_flg = True

            if "CD_VDDCORE" in onekey:
                if  (cds_pwr_info[onekey][0] > 1.15) & (cds_pwr_info[onekey][0] < 1.25) & (cds_pwr_info[onekey][1] > 7  ) & (cds_pwr_info[onekey][0] < 12  ) :
                    pass
                else:
                    print ("Warning: {} is out of range {}".format(onekey, cds_pwr_info[onekey]))
                    warn_flg = True
            if "CD_VDDD" in onekey: 
                if  (cds_pwr_info[onekey][0] > 1.15) & (cds_pwr_info[onekey][0] < 1.25) & (cds_pwr_info[onekey][1] > 15  ) & (cds_pwr_info[onekey][0] < 25  ) :
                    pass
                else:
                    print ("Warning: {} is out of range {}".format(onekey, cds_pwr_info[onekey]))
                    warn_flg = True
            if "CD_VDDIO" in onekey:
                if  (cds_pwr_info[onekey][0] > 2.20) & (cds_pwr_info[onekey][0] < 2.35) & (cds_pwr_info[onekey][1] > 40  ) & (cds_pwr_info[onekey][0] < 55  ) :
                    pass
                else:
                    print ("Warning: {} is out of range {}".format(onekey, cds_pwr_info[onekey]))
                    warn_flg = True

        vbgr = self.dat_fe_vbgrs()
        for fe in range(8):
            vtmp = vbgr['VBGR'][1][fe]
            if (vtmp > 1100) and (vtmp < 1300) :
                pass
            else:
                print ("Warning: VBGR of FE{} is out of range {}mV (typical 1.2V)".format(fe, vtmp))
                warn_flg = True


        if warn_flg:
            print ("\033[91m" + "please check before restart"+ "\033[0m")
            input ("\033[91m" + "exit by clicking any button and Enter"+ "\033[0m")
            self.femb_powering([])
            self.data_align_flg = False
            exit()

    def dat_adc_qc_cfg(self,data_fmt=0x08, diff_en=0, sdf_en=0, vrefp=0xE8, vrefn=0x18, vcmo=0x90, vcmi=0x60, autocali=1):
        self.femb_cd_rst()
        cfg_paras_rec = []
        for femb_id in self.fembs:
            self.adcs_paras = [ # c_id, data_fmt(0x89), diff_en(0x84), sdf_en(0x80), vrefp, vrefn, vcmo, vcmi, autocali
                                [0x4, data_fmt, diff_en, sdf_en, vrefp, vrefn, vcmo, vcmi, autocali],
                                [0x5, data_fmt, diff_en, sdf_en, vrefp, vrefn, vcmo, vcmi, autocali],
                                [0x6, data_fmt, diff_en, sdf_en, vrefp, vrefn, vcmo, vcmi, autocali],
                                [0x7, data_fmt, diff_en, sdf_en, vrefp, vrefn, vcmo, vcmi, autocali],
                                [0x8, data_fmt, diff_en, sdf_en, vrefp, vrefn, vcmo, vcmi, autocali],
                                [0x9, data_fmt, diff_en, sdf_en, vrefp, vrefn, vcmo, vcmi, autocali],
                                [0xA, data_fmt, diff_en, sdf_en, vrefp, vrefn, vcmo, vcmi, autocali],
                                [0xB, data_fmt, diff_en, sdf_en, vrefp, vrefn, vcmo, vcmi, autocali],
                              ]
            self.set_fe_reset()
            self.set_fe_sync()
            adac_pls_en = 0 #enable LArASIC interal calibraiton pulser
            cfg_paras_rec.append( (femb_id, copy.deepcopy(self.adcs_paras), copy.deepcopy(self.regs_int8), adac_pls_en, self.cd_sel) )
            self.femb_cfg(femb_id, adac_pls_en )
        if self.data_align_pwron_flg == True:
            self.data_align(self.fembs)
            self.data_align_pwron_flg = False
            time.sleep(0.1)
        if self.data_align_flg != True:
            self.data_align(self.fembs)
            self.data_align_flg = False
        return cfg_paras_rec

    def dat_fe_qc_cfg(self, adac_pls_en=0, sts=0, snc=0,sg0=0, sg1=0, st0=1, st1=1, swdac=0, sdd=0, sdf=0, dac=0x00, sgp=0, slk0=0, slk1=0, chn=128):
        self.femb_cd_rst()
        cfg_paras_rec = []
        for femb_id in self.fembs:
#            self.adcs_paras = [ # c_id, data_fmt(0x89), diff_en(0x84), sdf_en(0x80), vrefp, vrefn, vcmo, vcmi, autocali
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
            self.femb_cfg(femb_id, adac_pls_en )
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
#                self.adcs_paras = [ # c_id, data_fmt(0x89), diff_en(0x84), sdf_en(0x80), vrefp, vrefn, vcmo, vcmi, autocali
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
        data =  self.dat_fe_qc_acq(num_samples)
        #self.dat_fe_qc_rst()
        return data, cfg_info

    def dat_cali_source(self, cali_mode, val=1.0, period=0x200, width=0x180, asicdac=0x10):
        #cali_mode: 0 = direct input, 1 = DAT DAC, 2 = ASIC DAC, 3 or larger: disable cali
        if cali_mode <0 or cali_mode >3:
            print ("\033[91m" + "Wrong value for cali_mode"+ "\033[0m")
            print ("\033[91m" + "cali_mode: 0 = direct input, 1 = DAT DAC, 2 = ASIC DAC, 3 =disable cali" + "\033[0m" )
            print ("\033[91m" + "Exit anyway!"+ "\033[0m")
            self.femb_powering([])
            self.data_align_flg = False
            exit()

        self.dat_fpga_reset()
        if cali_mode < 2:
            valint = int(val*65536/self.ADCVREF)
            self.dat_set_dac(val=valint, fe_cal=0)
            self.cdpoke(0, 0xC, 0, self.DAT_FE_CMN_SEL, 4)    
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
            self.cdpoke(0, 0xC, 0, self.DAT_ADC_FE_TEST_SEL, 3<<4)    

            self.cdpoke(0, 0xC, 0, self.DAT_FE_TEST_SEL_INHIBIT, 0x00)   
            if cali_mode == 0:
                self.cdpoke(0, 0xC, 0, self.DAT_FE_CALI_CS, 0x00)  #direct input
                self.cdpoke(0, 0xC, 0, self.DAT_FE_IN_TST_SEL_MSB, 0xff)   #direct input
                self.cdpoke(0, 0xC, 0, self.DAT_FE_IN_TST_SEL_LSB, 0xff)   #direct input
                adac_pls_en = 0
                sts = 0
                swdac = 0
                dac = 0
            if cali_mode == 1:
                self.cdpoke(0, 0xC, 0, self.DAT_FE_CALI_CS, 0xff)  #DAT DAC
                self.cdpoke(0, 0xC, 0, self.DAT_FE_IN_TST_SEL_MSB, 0x00)   #DAT DAC
                self.cdpoke(0, 0xC, 0, self.DAT_FE_IN_TST_SEL_LSB, 0x00)   #DAT DAC
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
        for fedly in [3,3,5]:
            self.fedly = fedly
            datad = {}
            adac_pls_en, sts, swdac, dac = self.dat_cali_source(cali_mode=2,asicdac=0x20)
            rawdata = self.dat_fe_qc(adac_pls_en=adac_pls_en, sts=sts, swdac=swdac, dac=dac,snc=1,sg0=0, sg1=0, st0=1, st1=1, sdd=1, sdf=0, slk0=0, slk1=0)
            wibdata = wib_dec(rawdata[0], fembs=self.fembs, spy_num=1)[0]
            datd = [wibdata[0], wibdata[1],wibdata[2],wibdata[3]][self.dat_on_wibslot]
            initchk_flg = True
            for ch in range(16*8):
                chmax = np.max(datd[ch][500:1500])
                if ch == 0:
                    chmaxpos = np.where(datd[ch][500:1500] == chmax)[0][0] + 500
                if ch == 64:
                    chmaxpos = np.where(datd[ch][500:1500] == chmax)[0][0] + 500
                chped = np.mean(datd[ch][chmaxpos-100:chmaxpos-50])
                chmin = np.min(datd[ch][500:1500])
                if ( (datd[ch][chmaxpos] - datd[ch][chmaxpos-3]) > 1000) and ( (datd[ch][chmaxpos] - datd[ch][chmaxpos+3]) > 1000) :
                    c1 = True
                else:
                    c1 = False
                if ( (datd[ch][chmaxpos-2] - datd[ch][chmaxpos-10]) > 1000) and ( (datd[ch][chmaxpos+2] - datd[ch][chmaxpos+20]) > 1000) :
                    c2 = True
                else:
                    c2 = False
                if (chmax > 8000) & (chped < 2000) & (chped > 200) & (chmin<100) & c1 & c2:
                    pass
                else:
                    initchk_flg = False 
                    print ("\033[91m" + "Cali Input ERROR ch={}, chmax={}, chped={}, chmin={}".format(ch, chmax, chped, chmin)+ "\033[0m" ) 
                    #should add chip infomation later
                    #exit()
            datad["ASICDAC_CALI_CHK"] = (self.fembs, rawdata[0], rawdata[1], None)

            adac_pls_en, sts, swdac, dac = self.dat_cali_source(cali_mode=0, val=1.53, period=0x200, width=0x180, asicdac=0x10)
            rawdata = self.dat_fe_qc(adac_pls_en=adac_pls_en, sts=sts, swdac=swdac, dac=dac, snc=1) #direct FE input
            wibdata = wib_dec(rawdata[0], fembs=self.fembs, spy_num=1)[0]
            datd = [wibdata[0], wibdata[1],wibdata[2],wibdata[3]][self.dat_on_wibslot]
            for ch in range(16*8):
                chmax = np.max(datd[ch][500:1500])
                if ch == 0:
                    chmaxpos = np.where(datd[ch][500:1500] == chmax)[0][0] + 500
                if ch == 64:
                    chmaxpos = np.where(datd[ch][500:1500] == chmax)[0][0] + 500
                chped = np.mean(datd[ch][chmaxpos-100:chmaxpos-50])
                chmin = np.min(datd[ch][500:1500])
                if ( (datd[ch][chmaxpos] - datd[ch][chmaxpos-2]) > 1000) and ( (datd[ch][chmaxpos] - datd[ch][chmaxpos+2]) > 1000) :
                    c1 = True
                if ( (datd[ch][chmaxpos-2] - datd[ch][chmaxpos-10]) > 1000) and ( (datd[ch][chmaxpos+2] - datd[ch][chmaxpos+20]) > 1000) :
                    c2 = True
                if (chmax > 8000) & (chped < 2000) & (chped > 300) & (chmin<100) & c1 & c2:
                    pass
                else:
                    initchk_flg = False 
                    print ("\033[91m" + "Direct Input ERROR ch={}, chmax={}, chped={}, chmin={}".format(ch, chmax, chped, chmin)+ "\033[0m")
                    #should add chip infomation later
                    #exit()
            datad["DIRECT_PLS_CHK"] = (self.fembs, rawdata[0], rawdata[1], None)

            if initchk_flg:
                print ("\033[92m" + "Pass the interconnection checkout, QC may start now!"+ "\033[0m")
                break
            else:
                if self.fedly == 5:
                    print ("\033[91m" + "the interconnection checkout fails, exit anyway !"+ "\033[0m")
                    self.femb_powering([])
                    self.data_align_flg = False
                    exit()
                    #pass
        return datad

    def dat_coldadc_cali_cs(self,  mode="SE", chsenl=0x0000):
        if "DIFF" in mode:
            self.cdpoke(0, 0xC, 0, self.DAT_ADC_PN_TST_SEL, 0x33)
        else:
            self.cdpoke(0, 0xC, 0, self.DAT_ADC_PN_TST_SEL, 0x03)

        self.cdpoke(0, 0xC, 0, self.DAT_ADC_TEST_IN_SEL, 0)
        # ##Set ADC_SRC_CS_P to 0x0000 (ADC_SRC_CS_P_MSB, ADC_SRC_CS_P_LSB)

        self.cdpoke(0, 0xC, 0, self.DAT_ADC_SRC_CS_P_LSB, chsenl&0xFF)
        self.cdpoke(0, 0xC, 0, self.DAT_ADC_SRC_CS_P_MSB, (chsenl>>8)&0xFF)


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
                break
            else:
                time.sleep(1)
                if tmpi < 30:
                    print ("Try to reset DAT FPGA...")
                else:
                    tmpstr = input ("Continue trying (Y/N) : ")
                    if "Y" in tmpstr or "y" in tmpstr:
                        tmpi = 0
                    else:
                        print ("Can't reset DAT FPGA, please check data cable connection")
                        input ("\033[91m" + "exit by clicking any button and Enter"+ "\033[0m")
                        self.femb_powering([])
                        exit()


    def dat_monadcs(self):
        avg_datas = [[],[],[],[],[],[],[],[]]
        avg = self.monadc_avg
        for avgi in range(avg):
            self.dat_monadc_trig() #get rid of previous result    
            self.dat_monadc_trig() #get rid of previous result   
            for fe in range(8):
                for check in range(10):
                    if not self.dat_monadc_busy(fe=fe):
                        break;
                    if check is 9:
                        print("Timed out while waiting for AD7274 controller to finish")
                data = self.dat_monadc_getdata(fe=fe)
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
        datas = self.dat_monadcs()[0]
        datas_v = np.array(datas)*self.AD_LSB
        mon_datas["VBGR"] = [datas, datas_v]
        return mon_datas


    def dat_fe_mons(self, mon_type=0x1f ):
        #measure VBGR/Temperature through Monitoring pin
        femb_id = self.fembs[0]

        for i in range(8):
            self.adcs_paras[i][8] = 0 # disable autocali 
#        self.adcs_paras = [ # c_id, data_fmt(0x89), diff_en(0x84), sdf_en(0x80), vrefp, vrefn, vcmo, vcmi, autocali
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
        self.cdpoke(0, 0xC, 0, self.DAT_FE_CALI_CS, 0xFF)    
        self.cdpoke(0, 0xC, 0, self.DAT_TEST_PULSE_EN, 0x00) #disable pin4 of U230 (FE_INS_PLS_CS)   
        self.cdpoke(0, 0xC, 0, self.DAT_TEST_PULSE_SOCKET_EN, 0x00) #disable pin4 of U230 (FE_INS_PLS_CS = 1)   
        self.cdpoke(0, 0xC, 0, self.DAT_FE_IN_TST_SEL_LSB, 0x00)    
        self.cdpoke(0, 0xC, 0, self.DAT_FE_IN_TST_SEL_MSB, 0x00)    
        self.cdpoke(0, 0xC, 0, self.DAT_ADC_FE_TEST_SEL, mux_cs<<4)    
        self.cdpoke(0, 0xC, 0, self.DAT_FE_TEST_SEL_INHIBIT, 0xff)    

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
            self.cdpoke(0, 0xC, 0, self.DAT_FE_CALI_CS, 0x00)    
            self.cdpoke(0, 0xC, 0, self.DAT_TEST_PULSE_EN, 0x00) #disable pin4 of U230 (FE_INS_PLS_CS = 1)   
            self.cdpoke(0, 0xC, 0, self.DAT_TEST_PULSE_SOCKET_EN, 0x00) #disable pin4 of U230 (FE_INS_PLS_CS = 1)   
            self.cdpoke(0, 0xC, 0, self.DAT_ADC_FE_TEST_SEL, mux_cs<<4)    
            self.cdpoke(0, 0xC, 0, self.DAT_FE_TEST_SEL_INHIBIT, 0xFF)    
        return mon_datas


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


