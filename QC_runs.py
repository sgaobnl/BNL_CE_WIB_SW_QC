import glob

from wib_cfgs import WIB_CFGS
import time
import sys
import numpy as np
import pickle
import copy
import os
import time, datetime, random, statistics
import subprocess
import QC_components.qc_function as a_func
import QC_components.qc_log as log
from QC_tools import ana_tools
#import TestPattern_chk as PLL_TP

class QC_Runs:
    def __init__(self, fembs, sample_N=1):
        self.fembs = fembs
        self.sample_N = sample_N
        self.fembNo={}
        self.fembName={}
        self.vgndoft = 0
        self.vdacmax = 0.5
        self.vstep = 10
        self.chk = WIB_CFGS()
        self.LAr_Dalay = 5
        self.sdd0 = 0
        self.sdf0 = 0
        self.sncs = ["900mVBL", "200mVBL"]
        self.sgs = ["14_0mVfC", "25_0mVfC", "7_8mVfC", "4_7mVfC" ]
        self.pts = ["1_0us", "0_5us",  "3_0us", "2_0us"]

        ####### Test enviroment logs #######

        self.logs={}

        tester=input("please input your name:  ")
        self.logs['tester']=tester
        env_cs = input("Test is performed at cold(LN2) (Y/N)? : ")
        if ("Y" in env_cs) or ("y" in env_cs):
            env = "LN"
            self.logs['env'] = 'Cold'
        else:
            env = "RT"
            self.logs['env'] = 'Warm'


        ToyTPC_en = input("ToyTPC at FE inputs (Y/N) : ")
        if ("Y" in ToyTPC_en) or ("y" in ToyTPC_en):
            toytpc = "PCB_Based"
        else:
            toytpc = "No Toy_TPC"
        self.logs['toytpc']=toytpc

        note = input("A short note (<200 letters):")
        self.logs['note']=note

        for i in self.fembs:
            self.fembNo['femb{}'.format(i)]=input("FEMB{} ID: ".format(i)).strip()

        self.logs['femb id']=self.fembNo
        self.logs['UTC_Date']=datetime.datetime.now().strftime("%m_%d_%Y_%H_%M_%S")
        log.report_log00 = self.logs    ### report
        ####### Create data saving directory #######

        save_dir = "./QC"
        if not os.path.exists(save_dir):
            try:
                os.makedirs(save_dir)
            except OSError:
                print("Error to create folder %s" % save_dir)
                sys.exit()

        self.save_dir = save_dir+"/"

        fp = self.save_dir + "logs_env.bin"
        with open(fp, 'wb') as fn:
             pickle.dump(self.logs, fn)

    def pwr_fembs(self, status):

        #self.chk = WIB_CFGS()
        self.chk.wib_fw()
        self.chk.fembs_vol_set(vfe=3.0, vcd=3.0, vadc=3.5)

        if status=='on':
            print("Turning on FEMBs")
            self.chk.femb_power_com_on(self.fembs)
            # self.chk.femb_power_com_on(self.fembs)
            # pwr_meas = self.chk.get_sensors()
        if status=='off':
            print("Turning off FEMBs")
            self.chk.femb_powering([])
            # self.chk.femb_power_com_off([])

    def check_pwr_off(self, pwr_data):
        pwr_sts = True
        for i in self.fembs:
           bias_v = pwr_data['FEMB%d_BIAS_V'%i]
           fe_v = pwr_data['FEMB%d_DC2DC0_V'%i]
           cd_v = pwr_data['FEMB%d_DC2DC1_V'%i]
           adc_v = pwr_data['FEMB%d_DC2DC2_V'%i]
           print (bias_v, fe_v, cd_v, adc_v)

           if (bias_v < 3.0) and (fe_v < 0.5) and (cd_v < 0.5) and (adc_v < 0.5):
               print ("FEMB {} is turned off".format(i))
           else:
               pwr_sts = False
        return pwr_sts

    def take_data(self, sts=0, snc=0, sg0=0, sg1=0, st0=0, st1=0, dac=0, fp=None, sdd=0, sdf=0, slk0=0, slk1=0, sgp=0,  pwr_flg=False, swdac=1, adc_sync_pat=False, bypass = False, autocali=0, excali = False):

        cfg_paras_rec = []
        ext_cali_flg = False  # Lingyunlke for Debug
        datad = {}

        self.chk.adcs_paras = [ # c_id, data_fmt(0x89), diff_en(0x84), sdc_en(0x80), vrefp, vrefn, vcmo, vcmi,
                            [0x4, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, autocali],
                            [0x5, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, autocali],
                            [0x6, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, autocali],
                            [0x7, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, autocali],
                            [0x8, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, autocali],
                            [0x9, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, autocali],
                            [0xA, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, autocali],
                            [0xB, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, autocali],
                          ]
        if sts == 1 :
            if swdac==1: #internal ASIC-DAC is enabled
                self.chk.set_fe_board(sts=sts,snc=snc,sg0=sg0,sg1=sg1, st0=st0, st1=st1, swdac=1, dac=dac, sdd=sdd,sdf=sdf,slk0=slk0,slk1=slk1,sgp=sgp)
                adac_pls_en = 1
                for femb_id in self.fembs:
                    self.chk.femb_cd_gpio(femb_id=femb_id, cd1_0x26=0x02, cd1_0x27=0x1f, cd2_0x26=0x00, cd2_0x27=0x1f)
            elif swdac==2: #external DAC is enabled
                self.chk.set_fe_board(sts=sts,snc=snc,sg0=sg0,sg1=sg1, st0=st0, st1=st1, swdac=2, dac=dac, sdd=sdd,sdf=sdf,slk0=slk0,slk1=slk1,sgp=sgp)
                adac_pls_en = 0
                ext_cali_flg = True
                for femb_id in self.fembs:
                    self.chk.femb_cd_gpio(femb_id=femb_id, cd1_0x26=0x00, cd1_0x27=0x1f, cd2_0x26=0x00, cd2_0x27=0x1f)
        else:
            self.chk.set_fe_board(sts=sts, snc=snc, sg0=sg0, sg1=sg1, st0=st0, st1=st1, swdac=0, dac=0x0, sdd=sdd,sdf=sdf,slk0=slk0,slk1=slk1,sgp=sgp)
            adac_pls_en = 0
            for femb_id in self.fembs:
                self.chk.femb_cd_gpio(femb_id=femb_id, cd1_0x26=0x02, cd1_0x27=0x1f, cd2_0x26=0x00, cd2_0x27=0x1f)

        if adc_sync_pat:
            for i in range(8):
                if bypass:
                    self.chk.adcs_paras[i][1] = self.chk.adcs_paras[i][1]|0x20
                else:
                    self.chk.adcs_paras[i][1] = self.chk.adcs_paras[i][1]|0x10
        for femb_id in self.fembs:
            if sdd==1:
                self.chk.adc_flg[femb_id] = True
                for i in range(8):
                    self.chk.adcs_paras[i][2]=1   # enable differential

            if adc_sync_pat:
                self.chk.adc_flg[femb_id] = True

            self.chk.fe_flg[femb_id] = True
            cfg_paras_rec.append( (femb_id, copy.deepcopy(self.chk.adcs_paras), copy.deepcopy(self.chk.regs_int8), adac_pls_en) )
            self.chk.femb_cfg(femb_id, adac_pls_en )
        #if (self.sdd0 != sdd) or (self.sdf0 != sdf):
        #self.sdd0 = sdd
        #self.sdf0 = sdf
        if autocali&0x01:
            time.sleep(0.5)
            for femb_id in self.fembs:
                self.chk.femb_autocali_off(femb_id)
        else:
            time.sleep(0.1) # temperary

        if self.chk.align_flg == True:
            self.chk.data_align(self.fembs)
            self.chk.align_flg = False
            time.sleep(0.001)

        # self.chk.wib_pls_gen(fembs=self.fembs, cp_period=500, cp_phase=0, cp_high_time=0)
        # self.chk.wib_mon_switches(dac0_sel=0, dac1_sel=0, dac2_sel=0, dac3_sel=0, mon_vs_pulse_sel=1, inj_cal_pulse=1)
        # for femb_id in self.fembs:
        #     self.chk.femb_cd_gpio(femb_id=femb_id, cd1_0x26=0x03, cd1_0x27=0x1f, cd2_0x26=0x00, cd2_0x27=0x1f)

        if pwr_flg==True:
            time.sleep(0.5)
            pwr_meas = self.chk.get_sensors()
            sps = 10
            vold = self.chk.wib_vol_mon(femb_ids=self.fembs,sps=sps)
            pwr_meas["Powerrails"] = vold
        else:
            time.sleep(0.01)
            pwr_meas = None

        if autocali&0x01:
            return  None
        if dac == 0:
            time.sleep(0.5)

        if (sdd == 1) or (sdf == 1) or (sgp == 1):
            print ("warning: extra 3.5 delay for DIFF and SE_ON after configuration")
            time.sleep(self.LAr_Dalay)
        else:
            time.sleep(0.3)

        if ext_cali_flg:
            if excali == False:
                datae = {}
                print ("Calibration with pulser from WIB starts...")
                cp_period = 500
                vdacmax=self.vdacmax
                vdacs = np.arange(vdacmax,self.vgndoft,-(vdacmax-self.vgndoft)/self.vstep)
                dac0_sel = 0
                dac1_sel = 0
                dac2_sel = 0
                dac3_sel = 0
                for vdac in vdacs:
                    self.chk.wib_cali_dac(dacvol=vdac)
                    for femb_id in self.fembs:
                        if femb_id == 0:
                            dac0_sel=1
                        if femb_id == 1:
                            dac1_sel=1
                        if femb_id == 2:
                            dac2_sel=1
                        if femb_id == 3:
                            dac3_sel=1
                    self.chk.wib_mon_switches(dac0_sel, dac1_sel, dac2_sel, dac3_sel, mon_vs_pulse_sel=1, inj_cal_pulse=1)
                    cp_high_time = int(cp_period*32*7/8)
                    self.chk.wib_pls_gen(fembs=self.fembs, cp_period=cp_period, cp_phase=1, cp_high_time=cp_high_time)
                    time.sleep(0.01)
                    rawdata = self.chk.spybuf_trig(fembs=self.fembs, num_samples=self.sample_N,trig_cmd=0)
                    fplocal = fp[0:-4] + "_vdac%06dmV"%(int((vdac+0.0001)*1000))+fp[-4:]
                    # with open(fplocal, 'wb') as fn:
                    #     pickle.dump( [rawdata, pwr_meas, cfg_paras_rec, self.logs, vdac], fn)
                    fsubdirs = fplocal.split("/")
                    print(fsubdirs)
                    print(fsubdirs[-1])
                    datad[fsubdirs[-1]] = [rawdata, pwr_meas, cfg_paras_rec, self.logs]
                self.chk.wib_pls_gen(fembs=self.fembs, cp_period=cp_period, cp_phase=0, cp_high_time=0)
                self.chk.wib_mon_switches() #close wib_mon
            else:
                time.sleep(0.5)
                dac0_sel = 0
                dac1_sel = 0
                dac2_sel = 0
                dac3_sel = 0
                for x in [22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36]:
                    dacvol = x * 0.05
                    self.chk.wib_cali_dac(dacvol=dacvol)
                    for fembid in self.fembs:
                        if fembid == 0:
                            dac0_sel = 1
                        if fembid == 1:
                            dac1_sel = 1
                        if fembid == 2:
                            dac2_sel = 1
                        if fembid == 3:
                            dac3_sel = 1
                    self.chk.wib_mon_switches(dac0_sel=dac0_sel, dac1_sel=dac1_sel, dac2_sel=dac2_sel, dac3_sel=dac3_sel, mon_vs_pulse_sel=1, inj_cal_pulse=0)
                    print('DAC value: {}'.format(dacvol))
                    # input('debug dac, enable route')
                    cp_period = 500
                    cp_high_time = int(cp_period * 32 * 1 / 8)
                    # cp_high_time = int(cp_period*32*1/2)
                    self.chk.wib_pls_gen(fembs=self.fembs, cp_period=cp_period, cp_phase=0, cp_high_time=cp_high_time, inj_cal_pulse_sw=1)
                    # input('debug pulse enable')
                    for femb_id in self.fembs:
                        self.chk.femb_cd_gpio(femb_id=femb_id, cd1_0x26=0x00, cd1_0x27=0x1f, cd2_0x26=0x00, cd2_0x27=0x1f)
                    # input('debug enable FEMB external pulse route')
                    time.sleep(0.01)
                    ####################FEMBs Data taking################################
                    rawdata = self.chk.spybuf_trig(fembs=self.fembs, num_samples=self.sample_N, trig_cmd=0)
                    fplocal = fp[0:-4] + "_vdac%06dmV" % (int((dacvol + 0.0001) * 1000)) + fp[-4:]
                    with open(fplocal, 'wb') as fn:
                        pickle.dump( [rawdata, pwr_meas, cfg_paras_rec, self.logs, x], fn)
                    fsubdirs = fplocal.split("/")
                    print(fsubdirs)
                    print(fsubdirs[-1])
                    datad[fsubdirs[-1]] = [rawdata, pwr_meas, cfg_paras_rec, self.logs]
                self.chk.wib_mon_switches()  # close wib_mon

        else:
            rawdata = self.chk.spybuf_trig(fembs=self.fembs, num_samples=self.sample_N,trig_cmd=0)

            # with open(fp, 'wb') as fn:
            #     pickle.dump( [rawdata, pwr_meas, cfg_paras_rec, self.logs], fn)
            datad = [rawdata, pwr_meas, cfg_paras_rec, self.logs]
        return datad

    def merge_bin_files_to_dictbin(self, folder_path, output_file):

        bin_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.bin')]
        merged_dict = {}
        for bin_file in bin_files:
            file_name = os.path.basename(bin_file)
            with open(bin_file, 'rb') as f:
                merged_dict[file_name] = f.read()
            # os.remove(bin_file)   # remove the raw bin_file
        local_username = 'DUNE'
        local_password = '216'
        local_ip = '192.168.121.10'
        local_path = r'D:\A0-FEMB_07_1T_Auto\{}'.format(output_file)

        output_file = folder_path + output_file
        with open(output_file, 'wb') as out:
            for content in merged_dict.values():
                out.write(content)

        return merged_dict

    def pwr_consumption(self):
        print('QC Item Begin')
        datad = {}
        datadir = self.save_dir+"PWR_Meas/"
        try:
            os.makedirs(datadir)
        except OSError:
            print ("Error to create folder %s !!! Continue to next test........"%datadir)
            return

        snc = 1 # 200 mV
        sg0 = 0
        sg1 = 0 # 14mV/fC
        st0 = 1
        st1 = 1 # 2us

        ####### SE OFF #######
        self.sample_N = 1
        self.chk.femb_cd_rst()
        dac = 0x00
        sts = 0
        fp = datadir + "PWR_SE_OFF_{}_{}_{}_0x{:02x}.bin".format("200mVBL","14_0mVfC","2_0us",dac)
        datad["PWR_SE_OFF_{}_{}_{}_0x{:02x}.bin".format("200mVBL","14_0mVfC","2_0us",dac)] = self.take_data(sts, snc, sg0, sg1, st0, st1, dac, fp, pwr_flg=True) #   power measurement


        #   SE OFF Power Rail
        datad["MON_Regular_SE_OFF_200mVBL_14_0mVfC_2_0us_0x00.bin"]=a_func.monitor_power_rail("SE_OFF", self.fembs, datadir, 1)
        dac = 0x20
        sts = 1
        fp = datadir + "PWR_SE_OFF_pulse_{}_{}_{}_0x{:02x}.bin".format("200mVBL","14_0mVfC","2_0us",dac)
        datad["PWR_SE_OFF_pulse_{}_{}_{}_0x{:02x}.bin".format("200mVBL","14_0mVfC","2_0us",dac)] = self.take_data(sts, snc, sg0, sg1, st0, st1, dac, fp, pwr_flg=False)


        ####### SE with LArASIC buffer on #######
        #self.chk.femb_cd_rst()
        dac = 0x00
        sts=1
        fp = datadir + "PWR_SE_ON_{}_{}_{}_0x{:02x}.bin".format("200mVBL","14_0mVfC","2_0us",dac)
        datad["PWR_SE_ON_{}_{}_{}_0x{:02x}.bin".format("200mVBL","14_0mVfC","2_0us",dac)] = self.take_data(sts, snc, sg0, sg1, st0, st1, dac, fp, sdf=1, pwr_flg=True)

        #   SE on Power Rail
        datad["MON_Regular_SE_ON_200mVBL_14_0mVfC_2_0us_0x00.bin"] = a_func.monitor_power_rail("SE_ON", self.fembs, datadir, 1)
        dac = 0x20
        sts=1
        fp = datadir + "PWR_SE_ON_pulse_{}_{}_{}_0x{:02x}.bin".format("200mVBL","14_0mVfC","2_0us",dac)
        datad["PWR_SE_ON_pulse_{}_{}_{}_0x{:02x}.bin".format("200mVBL","14_0mVfC","2_0us",dac)] = self.take_data(sts, snc, sg0, sg1, st0, st1, dac, fp, sdf=1, pwr_flg=False)
        ####### DIFF #######
        #self.chk.femb_cd_rst()
        dac = 0x00
        sts = 1
        for i in range(8):
            self.chk.adcs_paras[i][2] = 1    # enable differential interface
        fp = datadir + "PWR_DIFF_{}_{}_{}_0x{:02x}.bin".format("200mVBL","14_0mVfC","2_0us",dac)
        datad["PWR_DIFF_{}_{}_{}_0x{:02x}.bin".format("200mVBL","14_0mVfC","2_0us",dac)] = self.take_data(sts, snc, sg0, sg1, st0, st1, dac, fp, sdd=1, pwr_flg=True)

        #   DIFF Power Rail
        datad["MON_Regular_DIFF_200mVBL_14_0mVfC_2_0us_0x00.bin"] = a_func.monitor_power_rail("DIFF", self.fembs, datadir, 1)
        dac = 0x20
        sts = 1
        fp = datadir + "PWR_DIFF_pulse_{}_{}_{}_0x{:02x}.bin".format("200mVBL","14_0mVfC","2_0us",dac)
        datad["PWR_DIFF_pulse_{}_{}_{}_0x{:02x}.bin".format("200mVBL","14_0mVfC","2_0us",dac)] = self.take_data(sts, snc, sg0, sg1, st0, st1, dac, fp, sdd=1, pwr_flg=False)

        # folder_path = datadir
        # output_file = 'power.bin'
        # self.merge_bin_files_to_dictbin(folder_path, output_file)   # merge into one bin file
        fp = datadir + "QC_PWR_t1" + ".bin"
        with open(fp, 'wb') as fn:
            pickle.dump(datad, fn)
        print('QC Item Done')


    def pwr_cycle(self):
        print('QC Item Begin')
        datad = {}
        datadir = self.save_dir+"PWR_Cycle/"
        if not os.path.exists(datadir):
            try:
                os.makedirs(datadir)
            except OSError:
                print("Error to create folder %s" % datadir)
                sys.exit()
        snc = 1 # 200 mV
        sg0 = 0
        sg1 = 0 # 14mV/fC
        st0 = 1
        st1 = 1 # 2us
        dac = 0x20

        ####### SE 3 cycles #######
        self.chk.femb_cd_rst()
        self.sample_N = 1
        for i in range(3):
            dac = 0
            sts = 0
            fp = datadir + "PWR_cycle{}_SE_{}_{}_{}_0x{:02x}.bin".format(i,"200mVBL","14_0mVfC","2_0us",dac)
            datad["PWR_cycle{}_SE_{}_{}_{}_0x{:02x}.bin".format(i,"200mVBL","14_0mVfC","2_0us",dac)] = self.take_data(sts, snc, sg0, sg1, st0, st1, dac, fp, pwr_flg=True)
            dac = 0x20
            sts = 1
            fp = datadir + "PWR_cycle{}_SE_{}_{}_{}_0x{:02x}.bin".format(i,"200mVBL","14_0mVfC","2_0us",dac)
            datad["PWR_cycle{}_SE_{}_{}_{}_0x{:02x}_pulse.bin".format(i,"200mVBL","14_0mVfC","2_0us",dac)] = self.take_data(sts, snc, sg0, sg1, st0, st1, dac, fp, pwr_flg=False)
            # datad["MON_Regular{}__SE_OFF_{}_{}_{}_0x{:02x}.bin"] = a_func.monitor_power_rail(i,"SE_OFF",
            #                                                                                         self.fembs, datadir,
            #                                                                                         1)
            self.pwr_fembs('off')
            pwr_info = self.chk.get_sensors()
            pwr_status = self.check_pwr_off(pwr_info)

            nn=0
            # change bias value from 5 to 0
            while not pwr_status:
                time.sleep(20)
                nn=nn+1
                pwr_info = self.chk.get_sensors()
                pwr_status = self.check_pwr_off(pwr_info)
                print ("Wait {}s until completely shut down".format(nn))
            self.pwr_fembs('on')

        ####### SE with LArASIC buffer on (1 cycle)#######
        self.chk.femb_cd_rst()
        dac = 0
        sts = 0
        fp = datadir + "PWR_SE_SDF_{}_{}_{}_0x{:02x}.bin".format("200mVBL","14_0mVfC","2_0us",dac)
        datad["PWR_SE_SDF_{}_{}_{}_0x{:02x}.bin".format("200mVBL","14_0mVfC","2_0us",dac)] = self.take_data(sts,snc, sg0, sg1, st0, st1, dac, fp, sdf=1, pwr_flg=True)
        dac = 0x20
        sts = 1
        fp = datadir + "PWR_SE_SDF_{}_{}_{}_0x{:02x}_pulse.bin".format("200mVBL","14_0mVfC","2_0us",dac)
        datad["PWR_SE_SDF_{}_{}_{}_0x{:02x}_pulse.bin".format("200mVBL","14_0mVfC","2_0us",dac)] = self.take_data(sts,snc, sg0, sg1, st0, st1, dac, fp, sdf=1, pwr_flg=False)
        self.pwr_fembs('off')
        pwr_info = self.chk.get_sensors()
        pwr_status = self.check_pwr_off(pwr_info)

        nn=0
        while not pwr_status:
              time.sleep(20)
              nn=nn+1
              pwr_info = self.chk.get_sensors()
              pwr_status = self.check_pwr_off(pwr_info)
              print ("Wait {}s until completely shut down".format(nn))

        self.pwr_fembs('on')

        ####### DIFF (1 cycle) #######
        self.chk.femb_cd_rst()
        dac = 0
        sts = 0
        fp = datadir + "PWR_DIFF_{}_{}_{}_0x{:02x}.bin".format("200mVBL","14_0mVfC","2_0us",dac)
        datad["PWR_DIFF_{}_{}_{}_0x{:02x}.bin".format("200mVBL","14_0mVfC","2_0us",dac)] = self.take_data(sts, snc, sg0, sg1, st0, st1, dac, fp, sdd=1, pwr_flg=True)
        dac = 0x20
        sts = 1
        fp = datadir + "PWR_DIFF_{}_{}_{}_0x{:02x}_pulse.bin".format("200mVBL","14_0mVfC","2_0us",dac)
        datad["PWR_DIFF_{}_{}_{}_0x{:02x}_pulse.bin".format("200mVBL","14_0mVfC","2_0us",dac)] = self.take_data(sts, snc, sg0, sg1, st0, st1, dac, fp, sdd=1, pwr_flg=False)

        fp = datadir + "QC_PWR_Cycle_t2" + ".bin"
        with open(fp, 'wb') as fn:
            pickle.dump(datad, fn)
        print('QC Item Done')


    def femb_leakage_cur(self):
        print('QC Item Begin')
        datad = {}
        datadir = self.save_dir+"Leakage_Current/"
        try:
            os.makedirs(datadir)
        except OSError:
            print ("Error to create folder %s !!! Continue to next test........"%datadir)
            return

        snc = 1 # 200 mV
        sg0 = 0
        sg1 = 0 # 14mV/fC
        st0 = 1
        st1 = 1 # 2us
        dac = 0x20
        sts = 1

        ####### 500 pA #######
        self.chk.femb_cd_rst()
        self.sample_N = 5
        fp = datadir + "LC_SE_{}_{}_{}_0x{:02x}_{}.bin".format("200mVBL","14_0mVfC","2_0us",0x20, "500pA")
        datad["LC_SE_{}_{}_{}_0x{:02x}_{}.bin".format("200mVBL","14_0mVfC","2_0us",0x20, "500pA")] = self.take_data(sts, snc, sg0, sg1, st0, st1, dac, fp, slk0=0, slk1=0, pwr_flg=False)

        ####### 100 pA #######
        #self.chk.femb_cd_rst()
        fp = datadir + "LC_SE_{}_{}_{}_0x{:02x}_{}.bin".format("200mVBL","14_0mVfC","2_0us",0x20, "100pA")
        datad["LC_SE_{}_{}_{}_0x{:02x}_{}.bin".format("200mVBL","14_0mVfC","2_0us",0x20, "100pA")] = self.take_data(sts, snc, sg0, sg1, st0, st1, dac, fp, slk0=1, slk1=0, pwr_flg=False)

        ####### 5 nA #######
        #self.chk.femb_cd_rst()
        fp = datadir + "LC_SE_{}_{}_{}_0x{:02x}_{}.bin".format("200mVBL","14_0mVfC","2_0us",0x20, "5nA")
        datad["LC_SE_{}_{}_{}_0x{:02x}_{}.bin".format("200mVBL","14_0mVfC","2_0us",0x20, "5nA")] = self.take_data(sts, snc, sg0, sg1, st0, st1, dac, fp, slk0=0, slk1=1, pwr_flg=False)

        ####### 1 nA #######
        #self.chk.femb_cd_rst()
        fp = datadir + "LC_SE_{}_{}_{}_0x{:02x}_{}.bin".format("200mVBL","14_0mVfC","2_0us",0x20, "1nA")
        datad["LC_SE_{}_{}_{}_0x{:02x}_{}.bin".format("200mVBL","14_0mVfC","2_0us",0x20, "1nA")] = self.take_data(sts, snc, sg0, sg1, st0, st1, dac, fp, slk0=1, slk1=1, pwr_flg=False)

        fp = datadir + "QC_femb_leakage_cur_t3" + ".bin"
        with open(fp, 'wb') as fn:
            pickle.dump(datad, fn)
        print('QC Item Done')

    def femb_chk_pulse(self):
        print('QC Item Begin')
        datadir = self.save_dir+"CHK/"
        datad = {}
        try:
            os.makedirs(datadir)
        except OSError:
            print ("Error to create folder %s !!! Continue to next test........"%datadir)
            return

        sncs = self.sncs
        sgs = self.sgs
        pts = self.pts

        dac = 0x10
        sts = 1

        self.chk.femb_cd_rst()
        self.sample_N = 1
        for snci in range(2):
            for sgi in  range(4):
                sg0 = sgi%2
                sg1 = sgi//2
                for sti in range(4):
                    st0 = sti%2
                    st1 = sti//2
#   SE  2*4*4 = 32  {[snc 200/900 mV] * [sg 4.7/7.8/14/25 mV/fC] * [st 0.5/1/2/3 us]}
                    fp = datadir + "CHK_SE_{}_{}_{}_0x{:02x}.bin".format(sncs[snci],sgs[sgi],pts[sti],dac)
                    datad["CHK_SE_{}_{}_{}_0x{:02x}.bin".format(sncs[snci],sgs[sgi],pts[sti],dac)] = self.take_data(sts, snci, sg0, sg1, st0, st1, dac, fp, pwr_flg=False)

        print('SEON pulse')
        sg1 = 0;    sg0 = 0     # 14 mV/fC
        st1 = 1;    st0 = 1     # 2 us
        self.chk.femb_cd_rst()
        self.sample_N = 1
        for snci in range(2):
#   SEON    2   {[snc 200/900 mV] * [sg 14 mV/fC] * [st 2 us]}  sdf = 1
                    fp = datadir + "CHK_SEON_{}_{}_{}_0x{:02x}.bin".format(sncs[snci], sgs[0], pts[3], dac)
                    datad["CHK_SEON_{}_{}_{}_0x{:02x}.bin".format(sncs[snci], sgs[0], pts[3], dac)] = self.take_data(sts, snci, sg0, sg1, st0, st1, dac, fp, sdf = 1, pwr_flg=False)


        print('Differential Pulse')
#   DIFF    2       {[snc 200/900 mV] * [14 mV/fc] *[2 us]}
        sg1 = 0;    sg0 = 0     # 14 mV/fC
        st1 = 1;    st0 = 1     # 2 us
        self.chk.femb_cd_rst()
        cfg_paras_rec = []
        for i in range(8):
            self.chk.adcs_paras[i][2] = 1    # enable differential interface
        #self.chk.set_fe_board(sts=1, snc=0, sg0=sg0, sg1=sg1, st0=st0, st1=st1, sdd=1, swdac=1, dac=0x10)
        self.sample_N = 1
        for snci in range(2):
                    fp = datadir + "CHK_DIFF_{}_{}_{}_0x{:02x}.bin".format(sncs[snci], sgs[0], pts[3], dac)
                    datad["CHK_DIFF_{}_{}_{}_0x{:02x}.bin".format(sncs[snci], sgs[0], pts[3], dac)] = self.take_data(sts, snci, sg0, sg1, st0, st1, dac, fp, sdd = 1, pwr_flg=False, swdac = 1)
                                #time.sleep(0.5)
        for i in range(8):
            self.chk.adcs_paras[i][2] = 0    # disable differential interface


        print('SGP pulse response')
        #   SGP    4       {[snc 200 mV] * [4.7 7.8 14 25 mV/fc] *[2 us]}
        st1 = 1
        st0 = 1  # 2 us
        sts = 1
        self.chk.femb_cd_rst()
        dac = 0x0C
        cfg_paras_rec = []
        for i in range(8):
            self.chk.adcs_paras[i][2] = 1  # enable differential interface
        # self.chk.set_fe_board(sts=1, snc=0, sg0=sg0, sg1=sg1, st0=st0, st1=st1, sdd=1, swdac=1, dac=0x10)
        self.sample_N = 1
        for sgi in range(4):    # adjust Gain 4.7 7.8 14 25 mV/fc
            sg0 = sgi % 2
            sg1 = sgi // 2
            fp = datadir + "CHK_SGP_{}_{}_{}_0x{:02x}.bin".format(sncs[1], sgs[sgi], pts[3], dac)
            datad["CHK_SGP_{}_{}_{}_0x{:02x}.bin".format(sncs[1], sgs[sgi], pts[3], dac)] = self.take_data(sts, snci, sg0, sg1, st0, st1, dac, fp, sgp=1, pwr_flg=False)


#       External Pulse
        print('External pulse')

        snc = 1 # 200 mV BL
        sg0 = 0
        sg1 = 0 # 14_0 mv/fC
        st0 = 1
        st1 = 1 # 2 us
        sts = 1
        dac=0
        self.chk.femb_cd_rst()
        self.sample_N = 1
        fp = datadir + "CHK_EX_{}_{}_{}.bin".format("200mVBL","14_0mVfC","2_0us")
        datad.update(self.take_data(sts, snc, sg0, sg1, st0, st1, dac, fp, swdac=2, pwr_flg=False))

        fp = datadir + "femb_chk_pulse_t4" + ".bin"
        with open(fp, 'wb') as fn:
            pickle.dump(datad, fn)
        print('QC Item Done')

    #    def femb_chk_pulse2(self):
#
#        datadir = self.save_dir+"CHK2/"
#        try:
#            os.makedirs(datadir)
#        except OSError:
#            print ("Error to create folder %s !!! Continue to next test........"%datadir)
#            return
#
##SE off/on, DIFF on  (14mV/fC, 200mV BL/ 900mV BL, 2us) = 3*2, External pulse
    def debug_02(self):
        print('QC Item Begin')
        datadir = self.save_dir + "CHK/"
        datad = {}
        try:
            os.makedirs(datadir)
        except OSError:
            print("Error to create folder %s !!! Continue to next test........" % datadir)
            return

        #       External Pulse
        print('External pulse')

        snc = 1  # 200 mV BL
        sg0 = 0
        sg1 = 0  # 14_0 mv/fC
        st0 = 1
        st1 = 1 # 2 us
        sts = 1
        dac = 0
        self.chk.femb_cd_rst()
        self.sample_N = 1

        fp = datadir + "CHK_EX_{}_{}_{}.bin".format("200mVBL", "14_0mVfC", "2_0us")

        cfg_paras_rec = []
        datad = {}
        self.chk.adcs_paras = [ # c_id, data_fmt(0x89), diff_en(0x84), sdc_en(0x80), vrefp, vrefn, vcmo, vcmi,
                            [0x4, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 0],
                            [0x5, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 0],
                            [0x6, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 0],
                            [0x7, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 0],
                            [0x8, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 0],
                            [0x9, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 0],
                            [0xA, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 0],
                            [0xB, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 0]
                          ]
        #external DAC is enabled
        self.chk.set_fe_board(sts=1,snc=1,sg0=0,sg1=0, st0=1, st1=1, swdac=2, dac=0, sdd=0,sdf=0,slk0=0,slk1=0,sgp=0)
        adac_pls_en = 0
        ext_cali_flg = True

        for femb_id in self.fembs:
            self.chk.fe_flg[femb_id] = True
            cfg_paras_rec.append( (femb_id, copy.deepcopy(self.chk.adcs_paras), copy.deepcopy(self.chk.regs_int8), adac_pls_en) )
            self.chk.femb_cfg(femb_id, adac_pls_en )
        #self.sdd0 = sdd
        time.sleep(1) #temperary

        if self.chk.align_flg == True:
            self.chk.data_align(self.fembs)
            self.chk.align_flg = False
            time.sleep(0.001)


        time.sleep(0.01)
        pwr_meas = None

        if ext_cali_flg:
            datae = {}
            print ("Calibration with pulser from WIB starts...")
            cp_period = 1000
            vdacmax=self.vdacmax
            vdacs = np.arange(vdacmax,self.vgndoft,-(vdacmax-self.vgndoft)/self.vstep)
            dac0_sel = 0
            dac1_sel = 0
            dac2_sel = 0
            dac3_sel = 0
            for vdac in vdacs:
                self.chk.wib_cali_dac(dacvol=vdac)
                for femb_id in self.fembs:
                    if femb_id == 0:
                        dac0_sel=1
                    if femb_id == 1:
                        dac1_sel=1
                    if femb_id == 2:
                        dac2_sel=1
                    if femb_id == 3:
                        dac3_sel=1
                self.chk.wib_mon_switches(dac0_sel, dac1_sel, dac2_sel, dac3_sel, mon_vs_pulse_sel=1, inj_cal_pulse=1)
                cp_high_time = int(cp_period*32*7/8)
                self.chk.wib_pls_gen(fembs=self.fembs, cp_period=cp_period, cp_phase=0, cp_high_time=cp_high_time)
                rawdata = self.chk.spybuf_trig(fembs=self.fembs, num_samples=self.sample_N,trig_cmd=0)
                fplocal = fp[0:-4] + "_vdac%06dmV"%(int((vdac+0.0001)*1000))+fp[-4:]
                fsubdirs = fplocal.split("/")
                print(fsubdirs)
                print(fsubdirs[-1])
                datad[fsubdirs[-1]] = [rawdata, pwr_meas, cfg_paras_rec, self.logs]
                with open(fplocal, 'wb') as fn:
                    pickle.dump( [rawdata, pwr_meas, cfg_paras_rec, self.logs], fn)
            self.chk.wib_mon_switches()  # close wib_mon
        print('QC Item Done')

    ##
    def femb_rms(self):
        print('QC Item Begin')
        datadir = self.save_dir+"RMS/"
        datad = {}
        try:
            os.makedirs(datadir)
        except OSError:
            print ("Error to create folder %s !!! Continue to next test........"%datadir)
            return

        sncs = self.sncs
        sgs = self.sgs
        pts = self.pts

        dac = 0
        sts = 0

        self.chk.femb_cd_rst()
        self.take_data(autocali=1) #ADC autocalibration once after femb_cd_rst()

        self.sample_N = 10
#

        for sgi in  range(4):
            sg0 = sgi%2
            sg1 = sgi//2
            for sti in range(4):
                st0 = sti%2
                st1 = sti//2
                for snci in range(2):
#   SE OFF  2*4*4 = 32  {[snc 200/900 mV] * [sg 4.7/7.8/14/25 mV/fC] * [st 0.5/1/2/3 us]}
                    fp = datadir + "RMS_SE_{}_{}_{}_0x{:02x}.bin".format(sncs[snci],sgs[sgi],pts[sti],dac)
                    datad["RMS_SE_{}_{}_{}_0x{:02x}.bin".format(sncs[snci],sgs[sgi],pts[sti],dac)] = self.take_data(sts, snci, sg0, sg1, st0, st1, dac, fp, swdac=0, pwr_flg=False)
#   SE  OFF Leakage current *4  100 pA, 500 pA, 1 nA, 5 nA  {200 mV * 14 mV/fC * 2 us}
        snc = 1 # 200 mV
        sg0 = 0;        sg1 = 0 # 14mV/fC
        st0 = 1;        st1 = 1 # 2us
        # 500 pA
        fp = datadir + "RMS_SELC_{}_{}_{}_{}_0x{:02x}.bin".format("200mVBL","14_0mVfC","2_0us", "500pA", dac)
        datad["RMS_SELC_{}_{}_{}_{}_0x{:02x}.bin".format("200mVBL","14_0mVfC","2_0us", "500pA", dac)] = self.take_data(sts, snc, sg0, sg1, st0, st1, dac, fp, slk0=0, slk1=0, swdac=0, pwr_flg=False)
        # 100 pA
        fp = datadir + "RMS_SELC_{}_{}_{}_{}_0x{:02x}.bin".format("200mVBL","14_0mVfC","2_0us", "100pA", dac)
        datad["RMS_SELC_{}_{}_{}_{}_0x{:02x}.bin".format("200mVBL","14_0mVfC","2_0us", "100pA", dac)] = self.take_data(sts, snc, sg0, sg1, st0, st1, dac, fp, slk0=1, slk1=0, swdac=0, pwr_flg=False)
        # 5000 pA
        fp = datadir + "RMS_SELC_{}_{}_{}_{}_0x{:02x}.bin".format("200mVBL","14_0mVfC","2_0us", "5nA", dac)
        datad["RMS_SELC_{}_{}_{}_{}_0x{:02x}.bin".format("200mVBL","14_0mVfC","2_0us", "5nA", dac)] = self.take_data(sts, snc, sg0, sg1, st0, st1, dac, fp, slk0=0, slk1=1, swdac=0, pwr_flg=False)
        # 1000 pA
        fp = datadir + "RMS_SELC_{}_{}_{}_{}_0x{:02x}.bin".format("200mVBL","14_0mVfC","2_0us", "1nA", dac)
        datad["RMS_SELC_{}_{}_{}_{}_0x{:02x}.bin".format("200mVBL","14_0mVfC","2_0us", "1nA", dac)] = self.take_data(sts, snc, sg0, sg1, st0, st1, dac, fp, slk0=1, slk1=1, swdac=0, pwr_flg=False)
#   SE ON  2*4*1 = 8  {[snc 200/900 mV] * [sg 4.7/7.8/14/25 mV/fC] * [st 2 us]}
        st1 = 1;    st0 = 1     # 2 us
        for snci in range(2):
            for sgi in range(4):
                sg0 = sgi % 2
                sg1 = sgi // 2
                fp = datadir + "RMS_SEON_{}_{}_{}_0x{:02x}.bin".format(sncs[snci], sgs[sgi], pts[3], dac)
                # time.sleep(0.1)
                datad["RMS_SEON_{}_{}_{}_0x{:02x}.bin".format(sncs[snci], sgs[sgi], pts[3], dac)] = self.take_data(sts, snci, sg0, sg1, st0, st1, dac, fp, swdac=0, sdf = 1, pwr_flg=False)
#   DIFF  2*4*1 = 8  {[snc 200/900 mV] * [sg 4.7/7.8/14/25 mV/fC] * [st 2 us]}
        for i in range(8):
            self.chk.adcs_paras[i][2] = 1    # enable differential interface, seems repeat with sdd = 1
        for snci in range(2):
            for sgi in range(4):
                sg0 = sgi % 2
                sg1 = sgi // 2
                for sti in range(4):
                    st0 = sti%2
                    st1 = sti//2
                    fp = datadir + "RMS_DIFF_{}_{}_{}_0x{:02x}.bin".format(sncs[snci], sgs[sgi], pts[3], dac)
                    datad["RMS_DIFF_{}_{}_{}_0x{:02x}.bin".format(sncs[snci], sgs[sgi], pts[3], dac)] = self.take_data(sts, snci, sg0, sg1, st0, st1, dac, fp, swdac=0, sdd = 1, pwr_flg=False)

        fp = datadir + "QC_femb_rms_t5" + ".bin"
        with open(fp, 'wb') as fn:
            pickle.dump(datad, fn)
        print('QC Item Done')


    def femb_adc_sync_pat(self):
        print('QC Item Begin')
        datadir = self.save_dir+"ADC_SYNC_PAT/"
        datad = {}
        try:
            os.makedirs(datadir)
        except OSError:
            print ("Error to create folder %s !!! Continue to next test........"%datadir)
            return

        self.chk.femb_cd_rst()
        self.take_data(autocali=1) #ADC autocalibration once after femb_cd_rst()

        self.sample_N = 10
        fp = datadir + "ADC_SYNC_PAT_SHA_SE.bin"
        datad["ADC_SYNC_PAT_SHA_SE.bin"] = self.take_data(fp=fp, adc_sync_pat=True)

        #self.chk.femb_cd_rst()
        self.sample_N = 10
        fp = datadir + "ADC_SYNC_PAT_SHA_DIFF.bin"
        datad["ADC_SYNC_PAT_SHA_DIFF.bin"] = self.take_data(fp=fp, sdd = 1, adc_sync_pat=True)

        #self.chk.femb_cd_rst()
        self.sample_N = 10
        fp = datadir + "ADC_Test_mode_DC_Noise_SE.bin"
        datad["ADC_Test_mode_DC_Noise_SE.bin"] = self.take_data(fp=fp, adc_sync_pat = True, bypass = True)


        fp = datadir + "QC_femb_adc_sync_pat_t15" + ".bin"
        with open(fp, 'wb') as fn:
            pickle.dump(datad, fn)
        print('QC Item Done')
        # folder_path = datadir
        # output_file = 'femb_adc_sync_pat_merge.bin'
        # datad["ADC_Test_mode_DC_Noise_SE.bin"] = self.merge_bin_files_to_dictbin(folder_path, output_file)   # merge into one bin file

        # self.chk.femb_cd_rst()
        # self.sample_N = 10
        # for i in range(8):
        #     self.chk.adcs_paras[i][1] = 0x30    # adc_sync_mode = 1 + adc_test_mode = 1, bypass SHA
        # fp = datadir + "ADC_SYNC_PAT_noSHA_DIFF.bin"
        # self.take_data(fp=fp, sdd = 1, adc_sync_pat=True)


    def femb_test_pattern_pll(self):
        print('QC Item Begin')
        datad = {}
        datadir = self.save_dir + "PLL_PAT/"
        try:
            os.makedirs(datadir)
        except OSError:
            print ("Error to create folder %s !!! Continue to next test........"%datadir)
            return
        self.chk.femb_cd_rst()

        snc = 1  # 200 mV
        sg0 = 0;        sg1 = 0  # 14mV/fC
        st0 = 1;        st1 = 1  # 2us


        self.chk.set_fe_board(sts=0, snc=snc, sg0=sg0, sg1=sg1, st0=st0, st1=st1, swdac=0, dac=0x00)
        adac_pls_en = 0

        for i in range(0x21, 0x29):
            self.chk.pll = i
            print("PLL value = ", end="");  print(hex(i), end=" "); print("Take TestPattern data")
            self.chk.femb_cd_rst()
            for j in range(8):
                self.chk.adcs_paras[j][8] = 0x02  # set autocali = 2 and PLL mode; it should be set after cd_rst
            cfg_paras_rec = []
            for femb_id in self.fembs:
                self.chk.femb_cfg(femb_id, adac_pls_en)
                cfg_paras_rec.append((femb_id, copy.deepcopy(self.chk.adcs_paras), copy.deepcopy(self.chk.regs_int8), adac_pls_en))

            self.chk.data_align(self.fembs)

            rms_rawdata = self.chk.spybuf_trig(fembs=self.fembs, num_samples=1, trig_cmd=0, TP = True)  # returns list of size 1
            file_name = "Raw_SE_{}_{}_{}_0x{:02x}_{}.bin".format("200mVBL", "14_0mVfC", "2_0us", 0x00, hex(i))
            # begin

            datad[file_name] = [rms_rawdata, cfg_paras_rec, self.fembs]

        fp = datadir + "QC_femb_test_pattern_pll_t16" + ".bin"
        with open(fp, 'wb') as fn:
            pickle.dump(datad, fn)
        print('QC Item Done')

            # fp = datadir + file_name
            # with open(fp, 'wb') as fn:
            #     pickle.dump( [rms_rawdata, cfg_paras_rec, self.fembs], fn)

        # folder_path = datadir
        # output_file = 'femb_test_pattern_pll_merge.bin'
        # self.merge_bin_files_to_dictbin(folder_path, output_file)  # merge into one bin file

            # with open('./TestPattern/rms.dat', 'w') as f:
            #     for data in rms_rawdata:
            #         f.write(str(data))


# item #6
    def femb_CALI_1(self):
        print('QC Item Begin')
        datadir = self.save_dir+"CALI1/"
        datad = {}
        try:
            os.makedirs(datadir)
        except OSError:
            print ("Error to create folder %s !!! Continue to next test........"%datadir)
            return

        snc = 1 # 200 mV BL
        sgs = self.sgs      # self.sgs = ["14_0mVfC", "25_0mVfC", "7_8mVfC", "4_7mVfC" ]
        st0 = 1
        st1 = 1 # 2 us
        sts = 1

        self.chk.femb_cd_rst()
        self.take_data(autocali=1) #ADC autocalibration once after femb_cd_rst()
        self.sample_N = 5

        for sgi in  range(4):
            sg0 = sgi%2
            sg1 = sgi//2
#            time.sleep(5)
            if sg0 ==0 and sg1 == 0: #14mV/fC
                dacstep = 1
            else:
                dacstep = 4
            for dac in range(0,64, dacstep):
                fp = datadir + "CALI1_SE_{}_{}_{}_0x{:02x}.bin".format("200mVBL",sgs[sgi],"2_0us",dac)
                datad["CALI1_SE_{}_{}_{}_0x{:02x}.bin".format("200mVBL",sgs[sgi],"2_0us",dac)] = self.take_data(sts, snc, sg0, sg1, st0, st1, dac, fp, pwr_flg=False)

        #   DIFF
        # self.chk.femb_cd_rst()
        # self.take_data(autocali=1) #ADC autocalibration once after femb_cd_rst()
        fp = datadir + "QC_Cali01_t6" + ".bin"
        with open(fp, 'wb') as fn:
            pickle.dump(datad, fn)
        for i in range(8):
            self.chk.adcs_paras[i][2] = 0
        print('QC Item Done')

    def femb_CALI_2(self):
        print('QC Item Begin')
        datadir = self.save_dir+"CALI2/"
        datad = {}
        try:
            os.makedirs(datadir)
        except OSError:
            print ("Error to create folder %s !!! Continue to next test........"%datadir)
            return

        snc = 0 # 900 mV BL
        sg0 = 0
        sg1 = 0 # 14_0 mv/fC
        st0 = 1
        st1 = 1 # 2 us
        sts = 1

        self.chk.femb_cd_rst()
        self.take_data(autocali=1) #ADC autocalibration once after femb_cd_rst()
        self.sample_N = 5
        for dac in range(0,32,1):
            fp = datadir + "CALI2_SE_{}_{}_{}_0x{:02x}.bin".format("900mVBL","14_0mVfC","2_0us",dac)
            datad["CALI2_SE_{}_{}_{}_0x{:02x}.bin".format("900mVBL","14_0mVfC","2_0us",dac)] = self.take_data(sts, snc, sg0, sg1, st0, st1, dac, fp, pwr_flg=False)

        print('cali2_differential pusle')
        self.chk.femb_cd_rst()
        self.take_data(autocali=1) #ADC autocalibration once after femb_cd_rst()
        cfg_paras_rec = []
        # for i in range(8):
        #     self.chk.adcs_paras[i][2] = 1    # enable differential interface

        self.sample_N = 5
        for dac in range(0,32,4):
            fp = datadir + "CALI2_DIFF_{}_{}_{}_0x{:02x}.bin".format("900mVBL","14_0mVfC","2_0us",dac)
            datad["CALI2_DIFF_{}_{}_{}_0x{:02x}.bin".format("900mVBL","14_0mVfC","2_0us",dac)] = self.take_data(sts, snc, sg0, sg1, st0, st1, dac, fp, sdd = 1, pwr_flg=False)

        fp = datadir + "QC_Cali02_t7" + ".bin"
        with open(fp, 'wb') as fn:
            pickle.dump(datad, fn)
        print('QC Item Done')



    def femb_CALI_3(self):
        print('QC Item Begin')
        datadir = self.save_dir+"CALI3/"
        datad = {}
        try:
            os.makedirs(datadir)
        except OSError:
            print ("Error to create folder %s !!! Continue to next test........"%datadir)
            return

        snc = 1 # 200 mV BL
        sg0 = 0
        sg1 = 0 # 14 mv/fC
        st0 = 1
        st1 = 1 # 2 us
        sts = 1

        self.chk.femb_cd_rst()
        self.take_data(autocali=1) #ADC autocalibration once after femb_cd_rst()
        self.sample_N = 5
        for dac in range(0,64,8):
            fp = datadir + "CALI3_SE_{}_{}_{}_0x{:02x}_sgp1.bin".format("200mVBL","14_0mVfC","2_0us",dac)
            datad["CALI3_SE_{}_{}_{}_0x{:02x}_sgp1.bin".format("200mVBL","14_0mVfC","2_0us",dac)] = self.take_data(sts, snc, sg0, sg1, st0, st1, dac, fp, sgp=1, pwr_flg=False)

        print('cali3_differential pusle')
        self.chk.femb_cd_rst()
        self.take_data(autocali=1) #ADC autocalibration once after femb_cd_rst()

        self.sample_N = 5
        for dac in range(0,64,8):
            fp = datadir + "CALI3_DIFF_{}_{}_{}_0x{:02x}_sgp1.bin".format("200mVBL","14_0mVfC","2_0us",dac)
            datad["CALI3_DIFF_{}_{}_{}_0x{:02x}_sgp1.bin".format("200mVBL","14_0mVfC","2_0us",dac)] = self.take_data(sts, snc, sg0, sg1, st0, st1, dac, fp, sdd = 1, sgp=1, pwr_flg=False)

        fp = datadir + "QC_Cali03_t8" + ".bin"
        with open(fp, 'wb') as fn:
            pickle.dump(datad, fn)
        print('QC Item Done')


    def femb_CALI_4(self):
        print('QC Item Begin')
        datadir = self.save_dir+"CALI4/"
        datad = {}
        try:
            os.makedirs(datadir)
        except OSError:
            print ("Error to create folder %s !!! Continue to next test........"%datadir)
            return

        snc = 0 # 900 mV BL
        sg0 = 0
        sg1 = 0 # 14 mv/fC (we need to adjust the DAC, so the SG0 and SG1 still needed)
        st0 = 1
        st1 = 1 # 2 us
        sts = 1

        self.chk.femb_cd_rst()
        self.take_data(autocali=1) #ADC autocalibration once after femb_cd_rst()
        self.sample_N = 5
        for dac in range(0, 32,4):
            fp = datadir + "CALI4_SE_{}_{}_{}_0x{:02x}_sgp1.bin".format("900mVBL","14_0mVfC","2_0us",dac)
            datad["CALI4_SE_{}_{}_{}_0x{:02x}_sgp1.bin".format("900mVBL","14_0mVfC","2_0us",dac)] = self.take_data(sts, snc, sg0, sg1, st0, st1, dac, fp, sgp=1, pwr_flg=False)

        print('cali4_differential pusle')
        self.chk.femb_cd_rst()
        self.take_data(autocali=1) #ADC autocalibration once after femb_cd_rst()
        cfg_paras_rec = []
        # for i in range(8):
        #     self.chk.adcs_paras[i][2] = 1    # enable differential interface

        self.sample_N = 5
        for dac in range(0,32,4):
            fp = datadir + "CALI4_DIFF_{}_{}_{}_0x{:02x}_sgp1.bin".format("900mVBL","14_0mVfC","2_0us",dac)
            datad["CALI4_DIFF_{}_{}_{}_0x{:02x}_sgp1.bin".format("900mVBL","14_0mVfC","2_0us",dac)] = self.take_data(sts, snc, sg0, sg1, st0, st1, dac, fp, sdd = 1, sgp=1, pwr_flg=False)

        fp = datadir + "QC_Cali04_t9" + ".bin"
        with open(fp, 'wb') as fn:
            pickle.dump(datad, fn)
        print('QC Item Done')

    def femb_CALI_5(self):
        print('QC Item Begin')
        datadir = self.save_dir+"CALI5/"
        datad = {}
        try:
            os.makedirs(datadir)
        except OSError:
            print ("Error to create folder %s !!! Continue to next test........"%datadir)
            return
        snc = 0 # 900 mV BL
        sg0 = 0
        sg1 = 0 # 14_0 mv/fC
        st0 = 1
        st1 = 1 # 2 us
        sts = 1
        dac=0
        self.chk.femb_cd_rst()
        self.take_data(autocali=1) #ADC autocalibration once after femb_cd_rst()
        self.sample_N = 5
        # get baseline
        fp = datadir + "CALI5_SE_{}_{}_{}_RMS.bin".format("900mVBL","14_0mVfC","2_0us")
        datad["CALI5_SE_{}_{}_{}_RMS.bin".format("900mVBL","14_0mVfC","2_0us")] = self.take_data(0, snc, sg0, sg1, st0, st1, dac, fp, swdac=2, pwr_flg=False)
        fp = datadir + "CALI5_SE_{}_{}_{}.bin".format("900mVBL","14_0mVfC","2_0us")
        datad.update(self.take_data(sts, snc, sg0, sg1, st0, st1, dac, fp, swdac=2, pwr_flg=False, excali = True))

        fp = datadir + "QC_Cali05_t13" + ".bin"
        with open(fp, 'wb') as fn:
            pickle.dump(datad, fn)
        print('QC Item Done')

    def femb_CALI_6(self):
        print('QC Item Begin')
        datadir = self.save_dir+"CALI6/"
        datad = {}
        try:
            os.makedirs(datadir)
        except OSError:
            print ("Error to create folder %s !!! Continue to next test........"%datadir)
            return
        snc = 1 # 200 mV BL
        sg0 = 0
        sg1 = 0 # 14_0 mv/fC
        st0 = 1
        st1 = 1 # 2 us
        sts = 1
        dac=0
        self.chk.femb_cd_rst()
        self.take_data(autocali=1) #ADC autocalibration once after femb_cd_rst()
        self.sample_N = 5
        # get baseline
        fp = datadir + "CALI6_SE_{}_{}_{}_RMS.bin".format("200mVBL","14_0mVfC","2_0us")
        datad["CALI6_SE_{}_{}_{}_RMS.bin".format("200mVBL","14_0mVfC","2_0us")] = self.take_data(0, snc, sg0, sg1, st0, st1, dac, fp, swdac=2, pwr_flg=False)
        fp = datadir + "CALI6_SE_{}_{}_{}.bin".format("200mVBL","14_0mVfC","2_0us")
        datad.update(self.take_data(sts, snc, sg0, sg1, st0, st1, dac, fp, swdac=2, pwr_flg=False, excali = True))

        fp = datadir + "QC_Cali06_t14" + ".bin"
        with open(fp, 'wb') as fn:
            pickle.dump(datad, fn)
        print('QC Item Done')

    def femb_MON_1(self, sps=5):
        print('QC Item Begin')
        datadir = self.save_dir+"MON_FE/"
        datad = {}
        if not os.path.exists(datadir):
           try:
               os.makedirs(datadir)
           except OSError:
               print ("Error to create folder %s !!! Continue to next test........"%datadir)
               return

        # 步骤1: 完全复位COLDATA和所有配置
        self.chk.femb_cd_rst(adcspara=True)  # 确保 adcspara=True

        # 步骤2: 显式恢复ADC默认配置
        self.chk.adcs_paras = copy.deepcopy([
            [0x4, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 0],
            [0x5, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 0],
            [0x6, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 0],
            [0x7, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 0],
            [0x8, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 0],
            [0x9, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 0],
            [0xA, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 0],
            [0xB, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 0],
        ])

        # 步骤3: 强制标记需要重新配置ADC
        self.chk.adc_flg = [True, True, True, True]

        # 步骤4: 对所有FEMB重新配置ADC硬件
        for femb_id in self.fembs:
            # print(f"Re-configuring ADC for FEMB{femb_id}...")
            self.chk.femb_adc_cfg(femb_id)

        time.sleep(0.1)  # 等待配置稳定
        # print("ADC configuration reset complete.")
        # ==========================================

        chips = 8
        print ("monitor bandgap reference")
        mon_refs = {}
        for mon_chip in range(chips):
            print ("measure chip#%d of all boards..."%mon_chip)
            adcrst = self.chk.wib_fe_mon(femb_ids=self.fembs, mon_type=2, mon_chip=mon_chip, sps=sps)
            mon_refs[f"chip{mon_chip}"] = adcrst[7]

        print ("monitor temperature")
        mon_temps = {}
        for mon_chip in range(chips):
            print ("measure chip#%d of all boards..."%mon_chip)
            adcrst = self.chk.wib_fe_mon(femb_ids=self.fembs, mon_type=1, mon_chip=mon_chip, sps=sps)
            mon_temps[f"chip{mon_chip}"] = adcrst[7]

        print ("monitor BL 200mV sdf=1")
        mon_200bls_sdf1 = {}
        for mon_chip in range(chips):
            print ("measure chip#%d of all boards..."%mon_chip)
            #for mon_chipchn in range(16):
            for mon_chipchn in [0,8,15]:
                adcrst = self.chk.wib_fe_mon(femb_ids=self.fembs, mon_type=0, snc=1, mon_chip=mon_chip, mon_chipchn=mon_chipchn, sps=sps)
                mon_200bls_sdf1["chip%dchn%02d"%(mon_chip, mon_chipchn)] = adcrst[7]

        print ("monitor BL 200mV sdf=0")
        mon_200bls_sdf0 = {}
        for mon_chip in range(chips):
            print ("measure chip#%d of all boards..."%mon_chip)
            for mon_chipchn in range(16):
                adcrst = self.chk.wib_fe_mon(femb_ids=self.fembs, mon_type=0, snc=1, sdf=0, mon_chip=mon_chip, mon_chipchn=mon_chipchn, sps=sps)
                mon_200bls_sdf0["chip%dchn%02d"%(mon_chip, mon_chipchn)] = adcrst[7]

        print ("monitor BL 900mV sdf=1")
        mon_900bls_sdf1 = {}
        for mon_chip in range(chips):
            print ("measure chip#%d of all boards..."%mon_chip)
            #for mon_chipchn in range(16):
            for mon_chipchn in [0,8,15]:
                adcrst = self.chk.wib_fe_mon(femb_ids=self.fembs, mon_type=0, snc=0, mon_chip=mon_chip, mon_chipchn=mon_chipchn, sps=sps)
                mon_900bls_sdf1["chip%dchn%02d"%(mon_chip, mon_chipchn)] = adcrst[7]

        print ("monitor BL 900mV sdf=0")
        mon_900bls_sdf0 = {}
        for mon_chip in range(chips):
            print ("measure chip#%d of all boards..."%mon_chip)
            for mon_chipchn in range(16):
                adcrst = self.chk.wib_fe_mon(femb_ids=self.fembs, mon_type=0, snc=0, sdf=0, mon_chip=mon_chip, mon_chipchn=mon_chipchn, sps=sps)
                mon_900bls_sdf0["chip%dchn%02d"%(mon_chip, mon_chipchn)] = adcrst[7]

        fp = datadir + "LArASIC_mon_t10.bin"
        with open(fp, 'wb') as fn:
            pickle.dump( [mon_refs, mon_temps, mon_200bls_sdf1, mon_200bls_sdf0, mon_900bls_sdf1, mon_900bls_sdf0, self.logs], fn)
        self.chk.wib_fe_mon(femb_ids=self.fembs)
        print('QC Item Done')

# ============================================================================
    def LArASIC_Analog(self, sps=500):
        print('QC Item Begin')
        #monitor the pulse of LArASIC channel from WIB side
        #self.chk = WIB_CFGS()
        datadir = self.save_dir + "LArASIC_Analog/"
        try:
            os.makedirs(datadir)
        except OSError:
            print("Error to create folder %s !!! Continue to next test........" % datadir)
            return

        self.chk.femb_cd_rst()
        print("monitor pulse 200mV sdf=0")
        for i in range(8):
            self.chk.adcs_paras[i][2] = 1
        self.sample_N = 5
        mon_900bls_sdf0_pulse = {}
        for mon_chip in range(8):
            for mon_chipchn in range(16):
                adcrst = self.chk.wib_fe_mon(femb_ids=self.fembs, adac_pls_en = 1,mon_type=0, snc=1, sdf=0, mon_chip=mon_chip,
                                             mon_chipchn=mon_chipchn, sps=sps, sdd = 1)
                mon_900bls_sdf0_pulse["chip%dchn%02d" % (mon_chip, mon_chipchn)] = adcrst[7]

        print(mon_900bls_sdf0_pulse)

        fp = datadir + "LArASIC_Analog.bin"
        with open(fp, 'wb') as fn:
            pickle.dump([mon_900bls_sdf0_pulse, self.logs], fn)

        for i in range(8):
            self.chk.adcs_paras[i][2] = 0
        print('QC Item Done')

    def femb_MON_2(self, sps=10):
        print('QC Item Begin')
        datadir = self.save_dir+"MON_FE/"
        if not os.path.exists(datadir):
           try:
               os.makedirs(datadir)
           except OSError:
               print ("Error to create folder %s !!! Continue to next test........"%datadir)
               return
        self.chk.femb_cd_rst()
        chips = 8
        print ("monitor LArASIC DAC sgp=1")
        mon_fedacs_sgp1 = {}
        #vdacs=range(64)
        vdacs=range(1,64,8)
        for mon_chip in range(chips):
            print ("measure chip#%d of all boards..."%mon_chip)
            adcrst = self.chk.wib_fe_dac_mon(femb_ids=self.fembs, mon_chip=mon_chip, sgp=True, vdacs=vdacs, sps=sps )
            mon_fedacs_sgp1["CHIP%d_SGP1"%(mon_chip)] = [adcrst, vdacs]

        print ("monitor LArASIC DAC 14 mV/fC")
        mon_fedacs_14mVfC = {}
        vdacs=range(1,64)
        for mon_chip in range(chips):
            print ("measure chip#%d of all boards..."%mon_chip)
            adcrst = self.chk.wib_fe_dac_mon(femb_ids=self.fembs, mon_chip=mon_chip, sgp=False, sg0=0, sg1=0, vdacs=vdacs, sps=sps)
            mon_fedacs_14mVfC["CHIP%d"%(mon_chip)] = [adcrst, vdacs]

        print ("monitor LArASIC DAC 7.8 mV/fC")
        mon_fedacs_7_8mVfC = {}
        #vdacs=range(64)
        vdacs=range(1,64,8)
        for mon_chip in range(chips):
            print ("measure chip#%d of all boards..."%mon_chip)
            adcrst = self.chk.wib_fe_dac_mon(femb_ids=self.fembs, mon_chip=mon_chip, sgp=False, sg0=0, sg1=1, vdacs=vdacs, sps=sps)
            mon_fedacs_7_8mVfC["CHIP%d"%(mon_chip)] = [adcrst, vdacs]

        print ("monitor LArASIC DAC 25 mV/fC")
        mon_fedacs_25mVfC = {}
        #vdacs=range(64)
        vdacs=range(1,64,8)
        for mon_chip in range(chips):
            print ("measure chip#%d of all boards..."%mon_chip)
            adcrst = self.chk.wib_fe_dac_mon(femb_ids=self.fembs, mon_chip=mon_chip, sgp=False, sg0=1, sg1=0, vdacs=vdacs, sps=sps)
            mon_fedacs_25mVfC["CHIP%d"%(mon_chip)] = [adcrst, vdacs]

        fp = datadir + "LArASIC_mon_DAC_t11.bin"
        with open(fp, 'wb') as fn:
            pickle.dump( [mon_fedacs_sgp1, mon_fedacs_14mVfC, mon_fedacs_7_8mVfC, mon_fedacs_25mVfC, self.logs], fn)
        self.chk.wib_fe_mon(femb_ids=self.fembs)
        print('QC Item Done')

    def femb_MON_3(self, sps=5):
        print('QC Item Begin')
        t0 = time.time_ns()
        datadir = self.save_dir+"MON_ADC/"
        if not os.path.exists(datadir):
           try:
               os.makedirs(datadir)
           except OSError:
               print ("Error to create folder %s !!! Continue to next test........"%datadir)
               return

        self.chk.femb_cd_rst()
        self.chk.adcs_paras = copy.deepcopy([ # c_id, data_fmt(0x89), diff_en(0x84), sdc_en(0x80), vrefp, vrefn, vcmo, vcmi
                       [0x4, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 0],
                       [0x5, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 0],
                       [0x6, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 0],
                       [0x7, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 0],
                       [0x8, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 0],
                       [0x9, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 0],
                       [0xA, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 0],
                       [0xB, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 0],
                     ])

        print ("monitor ColdADC reference (default)")
        mon_adc_default = self.chk.wib_adc_mon(femb_ids=self.fembs, sps=sps)

        print ("monitor ColdADC reference")
        vset = [0, 16, 32, 48, 64, 80, 96, 112, 128, 144, 160, 176, 192, 208, 224, 240,255]
        mon_adc=[]
        for i in range(len(vset)):
            for j in range(8):
                self.chk.adcs_paras[j][4]=vset[i]
                self.chk.adcs_paras[j][5]=vset[i]
                self.chk.adcs_paras[j][6]=vset[i]
                self.chk.adcs_paras[j][7]=vset[i]

            mondata = self.chk.wib_adc_mon(femb_ids=self.fembs, sps=sps)
            mon_adc.append([vset[i], mondata])

        fp = datadir + "ColdADC_mon_t12.bin"
        with open(fp, 'wb') as fn:
            pickle.dump( [mon_adc_default, mon_adc, self.logs], fn)
        print('QC Item Done')

if __name__=='__main__':

   if len(sys.argv) < 2:
       print('Please specify at least one FEMB # to test')
       print('Usage: python wib.py 0')
       exit()

   if 'save' in sys.argv:
       save = True
       for i in range(len(sys.argv)):
           if sys.argv[i] == 'save':
               pos = i
               break
       sample_N = int(sys.argv[pos+1] )
       sys.argv.remove('save')
   else:
       save = False
       sample_N = 1

   fembs = [int(a) for a in sys.argv[1:pos]]

   chkout = QC_Runs(fembs, sample_N)
   chkout.pwr_fembs('on')
   chkout.femb_rms()
   chkout.pwr_fembs('off')

