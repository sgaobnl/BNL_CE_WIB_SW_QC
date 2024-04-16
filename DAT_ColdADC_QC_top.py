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
print ("\033[96m 1: ADC power cycling measurement  \033[0m")
print ("\033[96m 2: ADC I2C communication checkout  \033[0m")
print ("\033[96m 3: ADC reference voltage measurement  \033[0m")
print ("\033[96m 4: ADC autocalibration check  \033[0m")
print ("\033[96m 5: ADC open channel noise measurement  \033[0m")
print ("\033[96m 6: ADC DNL/INL measurement  \033[0m")
print ("\033[96m 7: ADC overflow check  \033[0m")
print ("\033[96m 8: ADC ENOB measurement \033[0m")
print ("\033[96m 9: ADC ring oscillator frequency readout \033[0m")
print ("\033[96m 10: ADC gain test \033[0m")
print ("\033[96m 11: Turn DAT off \033[0m")
print ("\033[96m 12: Turn DAT (on WIB slot0) on without any check\033[0m")

ag = argparse.ArgumentParser()
ag.add_argument("-t", "--task", help="which QC tasks to be performed", type=int, choices=[0, 1,2,3,4,5,6,7,8,9,10,11,12],  nargs='+', default=[0,1,2,3,4,5,6,7,8,9,10,11])
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

#Possibly put DAT version in a DAT register that we can peek?
dat_revision = 0 # 0 = old dat

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
            if (not on_f) and (tms[0] != 11):
                tms = [11] + tms #turn DAT on
                if 11 not in tms:
                    tms = tms + [11] #turn DAT off after testing

####### Init check information #######
if 12 in tms:
    print ("Turn DAT on and wait 10 seconds")
    #set FEMB voltages
    dat.fembs_vol_set(vfe=4.0, vcd=4.0, vadc=4.0)
    dat.femb_powering([dat.dat_on_wibslot])
    dat.data_align_pwron_flg = True
    time.sleep(10)
    
if 0 in tms:
    print ("Init check after chips are installed")
    datad = {}

    pwr_meas, link_mask = dat.wib_pwr_on_dat()
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
    print ("FE mapping to be done")
    print ("FE mapping to be done")
    print ("FE mapping to be done")
    print ("FE mapping to be done")
    print ("FE mapping to be done")
    
    #Monitor reference voltages
    datad_mons = dat.dat_adc_mons(mon_type=0x3c)  
    passf = True
    for onekey in datad_mons.keys():
        if dat.adc_refv_chk({onekey:datad_mons[onekey]}): #warn_flag == True
            print(onekey+": FAIL")
            datad_mons[onekey].append("FAIL")
            passf = False
        else:
            pass
            datad_mons[onekey].append("PASS")
            #print(onekey+": PASS")
    datad.update(datad_mons)
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
    if passf:
        print ("\033[92mPass init check, it took %d seconds \033[0m"%(tt[-1]-tt[-2]))
    else:
       print ("\033[91mFail init check, it took %d seconds \033[0m"%(tt[-1]-tt[-2])) 
    
    
###



if 1 in tms: #if "cycling_placeholder" in tms:
    print ("\033[95mADC power cycling measurement starts...\033[0m")
    cycle_times = 6
    
    datad = {}
    datad['logs'] = logs
    

    adcs_addr=[0x08,0x09,0x0A,0x0B,0x04,0x05,0x06,0x07] 
    
    for ci in range(cycle_times):
        dat.dat_pwroff_chk(env = logs['env']) #make sure DAT is off
        dat.wib_pwr_on_dat() #turn DAT on
        adac_pls_en, sts, swdac, dac = dat.dat_cali_source(cali_mode=2,asicdac=0x20)
        
        cseti = ci%4   


        
        if cseti == 0: #SDC off(bypass), DB(bypass), SE : Regaddr0x80[1:0] = b”11” [por default], regaddr0x84[3]=b’1’ (diff_en = 0, sdc_en = 0)
            # cfg_info = dat.dat_adc_qc_cfg(diff_en=0, sdf_en=0,adac_pls_en=1)   
            diff_en = 0
            sdf_en = 0

            # rawdata, cfg_info = dat.dat_fe_qc(adac_pls_en=adac_pls_en, sts=sts, swdac=swdac, dac=dac)
        if cseti == 1: #SDC off(bypass), DB(bypass), DIFF : Regaddr0x80[1:0] = b”11”[por default], regaddr0x84[3]=b’0’ (diff_en = 1)
            # cfg_info = dat.dat_adc_qc_cfg(diff_en=1, sdf_en=0,adac_pls_en=1)
            diff_en = 1
            sdf_en = 0
            # rawdata, cfg_info = dat.dat_fe_qc(adac_pls_en=adac_pls_en, sts=sts, swdac=swdac, dac=dac)
        #Skipping this config because datasheet says not to do it:
        # if cseti == 2: #SDC on, DB on, SE:  Regaddr0x80[1:0] = b”00” (must set manually), regaddr0x84[3]=b’1’ (diff_en = 0)
            # cfg_info = dat.dat_adc_qc_cfg(diff_en=0, sdf_en=0)
            # wrdata = 0xe0 #turns on both buffers and directs currents from cmos reference to the buffer
            # for chip in range(0x8):
                # self.femb_i2c_wrchk(femb_id=dat.dat_on_wibslot, chip_addr=adcs_addr[chip], reg_page=1, reg_addr=0x80, wrdata=wrdata)                
            # rawdata = dat.dat_adc_qc_acq()        
        if cseti == 2: #SDC on, DB off, SE:  Regaddr0x80[1:0] = b”10”, regaddr0x84[3]=b’1’ (sdc_en = 1, diff_en = 0)
            # cfg_info = dat.dat_adc_qc_cfg(diff_en=0, sdf_en=1,adac_pls_en=1)
            diff_en = 0
            sdf_en = 1
            # rawdata, cfg_info = dat.dat_fe_qc(adac_pls_en=adac_pls_en, sts=sts, swdac=swdac, dac=dac)
        if cseti == 3: #SDC off, DB on, DIFF:  Regaddr0x80[1:0] = b”01”(must set manually), regaddr0x84[3]=b’0’ [por default]
            # cfg_info = dat.dat_adc_qc_cfg(diff_en=1, sdf_en=0,adac_pls_en=1)
            diff_en = 1
            sdf_en = 0

             
            # rawdata, cfg_info = dat.dat_fe_qc(adac_pls_en=adac_pls_en, sts=sts, swdac=swdac, dac=dac)
        for adc_no in range(0x8):
            dat.adcs_paras[adc_no][2] = diff_en
            dat.adcs_paras[adc_no][3] = sdf_en
        
        cfg_info = dat.dat_fe_qc_cfg(adac_pls_en=adac_pls_en, sts=sts, swdac=swdac, dac=dac)                    
        if cseti == 3:
            wrdata = 0xA1 #turns on diff buffer and directs currents from cmos reference to the buffer
            # wrdata = 0x1
            # wrdata = 0x91
            for chip in range(0x8):
                dat.femb_i2c_wrchk(femb_id=dat.dat_on_wibslot, chip_addr=adcs_addr[chip], reg_page=1, reg_addr=0x80, wrdata=wrdata)
                
        if cseti == 2 or cseti == 3:
            wrdata = 0x33 #turns on diff buffer and directs currents from cmos reference to the buffer
            for chip in range(0x8):
                dat.femb_i2c_wrchk(femb_id=dat.dat_on_wibslot, chip_addr=adcs_addr[chip], reg_page=1, reg_addr=0x84, wrdata=wrdata) 
                
        if diff_en or sdf_en:
            for chip in range(0x8):
                for reg_addr in [0x8f, 0x90, 0x91, 0x92]:
                    dat.femb_i2c_wrchk(femb_id=dat.dat_on_wibslot, chip_addr=adcs_addr[chip], reg_page=1, reg_addr=reg_addr, wrdata=0x99)
        # if sdf_en:
            # wrdata = 0x42
            # for chip in range(0x8):
                # dat.femb_i2c_wrchk(femb_id=dat.dat_on_wibslot, chip_addr=adcs_addr[chip], reg_page=1, reg_addr=0x80, wrdata=wrdata)            
        
        for chip in range(0x8):
            print("\033[95m  ADC%d  \033[0m"%(chip))
            print ("\033[95m  cseti="+str(cseti)+"   \033[0m")  
            reg80 = dat.femb_i2c_rd(femb_id=dat.dat_on_wibslot, chip_addr=adcs_addr[chip], reg_page=1, reg_addr=0x80)
            reg84 = dat.femb_i2c_rd(femb_id=dat.dat_on_wibslot, chip_addr=adcs_addr[chip], reg_page=1, reg_addr=0x84)
            reg8f = dat.femb_i2c_rd(femb_id=dat.dat_on_wibslot, chip_addr=adcs_addr[chip], reg_page=1, reg_addr=0x8f)
            reg90 = dat.femb_i2c_rd(femb_id=dat.dat_on_wibslot, chip_addr=adcs_addr[chip], reg_page=1, reg_addr=0x90)
            reg91 = dat.femb_i2c_rd(femb_id=dat.dat_on_wibslot, chip_addr=adcs_addr[chip], reg_page=1, reg_addr=0x91)
            reg92 = dat.femb_i2c_rd(femb_id=dat.dat_on_wibslot, chip_addr=adcs_addr[chip], reg_page=1, reg_addr=0x92)
            
            print ("\033[95m  0x80="+hex(reg80)+"   \033[0m")
            print ("\033[95m  0x84="+hex(reg84)+"   \033[0m")
            print ("\033[95m  0x8f="+hex(reg8f)+"   \033[0m") 
            print ("\033[95m  0x90="+hex(reg90)+"   \033[0m") 
            print ("\033[95m  0x91="+hex(reg91)+"   \033[0m") 
            print ("\033[95m  0x92="+hex(reg92)+"   \033[0m") 
        
        rawdata = dat.dat_adc_qc_acq()      

        
        fes_pwr_info = dat.fe_pwr_meas()
        adcs_pwr_info = dat.adc_pwr_meas()
        cds_pwr_info = dat.dat_cd_pwr_meas()
        
        datad["PwrCycle_%d"%cseti] = [dat.fembs, rawdata, cfg_info, fes_pwr_info, adcs_pwr_info, cds_pwr_info]
               

    fp = fdir + "QC_PWR_CYCLE" + ".bin"
    with open(fp, 'wb') as fn:
        pickle.dump(datad, fn)
    tt.append(time.time())
    print ("\033[92mADC power cycling measurement is done. it took %d seconds   \033[0m"%(tt[-1]-tt[-2]))
        
if 2 in tms:#if "i2c_placeholder" in tms:
    print ("\033[95mI2C communication test starts...   \033[0m")
    datad = {}
    datad['logs'] = logs

    #Check power-on reset
    dat.dat_pwroff_chk(env = logs['env']) #make sure DAT is off
    dat.wib_pwr_on_dat() #turn DAT on    
    error = dat.femb_adc_chkreg(dat.dat_on_wibslot)
    
    if error:
        print("\033[91mPOR reg check failed.   \033[0m")
        #read all registers and save values?
        reg_addr1=range(0x80,0xB3)
        reg_addr2=range(1,5)
        
        adcs_rdregs = [[[],[]] for adc_no in range(8)] 
        for adc_no in range(8):
            c_id = dat.adcs_paras[adc_no][0]

            reg_page=1
            nreg=0
            for reg_addr in reg_addr1:
                rdreg = dat.femb_i2c_rd(dat.dat_on_wibslot, c_id, reg_page, reg_addr)
                #defreg = reg_dval1[nreg]
                nreg = nreg+1
                # if rdreg!=defreg:
                   # print("ERROR: femb {} chip {} ADC page_reg={} reg_addr={} read value({}) is not default({})".format(femb_id, c_id, hex(reg_page), hex(reg_addr),hex(rdreg),hex(defreg)))
                   # hasERROR = True
                adcs_rdregs[adc_no][0].append(rdreg)   
    
            reg_page=2
            nreg=0
            for reg_addr in reg_addr2:
                rdreg = dat.femb_i2c_rd(dat.dat_on_wibslot, c_id, reg_page, reg_addr)
                # defreg = reg_dval2[nreg]
                nreg = nreg+1
                # if rdreg!=defreg:
                   # print("ERROR: femb {} chip {} ADC page_reg={} reg_addr={} read value({}) is not default({})".format(femb_id, c_id, hex(reg_page), hex(reg_addr),hex(rdreg),hex(defreg)))
                   # hasERROR = True        
                adcs_rdregs[adc_no][1].append(rdreg) 
        #Store registers
        datad['POR_CHKREG_FAIL'] = adcs_rdregs
    else:
        datad['POR_CHKREG_FAIL'] = None
    
    #Write/read registers
    ## What values to check for test write? What is safe?
    ## Save failed reads info in datad
    
    fp = fdir + "QC_I2C_COMM" + ".bin"
    with open(fp, 'wb') as fn:
        pickle.dump(datad, fn)
    tt.append(time.time())
    print ("\033[92mADC I2C communication check is done. it took %d seconds   \033[0m"%(tt[-1]-tt[-2]))
    

if 3 in tms:#if "refv_placeholder" in tms:
    
    print ("\033[95mADC monitoring measurement starts...   \033[0m")
    data = {}
    data['logs'] = logs   
    cfg_info = dat.dat_adc_qc_cfg()
    time.sleep(1)
        
    #measure default outputs of VREFP, VREFN, VCMI, VCMO
    data.update(dat.dat_adc_mons(mon_type=0x3c))
    
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
        cfg_info = dat.dat_adc_qc_cfg(vrefp=dac, vrefn=dac, vcmo=dac, vcmi=dac)
        # refv_dacs[dac] = dat.dat_adc_mons(mon_type=0x3c)
        refv_dacs.append(dat.dat_adc_mons(mon_type=0x3c))
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

    
    #In a well-behaved DAC where superposition holds, these tests should be sufficient to verify
    #the static performance.
    data["refv_dacs"] = refv_dacs
    #Use ^ for DNL/INL
    
    #return voltages to normal
    cfg_info = dat.dat_adc_qc_cfg() 
    
    #Check the current monitors
    imons = {}
    for imon_select in range(0x8):
        adcs_addr=[0x08,0x09,0x0A,0x0B,0x04,0x05,0x06,0x07]  
        #turn on and select current monitor
        for chip in range(0x8):
            dat.femb_i2c_wrchk(femb_id=dat.dat_on_wibslot, chip_addr=adcs_addr[chip], reg_page=1, reg_addr=0xaf, wrdata=(imon_select<<5)|0x02)
        
    
        imon_datas = dat.dat_adc_mons(mon_type=0x2)["MON_Imon"]
        #Add current (mA) calculation to dict
        imon_datas.append(np.array(imon_datas[1])/dat.imon_R)
        imons[dat.adc_imon_sel[imon_select]] = imon_datas        
    data['Imons'] = imons    
    
    fp = fdir + "QC_REFV" + ".bin"
    with open(fp, 'wb') as fn:
        pickle.dump(data, fn)    
    tt.append(time.time())
    print ("\033[92mADC monitoring measurement is done. it took %d seconds   \033[0m"%(tt[-1]-tt[-2]))        
    
if 4 in tms:#if "autocali_placeholder" in tms:
    print ("\033[95mADC autocalibration check starts...   \033[0m")
    
    datad = {}
    datad['logs'] = logs
    
    #Perform autocalibration
    cfg_info = dat.dat_adc_qc_cfg() 
    
    #Check weights   
    datad['weights'] = []
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
                    weight_lsb = dat.femb_i2c_rd(dat.dat_on_wibslot, adcs_addr[chip], 0x1, weight_lsb_addr)
                    weight_msb = dat.femb_i2c_rd(dat.dat_on_wibslot, adcs_addr[chip], 0x1, weight_msb_addr)
                    weight_16b = (weight_msb << 8) | weight_lsb
                    stage_weights.append(weight_16b)
                adc_weights.append(stage_weights)
            chip_weights.append(adc_weights)
        datad['weights'].append(chip_weights)
        
    fp = fdir + "QC_AUTOCALI" + ".bin"
    with open(fp, 'wb') as fn:
        pickle.dump(datad, fn)    
    tt.append(time.time())
    print ("\033[92mADC autocalibration check is done. it took %d seconds   \033[0m"%(tt[-1]-tt[-2]))   
    
if 5 in tms:#if "noise_placeholder" in tms:
    print ("\033[95mADC open channel noise measurement starts...   \033[0m")
    
    datad = {}
    datad['logs'] = logs  

    
    measure_mode = "fe_dc"
    
    datad["fembs"] = dat.fembs
    
    # if measure_mode == "fe_dc": #Measure DC from LArASIC #200 mv and 900 mV
        # adac_pls_en, sts, swdac, dac = dat.dat_cali_source(cali_mode=0)
          
    dat.cdpoke(dat.dat_on_wibslot, 0xC, 0, dat.DAT_ADC_SRC_CS_P_MSB, 0xFF) 
    dat.cdpoke(dat.dat_on_wibslot, 0xC, 0, dat.DAT_ADC_SRC_CS_P_LSB, 0xFF)     
    # cfg_info = dat.dat_fe_qc_cfg(adac_pls_en=0, sts=1, swdac=1, dac=1, snc=0) #900mV
    datad['FE_DC_900mV'], datad['900mV_cfg'] = dat.dat_fe_qc(adac_pls_en=0, sts=1, swdac=1, dac=0x5, snc=0, num_samples=10) #900mV
    datad['FE_DC_200mV'], datad['200mV_cfg'] = dat.dat_fe_qc(adac_pls_en=0, sts=1, swdac=1, dac=0x5, snc=1, num_samples=10) #200mV
    print("len of FE_DC_900mV",len(datad['FE_DC_900mV']))
    # elif measure_mode == "open_ch": #Measure open channel noise (but there is 8 channels tied together)
    dat.cdpoke(dat.dat_on_wibslot, 0xC, 0, dat.DAT_ADC_SRC_CS_P_MSB, 0x0) 
    dat.cdpoke(dat.dat_on_wibslot, 0xC, 0, dat.DAT_ADC_SRC_CS_P_LSB, 0x0) 
    dat.cdpoke(dat.dat_on_wibslot, 0xC, 0, dat.DAT_ADC_TEST_IN_SEL, 0x0)
    dat.cdpoke(dat.dat_on_wibslot, 0xC, 0, dat.DAT_ADC_PN_TST_SEL, 0x67) #connect P and N to different open sources?
    datad['open_adc_cfg'] = dat.dat_adc_qc_cfg()
    datad['Mux_open'] = dat.dat_adc_qc_acq(num_samples=10)
    
    fp = fdir + "QC_RMS" + ".bin"
    with open(fp, 'wb') as fn:
        pickle.dump(datad, fn)

    tt.append(time.time())        
    print ("\033[92mADC open channel noise measurement is done. it took %d seconds   \033[0m"%(tt[-1]-tt[-2])) 
    
if 6 in tms:
    print ("\033[95mADC DNL/INL measurement starts...   \033[0m")
    
    datad = {}
    datad['logs'] = logs  
    
    cfg_info = dat.dat_adc_qc_cfg() 
    
    #Assuming slow ramp config
    #Replace these or input them in DAT_user_input.py as necessary:
    datad['fembs'] = dat.fembs
    # datad['waveform'] = 'SINE' 
    datad['waveform'] = 'RAMP'
    datad['source'] = 'DAT_P6'
    # datad['source'] = 'WIB'
    # datad['freq'] = 1000 # Hz
    datad['freq'] = 1 # Hz
    datad['voltage_low'] = -0.1 # Vpp
    datad['voltage_high'] = 2.5
    # datad['offset'] = 1 #V    
    datad['num_samples'] = 2000000
    
    dat.sig_gen_config(datad['waveform'], datad['freq'], datad['voltage_low'], datad['voltage_high']) 
    
    dat.dat_coldadc_ext(ext_source=datad['source'])
    # input("Scope U91 top left pin")
    datad['rawdata'] = dat.dat_adc_qc_acq() #trigger readout
    datad['histdata'] = dat.dat_adc_histbuf_trig(num_samples=datad['num_samples'], waveform=datad['waveform'])  

    dat.sig_gen_config()
    
    fp = fdir + "QC_DNL_INL" + ".bin"
    with open(fp, 'wb') as fn:
        pickle.dump(datad, fn)

    tt.append(time.time())        
    print ("\033[92mADC DNL/INL measurement is done. it took %d seconds   \033[0m"%(tt[-1]-tt[-2])) 
    
if 7 in tms:#if "overflow_placeholder" in tms:
    print ("\033[95mADC overflow check starts...   \033[0m")
    
    datad = {}
    datad['logs'] = logs  
    
    cfg_info = dat.dat_adc_qc_cfg()  


    #take data for underflow
    ##tie ADC to gnd
    # dat.cdpoke(dat.dat_on_wibslot, 0xC, 0, dat.DAT_ADC_SRC_CS_P_MSB, 0x0) 
    # dat.cdpoke(dat.dat_on_wibslot, 0xC, 0, dat.DAT_ADC_SRC_CS_P_LSB, 0x0) 
    # dat.cdpoke(dat.dat_on_wibslot, 0xC, 0, dat.DAT_ADC_TEST_IN_SEL, 0x0)  
    # # dat.cdpoke(dat.dat_on_wibslot, 0xC, 0, dat.DAT_ADC_PN_TST_SEL, 0x0)
    # dat.cdpoke(dat.dat_on_wibslot, 0xC, 0, dat.DAT_ADC_PN_TST_SEL, 0x33)
    dat.dat_set_dac(0x0, adc=0)  #Set ADCP to 0
    dat.dat_set_dac(0xFFFF, adc=1)  #give ADCN a positive voltage   
    # import pyvisa  
    # rm = pyvisa.ResourceManager()    
    # sigconfig_done = False
    # while not sigconfig_done:
        # try:
            # sig_gen = rm.open_resource('TCPIP::192.168.121.10::INSTR')
            # print(sig_gen.query("*IDN?"))
            # sig_gen.write("FUNCTION DC")
            # sig_gen.write("VOLTAGE:OFFSET -2.5V")
            # sig_gen.write("OUTP ON")
            # sigconfig_done = True
            # print("Successfully configured signal generator")
        # except:
            # print("Error configuring signal generator. Trying again...")
            # sigconfig_done = False
        
        # sig_gen.close()

    
    # dat.dat_coldadc_ext(ext_source='DAT_P6')
    dat.dat_coldadc_cali_cs(mode="DIFF")
        
    
    # input("Probe DACs - underflow")
    print(hex(dat.peek(0xa00c00f0) >> 10))
    datad['rawdata_under'] = dat.dat_adc_qc_acq(num_samples = 20) 
    
    # sig_gen = rm.open_resource('TCPIP::192.168.121.10::INSTR')
    # sig_gen.write("OUTP OFF")
    # sig_gen.close()

    
    #take data for overflow
    # ##tie ADC P  to DAT PDAC set to max
    # # dat.cdpoke(dat.dat_on_wibslot, 0xC, 0, dat.DAT_ADC_SRC_CS_P_MSB, 0x0) 
    # # dat.cdpoke(dat.dat_on_wibslot, 0xC, 0, dat.DAT_ADC_SRC_CS_P_LSB, 0x0) 
    # # dat.cdpoke(dat.dat_on_wibslot, 0xC, 0, dat.DAT_ADC_TEST_IN_SEL, 0x0)  
    # # # dat.cdpoke(dat.dat_on_wibslot, 0xC, 0, dat.DAT_ADC_PN_TST_SEL, 0x0)    
    # dat.cdpoke(dat.dat_on_wibslot, 0xC, 0, dat.DAT_ADC_PN_TST_SEL, 0x33)
    dat.dat_coldadc_cali_cs(mode="DIFF")
    dat.dat_set_dac(0xFFFF, adc=0)
    dat.dat_set_dac(0x0, adc=1)
    # input("Probe DACs - overflow")
    print(hex(dat.peek(0xa00c00f0) >> 10))
    datad['rawdata_over'] = dat.dat_adc_qc_acq(num_samples = 20) 
    
    dat.dat_set_dac(0x0, adc=0) #set ADC PDAC back to 0
    dat.dat_set_dac(0x0, adc=1) #set ADC NDAC back to 0
    
    fp = fdir + "QC_OVERFLOW" + ".bin"
    with open(fp, 'wb') as fn:
        pickle.dump(datad, fn)

    tt.append(time.time())        
    print ("\033[92mADC overflow check is done. it took %d seconds   \033[0m"%(tt[-1]-tt[-2])) 
    
if 8 in tms:#if "enob_placeholder" in tms:
    print ("\033[95mADC ENOB measurement starts...   \033[0m")
    
    datad = {}
    datad['logs'] = logs 
    
    datad['num_samples'] = 16384
    #Replace these or input them in DAT_user_input.py as necessary:
    datad['sine_freq'] = 1000 #Hz
    datad['sine_low'] = 0.2 # V
    datad['sine_high'] = 1.3 #V
    datad['source'] = 'DAT_P6'
    # datad['source'] = 'WIB'    
    
    dat.sig_gen_config("SINE", datad['sine_freq'], datad['sine_low'],  datad['sine_high'])
        
    dat.dat_coldadc_ext(ext_source=datad['source'])
    cfg_info = dat.dat_adc_qc_cfg() 
    datad['raw_spybuf'] = dat.dat_adc_qc_acq() #trigger readout, save in case of issue
    datad['rawdata'] = dat.dat_enob_acq()
    
    dat.sig_gen_config()
    
    fp = fdir + "QC_ENOB" + ".bin"
    with open(fp, 'wb') as fn:
        pickle.dump(datad, fn)

    tt.append(time.time())        
    print ("\033[92mADC enob measurement is done. it took %d seconds   \033[0m"%(tt[-1]-tt[-2])) 
    
if 9 in tms:#if "ringosc_placeholder" in tms:
    print ("\033[95mADC ring oscillator frequency readout starts...   \033[0m")
    
    datad = {}
    datad['logs'] = logs     
    
    datad['ring_osc_freq'] = []
    
    adcs_addr=[0x08,0x09,0x0A,0x0B,0x04,0x05,0x06,0x07] 
    
    for chip in range(8): #turn ring osc output on
    # for chip in range(7,-1,-1): #reverse order
        # print(dat.cdpeek(0, adcs_addr[chip], 1, 0xAA))
        dat.femb_i2c_wrchk(0, adcs_addr[chip], 1, 0xAA, 0x1)
        # print(dat.cdpeek(0, adcs_addr[chip], 1, 0xAA))
    # input("Trigger readout")    
    for seconds in range(10):    
        time.sleep(1) #Allow DAT ro counters to count number of pulses in 1 second
        print(seconds+1,"seconds:")
        for chip in range(8):       
            dat.cdpoke(0, 0xC, 0, dat.DAT_SOCKET_SEL, chip)
            byte3 = dat.cdpeek(0, 0xC, 0, dat.DAT_ADC_RING_OSC_COUNT_B3)
            byte2 = dat.cdpeek(0, 0xC, 0, dat.DAT_ADC_RING_OSC_COUNT_B2)
            byte1 = dat.cdpeek(0, 0xC, 0, dat.DAT_ADC_RING_OSC_COUNT_B1)
            byte0 = dat.cdpeek(0, 0xC, 0, dat.DAT_ADC_RING_OSC_COUNT_B0)
            
            freq = (byte3 << 8*3) | (byte2 << 8*2) | (byte1 << 8*1) | byte0
            print((freq/1000000)," MHz")
            datad['ring_osc_freq'].append(freq)
            # dat.cdpoke(0,  adcs_addr[chip], 1, 0xAA, 0x0)
        
    
    fp = fdir + "QC_RINGO" + ".bin"
    with open(fp, 'wb') as fn:
        pickle.dump(datad, fn)

    tt.append(time.time())        
    print ("\033[92mADC ring oscillator frequency readout is done. it took %d seconds   \033[0m"%(tt[-1]-tt[-2])) 

if 10 in tms:
    print ("\033[95mADC gain test starts...   \033[0m")
    
    datad = {}
    datad['logs'] = logs  

    datad['num_samples'] = 16384
    #Replace these or input them in DAT_user_input.py as necessary:
    datad['ramp_freq'] = 200 #Hz
    datad['ramp_low'] = 0 # V
    datad['ramp_high'] = 2 #V
    datad['ramp_high'] = 2 #V
    datad['source'] = 'DAT_P6'
    # datad['source'] = 'WIB'    
    
    dat.sig_gen_config("RAMP", datad['ramp_freq'], datad['ramp_low'],  datad['ramp_high'])    
    dat.dat_coldadc_ext(ext_source=datad['source'])
    cfg_info = dat.dat_adc_qc_cfg() 

    datad['raw_spybuf'] = dat.dat_adc_qc_acq() #trigger readout, save in case of issue
    datad['rawdata'] = dat.dat_enob_acq()    

    dat.sig_gen_config()
    
    fp = fdir + "QC_GAIN" + ".bin"
    with open(fp, 'wb') as fn:
        pickle.dump(datad, fn)

    tt.append(time.time())        
    print ("\033[92mADC gain measurement is done. it took %d seconds   \033[0m"%(tt[-1]-tt[-2])) 
    
if 11 in tms:
    print ("Turn DAT off")
    dat.femb_powering([])
    tt.append(time.time())
    print ("It took %d seconds in total for the entire test"%(tt[-1]-tt[0]))
    print ("\033[92m  please move data in folder ({}) to the PC and perform the analysis script \033[0m".format(fdir))
    print ("\033[92m  Well done \033[0m")