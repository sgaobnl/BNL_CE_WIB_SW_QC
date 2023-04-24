import time
import sys
import numpy as np
import pickle
import copy
import os
import time, datetime, random, statistics
from QC_tools import ana_tools
import QC_check
from fpdf import FPDF
import matplotlib.pyplot as plt


def CreateFolders(fembs, fembNo, env, toytpc):

    #reportdir = "/nfs/hothstor1/towibs/tmp/FEMB_QC_reports/CHK/"+datadir+"/"
    reportdir = "reports/"+datadir+"/"
    PLOTDIR = {}

    for ifemb in fembs:
        femb_no = fembNo['femb%d'%ifemb]
        plotdir = reportdir + "FEMB{}_{}_{}".format(femb_no, env, toytpc)

        n=1
        while (os.path.exists(plotdir)):
            if n==1:
                plotdir = plotdir + "_R{:03d}".format(n)
            else:
                plotdir = plotdir[:-3] + "{:03d}".format(n)
            n=n+1
            if n>20:
                raise Exception("There are more than 20 folders for FEMB %d..."%femb_no)

        try:
            os.makedirs(plotdir)
        except OSError:
            print ("Error to create folder %s"%plotdir)
            sys.exit()

        plotdir = plotdir+"/"


        PLOTDIR[ifemb] = plotdir+'/'

    return PLOTDIR

###### Main ######

if len(sys.argv) < 2:
    print('Please specify the folder to analyze')
    exit()

if len(sys.argv) > 2:
    print('Too many arguments!')
    exit()

datadir = sys.argv[1]
#fdata = "/nfs/hothstor1/towibs/tmp/FEMB_QC_data/CHK/"+datadir+"/"
fdata = "tmp_data/"+datadir+"/"
print(fdata)

###### load logs and create report folder ######
flog = fdata+"logs_env.bin"
with open(flog, 'rb') as fn:
    evlog = pickle.load(fn)

tester = evlog['tester']
env = evlog['env']
toytpc = evlog['toytpc']
note = evlog['note']
fembNo = evlog['femb id']
date = evlog['date']

###### analyze RMS Raw Data ######

frms = fdata+"Raw_SE_200mVBL_14_0mVfC_2_0us_0x00.bin"
with open(frms, 'rb') as fn:
    raw = pickle.load(fn)

rmsdata = raw[0]
fembs = raw[2]

PLOTDIR=CreateFolders(fembs, fembNo, env, toytpc)

qc_tools = ana_tools()

pldata,_ = qc_tools.data_decode(rmsdata, fembs)
pldata = np.array(pldata)

for ifemb in fembs:
    fp = PLOTDIR[ifemb]
    ped,rms=qc_tools.GetRMS(pldata, ifemb, fp, "SE_200mVBL_14_0mVfC_2_0us")
#    qc_tools.ChkRMS(env, fp, "SE_200mVBL_14_0mVfC_2_0us", 1, 0, 3)

fpulse = fdata+"Raw_SE_900mVBL_14_0mVfC_2_0us_0x10.bin"
fname = "SE_900mVBL_14_0mVfC_2_0us_0x10"
with open(fpulse, 'rb') as fn:
    raw = pickle.load(fn)

sedata = raw[0]

pldata,tmst = qc_tools.data_decode(sedata, fembs)
pldata = np.array(pldata)
tmst = np.array(tmst)

plflag_se=np.zeros(4)
plcheck_SE=[[]]*4

for ifemb in fembs:
    fp = PLOTDIR[ifemb]
    ppk,npk,bl=qc_tools.GetPeaks(pldata, tmst, ifemb, fp, fname, funcfit=False)
    outfp = fp + "pulse_{}.bin".format(fname)
    with open(outfp, 'wb') as fn:
         pickle.dump([ppk,npk,bl], fn)

    tmp = QC_check.CHKPulse(ppk)
    if tmp[0]==False:
       plflag_se[ifemb]=4
    plcheck_SE[ifemb].append(tmp)

    tmp = QC_check.CHKPulse(npk)
    if tmp[0]==False:
       plflag_se[ifemb]=4
    plcheck_SE[ifemb].append(tmp)

    tmp = QC_check.CHKPulse(bl)
    if tmp[0]==False:
       plflag_se[ifemb]=4
    plcheck_SE[ifemb].append(tmp)
    

fpulse = fdata+"Raw_DIFF_900mVBL_14_0mVfC_2_0us_0x10.bin"
fname = "DIFF_900mVBL_14_0mVfC_2_0us_0x10"
with open(fpulse, 'rb') as fn:
    raw = pickle.load(fn)

diffdata = raw[0]

pldata,tmst = qc_tools.data_decode(diffdata, fembs)
pldata = np.array(pldata)
tmst = np.array(tmst)

plflag_diff=np.zeros(4)
plcheck_DIFF=[[]]*4

for ifemb in fembs:
    fp = PLOTDIR[ifemb]
    ppk,npk,bl=qc_tools.GetPeaks(pldata, tmst, ifemb, fp, fname)
    outfp = fp + "pulse_{}.bin".format(fname)
    with open(outfp, 'wb') as fn:
         pickle.dump([ppk,npk,bl], fn)

    tmp = QC_check.CHKPulse(ppk)
    if tmp[0]==False:
       plflag_diff[ifemb]=5
    plcheck_DIFF[ifemb].append(tmp)

    tmp = QC_check.CHKPulse(npk)
    if tmp[0]==False:
       plflag_diff[ifemb]=5
    plcheck_DIFF[ifemb].append(tmp)

    tmp = QC_check.CHKPulse(bl)
    if tmp[0]==False:
       plflag_diff[ifemb]=5
    plcheck_DIFF[ifemb].append(tmp)

fmon = fdata+"Mon_200mVBL_14_0mVfC.bin"
with open(fmon, 'rb') as fn:
    rawmon = pickle.load(fn)

mon_refs = rawmon[0]
mon_temps = rawmon[1]
mon_adcs = rawmon[2]

fpwr = fdata+"PWR_SE_200mVBL_14_0mVfC_2_0us_0x00.bin"
with open(fpwr, 'rb') as fn:
    rawpwr = pickle.load(fn)

pwr_meas=rawpwr[0]
pwrflag=np.zeros(4)
for ifemb in fembs:
    fp_pwr = PLOTDIR[ifemb]+"pwr_meas"
    qc_tools.PrintPWR(pwr_meas, ifemb, fp_pwr)
    pwrflag[ifemb]=QC_check.CHKPWR(pwr_meas,ifemb)

nchips=range(8)
makeplot=True
qc_tools.PrintMON(fembs, nchips, mon_refs, mon_temps, mon_adcs, PLOTDIR, makeplot)

montflag = np.zeros(4)
monbgpflag = np.zeros(4)
for ifemb in fembs:
    montflag[ifemb] = QC_check.CHKFET(mon_temps,ifemb,nchips,env)
    monbgpflag[ifemb] = QC_check.CHKFEBGP(mon_refs,ifemb,nchips)

###### Generate Report ######

for ifemb in fembs:
    plotdir = PLOTDIR[ifemb]

    pdf = FPDF(orientation = 'P', unit = 'mm', format='Letter')
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_auto_page_break(False,0)
    pdf.set_font('Times', 'B', 20)
    pdf.cell(85)
    pdf.l_margin = pdf.l_margin*2
    pdf.cell(30, 5, 'FEMB#{:04d} Checkout Test Report'.format(int(fembNo['femb%d'%ifemb])), 0, new_x="LMARGIN", new_y="NEXT", align='C')
    pdf.ln(2)

    pdf.set_font('Times', '', 12)
    pdf.cell(30, 5, 'Tester: {}'.format(tester), 0, new_x="RIGHT", new_y="TOP")
    pdf.cell(80)
    pdf.cell(30, 5, 'Date: {}'.format(date), 0, new_x="LMARGIN", new_y="NEXT")

    pdf.cell(30, 5, 'Temperature: {}'.format(env), 0, new_x="RIGHT", new_y="TOP")
    pdf.cell(80)
    pdf.cell(30, 5, 'Input Capacitor(Cd): {}'.format(toytpc), 0, new_x="LMARGIN", new_y="NEXT")
    pdf.cell(30, 5, 'Note: {}'.format(note[0:80]), 0, new_x="LMARGIN", new_y="NEXT")
    pdf.cell(30, 5, 'FEMB configuration: {}, {}, {}, {}, DAC=0x{:02x}'.format("200mVBL","14_0mVfC","2_0us","500pA",0x20), 0, new_x="LMARGIN", new_y="NEXT")

    pdf.ln(10)

    chk_result = ( ("Test", "Result"),
                   ("Power Measurement", "Pass" if pwrflag[ifemb]==0 else "Fail"),
                   ("Temperature", "Pass" if montflag[ifemb]==0 else "Fail"),
                   ("Bandgap", "Pass" if monbgpflag[ifemb]==0 else "Fail"),
                   ("SE Pulse Shapes", "Pass" if plflag_se[ifemb]==0 else "Fail"),
                   ("DIFF Pulse Shapes", "Pass" if plflag_diff[ifemb]==0 else "Fail")
                 )

    with pdf.table() as table:
        for data_row in chk_result:
            row = table.row()
            for datum in data_row:
                row.cell(datum)

    if plflag_se[ifemb]>0:
       pdf.ln(10)
       for jj in plcheck_SE[ifemb]:
           if jj[0]==True:
              continue

           if len(jj[1])>0:
              pdf.cell(30, 5, 'SE: Bad channels: {}'.format(jj[1]), 0, new_x="LMARGIN", new_y="NEXT")
 
           if len(jj[2])>0:
              pdf.cell(30, 5, 'SE: Bad chips: {}'.format(jj[2]), 0, new_x="LMARGIN", new_y="NEXT")

    if plflag_diff[ifemb]>0:
       pdf.ln(10)
       for jj in plcheck_DIFF[ifemb]:
           if jj[0]==True:
              continue

           if len(jj[1])>0:
              pdf.cell(30, 5, 'DIFF: Bad channels: {}'.format(jj[1]), 0, new_x="LMARGIN", new_y="NEXT")
 
           if len(jj[2])>0:
              pdf.cell(30, 5, 'DIFF: Bad chips: {}'.format(jj[2]), 0, new_x="LMARGIN", new_y="NEXT")


    pdf.add_page()

    pwr_image = plotdir+"pwr_meas.png"
    pdf.image(pwr_image,0,40,200,40)

    mon_image = plotdir+"mon_meas_plot.png"
    pdf.image(mon_image,10,85,180,72)

    mon_image = plotdir+"mon_meas.png"
    pdf.image(mon_image,0,157,200,95)

    pdf.add_page()

    rms_image = plotdir+"rms_SE_200mVBL_14_0mVfC_2_0us.png"
    pdf.image(rms_image,5,10,100,70)

    ped200_image = plotdir+"ped_SE_200mVBL_14_0mVfC_2_0us.png"
    pdf.image(ped200_image,105,10,100,70)

    pulse_se_image = plotdir+"pulse_SE_900mVBL_14_0mVfC_2_0us_0x10.png"
    pdf.image(pulse_se_image,0,80,220,70)

    pulse_diff_image = plotdir+"pulse_DIFF_900mVBL_14_0mVfC_2_0us_0x10.png"
    pdf.image(pulse_diff_image,0,150,220,70)

    outfile = plotdir+'report.pdf'
    pdf.output(outfile)

