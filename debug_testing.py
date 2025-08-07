import pickle 
import os
import sys
sys.path.append('./SN_recognition/')  
from SN_CLASS import SN_CLASS
from SN_chip_CPM_scan import ocr_chip



rootdir = '''C:/SGAO/ColdTest/Tested/DAT_LArASIC_QC/B009T0009/'''

#ocrbin_fp = rootdir + "ocr_results_bak.bin"
ocrbin_fp = rootdir + "ocr_results.bin"
with open(ocrbin_fp, 'rb') as fn:
    chip_ocr  = pickle.load( fn)
for key in chip_ocr.keys():
    print (chip_ocr[key])

exit()

dut_skt_n =  {'20250805145832': (25, 0), '20250805145933': (26, 1), '20250805150025': (27, 2), '20250805150122': (28, 3), '20250805150219': (29, 4), '20250805150318': (30, 5), '20250805150418': (31, 6), '20250805150518': (32, 7)}

for key in list(dut_skt_n.keys()):
    dut_chip_dir = "/".join([rootdir, 'images'])
    dut_chip_fn =  f'{key}_SN.bmp'
    sn_ocr_imgdir = "/".join([rootdir, 'images', 'SN_OCR']) 
    if not os.path.exists(sn_ocr_imgdir):  # Check if the folder already exists
        os.mkdir(sn_ocr_imgdir)

    if os.path.isfile(dut_chip_dir + "/" + dut_chip_fn):
        tray_slot = dut_skt_n[key][0]+1 #start from 1
        ocr_sn = chip_ocr[tray_slot][1]
        ocr_chip_fn =  f'SN_{ocr_sn}_Tray_{tray_slot}_{key}.bmp'.replace("-","_")
        ocr_image_dir = sn_ocr_imgdir + "/" + ocr_chip_fn
        ocr_info = ocr_chip(image_fp = dut_chip_dir, image_fn = dut_chip_fn, ocr_image_dir = ocr_image_dir, degree=180, x=1115, y=785, w=330, h=330, valid_flg=False)
        if ocr_sn not in ocr_info:
            print ("Chip to be tested have different SN from the tray scanning!")
            print (f"file path: {ocr_image_dir}")


exit()

if True:
    sn=SN_CLASS()
    chip_ocr = sn.chip_ocr(rootdir)
    
    ocrbin_fp = rootdir + "ocr_results_bak.bin"
    with open(ocrbin_fp, 'wb') as fn:
        chip_ocr  = pickle.dump(chip_ocr, fn)

ocrbin_fp = rootdir + "ocr_results_bak.bin"
if os.path.isfile(ocrbin_fp) :
    with open(ocrbin_fp, 'rb') as fn:
        chip_ocr  = pickle.load(fn)

    for key in chip_ocr.keys():
        if (chip_ocr[key][1][4:] in "RT_FE_009003635_009003760_009003561_009003515_009003507_009003558_009003628_009003620")  or (chip_ocr[key][1][4:] in "RT_FE_009003609_009003610_009003626_009003611_009003732_009003612_009003605_009003590")  or (chip_ocr[key][1][4:] in "RT_FE_009003796_009003608_009003613_009003614_009003615_009003616_009003621_009003622"):
            if len(chip_ocr[key]) == 8:
                chip_ocr[key] = chip_ocr[key] + [f'PASS_QC'] 
        if not chip_ocr[key][0]:
            if len(chip_ocr[key]) == 8:
                chip_ocr[key] = chip_ocr[key] + [f'Failed_in_OCR'] + ['Moved_to_bad_tray_slot_1']

    for key in chip_ocr.keys():
        print (chip_ocr[key])
    with open(ocrbin_fp, 'wb') as fn:
        chip_ocr  = pickle.dump(chip_ocr, fn)

