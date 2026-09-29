import os
import sys
import numpy as np
import pickle
from spymemory_decode import wib_dec
from highpass_filter import hp_flt_applied

def data_ana(fembs, rawdata, rms_flg=False):
    wibdata = wib_dec(rawdata,fembs, spy_num=2, cd0cd1sync=False)[0]
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
        chndata = np.array(datd[achn])-np.mean(datd[achn]) + 20
        chndata_hf = hp_flt_applied(chndata, fs=1953125, passfreq=10000)
        print ("%03d, %03.3f, %03.3f, %03.3f"%(achn, np.std(chndata), np.std(chndata_hf), (np.std(chndata)- np.std(chndata_hf))))
        #import matplotlib.pyplot as plt
        #plt.plot(chndata, label="%d"%achn)
        #plt.plot(chndata_hf)
        #plt.legend()
        #plt.show()
        #plt.close()



def dat_larasic_qc_rms_ana(fdir="/."):

    if True:
        fp = fdir + "QC_RMS" + ".bin"
        with open(fp, 'rb') as fn:
            data = pickle.load( fn)
        
        dkeys = list(data.keys())
        
        logsd = data["logs"]
        dkeys.remove("logs")
    
      
        for st0 in [0, 1]:
            for st1 in [0, 1]:
                for onekey in dkeys:
                    if "RMS_SDD0_SDF0_SLK00_SLK10_SNC0_ST0%d_ST1%d_SG00_SG10"%(st0, st1) in onekey:
                        print (onekey)
                        cfgdata = data[onekey]
                        fembs = cfgdata[0]
                        rawdata = cfgdata[1]
                        cfg_info = cfgdata[2]
                        chns, rmss, peds, pkps, pkns, wfs, wfsf = data_ana(fembs, rawdata, rms_flg=True)
    
    
      
        for st0 in [0, 1]:
            for st1 in [0, 1]:
                for onekey in dkeys:
                    if "RMS_SDD0_SDF0_SLK00_SLK10_SNC1_ST0%d_ST1%d_SG00_SG10"%(st0, st1) in onekey:
                        print (onekey)
                        cfgdata = data[onekey]
                        fembs = cfgdata[0]
                        rawdata = cfgdata[1]
                        cfg_info = cfgdata[2]
                        chns, rmss, peds, pkps, pkns, wfs, wfsf = data_ana(fembs, rawdata, rms_flg=True)
    
    
        for snc in [0, 1]:
            for buf in [0, 1, 2]:
                sdd = buf//2
                sdf=buf%2
                for onekey in dkeys:
                    if "RMS_OUTPUT_SDD%d_SDF%d_SLK00_SLK10_SNC%d_ST01_ST11_SG00_SG10"%(sdd, sdf, snc) in onekey:
                        print (onekey)
                        cfgdata = data[onekey]
                        fembs = cfgdata[0]
                        rawdata = cfgdata[1]
                        cfg_info = cfgdata[2]
                        chns, rmss, peds, pkps, pkns, wfs, wfsf = data_ana(fembs, rawdata, rms_flg=True)
    

      
        for sg0 in [0, 1]:
            for sg1 in [0, 1]:
                for onekey in dkeys:
                    if "RMS_SDD0_SDF0_SLK00_SLK10_SNC0_ST00_ST10_SG0%d_SG1%d"%(sg0, sg1) in onekey:
                        print (onekey)
                        cfgdata = data[onekey]
                        fembs = cfgdata[0]
                        rawdata = cfgdata[1]
                        cfg_info = cfgdata[2]
                        chns, rmss, peds, pkps, pkns, wfs, wfsf = data_ana(fembs, rawdata, rms_flg=True)
    
                        ax1.plot(np.array(peds), marker='.', label="SNC0_SG0%d_SG1%d"%(sg0, sg1))
                        ax2.plot(np.array(rmss), marker='.', label="SNC0_SG0%d_SG1%d"%(sg0, sg1))
    
      
        for slk0 in [0, 1]:
            for slk1 in [0, 1]:
                for onekey in dkeys:
                    if "RMS_SLK_SDD0_SDF0_SLK0%d_SLK1%d_SNC0_ST01_ST11_SG00_SG10"%(slk0, slk1) in onekey:
                        print (onekey)
                        cfgdata = data[onekey]
                        fembs = cfgdata[0]
                        rawdata = cfgdata[1]
                        cfg_info = cfgdata[2]
                        chns, rmss, peds, pkps, pkns, wfs, wfsf = data_ana(fembs, rawdata, rms_flg=True)
    
    
       
    

if __name__=="__main__":
    fdir = '''S:\RTS_DAT_LArASIC_QC\B006T0001\Time_20251006150332_DUT_0048_1049_2050_3051_4052_5053_6054_7055\LN_FE_006002185_006002377_006002378_006002379_006002380_006002385_006002386_006002387/'''
    
    dat_larasic_qc_rms_ana(fdir=fdir)
    #QCstatus, bads = dat_larasic_initchk(fdir)
    #print (bads)

