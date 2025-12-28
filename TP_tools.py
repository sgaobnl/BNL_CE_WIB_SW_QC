from spymemory_decode import wib_spy_dec_syn
import numpy as np
import matplotlib.pyplot as plt
import pickle
from scipy.optimize import curve_fit
import pandas as pd
import statistics
from spymemory_decode import wib_dec


def ResFunc(x, par0, par1, par2, par3):
    xx = x - par2

    A1 = 4.31054 * par0
    A2 = 2.6202 * par0
    A3 = 0.464924 * par0
    A4 = 0.762456 * par0
    A5 = 0.327684 * par0

    E1 = np.exp(-2.94809 * xx / par1)
    E2 = np.exp(-2.82833 * xx / par1)
    E3 = np.exp(-2.40318 * xx / par1)

    lambda1 = 1.19361 * xx / par1
    lambda2 = 2.38722 * xx / par1
    lambda3 = 2.5928 * xx / par1
    lambda4 = 5.18561 * xx / par1

    return par3 + (A1 * E1 - A2 * E2 * (
                np.cos(lambda1) + np.cos(lambda1) * np.cos(lambda2) + np.sin(lambda1) * np.sin(lambda2)) + A3 * E3 * (
                               np.cos(lambda3) + np.cos(lambda3) * np.cos(lambda4) + np.sin(lambda3) * np.sin(
                           lambda4)) + A4 * E2 * (
                               np.sin(lambda1) - np.cos(lambda2) * np.sin(lambda1) + np.cos(lambda1) * np.sin(
                           lambda2)) - A5 * E3 * (
                               np.sin(lambda3) - np.cos(lambda4) * np.sin(lambda3) + np.cos(lambda3) * np.sin(
                           lambda4))) * np.heaviside(xx, 1)


def FitFunc(pldata, shapetime, makeplot=False):  # pldata is the 500 samples

    pmax = np.amax(pldata)
    maxpos = np.argmax(pldata)

    if shapetime == 0.5:
        nbf = 2
        naf = 4

    if shapetime == 1:
        nbf = 3
        naf = 6

    if shapetime == 2:
        nbf = 5
        naf = 8

    if shapetime == 3:
        nbf = 7
        naf = 10

    pbl = pldata[maxpos - nbf]
    a_xx = np.array(range(nbf + naf)) * 0.5
    popt, pcov = curve_fit(ResFunc, a_xx, pldata[maxpos - nbf:maxpos + naf], maxfev=10000, p0=[pmax, shapetime, 0, pbl])
    nbf_1 = 10
    naf_1 = 10
    a_xx = np.array(range(nbf_1 + naf_1)) * 0.5
    popt_1, pcov_1 = curve_fit(ResFunc, a_xx, pldata[maxpos - nbf_1:maxpos + naf_1], maxfev=10000,
                               p0=[popt[0], popt[1], popt[2] + (nbf_1 - nbf) * 0.5, popt[3]])

    if makeplot:
        fig, ax = plt.subplots()
        ax.scatter(a_xx, pldata[maxpos - nbf_1:maxpos + naf_1], c='r')
        xx = np.linspace(0, nbf_1 + naf_1, 100) * 0.5
        ax.plot(xx, ResFunc(xx, popt_1[0], popt_1[1], popt_1[2], popt_1[3]))
        ax.set_xlabel('us')
        ax.set_ylabel('ADC')
        ax.text(0.6, 0.8, 'A0=%.2f' % popt_1[0], fontsize=15, transform=ax.transAxes)
        ax.text(0.6, 0.7, 'tp=%.2f' % popt_1[1], fontsize=15, transform=ax.transAxes)
        ax.text(0.6, 0.6, 't0=%.2f' % popt_1[2], fontsize=15, transform=ax.transAxes)
        ax.text(0.6, 0.5, 'bl=%.2f' % popt_1[3], fontsize=15, transform=ax.transAxes)
        plt.show()

    return popt_1


class ana_tools:
    def __init__(self):
        self.fadc = 1 / (2 ** 14) * 2048  # mV

    def data_decode(self,raw,fembs):
        wibdata = wib_dec(data=raw, fembs=fembs,fastchk = False, cd0cd1sync=True)
        return wibdata

    # def data_decode(self, raw, fembs):
    #
    #     nevent = len(raw)
    #     sss = []
    #     ttt = []
    #
    #     for i in range(nevent):
    #         data = raw[i][0]
    #         buf_end_addr = raw[i][1]
    #         trigger_rec_ticks = raw[i][2]
    #         if raw[i][3] != 0:
    #             trigmode = 'HW';
    #         else:
    #             trigmode = 'SW';
    #
    #         buf0 = data[0]
    #         buf1 = data[1]
    #
    #         wib_data = wib_spy_dec_syn(buf0, buf1, trigmode, buf_end_addr, trigger_rec_ticks, fembs)
    #
    #         if (0 in fembs) or (1 in fembs):
    #             nsamples0 = len(wib_data[0])
    #         else:
    #             nsamples0 = -1
    #         if (2 in fembs) or (3 in fembs):
    #             nsamples1 = len(wib_data[1])
    #         else:
    #             nsamples1 = -1
    #         if (nsamples0 > 0) and (nsamples1 > 0):
    #             if nsamples0 > nsamples1:
    #                 nsamples = nsamples1
    #             else:
    #                 nsamples = nsamples0
    #         elif nsamples0 > 0:
    #             nsamples = nsamples0
    #         elif nsamples1 > 0:
    #             nsamples = nsamples1
    #
    #         chns = []
    #         tmst0 = []
    #         tmst1 = []
    #         for j in range(nsamples):
    #             if 0 in fembs:
    #                 a0 = wib_data[0][j]["FEMB0_2"]
    #             else:
    #                 a0 = [0] * 128
    #
    #             if 1 in fembs:
    #                 a1 = wib_data[0][j]["FEMB1_3"]
    #             else:
    #                 a1 = [0] * 128
    #
    #             if 2 in fembs:
    #                 a2 = wib_data[1][j]["FEMB0_2"]
    #             else:
    #                 a2 = [0] * 128
    #
    #             if 3 in fembs:
    #                 a3 = wib_data[1][j]["FEMB1_3"]
    #             else:
    #                 a3 = [0] * 128
    #
    #             if 0 in fembs or 1 in fembs:
    #                 t0 = wib_data[0][j]["TMTS"]
    #             else:
    #                 t0 = 0
    #
    #             if 2 in fembs or 3 in fembs:
    #                 t1 = wib_data[1][j]["TMTS"]
    #             else:
    #                 t1 = 0
    #
    #             aa = a0 + a1 + a2 + a3
    #             chns.append(aa)
    #             tmst0.append(t0)
    #             tmst1.append(t1)
    #
    #         chns = list(zip(*chns))
    #         sss.append(chns)
    #         ttt.append([tmst0, tmst1])
    #
    #     return sss, ttt

    def GetRMS(self, data, nfemb, fp, fname):

        nevent = len(data)

        rms = []
        ped = []

        for ich in range(128):
            global_ch = nfemb * 128 + ich
            peddata = np.empty(0)

            npulse = 0
            first = True
            allpls = np.empty(0)
            for itr in range(nevent):
                evtdata = data[itr][nfemb][ich]
                allpls = np.append(allpls, evtdata)

            ch_ped = np.mean(allpls)
            ch_rms = np.std(allpls)

            ped.append(ch_ped)
            rms.append(ch_rms)

        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(range(128), rms, marker='.')
        ax.set_title(fname)
        ax.set_xlabel("chan")
        ax.set_ylabel("rms")
        fp_fig = fp + "rms_{}.png".format(fname)
        plt.savefig(fp_fig)
        plt.close(fig)

        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(range(128), ped, marker='.')
        ax.set_title(fname)
        ax.set_xlabel("chan")
        ax.set_ylabel("ped")
        fp_fig = fp + "ped_{}.png".format(fname)
        plt.savefig(fp_fig)
        plt.close(fig)

        fp_bin = fp + "RMS_{}.bin".format(fname)
        with open(fp_bin, 'wb') as fn:
            pickle.dump([ped, rms], fn)

        return ped, rms
