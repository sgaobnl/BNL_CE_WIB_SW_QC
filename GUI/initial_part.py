# library
# from QC_runs import QC_Runs
import argparse
import time
# from wib_cfgs import WIB_CFGS
import time
import sys
import pickle
import copy
import os
import datetime
import subprocess


tt=0
t1=time.time()

# Initial Part
## First   is the data acquisition
user_input_1 = "lke\nn\ny\ncom\nG9\nG10\nG11\nG12\n".encode("utf-8")# + b"6\n7\n8\n9\n"

## wib start up
action_1 = subprocess.run(['python3', './wib_startup.py'], capture_output=False, text=False)

## input information
logs={}
logs['date']=datetime.datetime.now().strftime("%m_%d_%Y_%H_%M_%S")
index_f = "./femb_info.csv"

with open(index_f, 'r') as fp:
    print(index_f)
    for cl in fp:
        tmp = cl.split(",")
        tmp = tmp[:-1]
        if "tester" not in tmp[0]:
            print(cl)
            logs[tmp[0]] = tmp[1]

# User Interaction
while True:
    # ensure the FEMB QC info
    csvfile = input("\033[95m Is femb_info.csv updated? (Y/N) : \033[0m")
    if ("Y" in csvfile) or ("y" in csvfile):
        pass
    else:
        input("click ENTER after you modify and save asic_info.csv.")
        continue

    fe_id = {}
    re_flg = False

    for FEMB in range(4):
        dkey = "FEMB%d" % FEMB
        festr = logs[dkey]
        print(festr)

    logs['date'] = datetime.datetime.now().strftime("%m_%d_%Y_%H_%M_%S")
    print(logs)
    break












# action_2 = subprocess.run(['python3', './wib_startup.py'], capture_output=False, text=False)
# action_3 = subprocess.run(['python3', './wib_startup.py'], capture_output=False, text=False)
