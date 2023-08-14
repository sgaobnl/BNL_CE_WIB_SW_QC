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


def dat_user_input(infile_mode = False, froot = "./tmp_data/" ):
    ag = argparse.ArgumentParser()
    ag.add_argument("-t", "--task", help="which QC tasks to be performed", type=int, choices=[0,1,2,3,4,5,6,7,8,9,10],  nargs='+', default=[0,1,2,3,4,5,6,7,8,9,10])
    args = ag.parse_args()   
    tms = args.task

    logs={}
    logs['date']=datetime.datetime.now().strftime("%m_%d_%Y_%H_%M_%S")
    
    if infile_mode:
        while True:
            csvfile = input ("\033[95m Is asic_info.csv updated? (Y/N) : \033[0m" )
            if ("Y" in csvfile) or ("y" in csvfile):
                pass
            else:
                continue

            logs={}
            logs['date']=datetime.datetime.now().strftime("%m_%d_%Y_%H_%M_%S")
            index_f = "./asic_info.csv"
            with open(index_f, 'r') as fp:
                for cl in fp:
                    tmp = cl.split(",")
                    tmp = tmp[:-1]
                    logs[tmp[0]] = tmp[1]

            fe_id = {}
            re_flg = False
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
                        re_flg = True
                        break
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
                            re_flg = True
                            break
                    else:
                        print ("\033[93m FE Serial number is not in right format (XXX-XXXXX), please correct\033[0m") 
                        re_flg = True
                        break
                else:
                    print ("\033[93m FE Serial number is not in right format (XXX-XXXXX), please correct\033[0m") 
                    re_flg = True
                    break
            if not re_flg:
                break
            else:
                logs={}
                logs['date']=datetime.datetime.now().strftime("%m_%d_%Y_%H_%M_%S")

    else:
        tester=input("please input your name:  ")
        logs['tester']=tester
        testsite=input("please input test location (eg. BNL):  ")
        logs['testsite']=testsite
        env_cs = input("Test is performed at cold(LN2) (Y/N)? : ")
        if ("Y" in env_cs) or ("y" in env_cs):
            env = "LN"
        else:
            env = "RT"
        logs['env']=env
    
        note = input("A short note (<200 letters):")
        logs['note']=note
    
        while True:
            datsn=input("DAT Serial Number :")
            try :
                datsnno = int(datsn)
                break
            except ValueError:
                print ("ValueError: Wrong input, please input a number ")
        datsn = "1"
        logs['DAT_SN']=datsn
    
        #while True:
        #    datowib=input("DAT on WIB slot (0, 1, 2, 3) :")
        #    try :
        #        datno = int(datowib)
        #        if datno>=0 and datno <=3:
        #            dat.fembs = [datno]
        #            break
        #        else:
        #            print ("Wrong input, please input number 0 to 3")
        #    except ValueError:
        #        print ("ValueError: Wrong input, please input number 0 to 3")
    
        #while True:
        #    datowib=input("is DAT on WIB slot 0? (Y/N) :")
        #    if ("Y" in datowib) or ("y" in datowib):
        #        fembs = [0]
        #        break
        #    else:
        #        print ("\033[91m Please contact tech coordinator...\033[0m")
        #        print ("Exit anyway")
        #        exit()
    
        logs['DAT_on_WIB_slot']=""
        for femb_id in fembs:
            logs['DAT_on_WIB_slot']+="FEMB%02d--"%femb_id
        logs['DAT_on_WIB_slot']+= "\n"
    
        fe_id = {}
        for fe in range(8):
            while True:
                festr = input("FE SN on socket {}: ".format(fe))
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
                        print ("\033[93m FE Serial number exists, please re-enter\033[0m") 
                    elif festr[3] == ("-") or festr[3] == ("1") :
                        try: 
                            febatch = int(festr[0:3])
                            fesn = int(festr[4:])
                            if festr[3] == ("1") :
                                fe_id['FE{}'.format(fe)] = festr[0:3]+"1"+festr[4:]
                            else:
                                fe_id['FE{}'.format(fe)] = festr[0:3]+"0"+festr[4:]
                            break
                        except ValueError:
                            print ("\033[93m FE Serial number is not in right format (XXX-XXXXX), please re-enter\033[0m") 
                    else:
                        print ("\033[93m FE Serial number is not in right format (XXX-XXXXX), please re-enter\033[0m") 
                else:
                    print ("\033[93m FE Serial number is not in right format (XXX-XXXXX), please re-enter\033[0m") 
    
    while True:
        ccflg=input("\033[93m Do covers of shielding box close? (Y/N) : \033[0m")
        if ("Y" in ccflg) or ("y" in ccflg):
            break
        else:
            print ("Please close the covers and continue...")
            exit()
    
    fsubdir = "FE_{}_{}_{}_{}_{}_{}_{}_{}".format(fe_id['FE0'],fe_id['FE1'], fe_id['FE2'], fe_id['FE3'], fe_id['FE4'], fe_id['FE5'], fe_id['FE6'], fe_id['FE7']) 
    fdir = froot + fsubdir + "/"
    #print (fdir)

    #tms=[0,1,2,3,4,5,6,7,8,9,10]

    return logs,  fdir, tms
