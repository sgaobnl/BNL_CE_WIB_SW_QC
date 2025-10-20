import sys
import os
import numpy as np
from SN_chip_CPM_scan import ocr_chip
import pickle

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

class SN_CLASS():
    def __init__(self):
        self.chip_ds = {}
        pass
    #    self.imagedir =  "/images/"
        
#    def Chips_on_Tray(self, rootdir):
#        fn = rootdir  + "/chips_on_tray.txt"
#        try:
#            with open(fn, "r") as fp:
#                rmsg = fp.read() 
#        except:
#            print (f"can not open{fn}" )
#            exit()
#        tmps = rmsg.split(",")
#        for tmp in tmps:
#            try:
#                t = int(tmp)
#            except:
#                pass

    def chip_ocr(self, rootdir):
        imagedir = rootdir + "/images/"
        ocrdirs = [d for d in os.listdir(imagedir) if "_OCR" in d[-4:]]
        ocrdirs.sort()
        if len(ocrdirs) > 0:
            nocrdir =ocrdirs[-1]
        ocr_imgdir = "/".join([imagedir, nocrdir])
        post_ocr_imgdir = ocr_imgdir  + "_POST"
        if not os.path.exists(post_ocr_imgdir):  # Check if the folder already exists
            os.mkdir(post_ocr_imgdir)

        image_fns = [d for d in os.listdir(ocr_imgdir) ]
        for ifn in image_fns:
            if "tray_label" in ifn:
                pass
            else:
                if ("NAN" not in ifn) and (".bmp" in ifn) and ("tray_" in ifn):
                    tmps = ifn[0:-4].split("_")
                    if len(tmps) >= 3:
                        self.chip_ds[int(tmps[1])] = {"Degree":int(tmps[2]), "fn":ifn}
                    elif len(tmps) == 2:
                        self.chip_ds[int(tmps[1])] = {"Degree":int(180), "fn":ifn}
        chips = list(self.chip_ds.keys())
        chips.sort()
        #goodchips = {}
        #badchips = {}
        chips_ocr = {}
        for key in chips:
            fn = "/".join([ocr_imgdir , self.chip_ds[key]["fn"]])
            ocr_result = ocr_chip(image_fp = ocr_imgdir, image_fn = self.chip_ds[key]["fn"], ocr_image_dir = "/".join([post_ocr_imgdir, self.chip_ds[key]["fn"]]), degree=self.chip_ds[key]["Degree"])
            chips_ocr[key] =  ocr_result
            #print (ocr_result)
            if ocr_result[0]: #good chip
                #goodchips[key] = ocr_result
                print ("\033[92m OCR_PASS:",  key, ocr_result, "\033[0m")
            else:
                #badchips[key] = ocr_result
                print ("\033[91m OCR_FAIL: ",key, ocr_result, "\033[0m")

        with open(rootdir + "ocr_results.bin", 'wb') as fn:
            pickle.dump(chips_ocr, fn)
        return chips_ocr
        #print ( self.chip_ds)

if __name__ == '__main__':
    rootdir = "C:/SGAO/ColdTest/Tested/DAT_LArASIC_QC/B006T0001bak/"
    sn = SN_CLASS()
    #chips = sn.Chips_on_Tray(rootdir)
    sn.chip_ocr(rootdir)




