from spymemory_decode import wib_dec
import pickle
from scipy.optimize import curve_fit
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict
import QC_components.qc_log as log
import QC_check as QC_check
import csv
from scipy import stats
import platform

system_info = platform.system()

index_tmts = 5
if system_info == 'Linux':
    index_tmts = 5
elif system_info == 'Windows':
    index_tmts = 5


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

    def data_decode(self, raw, fembs):
        # wibdata = wib_dec(data=raw, fembs=fembs,fastchk = False, cd0cd1sync=True)
        wibdata = wib_dec(raw, fembs, spy_num=1, cd0cd1sync=False)
        return wibdata

    def pulse_ana(pls_rawdata, fembs, fembNo, datareport, fname):
        qc = ana_tools()
        pldata = qc.data_decode(pls_rawdata, fembs)

        for ifemb in range(len(fembs)):
            femb_id = "FEMB ID {}".format(fembNo['femb%d' % fembs[ifemb]])
            ppk, npk, bl = qc.GetPeaks(pldata, fembs[ifemb], datareport[fembs[ifemb]], fname, funcfit=False)
            # outfp = datareport[fembs[ifemb]] + "pulse_{}.bin".format(fname)
            # with open(outfp, 'wb') as fn:
            #      pickle.dump([ppk,npk,bl], fn)

            tmp = QC_check.CHKPulse(ppk)

            log.chkflag["Pulse"]["PPK"] = (tmp[0])
            log.badlist["Pulse"]["PPK"] = (tmp[1])

            tmp = QC_check.CHKPulse(npk)
            log.chkflag["Pulse"]["NPK"] = (tmp[0])
            log.badlist["Pulse"]["NPK"] = (tmp[1])

            tmp = QC_check.CHKPulse(bl)
            log.chkflag["Pulse"]["BL"] = (tmp[0])
            log.badlist["Pulse"]["BL"] = (tmp[1])

            if (log.chkflag["Pulse"]["PPK"] == False) and (log.chkflag["Pulse"]["NPK"] == False) and (
                    log.chkflag["Pulse"]["BL"] == False):
                log.report_log07[femb_id]["Result"] = True
            else:
                log.report_log07[femb_id]["Pulse PPK err_status"] = log.badlist["Pulse"]["PPK"]
                log.report_log07[femb_id]["Pulse NPK err_status"] = log.badlist["Pulse"]["NPK"]
                log.report_log07[femb_id]["Pulse BL err_status"] = log.badlist["Pulse"]["BL"]
                log.report_log07[femb_id]["Result"] = False

    def GetRMS(self, data, nfemb, fp, fname):
        """Calculate and plot the pedestal (PED) and root mean square (RMS) for each channel."""

        nevent = len(data)
        num_channels = 128

        ped, rms, pedmax, pedmin = [], [], [], []
        rms_max, rms_min = float('-inf'), float('inf')
        ped_max, ped_min = float('-inf'), float('inf')

        for ich in range(num_channels):
            allpls = np.concatenate([data[itr][nfemb][ich] for itr in range(nevent)])

            ch_ped = np.mean(allpls)
            ch_pedmax = np.max(allpls)
            ch_pedmin = np.min(allpls)
            ch_rms = np.std(allpls)

            ped.append(ch_ped)
            rms.append(ch_rms)
            pedmax.append(ch_pedmax)
            pedmin.append(ch_pedmin)

            rms_max = max(rms_max, ch_rms)
            rms_min = min(rms_min, ch_rms)
            ped_max = max(ped_max, ch_ped)
            ped_min = min(ped_min, ch_ped)

        fe_rms_mean, fe_ped_mean = np.mean(rms), np.mean(ped)

        self._plot_data(range(num_channels), rms, fname, "Root Mean Square", "rms", fp, fe_rms_mean, 8, rms_max, rms_min)
        self._plot_data(range(num_channels), ped, fname, "Pedestal", "ped", fp, fe_ped_mean, 500, ped_max, ped_min)

        self._save_data(fp, fname, ped, rms)

        return ped, rms, pedmax, pedmin

    def _plot_data(self, x, y, fname, ylabel, fprefix, fp, mean, threshold, max_val, min_val):
        """Helper function to plot and save figures."""
        plt.figure(figsize=(6, 4))
        plt.plot(x, y, marker='.', linestyle='-', alpha=0.7, label='mean of {}: {}'.format(fprefix,  f"{mean:.2f}"))
        plt.title('{} Distribution'.format(ylabel), fontsize=14)
        plt.xlabel("Channel", fontsize=14)
        plt.ylabel(ylabel, fontsize=14)
        plt.xticks(range(0, 129, 16))
        plt.grid(axis='x')

        if 'Root' in ylabel:
            if 'ADC' in fname:
                y_limlow = 0
                y_limhig = 10
            else:
                y_limlow = 0
                y_limhig = 50
        elif 'ADC' in fname:
            y_limlow = 0
            y_limhig = 16500
        elif '200' in fname:
            y_limlow = 500
            y_limhig = 1500
        else:
            y_limlow = 7900
            y_limhig = 9400

        if y_limlow <= min_val < max_val <= y_limhig:
            plt.ylim(y_limlow, y_limhig)
        else:
            plt.grid(axis='y')

        plt.gca().set_facecolor('none')
        plt.grid(True, axis='y', linestyle='--', alpha=0.3)
        plt.legend()
        plt.tight_layout()
        plt.savefig(f"{fp}{fprefix}_{fname}.png", transparent=True)
        plt.close()

    def _save_data(self, fp, fname, ped, rms):
        """Helper function to save pedestal and RMS data."""
        with open(f"{fp}RMS_{fname}.bin", 'wb') as fn:
            pickle.dump([ped, rms], fn)

    def GetPeaks(self, data, nfemb, fp, fname, funcfit=False, shapetime=2, period=500, dac=0):

        global dat_tmts_l
        nevent = len(data)

        ppk_val = []
        npk_val = []
        bl_val = []
        ppk = []
        npk = []
        bl = []
        bl_rms = []

        # new=======
        dat_tmts_l = []
        dat_tmts_h = []
        for wibdata in data:
            dat_tmts_l.append(wibdata[nfemb][nfemb * 2][0])
            dat_tmts_h.append(wibdata[nfemb][nfemb * 2 + 1][0])
        dat_tmtsl_oft = (np.array(dat_tmts_l) // 32) % period
        dat_tmtsh_oft = (np.array(dat_tmts_h) // 32) % period

        all_data = []

        for achn in range(128):
            conchndata = []

            for i in range(len(data)):
                if achn < 64:
                    oft = dat_tmtsl_oft[i]
                else:
                    oft = dat_tmtsh_oft[i]

                wibdata = data[i]
                datd = [wibdata[0], wibdata[1], wibdata[2], wibdata[3]][nfemb]
                chndata = np.array(datd[achn], dtype=np.uint32)
                lench = len(chndata)
                tmp = int(period - oft)
                conchndata = conchndata + list(chndata[tmp: ((lench - tmp) // period) * period + tmp])
            all_data.append(conchndata)

        chns = list(range(128))
        rmss = []
        peds = []
        pkps, pkns = [], []
        pulse = []
        wfs, wfsf = [], []
        plt.figure(figsize=(12, 6))
        plt.subplot(1, 2, 1)
        for achn in range(128):
            chdata = []
            N_period = len(all_data[achn]) // period
            for iperiod in range(N_period):
                istart = iperiod * period
                iend = istart + period
                chunkdata = all_data[achn][istart: iend]
                chdata.append(chunkdata)
            chdata = np.array(chdata)
            avg_wf = np.average(np.transpose(chdata), axis=1)
            wfsf.append(avg_wf)
            amax = np.max(avg_wf)
            amin = np.min(avg_wf)
            pkps.append(amax)
            pkns.append(amin)
            ppos = np.where(avg_wf == amax)[0][0]
            p0 = ppos + period

            peddata = []

            for iperid in range(N_period):
                if p0 < len(all_data[achn]):
                    peddata += all_data[achn][p0 + iperid * period - 250: p0 + iperid * period - 50]
                else:
                    if ppos > 250:
                        peddata += all_data[achn][ppos - 250: ppos - 50]
                    else:
                        peddata += all_data[achn][ppos + 200: ppos + 400]
            rmss.append(np.std(peddata))
            peds.append(np.mean(peddata))
            pulse.append(np.round(avg_wf, 1))
            tmpwf = avg_wf
            if ppos - 50 < 0:
                front = avg_wf[-50:]
                back = avg_wf[:-50]
                tmpwf = np.concatenate((front, back))
            ppos = np.where(tmpwf == np.max(tmpwf))[0][0]
            if ppos + 150 > period:
                front = tmpwf[ppos - 50:]
                back = tmpwf[: ppos - 50]
                tmpwf = np.concatenate((front, back))
            ppos = np.where(tmpwf == np.max(tmpwf))[0][0]
            wfs.append(tmpwf[ppos - 50:ppos + 150])
            plt.plot(range(len(tmpwf[ppos - 50:ppos + 150])), tmpwf[ppos - 50:ppos + 150])
            if achn == 0:
                log.channel0_pulse[nfemb][dac] = tmpwf[ppos - 50:ppos + 150]  # - np.mean(peddata)

        bottom = -1000
        plt.title('128-CH Waveform Overlap', fontsize=14)  # "128-CH Pulse Response Overlap"
        plt.ylim(bottom, 16384 + 1000)
        plt.xlabel("Time (512 ns / step)", fontsize=14)
        plt.ylabel("ADC count", fontsize=14)
        plt.grid(axis='y', color='gray', linestyle='--', alpha=0.5)

        plt.subplot(1, 2, 2)
        plt.plot(range(128), pkps, marker='.', linestyle='-', alpha=0.7, label='Positive Peak', color='blue')
        plt.plot(range(128), peds, marker='.', linestyle='-', alpha=0.9, label='Pedestal', color='0.3')
        plt.plot(range(128), pkns, marker='.', linestyle='-', alpha=0.7, label='Negitive Peak', color='orange')
        plt.grid(axis='x', color='gray', linestyle='--', alpha=0.5)

        # pl1.plot(range(128), bl_rms)
        plt.title("Amplitude Distribution", fontsize=14)
        plt.ylim(bottom, 16384 + 1000)
        plt.xlabel("Channel", fontsize=14)
        plt.xticks(np.arange(0, 129, 16))
        plt.grid(axis='y', color='gray', linestyle='--', alpha=0.1)
        plt.ylabel("ADC count", fontsize=14)
        plt.legend()

        fp_fig = fp + "pulse_{}.png".format(fname)
        plt.gca().set_facecolor('none')  # set background as transparent
        plt.tight_layout()
        plt.savefig(fp_fig, transparent=True)
        plt.close()

        fp_bin = fp + "Pulse_{}.bin".format(fname)
        with open(fp_bin, 'wb') as fn:
            pickle.dump([pkps, pkns, peds], fn)

        # fp_bin = fp + "allPulse_{}.csv".format(fname)
        # with open(fp_bin, 'w') as fn:
        #     writer = csv.writer(fn)
        #     writer.writerows(pulse)

        return pkps, pkns, peds

    def PrintPWR(self, pwr_data, nfemb, fp):

        pwr_set = [5, 3, 3, 3.5]
        pwr_dic = {'name': [], 'V_set/V': [], 'V_meas/V': [], 'I_meas/A': [], 'P_meas/W': []}
        i = 0
        total_p = 0

        pwr_dic['name'] = ['BIAS', 'LArASIC', 'ColdDATA', 'ColdADC']
        bias_v = round(pwr_data['FEMB%d_BIAS_V' % nfemb], 3)
        bias_i = round(pwr_data['FEMB%d_BIAS_I' % nfemb], 3)

        if abs(bias_i) > 0.005:
            print('Warning: FEMB{} Bias current abs({})>0.005'.format(nfemb, bias_i))

        pwr_dic['V_set/V'].append(pwr_set[0])
        pwr_dic['V_meas/V'].append(bias_v)
        pwr_dic['I_meas/A'].append(bias_i)
        pwr_dic['P_meas/W'].append(round(bias_v * bias_i, 3))
        total_p = total_p + round(bias_v * bias_i, 3)

        for i in range(3):
            tmpv = round(pwr_data['FEMB{}_DC2DC{}_V'.format(nfemb, i)], 3)
            tmpi = round(pwr_data['FEMB{}_DC2DC{}_I'.format(nfemb, i)], 3)
            tmpp = round(tmpv * tmpi, 3)

            pwr_dic['V_set/V'].append(pwr_set[i + 1])
            pwr_dic['V_meas/V'].append(tmpv)
            pwr_dic['I_meas/A'].append(tmpi)
            pwr_dic['P_meas/W'].append(tmpp)

            total_p = total_p + tmpp

        # df=pd.DataFrame(data=pwr_dic)
        # fig, ax =plt.subplots(figsize=(10,2))
        # ax.axis('off')
        # table = ax.table(cellText=df.values,colLabels=df.columns,loc='center')
        # ax.set_title("Power Consumption = {} W".format(round(total_p,3)))
        # table.set_fontsize(14)
        # table.scale(1,2)
        # fig.savefig(fp+".png")
        # plt.close(fig)

    def PlotMon(self, fembs, mon_dic, savedir, fdir, fname, fembNo, NewWIB=True):
        issue_log = defaultdict(dict)
        pulse_log = defaultdict(dict)
        if NewWIB:
            fadc = 1 / (2 ** 14) * 2500
        else:
            fadc = 1 / (2 ** 14) * 2048
        for nfemb in fembs:
            mon_list = []
            femb_id = "FEMB ID {}".format(fembNo['femb%d' % nfemb])
            for key, mon_data in mon_dic.items():
                chip_list = []
                sps = len(mon_data)

                for j in range(sps):
                    a_mon = mon_data[j][nfemb]
                    chip_list.append(a_mon)

                if sps > 1:
                    chip_list = np.array(chip_list)
                    mon_mean = np.mean(chip_list)
                else:
                    mon_mean = chip_list[0]

                mon_list.append(mon_mean * fadc)

            # fig,ax = plt.subplots(figsize=(6,4))
            xx = range(len(mon_dic))
            mon_mean = np.mean(mon_list)
            mon_std = np.std(mon_list)
            i = 0
            issue_log[femb_id]["Result"] = True
            for data in mon_list:
                i = i + 1
                if data > (mon_mean + 50) or data < (mon_mean - 50):
                    issue_log[femb_id]["{}_C{}".format(fname, i)] = data
                    issue_log[femb_id]["Result"] = False
            pulse_log[femb_id] = mon_list
            # ax.plot(xx, mon_list, marker='.')
            # ax.set_ylabel(fname)
            # fp = savedir[nfemb] + fdir + "/mon_{}.png".format(fname)
            # fig.savefig(fp)
            # plt.close(fig)
        return issue_log, pulse_log

    def PlotMonDAC(self, fembs, mon_dic, savedir, fdir, fembNo, NewWIB=True):
        issue_inl = defaultdict(dict)
        for nfemb in fembs:
            femb_id = "FEMB ID {}".format(fembNo['femb%d' % nfemb])
            fig, ax = plt.subplots(figsize=(6, 5))
            issue_inl[femb_id]["Result"] = True
            if NewWIB:
                fadc = 1 / (2 ** 14) * 2500
            else:
                fadc = 1 / (2 ** 14) * 2048
            for main_key, sub_dict in mon_dic.items():
                item = 0
                for key, mon_list in sub_dict.items():
                    data_list = []
                    dac_list = mon_list[1]
                    # print(dac_list)
                    mon_data = mon_list[0]
                    sps = mon_data[0][3]
                    item = item + 1
                    # print(dac_list)
                    for i in range(len(dac_list)):
                        sps_list = []
                        for j in range(sps):
                            a_mon = mon_data[i][4][j][nfemb]
                            sps_list.append(a_mon)

                        if sps > 1:
                            sps_list = np.array(sps_list)
                            mon_mean = np.mean(sps_list)
                            # mon_mean = stats.mode(sps_list)[0]

                        else:
                            mon_mean = sps_list[0]

                        data_list.append(mon_mean * fadc)

                    if item == 8:
                        plt.plot(dac_list, data_list, marker='.', label=main_key)
                    else:
                        plt.plot(dac_list, data_list, marker='.')
                    #   INL judgement
                    if main_key == 'AAAAAAAAA':
                        x_data = np.array(dac_list[0:31])
                        y_data = np.array(data_list[0:31])
                    else:
                        x_data = dac_list[0:-1]
                        y_data = np.array(data_list[0:-1])
                    coefficients = np.polyfit(x_data, y_data, deg=1)
                    fit_function = np.poly1d(coefficients)
                    fit_y = fit_function(x_data)
                    inl = np.max(abs(fit_y - y_data) / abs(y_data[0] - y_data[-1]) * 100)
                    LSB = np.round(abs(y_data[0] - y_data[-1]) / abs(x_data[0] - x_data[-1]), 2)
                    print(inl)
                    if inl > 1.5:
                        issue_inl[femb_id]["INL-{}-{}".format(main_key, key)] = inl
                        print('========================')
                        log.report_log1102csv[femb_id]["INL-{}-{}".format(main_key, key)] = "INL-{}-{}".format(main_key,
                                                                                                               inl)
                        issue_inl[femb_id]["Result"] = False
                    else:
                        log.report_log1102csv[femb_id]["INL-{}-{}".format(main_key, key)] = "INL-{}-{}".format(main_key,
                                                                                                               inl)
                        print('aaaaaaaaaaaaaaaaaaaaaaaaa')
                    log.report_log1101csv[femb_id]["LSB-{}-{}".format(main_key, key)] = 'LSB-{}-{}={}'.format(main_key,
                                                                                                              key, LSB)
                    print(log.report_log1101csv[femb_id]["LSB-{}-{}".format(main_key, key)])
            fp = savedir[nfemb] + fdir + "/mon_{}.png".format(main_key)
            plt.legend()
            plt.grid(True, axis='y', linestyle='--')
            plt.ylim(0, 1400)
            plt.xlabel("DAC Selection", fontsize=12)
            plt.ylabel("Voltage / mV", fontsize=12)
            plt.title("LArASIC DAC Linearity", fontsize=12)
            plt.gca().set_facecolor('none')  # set background as transparent
            plt.tight_layout()
            plt.savefig(fp, transparent=True)
            plt.close(fig)
        return issue_inl

    def PlotADCMon(self, fembs, mon_list, savedir, fdir, fembNo, NewWIB=True):
        issue_inl = defaultdict(dict)
        mon_items = ["VCMI", "VCMO", "VREFP", "VREFN", "VBGR", "VSSA", "VSSA"]
        mon_items_n = [0,1, 2, 3]
        nvset = len(mon_list)
        print(nvset)
        status = True
        if NewWIB:
            fadc = 1 / (2 ** 14) * 2500
        else:
            fadc = 1 / (2 ** 14) * 2048

        for nfemb in fembs:
            femb_id = "FEMB ID {}".format(fembNo['femb%d' % nfemb])
            check = True
            check_issue = []
            print(mon_list[4][1])
            for imon in mon_items_n:

                vset_list = []
                fig, ax = plt.subplots(figsize=(6, 4))
                data_dic = {}

                for i in [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]:#range(nvset):
                    print(i)
                    vset_list.append(mon_list[i][0])
                    mon_data = mon_list[i][1]
                    print(mon_list[i][1])
                    print(imon)
                    chip_dic = mon_data[imon]
                    # for key, chip_data in chip_dic.items():
                    #     print(key)
                    #     print(chip_data)
                    #     print('\n')
                    # input('debug')
                    for key, chip_data in chip_dic.items():
                        # print(key)
                        # print(chip_data)
                        # print(chip_data[3])

                        sps = len(chip_data[3])
                        sps_list = []
                        for j in range(sps):
                            a_mon = chip_data[3][j][nfemb]
                            sps_list.append(a_mon)
                        if sps > 1:
                            sps_list = np.array(sps_list)
                            mon_mean = np.mean(sps_list)
                        else:
                            mon_mean = sps_list[0]
                        if key not in data_dic:
                            data_dic[key] = []
                        data_dic[key].append(mon_mean * fadc)  ###

                for key, chip_data in chip_dic.items():
                    #   INL judgement
                    # x_data = np.array(range(0, 256, 16))
                    x_data = [0, 16, 32, 48, 64, 80, 96, 112, 128, 144, 160, 176, 192, 208, 224, 240,255]
                    y_data = np.array(data_dic[key])
                    coefficients = np.polyfit(x_data[0:14], y_data[0:14], deg=1)
                    fit_function = np.poly1d(coefficients)
                    fit_y = fit_function(x_data[0:14])
                    inl = round(np.max(abs(fit_y - y_data[0:14]) * 100 / abs(y_data[0] - y_data[-1])), 2)
                    LSB = np.round(abs(y_data[0] - y_data[-1]) / abs(x_data[0] - x_data[-1]), 2)
                    log.report_log1201csv[femb_id]["INL-{}-{}".format(mon_items[imon], key)] = 'INL-{}-{}={}'.format(
                        mon_items[imon], key, inl)
                    log.report_log1202csv[femb_id]["LSB-{}-{}".format(mon_items[imon], key)] = 'LSB-{}-{}={}'.format(
                        mon_items[imon], key, LSB)
                    if inl < 1:
                        log.ADCMON_table_cell[femb_id]["{}_{}".format(mon_items[imon], key)] = "{}".format(inl)
                    else:
                        check = False
                        check_issue.append("ADC ref voltage: {}, chip: {}, inl issue: {} \n".format(imon, key, inl))
                        log.ADCMON_table_cell[femb_id][
                            "{}_{}".format(mon_items[imon], key)] = "<span style = 'color:red;'> {} </span>".format(inl)
                for key, values in data_dic.items():
                    ax.plot(vset_list, data_dic[key], marker='.', label=key)
                ax.set_ylabel(mon_items[imon])
                ax.legend()
                fp = savedir[nfemb] + fdir + "/mon_{}.png".format(mon_items[imon])
                plt.legend()
                plt.grid(True, axis='y', linestyle='--')
                plt.ylim(0, 2500)
                plt.xlabel("V Set", fontsize=12)
                plt.ylabel("Voltage / mV", fontsize=12)
                plt.title("ColdADC ref_voltage {}".format(mon_items[imon]), fontsize=12)
                plt.gca().set_facecolor('none')  # set background as transparent
                plt.tight_layout()
                plt.savefig(fp, transparent=True)
                plt.close(fig)

            log.check_log[femb_id]["Result"] = check
            log.check_log[femb_id]["Issue List"] = check_issue

            log.ADCMON_table[femb_id]["VCMI / %"] = " {} | {} | {} | {} | {} | {} | {} | {} ".format(
                log.ADCMON_table_cell[femb_id]["VCMI_chip0"], log.ADCMON_table_cell[femb_id]["VCMI_chip1"],
                log.ADCMON_table_cell[femb_id]["VCMI_chip2"], log.ADCMON_table_cell[femb_id]["VCMI_chip3"],
                log.ADCMON_table_cell[femb_id]["VCMI_chip4"], log.ADCMON_table_cell[femb_id]["VCMI_chip5"],
                log.ADCMON_table_cell[femb_id]["VCMI_chip6"], log.ADCMON_table_cell[femb_id]["VCMI_chip7"])
            log.ADCMON_table[femb_id]["VCMO / %"] = " {} | {} | {} | {} | {} | {} | {} | {} ".format(
                log.ADCMON_table_cell[femb_id]["VCMO_chip0"], log.ADCMON_table_cell[femb_id]["VCMO_chip1"],
                log.ADCMON_table_cell[femb_id]["VCMO_chip2"], log.ADCMON_table_cell[femb_id]["VCMO_chip3"],
                log.ADCMON_table_cell[femb_id]["VCMO_chip4"], log.ADCMON_table_cell[femb_id]["VCMO_chip5"],
                log.ADCMON_table_cell[femb_id]["VCMO_chip6"], log.ADCMON_table_cell[femb_id]["VCMO_chip7"])
            log.ADCMON_table[femb_id]["VREFP / %"] = " {} | {} | {} | {} | {} | {} | {} | {} ".format(
                log.ADCMON_table_cell[femb_id]["VREFP_chip0"], log.ADCMON_table_cell[femb_id]["VREFP_chip1"],
                log.ADCMON_table_cell[femb_id]["VREFP_chip2"], log.ADCMON_table_cell[femb_id]["VREFP_chip3"],
                log.ADCMON_table_cell[femb_id]["VREFP_chip4"], log.ADCMON_table_cell[femb_id]["VREFP_chip5"],
                log.ADCMON_table_cell[femb_id]["VREFP_chip6"], log.ADCMON_table_cell[femb_id]["VREFP_chip7"])
            log.ADCMON_table[femb_id]["VREFN / %"] = " {} | {} | {} | {} | {} | {} | {} | {} ".format(
                log.ADCMON_table_cell[femb_id]["VREFN_chip0"], log.ADCMON_table_cell[femb_id]["VREFN_chip1"],
                log.ADCMON_table_cell[femb_id]["VREFN_chip2"], log.ADCMON_table_cell[femb_id]["VREFN_chip3"],
                log.ADCMON_table_cell[femb_id]["VREFN_chip4"], log.ADCMON_table_cell[femb_id]["VREFN_chip5"],
                log.ADCMON_table_cell[femb_id]["VREFN_chip6"], log.ADCMON_table_cell[femb_id]["VREFN_chip7"])

    def CheckLinearty(self, dac_list, pk_list, updac, lodac, chan, fp):
        #   first sample and fit
        #   the updac range need to be ensured
        dac_init = []
        pk_init = []
        for i in range(len(dac_list)):
            if ((pk_list[i] < updac) and (pk_list[i] > lodac)):
                dac_init.append(dac_list[i])
                pk_init.append(pk_list[i])

        #   first fit, use initial sample points
        try:
            slope_i, intercept_i = np.polyfit(dac_init, pk_init, 1)
        except:
            # we suggest here report an issue
            fig1, ax1 = plt.subplots()
            ax1.plot(dac_init, pk_init, marker='.')
            ax1.set_xlabel("DAC")
            ax1.set_ylabel("Peak Value")
            ax1.set_title("chan%d fail first gain fit" % chan)
            plt.tight_layout()
            plt.savefig(fp + 'fail_first_fit_ch%d.png' % chan)
            plt.close(fig1)

            print("fail at first gain fit")
            return 0, 0, 0

        #   with these filter, get a line and find the most line area
        y_min = pk_list[0]
        y_max = pk_list[-1]
        linear_dac_max = dac_list[-1]
        if 'vdac' in fp:
            inl_th = 0.01
        else:
            inl_th = 0.015
        index = len(dac_list) - 1

        for i in range(len(dac_list)):
            y_r = pk_list[i]
            y_p = dac_list[i] * slope_i + intercept_i
            inl = abs(y_r - y_p) / (y_max - y_min)
            if inl > inl_th:
                if dac_list[i] < 5:
                    continue
                linear_dac_max = dac_list[i - 1]
                index = i
                break
        # print(linear_dac_max)
        # print(index)

        if index == 0:
            fig2, ax2 = plt.subplots(1, 2, figsize=(12, 6))
            ax2[0].plot(dac_list, pk_list, marker='.')
            ax2[0].set_xlabel("DAC")
            ax2[0].set_ylabel("Peak Value")
            ax2[0].set_title("chan%d fail linear range searching" % chan)

            tmp_inl = []
            tmp_dac = []
            for i in range(len(dac_list)):
                if dac_list[i] > updac:
                    break
                y_r = pk_list[i]
                y_p = dac_list[i] * slope_i + intercept_i
                inl_1 = abs(y_r - y_p) / (y_max - y_min)
                tmp_inl.append(inl_1)
                tmp_dac.append(i)

            ax2[1].plot(tmp_dac, tmp_inl, marker='.')
            ax2[1].set_xlabel("DAC")
            ax2[1].set_ylabel("Peak Value")
            ax2[1].set_title("chan%d inl" % chan)
            plt.tight_layout()
            plt.savefig(fp + 'fail_inl_ch%d.png' % chan)
            plt.close(fig2)
            print("fail at first linear range searching: inl=%f for dac=0 is bigger than 0.03" % inl)
            return 0, 0, 0

        # print(dac_list[:index])
        #   second linear fit, with all linear area
        try:
            slope_f, intercept_f = np.polyfit(dac_list[1:index], pk_list[1:index], 1)
        except:
            fig3, ax3 = plt.subplots()
            ax3.plot(dac_list[1:index], pk_list[1:index], marker='.')
            ax3.set_xlabel("DAC")
            ax3.set_ylabel("Peak Value")
            ax3.set_title("chan%d fail second gain fit" % chan)
            plt.tight_layout()
            plt.savefig(fp + 'fail_second_fit_ch%d.png' % chan)
            plt.close(fig3)
            print("fail at second gain fit")
            return 0, 0, 0
        y_max = pk_list[index]
        y_min = pk_list[0]

        INL = 0
        if len(dac_list) > 32:
            index = index - 3
        else:
            index = index
        for i in range(0, index):
            y_r = pk_list[i]
            y_p = dac_list[i] * slope_f + intercept_f
            inl = abs(y_r - y_p) / (abs(y_max - y_min) * 1.5)
            if inl * 100 > INL:
                INL = inl

        return slope_f, INL, linear_dac_max

    def GetGain(self, fembs, fembNo, Cali_dict, savedir, fdir, namepat, snc, sgs, sts, dac_list, updac=25, lodac=10):
        global fname_1, ppk, bl, line_range_list, inl_list, gain_list
        log.tmp_log.clear()
        log.check_log.clear()
        log.chkflag.clear()
        log.badlist.clear()
        dac_v = {}  # mV/bit
        dac_v['4_7mVfC'] = 18.66
        dac_v['7_8mVfC'] = 14.33
        dac_v['14_0mVfC'] = 8.08
        dac_v['25_0mVfC'] = 4.61

        CC = 1.85 * pow(10, -13)
        e = 1.602 * pow(10, -19)
        # print(namepat)
        if "sgp1" in namepat:
            dac_du = dac_v['4_7mVfC']
            fname = '{}_{}_{}_sgp1'.format(snc, sgs, sts)
        else:
            dac_du = dac_v[sgs]
            fname = '{}_{}_{}'.format(snc, sgs, sts)

        pk_list = [[], [], [], []]
        if 'CALI5' in namepat or 'CALI6' in namepat:
            dac_list = dac_list[::-1]
            dac_list = [(1650 - x) for x in dac_list]
        for dac in dac_list:
            if 'CALI5' in namepat or 'CALI6' in namepat:
                dacname = 1650 - dac
            else:
                dacname = dac
            key_dict = namepat.format(snc, sgs, sts, dacname) + '.bin'
            raw = Cali_dict[key_dict]
            rawdata = raw[0]
            pwr_meas = raw[1]
            wibdata = self.data_decode(rawdata, fembs)
            pldata = wibdata

            for ifemb in fembs:
                fp = savedir[ifemb] + fdir
                if dac == 0:
                    fname_1 = namepat.format(snc, sgs, sts, dacname)
                    ped, rms, _, _ = self.GetRMS(pldata, ifemb, fp, fname)
                    ppk, bpk, bl = self.GetPeaks(pldata, ifemb, fp, fname_1, dac=dac)
                    ppk_np = np.array(ppk) - np.array(bl)
                    if not ('vdac' in fname_1):
                        pk_list[ifemb].append(ppk_np)
                else:
                    fname_1 = namepat.format(snc, sgs, sts, dacname)
                    if ('vdac' in fname_1):
                        if not ('000mV' in fname_1):
                            ppk, bpk, bl = self.GetPeaks(pldata, ifemb, fp, fname_1, period=500, dac=dac)
                            # bl = 0
                    else:
                        ppk, bpk, bl = self.GetPeaks(pldata, ifemb, fp, fname_1, dac=dac)
                    ppk_np = np.array(ppk) - np.array(bl)
                    pk_list[ifemb].append(ppk_np)

        for ifemb in fembs:
            femb_id = "FEMB ID {}".format(fembNo['femb%d' % ifemb])
            tmp_list = pk_list[ifemb]
            new_pk_list = list(zip(*tmp_list))

            check = True
            check_issue = []
            dac_np = np.array(dac_list)
            pk_np = np.array(new_pk_list)
            fp = savedir[ifemb] + fdir

            gain_list = []
            inl_list = []
            inl_listcsv = []
            line_range_list = []
            max_dac_list = []
            plt.figure(figsize=(9, 6))
            #   overlap channel 0 pulse from [1 - 63]

            #   peak - dac linear
            plt.subplot(2, 2, 2)
            for ch in range(128):
                uplim = np.max(pk_np[ch]) * 6 / 7
                lodac = np.max(pk_np[ch]) * 1 / 7
                gain, inl, line_range = self.CheckLinearty(dac_np, pk_np[ch], uplim, lodac, ch, fp)
                if gain == 0:
                    print("femb%d ch%d gain is zero" % (ifemb, ch))
                else:
                    if ('vdac' in namepat):
                        gain = 1 / gain / 1000 * CC / e
                    else:
                        gain = 1 / gain * dac_du / 1000 * CC / e
                gain_list.append(round(gain, 3))
                inl_list.append(round(inl * 100, 2))
                inl_listcsv.append(round(inl * 100, 2))
                line_range_list.append(round(line_range * dac_du / 1000 * 185))
                if ('vdac' in fname_1):
                    if inl > 0.2:
                        check = False
                        check_issue.append("ch {} INL issue: {}".format(ch, inl))
                    if line_range < 100:
                        check = False
                        check_issue.append("ch {} line range issue: {}".format(ch, line_range))
                    if gain > 50:
                        check = False
                        check_issue.append("ch {} gain issue: {}".format(ch, gain))
                    plt.plot(dac_np, pk_np[ch])
                else:
                    if inl > 0.01:
                        check = False
                        check_issue.append("ch {} INL issue: {}".format(ch, inl))
                    if "900mV" in fname_1:
                        if 'sgp1' in fname_1:
                            plt.plot(dac_np * dac_du / 1000 * 185, pk_np[ch])
                            if line_range < 4:
                                check = False
                                check_issue.append("ch {} line range issue: {}".format(ch, line_range))
                        else:
                            plt.plot(dac_np * dac_du / 1000 * 185, pk_np[ch])
                            if line_range < 25:
                                check = False
                                check_issue.append("ch {} line range issue: {}".format(ch, line_range))
                        if gain > 43:
                            check = False
                            check_issue.append("ch {} Gain issue at 14_0 mVfC: {}".format(ch, line_range))


                    elif '200mV' in fname_1:
                        if 'sgp1' in fname_1:
                            if line_range < 20:
                                check = False
                                check_issue.append("ch {} Line range issue lower than 20: {}".format(ch, line_range))
                        else:
                            if line_range < 48:
                                check = False
                                check_issue.append("ch {} Line range issue lower than 50: {}".format(ch, line_range))
                        if '4_7' in fname_1:
                            plt.plot(dac_np * dac_du / 1000 * 185, pk_np[ch])
                            if gain > 135:
                                check = False
                                check_issue.append("ch {} Gain issue at 4_7 mVfC: {}".format(ch, line_range))
                        if '7_8' in fname_1:
                            plt.plot(dac_np * dac_du / 1000 * 185, pk_np[ch])
                            if gain > 78:
                                check = False
                                check_issue.append("ch {} Gain issue at 7_8 mVfC: {}".format(ch, line_range))
                        if '14_0' in fname_1:
                            if 'sgp1' in fname_1:
                                plt.plot(dac_np * dac_du / 1000 * 185, pk_np[ch])
                            else:
                                plt.plot(dac_np * dac_du / 1000 * 185, pk_np[ch])
                            if gain > 45:
                                check = False
                                check_issue.append("ch {} Gain issue at 14_0 mVfC: {}".format(ch, line_range))
                        if '25_0' in fname_1:
                            plt.plot(dac_np * dac_du / 1000 * 185, pk_np[ch])
                            if gain > 26:
                                check = False
                                check_issue.append("ch {} Gain issue at 25_0 mVfC: {}".format(ch, line_range))

                # max_dac_list.append(max_dac)

            log.tmp_log[femb_id]["INL"] = np.max(inl_list)
            log.tmp_log[femb_id]["Gain"] = np.mean(gain_list)
            log.tmp_log[femb_id]["Gainstd"] = np.std(gain_list)
            log.tmp_log[femb_id]["Linearangemin"] = np.min(line_range_list)
            log.check_log[femb_id]["Result"] = check
            log.check_log[femb_id]["Issue List"] = check_issue

            log.tmp_log[ifemb]["inl_list"] = inl_listcsv
            log.tmp_log[ifemb]["gain_list"] = gain_list
            log.tmp_log[ifemb]["line_range_list"] = line_range_list

            plt.ylabel("Amplitude / ADC_bit", fontsize=14)
            plt.xlabel("Input Setting / mV", fontsize=14)
            plt.title("Amplitude vs Input", fontsize=14)
            plt.ylim(0, 16500)
            plt.grid(True, axis='y', linestyle='--')
            line_min = np.min(line_range_list)

            plt.subplot(2, 2, 1)
            for dac in dac_list[1: ]:
                if len(dac_list) > 12:
                    if dac in [2, 10, 18, 26, 34, 42, 50, 58]:
                        plt.plot(range(len(log.channel0_pulse[ifemb][dac])), log.channel0_pulse[ifemb][dac])
                else:
                    plt.plot(range(len(log.channel0_pulse[ifemb][dac])), log.channel0_pulse[ifemb][dac])
            plt.ylabel("Pulse / ADC_bit", fontsize=14)
            plt.xlabel("Time / 512 ns", fontsize=14)
            plt.ylim(0, 16500)
            plt.grid(True, axis='y', linestyle='--')
            # plt.legend()
            plt.title("Waveform from channel_0", fontsize=14)
            #   Gain
            plt.subplot(2, 2, 3)
            plt.plot(range(128), gain_list, marker='.')
            plt.xlabel("Channel", fontsize=14)
            plt.ylabel("Gain / (e- / bit)", fontsize=14)
            x_sticks = range(0, 129, 16)
            plt.ylim(0, 120)
            plt.xticks(x_sticks)
            plt.grid(True, axis='y', linestyle='--')
            plt.grid(axis='x')
            plt.title("128-ch Gain Distribution", fontsize=14)

            #   INL
            plt.subplot(2, 2, 4)
            plt.plot(range(128), inl_list, marker='.')
            plt.xlabel("Channel", fontsize=14)
            plt.ylabel("INL (%)", fontsize=14)
            plt.ylim(0, 0.02)
            x_sticks = range(0, 129, 16)
            plt.xticks(x_sticks)
            plt.grid(axis='x')
            plt.grid(True, axis='y', linestyle='--')
            plt.title("128-Ch INL Distribution", fontsize=14)
            plt.ylim(0, 2)
            # plt.yscale("log")
            plt.gca().set_facecolor('none')  # set background as transparent
            plt.tight_layout()
            plt.savefig(fp + 'gain_{}.png'.format(fname), transparent=True)
            plt.close()

            fp_bin = fp + "Gain_{}.bin".format(fname)
            with open(fp_bin, 'wb') as fn:
                pickle.dump(gain_list, fn)

            plt.figure(figsize=(4, 3))
            xx = range(128)
            plt.plot(xx, line_range_list, marker='.')
            if 'vdac' in namepat:
                plt.ylim(0, 700)
            else:
                plt.ylim(0, 200)
            plt.xlabel("Channel", fontsize=14)
            plt.ylabel("Input Range / mV", fontsize=14)
            x_sticks = range(0, 129, 16)
            plt.title(fname, fontsize=14)
            plt.grid(True, axis='y', linestyle='--')
            fp = savedir[ifemb] + fdir + "Line_range_{}.png".format(fname)
            plt.gca().set_facecolor('none')  # set background as transparent
            plt.tight_layout()
            plt.savefig(fp, transparent=True)
            plt.close()

    def GetENC(self, fembs, fembNo, snc, sgs, sts, sgp, savedir, fdir):
        for ifemb in fembs:
            femb_id = "FEMB ID {}".format(fembNo['femb%d' % ifemb])
            if sgp == 0:
                fname = "{}_{}_{}".format(snc, sgs, sts)
            if sgp == 1:
                fname = "{}_{}_{}_sgp1".format(snc, sgs, sts)

            frms = savedir[ifemb] + fdir + "RMS_{}.bin".format(fname)
            fgain = savedir[ifemb] + fdir + "Gain_{}.bin".format(fname)

            with open(frms, 'rb') as fn:
                rms_list = pickle.load(fn)
            rms_list = np.array(rms_list[1])

            with open(fgain, 'rb') as fn:
                gain_list = pickle.load(fn)
            gain_list = np.array(gain_list)

            enc_list = rms_list * gain_list
            rms_mean = np.mean(rms_list)
            rms_std = np.std(rms_list)
            enc_mean = np.mean(enc_list)
            enc_std = np.std(enc_list)

            plt.figure(figsize=(4, 3))
            xx = range(128)
            plt.plot(xx, enc_list, marker='.')
            plt.ylim(enc_mean - 300, enc_mean + 300)
            plt.xlabel("chan", fontsize=14)
            plt.ylabel("ENC", fontsize=14)
            x_sticks = range(0, 129, 16)
            plt.xticks(x_sticks)
            plt.grid(axis='x')
            plt.grid(True, axis='y', linestyle='--')
            plt.title(fname, fontsize=14)
            fp = savedir[ifemb] + fdir + "enc_{}.png".format(fname)
            plt.gca().set_facecolor('none')  # set background as transparent
            plt.tight_layout()
            plt.savefig(fp, transparent=True)
            plt.close()

            log.tmp_log[femb_id]["ENC"] = round(enc_mean)
            log.tmp_log[femb_id]["ENC_std"] = enc_std
            log.tmp_log[femb_id]["RMS"] = round(rms_mean)
            log.tmp_log[femb_id]["RMS_std"] = rms_std

            fp_bin = savedir[ifemb] + fdir + "ENC_{}.bin".format(fname)
            with open(fp_bin, 'wb') as fn:
                pickle.dump(enc_list, fn)

    # for SGP_Calibration
    def GetGain_SGP1(self, fembs, fembNo, Cali_dict, savedir, fdir, namepat, snc, sgs, sts, dac_list, updac=25, lodac=10):
        global fname_1, ppk, bl, line_range_list, inl_list, gain_list
        log.tmp_log.clear()
        log.check_log.clear()
        log.chkflag.clear()
        log.badlist.clear()
        dac_v = {}  # mV/bit
        dac_v['4_7mVfC'] = 18.66
        dac_v['7_8mVfC'] = 14.33
        dac_v['14_0mVfC'] = 8.08
        dac_v['25_0mVfC'] = 4.61
        check = True
        CC = 1.85 * pow(10, -13)
        e = 1.602 * pow(10, -19)
        # print(namepat)
        if "sgp1" in namepat:
            dac_du = dac_v['4_7mVfC']
            fname = '{}_{}_{}_sgp1'.format(snc, sgs, sts)
        else:
            dac_du = dac_v[sgs]
            fname = '{}_{}_{}'.format(snc, sgs, sts)

        pk_list = [[], [], [], []]
        if 'CALI5' in namepat or 'CALI6' in namepat:
            dac_list = dac_list[::-1]
            dac_list = [(1650 - x) for x in dac_list]
        check = True
        check_issue = []
        for dac in dac_list:
            if 'CALI5' in namepat or 'CALI6' in namepat:
                dacname = 1650 - dac
            else:
                dacname = dac
            key_dict = namepat.format(snc, sgs, sts, dacname) + '.bin'
            raw = Cali_dict[key_dict]
            rawdata = raw[0]
            pwr_meas = raw[1]
            wibdata = self.data_decode(rawdata, fembs)
            pldata = wibdata

            for ifemb in fembs:
                fp = savedir[ifemb] + fdir
                if dac == 0:
                    fname_1 = namepat.format(snc, sgs, sts, dacname)
                    ped, rms, _, _ = self.GetRMS(pldata, ifemb, fp, fname)
                    ppk, bpk, bl = self.GetPeaks(pldata, ifemb, fp, fname_1, dac=dac)
                    ppk_np = np.array(ppk) - np.array(bl)
                    if not ('vdac' in fname_1):
                        pk_list[ifemb].append(ppk_np)
                else:
                    fname_1 = namepat.format(snc, sgs, sts, dacname)
                    ppk, bpk, bl = self.GetPeaks(pldata, ifemb, fp, fname_1, dac=dac)
                    ppk_np = np.array(ppk) - np.array(bl)
                    pk_list[ifemb].append(ppk_np)

                    if 'CALI3' in namepat:
                        if dac > 42:
                            if ppk_np[dac] < 12500:
                                check = False
                                check_issue.append('issue dac: {}'.format(dac))
                    elif 'CALI4' in namepat:
                        if dac > 22:
                            if ppk_np[dac] < 7000:
                                check = False
                                check_issue.append('issue dac: {}'.format(dac))
                    print(ppk_np[dac])
                    print(check)

        for ifemb in fembs:
            femb_id = "FEMB ID {}".format(fembNo['femb%d' % ifemb])
            tmp_list = pk_list[ifemb]
            new_pk_list = list(zip(*tmp_list))
            dac_np = np.array(dac_list)
            pk_np = np.array(new_pk_list)
            fp = savedir[ifemb] + fdir

            gain_list = []
            inl_list = []
            inl_listcsv = []
            line_range_list = []
            max_dac_list = []
            plt.figure(figsize=(9, 6))
            #   overlap channel 0 pulse from [1 - 63]

            #   peak - dac linear
            plt.figure(figsize=(12, 6))
            plt.subplot(1, 2, 2)
            for ch in range(128):
                uplim = np.max(pk_np[ch]) * 6 / 7
                lodac = np.max(pk_np[ch]) * 1 / 7
                gain, inl, line_range = self.CheckLinearty(dac_np, pk_np[ch], uplim, lodac, ch, fp)
                if gain == 0:
                    print("femb%d ch%d gain is zero" % (ifemb, ch))
                else:
                    if ('vdac' in namepat):
                        gain = 1 / gain / 1000 * CC / e
                    else:
                        gain = 1 / gain * dac_du / 1000 * CC / e
                gain_list.append(round(gain, 3))
                line_range_list.append(round(line_range * dac_du / 1000 * 185))
                plt.plot(dac_np * dac_du / 1000 * 185, pk_np[ch])
        #         if ('vdac' in fname_1):
        #             if inl > 0.2:
        #                 check = False
        #                 check_issue.append("ch {} INL issue: {}".format(ch, inl))
        #             if line_range < 100:
        #                 check = False
        #                 check_issue.append("ch {} line range issue: {}".format(ch, line_range))
        #             if gain > 50:
        #                 check = False
        #                 check_issue.append("ch {} gain issue: {}".format(ch, gain))
        #             plt.plot(dac_np, pk_np[ch])
        #         else:
        #             if inl > 0.01:
        #                 check = False
        #                 check_issue.append("ch {} INL issue: {}".format(ch, inl))
        #             if "900mV" in fname_1:
        #                 if 'sgp1' in fname_1:
        #                     plt.plot(dac_np * dac_du / 1000 * 185, pk_np[ch])
        #                     if line_range < 4:
        #                         check = False
        #                         check_issue.append("ch {} line range issue: {}".format(ch, line_range))
        #                 else:
        #                     plt.plot(dac_np * dac_du / 1000 * 185, pk_np[ch])
        #                     if line_range < 25:
        #                         check = False
        #                         check_issue.append("ch {} line range issue: {}".format(ch, line_range))
        #                 if gain > 43:
        #                     check = False
        #                     check_issue.append("ch {} Gain issue at 14_0 mVfC: {}".format(ch, line_range))
        #
        #
        #             elif '200mV' in fname_1:
        #                 if 'sgp1' in fname_1:
        #                     if line_range < 20:
        #                         check = False
        #                         check_issue.append("ch {} Line range issue lower than 20: {}".format(ch, line_range))
        #                 else:
        #                     if line_range < 48:
        #                         check = False
        #                         check_issue.append("ch {} Line range issue lower than 50: {}".format(ch, line_range))
        #                 if '4_7' in fname_1:
        #                     plt.plot(dac_np * dac_du / 1000 * 185, pk_np[ch])
        #                     if gain > 135:
        #                         check = False
        #                         check_issue.append("ch {} Gain issue at 4_7 mVfC: {}".format(ch, line_range))
        #                 if '7_8' in fname_1:
        #                     plt.plot(dac_np * dac_du / 1000 * 185, pk_np[ch])
        #                     if gain > 78:
        #                         check = False
        #                         check_issue.append("ch {} Gain issue at 7_8 mVfC: {}".format(ch, line_range))
        #                 if '14_0' in fname_1:
        #                     if 'sgp1' in fname_1:
        #                         plt.plot(dac_np * dac_du / 1000 * 185, pk_np[ch])
        #                     else:
        #                         plt.plot(dac_np * dac_du / 1000 * 185, pk_np[ch])
        #                     if gain > 45:
        #                         check = False
        #                         check_issue.append("ch {} Gain issue at 14_0 mVfC: {}".format(ch, line_range))
        #                 if '25_0' in fname_1:
        #                     plt.plot(dac_np * dac_du / 1000 * 185, pk_np[ch])
        #                     if gain > 26:
        #                         check = False
        #                         check_issue.append("ch {} Gain issue at 25_0 mVfC: {}".format(ch, line_range))

                # max_dac_list.append(max_dac)
        # for ifemb in fembs:
        #     femb_id = "FEMB ID {}".format(fembNo['femb%d' % ifemb])
            # log.tmp_log[femb_id]["INL"] = np.max(inl_list)
            # log.tmp_log[femb_id]["Gain"] = np.mean(gain_list)
            # log.tmp_log[femb_id]["Gainstd"] = np.std(gain_list)
            log.tmp_log[femb_id]["Linearangemin"] = np.min(line_range_list)
            log.tmp_log[ifemb]["line_range_list"] = line_range_list
            log.check_log[femb_id]["Result"] = check
            log.check_log[femb_id]["Issue List"] = check_issue
            plt.ylabel("Amplitude / ADC_bit", fontsize=14)
            plt.xlabel("Input Setting / mV", fontsize=14)
            plt.title("Amplitude vs Input", fontsize=14)
            plt.ylim(0, 16500)
            plt.grid(True, axis='y', linestyle='--')

            plt.subplot(1, 2, 1)
            for dac in dac_list[1: ]:
                if len(dac_list) > 12:
                    if dac in [2, 10, 18, 26, 34, 42, 50, 58]:
                        plt.plot(range(len(log.channel0_pulse[ifemb][dac])), log.channel0_pulse[ifemb][dac])
                else:
                    plt.plot(range(len(log.channel0_pulse[ifemb][dac])), log.channel0_pulse[ifemb][dac])
            plt.ylabel("Pulse / ADC_bit", fontsize=14)
            plt.xlabel("Time / 512 ns", fontsize=14)
            plt.ylim(0, 16500)
            plt.grid(True, axis='y', linestyle='--')
            # plt.legend()
            plt.title("Waveform from channel_0", fontsize=14)
            # plt.yscale("log")
            plt.gca().set_facecolor('none')  # set background as transparent
            plt.tight_layout()
            plt.savefig(fp + 'gain_{}.png'.format(fname), transparent=True)
            plt.close()

