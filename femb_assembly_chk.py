import time
from wib_cfgs import WIB_CFGS
import sys
import pickle
import copy
import datetime
import components.assembly_parameter as paras
import components.assembly_log as log
import components.assembly_function as a_func
import components.assembly_report as a_repo
import matplotlib.pyplot as plt
# qc_tools = ana_tools()
# Create an array to store the merged image
LAr_Dalay = 5

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

if 'sp' in sys.argv:
    ship = True
else:
    ship = False

###########################################
#      PART 01 Input test information     #
###########################################
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
        toytpc = "100pF"
    else:
        toytpc = "0pF"
    logs['Toy_TPC']=toytpc
    
    note = input("A short note (<200 letters):")
    logs['Note']=note
    
    fembName={}
    fembNo={}
    for i in fembs:
        fembName['femb{}'.format(i)]=input("FEMB{}ID:".format(i)).strip()
        fembNo['femb{}'.format(i)]=fembName['femb{}'.format(i)][1:]
    logs['FEMB ID'] = fembName
    # logs['femb id']=fembNo
    logs['date']=datetime.datetime.now().strftime("%m_%d_%Y_%H_%M_%S")

    datadir=a_func.Create_data_folders(fembName, env, toytpc)
    fp = datadir + "logs_env.bin"
    with open(fp, 'wb') as fn:
        pickle.dump(logs, fn)

outfile = open(datadir+"chk_logs.txt", "w")
t1 = time.time()

log.report_log01["ITEM"] = "01 Initial Information"
log.report_log01["Detail"] = logs



###########################################
#      PART 02 Initial Power Measurement  #
###########################################
chk = WIB_CFGS()
chk.wib_fw()

####### Power off FEMBs #######
print("Power off FEMBs to initial the test")
chk.femb_powering([])

RP = 1
if RP == 1:
    chk.fembs_vol_set(vfe=3.0, vcd=3.0, vadc=3.5)

#   set FEMB voltages
#chk.fembs_vol_set(vfe = paras.voltage_FE, vcd = paras.voltage_COLDATA, vadc = paras.voltage_ColdADC)
chk.fembs_vol_set(vfe = 3.0, vcd = 3.0, vadc = 3.5)   #   this parameter can not be used in LN2
# chk.fembs_vol_set(vfe = 4, vcd = 4, vadc = 4)
print("Check FEMB currents")
fembs_remove = []

for ifemb in fembs:
    chk.femb_powering_single(ifemb, 'on')


chk.femb_cd_rst()
cfg_paras_rec = []
for i in range(8):
    chk.adcs_paras[i][8]=1   # enable  auto
for femb_id in fembs:
    chk.femb_cfg(femb_id, False )
#####   2.1  initial current measure #####
log.report_log02["ITEM"] = "2.1 Initial Current Measurement"
pwr_meas1 = chk.get_sensors()
result = False
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

    # if fe_i > paras.fe_i_high or fe_i < paras.fe_i_low:
    if  fe_i < paras.fe_i_low:
        print("ERROR: FEMB{} LArASIC current {} out of range (0.3A,0.6A)".format(ifemb,fe_i))
        hasERROR = True

    if cd_i>paras.cd_i_high:#  or cd_i<paras.cd_i_low :
        print("ERROR: FEMB{} COLDATA current {} out of range (0.1A,0.3A)".format(ifemb,cd_i))
        hasERROR = True

    # if adc_i>paras.adc_i_high or adc_i<paras.adc_i_low:
    #     print("ERROR: FEMB{} ColdADC current {} out of range (1.2A,1.8A)".format(ifemb,adc_i))
    #     hasERROR = True

    if hasERROR:
        print("FEMB ID {} Faild current check, will skip this femb".format(fembNo['femb%d'%ifemb]))
        log.report_log02[femb_id]['Part 2 Power Error List'] = "FEMB ID {} faild current #1 check\n".format(fembNo['femb%d' % ifemb])
        # fembs.remove(ifemb)

        #== I need to know how to merge the different dictionary, like the log here merge the log in induced function
        fembs_remove.append(ifemb)
        fembNo.pop('femb%d' % ifemb)
        chk.femb_powering_single(ifemb, 'off')
        result = False
    else:
        print("FEMB ID {} Pass current check".format(fembNo['femb%d'%ifemb]))
        result = True
for ifemb in range(len(fembs)):
    femb_id = "FEMB ID {}".format(fembNo['femb%d' % fembs[ifemb]])
    initial_power = a_func.power_ana(fembs, ifemb, femb_id, pwr_meas1, env)
    pwr1 = dict(log.tmp_log)
    check1 = dict(log.check_log)
    log.report_log02.update(pwr1)
    log.report_log021.update(check1)



for femb_id in fembs_remove:
    fembs.remove(femb_id)

if len(fembs) == 0:
    print ("All FEMB fail, exit anyway")
    exit()

chk.femb_powering(fembs)    #   close the FEMB channel without link

##### 2.2 check the default COLDATA and COLDADC register ##################
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

############################################
#      PART 03 SE Performance Measurement  #
############################################
#   create report dir
datareport = a_func.Create_report_folders(fembs, fembName, env, toytpc, datadir)
##### 3.1 Measure RMS at 200mV, 14mV/fC, 2us ###################
#   report in log04
print("Take RMS data")
log.report_log04["ITEM"] = "3.1 No Buffer RMS at 200mV, 14mV/fC, 2us, DAC = 0x00"
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
    cfg_paras_rec.append((femb_id, copy.deepcopy(chk.adcs_paras), copy.deepcopy(chk.regs_int8), adac_pls_en))
    chk.femb_cfg(femb_id, adac_pls_en )
time.sleep(LAr_Dalay)
chk.data_align(fembs)
# data acquire
rms_rawdata = chk.spybuf_trig(fembs=fembs, num_samples=sample_N, trig_cmd=0) #returns list of size 1

# report: data analysis ========================


#   save data ==========================
if save:
    fp = datadir + fname + ".bin"
    with open(fp, 'wb') as fn:
        pickle.dump( [rms_rawdata, cfg_paras_rec, fembs], fn)
a_func.rms_ped_ana(rms_rawdata, fembs, fembNo, datareport, fname)

pts = ["1_0us", "0_5us",  "3_0us", "2_0us"]
if ship:
    for sti in range(4):
        st0 = sti % 2
        st1 = sti // 2
        print("=== Take ship RMS data ===")
        log.report_log04["ITEM"] = "3.1 No Buffer RMS at 900mV, 14mV/fC, 2us, DAC = 0x00"
        fname = "Raw_SE_{}_{}_{}_0x{:02x}".format("900mVBL", "14_0mVfC", pts[sti], 0x00)
        snc = 0  # 900 mV
        sg0 = 0
        sg1 = 0  # 14mV/fC
        # configuration
        chk.femb_cd_rst()
        cfg_paras_rec = []
        for i in range(8):
            chk.adcs_paras[i][8]=1   # enable  auto
        for femb_id in fembs:
            chk.set_fe_board(sts=0, snc=snc, sg0=sg0, sg1=sg1, st0=st0, st1=st1, swdac=0, dac=0x00 )
            adac_pls_en = 0
            cfg_paras_rec.append((femb_id, copy.deepcopy(chk.adcs_paras), copy.deepcopy(chk.regs_int8), adac_pls_en))
            chk.femb_cfg(femb_id, adac_pls_en )
        time.sleep(LAr_Dalay)
        chk.data_align(fembs)

        # data acquire
        rms_rawdata = chk.spybuf_trig(fembs=fembs, num_samples=sample_N, trig_cmd=0) #returns list of size 1

        # report: data analysis ========================
        a_func.rms_ped_ana(rms_rawdata, fembs, fembNo, datareport, fname)
        #   save data ==========================
        if save:
            fp = datadir + fname + ".bin"
            with open(fp, 'wb') as fn:
                pickle.dump( [rms_rawdata, cfg_paras_rec, fembs], fn)
    for ifemb in range(len(fembs)):
        femb_id = "FEMB ID {}".format(fembNo['femb%d' % fembs[ifemb]])
        print(log.rmsdata[femb_id]["rmsRaw_SE_900mVBL_14_0mVfC_0_5us_0x00"])
        print(log.rmsdata[femb_id]["rmsRaw_SE_900mVBL_14_0mVfC_1_0us_0x00"])
        print(log.rmsdata[femb_id]["rmsRaw_SE_900mVBL_14_0mVfC_2_0us_0x00"])
        print(log.rmsdata[femb_id]["rmsRaw_SE_900mVBL_14_0mVfC_3_0us_0x00"])
        file_path = datareport[fembs[ifemb]]
        plt.figure(figsize=(6, 4))
        x_sticks = range(0, 129, 16)
        for key in log.rmsdata[femb_id]:
            if "0_5us" in key:
                plt.plot(range(128), log.rmsdata[femb_id][key], marker='.', linestyle='-', alpha=0.7, color='red', label='0_5us')
            if "1_0us" in key:
                plt.plot(range(128), log.rmsdata[femb_id][key], marker='.', linestyle='-', alpha=0.7, color='orange', label='1_0us')
            if "2_0us" in key:
                plt.plot(range(128), log.rmsdata[femb_id][key], marker='.', linestyle='-', alpha=0.7, color='green', label='2_0us')
            if "3_0us" in key:
                plt.plot(range(128), log.rmsdata[femb_id][key], marker='.', linestyle='-', alpha=0.7, color='blue', label='3_0us')
        plt.xlabel("Channel", fontsize=12)
        plt.ylabel("RMS", fontsize=12)
        plt.xticks(x_sticks)
        plt.ylim(5, 32)
        plt.grid(axis='x')
        plt.grid(axis='y')
        plt.legend()
        plt.title("SE 900 mV RMS Distribution", fontsize=12)
        plt.savefig(file_path + 'RMS_4_peak_time.png')
        plt.close()

################ Measure FEMB currents 2 ####################
print("Check FEMB current")
pwr_meas2 = chk.get_sensors()
result = False
#####   3.2  SE interface current measure #####
log.report_log05['ITEM'] = "3.2 No Buffer interface Current Measurement"   #05
for ifemb in fembs:
    femb_id = "FEMB ID {}".format(fembNo['femb%d' % ifemb])
    bias_i = round(pwr_meas2['FEMB%d_BIAS_I'%ifemb],3)  
    fe_i = round(pwr_meas2['FEMB%d_DC2DC0_I'%ifemb],3)
    cd_i = round(pwr_meas2['FEMB%d_DC2DC1_I'%ifemb],3)
    adc_i = round(pwr_meas2['FEMB%d_DC2DC2_I'%ifemb],3)

    hasERROR = False
    if abs(bias_i)>paras.bias_i_low:
       print("ERROR: FEMB{} BIAS current {} out of range (-0.02A,0.05A)".format(ifemb,bias_i)) 
       hasERROR = True

    if fe_i<0.35:
       print("ERROR: FEMB{} LArASIC current {} out of range (0.35A,0.55A)".format(ifemb,fe_i))
       hasERROR = True

    if cd_i>0.35:# or cd_i<0.15:
       print("ERROR: FEMB{} COLDATA current {} out of range (0.15A,0.35A)".format(ifemb,cd_i)) 
       hasERROR = True

    if adc_i>1.85 or adc_i<1.35:
       print("ERROR: FEMB{} ColdADC current {} out of range (1.35A,1.85A)".format(ifemb,adc_i)) 
       hasERROR = True

    if hasERROR:
        print("FEMB ID {} Faild current check 2, will skip this femb".format(fembNo['femb%d'%ifemb]))
        result = False
    else:
        print("FEMB ID {} Pass current check 2".format(fembNo['femb%d'%ifemb]))
        result = True

for ifemb in range(len(fembs)):
    femb_id = "FEMB ID {}".format(fembNo['femb%d' % fembs[ifemb]])
    se_power = a_func.power_ana(fembs, ifemb, femb_id, pwr_meas2, env)
    pwr2 = dict(log.tmp_log)
    check2 = dict(log.check_log)
    log.report_log05.update(pwr2)
    log.report_log051.update(check2)

#   power data save
if save:
    fp = datadir + "PWR_SE_{}_{}_{}_0x{:02x}.bin".format("200mVBL","14_0mVfC","2_0us",0x00)
    with open(fp, 'wb') as fn:
        pickle.dump([pwr_meas2, fembs], fn)


#   power analysis


#for ifemb in fembs:

################# monitoring power rails ###################
log.report_log06["ITEM"] = "3.3 No Buffer Interface power rail"
power_rail_d = a_func.monitor_power_rail("SE", fembs, datadir, save)
power_rail_a = a_func.monitor_power_rail_analysis("SE", datadir, fembNo)
log06 = dict(log.power_rail_report_log)
log.report_log06.update(log06)
log.report_log061 = dict(log.check_log)

############ Take pulse data 900mV 14mV/fC 2us ##################
print("Take single-ended pulse data")
fname = "Raw_SE_{}_{}_{}_0x{:02x}.bin".format("900mVBL","14_0mVfC","2_0us",0x10)
snc = 0 # 900 mV
sg0 = 0; sg1 = 0 # 14mV/fC
st0 = 1; st1 = 1 # 2us
log.report_log07["ITEM"] = "3.4 No Buffer Interface Pulse at 900mV 14mV/fC 2us"
#   initial configuration
chk.femb_cd_rst()
cfg_paras_rec = []
for i in range(8):
    chk.adcs_paras[i][8]=1   # enable  auto

for femb_id in fembs:
    chk.set_fe_board(sts=1, snc=snc, sg0=sg0, sg1=sg1, st0=st0, st1=st1, swdac=1, dac=0x10 )
    adac_pls_en = 1
    cfg_paras_rec.append( (femb_id, copy.deepcopy(chk.adcs_paras), copy.deepcopy(chk.regs_int8), adac_pls_en) )
    chk.femb_cfg(femb_id, adac_pls_en )     # enable the Pulse
time.sleep(LAr_Dalay)
chk.data_align(fembs)
#   data acquire
pls_rawdata = chk.spybuf_trig(fembs=fembs, num_samples=sample_N, trig_cmd=0) #returns list of size 1
#   data analysis


if save:
    fp = datadir + fname
    with open(fp, 'wb') as fn:
        pickle.dump( [pls_rawdata, cfg_paras_rec, fembs], fn)

a_func.se_pulse_ana(pls_rawdata, fembs, fembNo, datareport, fname)

##############################################
#      PART 04 DIFF Performance Measurement  #
##############################################

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
log.report_log08["ITEM"] = "4.1 SEDC Pulse Measurement at 900mV, 14mV/fC, 2us"
for i in range(8):
    chk.adcs_paras[i][2]=1   # enable differential 
    chk.adcs_paras[i][8]=1   # enable  auto
for femb_id in fembs:
    chk.set_fe_board(sts=1, snc=snc, sg0=sg0, sg1=sg1, st0=st0, st1=st1, sdd=1, swdac=1, dac=0x10 )
    adac_pls_en = 1
    cfg_paras_rec.append( (femb_id, copy.deepcopy(chk.adcs_paras), copy.deepcopy(chk.regs_int8), adac_pls_en) )
    chk.femb_cfg(femb_id, adac_pls_en )
time.sleep(LAr_Dalay)
chk.data_align(fembs)

#   data acquire
pls_rawdata = chk.spybuf_trig(fembs=fembs, num_samples=sample_N, trig_cmd=0) #returns list of size 1

#   data save
if save:
    fp = datadir + fname + ".bin"
    with open(fp, 'wb') as fn:
        pickle.dump( [pls_rawdata, cfg_paras_rec, fembs], fn)

#   data analysis
a_func.DIFF_pulse_data(pls_rawdata, fembs, fembNo,datareport, fname)


#####   4.2  DIFF interface current measure #####
print("Check DIFF current")
pwr_meas3 = chk.get_sensors()
log.report_log09['ITEM'] = "4.2 SEDC interface Current Measurement"   #05
result = False
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
        result = False
    else:
        print("FEMB ID {} Pass current check 2".format(fembNo['femb%d'%ifemb]))
        result = True

for ifemb in range(len(fembs)):
    femb_id = "FEMB ID {}".format(fembNo['femb%d' % fembs[ifemb]])
    diff_power = a_func.power_ana(fembs, ifemb, femb_id, pwr_meas3, env)
    pwr3 = dict(log.tmp_log)
    check3 = dict(log.check_log)
    log.report_log09.update(pwr3)
    log.report_log091.update(check3)

#   power data save
if save:
    fp = datadir + "PWR_DIFF_{}_{}_{}_0x{:02x}.bin".format("200mVBL","14_0mVfC","2_0us",0x00)
    with open(fp, 'wb') as fn:
        pickle.dump([pwr_meas3, fembs], fn)
#####   ====================== #####


######   6   DIFF monitor power rails   ######
log.report_log10["ITEM"] = "4.3 DIFF Power Rail"
power_rail_d = a_func.monitor_power_rail("DIFF", fembs, datadir, save)
power_rail_a = a_func.monitor_power_rail_analysis("DIFF", datadir, fembNo)
log10 = dict(log.power_rail_report_log)
log.report_log10.update(log10)
log.report_log101 = dict(log.check_log)

##################################
#      PART 05 Monitor Path      #
##################################
###### Take monitoring data ######
chk.femb_cd_rst()

mon_refs, mon_temps, mon_adcs = a_func.monitoring_path(fembs, snc, sg0,sg1,datadir, save)

a_func.mon_path_ana(fembs, mon_refs, mon_temps, mon_adcs, datareport, fembNo, env)

#================   Final Report    ===================================
a_repo.final_report(datareport, fembs, fembNo)

t2=time.time()
print(t2-t1)
####### Power off FEMBs #######
print("Turning off FEMBs")
chk.femb_powering([])
print("\n\n\n\n\n\n")