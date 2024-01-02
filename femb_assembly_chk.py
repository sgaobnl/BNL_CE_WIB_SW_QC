import PIL

from wib_cfgs import WIB_CFGS
import time
import sys
import pickle
import copy
import datetime
import QC_check
from fpdf import FPDF
import components.assembly_parameter as paras
import components.assembly_log as log
import components.assembly_function as a_func
import components.assembly_report as a_repo

# qc_tools = ana_tools()
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
    logs['Operator']=tester
    
    env_cs = input("Test is performed at cold(LN2) (Y/N)? : ")
    if ("Y" in env_cs) or ("y" in env_cs):
        env = "LN"
    else:
        env = "RT"
    logs['env']=env
    
    ToyTPC_en = input("ToyTPC at FE inputs (Y/N) : ")
    if ("Y" in ToyTPC_en) or ("y" in ToyTPC_en):
        toytpc = "150 pF"
    else:
        toytpc = "0 pF"
    logs['Toy_TPC']=toytpc
    
    note = input("A short note (<200 letters):")
    logs['Note']=note
    
    fembNo={}
    for i in fembs:
        fembNo['femb{}'.format(i)]=input("FEMB{} ID: ".format(i))
    
    #logs['femb id']=fembNo
    logs['date']=datetime.datetime.now().strftime("%m_%d_%Y_%H_%M_%S")

    datadir=a_func.Create_data_folders(fembNo, env, toytpc)
    fp = datadir + "logs_env.bin"
    with open(fp, 'wb') as fn:
        pickle.dump(logs, fn)

outfile = open(datadir+"chk_logs.txt", "w")
t1 = time.time()

log.report_log01["ITEM"] = "01 Initial Information"
log.report_log01["Detail"] = logs

################## Power on FEMBs and check currents ##################
chk = WIB_CFGS()
chk.wib_fw()

#   set FEMB voltages
chk.fembs_vol_set(vfe = paras.voltage_FE, vcd = paras.voltage_COLDATA, vadc = paras.voltage_ColdADC)
print("Check FEMB currents")
fembs_remove = []

for ifemb in fembs:
    chk.femb_powering_single(ifemb, 'on')

#   current measurement
log.report_log02["ITEM"] = "2.1 Initial Current Measurement"
pwr_meas1 = chk.get_sensors()
for ifemb in fembs:
    femb_id = "FEMB ID {}".format(fembNo['femb%d' % ifemb])
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
        log.report_log02[femb_id]['check_status'] = "FEMB ID {} faild current #1 check\n".format(fembNo['femb%d' % ifemb])
        # fembs.remove(ifemb)
        fembs_remove.append(ifemb)
        fembNo.pop('femb%d' % ifemb)
        chk.femb_powering_single(ifemb, 'off')
        log.report_log02[femb_id]["FC1_BIAS_current_1"] = "BIAS current: %f (default range: <0.05A)\n" % bias_i
        log.report_log02[femb_id]["FC1_LArASIC_current_1"] = "LArASIC current: %f (default range: (0.3A, 0.6A))\n" % fe_i
        log.report_log02[femb_id]["FC1_COLDATA_current_1"] = "COLDATA current: %f (default range: (0.1A, 0.3A))\n" % cd_i
        log.report_log02[femb_id]["FC1_ColdADC_current_1"] = "ColdADC current: %f (default range: (1.2A, 1.9A))\n" % adc_i
        log.report_log02[femb_id]["Result"] = False
    else:
        print("FEMB ID {} Pass current check".format(fembNo['femb%d'%ifemb]))
        log.report_log02[femb_id]['check_status'] = "FEMB Pass current #1 check\n"
        log.report_log02[femb_id]["FC1_BIAS_current_1"] = "BIAS current: %f (default range: <0.05A)\n" % bias_i
        log.report_log02[femb_id]["FC1_LArASIC_current_1"] = "LArASIC current: %f (default range: (0.3A, 0.6A))\n" % fe_i
        log.report_log02[femb_id]["FC1_COLDATA_current_1"] = "COLDATA current: %f (default range: (0.1A, 0.3A))\n" % cd_i
        log.report_log02[femb_id]["FC1_ColdADC_current_1"] = "ColdADC current: %f (default range: (1.2A, 1.9A))\n" % adc_i
        log.report_log02[femb_id]["Result"] = True

for femb_id in fembs_remove:
    fembs.remove(femb_id)

if len(fembs) == 0:
    print ("All FEMB fail, exit anyway")
    exit()

chk.femb_powering(fembs)    #   close the FEMB channel without link

################# check the default COLDATA and COLDADC register ##################
#   report in log03
if True:
    print("Check FEMB registers")
    log.report_log03["ITEM"] = "2.2 Check FEMB Registers"
    #   reset 3-ASIC
    a_func.chip_reset(fembs)
    check1 = a_func.register_check(fembs, fembNo, 1)
    ################ reset COLDATA, COLDADC and LArASIC ##############
    a_func.chip_reset(fembs)
    ################ check the default COLDATA and COLDADC register ###########
    print("Check FEMB registers second times")
    check2 = a_func.register_check(fembs, fembNo, 2, True)

if len(fembs) == 0:
   print ("All FEMB fail, exit anyway")
   exit()

################# enable certain fembs ###################
chk.wib_femb_link_en(fembs)

#   create report dir
datareport = a_func.Create_report_folders(fembs, fembNo, env, toytpc, datadir)

################ 04 Measure RMS at 200mV, 14mV/fC, 2us ###################
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
a_func.rms_ped_ana(rms_rawdata, fembs, fembNo, datareport, fname)

#   save data ==========================
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
        log.report_log05[femb_id]["Result"] = False
        log.report_log05[femb_id]['FEMB_current_2'] = "FEMB ID {} faild current #1 check\n".format(fembNo['femb%d'%ifemb])
    else:
        print("FEMB ID {} Pass current check 2".format(fembNo['femb%d'%ifemb]))
        log.report_log05[femb_id]["Result"] = True
        log.report_log05[femb_id]['FEMB_current_2'] = "FEMB ID {} Pass current #1 check\n".format(fembNo['femb%d' % ifemb])
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
a_func.power_ana(fembs, fembNo, datareport, pwr_meas, env)
#for ifemb in fembs:

################# monitoring power rails ###################
log.report_log06["ITEM"] = "06 FEMB power rail"
power_rail_d = a_func.monitor_power_rail("SE", fembs, datadir, save)
power_rail_a = a_func.monitor_power_rail_analysis("SE", datadir, datareport, fembNo)
log.report_log06.update(log.power_rail_report_log)

############ Take pulse data 900mV 14mV/fC 2us ##################
print("Take single-ended pulse data")
fname = "Raw_SE_{}_{}_{}_0x{:02x}.bin".format("900mVBL","14_0mVfC","2_0us",0x10)
snc = 0 # 900 mV
sg0 = 0; sg1 = 0 # 14mV/fC
st0 = 1; st1 = 1 # 2us
log.report_log07["ITEM"] = "07 single-ended pulse at 900mV 14mV/fC 2us"
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
a_func.se_pulse_ana(pls_rawdata, fembs, fembNo, datareport, fname)

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
a_func.DIFF_pulse_data(pls_rawdata, fembs, fembNo,datareport, fname)

######   6   DIFF monitor power rails   ######
log.report_log09["ITEM"] = "09 FEMB power rail"
power_rail_d = a_func.monitor_power_rail("DIFF", fembs, datadir, save)
power_rail_a = a_func.monitor_power_rail_analysis("DIFF", datadir, datareport, fembNo)
log.report_log09.update(log.power_rail_report_log)

######  7   Take monitoring data #######
#   initial ColdADC, COLDATA
chk.femb_cd_rst()
#   data acquisition
mon_refs, mon_temps, mon_adcs = a_func.monitoring_path(fembs, snc, sg0,sg1,datadir, save)
#   data analysis
a_func.mon_path_ana(fembs, mon_refs, mon_temps, mon_adcs, datareport, fembNo, env)

#   Generate Report
# a_func.generate_report()
###### Generate Report ######
# for ifemb in fembs:
# for ifemb in range(len(fembs)):
#     femb_id = "FEMB ID {}".format(fembNo['femb%d' % fembs[ifemb]])
#     chk_result = []
#     err_messg = []
#     chk_result.append(("Measurement", "Result"))
#
#     print("tb", end = " ")
#     tb1 = time.time()
#     # print(tb1-tb)
#
#     if log.chkflag["PWR"][ifemb] == False:
#         chk_result.append(("Power Measurement", "Pass"))
#     else:
#         chk_result.append(("Power Measurement", "Fail"))
#         err_messg.append(("Power Measurement: ", log.badlist["PWR"][ifemb]))
#
#     print("tb", end=" ")
#     tb2 = time.time()
#     print(tb2 - tb1)
#
#     if log.chkflag["MON_T"][ifemb] == False:
#         chk_result.append(("Temperature", "Pass"))
#     else:
#         chk_result.append(("Temperature", "Fail"))
#         err_messg.append(("Temperature issued chips: ", log.badlist["MON_T"][ifemb]))
#
#     if log.chkflag["MON_BGP"][ifemb] == False:
#         chk_result.append(("BGP", "Pass"))
#     else:
#         chk_result.append(("BGP", "Fail"))
#         err_messg.append(("BGP issued chips: ", log.badlist["MON_BGP"][ifemb]))
#
#     if log.chkflag["RMS"][ifemb] == False:
#         chk_result.append(("RMS", "Pass"))
#     else:
#         chk_result.append(("RMS", "Fail"))
#         err_messg.append(("RMS issued channels: ", log.badlist["RMS"][ifemb][0]))
#         if log.badlist["RMS"][ifemb][1]:
#             err_messg.append(("RMS issued chips: ", log.badlist["RMS"][ifemb][1]))
#
#     if log.chkflag["BL"][ifemb] == False:
#         chk_result.append(("200mV Baseline", "Pass"))
#     else:
#         chk_result.append(("200mV Baseline", "Fail"))
#         err_messg.append(("200mV BL issued channels: ", log.badlist["BL"][ifemb][0]))
#         if log.badlist["BL"][ifemb][1]:
#             err_messg.append(("200mV BL issued chips: ", log.badlist["BL"][ifemb][1]))
#     print("tc", end=" ")
#     tc = time.time()
#     print(tc-tb2)
#     tmp_key = ["Pulse_SE", "Pulse_DIFF"]
#     for ikey in tmp_key:
#         if log.chkflag[ikey]["PPK"][ifemb] == False and log.chkflag[ikey]["NPK"][ifemb] == False and log.chkflag[ikey]["BL"][
#             ifemb] == False:
#             chk_result.append((ikey, "Pass"))
#         else:
#             chk_result.append((ikey, "Fail"))
#             if log.chkflag[ikey]["PPK"][ifemb] == True:
#                 err_messg.append(("%s positive peak issued channels: " % ikey, log.badlist[ikey]["PPK"][ifemb][0]))
#                 if log.badlist[ikey]["PPK"][ifemb][1]:
#                     err_messg.append(("%s positive peak issued chips: " % ikey, log.badlist[ikey]["PPK"][ifemb][1]))
#
#             if log.chkflag[ikey]["NPK"][ifemb] == True:
#                 err_messg.append(("%s negative peak issued channels: " % ikey, log.badlist[ikey]["NPK"][ifemb][0]))
#                 if log.badlist[ikey]["NPK"][ifemb][1]:
#                     err_messg.append(("%s negative peak issued chips: " % ikey, log.badlist[ikey]["NPK"][ifemb][1]))
#
#             if log.chkflag[ikey]["BL"][ifemb] == True:
#                 err_messg.append(("%s baseline issued channels: " % ikey, log.badlist[ikey]["BL"][ifemb][0]))
#                 if log.badlist[ikey]["BL"][ifemb][1]:
#                     err_messg.append(("%s baseline issued chips: " % ikey, log.badlist[ikey]["BL"][ifemb][1]))
#
#     len1 = len(chk_result)
#     tmpkey = ["VCMI", "VCMO", "VREFP", "VREFN", "VSSA"]
#     for ikey in tmpkey:
#         if log.chkflag["MON_ADC"][ikey][ifemb] == True:
#             len2 = len(chk_result)
#             if len2 == len1:
#                 chk_result.append(("ADC Monitoring", "Fail"))
#             err_messg.append(("ADC MON %s issued chips: " % ikey, log.badlist["MON_ADC"][ikey][ifemb]))
#
#     len2 = len(chk_result)
#     if len2 == len1:
#         chk_result.append(("ADC Monitoring", "Pass"))


#================   Final Report    ===================================
a_repo.final_report(datareport, fembs, fembNo)

t2=time.time()
print(t2-t1)
####### Power off FEMBs #######
print("Turning off FEMBs")
chk.femb_powering([])
print("\n\n\n\n\n\n")