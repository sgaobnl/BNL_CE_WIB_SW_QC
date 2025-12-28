import numpy as np

#   current measurement parameter
bias_low = 4.2; bias_high = 5.1;    bias_i_high = 0.05
fe_v_low = 2.9; fe_v_high = 3;      fe_i_low = 0.35;    fe_i_high = 0.55

def CHKPWR(data, nfemb, env):

    BAD = False  
    bad_list=[]
  
    bias_v = data['FEMB%d_BIAS_V'%nfemb]
    bias_i = data['FEMB%d_BIAS_I'%nfemb]

    fe_v = data['FEMB%d_DC2DC0_V'%nfemb]
    fe_i = data['FEMB%d_DC2DC0_I'%nfemb]

    cd_v = data['FEMB%d_DC2DC1_V'%nfemb]
    cd_i = data['FEMB%d_DC2DC1_I'%nfemb]

    adc_v = data['FEMB%d_DC2DC2_V'%nfemb]
    adc_i = data['FEMB%d_DC2DC2_I'%nfemb]

    if bias_v>bias_high or bias_v<bias_low:
       BAD = True 
       bad_list.append("bias voltage")
    if abs(bias_i)>bias_i_high:
       BAD = True
       bad_list.append("bias current")

    if fe_v>fe_v_high or fe_v<fe_v_low:
       BAD = True 
       bad_list.append("LArASIC voltage")
    if fe_i>fe_i_high or fe_i<fe_i_low:
       BAD = True 
       bad_list.append("LArASIC current")

    if cd_v>3 or cd_v<2.90:
       BAD = True 
       bad_list.append("COLDATA voltage")
    if cd_i>0.35 or cd_i<0.15:
       BAD = True 
       bad_list.append("COLDATA current")

    if adc_v>3.6 or adc_v<3.30:
       BAD = True 
       bad_list.append("ColdADC voltage")
    if adc_i>1.95 or adc_i<1.35:
       BAD = True 
       bad_list.append("ColdADC current")

    return BAD,bad_list


def CHKFET(data, nfemb, nchips, env):

    fadc = 1/(2**14)*2048 # mV
    badlist=[]

    if env=='RT':
       lo = 890
       hi = 990

    if env=='LN':
       lo = 350
       hi = 250

    BAD = False

    for i in nchips: # 8 chips per board
        fe_t = data[f'chip{i}'][0][nfemb]*fadc
        if fe_t<lo or fe_t>hi:
           BAD = True 
           badlist.append(i)
 
    return BAD,badlist

def CHKFEBGP(data, nfemb, nchips, env):

    fadc = 1/(2**14)*2048 # mV

    if env=='RT':
       lo = 1260-50
       hi = 1260+50

    if env=='LN':
       lo = 1180-50
       hi = 1180+50

    BAD = False
    badlist=[]

    for i in nchips: # 8 chips per board
        fe_bgp = data[f'chip{i}'][0][nfemb]*fadc
        if fe_bgp<lo or fe_bgp>hi:
           BAD = True 
           badlist.append(i)
 
    return BAD,badlist

def CHKADC(data, nfemb, nchips, key, rtm, rterrbar, lnm, lnerrbar, env):

    fadc = 1/(2**14)*2048 # mV

    BAD = False
    badlist=[]

    if env=='RT':
       lo = rtm-rterrbar
       hi = rtm+rterrbar

    if env=='LN':
       lo = lnm-lnerrbar
       hi = lnm+lnerrbar

    for i in nchips: # 8 chips per board
        vcmi = data[f'chip{i}'][key][1][0][nfemb]*fadc

        if vcmi<lo or vcmi>hi:
           BAD = True 
           badlist.append(i)
 
    return BAD,badlist


def CHKPulse(para, para_range = 0.6, errbar=10, refmean = 0, type = 'rms'):  # assume the input is a list
    # para_range    rms : para_range = 7     ped : para_range = 350
    print("start check pulse")
    int_para = [int(x) for x in para]
    para_np = np.array(int_para)
    tmp_std = np.std(para_np)
    if type == '25mVfC':
        para_med = (np.max(para_np)+np.min(para_np))/2
    else:
        para_med = np.mean(para_np)

    # refine_para = [x for x in para_np if (abs(x - para_med) < para_range)]
    # fit_range = errbar * np.std(refine_para)

    flag = True
    bad_chan=[]
    bad_chip=[]
    pulse_mean = []
    pulse_max = []
    pulse_min = []
#   半高全宽
    if type == 'rms':
        for ch in range(128):
            pulse_mean.append(np.mean(para_np[ch]))
            pulse_max.append(np.max(para_np[ch]))
            pulse_min.append(np.min(para_np[ch]))
            if (abs(para_np[ch]-para_med)/para_med > para_range):
                flag = False
                bad_chan.append(ch)
                bad_chip.append(ch//16)
    else:
        for ch in range(128):
            pulse_mean.append(np.mean(para_np[ch]))
            pulse_max.append(np.max(para_np[ch]))
            pulse_min.append(np.min(para_np[ch]))
            if (abs(para_np[ch]-para_med) > para_range):
                flag = False
                bad_chan.append(ch)
                bad_chip.append(ch//16)


    return flag,[bad_chan,bad_chip], para_med, tmp_std, pulse_mean, pulse_max, pulse_min
       
def csvPulse(para, para_range = 0.4, errbar=10, refmean = 0, type = 'rms'):  # assume the input is a list
    # para_range    rms : para_range = 7     ped : para_range = 350
    print("start check pulse")
    int_para = [int(x) for x in para]
    para_np = np.array(int_para)
    tmp_std = np.std(para_np)
    if type == '25mVfC':
        para_med = (np.max(para_np)+np.min(para_np))/2
    else:
        para_med = np.mean(para_np)

    # refine_para = [x for x in para_np if (abs(x - para_med) < para_range)]
    # fit_range = errbar * np.std(refine_para)

    flag = True
    bad_chan=[]
    bad_chip=[]
    pulse_mean = []
    pulse_max = []
    pulse_min = []
#   半高全宽
    if type == 'rms':
        for ch in range(128):
            pulse_mean.append(np.mean(para_np[ch]))
            pulse_max.append(np.max(para_np[ch]))
            pulse_min.append(np.min(para_np[ch]))
            if (abs(para_np[ch]-para_med)/para_med > para_range):
                flag = False
                bad_chan.append(ch)
                bad_chip.append(ch//16)
    else:
        for ch in range(128):
            pulse_mean.append(np.mean(para_np[ch]))
            pulse_max.append(np.max(para_np[ch]))
            pulse_min.append(np.min(para_np[ch]))
            if (abs(para_np[ch]-para_med) > para_range):
                flag = False
                bad_chan.append(ch)
                bad_chip.append(ch//16)


    return flag,[bad_chan,bad_chip], para_med, tmp_std, pulse_mean, pulse_max, pulse_min
#    def ChkRMS(self, env, fp, fname, snc, sgs, sts):
#
#        infile = fp+"RMS_{}.bin".format(fname)
#        with open(infile, 'rb') as fn:
#            raw = pickle.load(fn)
#
#        ped = raw[0]
#        rms = raw[1]
#
#        if env=='LN':
#           if snc==0:
#              ped_std = 0.01
#           else:
#              ped_std = 0.07
#           ped_lo = QC_constants.PED_LN_mean[snc][sgs][sts]*(1-ped_std)
#           ped_hi = QC_constants.PED_LN_mean[snc][sgs][sts]*(1+ped_std)
#
#           rms_lo = QC_constants.RMS_LN_mean[snc][sgs][sts]*(1-0.06)
#           rms_hi = QC_constants.RMS_LN_mean[snc][sgs][sts]*(1+0.06)
#
#        if env=='RT':
#           if snc==0:
#              ped_std = 0.01
#           else:
#              ped_std = 0.07
#           ped_lo = QC_constants.PED_RT_mean[snc][sgs][sts]*(1-ped_std)
#           ped_hi = QC_constants.PED_RT_mean[snc][sgs][sts]*(1+ped_std)
#
#           rms_lo = QC_constants.RMS_RT_mean[snc][sgs][sts]*(1-0.06)
#           rms_hi = QC_constants.RMS_RT_mean[snc][sgs][sts]*(1+0.06)
#
#        outfile = open(fp+"issued_channels_ped_rms.txt", "a")
#        outfile.write("%s %s %s %s\n"%(env, QC_constants.SNC[snc], QC_constants.SGS[sgs], QC_constants.STS[sts]))
#        outfile.write("\n")
#
#        nfail=0
#        for ch in range(128):
#            failed=False
#            if ped[ch]<ped_lo:
#               outfile.write("ch%d low pedestal %f\n"%(ch,ped[ch]))
#               failed=True
#            if ped[ch]>ped_hi:
#               outfile.write("ch%d high pedestal %f\n"%(ch,ped[ch]))
#               failed=True
#
#            if rms[ch]<rms_lo:
#               outfile.write("ch%d low rms %f\n"%(ch,rms[ch]))
#               failed=True
#            if rms[ch]>rms_hi:
#               outfile.write("ch%d high rms %f\n"%(ch,rms[ch]))
#               failed=True
#
#            if failed:
#               nfail = nfail+1
#
#        outfile.write("\n")
#
#        return nfail
#
