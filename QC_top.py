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
t1=time.time()
for tm in tasks:

    print("start tm=",tm)
    if tm==1:
        qc.pwr_consumption()
        t2 = time.time()
        print(t2-t1)


    if tm==2:
        qc.pwr_cycle()
        t3 = time.time()
        print(t3 - t2)
       
    if tm==3:
        qc.femb_leakage_cur()
        t4 = time.time()
        print(t4 - t3)
       
    if tm==4:
        qc.femb_chk_pulse()
        t5 = time.time()
        print(t5 - t4)
    if tm==5:
        qc.femb_rms()
        t6 = time.time()
        print(t6 - t5)
    if tm==6:
        qc.femb_CALI_1()
        t7 = time.time()
        print(t7 - t6)
    if tm==7:
        qc.femb_CALI_2()
        t8 = time.time()
        print(t8 - t7)
    if tm==8:
        qc.femb_CALI_3()
        t9 = time.time()
        print(t9 - t8)
    if tm==9:
        qc.femb_CALI_4()
        t10 = time.time()
        print(t10 - t9)
    if tm==10:
        qc.femb_MON_1()
        t11 = time.time()
        print(t11 - t10)
    if tm==11:
        qc.femb_MON_2()
        t12 = time.time()
        print(t12 - t1)
    if tm==12:
        qc.femb_MON_3()
        t13 = time.time()
        print(t13 - t12)
    if tm==13:
        vdac_offset = 0.025
        qc.vgndoft = 0 + vdac_offset  # to be added later
        qc.vdacmax = 0.50 + vdac_offset
        qc.femb_CALI_5()  # external calibration 900mV BL
        t14 = time.time()
        print(t14 - t13)
    if tm==14:
        vdac_offset = 0.025
        qc.vgndoft = 0 + vdac_offset  # to be added later
        qc.vdacmax = 0.50 + vdac_offset
        qc.femb_CALI_6()  # external calibration 200mV BL
        t15 = time.time()
        print(t15 - t14)
    if tm==15:
        qc.femb_adc_sync_pat()
        t16 = time.time()
        print(t16 - t15)
    if tm == 16:
        qc.femb_test_pattern_pll()
        t17 = time.time()
        print(t17 - t16)
    if tm == 17:
        qc.LArASIC_Analog()
t2=time.time()
tt[tm]=t2-t1
time.sleep(1)

qc.pwr_fembs('off')
print(tt)
