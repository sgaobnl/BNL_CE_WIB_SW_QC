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



###################################################################################

def ocr_tray_id(image_fp, image_fn, ocr_image_dir):
    image_path ="/".join([ image_fp , image_fn])
    if os.path.isfile(image_path): 
        pass
    else:
        print ("File not found")
        return None

    # Constants
    x=600
    y=1250
    w=1900
    h=200
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
    
    #for degree in [0, 90, 180,270]:
    for degree in [0]:
        # Rotate the image 180 degrees
        rotated_image = image.rotate(degree)
        
        # Crop the image to the central chip
        cropped_chip = rotated_image.crop(crop_box)
        
        # Convert the cropped image to OpenCV format
        open_cv_image = cv2.cvtColor(np.array(cropped_chip), cv2.COLOR_RGB2BGR)
        
        # Resize the image to make the text more clear
        resized_image = cv2.resize(open_cv_image, None, fx=1, fy=1, interpolation=cv2.INTER_CUBIC)
        
        #cv2.imwrite(ocr_image_dir, resized_image)
        cv2.imwrite(ocr_image_dir, resized_image)
        ocr_result = perform_ocr_minicpm(image_path = ocr_image_dir)
        print (ocr_result)

    return ocr_result


if __name__ == '__main__':

    fp = """C:/SGAO/ColdTest/Tested/DAT_LArASIC_QC/B009T0067/images/20250804101023_OCR/"""
    fn = """tray_label.bmp"""
    x = ocr_tray_id(image_fp=fp, image_fn = fn, ocr_image_dir = fp + "../tray_label.png")
    print (x)
