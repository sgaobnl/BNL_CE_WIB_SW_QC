from spymemory_decode import wib_spy_dec_syn
import numpy as np
import matplotlib.pyplot as plt
import pickle
import QC_constants
from scipy.optimize import curve_fit
import pandas as pd

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
                   t0 = wib_data[0][j]["TMTS"]
                else:
                   t0 = 0
    
                if 2 in fembs or 3 in fembs:
                   t1 = wib_data[1][j]["TMTS"]
                else:
                   t1 = 0
   
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


    def GetPeaks(self, data, tmst, nfemb, fp, fname, funcfit=False, shapetime=2):
    
        nevent = len(data)
    
        ppk_val=[]
        npk_val=[]
        bl_val=[]
        fig,ax = plt.subplots(1,2,figsize=(12,4))
       
        for ich in range(128):
            global_ch = nfemb*128+ich
            allpls=np.zeros(500)
            npulse=0
            hasError=False
            for itr in range(nevent):
                evtdata = data[itr][global_ch]
        
                if itr==0:
                   peak1_pos = np.argmax(evtdata[0:500]) 
                   peak_val = evtdata[peak1_pos]
                   if peak1_pos<100:
                      tmp_bl = np.mean(evtdata[peak1_pos+200:500])
                   else:
                      tmp_bl = np.mean(evtdata[0:50])
                   if abs(peak_val/tmp_bl-1)<0.1:
                      print("femb%d ch%d event0 doesn't have pulse, will skip this chan"%(nfemb,ich))
                      hasError=True
                      break

                   if peak1_pos>400:
                      t0 = np.argmax(evtdata[peak1_pos+50:peak1_pos+550])
                      t0 = t0-200
                      allpls = allpls + evtdata[t0:t0+500]
                      t0 = tmst[0][nfemb//2][t0]
                   else:
                      allpls = allpls + evtdata[:500]
                      t0 = tmst[0][nfemb//2][0]
                   npulse=1

                start_t = 500-(tmst[itr][nfemb//2][0]-t0)%500
                end_t = len(evtdata)-500
                for tt in range(start_t, end_t, 500):
                    allpls = allpls + evtdata[tt:tt+500]
                    npulse = npulse+1

            if hasError:
               ppk_val.append(0)
               npk_val.append(0)
               bl_val.append(0)
               continue
 
            apulse = allpls/npulse

            pmax = np.amax(apulse)
            maxpos = np.argmax(apulse)
            ax[0].plot(range(120),apulse[maxpos-30:maxpos+90])
            if funcfit:
               popt = FitFunc(apulse, shapetime, makeplot=False)
               a_xx = np.array(range(20))*0.5
               a_yy = ResFunc(a_xx, popt[0],popt[1],popt[2],popt[3])
               pmax = np.amax(a_yy)
      
            if maxpos>100:
               bbl = np.mean(apulse[:maxpos-50])           
            else:
               bbl = np.mean(apulse[400:])           
          
            pmin = np.amin(apulse)

            ppk_val.append(pmax)
            npk_val.append(pmin)
            bl_val.append(bbl)
        
        ax[0].set_title(fname)
        ax[0].set_xlabel("ticks")
        ax[0].set_ylabel("ADC")

        ax[1].plot(range(128), ppk_val, marker='.',label='pos')
        ax[1].plot(range(128), npk_val, marker='.',label='neg')
        ax[1].plot(range(128), bl_val, marker='.',label='ped')
        ax[1].set_title(fname)
        ax[1].set_xlabel("chan")
        ax[1].set_ylabel("ADC")
        ax[1].legend()
        fp_fig = fp+"pulse_{}.png".format(fname)
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


