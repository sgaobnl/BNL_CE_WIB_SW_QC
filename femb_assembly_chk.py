from wib_cfgs import WIB_CFGS
import time
import sys
import pickle
import copy
import os
import time, datetime, random, statistics

def CreateFolders(fembNo, env, toytpc):

    datadir = "tmp_data/"
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

outfile = open("results_femb_assembly_chk.txt", "w")
t1 = time.time()

################## Power on FEMBs and check currents ##################
chk = WIB_CFGS()
chk.wib_fw()

# set FEMB voltages
chk.fembs_vol_set(vfe=3.0, vcd=3.0, vadc=3.5)

for ifemb in fembs:
    chk.femb_powering_single(ifemb, 'on')
    pwr_meas1 = chk.get_sensors()

    bias_i = round(pwr_meas1['FEMB%d_BIAS_I'%ifemb],3)  
    fe_i = round(pwr_meas1['FEMB%d_DC2DC0_I'%ifemb],3)
    cd_i = round(pwr_meas1['FEMB%d_DC2DC1_I'%ifemb],3)
    adc_i = round(pwr_meas1['FEMB%d_DC2DC2_I'%ifemb],3)

    hasERROR = False
    if abs(bias_i)>0.05:
       print("ERROR: FEMB{} BIAS current |{}|>0.05A".format(ifemb,bias_i)) 
       hasERROR = True

    if fe_i>0.6 or fe_i<0.3:
       print("ERROR: FEMB{} LArASIC current {} out of range (0.3A,0.6A)".format(ifemb,fe_i)) 
       hasERROR = True

    if cd_i>0.3 or cd_i<0.1:
       print("ERROR: FEMB{} COLDATA current {} out of range (0.1A,0.3A)".format(ifemb,cd_i)) 
       hasERROR = True

    if adc_i>1.8 or adc_i<1.2:
       print("ERROR: FEMB{} ColdADC current {} out of range (1.2A,1.8A)".format(ifemb,adc_i)) 
       hasERROR = True

    if hasERROR:
       Print("FEMB ID {} faild current check, will skip this femb".format(fembNo['femb%d'%ifemb]))
       outfile.write("FEMB ID {} faild current #1 check".format(fembNo['femb%d'%ifemb]))
       outfile.write("BIAS current: %f"%bias_i)
       outfile.write("LArASIC current: %f"%fe_i)
       outfile.write("COLDATA current: %f"%cd_i)
       outfile.write("ColdADC current: %f"%adc_i)
       fembs.remove(ifemb)
       fembNo.pop('femb%d'%ifemb)
       chk.femb_powering_single(ifemb, 'off')
       
################# check the default COLDATA and COLDADC register ##################
for ifemb in fembs:
    errflag = chk.femb_cd_chkreg(femb_id)
    if errflag:
       Print("FEMB ID {} faild COLDATA register check 1, will skip this femb".format(fembNo['femb%d'%ifemb]))
       outfile.write("FEMB ID {} faild COLDATA register 1 check".format(fembNo['femb%d'%ifemb]))
       fembs.remove(ifemb)
       fembNo.pop('femb%d'%ifemb)

    errflag = chk.femb_adc_chkreg(femb_id)
    if errflag:
       Print("FEMB ID {} faild COLDADC register check 1, will skip this femb".format(fembNo['femb%d'%ifemb]))
       outfile.write("FEMB ID {} faild COLDADC register 1 check".format(fembNo['femb%d'%ifemb]))
       fembs.remove(ifemb)
       fembNo.pop('femb%d'%ifemb)

################ reset COLDATA, COLDADC and LArASIC ##############
chk.femb_cd_rst()
time.sleep(0.01)
for ifemb in fembs:
    chk.femb_cd_fc_act(femb_id, act_cmd="rst_adcs")
    time.sleep(0.01)
    chk.femb_cd_fc_act(femb_id, act_cmd="rst_larasics")
    time.sleep(0.01)
    chk.femb_cd_fc_act(femb_id, act_cmd="rst_larasic_spi")

################ check the default COLDATA and COLDADC register ###########
for ifemb in fembs:
    errflag = chk.femb_cd_chkreg(femb_id)
    if errflag:
       Print("FEMB ID {} faild COLDATA register check 2, will skip this femb".format(fembNo['femb%d'%ifemb]))
       outfile.write("FEMB ID {} faild COLDATA register 2 check".format(fembNo['femb%d'%ifemb]))
       fembs.remove(ifemb)
       fembNo.pop('femb%d'%ifemb)

    errflag = chk.femb_adc_chkreg(femb_id)
    if errflag:
       Print("FEMB ID {} faild COLDADC register check 2, will skip this femb".format(fembNo['femb%d'%ifemb]))
       outfile.write("FEMB ID {} faild COLDADC register 2 check".format(fembNo['femb%d'%ifemb]))
       fembs.remove(ifemb)
       fembNo.pop('femb%d'%ifemb)

################# enable certain fembs ###################
chk.wib_femb_link_en(fembs)

################ Measure RMS at 200mV, 14mV/fC, 2us ###################
print("Take RMS data")
snc = 1 # 200 mV
sg0 = 0
sg1 = 0 # 14mV/fC
st0 = 1
st1 = 1 # 2us 

cfg_paras_rec = []
for femb_id in fembs:
    chk.set_fe_board(sts=0, snc=snc, sg0=sg0, sg1=sg1, st0=st0, st1=st1, swdac=0, dac=0x00 )
    adac_pls_en = 0
    cfg_paras_rec.append( (femb_id, copy.deepcopy(chk.adcs_paras), copy.deepcopy(chk.regs_int8), adac_pls_en) )
    chk.femb_cfg(femb_id, adac_pls_en )

chk.data_align(fembs)
time.sleep(0.5)

rms_rawdata = chk.spybuf_trig(fembs=fembs, num_samples=sample_N, trig_cmd=0) #returns list of size 1

if save:
    fp = datadir + "Raw_SE_{}_{}_{}_0x{:02x}.bin".format("200mVBL","14_0mVfC","2_0us",0x00)
    with open(fp, 'wb') as fn:
        pickle.dump( [rms_rawdata, cfg_paras_rec], fn)

################ Measure FEMB current 2 ####################
pwr_meas2 = chk.get_sensors()
for ifemb in fembs:
    bias_i = round(pwr_meas2['FEMB%d_BIAS_I'%ifemb],3)  
    fe_i = round(pwr_meas2['FEMB%d_DC2DC0_I'%ifemb],3)
    cd_i = round(pwr_meas2['FEMB%d_DC2DC1_I'%ifemb],3)
    adc_i = round(pwr_meas2['FEMB%d_DC2DC2_I'%ifemb],3)

    hasERROR = False
    if abs(bias_i)>0.02:
       print("ERROR: FEMB{} BIAS current |{}|>0.02A".format(ifemb,bias_i)) 
       hasERROR = True

    if fe_i>0.5 or fe_i<0.4:
       print("ERROR: FEMB{} LArASIC current {} out of range (0.4A,0.5A)".format(ifemb,fe_i)) 
       hasERROR = True

    if cd_i>0.3 or cd_i<0.2:
       print("ERROR: FEMB{} COLDATA current {} out of range (0.2A,0.3A)".format(ifemb,cd_i)) 
       hasERROR = True

    if adc_i>1.7 or adc_i<1.5:
       print("ERROR: FEMB{} ColdADC current {} out of range (1.5A,1.7A)".format(ifemb,adc_i)) 
       hasERROR = True

    if hasERROR:
       Print("FEMB ID {} faild current check 2. Test will continue".format(fembNo['femb%d'%ifemb]))
       outfile.write("FEMB ID {} faild current #2 check".format(fembNo['femb%d'%ifemb]))
       outfile.write("BIAS current: %f"%bias_i)
       outfile.write("LArASIC current: %f"%fe_i)
       outfile.write("COLDATA current: %f"%cd_i)
       outfile.write("ColdADC current: %f"%adc_i)

if save:
    fp = datadir + "PWR_SE_{}_{}_{}_0x{:02x}.bin".format("200mVBL","14_0mVfC","2_0us",0x00)
    with open(fp, 'wb') as fn:
        pickle.dump(pwr_meas2, fn)

############ Take pulse data 900mV 14mV/fC 2us ##################
print("Take pulse data")
snc = 0 # 900 mV
sg0 = 0
sg1 = 0 # 14mV/fC
st0 = 1
st1 = 1 # 2us 

cfg_paras_rec = []
for femb_id in fembs:
    chk.set_fe_board(sts=1, snc=snc, sg0=sg0, sg1=sg1, st0=st0, st1=st1, swdac=1, dac=0x20 )
    adac_pls_en = 1
    cfg_paras_rec.append( (femb_id, copy.deepcopy(chk.adcs_paras), copy.deepcopy(chk.regs_int8), adac_pls_en) )
    chk.femb_cfg(femb_id, adac_pls_en )

chk.data_align(fembs)
time.sleep(0.5)

pls_rawdata = chk.spybuf_trig(fembs=fembs, num_samples=sample_N, trig_cmd=0) #returns list of size 1

if save:
    fp = datadir + "Raw_SE_{}_{}_{}_0x{:02x}.bin".format("900mVBL","14_0mVfC","2_0us",0x20)
    with open(fp, 'wb') as fn:
        pickle.dump( [pls_rawdata, cfg_paras_rec], fn)

####### Take monitoring data #######
sps=1
print ("monitor bandgap reference")
nchips=range(8)
mon_refs = {}
for i in nchips:   # 8 chips per femb
    adcrst = chk.wib_fe_mon(femb_ids=fembs, mon_type=2, mon_chip=i, snc=snc, sg0=sg0, sg1=sg1, sps=sps)
    mon_refs[f"chip{i}"] = adcrst[7]

print ("monitor temperature")
mon_temps = {}
for i in nchips:
    adcrst = chk.wib_fe_mon(femb_ids=fembs, mon_type=1, mon_chip=i, snc=snc, sg0=sg0, sg1=sg1, sps=sps)
    mon_temps[f"chip{i}"] = adcrst[7]

print ("monitor ColdADCs")
mon_adcs = {}
for i in nchips:
    mon_adc =  chk.wib_adc_mon_chip(femb_ids=fembs, mon_chip=i, sps=sps)
    mon_adcs[f"chip{i}"] = mon_adc

if save:
    fp = datadir + "Mon_{}_{}.bin".format("200mVBL","14_0mVfC")

    with open(fp, 'wb') as fn:
        pickle.dump( [mon_refs, mon_temps, mon_adcs], fn)
####### Power off FEMBs #######
print("Turning off FEMBs")
chk.femb_powering([])

t2=time.time()
print(t2-t1)

