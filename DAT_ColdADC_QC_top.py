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
dat.rev = 1

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
print ("\033[96m 2: ADC reserved...  \033[0m")
print ("\033[96m 3: ADC reference voltage measurement  \033[0m")
print ("\033[96m 4: ADC autocalibration check  \033[0m")
print ("\033[96m 5: ADC noise measurement  \033[0m")
print ("\033[96m 6: ADC DNL/INL measurement  \033[0m")
print ("\033[96m 7: ADC DAT-DAC SCAN  \033[0m")
print ("\033[96m 8: ADC ENOB measurement \033[0m")
print ("\033[96m 9: ADC ring oscillator frequency readout \033[0m")
print ("\033[96m 10: ADC RANGE test \033[0m")
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
            print ("""\033[91m  ssh root@192.168.121.123  $wibdate  \033[0m""")
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

#to be change later sgao 04/19/24
itemized_flg = False
if itemized_flg:
    if not os.path.exists(fdir):
        print ("\033[91m Please perform a full test instead of the itemized tests, exit anyway\033[0m")
        exit()

dat.DAT_on_WIBslot = int(logsd["DAT_on_WIB_slot"])
fembs = [dat.DAT_on_WIBslot] 
dat.fembs = fembs

#Possibly put DAT version in a DAT register that we can peek?
#dat_revision = 0 # 0 = old dat

#if dat.rev == 0:
#    if dat_sn  == 1:
#        dat.fe_cali_vref = 1.583
#    if dat_sn  == 2:
#        dat.fe_cali_vref = 1.5738
#if dat.rev == 1:
#    dat.fe_cali_vref = 1.090
#Vref = dat.fe_cali_vref

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

#to be change later sgao 04/19/24
#tms=[0]
#if 0 not in tms :
#    pwr_meas = dat.get_sensors()
#    for key in pwr_meas:
#        if "FEMB%d"%dat.dat_on_wibslot in key:
#            on_f = False
#            if ("BIAS_V" in key) and (pwr_meas[key] > 4.5):
#                    if ("DC2DC0_V" in key) and (pwr_meas[key] > 3.5):
#                            if ("DC2DC1_V" in key) and (pwr_meas[key] > 3.5):
#                                    if ("DC2DC2_V" in key) and (pwr_meas[key] > 3.5):
#                                            on_f = True
#            if (not on_f) and (tms[0] != 11):
#                tms = [11] + tms #turn DAT on
#                if 11 not in tms:
#                    tms = tms + [11] #turn DAT off after testing

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

    pwr_meas, link_mask, init_f = dat.wib_pwr_on_dat()
    datad["WIB_PWR"] = pwr_meas
    datad["WIB_LINK"] = link_mask

    if False:
        fes_pwr_info = dat.fe_pwr_meas()
        datad["FE_PWRON"] = fes_pwr_info
        print (fes_pwr_info)
        adcs_pwr_info = dat.adc_pwr_meas()
        datad["ADC_PWRON"] = adcs_pwr_info
        print (adcs_pwr_info)
        cds_pwr_info = dat.dat_cd_pwr_meas()
        datad["CD_PWRON"] = cds_pwr_info
        print (cds_pwr_info)

    fes_pwr_info = dat.fe_pwr_meas()
    datad["FE_PWRON"] = fes_pwr_info
    adcs_pwr_info = dat.adc_pwr_meas()
    datad["ADC_PWRON"] = adcs_pwr_info
    cds_pwr_info = dat.dat_cd_pwr_meas()
    datad["CD_PWRON"] = cds_pwr_info
    warn_flg, febads, adcbads, cdbads = dat.asic_init_pwrchk(fes_pwr_info, adcs_pwr_info, cds_pwr_info)
    if warn_flg:
        print ("exit anyway")
        exit()
    dat.asic_init_por()
    chkdata = dat.dat_asic_chk()
    datad.update(chkdata)
    print ("to do: FE mapping to be done")
    
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
    print ("\033[92mPass init check, it took %d seconds \033[0m"%(tt[-1]-tt[-2]))
    
    
if 1 in tms: #if "cycling_placeholder" in tms:
    print ("\033[95mADC power cycling measurement starts...\033[0m")
    cycle_times = 6
    
    datad = {}
    datad['logs'] = logs
     
    for ci in range(cycle_times):
        dat.dat_pwroff_chk(env = logs['env']) #make sure DAT is off
        dat.wib_pwr_on_dat() #turn DAT on
        adac_pls_en, sts, swdac, dac = dat.dat_cali_source(cali_mode=2,asicdac=0x20)

        cseti = ci%4   
        if cseti == 0: #SDC off(bypass), DB(bypass), SE : Regaddr0x80[1:0] = b”11” [por default], regaddr0x84[3]=b’1’ (diff_en = 0, sdc_en = 0)
            sha_cs = 0
            ibuf_cs = 0
        if cseti == 1: #SDC off(bypass), DB(bypass), DIFF : Regaddr0x80[1:0] = b”11”[por default], regaddr0x84[3]=b’0’ (diff_en = 1)
            sha_cs = 1
            ibuf_cs = 0
        #Skipping this config because datasheet says not to do it:
        # if cseti == 2: #SDC on, DB on, SE:  Regaddr0x80[1:0] = b”00” (must set manually), regaddr0x84[3]=b’1’ (diff_en = 0)
        if cseti == 2: #SDC on, DB off, SE:  Regaddr0x80[1:0] = b”10”, regaddr0x84[3]=b’1’ (sdc_en = 1, diff_en = 0)
            sha_cs = 1
            ibuf_cs = 1
        if cseti == 3: #SDC off, DB on, DIFF:  Regaddr0x80[1:0] = b”01”(must set manually), regaddr0x84[3]=b’0’ [por default]
            sha_cs = 1
            ibuf_cs = 2
        
        cfg_info = dat.dat_adc_qc_cfg(sha_cs=sha_cs, ibuf_cs=ibuf_cs, autocali=0)                    
        rawdata = dat.dat_adc_qc_acq(num_samples = 1)
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
    print ("The test was included in the init chekcout")
    print ("PASS")

if 3 in tms:#if "refv_placeholder" in tms:
    print ("\033[95mADC monitoring measurement starts...   \033[0m")
#note: only WIB FEMB slot 0 is used for DAT now
    femb_id = dat.DAT_on_WIBslot
    data = {}
    data['logs'] = logs   

    cfg_info = dat.dat_adc_qc_cfg()
    time.sleep(0.5)
    #measure default outputs of VREFP, VREFN, VCMI, VCMO
    data.update(dat.dat_adc_mons(femb_id, mon_type=0x3c))

    #In a well-behaved DAC where superposition holds, these tests should be sufficient to verify
    #the static performance.
    data["refv_dacs"] = dat.dat_adc_qc_refdacs(femb_id)
    #Use ^ for DNL/INL
    data['Imons'] = dat.dat_adc_qc_imons(femb_id)    
    
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
    datad['weights'] =  dat.dat_adc_qc_auto_weithts()
        
    fp = fdir + "QC_AUTOCALI" + ".bin"
    with open(fp, 'wb') as fn:
        pickle.dump(datad, fn)    
    tt.append(time.time())
    print ("\033[92mADC autocalibration check is done. it took %d seconds   \033[0m"%(tt[-1]-tt[-2]))   
    
if 5 in tms:#if "noise_placeholder" in tms:
    print ("\033[95mADC  noise measurement starts...   \033[0m")
    datad = {}
    datad['logs'] = logs  
    adac_pls_en, sts, swdac, dac = dat.dat_cali_source(cali_mode=3)
    cfg_info = dat.dat_fe_qc_cfg(adac_pls_en=adac_pls_en, sts=sts, swdac=swdac, dac=dac)    

    if True:#test with LArASIC
        print ("Test RMS noise with differnt output modes under 14mV/fC, 2us")
        slk0=0
        slk1=0
        st0=1
        st1=1
        sg0=0
        sg1=0
        for snc in [0, 1]:
            for buf in [0,1,2]:
                sdd = buf//2
                sdf = buf%2
                fe_cfg_info = dat.dat_fe_only_cfg(snc=snc, sg0=sg0, sg1=sg1, st0=st0, st1=st1, slk0=slk0, slk1=slk1, sdd=sdd, sdf=sdf) 
                data = dat.dat_fe_qc_acq(num_samples=5)
                cfgstr = "RMS_OUTPUT_SDD%d_SDF%d_SLK0%d_SLK1%d_SNC%d_ST0%d_ST1%d_SG0%d_SG1%d"%(sdd, sdf, slk0, slk1, snc, st0, st1, sg0, sg1)
                datad[cfgstr] = [dat.fembs, data, cfg_info, fe_cfg_info]

    if True:#test with input open
        cfg_info = dat.dat_adc_qc_cfg(sha_cs=1, autocali=1)
        dat.dat_coldadc_input_cs(mode="OPEN", SHAorADC = "SHA", chsenl=0x0000)
        datad['DIFF_OPEN']   =  [dat.fembs, dat.dat_adc_qc_acq(5), cfg_info, "ColdADC_DIFF_OPEN"]

        cfg_info = dat.dat_adc_qc_cfg(sha_cs=0, autocali=1)
        dat.dat_coldadc_input_cs( mode="OPEN", SHAorADC = "SHA", chsenl=0x0000)
        datad['SE_OPEN']   =   [dat.fembs, dat.dat_adc_qc_acq(5), cfg_info, "ColdADC_SE_OPEN"]

    if True:#test with input is DAT-DAC
        val = 0.9 #V
        valint = int(val*65536/dat.ADCVREF)
        dat.dat_set_dac(val=valint, adc=0) #set ADC_P to 0 V
        dat.dat_set_dac(val=valint, adc=1) #set ADC_N to 0 V

        cfg_info = dat.dat_adc_qc_cfg(sha_cs=1, autocali=1)
        dat.dat_coldadc_input_cs( mode="DACDIFF", SHAorADC = "SHA", chsenl=0x0000)
        datad['DACDIFF']   =  [dat.fembs, dat.dat_adc_qc_acq(5), cfg_info, "ColdADC_DACDIFF"]

        cfg_info = dat.dat_adc_qc_cfg(sha_cs=0, autocali=1)
        dat.dat_coldadc_input_cs( mode="DACSE", SHAorADC = "SHA", chsenl=0x0000)
        datad['DACSE']   =  [dat.fembs, dat.dat_adc_qc_acq(5), cfg_info, "ColdADC_DACSE"]
   
    fp = fdir + "QC_RMS" + ".bin"
    with open(fp, 'wb') as fn:
        pickle.dump(datad, fn)

    tt.append(time.time())        
    print ("\033[92mADC noise measurement is done. it took %d seconds   \033[0m"%(tt[-1]-tt[-2])) 
    
if 6 in tms:
    print ("\033[95mADC DNL/INL measurement starts...   \033[0m")
    
    datad = {}
    datad['logs'] = logs  
    
    
    #Assuming slow ramp config
    #Replace these or input them in DAT_user_input.py as necessary:
    datad['fembs'] = dat.fembs
    datad['waveform'] = 'RAMP' 
    source = 'P6SE'
    datad['source'] = source
    datad['freq'] = 1 # Hz
    datad['voltage_low'] = -0.1 # Vpp
    datad['voltage_high'] = 2.0
    datad['num_samples'] = 2000000
    #datad['waveform'] = 'RAMP'
    #datad['source'] = 'DAT_P6'
    #datad['freq'] = 1000 # Hz
    #datad['offset'] = 1 #V    
    
    dat.sig_gen_config(waveform = datad['waveform'], freq=datad['freq'], vlow=datad['voltage_low'], vhigh=datad['voltage_high']) 

    cfg_info = dat.dat_adc_qc_cfg() 
    dat.dat_coldadc_input_cs(mode=source, SHAorADC = "SHA", chsenl=0x0000)
    dat.dat_adc_qc_acq(1)
    histdata = dat.dat_adc_histbuf_trig(num_samples=datad['num_samples'], waveform=datad['waveform'])  
    datad['histdata'] = [dat.fembs, histdata, cfg_info, "WIB_SE_SHA_HIST"]

    #new FE board
    
    dat.sig_gen_config() #turn signal generator off
    
    fp = fdir + "QC_DNL_INL" + ".bin"
    with open(fp, 'wb') as fn:
        pickle.dump(datad, fn)

    tt.append(time.time())        
    print ("\033[92mADC DNL/INL measurement is done. it took %d seconds   \033[0m"%(tt[-1]-tt[-2])) 
    
if 7 in tms:#if "overflow_placeholder" in tms:
    print ("\033[95mADC DAT-DAC SCAN starts...   \033[0m")
    datad = {}
    datad['logs'] = logs  
    adac_pls_en, sts, swdac, dac = dat.dat_cali_source(cali_mode=3)
    cfg_info = dat.dat_fe_qc_cfg(adac_pls_en=adac_pls_en, sts=sts, swdac=swdac, dac=dac)    
  
    cfg_info = dat.dat_adc_qc_cfg(sha_cs=1, autocali=1)
    dat.dat_coldadc_input_cs( mode="DACDIFF", SHAorADC = "SHA", chsenl=0x0000)

    step = 0.05
    for i in range(int(1.25/step)):
        valp = 0.9 + i*step
        valint = int(valp*65536/dat.ADCVREF)
        dat.dat_set_dac(val=valint, adc=0) #set ADC_P 
        valn = 0.9 - i*step
        if valn <= 0:
            valn = 0
        valint = int(valn*65536/dat.ADCVREF)
        dat.dat_set_dac(val=valint, adc=1) #set ADC_N 
        time.sleep(0.01)
        datad['DACDIFF_%04d'%i] = [dat.fembs, dat.dat_adc_qc_acq(1), cfg_info, valp-valn]

    cfg_info = dat.dat_adc_qc_cfg(sha_cs=0, autocali=1)
    dat.dat_coldadc_input_cs( mode="DACSE", SHAorADC = "SHA", chsenl=0x0000)
    for i in range(int(2.5/step)):
        val = i*step
        valint = int(val*65536/dat.ADCVREF)
        dat.dat_set_dac(val=valint, adc=0) #set ADC_P to 0 V
        dat.dat_set_dac(val=valint, adc=1) #set ADC_N to 0 V
        time.sleep(0.01)
        datad['DACSE_%04d'%i] = [dat.fembs, dat.dat_adc_qc_acq(1), cfg_info, val]
    fp = fdir + "QC_DACSCAN" + ".bin"
    with open(fp, 'wb') as fn:
        pickle.dump(datad, fn)

    tt.append(time.time())        
    print ("\033[92mADC DAT-DAC SCAN is done. it took %d seconds   \033[0m"%(tt[-1]-tt[-2])) 

#    datad = {}
#    datad['logs'] = logs  
#    
#    cfg_info = dat.dat_adc_qc_cfg()  
#
#
#    #take data for underflow
#    ##tie ADC to gnd
#    # dat.cdpoke(dat.dat_on_wibslot, 0xC, 0, dat.DAT_ADC_SRC_CS_P_MSB, 0x0) 
#    # dat.cdpoke(dat.dat_on_wibslot, 0xC, 0, dat.DAT_ADC_SRC_CS_P_LSB, 0x0) 
#    # dat.cdpoke(dat.dat_on_wibslot, 0xC, 0, dat.DAT_ADC_TEST_IN_SEL, 0x0)  
#    # # dat.cdpoke(dat.dat_on_wibslot, 0xC, 0, dat.DAT_ADC_PN_TST_SEL, 0x0)
#    # dat.cdpoke(dat.dat_on_wibslot, 0xC, 0, dat.DAT_ADC_PN_TST_SEL, 0x33)
#    dat.dat_set_dac(0x0, adc=0)  #Set ADCP to 0
#    dat.dat_set_dac(0xFFFF, adc=1)  #give ADCN a positive voltage   
#    # import pyvisa  
#    # rm = pyvisa.ResourceManager()    
#    # sigconfig_done = False
#    # while not sigconfig_done:
#        # try:
#            # sig_gen = rm.open_resource('TCPIP::192.168.121.10::INSTR')
#            # print(sig_gen.query("*IDN?"))
#            # sig_gen.write("FUNCTION DC")
#            # sig_gen.write("VOLTAGE:OFFSET -2.5V")
#            # sig_gen.write("OUTP ON")
#            # sigconfig_done = True
#            # print("Successfully configured signal generator")
#        # except:
#            # print("Error configuring signal generator. Trying again...")
#            # sigconfig_done = False
#        
#        # sig_gen.close()
#
#    
#    # dat.dat_coldadc_ext(ext_source='DAT_P6')
#    dat.dat_coldadc_cali_cs(mode="DIFF")
#        
#    
#    # input("Probe DACs - underflow")
#    print(hex(dat.peek(0xa00c00f0) >> 10))
#    datad['rawdata_under'] = dat.dat_adc_qc_acq(num_samples = 20) 
#    
#    # sig_gen = rm.open_resource('TCPIP::192.168.121.10::INSTR')
#    # sig_gen.write("OUTP OFF")
#    # sig_gen.close()
#
#    
#    #take data for overflow
#    # ##tie ADC P  to DAT PDAC set to max
#    # # dat.cdpoke(dat.dat_on_wibslot, 0xC, 0, dat.DAT_ADC_SRC_CS_P_MSB, 0x0) 
#    # # dat.cdpoke(dat.dat_on_wibslot, 0xC, 0, dat.DAT_ADC_SRC_CS_P_LSB, 0x0) 
#    # # dat.cdpoke(dat.dat_on_wibslot, 0xC, 0, dat.DAT_ADC_TEST_IN_SEL, 0x0)  
#    # # # dat.cdpoke(dat.dat_on_wibslot, 0xC, 0, dat.DAT_ADC_PN_TST_SEL, 0x0)    
#    # dat.cdpoke(dat.dat_on_wibslot, 0xC, 0, dat.DAT_ADC_PN_TST_SEL, 0x33)
#    dat.dat_coldadc_cali_cs(mode="DIFF")
#    dat.dat_set_dac(0xFFFF, adc=0)
#    dat.dat_set_dac(0x0, adc=1)
#    # input("Probe DACs - overflow")
#    print(hex(dat.peek(0xa00c00f0) >> 10))
#    datad['rawdata_over'] = dat.dat_adc_qc_acq(num_samples = 20) 
#    
#    dat.dat_set_dac(0x0, adc=0) #set ADC PDAC back to 0
#    dat.dat_set_dac(0x0, adc=1) #set ADC NDAC back to 0
#    
#    fp = fdir + "QC_OVERFLOW" + ".bin"
#    with open(fp, 'wb') as fn:
#        pickle.dump(datad, fn)
#
#    tt.append(time.time())        
#    print ("\033[92mADC overflow check is done. it took %d seconds   \033[0m"%(tt[-1]-tt[-2])) 
    
if 8 in tms:#if "enob_placeholder" in tms:
    print ("\033[95mADC ENOB measurement starts...   \033[0m")

    #source = 'WIBSE'
    source = 'P6SE'
    #source = 'P6DIFF'
    #source = 'V2P6_SE2DIFF'
    #source = 'V2WIB_SE2DIFF'
    cfg_info = dat.dat_adc_qc_cfg(autocali=1)  #SDC off, DIFF off
    #cfg_info = dat.dat_adc_qc_cfg(sha_cs=2, ibuf_cs=1)  #SED on, DIFF OFF
    dat.dat_coldadc_input_cs(mode=source, SHAorADC = "SHA", chsenl=0x0000)
   
    for freq in [8106.23, 14781.95, 31948.09, 72002.41, 119686.13, 200748.44, 358104.70]:  
    #for freq in [8106.23]:
    #for freq in [119686.13]:
    #for freq in [31948]:
        datad = {}
        datad['logs'] = logs 
        datad['source'] = source

        #Replace these or input them in DAT_user_input.py as necessary:
        datad['fembs'] = dat.fembs
        datad['waveform'] = 'SINE' 
        datad['num_samples'] = 16384
        datad['freq'] = freq #Hz
        datad['voltage_low'] = 0.3 # V
        datad['voltage_high'] = 1.5 #V
        
        dat.sig_gen_config(waveform = datad['waveform'], freq=datad['freq'], vlow=datad['voltage_low'], vhigh=datad['voltage_high']) 
        time.sleep(0.5)
            
        ##dat.dat_coldadc_input_cs(mode="P6SE", SHAorADC = "SHA", chsenl=0x0000)
        #input ("wait.......")

        #rawdata = dat.dat_adc_qc_acq(1) #trigger readout, save in case of issue
        #fp = fdir + "QC_raw_%08dHz"%datad['freq'] + ".bin"
        #with open(fp, 'wb') as fn:
        #    pickle.dump(rawdata, fn)
        #exit()
        
        datad['enobdata'] = [dat.fembs, dat.dat_enob_acq_2(sineflg=True), cfg_info, "SINE"]
        
        fp = fdir + "QC_ENOB_%08dHz"%datad['freq'] + ".bin"
        with open(fp, 'wb') as fn:
            pickle.dump(datad, fn)

    dat.sig_gen_config()
    tt.append(time.time())        
    print ("\033[92mADC enob measurement is done. it took %d seconds   \033[0m"%(tt[-1]-tt[-2])) 
    
if 9 in tms:#if "ringosc_placeholder" in tms:
    print ("\033[95mADC ring oscillator frequency readout starts...   \033[0m")
    
    datad = {}
    datad['logs'] = logs     
    
    datad['ring_osc_freq'] = dat.dat_adc_qc_oscfreq()
    print (datad['ring_osc_freq'])
    
    fp = fdir + "QC_RINGO" + ".bin"
    with open(fp, 'wb') as fn:
        pickle.dump(datad, fn)

    tt.append(time.time())        
    print ("\033[92mADC ring oscillator frequency readout is done. it took %d seconds   \033[0m"%(tt[-1]-tt[-2])) 

if 10 in tms:
    print ("\033[95mADC Triangle Waveform test starts...   \033[0m")

    datad = {}
    datad['logs'] = logs  

    #Replace these or input them in DAT_user_input.py as necessary:
    datad['fembs'] = dat.fembs
    datad['waveform'] = 'RAMP' 
    datad['num_samples'] = 16384
    datad['source'] = 'WIB'
    datad['freq'] = 400 #Hz
    datad['voltage_low'] = -0.2 # V
    datad['voltage_high'] = 2.2 #V
    
    dat.sig_gen_config(waveform = datad['waveform'], freq=datad['freq'], vlow=datad['voltage_low'], vhigh=datad['voltage_high']) 
        
    cfg_info = dat.dat_adc_qc_cfg() 
    #dat.dat_coldadc_input_cs(mode="WIBSE", SHAorADC = "SHA", chsenl=0x0000)
    dat.dat_coldadc_input_cs(mode="P6SE", SHAorADC = "SHA", chsenl=0x0000)
    dat.dat_adc_qc_acq(1) #trigger readout, save in case of issue
    datad['rawdata'] = [dat.fembs, dat.dat_enob_acq(sineflg=False), cfg_info, "TRIG"]
    dat.sig_gen_config()
    
    fp = fdir + "QC_TRIG" + ".bin"
    with open(fp, 'wb') as fn:
        pickle.dump(datad, fn)

    tt.append(time.time())        
    print ("\033[92mADC Triangle waveform measurement is done. it took %d seconds   \033[0m"%(tt[-1]-tt[-2])) 
    
if 11 in tms:
    print ("Turn DAT off")
    dat.femb_powering([])
    tt.append(time.time())
    print ("It took %d seconds in total for the entire test"%(tt[-1]-tt[0]))
    print ("\033[92m  please move data in folder ({}) to the PC and perform the analysis script \033[0m".format(fdir))
    print ("\033[92m  Well done \033[0m")
