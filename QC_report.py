import pickle
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
import sys
import time
import glob
from QC_tools import ana_tools
from fpdf import FPDF
import argparse

class QC_reports:

      def __init__(self, fdir, fembs=[]):

#          savedir = "/home/hanjie/Desktop/protoDUNE/cold_electronics/FEMB_QC/new_qc_data/results/"
#          self.datadir = "/home/hanjie/Desktop/protoDUNE/cold_electronics/FEMB_QC/new_qc_data/data/"+fdir+"/"

          savedir = "QC_reports/"
          self.datadir = "QC_data/"+fdir+"/"

          fp = self.datadir+"logs_env.bin"
          with open(fp, 'rb') as fn:
               logs = pickle.load(fn)
         
          logs["datadir"]=self.datadir
          self.logs=logs

          self.fembs={}
          if fembs:
              for ifemb in fembs:
                  self.fembs[f'femb{ifemb}'] = logs['femb id'][f'femb{ifemb}']
          else:
              self.fembs=logs['femb id']
          self.savedir={}
          print("Will analyze the following fembs: ", self.fembs)

          ##### create results dir for each FEMB #####
          for key,value in self.fembs.items():
              one_savedir = savedir+"FEMB{}_{}_{}".format(value, logs["env"], logs["toytpc"])

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

              self.savedir[key]=one_savedir+"/"

              fp = self.savedir[key] + "logs_env.bin"
              with open(fp, 'wb') as fn:
                   pickle.dump(self.logs, fn)

      def CreateDIR(self, fdir):

          for key,value in self.fembs.items():
              fp = self.savedir[key] + fdir + "/"
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
                 pdf.text(55, 45+45*nn, im_name)  
                 pdf.image(im,0,47+nn*45,200, 40)
              else:
                 if nn%3==0:
                    pdf.add_page()
                 pdf.text(55, 10+45*(nn-3), im_name)  
                 pdf.image(im,0,12+(nn-3)*45,200, 40)
              nn=nn+1
          
          pdf.alias_nb_pages()
          pdf.add_page()
          
          chk_images = sorted(glob.glob(fdir+"*_pulse_response.png"), key=os.path.getmtime)
          nn=0
          for im in chk_images:
              if '\\' in im:
                  im_name = im.split("\\")[-1][4:-19]
              else:
                  im_name = im.split("/")[-1][4:-19]

              pdf.set_font('Times', 'B', 14)
              if nn<3:
                 pdf.text(55, 10+nn*80, im_name)  
                 pdf.image(im,0,12+nn*80,200,80)
              else:
                 if nn%3==0:
                    pdf.alias_nb_pages()
                    pdf.add_page()
                 pdf.text(55, 10+(nn-3)*80, im_name)  
                 pdf.image(im,0,12+(nn-3)*80,200,80)
              nn=nn+1
          
          outfile = fdir+'report.pdf'
          pdf.output(outfile, "F")
         
      def PWR_consumption_report(self):
          
          self.CreateDIR("PWR_Meas")
          datadir = self.datadir+"PWR_Meas/"

          qc=ana_tools()
          files = sorted(glob.glob(datadir+"*.bin"), key=os.path.getmtime)  # list of data files in the dir
          for afile in files:
              with open(afile, 'rb') as fn:
                   raw = pickle.load(fn)

              rawdata = raw[0]
              pwr_meas = raw[1]

              pldata = qc.data_decode(rawdata)
              pldata = np.array(pldata)

              if '\\' in afile:
                  fname = afile.split("\\")[-1][:-4]
              else:
                  fname = afile.split("/")[-1][:-4]
              for key,value in self.fembs.items():
                  fp = self.savedir[key] + "PWR_Meas/" + fname + "_pwr_meas"
                  qc.PrintPWR(pwr_meas[key], fp)

                  ana = qc.data_ana(pldata,int(key[-1]))
                  fp_data = self.savedir[key] + "PWR_Meas/" + fname + "_pulse_response"
                  qc.FEMB_CHK_PLOT(ana[0], ana[1], ana[2], ana[3], ana[4], ana[5], fp_data)
 
          for key,value in self.fembs.items():
              fdir = self.savedir[key] + "PWR_Meas/"
              self.GEN_PWR_PDF(fdir, int(value))

      def PWR_cycle_report(self):

          self.CreateDIR("PWR_Cycle")
          datadir = self.datadir+"PWR_Cycle/"

          qc=QC_tools()
          files = sorted(glob.glob(datadir+"*.bin"), key=os.path.getmtime)  # list of data files in the dir
          for afile in files:
              with open(afile, 'rb') as fn:
                   raw = pickle.load(fn)

              rawdata = raw[0]
              pwr_meas = raw[1]

              pldata = qc.data_decode(rawdata)
              pldata = np.array(pldata)

              if '\\' in afile:
                  fname = afile.split("\\")[-1][:-4]
              else:
                  fname = afile.split("/")[-1][:-4]

              for key,value in self.fembs.items():
                  fp = self.savedir[key] + "PWR_Cycle/" + fname + "_pwr_meas"
                  qc.PrintPWR(pwr_meas[key], fp)

                  ana = qc.data_ana(pldata,int(key[-1]))
                  fp_data = self.savedir[key] + "PWR_Cycle/" + fname + "_pulse_response"
                  qc.FEMB_CHK_PLOT(ana[0], ana[1], ana[2], ana[3], ana[4], ana[5], fp_data)
 
          for key,value in self.fembs.items():
              fdir = self.savedir[key] + "PWR_Cycle/"
              self.GEN_PWR_PDF(fdir, int(value))

      def CHKPULSE(self, fdir):

          self.CreateDIR(fdir)
          datadir = self.datadir+fdir+"/"

          qc=QC_tools()
          files = sorted(glob.glob(datadir+"*.bin"), key=os.path.getmtime)  # list of data files in the dir
          for afile in files:
              with open(afile, 'rb') as fn:
                   raw = pickle.load(fn)

              rawdata = raw[0]
              pwr_meas = raw[1]

              pldata = qc.data_decode(rawdata)
              pldata = np.array(pldata)

              if '\\' in afile:
                  fname = afile.split("\\")[-1][:-4]
              else:
                  fname = afile.split("/")[-1][:-4]
              for key,value in self.fembs.items():
                  ana = qc.data_ana(pldata,int(key[-1]))
                  fp_data = self.savedir[key] + fdir+"/" + fname + "_pulse_response"
                  qc.FEMB_CHK_PLOT(ana[0], ana[1], ana[2], ana[3], ana[4], ana[5], fp_data)
         
      def FE_MON_report(self):

          self.CreateDIR("MON_FE")
          datadir = self.datadir+"MON_FE/"

          fp = datadir+"LArASIC_mon.bin"
          with open(fp, 'rb') as fn:
               raw = pickle.load(fn)

          mon_BDG=raw[0]
          mon_TEMP=raw[1]
          mon_200bls=raw[2]
          mon_900bls=raw[3]

          qc=QC_tools()
          qc.PlotMon(self.fembs, mon_BDG, self.savedir, "MON_FE", "bandgap")
          qc.PlotMon(self.fembs, mon_TEMP, self.savedir, "MON_FE", "temperature")
          qc.PlotMonChan(self.fembs, mon_200bls, self.savedir, "MON_FE", "200mVBL")
          qc.PlotMonChan(self.fembs, mon_900bls, self.savedir, "MON_FE", "900mVBL")

      def FE_DAC_MON_report(self):

          self.CreateDIR("MON_FE")
          datadir = self.datadir+"MON_FE/"

          fp = datadir+"LArASIC_mon_DAC.bin"
          with open(fp, 'rb') as fn:
               raw = pickle.load(fn)

          mon_sgp1=raw[0]
          mon_sgp0=raw[1]

          qc=QC_tools()
          qc.PlotMonDAC(self.fembs, mon_sgp1, self.savedir, "MON_FE", "LArASIC_DAC_sgp1", range(64), "VDAC{:02d}CHIP{}_SGP1")
          qc.PlotMonDAC(self.fembs, mon_sgp0, self.savedir, "MON_FE", "LArASIC_DAC_14mVfC", range(0,64,4), "VDAC{:02d}CHIP{}")

      def ColdADC_DAC_MON_report(self):

          self.CreateDIR("MON_ADC")
          datadir = self.datadir+"MON_ADC/"

          fp = datadir+"LArASIC_ColdADC_mon.bin"
          with open(fp, 'rb') as fn:
               raw = pickle.load(fn)

          mon_default=raw[0]
          mon_dac=raw[1]

          qc=QC_tools()
          qc.PlotADCMon(self.fembs, mon_dac, self.savedir, "MON_ADC")

      def RMS_report(self):

          self.CreateDIR("RMS")
          datadir = self.datadir+"RMS/"

          datafiles = sorted(glob.glob(datadir+"RMS*.bin"), key=os.path.getmtime)
          for afile in datafiles:
              with open(afile, 'rb') as fn:
                   raw = pickle.load(fn)

              rawdata=raw[0]
              if '\\' in afile:
                  fname = afile.split("\\")[-1][7:-9]
              else:
                  fname = afile.split("/")[-1][7:-9]

              qc=QC_tools()
              pldata = qc.data_decode(rawdata)
              pldata = np.array(pldata)

              for ifemb,femb_id in self.fembs.items():
                  nfemb=int(ifemb[-1])
                  fp = self.savedir[ifemb]+"RMS/"
                  qc.GetRMS(pldata, nfemb, fp, fname)

      def GenCALIPDF(self, snc, sgs, sts, sgp):

          if sgp==0:
             fname ="{}_{}_{}".format(snc, sgs, sts)
          if sgp==1:
             fname ="{}_{}_{}_sgp1".format(snc, sgs, sts)
          
          for ifemb,femb_id in self.fembs.items():
              pdf = FPDF(orientation = 'P', unit = 'mm', format='Letter')
              pdf.alias_nb_pages()
              pdf.add_page()
              pdf.set_auto_page_break(False,0)
              pdf.set_font('Times', 'B', 20)
              pdf.cell(85)
              pdf.l_margin = pdf.l_margin*2
              pdf.cell(30, 5, 'FEMB#{:04d} Calibration Test Report'.format(int(femb_id)), 0, 1, 'C')
              pdf.ln(2)

              rms_image = self.savedir[ifemb] + 'CALI/' + 'rms_{}.png'.format(fname)
              gain_image = self.savedir[ifemb] + 'CALI/' + 'gain_{}.png'.format(fname)
              ENC_image = self.savedir[ifemb] + 'CALI/' + 'enc_{}.png'.format(fname)
              inl_image = self.savedir[ifemb] + 'CALI/' + 'inl_{}.png'.format(fname)
              peak_image = self.savedir[ifemb] + 'CALI/' + 'peak_{}.png'.format(fname)
              dac_max_image = self.savedir[ifemb] + 'CALI/' + 'linear_max_dac_{}.png'.format(fname)

              pdf.image(rms_image,0,35,100,80)
              pdf.image(gain_image,100,35,100,80)
              pdf.image(ENC_image,0,115,100,80)
              pdf.image(peak_image,100,115,100,80)
              pdf.image(inl_image,0,195,100,80)
              pdf.image(dac_max_image,100,195,100,80)
              outfile = self.savedir[ifemb]+"CALI/"+'report_{}.pdf'.format(fname)
              pdf.output(outfile, "F")

      def CALI_report(self):

          self.CreateDIR("CALI")

          qc=QC_tools()
         
          dac_list = range(0,64,4) 
          datadir = self.datadir+"CALI1/"
          qc.GetGain(self.fembs, datadir, self.savedir, "CALI/", "CALI1_SE_{}_{}_{}_0x{:02x}.bin", "200mVBL", "4_7mVfC", "2_0us", "{}_{}_{}", dac_list)
          qc.GetENC(self.fembs, "200mVBL", "4_7mVfC", "2_0us", 0, self.savedir, "CALI/")
          self.GenCALIPDF("200mVBL", "4_7mVfC", "2_0us", 0)

          qc.GetGain(self.fembs, datadir, self.savedir, "CALI/", "CALI1_SE_{}_{}_{}_0x{:02x}.bin", "200mVBL", "7_8mVfC", "2_0us", "{}_{}_{}", dac_list)
          qc.GetENC(self.fembs, "200mVBL", "7_8mVfC", "2_0us", 0, self.savedir, "CALI/")
          self.GenCALIPDF("200mVBL", "7_8mVfC", "2_0us", 0)

          qc.GetGain(self.fembs, datadir, self.savedir, "CALI/", "CALI1_SE_{}_{}_{}_0x{:02x}.bin", "200mVBL", "14_0mVfC", "2_0us","{}_{}_{}", dac_list)
          qc.GetENC(self.fembs, "200mVBL", "14_0mVfC", "2_0us", 0, self.savedir, "CALI/")
          self.GenCALIPDF("200mVBL", "14_0mVfC", "2_0us", 0)

          qc.GetGain(self.fembs, datadir, self.savedir, "CALI/", "CALI1_SE_{}_{}_{}_0x{:02x}.bin", "200mVBL", "25_0mVfC", "2_0us", "{}_{}_{}", dac_list)
          qc.GetENC(self.fembs, "200mVBL", "25_0mVfC", "2_0us", 0, self.savedir, "CALI/")
          self.GenCALIPDF("200mVBL", "25_0mVfC", "2_0us", 0)

          datadir = self.datadir+"CALI2/"
          qc.GetGain(self.fembs, datadir, self.savedir, "CALI/", "CALI2_SE_{}_{}_{}_0x{:02x}.bin", "900mVBL", "14_0mVfC", "2_0us", "{}_{}_{}", dac_list)
          qc.GetENC(self.fembs, "900mVBL", "14_0mVfC", "2_0us", 0, self.savedir, "CALI/")
          self.GenCALIPDF("900mVBL", "14_0mVfC", "2_0us", 0)

          dac_list = range(0,64) 
          datadir = self.datadir+"CALI3/"
          qc.GetGain(self.fembs, datadir, self.savedir, "CALI/", "CALI3_SE_{}_{}_{}_0x{:02x}_sgp1.bin", "200mVBL", "14_0mVfC", "2_0us", "{}_{}_{}_sgp1", dac_list)
          qc.GetENC(self.fembs, "200mVBL", "14_0mVfC", "2_0us", 1, self.savedir, "CALI/")
          self.GenCALIPDF("200mVBL", "14_0mVfC", "2_0us", 1)
         
          dac_list = range(0,56) 
          datadir = self.datadir+"CALI4/"
          qc.GetGain(self.fembs, datadir, self.savedir, "CALI/", "CALI4_SE_{}_{}_{}_0x{:02x}_sgp1.bin", "900mVBL", "14_0mVfC", "2_0us", "{}_{}_{}_sgp1", dac_list, 10, 4)
          qc.GetENC(self.fembs, "900mVBL", "14_0mVfC", "2_0us", 1, self.savedir, "CALI/")
          self.GenCALIPDF("900mVBL", "14_0mVfC", "2_0us", 1)

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
          rp.CALI_report()
   
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
