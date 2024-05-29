import time
import sys
import numpy as np
import pickle
import copy
import time, datetime, random, statistics    
import os
from dat_cfg import DAT_CFGS
from DAT_read_cfg import dat_read_cfg
import argparse
                
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
print ("\033[96m 1: FE power consumption measurement  \033[0m")
print ("\033[96m 2: FE response measurement checkout  \033[0m")
print ("\033[96m 3: FE monitoring measurement  \033[0m")
print ("\033[96m 4: FE power cycling measurement  \033[0m")
print ("\033[96m 5: FE noise measurement  \033[0m")
print ("\033[96m 61: FE calibration measurement (ASIC-DAC)  \033[0m")
print ("\033[96m 62: FE calibration measurement (DAT-DAC) \033[0m")
print ("\033[96m 63: FE calibration measurement (Direct-Input) \033[0m")
print ("\033[96m 64: FE calibration measurement ((ASIC-DAC, 4.7mV/fC) \033[0m")
print ("\033[96m 7: FE delay run  \033[0m")
print ("\033[96m 8: FE cali-cap measurement \033[0m")
print ("\033[96m 9: Turn DAT off \033[0m")
print ("\033[96m 10: Turn DAT (on WIB slot0) on without any check\033[0m")

ag = argparse.ArgumentParser()
ag.add_argument("-t", "--task", help="which QC tasks to be performed", type=int, choices=[0, 1,2,3,4,5,61, 62, 63, 64, 7,8,9,10, 22, 100],  nargs='+', default=[1,2,3,4,5,61, 62, 63, 64, 7,8])
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
        print ("Error to create folder %s"%save_dir)
        sys.exit()

dat.DAT_on_WIBslot = int(logsd["DAT_on_WIB_slot"])
fembs = [dat.DAT_on_WIBslot] 
dat.fembs = fembs
dat.rev = int(logsd["DAT_Revision"])
dat_sn = int(logsd["DAT_SN"])

if dat.rev == 0:
    if dat_sn  == 1:
        Vref = 1.583
    if dat_sn  == 2:
        Vref = 1.5738
if dat.rev == 1:
    dat.fe_cali_vref = 1.090
    Vref = dat.fe_cali_vref
        
logs.update(logsd)

#if 100 in tms : #100 is only for itemed testing with power operation 
if True:
    pwr_meas = dat.get_sensors()
    on_f = False
    for key in pwr_meas:
        if "FEMB%d"%dat.dat_on_wibslot in key:
            if ("BIAS_V" in key) and (pwr_meas[key] > 4.5):
                    if ("DC2DC0_V" in key) and (pwr_meas[key] > 3.5):
                            if ("DC2DC1_V" in key) and (pwr_meas[key] > 3.5):
                                    if ("DC2DC2_V" in key) and (pwr_meas[key] > 3.5):
                                            on_f = True
                                            break
    if (not on_f): #turn DAT on
        tms = [10] + tms #turn DAT on


####### Init check information #######
if 10 in tms:
    print ("Turn DAT on and wait 5 seconds")
    #set FEMB voltages
    dat.fembs_vol_set(vfe=4.0, vcd=4.0, vadc=4.0)
    dat.femb_powering([dat.dat_on_wibslot])
    dat.data_align_pwron_flg = True
    time.sleep(5)

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

    datad['logs'] = logs

    fp = fdir + "QC_INIT_CHK" + ".bin"
    with open(fp, 'wb') as fn:
        pickle.dump(datad, fn)

    tt.append(time.time())
    print ("save_fdir_start_%s_end_save_fdir"%fdir)
    print ("save_file_start_%s_end_save_file"%fp)
    print ("Done! Pass!, it took %d seconds"%(tt[-1]-tt[-2]))

if 1 in tms:
    print ("FE power consumption measurement starts...")
    datad = {}
    datad['logs'] = logs
    for snc in [0, 1]:
        for sdd in [0, 1]:
            for sdf in [0, 1]:
                if sdd == 1 or sdf ==1:
                    dat.fedly = 3
                else:
                    dat.fedly = 1
                if (sdd == 1) and (sdf==1):
                    continue
                else:
                    adac_pls_en, sts, swdac, dac = dat.dat_cali_source(cali_mode=2, asicdac=0x10)
                    rawdata = dat.dat_fe_qc(adac_pls_en=adac_pls_en, sts=sts, swdac=swdac, dac=dac,snc=snc, sdd=sdd, sdf=sdf ) 
                    pwr_meas = dat.fe_pwr_meas()
                    datad["PWR_SDD%d_SDF%d_SNC%d"%(sdd,sdf,snc)] = [dat.fembs, rawdata[0], rawdata[1], pwr_meas]
    dat.fedly = 1

    fp = fdir + "QC_PWR" + ".bin"
    with open(fp, 'wb') as fn:
        pickle.dump(datad, fn)
    tt.append(time.time())
    print ("save_fdir_start_%s_end_save_fdir"%fdir)
    print ("save_file_start_%s_end_save_file"%fp)
    print ("Done! Pass!, it took %d seconds"%(tt[-1]-tt[-2]))

if 2 in tms:
    print ("FE check response measurement starts...")
    datad = {}
    datad['logs'] = logs

    adac_pls_en, sts, swdac, dac = dat.dat_cali_source(cali_mode=2, asicdac=0x10)
    cfg_info = dat.dat_fe_qc_cfg(adac_pls_en=adac_pls_en, sts=sts, swdac=swdac, dac=dac) 
    
    sdd=0
    sdf=0
    slk0=0
    slk1=0
    snc=0
    st0=1
    st1=1
    
    #response under different gains
    for snc in [0,1]:
        for sg0 in [0,1]:
            for sg1 in [0,1]:
                fe_cfg_info = dat.dat_fe_only_cfg(sts=sts, swdac=swdac, dac=dac, snc=snc, sg0=sg0, sg1=sg1, st0=st0, st1=st1, slk0=slk0, slk1=slk1, sdd=sdd, sdf=sdf) 
                data = dat.dat_fe_qc_acq(num_samples=1)
                cfgstr = "CHK_GAINs_SDD%d_SDF%d_SLK0%d_SLK1%d_SNC%d_ST0%d_ST1%d_SG0%d_SG1%d"%(sdd, sdf, slk0, slk1, snc, st0, st1, sg0, sg1)
                datad[cfgstr] = [dat.fembs, data, cfg_info, fe_cfg_info]
    snc=0
    sg0=0
    sg1=0
    
    #response under different output modes
    for buf in [0,1,2]:
        sdd = buf//2
        sdf = buf%2
        if sdd == 1 or sdf ==1:
            dat.fedly = 3
        else:
            dat.fedly = 1

        fe_cfg_info = dat.dat_fe_only_cfg(sts=sts, swdac=swdac, dac=dac, snc=snc, sg0=sg0, sg1=sg1, st0=st0, st1=st1, slk0=slk0, slk1=slk1, sdd=sdd, sdf=sdf) 
        data = dat.dat_fe_qc_acq(num_samples=1)
        cfgstr = "CHK_OUTPUT_SDD%d_SDF%d_SLK0%d_SLK1%d_SNC%d_ST0%d_ST1%d_SG0%d_SG1%d"%(sdd, sdf, slk0, slk1, snc, st0, st1, sg0, sg1)
        datad[cfgstr] = [dat.fembs, data, cfg_info, fe_cfg_info]
    dat.fedly = 1

    sdd=0
    sdf=0
    #response under different BLs
    for snc in [0,1]:
        fe_cfg_info = dat.dat_fe_only_cfg(sts=sts, swdac=swdac, dac=dac, snc=snc, sg0=sg0, sg1=sg1, st0=st0, st1=st1, slk0=slk0, slk1=slk1, sdd=sdd, sdf=sdf) 
        data = dat.dat_fe_qc_acq(num_samples=1)
        cfgstr = "CHK_BL_SDD%d_SDF%d_SLK0%d_SLK1%d_SNC%d_ST0%d_ST1%d_SG0%d_SG1%d"%(sdd, sdf, slk0, slk1, snc, st0, st1, sg0, sg1)
        datad[cfgstr] = [dat.fembs, data, cfg_info, fe_cfg_info]
    
    snc=0
    #response under different SLKs
    for slk0 in [0,1]:
        for slk1 in [0,1]:
            fe_cfg_info = dat.dat_fe_only_cfg(sts=sts, swdac=swdac, dac=dac, snc=snc, sg0=sg0, sg1=sg1, st0=st0, st1=st1, slk0=slk0, slk1=slk1, sdd=sdd, sdf=sdf) 
            data = dat.dat_fe_qc_acq(num_samples=1)
            cfgstr = "CHK_SLKS_SDD%d_SDF%d_SLK0%d_SLK1%d_SNC%d_ST0%d_ST1%d_SG0%d_SG1%d"%(sdd, sdf, slk0, slk1, snc, st0, st1, sg0, sg1)
            datad[cfgstr] = [dat.fembs, data, cfg_info, fe_cfg_info]
    
    slk0=0
    slk1=0
    #response under different peak times
    for st0 in [0,1]:
        for st1 in [0,1]:
            fe_cfg_info = dat.dat_fe_only_cfg(sts=sts, swdac=swdac, dac=dac, snc=snc, sg0=sg0, sg1=sg1, st0=st0, st1=st1, slk0=slk0, slk1=slk1, sdd=sdd, sdf=sdf) 
            data = dat.dat_fe_qc_acq(num_samples=1)
            cfgstr = "CHK_TP_SDD%d_SDF%d_SLK0%d_SLK1%d_SNC%d_ST0%d_ST1%d_SG0%d_SG1%d"%(sdd, sdf, slk0, slk1, snc, st0, st1, sg0, sg1)
            datad[cfgstr] = [dat.fembs, data, cfg_info, fe_cfg_info]
    
    fp = fdir + "QC_CHKRES.bin"
    with open(fp, 'wb') as fn:
        pickle.dump(datad, fn)
    tt.append(time.time())
    print ("save_fdir_start_%s_end_save_fdir"%fdir)
    print ("save_file_start_%s_end_save_file"%fp)
    print ("Done! Pass!, it took %d seconds"%(tt[-1]-tt[-2]))


if 3 in tms:
    print ("FE monitoring measurement starts...")
    data = {}
    data['logs'] = logs

    adac_pls_en, sts, swdac, dac = dat.dat_cali_source(cali_mode=3)
    cfg_info = dat.dat_fe_qc_cfg(adac_pls_en=adac_pls_en, sts=sts, swdac=swdac, dac=dac) 
    time.sleep(1)

    data.update( dat.dat_fe_vbgrs() )
    data.update( dat.dat_fe_mons(mon_type=0x01) )
    data.update( dat.dat_fe_mons(mon_type=0x02) )
    data.update( dat.dat_fe_mons(mon_type=0x04) )
    data.update( dat.dat_fe_mons(mon_type=0x08) )
    data.update( dat.dat_fe_mons(mon_type=0x10) )
    
    fp = fdir + "QC_MON" + ".bin"
    with open(fp, 'wb') as fn:
        pickle.dump(data, fn)
    
    tt.append(time.time())
    print ("save_fdir_start_%s_end_save_fdir"%fdir)
    print ("save_file_start_%s_end_save_file"%fp)
    print ("Done! Pass!, it took %d seconds"%(tt[-1]-tt[-2]))



if 4 in tms:
    print ("FE power cycling measurement starts...")
    cycle_times = 8
    
    datad = {}
    datad['logs'] = logs
    
    for ci in range(cycle_times):
        dat.dat_pwroff_chk(env = logs['env']) #make sure DAT is off
        dat.wib_pwr_on_dat() #turn DAT on
        cseti = ci%8
        if cseti == 0:
            adac_pls_en, sts, swdac, dac = dat.dat_cali_source(cali_mode=2,asicdac=0x10)
            rawdata = dat.dat_fe_qc(adac_pls_en=adac_pls_en, sts=sts, swdac=swdac, dac=dac,snc=0, sdd=0, sdf=0, slk0=0, slk1=0) #900mV, 500pA, SDD off, SDF off, ASIC-DAC
        if cseti == 1:
            adac_pls_en, sts, swdac, dac = dat.dat_cali_source(cali_mode=2,asicdac=0x10)
            rawdata = dat.dat_fe_qc(adac_pls_en=adac_pls_en, sts=sts, swdac=swdac, dac=dac,snc=0, sdd=0, sdf=0, slk0=1, slk1=0) #900mV, 100pA, SDD off, SDF off, ASIC-DAC
        if cseti == 2:
            adac_pls_en, sts, swdac, dac = dat.dat_cali_source(cali_mode=2,asicdac=0x10)
            rawdata = dat.dat_fe_qc(adac_pls_en=adac_pls_en, sts=sts, swdac=swdac, dac=dac,snc=0, sdd=0, sdf=0, slk0=1, slk1=1) #900mV, 1000pA, SDD off, SDF off, ASIC-DAC
        if cseti == 3:
            adac_pls_en, sts, swdac, dac = dat.dat_cali_source(cali_mode=2,asicdac=0x10)
            rawdata = dat.dat_fe_qc(adac_pls_en=adac_pls_en, sts=sts, swdac=swdac, dac=dac,snc=0, sdd=0, sdf=0, slk0=0, slk1=1) #900mV, 5000pA, SDD off, SDF off, ASIC-DAC
        if cseti == 4:
            adac_pls_en, sts, swdac, dac = dat.dat_cali_source(cali_mode=1, val=1.54, period=500, width=400)
            rawdata = dat.dat_fe_qc(adac_pls_en=adac_pls_en, sts=sts, swdac=swdac, dac=dac,snc=1, sdd=0, sdf=0 ) #200mV, 500pA, SDD off, SDF off, DAT-DAC
        if cseti == 5:
            adac_pls_en, sts, swdac, dac = dat.dat_cali_source(cali_mode=1, val=1.54, period=500, width=400)
            rawdata = dat.dat_fe_qc(adac_pls_en=adac_pls_en, sts=sts, swdac=swdac, dac=dac, snc=1, sdd=1, sdf=0 ) #200mV, 500pA, SDD on, SDF off, DAT-DAC
        if cseti == 6:
            adac_pls_en, sts, swdac, dac = dat.dat_cali_source(cali_mode=1, val=1.54, period=500, width=400)
            rawdata = dat.dat_fe_qc(adac_pls_en=adac_pls_en, sts=sts, swdac=swdac, dac=dac, snc=1, sdd=0, sdf=1 ) #200mV, 500pA, SDD off, SDF on, DAT-DAC
        if cseti == 7:
            adac_pls_en, sts, swdac, dac = dat.dat_cali_source(cali_mode=0, val=1.54, period=500, width=400)
            rawdata = dat.dat_fe_qc(adac_pls_en=adac_pls_en, sts=sts, swdac=swdac, dac=dac, snc=1, sdd=0, sdf=0 ) #200mV, 500pA, SDD off, SDF off, Direct-input
    
        fes_pwr_info = dat.fe_pwr_meas()
        adcs_pwr_info = dat.adc_pwr_meas()
        cds_pwr_info = dat.dat_cd_pwr_meas()
    
        datad["PwrCycle_%d"%cseti] = [dat.fembs, rawdata[0], rawdata[1], fes_pwr_info, adcs_pwr_info, cds_pwr_info]
    
    fp = fdir + "QC_PWR_CYCLE" + ".bin"
    with open(fp, 'wb') as fn:
        pickle.dump(datad, fn)
    tt.append(time.time())
    print ("save_fdir_start_%s_end_save_fdir"%fdir)
    print ("save_file_start_%s_end_save_file"%fp)
    print ("Done! Pass!, it took %d seconds"%(tt[-1]-tt[-2]))

    
if 5 in tms:
    print ("FE noise measurement starts...")
    datad = {}
    datad['logs'] = logs
    
    adac_pls_en, sts, swdac, dac = dat.dat_cali_source(cali_mode=3)
    cfg_info = dat.dat_fe_qc_cfg(adac_pls_en=adac_pls_en, sts=sts, swdac=swdac, dac=dac) 
    
    sdd=0
    sdf=0
    slk0=0
    slk1=0
    snc=0
    st0=0
    st1=0
    sg0=0
    sg1=0
    
    if True:
        print ("Test RMS noise with differnt BLs, peak times and gains")
        sdd=0
        sdf=0
        slk0=0
        slk1=0
        for snc in [0, 1]:
            for sg0 in [0,1]:
                for sg1 in [0,1]:
                    for st0 in [0,1]:
                        for st1 in [0,1]:
                            fe_cfg_info = dat.dat_fe_only_cfg(snc=snc, sg0=sg0, sg1=sg1, st0=st0, st1=st1, slk0=slk0, slk1=slk1, sdd=sdd, sdf=sdf) 
                            data = dat.dat_fe_qc_acq(num_samples=10)
                            cfgstr = "RMS_SDD%d_SDF%d_SLK0%d_SLK1%d_SNC%d_ST0%d_ST1%d_SG0%d_SG1%d"%(sdd, sdf, slk0, slk1, snc, st0, st1, sg0, sg1)
                            print (cfgstr)
                            datad[cfgstr] = [dat.fembs, data, cfg_info, fe_cfg_info]
    
    if True:
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
                data = dat.dat_fe_qc_acq(num_samples=10)
                cfgstr = "RMS_OUTPUT_SDD%d_SDF%d_SLK0%d_SLK1%d_SNC%d_ST0%d_ST1%d_SG0%d_SG1%d"%(sdd, sdf, slk0, slk1, snc, st0, st1, sg0, sg1)
                print (cfgstr)
                datad[cfgstr] = [dat.fembs, data, cfg_info, fe_cfg_info]
    
    if True:
        print ("Test RMS noise with differnt leakage currents under 14mV/fC, 2us")
        sdd=0
        sdf=0
        snc=0
        st0=1
        st1=1
        sg0=0
        sg1=0
        for slk0 in [0, 1]:
            for slk1 in [0,1]:
                fe_cfg_info = dat.dat_fe_only_cfg(snc=snc, sg0=sg0, sg1=sg1, st0=st0, st1=st1, slk0=slk0, slk1=slk1, sdd=sdd, sdf=sdf) 
                data = dat.dat_fe_qc_acq(num_samples=10)
                cfgstr = "RMS_SLK_SDD%d_SDF%d_SLK0%d_SLK1%d_SNC%d_ST0%d_ST1%d_SG0%d_SG1%d"%(sdd, sdf, slk0, slk1, snc, st0, st1, sg0, sg1)
                print (cfgstr)
                datad[cfgstr] = [dat.fembs, data, cfg_info, fe_cfg_info]
    
    fp = fdir + "QC_RMS" + ".bin"
    with open(fp, 'wb') as fn:
        pickle.dump(datad, fn)

    tt.append(time.time())
    print ("save_fdir_start_%s_end_save_fdir"%fdir)
    print ("save_file_start_%s_end_save_file"%fp)
    print ("Done! Pass!, it took %d seconds"%(tt[-1]-tt[-2]))


if 61 in tms:
    if True:
        print ("perform ASIC-DAC calibration under 14mV/fC, 2us")
        adac_pls_en, sts, swdac, dac = dat.dat_cali_source(cali_mode=2, asicdac=0)
        cfg_info = dat.dat_fe_qc_cfg(adac_pls_en=adac_pls_en, sts=sts, swdac=swdac, dac=dac) 
        datad = {}
        datad['logs'] = logs
    
        slk0=0
        slk1=0
        st0=1
        st1=1
        sg0=0
        sg1=0
        sdd=0
        sdf=0
        for snc in [0, 1]:
    #        for buf in [0,1,2]:
    #            sdd = buf//2
    #            sdf = buf%2
            if snc == 0:
                maxdac = 32
            else:
                maxdac = 64
            for dac in range(0, maxdac, maxdac//8):
                fe_cfg_info = dat.dat_fe_only_cfg(sts=sts, swdac=swdac, dac=dac, snc=snc, sg0=sg0, sg1=sg1, st0=st0, st1=st1, slk0=slk0, slk1=slk1, sdd=sdd, sdf=sdf) 
                data = dat.dat_fe_qc_acq(num_samples=5)
                cfgstr = "CALI_SNC%d_ASICDAC%02d"%(snc,dac)
                print (cfgstr)
                datad[cfgstr] = [dat.fembs, data, cfg_info, fe_cfg_info]
    
        fp = fdir + "QC_CALI_ASICDAC" + ".bin"
        with open(fp, 'wb') as fn:
            pickle.dump(datad, fn)
    tt.append(time.time())
    print ("FE calibration measurement (ASIC-DAC) is done. it took %d seconds"%(tt[-1]-tt[-2]))
      
if 62 in tms:
    if True:
        print ("perform DAT-DAC calibration under 14mV/fC, 2us")
        adac_pls_en, sts, swdac, dac = dat.dat_cali_source(cali_mode=1, val=Vref, period=1000, width=800) 
        cfg_info = dat.dat_fe_qc_cfg(adac_pls_en=adac_pls_en, sts=sts, swdac=swdac, dac=dac) 
        datad = {}
        datad['logs'] = logs
    
        slk0=0
        slk1=0
        st0=1
        st1=1
        sg0=0
        sg1=0
        sdd=0
        sdf=0
        for snc in [0, 1]:
            for buf in [0,1,2]:
                sdd = buf//2
                sdf = buf%2
                fe_cfg_info = dat.dat_fe_only_cfg(sts=sts, swdac=swdac, dac=dac, snc=snc, sg0=sg0, sg1=sg1, st0=st0, st1=st1, slk0=slk0, slk1=slk1, sdd=sdd, sdf=sdf) 
        
                if snc == 0:
                    minval = Vref - (50/185) 
                else:
                    minval = Vref - (100/185) 
                vals = np.arange(Vref,minval,(minval-Vref)/10)
                for val in vals:
                    adac_pls_en, sts, swdac, dac = dat.dat_cali_source(cali_mode=1, val=val, period=1000, width=800) 
                    data = dat.dat_fe_qc_acq(num_samples=5)
                    cfgstr = "CALI_DATDAC_%dmV_SDD%d_SDF%d_SNC%d"%(int(val*1000), sdd, sdf, snc)
                    print (cfgstr)
                    datad[cfgstr] = [dat.fembs, data, val,cfg_info, fe_cfg_info]
        
                fp = fdir + "QC_CALI_DATDAC" + ".bin"
                with open(fp, 'wb') as fn:
                    pickle.dump(datad, fn)
    tt.append(time.time())
    print ("save_fdir_start_%s_end_save_fdir"%fdir)
    print ("save_file_start_%s_end_save_file"%fp)
    print ("Done! Pass!, it took %d seconds"%(tt[-1]-tt[-2]))

      
if 63 in tms:
    if True:
        print ("perform DIRECT-input DAC calibration under 14mV/fC, 2us")
        adac_pls_en, sts, swdac, dac = dat.dat_cali_source(cali_mode=0, val=Vref, period=1000, width=800) 
        cfg_info = dat.dat_fe_qc_cfg(adac_pls_en=adac_pls_en, sts=sts, swdac=swdac, dac=dac) 
        datad = {}
        datad['logs'] = logs
    
        slk0=0
        slk1=0
        st0=1
        st1=1
        sg0=0
        sg1=0
        sdd=0
        sdf=0
        for snc in [0, 1]:
    #        for buf in [0,1,2]:
    #            sdd = buf//2
    #            sdf = buf%2
            fe_cfg_info = dat.dat_fe_only_cfg(sts=sts, swdac=swdac, dac=dac, snc=snc, sg0=sg0, sg1=sg1, st0=st0, st1=st1, slk0=slk0, slk1=slk1, sdd=sdd, sdf=sdf) 
    
            if snc == 0:
                minval = Vref - (50/1000) 
            else:
                minval = Vref - (100/1000) 
            vals = np.arange(Vref,minval,(minval-Vref)/10)
            for val in vals:
                adac_pls_en, sts, swdac, dac = dat.dat_cali_source(cali_mode=0, val=val, period=1000, width=800) 
                data = dat.dat_fe_qc_acq(num_samples=5)
                cfgstr = "CALI_SNC%d_DIRECT_%dmV"%(snc, int(val*1000))
                print (cfgstr)
                datad[cfgstr] = [dat.fembs, data, val,cfg_info, fe_cfg_info]
    
        fp = fdir + "QC_CALI_DIRECT" + ".bin"
        with open(fp, 'wb') as fn:
            pickle.dump(datad, fn)
    tt.append(time.time())
    print ("save_fdir_start_%s_end_save_fdir"%fdir)
    print ("save_file_start_%s_end_save_file"%fp)
    print ("Done! Pass!, it took %d seconds"%(tt[-1]-tt[-2]))

if 64 in tms:
    if True:
        print ("perform ASIC-DAC calibration under 4.7mV/fC, 2us")
        adac_pls_en, sts, swdac, dac = dat.dat_cali_source(cali_mode=2, asicdac=0)
        cfg_info = dat.dat_fe_qc_cfg(adac_pls_en=adac_pls_en, sts=sts, swdac=swdac, dac=dac) 
        datad = {}
        datad['logs'] = logs
    
        slk0=0
        slk1=0
        st0=1
        st1=1
        sg0=1
        sg1=1
        sdd=0
        sdf=0
        for snc in [0, 1]:
            if snc == 0:
                maxdac = 32
            else:
                maxdac = 64
            for dac in range(0, maxdac, maxdac//8):
                fe_cfg_info = dat.dat_fe_only_cfg(sts=sts, swdac=swdac, dac=dac, snc=snc, sg0=sg0, sg1=sg1, st0=st0, st1=st1, slk0=slk0, slk1=slk1, sdd=sdd, sdf=sdf) 
                data = dat.dat_fe_qc_acq(num_samples=5)
                cfgstr = "CALI_SNC%d_ASICDAC%02d"%(snc,dac)
                print (cfgstr)
                datad[cfgstr] = [dat.fembs, data, cfg_info, fe_cfg_info]
    
        fp = fdir + "QC_CALI_ASICDAC_47" + ".bin"
        with open(fp, 'wb') as fn:
            pickle.dump(datad, fn)
    tt.append(time.time())
    print ("save_fdir_start_%s_end_save_fdir"%fdir)
    print ("save_file_start_%s_end_save_file"%fp)
    print ("Done! Pass!, it took %d seconds"%(tt[-1]-tt[-2]))


if 7 in tms:
    print ("FE delay run starts...")
    datad = {}
    datad['logs'] = logs
    period = 1000
    width = 800
    val = 1.45
    adac_pls_en, sts, swdac, dac = dat.dat_cali_source(cali_mode=1, val=val, period=period, width=width)
    cfg_info = dat.dat_fe_qc_cfg(adac_pls_en=adac_pls_en, sts=sts, swdac=swdac, dac=dac) 
    
    for phase in range(0,32,1):
        dat.cdpoke(0, 0xC, 0, dat.DAT_TEST_PULSE_DELAY, phase%32)  #cali input
        time.sleep(0.1)
        data = dat.dat_fe_qc_acq(num_samples = 5)
        datad["Phase%04d_freq%04d"%(phase, period)] =[dat.fembs, data, cfg_info, phase, period, width, val]
    
    fp = fdir + "QC_DLY_RUN" + ".bin"
    with open(fp, 'wb') as fn:
        pickle.dump(datad, fn)
    tt.append(time.time())
    print ("save_fdir_start_%s_end_save_fdir"%fdir)
    print ("save_file_start_%s_end_save_file"%fp)
    print ("Done! Pass!, it took %d seconds"%(tt[-1]-tt[-2]))


if 8 in tms:
    print ("FE cali-cap measurement starts...")
    datad = {}
    datad['logs'] = logs

    #bl200mV
    snc=1
    #3.0us
    st0=0
    st1=1
    if dat.rev == 0:
        if True:
            #4.7mV/fC
            sg0=1
            sg1=1
            cali_vals=[0.6, 1.4]
            dire_vals=[1.40, 1.55]
        if False:
            #7.8mV/fC
            sg0=0
            sg1=1
            cali_vals=[0.95, 1.55]
            dire_vals=[1.47, 1.57]
        if False:
            #14mV/fC
            sg0=0
            sg1=0
            cali_vals=[1.2, 1.55]
            dire_vals=[1.52, 1.58]
    if dat.rev == 1:
        if True:
            #4.7mV/fC
            sg0=1
            sg1=1
            cali_vals=[0.1, 0.9]
            dire_vals=[0.95, 1.05]
        if False:
            #7.8mV/fC
            sg0=0
            sg1=1
            cali_vals=[0.5, 1.00]
            dire_vals=[1.00, 1.07]
        if False:
            #14mV/fC
            sg0=0
            sg1=0
            cali_vals=[0.8, 1.05]
            dire_vals=[1.03, 1.08]

    
    period = 1000
    width = 800
    
    cfg_info = dat.dat_fe_qc_cfg() #default setting 
    
    for chn in range(16):
        print ("DAC DAT cali for FE CH%02d"%chn)
        val = 1.4
        adac_pls_en, sts, swdac, dac = dat.dat_cali_source(cali_mode=1, val=val, period=period, width=width)
        cali_fe_info = dat.dat_fe_only_cfg(snc=snc, sg0=sg0, sg1=sg1, st0=st0, st1=st1, sts=sts, swdac=swdac, chn=chn) #direct input, tp=3us, sg=4.7mV
        
        for val in cali_vals:
            valint = int(val*65536/dat.ADCVREF)
            dat.dat_set_dac(val=valint, fe_cal=0)
            data = dat.dat_fe_qc_acq(num_samples=5)
            datad["FECHN%02d_%04dmV_CALI"%(chn, int(val*1000))] = [dat.fembs, data, chn, val, period, width, cali_fe_info, cfg_info]
        
        #inject directly (cali)
        val = 1.4
        print ("inject directly (cali) for FE CH%02d"%chn)
        adac_pls_en, sts, swdac, dac = dat.dat_cali_source(cali_mode=0, val=val, period=period, width=width)
        chn_sel = 0x01<<chn
        dat.cdpoke(0, 0xC, 0, dat.DAT_FE_IN_TST_SEL_MSB, (chn_sel>>8)&0xff)   #direct input
        dat.cdpoke(0, 0xC, 0, dat.DAT_FE_IN_TST_SEL_LSB, chn_sel&0xff)   #direct input
        direct_fe_info = dat.dat_fe_only_cfg(snc=snc, sg0=sg0, sg1=sg1, st0=st0, st1=st1, sts=0, swdac=0, chn=chn) #direct input, tp=3us, sg=4.7mV
        
        for val in  dire_vals:
            val = int(val*1000)/1000.0
            dat.dat_set_dac(val=valint, fe_cal=0)
            data = dat.dat_fe_qc_acq(num_samples=5)
            datad["FECHN%02d_%04dmV_INPUT"%(chn, int(val*1000))] = [dat.fembs, data, chn, val, period, width, direct_fe_info, cfg_info]
    
    fp = fdir + "QC_Cap_Meas" + ".bin"
    with open(fp, 'wb') as fn:
        pickle.dump(datad, fn)

    tt.append(time.time())
    print ("save_fdir_start_%s_end_save_fdir"%fdir)
    print ("save_file_start_%s_end_save_file"%fp)
    print ("Done! Pass!, it took %d seconds"%(tt[-1]-tt[-2]))

if 9 in tms:
    print ("Turn DAT off")
    dat.femb_powering([])
    tt.append(time.time())
    print ("It took %d seconds in total for the entire test"%(tt[-1]-tt[0]))
    #print ("\033[92m  please move data in folder ({}) to the PC and perform the analysis script \033[0m".format(fdir))
    #print ("\033[92m  Well done \033[0m")
    print ("Done! Pass!, it took %d seconds"%(tt[-1]-tt[-2]))


if 22 in tms: #debugging
    chkdata = dat.dat_asic_chk()

