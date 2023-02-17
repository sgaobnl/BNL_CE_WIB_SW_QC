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

t1 = time.time()

# Power on FEMBs
chk = WIB_CFGS()
chk.wib_fw()

# set FEMB voltages
chk.fembs_vol_set(vfe=3.0, vcd=3.0, vadc=3.5)
chk.femb_powering(fembs)
time.sleep(2)

# enable certain fembs
chk.wib_femb_link_en(fembs)

# check the default COLDATA and COLDADC register
for ifemb in fembs:
    errflag = chk.femb_cd_chkreg(self, femb_id):
    if errflag:
       Print("FEMB ID {} faild COLDATA register check 1, will skip this femb".format(fembNo['femb%d'%ifemb]))
       fembs.remove(ifemb)
       fembNo.pop('femb%d'%ifemb)

# reset COLDATA, COLDADC and LArASIC
chk.femb_cd_rst()
time.sleep(0.01)
for ifemb in fembs:
    chk.femb_cd_fc_act(femb_id, act_cmd="rst_adcs")
    time.sleep(0.01)
    chk.femb_cd_fc_act(femb_id, act_cmd="rst_larasics")
    time.sleep(0.01)
    chk.femb_cd_fc_act(femb_id, act_cmd="rst_larasic_spi")

# check the default COLDATA and COLDADC register
for ifemb in fembs:
    errflag = chk.femb_cd_chkreg(self, femb_id):
    if errflag:
       Print("FEMB ID {} faild COLDATA register check 2, will skip this femb".format(fembNo['femb%d'%ifemb]))
       fembs.remove(ifemb)
       fembNo.pop('femb%d'%ifemb)

# check ASICs' current
pwr_meas = chk.get_sensors()

