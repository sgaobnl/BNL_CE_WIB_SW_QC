import PIL

from wib_cfgs import WIB_CFGS
import time
import sys
import pickle
import copy
import datetime
from QC_tools import ana_tools

qc_tools = ana_tools()
# Create an array to store the merged image

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
    sample_N = int(sys.argv[pos + 1])
    sys.argv.remove('save')
    fembs = [int(a) for a in sys.argv[1:pos]]
else:
    save = False
    sample_N = 1
    fembs = [int(a) for a in sys.argv[1:]]

####### Input test information #######
if save:
    logs = {}
    tester = input("please input your name:  ")
    logs['tester'] = tester

    env_cs = input("Test is performed at cold(LN2) (Y/N)? : ")
    if ("Y" in env_cs) or ("y" in env_cs):
        env = "LN"
    else:
        env = "RT"
    logs['env'] = env

    ToyTPC_en = input("ToyTPC at FE inputs (Y/N) : ")
    if ("Y" in ToyTPC_en) or ("y" in ToyTPC_en):
        toytpc = "150pF"
    else:
        toytpc = "0pF"
    logs['toytpc'] = toytpc

    note = input("A short note (<200 letters):")
    logs['note'] = note

    fembNo = {}
    print(fembs)
    for i in fembs:
        print(i)
        fembNo['femb{}'.format(i)] = input("FEMB{} ID: ".format(i))

    logs['femb id'] = fembNo
    logs['date'] = datetime.datetime.now().strftime("%m_%d_%Y_%H_%M_%S")

    datadir = "./tmptest/"
    fp = datadir + "logs_env.txt"
    # with open(fp, 'wb') as fn:
    #     pickle.dump(logs, fn)

explan = logs


explan['first'] = 'linyun\n'
explan['first1'] = 'linyun1\n'
explan['first2'] = 'linyun2\n'

print(explan,  flush=True)

check_item = []