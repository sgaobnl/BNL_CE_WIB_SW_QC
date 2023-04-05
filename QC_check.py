def CHKPWR(data, nfemb):

    BAD = False  
  
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
    if abs(bias_i)>0.05:
       BAD = True 

    if fe_v>3 or fe_v<2.9:
       BAD = True 
    if fe_i>0.55 or fe_i<0.35:
       BAD = True 

    if cd_v>3 or cd_v<2.95:
       BAD = True 
    if cd_i>0.35 or cd_i<0.15:
       BAD = True 

    if adc_v>3.5 or adc_v<3.38:
       BAD = True 
    if adc_i>1.85 or adc_i<1.35:
       BAD = True 

    if BAD:
       return 1
    else:
       return 0


def CHKFET(data, nfemb, nchips, env):

    fadc = 1/(2**14)*2048 # mV

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
 
    if BAD:
       return 2
    else:
       return 0

def CHKFEBGP(data, nfemb, nchips):

    fadc = 1/(2**14)*2048 # mV

    lo = 1100
    hi = 1300

    BAD = False

    for i in nchips: # 8 chips per board
        fe_bgp = data[f'chip{i}'][0][nfemb]*fadc
        if fe_bgp<lo or fe_bgp>hi:
           BAD = True 
 
    if BAD:
       return 3
    else:
       return 0



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
