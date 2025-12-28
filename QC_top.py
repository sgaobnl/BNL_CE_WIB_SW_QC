from QC_runs import QC_Runs
import argparse
import time

ag = argparse.ArgumentParser()
ag.add_argument("fembs", help="a list of femb slots number", type=int, nargs='+')
#ag.add_argument("-s", "--save", help="number of pulses to be saved", type=int, default=1)
ag.add_argument("-t", "--task", help="which QC tasks to be performed", type=int, choices=range(1,17+1),  nargs='+', default=(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15,16, 17))
args = ag.parse_args()

fembs = args.fembs
#sampleN = args.save
tasks = args.task

#qc=QC_Runs(fembs, sampleN)
qc=QC_Runs(fembs)
# qc.pwr_fembs('on')

tt={}
for tm in tasks:
    print("start tm=",tm)
    if tm==1:
        t0=time.time()
        qc.pwr_consumption()

    if tm==2:
        t0=time.time()
        qc.pwr_cycle()
        qc.pwr_fembs('on')

       
    if tm==3:
        t0=time.time()
        qc.femb_leakage_cur()

    if tm==4:
        t0=time.time()
        qc.femb_chk_pulse()

    if tm==5:
        t0=time.time()
        qc.femb_rms()

    if tm==6:
        t0=time.time()
        qc.femb_CALI_1()

    if tm==7:
        t0=time.time()
        qc.femb_CALI_2()

    if tm==8:
        t0=time.time()
        qc.femb_CALI_3()

    if tm==9:
        t0=time.time()
        qc.femb_CALI_4()

    if tm==10:
        t0=time.time()
        qc.femb_MON_1()

    if tm==11:
        t0=time.time()
        qc.femb_MON_2()

    if tm==12:
        qc.pwr_fembs('on')
        t0=time.time()
        qc.femb_MON_3()

    if tm==13:
        t0=time.time()
        vdac_offset = 0.025
        qc.vgndoft = 0 + vdac_offset  # to be added later
        qc.vdacmax = 0.30 + vdac_offset
        qc.femb_CALI_5()  # external calibration 900mV BL

    if tm==14:
        t0=time.time()
        vdac_offset = 0.025
        qc.vgndoft = 0 + vdac_offset  # to be added later
        qc.vdacmax = 0.50 + vdac_offset
        qc.femb_CALI_6()  # external calibration 200mV BL

    if tm==15:
        t0=time.time()
        qc.femb_adc_sync_pat()

    if tm == 16:
        t0=time.time()
        qc.femb_test_pattern_pll()
        qc.pwr_fembs('off')

    if tm == 17: #debugging use only
        qc.debug_02()

# qc.pwr_fembs('off')
print(tt)
