import PIL

from wib_cfgs import WIB_CFGS
import time
import sys
import pickle
import copy
import datetime
from QC_tools import ana_tools
import QC_check
from fpdf import FPDF
import components.assembly_parameter as paras
import components.assembly_log as log
import components.assembly_function as a_func
import components.assembly_report as a_repo

qc_tools = ana_tools()
# Create an array to store the merged image

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

    datadir=a_func.Create_data_folders(fembNo, env, toytpc)
    fp = datadir + "logs_env.bin"
    with open(fp, 'wb') as fn:
        pickle.dump(logs, fn)

outfile = open(datadir+"chk_logs.txt", "w")
t1 = time.time()

log.report_log01["ITEM"] = "01 initial information"
log.report_log01["Detail"] = logs

check_item = []

################## Power on FEMBs and check currents ##################
chk = WIB_CFGS()
chk.wib_fw()
para_initial = paras.para(env)

# set FEMB voltages
chk.fembs_vol_set(vfe = paras.voltage_FE, vcd = paras.voltage_COLDATA, vadc = paras.voltage_ColdADC)
input("debug set FEMB voltages")


print("Check FEMB currents")
fembs_remove = []

log.report_log02["ITEM"] = "02 FEMB current measurement 1"
for ifemb in fembs:
    femb_id = "FEMB ID {}".format(fembNo['femb%d' % ifemb])
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
        print("FEMB ID {} Faild current check, will skip this femb".format(fembNo['femb%d'%ifemb]))
        log.report_log02[femb_id]['check_status'] = "FEMB ID {} faild current #1 check\n".format(fembNo['femb%d'%ifemb])
        log.report_log02[femb_id]["Result"] = False
        # fembs.remove(ifemb)
        fembs_remove.append(ifemb)
        fembNo.pop('femb%d' % ifemb)
        chk.femb_powering_single(ifemb, 'off')
    else:
        print("FEMB ID {} Pass current check".format(fembNo['femb%d'%ifemb]))
        log.report_log02[femb_id]['check_status'] = "FEMB Pass current #1 check\n"
        log.report_log02[femb_id]["Result"] = True
    log.report_log02[femb_id]["FC1_BIAS_current_1"] = "BIAS current: %f (default range: <0.05A)\n" % bias_i
    log.report_log02[femb_id]["FC1_LArASIC_current_1"] = "LArASIC current: %f (default range: <0.05A)\n" % fe_i
    log.report_log02[femb_id]["FC1_COLDATA_current_1"] = "COLDATA current: %f (default range: <0.05A)\n" % cd_i
    log.report_log02[femb_id]["FC1_ColdADC_current_1"] = "ColdADC current: %f (default range: <0.05A)\n" % adc_i

for femb_id in fembs_remove:
    fembs.remove(femb_id)

if len(fembs) == 0:
    print ("All FEMB fail, exit anyway")
    exit()
input("begin to check femb power")
chk.femb_powering(fembs)

################# check the default COLDATA and COLDADC register ##################
#   report in log03
if True:
    print("Check FEMB registers")
    log.report_log03["ITEM"] = "03 Check FEMB registers"
    #   reset 3-ASIC
    a_func.chip_reset(fembs)
    check1 = a_func.register_check(fembs, fembNo)
    log.report_log03.update(check1)
    ################ reset COLDATA, COLDADC and LArASIC ##############
    a_func.chip_reset(fembs)
    ################ check the default COLDATA and COLDADC register ###########
    print("Check FEMB registers second times")
    check2 = a_func.register_check(fembs, fembNo)
    for ifemb in fembs:
        femb_id = "FEMB ID {}".format(fembNo['femb%d' % ifemb])
        log.report_log03[femb_id]["state"] ="FEMB_REG_CHK_1 BEGIN"
        errflag = chk.femb_cd_chkreg(ifemb)
        if errflag:
           print("FEMB ID {} faild COLDATA register check 2".format(fembNo['femb%d'%ifemb]))
           log.report_log03[femb_id]["COLDATA_REG_CHK_2"] =("FEMB ID {} faild COLDATA register 1 check\n".format(fembNo['femb%d' % ifemb]))
           log.report_log03[femb_id]["Result01"] = False
           fembs.remove(ifemb)
           fembNo.pop('femb%d'%ifemb)
           strcs = input ("skip this femb? (Y/N)")
           if "Y" in strcs or "y" in strcs:
               pass
           else:
               print ("Exit anyway...")
               exit()
           continue
        else:
            log.report_log03[femb_id]["COLDATA_REG_CHK_2"] = ("FEMB ID {} SUCCESS\n".format(fembNo['femb%d' % ifemb]))
            log.report_log03[femb_id]["Result01"] = True

        errflag = chk.femb_adc_chkreg(ifemb)
        if errflag:
           print("FEMB ID {} faild COLDADC register check 2".format(fembNo['femb%d'%ifemb]))
           log.report_log03[femb_id]["ColdADC_REG_CHK_2"] = ("FEMB ID {} faild ColdADC register 1 check\n".format(fembNo['femb%d' % ifemb]))
           log.report_log03[femb_id]["Result02"] = False
           fembs.remove(ifemb)
           fembNo.pop('femb%d'%ifemb)
           strcs = input ("skip this femb? (Y/N)")
           if "Y" in strcs or "y" in strcs:
               pass
           else:
               print ("Exit anyway...")
               exit()
        else:
            log.report_log03[femb_id]["ColdADC_REG_CHK_2"] = ("FEMB ID {} SUCCESS\n".format(fembNo['femb%d' % ifemb]))
            log.report_log03[femb_id]["Result02"] = True

        if (log.report_log03[femb_id]["Result01"] == True) and (log.report_log03[femb_id]["Result02"] == True):
            log.report_log03[femb_id]["Result"] = True
        else:
            log.report_log03[femb_id]["Result"] = False
if len(fembs) == 0:
   print ("All FEMB fail, exit anyway")
   exit()

################# enable certain fembs ###################
chk.wib_femb_link_en(fembs)

#   create report dir
datareport = a_func.Create_report_folders(fembs, fembNo, env, toytpc, datadir)

################ Measure RMS at 200mV, 14mV/fC, 2us ###################
#   report in log04
print("Take RMS data")
log.report_log04["ITEM"] = "04 Measure RMS at 200mV, 14mV/fC, 2us"
fname = "Raw_SE_{}_{}_{}_0x{:02x}".format("200mVBL","14_0mVfC","2_0us",0x00)
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

pldata = qc_tools.data_decode(rms_rawdata, fembs)
for ifemb in range(len(fembs)):
    femb_id = "FEMB ID {}".format(fembNo['femb%d' % fembs[ifemb]])
    ped,rms=qc_tools.GetRMS(pldata, fembs[ifemb], datareport[fembs[ifemb]], fname)
    tmp = QC_check.CHKPulse(ped, 5)
    log.chkflag["BL"].append(tmp[0])
    log.badlist["BL"].append(tmp[1])
    log.report_log04[femb_id]["baseline chk_status"] = tmp[0]
    log.report_log04[femb_id]["baseline err_status"] = tmp[1]

    tmp = QC_check.CHKPulse(rms, 5)
    log.chkflag["RMS"].append(tmp[0])
    log.badlist["RMS"].append(tmp[1])
    log.report_log04[femb_id]["RMS chk_status"] = tmp[0]
    log.report_log04[femb_id]["RMS err_status"] = tmp[1]

    if (log.report_log04[femb_id]["baseline chk_status"] == False) and (log.report_log04[femb_id]["RMS chk_status"] == False):
        log.report_log04[femb_id]["Result"] = True
    else:
        log.report_log04[femb_id]["Result"] = False
#   =====================================
#   save data
if save:
    fp = datadir + fname + ".bin"
    with open(fp, 'wb') as fn:
        pickle.dump( [rms_rawdata, cfg_paras_rec, fembs], fn)

################ Measure FEMB currents 2 ####################
print("Check FEMB current")
pwr_meas2 = chk.get_sensors()
log.report_log05['ITEM'] = "05 FEMB SE current measurement 2"
for ifemb in fembs:
    femb_id = "FEMB ID {}".format(fembNo['femb%d' % ifemb])
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
        print("FEMB ID {} Faild current check 2, will skip this femb".format(fembNo['femb%d'%ifemb]))
        log.report_log05[femb_id]['FEMB_current_2'] = "FEMB ID {} faild current #1 check\n".format(fembNo['femb%d'%ifemb])
        log.report_log05[femb_id]["Result"] = False
    else:
        print("FEMB ID {} Pass current check 2".format(fembNo['femb%d'%ifemb]))
        log.report_log05[femb_id]['FEMB_current_2'] = "FEMB ID {} Pass current #1 check\n".format(fembNo['femb%d' % ifemb])
        log.report_log05[femb_id]["Result"] = True
    log.report_log05[femb_id]["FC1_BIAS_current_2"] = "BIAS current: %f (default range: <0.05A)\n" % bias_i
    log.report_log05[femb_id]["FC1_LArASIC_current_2"] = "LArASIC current: %f (default range: <0.05A)\n" % fe_i
    log.report_log05[femb_id]["FC1_COLDATA_current_2"] = "COLDATA current: %f (default range: <0.05A)\n" % cd_i
    log.report_log05[femb_id]["FC1_ColdADC_current_2"] = "ColdADC current: %f (default range: <0.05A)\n" % adc_i


#   power data save
if save:
    fp = datadir + "PWR_SE_{}_{}_{}_0x{:02x}.bin".format("200mVBL","14_0mVfC","2_0us",0x00)
    with open(fp, 'wb') as fn:
        pickle.dump([pwr_meas2, fembs], fn)


#   power analysis
pwr_meas=pwr_meas2
#for ifemb in fembs:
for ifemb in range(len(fembs)):
    femb_id = "FEMB ID {}".format(fembNo['femb%d' % fembs[ifemb]])
    fp_pwr = datareport[fembs[ifemb]]+"pwr_meas"
    qc_tools.PrintPWR(pwr_meas, fembs[ifemb], fp_pwr)
    tmp=QC_check.CHKPWR(pwr_meas,fembs[ifemb], env)
    log.chkflag["PWR"].append(tmp[0])
    log.badlist["PWR"].append(tmp[1])
    log.report_log05[femb_id]["Power check status"] = tmp[0]
    log.report_log05[femb_id]["Power ERROR status"] = tmp[1]

################# monitoring power rails ###################

log.report_log06["ITEM"] = "FEMB power rail"
power_rail_d = a_func.monitor_power_rail("SE", fembs, datadir, save)
power_rail_a = a_func.monitor_power_rail_analysis("SE", datadir, datareport)


############ Take pulse data 900mV 14mV/fC 2us ##################
print("Take single-ended pulse data")
fname = "Raw_SE_{}_{}_{}_0x{:02x}.bin".format("900mVBL","14_0mVfC","2_0us",0x10)
snc = 0 # 900 mV
sg0 = 0
sg1 = 0 # 14mV/fC
st0 = 1
st1 = 1 # 2us 
log.report_log07["ITEM"] = "single-ended pulse at 900mV 14mV/fC 2us"
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

pldata = qc_tools.data_decode(pls_rawdata, fembs)

for ifemb in range(len(fembs)):
    femb_id = "FEMB ID {}".format(fembNo['femb%d' % fembs[ifemb]])
    ppk,npk,bl=qc_tools.GetPeaks(pldata, fembs[ifemb], datareport[fembs[ifemb]], fname, funcfit=False)
    # outfp = datareport[fembs[ifemb]] + "pulse_{}.bin".format(fname)
    # with open(outfp, 'wb') as fn:
    #      pickle.dump([ppk,npk,bl], fn)

    tmp = QC_check.CHKPulse(ppk)
    log.chkflag["Pulse_SE"]["PPK"].append(tmp[0])
    log.badlist["Pulse_SE"]["PPK"].append(tmp[1])
    log.report_log07[femb_id]["Pulse_SE PPK err_status"] = tmp[1]
    log.report_log07[femb_id]["Pulse_SE PPK chk_status"] = tmp[0]

    tmp = QC_check.CHKPulse(npk)
    log.chkflag["Pulse_SE"]["NPK"].append(tmp[0])
    log.badlist["Pulse_SE"]["NPK"].append(tmp[1])
    log.report_log07[femb_id]["Pulse_SE NPK err_status"] = tmp[1]
    log.report_log07[femb_id]["Pulse_SE NPK chk_status"] = tmp[0]

    tmp = QC_check.CHKPulse(bl)
    log.chkflag["Pulse_SE"]["BL"].append(tmp[0])
    log.badlist["Pulse_SE"]["BL"].append(tmp[1])
    log.report_log07[femb_id]["Pulse_SE BL err_status"] = tmp[1]
    log.report_log07[femb_id]["Pulse_SE BL chk_status"] = tmp[0]

if save:
    fp = datadir + fname
    with open(fp, 'wb') as fn:
        pickle.dump( [pls_rawdata, cfg_paras_rec, fembs], fn)


############ Take pulse data 900mV 14mV/fC 2us (DIFF) ##################
#   take pulse structure:
#   initial <print note>    <fname>
#   cd_rst
#   LArASIC parameter
#   Coldadc parameter
#   set fe
#   femb cfg
#   data_align
#   spybuf
#   save
#Note: accually, all test actions could have a same general mode and we can just build a mode and reuse it with different items thus it could be concise for us
print("Take differential pulse data")
fname = "Raw_DIFF_{}_{}_{}_0x{:02x}".format("900mVBL","14_0mVfC","2_0us",0x10)
chk.femb_cd_rst()
cfg_paras_rec = []
log.report_log08["ITEM"] = "08 Measure differential pulse at 200mV, 14mV/fC, 2us"
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

pldata = qc_tools.data_decode(pls_rawdata, fembs)
for ifemb in range(len(fembs)):
    femb_id = "FEMB ID {}".format(fembNo['femb%d' % fembs[ifemb]])
    ppk,npk,bl=qc_tools.GetPeaks(pldata, fembs[ifemb], datareport[fembs[ifemb]], fname)

    tmp = QC_check.CHKPulse(ppk)
    log.chkflag["Pulse_DIFF"]["PPK"].append(tmp[0])
    log.badlist["Pulse_DIFF"]["PPK"].append(tmp[1])
    log.report_log08[femb_id]["Pulse_DIFF PPK err_status"] = tmp[1]
    log.report_log08[femb_id]["Pulse_DIFF PPK chk_status"] = tmp[0]

    tmp = QC_check.CHKPulse(npk)
    log.chkflag["Pulse_DIFF"]["NPK"].append(tmp[0])
    log.badlist["Pulse_DIFF"]["NPK"].append(tmp[1])
    log.report_log08[femb_id]["Pulse_DIFF npk err_status"] = tmp[1]
    log.report_log08[femb_id]["Pulse_DIFF npk chk_status"] = tmp[0]

    tmp = QC_check.CHKPulse(bl)
    log.chkflag["Pulse_DIFF"]["BL"].append(tmp[0])
    log.badlist["Pulse_DIFF"]["BL"].append(tmp[1])
    log.report_log08[femb_id]["Pulse_DIFF bl err_status"] = tmp[1]
    log.report_log08[femb_id]["Pulse_DIFF bl chk_status"] = tmp[0]

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
    tmp = QC_check.CHKFET(mon_temps,fembs[ifemb],nchips, env)
    log.chkflag["MON_T"].append(tmp[0])
    log.badlist["MON_T"].append(tmp[1])

    tmp = QC_check.CHKFEBGP(mon_refs,fembs[ifemb],nchips, env)
    log.chkflag["MON_BGP"].append(tmp[0])
    log.badlist["MON_BGP"].append(tmp[1])

    tmp = QC_check.CHKADC(mon_adcs,fembs[ifemb],nchips,"VCMI",985, 40,935, 40, env)
    log.chkflag["MON_ADC"]["VCMI"].append(tmp[0])
    log.badlist["MON_ADC"]["VCMI"].append(tmp[1])

    tmp = QC_check.CHKADC(mon_adcs,fembs[ifemb],nchips,"VCMO",1272, 40, 1232, 40, env)
    log.chkflag["MON_ADC"]["VCMO"].append(tmp[0])
    log.badlist["MON_ADC"]["VCMO"].append(tmp[1])

    tmp = QC_check.CHKADC(mon_adcs,fembs[ifemb],nchips,"VREFP",1988, 40, 1980, 40, env)
    log.chkflag["MON_ADC"]["VREFP"].append(tmp[0])
    log.badlist["MON_ADC"]["VREFP"].append(tmp[1])

    tmp = QC_check.CHKADC(mon_adcs,fembs[ifemb],nchips,"VREFN",550, 40, 482, 40, env)
    log.chkflag["MON_ADC"]["VREFN"].append(tmp[0])
    log.badlist["MON_ADC"]["VREFN"].append(tmp[1])

    tmp = QC_check.CHKADC(mon_adcs,fembs[ifemb],nchips,"VSSA",105, 40, 35, 20, env)
    log.chkflag["MON_ADC"]["VSSA"].append(tmp[0])
    log.badlist["MON_ADC"]["VSSA"].append(tmp[1])


####### Power off FEMBs #######
print("Turning off FEMBs")
chk.femb_powering([])

#   Generate Report
# a_func.generate_report()
###### Generate Report ######
# for ifemb in fembs:
for ifemb in range(len(fembs)):
    femb_id = "FEMB ID {}".format(fembNo['femb%d' % fembs[ifemb]])

    plotdir = datareport[fembs[ifemb]]
    ta = time.time()
    pdf = FPDF(orientation='P', unit='mm', format='Letter')
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_auto_page_break(False, 0)
    pdf.set_font('Times', 'B', 20)
    pdf.cell(85)
    pdf.l_margin = pdf.l_margin * 2
    pdf.cell(30, 5, 'FEMB#{:04d} Checkout Test Report'.format(int(fembNo['femb%d' % fembs[ifemb]])), 0)
    pdf.ln(2)

    pdf.set_font('Times', '', 12)
    pdf.cell(30, 5, 'Tester: {}'.format(tester), 0)
    pdf.cell(80)
    # pdf.cell(30, 5, 'Date: {}'.format(date), 0)

    pdf.cell(30, 5, 'Temperature: {}'.format(env), 0)
    pdf.cell(80)
    pdf.cell(30, 5, 'Input Capacitor(Cd): {}'.format(toytpc), 0)
    pdf.cell(30, 5, 'Note: {}'.format(note[0:80]), 0)
    pdf.cell(30, 5,
             'FEMB configuration: {}, {}, {}, {}, DAC=0x{:02x}'.format("200mVBL", "14_0mVfC", "2_0us", "500pA", 0x20),
             0)

    pdf.ln(10)
    print("tb", end = " ")
    tb = time.time()
    print(tb-ta)
    chk_result = []
    err_messg = []
    chk_result.append(("Measurement", "Result"))

    print("tb", end = " ")
    tb1 = time.time()
    print(tb1-tb)

    if log.chkflag["PWR"][ifemb] == False:
        chk_result.append(("Power Measurement", "Pass"))
    else:
        chk_result.append(("Power Measurement", "Fail"))
        err_messg.append(("Power Measurement: ", log.badlist["PWR"][ifemb]))

    print("tb", end=" ")
    tb2 = time.time()
    print(tb2 - tb1)

    if log.chkflag["MON_T"][ifemb] == False:
        chk_result.append(("Temperature", "Pass"))
    else:
        chk_result.append(("Temperature", "Fail"))
        err_messg.append(("Temperature issued chips: ", log.badlist["MON_T"][ifemb]))

    if log.chkflag["MON_BGP"][ifemb] == False:
        chk_result.append(("BGP", "Pass"))
    else:
        chk_result.append(("BGP", "Fail"))
        err_messg.append(("BGP issued chips: ", log.badlist["MON_BGP"][ifemb]))

    if log.chkflag["RMS"][ifemb] == False:
        chk_result.append(("RMS", "Pass"))
    else:
        chk_result.append(("RMS", "Fail"))
        err_messg.append(("RMS issued channels: ", log.badlist["RMS"][ifemb][0]))
        if log.badlist["RMS"][ifemb][1]:
            err_messg.append(("RMS issued chips: ", log.badlist["RMS"][ifemb][1]))

    if log.chkflag["BL"][ifemb] == False:
        chk_result.append(("200mV Baseline", "Pass"))
    else:
        chk_result.append(("200mV Baseline", "Fail"))
        err_messg.append(("200mV BL issued channels: ", log.badlist["BL"][ifemb][0]))
        if log.badlist["BL"][ifemb][1]:
            err_messg.append(("200mV BL issued chips: ", log.badlist["BL"][ifemb][1]))
    print("tc", end=" ")
    tc = time.time()
    print(tc-tb2)
    tmp_key = ["Pulse_SE", "Pulse_DIFF"]
    for ikey in tmp_key:
        if log.chkflag[ikey]["PPK"][ifemb] == False and log.chkflag[ikey]["NPK"][ifemb] == False and log.chkflag[ikey]["BL"][
            ifemb] == False:
            chk_result.append((ikey, "Pass"))
        else:
            chk_result.append((ikey, "Fail"))
            if log.chkflag[ikey]["PPK"][ifemb] == True:
                err_messg.append(("%s positive peak issued channels: " % ikey, log.badlist[ikey]["PPK"][ifemb][0]))
                if log.badlist[ikey]["PPK"][ifemb][1]:
                    err_messg.append(("%s positive peak issued chips: " % ikey, log.badlist[ikey]["PPK"][ifemb][1]))

            if log.chkflag[ikey]["NPK"][ifemb] == True:
                err_messg.append(("%s negative peak issued channels: " % ikey, log.badlist[ikey]["NPK"][ifemb][0]))
                if log.badlist[ikey]["NPK"][ifemb][1]:
                    err_messg.append(("%s negative peak issued chips: " % ikey, log.badlist[ikey]["NPK"][ifemb][1]))

            if log.chkflag[ikey]["BL"][ifemb] == True:
                err_messg.append(("%s baseline issued channels: " % ikey, log.badlist[ikey]["BL"][ifemb][0]))
                if log.badlist[ikey]["BL"][ifemb][1]:
                    err_messg.append(("%s baseline issued chips: " % ikey, log.badlist[ikey]["BL"][ifemb][1]))

    len1 = len(chk_result)
    tmpkey = ["VCMI", "VCMO", "VREFP", "VREFN", "VSSA"]
    for ikey in tmpkey:
        if log.chkflag["MON_ADC"][ikey][ifemb] == True:
            len2 = len(chk_result)
            if len2 == len1:
                chk_result.append(("ADC Monitoring", "Fail"))
            err_messg.append(("ADC MON %s issued chips: " % ikey, log.badlist["MON_ADC"][ikey][ifemb]))

    len2 = len(chk_result)
    if len2 == len1:
        chk_result.append(("ADC Monitoring", "Pass"))

    # with pdf.table() as table:
    #     for data_row in chk_result:
    #         row = table.row()
    #         for datum in data_row:
    #             row.cell(datum)

    if err_messg:
        pdf.ln(10)
        for istr in err_messg:
            pdf.cell(80, 5, "{} {}".format(istr[0], istr[1]), 0)
    td = time.time()
    print("td", end=" ")
    print(td-tc)

    pdf.add_page()
    td1 = time.time()
    print("td", end=" ")
    print(td-td1)

    # pwr_image = plotdir + "pwr_meas.png"
    # pdf.image(pwr_image, 0, 20, 200, 40)
    #
    # mon_image = plotdir + "mon_meas_plot.png"
    # pdf.image(mon_image, 10, 60, 200, 60)
    #
    # mon_image = plotdir + "MON_PWR_SE_200mVBL_14_0mVfC_2_0us_0x00.png"
    # pdf.image(mon_image, 10, 120, 200, 20)
    # mon_image = plotdir + "MON_PWR_DIFF_200mVBL_14_0mVfC_2_0us_0x00.png"
    # pdf.image(mon_image, 10, 140, 200, 20)
    #
    # mon_image = plotdir + "mon_meas.png"
    # pdf.image(mon_image, 10, 160, 200, 90)
    #
    # pdf.add_page()
    #
    # rms_image = plotdir + "rms_Raw_SE_200mVBL_14_0mVfC_2_0us_0x00.png"
    #
    # pdf.image(rms_image, 5, 10, 100, 70)
    #
    # ped200_image = plotdir + "ped_Raw_SE_200mVBL_14_0mVfC_2_0us_0x00.png"
    # pdf.image(ped200_image, 105, 10, 100, 70)
    #
    # pulse_se_image = plotdir + "pulse_Raw_DIFF_900mVBL_14_0mVfC_2_0us_0x10.png"
    # pdf.image(pulse_se_image, 0, 80, 220, 70)
    #
    # pulse_diff_image = plotdir + "pulse_Raw_DIFF_900mVBL_14_0mVfC_2_0us_0x10.png"
    # pdf.image(pulse_diff_image, 0, 150, 220, 70)

    outfile = plotdir + 'report.pdf'
    pdf.output(outfile)
    print("te", end=" ")

    outfile = plotdir+'report.pdf'
    pdf.output(outfile)
    for measurement, result in chk_result:
        print("FEMB: " + str(ifemb), end = "    ")
        print(f"{measurement}: {result}")
    print("\n")
    print("xxxxx")
    png_paths = [plotdir+"rms_Raw_SE_200mVBL_14_0mVfC_2_0us_0x00.png", plotdir+"ped_Raw_SE_200mVBL_14_0mVfC_2_0us_0x00.png", plotdir+"pulse_Raw_DIFF_900mVBL_14_0mVfC_2_0us_0x10.png"]
    #png_paths = ["path/to/image1.png", "path/to/image2.png", "path/to/image3.png"]

    # Replace this with the desired output path
    output_path = plotdir + "merged_output.png"

    # Merge PNGs using Matplotlib and imageio
    a_func.merge_pngs(png_paths, output_path)
    te = time.time()
    print(f"PNGs merged and saved at: {output_path}")
    print(te-td)

    #print(chk_result)
    for measurement, result in chk_result:
        print("FEMB: " + str(ifemb), end = "    ")
        print(f"{measurement}: {result}")
    print("\n")

    print(log.report_log01["ITEM"])
    print(log.report_log01["Detail"])
    print(log.report_log02["ITEM"])
    print(log.report_log02[femb_id])
    print(log.report_log03["ITEM"])
    print(log.report_log03[femb_id])
    print(log.report_log04["ITEM"])
    print(log.report_log04[femb_id])
    print(log.report_log05["ITEM"])
    print(log.report_log05[femb_id])
    print(log.report_log06["ITEM"])
    print(log.report_log06[femb_id])
    print(log.report_log07["ITEM"])
    print(log.report_log07[femb_id])
    print(log.report_log08["ITEM"])
    print(log.report_log08[femb_id])
    print(log.report_log09["ITEM"])
    print(log.report_log09[femb_id])


#================   Final Report    ===================================
a_repo.final_report(fembs, fembNo)

t2=time.time()
print(t2-t1)

print("\n\n\n\n\n\n")