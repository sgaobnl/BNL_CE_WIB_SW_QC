import sys, os 
import numpy as np
import pickle, struct
import time, datetime, random, statistics
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

fp = sys.argv[1]
sfn = fp.split("/") #default
if "/" in fp:
    sfn = fp.split("/")
elif "\\" in fp:
    sfn = fp.split("\\")
p = fp.find(sfn[-1])
fdir = fp[0:p]

with open(fp, 'rb') as fn:
    ch_data = pickle.load(fn)


fdir = os.getcwd() + "/" + fp[:-4] + "_wfs"

if not os.path.exists(fdir):
    os.mkdir(fdir)

for ch, rawdata in enumerate(ch_data):
    
    # fig, ax = plt.subplots(figsize=(10,6))
    num_16bwords = 0x8000 / 2
    words16b = list(struct.unpack_from("<%dH"%(num_16bwords),rawdata))

    chip = ch // 16
    if ch % 16 == 0:
        # fig, axs = plt.subplots(4, 4, 16, figsize=(15, 15))
        plt.figure(figsize=(15,15))
    # row = (ch % 16) // 4
    # column = ch % 4
    plt.subplot(4,4,ch%16+1)
    # axs[row][column].plot(words16b,color='C%d'%chip)
    plt.plot(words16b,color='C%d'%chip)
    # axs[row][column].title("Channel "+str(ch))
    plt.title("Channel "+str(ch))
    
    # plt.ylabel("ADC counts")
    
    if ch % 16 == 15:
        plt.suptitle("ENOB waveform for Chip "+str(chip))
        # fig.text(0.5, 0.04, 'common X', ha='center')
        # plt.text(0.04, 0.5, 'ADC counts', va='center', rotation='vertical')
        plt.tight_layout()
        plt.show()
        #plt.savefig(fdir+"/chip"+str(chip)+"_wf.jpg")
        plt.close()
        input ("wait...")
