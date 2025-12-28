from wib_cfgs import WIB_CFGS
import time
import sys
import pickle
import copy
import os
import datetime
import subprocess



tt=0
t1=time.time()
#   First   is the data acquisition
user_input_1 = "y\n".encode("utf-8")# + b"6\n7\n8\n9\n"
action_1 = subprocess.run(['python3', './wib_startup.py'],  input = user_input_1, capture_output=False, text=False)
time.sleep(1)
action_2 = subprocess.run(['python3', './top_femb_powering.py'] + ['off', 'on', 'off', 'on'], capture_output=False, text=False)
time.sleep(3)
action_3 = subprocess.run(['python3', './top_chkout_pls_fake_timing.py'] + [ '1', '3', 'save', '5'],  input = user_input_1, capture_output=False, text=False)
time.sleep(1)
action_2 = subprocess.run(['python3', './top_femb_powering.py'] + ['off', 'off', 'off', 'off'], capture_output=False, text=False)


#   Second  is the data analysis
# with open("./CHK/chk_tmp.txt", 'r') as file:
#     args_name = [file.read()]
# print(args_name)
# action_1 = subprocess.run(['python3', './ana_femb_assembly_chk.py'] + args_name,  capture_output=False, text=False)

t2=time.time()
tt=t2-t1
print(tt)

def main():
    print("tihis is the main function")

if __name__ == "__main__":
    main()