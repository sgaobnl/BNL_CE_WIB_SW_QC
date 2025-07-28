import os
import re
import pandas as pd
from PIL import Image
import cv2
import numpy as np
import requests
import base64
import io
import json

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

# Function to encode the image for MiniCPM
def encode_image(image):
    if not isinstance(image, Image.Image):
        image = Image.open(image).convert("RGB")

    max_size = 448 * 16
    if max(image.size) > max_size:
        w, h = image.size
        if w > h:
            new_w = max_size
            new_h = int(h * max_size / w)
        else:
            new_h = max_size
            new_w = int(w * max_size / h)
        image = image.resize((new_w, new_h), resample=Image.BICUBIC)

    # Convert image to base64
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    im_b64 = base64.b64encode(buffered.getvalue()).decode()

    return im_b64

# Function to perform OCR using MiniCPM API
def perform_ocr_minicpm(image_path):
    # Load and encode the image
    image = Image.open(image_path)
    encoded_image = encode_image(image)

    # API:
#    url = "http://localhost:XXXXX/api/generate"
    url = "http://wcgpu1.phy.bnl.gov:11434/api/generate"

    headers = {
        "Content-Type": "application/json",
    }

    # Set up:
    data = {
        "model": "aiden_lu/minicpm-v2.6:Q4_K_M",
        "prompt": "Please OCR this image with all output texts in one line with no space",
        "images": [encoded_image],
        "sampling": False,
        "stream": False,
        "num_beams": 3,
        "repetition_penalty": 1.2,
        "max_new_tokens": 2048,
        "max_inp_length": 4352,
        "decode_type": "beam_search",
        "options": {
            "seed": 42,
            "temperature": 0.0,
            "top_p": 0.1,
            "top_k": 10,
            "repeat_penalty": 1.0,
            "repeat_last_n": 0,
            "num_predict": 42,
        },
    }

    # Send the request to MiniCPM API
    response = requests.post(url, headers=headers, data=json.dumps(data))

    # Process the response
    if response.status_code == 200:
        try:
            responses = response.text.strip().split('\n')
            for line in responses:
                data = json.loads(line)
                actual_response = data.get("response", "")
                if actual_response:
                    return actual_response.strip()
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            return "Error: Unable to process OCR"
    else:
        print(f"Error {response.status_code}: {response.text}")
        return "Error: API request failed"



# Function to validate OCR results
def validate_ocr_result(ocr_result, process_id, ocr_image_dir):

    warnings = []

    # Extract the Serial Number in XXX-XXXXX format from the end
    serial_number_match = re.search(r"\d{3}-\d{5}$", ocr_result)

    if serial_number_match:
        serial_number = serial_number_match.group()
        #print(f"-----> Process ID #{process_id}. Serial Number (SN): {serial_number}")
    else:
        warnings.append(f"\n\n(!) ERROR (problem reading Serial Number). Please check the output .txt file and correct.")

    # Check for 5 spaces (6 words)
    space_count = ocr_result.count(' ')
    ocr_text = ocr_result.replace(' ', '')
    ocr_text = ocr_text.replace('.', '')
    ocr_text = ocr_text.replace('7', 'A')
    #warnings.append(f"(!) Warning: incorrect number of spaces.")
    #BNLLAASICVersionP5B24/19009-05518
    #words = [ocr_text[0:3],ocr_text[3:3+7],ocr_text[3+7:3+7+7],ocr_text[3+7+7:3+7+7+3],ocr_text[3+7+7+3:3+7+7+3+5],ocr_text[3+7+7+3+5:]]
    #print (words)
    bnl_pos = ocr_text.find('BNL')
    lar_pos = ocr_text.find('LArASIC')
    ver_pos = ocr_text.find('Version')
    p5b_pos = ocr_text.find('P5B')
    sls_pos = ocr_text.find('/')
    if sls_pos > 2:
        chip_wf = ocr_text[sls_pos-2:sls_pos+3]
        chip_sn = ocr_text[sls_pos+3:sls_pos+3+9]
        pat1_flg = re.fullmatch(r"\d{2}/\d{2}", chip_wf)
        pat2_flg = re.fullmatch(r"\d{3}-\d{5}", chip_sn)
    else:
        chip_wf = "00/00"
        chip_sn = "000-00000"
        pat1_flg = False
        pat2_flg = False

    if (bnl_pos >= 0) and (lar_pos > 0) and (ver_pos > 0) and (p5b_pos > 0) and (sls_pos > 0) and pat1_flg and pat2_flg:
        return [True,chip_sn, chip_wf,'BNL','LArASIC', 'Version', 'P5B', ocr_image_dir ]   
    else:
        if (p5b_pos<=0):
            print ("\033[91m Not recognized as P5B ASIC chip, marked as bad chip \033[0m")
            return [False, ocr_text, ocr_text,'BNL','LArASIC', 'Version', 'BAD', ocr_image_dir]   

        if (p5b_pos>0) and pat1_flg and pat2_flg:
            return [True,chip_sn, chip_wf,'BNL','LArASIC', 'Version', 'P5B', ocr_image_dir]   
        else:
            print ("\033[91m SN not recognized, marked as bad chip \033[0m")
            return [False, ocr_text, ocr_text, 'BNL','LArASIC', 'Version', 'BAD', ocr_image_dir]   
#            yorn = input (f"\033[91m {chip_wf} {chip_sn} correct? (Y/N): \033[0m")
#            if "Y" in yorn or "y" in yorn:
#                return [True,chip_sn, chip_wf,'BNL','LArASIC', 'Version', 'P5B']   
#            else:
#        else:
#            return [False, "00/00", "000-00000",'BNL','LArASIC', 'Version', 'BAD']   
#                if not pat1_flg:
#                    while True:
#                        chip_wf = input (f"\033[92m input ??\?? shown in picture: \033[95m")
#                        position = (300, 400)
#                        text = chip_wf
#                        draw.text(position, text, fill="blue", font=font)
#                        plt.imshow(image)
#                        plt.axis('off')
#                        plt.show()
#                        yorn = input (f"\033[91m Same? (Y/N): \033[95m")
#                        if "Y" in yorn or "y" in yorn:
#                            break
#
#                if not pat2_flg:
#                    while True:
#                        chip_sn = input (f"\033[92m input ???-????? shown in picture: \033[95m")
#                        position = (120, 550)
#                        text = chip_sn
#                        draw.text(position, text, fill="blue", font=font)
#                        plt.imshow(image)
#                        plt.axis('off')
#                        plt.show()
#                        yorn = input (f"\033[91m Same? (Y/N): \033[95m")
#                        if "Y" in yorn or "y" in yorn:
#                            break
#                return [True,chip_sn, chip_wf,'BNL','LArASIC', 'Version', 'P5B']   
#        plt.close()

       
        # Show the result
        #return [False]
#        
#



# Function to validate OCR results
#def validate_ocr_result(ocr_result, process_id, ocr_image_dir):
#
#    warnings = []
#
#    # Extract the Serial Number in XXX-XXXXX format from the end
#    serial_number_match = re.search(r"\d{3}-\d{5}$", ocr_result)
#
#    if serial_number_match:
#        serial_number = serial_number_match.group()
#        print(f"-----> Process ID #{process_id}. Serial Number (SN): {serial_number}")
#    else:
#        warnings.append(f"\n\n(!) ERROR (problem reading Serial Number). Please check the output .txt file and correct.")
#
#    # Check for 5 spaces (6 words)
#    space_count = ocr_result.count(' ')
#    ocr_text = ocr_result.replace(' ', '')
#    #warnings.append(f"(!) Warning: incorrect number of spaces.")
#    #BNLLAASICVersionP5B24/19009-05518
#    #words = [ocr_text[0:3],ocr_text[3:3+7],ocr_text[3+7:3+7+7],ocr_text[3+7+7:3+7+7+3],ocr_text[3+7+7+3:3+7+7+3+5],ocr_text[3+7+7+3+5:]]
#    #print (words)
#    bnl_pos = ocr_text.find('BNL')
#    lar_pos = ocr_text.find('LArASIC')
#    ver_pos = ocr_text.find('Version')
#    p5b_pos = ocr_text.find('P5B')
#    sls_pos = ocr_text.find('/')
#    if sls_pos > 2:
#        chip_wf = ocr_text[sls_pos-2:sls_pos+3]
#        chip_sn = ocr_text[sls_pos+3:sls_pos+3+9]
#        pat1_flg = re.fullmatch(r"\d{2}/\d{2}", chip_wf)
#        pat2_flg = re.fullmatch(r"\d{3}-\d{5}", chip_sn)
#    else:
#        chip_wf = "00/00"
#        chip_sn = "000-00000"
#        pat1_flg = False
#        pat2_flg = False
#
#    if (bnl_pos >= 0) and (lar_pos > 0) and (ver_pos > 0) and (p5b_pos > 0) and (sls_pos > 0) and pat1_flg and pat2_flg:
#        return [True,chip_sn, chip_wf,'BNL','LArASIC', 'Version', 'P5B']   
#    else:
#        from PIL import Image, ImageDraw, ImageFont
#        import matplotlib.pyplot as plt
#
#        # Load your image
#        image_path = ocr_image_dir # Replace with your image file
#        image = Image.open(image_path).convert("RGB")
#        
#        # Create drawing context
#        draw = ImageDraw.Draw(image)
#        font = ImageFont.truetype("arialbd.ttf", size=50)  # You can change the font file
#        
#        position = (5, 5) 
#        draw.text(position, ocr_text[0:20], fill="red", font=font)
#        position = (5, 65) 
#        draw.text(position, ocr_text[20:], fill="red", font=font)
#
#        if bnl_pos >= 0:
#            text = "BNL"
#            position = (280, 150) 
#            draw.text(position, text, fill="yellow", font=font)
#
#        if lar_pos >= 0:
#            text = "LArASIC"
#            position = (400, 230)
#            draw.text(position, text, fill="yellow", font=font)
#
#        if ver_pos >= 0:
#            text = "Version"
#            position = (110, 310)
#            draw.text(position, text, fill="yellow", font=font)
#
#        if p5b_pos >= 0:
#            position = (400, 310)
#            text = "P5B"
#            draw.text(position, text, fill="yellow", font=font)
#        if pat1_flg:
#            position = (300, 400)
#            text = chip_wf
#            draw.text(position, text, fill="yellow", font=font)
#        if pat2_flg:
#            position = (120, 550)
#            text = chip_sn
#            draw.text(position, text, fill="yellow", font=font)
#
#        plt.imshow(image)
#        plt.axis('off')
#        plt.show()
#
#
#        if (p5b_pos<=0):
#            print ("\033[91m Not recognized as P5B ASIC chip, marked as bad chip \033[0m")
#            return [False, "00/00", "000-00000",'BNL','LArASIC', 'Version', 'BAD']   
#
#        if (p5b_pos>0) and pat1_flg and pat2_flg:
#            return [True,chip_sn, chip_wf,'BNL','LArASIC', 'Version', 'P5B']   
#
#            yorn = input (f"\033[91m {chip_wf} {chip_sn} correct? (Y/N): \033[0m")
#            if "Y" in yorn or "y" in yorn:
#                return [True,chip_sn, chip_wf,'BNL','LArASIC', 'Version', 'P5B']   
#            else:
#                return [False, "00/00", "000-00000",'BNL','LArASIC', 'Version', 'BAD']   
#        else:
#            return [False, "00/00", "000-00000",'BNL','LArASIC', 'Version', 'BAD']   
#                if not pat1_flg:
#                    while True:
#                        chip_wf = input (f"\033[92m input ??\?? shown in picture: \033[95m")
#                        position = (300, 400)
#                        text = chip_wf
#                        draw.text(position, text, fill="blue", font=font)
#                        plt.imshow(image)
#                        plt.axis('off')
#                        plt.show()
#                        yorn = input (f"\033[91m Same? (Y/N): \033[95m")
#                        if "Y" in yorn or "y" in yorn:
#                            break
#
#                if not pat2_flg:
#                    while True:
#                        chip_sn = input (f"\033[92m input ???-????? shown in picture: \033[95m")
#                        position = (120, 550)
#                        text = chip_sn
#                        draw.text(position, text, fill="blue", font=font)
#                        plt.imshow(image)
#                        plt.axis('off')
#                        plt.show()
#                        yorn = input (f"\033[91m Same? (Y/N): \033[95m")
#                        if "Y" in yorn or "y" in yorn:
#                            break
#                return [True,chip_sn, chip_wf,'BNL','LArASIC', 'Version', 'P5B']   
#        plt.close()

       
        # Show the result
        #return [False]
#        
#
#
#    # Define the expected first four words
#    expected_first_four = ["BNL", "LArASIC", "Version", "P5B"]
#
#    # Check if there are at least 4 words to compare
#    if len(words) >= 4:
#        for i, expected_word in enumerate(expected_first_four):
#            if words[i] != expected_word:
#                warnings.append(f"(!) Warning: character mismatch in the first four words.")
#                break
#    else:
#        warnings.append(f"(!) Warning: insufficient number of words.")
#
#    # Check the format of the 5th word: "AB/CD" where A, B, C, D are digits
#    if len(words) >= 5:
#        fifth_word = words[4]
#        if not re.fullmatch(r"\d{2}/\d{2}", fifth_word):
#            warnings.append(f"(!) Warning: character mismatch in the 5th word.")
#    else:
#        warnings.append(f"(!) Warning: Potential Error (missing 5th word).")
#
#
#    # Print all warnings
#    for warning in warnings:
#        print(warning)
#
#    if len(warnings) > 0:
#        return False
#    else:
#        return True

###################################################################################

def ocr_chip(image_fp, image_fn, ocr_image_dir, degree):
    image_path ="/".join([ image_fp , image_fn])
#    if "_SN" not in image_fn:
#        print (f"{image_fn} is wrong")
    if os.path.isfile(image_path): 
        pass
    else:
        print ("File not found")
        return None

    # Constants
    x=350
    y=220
    w=330
    h=330
    crop_box = (x, y, x+w, y+h)  # (x, y, x+w, y+h)
    
    # Extract image_number from the filename (assuming it's before the first '_')
    image_number = image_fn.split('_')[0]
    
    # Create a directory with the name of image_number
    #os.makedirs(image_number, exist_ok=True)
    
    try:
        # Open the image
        #print (image_path)
        image = Image.open(image_path)
    except IOError as e:
        #print(f"Process ID #{image_number}: ERROR (cannot open image). {e}")
        return None
    
    # Rotate the image 180 degrees
    rotated_image = image.rotate(degree)
    
    # Crop the image to the central chip
    cropped_chip = rotated_image.crop(crop_box)
    
    # Convert the cropped image to OpenCV format
    open_cv_image = cv2.cvtColor(np.array(cropped_chip), cv2.COLOR_RGB2BGR)
    
    # Resize the image to make the text more clear
    resized_image = cv2.resize(open_cv_image, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    
    #cv2.imwrite(ocr_image_dir, resized_image)
    cv2.imwrite(ocr_image_dir, resized_image)
    ocr_result = perform_ocr_minicpm(image_path = ocr_image_dir)
    #print (ocr_result)

    ocr_info =  validate_ocr_result(ocr_result, image_number, ocr_image_dir)
    return ocr_info


if __name__ == '__main__':

    fp = """C:/SGAO/ColdTest/Tested/DAT_LArASIC_QC/Tested/B099T0097/images/20250612163810_OCR/"""
    fn = """tray_56_270.bmp"""
    x = ocr_chip(image_fp=fp, image_fn = fn, ocr_image_dir = fp + "/1_ocr.png", degree=270)
    print (x)
