import time
import sys
import numpy as np
import pickle
import copy
import time, datetime, random, statistics    
import os
from dat_cfg import DAT_CFGS
from DAT_user_input import dat_user_input
import argparse
                
dat =  DAT_CFGS()

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
#print ("\033[96m 2: FE response measurement checkout  \033[0m")
#print ("\033[96m 3: FE monitoring measurement  \033[0m")
#print ("\033[96m 4: FE power cycling measurement  \033[0m")
#print ("\033[96m 5: FE noise measurement  \033[0m")
#print ("\033[96m 61: FE calibration measurement (ASIC-DAC)  \033[0m")
#print ("\033[96m 62: FE calibration measurement (DAT-DAC) \033[0m")
#print ("\033[96m 63: FE calibration measurement (Direct-Input) \033[0m")
#print ("\033[96m 7: FE delay run  \033[0m")
#print ("\033[96m 8: FE cali-cap measurement \033[0m")
print ("\033[96m 7: COLDATA EFUSE burn-in \033[0m")
print ("\033[96m 9: Turn DAT on \033[0m")
print ("\033[96m 10: Turn DAT (on WIB slot0) on without any check\033[0m")

ag = argparse.ArgumentParser()
ag.add_argument("-t", "--task", help="which QC tasks to be performed", type=int, choices=[0, 1,2,3,4,5,6,7,9,10],  nargs='+', default=[0,1,2,3,4,5,6,7,9])
args = ag.parse_args()   
tms = args.task

wib_time = datetime.datetime.now().strftime("%m-%d-%Y %H:%M:%S")

tt = []
tt.append(time.time())

if 0 in tms:
    while True:
        print ("\033[92m WIB time: " + wib_time + " \033[0m")
        wibtimechk=input("\033[95m Is time of WIB current ? (Y/N):  \033[0m")
        if ("Y" in wibtimechk) or ("y" in wibtimechk):
            break
        else:
            print ("Please follow these steps to reset WIB time")
            print ("(Windows PC only) open Powershell, type in: ")
            print ("""\033[91m  $cdate = get-date  \033[0m""")
            print ("""\033[91m  $wibdate = "date -s '$cdate'"  \033[0m""")
            print ("""\033[91m  ssh root@192.168.121.1  $wibdate  \033[0m""")
            print ("""\033[91m  password: fpga  \033[0m""")
            print ("Restart this script...")
            exit()
    itemized_flg = False
else:
    itemx = input ("""\033[92m Test item# {}, Y/N? : \033[0m""".format(tms) )
    if ("Y" in itemx) or ("y" in itemx):
        pass
    else:
        print ("\033[91m Exit, please re-choose and restart...\033[0m")
        exit()
    itemized_flg = True

logs = {}
logsd, fdir =  dat_user_input(infile_mode=True,  froot = "./tmp_data/",  itemized_flg=itemized_flg)
if itemized_flg:
    if not os.path.exists(fdir):
        print ("\033[91m Please perform a full test instead of the itemized tests, exit anyway\033[0m")
        exit()

dat.DAT_on_WIBslot = int(logsd["DAT_on_WIB_slot"])
fembs = [dat.DAT_on_WIBslot] 
dat.fembs = fembs
dat.rev = int(logsd["DAT_Revision"])
dat_sn = int(logsd["DAT_SN"])
if dat_sn  == 1:
    Vref = 1.583
if dat_sn  == 2:
    Vref = 1.5738
logs.update(logsd)

#tms=[0]
if 0 not in tms :
    pwr_meas = dat.get_sensors()
    for key in pwr_meas:
        if "FEMB%d"%dat.dat_on_wibslot in key:
            on_f = False
            if ("BIAS_V" in key) and (pwr_meas[key] > 4.5):
                    if ("DC2DC0_V" in key) and (pwr_meas[key] > 3.5):
                            if ("DC2DC1_V" in key) and (pwr_meas[key] > 3.5):
                                    if ("DC2DC2_V" in key) and (pwr_meas[key] > 3.5):
                                            on_f = True
            if (not on_f) and (tms[0] != 9):
                tms = [10] + tms #turn DAT on
                if 9 not in tms:
                    tms = tms + [9] #turn DAT off after testing

####### Init check information #######
if 10 in tms:
    print ("Turn DAT on and wait 10 seconds")
    #set FEMB voltages
    dat.fembs_vol_set(vfe=4.0, vcd=4.0, vadc=4.0)
    dat.femb_powering([dat.dat_on_wibslot])
    dat.data_align_pwron_flg = True
    time.sleep(10)

if 0 in tms:
    print ("Init check after chips are installed")
    datad = {}

    pwr_meas, link_mask, init_f = dat.wib_pwr_on_dat()
    datad["WIB_PWR"] = pwr_meas
    datad["WIB_LINK"] = link_mask
    fes_pwr_info = dat.fe_pwr_meas()
    datad["FE_PWRON"] = fes_pwr_info
    adcs_pwr_info = dat.adc_pwr_meas()
    datad["ADC_PWRON"] = adcs_pwr_info
    cds_pwr_info = dat.dat_cd_pwr_meas()
    datad["CD_PWRON"] = cds_pwr_info
    dat.asic_init_pwrchk(fes_pwr_info, adcs_pwr_info, cds_pwr_info)
    chkdata = dat.dat_asic_chk()
    datad.update(chkdata)

    datad['logs'] = logs

    if not os.path.exists(fdir):
        try:
            os.makedirs(fdir)
        except OSError:
            print ("Error to create folder %s"%save_dir)
            sys.exit()

    fp = fdir + "QC_INIT_CHK" + ".bin"
    with open(fp, 'wb') as fn:
        pickle.dump(datad, fn)

    tt.append(time.time())
    print ("Pass init check, it took %d seconds"%(tt[-1]-tt[-2]))


if 1 in tms:
    print ("COLDATA basic functionality checkout...")
    datad = {}
    datad['logs'] = logs
    
    # dat.femb_cd_rst()    
    #Write to registers to test reset
    dat.femb_cd_cfg(femb_id = dat.fembs[0])


    print ("COLDATA hard reset check")
    dat.dat_cd_hard_reset(femb_id = dat.fembs[0])
    time.sleep(3)
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

    fp = fdir + "QC_BASIC_FUNC" + ".bin"
    with open(fp, 'wb') as fn:
        pickle.dump(datad, fn)
    tt.append(time.time())
    print ("\033[92mCOLDATA basic functionality checkout is done. it took %d seconds   \033[0m"%(tt[-1]-tt[-2]))



if 2 in tms:
    print ("COLDATA primary/secondary swap check")
    datad = {}
    datad['logs'] = logs   
    
    swapdata = dat.dat_cd_order_swap(femb_id = dat.fembs[0])
    datad.update(swapdata)
    
    fp = fdir + "QC_SWAP" + ".bin"
    with open(fp, 'wb') as fn:
        pickle.dump(datad, fn)
    tt.append(time.time())
    print ("\033[92mCOLDATA primary/secondary swap check is done. it took %d seconds   \033[0m"%(tt[-1]-tt[-2]))


if 3 in tms:
    print ("COLDATA power consumption measurement")
    datad = {}
    datad['logs'] = logs      
    
    # Power cycle at least 5 times; measure currents
    # Q: any different configuration for each power cycle? 
    # Reg 0x41 : 0x20, 0x25(RT), 0x26(LN2)
    # LDVDS current set? (reg 0x11)  (0x0, typical[0x2 is default], 0x7)    

    dat.femb_cd_rst()
    time.sleep(1)  
    cfg_info = dat.femb_cd_cfg(dat.fembs[0])
    
    val = 0x20    
    dat.femb_i2c_wrchk(dat.fembs[0], 0x2, 0x5, 0x41, val)
    dat.femb_i2c_wrchk(dat.fembs[0], 0x3, 0x5, 0x41, val)
    cds_pwr_info = dat.dat_cd_pwr_meas()
    datad["BAND_"+hex(val)]= (dat.fembs, cfg_info, cds_pwr_info)
    
    val = 0x25
    dat.femb_i2c_wrchk(dat.fembs[0], 0x2, 0x5, 0x41, val)
    dat.femb_i2c_wrchk(dat.fembs[0], 0x3, 0x5, 0x41, val)
    cds_pwr_info = dat.dat_cd_pwr_meas()
    datad["BAND_"+hex(val)]= (dat.fembs, cfg_info, cds_pwr_info)   
    
    val = 0x26
    dat.femb_i2c_wrchk(dat.fembs[0], 0x2, 0x5, 0x41, val)
    dat.femb_i2c_wrchk(dat.fembs[0], 0x3, 0x5, 0x41, val)
    cds_pwr_info = dat.dat_cd_pwr_meas()
    datad["BAND_"+hex(val)]= (dat.fembs, cfg_info, cds_pwr_info)    

    dat.femb_cd_rst()
    time.sleep(1)  
    cfg_info = dat.femb_cd_cfg(dat.fembs[0])

    val = 0x0
    dat.femb_i2c_wrchk(dat.fembs[0], 0x2, 0x0, 0x11, val)
    dat.femb_i2c_wrchk(dat.fembs[0], 0x3, 0x0, 0x11, val)
    cds_pwr_info = dat.dat_cd_pwr_meas()
    datad["LVDS_CUR_"+hex(val)]= (dat.fembs, cfg_info, cds_pwr_info)
    
    val = 0x2
    dat.femb_i2c_wrchk(dat.fembs[0], 0x2, 0x0, 0x11, val)
    dat.femb_i2c_wrchk(dat.fembs[0], 0x3, 0x0, 0x11, val)
    cds_pwr_info = dat.dat_cd_pwr_meas()
    datad["LVDS_CUR_"+hex(val)]= (dat.fembs, cfg_info, cds_pwr_info) 
 
    val = 0x7
    dat.femb_i2c_wrchk(dat.fembs[0], 0x2, 0x0, 0x11, val)
    dat.femb_i2c_wrchk(dat.fembs[0], 0x3, 0x0, 0x11, val)
    cds_pwr_info = dat.dat_cd_pwr_meas()
    datad["LVDS_CUR_"+hex(val)]= (dat.fembs, cfg_info, cds_pwr_info)
 
    fp = fdir + "QC_PWR" + ".bin"
    with open(fp, 'wb') as fn:
        pickle.dump(datad, fn)
    tt.append(time.time())
    print ("\033[92mCOLDATA power consumption measurement is done. it took %d seconds   \033[0m"%(tt[-1]-tt[-2]))

if 4 in tms:
    print ("COLDATA PLL lock range measurement")
    datad = {}
    datad['logs'] = logs      
    
    # Check the LOCK pin (TP4 or net CD_LOCK) 
    # Scan reg 0x41 from 0x1A to 0x3f. → will look into the data.(CD timestamp should increase) 
    # Bias to 1.2V the locking range may vary.         
    datad['CD1_locked'] = [None for i in range(38)]
    datad['CD2_locked'] = [None for i in range(38)]
    datad['CD_data'] = [None for i in range(38)]
    
    for pll_band in range(0x1a, 0x3f + 1):
        print("PLL band",hex(pll_band))
        dat.femb_i2c_wrchk(dat.fembs[0], 0x2, 0x5, 0x41, pll_band)
        dat.femb_i2c_wrchk(dat.fembs[0], 0x3, 0x5, 0x41, pll_band)
        
        samples=100        
        
        cd1_lock, cd2_lock, cd_sel = dat.dat_cd_are_locked(dat.fembs[0],samples)     
        
        datad['CD1_locked'][pll_band - 0x1a] = cd1_lock
        datad['CD2_locked'][pll_band - 0x1a] = cd2_lock         
        
        rawdata = dat.spybuf_trig(fembs=dat.fembs, num_samples=1, trig_cmd=0, synctries=10) #will return False if data not synced
        datad['CD_data'][pll_band - 0x1a] = rawdata         
    
    #restore to default 
    dat.femb_i2c_wrchk(dat.fembs[0], 0x2, 0x5, 0x41, 0x20)
    dat.femb_i2c_wrchk(dat.fembs[0], 0x3, 0x5, 0x41, 0x20)    
    
    fp = fdir + "QC_LOCK" + ".bin"
    with open(fp, 'wb') as fn:
        pickle.dump(datad, fn)
    tt.append(time.time())
    print ("\033[92mCOLDATA PLL lock range measurement is done. it took %d seconds   \033[0m"%(tt[-1]-tt[-2]))
   
if 5 in tms:
    print ("COLDATA fast command verification")
    datad = {}
    datad['logs'] = logs      
    
    fastcmd_data = dat.dat_cd_fast_cmd_chk(dat.fembs[0])
    datad.update(fastcmd_data)    
    
    fp = fdir + "QC_FASTCMD" + ".bin"
    with open(fp, 'wb') as fn:
        pickle.dump(datad, fn)
    tt.append(time.time())
    print ("\033[92mCOLDATA fast command verification is done. it took %d seconds   \033[0m"%(tt[-1]-tt[-2]))
   
if 6 in tms:
    print ("COLDATA output link verification check")
    datad = {}
    datad['logs'] = logs   
    
    
    datad['LArASIC_pulse'] = []
    datad['ADC_pattern'] = []
    # Scan LVDS current set  (reg 0x11)  (0x0, typical, 0x7)
    dat.femb_cfg(dat.fembs[0])
    dat.cd_flg[dat.fembs[0]]=False #keep subsequent femb_cfg calls from overwriting current setting
    for current in range(0x8):        
        dat.femb_i2c_wrchk(dat.fembs[0], 0x2, 0x0, 0x11, current)
        dat.femb_i2c_wrchk(dat.fembs[0], 0x3, 0x0, 0x11, current)       
        #Verify output links using FRAME 14 
        adac_pls_en, sts, swdac, dac = dat.dat_cali_source(cali_mode=2,asicdac=0x20)
        rawdata, cfg_info = dat.dat_fe_qc(num_samples=5, adac_pls_en=adac_pls_en, sts=sts, swdac=swdac, dac=dac,snc=1,sg0=0, sg1=0, sdd=1)        
        datad['LArASIC_pulse'].append((dat.fembs, rawdata, cfg_info))
        
        # ADC test pattern data, 
        dat.dat_adc_qc_cfg(autocali=0x2)
        rawdata = dat.spybuf_trig(fembs=dat.fembs, num_samples=1, trig_cmd=0)
        datad['ADC_pattern'].append((dat.fembs, rawdata))       
        
        dat.dat_adc_qc_cfg(autocali=0x1) #set adc mode back to default
    
    
    fp = fdir + "QC_OUTPUT" + ".bin"
    with open(fp, 'wb') as fn:
        pickle.dump(datad, fn)
    tt.append(time.time())
    print ("\033[92mCOLDATA output link verification is done. it took %d seconds   \033[0m"%(tt[-1]-tt[-2]))

if 7 in tms:
    print ("COLDATA EFUSE burn-in")
    datad = {}
    datad['logs'] = logs   

    val = 0b11
    cd = "CD1"
    input(cd+" Debug: Press enter if you want to continue burning in value "+hex(val)+" (irreversible)")
    
    efuse_readout = dat.dat_coldata_efuse_prm(dat.fembs[0], cd, val)
    datad[cd] = (val, efuse_readout)
    
    val = 0b1
    cd = "CD2"
    input(cd+" Debug: Press enter if you want to continue burning in value "+hex(val)+" (irreversible)")
    
    efuse_readout = dat.dat_coldata_efuse_prm(dat.fembs[0], cd, val)
    datad[cd] = (val, efuse_readout)
    
    fp = fdir + "QC_EFUSE" + ".bin"
    with open(fp, 'wb') as fn:
        pickle.dump(datad, fn)
    tt.append(time.time())
    print ("\033[92mCOLDATA EFUSE burn-in is done. it took %d seconds   \033[0m"%(tt[-1]-tt[-2]))


if 9 in tms:
    print ("Turn DAT off")
    dat.femb_powering([])
    tt.append(time.time())
    print ("It took %d seconds in total for the entire test"%(tt[-1]-tt[0]))
    print ("\033[92m  please move data in folder ({}) to the PC and perform the analysis script \033[0m".format(fdir))
    print ("\033[92m  Well done \033[0m")


