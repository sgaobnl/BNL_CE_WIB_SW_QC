from spymemory_decode import wib_spy_dec_syn
import numpy as np
import matplotlib.pyplot as plt
import pickle
import QC_constants
from scipy.optimize import curve_fit
import pandas as pd

def Gauss(x, H, A, x0, sigma):
    return H + A * np.exp(-(x - x0) ** 2 / (2 * sigma ** 2))

def Gauss_fit(x, y):
    mean = sum(x * y) / sum(y)
    sigma = np.sqrt(sum(y * (x - mean) ** 2) / sum(y))
    popt, pcov = curve_fit(Gauss, x, y, p0=[min(y), max(y), mean, sigma])
    yp = Gauss(x,popt[0],popt[1],popt[2],popt[3])
    chi2 = sum((y - yp)**2/yp)
    return popt,chi2

class ana_tools:
    def __init__(self):
        self.fadc = 1/(2**14)*2048 # mV

    def data_decode(self,raw,fembs):
    
        nevent = len(raw)
        sss=[]
        ttt=[]
   
        for i in range(nevent):
            data = raw[i][0]
            buf_end_addr = raw[i][1]
            trigger_rec_ticks = raw[i][2]
            if raw[i][3] != 0:
                trigmode = 'HW';
            else:
                trigmode = 'SW';
    
            buf0 = data[0]
            buf1 = data[1]
    
            wib_data = wib_spy_dec_syn(buf0, buf1, trigmode, buf_end_addr, trigger_rec_ticks, fembs)
    
            if (0 in fembs) or (1 in fembs):
               nsamples = len(wib_data[0])
            else:
               nsamples = len(wib_data[1])
    
            chns=[]
            tmst0=[]
            tmst1=[]
            for j in range(nsamples):
                if 0 in fembs:
                   a0 = wib_data[0][j]["FEMB0_2"]
                else:
                   a0 = [0]*128
    
                if 1 in fembs:
                   a1 = wib_data[0][j]["FEMB1_3"]
                else:
                   a1 = [0]*128
    
                if 2 in fembs:
                   a2 = wib_data[1][j]["FEMB0_2"]
                else:
                   a2 = [0]*128
    
                if 3 in fembs:
                   a3 = wib_data[1][j]["FEMB1_3"]
                else:
                   a3 = [0]*128

                if 0 in fembs or 1 in fembs:
                   t0 = wib_data[0][j]["TMTS_low5"]
                else:
                   t0 = [0]*128
    
                if 2 in fembs or 3 in fembs:
                   t1 = wib_data[1][j]["TMTS_low5"]
                else:
                   t1 = [0]*128
    
                aa=a0+a1+a2+a3
                chns.append(aa)
                tmst0.append(t0)
                tmst1.append(t1)
    
            chns = list(zip(*chns))
            sss.append(chns)
            ttt.append([tmst0,tmst1])
    
        return sss,ttt
    
    def GetRMS(self, data, nfemb, fp, fname):
    
        nevent = len(data)
    
        rms=[]
        ped=[]
    
        for ich in range(128):
            global_ch = nfemb*128+ich
            peddata=np.empty(0)
    
            npulse=0
            first = True
            allpls=np.empty(0)
            for itr in range(nevent):
                evtdata = data[itr][global_ch]
                allpls=np.append(allpls,evtdata)
    
            ch_ped = np.mean(allpls)
            ch_rms = np.std(allpls)

            ped.append(ch_ped)
            rms.append(ch_rms)
    
        fig,ax = plt.subplots(figsize=(6,4))
        ax.plot(range(128), rms, marker='.')
        ax.set_title(fname)
        ax.set_xlabel("chan")
        ax.set_ylabel("rms")
        fp_fig = fp+"rms_{}.png".format(fname)
        plt.savefig(fp_fig)
        plt.close(fig)

        fig,ax = plt.subplots(figsize=(6,4))
        ax.plot(range(128), ped, marker='.')
        ax.set_title(fname)
        ax.set_xlabel("chan")
        ax.set_ylabel("ped")
        fp_fig = fp+"ped_{}.png".format(fname)
        plt.savefig(fp_fig)
        plt.close(fig)
    
        fp_bin = fp+"RMS_{}.bin".format(fname)
        with open(fp_bin, 'wb') as fn:
             pickle.dump( [ped, rms], fn)
    
        return ped,rms

    def ChkRMS(self, env, fp, fname, snc, sgs, sts):
      
        infile = fp+"RMS_{}.bin".format(fname)
        with open(infile, 'rb') as fn:
            raw = pickle.load(fn)  

        ped = raw[0]
        rms = raw[1]
       
        if env=='LN': 
           if snc==0:
              ped_std = 0.01 
           else:
              ped_std = 0.07
           ped_lo = QC_constants.PED_LN_mean[snc][sgs][sts]*(1-ped_std)
           ped_hi = QC_constants.PED_LN_mean[snc][sgs][sts]*(1+ped_std)

           rms_lo = QC_constants.RMS_LN_mean[snc][sgs][sts]*(1-0.06)
           rms_hi = QC_constants.RMS_LN_mean[snc][sgs][sts]*(1+0.06)

        if env=='RT': 
           if snc==0:
              ped_std = 0.01 
           else:
              ped_std = 0.07
           ped_lo = QC_constants.PED_RT_mean[snc][sgs][sts]*(1-ped_std)
           ped_hi = QC_constants.PED_RT_mean[snc][sgs][sts]*(1+ped_std)
                                                                    
           rms_lo = QC_constants.RMS_RT_mean[snc][sgs][sts]*(1-0.06)
           rms_hi = QC_constants.RMS_RT_mean[snc][sgs][sts]*(1+0.06)

        outfile = open(fp+"issued_channels_ped_rms.txt", "a")
        outfile.write("%s %s %s %s\n"%(env, QC_constants.SNC[snc], QC_constants.SGS[sgs], QC_constants.STS[sts]))
        outfile.write("\n")

        nfail=0
        for ch in range(128):
            failed=False
            if ped[ch]<ped_lo:
               outfile.write("ch%d low pedestal %f\n"%(ch,ped[ch]))
               failed=True
            if ped[ch]>ped_hi:
               outfile.write("ch%d high pedestal %f\n"%(ch,ped[ch]))
               failed=True

            if rms[ch]<rms_lo:
               outfile.write("ch%d low rms %f\n"%(ch,rms[ch]))
               failed=True
            if rms[ch]>rms_hi:
               outfile.write("ch%d high rms %f\n"%(ch,rms[ch]))
               failed=True

            if failed:
               nfail = nfail+1 

        outfile.write("\n")

        return nfail


    def GetPeaks(self, data, tmst, nfemb, fp, fname):
    
        nevent = len(data)
        print(nevent)
    
        ppk_val=[]
        npk_val=[]
        bl_val=[]
        fig,ax = plt.subplots(figsize=(6,4))

        for ich in range(128):
            global_ch = nfemb*128+ich
            allpls=np.zeros(500)
            npulse=0
            for itr in range(nevent):
                evtdata = data[itr][global_ch]
                allpls = allpls + evtdata[0:500] + evtdata[500:1000] + evtdata[1000:1500] + evtdata[1500:2000]
                npulse = npulse+4
#                plt.plot(range(500),evtdata[0:500])
#                plt.plot(range(500),evtdata[500:1000])
#                plt.plot(range(500),evtdata[1000:1500])
#                plt.plot(range(500),evtdata[1500:2000])
                #plt.plot(range(len(tmst[itr][nfemb//2])),tmst[itr][nfemb//2]-tmst[itr][nfemb//2][0])
                plt.plot(range(len(tmst[itr][nfemb//2])),tmst[itr][nfemb//2])

            plt.show()
            break
            apulse = allpls/npulse
            ax.plot(range(500),apulse)
 
            pmax = np.amax(apulse)
            maxpos = np.argmax(apulse) 
            ppkt,pchi2 = Gauss_fit(range(40), apulse[maxpos-20:maxpos+20])
            ppk = ppkt[1] + ppkt[0]
           
#            plt.scatter(range(40), apulse[maxpos-20:maxpos+20])
#            xx = np.linspace(0,40,100)
#            plt.plot(xx, Gauss(xx,ppkt[0],ppkt[1],ppkt[2],ppkt[3]))
#            plt.show()

            if maxpos>100:
               bbl = np.mean(apulse[:maxpos-50])           
            else:
               bbl = np.mean(apulse[400:])           
          
            pmin = np.amin(apulse)
            minpos = np.argmin(apulse) 
            npkt,nchi2 = Gauss_fit(range(40), apulse[minpos-20:minpos+20])
            npk = npkt[1] + npkt[0]

#            plt.scatter(range(40), apulse[minpos-20:minpos+20])
#            xx = np.linspace(0,40,1)
#            plt.plot(xx, Gauss(xx,npkt[0],npkt[1],npkt[2],npkt[3]))
#            plt.show()

            ppk_val.append(ppk)
            npk_val.append(npk)
            bl_val.append(bbl)
        
        ax.set_title(fname)
        ax.set_xlabel("ticks")
        ax.set_ylabel("ADC")
        fp_fig = fp+"avg_pulse_{}.png".format(fname)
        plt.savefig(fp_fig)
        plt.close(fig)
    
        return ppk_val,npk_val,bl_val    

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

        df=pd.DataFrame(data=pwr_dic)
        fig, ax =plt.subplots(figsize=(10,2))
        ax.axis('off')
        table = ax.table(cellText=df.values,colLabels=df.columns,loc='center')
        ax.set_title("Power Consumption = {} W".format(round(total_p,3)))
        table.set_fontsize(14)
        table.scale(1,2)
        fig.savefig(fp+".png")
        plt.close(fig)

    def PrintMON(self, fembs, nchips, mon_bgp, mon_t, mon_adcs, fp, makeplot=False):

        for nfemb in fembs:

            mon_dic={'ASIC#':[],'FE T':[],'FE BGP':[],'ADC VCMI':[],'ADC VCMO':[], 'ADC VREFP':[], 'ADC VREFN':[], 'ADC VSSA':[]}

            for i in nchips: # 8 chips per board

                mon_dic['ASIC#'].append(i)
                fe_t = round(mon_t[f'chip{i}'][0][nfemb]*self.fadc,1)
                fe_bgp = round(mon_bgp[f'chip{i}'][0][nfemb]*self.fadc,1)
                mon_dic['FE T'].append(fe_t)
                mon_dic['FE BGP'].append(fe_bgp)

                vcmi = round(mon_adcs[f'chip{i}']["VCMI"][1][0][nfemb]*self.fadc,1)
                vcmo = round(mon_adcs[f'chip{i}']["VCMO"][1][0][nfemb]*self.fadc,1)
                vrefp = round(mon_adcs[f'chip{i}']["VREFP"][1][0][nfemb]*self.fadc,1)
                vrefn = round(mon_adcs[f'chip{i}']["VREFN"][1][0][nfemb]*self.fadc,1)
                vssa = round(mon_adcs[f'chip{i}']["VSSA"][1][0][nfemb]*self.fadc,1)

                mon_dic['ADC VCMI'].append(vcmi)
                mon_dic['ADC VCMO'].append(vcmo)
                mon_dic['ADC VREFP'].append(vrefp)
                mon_dic['ADC VREFN'].append(vrefn)
                mon_dic['ADC VSSA'].append(vssa)

            df=pd.DataFrame(data=mon_dic)
            fig, ax =plt.subplots(figsize=(10,5))
            ax.axis('off')
            table = ax.table(cellText=df.values,colLabels=df.columns,loc='center')
            ax.set_title("Monitoring path for FE-ADC (#mV)")
            table.set_fontsize(14)
            table.scale(1,2.2)
            newfp=fp[nfemb]+"mon_meas.png"
            fig.savefig(newfp)
            plt.close(fig)

            if makeplot:
               fig1, ax1 =plt.subplots(1,2,figsize=(10,4))
               ax1[0].plot(nchips, mon_dic['FE T'],marker='.',label='FE T')
               ax1[0].plot(nchips, mon_dic['FE BGP'],marker='.',label='FE BGP')
               ax1[0].set_title("Monitoring path for FE (mV)")
               ax1[0].set_xlabel("nchip")
               ax1[0].legend()

               ax1[1].plot(nchips, mon_dic['ADC VCMI'],marker='.',label='ADC VCMI')
               ax1[1].plot(nchips, mon_dic['ADC VCMO'],marker='.',label='ADC VCMO')
               ax1[1].plot(nchips, mon_dic['ADC VREFP'],marker='.',label='ADC VREFP')
               ax1[1].plot(nchips, mon_dic['ADC VREFN'],marker='.',label='ADC VREFN')
               ax1[1].plot(nchips, mon_dic['ADC VSSA'],marker='.',label='ADC VSSA')
               ax1[1].set_title("Monitoring path for ADC (mV)")
               ax1[1].set_xlabel("nchip")
               ax1[1].legend()
               plt.tight_layout()

               newfp=fp[nfemb]+"mon_meas_plot.png"
               fig1.savefig(newfp)
               plt.close(fig1)


