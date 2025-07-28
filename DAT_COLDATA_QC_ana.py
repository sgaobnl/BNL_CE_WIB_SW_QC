import time
import os
import sys
import numpy as np
import pickle
import copy
import time, datetime
from spymemory_decode import wib_dec
#from spymemory_decode import avg_aligned_by_ts
import statsmodels.api as sm
import colorama
from colorama import Fore, Back
colorama.init(autoreset=True)


class CD_QC_ANA():
    def __init__(self):
        #self.AD_LSB = 2564/4096 
        self.qc_stats = {}
        self.env="RT"

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
    
    
    def plt_log(self, plt,fig, logsd, onekey, data):
        fig.suptitle("Test Result of " + onekey, weight ="bold", fontsize = 12)
        lkeys = list(logsd)
        keys_tmp = ['date', 'tester', 'testsite', 'env', 'CD0', 'CD1']
        for i in range(len(keys_tmp)):
            loginfo ="{} : {}".format(keys_tmp[i], data["logs"][keys_tmp[i]])
            if i == 0:
                x = 0.05
            elif i == 1:
                x = 0.30 
            else:
                x = 0.25 + 0.15*(i-1)
            y = 0.92
            fig.text(x, y, loginfo, fontsize=10)
    
    #Todo change default V & C ranges
    #def ana_cdpwr(self, pwr_meas, vddfe =[1.7, 1.9], v1p1 = [1.0, 1.2], vddio = [2.15, 2.35], cdda = [8.5, 9.5], cddfe = [0, 0.1], cddcore = [9, 11], cddd = [21, 23], cddio = [66, 69]):
    def ana_cdpwr(self, pwr_meas, vddfe = [1.7, 1.9], v1p1 = [1.15, 1.25], vddio = [2.15, 2.35], cdda = [7, 11], cddfe = [-1, 1], cddcore = [8, 13], cddd = [20, 25], cddio = [60, 75]):
        kpwrs = list(pwr_meas.keys())
    
        vddas = []
        fe_vddas = []
        vddcores = []
        vddds = []
        vddios = []
    
        cddas = []
        fe_cddas = []
        cddcores = []
        cddds = []
        cddios = []
        
        for i in range(len(kpwrs)):      
            if "CD_VDDA" in kpwrs[i]:
                vddas.append(pwr_meas[kpwrs[i]][0])
                cddas.append(pwr_meas[kpwrs[i]][1])
            if "FE_VDDA" in kpwrs[i]:
                fe_vddas.append(pwr_meas[kpwrs[i]][0])
                fe_cddas.append(pwr_meas[kpwrs[i]][1]) 
            if "VDDCORE" in kpwrs[i]:
                vddcores.append(pwr_meas[kpwrs[i]][0])
                cddcores.append(pwr_meas[kpwrs[i]][1])
            if "VDDD" in kpwrs[i]:
                vddds.append(pwr_meas[kpwrs[i]][0])
                cddds.append(pwr_meas[kpwrs[i]][1])        
            if "VDDIO" in kpwrs[i]:
                vddios.append(pwr_meas[kpwrs[i]][0])
                cddios.append(pwr_meas[kpwrs[i]][1])
        #    print (kpwrs[i], pwr_meas[kpwrs[i]][0], pwr_meas[kpwrs[i]][1])
      
        pass_flg = False
        if all(v1p1[0] <= item <= v1p1[1] for item in vddas) and all(cdda[0] <= item <= cdda[1] for item in cddas) :
            if all(vddfe[0] <= item <= vddfe[1] for item in fe_vddas) and all(cddfe[0] <= item <= cddfe[1] for item in fe_cddas) :
                if all(v1p1[0] <= item <= v1p1[1] for item in vddcores) and all(cddcore[0] <= item <= cddcore[1] for item in cddcores) :
                    if all(v1p1[0] <= item <= v1p1[1] for item in vddds) and all(cddd[0] <= item <= cddd[1] for item in cddds) :
                        if all(vddio[0] <= item <= vddio[1] for item in vddios) and all(cddio[0] <= item <= cddio[1] for item in cddios) : 
                            pass_flg = True
        return pass_flg
    
    
    def plt_cdpwr(self, plt, pwr_meas):
        kpwrs = list(pwr_meas.keys())
        ax5 = plt.subplot2grid((2, 3), (0, 0), colspan=1, rowspan=1)
        ax6 = plt.subplot2grid((2, 3), (1, 0), colspan=1, rowspan=1)
    
        vddas = []
        fe_vddas = []
        vddcores = []
        vddds = []
        vddios = []
    
        cddas = []
        fe_cddas = []
        cddcores = []
        cddds = []
        cddios = []
        
        for i in range(len(kpwrs)):      
            if "CD_VDDA" in kpwrs[i]:
                vddas.append(pwr_meas[kpwrs[i]][0])
                cddas.append(pwr_meas[kpwrs[i]][1])
            if "FE_VDDA" in kpwrs[i]:
                fe_vddas.append(pwr_meas[kpwrs[i]][0])
                fe_cddas.append(pwr_meas[kpwrs[i]][1]) 
            if "VDDCORE" in kpwrs[i]:
                vddcores.append(pwr_meas[kpwrs[i]][0])
                cddcores.append(pwr_meas[kpwrs[i]][1])
            if "VDDD" in kpwrs[i]:
                vddds.append(pwr_meas[kpwrs[i]][0])
                cddds.append(pwr_meas[kpwrs[i]][1])        
            if "VDDIO" in kpwrs[i]:
                vddios.append(pwr_meas[kpwrs[i]][0])
                cddios.append(pwr_meas[kpwrs[i]][1]) 
    
        # adc=[0,1,2,3,4,5,6,7]
        cd=[0,1]
        import matplotlib.ticker as ticker
        
        ax5.scatter(cd, vddas, color='b', marker = 'o', label="CD_VDDA")
        ax5.scatter(cd, fe_vddas, color='r', marker = 'o', label="FE_VDDA")
        ax5.scatter(cd, vddcores, color='g', marker = 'o', label="VDDCORE")
        ax5.scatter(cd, vddds, color='c', marker = 'o', label="VDDD")
        ax5.scatter(cd, vddios, color='m', marker = 'o', label="VDDIO")
        ax5.set_title("Voltage Measurement", fontsize=8)
        ax5.get_xaxis().set_major_locator(ticker.MultipleLocator(1))
        ax5.set_ylabel("Voltage (V)", fontsize=8)
        ax5.set_xlim((-0.5,1.5))
        ax5.set_ylim((0,3))
        ax5.set_xlabel("CD no", fontsize=8)
        ax5.grid()
        ax5.legend()
    
        ax6.scatter(cd, cddas, color='b', marker = 'o', label='CD_VDDA')
        ax6.scatter(cd, fe_cddas, color='r', marker = 'o', label='FE_VDDA')
        ax6.scatter(cd, cddcores, color='g', marker = 'o', label='VDDCORE')
        ax6.scatter(cd, cddds, color='c', marker = 'o', label='VDDD')
        ax6.scatter(cd, cddios, color='m', marker = 'o', label='VDDIO') 
        ax6.get_xaxis().set_major_locator(ticker.MultipleLocator(1))
        ax6.set_title("Current Measurement", fontsize=8)
        ax6.set_ylabel("Current (mA)", fontsize=8)
        ax6.set_xlim((-0.5,1.5))
        ax6.set_ylim((-10,200))
        ax6.set_xlabel("CD no", fontsize=8)
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
        return chns, rmss, peds, pkps, pkns, wfs,wfsf
    
    def ana_res(self, fembs, rawdata, par=[7000,10000], rmsr=[5,25], pedr=[500,3000] ):
        chns, rmss, peds, pkps, pkns, wfs, wfsf = self.data_ana(fembs, rawdata)
        fail_flg=True
        amps = np.array(pkps) - np.array(peds)
        if all(item > par[0] for item in amps) and all(item < par[1] for item in amps) :
            if all(item > rmsr[0] for item in rmss) and all(item < rmsr[1] for item in rmss) :
                if all(item > pedr[0] for item in peds) and all(item < pedr[1] for item in peds) :
                    fail_flg = False
        return fail_flg
    
    
    def plt_subplot(self, plt, fembs, rawdata ):
        ax1 = plt.subplot2grid((2, 3), (0, 1), colspan=1, rowspan=1)
        ax2 = plt.subplot2grid((2, 3), (0, 2), colspan=1, rowspan=1)
        ax3 = plt.subplot2grid((2, 3), (1, 1), colspan=1, rowspan=1)
        ax4 = plt.subplot2grid((2, 3), (1, 2), colspan=1, rowspan=1)
    
        chns, rmss, peds, pkps, pkns, wfs, wfsf = self.data_ana(fembs, rawdata)
    
    #    wibdata = wib_dec(rawdata,fembs, spy_num=1)
    #    datd = [wibdata[0], wibdata[1],wibdata[2],wibdata[3]][fembs[0]]
    #
    #    chns =[]
    #    rmss = []
    #    peds = []
    #    pkps = []
    #    pkns = []
    #    wfs = []
    #
    #    ppos=0
    #    npos=0
    #    for achn in range(len(datd)):
    #        chndata = datd[achn]
    #        amax = np.max(chndata[300:])
    #        amin = np.min(chndata[300:])
    #        if achn==0:
    #            ppos = np.where(chndata==amax)[0][0]
    #            npos = np.where(chndata==amin)[0][0]
    #        aped = int(np.mean(chndata[ppos-150:ppos-50]))
    #
    #        arms = np.std(chndata[ppos-150:ppos-50])
    #        chns.append(achn)
    #        rmss.append(arms)
    #        peds.append(aped)
    #        pkps.append(amax)
    #        pkns.append(amin)
    #        wfs.append(chndata[ppos-50:ppos+150])
    #        ax1.plot(chndata[ppos-20:ppos+20])
    #        ax2.plot(chndata[npos-20:npos+20])
    
        for chn in chns:
            ax1.plot(wfs[chn][30:70], marker='.')
            ax2.plot(wfsf[chn], color="C%d"%(chn//64+1))
        ax1.set_title("Overlap waveforms", fontsize=8)
        ax1.set_ylabel("Amplitude / bit", fontsize=8)
        ax1.set_xlabel("Time", fontsize=8)
        ax2.set_title("Overlap waveforms", fontsize=8)
        ax2.set_ylabel("Amplitude / bit", fontsize=8)
        ax2.set_xlabel("Time", fontsize=8)
    
        for i in range(0,128,16):
            ax3.vlines(i-0.5, 0, (np.max(pkps)//1000+1)*1000, color='y')
            ax4.vlines(i-0.5, 0, 50, color='y')
    
        ax3.plot(chns, pkps, color='r', marker='.')
        ax3.plot(chns, peds, color='b', marker='.')
        ax3.plot(chns, pkns, color='m', marker='.')
        ax3.set_title("Pulse Response Distribution", fontsize=8)
        ax3.set_xlabel("CH number", fontsize=8)
        ax3.set_ylabel("Amplitude /bit", fontsize=8)
    
        ax4.plot(chns,rmss, color='r', marker='.')
        ax4.set_title("Noise", fontsize=8)
        ax4.set_xlabel("CH number", fontsize=8)
        ax4.set_ylabel("Amplitude / bit", fontsize=8)
        ax1.grid()
        ax2.grid()
    
    def dat_cd_qc_ana(self, fdir="/.", tms=[0,1,2,3,4,5,6,7]):
        if 0 in tms:
            print ("-------------------------------------------------------------------------")
            print ("0: Initilization checkout")
            fp = fdir + "QC_INIT_CHK" + ".bin"
        
            with open(fp, 'rb') as fn:
                data = pickle.load( fn)
            
            dkeys = list(data.keys())
            for key in dkeys:
                print (key, data[key])
            
            logsd = data["logs"]
            dkeys.remove("logs")
            
            for onekey in dkeys:
                if ("DIRECT_PLS_CHK" in onekey) or ("ASICDAC_CALI_CHK" in onekey):
                    cfgdata = data[onekey]
                    fembs = cfgdata[0]
                    rawdata = cfgdata[1]
                    cfg_info = cfgdata[2]
                    pwr_meas = cfgdata[5]

                    if ("DIRECT_PLS_CHK" in onekey) :
                        failflg = self.ana_res(fembs, rawdata, par=[4000,10000], rmsr=[2,25], pedr=[200,3000] )
                    if ("ASICDAC_CALI_CHK" in onekey):
                        failflg = self.ana_res(fembs, rawdata, par=[6000,10000], rmsr=[2,25], pedr=[200,3000] )

                    if True:
                        import matplotlib.pyplot as plt
                        plt.rcParams.update({'font.size': 8})
                        fig = plt.figure(figsize=(12,8))
                        self.plt_log(plt,fig, logsd, onekey, data)
                        self.plt_cdpwr(plt, pwr_meas)
                        self.plt_subplot(plt, fembs, rawdata)
                        plt.tight_layout( rect=[0.05, 0.05, 0.95, 0.95])
                        plt.plot()
                        #plt.show()
                        plt.savefig( fp[0:-4] + "_" + onekey + ".png")
                        plt.close()
    
                    if not failflg:
                        print (Fore.GREEN + onekey + "  : PASS")
                        self.qc_stats[onekey] ="PASS"
                    else:
                        print(Fore.RED + onekey + " : Fail")
                        self.qc_stats[onekey] ="Fail"
                        #break
            print ("#########################################################################")
    
    
        if 1 in tms:
            print ("-------------------------------------------------------------------------")
            print ("1: COLDATA basic functionality checkout  ")
            print ("command on WIB terminal to retake data for this test item is as bellow :")
            fp = fdir + "QC_BASIC_FUNC" + ".bin"
            if os.path.isfile(fp):
                with open(fp, 'rb') as fn:
                    data = pickle.load( fn)
            
                dkeys = list(data.keys())
                
                logsd = data["logs"]
                dkeys.remove("logs")
            else:
                print(Fore.RED + fp + " not found.")
                exit()
                
            for onekey in dkeys:
                if "Post-Hard_Reset" in onekey: 
                    rstdata = data[onekey]
                    hasError = rstdata[1]
                elif "Post-Soft_Reset" in onekey: 
                    rstdata = data[onekey]
                    hasError = rstdata[1]
                    if hasError:
                        print(Fore.RED + onekey + " : Fail")
                elif "FAST_CMD_Reset" in onekey: 
                    rstdata = data[onekey]
                    hasError = rstdata[1]
                    if hasError:
                        print(Fore.RED + onekey + " check Fail")
                elif "CD0_GPIO" in onekey: 
                    rstdata = data[onekey]
                    if "PASS" in rstdata[1]:
                        hasError = False
                    else:
                        hasError = True
                elif "CD1_GPIO" in onekey: 
                    rstdata = data[onekey]
                    if "PASS" in rstdata[1]:
                        hasError = False
                    else:
                        hasError = True
                elif "SPI_config" in onekey: 
                    hasError = not data[onekey]
                else:
                    hasError = True
    
                if hasError:
                    print(Fore.RED + onekey + " : Fail")
                    self.qc_stats[onekey] ="Fail"
                else:
                    print (Fore.GREEN + onekey + "  : PASS")
                    self.qc_stats[onekey] ="PASS"
    
    
        if 2 in tms:
            print ("-------------------------------------------------------------------------")
            print ("2: COLDATA primary/secondary swap check  ")
            fp = fdir + "QC_SWAP" + ".bin"
            if os.path.isfile(fp):
                with open(fp, 'rb') as fn:
                    data = pickle.load( fn)
            
                dkeys = list(data.keys())
                
                logsd = data["logs"]
                dkeys.remove("logs")
            else:
                print(Fore.RED + fp + " not found.")
                exit()
                
            for onekey in dkeys:
                if "LVDS" in onekey or "CMOS" in onekey or  "ADCs" in onekey:
                    i2cerror = data[onekey]
                    if i2cerror:
                        print(Fore.RED + onekey + " : Fail")
                        self.qc_stats[onekey] ="Fail"
                    else:
                        print (Fore.GREEN + onekey + "  : PASS")
                        self.qc_stats[onekey] ="PASS"
                if "Data" in onekey:
                    cfgdata = data[onekey]
                    fembs = cfgdata[0]
                    rawdata = cfgdata[1]
                    chns, rmss, peds, pkps, pkns, wfs, wfsf = self.data_ana(fembs, rawdata)
                    if True:
                        import matplotlib.pyplot as plt
                        plt.rcParams.update({'font.size': 8})
                        fig = plt.figure(figsize=(12,8))
                        self.plt_log(plt,fig, logsd, onekey, data)
                        self.plt_subplot(plt, fembs, rawdata)
                        plt.tight_layout( rect=[0.05, 0.05, 0.95, 0.95])
                        plt.plot()
                        #plt.show()
                        plt.savefig( fp[0:-4] + "_" + onekey + ".png")
                        plt.close()
    
    
                    if "U1" in onekey:
                        for chn in chns:
                            chip = chn//16
                            if chip == 0:
                                data_pass = peds[chn] == 0x204
                            elif chip == 1:     
                                data_pass = peds[chn] == 0x245
                            elif chip == 2:     
                                data_pass = peds[chn] == 0x286
                            elif chip == 3:     
                                data_pass = peds[chn] == 0x2c7
                            elif chip == 4:     
                                data_pass = peds[chn] == 0x100
                            elif chip == 5:     
                                data_pass = peds[chn] == 0x141
                            elif chip == 6:     
                                data_pass = peds[chn] == 0x182
                            elif chip == 7:     
                                data_pass = peds[chn] == 0x1c3
                    elif "U2" in onekey:        
                        for chn in chns:        
                            chip = chn//16      
                            if chip == 0:       
                                data_pass = peds[chn] == 0x100
                            elif chip == 1:     
                                data_pass = peds[chn] == 0x141
                            elif chip == 2:     
                                data_pass = peds[chn] == 0x182
                            elif chip == 3:     
                                data_pass = peds[chn] == 0x1c3
                            elif chip == 4:     
                                data_pass = peds[chn] == 0x204
                            elif chip == 5:     
                                data_pass = peds[chn] == 0x245
                            elif chip == 6:     
                                data_pass = peds[chn] == 0x286
                            elif chip == 7:     
                                data_pass = peds[chn] == 0x2c7
                    if data_pass:
                        print (Fore.GREEN + onekey + "  : PASS")
                        self.qc_stats[onekey] ="PASS"
                    else:
                        print(Fore.RED + onekey + " : Fail")
                        self.qc_stats[onekey] ="Fail"
                      
        if 3 in tms:
            print ("-------------------------------------------------------------------------")
            print ("3: COLDATA power cycling measurement  ")
            fp = fdir + "QC_PWR_CYCLE" + ".bin"
            if os.path.isfile(fp):
                with open(fp, 'rb') as fn:
                    data = pickle.load( fn)
            
                dkeys = list(data.keys())
                
                logsd = data["logs"]
                dkeys.remove("logs")
            else:
                print(Fore.RED + fp + " not found.")
                exit()
                
            for onekey in dkeys:
                cfgdata = data[onekey]
                fembs = cfgdata[0]
                rawdata = cfgdata[1]
                pwr_meas = cfgdata[5]
    
    
                if "RT" in self.env:
                    cdda = [7, 11] 
                    rmsr=[5,25]
                    pedr=[7000,10000]

                else:
                    cdda = [5, 9]
                    rmsr=[2,35]
                    pedr=[7000,10000]

                if "CUR_0x0" in onekey:
                    pass_flg = self.ana_cdpwr(pwr_meas, cdda =cdda, cddio = [25, 35])
                elif "CUR_0x2" in onekey :
                    pass_flg = self.ana_cdpwr(pwr_meas, cdda =cdda, cddio = [35, 50])
                else:
                    pass_flg = self.ana_cdpwr(pwr_meas, cdda =cdda, cddio = [60, 75])



                if pass_flg:
                    print (Fore.GREEN + onekey + " Power Consumption: PASS")
                    self.qc_stats[onekey+"_Power"] ="PASS"
                else:
                    print(Fore.RED + onekey + " Power Consumption: Fail")
                    self.qc_stats[onekey+"_Power"] ="Fail"
    
                chns, rmss, peds, pkps, pkns, wfs, wfsf = self.data_ana(fembs, rawdata)
                failflg = self.ana_res(fembs, rawdata, par=[2500,5000], rmsr=rmsr, pedr=pedr )
                
                if failflg:
                    print(Fore.RED + onekey + " Pulse Response: Fail")
                    self.qc_stats[onekey+"_PLS"] ="Fail"
                else:
                    print (Fore.GREEN + onekey + " Pulse Response: PASS")
                    self.qc_stats[onekey+"_PLS"] ="PASS"
       
                if True:
                    import matplotlib.pyplot as plt
                    plt.rcParams.update({'font.size': 8})
                    fig = plt.figure(figsize=(12,8))
                    self.plt_log(plt,fig, logsd, onekey, data)
                    self.plt_cdpwr(plt, pwr_meas)
                    self.plt_subplot(plt, fembs, rawdata)
                    plt.tight_layout( rect=[0.05, 0.05, 0.95, 0.95])
                    plt.plot()
                    plt.savefig( fp[0:-4] + "_" + onekey + ".png")
                    plt.close()
    
            print ("#########################################################################")   
        
        if 4 in tms:
            print ("-------------------------------------------------------------------------")
            print ("4: COLDATA PLL lock range measurement  ")
            fp = fdir + "QC_LOCK" + ".bin"
            if os.path.isfile(fp):
                with open(fp, 'rb') as fn:
                    data = pickle.load( fn)
                dkeys = list(data.keys())
                logsd = data["logs"]
                dkeys.remove("logs")
            else:
                print(Fore.RED + fp + " not found.")
                exit()
            
            pllbands = np.arange(0x00,0x40,1)
            if "RT" in self.env:
                pllbands_pass = np.arange(0x1d+2,0x2b,1)
            else:
                pllbands_pass = np.arange(0x1d+3,0x2b-3,1)

                    
            cd1monvs = []
            cd2monvs = []
            datachks = []
            cd1monvs = data['CD1_locked']
            cd2monvs = data['CD2_locked']

    
            for pllband in pllbands:
                fembs=[0]
                rawdata = data['CD_data'][pllband]
                if rawdata != False:
                    chns, rmss, peds, pkps, pkns, wfs, wfsf = self.data_ana(fembs, rawdata)
                    for chn in chns:
                        if chn%16 < 8:
                            pass_flg = (peds[chn] == 0x2af3)
                        else:
                            pass_flg = (peds[chn] == 0x48d)
                        if not pass_flg:
                            datachks.append(0) #False
                            break
                    if pass_flg:
                        datachks.append(1)
                else:
                    datachks.append(0) #False
    
            cd1v_avg = np.mean(cd1monvs[pllbands_pass[0]: pllbands_pass[-1]])
            cd1v_std = np.std(cd1monvs[pllbands_pass[0]: pllbands_pass[-1]])
            cd2v_avg = np.mean(cd2monvs[pllbands_pass[0]: pllbands_pass[-1]])
            cd2v_std = np.std(cd2monvs[pllbands_pass[0]: pllbands_pass[-1]])
    
            for pllband in pllbands_pass:
                if datachks[pllband] == 0: 
                    pass_flg = False
                if (cd1monvs[pllband] > cd1v_avg + 10) or (cd1monvs[pllband] < cd1v_avg - 10): 
                    pass_flg = False
                if (cd2monvs[pllband] > cd2v_avg + 10) or (cd2monvs[pllband] < cd2v_avg - 10) :
                    pass_flg = False
                if cd1v_std > 10:
                    pass_flg = False
                if cd2v_std > 10:
                    pass_flg = False
                if not pass_flg:
                    break
    
            onekey = "PLL_Locked"
            if pass_flg:
                print (Fore.GREEN + onekey + ": PASS")
                self.qc_stats[onekey] ="PASS"
            else:
                print(Fore.RED + onekey + ": Fail")
                self.qc_stats[onekey] ="Fail"

            import matplotlib.pyplot as plt
    
            plt.rcParams.update({'font.size': 12})
            fig = plt.figure(figsize=(12,8))
            self.plt_log(plt,fig, logsd, onekey, data)
            ymin = (np.min(cd1monvs)//100-1)*100
            ymax = (np.max(cd1monvs)//100 + 2)*100
            plt.vlines(pllbands_pass[0], ymin, ymax, color="C5",  linestyle='--', label="0x%x pass_min"%pllbands_pass[0])
            plt.vlines(pllbands_pass[-1], ymin, ymax, color="C5",linestyle='--',  label="0x%x pass_max"%pllbands_pass[-1])
            plt.vlines(0x20, ymin, ymax, color = "C2",linestyle='--',  label="0x20 default")
            plt.vlines(0x25, ymin, ymax, color = "C3",linestyle='--',  label="0x25 mid point for warm")
            plt.vlines(0x26, ymin, ymax, color = "C4",linestyle='--',  label="0x26 mid point for cold")
            plt.plot(pllbands, cd1monvs)
            plt.plot(pllbands, cd2monvs)
            plt.ylabel("Voltage (V) of Lock", fontsize=12)
            plt.xlabel("REG_CONFIG_PLL_BAND", fontsize=12)
            plt.ylim((ymin, ymax))
            plt.xlim((-1,70))
            plt.grid()
            plt.legend()

            #plt.show()
            plt.savefig( fp[0:-4] + "_" + "PLL_LOCK" + ".png")
            plt.close()
    
        
        if 5 in tms:
            print ("-------------------------------------------------------------------------")
            print ("5: COLDATA fast command verification  ")
            fp = fdir + "QC_FASTCMD" + ".bin"
            if os.path.isfile(fp):
                with open(fp, 'rb') as fn:
                    data = pickle.load( fn)
            
                dkeys = list(data.keys())
                
                logsd = data["logs"]
                dkeys.remove("logs")
            else:
                print(Fore.RED + fp + " not found.")
                exit()
    
            pass_flg = True
            for onekey in ['FC_ACT_Pre_EDGE_SYNC','FC_ACT_Post_EDGE_SYNC','FC_ACT_Post_EDGE_SYNC_IDLE','FC_ACT_CLR_SAVES','FC_ACT_SAVE_STATUS',  'FC_ACT_rst_adcs' ]:
                if "PASS" not in data[onekey]:
                    pass_flg = False
                    print(Fore.RED + onekey + " : Fail")
                    self.qc_stats[onekey] ="FAIL"
                else:
                    print (Fore.GREEN + onekey + "  : PASS")
                    self.qc_stats[onekey] ="PASS"
    
            cfgdata = data["FC_ACT_RST_LARASIC_Before"] #200mV, pulsed
            fembs = cfgdata[0]
            rawdata = cfgdata[1]
            chns, rmss, peds_p, pkps_p, pkns, wfs, wfsf = self.data_ana(fembs, rawdata)
            pamps_p = np.array(pkps_p) - np.array(peds_p)
    
            cfgdata = data["FC_ACT_RST_LARASIC_After"] #900mV, RMS data
            fembs = cfgdata[0]
            rawdata = cfgdata[1]
            chns, rmss, peds_a, pkps_a, pkns, wfs, wfsf = self.data_ana(fembs, rawdata)
    
            pamps_a = np.array(pkps_a) - np.array(peds_a)
    
            for chn in chns:
                if (peds_p[chn] < 4000) and (pamps_p[chn] > 5000) and (peds_a[chn] > 6000) and (pamps_a[chn] < 3000): 
                    if chn == chns[-1]:
                        print (Fore.GREEN + "FC_ACT_RST_LARASIC" + "  : PASS")
                else:
                    #print (chn, peds_p[chn] , pamps_p[chn], peds_a[chn], pamps_a[chn])
                    print(Fore.RED + "FC_ACT_RST_LARASIC" + " : Fail")
                    pass_flg = False
                    break
            if pass_flg:
                self.qc_stats[onekey] ="PASS"
            else:
                self.qc_stats[onekey] ="FAIL"
    
            cfgdata = data["FC_ACT_RST_LARASIC_SPI_Before"] #200mV, pulsed
            fembs = cfgdata[0]
            rawdata = cfgdata[1]
            chns, rmss, peds_p, pkps_p, pkns, wfs, wfsf = self.data_ana(fembs, rawdata)
            pamps_p = np.array(pkps_p) - np.array(peds_p)
    
            cfgdata = data["FC_ACT_RST_LARASIC_SPI_DIS"] #200mV, RMS data
            fembs = cfgdata[0]
            rawdata = cfgdata[1]
            chns, rmss, peds_d, pkps_d, pkns, wfs, wfsf = self.data_ana(fembs, rawdata)
            pamps_d = np.array(pkps_d) - np.array(peds_d)
    
            cfgdata = data["FC_ACT_RST_LARASIC_SPI_After"] #900mV
            fembs = cfgdata[0]
            rawdata = cfgdata[1]
            chns, rmss, peds_a, pkps_a, pkns, wfs, wfsf = self.data_ana(fembs, rawdata)
            pamps_a = np.array(pkps_a) - np.array(peds_a)
    
            for chn in chns:
                if (peds_p[chn] < 4000) and (pamps_p[chn] > 5000) and (peds_d[chn] < 4000) and (pamps_d[chn] < 3000) and (peds_a[chn] > 6000) and (pamps_a[chn] < 3000): 
                    if chn == chns[-1]:
                        print (Fore.GREEN + "FC_ACT_RST_LARASIC" + "  : PASS")
                else:
                    #print (chn, peds_p[chn] , pamps_p[chn], peds_a[chn], pamps_a[chn])
                    print(Fore.RED + "FC_ACT_RST_LARASIC_SPI" + " : Fail")
                    pass_flg = False
                    break
            if pass_flg:
                self.qc_stats[onekey] ="PASS"
            else:
                self.qc_stats[onekey] ="FAIL"

    
        if 6 in tms:
            print ("-------------------------------------------------------------------------")
            print ("6: COLDATA output link verification  ")
            fp = fdir + "QC_LVDS_Curs" + ".bin"
            if os.path.isfile(fp):
                with open(fp, 'rb') as fn:
                    data = pickle.load( fn)
                dkeys = list(data.keys())
                logsd = data["logs"]
                dkeys.remove("logs")
            else:
                print(Fore.RED + fp + " not found.")
                exit()
            
            if 'ADC_pattern_LVDS_CUR_ERROR' in dkeys:
                print(Fore.RED + 'ADC_pattern_LVDS_CUR_ERROR' + " : Fail")
                pass_flg = False
            else:
                pass_flg = True
                for curi in range(0x8):
                    onekey = 'ADC_pattern_LVDS_CUR_%d'%curi
                    fembs = data[onekey][0]
                    rawdata = data[onekey][1]
                    pwr_meas =  data[onekey][3]
                    if "RT" in self.env:
                        cdda = [7, 11] 
                        rmsr=[5,25]
                        pedr=[7000,10000]
                    else:
                        cdda = [5, 9]
                        rmsr=[2,35]
                        pedr=[7000,10000]
   
   
                    if "CUR_0" in onekey:
                        pass_flg = self.ana_cdpwr(pwr_meas, cdda=cdda, cddio = [25, 35])
                    elif "CUR_1" in onekey:
                        pass_flg = self.ana_cdpwr(pwr_meas, cdda=cdda, cddio = [35, 50])
                    elif "CUR_2" in onekey:
                        pass_flg = self.ana_cdpwr(pwr_meas, cdda=cdda, cddio = [35, 50])
                    elif "CUR_3" in onekey:
                        pass_flg = self.ana_cdpwr(pwr_meas, cdda=cdda, cddio = [50, 65])
                    elif "CUR_4" in onekey:
                        pass_flg = self.ana_cdpwr(pwr_meas, cdda=cdda, cddio = [35, 50])
                    elif "CUR_5" in onekey:
                        pass_flg = self.ana_cdpwr(pwr_meas, cdda=cdda, cddio = [50, 65])
                    elif "CUR_6" in onekey:
                        pass_flg = self.ana_cdpwr(pwr_meas, cdda=cdda, cddio = [50, 65])
                    else:
                        pass_flg = self.ana_cdpwr(pwr_meas, cdda=cdda, cddio = [60, 75])


                    if pass_flg:
                        print (Fore.GREEN + onekey + " Power Consumption: PASS")
                        self.qc_stats[onekey] ="PASS"
                    else:
                        print(Fore.RED + onekey + " Power Consumption: Fail")
                        self.qc_stats[onekey] ="FAIL"

                    chns, rmss, peds, pkps, pkns, wfs, wfsf = self.data_ana(fembs, rawdata)

                    for chn in chns:
                        if chn%16 < 8:
                            pass_flg = peds[chn] == 0x2af3
                        else:
                            pass_flg = peds[chn] == 0x48d
                        if not pass_flg:
                            break
    
                    if pass_flg:
                        print (Fore.GREEN + onekey + " Pulse Response: PASS")
                        self.qc_stats[onekey] ="PASS"
                    else:
                        print(Fore.RED + onekey + " Pulse Response: Fail")
                        self.qc_stats[onekey] ="FAIL"
       
                    if True:
                        import matplotlib.pyplot as plt
                        plt.rcParams.update({'font.size': 8})
                        fig = plt.figure(figsize=(12,8))
                        self.plt_log(plt,fig, logsd, onekey, data)
                        self.plt_cdpwr(plt, pwr_meas)
                        self.plt_subplot(plt, fembs, rawdata)
                        plt.tight_layout( rect=[0.05, 0.05, 0.95, 0.95])
                        plt.plot()
                        plt.savefig( fp[0:-4] + "_" + onekey + ".png")
                        plt.close()
    
        if 7 in tms:
            print ("-------------------------------------------------------------------------")
            print ("7: COLDATA EFUSE burn-in  ")
            fp = fdir + "QC_EFUSE" + ".bin"
            if os.path.isfile(fp):
                with open(fp, 'rb') as fn:
                    data = pickle.load( fn)
            
                dkeys = list(data.keys())
                
                logsd = data["logs"]
                dkeys.remove("logs")
            else:
                print(Fore.RED + fp + " not found.")
                exit()
                
            for onekey in dkeys:
                if "CD" in onekey:
                    efusedata = data[onekey]
                    val = efusedata[0]
                    readout = efusedata[1]
                    print(onekey,"programmed with",val,", reads out",readout)
                    if (readout & 0x7fffffff) == val: 
                        print (Fore.GREEN + onekey + "  : PASS")
                        self.qc_stats[onekey] ="PASS. Programmed %d, reads out %d"%(val,readout)
                    else:
                        print(Fore.RED + onekey+": Fail")
                        self.qc_stats[onekey] ="FAIL. Programmed %d, reads out %d"%(val,readout)


if __name__=="__main__":
    #fsubdir = "RT_CD_060592417_060542417"
    #fsubdir = "RT_CD_000000003_000000006"
    #froot = "D:\\DAT_CD_QC\\Tested\\Time_20241015203556_DUT_1000_2000\\"
    #fdir = froot + fsubdir + "\\"

    fdir = """D:\DAT_CD_QC\RT_CD_031672417_031862417/"""
    fdir = '''D:\DAT_SN_data\SN1\Time_20250103160419_DUT_1000_2000\RT_CD_060602417_060562417/'''
    fdir = '''D:\DAT_CD_QC\Tested\Time_20250109200316_DUT_1000_2000\RT_CD_031702417_031722417/'''
    fdir = '''C:\SGAO\ColdTest\Tested\DAT_CD_QC\Tested\Time_20250508183918_DUT_1000_2000\RT_CD_000000001_000000002/'''
    fdir = '''E:/tmp/'''


    evl = input ("Analyze all test items? (Y/N) : " )
    if ("Y" in evl) or ("y" in evl):
        tms = [0, 1, 2,3,4,5,6,7 ]
        pass
    else:
        print ("\033[93m  QC task list   \033[0m")
        print ("\033[96m 0: Initilization checkout (not selectable for itemized test item) \033[0m")
        print ("\033[96m 1: COLDATA basic functionality checkout  \033[0m")
        print ("\033[96m 2: COLDATA primary/secondary swap check  \033[0m")
        print ("\033[96m 3: COLDATA power consumption measurement  \033[0m")
        print ("\033[96m 4: COLDATA PLL lock range measurement  \033[0m")
        print ("\033[96m 5: COLDATA fast command verification  \033[0m")
        print ("\033[96m 6: COLDATA output link verification \033[0m")
        print ("\033[96m 7: COLDATA EFUSE burn-in \033[0m")
        print ("\033[96m 9: Turn DAT on \033[0m")
        print ("\033[96m 10: Turn DAT (on WIB slot0) on without any check\033[0m")
    
        while True:
            testnostr = input ("Please input a number (0, 1, 2, 3, 4, 5, 6, 7) for one test item: " )
            try:
                testno = int(testnostr)
                tms = [testno]
                break
            except ValueError:
                print ("Wrong value, please re-enter...")
    

    qc = CD_QC_ANA()
    qc.env = "LN"
    qc.dat_cd_qc_ana(fdir=fdir, tms=tms)
    print (qc.qc_stats)

