import sys
import numpy as np
import pickle
import time, datetime, random, statistics
import matplotlib.pyplot as plt
import copy
from collections import defaultdict
import struct
from spymemory_decode import wib_dec
datadir = 'D:/GitHub/DAT_QC_HERMES/BNL_CE_WIB_SW_QC/tmp_data/'

snc = '200mVBL'
sgs = '4_7mVfC'
sts = '2_0us'
dac_list = range(0,64,4)
runi = 0
fembs = [1]
peakdic = defaultdict(dict)

chip = 6        #   issue chip
ref_chn = 4     #   issue channel

fig = plt.figure(figsize=(26, 13))
plt.subplot(1, 2, 1)
# plt.rcParams.update({'font.size': 14})

check_list = range(0,48,8)
for dac in dac_list:
    fdata = datadir + 'CALI1_SE_{}_{}_{}_0x{:02x}'.format(snc, sgs, sts, dac) + '.bin'
    with open(fdata,'rb') as fn:
        raw = pickle.load(fn)
        rawdata = raw[0]
        pwr_meas = raw[1]
        wibdata = wib_dec(rawdata, fembs, spy_num=5)
        datd = []
        fechndata = []
        for i in [0]:
            wibdatai = wibdata[i]
            datd = [wibdatai[0], wibdatai[1], wibdatai[2], wibdatai[3]][fembs[0]]
        rms = []
        pkp = []
        peak = []
        for fe in [chip]:  # range(8):
            for fe_chn in [ref_chn, ref_chn+3]:  # range(16):
                fechndata = datd[fe * 16 + fe_chn]
                rms.append(np.mean(fechndata))
                maxpos = np.argmax(fechndata[100:-300]) + 100
                blvalue = fechndata[maxpos - 10]
                maxvalue = fechndata[maxpos]
                peakdic[fe_chn][dac] = maxvalue-blvalue
                if dac in check_list:
                    if (dac / 8) % 2 == 0:
                        style = '-'
                    else:
                        style = '--'
                    if fe_chn == ref_chn:
                        # plt.text(0, maxvalue, '{}-{}'.format(maxvalue, blvalue), color='red')
                        plt.plot(range(0, 30, 1), fechndata[maxpos - 15: maxpos + 15], marker='.', linestyle = style, alpha=1, color='red',
                                 linewidth=1)
                        plt.plot(15, fechndata[maxpos], marker='^', markersize=12, alpha=1, color='red',
                                 linewidth=2.0)
                    else:
                        plt.text(7, maxvalue-50, 'DAC = {}'.format(dac), color='green', fontsize=16)
                        plt.plot(range(0, 30, 1), fechndata[maxpos - 15: maxpos + 15], marker='.', linestyle=style, alpha=1,
                                 color='green', linewidth=1)
                        plt.plot(15, fechndata[maxpos], marker='o', markersize=12, alpha=1, color='green',
                                 linewidth=2.0)

print(peakdic)
plt.title('CALI1_SE_200mVBL_4_7mVfC_2_0us', fontsize=24)
plt.plot(0,0,color='green', marker='o', markersize=12,label = "Normal_chip{}_ch{}".format(fe, ref_chn+3))
plt.plot(0,0,color='red', marker='^', markersize=12, label = "Issue_chip{}_ch{}".format(fe, ref_chn))
plt.legend(prop={'family': 'serif', 'size': 24})
plt.ylabel("Amplitude / ADC bit", fontsize=20)
plt.xlim((5, 30))
plt.ylim((0, 9000))
plt.xlabel("Time / 500 ns", fontsize=20)
plt.grid()
# plt.show()
xray = []
xray2 = []
chip1=[]
chip2=[]
chk1=[]
chk2=[]
for i in dac_list:
    xray.append(i)
    chip1.append(peakdic[ref_chn][i])
    chip2.append(peakdic[ref_chn + 3][i])
    if i in check_list:
        xray2.append(i)
        chk1.append(peakdic[ref_chn][i])
        chk2.append(peakdic[ref_chn + 3][i])

plt.subplot(1, 2, 2)
plt.title("Linearity of the Positive Peak", fontsize=24)
print(chip1)
# j = 0
# for i in dac_list:
#     print(i)
#     if i in check_list:
#         if chip1[j] < 12000:
#             plt.plot(dac_list[j], chip1[j], marker='o', linestyle='-', alpha=0.9,  color='red', linewidth = 2.0, label="issue_chip{}_ch{}".format(fe, ref_chn))
#         else:
#             plt.plot(dac_list[j], chip1[j], marker='o', alpha=0.9, color='#009900', linewidth=2.0, label="issue_chip{}_ch{}".format(fe, ref_chn))
#     j = j + 1
# plt.plot(dac_list, chip2, marker='o', alpha=0.9,  color='#990000', linewidth = 2.0, label="normal_chip{}_ch{}".format(fe, ref_chn+1))
plt.plot(xray2,chk2, marker='o', markersize=15, alpha=1, color='green', linewidth=2.0, label="Normal_chip{}_ch{}".format(fe, ref_chn+3))
plt.plot(xray2,chk1, marker='^', markersize=12, alpha=1, color='red', linewidth=2.0, label="Issue_chip{}_ch{}".format(fe, ref_chn))

# for i in range(len(dac_list)):
#     print(i)
#     if dac_list[i] in check_list:
#         plt.plot(dac_list[i], chip2[i], marker='o', markersize=15, alpha=1, color='green', linewidth=2.0)
#         plt.plot(dac_list[i], chip1[i], marker='^', markersize = 12, alpha=1, color='red', linewidth=2.0)
plt.legend(prop={'family': 'serif', 'size': 24})
x_sticks = range(0, 48, 8)
plt.xticks(x_sticks)
# plt.xlim((0, 42))
plt.ylim(-1000, 8000)
plt.grid()
# peakdic[fe_chn][dac]
plt.title("Linearity of the Peak Value", fontsize=24)
plt.ylabel("Amplitude / ADC bit", fontsize=20)
plt.xlabel("DAC / bit", fontsize=20)

plt.show()

exit()










fp = 'D:/GitHub/DAT_QC_HERMES/BNL_CE_WIB_SW_QC/tmp_data/CALI1_SE_200mVBL_4_7mVfC_2_0us_0x0c.bin'
sfn = fp.split("/")  # default
if "/" in fp:
    sfn = fp.split("/")
elif "\\" in fp:
    sfn = fp.split("\\")
p = fp.find(sfn[-1])
fdir = fp[0:p]

with open(fp, 'rb') as fn:
    raw = pickle.load(fn)
print(fp[p + 31:-4])
dac = fp[p + 31:-4]
rawdata = raw[0]
pwr_meas = raw[1]
runi = 0
fembs = [1]
peakdic = defaultdict(dict)
wibdata = wib_dec(rawdata, fembs, spy_num=5)

datd = []
fechndata = []
for i in [0]:
    wibdatai = wibdata[i]
    datd = [wibdatai[0], wibdatai[1], wibdatai[2], wibdatai[3]][fembs[0]]


fig = plt.figure(figsize=(26, 13))
plt.subplot(1, 2, 1)
plt.rcParams.update({'font.size': 14})
rms = []
pkp = []
peak = []
chip = 0
ref_chn = 3
for fe in [chip]:  # range(8):
    for fe_chn in [ref_chn, ref_chn + 1]:  # range(16):
        fechndata = datd[fe * 16 + fe_chn]
        rms.append(np.mean(fechndata))
        # rms_tmp = round(np.std(fechndata), 2)
        maxpos = np.argmax(fechndata[100:-100]) + 100
        blvalue = fechndata[maxpos - 10]
        maxvalue = fechndata[maxpos]
        peakdic[fe_chn][dac] = maxvalue
        if fe_chn == ref_chn:
            plt.text(0, maxvalue, '{}-{}'.format(maxvalue,blvalue), color='#00FF00')
            plt.plot(range(0, 30, 1), fechndata[maxpos - 15: maxpos + 15], marker='.', alpha=1, color='#CCFFCC', linewidth = 1,
                     label="issue_chip{}_ch{}_{}".format(fe, fe_chn, dac))
        else:
            plt.text(0+5, maxvalue, '{}-{}'.format(maxvalue,blvalue), color='#FF0000')
            plt.plot(range(0, 30, 1), fechndata[maxpos - 15: maxpos + 15], marker='.', linestyle='--', alpha=1,
                     color='#FFCCCC',  linewidth = 1,label="normal_chip{}_ch{}_{}".format(fe, fe_chn, dac))

fp = 'D:/GitHub/DAT_QC_HERMES/BNL_CE_WIB_SW_QC/tmp_data/CALI1_SE_200mVBL_4_7mVfC_2_0us_0x1c.bin'
sfn = fp.split("/")  # default
if "/" in fp:
    sfn = fp.split("/")
elif "\\" in fp:
    sfn = fp.split("\\")
p = fp.find(sfn[-1])
fdir = fp[0:p]

with open(fp, 'rb') as fn:
    raw = pickle.load(fn)
print(fp[p + 31:-4])
dac = fp[p + 31:-4]
rawdata = raw[0]
pwr_meas = raw[1]
runi = 0

wibdata = wib_dec(rawdata, fembs, spy_num=5)

datd2 = []
fechndata = []
for i in [0]:
    wibdatai = wibdata[i]
    datd2 = [wibdatai[0], wibdatai[1], wibdatai[2], wibdatai[3]][fembs[0]]

# fig = plt.figure(figsize=(8, 6))
# plt.rcParams.update({'font.size': 14})
rms = []
pkp = []
for fe in [chip]:  # range(8):
    for fe_chn in [ref_chn, ref_chn + 1]:  # range(16):
        fechndata = datd2[fe * 16 + fe_chn]
        rms.append(np.mean(fechndata))
        # rms_tmp = round(np.std(fechndata), 2)
        maxpos = np.argmax(fechndata[100:-100]) + 100
        blvalue = fechndata[maxpos-10]
        maxvalue = fechndata[maxpos]
        peakdic[fe_chn][dac] = maxvalue
        if fe_chn == ref_chn:
            plt.text(0, maxvalue, '{}-{}'.format(maxvalue,blvalue), color='#00FF00')
            plt.plot(range(0, 30, 1), fechndata[maxpos - 15: maxpos + 15], marker='.', alpha=0.9,  color='#66FF66', linewidth = 2.0, label="issue_chip{}_ch{}_{}".format(fe, fe_chn, dac))
        else:
            plt.text(0+5, maxvalue, '{}-{}'.format(maxvalue,blvalue), color='#FF0000')
            plt.plot(range(0, 30, 1), fechndata[maxpos - 15: maxpos + 15], marker='.', linestyle='--', alpha=0.9, color='#FF6666', linewidth = 2.0, label="normal_chip{}_ch{}_{}".format(fe, fe_chn, dac))







fp = 'D:/GitHub/DAT_QC_HERMES/BNL_CE_WIB_SW_QC/tmp_data/CALI1_SE_200mVBL_4_7mVfC_2_0us_0x2c.bin'
sfn = fp.split("/")  # default
if "/" in fp:
    sfn = fp.split("/")
elif "\\" in fp:
    sfn = fp.split("\\")
p = fp.find(sfn[-1])
fdir = fp[0:p]

with open(fp, 'rb') as fn:
    raw = pickle.load(fn)
print(fp[p + 31:-4])
dac = fp[p + 31:-4]
rawdata = raw[0]
pwr_meas = raw[1]
runi = 0

wibdata = wib_dec(rawdata, fembs, spy_num=5)

datd2 = []
fechndata = []
for i in [0]:
    wibdatai = wibdata[i]
    datd2 = [wibdatai[0], wibdatai[1], wibdatai[2], wibdatai[3]][fembs[0]]

# fig = plt.figure(figsize=(8, 6))
# plt.rcParams.update({'font.size': 14})
rms = []
pkp = []
for fe in [chip]:  # range(8):
    for fe_chn in [ref_chn, ref_chn + 1]:  # range(16):
        fechndata = datd2[fe * 16 + fe_chn]
        rms.append(np.mean(fechndata))
        # rms_tmp = round(np.std(fechndata), 2)
        maxpos = np.argmax(fechndata[100:-100]) + 100
        blvalue = fechndata[maxpos - 10]
        maxvalue = fechndata[maxpos]
        peakdic[fe_chn][dac] = maxvalue
        if fe_chn == ref_chn:
            plt.text(0, maxvalue, '{}-{}'.format(maxvalue,blvalue), color='#00FF00')
            plt.plot(range(0, 30, 1), fechndata[maxpos - 15: maxpos + 15], marker='.', alpha=0.9,  color='#00FF00', linewidth = 2.0, label="issue_chip{}_ch{}_{}".format(fe, fe_chn, dac))
        else:
            plt.text(0+5, maxvalue, '{}-{}'.format(maxvalue,blvalue), color='#FF0000')
            plt.plot(range(0, 30, 1), fechndata[maxpos - 15: maxpos + 15], marker='.', linestyle='--', alpha=0.9, color='#FF0000', linewidth = 2.0, label="normal_chip{}_ch{}_{}".format(fe, fe_chn, dac))

fp = 'D:/GitHub/DAT_QC_HERMES/BNL_CE_WIB_SW_QC/tmp_data/CALI1_SE_200mVBL_4_7mVfC_2_0us_0x3c.bin'
sfn = fp.split("/")  # default
if "/" in fp:
    sfn = fp.split("/")
elif "\\" in fp:
    sfn = fp.split("\\")
p = fp.find(sfn[-1])
fdir = fp[0:p]

with open(fp, 'rb') as fn:
    raw = pickle.load(fn)
print(fp[p + 31:-4])
dac = fp[p + 31:-4]
inf = fp[p :-9]
print(inf)
rawdata = raw[0]
pwr_meas = raw[1]
runi = 0

wibdata = wib_dec(rawdata, fembs, spy_num=5)

datd2 = []
fechndata = []
for i in [0]:
    wibdatai = wibdata[i]
    datd2 = [wibdatai[0], wibdatai[1], wibdatai[2], wibdatai[3]][fembs[0]]

# fig = plt.figure(figsize=(8, 6))
# plt.rcParams.update({'font.size': 14})
rms = []
pkp = []
for fe in [chip]:  # range(8):
    for fe_chn in [ref_chn, ref_chn + 1]:  # range(16):
        fechndata = datd2[fe * 16 + fe_chn]
        rms.append(np.mean(fechndata))
        # rms_tmp = round(np.std(fechndata), 2)
        maxpos = np.argmax(fechndata[100:-100]) + 100
        blvalue = fechndata[maxpos - 10]
        maxvalue = fechndata[maxpos]
        peakdic[fe_chn][dac] = maxvalue
        if fe_chn == ref_chn:
            plt.text(0, maxvalue, '{}-{}'.format(maxvalue,blvalue), color='#00FF00')
            plt.plot(range(0, 30, 1), fechndata[maxpos - 15: maxpos + 15], marker='.', alpha=0.9,  color='#009900', linewidth = 2.0, label="issue_chip{}_ch{}_{}".format(fe, fe_chn, dac))
        else:
            plt.text(0+5, maxvalue, '{}-{}'.format(maxvalue,blvalue), color='#FF0000')
            plt.plot(range(0, 30, 1), fechndata[maxpos - 15: maxpos + 15], marker='.', linestyle='--', alpha=0.9, color='#990000', linewidth = 2.0, label="normal_chip{}_ch{}_{}".format(fe, fe_chn, dac))

plt.title("{}".format(inf), fontsize=24)
plt.legend()
plt.ylabel("Amplitude / ADC bit", fontsize=20)
plt.xlim((0, 30))
plt.ylim((0, 16000))
plt.xlabel("Channel", fontsize=20)
plt.grid()

x= (12, 28, 44, 60)
chip1 = [peakdic[ref_chn]['0x0c'],peakdic[ref_chn]['0x1c'],peakdic[ref_chn]['0x2c'],peakdic[ref_chn]['0x3c']]
chip2 = [peakdic[ref_chn + 1]['0x0c'],peakdic[ref_chn + 1]['0x1c'],peakdic[ref_chn + 1]['0x2c'],peakdic[ref_chn + 1]['0x3c']]
print(peakdic)

coefficients = np.polyfit(x, chip1, deg=1)
fit_function = np.poly1d(coefficients)
fit_y = fit_function(x)
inl1 = round(np.max(abs(fit_y - chip1) * 100 / abs(chip1[0] - chip1[3])),2)
print(inl1)
coefficients = np.polyfit(x, chip2, deg=1)
fit_function = np.poly1d(coefficients)
fit_y = fit_function(x)
inl2 = round(np.max(abs(fit_y - chip2) * 100 / abs(chip2[0] - chip2[3])),2)
print(inl2)

plt.subplot(1, 2, 2)
plt.title("Linearity of the Peak Value", fontsize=24)
plt.plot(x, chip1, marker='o', alpha=0.9,  color='#009900', linewidth = 2.0, label="issue_chip{}_ch{}_inl={}%".format(fe, fe_chn, inl1))
plt.plot(x, chip2, marker='o', alpha=0.9,  color='#990000', linewidth = 2.0, label="normal_chip{}_ch{}_inl={}%".format(fe, fe_chn+1, inl2))
plt.legend()
plt.xlim((0, 64))
plt.ylim((0, 16000))
plt.grid()
# peakdic[fe_chn][dac]
plt.title("Linearity of the Peak Value", fontsize=24)
plt.ylabel("Amplitude / ADC bit", fontsize=20)
plt.xlabel("DAC / bit", fontsize=20)

# plt.tight_layout(rect=[0.05, 0.05, 0.95, 0.95])
plt.show()
plt.close()

exit()

# for xi in [0,4]:
#    datd = []
#    fechndata = []
#    for i in range(10):
#    #for i in [0]:
#        wibdatai = wibdata[i]
#        datd = [wibdatai[0], wibdatai[1],wibdatai[2],wibdatai[3]][fembs[0]]
#        for fe in [xi]:
#            for fe_chn in [0]:
#                fechndata = fechndata + list(datd[fe*16+fe_chn])
#
#    print (fe*16+fe_chn, "RMS=%.3f"%np.std(fechndata))
#    #print (len(fechndata))
##    import matplotlib.pyplot as plt
##    plt.plot(fechndata)
##    #plt.title("Waveform (leakage current = 500pA)")
##    plt.title("Waveform ")
##    plt.ylabel("ADC readout / bit")
##    plt.xlabel("Time (512ns/step)")
##    plt.show()
##    plt.close()
##
#    from fft_chn import chn_rfft_psd
#    f,p = chn_rfft_psd(fechndata,  fft_s = 2000, avg_cycle = 20)
#    import matplotlib.pyplot as plt
#    plt.plot(f,p)
#    #plt.title("Waveform (leakage current = 500pA)")
#    plt.title("FFT ")
#    plt.ylabel(" / dB ")
#    plt.xlabel("Freq / Hz")
#    plt.show()
#    plt.close()
##exit()
#####

if 0:
    import matplotlib.pyplot as plt

    rms = []
    pkp = []
    for fe in range(8):
        for fe_chn in range(16):
            fechndata = datd[fe * 16 + fe_chn]
            #            plt.plot(fechndata)
            #        print (np.std(fechndata))
            rms.append(np.std(fechndata))
    #            pkp.append(np.max(fechndata))
    #            rms.append(np.mean(fechndata))
    plt.plot(np.arange(64), rms[0:64], color='b', label="Tied")
    plt.plot(np.arange(64, 128, 1), rms[64:128], color='r', label="Separate")
    plt.legend()
    #    plt.plot(np.arange(128),pkp)

    #    ax1.set_title("Overlap Waveforms of CH0-63")
    #    ax1.set_ylabel("ADC readout / bit")
    #    ax1.set_xlabel("Time (512ns/step)")
    #    ax2.set_title("Overlap Waveforms of CH64-127")
    #    ax2.set_ylabel("ADC readout / bit")
    #    ax2.set_xlabel("Time (512ns/step)")
    #
    #
    #    ax1.grid()
    #    ax2.grid()
    plt.grid()

    plt.title("Noise distribution")
    plt.ylabel("RMS noise / bit")
    plt.xlabel("Channel")
    plt.tight_layout(rect=[0.05, 0.05, 0.95, 0.95])
    plt.show()
    plt.close()
    exit()

if 1:
    import matplotlib.pyplot as plt

    rms = []
    pkp = []
    ax1 = plt.subplot(211)
    ax2 = plt.subplot(212)
    for fe in range(8):
        # for fe in [4,5,6,7]:
        # for fe in [0,1,2,3]:
        for fe_chn in range(16):
            # for fe in [3]:
            #   for fe_chn in [0]:

            fechndata = datd[fe * 16 + fe_chn]
            if np.max(fechndata) > 12000:
                if fe * 16 + fe_chn < 64:
                    print("PLS w/ SE ON CHN %d" % (fe * 16 + fe_chn))
            if fe * 16 + fe_chn < 64:
                ax1.plot(fechndata[000:1400], color='b')
            else:
                ax2.plot(fechndata[000:1400], color='r')

    #            if fe*16+fe_chn < 16:
    #                ax1.plot(fechndata[000:2000], color='b' )
    #                #ax1.plot(fechndata, color='b' )
    #            elif fe*16+fe_chn < 32:
    #                ax1.plot(fechndata[000:2000], color='g' )
    #                #ax1.plot(fechndata, color='g' )
    #            elif fe*16+fe_chn < 48:
    #                ax1.plot(fechndata[000:2000], color='m' )
    #                #ax1.plot(fechndata, color='m' )
    #            elif fe*16+fe_chn < 64:
    #                ax1.plot(fechndata[000:2000], color='y' )
    #                #ax1.plot(fechndata, color='y' )
    #            else:
    #                #ax2.plot(fechndata[400:900], color='r')
    #                #ax2.plot(fechndata, color='r')
    #                if fe*16+fe_chn < 80:
    #                    ax2.plot(fechndata[000:2000], color='b' )
    #                    #ax1.plot(fechndata, color='b' )
    #                elif fe*16+fe_chn < 96:
    #                    ax2.plot(fechndata[000:2000], color='g' )
    #                    #ax1.plot(fechndata, color='g' )
    #                elif fe*16+fe_chn < 112:
    #                    ax2.plot(fechndata[000:2000], color='m' )
    #                    #ax1.plot(fechndata, color='m' )
    #                elif fe*16+fe_chn < 128:
    #                    ax2.plot(fechndata[000:2000], color='y' )
    #                    #ax1.plot(fechndata, color='y' )

    #        print (np.std(fechndata))
    #        rms.append(np.std(fechndata))
    #            pkp.append(np.max(fechndata))
    #            rms.append(np.mean(fechndata))
    #    plt.plot(np.arange(128),rms)
    #    plt.plot(np.arange(128),pkp)

    ax1.set_title("Overlap Waveforms of CH0-63")
    ax1.set_ylabel("ADC readout / bit")
    ax1.set_xlabel("Time (512ns/step)")
    ax2.set_title("Overlap Waveforms of CH64-127")
    ax2.set_ylabel("ADC readout / bit")
    ax2.set_xlabel("Time (512ns/step)")

    ax1.grid()
    ax2.grid()

    #    plt.title("Noise distribution")
    #    plt.ylabel("RMS noise / bit")
    #    plt.xlabel("Channel")
    plt.tight_layout(rect=[0.05, 0.05, 0.95, 0.95])
    plt.show()
    plt.close()
    exit()

##for xi in range(16):
for xi in [15]:
    datd = []
    fechndata = []
    for i in range(10):
        # for i in [0]:
        wibdatai = wibdata[i]
        datd = [wibdatai[0], wibdatai[1], wibdatai[2], wibdatai[3]][fembs[0]]
        for fe in [1]:
            for fe_chn in [xi]:
                fechndata = fechndata + list(datd[fe * 16 + fe_chn])

    print(fe * 16 + fe_chn, "RMS=%.3f" % np.std(fechndata))
    # print (len(fechndata))
    import matplotlib.pyplot as plt

    plt.plot(fechndata)
    # plt.title("Waveform (leakage current = 500pA)")
    plt.title("Waveform ")
    plt.ylabel("ADC readout / bit")
    plt.xlabel("Time (512ns/step)")
    plt.show()
    plt.close()

    import matplotlib.pyplot as plt

    # Create a histogram
    plt.hist(fechndata, bins=(np.max(fechndata) - np.min(fechndata) + 1), rwidth=0.8, color='blue', alpha=0.7)
    # Add labels and title
    plt.xlabel('Amplitude / bit')
    plt.ylabel('Counts')
    plt.title('Histogram Plot')
    # Show the plot
    plt.show()
    plt.close()

# exit()

# import matplotlib.pyplot as plt
# rms = []
# for fe in range(8):
##for fe in [2]:
#    for fe_chn in range(16):
#        fechndata = datd[fe*16+fe_chn]
#        #print (fe, fe_chn, np.std(fechndata))
#        #if np.max(fechndata) - np.mean(fechndata) > 6000:
#        #    pass
#        #else:
#        #    print (fe*16+fe_chn,fe, fe_chn)
#        #if fe*16+fe_chn < 64:
#        #    c = 'r'
#        #else:
#        #    c = 'b'
#        #c = 'r'
#        #plt.plot(fechndata)
#        #print (np.std(fechndata))
#        #rms.append(np.std(fechndata))
##print (rms)
##plt.plot(np.arange(128),rms)
# plt.show()
# plt.close()
#

# rms = []
##for fe in range(8):
# for fe in [1]:
##    for fe_chn in range(16):
#    for fe_chn in [15]:
#        import matplotlib.pyplot as plt
#        fechndata = datd[fe*16+fe_chn]
#        #print (fe, fe_chn, np.std(fechndata))
#        #if np.max(fechndata) - np.mean(fechndata) > 6000:
#        #    pass
#        #else:
#        #    print (fe*16+fe_chn,fe, fe_chn)
#        #if fe*16+fe_chn < 64:
#        #    c = 'r'
#        #else:
#        #    c = 'b'
#        c = 'r'
#        plt.plot(fechndata, color=c)
#        print (fe*16+fe_chn, np.std(fechndata))
#        #rms.append(np.std(fechndata))
#        #print (rms)
#        #plt.plot(np.arange(128),rms)
#        plt.show()
#        plt.close()
##bufs = [[],[],[],[],[],[],[],[]]
#
# for i in range(8):
#    bufs[i] = rawdata[runi][0][i]
#
# buf_end_addr = rawdata[runi][1]
# trigger_rec_ticks = rawdata[runi][2]
# if rawdata[runi][3] != 0:
#    trigmode = 'HW';
# else:
#    trigmode = 'SW';
#
# dec_data = wib_spy_dec_syn(bufs, trigmode, buf_end_addr, trigger_rec_ticks, fembs)
# print("Done decoding")
# flen = len(dec_data[0])
# for d in dec_data:
#    print(len(d))
#
# tmts = []
##sfs0 = [] #not in new format?
##sfs1 = []
# cdts_0 = [[],[],[],[],[],[],[],[]]
# cdts_1 = [[],[],[],[],[],[],[],[]]
# femb0 = []
# femb1 = []
# femb2 = []
# femb3 = []
#
# for i in range(flen):
#    tmts.append(dec_data[0][i]["TMTS"])
#    #print(hex(tmts[-1]))
#
#    for cd in range(8):
#        if cd // 2 in fembs:
#            cdts_0[cd].append(dec_data[cd][i]["FEMB_CD0TS"])
#            cdts_1[cd].append(dec_data[cd][i]["FEMB_CD1TS"])
#
#    if 0 in fembs:
#        chdata_64ticks = [dec_data[0][i]["CD_data"][tick] + dec_data[1][i]["CD_data"][tick] for tick in range(64)]
#        femb0 = femb0 + chdata_64ticks
#
#    if 1 in fembs:
#        chdata_64ticks = [dec_data[2][i]["CD_data"][tick] + dec_data[3][i]["CD_data"][tick] for tick in range(64)]
#        femb1 = femb1 + chdata_64ticks
#
#    if 2 in fembs:
#        chdata_64ticks = [dec_data[4][i]["CD_data"][tick] + dec_data[5][i]["CD_data"][tick] for tick in range(64)]
#        femb2 = femb2 + chdata_64ticks
#
#    if 3 in fembs:
#        chdata_64ticks = [dec_data[6][i]["CD_data"][tick] + dec_data[7][i]["CD_data"][tick] for tick in range(64)]
#        femb3 = femb3 + chdata_64ticks
#
# print (f"timestampe of first 10 events {tmts[0:10]}")
#
# femb0 = list(zip(*femb0))
# femb1 = list(zip(*femb1))
# femb2 = list(zip(*femb2))
# femb3 = list(zip(*femb3))
#
# wib = [femb0, femb1, femb2, femb3]
#
# x = np.arange(len(tmts)*64)
# x_tmts = np.arange(len(tmts))
#
# if True:
#    fig = plt.figure(figsize=(10,6))
#    plt.plot(x_tmts, np.array(tmts)-tmts[0], label ="Time Master Timestamp")
#    plt.plot(x_tmts, np.array(cdts_0[0])-cdts_0[0][0], label ="Coldata Timestamp (FEMB0 CD0)")
#    plt.plot(x_tmts, np.array(cdts_1[0])-cdts_1[0][0], label ="Coldata Timestamp (FEMB0 CD1)")
#    plt.legend()
#    #plt.show()
#    plt.savefig(fdir + "timestamp.jpg")
#    plt.close()
#
#    for fembi in fembs:
#        #maxpos = np.where(wib[fembi][0][0:1500] == np.max(wib[fembi][0][0:1500]))[0][0] #not used?
#        fig = plt.figure(figsize=(10,6))
#
#        for chip in range(8): #coldata
#            for chn in range(16):
#                i = chip*16 + chn
#                # if chn == 0:
#                   # plt.plot(x, wib[fembi][i],color = 'C%d'%chip, label = "Chip%dCH0"%chip )
#
#                # if not all(wib[fembi][i][tick] == wib[fembi][i][0] for tick in range(len(wib[fembi][i]))):
#                    # print("FEMB%dChip%dCH%d messed up"%(fembi,chip,chn))
#                # else:
#                    # print("Chip%dCH%d all channels = 0x%x"%(chip,chn,wib[fembi][i][0])) #all channels same value
#                plt.plot(x, wib[fembi][i],color = 'C%d'%chip )
#        plt.title(f"Waveform of FEMB{fembi}")
#        # plt.xlim([0,400])
#        # plt.ylim([0,1000])
#        #plt.legend()
#        ##plt.show()
#        plt.savefig(fdir + f"{fembi}_wf.jpg")
#        plt.close()
#
