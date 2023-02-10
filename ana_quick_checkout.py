import time
import sys
import numpy as np
import pickle
import copy
import os
import time, datetime, random, statistics
from tools import ana_tools
from fpdf import FPDF

def CreateFolders(fembNo, env, toytpc, subname):

    reportdir = "reports/"
    PLOTDIR = {}

    for ifemb,femb_no in fembNo.items():
        plotdir = reportdir + "FEMB{}_{}_{}".format(femb_no, env, toytpc)
        plotdir = plotdir + subname
       
        if os.path.exists(plotdir):
           print("Folder %s exist, will overwrite"%plotdir)
        else:
           try:
               os.makedirs(plotdir)
           except OSError:
               print ("Error to create folder %s"%plotdir)
               sys.exit()

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
fdata = "tmp_data/"+datadir+"/"

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

nfemb = len(fembNo)
if datadir.count('_')==(nfemb+1):
   subname=''
else:
   loc = [i for i,x in enumerate(datadir) if x == '_']
   lastloc = loc[-1]
   subname = datadir[lastloc:]

PLOTDIR=CreateFolders(fembNo, env, toytpc, subname)

###### Load Raw Data ######

fpulse = fdata+"Raw_SE_200mVBL_14_0mVfC_2_0us_0x20.bin"
with open(fpulse, 'rb') as fn:
    raw = pickle.load(fn)

rawdata = raw[0]
pwr_meas = raw[1]

fmon = fdata+"Mon_200mVBL_14_0mVfC.bin"
with open(fmon, 'rb') as fn:
    rawmon = pickle.load(fn)

mon_refs = rawmon[0]
mon_temps = rawmon[1]
mon_adcs = rawmon[2]

qc_tools = ana_tools()

femb_list = [int(ifemb[-1]) for ifemb,_ in fembNo.items()]
print(femb_list)

pldata = qc_tools.data_decode(rawdata, femb_list)
pldata = np.array(pldata)

#nchips=[0,4]
nchips=range(8)
makeplot=True
qc_tools.PrintMON(fembNo, nchips, mon_refs, mon_temps, mon_adcs, PLOTDIR, makeplot)

###### Generate Report ######

for ifemb,femb_no in fembNo.items():
    i=int(ifemb[-1])

    plotdir = PLOTDIR[ifemb]
    ana = qc_tools.data_ana(pldata,i)
    fp_data = plotdir+"SE_response"
    qc_tools.FEMB_CHK_PLOT(ana[0], ana[1], ana[2], ana[3], ana[4], ana[5], fp_data)

    fp_pwr = plotdir+"pwr_meas"
    qc_tools.PrintPWR(pwr_meas, i, fp_pwr)

    pdf = FPDF(orientation = 'P', unit = 'mm', format='Letter')
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_auto_page_break(False,0)
    pdf.set_font('Times', 'B', 20)
    pdf.cell(85)
    pdf.l_margin = pdf.l_margin*2
    pdf.cell(30, 5, 'FEMB#{:04d} Checkout Test Report'.format(int(femb_no)), 0, 1, 'C')
    pdf.ln(2)

    pdf.set_font('Times', '', 12)
    pdf.cell(30, 5, 'Tester: {}'.format(tester), 0, 0)
    pdf.cell(80)
    pdf.cell(30, 5, 'Date: {}'.format(date), 0, 1)


    pdf.cell(30, 5, 'Temperature: {}'.format(env), 0, 0)
    pdf.cell(80)
    pdf.cell(30, 5, 'Input Capacitor(Cd): {}'.format(toytpc), 0, 1)
    pdf.cell(30, 5, 'Note: {}'.format(note[0:80]), 0, 1)
    pdf.cell(30, 5, 'FEMB configuration: {}, {}, {}, {}, DAC=0x{:02x}'.format("200mVBL","14_0mVfC","2_0us","500pA",0x20), 0, 1)

    pwr_image = fp_pwr+".png"
    pdf.image(pwr_image,0,40,200,40)

    if makeplot:
       mon_image = plotdir+"mon_meas_plot.png"
       pdf.image(mon_image,10,85,180,72)
    else:
       mon_image = plotdir+"mon_meas.png"
       pdf.image(mon_image,0,77,200,95)

    chk_image = fp_data+".png"
    pdf.image(chk_image,3,158,200,120)

    outfile = plotdir+'report.pdf'
    pdf.output(outfile, "F")

