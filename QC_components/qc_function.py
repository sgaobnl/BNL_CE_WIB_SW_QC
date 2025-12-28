import pickle
import copy
import time
import numpy as np
import QC_components.qc_log as log
from wib_cfgs import WIB_CFGS

chk = WIB_CFGS()

def monitor_power_rail(interface, fembs, datadir, save = False):
    sps = 10
    vold = chk.wib_vol_mon(femb_ids=fembs, sps=sps)
    dkeys = list(vold.keys())
    LSB = 2.048 / 16384
    for fembid in fembs:
        vgnd = vold["GND"][0][fembid]
    rawdata = [vold, fembs]
    if save:
        fp = datadir + "MON_Regular_"+ interface +"_{}_{}_{}_0x{:02x}.bin".format("200mVBL", "14_0mVfC", "2_0us", 0x00)
        # with open(fp, 'wb') as fn:
        #     pickle.dump([vold, fembs], fn)
    return rawdata

def take_data(self, sts=0, snc=0, sg0=0, sg1=0, st0=0, st1=0, dac=0, fp=None, sdd=0, sdf=0, slk0=0, slk1=0, sgp=0,
              pwr_flg=True, swdac=1, adc_sync_pat=False, bypass=False):
    cfg_paras_rec = []
    ext_cali_flg = False
    self.chk.adcs_paras = [  # c_id, data_fmt(0x89), diff_en(0x84), sdc_en(0x80), vrefp, vrefn, vcmo, vcmi,
        [0x4, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 1],
        [0x5, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 1],
        [0x6, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 1],
        [0x7, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 1],
        [0x8, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 1],
        [0x9, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 1],
        [0xA, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 1],
        [0xB, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 1],
    ]
    for femb_id in self.fembs:
        if sdd == 1:
            self.chk.adc_flg[femb_id] = True
            for i in range(8):
                self.chk.adcs_paras[i][2] = 1  # enable differential
        if adc_sync_pat:
            self.chk.adc_flg[femb_id] = True
            for i in range(8):
                if bypass:
                    self.chk.adcs_paras[i][1] = self.chk.adcs_paras[i][1] | 0x20
                else:
                    self.chk.adcs_paras[i][1] = self.chk.adcs_paras[i][1] | 0x10
        # if self.autocali_flg not True:
        #    self.chk.adc_flg[femb_id] = True
        #    for i in range(8):
        #        self.chk.adcs_paras[i][8]=1   # enable adc calibration
        self.chk.fe_flg[femb_id] = True
        if sts == 1:
            if swdac == 1:  # internal ASIC-DAC is enabled
                self.chk.set_fe_board(sts=sts, snc=snc, sg0=sg0, sg1=sg1, st0=st0, st1=st1, swdac=1, dac=dac,
                                      sdd=sdd, sdf=sdf, slk0=slk0, slk1=slk1, sgp=sgp)
                adac_pls_en = 1
            elif swdac == 2:  # external DAC is enabled
                self.chk.set_fe_board(sts=sts, snc=snc, sg0=sg0, sg1=sg1, st0=st0, st1=st1, swdac=2, dac=dac,
                                      sdd=sdd, sdf=sdf, slk0=slk0, slk1=slk1, sgp=sgp)
                adac_pls_en = 0
                ext_cali_flg = True
        else:
            self.chk.set_fe_board(sts=sts, snc=snc, sg0=sg0, sg1=sg1, st0=st0, st1=st1, swdac=0, dac=0x0, sdd=sdd,
                                  sdf=sdf, slk0=slk0, slk1=slk1, sgp=sgp)
            adac_pls_en = 0
        time.sleep(0.001)
        cfg_paras_rec.append((femb_id, copy.deepcopy(self.chk.adcs_paras), copy.deepcopy(self.chk.regs_int8), adac_pls_en))
        time.sleep(0.001)
        self.chk.femb_cfg(femb_id, adac_pls_en)
    time.sleep(1)
    if self.chk.align_flg == True:
        self.chk.data_align(self.fembs)
        self.chk.align_flg = False
        time.sleep(0.1)
    # if swdac==2:
    #    sps = 10
    #    vold = self.chk.wib_vol_mon(femb_ids=self.fembs,sps=sps)
    #    time.sleep(1)
    #    vold = self.chk.wib_vol_mon(femb_ids=self.fembs,sps=sps)
    #    dkeys = list(vold.keys())
    #    LSB = 2.048/16384
    #    for fembid in self.fembs:
    #        vgnd = vold["GND"][0][fembid]*LSB
    #        print ("vgnd", vgnd)
    #        break
    #    self.vgndoft = vgnd
    if pwr_flg == True:
        time.sleep(0.5)
        pwr_meas = self.chk.get_sensors()
        sps = 10
        vold = self.chk.wib_vol_mon(femb_ids=self.fembs, sps=sps)
        pwr_meas["Powerrails"] = vold
    else:
        time.sleep(0.05)
        pwr_meas = None
    if ext_cali_flg:
        vdacmax = self.vdacmax
        vdacs = np.arange(vdacmax, self.vgndoft, -(vdacmax - self.vgndoft) / 16)
        for vdac in vdacs:
            for femb_id in self.fembs:
                self.chk.wib_cali_dac(dacvol=vdac)
                if femb_id == 0:
                    self.chk.wib_mon_switches(dac0_sel=1, mon_vs_pulse_sel=1, inj_cal_pulse=1)
                if femb_id == 1:
                    self.chk.wib_mon_switches(dac1_sel=1, mon_vs_pulse_sel=1, inj_cal_pulse=1)
                if femb_id == 2:
                    self.chk.wib_mon_switches(dac2_sel=1, mon_vs_pulse_sel=1, inj_cal_pulse=1)
                if femb_id == 3:
                    self.chk.wib_mon_switches(dac3_sel=1, mon_vs_pulse_sel=1, inj_cal_pulse=1)
            cp_period = 1000
            cp_high_time = int(cp_period * 32 * 3 / 4)
            self.chk.wib_pls_gen(fembs=self.fembs, cp_period=cp_period, cp_phase=0, cp_high_time=cp_high_time)
            rawdata = self.chk.spybuf_trig(fembs=self.fembs, num_samples=self.sample_N, trig_cmd=0)
            fplocal = fp[0:-4] + "_vdac%06dmV" % (int((vdacmax - vdac + 0.0001) * 1000)) + fp[-4:]
            with open(fplocal, 'wb') as fn:
                pickle.dump([rawdata, pwr_meas, cfg_paras_rec, self.logs, vdac], fn)
    else:
        rawdata = self.chk.spybuf_trig(fembs=self.fembs, num_samples=self.sample_N, trig_cmd=0)
        with open(fp, 'wb') as fn:
            pickle.dump([rawdata, pwr_meas, cfg_paras_rec, self.logs], fn)
