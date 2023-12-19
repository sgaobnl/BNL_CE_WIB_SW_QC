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
from matplotlib.backends.backend_pdf import PdfPages
import Path as newpath

def create_pdf(pdf_paths, output_path):
    # Create a PdfPages object to save the plots into a PDF
    with PdfPages(output_path) as pdf:
        for pdf_path in pdf_paths:
            # Read each PDF page using Matplotlib and append it to the PdfPages
            fig = plt.figure(figsize=(8.27, 11.69))  # A4 size
            pdf_pages = PdfPages(pdf_path)
            pdf_pages.savefig(fig)
            pdf_pages.close()
            plt.close(fig)
            pdf.attach_note(pdf_path)

def CreateFolders(fembs, fembNo, env, toytpc, datadir):

    #reportdir = "./CHK/" + datadir + "/"
    reportdir = newpath.report_dir_RTCK + "/"

    PLOTDIR = {}

    for ifemb in fembs:
        femb_no = fembNo['femb%d'%ifemb]
        plotdir = reportdir + "FEMB{}_{}_{}".format(femb_no, env, toytpc)

        if os.path.exists(plotdir):
            pass
        else:
            try:
                os.makedirs(plotdir)
            except OSError:
                print ("Error to create folder %s"%plotdir)
                sys.exit()

        plotdir = plotdir+"/"


        PLOTDIR[ifemb] = plotdir+'/'

    return PLOTDIR


def merge_pngs(png_paths, output_path):
    images = [plt.imread(png_path) for png_path in png_paths]

    # Determine the maximum height among images
    max_height = max(image.shape[0] for image in images)

    # Pad images to have the same height
    padded_images = [np.pad(image, ((0, max_height - image.shape[0]), (0, 0), (0, 0)), mode='constant') for image in images]

    # Concatenate images horizontally
    merged_image = np.concatenate(padded_images, axis=1)

    # Display the merged image
    plt.imshow(merged_image)
    plt.axis('off')

    # Save the figure as a new PNG file
    plt.savefig(output_path, bbox_inches='tight', pad_inches=0)
    plt.close()
###### Main ######
t1=time.time()
if len(sys.argv) < 2:
    print('Please specify the folder to analyze')
    exit()

if len(sys.argv) > 2:
    print('Too many arguments!')
    exit()

datadir = sys.argv[1]
#fdata = "/nfs/hothstor1/towibs/tmp/FEMB_QC_data/CHK/"+datadir+"/"
fdata = newpath.data_dir_RTCK + datadir+"/"
#fdata = "./CHK/" + datadir + "/"

#fdata = "D:/Github/BNL_CE_WIB_SW_QC_main/tmp_data/CHK/"+datadir+"/"

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

chkflag={"RMS":[],"BL":[],"Pulse_SE":{},"Pulse_DIFF":{},"PWR":[],"MON_T":[],"MON_BGP":[],"MON_ADC":{}}
chkflag["Pulse_SE"]={"PPK":[],"NPK":[],"BL":[]}
chkflag["Pulse_DIFF"]={"PPK":[],"NPK":[],"BL":[]}
chkflag["MON_ADC"]={"VCMI":[],"VCMO":[],"VREFP":[],"VREFN":[],"VSSA":[]}

badlist={"RMS":[],"BL":[],"Pulse_SE":{},"Pulse_DIFF":{},"PWR":[],"MON_T":[],"MON_BGP":[],"MON_ADC":{}}
badlist["Pulse_SE"]={"PPK":[],"NPK":[],"BL":[]}
badlist["Pulse_DIFF"]={"PPK":[],"NPK":[],"BL":[]}
badlist["MON_ADC"]={"VCMI":[],"VCMO":[],"VREFP":[],"VREFN":[],"VSSA":[]}

###### analyze RMS Raw Data ######

frms = fdata+"Raw_SE_200mVBL_14_0mVfC_2_0us_0x00.bin"
with open(frms, 'rb') as fn:
    raw = pickle.load(fn)

rmsdata = raw[0]
fembs = raw[2]

PLOTDIR=CreateFolders(fembs, fembNo, env, toytpc, datadir)

qc_tools = ana_tools()

pldata = qc_tools.data_decode(rmsdata, fembs)
#pldata = np.array(pldata)

for ifemb in range(len(fembs)):
    fp = PLOTDIR[fembs[ifemb]]
    ped,rms=qc_tools.GetRMS(pldata, fembs[ifemb], fp, "SE_200mVBL_14_0mVfC_2_0us")
    tmp = QC_check.CHKPulse(ped, 5)
    chkflag["BL"].append(tmp[0])
    badlist["BL"].append(tmp[1])

    tmp = QC_check.CHKPulse(rms, 5)
    chkflag["RMS"].append(tmp[0])
    badlist["RMS"].append(tmp[1])


###### analyze SE pulse Data ######
fpulse = fdata+"Raw_SE_900mVBL_14_0mVfC_2_0us_0x10.bin"
fname = "SE_900mVBL_14_0mVfC_2_0us_0x10"
with open(fpulse, 'rb') as fn:
    raw = pickle.load(fn)

sedata = raw[0]

pldata = qc_tools.data_decode(sedata, fembs)

#for ifemb in fembs:
for ifemb in range(len(fembs)):
    fp = PLOTDIR[fembs[ifemb]]
    ppk,npk,bl=qc_tools.GetPeaks(pldata, fembs[ifemb], fp, fname, funcfit=False)
    outfp = fp + "pulse_{}.bin".format(fname)
    with open(outfp, 'wb') as fn:
         pickle.dump([ppk,npk,bl], fn)

    tmp = QC_check.CHKPulse(ppk, 2)
    chkflag["Pulse_SE"]["PPK"].append(tmp[0])
    badlist["Pulse_SE"]["PPK"].append(tmp[1])

    tmp = QC_check.CHKPulse(npk)
    chkflag["Pulse_SE"]["NPK"].append(tmp[0])
    badlist["Pulse_SE"]["NPK"].append(tmp[1])

    tmp = QC_check.CHKPulse(bl)
    print("bl")
    chkflag["Pulse_SE"]["BL"].append(tmp[0])
    badlist["Pulse_SE"]["BL"].append(tmp[1])

fpulse = fdata+"Raw_DIFF_900mVBL_14_0mVfC_2_0us_0x10.bin"
fname = "DIFF_900mVBL_14_0mVfC_2_0us_0x10"
with open(fpulse, 'rb') as fn:
    raw = pickle.load(fn)

diffdata = raw[0]

pldata = qc_tools.data_decode(diffdata, fembs)

#for ifemb in fembs:
for ifemb in range(len(fembs)):
    fp = PLOTDIR[fembs[ifemb]]
    ppk,npk,bl=qc_tools.GetPeaks(pldata, fembs[ifemb], fp, fname)
    outfp = fp + "pulse_{}.bin".format(fname)
    with open(outfp, 'wb') as fn:
         pickle.dump([ppk,npk,bl], fn)

    tmp = QC_check.CHKPulse(ppk)
    chkflag["Pulse_DIFF"]["PPK"].append(tmp[0])
    badlist["Pulse_DIFF"]["PPK"].append(tmp[1])

    tmp = QC_check.CHKPulse(npk)
    chkflag["Pulse_DIFF"]["NPK"].append(tmp[0])
    badlist["Pulse_DIFF"]["NPK"].append(tmp[1])

    tmp = QC_check.CHKPulse(bl)
    chkflag["Pulse_DIFF"]["BL"].append(tmp[0])
    badlist["Pulse_DIFF"]["BL"].append(tmp[1])


#   mon analysis

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
#for ifemb in fembs:
for ifemb in range(len(fembs)):
    fp_pwr = PLOTDIR[fembs[ifemb]]+"pwr_meas"
    qc_tools.PrintPWR(pwr_meas, fembs[ifemb], fp_pwr)
    tmp=QC_check.CHKPWR(pwr_meas,fembs[ifemb], env)
    chkflag["PWR"].append(tmp[0])
    badlist["PWR"].append(tmp[1])

nchips=range(8)
makeplot=True
qc_tools.PrintMON(fembs, nchips, mon_refs, mon_temps, mon_adcs, PLOTDIR, makeplot)

#for ifemb in fembs:
for ifemb in range(len(fembs)):
    tmp = QC_check.CHKFET(mon_temps,fembs[ifemb],nchips, env)
    chkflag["MON_T"].append(tmp[0])
    badlist["MON_T"].append(tmp[1])

    tmp = QC_check.CHKFEBGP(mon_refs,fembs[ifemb],nchips, env)
    chkflag["MON_BGP"].append(tmp[0])
    badlist["MON_BGP"].append(tmp[1])

    tmp = QC_check.CHKADC(mon_adcs,fembs[ifemb],nchips,"VCMI",985, 40,935, 40, env)
    chkflag["MON_ADC"]["VCMI"].append(tmp[0])
    badlist["MON_ADC"]["VCMI"].append(tmp[1])

    tmp = QC_check.CHKADC(mon_adcs,fembs[ifemb],nchips,"VCMO",1272, 40, 1232, 40, env)
    chkflag["MON_ADC"]["VCMO"].append(tmp[0])
    badlist["MON_ADC"]["VCMO"].append(tmp[1])

    tmp = QC_check.CHKADC(mon_adcs,fembs[ifemb],nchips,"VREFP",1988, 40, 1980, 40, env)
    chkflag["MON_ADC"]["VREFP"].append(tmp[0])
    badlist["MON_ADC"]["VREFP"].append(tmp[1])

    tmp = QC_check.CHKADC(mon_adcs,fembs[ifemb],nchips,"VREFN",550, 40, 482, 40, env)
    chkflag["MON_ADC"]["VREFN"].append(tmp[0])
    badlist["MON_ADC"]["VREFN"].append(tmp[1])

    tmp = QC_check.CHKADC(mon_adcs,fembs[ifemb],nchips,"VSSA",105, 40, 35, 20, env)
    chkflag["MON_ADC"]["VSSA"].append(tmp[0])
    badlist["MON_ADC"]["VSSA"].append(tmp[1])


for buf in ["SE", "DIFF"]:
    fsub = "MON_PWR_" + buf + "_200mVBL_14_0mVfC_2_0us_0x00.bin"
    fpwr = fdata+ fsub
    with open(fpwr, 'rb') as fn:
        monvols = pickle.load(fn)
        vfembs = monvols[1]
        vold = monvols[0]
    vkeys = list(vold.keys())
    LSB = 2.048/16384
    for ifemb in range(len(vfembs)):
        mvold = {}
        for key in vkeys:
            f0, f1, f2, f3=zip(*vold[key])
            vfs=[f0, f1,f2,f3]
            vf = list(vfs[vfembs[ifemb]])
            vf.remove(np.max(vf))
            vf.remove(np.min(vf))
            vfm = np.mean(vf)
            vfstd = np.std(vf)
            mvold[key] = [vfm, vfstd]
    
        mvvold = {}
        for key in vkeys:
            if "GND" in key:
                mvvold[key] = [int(mvold[key][0]*LSB*1000)]
            elif "HALF" in key:
                mvvold[key.replace("_HALF", "")] = [int((mvold[key][0]-mvold["GND"][0])*LSB*2*1000)]
            else:
                mvvold[key] = [int((mvold[key][0]-mvold["GND"][0])*LSB*1000)]

    qc_tools.PrintVolMON(vfembs, mvvold, PLOTDIR, fsub)


###### Generate Report ######
#for ifemb in fembs:
for ifemb in range(len(fembs)):
    plotdir = PLOTDIR[fembs[ifemb]]

    pdf = FPDF(orientation = 'P', unit = 'mm', format='Letter')
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_auto_page_break(False,0)
    pdf.set_font('Times', 'B', 20)
    pdf.cell(85)
    pdf.l_margin = pdf.l_margin*2
    pdf.cell(30, 5, 'FEMB#{:04d} Checkout Test Report'.format(int(fembNo['femb%d'%fembs[ifemb]])), 0)
    pdf.ln(2)

    pdf.set_font('Times', '', 12)
    pdf.cell(30, 5, 'Tester: {}'.format(tester), 0)
    pdf.cell(80)
    pdf.cell(30, 5, 'Date: {}'.format(date), 0)

    pdf.cell(30, 5, 'Temperature: {}'.format(env), 0)
    pdf.cell(80)
    pdf.cell(30, 5, 'Input Capacitor(Cd): {}'.format(toytpc), 0)
    pdf.cell(30, 5, 'Note: {}'.format(note[0:80]), 0)
    pdf.cell(30, 5, 'FEMB configuration: {}, {}, {}, {}, DAC=0x{:02x}'.format("200mVBL","14_0mVfC","2_0us","500pA",0x20), 0)

    pdf.ln(10)

    chk_result = []
    err_messg = []
    chk_result.append(("Measurement","Result"))

    if chkflag["PWR"][ifemb]==False:
       chk_result.append(("Power Measurement","Pass"))
    else:
       chk_result.append(("Power Measurement","Pass"))
       err_messg.append(("Power Measurement: ",badlist["PWR"][ifemb]))
       
    if chkflag["MON_T"][ifemb]==False:
       chk_result.append(("Temperature","Pass"))
    else:
       chk_result.append(("Temperature","Fail"))
       err_messg.append(("Temperature issued chips: ",badlist["MON_T"][ifemb]))
       
    if chkflag["MON_BGP"][ifemb]==False:
       chk_result.append(("BGP","Pass"))
    else:
       chk_result.append(("BGP","Fail"))
       err_messg.append(("BGP issued chips: ",badlist["MON_BGP"][ifemb]))

    if chkflag["RMS"][ifemb]==False:
       chk_result.append(("RMS","Pass"))
    else:
       chk_result.append(("RMS","Pass"))
       err_messg.append(("RMS issued channels: ",badlist["RMS"][ifemb][0]))
       if badlist["RMS"][ifemb][1]:
          err_messg.append(("RMS issued chips: ",badlist["RMS"][ifemb][1]))
       
    if chkflag["BL"][ifemb]==False:
       chk_result.append(("200mV Baseline","Pass"))
    else:
       chk_result.append(("200mV Baseline","Pass"))
       err_messg.append(("200mV BL issued channels: ",badlist["BL"][ifemb][0]))
       if badlist["BL"][ifemb][1]:
          err_messg.append(("200mV BL issued chips: ",badlist["BL"][ifemb][1]))
      
    tmp_key = ["Pulse_SE","Pulse_DIFF"]
    for ikey in tmp_key:
        if chkflag[ikey]["PPK"][ifemb]==False and chkflag[ikey]["NPK"][ifemb]==False and chkflag[ikey]["BL"][ifemb]==False:
           chk_result.append((ikey,"Pass"))
        else:
           chk_result.append((ikey,"Pass"))
           if chkflag[ikey]["PPK"][ifemb]==True:
              err_messg.append(("%s positive peak issued channels: "%ikey,badlist[ikey]["PPK"][ifemb][0]))
              if badlist[ikey]["PPK"][ifemb][1]:
                 err_messg.append(("%s positive peak issued chips: "%ikey,badlist[ikey]["PPK"][ifemb][1]))
           
           if chkflag[ikey]["NPK"][ifemb]==True:
              err_messg.append(("%s negative peak issued channels: "%ikey,badlist[ikey]["NPK"][ifemb][0]))
              if badlist[ikey]["NPK"][ifemb][1]:
                 err_messg.append(("%s negative peak issued chips: "%ikey,badlist[ikey]["NPK"][ifemb][1]))
           
           if chkflag[ikey]["BL"][ifemb]==True:
              err_messg.append(("%s baseline issued channels: "%ikey,badlist[ikey]["BL"][ifemb][0]))
              if badlist[ikey]["BL"][ifemb][1]:
                 err_messg.append(("%s baseline issued chips: "%ikey,badlist[ikey]["BL"][ifemb][1]))
   
    len1 = len(chk_result)
    tmpkey =["VCMI","VCMO","VREFP","VREFN","VSSA"]
    for ikey in tmpkey:
        if chkflag["MON_ADC"][ikey][ifemb]==True:
           len2 = len(chk_result)
           if len2==len1:
              chk_result.append(("ADC Monitoring","Fail"))
           err_messg.append(("ADC MON %s issued chips: "%ikey,badlist["MON_ADC"][ikey][ifemb]))

    len2 = len(chk_result)
    if len2==len1:
       chk_result.append(("ADC Monitoring","Pass"))
           
    # with pdf.table() as table:
    #     for data_row in chk_result:
    #         row = table.row()
    #         for datum in data_row:
    #             row.cell(datum)

    if err_messg:
       pdf.ln(10)
       for istr in err_messg:
           pdf.cell(80, 5, "{} {}".format(istr[0],istr[1]), 0)
 
    # pdf.add_page()
    #
    # pwr_image = plotdir+"pwr_meas.png"
    # pdf.image(pwr_image,0,20,200,40)
    #
    # mon_image = plotdir+"mon_meas_plot.png"
    # pdf.image(mon_image,10,60,200,60)
    #
    # mon_image = plotdir+"MON_PWR_SE_200mVBL_14_0mVfC_2_0us_0x00.png"
    # pdf.image(mon_image,10,120,200,20)
    # mon_image = plotdir+"MON_PWR_DIFF_200mVBL_14_0mVfC_2_0us_0x00.png"
    # pdf.image(mon_image,10,140,200,20)
    #
    # mon_image = plotdir+"mon_meas.png"
    # pdf.image(mon_image,10,160,200,90)
    #
    # pdf.add_page()
    #
    # rms_image = plotdir+"rms_SE_200mVBL_14_0mVfC_2_0us.png"
    # pdf.image(rms_image,5,10,100,70)
    #
    # ped200_image = plotdir+"ped_SE_200mVBL_14_0mVfC_2_0us.png"
    # pdf.image(ped200_image,105,10,100,70)
    #
    # pulse_se_image = plotdir+"pulse_SE_900mVBL_14_0mVfC_2_0us_0x10.png"
    # pdf.image(pulse_se_image,0,80,220,70)
    #
    # pulse_diff_image = plotdir+"pulse_DIFF_900mVBL_14_0mVfC_2_0us_0x10.png"
    # pdf.image(pulse_diff_image,0,150,220,70)

    outfile = plotdir+'report.pdf'
    pdf.output(outfile)
    for measurement, result in chk_result:
        print("FEMB: " + str(ifemb), end = "    ")
        print(f"{measurement}: {result}")
    print("\n")
    print("xxxxx")
    png_paths = [plotdir+"ped_SE_200mVBL_14_0mVfC_2_0us.png", plotdir+"pulse_SE_900mVBL_14_0mVfC_2_0us_0x10.png", plotdir+"pulse_DIFF_900mVBL_14_0mVfC_2_0us_0x10.png"]
    #png_paths = ["path/to/image1.png", "path/to/image2.png", "path/to/image3.png"]

    # Replace this with the desired output path
    output_path = plotdir + "merged_output.png"

    # Merge PNGs using Matplotlib and imageio
    merge_pngs(png_paths, output_path)

    print(f"PNGs merged and saved at: {output_path}")

t2=time.time()
print(t2-t1)
