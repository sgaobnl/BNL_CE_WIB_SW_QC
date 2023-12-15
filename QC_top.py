import sys
from QC_runs import QC_Runs
import argparse
import time

ag = argparse.ArgumentParser()
ag.add_argument("fembs", help="a list of femb slots number", type=int, nargs='+')
#ag.add_argument("-s", "--save", help="number of pulses to be saved", type=int, default=1)
ag.add_argument("-t", "--task", help="which QC tasks to be performed", type=int, choices=range(1,16+1),  nargs='+', default=range(1,16+1))
args = ag.parse_args()

fembs = args.fembs
#sampleN = args.save
tasks = args.task

#qc=QC_Runs(fembs, sampleN)
qc=QC_Runs(fembs)
qc.pwr_fembs('on')

tt={}
t1=time.time()
for tm in tasks:

    print("start tm=",tm)
    if tm==1:
       qc.pwr_consumption()

    if tm==2:
       qc.pwr_cycle()
       
    if tm==3:
       qc.femb_leakage_cur()
       
    if tm==4:
       qc.femb_chk_pulse()

    if tm==5:
       qc.femb_rms()

    if tm==6:
       qc.femb_CALI_1()

    if tm==7:
       qc.femb_CALI_2()

    if tm==8:
       qc.femb_CALI_3()

    if tm==9:
       qc.femb_CALI_4()

    if tm==10:
       qc.femb_MON_1()

    if tm==11:
       qc.femb_MON_2()

    if tm==12:
       qc.femb_MON_3()

    if tm==13:
       vdac_offset = 0.084
       qc.vgndoft = 1.04 + vdac_offset - 0.4  # to be added later
       qc.vdacmax = 1.04 + vdac_offset
       qc.femb_CALI_5()  # external calibration 900mV BL

    if tm==14:
       vdac_offset = 0.084
       qc.vgndoft = 1.04 + vdac_offset - 0.8  # to be added later
       qc.vdacmax = 1.04 + vdac_offset
       qc.femb_CALI_6()  # external calibration 200mV BL

    if tm==15:
       qc.femb_adc_sync_pat()

    # if tm == 16:
    #    qc.femb_test_pattern_pll()

t2=time.time()
tt[tm]=t2-t1
time.sleep(1)

qc.pwr_fembs('off')
print(tt)
