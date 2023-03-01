from spymemory_decode import wib_spy_dec_syn
import numpy as np
import matplotlib.pyplot as plt
import pickle
import QC_constants

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

    def GetPeaks(self, data, nfemb, fp, fname):
    
        nevent = len(data)
        print(nevent)
    
        rms=[]
        ped=[]
    
        for ich in range(5):
            global_ch = nfemb*128+ich
#            peddata=np.empty(0)
#    
#            npulse=0
#            first = True
            allpls=np.zeros(500)
            for itr in range(nevent):
                evtdata = data[itr][global_ch]
#                allpls = allpls + evtdata[0:500] + evtdata[500:1000] + evtdata[1000:1500] + evtdata[1500:2000]
                plt.plot(range(500),evtdata[0:500])
                plt.plot(range(500),evtdata[500:1000])
                plt.plot(range(500),evtdata[1000:1500])
                plt.plot(range(500),evtdata[1500:2000])
#                allpls=np.append(allpls,evtdata)
            plt.show()
#    
#            ch_ped = np.mean(allpls)
#            ch_rms = np.std(allpls)
#
#            ped.append(ch_ped)
#            rms.append(ch_rms)
#    
#        fig,ax = plt.subplots(figsize=(6,4))
#        ax.plot(range(128), rms, marker='.')
#        ax.set_title(fname)
#        ax.set_xlabel("chan")
#        ax.set_ylabel("rms")
#        fp_fig = fp+"rms_{}.png".format(fname)
#        plt.savefig(fp_fig)
#        plt.close(fig)
#
#        fig,ax = plt.subplots(figsize=(6,4))
#        ax.plot(range(128), ped, marker='.')
#        ax.set_title(fname)
#        ax.set_xlabel("chan")
#        ax.set_ylabel("ped")
#        fp_fig = fp+"ped_{}.png".format(fname)
#        plt.savefig(fp_fig)
#        plt.close(fig)
#    
#        fp_bin = fp+"RMS_{}.bin".format(fname)
#        with open(fp_bin, 'wb') as fn:
#             pickle.dump( [ped, rms], fn)
#    
#        return ped,rms
#
