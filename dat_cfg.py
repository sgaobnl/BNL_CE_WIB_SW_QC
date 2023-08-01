from llc import LLC
from fe_asic_reg_mapping import FE_ASIC_REG_MAPPING
from wib_cfgs import WIB_CFGS
from spymemory_decode import wib_spy_dec_syn
import time
import sys
import numpy as np
import pickle
import copy
import time, datetime, random, statistics    



class DAT_CFGS(WIB_CFGS):
    def __init__(self):
        super().__init__()
        self.dat_on_wibslot = 0
        self.fembs = [self.dat_on_wibslot]
        self.data_align_flg = False
        #MUX (SN74LV405AD)
        self.mon_fe_cs = ["GND", "Ext_Test", "DAC", "FE_COMMON_DAC", "VBGR", "DNI[To_AmpADC]", "GND", "AUX_VOLTAGE_MUX"]
        self.mon_AD_REF = 2.564 #need to update accoring to board
        self.AD_LSB = 2564/4096 #mV/bit #need to update accoring to board
        self.monadc_avg = 1

    def wib_pwr_on_dat(self):
        print ("Initilization checkout")
        self.wib_fw()
        print ("Turn off all power rails for FEMBs")
        self.femb_cd_rst()
        self.femb_powering([])
        self.data_align_flg = False
        time.sleep(2)
        
        #set FEMB voltages
        self.fembs_vol_set(vfe=4.0, vcd=4.0, vadc=4.0)
        #power on FEMBs
        self.femb_powering(self.fembs)
        self.data_align_flg = False
        print ("Wait 10 seconds ...")
        time.sleep(6)
        self.femb_cd_rst()
        for femb_id in self.fembs:
           self.femb_cd_fc_act(femb_id, act_cmd="rst_adcs")
           self.femb_cd_fc_act(femb_id, act_cmd="rst_larasics")
           self.femb_cd_fc_act(femb_id, act_cmd="rst_larasic_spi")
        time.sleep(4)

        pwr_meas = self.get_sensors()
        time.sleep(0.1)
        pwr_meas = self.get_sensors()
        for key in pwr_meas:
            if "FEMB%d"%self.dat_on_wibslot in key:
                init_f = False
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
                if "DC2DC3_V" in key:
                    if pwr_meas[key] < 3.5:
                        init_f = True
        
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
                if "DC2DC3_I" in key:
                    if pwr_meas[key] > 1:
                        init_f = True
                if init_f:
                    print ("DAT power consumption @ (power on) is not right, please contact tech coordinator!")
                    print ("Turn DAT off, exit anyway!")
                    self.femb_powering([])
                    self.data_align_flg = False
                    time.sleep(1)
                    exit()
        
        link_mask=self.wib_femb_link_en(self.fembs)
        for femb_no in self.fembs:
            if (0xf<<(femb_no*4))&link_mask == 0:
                print ("HS links are good")
                self.data_align_flg = False
                self.femb_cd_fc_act(femb_no, act_cmd="rst_adcs")
                self.femb_cd_fc_act(femb_no, act_cmd="rst_larasics")
                self.femb_cd_fc_act(femb_no, act_cmd="rst_larasic_spi")

            else:
                print ("FEMB%d, HS links are broken, 0x%H"%(femb_no, link_mask))
                print ("Turn DAT off, exit anyway!")
                self.femb_powering([])
                self.data_align_flg = False
                exit()
        return pwr_meas, link_mask

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

    def cd_pwr_meas(self):
        cd_list = ["CD0-0x3", "CD1-0x2"]
        addrs = [0x40, 0x41, 0x43, 0x45, 0x44]
        pwrrails = ["CD_VDDA", "FE_VDDA", "CD_VDDCORE", "CD_VDDD", "CD_VDDIO"]
        cds_pwr_info = self.cd_pwr_info(asic_list=cd_list, dat_addrs=addrs, pwrrails=pwrrails)
        return cds_pwr_info

    def asic_init_pwrchk(self, fes_pwr_info, adcs_pwr_info, cds_pwr_info):
        warn_flg = False
        kl = list(fes_pwr_info.keys())
        for onekey in kl:
            if "VDDA" in onekey:
                if  (fes_pwr_info[onekey][0] > 1.70) & (fes_pwr_info[onekey][0] < 1.85) & (fes_pwr_info[onekey][1] > 15  ) & (fes_pwr_info[onekey][0] < 25  ) :
                    pass
                else:
                    print ("Warning: {} is out of range {}".format(onekey, fes_pwr_info[onekey]))
                    warn_flg = True
            if "VDDO" in onekey:
                if  (fes_pwr_info[onekey][0] > 1.70) & (fes_pwr_info[onekey][0] < 1.85) & (fes_pwr_info[onekey][1] > -0.1  ) & (fes_pwr_info[onekey][0] < 3  ) :
                    pass
                else:
                    print ("Warning: {} is out of range {}".format(onekey, fes_pwr_info[onekey]))
                    warn_flg = True
            if "VDDP" in onekey:
                if  (fes_pwr_info[onekey][0] > 1.70) & (fes_pwr_info[onekey][0] < 1.85) & (fes_pwr_info[onekey][1] > 28  ) & (fes_pwr_info[onekey][0] < 37  ) :
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
                if  (cds_pwr_info[onekey][0] > 1.05) & (cds_pwr_info[onekey][0] < 1.15) & (cds_pwr_info[onekey][1] > 5   ) & (cds_pwr_info[onekey][0] < 10  ) :
                    pass
                else:
                    print ("Warning: {} is out of range {}".format(onekey, cds_pwr_info[onekey]))
                    warn_flg = True
            if "FE_VDDA" in onekey:
                if  (cds_pwr_info[onekey][0] > 1.70) & (cds_pwr_info[onekey][0] < 1.85) & (cds_pwr_info[onekey][1] > -0.1  ) & (cds_pwr_info[onekey][0] < 3  ) :
                    pass
                else:
                    print ("Warning: {} is out of range {}".format(onekey, cds_pwr_info[onekey]))
                    warn_flg = True

            if "CD_VDDCORE" in onekey:
                if  (cds_pwr_info[onekey][0] > 1.05) & (cds_pwr_info[onekey][0] < 1.15) & (cds_pwr_info[onekey][1] > 7  ) & (cds_pwr_info[onekey][0] < 12  ) :
                    pass
                else:
                    print ("Warning: {} is out of range {}".format(onekey, cds_pwr_info[onekey]))
                    warn_flg = True
            if "CD_VDDD" in onekey: 
                if  (cds_pwr_info[onekey][0] > 1.05) & (cds_pwr_info[onekey][0] < 1.15) & (cds_pwr_info[onekey][1] > 15  ) & (cds_pwr_info[onekey][0] < 25  ) :
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
            print ("please check before restart")
            input ("exit by clicking any button and Enter")
            #exit()

    def dat_fe_qc_cfg(self, adac_pls_en=0, sts=0, snc=0,sg0=0, sg1=0, st0=1, st1=1, swdac=0, sdd=0, sdf=0, dac=0x00, sgp=0, slk0=0, slk1=0, chn=128):
        self.femb_cd_rst()
        cfg_paras_rec = []
        for femb_id in self.fembs:
            self.adcs_paras = [ # c_id, data_fmt(0x89), diff_en(0x84), sdf_en(0x80), vrefp, vrefn, vcmo, vcmi, autocali
                                [0x4, 0x08, sdd, 0, 0xDF, 0x33, 0x89, 0x67, 0],
                                [0x5, 0x08, sdd, 0, 0xDF, 0x33, 0x89, 0x67, 0],
                                [0x6, 0x08, sdd, 0, 0xDF, 0x33, 0x89, 0x67, 0],
                                [0x7, 0x08, sdd, 0, 0xDF, 0x33, 0x89, 0x67, 0],
                                [0x8, 0x08, sdd, 0, 0xDF, 0x33, 0x89, 0x67, 0],
                                [0x9, 0x08, sdd, 0, 0xDF, 0x33, 0x89, 0x67, 0],
                                [0xA, 0x08, sdd, 0, 0xDF, 0x33, 0x89, 0x67, 0],
                                [0xB, 0x08, sdd, 0, 0xDF, 0x33, 0x89, 0x67, 0],
                              ]
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
            print (self.regs_int8)
            cfg_paras_rec.append( (femb_id, copy.deepcopy(self.adcs_paras), copy.deepcopy(self.regs_int8), adac_pls_en) )
            self.femb_cfg(femb_id, adac_pls_en )
        if self.data_align_flg != True:
            self.data_align(self.fembs)
            self.data_align_flg = True


    def dat_fe_only_cfg(self, sts=0, snc=0,sg0=0, sg1=0, st0=1, st1=1, swdac=0, sdd=0, sdf=0, dac=0x00, sgp=0, slk0=0, slk1=0, chn=128):
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

    def dat_fe_qc_acq(self, num_samples = 1):
        time.sleep(1)
        rawdata = self.spybuf_trig(fembs=self.fembs, num_samples=num_samples, trig_cmd=0) #returns list of size 1
        return rawdata

    def dat_fe_qc_rst(self, num_samples = 1):
        self.femb_cd_rst()
        for femb_id in self.fembs:
            self.femb_cd_fc_act(femb_id, act_cmd="rst_adcs")
            self.femb_cd_fc_act(femb_id, act_cmd="rst_larasics")
            self.femb_cd_fc_act(femb_id, act_cmd="rst_larasic_spi")

    def dat_fe_qc(self, num_samples=1, adac_pls_en=0, sts=0, snc=0,sg0=0, sg1=0, st0=1, st1=1, swdac=0, sdd=0, sdf=0, dac=0x00, sgp=0, slk0=0, slk1=0, chn=128):
        self.dat_fe_qc_cfg(adac_pls_en=adac_pls_en, sts=sts, snc=snc,sg0=sg0, sg1=sg1, st0=st0, st1=st1, swdac=swdac, sdd=sdd, sdf=sdf, dac=dac, sgp=sgp, slk0=slk0, slk1=slk1 )
        data =  self.dat_fe_qc_acq(num_samples)
        self.dat_fe_qc_rst()
        return data


    def dat_asic_chk(self):
        rawdata = self.dat_fe_qc( num_samples = 1, adac_pls_en = 1, sts=1, snc=1,sg0=0, sg1=0, st0=1, st1=1, swdac=1, sdd=1, sdf=0, dac=0x20, slk0=0, slk1=0)
        dec_data = wib_spy_dec_syn(buf0=rawdata[0][0][0], buf1=rawdata[0][0][0], trigmode='SW', buf_end_addr=rawdata[0][1], trigger_rec_ticks=rawdata[0][1], fembs=self.fembs)
        if self.dat_on_wibslot<=1:
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
        
            if link == 0:
                femb0.append(dec_data[0][i]["FEMB0_2"])
                femb1.append(dec_data[0][i]["FEMB1_3"])
            else:
                femb2.append(dec_data[1][i]["FEMB0_2"])
                femb3.append(dec_data[1][i]["FEMB1_3"])

    
        datd = [femb0, femb1, femb2, femb3][self.dat_on_wibslot]
        datd = list(zip(*datd))
        initchk_flg = True
        for ch in range(16*8):
            chmax = np.max(datd[ch][0:1500])
            chped = np.mean(datd[ch][0:1500])
            chmin = np.min(datd[ch][0:1500])
            if (chmax > 8000) & (chped < 2000) & (chped > 300) & (chmin<100):
                pass
            else:
                initchk_flg = False 
                print ("ERROR", ch, chmax, chped, chmin)
        if initchk_flg:
            print ("Pass the interconnection checkout, QC may start now!")

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
        self.adcs_paras = [ # c_id, data_fmt(0x89), diff_en(0x84), sdf_en(0x80), vrefp, vrefn, vcmo, vcmi, autocali
                            [0x4, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 0],
                            [0x5, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 0],
                            [0x6, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 0],
                            [0x7, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 0],
                            [0x8, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 0],
                            [0x9, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 0],
                            [0xA, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 0],
                            [0xB, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 0],
                          ]
        mux_cs=5
        mux_name = self.mon_fe_cs[mux_cs]
        self.cdpoke(0, 0xC, 0, self.DAT_FE_CALI_CS, 0x00)    
        self.cdpoke(0, 0xC, 0, self.DAT_TEST_PULSE_EN, 0x00) #disable pin4 of U230 (FE_INS_PLS_CS)   
        self.cdpoke(0, 0xC, 0, self.DAT_TEST_PULSE_SOCKET_EN, 0x00) #disable pin4 of U230 (FE_INS_PLS_CS = 1)   
        self.cdpoke(0, 0xC, 0, self.DAT_FE_IN_TST_SEL_LSB, 0x00)    
        self.cdpoke(0, 0xC, 0, self.DAT_FE_IN_TST_SEL_MSB, 0x00)    
        self.cdpoke(0, 0xC, 0, self.DAT_ADC_FE_TEST_SEL, mux_cs<<4)    
        self.cdpoke(0, 0xC, 0, self.DAT_FE_TEST_SEL_INHIBIT, 0x00)    

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
            mon_datas["MON_DAC_SGP1"] = datas_dac

            for sg0 in [0,1]:
                for sg1 in [0,1]:
                    datas_dac =[]
                    for dac in range(0,64, 1):
                        for fe in range(8):
                            self.set_fechip_global(chip=fe&0x07, swdac=3, dac=dac, sgp=sgp)
                        self.set_fe_sync()
                        self.femb_fe_cfg(femb_id=femb_id)
                        time.sleep(0.1)
                        datas = self.dat_monadcs()[0]
                        datas_dac.append([dac, datas])
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

