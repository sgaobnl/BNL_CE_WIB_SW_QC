from wib_cfgs import WIB_CFGS
import ctypes, ctypes.util
import time
import sys
import numpy as np
import pickle
import copy
import time, datetime, random, statistics

if len(sys.argv) < 2:
    print('Please specify at least one FEMB # to test')
    print('Usage: python wib.py 0')
    exit()    

if 'save' in sys.argv:
    save = True
    for i in range(len(sys.argv)):
        if sys.argv[i] == 'save':
            pos = i
            break
    sample_N = int(sys.argv[pos+1] )
    sys.argv.remove('save')
else:
    save = False
    sample_N = 1

fembs = [int(a) for a in sys.argv[1:pos]] 

chk = WIB_CFGS()

wib_path = "/home/root/dat_sw/build/wib_util.so" #os.getcwd() + "/build/wib_util.so"
wib = ctypes.CDLL(wib_path)

####################WIB init################################
#check if WIB is in position
chk.wib_fw()
time.sleep(1)

####################FEMBs Configuration################################
#step 1
#reset all FEMBs on WIB
chk.femb_cd_rst()

cfg_paras_rec = []
for femb_id in fembs:
#step 2
#Configur Coldata, ColdADC, and LArASIC parameters. 
#Here Coldata uses default setting in the script (not the ASIC default register values)
#ColdADC configuraiton
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

#LArASIC register configuration
    chk.set_fe_board(sts=1, snc=1,sg0=0, sg1=0, st0=1, st1=1, sdf=0, swdac=1, sdd=0,dac=0x20 )
 #   chk.set_fechn_reg(chip=3,chn=0, sts=1, snc=1,sg0=0, sg1=0, st0=0, st1=0)
 #   chk.set_fechn_reg(chip=7,chn=0, sts=1, snc=1,sg0=0, sg1=0, st0=0, st1=0)

 #   chk.set_fechn_reg(chip=3,chn=1, sts=1, snc=1,sg0=0, sg1=0, st0=0, st1=0)
 #   chk.set_fechn_reg(chip=7,chn=1, sts=1, snc=1,sg0=0, sg1=0, st0=0, st1=0)

 #   chk.set_fechn_reg(chip=3,chn=2, sts=1, snc=1,sg0=0, sg1=0, st0=0, st1=0)
 #   chk.set_fechn_reg(chip=7,chn=2, sts=1, snc=1,sg0=0, sg1=0, st0=0, st1=0)

 #   chk.set_fechn_reg(chip=3,chn=3, sts=1, snc=1,sg0=0, sg1=0, st0=0, st1=0)
 #   chk.set_fechn_reg(chip=7,chn=3, sts=1, snc=1,sg0=0, sg1=0, st0=0, st1=0)

#    for tmp in range(16):
#        chk.set_fechn_reg(chip=3,chn=tmp, sts=1, snc=1,sg0=0, sg1=0, st0=0, st1=0) #, sdf=1)

 #   for tmp in [0,3,5,7]:
 #       chk.set_fechn_reg(chip=tmp,chn=5, sts=1, snc=1,sg0=0, sg1=0, st0=0, st1=0)

 #   for tmp in [0,3,7]:
 #       chk.set_fechn_reg(chip=tmp,chn=6, sts=1, snc=1,sg0=0, sg1=0, st0=0, st1=0)

 #   for tmp in [0,3,7]:
 #       chk.set_fechn_reg(chip=tmp,chn=7, sts=1, snc=1,sg0=0, sg1=0, st0=0, st1=0)
#    for tmp in range(16):
#        chk.set_fechn_reg(chip=6,chn=tmp, sts=1, snc=1,sg0=0, sg1=0, st0=0, st1=0)



#    chk.set_fechn_reg(chip=0,chn=0, sts=1, snc=1,sg0=0, sg1=0, st0=0, st1=0, sdf=1)
#    chk.set_fechn_reg(chip=1,chn=1, sts=1, snc=1,sg0=0, sg1=0, st0=0, st1=0, sdf=1)
#    chk.set_fechn_reg(chip=2,chn=2, sts=1, snc=1,sg0=0, sg1=0, st0=0, st1=0, sdf=1)
#    chk.set_fechn_reg(chip=3,chn=3, sts=1, snc=1,sg0=0, sg1=0, st0=0, st1=0, sdf=1)
#    chk.set_fechn_reg(chip=4,chn=4, sts=1, snc=1,sg0=0, sg1=0, st0=0, st1=0, sdf=1)
#    chk.set_fechn_reg(chip=5,chn=5, sts=1, snc=1,sg0=0, sg1=0, st0=0, st1=0, sdf=1)
#    chk.set_fechn_reg(chip=6,chn=6, sts=1, snc=1,sg0=0, sg1=0, st0=0, st1=0, sdf=1)
#    chk.set_fechn_reg(chip=7,chn=7, sts=1, snc=1,sg0=0, sg1=0, st0=0, st1=0, sdf=1)

#    chk.set_fechn_reg(chip=0,chn=8+0, sts=1, snc=1,sg0=0, sg1=0, st0=0, st1=0, sdf=1)
#    chk.set_fechn_reg(chip=1,chn=8+1, sts=1, snc=1,sg0=0, sg1=0, st0=0, st1=0, sdf=1)
#    chk.set_fechn_reg(chip=2,chn=8+2, sts=1, snc=1,sg0=0, sg1=0, st0=0, st1=0, sdf=1)
#    chk.set_fechn_reg(chip=3,chn=8+3, sts=1, snc=1,sg0=0, sg1=0, st0=0, st1=0, sdf=1)
#    chk.set_fechn_reg(chip=4,chn=8+4, sts=1, snc=1,sg0=0, sg1=0, st0=0, st1=0, sdf=1)
#    chk.set_fechn_reg(chip=5,chn=8+5, sts=1, snc=1,sg0=0, sg1=0, st0=0, st1=0, sdf=1)
#    chk.set_fechn_reg(chip=6,chn=8+6, sts=1, snc=1,sg0=0, sg1=0, st0=0, st1=0, sdf=1)
#    chk.set_fechn_reg(chip=7,chn=8+7, sts=1, snc=1,sg0=0, sg1=0, st0=0, st1=0, sdf=1)
#    chk.set_fechn_reg(chip=4,chn=8, sts=1, snc=1,sg0=0, sg1=0, st0=0, st1=0)
#    chk.set_fechn_reg(chip=4,chn=9, sts=1, snc=1,sg0=0, sg1=0, st0=0, st1=0)
#    chk.set_fechn_reg(chip=6,chn=8, sts=1, snc=1,sg0=0, sg1=0, st0=0, st1=0)
#    chk.set_fechn_reg(chip=6,chn=9, sts=1, snc=1,sg0=0, sg1=0, st0=0, st1=0)
#    chk.set_fechn_reg(chip=6,chn=10, sts=1, snc=1,sg0=0, sg1=0, st0=0, st1=0)
#    chk.set_fechn_reg(chip=7,chn=8, sts=1, snc=1,sg0=0, sg1=0, st0=0, st1=0)
#    chk.set_fechn_reg(chip=7,chn=9, sts=1, snc=1,sg0=0, sg1=0, st0=0, st1=0)
#    chk.set_fechn_reg(chip=7,chn=10, sts=1, snc=1,sg0=0, sg1=0, st0=0, st1=0)
    adac_pls_en = 1 #enable LArASIC interal calibraiton pulser
    cfg_paras_rec.append( (femb_id, copy.deepcopy(chk.adcs_paras), copy.deepcopy(chk.regs_int8), adac_pls_en) )
#step 3
    chk.femb_cfg(femb_id, adac_pls_en )

chk.data_align(fembs)

time.sleep(0.5)

####################FEMBs Data taking################################
rawdata = chk.spybuf_trig(fembs=fembs, num_samples=sample_N, trig_cmd=0) #returns list of size 1

pwr_meas = chk.get_sensors()

if save:
    fdir = "./tmp_data/"
    ts = datetime.datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
    fp = fdir + "Raw_" + ts  + ".bin"
    with open(fp, 'wb') as fn:
        pickle.dump( [rawdata, pwr_meas, cfg_paras_rec], fn)


################## FE Power Measurement ######################
def datpower_getvoltage(addr, cd=-1, fe=-1):
    return wib.datpower_getvoltage(addr, cd, fe)

def datpower_getcurrent(addr, cd=-1, fe=-1):
    return wib.datpower_getcurrent(addr, cd, fe)

fe_name = ["FE1", "FE2", "FE3", "FE4", "FE5", "FE6", "FE7", "FE8"]
addrs = [0x40, 0x41, 0x42, 0x43, 0x45, 0x46, 0x44]
name = ["VDD", "VDDO", "VPPP", "VDDA2P5", "VDDD2P5", "VDDIO", "VDDD1P2"]
V_LSB = 1.25e-3
I_LSB = 0.01e-3 #amps
R = 0.1 #ohms
cal = 0.00512/(I_LSB*R)
print("cal is",hex(int(cal)))
for fe in range(8):
# for cd in range(1):
    total_pwr_mw = 0
    for i in range(7):
    #addr = 0x40
        addr = addrs[i]


        bus_voltage = datpower_getvoltage(addr, fe=fe)
        current = datpower_getcurrent(addr, fe=fe)
        total_pwr_mw = total_pwr_mw + bus_voltage*current*1e+3

        print (fe_name[fe], name[i], "Voltage =\t", bus_voltage, "V") #0x40 nominal vals: 1.19 V
        print (fe_name[fe], name[i], "Current =\t", current*1e+3, "mA")# print("Current I (mA)=",  current*1e+3, "mA", hex(current_reg))                  #9.2 mA
        print (fe_name[fe], name[i], "Power =\t", bus_voltage*current*1e+3, "mW")
    print (fe_name[fe], "Total Power =\t", total_pwr_mw, "mW")
    print("")
