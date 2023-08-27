import numpy as np
def CHKPWR(data, nfemb):

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

    if bias_v>5 or bias_v<4.95:
       BAD = True 
       bad_list.append("bias voltage")
    if abs(bias_i)>0.05:
       BAD = True
       bad_list.append("bias current")

    if fe_v>3 or fe_v<2.9:
       BAD = True 
       bad_list.append("LArASIC voltage")
    if fe_i>0.55 or fe_i<0.35:
       BAD = True 
       bad_list.append("LArASIC current")

    if cd_v>3 or cd_v<2.95:
       BAD = True 
       bad_list.append("COLDATA voltage")
    if cd_i>0.35 or cd_i<0.15:
       BAD = True 
       bad_list.append("COLDATA current")

    if adc_v>3.5 or adc_v<3.38:
       BAD = True 
       bad_list.append("ColdADC voltage")
    if adc_i>1.85 or adc_i<1.35:
       BAD = True 
       bad_list.append("ColdADC current")

    return BAD,bad_list


def CHKFET(data, nfemb, nchips, env):

    fadc = 1/(2**14)*2048 # mV
    badlist=[]

    if env=='RT':
       lo = 850
       hi = 950

    if env=='LN':
       lo = 310
       hi = 250

    BAD = False

    for i in nchips: # 8 chips per board
        fe_t = data[f'chip{i}'][0][nfemb]*fadc
        if fe_t<lo or fe_t>hi:
           BAD = True 
           badlist.append(i)
 
    return BAD,badlist

def CHKFEBGP(data, nfemb, nchips):

    fadc = 1/(2**14)*2048 # mV

    lo = 1100
    hi = 1300

    BAD = False
    badlist=[]

    for i in nchips: # 8 chips per board
        fe_bgp = data[f'chip{i}'][0][nfemb]*fadc
        if fe_bgp<lo or fe_bgp>hi:
           BAD = True 
           badlist.append(i)
 
    return BAD,badlist

def CHKADC(data, nfemb, nchips, key, lo, hi):

    fadc = 1/(2**14)*2048 # mV

    BAD = False
    badlist=[]

    for i in nchips: # 8 chips per board
        vcmi = data[f'chip{i}'][key][1][0][nfemb]*fadc

        if vcmi<lo or vcmi>hi:
           BAD = True 
           badlist.append(i)
 
    return BAD,badlist


def CHKPulse(data, errbar=3):  # assume the input is a list
    data_np = np.array(data)
    tmp_max = np.max(data_np) 
    tmp_max_pos = np.argmax(data_np) 
    tmp_min = np.min(data_np) 
    tmp_min_pos = np.argmin(data_np) 
    tmp_data = np.delete(data_np, [tmp_max_pos,tmp_min_pos])
    tmp_mean = np.mean(data_np) 
    tmp_std = np.std(data_np) 

    flag = False
    bad_chan=[]
    bad_chip=[]

    for ch in range(128):
        if abs(data_np[ch]-tmp_mean)>tmp_std*3:
           flag = True
           bad_chan.append(ch)
           bad_chip.append(ch//16)

    return flag,[bad_chan,bad_chip]
       

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
