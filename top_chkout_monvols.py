from wib_cfgs import WIB_CFGS
import time
import sys
import numpy as np
import pickle
import copy
import time, datetime, random, statistics

fembs = [0]

chk = WIB_CFGS()
#check if WIB is in position
chk.wib_fw()

def vol_cal(vms_dict, femb_id):
    LSB = 2.048/16384
    vols = {}
    for key in vms_dict:
        xs = []
        for x in vms_dict[key]:
            xs.append(x[femb_id])
        mxs = np.mean(xs)
        vols[key] = mxs*LSB
    for key in vols:
        if 'GND' not in key:
            if "_HALF" in key:
                vols[key] = (vols[key]-vols['GND'])*2
            else:
                vols[key] = (vols[key]-vols['GND'])
    return vols


##set FEMB voltages
#chk.fembs_vol_set(vfe=3.0, vcd=3.0, vadc=3.5)
##power on FEMBs
#chk.femb_powering(fembs)
#time.sleep(2)
#pwr_meas = chk.get_sensors()
#for key in pwr_meas:
#    if "FEMB0_" in key:
#        print (key, ":", pwr_meas[key])
#
#print ("################")
#
#
#
#vms_dict = chk.wib_vol_mon(femb_ids=fembs)
#vols= vol_cal(vms_dict, femb_id=fembs[0])
#for key in vols:
#    print (key, ":", vols[key])
#
#input ("continue")
#


#a = chk.femb_LN2QC_powering(fembs)
#for key in a.keys():
#    print (key, a[key])

a = chk.femb_power_com_on(fembs)
for key in a.keys():
    print (key, a[key])
input ("aaa")
time.sleep(1)
chk.femb_powering(fembs=[])
exit()

a = chk.femb_power_com_step1(fembs)
print (a)
a = chk.femb_power_com_step2(fembs)
print (a)
a = chk.femb_power_com_step3(fembs)
print (a)
input ("off")
a = chk.femb_power_com_off(fembs)

#power off FEMBs
chk.femb_powering([])
time.sleep(2)
pwr_meas = chk.get_sensors()
for key in pwr_meas:
    if "FEMB0_" in key:
        print (key, ":", pwr_meas[key])

exit()
#set FEMB voltages
chk.fembs_vol_set(vfe=3.0, vcd=3.0, vadc=3.5)
#power on FEMBs
chk.femb_powering(fembs)
time.sleep(2)
pwr_meas = chk.get_sensors()
for key in pwr_meas:
    if "FEMB0_" in key:
        print (key, ":", pwr_meas[key])

print ("################")



vms_dict = chk.wib_vol_mon(femb_ids=fembs)
vols= vol_cal(vms_dict, femb_id=fembs[0])
for key in vols:
    print (key, ":", vols[key])

input ("continue")


#chk.wib_femb_link_en(fembs)
#chk.femb_cd_rst()

#time.sleep(3)

#cfg_paras_rec = []
#for femb_id in fembs:
#    chk.adcs_paras = [ # c_id, data_fmt(0x89), diff_en(0x84), sdc_en(0x80), vrefp, vrefn, vcmo, vcmi, autocali
#                        [0x4, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 1],
#                        [0x5, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 1],
#                        [0x6, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 1],
#                        [0x7, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 1],
#                        [0x8, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 1],
#                        [0x9, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 1],
#                        [0xA, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 1],
#                        [0xB, 0x08, 0, 0, 0xDF, 0x33, 0x89, 0x67, 1],
#                      ]
#    chk.set_fe_board(sts=0, snc=0,sg0=0, sg1=0, st0=0, st1=0, swdac=1, sdd=0,dac=0x20 )
#    adac_pls_en = 1 #enable LArASIC interal calibraiton pulser
#    cfg_paras_rec.append( (femb_id, copy.deepcopy(chk.adcs_paras), copy.deepcopy(chk.regs_int8), adac_pls_en) )
#    chk.fe_flg[femb_id] = True
#    chk.femb_cfg(femb_id, adac_pls_en )
#
#print ("################")
#vms_dict = chk.wib_vol_mon(femb_ids=fembs)
#vols= vol_cal(vms_dict, femb_id=fembs[0])
#for key in vols:
#    print (key, ":", vols[key])


print ("################")

#power off FEMBs
chk.femb_powering([])
time.sleep(2)
pwr_meas = chk.get_sensors()
for key in pwr_meas:
    if "FEMB0_" in key:
        print (key, ":", pwr_meas[key])



if False: # FE monitoring 
    if True: # FE monitoring 
        chips = 8
        sps=10
        if True:
            print ("monitor bandgap reference")
            mon_refs = {}
            for mon_chip in range(chips):
                #adcrst = chk.wib_fe_mon(femb_ids=fembs, mon_type=2, mon_chip=mon_chip, sps=sps, sdf=1)
                #print (adcrst)
                adcrst = chk.wib_fe_mon(femb_ids=fembs, mon_type=2, mon_chip=mon_chip, sps=sps, sdf=0)
                print (adcrst)
                print ("###################")
        exit()


        sps = 100 
        if True:
            print ("monitor vdac ")
            mon_refs = {}
            #for mon_chip in range(chips):

            #for mon_chip in [1]:
            while True:
                #for mon_chip in range(chips):
                for mon_chip in [0]:
                    adcrst = chk.wib_fe_dac_mon(femb_ids=fembs, mon_chip=mon_chip, sgp=False, sg0=1, sg1=0, vdacs=range(64), sps = sps )
                    brd = 0
                    k0 = adcrst[0][4][0][brd]
                    for y in adcrst:
                       # print (y[2], y[4][0][brd]-k0, (y[4][0][brd]-k0)*2048.0/(2**14))
                        k0 = y[4][0][brd]

                    k0s = []
                    for b in range(sps):

                        k0s.append(adcrst[0][4][b][brd])

                    mk0 = np.mean(k0s)
                    for y in adcrst:
                        k1s = []
                        for b in range(sps):
                            k1s.append(y[4][b][brd])
                        mk1 = np.mean(k1s)

                        print (y[2], y[4][0][brd]-k0, int(mk1-mk0), int((y[4][0][brd]-k0)*25000.0/(2**14)), int((mk1-mk0)*25000.0/(2**14)))
                        mk0=mk1
                        k0 = y[4][0][brd]

                    exit()
                break


        exit()

        if True:
            print ("monitor power rails")
            vold = chk.wib_vol_mon(femb_ids=fembs,sps=sps)
            dkeys = list(vold.keys())
            print (dkeys)
            LSB = 2.048/16384
            for fembid in fembs:
                vgnd = vold["GND"][0][fembid]
                print (vgnd)
                for key in dkeys:
                    if "GND" in key:
                        print ( key, vold[key][0][fembid], vold[key][0][fembid]*LSB) 
                    elif "HALF" in key:
                        print ( key, vold[key][0][fembid], (vold[key][0][fembid]-vgnd)*LSB*2, "voltage offset caused by power cable is substracted") 
                    else:
                        print ( key, vold[key][0][fembid], (vold[key][0][fembid]-vgnd)*LSB, "voltage offset caused by power cable is substracted") 
            print ("###################")
        exit()

        if True:
            print ("monitor bandgap reference")
            mon_refs = {}
            for mon_chip in range(chips):
                adcrst = chk.wib_fe_mon(femb_ids=fembs, mon_type=2, mon_chip=mon_chip, sps=sps, sdf=1)
                print (adcrst)
                adcrst = chk.wib_fe_mon(femb_ids=fembs, mon_type=2, mon_chip=mon_chip, sps=sps, sdf=0)
                print (adcrst)
                print ("###################")

##
        if True:
            print ("monitor temperature")
            mon_temps = {}
            for mon_chip in range(chips):
                adcrst = chk.wib_fe_mon(femb_ids=fembs, mon_type=1, mon_chip=mon_chip, sps=sps, sdf=1)
                print (adcrst)
                adcrst = chk.wib_fe_mon(femb_ids=fembs, mon_type=1, mon_chip=mon_chip, sps=sps, sdf=0)
                print (adcrst)
                print ("###################")


        if True:
            print ("monitor BL")
            mon_temps = {}
            for mon_chip in range(chips):
                for chni in range(16):
                    adcrst = chk.wib_fe_mon(femb_ids=fembs, mon_type=0, mon_chip=mon_chip, mon_chipchn=chni, snc=1, sdf=0, sps=sps)
                    print (mon_chip*16+chni, adcrst)
                    adcrst = chk.wib_fe_mon(femb_ids=fembs, mon_type=0, mon_chip=mon_chip, mon_chipchn=0, snc=0, sdf=1, sps=sps)
                    print (adcrst)
                    adcrst = chk.wib_fe_mon(femb_ids=fembs, mon_type=0, mon_chip=mon_chip, mon_chipchn=0, snc=1, sdf=0, sps=sps)
                    print (adcrst)
                    adcrst = chk.wib_fe_mon(femb_ids=fembs, mon_type=0, mon_chip=mon_chip, mon_chipchn=0, snc=1, sdf=1, sps=sps)
                    print (adcrst)

        if True:
            print ("monitor vdac ")
            mon_refs = {}
            #for mon_chip in range(chips):
            #for mon_chip in [1]:
            while True:
                for mon_chip in range(chips):
                    #adcrst = chk.wib_fe_dac_mon(femb_ids=fembs, mon_chip=mon_chip, sgp=True, sg0=0, sg1=0, vdacs=range(0,64,8), sps = 1 )
                    adcrst = chk.wib_fe_dac_mon(femb_ids=fembs, mon_chip=mon_chip, sgp=True, sg0=0, sg1=0, vdacs=[63], sps = 1 )
                    print (adcrst)
                for mon_chip in range(chips):
                    #adcrst = chk.wib_fe_dac_mon(femb_ids=fembs, mon_chip=mon_chip, sgp=True, sg0=0, sg1=0, vdacs=range(0,64,8), sps = 1 )
                    adcrst = chk.wib_fe_dac_mon(femb_ids=fembs, mon_chip=mon_chip, sgp=True, sg0=0, sg1=0, vdacs=[0], sps = 1 )
                    print (adcrst)
                break

#        if True:
#            print ("monitor vdac ")
#            mon_refs = {}
#            #for mon_chip in range(chips):
#            #for mon_chip in [1]:
#            for mon_chip in range(chips):
#                adcrst = chk.wib_fe_dac_mon(femb_ids=fembs, mon_chip=mon_chip, sgp=True, sg0=1, sg1=0, vdacs=[64], sps = 1 )
#                print (adcrst)

        if True:
            print ("monitor bandgap reference")
            mon_refs = {}
            #for mon_chip in range(chips):
            #for mon_chip in [1]:
            for mon_chip in range(chips):
                adcrst = chk.wib_fe_mon(femb_ids=fembs, mon_type=2, mon_chip=mon_chip, sps=sps)
                #chk.wib_fe_dac_mon(femb_ids=fembs, mon_chip=0,sgp=True, sg0=1, sg1=0, vdacs=range(64), sps = 3 )
                print (adcrst)
     
        #if True:
        #    print ("monitor temperature")
        #    mon_temps = {}
        #    for mon_chip in range(chips):
        #        adcrst = chk.wib_fe_mon(femb_ids=fembs, mon_type=1, mon_chip=mon_chip, sps=sps)
        #        mon_ts=time.time_ns()
        #        mon_temps[f"chip{mon_chip}_temper"] = adcrst
        #    mon_paras.append([ip,mon_temps, mon_ts])

