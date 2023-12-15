from wib_cfgs import WIB_CFGS
import time
import sys
import pickle
import copy
import os
import datetime
from QC_tools import ana_tools
import QC_check
import components.assembly_parameter as paras
import components.assembly_log as log
import components.assembly_function as a_func
import numpy as np

qc_tools = ana_tools()
def CreateFolders(fembNo, env, toytpc):

    datadir = "./CHK/"
    for key,femb_no in fembNo.items():
        datadir = datadir + "femb{}_".format(femb_no)

    datadir = datadir+"{}_{}".format(env,toytpc)
    n=1
    while (os.path.exists(datadir)):
        if n==1:
            datadir = datadir + "_R{:03d}".format(n)
        else:
            datadir = datadir[:-3] + "{:03d}".format(n)
        n=n+1
        if n>20:
            raise Exception("There are more than 20 folders...")

    try:
        os.makedirs(datadir)
    except OSError:
        print ("Error to create folder %s"%datadir)
        sys.exit()

    datadir = datadir+"/"


    return datadir

####### Input FEMB slots #######

if len(sys.argv) < 2:
    print('Please specify at least one FEMB # to test')
    print('e.g. python3 quick_checkout.py 0')
    exit()

if 'save' in sys.argv:
    save = True
    for i in range(len(sys.argv)):
        if sys.argv[i] == 'save':
            pos = i
            break
    sample_N = int(sys.argv[pos+1] )
    sys.argv.remove('save')
    fembs = [int(a) for a in sys.argv[1:pos]]
else:
    save = False
    sample_N = 1
    fembs = [int(a) for a in sys.argv[1:]]


####### Input test information #######
if save:
    logs={}
    tester=input("please input your name:  ")
    logs['tester']=tester
    
    env_cs = input("Test is performed at cold(LN2) (Y/N)? : ")
    if ("Y" in env_cs) or ("y" in env_cs):
        env = "LN"
    else:
        env = "RT"
    logs['env']=env
    
    ToyTPC_en = input("ToyTPC at FE inputs (Y/N) : ")
    if ("Y" in ToyTPC_en) or ("y" in ToyTPC_en):
        toytpc = "150pF"
    else:
        toytpc = "0pF"
    logs['toytpc']=toytpc
    
    note = input("A short note (<200 letters):")
    logs['note']=note
    
    fembNo={}
    for i in fembs:
        fembNo['femb{}'.format(i)]=input("FEMB{} ID: ".format(i))
    
    logs['femb id']=fembNo
    logs['date']=datetime.datetime.now().strftime("%m_%d_%Y_%H_%M_%S")

    datadir=CreateFolders(fembNo, env, toytpc)
    fp = datadir + "logs_env.bin"
    with open(fp, 'wb') as fn:
        pickle.dump(logs, fn)

outfile = open(datadir+"chk_logs.txt", "w")
t1 = time.time()

################## Power on FEMBs and check currents ##################
chk = WIB_CFGS()
chk.wib_fw()
para_initial = paras.para(env)

# set FEMB voltages
chk.fembs_vol_set(vfe = paras.voltage_FE, vcd = paras.voltage_COLDATA, vadc = paras.voltage_ColdADC)
print("Check FEMB currents")

fembs_remove = []
for ifemb in fembs:
    chk.femb_powering_single(ifemb, 'on')
    pwr_meas1 = chk.get_sensors()

    bias_i  =   round(pwr_meas1['FEMB%d_BIAS_I'%ifemb],3)
    fe_i    =   round(pwr_meas1['FEMB%d_DC2DC0_I'%ifemb],3)
    cd_i    =   round(pwr_meas1['FEMB%d_DC2DC1_I'%ifemb],3)
    adc_i   =   round(pwr_meas1['FEMB%d_DC2DC2_I'%ifemb],3)

    hasERROR = False
    if abs(bias_i)>paras.bias_i_low:
       print("ERROR: FEMB{} BIAS current |{}|>0.05A".format(ifemb,bias_i)) 
       hasERROR = True

    if fe_i > paras.fe_i_high or fe_i < paras.fe_i_low:
       print("ERROR: FEMB{} LArASIC current {} out of range (0.3A,0.6A)".format(ifemb,fe_i)) 
       hasERROR = True

    if cd_i>paras.cd_i_high  or cd_i<paras.cd_i_low :
       print("ERROR: FEMB{} COLDATA current {} out of range (0.1A,0.3A)".format(ifemb,cd_i)) 
       hasERROR = True

    if adc_i>paras.adc_i_high or adc_i<paras.adc_i_low:
       print("ERROR: FEMB{} ColdADC current {} out of range (1.2A,1.8A)".format(ifemb,adc_i)) 
       hasERROR = True

    if hasERROR:
       print("FEMB ID {} faild current check, will skip this femb".format(fembNo['femb%d'%ifemb]))
       outfile.write("FEMB ID {} faild current #1 check\n".format(fembNo['femb%d'%ifemb]))
       outfile.write("BIAS current: %f (default range: <0.05A)\n"%bias_i)
       outfile.write("LArASIC current: %f (default range: (0.3A, 0.6A)) \n"%fe_i)
       outfile.write("COLDATA current: %f (default range: (0.1A, 0.3A))\n"%cd_i)
       outfile.write("ColdADC current: %f (default range: (1.2A, 1.9A))\n"%adc_i)
       #fembs.remove(ifemb)
       fembs_remove.append(ifemb)
       fembNo.pop('femb%d'%ifemb)
       chk.femb_powering_single(ifemb, 'off')
 
for femb_id in fembs_remove:
    fembs.remove(femb_id)

if len(fembs) == 0:
    print ("All FEMB fail, exit anyway")
    exit()
       
chk.femb_powering(fembs)

################# check the default COLDATA and COLDADC register ##################
if True:    
    print("Check FEMB registers")
    chk.femb_cd_rst()
    chk.femb_cd_rst()
    time.sleep(0.1)
    for ifemb in fembs:
        chk.femb_cd_fc_act(ifemb, act_cmd="rst_adcs")
        chk.femb_cd_fc_act(ifemb, act_cmd="rst_adcs")
        time.sleep(0.01)
        chk.femb_cd_fc_act(ifemb, act_cmd="rst_larasics")
        chk.femb_cd_fc_act(ifemb, act_cmd="rst_larasics")
        time.sleep(0.01)
        chk.femb_cd_fc_act(ifemb, act_cmd="rst_larasic_spi")
        chk.femb_cd_fc_act(ifemb, act_cmd="rst_larasics")
    time.sleep(0.1)
    for ifemb in fembs:
        errflag = chk.femb_cd_chkreg(ifemb)
        if errflag:
           print("FEMB ID {} faild COLDATA register check 1, continue testing".format(fembNo['femb%d'%ifemb]))
           outfile.write("FEMB ID {} faild COLDATA register 1 check\n".format(fembNo['femb%d'%ifemb]))
           #fembs.remove(ifemb)
           #fembNo.pop('femb%d'%ifemb)
           continue
    
        errflag = chk.femb_adc_chkreg(ifemb)
        if errflag:
           print("FEMB ID {} faild COLDADC register check 1, continue testing".format(fembNo['femb%d'%ifemb]))
           outfile.write("FEMB ID {} faild COLDADC register 1 check\n".format(fembNo['femb%d'%ifemb]))
           #fembs.remove(ifemb)
           #fembNo.pop('femb%d'%ifemb)

    ################ reset COLDATA, COLDADC and LArASIC ##############
    print("Reset FEMBs")
    chk.femb_cd_rst()
    chk.femb_cd_rst()
    time.sleep(0.1)
    for ifemb in fembs:
        chk.femb_cd_fc_act(ifemb, act_cmd="rst_adcs")
        time.sleep(0.01)
        chk.femb_cd_fc_act(ifemb, act_cmd="rst_adcs")
        time.sleep(0.01)
        chk.femb_cd_fc_act(ifemb, act_cmd="rst_larasics")
        chk.femb_cd_fc_act(ifemb, act_cmd="rst_larasics")
        time.sleep(0.01)
        chk.femb_cd_fc_act(ifemb, act_cmd="rst_larasic_spi")
        chk.femb_cd_fc_act(ifemb, act_cmd="rst_larasic_spi")
    
    time.sleep(0.1)
    ################ check the default COLDATA and COLDADC register ###########
    print("Check FEMB registers second times")
    for ifemb in fembs:
        errflag = chk.femb_cd_chkreg(ifemb)
        if errflag:
           print("FEMB ID {} faild COLDATA register check 2".format(fembNo['femb%d'%ifemb]))
           strcs = input ("skip this femb? (Y/N)")
           if "Y" in strcs or "y" in strcs:
               pass
           else:
               print ("Exit anyway...")
               exit()
           outfile.write("FEMB ID {} faild COLDATA register 2 check\n".format(fembNo['femb%d'%ifemb]))
           fembs.remove(ifemb)
           fembNo.pop('femb%d'%ifemb)
           continue
    
        errflag = chk.femb_adc_chkreg(ifemb)
        if errflag:
           print("FEMB ID {} faild COLDADC register check 2".format(fembNo['femb%d'%ifemb]))
           strcs = input ("skip this femb? (Y/N)")
           if "Y" in strcs or "y" in strcs:
               pass
           else:
               print ("Exit anyway...")
               exit()

           outfile.write("FEMB ID {} faild COLDADC register 2 check\n".format(fembNo['femb%d'%ifemb]))
           fembs.remove(ifemb)
           fembNo.pop('femb%d'%ifemb)

if len(fembs) == 0:
   print ("All FEMB fail, exit anyway")
   exit()
   
################# enable certain fembs ###################
chk.wib_femb_link_en(fembs)

#   create report dir
datareport = a_func.CreateFolders(fembs, fembNo, env, toytpc, datadir)

################ Measure RMS at 200mV, 14mV/fC, 2us ###################
print("Take RMS data")
snc = 1 # 200 mV
sg0 = 0
sg1 = 0 # 14mV/fC
st0 = 1
st1 = 1 # 2us 

# configuration
chk.femb_cd_rst()
cfg_paras_rec = []
for i in range(8):
    chk.adcs_paras[i][8]=1   # enable  auto
for femb_id in fembs:
    chk.set_fe_board(sts=0, snc=snc, sg0=sg0, sg1=sg1, st0=st0, st1=st1, swdac=0, dac=0x00 )
    adac_pls_en = 0
    cfg_paras_rec.append( (femb_id, copy.deepcopy(chk.adcs_paras), copy.deepcopy(chk.regs_int8), adac_pls_en) )
    chk.femb_cfg(femb_id, adac_pls_en )
chk.data_align(fembs)
time.sleep(1)
# data acquire
rms_rawdata = chk.spybuf_trig(fembs=fembs, num_samples=sample_N, trig_cmd=0) #returns list of size 1

# data analysis ========================
fname = "Raw_SE_{}_{}_{}_0x{:02x}".format("200mVBL","14_0mVfC","2_0us",0x00)
pldata = qc_tools.data_decode(rms_rawdata, fembs)
for ifemb in range(len(fembs)):
    ped,rms=qc_tools.GetRMS(pldata, fembs[ifemb], datareport[fembs[ifemb]], fname)
    tmp = QC_check.CHKPulse(ped)
    log.chkflag["BL"].append(tmp[0])
    log.badlist["BL"].append(tmp[1])

    tmp = QC_check.CHKPulse(rms)
    log.chkflag["RMS"].append(tmp[0])
    log.badlist["RMS"].append(tmp[1])
#   =====================================
#   save data
if save:
    fp = datadir + fname + ".bin"
    with open(fp, 'wb') as fn:
        pickle.dump( [rms_rawdata, cfg_paras_rec, fembs], fn)

################ Measure FEMB current 2 ####################
print("Check FEMB current")
pwr_meas2 = chk.get_sensors()
for ifemb in fembs:
    bias_i = round(pwr_meas2['FEMB%d_BIAS_I'%ifemb],3)  
    fe_i = round(pwr_meas2['FEMB%d_DC2DC0_I'%ifemb],3)
    cd_i = round(pwr_meas2['FEMB%d_DC2DC1_I'%ifemb],3)
    adc_i = round(pwr_meas2['FEMB%d_DC2DC2_I'%ifemb],3)

    hasERROR = False
    if bias_i>0.15 or bias_i<-0.02:
       print("ERROR: FEMB{} BIAS current {} out of range (-0.02A,0.05A)".format(ifemb,bias_i)) 
       hasERROR = True

    if fe_i>0.55 or fe_i<0.35:
       print("ERROR: FEMB{} LArASIC current {} out of range (0.35A,0.55A)".format(ifemb,fe_i)) 
       hasERROR = True

    if cd_i>0.35 or cd_i<0.15:
       print("ERROR: FEMB{} COLDATA current {} out of range (0.15A,0.35A)".format(ifemb,cd_i)) 
       hasERROR = True

    if adc_i>1.85 or adc_i<1.35:
       print("ERROR: FEMB{} ColdADC current {} out of range (1.35A,1.85A)".format(ifemb,adc_i)) 
       hasERROR = True

    if hasERROR:
       print("FEMB ID {} faild current check 2. But test will continue".format(fembNo['femb%d'%ifemb]))
       outfile.write("FEMB ID {} faild current #2 check\n".format(fembNo['femb%d'%ifemb]))
       outfile.write("BIAS current: %f (default range: (-0.02A, 0.05A))\n"%bias_i)
       outfile.write("LArASIC current: %f (default range: (0.35A, 0.55A))\n"%fe_i)
       outfile.write("COLDATA current: %f (default range: (0.15A, 0.35A))\n"%cd_i)
       outfile.write("ColdADC current: %f (default range: (1.35A, 1.85A))\n"%adc_i)

if save:
    fp = datadir + "PWR_SE_{}_{}_{}_0x{:02x}.bin".format("200mVBL","14_0mVfC","2_0us",0x00)
    with open(fp, 'wb') as fn:
        pickle.dump([pwr_meas2, fembs], fn)


#   power analysis
pwr_meas=pwr_meas2
#for ifemb in fembs:
for ifemb in range(len(fembs)):
    fp_pwr = datareport[fembs[ifemb]]+"pwr_meas"
    qc_tools.PrintPWR(pwr_meas, fembs[ifemb], fp_pwr)
    tmp=QC_check.CHKPWR(pwr_meas,fembs[ifemb])
    log.chkflag["PWR"].append(tmp[0])
    log.badlist["PWR"].append(tmp[1])

################# monitoring power rails ###################

power_rail_d = a_func.monitor_power_rail("SE", fembs, datadir, save)
power_rail_a = a_func.monitor_power_rail_analysis("SE", datadir, datareport)

############ Take pulse data 900mV 14mV/fC 2us ##################
print("Take single-ended pulse data")
snc = 0 # 900 mV
sg0 = 0
sg1 = 0 # 14mV/fC
st0 = 1
st1 = 1 # 2us 

#   initial configuration
chk.femb_cd_rst()
cfg_paras_rec = []
for i in range(8):
    chk.adcs_paras[i][8]=1   # enable  auto

for femb_id in fembs:
    chk.set_fe_board(sts=1, snc=snc, sg0=sg0, sg1=sg1, st0=st0, st1=st1, swdac=1, dac=0x10 )
    adac_pls_en = 1
    cfg_paras_rec.append( (femb_id, copy.deepcopy(chk.adcs_paras), copy.deepcopy(chk.regs_int8), adac_pls_en) )
    chk.femb_cfg(femb_id, adac_pls_en )

chk.data_align(fembs)
time.sleep(1)
#   data acquire
pls_rawdata = chk.spybuf_trig(fembs=fembs, num_samples=sample_N, trig_cmd=0) #returns list of size 1

#   data analysis
fname = "Raw_SE_{}_{}_{}_0x{:02x}.bin".format("900mVBL","14_0mVfC","2_0us",0x10)
pldata = qc_tools.data_decode(pls_rawdata, fembs)

for ifemb in range(len(fembs)):
    ppk,npk,bl=qc_tools.GetPeaks(pldata, fembs[ifemb], datareport[fembs[ifemb]], fname, funcfit=False)
    # outfp = datareport[fembs[ifemb]] + "pulse_{}.bin".format(fname)
    # with open(outfp, 'wb') as fn:
    #      pickle.dump([ppk,npk,bl], fn)

    tmp = QC_check.CHKPulse(ppk)
    log.chkflag["Pulse_SE"]["PPK"].append(tmp[0])
    log.badlist["Pulse_SE"]["PPK"].append(tmp[1])

    tmp = QC_check.CHKPulse(npk)
    log.chkflag["Pulse_SE"]["NPK"].append(tmp[0])
    log.badlist["Pulse_SE"]["NPK"].append(tmp[1])

    tmp = QC_check.CHKPulse(bl)
    log.chkflag["Pulse_SE"]["BL"].append(tmp[0])
    log.badlist["Pulse_SE"]["BL"].append(tmp[1])

if save:
    fp = datadir + fname
    with open(fp, 'wb') as fn:
        pickle.dump( [pls_rawdata, cfg_paras_rec, fembs], fn)

############ Take pulse data 900mV 14mV/fC 2us (DIFF) ##################
print("Take differential pulse data")
chk.femb_cd_rst()
cfg_paras_rec = []
for i in range(8):
    chk.adcs_paras[i][2]=1   # enable differential 
    chk.adcs_paras[i][8]=1   # enable  auto
for femb_id in fembs:
    chk.set_fe_board(sts=1, snc=snc, sg0=sg0, sg1=sg1, st0=st0, st1=st1, sdd=1, swdac=1, dac=0x10 )
    adac_pls_en = 1
    cfg_paras_rec.append( (femb_id, copy.deepcopy(chk.adcs_paras), copy.deepcopy(chk.regs_int8), adac_pls_en) )
    chk.femb_cfg(femb_id, adac_pls_en )

chk.data_align(fembs)
time.sleep(5)

#   data acquire
pls_rawdata = chk.spybuf_trig(fembs=fembs, num_samples=sample_N, trig_cmd=0) #returns list of size 1
#   data save
if save:
    fp = datadir + fname + ".bin"
    with open(fp, 'wb') as fn:
        pickle.dump( [pls_rawdata, cfg_paras_rec, fembs], fn)

#   data analysis
fname = "Raw_DIFF_{}_{}_{}_0x{:02x}".format("900mVBL","14_0mVfC","2_0us",0x10)
pldata = qc_tools.data_decode(pls_rawdata, fembs)
for ifemb in range(len(fembs)):
    ppk,npk,bl=qc_tools.GetPeaks(pldata, fembs[ifemb], datareport[fembs[ifemb]], fname)

    tmp = QC_check.CHKPulse(ppk)
    log.chkflag["Pulse_DIFF"]["PPK"].append(tmp[0])
    log.badlist["Pulse_DIFF"]["PPK"].append(tmp[1])

    tmp = QC_check.CHKPulse(npk)
    log.chkflag["Pulse_DIFF"]["NPK"].append(tmp[0])
    log.badlist["Pulse_DIFF"]["NPK"].append(tmp[1])

    tmp = QC_check.CHKPulse(bl)
    log.chkflag["Pulse_DIFF"]["BL"].append(tmp[0])
    log.badlist["Pulse_DIFF"]["BL"].append(tmp[1])

######   6   DIFF monitor power rails   ######
power_rail_d = a_func.monitor_power_rail("DIFF", fembs, datadir, save)
power_rail_a = a_func.monitor_power_rail_analysis("DIFF", datadir, datareport)


######  7   Take monitoring data #######
#   initial ColdADC, COLDATA
chk.femb_cd_rst()
#   data acquisition
mon_refs, mon_temps, mon_adcs = a_func.monitoring_path(fembs, snc, sg0,sg1,datadir, save)
#   data analysis
nchips = range(8)
qc_tools.PrintMON(fembs, nchips, mon_refs, mon_temps, mon_adcs, datareport, makeplot = True)

for ifemb in range(len(fembs)):
    tmp = QC_check.CHKFET(mon_temps,fembs[ifemb],nchips,env)
    log.chkflag["MON_T"].append(tmp[0])
    log.badlist["MON_T"].append(tmp[1])

    tmp = QC_check.CHKFEBGP(mon_refs,fembs[ifemb],nchips)
    log.chkflag["MON_BGP"].append(tmp[0])
    log.badlist["MON_BGP"].append(tmp[1])

    tmp = QC_check.CHKADC(mon_adcs,fembs[ifemb],nchips,"VCMI",900,950)
    log.chkflag["MON_ADC"]["VCMI"].append(tmp[0])
    log.badlist["MON_ADC"]["VCMI"].append(tmp[1])

    tmp = QC_check.CHKADC(mon_adcs,fembs[ifemb],nchips,"VCMO",1200,1250)
    log.chkflag["MON_ADC"]["VCMO"].append(tmp[0])
    log.badlist["MON_ADC"]["VCMO"].append(tmp[1])

    tmp = QC_check.CHKADC(mon_adcs,fembs[ifemb],nchips,"VREFP",1900,1950)
    log.chkflag["MON_ADC"]["VREFP"].append(tmp[0])
    log.badlist["MON_ADC"]["VREFP"].append(tmp[1])

    tmp = QC_check.CHKADC(mon_adcs,fembs[ifemb],nchips,"VREFN",460,510)
    log.chkflag["MON_ADC"]["VREFN"].append(tmp[0])
    log.badlist["MON_ADC"]["VREFN"].append(tmp[1])

    tmp = QC_check.CHKADC(mon_adcs,fembs[ifemb],nchips,"VSSA",0,70)
    log.chkflag["MON_ADC"]["VSSA"].append(tmp[0])
    log.badlist["MON_ADC"]["VSSA"].append(tmp[1])

####### Power off FEMBs #######
print("Turning off FEMBs")
chk.femb_powering([])

t2=time.time()
print(t2-t1)

