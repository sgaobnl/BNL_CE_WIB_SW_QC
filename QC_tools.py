from spymemory_decode import wib_spy_dec_syn

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
    
    def GetRMS(self, data, nfemb, snc, sgs, sts, fp, fname):
    
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
    
        fp_bin = fp+"RMS_{}.bin".format(fname)
        with open(fp_bin, 'wb') as fn:
             pickle.dump( [ped, rms], fn)
    
        return ped,rms
    