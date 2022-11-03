import numpy as np
import pandas as pd
from scipy.signal import find_peaks
import matplotlib.pyplot as plt
import sys
from spymemory_decode import wib_spy_dec_syn
import time
import pickle
import os

class QC_tools:
    def __init__(self):
        self.fadc = 1/(2**14)*2048 # mV

    def data_decode(self,raw,fembs):

        nevent = len(raw) 
        sss=[]
     
        for i in range(nevent):
            data = raw[0]
            buf_end_addr = raw[1]
            trigger_rec_ticks = raw[2]
            if raw[3] != 0:
                trigmode = 'HW';
            else:
                trigmode = 'SW';

            buf0 = data[0]
            buf1 = data[1]
           
            wib_data = wib_spy_dec_syn(buf0, buf1, trigmode, buf_end_addr, trigger_rec_ticks, fembs)
 
            nsamples = len(wib_data[0])

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

                
                a1 = wib_data[0][j]["FEMB1_3"]
                a2 = wib_data[1][j]["FEMB0_2"]
                a3 = wib_data[1][j]["FEMB1_3"]
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

                pos_peaks, _ = find_peaks(evtdata,height=pmax-100) 

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
                print("femb {} ch{} doesn't have pulse!".format(nfemb,ich))
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

    def GetGain(self, fembs, datadir, savedir, fdir, namepat, snc, sgs, sts, outpat, dac_list, updac=25, lodac=10): 

        dac_v = {}  # mV/bit
        dac_v['4_7mVfC']=18.66
        dac_v['7_8mVfC']=14.33
        dac_v['14_0mVfC']=8.08
        dac_v['25_0mVfC']=4.61

        CC=1.85*pow(10,-13)
        e=1.602*pow(10,-19)

        if "sgp1" in outpat:
            dac_du = dac_v['4_7mVfC']
        else:
            dac_du = dac_v[sgs]

        pk_dic={}
        for ifemb,_ in fembs.items():
            pk_dic[ifemb]=[]

        fname = outpat.format(snc, sgs, sts)

        for dac in dac_list:
            afile = datadir + namepat.format(snc, sgs, sts, dac)
            with open(afile, 'rb') as fn:
                 raw = pickle.load(fn)

            rawdata=raw[0]
            pldata = self.data_decode(rawdata)
            pldata = np.array(pldata, dtype=object)

            for ifemb,femb_id in fembs.items():
                nfemb=int(ifemb[-1])
                if dac==0:
                   tmpped,_ = self.GetRMS(pldata, nfemb, savedir[ifemb]+fdir, fname)
                   pk_dic[ifemb].append(tmpped)
                else:
                   ana = self.data_ana(pldata, nfemb)
                   pk_dic[ifemb].append(ana[2])

        for ifemb,femb_id in fembs.items():
            nfemb=int(ifemb[-1])
            pk_list = pk_dic[ifemb]
            new_pk_list = list(zip(*pk_list))

            fig1,ax1 = plt.subplots(figsize=(6,4))
            ch_inl=[]
            ch_gain=[]
            ch_linear_dac=[]

            for ch in range(128):
                ch_pk = list(new_pk_list[ch])
                ana=self.CheckLinearty(dac_list, ch_pk, updac, lodac)

                if ana[0]>0:
                    tmpgain = 1/ana[0]*dac_du/1000 *CC/e
                else:
                    tmpgain=0

                ch_gain.append(tmpgain)                
                ch_inl.append(ana[1])                
                ch_linear_dac.append(ana[2])                

                ax1.plot(dac_list, ch_pk)

            ax1.set_xlabel("DAC")
            ax1.set_ylabel("Peak Value")
            ax1.set_title(fname)
            fp = savedir[ifemb]+fdir+"peak_{}.png".format(fname)
            plt.savefig(fp)
            plt.close(fig1)

            fig2,ax2 = plt.subplots(figsize=(6,4))
            xx=range(128)
            ax2.plot(xx, ch_gain, marker='.')
            ax2.set_xlabel("chan")
            ax2.set_ylabel("gain")
            ax2.set_title(fname)
            fp = savedir[ifemb]+fdir+"gain_{}.png".format(fname)
            plt.savefig(fp)
            plt.close(fig2)

            fig3,ax3 = plt.subplots(figsize=(6,4))
            xx=range(128)
            ax3.plot(xx, ch_inl, marker='.')
            ax3.set_xlabel("chan")
            ax3.set_ylabel("INL")
            ax3.set_title(fname)
            fp = savedir[ifemb]+fdir+"inl_{}.png".format(fname)
            plt.savefig(fp)
            plt.close(fig3)

            fig4,ax4 = plt.subplots(figsize=(6,4))
            xx=range(128)
            ax4.plot(xx, ch_linear_dac, marker='.')
            ax4.set_xlabel("chan")
            ax4.set_ylabel("max linear dac")
            ax4.set_title(fname)
            fp = savedir[ifemb]+fdir+"linear_max_dac_{}.png".format(fname)
            plt.savefig(fp)
            plt.close(fig4)

            fp_bin = savedir[ifemb] + fdir + "Gain_{}.bin".format(fname)
            with open(fp_bin, 'wb') as fn:
                 pickle.dump( [ch_gain, ch_inl, ch_linear_dac], fn) 

    def CheckLinearty(self, dac_list, pk_list, updac, lodac):

        dac_init=[]
        pk_init=[]
        for i in range(len(dac_list)):
            if dac_list[i]<updac and dac_list[i]>=lodac:
               dac_init.append(dac_list[i])
               pk_init.append(pk_list[i])

        slope_i,intercept_i=np.polyfit(dac_init,pk_init,1)

        y_min = pk_list[0]
        y_max = pk_list[-1]
        linear_dac_max=dac_list[-1]

        index=-1
        for i in range(len(dac_list)):
            y_r = pk_list[i]
            y_p = dac_list[i]*slope_i + intercept_i
            inl = abs(y_r-y_p)/(y_max-y_min)
            if inl>0.03:
               linear_dac_max = dac_list[i-1]
               index=i
               break
        
        if index==0:
            return 0,0,0

        slope_f,intercept_f=np.polyfit(dac_list[:index],pk_list[:index],1)

        y_max = pk_list[index-1]
        y_min = pk_list[0]
        INL=0
        for i in range(index):
            y_r = pk_list[i]
            y_p = dac_list[i]*slope_f + intercept_f
            inl = abs(y_r-y_p)/(y_max-y_min)
            if inl>INL:
               INL=inl

        return slope_f, INL, linear_dac_max

    def GetENC(self, fembs, snc, sgs, sts, sgp, savedir, fdir):


        for ifemb,femb_id in fembs.items():
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
            gain_list=np.array(gain_list[0])
    
            enc_list = rms_list*gain_list
        
            fig,ax = plt.subplots(figsize=(6,4))
            xx=range(128)
            ax.plot(xx, enc_list, marker='.')
            ax.set_xlabel("chan")
            ax.set_ylabel("ENC")
            ax.set_title(fname)
            fp = savedir[ifemb]+fdir+"enc_{}.png".format(fname)
            plt.savefig(fp)
            plt.close(fig)

            fp_bin = savedir[ifemb] + fdir + "ENC_{}.bin".format(fname)
            with open(fp_bin, 'wb') as fn:
                 pickle.dump( enc_list, fn) 

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

    def PrintPWR(self, pwr_data, fp):

        pwr_names=['BIAS','LArASIC','ColdDATA','ColdADC']
        pwr_set=[5,3,3,3.5]
        pwr_dic={'name':[],'V_set/V':[],'V_meas/V':[],'I_meas/A':[],'P_meas/W':[]}
        i=0
        total_p = 0
        for ilist in pwr_data:
            pwr_dic['name'].append(pwr_names[i])
            pwr_dic['V_set/V'].append(pwr_set[i])
            i=i+1
            pwr_dic['V_meas/V'].append(round(ilist[1],3))
            pwr_dic['I_meas/A'].append(round(ilist[2],3))
            pwr_dic['P_meas/W'].append(round(ilist[3],3))
            total_p = total_p + ilist[3]

        df=pd.DataFrame(data=pwr_dic)

        fig, ax =plt.subplots(figsize=(10,2))
        ax.axis('off')
        table = ax.table(cellText=df.values,colLabels=df.columns,loc='center')
        ax.set_title("Power Consumption = {} W".format(round(total_p,3)))
        table.set_fontsize(14)
        table.scale(1,2)
        fig.savefig(fp+".png")
        plt.close(fig)

    def PrintMON(self, fembs, nchips, mon_bgp, mon_t, mon_adcs, fp):
       
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

            fig, ax =plt.subplots(figsize=(10,2))
            ax.axis('off')
            table = ax.table(cellText=df.values,colLabels=df.columns,loc='center')
            ax.set_title("Monitoring path for FE-ADC (#mV)")
            table.set_fontsize(14)
            table.scale(1,2.2)
            newfp=fp[ifemb]+"mon_meas.png"
            fig.savefig(newfp)
            plt.close(fig)
 
    def PlotMon(self, fembs, mon_data, savedir, fdir, fname):

        for ifemb,femb_id in fembs.items():
            mon_list=[] 
            xlabels=[] 
            nfemb=int(ifemb[-1])
            for key,value in mon_data.items():
                sps=len(value)
                total=list(map(sum, zip(*value)))
                avg=np.array(total)/sps*self.fadc
                mon_list.append(avg[nfemb])
                xlabels.append(key)
              
            fig,ax = plt.subplots(figsize=(6,4))
            xx=range(len(xlabels))
            ax.plot(xx, mon_list, marker='.')
            plt.setp(ax, xticks=xx, xticklabels=xlabels)
            ax.set_ylabel(fname)
            fp = savedir[ifemb] + fdir + "/mon_{}.png".format(fname)
            fig.savefig(fp)
            plt.close(fig)
             
    def PlotMonChan(self, fembs, mon_data, savedir, fdir, fname):

        for ifemb,femb_id in fembs.items():
            mon_list=[] 
            nfemb=int(ifemb[-1])
            for key,value in mon_data.items():
                sps=len(value)
                total=list(map(sum, zip(*value)))
                avg=np.array(total)/sps*self.fadc
                mon_list.append(avg[nfemb])
              
            fig,ax = plt.subplots(figsize=(6,4))
            xx=range(128)
            ax.scatter(xx, mon_list, marker='.')
            ax.set_ylabel(fname)
            ax.set_xlabel("chan")
            fp = savedir[ifemb] + fdir + "/mon_{}.png".format(fname)
            fig.savefig(fp)
            plt.close(fig)
             
    def PlotMonDAC(self, fembs, mon_data, savedir, fdir, fname, dac_list, key_patt):

        for ifemb,femb_id in fembs.items():

            nfemb=int(ifemb[-1])
            fig,ax = plt.subplots(figsize=(6,4))
            for ichip in range(8):
                mon_list=[]
                for vdac in dac_list:
                    value=mon_data[key_patt.format(vdac,ichip)]
                    sps=len(value)
                    total=list(map(sum, zip(*value)))
                    avg=np.array(total)/sps*self.fadc
                    mon_list.append(avg[nfemb]) 

                ax.plot(dac_list, mon_list, label='chip{}'.format(ichip))
              
            ax.set_title(fname)
            ax.set_xlabel("DAC")
            plt.legend()
            fp = savedir[ifemb] + fdir + "/mon_{}.png".format(fname)
            fig.savefig(fp)
            plt.close(fig)
             
    def PlotADCMon(self, fembs, mon_data, savedir, fdir):

        mons=["VCMI", "VCMO", "VREFP", "VREFN"]

        for ifemb,femb_id in fembs.items():
            nfemb=int(ifemb[-1])

            for i in range(len(mons)):
                fig,ax = plt.subplots(figsize=(6,4))
                ndac=len(mon_data)

                for j in range(8):  # chip #
                    mon_list=[]
                    dac_list=[]
                    for k in range(ndac):
                        value = mon_data[k][1][1+i][f'chip{j}'][3]
                        sps=len(value)
                        total=list(map(sum, zip(*value)))
                        avg=np.array(total)/sps*self.fadc
                        mon_list.append(avg[nfemb]) 
                        dac_list.append(mon_data[k][0])

                    ax.plot(dac_list, mon_list, marker='.', label='chip{}'.format(j))
              
                ax.set_title(mons[i])
                ax.set_xlabel("DAC")
                plt.legend()
                fp = savedir[ifemb] + fdir + "/mon_{}.png".format(mons[i])
                fig.savefig(fp)
                plt.close(fig)

