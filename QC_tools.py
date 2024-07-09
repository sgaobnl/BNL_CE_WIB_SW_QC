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

def ResFunc(x, par0, par1, par2, par3):

    xx = x-par2

    A1 = 4.31054*par0
    A2 = 2.6202*par0
    A3 = 0.464924*par0
    A4 = 0.762456*par0
    A5 = 0.327684*par0

    E1 = np.exp(-2.94809*xx/par1)
    E2 = np.exp(-2.82833*xx/par1)
    E3 = np.exp(-2.40318*xx/par1)

    lambda1 = 1.19361*xx/par1
    lambda2 = 2.38722*xx/par1
    lambda3 = 2.5928*xx/par1
    lambda4 = 5.18561*xx/par1

    return par3+(A1*E1-A2*E2*(np.cos(lambda1)+np.cos(lambda1)*np.cos(lambda2)+np.sin(lambda1)*np.sin(lambda2))+A3*E3*(np.cos(lambda3)+np.cos(lambda3)*np.cos(lambda4)+np.sin(lambda3)*np.sin(lambda4))+A4*E2*(np.sin(lambda1)-np.cos(lambda2)*np.sin(lambda1)+np.cos(lambda1)*np.sin(lambda2))-A5*E3*(np.sin(lambda3)-np.cos(lambda4)*np.sin(lambda3)+np.cos(lambda3)*np.sin(lambda4)))*np.heaviside(xx,1)

def FitFunc(pldata, shapetime, makeplot=False):  # pldata is the 500 samples
    
    pmax = np.amax(pldata)
    maxpos = np.argmax(pldata)

    if shapetime==0.5:
       nbf = 2
       naf = 4

    if shapetime==1:
       nbf = 3
       naf = 6

    if shapetime==2:
       nbf = 5
       naf = 8

    if shapetime==3:
       nbf = 7
       naf = 10

    pbl = pldata[maxpos-nbf]
    a_xx = np.array(range(nbf+naf))*0.5
    popt, pcov = curve_fit(ResFunc, a_xx, pldata[maxpos-nbf:maxpos+naf],maxfev= 10000,p0=[pmax,shapetime,0,pbl])
    nbf_1=10
    naf_1=10
    a_xx = np.array(range(nbf_1+naf_1))*0.5
    popt_1, pcov_1 = curve_fit(ResFunc, a_xx, pldata[maxpos-nbf_1:maxpos+naf_1],maxfev= 10000,p0=[popt[0],popt[1],popt[2]+(nbf_1-nbf)*0.5,popt[3]])

    if makeplot:
       fig,ax = plt.subplots()
       ax.scatter(a_xx, pldata[maxpos-nbf_1:maxpos+naf_1], c='r')
       xx = np.linspace(0,nbf_1+naf_1,100)*0.5
       ax.plot(xx, ResFunc(xx,popt_1[0],popt_1[1],popt_1[2],popt_1[3]))
       ax.set_xlabel('us')
       ax.set_ylabel('ADC')
       ax.text(0.6,0.8,'A0=%.2f'%popt_1[0],fontsize = 15,transform=ax.transAxes)
       ax.text(0.6,0.7,'tp=%.2f'%popt_1[1],fontsize = 15,transform=ax.transAxes)
       ax.text(0.6,0.6,'t0=%.2f'%popt_1[2],fontsize = 15,transform=ax.transAxes)
       ax.text(0.6,0.5,'bl=%.2f'%popt_1[3],fontsize = 15,transform=ax.transAxes)
       plt.show()

    return popt_1 

class ana_tools:
    def __init__(self):
        self.fadc = 1/(2**14)*2048 # mV

    def data_decode(self,raw,fembs):
        #wibdata = wib_dec(data=raw, fembs=fembs,fastchk = False, cd0cd1sync=True)
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
        # acquire and plot the  < PED & RMS> characters for each channel
    
        nevent = len(data)
    
        rms=[]
        ped=[]
        med = []
        rms_max = 0
        rms_min = 1000
        ped_max = 0
        ped_min = 10000
    
        for ich in range(128):
            global_ch = nfemb*128+ich
            peddata=np.empty(0)
            npulse=0
            first = True
            allpls=np.empty(0)
            for itr in range(nevent):
                evtdata = data[itr][nfemb][ich]
                allpls=np.append(allpls,evtdata)

            ch_ped = np.mean(allpls)
            ch_rms = np.std(allpls)

            ped.append(ch_ped)
            rms.append(ch_rms)

            if ch_rms > rms_max:
                rms_max = ch_rms
            if ch_rms < rms_min:
                rms_min = ch_rms

            if ch_ped > ped_max:
                ped_max = ch_ped
            if ch_ped < ped_min:
                ped_min = ch_ped

        # abstract assume valid parameter to calculate median and std of ped, which used to static valid parameters
        fe_rms_med = np.median(rms)
        refine_rms = [x for x in rms if (abs(x-fe_rms_med) < 7)]
        rms_5std = 5 * np.std(refine_rms)
        fe_ped_med = np.median(ped)
        refine_ped = [x for x in ped if (abs(x-fe_ped_med) < 350)]
        ped_5std = 5 * np.std(refine_ped)

        plt.figure(figsize=(12, 4))
        plt.subplot(1, 2, 2)
        plt.plot(range(128), rms, marker='o', linestyle = '-', alpha = 0.7, label='pos')
        plt.title(fname, fontsize = 14)
        plt.xlabel("Channel", fontsize = 14)
        plt.ylabel("Root Mean Square", fontsize = 14)
        x_sticks = range(0, 129, 16)
        plt.xticks(x_sticks)
        plt.grid(axis='x')
        if (rms_max < (fe_rms_med + 8)) and (rms_min > (fe_rms_med - 8)):
            plt.ylim(fe_rms_med - 8, fe_rms_med + 8)
        else:
            plt.grid(axis='y')
        # fp_fig = fp+"rms_{}.png".format(fname)
        # plt.savefig(fp_fig)
        # plt.close()

        plt.subplot(1, 2, 1)
        plt.plot(range(128), ped, marker='.', linestyle = '-', alpha = 0.7, label='pos')
        plt.title(fname, fontsize = 14)
        plt.xlabel("Channel", fontsize = 14)
        plt.ylabel("Pedestal", fontsize = 14)
        x_sticks = range(0, 129, 16)
        plt.xticks(x_sticks)
        plt.grid(axis = 'x')
        if (ped_max < (fe_ped_med + 500)) and (ped_min > (fe_ped_med - 500)):
            plt.ylim(fe_ped_med - 500, fe_ped_med + 500)
        else:
            plt.grid(axis = 'y')
        fp_fig = fp+"ped_{}.png".format(fname)
        plt.gca().set_facecolor('none')  # set background as transparent
        plt.tight_layout()
        plt.savefig(fp_fig, transparent = True)
        plt.close()

        fp_bin = fp+"RMS_{}.bin".format(fname)
        with open(fp_bin, 'wb') as fn:
             pickle.dump( [ped, rms], fn)

        return ped,rms

    def GetPeaks(self, data, nfemb, fp, fname, funcfit=False, shapetime=2, period=500, dac = 0):

        nevent = len(data)

        ppk_val = []
        npk_val = []
        bl_val = []
        ppk = []
        npk = []
        bl = []
        bl_rms = []

        rms = []
        ped = []

        plt.figure(figsize=(12, 4))

        if period == 500:
            pulrange = 120
            pulseoffset = 30
            offset2 = 120
        else:
            pulrange = 220
            pulseoffset = 30
            offset2 = 220

        for ich in range(128):
            global_ch = nfemb * 128 + ich
            allpls = np.zeros(period)
            allpls2 = np.zeros(period)
            npulse = 0
            hasError = False
            pulse = []
            pulse2 = []
            for itr in range(nevent):
                # print(data[itr])
                # print(nfemb)
                # input()
                evtdata = np.array(data[itr][nfemb][ich])
                tstart = data[itr][4] // 0x20
                for tt in range(int(period - (tstart % period)), len(evtdata) - period - offset2 - 1, period):
                    allpls = allpls + evtdata[tt:tt + period]
                    pulse.extend(evtdata[tt:tt + period])
                    allpls2 = allpls2 + evtdata[tt + offset2:tt + period + offset2]
                    pulse2.extend(evtdata[tt + offset2:tt + period + offset2])
                    npulse = npulse + 1

            apulse = allpls / npulse
            apulse2 = allpls2 / npulse
            pmax = np.amax(apulse)
            maxpos = np.argmax(apulse)
            if dac == 48:
                # print(len(evtdata))
                if ich == 70:
                # print(allpls)
                    print(evtdata)
                    print(ich)
                    print(dac)
                    plt.figure(figsize=(8, 6))
                    plt.plot(range(len(evtdata)), evtdata, marker='o', linestyle='-')
                    plt.show()

                if ich == 1:
                    print(evtdata)
                    print(ich)
                    print(dac)
                    plt.figure(figsize=(8, 6))
                    plt.plot(range(len(evtdata)), evtdata, marker='o', linestyle='-')
                    # plt.show()



            data_type = apulse.dtype
            plt.subplot(1, 2, 1)
            if maxpos >= pulseoffset and maxpos < len(apulse) + pulseoffset - pulrange:
                plot_pulse = apulse[maxpos - pulseoffset:maxpos - pulseoffset + pulrange]
                plt.plot(range(len(plot_pulse)), plot_pulse)
                if maxpos < 70:
                    baseline = pulse[:maxpos - 20]
                else:
                    baseline = pulse[maxpos - 40:maxpos - 20]
                baseline.extend(pulse[maxpos - 40 + period:maxpos - 20 + period])
                if npulse > 2:
                    baseline.extend(pulse[maxpos - 40 + 2*period:maxpos - 20 + 2*period])

            if maxpos < pulseoffset:
                plot_pulse = apulse2[maxpos - pulseoffset + period-offset2:maxpos - pulseoffset + period-offset2 + pulrange]
                plt.plot(range(len(plot_pulse)), plot_pulse)
                baseline = pulse[maxpos + period - 40:maxpos + period - 20]
                # baseline = pulse[maxpos + offset2+pulseoffset+pulseoffset:maxpos + period - 100]
                # baseline.extend(pulse[maxpos + offset2+pulseoffset+pulseoffset + period:maxpos + period - 100 + period])
                baseline.extend(pulse[maxpos + period - 40 + period:maxpos + period - 20 + period])
                # baseline.extend(pulse[maxpos + 180 + 2*period:maxpos + 500 - 100 + 2*period])

            if maxpos >= len(apulse) + pulseoffset - pulrange:
                plot_pulse = apulse2[maxpos - pulseoffset - offset2:maxpos - pulseoffset - offset2 + pulrange]
                plt.plot(range(len(plot_pulse)), plot_pulse)
                baseline = pulse[maxpos - 40:maxpos - 20]
                # baseline = pulse[180:maxpos - 20]
                # baseline.extend(pulse[180 + period: maxpos - 20 + period])
                baseline.extend(pulse[maxpos - 40 + period: maxpos - 20 + period])
                # baseline.extend(pulse[180 + 2*period: maxpos - 20 + 2*period])

            pulse_rms = np.std(baseline)
            pulse_ped = np.mean(baseline)

            if funcfit:
                popt = FitFunc(apulse, shapetime, makeplot=False)
                a_xx = np.array(range(20)) * 0.5
                a_yy = ResFunc(a_xx, popt[0], popt[1], popt[2], popt[3])
                pmax = np.amax(a_yy)

            if maxpos > 100:
                bbl = np.mean(apulse[:maxpos - 50])
            else:
                bbl = np.mean(apulse[400:])

            pmin = np.amin(apulse)

            ppk_val.append(pmax)
            # ppk.append(pmax - pulse_ped)
            npk_val.append(pmin)
            # npk.append(pmin - pulse_ped)
            # bl_rms.append(bbl_rms)
            # bl_val.append(bbl)
            bl_val.append(pulse_ped)
            bl.append(bbl)

            rms.append(pulse_rms)
            ped.append(pulse_ped)

            if ich == 64:
                log.channel0_pulse[nfemb][dac] = plot_pulse - pulse_ped

        rms_mean = np.mean(rms)

        bottom = -1000
        plt.title(fname, fontsize=14)  # "128-CH Pulse Response Overlap"
        plt.ylim(bottom, 16384 + 1000)
        plt.xlabel("Time (512 ns / step)", fontsize=14)
        plt.ylabel("ADC count", fontsize=14)
        plt.grid(axis='y', color='gray', linestyle='--', alpha=0.5)

        plt.subplot(1, 2, 2)
        plt.plot(range(128), ppk_val, marker='|', linestyle='-', alpha=0.7, label='pos', color='blue')
        plt.plot(range(128), bl_val, marker='|', linestyle='-', alpha=0.9, label='ped', color='0.3')
        plt.plot(range(128), npk_val, marker='|', linestyle='-', alpha=0.7, label='neg', color='orange')
        plt.grid(axis='x', color='gray', linestyle='--', alpha=0.5)

        # pl1.plot(range(128), bl_rms)
        plt.title("Parameater Distribution: PPK, BBL, NPK", fontsize=14)
        plt.ylim(bottom, 16384 + 1000)
        plt.xlabel("Channel", fontsize=14)
        plt.xticks(np.arange(0, 129, 16))
        plt.ylabel("ADC count", fontsize=14)
        plt.legend()

        # plt.subplot(1, 3, 3)
        # plt.plot(range(128), rms, marker='o', linestyle='-', alpha=0.5, label='RMS')
        # plt.title("RMS Distribution", fontsize=14)
        # plt.ylim(rms_mean - 5, rms_mean + 5)
        # plt.xlabel("chan", fontsize=14)
        # plt.xticks(np.arange(0, 129, 16))
        # plt.ylabel("RMS", fontsize=14)
        # plt.grid(axis='x', color='gray', linestyle='--', alpha=0.7)
        #
        # plt.legend()

        fp_fig = fp + "pulse_{}.png".format(fname)
        plt.gca().set_facecolor('none')  # set background as transparent
        plt.tight_layout()
        plt.savefig(fp_fig, transparent = True)
        plt.close()

        fp_bin = fp + "Pulse_{}.bin".format(fname)
        with open(fp_bin, 'wb') as fn:
            pickle.dump([ppk_val, npk_val, bl_val], fn)

        return ppk_val, npk_val, bl_val


    def PrintPWR(self, pwr_data, nfemb, fp):

        pwr_set=[5,3,3,3.5]
        pwr_dic={'name':[],'V_set/V':[],'V_meas/V':[],'I_meas/A':[],'P_meas/W':[]}
        i=0
        total_p = 0

        pwr_dic['name'] = ['BIAS','LArASIC','ColdDATA','ColdADC']
        bias_v = round(pwr_data['FEMB%d_BIAS_V'%nfemb],3)
        bias_i = round(pwr_data['FEMB%d_BIAS_I'%nfemb],3)

        if abs(bias_i)>0.005:
           print('Warning: FEMB{} Bias current abs({})>0.005'.format(nfemb,bias_i))

        pwr_dic['V_set/V'].append(pwr_set[0])
        pwr_dic['V_meas/V'].append(bias_v)
        pwr_dic['I_meas/A'].append(bias_i)
        pwr_dic['P_meas/W'].append(round(bias_v*bias_i,3))
        total_p = total_p + round(bias_v*bias_i,3)

        for i in range(3):
            tmpv = round(pwr_data['FEMB{}_DC2DC{}_V'.format(nfemb,i)],3)
            tmpi = round(pwr_data['FEMB{}_DC2DC{}_I'.format(nfemb,i)],3)
            tmpp = round(tmpv*tmpi,3)

            pwr_dic['V_set/V'].append(pwr_set[i+1])
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

    def PlotMon(self, fembs, mon_dic, savedir, fdir, fname, fembNo):
        issue_log = defaultdict(dict)
        pulse_log = defaultdict(dict)
        for nfemb in fembs:
            mon_list=[]
            femb_id = "FEMB ID {}".format(fembNo['femb%d' % nfemb])
            for key,mon_data in mon_dic.items():
                chip_list=[]
                sps = len(mon_data)

                for j in range(sps):
                    a_mon = mon_data[j][nfemb]
                    chip_list.append(a_mon)

                if sps>1:
                   chip_list = np.array(chip_list)
                   mon_mean = np.mean(chip_list)
                else:
                   mon_mean = chip_list[0]

                mon_list.append(mon_mean*self.fadc)

            # fig,ax = plt.subplots(figsize=(6,4))
            xx=range(len(mon_dic))
            mon_mean = np.mean(mon_list)
            mon_std = np.std(mon_list)
            i = 0
            issue_log[femb_id]["Result"] = True
            for data in mon_list:
                i = i + 1
                if data > (mon_mean + 50) or data < (mon_mean -50):
                    issue_log[femb_id]["{}_C{}".format(fname, i)] = data
                    issue_log[femb_id]["Result"] = False
            pulse_log[femb_id] = mon_list
            # ax.plot(xx, mon_list, marker='.')
            # ax.set_ylabel(fname)
            # fp = savedir[nfemb] + fdir + "/mon_{}.png".format(fname)
            # fig.savefig(fp)
            # plt.close(fig)
        return issue_log, pulse_log

    def PlotMonDAC(self, fembs, mon_dic, savedir, fdir, fembNo):
        issue_inl = defaultdict(dict)
        for nfemb in fembs:
            femb_id = "FEMB ID {}".format(fembNo['femb%d' % nfemb])
            fig, ax = plt.subplots(figsize=(6, 5))
            issue_inl[femb_id]["Result"] = True
            for main_key, sub_dict in mon_dic.items():
                item = 0
                for key,mon_list in sub_dict.items():
                    data_list=[]
                    dac_list = mon_list[1]
                    # print(dac_list)
                    mon_data = mon_list[0]
                    sps = mon_data[0][3]
                    item = item + 1
                    print(dac_list)
                    for i in range(len(dac_list)):
                        sps_list=[]
                        for j in range(sps):
                            a_mon = mon_data[i][4][j][nfemb]
                            sps_list.append(a_mon)

                        if sps>1:
                           sps_list = np.array(sps_list)
                           mon_mean = np.mean(sps_list)
                           # mon_mean = stats.mode(sps_list)[0]

                        else:
                           mon_mean = sps_list[0]

                        data_list.append(mon_mean*self.fadc)

                    if item == 8:
                        plt.plot(dac_list, data_list, marker='.', label = main_key)
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
                    inl = np.max(abs(fit_y - y_data)*100/abs(data_list[0]-data_list[-3]))
                    if inl > 1:
                        issue_inl[femb_id]["INL-{}-{}".format(main_key, key)] = inl
                        issue_inl[femb_id]["Result"] = False
                        # print(issue_inl)
                        # print(abs(fit_y - y_data)*100/abs(data_list[0]-data_list[63]))
                        # input()
            fp = savedir[nfemb] + fdir + "/mon_{}.png".format(main_key)
            plt.legend()
            plt.grid(True, axis='y', linestyle='--')
            plt.ylim(0, 1400)
            plt.xlabel("DAC Selection", fontsize=12)
            plt.ylabel("Voltage / mV", fontsize=12)
            plt.title("LArASIC DAC Linearity", fontsize=12)
            plt.gca().set_facecolor('none')  # set background as transparent
            plt.tight_layout()
            plt.savefig(fp, transparent = True)
            plt.close(fig)
            print(issue_inl)
        return issue_inl


    def PlotADCMon(self, fembs, mon_list, savedir, fdir, fembNo):
        issue_inl = defaultdict(dict)
        mon_items = ["VBGR", "VCMI", "VCMO", "VREFP", "VREFN", "VBGR", "VSSA", "VSSA"]
        mon_items_n=[1,2,3,4]
        nvset = len(mon_list)
        status = True

        for nfemb in fembs:
            femb_id = "FEMB ID {}".format(fembNo['femb%d' % nfemb])
            check = True
            check_issue = []
            for imon in mon_items_n:
                vset_list=[]
                fig,ax = plt.subplots(figsize=(6,4))
                data_dic={}

                for i in range(nvset):
                    vset_list.append(mon_list[i][0])
                    mon_data = mon_list[i][1]
                    chip_dic = mon_data[imon]
                    for key,chip_data in chip_dic.items():
                        sps = len(chip_data[3])
                        sps_list=[]
                        for j in range(sps):
                            a_mon = chip_data[3][j][nfemb]
                            sps_list.append(a_mon)
                        if sps>1:
                           sps_list = np.array(sps_list)
                           mon_mean = np.mean(sps_list)
                        else:
                           mon_mean = sps_list[0]
                        if key not in data_dic:
                           data_dic[key]=[]
                        data_dic[key].append(mon_mean*self.fadc)

                for key, chip_data in chip_dic.items():
                    #   INL judgement
                    x_data = np.array(range(0,256,16))
                    y_data = np.array(data_dic[key])
                    coefficients = np.polyfit(x_data[0:14], y_data[0:14], deg=1)
                    fit_function = np.poly1d(coefficients)
                    fit_y = fit_function(x_data[0:14])
                    inl = round(np.max(abs(fit_y - y_data[0:14]) * 100 / abs(y_data[0] - y_data[-1])), 2)
                    # print(key)
                    # print(mon_items[imon])
                    # print(inl)
                    if inl < 1:
                        log.ADCMON_table_cell[femb_id]["{}_{}".format(mon_items[imon], key)] = "{}".format(inl)
                    else:
                        check = False
                        check_issue.append("ADC ref voltage: {}, chip: {}, inl issue: {} \n".format(imon, key, inl))
                        log.ADCMON_table_cell[femb_id]["{}_{}".format(mon_items[imon], key)] =  "<span style = 'color:red;'> {} </span>".format(inl)
                # print(log.ADCMON_table_cell)
                # input()

                for key,values in data_dic.items():
                    ax.plot(vset_list, data_dic[key], marker='.',label=key)
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
                plt.savefig(fp, transparent = True)
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
        dac_init=[]
        pk_init=[]
        for i in range(len(dac_list)):
            if ((pk_list[i]<updac) and (pk_list[i]>lodac)):
                dac_init.append(dac_list[i])
                pk_init.append(pk_list[i])

    #   first fit, use initial sample points
        try:
           slope_i,intercept_i=np.polyfit(dac_init,pk_init,1)
        except:
            # we suggest here report an issue
           fig1,ax1 = plt.subplots()
           ax1.plot(dac_init,pk_init, marker='.')
           ax1.set_xlabel("DAC")
           ax1.set_ylabel("Peak Value") 
           ax1.set_title("chan%d fail first gain fit"%chan)
           plt.tight_layout()
           plt.savefig(fp+'fail_first_fit_ch%d.png'%chan)
           plt.close(fig1)
         
           print("fail at first gain fit")
           return 0,0,0

#   with these filter, get a line and find the most line area
        y_min = pk_list[0]
        y_max = pk_list[-1]
        linear_dac_max=dac_list[-1]
        if 'CALI5' in fp or 'CALI6' in fp:
            inl_th = 0.08
        else:
            inl_th = 0.018
        index=len(dac_init)-1
        for i in range(len(dac_list)):
            y_r = pk_list[i]
            y_p = dac_list[i]*slope_i + intercept_i
            inl = abs(y_r-y_p)/(y_max-y_min)
            if inl>inl_th:
                if dac_list[i]<5:
                    continue
                linear_dac_max = dac_list[i-1]
                index=i
                break
        # print(linear_dac_max)
        # print(index)

        if index==0:
            fig2,ax2 = plt.subplots(1,2, figsize=(12,6))
            ax2[0].plot(dac_list,pk_list, marker='.')
            ax2[0].set_xlabel("DAC")
            ax2[0].set_ylabel("Peak Value") 
            ax2[0].set_title("chan%d fail linear range searching"%chan)

            tmp_inl=[]
            tmp_dac=[]
            for i in range(len(dac_list)):
                if dac_list[i]>updac:
                   break
                y_r = pk_list[i]
                y_p = dac_list[i]*slope_i + intercept_i
                inl_1 = abs(y_r-y_p)/(y_max-y_min)
                tmp_inl.append(inl_1)
                tmp_dac.append(i)

            ax2[1].plot(tmp_dac,tmp_inl, marker='.')
            ax2[1].set_xlabel("DAC")
            ax2[1].set_ylabel("Peak Value") 
            ax2[1].set_title("chan%d inl"%chan)
            plt.tight_layout()
            plt.savefig(fp+'fail_inl_ch%d.png'%chan)
            plt.close(fig2)
            print("fail at first linear range searching: inl=%f for dac=0 is bigger than 0.03"%inl)
            return 0,0,0

        # print(dac_list[:index])
#   second linear fit, with all linear area
        try:
            slope_f,intercept_f=np.polyfit(dac_list[:index],pk_list[:index],1)
        except:
            fig3,ax3 = plt.subplots()
            ax3.plot(dac_list[:index],pk_list[:index],marker='.')
            ax3.set_xlabel("DAC")
            ax3.set_ylabel("Peak Value") 
            ax3.set_title("chan%d fail second gain fit"%chan)
            plt.tight_layout()
            plt.savefig(fp+'fail_second_fit_ch%d.png'%chan)
            plt.close(fig3)
            print("fail at second gain fit")
            return 0,0,0

        y_max = pk_list[index-1]
        y_min = pk_list[0]
        INL=0
        # print(index)
        for i in range(index):
            y_r = pk_list[i]
            y_p = dac_list[i]*slope_f + intercept_f
            inl = abs(y_r-y_p)/((y_max-y_min)*2)
            if inl>INL:
               INL=inl

        return slope_f, INL, linear_dac_max


    def GetGain(self, fembs, fembNo, datadir, savedir, fdir, namepat, snc, sgs, sts, dac_list, updac=25, lodac=10):
        log.tmp_log.clear()
        log.check_log.clear()
        log.chkflag.clear()
        log.badlist.clear()
        dac_v = {}  # mV/bit
        dac_v['4_7mVfC']=18.66
        dac_v['7_8mVfC']=14.33
        dac_v['14_0mVfC']=8.08
        dac_v['25_0mVfC']=4.61

        CC=1.85*pow(10,-13)
        e=1.602*pow(10,-19)

        if "sgp1" in namepat:
            dac_du = dac_v['4_7mVfC']
            fname = '{}_{}_{}_sgp1'.format(snc,sgs,sts)
        else:
            dac_du = dac_v[sgs]
            fname = '{}_{}_{}'.format(snc,sgs,sts)

        pk_list = [[],[],[],[]]
        print(dac_list)
        for dac in dac_list:
            fdata = datadir+namepat.format(snc,sgs,sts,dac)+'.bin'
            with open(fdata, 'rb') as fn:
                 raw = pickle.load(fn)

            rawdata = raw[0]
            pwr_meas = raw[1]
            wibdata = self.data_decode(rawdata, fembs)
            pldata = wibdata

            for ifemb in fembs:
                fp = savedir[ifemb]+fdir
                if dac==0:
                    fname_1 = namepat.format(snc, sgs, sts, dac)
                    ped,rms = self.GetRMS(pldata, ifemb, fp, fname)
                    if not('vdac' in fname_1):
                        pk_list[ifemb].append(np.zeros(128))
                else:
                    fname_1 = namepat.format(snc,sgs,sts,dac)
                    if ('vdac' in fname_1):
                        if not ('000mV' in fname_1):
                            ppk,bpk,bl=self.GetPeaks(pldata, ifemb, fp, fname_1, period = 1000, dac = dac)
                    else:
                        ppk,bpk,bl=self.GetPeaks(pldata, ifemb, fp, fname_1, dac = dac)
                    ppk_np = np.array(ppk)-np.array(bl)
                    pk_list[ifemb].append(ppk_np)


        for ifemb in fembs:
            femb_id = "FEMB ID {}".format(fembNo['femb%d' % ifemb])
            tmp_list = pk_list[ifemb]
            new_pk_list = list(zip(*tmp_list))
            check = True
            check_issue = []
            dac_np = np.array(dac_list)
            pk_np = np.array(new_pk_list)
            fp = savedir[ifemb]+fdir
             
            gain_list = []
            inl_list = []
            line_range_list = []
            max_dac_list = []
            plt.figure(figsize=(9, 6))
            #   overlap channel 0 pulse from [1 - 63]

            #   peak - dac linear
            plt.subplot(2, 2, 2)
            for ch in range(128):
                uplim = np.max(pk_np[ch])*4/5
                lodac = np.max(pk_np[ch])*1/5
                gain,inl,line_range = self.CheckLinearty(dac_np,pk_np[ch],uplim,lodac,ch,fp)
                if gain==0:
                    print("femb%d ch%d gain is zero"%(ifemb,ch))
                else:
                    if ('vdac' in namepat):
                        gain = 1/gain/1000 *CC/e
                    else:
                        gain = 1 / gain * dac_du / 1000 * CC / e
                gain_list.append(gain)
                inl_list.append(inl)
                line_range_list.append(line_range)
                if ('vdac' in namepat):
                    if inl > 0.1:
                        check = False
                        check_issue.append("ch {} INL issue: {}".format(ch, inl))
                    if line_range < 200:
                        check = False
                        check_issue.append("ch {} line range issue: {}".format(ch, line_range))
                    if gain > 45:
                        check = False
                        check_issue.append("ch {} gain issue: {}".format(ch, gain))
                else:
                    if inl > 0.01:
                        check = False
                        check_issue.append("ch {} INL issue: {}".format(ch, inl))
                    if "900mV" in fname_1:
                        if line_range < 25:
                            check = False
                            check_issue.append("ch {} line range issue: {}".format(ch, line_range))
                        if gain > 43:
                            check = False
                            check_issue.append("ch {} Gain issue at 14_0 mVfC: {}".format(ch, line_range))

                    elif '200mV' in fname_1:
                        if line_range < 50:
                            check = False
                            check_issue.append("ch {} Line range issue at 4_7 mVfC: {}".format(ch, line_range))
                        if '4_7' in fname_1:
                            if gain > 135:
                                check = False
                                check_issue.append("ch {} Gain issue at 4_7 mVfC: {}".format(ch, line_range))
                        if '7_8' in fname_1:
                            if gain > 78:
                                check = False
                                check_issue.append("ch {} Gain issue at 7_8 mVfC: {}".format(ch, line_range))
                        if '14_0' in fname_1:
                            if gain > 45:
                                check = False
                                check_issue.append("ch {} Gain issue at 14_0 mVfC: {}".format(ch, line_range))
                        if '25_0' in fname_1:
                            if gain > 26:
                                check = False
                                check_issue.append("ch {} Gain issue at 25_0 mVfC: {}".format(ch, line_range))

                        if line_range < 50:
                            check = False
                            check_issue.append("ch {} line range issue: {}".format(ch, line_range))
                # max_dac_list.append(max_dac)
                plt.plot(dac_np, pk_np[ch])
            log.tmp_log[femb_id]["INL"] = np.max(inl_list)
            log.tmp_log[femb_id]["Gain"] = np.mean(gain_list)
            log.tmp_log[femb_id]["Gainstd"] = np.std(gain_list)
            log.tmp_log[femb_id]["Linearangemin"] = np.min(line_range_list)
            log.check_log[femb_id]["Result"] = check
            log.check_log[femb_id]["Issue List"] = check_issue

            plt.ylabel("Peak Value", fontsize=14)
            plt.xlabel("DAC", fontsize=14)
            plt.title("Peak vs. DAC Linearity", fontsize=14)
            line_min = np.min(line_range_list)

            plt.subplot(2, 2, 1)
            # print(log.channel0_pulse[ifemb][dac])
            for dac in dac_list[1: -2]:
                plt.plot(range(len(log.channel0_pulse[ifemb][dac])), log.channel0_pulse[ifemb][dac])
                # if line_min < 15:
                #     plt.plot(range(len(log.channel0_pulse[ifemb][dac])), log.channel0_pulse[ifemb][dac])
                # else:
                #     if dac % 4 == 0:
                #         plt.plot(range(len(log.channel0_pulse[ifemb][dac])), log.channel0_pulse[ifemb][dac])
            plt.ylabel("ADC value", fontsize=14)
            plt.xlabel("Sample", fontsize=14)
            # plt.legend()
            plt.title("Pulse Response in DAC linear range", fontsize=14)
            #   Gain
            plt.subplot(2, 2, 3)
            plt.plot(range(128), gain_list, marker='.')
            plt.xlabel("Channel", fontsize=14)
            plt.ylabel("Gain", fontsize=14)
            x_sticks = range(0, 129, 16)
            plt.ylim(0, 120)
            plt.xticks(x_sticks)
            plt.grid(axis='x')
            plt.title("128-ch Gain Distribution", fontsize=14)

            #   INL
            plt.subplot(2, 2, 4)
            plt.plot(range(128), inl_list, marker='.')
            plt.xlabel("Channel", fontsize=14)
            plt.ylabel("INL", fontsize=14)
            plt.ylim(0, 0.02)
            x_sticks = range(0, 129, 16)
            plt.xticks(x_sticks)
            plt.grid(axis='x')
            plt.title("INL Distribution for the 128-Channel", fontsize=14)
            # plt.plot(range(128), max_dac_list, marker='.')
            # plt.xlabel("chan")
            # plt.ylabel("linear_range")
            # plt.title("linear range")
            plt.gca().set_facecolor('none')  # set background as transparent
            plt.tight_layout()
            plt.savefig(fp + 'gain_{}.png'.format(fname), transparent = True)
            plt.close()

            fp_bin = fp + "Gain_{}.bin".format(fname)
            with open(fp_bin, 'wb') as fn:
                pickle.dump(gain_list, fn)

            plt.figure(figsize=(4,3))
            xx=range(128)
            plt.plot(xx, line_range_list, marker='.')
            if 'vdac' in namepat:
                plt.ylim(0, 700)
            else:
                plt.ylim(0, 70)
            plt.xlabel("Channel", fontsize = 14)
            plt.ylabel("Line_range", fontsize = 14)
            plt.title(fname, fontsize = 14)
            fp = savedir[ifemb]+fdir+"Line_range_{}.png".format(fname)
            plt.gca().set_facecolor('none')  # set background as transparent
            plt.tight_layout()
            plt.savefig(fp, transparent = True)
            plt.close()



                
    def GetENC(self, fembs, fembNo, snc, sgs, sts, sgp, savedir, fdir):
        for ifemb in fembs:
            femb_id = "FEMB ID {}".format(fembNo['femb%d' % ifemb])
            if sgp==0:
               fname ="{}_{}_{}".format(snc, sgs, sts)
            if sgp==1:
               fname ="{}_{}_{}_sgp1".format(snc, sgs, sts)

            frms = savedir[ifemb] + fdir + "RMS_{}.bin".format(fname)
            fgain = savedir[ifemb] + fdir + "Gain_{}.bin".format(fname)

            with open(frms, 'rb') as fn:
                 rms_list = pickle.load(fn)
            rms_list=np.array(rms_list[1])

            with open(fgain, 'rb') as fn:
                 gain_list = pickle.load(fn)
            gain_list=np.array(gain_list)

            enc_list = rms_list*gain_list
            enc_mean = np.mean(enc_list)
            enc_std = np.std(enc_list)

            plt.figure(figsize=(4,3))
            xx=range(128)
            plt.plot(xx, enc_list, marker='.')
            plt.ylim(enc_mean-300, enc_mean + 300)
            plt.xlabel("chan", fontsize = 14)
            plt.ylabel("ENC", fontsize = 14)
            x_sticks = range(0, 129, 16)
            plt.xticks(x_sticks)
            plt.grid(axis='x')
            plt.title(fname, fontsize = 14)
            fp = savedir[ifemb]+fdir+"enc_{}.png".format(fname)
            plt.gca().set_facecolor('none')  # set background as transparent
            plt.tight_layout()
            plt.savefig(fp, transparent = True)
            plt.close()

            log.tmp_log[femb_id]["ENC"] = enc_mean
            log.tmp_log[femb_id]["ENC_std"] = enc_std

            fp_bin = savedir[ifemb] + fdir + "ENC_{}.bin".format(fname)
            with open(fp_bin, 'wb') as fn:
                 pickle.dump( enc_list, fn) 
