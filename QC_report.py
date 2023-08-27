import pickle
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
import sys
import time
import glob
from QC_tools import ana_tools
import QC_check
from fpdf import FPDF
import argparse

class QC_reports:

      def __init__(self, fdir, fembs=[]):

          savedir = "./QC_reports/"
          self.datadir = "./tmp_data/"+fdir+"/"

#          savedir = "/nfs/hothstor1/towibs/tmp/FEMB_QC_reports/QC/"+fdir+"/"
#          self.datadir = "/nfs/hothstor1/towibs/tmp/FEMB_QC_data/QC/"+fdir+"/"

          fp = self.datadir+"logs_env.bin"
          with open(fp, 'rb') as fn:
               logs = pickle.load(fn)
         
          logs["datadir"]=self.datadir
          self.logs=logs

          self.fembsID={}
          if fembs:
              self.fembs = fembs
              for ifemb in fembs:
                  self.fembsID[f'femb{ifemb}'] = logs['femb id'][f'femb{ifemb}']
          else:
              self.fembsID=logs['femb id']
              self.fembs=[]
              for key,value in logs['femb id'].items():
                  self.fembs.append(int(key[-1]))

          self.savedir={}
          print("Will analyze the following fembs: ", self.fembs)

          ##### create results dir for each FEMB #####
          for ifemb in self.fembs:
              fembid = self.fembsID[f'femb{ifemb}']
              one_savedir = savedir+"FEMB{}_{}_{}".format(fembid, logs["env"], logs["toytpc"])

              n=1
              while (os.path.exists(one_savedir)):
                  if n==1:
                      one_savedir = one_savedir + "_R{:03d}".format(n)
                  else:
                      one_savedir = one_savedir[:-3] + "{:03d}".format(n)
                  n=n+1
                  if n>20:
                      raise Exception("There are more than 20 folders...")

              try:
                  os.makedirs(one_savedir)
              except OSError:
                  print ("Error to create folder %s"%one_savedir)
                  sys.exit()

              self.savedir[ifemb]=one_savedir+"/"

              fp = self.savedir[ifemb] + "logs_env.bin"
              with open(fp, 'wb') as fn:
                   pickle.dump(self.logs, fn)

      def CreateDIR(self, fdir):

          for ifemb in self.fembs:
              fp = self.savedir[ifemb] + fdir + "/"
              if not os.path.exists(fp):
                 try:
                     os.makedirs(fp)
                 except OSError:
                     print ("Error to create folder %s"%fp)
                     sys.exit()

      def GEN_PWR_PDF(self,fdir,femb_id):

          pdf = FPDF(orientation = 'P', unit = 'mm', format='Letter')
          pdf.alias_nb_pages()
          pdf.add_page()
          pdf.set_auto_page_break(False,0)
          pdf.set_font('Times', 'B', 20)
          pdf.cell(85)
          pdf.l_margin = pdf.l_margin*2
          pdf.cell(30, 5, 'FEMB#{:04d} Power Test Report'.format(femb_id), 0, 1, 'C')
          pdf.ln(2)
          
          pdf.set_font('Times', '', 12)
          pdf.cell(30, 5, 'Tester: {}'.format(self.logs["tester"]), 0, 0)
          pdf.cell(80)
          pdf.cell(30, 5, 'Date: {}'.format(self.logs["date"]), 0, 1)
          
          pdf.cell(30, 5, 'Temperature: {}'.format(self.logs["env"]), 0, 0)
          pdf.cell(80)
          pdf.cell(30, 5, 'Input Capacitor(Cd): {}'.format(self.logs["toytpc"]), 0, 1)
          pdf.cell(30, 5, 'Note: {}'.format(self.logs["note"][0:80]), 0, 1)
          pdf.cell(30, 5, 'FEMB configuration: {}, {}, {}, {}, DAC=0x{:02x}'.format("200mVBL","14_0mVfC","2_0us","500pA",0x20), 0, 1)
         
          pwr_images = sorted(glob.glob(fdir+"*_pwr_meas.png"), key=os.path.getmtime)
          nn=0
          for im in pwr_images:
              if '\\' in im:
                  im_name = im.split("\\")[-1][4:-13]
              else:
                  im_name = im.split("/")[-1][4:-13]
              pdf.set_font('Times', 'B', 14)
              if nn<3:
                 pdf.text(55, 45+50*nn, im_name)  
                 pdf.image(im,0,47+nn*50,200, 40)
              else:
                 if nn%3==0:
                    pdf.add_page()
                 pdf.text(55, 10+50*(nn-3), im_name)  
                 pdf.image(im,0,12+(nn-3)*50,200, 40)
              nn=nn+1
          
          pdf.alias_nb_pages()
          pdf.add_page()
          
          chk_images = sorted(glob.glob(fdir+"pulse_*.png"), key=os.path.getmtime)
          nn=0
          for im in chk_images:
              if '\\' in im:
                  im_name = im.split("\\")[-1][6:-4]
              else:
                  im_name = im.split("/")[-1][6:-4]

              pdf.set_font('Times', 'B', 14)
              if nn<3:
                 pdf.text(55, 10+nn*80, im_name)  
                 pdf.image(im,0,12+nn*80,220,70)
              else:
                 if nn%3==0:
                    pdf.alias_nb_pages()
                    pdf.add_page()
                 pdf.text(55, 10+(nn-3)*80, im_name)  
                 pdf.image(im,0,12+(nn-3)*80,220,70)
              nn=nn+1
          
          outfile = fdir+'report.pdf'
          pdf.output(outfile, "F")
         
      def PWR_consumption_report(self):
          
          self.CreateDIR("PWR_Meas")
          datadir = self.datadir+"PWR_Meas/"

          qc=ana_tools()

          f_pwr = datadir+"PWR_SE_200mVBL_14_0mVfC_2_0us_0x00.bin"
          with open(f_pwr, 'rb') as fn:
               pwr_meas = pickle.load(fn)[1]

          f_pl = datadir+"PWR_SE_200mVBL_14_0mVfC_2_0us_0x20.bin"
          with open(f_pl, 'rb') as fn:
               rawdata = pickle.load(fn)[0]

          pldata = qc.data_decode(rawdata, self.fembs)

          for ifemb in self.fembs:
              fp_pwr = self.savedir[ifemb] + "PWR_Meas/PWR_SE_200mVBL_14_0mVfC_2_0us_pwr_meas"
              qc.PrintPWR(pwr_meas, ifemb, fp_pwr)

              fp = self.savedir[ifemb] + "PWR_Meas/"
              qc.GetPeaks(pldata, ifemb, fp, "PWR_SE_200mVBL_14_0mVfC_2_0us")

          f_pwr = datadir+"PWR_DIFF_200mVBL_14_0mVfC_2_0us_0x00.bin"
          with open(f_pwr, 'rb') as fn:
               pwr_meas = pickle.load(fn)[1]

          f_pl = datadir+"PWR_DIFF_200mVBL_14_0mVfC_2_0us_0x20.bin"
          with open(f_pl, 'rb') as fn:
               rawdata = pickle.load(fn)[0]

          pldata = qc.data_decode(rawdata, self.fembs)

          for ifemb in self.fembs:
              fp_pwr = self.savedir[ifemb] + "PWR_Meas/PWR_DIFF_200mVBL_14_0mVfC_2_0us_pwr_meas"
              qc.PrintPWR(pwr_meas, ifemb, fp_pwr)

              fp = self.savedir[ifemb] + "PWR_Meas/"
              qc.GetPeaks(pldata, ifemb, fp, "PWR_DIFF_200mVBL_14_0mVfC_2_0us")

          f_pwr = datadir+"PWR_SE_SDF_200mVBL_14_0mVfC_2_0us_0x00.bin"
          with open(f_pwr, 'rb') as fn:
               pwr_meas = pickle.load(fn)[1]

          f_pl = datadir+"PWR_SE_SDF_200mVBL_14_0mVfC_2_0us_0x20.bin"
          with open(f_pl, 'rb') as fn:
               rawdata = pickle.load(fn)[0]

          pldata= qc.data_decode(rawdata, self.fembs)

          for ifemb in self.fembs:
              fp_pwr = self.savedir[ifemb] + "PWR_Meas/PWR_SE_SDF_200mVBL_14_0mVfC_2_0us_pwr_meas"
              qc.PrintPWR(pwr_meas, ifemb, fp_pwr)

              fp = self.savedir[ifemb] + "PWR_Meas/"
              qc.GetPeaks(pldata, ifemb, fp, "PWR_SE_SDF_200mVBL_14_0mVfC_2_0us")

          for ifemb in self.fembs:
              fdir = self.savedir[ifemb] + "PWR_Meas/"
              fembid = int(self.fembsID[f'femb{ifemb}'])
              self.GEN_PWR_PDF(fdir, fembid)

      def PWR_cycle_report(self):

          if 'RT' in self.logs['env']:
              return

          self.CreateDIR("PWR_Cycle")
          datadir = self.datadir+"PWR_Cycle/"

          qc=ana_tools()

          for i in range(3):
              f_pwr = datadir+"PWR_cycle{}_SE_200mVBL_14_0mVfC_2_0us_0x00.bin".format(i)
              with open(f_pwr, 'rb') as fn:
                   pwr_meas = pickle.load(fn)[1]

              f_pl = datadir+"PWR_cycle{}_SE_200mVBL_14_0mVfC_2_0us_0x20.bin".format(i)
              with open(f_pl, 'rb') as fn:
                   rawdata = pickle.load(fn)[0]

              pldata = qc.data_decode(rawdata, self.fembs)

              for ifemb in self.fembs:
                  fp_pwr = self.savedir[ifemb] + "PWR_Cycle/PWR_cycle{}_SE_200mVBL_14_0mVfC_2_0us_pwr_meas".format(i)
                  qc.PrintPWR(pwr_meas, ifemb, fp_pwr)

                  fp = self.savedir[ifemb] + "PWR_Cycle/"
                  qc.GetPeaks(pldata, ifemb, fp, "PWR_cycle{}_SE_200mVBL_14_0mVfC_2_0us".format(i))

          f_pwr = datadir+"PWR_DIFF_200mVBL_14_0mVfC_2_0us_0x00.bin"
          with open(f_pwr, 'rb') as fn:
               pwr_meas = pickle.load(fn)[1]

          f_pl = datadir+"PWR_DIFF_200mVBL_14_0mVfC_2_0us_0x20.bin"
          with open(f_pl, 'rb') as fn:
               rawdata = pickle.load(fn)[0]

          pldata = qc.data_decode(rawdata, self.fembs)

          for ifemb in self.fembs:
              fp_pwr = self.savedir[ifemb] + "PWR_Cycle/PWR_DIFF_200mVBL_14_0mVfC_2_0us_pwr_meas"
              qc.PrintPWR(pwr_meas, ifemb, fp_pwr)

              fp = self.savedir[ifemb] + "PWR_Cycle/"
              qc.GetPeaks(pldata, ifemb, fp, "PWR_DIFF_200mVBL_14_0mVfC_2_0us")

          f_pwr = datadir+"PWR_SE_SDF_200mVBL_14_0mVfC_2_0us_0x00.bin"
          with open(f_pwr, 'rb') as fn:
               pwr_meas = pickle.load(fn)[1]

          f_pl = datadir+"PWR_SE_SDF_200mVBL_14_0mVfC_2_0us_0x20.bin"
          with open(f_pl, 'rb') as fn:
               rawdata = pickle.load(fn)[0]

          pldata = qc.data_decode(rawdata, self.fembs)

          for ifemb in self.fembs:
              fp_pwr = self.savedir[ifemb] + "PWR_Cycle/PWR_SE_SDF_200mVBL_14_0mVfC_2_0us_pwr_meas"
              qc.PrintPWR(pwr_meas, ifemb, fp_pwr)

              fp = self.savedir[ifemb] + "PWR_Cycle/"
              qc.GetPeaks(pldata, ifemb, fp, "PWR_SE_SDF_200mVBL_14_0mVfC_2_0us")


          for ifemb in self.fembs:
              fdir = self.savedir[ifemb] + "PWR_Cycle/"
              fembid = int(self.fembsID[f'femb{ifemb}'])
              self.GEN_PWR_PDF(fdir, fembid)

      def CHKPULSE(self, fdir):

          self.CreateDIR(fdir)
          datadir = self.datadir+fdir+"/"

          qc=ana_tools()
          files = sorted(glob.glob(datadir+"*.bin"), key=os.path.getmtime)  # list of data files in the dir
          for afile in files:
              with open(afile, 'rb') as fn:
                   raw = pickle.load(fn)
              print("analyze file: %s"%afile)

              rawdata = raw[0]
              pwr_meas = raw[1]

              pldata = qc.data_decode(rawdata, self.fembs)

              if '\\' in afile:
                  fname = afile.split("\\")[-1][:-4]
              else:
                  fname = afile.split("/")[-1][:-4]
              for ifemb in self.fembs:
                  fp = self.savedir[ifemb] + fdir+"/" 
                  qc.GetPeaks(pldata, ifemb, fp, fname)

      def RMS_report(self):

          self.CreateDIR("RMS")
          datadir = self.datadir+"RMS/"

          datafiles = sorted(glob.glob(datadir+"RMS*.bin"), key=os.path.getmtime)
          for afile in datafiles:
              with open(afile, 'rb') as fn:
                   raw = pickle.load(fn)
              print("analyze file: %s"%afile)

              rawdata=raw[0]
              if '\\' in afile:
                  fname = afile.split("\\")[-1][7:-9]
              else:
                  fname = afile.split("/")[-1][7:-9]

              qc=ana_tools()
              pldata = qc.data_decode(rawdata, self.fembs)

              for ifemb in self.fembs:
                  fp = self.savedir[ifemb]+"RMS/"
                  qc.GetRMS(pldata, ifemb, fp, fname)
         
      def FE_MON_report(self):

          self.CreateDIR("MON_FE")
          datadir = self.datadir+"MON_FE/"

          fp = datadir+"LArASIC_mon.bin"
          with open(fp, 'rb') as fn:
               raw = pickle.load(fn)
          print("analyze file: %s"%fp)

          mon_BDG=raw[0]
          mon_TEMP=raw[1]
          mon_200bls_sdf1=raw[2]
          mon_200bls_sdf0=raw[3]
          mon_900bls_sdf1=raw[4]
          mon_900bls_sdf0=raw[5]

          qc=ana_tools()
          qc.PlotMon(self.fembs, mon_BDG, self.savedir, "MON_FE", "bandgap")
          qc.PlotMon(self.fembs, mon_TEMP, self.savedir, "MON_FE", "temperature")
          qc.PlotMon(self.fembs, mon_200bls_sdf1, self.savedir, "MON_FE", "200mVBL_sdf1")
          qc.PlotMon(self.fembs, mon_200bls_sdf0, self.savedir, "MON_FE", "200mVBL_sdf0")
          qc.PlotMon(self.fembs, mon_900bls_sdf1, self.savedir, "MON_FE", "900mVBL_sdf1")
          qc.PlotMon(self.fembs, mon_900bls_sdf0, self.savedir, "MON_FE", "900mVBL_sdf0")

      def FE_DAC_MON_report(self):

          self.CreateDIR("MON_FE")
          datadir = self.datadir+"MON_FE/"

          fp = datadir+"LArASIC_mon_DAC.bin"
          with open(fp, 'rb') as fn:
               raw = pickle.load(fn)
          print("analyze file: %s"%fp)

          mon_sgp1=raw[0]
          mon_14mVfC=raw[1]
          mon_7_8mVfC=raw[2]
          mon_25mVfC=raw[3]

          qc=ana_tools()
          qc.PlotMonDAC(self.fembs, mon_sgp1, self.savedir, "MON_FE", "LArASIC_DAC_sgp1")
          qc.PlotMonDAC(self.fembs, mon_14mVfC, self.savedir, "MON_FE", "LArASIC_DAC_14mVfC")
          qc.PlotMonDAC(self.fembs, mon_7_8mVfC, self.savedir, "MON_FE", "LArASIC_DAC_7_8mVfC")
          qc.PlotMonDAC(self.fembs, mon_25mVfC, self.savedir, "MON_FE", "LArASIC_DAC_25mVfC")

      def ColdADC_DAC_MON_report(self):

          self.CreateDIR("MON_ADC")
          datadir = self.datadir+"MON_ADC/"

          fp = datadir+"LArASIC_ColdADC_mon.bin"
          with open(fp, 'rb') as fn:
               raw = pickle.load(fn)
          print("analyze file: %s"%fp)

          mon_default=raw[0]
          mon_dac=raw[1]

          qc=ana_tools()
          qc.PlotADCMon(self.fembs, mon_dac, self.savedir, "MON_ADC")

      def GenCALIPDF(self, snc, sgs, sts, sgp, fdir):

          if sgp==0:
             fname ="{}_{}_{}".format(snc, sgs, sts)
          if sgp==1:
             fname ="{}_{}_{}_sgp1".format(snc, sgs, sts)
          
          for ifemb in self.fembs:
              pdf = FPDF(orientation = 'P', unit = 'mm', format='Letter')
              pdf.alias_nb_pages()
              pdf.add_page()
              pdf.set_auto_page_break(False,0)
              pdf.set_font('Times', 'B', 20)
              pdf.cell(85)
              pdf.l_margin = pdf.l_margin*2
              pdf.cell(30, 5, 'FEMB#{:04d} Calibration Test Report'.format(int(self.fembsID[f'femb{ifemb}'])), 0, 1, 'C')
              pdf.ln(2)

              rms_image = self.savedir[ifemb] + fdir + 'rms_{}.png'.format(fname)
              gain_image = self.savedir[ifemb] + fdir + 'gain_{}.png'.format(fname)
              ENC_image = self.savedir[ifemb] + fdir + 'enc_{}.png'.format(fname)

              pdf.image(gain_image,0,35,220,150)
              pdf.image(rms_image,10,185,100,70)
              pdf.image(ENC_image,105,185,100,70)
              outfile = self.savedir[ifemb]+fdir+'report_{}.pdf'.format(fname)
              pdf.output(outfile, "F")

      def CALI_report_1(self):
          qc=ana_tools()
    
          self.CreateDIR("CALI1")
          dac_list = range(0,64,4) 
          datadir = self.datadir+"CALI1/"
          print("analyze CALI1 200mVBL 4_7mVfC 2_0us")
          qc.GetGain(self.fembs, datadir, self.savedir, "CALI1/", "CALI1_SE_{}_{}_{}_0x{:02x}", "200mVBL", "4_7mVfC", "2_0us", dac_list)
          qc.GetENC(self.fembs, "200mVBL", "4_7mVfC", "2_0us", 0, self.savedir, "CALI1/")
          self.GenCALIPDF("200mVBL", "4_7mVfC", "2_0us", 0, "CALI1/")

          datadir = self.datadir+"CALI1/"
          print("analyze CALI1 200mVBL 7_8mVfC 2_0us")
          qc.GetGain(self.fembs, datadir, self.savedir, "CALI1/", "CALI1_SE_{}_{}_{}_0x{:02x}", "200mVBL", "7_8mVfC", "2_0us", dac_list)
          qc.GetENC(self.fembs, "200mVBL", "7_8mVfC", "2_0us", 0, self.savedir, "CALI1/")
          self.GenCALIPDF("200mVBL", "7_8mVfC", "2_0us", 0, "CALI1/")

          datadir = self.datadir+"CALI1/"
          print("analyze CALI1 200mVBL 14_0mVfC 2_0us")
          qc.GetGain(self.fembs, datadir, self.savedir, "CALI1/", "CALI1_SE_{}_{}_{}_0x{:02x}", "200mVBL", "14_0mVfC", "2_0us", dac_list)
          qc.GetENC(self.fembs, "200mVBL", "14_0mVfC", "2_0us", 0, self.savedir, "CALI1/")
          self.GenCALIPDF("200mVBL", "14_0mVfC", "2_0us", 0, "CALI1/")

          datadir = self.datadir+"CALI1/"
          print("analyze CALI1 200mVBL 25_0mVfC 2_0us")
          qc.GetGain(self.fembs, datadir, self.savedir, "CALI1/", "CALI1_SE_{}_{}_{}_0x{:02x}", "200mVBL", "25_0mVfC", "2_0us", dac_list)
          qc.GetENC(self.fembs, "200mVBL", "25_0mVfC", "2_0us", 0, self.savedir, "CALI1/")
          self.GenCALIPDF("200mVBL", "25_0mVfC", "2_0us", 0, "CALI1/")

      def CALI_report_2(self):

          qc=ana_tools()
          dac_list = range(0,64,4) 

          self.CreateDIR("CALI2")
          datadir = self.datadir+"CALI2/"
          print("analyze CALI2 900mVBL 14_0mVfC 2_0us")
          qc.GetGain(self.fembs, datadir, self.savedir, "CALI2/", "CALI2_SE_{}_{}_{}_0x{:02x}", "900mVBL", "14_0mVfC", "2_0us", dac_list)
          qc.GetENC(self.fembs, "900mVBL", "14_0mVfC", "2_0us", 0, self.savedir, "CALI2/")
          self.GenCALIPDF("900mVBL", "14_0mVfC", "2_0us", 0, "CALI2/")

      def CALI_report_3(self):

          qc=ana_tools()
          dac_list = range(0,32) 

          self.CreateDIR("CALI3")
          datadir = self.datadir+"CALI3/"
          print("analyze CALI3 200mVBL 14_0mVfC sgp=1")
          qc.GetGain(self.fembs, datadir, self.savedir, "CALI3/", "CALI3_SE_{}_{}_{}_0x{:02x}_sgp1", "200mVBL", "14_0mVfC", "2_0us", dac_list,20,10)
          qc.GetENC(self.fembs, "200mVBL", "14_0mVfC", "2_0us", 1, self.savedir, "CALI3/")
          self.GenCALIPDF("200mVBL", "14_0mVfC", "2_0us", 1, "CALI3/")

      def CALI_report_4(self):

          qc=ana_tools()
          dac_list = range(0,32) 

          self.CreateDIR("CALI4")
          datadir = self.datadir+"CALI4/"
          print("analyze CALI4 900mVBL 14_0mVfC sgp=1")
          qc.GetGain(self.fembs, datadir, self.savedir, "CALI4/", "CALI4_SE_{}_{}_{}_0x{:02x}_sgp1", "900mVBL", "14_0mVfC", "2_0us", dac_list, 10, 4)
          qc.GetENC(self.fembs, "900mVBL", "14_0mVfC", "2_0us", 1, self.savedir, "CALI4/")
          self.GenCALIPDF("900mVBL", "14_0mVfC", "2_0us", 1, "CALI4/")

      def CHK_Peaks(self,data,fname):

          err_mssg=[]
          chkflag="Pass"

          tmp = QC_check.CHKPulse(data[0])  # positive peak
          if tmp[0]==True:
             chkflag="Fail"
             err_mssg.append("{} positive peak chans: {}".format(fname,tmp[1][0]))
             if tmp[1][1]:
                err_mssg.append("{} positive peak chips: {}".format(fname,tmp[1][1]))

          tmp = QC_check.CHKPulse(data[1])  # negative peak
          if tmp[0]==True:
             chkflag="Fail"
             err_mssg.append("{} negative peak chans: {}".format(fname,tmp[1][0]))
             if tmp[1][1]:
                err_mssg.append("{} negative peak chips: {}".format(fname,tmp[1][1]))

          tmp = QC_check.CHKPulse(data[2])  # BL peak
          if tmp[0]==True:
             chkflag="Fail"
             err_mssg.append("{} baseline chans: {}".format(fname,tmp[1][0]))
             if tmp[1][1]:
                err_mssg.append("{} baseline chips: {}".format(fname,tmp[1][1]))

          return chkflag,err_mssg

      def CHK_pwr(self,data,fdir,fname,ifemb):

          err_mssg=[]
          chkflag="Pass"

          tmp=QC_check.CHKPWR(data,ifemb)
          if tmp[0]==True:
             chkflag="Fail"
             err_mssg.append("{} issues: {}".format(fname,tmp[1]))

          f_pwr = self.savedir[ifemb]+"{}/Pulse_{}_200mVBL_14_0mVfC_2_0us.bin".format(fdir,fname)
          with open(f_pwr, 'rb') as fn:
               pwr_meas_pl = pickle.load(fn)

          tmp=self.CHK_Peaks(pwr_meas_pl,fname)
          if tmp[0]=="Fail": 
             chkflag="Fail"
             err_mssg = err_mssg + tmp[1]

          return chkflag,err_mssg

      def CHK_genreport(self,chkflag,err_mssg,nfemb):

          fembid = int(self.fembsID[f'femb{nfemb}'])

          pdf = FPDF(orientation = 'P', unit = 'mm', format='Letter')
          pdf.alias_nb_pages()
          pdf.add_page()
          pdf.set_auto_page_break(False,0)
          pdf.set_font('Times', 'B', 20)
          pdf.cell(85)
          pdf.l_margin = pdf.l_margin*2
          pdf.cell(30, 5, 'FEMB#{:04d} QC Report'.format(fembid), 0, new_x="LMARGIN", new_y="NEXT", align='C')
          pdf.ln(2)

          pdf.set_font('Times', '', 12)
          pdf.cell(30, 5, 'Tester: {}'.format(self.logs['tester']), 0, new_x="RIGHT", new_y="TOP")
          pdf.cell(80)
          pdf.cell(30, 5, 'Date: {}'.format(self.logs['date']), 0, new_x="LMARGIN", new_y="NEXT")

          pdf.cell(30, 5, 'Temperature: {}'.format(self.logs['env']), 0, new_x="RIGHT", new_y="TOP")
          pdf.cell(80)
          pdf.cell(30, 5, 'Input Capacitor(Cd): {}'.format(self.logs['toytpc']), 0, new_x="LMARGIN", new_y="NEXT")
          pdf.cell(30, 5, 'Note: {}'.format(self.logs['note']), 0, new_x="LMARGIN", new_y="NEXT")

          pdf.ln(10)

          if self.logs['env']=='LN':
             chk_result=( ("Measurement","Result"),
                          ("Power consumption",chkflag["PWR_Meas"]),
                          ("Power cycles",chkflag["PWR_Cycle"]),
                          ("Leakage current",chkflag["LK_curr"]),
                          ("Pulse check",chkflag["CHK"]),
                          ("RMS check",chkflag["RMS"])
                        )
          else:
             chk_result=( ("Measurement","Result"),
                          ("Power consumption",chkflag["PWR_Meas"]),
                          ("Leakage current",chkflag["LK_curr"]),
                          ("Pulse check",chkflag["CHK"]),
                          ("RMS check",chkflag["RMS"])
                        )

          
          with pdf.table() as table:
              for data_row in chk_result:
                  row = table.row()
                  for datum in data_row:
                      row.cell(datum)

          pdf.add_page()
          nn=0
          if err_mssg["PWR_Meas"]:
             pdf.ln(1)
             pdf.set_font('Times', 'B', 11)
             pdf.cell(80, 5, "Power consumption issues:", 0, new_x="LMARGIN", new_y="NEXT")
             pdf.set_font('Times', '', 10)
             nn = nn+1
             for istr in err_mssg["PWR_Meas"]:
                 pdf.cell(80, 5, "{}".format(istr), 0, new_x="LMARGIN", new_y="NEXT")
                 nn = nn+1

          if nn>50:
             pdf.add_page()
             nn=0

          if err_mssg["PWR_Cycle"]:
             pdf.ln(1)
             pdf.set_font('Times', 'B', 11)
             pdf.cell(80, 5, "Power cycles issues:", 0, new_x="LMARGIN", new_y="NEXT")
             pdf.set_font('Times', '', 10)
             nn = nn+1
             for istr in err_mssg["PWR_Cycle"]:
                 pdf.cell(80, 5, "{}".format(istr), 0, new_x="LMARGIN", new_y="NEXT")
                 nn = nn+1

          if nn>50:
             pdf.add_page()
             nn=0

          if err_mssg["LK_curr"]:
             pdf.ln(1)
             pdf.set_font('Times', 'B', 11)
             pdf.cell(80, 5, "Leakage current issues:", 0, new_x="LMARGIN", new_y="NEXT")
             pdf.set_font('Times', '', 10)
             nn = nn+1
             for istr in err_mssg["LK_curr"]:
                 pdf.cell(80, 5, "{}".format(istr), 0, new_x="LMARGIN", new_y="NEXT")
                 nn = nn+1

          if nn>50:
             pdf.add_page()
             nn=0

          if err_mssg["CHK"]:
             pdf.ln(1)
             pdf.set_font('Times', 'B', 11)
             pdf.cell(80, 5, "CHK pulse issues:", 0, new_x="LMARGIN", new_y="NEXT")
             pdf.set_font('Times', '', 10)
             nn = nn+1
             for istr in err_mssg["CHK"]:
                 pdf.cell(80, 5, "{}".format(istr), 0, new_x="LMARGIN", new_y="NEXT")
                 nn = nn+1
                 if nn>50:
                    pdf.add_page()
                    nn=0

          if err_mssg["RMS"]:
             pdf.ln(1)
             pdf.set_font('Times', 'B', 11)
             pdf.cell(80, 5, "RMS issues:", 0, new_x="LMARGIN", new_y="NEXT")
             pdf.set_font('Times', '', 10)
             nn = nn+1
             for istr in err_mssg["RMS"]:
                 pdf.cell(80, 5, "{}".format(istr), 0, new_x="LMARGIN", new_y="NEXT")
                 nn = nn+1
                 if nn>50:
                    pdf.add_page()
                    nn=0

          outfile = self.savedir[nfemb]+'report.pdf'
          pdf.output(outfile)
      

      def CHK_report(self):

          datadir = self.datadir+"PWR_Meas/"
          f_pwr = datadir+"PWR_SE_200mVBL_14_0mVfC_2_0us_0x00.bin"
          with open(f_pwr, 'rb') as fn:
               pwr_meas_se = pickle.load(fn)[1]

          f_pwr = datadir+"PWR_DIFF_200mVBL_14_0mVfC_2_0us_0x00.bin"
          with open(f_pwr, 'rb') as fn:
               pwr_meas_diff = pickle.load(fn)[1]

          f_pwr = datadir+"PWR_SE_SDF_200mVBL_14_0mVfC_2_0us_0x00.bin"
          with open(f_pwr, 'rb') as fn:
               pwr_meas_sesdf = pickle.load(fn)[1]

          if 'LN' in self.logs['env']:
             datadir = self.datadir+"PWR_Cycle/"
             pwr_cycle_se=[]
             for ii in range(3):
                 f_pwr = datadir+"PWR_cycle{}_SE_200mVBL_14_0mVfC_2_0us_0x00.bin".format(ii)
                 with open(f_pwr, 'rb') as fn:
                      pwr_cycle_se.append( pickle.load(fn)[1] )
   
             f_pwr = datadir+"PWR_DIFF_200mVBL_14_0mVfC_2_0us_0x00.bin"
             with open(f_pwr, 'rb') as fn:
                  pwr_cycle_diff = pickle.load(fn)[1]
   
             f_pwr = datadir+"PWR_SE_SDF_200mVBL_14_0mVfC_2_0us_0x00.bin"
             with open(f_pwr, 'rb') as fn:
                  pwr_cycle_sesdf = pickle.load(fn)[1]
   
          for ifemb in self.fembs:
              chkflag={"PWR_Meas":"Pass","PWR_Cycle":"Pass","LK_curr":"Pass","CHK":"Pass","RMS":"Pass","CALI1":"Pass"}
              err_mssg={"PWR_Meas":[],"PWR_Cycle":[],"LK_curr":[],"CHK":[],"RMS":[],"CALI1":[]}

              # check power consumptions          
              tmp = self.CHK_pwr(pwr_meas_se,"PWR_Meas","PWR_SE",ifemb)
              if tmp[0]=="Fail":
                 chkflag["PWR_Meas"]="Fail"
                 err_mssg["PWR_Meas"] = err_mssg["PWR_Meas"] + tmp[1] 

              tmp = self.CHK_pwr(pwr_meas_se,"PWR_Meas","PWR_DIFF",ifemb)
              if tmp[0]=="Fail":
                 chkflag["PWR_Meas"]="Fail"
                 err_mssg["PWR_Meas"] = err_mssg["PWR_Meas"] + tmp[1] 

              tmp = self.CHK_pwr(pwr_meas_se,"PWR_Meas","PWR_SE_SDF",ifemb)
              if tmp[0]=="Fail":
                 chkflag["PWR_Meas"]="Fail"
                 err_mssg["PWR_Meas"] = err_mssg["PWR_Meas"] + tmp[1] 

              # check power cycles
              if 'LN' in self.logs['env']:
                 for ii in range(3): 
                     tmp = self.CHK_pwr(pwr_cycle_se[ii],"PWR_Cycle","PWR_cycle{}_SE".format(ii),ifemb)
                     if tmp[0]=="Fail":
                        chkflag["PWR_Cycle"]="Fail"
                        err_mssg["PWR_Cycle"] = err_mssg["PWR_Cycle"] + tmp[1] 

                 tmp = self.CHK_pwr(pwr_cycle_diff,"PWR_Cycle","PWR_DIFF",ifemb)
                 if tmp[0]=="Fail":
                    chkflag["PWR_Cycle"]="Fail"
                    err_mssg["PWR_Cycle"] = err_mssg["PWR_Cycle"] + tmp[1] 

                 tmp = self.CHK_pwr(pwr_cycle_sesdf,"PWR_Cycle","PWR_SE_SDF",ifemb)
                 if tmp[0]=="Fail":
                    chkflag["PWR_Cycle"]="Fail"
                    err_mssg["PWR_Cycle"] = err_mssg["PWR_Cycle"] + tmp[1] 

              # check leakage current
              datadir = self.savedir[ifemb]+"Leakage_Current/"
              fname = ["1nA","5nA","100pA","500pA"]
              for ii in range(4): 
                  fpl = datadir+"Pulse_LC_SE_200mVBL_14_0mVfC_2_0us_0x20_{}.bin".format(fname[ii])
                  with open(fpl, 'rb') as fn:
                       pldata = pickle.load(fn)
                  tmp = self.CHK_Peaks(pldata,fname[ii])

                  if tmp[0]=="Fail":
                     chkflag["LK_curr"]="Fail"
                     err_mssg["LK_curr"] = err_mssg["LK_curr"] + tmp[1] 

              # CHK
              datadir = self.savedir[ifemb]+"CHK/"
              blname = ["200mVBL","900mVBL"]
              gainname = ["4_7mVfC","7_8mVfC","14_0mVfC","25_0mVfC"]
              stname = ["0_5us","1_0us","2_0us","3_0us"]
              for ii in range(2):
                  for jj in range(4):
                      for kk in range(4): 
                          fname = "{}_{}_{}".format(blname[ii],gainname[jj],stname[kk])
                          fpl = datadir+"Pulse_CHK_SE_{}_0x10.bin".format(fname)
                          with open(fpl, 'rb') as fn:
                               pldata = pickle.load(fn)
                          tmp = self.CHK_Peaks(pldata,fname)

                          if tmp[0]=="Fail":
                             chkflag["CHK"]="Fail"
                             err_mssg["CHK"] = err_mssg["CHK"] + tmp[1] 

              # RMS
              datadir = self.savedir[ifemb]+"RMS/"
              for ii in range(2):
                  for jj in range(4):
                      for kk in range(4): 
                          fname = "{}_{}_{}".format(blname[ii],gainname[jj],stname[kk])
                          frms = datadir+"RMS_{}.bin".format(fname)
                          with open(frms, 'rb') as fn:
                               rmsdata = pickle.load(fn)

                          tmp = QC_check.CHKPulse(rmsdata[1])  # rms
                          if tmp[0]==True:
                             chkflag["RMS"]="Fail"
                             err_mssg["RMS"].append("RMS {} chans: {}".format(fname,tmp[1][0]))
                             if tmp[1][1]:
                                err_mssg["RMS"].append("RMS {} chips: {}".format(fname,tmp[1][1]))

                          tmp = QC_check.CHKPulse(rmsdata[0])  # ped
                          if tmp[0]==True:
                             chkflag["RMS"]="Fail"
                             err_mssg["RMS"].append("BL {} chans: {}".format(fname,tmp[1][0]))
                             if tmp[1][1]:
                                err_mssg["RMS"].append("BL {} chips: {}".format(fname,tmp[1][1]))


          
              self.CHK_genreport(chkflag,err_mssg,ifemb)

if __name__=='__main__':

   ag = argparse.ArgumentParser()
   ag.add_argument("task", help="a list of tasks to be analyzed", type=int, choices=range(1,13), nargs='+')
   ag.add_argument("-n", "--fembs", help="a list of fembs to be analyzed", type=int, choices=range(0,4), nargs='+')
   args = ag.parse_args()
   
   tasks = args.task
   fembs = args.fembs
   
   rp = QC_reports("femb101_femb107_femb105_femb111_LN_150pF", fembs)
   
   tt={}
   
   for tm in tasks:
       t1=time.time()
       print("start tm=",tm)
       if tm==1:
          rp.PWR_consumption_report()
   
       if tm==2:
          rp.PWR_cycle_report()
          
       if tm==3:
          rp.CHKPULSE("Leakage_Current")
          
       if tm==4:
          rp.CHKPULSE("CHK")
   
       if tm==5:
          rp.RMS_report()
   
       if tm==6:
          rp.CALI_report_1()
   
       if tm==7:
          rp.CALI_report_2()
   
       if tm==8:
          rp.CALI_report_3()
   
       if tm==9:
          rp.CALI_report_4()
   
       if tm==10:
          rp.FE_MON_report()
   
       if tm==11:
          rp.FE_DAC_MON_report()
   
       if tm==12:
          rp.ColdADC_DAC_MON_report()
   
       t2=time.time()
       tt[tm]=t2-t1
       time.sleep(1)
   
   print(tt)
