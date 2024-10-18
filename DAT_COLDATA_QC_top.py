import time
import sys
import numpy as np
import pickle
import copy
import time, datetime, random, statistics    
import os
from dat_cfg import DAT_CFGS
import argparse
from DAT_read_cfg import dat_read_cfg
                
dat =  DAT_CFGS()
froot = "/home/root/BNL_CE_WIB_SW_QC/tmp_data/"

####### Input test information #######
#Red = '\033[91m'
#Green = '\033[92m'
#Blue = '\033[94m'
#Cyan = '\033[96m'
#White = '\033[97m'
#Yellow = '\033[93m'
#Magenta = '\033[95m'
#Grey = '\033[90m'
#Black = '\033[90m'
#Default = '\033[99m'

print ("\033[93m  QC task list   \033[0m")
print ("\033[96m 0: Initilization checkout (not selectable for itemized test item) \033[0m")
print ("\033[96m 1: COLDATA basic functionality checkout  \033[0m")
print ("\033[96m 2: COLDATA primary/secondary swap check  \033[0m")
print ("\033[96m 3: COLDATA power consumption measurement  \033[0m")
print ("\033[96m 4: COLDATA PLL lock range measurement  \033[0m")
print ("\033[96m 5: COLDATA fast command verification  \033[0m")
print ("\033[96m 6: COLDATA output link verification \033[0m")
print ("\033[96m 7: COLDATA EFUSE burn-in \033[0m")
print ("\033[96m 9: Turn DAT off \033[0m")
print ("\033[96m 10: Turn DAT (on WIB slot0) on without any check\033[0m")

ag = argparse.ArgumentParser()
ag.add_argument("-t", "--task", help="which QC tasks to be performed", type=int, choices=[0, 1,2,3,4,5,6,7,9,10],  nargs='+', default=[0,1,2,3,4,5,6,7,9])
args = ag.parse_args()   
tms = args.task

wib_time = datetime.datetime.now().strftime("%m-%d-%Y %H:%M:%S")

tt = []
tt.append(time.time())

logs = {}
logsd, fdir =  dat_read_cfg(infile_mode=True,  froot = froot)

if not os.path.exists(fdir):
    try:
        os.makedirs(fdir)
    except OSError:
        print ("Error to create folder %s"%fdir)
        sys.exit()

dat.DAT_on_WIBslot = int(logsd["DAT_on_WIB_slot"])
fembs = [dat.DAT_on_WIBslot] 
dat.fembs = fembs
dat.rev = int(logsd["DAT_Revision"])
dat_sn = int(logsd["DAT_SN"])

logs.update(logsd)


if dat.rev == 0:
    if dat_sn  == 1:
        dat.fe_cali_vref = 1.583
    if dat_sn  == 2:
        dat.fe_cali_vref = 1.5738
if dat.rev == 1:
    if 'RT' in logs['env']:
        dat.fe_cali_vref = 1.090
    else:
        dat.fe_cali_vref = 1.030 #DAT_SN=3
Vref = dat.fe_cali_vref

#if 100 in tms : #100 is only for itemed testing with power operation 
if True:
    print ("Check DAT power status")
    pwr_meas = dat.get_sensors()
    on_f = True
    for key in pwr_meas:
        if "FEMB%d"%dat.dat_on_wibslot in key:
            if ("BIAS_V" in key) and (pwr_meas[key] < 4.5):
                on_f = False
            if ("DC2DC0_V" in key) and (pwr_meas[key] < 3.5):
                on_f = False
            if ("DC2DC1_V" in key) and (pwr_meas[key] < 3.5):
                on_f = False
            if ("DC2DC2_V" in key) and (pwr_meas[key] < 3.5):
                on_f = False
    if (not on_f) and (tms[0] != 0) : #turn DAT on
        tms = [10] + tms #turn DAT on

####### Init check information #######
if 10 in tms:
    print ("Turn DAT on and wait 5 seconds")
    tt.append(time.time())
    #set FEMB voltages
    dat.fembs_vol_set(vfe=4.0, vcd=4.0, vadc=4.0)
    dat.femb_powering([dat.dat_on_wibslot])
    dat.data_align_pwron_flg = True
    time.sleep(5)
    print ("DAT_Power_On, it took %d seconds"%(tt[-1]-tt[-2]))

if 0 in tms:
    print ("Init check after chips are installed")
    datad = {}
    pwr_meas, link_mask, init_f = dat.wib_pwr_on_dat()
    datad["WIB_PWR"] = pwr_meas
    datad["WIB_LINK"] = link_mask
    if init_f:
        datad["FE_Fail"] = []
        datad["ADC_Fail"] = [] 
        datad["CD_Fail"] = [0,1]
        datad["QCstatus"] = "Code#E001: large current or HS link error when DAT is powered on"
    else:
        fes_pwr_info = dat.fe_pwr_meas()
        datad["FE_PWRON"] = fes_pwr_info
        adcs_pwr_info = dat.adc_pwr_meas()
        datad["ADC_PWRON"] = adcs_pwr_info
        cds_pwr_info = dat.dat_cd_pwr_meas()
        datad["CD_PWRON"] = cds_pwr_info
        warn_flg, febads, adcbads, cdbads = dat.asic_init_pwrchk(fes_pwr_info, adcs_pwr_info, cds_pwr_info)

        if warn_flg:
            datad["QCstatus"] = "Code#E002: Large current of some ASIC chips is observed"
            datad["FE_Fail"] = febads
            datad["ADC_Fail"] = adcbads
            datad["CD_Fail"] = cdbads

        else: #if all chips look good
            warn_flg, febads, adcbads, cdbads = dat.asic_init_por(duts=["CD"])
            if warn_flg:
                datad["FE_Fail"] = febads
                datad["ADC_Fail"] = adcbads
                datad["CD_Fail"] = cdbads
                datad["QCstatus"] = "Code#W003: COLDATA POR is not default, can be ignored"
            else:
                chkdata = dat.dat_asic_chk(duts=logsd['DUT'])
                if chkdata == False:
                    datad["QCstatus"] = "Code#E005: Can't Configurate DAT"
                    febads = []
                    adcbads = []
                    cdbads = []
                    for chip in range(2):
                        cdbads.append(chip)
                    datad["CD_Fail"] = cdbads
                    print ("CD_Fail(0-1):", datad["CD_Fail"])
                else:
                    datad.update(chkdata)
                    datad["QCstatus"] = "Code#W004: To be anlyze at PC side"
    datad['logs'] = logs
    print ("QCstatus:", datad["QCstatus"])

    dat.femb_cd_rst()
    adac_pls_en, sts, swdac, dac = dat.dat_cali_source(cali_mode=3)
    cfg_info = dat.dat_adc_qc_cfg(autocali=0)
    dat.femb_cd_rst()

    fp = fdir + "QC_INIT_CHK" + ".bin"
    with open(fp, 'wb') as fn:
        pickle.dump(datad, fn)

    tt.append(time.time())
    print ("save_fdir_start_%s_end_save_fdir"%fdir)
    print ("save_file_start_%s_end_save_file"%fp)
    print ("Done! Pass! It took %d seconds"%(tt[-1]-tt[-2]))

if 1 in tms:
    print ("COLDATA basic functionality checkout...")
    datad = {}
    datad['logs'] = logs
    
    # dat.femb_cd_rst()    
    #Write to registers to test reset
    dat.femb_cd_cfg(femb_id = dat.fembs[0])

    print ("COLDATA hard reset check")
    dat.dat_cd_hard_reset(femb_id = dat.fembs[0])
    time.sleep(1)
    cds_pwr_info = dat.dat_cd_pwr_meas()
    regerrflg = dat.femb_cd_chkreg(femb_id = dat.fembs[0])
    datad["Post-Hard_Reset"] = [dat.fembs, regerrflg, cds_pwr_info ]
    
    #Write to registers to test reset
    dat.femb_cd_cfg(femb_id = dat.fembs[0])
    
    print ("COLDATA soft reset check")
    #The Soft Reset command has the format of a Write to chip address 0, register page 0, 
    #register address 6: ([00000000][00000110]). The contents of the third byte are unimportant.
    dat.femb_i2c_wr(dat.fembs[0], 0x0, 0x0, 0x6, 0x1) #no need to verify
    time.sleep(1)
    cds_pwr_info = dat.dat_cd_pwr_meas()
    regerrflg = dat.femb_cd_chkreg(femb_id = dat.fembs[0])
    datad["Post-Soft_Reset"] = [dat.fembs, regerrflg, cds_pwr_info ]
    
    #Write to registers to test reset
    dat.femb_cd_cfg(femb_id = dat.fembs[0])    
    
    print ("COLDATA fast reset check") 
    dat.femb_cd_rst()
    time.sleep(1)
    cds_pwr_info = dat.dat_cd_pwr_meas()
    regerrflg = dat.femb_cd_chkreg(femb_id = dat.fembs[0])
    datad["FAST_CMD_Reset"] = [dat.fembs, regerrflg, cds_pwr_info ]
    

    print ("COLDATA GPIO check")
    cntrl_chk = dat.dat_cd_gpio_chk(femb_id = dat.fembs[0])
    datad.update(cntrl_chk)
    
    print ("COLDATA SPI functionality check") 
    spi_config = dat.femb_fe_cfg(femb_id = dat.fembs[0])
    datad["SPI_config"] = spi_config    

    dat.femb_cd_rst()
    adac_pls_en, sts, swdac, dac = dat.dat_cali_source(cali_mode=3)
    cfg_info = dat.dat_adc_qc_cfg(autocali=0)
    dat.femb_cd_rst()

    fp = fdir + "QC_BASIC_FUNC" + ".bin"
    with open(fp, 'wb') as fn:
        pickle.dump(datad, fn)
    tt.append(time.time())
    #print ("\033[92mCOLDATA basic functionality checkout is done. it took %d seconds   \033[0m"%(tt[-1]-tt[-2]))
    print ("save_fdir_start_%s_end_save_fdir"%fdir)
    print ("save_file_start_%s_end_save_file"%fp)
    print ("Done! Pass! It took %d seconds"%(tt[-1]-tt[-2]))


if 2 in tms:
    print ("COLDATA primary/secondary swap check")
    datad = {}
    datad['logs'] = logs   
    
    swapdata = dat.dat_cd_order_swap(femb_id = dat.fembs[0])
    datad.update(swapdata)
    
    dat.femb_cd_rst()
    adac_pls_en, sts, swdac, dac = dat.dat_cali_source(cali_mode=3)
    cfg_info = dat.dat_adc_qc_cfg(autocali=0)
    dat.femb_cd_rst()

    fp = fdir + "QC_SWAP" + ".bin"
    with open(fp, 'wb') as fn:
        pickle.dump(datad, fn)
    tt.append(time.time())
    #print ("\033[92mCOLDATA primary/secondary swap check is done. it took %d seconds   \033[0m"%(tt[-1]-tt[-2]))
    print ("save_fdir_start_%s_end_save_fdir"%fdir)
    print ("save_file_start_%s_end_save_file"%fp)
    print ("Done! Pass! It took %d seconds"%(tt[-1]-tt[-2]))


if 3 in tms:
    print ("COLDATA power cycling measurement")
    cycle_times = 6
    
    datad = {}
    datad['logs'] = logs
    
    for ci in range(cycle_times):
        dat.dat_pwroff_chk(env = logs['env']) #make sure DAT is off
        dat.wib_pwr_on_dat() #turn DAT on
        cseti = ci%8
        adac_pls_en, sts, swdac, dac = dat.dat_cali_source(cali_mode=2,asicdac=0x10)
        cfg_info = dat.dat_fe_qc_cfg(adac_pls_en=adac_pls_en, sts=sts, swdac=swdac, dac=dac)
        if cseti == 0:
            val = 0x20    
            dat.femb_i2c_wrchk(dat.fembs[0], 0x2, 0x5, 0x41, val)
            dat.femb_i2c_wrchk(dat.fembs[0], 0x3, 0x5, 0x41, val)
            key ="BAND_"+hex(val) 
        if cseti == 1:
            val = 0x25
            dat.femb_i2c_wrchk(dat.fembs[0], 0x2, 0x5, 0x41, val)
            dat.femb_i2c_wrchk(dat.fembs[0], 0x3, 0x5, 0x41, val)
            key ="BAND_"+hex(val) 
        if cseti == 2:
            val = 0x26
            dat.femb_i2c_wrchk(dat.fembs[0], 0x2, 0x5, 0x41, val)
            dat.femb_i2c_wrchk(dat.fembs[0], 0x3, 0x5, 0x41, val)
            key ="BAND_"+hex(val) 
        if cseti == 3:
            val = 0x0
            dat.femb_i2c_wrchk(dat.fembs[0], 0x2, 0x0, 0x11, val)
            dat.femb_i2c_wrchk(dat.fembs[0], 0x3, 0x0, 0x11, val)
            key ="LVDS_CUR_"+hex(val) 
        if cseti == 4:
            val = 0x2
            dat.femb_i2c_wrchk(dat.fembs[0], 0x2, 0x0, 0x11, val)
            dat.femb_i2c_wrchk(dat.fembs[0], 0x3, 0x0, 0x11, val)
            key ="LVDS_CUR_"+hex(val) 
        if cseti == 5:
            val = 0x7
            dat.femb_i2c_wrchk(dat.fembs[0], 0x2, 0x0, 0x11, val)
            dat.femb_i2c_wrchk(dat.fembs[0], 0x3, 0x0, 0x11, val)
            key ="LVDS_CUR_"+hex(val) 

        time.sleep(1)
        rawdata = dat.dat_fe_qc_acq(num_samples=1)
    
        fes_pwr_info = dat.fe_pwr_meas()
        adcs_pwr_info = dat.adc_pwr_meas()
        cds_pwr_info = dat.dat_cd_pwr_meas()
    
        datad["PC%d_"%cseti+key] = [dat.fembs, rawdata, cfg_info, fes_pwr_info, adcs_pwr_info, cds_pwr_info]
    
    dat.femb_cd_rst()
    adac_pls_en, sts, swdac, dac = dat.dat_cali_source(cali_mode=3)
    cfg_info = dat.dat_adc_qc_cfg(autocali=0)
    dat.femb_cd_rst()

    fp = fdir + "QC_PWR_CYCLE" + ".bin"
    with open(fp, 'wb') as fn:
        pickle.dump(datad, fn)
    tt.append(time.time())
    print ("save_fdir_start_%s_end_save_fdir"%fdir)
    print ("save_file_start_%s_end_save_file"%fp)
    print ("Done! Pass! it took %d seconds"%(tt[-1]-tt[-2]))

if 4 in tms:
    print ("COLDATA PLL lock range measurement")
    datad = {}
    datad['logs'] = logs      
    
    # Check the LOCK pin (TP4 or net CD_LOCK) 
    # Scan reg 0x41 from 0x1A to 0x3f. → will look into the data.(CD timestamp should increase) 
    # Bias to 1.2V the locking range may vary.        
    datad['CD1_locked'] = [None for i in range(0x40)]
    datad['CD2_locked'] = [None for i in range(0x40)]
    datad['CD_data'] = [None for i in range(0x40)]

    adac_pls_en, sts, swdac, dac = dat.dat_cali_source(cali_mode=3)
    cfg_info = dat.dat_adc_qc_cfg(autocali=2)
    
    for pll_band in range(0x00, 0x3f + 1):
        print("PLL band",hex(pll_band))
        dat.femb_i2c_wrchk(dat.fembs[0], 0x2, 0x5, 0x41, pll_band)
        dat.femb_i2c_wrchk(dat.fembs[0], 0x3, 0x5, 0x41, pll_band)
        mon_datas = dat.dat_cd_mons(mon_type=0x04)
        
        datad['CD1_locked'][pll_band ] = mon_datas["MON_LOCK"][1][0] 
        datad['CD2_locked'][pll_band ] = mon_datas["MON_LOCK"][1][1]        

        if (pll_band >= 0x1d) and (pll_band <= 0x2d) :
            rawdata = dat.spybuf_trig(fembs=dat.fembs, num_samples=1, trig_cmd=0, fastchk=True, synctries=2) #will return False if data not synced
        else:
            rawdata = False
        datad['CD_data'][pll_band] = rawdata         
    
    #restore to default 
    dat.femb_i2c_wrchk(dat.fembs[0], 0x2, 0x5, 0x41, 0x20)
    dat.femb_i2c_wrchk(dat.fembs[0], 0x3, 0x5, 0x41, 0x20)    

    dat.femb_cd_rst()
    adac_pls_en, sts, swdac, dac = dat.dat_cali_source(cali_mode=3)
    cfg_info = dat.dat_adc_qc_cfg(autocali=0)
    dat.femb_cd_rst()
    
    fp = fdir + "QC_LOCK" + ".bin"
    with open(fp, 'wb') as fn:
        pickle.dump(datad, fn)
    tt.append(time.time())
#    print ("\033[92mCOLDATA PLL lock range measurement is done. it took %d seconds   \033[0m"%(tt[-1]-tt[-2]))
    print ("save_fdir_start_%s_end_save_fdir"%fdir)
    print ("save_file_start_%s_end_save_file"%fp)
    print ("Done! Pass! it took %d seconds"%(tt[-1]-tt[-2]))

   
if 5 in tms:
    print ("COLDATA fast command verification")
    datad = {}
    datad['logs'] = logs      
    
    fastcmd_data = dat.dat_cd_fast_cmd_chk(dat.fembs[0])
    datad.update(fastcmd_data)    
    
    dat.femb_cd_rst()       
    adac_pls_en, sts, swdac, dac = dat.dat_cali_source(cali_mode=3)
    cfg_info = dat.dat_adc_qc_cfg(autocali=0)
    dat.femb_cd_rst()

    fp = fdir + "QC_FASTCMD" + ".bin"
    with open(fp, 'wb') as fn:
        pickle.dump(datad, fn)
    tt.append(time.time())
    #print ("\033[92mCOLDATA fast command verification is done. it took %d seconds   \033[0m"%(tt[-1]-tt[-2]))
    print ("save_fdir_start_%s_end_save_fdir"%fdir)
    print ("save_file_start_%s_end_save_file"%fp)
    print ("Done! Pass! it took %d seconds"%(tt[-1]-tt[-2]))

   
if 6 in tms:
    print ("COLDATA output link verification check (current)")
    datad = {}
    datad['logs'] = logs   
    
    dat.femb_cd_rst()       
    adac_pls_en, sts, swdac, dac = dat.dat_cali_source(cali_mode=3)
    cfg_info = dat.dat_adc_qc_cfg(autocali=2)
    if cfg_info == False:
        datad['ADC_pattern_LVDS_CUR_ERROR']= "Fail, can't complete configuration"
    for current in range(0x8):        
        print ('ADC_const_pattern: LVDS_CUR_reg0x11_%d'%current)
        dat.femb_i2c_wrchk(dat.fembs[0], 0x2, 0x0, 0x11, current)
        dat.femb_i2c_wrchk(dat.fembs[0], 0x3, 0x0, 0x11, current)       
        time.sleep(2)
        rawdata = dat.spybuf_trig(fembs=dat.fembs, num_samples=1, trig_cmd=0)
        cds_pwr_info = dat.dat_cd_pwr_meas()
        datad['ADC_pattern_LVDS_CUR_%d'%current]= (dat.fembs, rawdata, cfg_info, cds_pwr_info)
    
    #back to default
    dat.femb_cd_rst()       
    adac_pls_en, sts, swdac, dac = dat.dat_cali_source(cali_mode=3)
    cfg_info = dat.dat_adc_qc_cfg(autocali=0)
    dat.femb_cd_rst()

    fp = fdir + "QC_LVDS_CURs" + ".bin"
    with open(fp, 'wb') as fn:
        pickle.dump(datad, fn)
    tt.append(time.time())
    #print ("\033[92mCOLDATA output link verification is done. it took %d seconds   \033[0m"%(tt[-1]-tt[-2]))
    print ("save_fdir_start_%s_end_save_fdir"%fdir)
    print ("save_file_start_%s_end_save_file"%fp)
    print ("Done! Pass! it took %d seconds"%(tt[-1]-tt[-2]))

if 7 in tms:
    if 'RT' in logs['env']:
        print ("COLDATA EFUSE burn-in")
        datad = {}
        datad['logs'] = logs   
        print("Set U1 (left) as primary")        
        dat.cd_sel = 0
        femb_id=dat.fembs[0]
        dat.femb_i2c_wrchk(femb_id, 0xC, 0, dat.DAT_CD_CONFIG, 0x00)
        dat.femb_cd_rst()       

        cd0_sn = int(datad['logs']['CD0'])&0xffffffff 
        cd1_sn = int(datad['logs']['CD1'])&0xffffffff   
        if cd0_sn >= 0x80000000:
            datad["U1_CD1_SN_Error"] = False 
        elif cd1_sn >= 0x80000000:
            datad["U1_CD2_SN_Error"] = False
        else:
            efuse_readout_u1 = dat.dat_coldata_efuse_prm(femb_id=dat.fembs[0], cd_id="CD1", efuseid=cd0_sn)
            datad["U1_CD1"] = (cd0_sn, efuse_readout_u1)
            efuse_readout_u2 = dat.dat_coldata_efuse_prm(femb_id=dat.fembs[0], cd_id="CD2", efuseid=cd1_sn)
            datad["U2_CD2"] = (cd1_sn, efuse_readout_u2)
        
        fp = fdir + "QC_EFUSE" + ".bin"
        with open(fp, 'wb') as fn:
            pickle.dump(datad, fn)
        tt.append(time.time())
        #print ("\033[92mCOLDATA EFUSE burn-in is done. it took %d seconds   \033[0m"%(tt[-1]-tt[-2]))
        print ("save_fdir_start_%s_end_save_fdir"%fdir)
        print ("save_file_start_%s_end_save_file"%fp)
        print ("Done! Pass! it took %d seconds"%(tt[-1]-tt[-2]))

if 9 in tms:
    print ("Turn DAT off")
    dat.femb_powering([])
    tt.append(time.time())
    print ("It took %d seconds in total for the entire test"%(tt[-1]-tt[0]))
    #print ("\033[92m  please move data in folder ({}) to the PC and perform the analysis script \033[0m".format(fdir))
    #print ("\033[92m  Well done \033[0m")
    print ("DAT_Power_Off, it took %d seconds"%(tt[-1]-tt[-2]))


