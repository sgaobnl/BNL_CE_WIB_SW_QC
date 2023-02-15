import numpy as np
import pandas as pd
from scipy.signal import find_peaks
import matplotlib.pyplot as plt
import sys
from spymemory_decode import wib_spy_dec_syn
import time
import pickle
import os

class ana_tools:
    def __init__(self):
        self.fadc = 1/(2**14)*2048 # mV

    def data_decode(self,raw,fembs):

        nevent = len(raw) 
        sss=[]
     
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

                aa=a0+a1+a2+a3
                chns.append(aa)

            chns = list(zip(*chns))    
            sss.append(chns) 
               
        return sss        

    def data_ana(self, data, nfemb):
        
        nevent = len(data)

        if nevent>100:
           nevent=100

        rms=[]
        ped=[]
        pkp=[]
        pkn=[]
        onewf=[]
        avgwf=[] 

        for ich in range(128):
            global_ch = nfemb*128+ich
            peddata=np.empty(0)
            pkpdata=np.empty(0)
            pkndata=np.empty(0)
            wfdata = np.zeros(500)

            npulse=0
            first = True
            for itr in range(nevent):
                evtdata = data[itr][global_ch] 
                pmax = np.amax(evtdata)
                pos = np.argmax(evtdata)

                pos_peaks, _ = find_peaks(evtdata,height=pmax-1000) 

                for ipos in pos_peaks:
                    startpos=ipos-50
                    if startpos<0:
                       continue

                    if startpos+500>=len(evtdata):
                       break

                    tmp_wf = evtdata[startpos:startpos+500]     # one wave
                    if first:
                       onewf.append(tmp_wf)
                       first=False
 
                    npulse=npulse+1
                    wfdata = wfdata + tmp_wf
                    peddata = np.hstack([peddata,tmp_wf[250:450]])
                    pkpdata = np.hstack([pkpdata,np.max(tmp_wf)])
                    pkndata = np.hstack([pkndata,np.min(tmp_wf)])

            ch_ped = np.mean(peddata)
            ch_rms = np.std(peddata)
            ch_pkp = np.mean(pkpdata)
            ch_pkn = np.mean(pkndata)

            ped.append(ch_ped)
            rms.append(ch_rms)
            pkp.append(ch_pkp)
            pkn.append(ch_pkn)
 
            if npulse>0:
                avgwf.append(wfdata/npulse)
            else:
                print("Error: femb {} ch{} may not have pulse! Check the plot!".format(nfemb,ich))
               # evdata = data[0][128*nfemb+ich] 
               # plt.plot(range(len(evdata)),evdata)
               # plt.show()
                sys.exit()

        return rms,ped,pkp,pkn,onewf,avgwf 


    def GetRMS(self, data, nfemb, fp, fname):
        
        nevent = len(data)

        if nevent>100:
           nevent=100

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

        fp_bin = fp+"RMS_{}.bin".format(fname)
        with open(fp_bin, 'wb') as fn:
             pickle.dump( [ped, rms], fn) 

        return ped,rms


    def FEMB_SUB_PLOT(self, ax, x, y, title, xlabel, ylabel, color='b', marker='.', ylabel_twx = "", limit=False, ymin=0, ymax=1000):
        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.grid(True)
        if limit:
            ax.plot(x,y, marker=marker, color=color)
            ax.set_ylim([ymin, ymax])
        else:
            ax.plot(x,y, marker=marker, color=color)

    def FEMB_CHK_PLOT(self, chn_rmss,chn_peds, chn_pkps, chn_pkns, chn_onewfs, chn_avgwfs, fp):
        fig = plt.figure(figsize=(10,5))
        fn = fp.split("/")[-1]
        ax1 = plt.subplot2grid((4, 4), (0, 0), colspan=2, rowspan=2)
        ax2 = plt.subplot2grid((4, 4), (0, 2), colspan=2, rowspan=2)
        ax3 = plt.subplot2grid((4, 4), (2, 0), colspan=2, rowspan=2)
        ax4 = plt.subplot2grid((4, 4), (2, 2), colspan=2, rowspan=2)
        chns = range(128)
#        self.FEMB_SUB_PLOT(ax1, chns, chn_rmss, title="RMS Noise", xlabel="CH number", ylabel ="ADC / bin", color='r', marker='.', limit=True, ymin=0, ymax=25)
#        self.FEMB_SUB_PLOT(ax2, chns, chn_peds, title="Red: Pos Peak. Blue: Pedestal. Green: Neg Peak", xlabel="CH number", ylabel ="ADC / bin", color='b', marker='.', limit=True, ymin=0, ymax=10000)
#        self.FEMB_SUB_PLOT(ax2, chns, chn_pkps, title="Red: Pos Peak. Blue: Pedestal. Green: Neg Peak", xlabel="CH number", ylabel ="ADC / bin", color='r', marker='.', limit=True, ymin=0, ymax=10000)
#        self.FEMB_SUB_PLOT(ax2, chns, chn_pkns, title="Red: Pos Peak. Blue: Pedestal. Green: Neg Peak", xlabel="CH number", ylabel ="ADC / bin", color='g', marker='.', limit=True, ymin=0, ymax=10000)

        self.FEMB_SUB_PLOT(ax1, chns, chn_rmss, title="RMS Noise", xlabel="CH number", ylabel ="ADC / bin", color='r', marker='.')
        self.FEMB_SUB_PLOT(ax2, chns, chn_peds, title="Red: Pos Peak. Blue: Pedestal. Green: Neg Peak", xlabel="CH number", ylabel ="ADC / bin", color='b', marker='.')
        self.FEMB_SUB_PLOT(ax2, chns, chn_pkps, title="Red: Pos Peak. Blue: Pedestal. Green: Neg Peak", xlabel="CH number", ylabel ="ADC / bin", color='r', marker='.')
        self.FEMB_SUB_PLOT(ax2, chns, chn_pkns, title="Red: Pos Peak. Blue: Pedestal. Green: Neg Peak", xlabel="CH number", ylabel ="ADC / bin", color='g', marker='.')
        for chni in chns:
            ts = 100
            x = (np.arange(ts)) * 0.5
            y3 = chn_onewfs[chni][25:ts+25]
            y4 = chn_avgwfs[chni][25:ts+25]
            self.FEMB_SUB_PLOT(ax3, x, y3, title="Waveform Overlap", xlabel="Time / $\mu$s", ylabel="ADC /bin", color='C%d'%(chni%9))
            self.FEMB_SUB_PLOT(ax4, x, y4, title="Averaging Waveform Overlap", xlabel="Time / $\mu$s", ylabel="ADC /bin", color='C%d'%(chni%9))

        #fig.suptitle(fn)
        plt.tight_layout( rect=[0.05, 0.05, 0.95, 0.95])
        fn = fp + ".png"
        plt.savefig(fn)
        plt.close(fig)

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
       
        for ifemb,femb_no in fembs.items():
            nfemb=int(ifemb[-1])
            
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
            newfp=fp[ifemb]+"mon_meas.png"
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

               newfp=fp[ifemb]+"mon_meas_plot.png"
               fig1.savefig(newfp)
               plt.close(fig1)

  
 
