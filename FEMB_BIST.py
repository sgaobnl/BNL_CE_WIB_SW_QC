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
user_input_1 = "lke\nn\ny\ncom\nB06\nB12\nB17\nB16\n".encode("utf-8")# + b"6\n7\n8\n9\n"
action_1 = subprocess.run(['python3', './femb_assembly_chk.py'] + ['0', '1', '2', '3', 'save', '5'],  input = user_input_1, capture_output=False, text=False)


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