from spymemory_decode import wib_dec
import numpy as np
import matplotlib.pyplot as plt
import pickle
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
        wibdata = wib_dec(data=raw, fembs=fembs,fastchk = False, cd0cd1sync=True) 
        return wibdata
#        sss=[]
#        ttt=[]
#   
###        for i in range(nevent):
#            wib_data = wib_dec(raw[i], fembs)
#            data = raw[i][0]
#            buf_end_addr = raw[i][1]
#            trigger_rec_ticks = raw[i][2]
#            if raw[i][3] != 0:
#                trigmode = 'HW';
#            else:
#                trigmode = 'SW';
#    
#            buf0 = data[0]
#            buf1 = data[1]
#    
#            wib_data = wib_dec(data, trigmode, buf_end_addr, trigger_rec_ticks, fembs)
#    
#            if (0 in fembs) or (1 in fembs):
#                nsamples0 = len(wib_data[0])
#            else:
#                nsamples0 = -1
#            if (2 in fembs) or (3 in fembs):
#                nsamples1 = len(wib_data[1])
#            else:
#                nsamples1 = -1
#            if (nsamples0 > 0) and (nsamples1 > 0):
#                if nsamples0 > nsamples1:
#                    nsamples = nsamples1
#                else:
#                    nsamples = nsamples0
#            elif nsamples0 > 0 :
#                nsamples = nsamples0
#            elif nsamples1 > 0 :
#                nsamples = nsamples1
#    
#            chns=[]
#            tmst0=[]
#            tmst1=[]
#            for j in range(nsamples):
#                if 0 in fembs:
#                   a0 = wib_data[0][j]["FEMB0_2"]
#                else:
#                   a0 = [0]*128
#    
#                if 1 in fembs:
#                   a1 = wib_data[0][j]["FEMB1_3"]
#                else:
#                   a1 = [0]*128
#    
#                if 2 in fembs:
#                   a2 = wib_data[1][j]["FEMB0_2"]
#                else:
#                   a2 = [0]*128
#    
#                if 3 in fembs:
#                   a3 = wib_data[1][j]["FEMB1_3"]
#                else:
#                   a3 = [0]*128
#
#                if 0 in fembs or 1 in fembs:
#                   t0 = wib_data[0][j]["TMTS"]
#                else:
#                   t0 = 0
#    
#                if 2 in fembs or 3 in fembs:
#                   t1 = wib_data[1][j]["TMTS"]
#                else:
#                   t1 = 0
#   
#                aa=a0+a1+a2+a3
#                chns.append(aa)
#                tmst0.append(t0)
#                tmst1.append(t1)
#    
#            chns = list(zip(*chns))
#            sss.append(chns)
#            ttt.append([tmst0,tmst1])
#    
#        return sss,ttt
    
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
                evtdata = data[itr][nfemb][ich]
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

    def GetPeaks(self, data,  nfemb, fp, fname, funcfit=False, shapetime=2, period=500):
    
        nevent = len(data)
    
        ppk_val=[]
        npk_val=[]
        bl_val=[]
        fig,ax = plt.subplots(1,2,figsize=(12,4))
       
        for ich in range(128):
            global_ch = nfemb*128+ich
            allpls=np.zeros(period)
            npulse=0
            hasError=False
            for itr in range(nevent):
                evtdata = np.array(data[itr][nfemb][ich])
                tstart = data[itr][4]//0x20
                for tt in range(period-(tstart%period), len(evtdata)-period, period):
                    allpls = allpls + evtdata[tt:tt+period]
                    npulse = npulse+1

            apulse = allpls/npulse

            pmax = np.amax(apulse)
            maxpos = np.argmax(apulse)

            if maxpos>=30 and maxpos<len(apulse)-90:
               ax[0].plot(range(120),apulse[maxpos-30:maxpos+90])
            if maxpos<30:
               ax[0].plot(range(120),apulse[0:120])
            if maxpos>=len(apulse)-90:
                ax[0].plot(range(120),apulse[len(apulse)-120:])

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
   
        fp_bin = fp+"Pulse_{}.bin".format(fname)
        with open(fp_bin, 'wb') as fn:
             pickle.dump([ppk_val,npk_val,bl_val], fn) 
        return ppk_val,npk_val,bl_val    


#
#
#                if itr==0:
#                    peak1_pos = np.argmax(evtdata[200:period+200]) 
#                    peak_val = evtdata[peak1_pos]
#                    tmp_bl = np.mean(evtdata[peak1_pos-50:peak1_pos-150])
#                    t0 = (peak1_pos + tstart + 200)%period
#                    if abs(peak_val/tmp_bl-1)<0.04:
#                        print(fname)
#                        print("femb%d ch%d event0 doesn't have pulse, will skip this chan (peak=%d, BL=%d)"%(nfemb,ich,peak_val,tmp_bl))
#                        hasError=True
#                        break
#                start_t = period - tstart%500kk
#                  
#
#
#
#        
#                if itr==0:
#                   peak1_pos = np.argmax(evtdata[0:500]) 
#                   peak_val = evtdata[peak1_pos]
#
#                   if peak1_pos<100:
#                      tmp_bl = np.mean(evtdata[peak1_pos+200:500])
#                   else:
#                      tmp_bl = np.mean(evtdata[0:50])
#                   if abs(peak_val/tmp_bl-1)<0.04:
#                      print(fname)
#                      print("femb%d ch%d event0 doesn't have pulse, will skip this chan (peak=%d, BL=%d)"%(nfemb,ich,peak_val,tmp_bl))
#                      hasError=True
#                      break
#
#                   if peak1_pos>400 or peak1_pos<50:
#                      t0 = peak1_pos+50+np.argmax(evtdata[peak1_pos+50:peak1_pos+550])
#                      t0 = t0-200
#                      if t0<0:
#                          t0=0
#                      allpls = allpls + evtdata[t0:t0+500]
#                      t0 = tmst[0][nfemb//2][t0]
#                   else:
#                      allpls = allpls + evtdata[:500]
#                      t0 = tmst[0][nfemb//2][0]
#                   npulse=1
#
#                start_t = 500-(tmst[itr][nfemb//2][0]-t0)%500
#                end_t = len(evtdata)-500
#                for tt in range(start_t, end_t, 500):
#                    allpls = allpls + evtdata[tt:tt+500]
#                    npulse = npulse+1
#
#            if hasError:
#               ppk_val.append(peak_val)
#               npk_val.append(0)
#               bl_val.append(tmp_bl)
#               apulse = data[0][nfemb][ich] 
#               if peak1_pos>=30 and peak1_pos<len(apulse)-90:
#                  ax[0].plot(range(120),apulse[peak1_pos-30:peak1_pos+90])
#               if peak1_pos<30:
#                  ax[0].plot(range(120),apulse[0:120])
#               if peak1_pos>=len(apulse)-90:
#                   ax[0].plot(range(120),apulse[len(apulse)-120:])
#               continue
# 
#




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


    def PrintVolMON(self, fembs, mvold, fp, fsub):
        for nfemb in fembs:
            mon_dic = mvold
            df=pd.DataFrame(data=mon_dic)
            fig, ax =plt.subplots(figsize=(12,1))
            ax.axis('off')
            table = ax.table(cellText=df.values,colLabels=df.columns,loc='center')
            ax.set_title("Monitoring power rails (#mV) when " + fsub[0:-4])
            table.auto_set_font_size(False)
            table.set_fontsize(10)
            table.scale(1,2)
            newfp=fp[nfemb]+fsub[0:-4]+".png"
            plt.tight_layout()
            fig.savefig(newfp)
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
            fig, ax =plt.subplots(figsize=(10,4.5))
            ax.axis('off')
            table = ax.table(cellText=df.values,colLabels=df.columns,loc='center')
            ax.set_title("Monitoring path for FE-ADC (#mV)")
            table.set_fontsize(14)
            table.scale(1,2.2)
            newfp=fp[nfemb]+"mon_meas.png"
            plt.tight_layout()
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

    def PlotMon(self, fembs, mon_dic, savedir, fdir, fname):

        for nfemb in fembs:
            mon_list=[]

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

            fig,ax = plt.subplots(figsize=(6,4))
            xx=range(len(mon_dic))
            ax.plot(xx, mon_list, marker='.')
            ax.set_ylabel(fname)
            fp = savedir[nfemb] + fdir + "/mon_{}.png".format(fname)
            fig.savefig(fp)
            plt.close(fig)

    def PlotMonDAC(self, fembs, mon_dic, savedir, fdir, fname):

        for nfemb in fembs:

            fig,ax = plt.subplots(figsize=(10,8))

            for key,mon_list in mon_dic.items(): 
                data_list=[]
                dac_list = mon_list[1]
                mon_data = mon_list[0]
                sps = len(mon_data[0])

                for i in range(len(dac_list)):
                    sps_list=[]
                    for j in range(sps):
                        a_mon = mon_data[i][4][j][nfemb]
                        sps_list.append(a_mon)

                    if sps>1:
                       sps_list = np.array(sps_list)
                       mon_mean = np.mean(sps_list)
                    else:
                       mon_mean = sps_list[0]

                    data_list.append(mon_mean*self.fadc)

                ax.plot(dac_list, data_list, marker='.',label=key)
            ax.set_ylabel(fname)
            ax.legend()
            fp = savedir[nfemb] + fdir + "/mon_{}.png".format(fname)
            plt.savefig(fp)
            plt.close(fig)

    def PlotADCMon(self, fembs, mon_list, savedir, fdir):

        mon_items = ["VBGR", "VCMI", "VCMO", "VREFP", "VREFN", "VBGR", "VSSA", "VSSA"]
        mon_items_n=[1,2,3,4]
        nvset = len(mon_list)

        for nfemb in fembs:

            for imon in mon_items_n:
                vset_list=[]
                fig,ax = plt.subplots(figsize=(10,8))
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

                for key,values in data_dic.items():
                    ax.plot(vset_list, data_dic[key], marker='.',label=key)
                ax.set_ylabel(mon_items[imon])
                ax.legend()
                fp = savedir[nfemb] + fdir + "/mon_{}.png".format(mon_items[imon])
                plt.savefig(fp)
                plt.close(fig)

#    def CheckLinearty(self,x_np, y_np, fdir, fname, x_lo, x_hi):
#
#        delx = x_np[1]-x_np[0]
#        y1 = y_np[:-1]
#        y2 = y_np[1:]
#
#        slp1 = (y2-y1)/delx
#        slp2 = (slp1[1:]-slp1[:-1])/delx
#
#        fig1,ax1 = plt.subplots(1,2,figsize=(12,4))
#        ax1[0].plot(x_np[1:],slp1,marker='.',label='dy/dx')
#        ax1[0].set_ylabel("slope1")
#        ax1[0].legend()
#        ax1[0].set_title("first order deviation") 
#
#        ax1[1].plot(x_np[2:],slp2,marker='.',label='d^2y/dx^2')
#        ax1[1].set_ylabel("slope2")
#        ax1[1].legend()
#        ax1[1].set_title("second order deviation") 
#
#        plt.savefig(fdir+'chk_linear_{}.png'.format(fname))
#        plt.close(fig1)
#
#        non_linear_x=[]
#
#        for i in range(len(slp2)):
#            if abs(slp2[i])>5:
#               non_linear_x.append(i+2)
#
#        if not non_linear_x:
#           max_dac = x_np[-1]
#           ln_slp,ln_intercept = np.polyfit(x_np,y_np,1)           
#
#           y_max = y_np[-1]
#           y_min = y_np[0]
#           INL=0
#           for i in range(len(x_np)):
#               y_r = y_np[i]
#               y_p = x_np[i]*ln_slp + ln_intercept
#               inl = abs(y_r-y_p)/(y_max-y_min)
#               if inl>INL:
#                  INL=inl
#        else:
#           max_i = 0
#           for xx in non_linear_x:
#               if x_np[xx] in range(x_lo, x_hi):
#                  ln_slp=0
#                  INL=0
#                  max_dac=0
#                  break
#               if x_np[xx]>x_hi:
#                  max_i = xx
#                  break
#
#           if max_i>0:
#              ln_slp,ln_intercept = np.polyfit(x_np[:max_i],y_np[:max_i],1)                       
#
#              max_dac = x_np[max_i-1]
#              y_max = y_np[max_i-1]
#              y_min = y_np[0]
#              INL=0
#              for i in range(max_i):
#                  y_r = y_np[i]
#                  y_p = x_np[i]*ln_slp + ln_intercept
#                  inl = abs(y_r-y_p)/(y_max-y_min)
#                  if inl>INL:
#                     INL=inl           
#                
#        return ln_slp,INL,max_dac
#        
    def CheckLinearty(self, dac_list, pk_list, updac, lodac, chan, fp):

        dac_init=[]
        pk_init=[]
        for i in range(len(dac_list)):
            if dac_list[i]<updac and dac_list[i]>=lodac:
               dac_init.append(dac_list[i])
               pk_init.append(pk_list[i])

        try:
           slope_i,intercept_i=np.polyfit(dac_init,pk_init,1)
        except:
           fig1,ax1 = plt.subplots()
           ax1.plot(dac_init,pk_init, marker='.')
           ax1.set_xlabel("DAC")
           ax1.set_ylabel("Peak Value") 
           ax1.set_title("chan%d fail first gain fit"%chan)
           plt.savefig(fp+'fail_first_fit_ch%d.png'%chan)
           plt.close(fig1)
         
           print("fail at first gain fit")
           return 0,0,0

        y_min = pk_list[0]
        y_max = pk_list[-1]
        linear_dac_max=dac_list[-1]

        index=-1
        for i in range(len(dac_list)):
            y_r = pk_list[i]
            y_p = dac_list[i]*slope_i + intercept_i
            inl = abs(y_r-y_p)/(y_max-y_min)
            if inl>0.01:
               if dac_list[i]<5:
                  continue
               linear_dac_max = dac_list[i-1]
               index=i
               break

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
            plt.savefig(fp+'fail_inl_ch%d.png'%chan)
            plt.close(fig2)
            print("fail at first linear range searching: inl=%f for dac=0 is bigger than 0.03"%inl)
            return 0,0,0

        try:
            slope_f,intercept_f=np.polyfit(dac_list[:index],pk_list[:index],1)
        except:
            fig3,ax3 = plt.subplots()
            ax3.plot(dac_list[:index],pk_list[:index],marker='.')
            ax3.set_xlabel("DAC")
            ax3.set_ylabel("Peak Value") 
            ax3.set_title("chan%d fail second gain fit"%chan)
            plt.savefig(fp+'fail_second_fit_ch%d.png'%chan)
            plt.close(fig3)
            print("fail at second gain fit")
            return 0,0,0

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


    def GetGain(self, fembs, datadir, savedir, fdir, namepat, snc, sgs, sts, dac_list, updac=25, lodac=10):

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
        for dac in dac_list:
            fdata = datadir+namepat.format(snc,sgs,sts,dac)+'.bin'
            with open(fdata, 'rb') as fn:
                 raw = pickle.load(fn)

            rawdata = raw[0]
            pwr_meas = raw[1]

            wibdata = self.data_decode(rawdata, fembs)
            pldata = wibdata
            #tmst = np.array(tmst)

            for ifemb in fembs:
                fp = savedir[ifemb]+fdir
                if dac==0:
                   ped,rms = self.GetRMS(pldata, ifemb, fp, fname)
                   pk_list[ifemb].append(np.zeros(128)) 
                else:
                   fname_1 = namepat.format(snc,sgs,sts,dac)
                   #ppk,bpk,bl=self.GetPeaks(pldata, tmst, ifemb, fp, fname_1)
                   ppk,bpk,bl=self.GetPeaks(pldata, ifemb, fp, fname_1)
                   ppk_np = np.array(ppk)
                   bl_np = np.array(bl)
                   new_ppk = ppk_np-bl_np
                   pk_list[ifemb].append(new_ppk) 
      

        for ifemb in fembs:
            tmp_list = pk_list[ifemb]
            new_pk_list = list(zip(*tmp_list))
            #print(new_pk_list[0])

            dac_np = np.array(dac_list)
            pk_np = np.array(new_pk_list)
            fp = savedir[ifemb]+fdir
             
            gain_list = []
            inl_list = []
            max_dac_list = []
            fig,ax = plt.subplots(2,2,figsize=(12,10))
            for ch in range(128):
                #gain,inl,max_dac = self.CheckLinearty(dac_np,pk_np[ch],fp,fname,lodac,updac)
                gain,inl,max_dac = self.CheckLinearty(dac_np,pk_np[ch],updac,lodac,ch,fp)
                if gain==0:
                   print("femb%d ch%d gain is zero"%(ifemb,ch))           
                else:
                   gain = 1/gain*dac_du/1000 *CC/e
                gain_list.append(gain)
                inl_list.append(inl)
                max_dac_list.append(max_dac)
                ax[0,0].plot(dac_np,pk_np[ch])

            ax[0,0].set_ylabel("peak value")
            ax[0,0].set_xlabel("DAC")
            ax[0,0].set_title("Peak vs. DAC") 

            ax[0,1].plot(range(128),gain_list,marker='.')
            ax[0,1].set_xlabel("chan")
            ax[0,1].set_ylabel("gain")
            ax[0,1].set_title("gain") 

            ax[1,0].plot(range(128),inl_list,marker='.')
            ax[1,0].set_xlabel("chan")
            ax[1,0].set_ylabel("INL")
            ax[1,0].set_title("INL") 

            ax[1,1].plot(range(128),max_dac_list,marker='.')
            ax[1,1].set_xlabel("chan")
            ax[1,1].set_ylabel("linear_range")
            ax[1,1].set_title("linear range") 

            plt.savefig(fp+'gain_{}.png'.format(fname))
            plt.close(fig)
               
            fp_bin = fp+"Gain_{}.bin".format(fname)
            with open(fp_bin, 'wb') as fn:
                 pickle.dump( gain_list, fn)
                
    def GetENC(self, fembs, snc, sgs, sts, sgp, savedir, fdir):

        for ifemb in fembs:
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
