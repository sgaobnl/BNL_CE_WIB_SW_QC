
from wib_cfgs import WIB_CFGS
import time
import sys
import pickle
import copy
import os
import time, datetime, random, statistics
from TP_tools import ana_tools
import numpy as np

def CreateFolders(fembNo, env, toytpc):

    #datadir = "/mnt/towibs/tmp/FEMB_QC_data/CHK/"
    datadir = "./TestPattern/"
    datadir = datadir + "{}_{}".format(env, toytpc)
    for key,femb_no in fembNo.items():
        datadir = datadir + "_femb{}".format(femb_no)


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
        env = "TPL"
    else:
        env = "TPR"
    logs['env']=env

    ToyTPC_en = input("ToyTPC at FE inputs (Y/N) : ")
    if ("Y" in ToyTPC_en) or ("y" in ToyTPC_en):
        toytpc = "TPC_pF"
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

# set FEMB voltages
chk.fembs_vol_set(vfe=3.0, vcd=3.0, vadc=3.5)

print("Check FEMB currents")

fembs_remove = []
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
print("Check FEMB registers")
chk.femb_cd_rst()
time.sleep(0.1)
for ifemb in fembs:
    chk.femb_cd_fc_act(ifemb, act_cmd="rst_adcs")
    time.sleep(0.01)
    chk.femb_cd_fc_act(ifemb, act_cmd="rst_larasics")
    time.sleep(0.01)
    chk.femb_cd_fc_act(ifemb, act_cmd="rst_larasic_spi")
time.sleep(0.1)

for ifemb in fembs:
    errflag = chk.femb_cd_chkreg(ifemb)
    if errflag:
       print("FEMB ID {} faild COLDATA register check 1, will skip this femb".format(fembNo['femb%d'%ifemb]))
       outfile.write("FEMB ID {} faild COLDATA register 1 check\n".format(fembNo['femb%d'%ifemb]))
       fembs.remove(ifemb)
       fembNo.pop('femb%d'%ifemb)
       continue

    errflag = chk.femb_adc_chkreg(ifemb)
    if errflag:
       print("FEMB ID {} faild COLDADC register check 1, will skip this femb".format(fembNo['femb%d'%ifemb]))
       outfile.write("FEMB ID {} faild COLDADC register 1 check\n".format(fembNo['femb%d'%ifemb]))
       fembs.remove(ifemb)
       fembNo.pop('femb%d'%ifemb)

################ reset COLDATA, COLDADC and LArASIC ##############
print("Reset FEMBs")
chk.femb_cd_rst()
time.sleep(0.1)
for ifemb in fembs:
    chk.femb_cd_fc_act(ifemb, act_cmd="rst_adcs")
    time.sleep(0.01)
    chk.femb_cd_fc_act(ifemb, act_cmd="rst_larasics")
    time.sleep(0.01)
    chk.femb_cd_fc_act(ifemb, act_cmd="rst_larasic_spi")

time.sleep(0.1)
################ check the default COLDATA and COLDADC register ###########
print("Check FEMB registers")
for ifemb in fembs:
    errflag = chk.femb_cd_chkreg(ifemb)
    if errflag:
       print("FEMB ID {} faild COLDATA register check 2, will skip this femb".format(fembNo['femb%d'%ifemb]))
       outfile.write("FEMB ID {} faild COLDATA register 2 check\n".format(fembNo['femb%d'%ifemb]))
       fembs.remove(ifemb)
       fembNo.pop('femb%d'%ifemb)
       continue

    errflag = chk.femb_adc_chkreg(ifemb)
    if errflag:
       print("FEMB ID {} faild COLDADC register check 2, will skip this femb".format(fembNo['femb%d'%ifemb]))
       outfile.write("FEMB ID {} faild COLDADC register 2 check\n".format(fembNo['femb%d'%ifemb]))
       fembs.remove(ifemb)
       fembNo.pop('femb%d'%ifemb)

################# enable certain fembs ###################

chk.wib_femb_link_en(fembs)

chk.adcs_paras = [  # c_id, data_fmt(0x89), diff_en(0x84), sdc_en(0x80), vrefp, vrefn, vcmo, vcmi, autocali
    [0x4, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 2],
    [0x5, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 2],
    [0x6, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 2],
    [0x7, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 2],
    [0x8, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 2],
    [0x9, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 2],
    [0xA, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 2],
    [0xB, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 2],
]

V_Range = [0]*128
c = 0
################ Measure RMS at 200mV, 14mV/fC, 2us ###################
for i in range(0x1C, 0x3F):
    print("\n")
    print(V_Range)
    chk.pll = i
    print("PLL value = ", end="")
    print(hex(i), end=" ")
    print("Take TestPattern data")
    snc = 1 # 200 mV
    sg0 = 0
    sg1 = 0 # 14mV/fC
    st0 = 1
    st1 = 1 # 2us
    print("Check FEMB registers")

    chk.femb_cd_rst()
    cfg_paras_rec = []
    for femb_id in fembs:
        # errflag = chk.femb_cd_chkreg(femb_id)
        # if errflag:
        #    print("FEMB ID {} faild COLDATA register check 2, will skip this femb".format(fembNo['femb%d'%femb_id]))
        #    outfile.write("FEMB ID {} faild COLDATA register 2 check\n".format(fembNo['femb%d'%femb_id]))
        #    fembs.remove(femb_id)
        #    fembNo.pop('femb%d'%femb_id)
        #    continue
        chk.set_fe_board(sts=0, snc=snc, sg0=sg0, sg1=sg1, st0=st0, st1=st1, swdac=0, dac=0x00 )
        adac_pls_en = 0
        cfg_paras_rec.append( (femb_id, copy.deepcopy(chk.adcs_paras), copy.deepcopy(chk.regs_int8), adac_pls_en) )
        chk.femb_cfg(femb_id, adac_pls_en )

    chk.data_align(fembs)
    time.sleep(0.5)

    rms_rawdata = chk.spybuf_trig(fembs=fembs, num_samples=sample_N, trig_cmd=0) #returns list of size 1

    file_name = "Raw_SE_{}_{}_{}_0x{:02x}_{}.bin".format("200mVBL","14_0mVfC","2_0us",0x00, hex(i))
    ''' # begin   
    if save:
        fp = datadir + file_name
        with open(fp, 'wb') as fn:
            pickle.dump( [rms_rawdata, cfg_paras_rec, fembs], fn)

    # with open('./TestPattern/rms.dat', 'w') as f:
    #     for data in rms_rawdata:
    #         f.write(str(data))


    #=========== analysis ===================
    fdata = datadir
    print(fdata)
    frms = fdata+file_name
    print(frms)
    with open(frms, 'rb') as fn:
        raw = pickle.load(fn)

    rmsdata = raw[0]
    fembs = raw[2]
# end
'''
    PLOTDIR=datadir
    print(PLOTDIR)


    qc_tools = ana_tools()

    #pldata,_ = qc_tools.data_decode(rmsdata, fembs)
    pldata = qc_tools.data_decode(rms_rawdata, fembs)
    pldata = np.array(pldata)

    for ifemb in fembs:
        fp = PLOTDIR
        #ped,rms=qc_tools.GetRMS(pldata, ifemb, fp, "SE_200mVBL_14_0mVfC_2_0us")
        ped,rms=qc_tools.GetRMS(pldata, ifemb, fp, file_name)
        # if judge:
        #     V_Range[c] = hex(i)
    c = c + 1












print("Turning off FEMBs")
chk.femb_powering([])

t2=time.time()
print(t2-t1)
'''
'''