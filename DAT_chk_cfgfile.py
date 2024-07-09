import sys
import numpy as np
import copy
import time, datetime, random, statistics    
import os
import argparse

####### Input test information #######
#Red = '\033[91m'
#Green = '\033[92m'
#Blue = '\033[94m'
#Cyan = '\033[96m'
#White = '\033[97m'
#Yellow = '\033[93m'
#Magenta = '\033[95m'
#Grey = '\033[90m'
#Black = '\033[90m'
#Default = '\033[99m'

from colorama import just_fix_windows_console
just_fix_windows_console()

#def dat_chk_cfgfile(froot = "./tmp_data/" ):
def dat_chk_cfgfile(fcfg = "./asic_info.csv" ):
    logs={}
    #tester=input("please input your name:  ")
    #logs['tester']=tester
   
    if True:
        logs['date']=datetime.datetime.now().strftime("%m_%d_%Y_%H_%M_%S")
        index_f = fcfg

        with open(index_f, 'r') as fp:
            for cl in fp:
                tmp = cl.split(",")
                tmp = tmp[:-1]
                logs[tmp[0]] = tmp[1]

        if False:
            print ("Tester  :  ", "\033[91m {} \033[0m".format(logs['tester']))
            #csvfile = input ("\033[92m Is tester updated? (Y/N) : \033[0m" )
            if ("Y" in csvfile) or ("y" in csvfile):
                pass
            else:
                #input ("click ENTER after you modify and save asic_info.csv.")
                #continue
                return False
            print ("Test Site  :     ", logs['testsite'])
            print ("Enviroment :     ", logs['env'])
            print ("DAT SN     :     ", logs['DAT_SN'])
            print ("DAT_on_WIB_slot: ", logs['DAT_on_WIB_slot'])
            print ("DUT        :     ", logs['DUT'])
            if "CD" in logs['DUT']:
                print ("\033[92m COLDATA0  : {} \033[0m".format(logs['CD0']))
                print ("\033[92m COLDATA1  : {} \033[0m".format(logs['CD1']))
            elif "ADC" in logs['DUT']:
                print ("\033[92m ColdADC0  : {} \033[0m".format(logs['ADC0']))
                print ("\033[92m ColdADC1  : {} \033[0m".format(logs['ADC1']))
                print ("\033[92m ColdADC2  : {} \033[0m".format(logs['ADC2']))
                print ("\033[92m ColdADC3  : {} \033[0m".format(logs['ADC3']))
                print ("\033[92m ColdADC4  : {} \033[0m".format(logs['ADC4']))
                print ("\033[92m ColdADC5  : {} \033[0m".format(logs['ADC5']))
                print ("\033[92m ColdADC6  : {} \033[0m".format(logs['ADC6']))
                print ("\033[92m ColdADC7  : {} \033[0m".format(logs['ADC7']))
            elif "FE" in logs['DUT']:
                print ("\033[92m LArASIC0  : {} \033[0m".format(logs['FE0']))
                print ("\033[92m LArASIC2  : {} \033[0m".format(logs['FE1']))
                print ("\033[92m LArASIC2  : {} \033[0m".format(logs['FE2']))
                print ("\033[92m LArASIC3  : {} \033[0m".format(logs['FE3']))
                print ("\033[92m LArASIC4  : {} \033[0m".format(logs['FE4']))
                print ("\033[92m LArASIC5  : {} \033[0m".format(logs['FE5']))
                print ("\033[92m LArASIC6  : {} \033[0m".format(logs['FE6']))
                print ("\033[92m LArASIC7  : {} \033[0m".format(logs['FE7']))
            #csvfile = input ("\033[95m Is asic_info.csv updated? (Y/N) : \033[0m" )
            csvfile = "Y"
            if ("Y" in csvfile) or ("y" in csvfile):
                pass
            else:
                #input ("click ENTER after you modify and save asic_info.csv.")
                #continue
                return False

        cd_id = {}
        for cd in range(2):
            dkey = "CD%d"%cd
            cdstr=logs[dkey]
            if (len(cdstr) == 9) :
                cdexist_flg = False
                cdks = list(cd_id.keys())
                for cdk in cdks:
                    cdexist = cd_id[cdk]
                    if (cdstr[4] == ("-")) :
                        if (cdstr[0:4] in cdexist)  and (cdstr[5:] in cdexist):
                            cdexist_flg = True
                    else:
                        if (cdstr == cdexist):
                            cdexist_flg = True
                        
                if cdexist_flg:
                    print ("\033[93m COLDATA Serial number exists, please correct \033[0m") 
                    return False
                elif cdstr[4] == ("-")  :
                    try: 
                        cdbatch = int(cdstr[0:4])
                        cdsn = int(cdstr[5:])
                        cd_id['CD{}'.format(cd)] = cdstr[0:4]+cdstr[4:]
                    except ValueError:
                        print ("\033[93m COLDATA Serial number is not in right format (XXXX-XXXX), please correct\033[0m") 
                        return False
                else:
                    print ("\033[93m COLDATA Serial number is not in right format (XXXX-XXXX), please correct\033[0m") 
                    return False
            else:
                print ("\033[93m COLDATA Serial number is not in right format (XXXX-XXXX), please correct\033[0m") 
                return False

        adc_id = {}
        for adc in range(8):
            dkey = "ADC%d"%adc
            adcstr=logs[dkey]
            if (len(adcstr) == 10) :
                adcexist_flg = False
                adcks = list(adc_id.keys())
                for adck in adcks:
                    adcexist = adc_id[adck]
                    if (adcstr[5] == ("-")) :
                        if (adcstr[0:4] in adcexist)  and (adcstr[5:] in adcexist):
                            adcexist_flg = True
                    else:
                        if (adcstr == adcexist):
                            adcexist_flg = True
                        
                if adcexist_flg:
                    print ("\033[93m ColdADC Serial number exists, please correct \033[0m") 
                    return False
                elif adcstr[4] == ("-")  :
                    try: 
                        adcbatch = int(adcstr[0:4])
                        adcsn = int(adcstr[5:])
                        adc_id['ADC{}'.format(adc)] = adcstr[0:4]+adcstr[5:]
                    except ValueError:
                        print ("\033[93m ColdADC Serial number is not in right format (XXXX-XXXXX), please correct\033[0m") 
                        return False
                else:
                    print ("\033[93m ColdADC Serial number is not in right format (XXXX-XXXXX), please correct\033[0m") 
                    return False
            else:
                print ("\033[93m ColdADC Serial number is not in right format (XXXX-XXXXX), please correct\033[0m") 
                return False

        fe_id = {}
        for fe in range(8):
            dkey = "FE%d"%fe
            festr=logs[dkey]
            if (len(festr) == 9) :
                feexist_flg = False
                feks = list(fe_id.keys())
                for fek in feks:
                    feexist = fe_id[fek]
                    if (festr[3] == ("-")) :
                        if (festr[0:3] in feexist)  and (festr[3] == '0')and (festr[4:] in feexist):
                            feexist_flg = True
                    else:
                        if (festr == feexist):
                            feexist_flg = True
                        
                if feexist_flg:
                    print ("\033[93m FE Serial number exists, please correct \033[0m") 
                    return False
                elif festr[3] == ("-") or festr[3] == ("1") :
                    try: 
                        febatch = int(festr[0:3])
                        fesn = int(festr[4:])
                        if festr[3] == ("1") :
                            fe_id['FE{}'.format(fe)] = festr[0:3]+"1"+festr[4:]
                        else:
                            fe_id['FE{}'.format(fe)] = festr[0:3]+"0"+festr[4:]
                    except ValueError:
                        print ("\033[93m FE Serial number is not in right format (XXX-XXXXX), please correct\033[0m") 
                        return False
                else:
                    print ("\033[93m FE Serial number is not in right format (XXX-XXXXX), please correct\033[0m") 
                    return False
            else:
                print ("\033[93m FE Serial number is not in right format (XXX-XXXXX), please correct\033[0m") 
                return False


    while False:
        ccflg=input("\033[93m Do covers of shielding box close? (Y/N) : \033[0m")
        if ("Y" in ccflg) or ("y" in ccflg):
            break
        else:
            print ("Please close the covers and continue...")
            exit()
    return True

    #if "CD" in logs['DUT']:
    #    fsubdir = "CD_{}_{}".format(cd_id['CD0'],cd_id['CD1']) 
    #elif "ADC" in logs['DUT']:
    #    fsubdir = "ADC_{}_{}_{}_{}_{}_{}_{}_{}".format(adc_id['ADC0'],adc_id['ADC1'], adc_id['ADC2'], adc_id['ADC3'], adc_id['ADC4'], adc_id['ADC5'], adc_id['ADC6'], adc_id['ADC7']) 
    #elif "FE" in logs['DUT']:
    #    fsubdir = "FE_{}_{}_{}_{}_{}_{}_{}_{}".format(fe_id['FE0'],fe_id['FE1'], fe_id['FE2'], fe_id['FE3'], fe_id['FE4'], fe_id['FE5'], fe_id['FE6'], fe_id['FE7']) 
    #fdir = froot + fsubdir + "/"

    #return logs,  fdir



