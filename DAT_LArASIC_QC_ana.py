#----------------
# DAT_LArASIC_QC_ana.py based on the DAT_LArASIC_QC_quick_ana.py written by Shanshan
# Created on March, 13th, 2024
#
#-----------------
import datetime
import os, sys
import numpy as np
import pickle
import matplotlib.pyplot as plt
from spymemory_decode import wib_dec

class DAT_LArASIC_QC_ana:
    def __init__(self, rootpath='', datadir=''):
        self.__rootpath = '/'.join([rootpath, datadir])
        self.__tms = [0] # initialization checkout
        self.__testItems_dict = {0: "Initialization checkout",
                                 1: "FE power consumption measurement",
                                 2: "FE response measurement checkout",
                                 3: "FE monitoring measurement",
                                 4: "FE power cycling measurement",
                                 5: "FE noise measurement",
                                 61: "FE calibration measurement (ASIC-DAC)",
                                 62: "FE calibration measurement (DAT-DAC)",
                                 63: "FE calibration measurement (Direct-Input)",
                                 7: "FE delay run",
                                 8: "FE cali-cap measurement"}
        self.__ItemsFilename_dict = {
                                        0: 'QC_INIT_CHK.bin',
                                        1: 'QC_PWR.bin',
                                        2: 'QC_CHKRES.bin',
                                        3: 'QC_MON.bin',
                                        4: 'QC_PWR_CYCLE.bin',
                                        5: 'QC_RMS.bin',
                                        61: 'QC_CALI_ASICDAC.bin',
                                        62: 'QC_CALI_DATDAC.bin',
                                        63: 'QC_CALI_DIRECT.bin',
                                        7: 'QC_DLY_RUN.bin',
                                        8: 'QC_Cap_Meas.bin'
                                    }
    
    def printTestItems(self):
        for i, elt in self.__testItems_dict.items():
            print("{} : {}".format(i, elt))
    
    def __printItem(self, tms):
        print('--'*20)
        print('*\t{}\t\t*'.format(self.__testItems_dict[tms]))
        print('--'*20)

    def doQC_all(self):
        evl = input ("Analyze all test items? (Y/N) : " )
        if ("Y" in evl) or ("y" in evl):
            self.__tms = [0, 1, 2,3,4,5,61, 62, 63,7,8]
        else:
            while True:
                testnostr = input ("Please input a number (0, 1, 2, 3, 4, 5, 61, 62, 63, 8) for one test item: " )
                try:
                    testno = int(testnostr)
                    self.__tms = [testno]
                    break
                except ValueError:
                    print ("Wrong value, please re-enter...")
    
    def linear_fit(self, x, y):
        error_fit = False 
        try:
            results = sm.OLS(y,sm.add_constant(x)).fit()
        except ValueError:
            error_fit = True 
        if ( error_fit == False ):
            error_gain = False 
            try:
                slope = results.params[1]
            except IndexError:
                slope = 0
                error_gain = True
            try:
                constant = results.params[0]
            except IndexError:
                constant = 0
        else:
            slope = 0
            constant = 0
            error_gain = True

        y_fit = np.array(x)*slope + constant
        delta_y = abs(y - y_fit)
        inl = delta_y / (max(y)-min(y))
        peakinl = max(inl)
        return slope, constant, peakinl, error_gain
    
    def ana_fepwr(self, pwr_meas, vin=[1.7,1.9], cdda=[15,25], cddp=[20,35], cddo=[0,5]):
        kpwrs = list(pwr_meas.keys())

        vddas = []
        vddos = []
        vddps = []
        cddas = []
        cddos = []
        cddps = []

        for i in range(len(kpwrs)):
            if "VDDA" in kpwrs[i]:
                vddas.append(pwr_meas[kpwrs[i]][0])
                cddas.append(pwr_meas[kpwrs[i]][1])
            if "VDDO" in kpwrs[i]:
                vddos.append(pwr_meas[kpwrs[i]][0])
                cddos.append(pwr_meas[kpwrs[i]][1])
            if "VPPP" in kpwrs[i]:
                vddps.append(pwr_meas[kpwrs[i]][0])
                cddps.append(pwr_meas[kpwrs[i]][1])
        
        show_flg=True
        if all(item >= vin[0] for item in vddas) and all(item <= vin[1] for item in vddas) :
            if all(item >= vin[0] for item in vddos) and all(item <= vin[1] for item in vddos) :
                if all(item >= vin[0] for item in vddps) and all(item <= vin[1] for item in vddps) :
                    if all(item >= cdda[0] for item in cddas) and all(item <= cdda[1] for item in cddas) :
                        if all(item >= cddp[0] for item in cddps) and all(item <= cddp[1] for item in cddps) :
                            if all(item >= cddo[0] for item in cddos) and all(item <= cddo[1] for item in cddos) :
                                show_flg = False
        return show_flg

    def plt_fepwr(self, plt, pwr_meas):
        kpwrs = list(pwr_meas.keys())
        ax5 = plt.subplot2grid((2, 3), (0, 0), colspan=1, rowspan=1)
        ax6 = plt.subplot2grid((2, 3), (1, 0), colspan=1, rowspan=1)

        vddas = []
        vddos = []
        vddps = []
        cddas = []
        cddos = []
        cddps = []

        for i in range(len(kpwrs)):
            if "VDDA" in kpwrs[i]:
                vddas.append(pwr_meas[kpwrs[i]][0])
                cddas.append(pwr_meas[kpwrs[i]][1])
            if "VDDO" in kpwrs[i]:
                vddos.append(pwr_meas[kpwrs[i]][0])
                cddos.append(pwr_meas[kpwrs[i]][1])
            if "VPPP" in kpwrs[i]:
                vddps.append(pwr_meas[kpwrs[i]][0])
                cddps.append(pwr_meas[kpwrs[i]][1])

        fe=[0,1,2,3,4,5,6,7]
        ax5.plot(fe, vddas, color='b', marker = 'o', label='VDDA')
        ax5.plot(fe, vddps, color='r', marker = 'o', label='VDDP')
        ax5.plot(fe, vddos, color='g', marker = 'o', label='VDDO')
        ax5.set_title("Voltage Measurement", fontsize=8)
        ax5.set_ylabel("Voltage / V", fontsize=8)
        ax5.set_ylim((0,2))
        ax5.set_xlabel("FE no", fontsize=8)
        ax5.grid()
        ax5.legend()

        ax6.scatter(fe, cddas, color='b', marker = 'o', label='VDDA')
        ax6.scatter(fe, cddps, color='r', marker = 'o', label='VDDP')
        ax6.scatter(fe, cddos, color='g', marker = 'o', label='VDDO')
        ax6.set_title("Current Measurement", fontsize=8)
        ax6.set_ylabel("Current / mA", fontsize=8)
        ax6.set_ylim((-10,50))
        ax6.set_xlabel("FE no", fontsize=8)
        ax6.legend()
        ax6.grid()

    def data_ana(self, fembs, rawdata, rms_flg=False):
        wibdata = wib_dec(rawdata,fembs, spy_num=1, cd0cd1sync=False)[0]
        datd = [wibdata[0], wibdata[1],wibdata[2],wibdata[3]][fembs[0]]

        chns =[]
        rmss = []
        peds = []
        pkps = []
        pkns = []
        wfs = []
        wfsf = []

        ppos0=0
        npos0=0
        ppos64=0
        npos64=0
        for achn in range(len(datd)):
            chndata = datd[achn]
            amax = np.max(chndata[300:-150])
            amin = np.min(chndata[300:-150])
            if achn==0:
                ppos0 = np.where(chndata[300:-150]==amax)[0][0] + 300
                npos0 = np.where(chndata[300:-150]==amin)[0][0] + 300
            if achn==64:
                ppos64 = np.where(chndata[300:-150]==amax)[0][0] + 300
                npos64 = np.where(chndata[300:-150]==amin)[0][0] + 300

            if rms_flg:
                arms = np.std(chndata)
                aped = int(np.mean(chndata))
            else:
                if achn <64:
                    arms = np.std(chndata[ppos0-150:ppos0-50])
                    aped = int(np.mean(chndata[ppos0-150:ppos0-50]))
                    wfs.append(chndata[ppos0-50:ppos0+150])
                    wfsf.append(chndata)
                else:
                    arms = np.std(chndata[ppos64-150:ppos64-50])
                    aped = int(np.mean(chndata[ppos64-150:ppos64-50]))
                    wfs.append(chndata[ppos64-50:ppos64+150])
                    wfsf.append(chndata)
            chns.append(achn)
            rmss.append(arms)
            peds.append(aped)
            pkps.append(amax)
            pkns.append(amin)
        return chns, rmss, peds, pkps, pkns, wfs, wfsf
    
    def ana_res(self, fembs, rawdata, par=[7000,10000], rmsr=[5,25], pedr=[500,3000] ):
        chns, rmss, peds, pkps, pkns, wfs, wfsf = self.data_ana(fembs, rawdata)
        # show_flg_failed=True
        amps = np.array(pkps) - np.array(peds)

        ## All of these conditions need to be satisfied for the chips to pass the QC
        # if all(item > par[0] for item in amps) and all(item < par[1] for item in amps) :
        #     if all(item > rmsr[0] for item in rmss) and all(item < rmsr[1] for item in rmss) :
        #         if all(item > pedr[0] for item in peds) and all(item < pedr[1] for item in peds) :
                    # show_flg_failed = False
        # return show_flg_failed

        ## Improvement: get the result for each chip
        flg_amps_passed = False
        flg_rms_passed = False
        flg_ped_passed = False
        if all(item > par[0] for item in amps) and all(item < par[1] for item in amps) :
            flg_amps_passed = True
        if all(item > rmsr[0] for item in rmss) and all(item < rmsr[1] for item in rmss) :
            flg_rms_passed = True
        if all(item > pedr[0] for item in peds) and all(item < pedr[1] for item in peds) :
            flg_ped_passed = True
        
        flgs_amps = []
        passed = True
        for chn in range(128):
            if (amps[chn] < par[0]) or (amps[chn] > par[1]):
                passed = False
            if (chn+1)%16==0:
                flgs_amps.append(passed)
                passed = True
        
        flgs_rms = []
        passed = True
        for chn in range(128):
            if (rmss[chn] < rmsr[0]) and (rmss[chn] > rmsr[1]):
                passed = False
            if (chn+1)%16==0:
                flgs_rms.append(passed)
                passed = True
        print(flgs_rms)
        print(len(flgs_rms))

        result = {'Amplitude': flg_amps_passed,
                  'RMS': flg_rms_passed,
                  'Pedestal': flg_ped_passed}
        return result

    # def plt_subplot(self, plt, fembs, rawdata ):
    def plt_subplot(self, plt, chns, rmss, peds, pkps, pkns, wfs, wfsf):
        ax1 = plt.subplot2grid((2, 3), (0, 1), colspan=1, rowspan=1)
        ax2 = plt.subplot2grid((2, 3), (0, 2), colspan=1, rowspan=1)
        ax3 = plt.subplot2grid((2, 3), (1, 1), colspan=1, rowspan=1)
        ax4 = plt.subplot2grid((2, 3), (1, 2), colspan=1, rowspan=1)

        # chns, rmss, peds, pkps, pkns, wfs, wfsf = self.data_ana(fembs, rawdata)

        for chn in chns:
            ax1.plot(wfs[chn][30:70], marker='.')
            ax2.plot(wfsf[chn], color="C%d"%(chn//64+1))
        ax1.set_title("Overlap waveforms", fontsize=8)
        ax1.set_ylabel("Amplitude", fontsize=8)
        ax1.set_xlabel("Time", fontsize=8)
        ax2.set_title("Overlap waveforms", fontsize=8)
        ax2.set_ylabel("Amplitude", fontsize=8)
        ax2.set_xlabel("Time", fontsize=8)

        for i in range(0,128,16):
            ax3.vlines(i-0.5, 0, 17000, color='y')
            ax4.vlines(i-0.5, 0, 50, color='y')

        ax3.plot(chns, pkps, color='r', marker='.')
        ax3.plot(chns, peds, color='b', marker='.')
        ax3.plot(chns, pkns, color='m', marker='.')
        ax3.set_title("Pulse Response Distribution", fontsize=8)
        ax3.set_ylabel("Amplitude", fontsize=8)
        ax3.set_xlabel("CH number", fontsize=8)

        ax4.plot(chns,rmss, color='r', marker='.')
        ax4.set_title("Noise", fontsize=8)
        ax4.set_ylabel("ADC / bit", fontsize=8)
        ax4.set_xlabel("CH number", fontsize=8)
        ax1.grid()
        ax2.grid()

    def dacana(self, data,dacdkey):
        dacs, dacv = zip(*data[dacdkey])
        fedacs = [[], [], [], [], [], [], [], []]
        fes = []
        for fe in range(8):
            for dac in range(len(dacs)):
                fedacs[fe].append([dacs[dac],dacv[dac][fe]])
        
            x, y = zip(*fedacs[fe])
            y = np.array(y)*AD_LSB
            if ("SGP1" in dacdkey) or ("SG0_1_SG1_1" in dacdkey):
                slope, constant, peakinl, error_gain = linear_fit(x[:-3], y[:-3])
            else:
                slope, constant, peakinl, error_gain = linear_fit(x, y)
            fes.append([dacdkey, fe,x,y,slope, constant, peakinl])
        return fes

    # Analysis
    def Init_checkout(self):
        tms = self.__tms[0]
        self.__printItem(tms)
        fp = '/'.join([self.__rootpath, self.__ItemsFilename_dict[tms]])
        with open(fp, 'rb') as fn:
            data = pickle.load(fn)
        
        dkeys = list(data.keys())
        logsd = data["logs"]
        dkeys.remove("logs")
        for onekey in dkeys:
            if (onekey=='DIRECT_PLS_CHK') or (onekey=='ASICDAC_CALI_CHK'):
                cfgdata = data[onekey]
                fembs = cfgdata[0]
                rawdata = cfgdata[1]
                cfg_info = cfgdata[2]
                # decode raw data
                chns, rmss, peds, pkps, pkns, wfs, wfsf = self.data_ana(fembs, rawdata)
                if (onekey=="DIRECT_PLS_CHK") :
                    show_flg = self.ana_res(fembs, rawdata, par=[9000,16000], rmsr=[5,25], pedr=[300,3000] )
                    # print(show_flg)
                    
                    # fig = plt.figure(figsize=(16,8))
                    # # self.plt_subplot(plt=plt, fembs=fembs, rawdata=rawdata)
                    # self.plt_subplot(plt=plt, chns=chns, rmss=rmss, peds=peds,
                    #                  pkps=pkps, pkns=pkns, wfs=wfs, wfsf=wfsf)
                    # plt.show()
                    sys.exit()


if __name__ == "__main__":
    print("Analyzing all test items...")
    rootpath = '../Data_BNL_CE_WIB_SW_QC'
    datadir = 'FE_004003138_004003139_004003140_004003145_004003157_004003146_004003147_004003148'
    qc = DAT_LArASIC_QC_ana(rootpath=rootpath, datadir=datadir)
    qc.printTestItems()
    # qc.doQC_all()
    qc.Init_checkout()