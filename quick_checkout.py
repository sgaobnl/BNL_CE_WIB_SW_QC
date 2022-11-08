from wib_cfgs import WIB_CFGS
import time
import sys
import numpy as np
import pickle
import copy
import os
import time, datetime, random, statistics
from QC_tools import QC_tools
from fpdf import FPDF

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
    
    reportdir = "reports/"
    PLOTDIR = {}

    for ifemb,femb_no in fembNo.items():
        plotdir = reportdir + "FEMB{}_{}_{}".format(femb_no, env, toytpc)
    
        n=1
        while (os.path.exists(plotdir)):
            if n==1:
                plotdir = plotdir + "_R{:03d}".format(n)
            else:
                plotdir = plotdir[:-3] + "{:03d}".format(n)
            n=n+1
            if n>20:
                raise Exception("There are more than 20 FEMB{} folders...".format(femb_no))
        
        try:
            os.makedirs(plotdir)
        except OSError:
            print ("Error to create folder %s"%plotdir)
            sys.exit()
    
        PLOTDIR[ifemb] = plotdir+'/'

    return datadir,PLOTDIR 

def GenReport(fembNo, rawdata, pwr_meas, mon_refs, mon_temps, mon_adcs, logs, PLOTDIR, nchips):

    qc_tools = QC_tools()
   
    femb_list = [int(ifemb[-1]) for ifemb,_ in fembNo.items()]
    print(femb_list)
 
    pldata = qc_tools.data_decode(rawdata, femb_list)
    pldata = np.array(pldata)
    
    qc_tools.PrintMON(fembNo, nchips, mon_refs, mon_temps, mon_adcs, PLOTDIR)
    
    for ifemb,femb_no in fembNo.items():
        i=int(ifemb[-1])
    
        plotdir = PLOTDIR[ifemb]
        ana = qc_tools.data_ana(pldata,i)
        fp_data = plotdir+"SE_response"
        qc_tools.FEMB_CHK_PLOT(ana[0], ana[1], ana[2], ana[3], ana[4], ana[5], fp_data)
    
        fp_pwr = plotdir+"pwr_meas"
        qc_tools.PrintPWR(pwr_meas, i, fp_pwr)
    
        pdf = FPDF(orientation = 'P', unit = 'mm', format='Letter')
        pdf.alias_nb_pages()
        pdf.add_page()
        pdf.set_auto_page_break(False,0)
        pdf.set_font('Times', 'B', 20)
        pdf.cell(85)
        pdf.l_margin = pdf.l_margin*2
        pdf.cell(30, 5, 'FEMB#{:04d} Checkout Test Report'.format(int(femb_no)), 0, 1, 'C')
        pdf.ln(2)
    
        pdf.set_font('Times', '', 12)
        pdf.cell(30, 5, 'Tester: {}'.format(logs["tester"]), 0, 0)
        pdf.cell(80)
        pdf.cell(30, 5, 'Date: {}'.format(logs["date"]), 0, 1)
    
    
        pdf.cell(30, 5, 'Temperature: {}'.format(logs["env"]), 0, 0)
        pdf.cell(80)
        pdf.cell(30, 5, 'Input Capacitor(Cd): {}'.format(logs["toytpc"]), 0, 1)
        pdf.cell(30, 5, 'Note: {}'.format(logs["note"][0:80]), 0, 1)
        pdf.cell(30, 5, 'FEMB configuration: {}, {}, {}, {}, DAC=0x{:02x}'.format("200mVBL","14_0mVfC","2_0us","500pA",0x20), 0, 1)
    
        pwr_image = fp_pwr+".png"
        pdf.image(pwr_image,0,40,200,40)
    
        mon_image = plotdir+"mon_meas.png"
        pdf.image(mon_image,0,80,200,40)
    
        chk_image = fp_data+".png"
        pdf.image(chk_image,3,120,200,120)
    
        outfile = plotdir+'report.pdf'
        pdf.output(outfile, "F")

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

####### Create data save directory #######
if save:
    datadir,PLOTDIR=CreateFolders(fembNo, env, toytpc)
    fp = datadir + "logs_env.bin"
    with open(fp, 'wb') as fn:
         pickle.dump(logs, fn)

t1 = time.time()
####### Power and configue FEMBs #######
chk = WIB_CFGS()
chk.wib_rst_tp()
chk.wib_fw()
chk.wib_timing(pll=True, fp1_ptc0_sel=0, cmd_stamp_sync = 0x0)

#set FEMB voltages
chk.fembs_vol_set(vfe=3.0, vcd=3.0, vadc=3.5)

#power on FEMBs
chk.femb_powering(fembs)
time.sleep(2)
pwr_meas = chk.get_sensors()
chk.femb_cd_rst()

snc = 1 # 200 mV
sg0 = 0
sg1 = 0 # 14mV/fC
st0 = 1 
st1 = 1 # 2us 

cfg_paras_rec = []
for femb_id in fembs:
    chk.adcs_paras = [ # c_id, data_fmt(0x89), diff_en(0x84), sdc_en(0x80), vrefp, vrefn, vcmo, vcmi, autocali
                        [0x4, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 1],
                        [0x5, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 1],
                        [0x6, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 1],
                        [0x7, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 1],
                        [0x8, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 1],
                        [0x9, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 1],
                        [0xA, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 1],
                        [0xB, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 1],
                      ]
    chk.set_fe_board(sts=1, snc=snc, sg0=sg0, sg1=sg1, st0=st0, st1=st1, swdac=1, dac=0x20 )
    adac_pls_en = 1 
    cfg_paras_rec.append( (femb_id, copy.deepcopy(chk.adcs_paras), copy.deepcopy(chk.regs_int8), adac_pls_en) )
    chk.femb_cfg(femb_id, adac_pls_en )

time.sleep(0.5)

####### Take data #######
rawdata = chk.spybuf_trig(fembs=fembs, num_samples=sample_N, trig_cmd=0) #returns list of size 1
pwr_meas = chk.get_sensors()

####### Save data #######
if save:
    fp = datadir + "Raw_SE_{}_{}_{}_0x{:02x}.bin".format("200mVBL","14_0mVfC","2_0us",0x20)

    with open(fp, 'wb') as fn:
        pickle.dump( [rawdata, pwr_meas, cfg_paras_rec, logs], fn)

####### Take monitoring data #######
sps=1
print ("monitor bandgap reference")
nchips=[0,4]
mon_refs = {}
for i in nchips:   # 8 chips per femb
    adcrst = chk.wib_fe_mon(femb_ids=fembs, mon_type=2, mon_chip=i, snc=snc, sg0=sg0, sg1=sg1, sps=sps)
    mon_refs[f"chip{i}"] = adcrst

print ("monitor temperature")
mon_temps = {}
for i in nchips:
    adcrst = chk.wib_fe_mon(femb_ids=fembs, mon_type=1, mon_chip=i, snc=snc, sg0=sg0, sg1=sg1, sps=sps)
    mon_temps[f"chip{i}"] = adcrst

print ("monitor ColdADCs")
mon_adcs = {}
for i in nchips:
    mon_adc =  chk.wib_adc_mon_chip(femb_ids=fembs, mon_chip=i, sps=sps)
    mon_adcs[f"chip{i}"] = mon_adc

if save:
    fp = datadir + "Mon_{}_{}.bin".format("200mVBL","14_0mVfC")

    with open(fp, 'wb') as fn:
        pickle.dump( [mon_refs, mon_temps, mon_adcs, logs], fn)

####### Power off FEMBs #######
print("Turning off FEMBs")
chk.femb_powering([])

####### Generate report #######
if save:
   GenReport(fembNo, rawdata, pwr_meas, mon_refs, mon_temps, mon_adcs, logs, PLOTDIR, nchips)

t2=time.time()
print(t2-t1)
