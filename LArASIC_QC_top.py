import time
import sys
import numpy as np
import pickle
import copy
import time, datetime, random, statistics    
import os
from dat_cfg import DAT_CFGS
from DAT_user_input import dat_user_input
                
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

wib_time = datetime.datetime.now().strftime("%m-%d-%Y %H:%M:%S")
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

while True:
    datowib=input("\033[95m Is DAT on WIB slot 0? (Y/N) : \033[0m")
    if ("Y" in datowib) or ("y" in datowib):
        fembs = [0]
        break
    else:
        print ("\033[91m Please contact tech coordinator...\033[0m")
        print ("Exit anyway")
        exit()

dat.fembs = fembs

tt = []
tt.append(time.time())

logs = {}
tms=[0]
####### Init check information #######
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
    cds_pwr_info = dat.cd_pwr_meas()
    datad["CD_PWRON"] = cds_pwr_info
    dat.asic_init_pwrchk(fes_pwr_info, adcs_pwr_info, cds_pwr_info)
    chkdata = dat.dat_asic_chk()
    datad.update(chkdata)
    print ("FE mapping to be done")
    print ("FE mapping to be done")
    print ("FE mapping to be done")
    print ("FE mapping to be done")
    print ("FE mapping to be done")
    logsd, fdir, tms= dat_user_input(infile_mode=True)
    logs.update(logsd)
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
    print ("FE power consumption measurement starts...")
    datad = {}
    datad['logs'] = logs
    for snc in [0, 1]:
        for sdd in [0, 1]:
            for sdf in [0, 1]:
                if (sdd == 1) and (sdf==1):
                    continue
                else:
                    adac_pls_en, sts, swdac, dac = dat.dat_cali_source(cali_mode=2, asicdac=0x10)
                    rawdata = dat.dat_fe_qc(adac_pls_en=adac_pls_en, sts=sts, swdac=swdac, dac=dac,snc=snc, sdd=sdd, sdf=sdf ) 
                    pwr_meas = dat.fe_pwr_meas()
                    datad["PWR_SDD%d_SDF%d_SNC%d"%(sdd,sdf,snc)] = [dat.fembs, rawdata[0], rawdata[1], pwr_meas]
    
    fp = fdir + "QC_PWR" + ".bin"
    with open(fp, 'wb') as fn:
        pickle.dump(datad, fn)
    tt.append(time.time())
    print ("FE power consumption measurement is done. it took %d seconds"%(tt[-1]-tt[-2]))

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
    for sg0 in [0,1]:
        for sg1 in [0,1]:
            fe_cfg_info = dat.dat_fe_only_cfg(sts=sts, swdac=swdac, dac=dac, snc=snc, sg0=sg0, sg1=sg1, st0=st0, st1=st1, slk0=slk0, slk1=slk1, sdd=sdd, sdf=sdf) 
            data = dat.dat_fe_qc_acq(num_samples=1)
            cfgstr = "CHK_GAINs_SDD%d_SDF%d_SLK0%d_SLK1%d_SNC%d_ST0%d_ST1%d_SG0%d_SG1%d"%(sdd, sdf, slk0, slk1, snc, st0, st1, sg0, sg1)
            datad[cfgstr] = [dat.fembs, data, cfg_info, fe_cfg_info]
    sg0=0
    sg1=0
    
    #response under different output modes
    for buf in [0,1,2]:
        sdd = buf//2
        sdf = buf%2
        fe_cfg_info = dat.dat_fe_only_cfg(sts=sts, swdac=swdac, dac=dac, snc=snc, sg0=sg0, sg1=sg1, st0=st0, st1=st1, slk0=slk0, slk1=slk1, sdd=sdd, sdf=sdf) 
        data = dat.dat_fe_qc_acq(num_samples=1)
        cfgstr = "CHK_OUTPUT_SDD%d_SDF%d_SLK0%d_SLK1%d_SNC%d_ST0%d_ST1%d_SG0%d_SG1%d"%(sdd, sdf, slk0, slk1, snc, st0, st1, sg0, sg1)
        datad[cfgstr] = [dat.fembs, data, cfg_info, fe_cfg_info]
    
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
    print ("FE CHECK RESPONSE is done. it took %d seconds"%(tt[-1]-tt[-2]))


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
    print ("FE monitoring measurement is done. it took %d seconds"%(tt[-1]-tt[-2]))

if 4 in tms:
    print ("FE power cycling measurement starts...")
    cycle_times = 8
    
    datad = {}
    datad['logs'] = logs
    
    for ci in range(cycle_times):
        dat.dat_pwroff_chk() #make sure DAT is off
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
            adac_pls_en, sts, swdac, dac = dat.dat_cali_source(cali_mode=1, val=1.53, period=500, width=400)
            rawdata = dat.dat_fe_qc(adac_pls_en=adac_pls_en, sts=sts, swdac=swdac, dac=dac,snc=1, sdd=0, sdf=0 ) #200mV, 500pA, SDD off, SDF off, DAT-DAC
        if cseti == 5:
            adac_pls_en, sts, swdac, dac = dat.dat_cali_source(cali_mode=1, val=1.53, period=500, width=400)
            rawdata = dat.dat_fe_qc(adac_pls_en=adac_pls_en, sts=sts, swdac=swdac, dac=dac, snc=1, sdd=1, sdf=0 ) #200mV, 500pA, SDD on, SDF off, DAT-DAC
        if cseti == 6:
            adac_pls_en, sts, swdac, dac = dat.dat_cali_source(cali_mode=1, val=1.53, period=500, width=400)
            rawdata = dat.dat_fe_qc(adac_pls_en=adac_pls_en, sts=sts, swdac=swdac, dac=dac, snc=1, sdd=0, sdf=1 ) #200mV, 500pA, SDD off, SDF on, DAT-DAC
        if cseti == 7:
            adac_pls_en, sts, swdac, dac = dat.dat_cali_source(cali_mode=0, val=1.53, period=500, width=400)
            rawdata = dat.dat_fe_qc(adac_pls_en=adac_pls_en, sts=sts, swdac=swdac, dac=dac, snc=1, sdd=0, sdf=0 ) #200mV, 500pA, SDD off, SDF off, Direct-input
    
        fes_pwr_info = dat.fe_pwr_meas()
        adcs_pwr_info = dat.adc_pwr_meas()
        cds_pwr_info = dat.cd_pwr_meas()
    
        datad["PwrCycle_%d"%cseti] = [dat.fembs, rawdata[0], rawdata[1], fes_pwr_info, adcs_pwr_info, cds_pwr_info]
    
    fp = fdir + "QC_PWR_CYCLE" + ".bin"
    with open(fp, 'wb') as fn:
        pickle.dump(datad, fn)
    tt.append(time.time())
    print ("FE power cycling measurement is done. it took %d seconds"%(tt[-1]-tt[-2]))
    
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
    print ("FE noise measurement is done. it took %d seconds"%(tt[-1]-tt[-2]))

if 6 in tms:
    print ("FE calibration measurement starts...")

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
       
    Vref = 1.583
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
    print ("FE calibration measurement is done. it took %d seconds"%(tt[-1]-tt[-2]))

if 7 in tms:
    print ("FE delay run starts...")
    datad = {}
    datad['logs'] = logs
    period = 1000
    width = 800
    val = 1.4
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
    print ("FE delay run is done. it took %d seconds"%(tt[-1]-tt[-2]))

if 8 in tms:
    print ("FE cali-cap measurement starts...")
    datad = {}
    datad['logs'] = logs

    #bl200mV
    snc=1
    #3.0us
    st0=0
    st1=1
    Vref = 1.583
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
    
    period = 1000
    width = 800
    
    cfg_info = dat.dat_fe_qc_cfg() #default setting 
    
    for chn in range(16):
        print ("DAC DAT cali for FE CH%02d"%chn)
        val = 1.4
        adac_pls_en, sts, swdac, dac = dat.dat_cali_source(cali_mode=1, val=val, period=period, width=width)
        cali_fe_info = dat.dat_fe_only_cfg(snc=snc, sg0=sg0, sg1=sg1, st0=st0, st1=st1, sts=sts, swdac=swdac, chn=chn) #direct input, tp=3us, sg=4.7mV
        
        for val in cali_vals:
            val = int(val*1000)/1000.0
            dat.dat_set_dac(val=val, fe_cal=0)
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
            dat.dat_set_dac(val=val, fe_cal=0)
            data = dat.dat_fe_qc_acq(num_samples=5)
            datad["FECHN%02d_%04dmV_INPUT"%(chn, int(val*1000))] = [dat.fembs, data, chn, val, period, width, direct_fe_info, cfg_info]
    
    fp = fdir + "QC_Cap_Meas" + ".bin"
    with open(fp, 'wb') as fn:
        pickle.dump(datad, fn)

    tt.append(time.time())
    print ("FE cali-cap measurement is done. it took %d seconds"%(tt[-1]-tt[-2]))

if 9 in tms:
    print ("Turn DAT off")
    dat.femb_powering([])
    tt.append(time.time())
    print ("It took %d seconds in total for the entire test"%(tt[-1]-tt[0]))
    print ("\033[92m  please move data in folder ({}) to the PC and perform the analysis script \033[0m".format(fdir))
    print ("\033[92m  Well done \033[0m")

