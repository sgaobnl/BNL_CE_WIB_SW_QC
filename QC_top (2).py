from QC_runs import QC_Runs
import argparse
import time

ag = argparse.ArgumentParser()
ag.add_argument("fembs", help="a list of femb slots number", type=int, nargs='+')
#ag.add_argument("-s", "--save", help="number of pulses to be saved", type=int, default=1)
ag.add_argument("-t", "--task", help="which QC tasks to be performed", type=int, choices=range(1,16+1),  nargs='+', default=(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16))
args = ag.parse_args()

fembs = args.fembs
#sampleN = args.save
tasks = args.task

#qc=QC_Runs(fembs, sampleN)
qc=QC_Runs(fembs)
qc.pwr_fembs('on')

tt={}
for tm in tasks:
    print("start tm=",tm)
    if tm==1:
        t0=time.time()
        qc.pwr_consumption()
        tt[tm] = time.time() - t0
        print ("Test{} comsums {} seconds".format(tm, tt[tm]))

    if tm==2:
        t0=time.time()
        qc.pwr_cycle()
        tt[tm] = time.time() - t0
        print ("Test{} comsums {} seconds".format(tm, tt[tm]))

       
    if tm==3:
        t0=time.time()
        qc.femb_leakage_cur()
        tt[tm] = time.time() - t0
        print ("Test{} comsums {} seconds".format(tm, tt[tm]))

    if tm==4:
        t0=time.time()
        qc.femb_chk_pulse()
        tt[tm] = time.time() - t0
        print ("Test{} comsums {} seconds".format(tm, tt[tm]))

    if tm==5:
        t0=time.time()
        qc.femb_rms()
        tt[tm] = time.time() - t0
        print ("Test{} comsums {} seconds".format(tm, tt[tm]))

    if tm==6:
        t0=time.time()
        qc.femb_CALI_1()
        tt[tm] = time.time() - t0
        print ("Test{} comsums {} seconds".format(tm, tt[tm]))

    if tm==7:
        t0=time.time()
        qc.femb_CALI_2()
        tt[tm] = time.time() - t0
        print ("Test{} comsums {} seconds".format(tm, tt[tm]))

    if tm==8:
        t0=time.time()
        qc.femb_CALI_3()
        tt[tm] = time.time() - t0
        print ("Test{} comsums {} seconds".format(tm, tt[tm]))

    if tm==9:
        t0=time.time()
        qc.femb_CALI_4()
        tt[tm] = time.time() - t0
        print ("Test{} comsums {} seconds".format(tm, tt[tm]))

    if tm==10:
        t0=time.time()
        qc.femb_MON_1()
        tt[tm] = time.time() - t0
        print ("Test{} comsums {} seconds".format(tm, tt[tm]))

    if tm==11:
        t0=time.time()
        qc.femb_MON_2()
        tt[tm] = time.time() - t0
        print ("Test{} comsums {} seconds".format(tm, tt[tm]))

    if tm==12:
        t0=time.time()
        qc.femb_MON_3()
        tt[tm] = time.time() - t0
        print ("Test{} comsums {} seconds".format(tm, tt[tm]))

    if tm==13:
        t0=time.time()
        vdac_offset = 0.025
        qc.vgndoft = 0 + vdac_offset  # to be added later
        qc.vdacmax = 0.50 + vdac_offset
        qc.femb_CALI_5()  # external calibration 900mV BL
        tt[tm] = time.time() - t0
        print ("Test{} comsums {} seconds".format(tm, tt[tm]))

    if tm==14:
        t0=time.time()
        vdac_offset = 0.025
        qc.vgndoft = 0 + vdac_offset  # to be added later
        qc.vdacmax = 0.50 + vdac_offset
        qc.femb_CALI_6()  # external calibration 200mV BL
        tt[tm] = time.time() - t0
        print ("Test{} comsums {} seconds".format(tm, tt[tm]))

    if tm==15:
        t0=time.time()
        qc.femb_adc_sync_pat()
        tt[tm] = time.time() - t0
        print ("Test{} comsums {} seconds".format(tm, tt[tm]))

    if tm == 16:
        t0=time.time()
        qc.femb_test_pattern_pll()
        tt[tm] = time.time() - t0
        print ("Test{} comsums {} seconds".format(tm, tt[tm]))

    if tm == 17: #debugging use only
        qc.LArASIC_Analog()

qc.pwr_fembs('off')
print(tt)
