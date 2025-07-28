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
def validate_ocr_result(ocr_result, process_id):

    warnings = []

    # Extract the Serial Number in XXX-XXXXX format from the end
    serial_number_match = re.search(r"\d{3}-\d{5}$", ocr_result)

    if serial_number_match:
        serial_number = serial_number_match.group()
        print(f"-----> Process ID #{process_id}. Serial Number (SN): {serial_number}")
    else:
        warnings.append(f"\n\n(!) ERROR (problem reading Serial Number). Please check the output .txt file and correct.")

    # Check for 5 spaces (6 words)
    space_count = ocr_result.count(' ')
    if space_count != 5:
        warnings.append(f"(!) Warning: incorrect number of spaces.")

    # Split the OCR result into words
    words = ocr_result.split()

    # Define the expected first four words
    expected_first_four = ["BNL", "LArASIC", "Version", "P5B"]

    # Check if there are at least 4 words to compare
    if len(words) >= 4:
        for i, expected_word in enumerate(expected_first_four):
            if words[i] != expected_word:
                warnings.append(f"(!) Warning: character mismatch in the first four words.")
                break
    else:
        warnings.append(f"(!) Warning: insufficient number of words.")

    # Check the format of the 5th word: "AB/CD" where A, B, C, D are digits
    if len(words) >= 5:
        fifth_word = words[4]
        if not re.fullmatch(r"\d{2}/\d{2}", fifth_word):
            warnings.append(f"(!) Warning: character mismatch in the 5th word.")
    else:
        warnings.append(f"(!) Warning: Potential Error (missing 5th word).")


    # Print all warnings
    for warning in warnings:
        print(warning)

    if len(warnings) > 0:
        return False
    else:
        return True

###################################################################################

def ocr_chip(image_fp, image_fn, ocr_image_dir):
    image_path = image_fp + image_fn
    if "_SN" not in image_fn:
        print (f"{image_fn} is wrong")
    elif os.path.isfile(image_path): 
        pass
    else:
        print ("File not found")
        return None

    # Constants
    crop_box = (1120, 792, 1120 + 326, 792 + 326)  # (x, y, x+w, y+h)
    
    # Extract image_number from the filename (assuming it's before the first '_')
    image_number = image_fn.split('_')[0]
    
    # Create a directory with the name of image_number
    #os.makedirs(image_number, exist_ok=True)
    
    try:
        # Open the image
   #     print (image_path)
        image = Image.open(image_path)
    except IOError as e:
        print(f"Process ID #{image_number}: ERROR (cannot open image). {e}")
        return None
    
    # Rotate the image 180 degrees
    rotated_image = image.rotate(180)
    
    # Crop the image to the central chip
    cropped_chip = rotated_image.crop(crop_box)
    
    # Convert the cropped image to OpenCV format
    open_cv_image = cv2.cvtColor(np.array(cropped_chip), cv2.COLOR_RGB2BGR)
    
    # Resize the image to make the text more clear
    resized_image = cv2.resize(open_cv_image, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    
    #cv2.imwrite(ocr_image_dir, resized_image)
    cv2.imwrite(ocr_image_dir, resized_image)
    ocr_result = perform_ocr_minicpm(image_path = ocr_image_dir)

    #ocr_flg =  validate_ocr_result(ocr_result, image_number)
    ocr_flg = True
    if ocr_flg: 
        # Save the resized image tepmorarily to disk
        return ocr_result
    else:
        print ("invalid result")
        return False

#def ocr_chip(ocr_image_dir):
#    
##        temp_image_path = os.path.join(ocr_results_dir, f"{image_number}.png")
##        cv2.imwrite(temp_image_path, resized_image)
##
##        #print (ocr_results_dir)
##        #temp_image_path = os.path.join(ocr_results_dir, f"{image_number}.png")
##        #image = Image.open(os.path.join(ocr_results_dir, f"{image_number}.png"))
##        #rotated_image = image.rotate(180)
##        #open_cv_image = cv2.cvtColor(np.array(rotated_image), cv2.COLOR_RGB2BGR)
##        #cv2.imwrite(temp_image_path, open_cv_image)
#    
#        # Perform OCR using MiniCPM
#        ocr_result = perform_ocr_minicpm(temp_image_path)
#    
#        # Save the OCR result to a text file
#        #ocr_output_path = os.path.join(image_number, f"{image_number}.txt")
#        #with open(ocr_output_path, 'w') as f:
#            #f.write(ocr_result)
#    
#         # Save the OCR result to a txt file
#        #ocr_output_path = os.path.join(ocr_results_dir, f"{image_number}.txt")
#        #with open(ocr_output_path, 'w') as f:
#        #    f.write(ocr_result)
#    
#        # Validate the OCR result
#        validate_ocr_result(ocr_result, image_number)
#        return ocr_result
#    
##        print(f"Processed image {image_path}\nOCR result saved to {ocr_output_path}")
##        print("***********************************************************************")
#    

if __name__ == '__main__':

    root = """E:/tmp/008/"""
    fss = []
    for root, dirs, files in os.walk(root):
        for fn in files:
            if "_SN.bmp" in fn:
                x = ocr_chip(image_fp=root, image_fn = fn, ocr_image_dir = root + "ocred/" + fn[0:-4] + ".png")
                chip_sns = ["3495", "3549", "3493","3497","3525","3529","3555","3551","3490","3518"]
                for chip_sn in chip_sns:
                    if chip_sn in x:
                        print (fn, x)
