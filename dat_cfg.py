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

    def wib_pwr_on_dat(self):
        print ("Initilization checkout")
        self.wib_fw()
        print ("Turn off all power rails for FEMBs")
        self.femb_powering([])
        self.data_align_flg = False
        time.sleep(1)
        
        #set FEMB voltages
        self.fembs_vol_set(vfe=4.0, vcd=4.0, vadc=4.0)
        #power on FEMBs
        self.femb_powering(self.fembs)
        self.data_align_flg = False
        self.femb_cd_rst()
        print ("Wait 10 seconds ...")
        time.sleep(10)

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
                    if (pwr_meas[key] < 1) or (pwr_meas[key] > 2) :
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
                bus_voltage = self.datpower_getvoltage(addr, fe=asic)
                current = self.datpower_getcurrent(addr, fe=asic)
                asics_pwr_info[asic_list[asic] + "_" + pwrrails[i]] = [bus_voltage, current*1e+3, bus_voltage*current*1e+3]
        return asics_pwr_info

    def cd_pwr_info(self,asic_list, dat_addrs, pwrrails):
        asics_pwr_info = {}
        for asic in range(2):
            for i in range(len(dat_addrs)):
                addr = dat_addrs[i]
                bus_voltage = self.datpower_getvoltage(addr, cd=asic)
                current = self.datpower_getcurrent(addr, cd=asic)
                asics_pwr_info[asic_list[asic] + "_" + pwrrails[i]] = [bus_voltage, current*1e+3, bus_voltage*current*1e+3]
        return asics_pwr_info


    def fe_pwr_meas(self,):
        print("Power Check for All power rails")
        fe_list = ["FE1", "FE2", "FE3", "FE4", "FE5", "FE6", "FE7", "FE8"]
        addrs = [0x40, 0x41, 0x42]
        pwrrails = ["VDDA", "VDDO", "VPPP"]
        fes_pwr_info = self.feadc_pwr_info(asic_list=fe_list, dat_addrs=addrs, pwrrails=pwrrails)
        return fes_pwr_info

    def adc_pwr_meas(self):
        adc_list = ["ADC1", "ADC2", "ADC3", "ADC4", "ADC5", "ADC6", "ADC7", "ADC8"]
        addrs = [0x43, 0x44, 0x45, 0x46]
        pwrrails = ["VDDA2P5", "VDDD1P2", "VDDIO", "VDDD2P5"]
        adcs_pwr_info = self.feadc_pwr_info(asic_list=adc_list, dat_addrs=addrs, pwrrails=pwrrails)
#        kl = list(adcs_pwr_info.keys())
#        for onekey in kl:
#            print (onekey, adcs_pwr_info[onekey])
        return adcs_pwr_info

    def cd_pwr_meas(self):
        cd_list = ["CD1", "CD2"]
        addrs = [0x40, 0x41, 0x43, 0x45, 0x44]
        pwrrails = ["CD_VDDA", "FE_VDDA", "CD_VDDCORE", "CD_VDDD", "CD_VDDIO"]
        cds_pwr_info = self.cd_pwr_info(asic_list=cd_list, dat_addrs=addrs, pwrrails=pwrrails)
        return cds_pwr_info

    def asic_init_pwrchk(self, fes_pwr_info, adcs_pwr_info, cds_pwr_info):
        warn_flg = False
        kl = list(fes_pwr_info.keys())
        for onekey in kl:
            if "VDDA" in onekey:
                if  (fes_pwr_info[onekey][0] > 1.75) & (fes_pwr_info[onekey][0] < 1.85) & (fes_pwr_info[onekey][1] > 15  ) & (fes_pwr_info[onekey][0] < 25  ) :
                    pass
                else:
                    print ("Warning: {} is out of range {}".format(onekey, fes_pwr_info[onekey]))
                    warn_flg = True
            if "VDDO" in onekey:
                if  (fes_pwr_info[onekey][0] > 1.75) & (fes_pwr_info[onekey][0] < 1.85) & (fes_pwr_info[onekey][1] > -0.1  ) & (fes_pwr_info[onekey][0] < 3  ) :
                    pass
                else:
                    print ("Warning: {} is out of range {}".format(onekey, fes_pwr_info[onekey]))
                    warn_flg = True
            if "VDDP" in onekey:
                if  (fes_pwr_info[onekey][0] > 1.75) & (fes_pwr_info[onekey][0] < 1.85) & (fes_pwr_info[onekey][1] > 28  ) & (fes_pwr_info[onekey][0] < 37  ) :
                    pass
                else:
                    print ("Warning: {} is out of range {}".format(onekey, fes_pwr_info[onekey]))
                    warn_flg = True

        kl = list(adcs_pwr_info.keys())
        for onekey in kl:
            if "VDDA2P5" in onekey:
                if  (adcs_pwr_info[onekey][0] > 2.20) & (adcs_pwr_info[onekey][0] < 2.30) & (adcs_pwr_info[onekey][1] > 110  ) & (adcs_pwr_info[onekey][0] < 140  ) :
                    pass
                else:
                    print ("Warning: {} is out of range {}".format(onekey, adcs_pwr_info[onekey]))
                    warn_flg = True
            if "VDDD2P5" in onekey:
                if  (adcs_pwr_info[onekey][0] > 2.20) & (adcs_pwr_info[onekey][0] < 2.30) & (adcs_pwr_info[onekey][1] > 15  ) & (adcs_pwr_info[onekey][0] < 25  ) :
                    pass
                else:
                    print ("Warning: {} is out of range {}".format(onekey, adcs_pwr_info[onekey]))
                    warn_flg = True

            if "VDDIO" in onekey:
                if  (adcs_pwr_info[onekey][0] > 2.20) & (adcs_pwr_info[onekey][0] < 2.30) & (adcs_pwr_info[onekey][1] > 3  ) & (adcs_pwr_info[onekey][0] < 8  ) :
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
                if  (cds_pwr_info[onekey][0] > 1.75) & (cds_pwr_info[onekey][0] < 1.85) & (cds_pwr_info[onekey][1] > -0.1  ) & (cds_pwr_info[onekey][0] < 3  ) :
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
        if warn_flg:
            print ("please check before restart")
            input ("exit by clicking any button and Enter")
            exit()

    def dat_fe_qc(self, num_samples = 1, adac_pls_en = 1, sts=1, snc=1,sg0=0, sg1=0, st0=1, st1=1, swdac=1, sdd=1, sdc=0, dac=0x20, slk0=0, slk1=1):
        self.femb_cd_rst()
        cfg_paras_rec = []
        for femb_id in self.fembs:
            self.adcs_paras = [ # c_id, data_fmt(0x89), diff_en(0x84), sdc_en(0x80), vrefp, vrefn, vcmo, vcmi, autocali
                                [0x4, 0x08, sdd, 0, 0xDF, 0x33, 0x89, 0x67, 0],
                                [0x5, 0x08, sdd, 0, 0xDF, 0x33, 0x89, 0x67, 0],
                                [0x6, 0x08, sdd, 0, 0xDF, 0x33, 0x89, 0x67, 0],
                                [0x7, 0x08, sdd, 0, 0xDF, 0x33, 0x89, 0x67, 0],
                                [0x8, 0x08, sdd, 0, 0xDF, 0x33, 0x89, 0x67, 0],
                                [0x9, 0x08, sdd, 0, 0xDF, 0x33, 0x89, 0x67, 0],
                                [0xA, 0x08, sdd, 0, 0xDF, 0x33, 0x89, 0x67, 0],
                                [0xB, 0x08, sdd, 0, 0xDF, 0x33, 0x89, 0x67, 0],
                              ]
            self.set_fe_board(sts=sts, snc=snc,sg0=sg0, sg1=sg1, st0=st0, st1=st1, swdac=swdac, sdd=sdd, sdc=sdc, dac=dac, slk0=slk0, slk1=slk1 )
            adac_pls_en = adac_pls_en #enable LArASIC interal calibraiton pulser
            cfg_paras_rec.append( (femb_id, copy.deepcopy(self.adcs_paras), copy.deepcopy(self.regs_int8), adac_pls_en) )
            self.femb_cfg(femb_id, adac_pls_en )
        if self.data_align_flg != True:
            self.data_align(self.fembs)
            self.data_align_flg = True
        time.sleep(1)
        rawdata = self.spybuf_trig(fembs=self.fembs, num_samples=num_samples, trig_cmd=0) #returns list of size 1
        return rawdata


    def dat_asic_chk(self):
        rawdata = self.dat_fe_qc( num_samples = 1, adac_pls_en = 1, sts=1, snc=1,sg0=0, sg1=0, st0=1, st1=1, swdac=1, sdd=1, sdc=0, dac=0x20, slk0=0, slk1=1)
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
            if (chmax > 10000) & (chped < 3500) & (chped > 2000) & (chmin<100):
                pass
            else:
                initchk_flg = False 
                print (ch, chmax, chped, chmin)
        if initchk_flg:
            print ("Pass the interconnection checkout, QC starts now!")
                
dat =  DAT_CFGS()
dat.wib_pwr_on_dat()
fes_pwr_info = dat.fe_pwr_meas()
adcs_pwr_info = dat.adc_pwr_meas()
cds_pwr_info = dat.cd_pwr_meas()
dat.asic_init_pwrchk(fes_pwr_info, adcs_pwr_info, cds_pwr_info)
dat.dat_asic_chk()

#        print ("Data save in %s"%outputFile)
#        with open(outputFile, 'wb') as f:
#            pickle.dump([pwr_meas, fes_pwr_info], f)
