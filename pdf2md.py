import fitz
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials

from array import array
import os
import sys
import time

from io import BytesIO

from tqdm import tqdm

from txt2md import *

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY")
endpoint = os.getenv("AZURE_ENDPOINT")

computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))

cooldown = 20 # seconds, 20 calls per minute for student tier but doesn't work without cooldown

def get_images_from_pdf(pdf_file):
    pdf_file = fitz.open(pdf_file)

    images = []

    # Get Pages
    for page_index in tqdm(range(len(pdf_file))):
        page = pdf_file[page_index]
        image_list = page.get_images()

        # printing number of images found in this page
        if image_list:
            print(f"[+] Found a total of {len(image_list)} images in page {page_index}")
        else:
            print("[!] No images found on page", page_index)
        for image_index, img in enumerate(page.get_images(), start=1):
            
            # get the XREF of the image
            xref = img[0]
            
            # extract the image bytes
            base_image = pdf_file.extract_image(xref)
            image_bytes = base_image["image"]
            
            # get the image extension
            image_ext = base_image["ext"]
            images.append(image_bytes)

    return images


def get_text_from_pdf(fname: str):
    all_txt = ""

    images = get_images_from_pdf(fname)

    count = 0

    for image in tqdm(images):
        count += 1
        '''
        OCR: Read File using the Read API, extract text - local
        This example will extract text in an image
        This API call can also extract handwriting style text
        '''

        # Call API with file and raw response (allows you to get the operation location)
        read_response = computervision_client.read_in_stream(BytesIO(image),  raw=True)

        # Get the operation location (URL with an ID at the end) from the response
        read_operation_location = read_response.headers["Operation-Location"]
        # Grab the ID from the URL
        operation_id = read_operation_location.split("/")[-1]

        # Call the "GET" API and wait for it to retrieve the results 
        while True:
            read_result = computervision_client.get_read_result(operation_id)
            if read_result.status not in ['notStarted', 'running']:
                break
            time.sleep(1)

        # Append the detected text, line by line
        if read_result.status == OperationStatusCodes.succeeded:
            for text_result in read_result.analyze_result.read_results:
                for line in text_result.lines:
                    all_txt += line.text + "\n"

        # Now, sleep for cooldown period
        if (len(images)-count > 0):
            time.sleep(cooldown)

    return all_txt

if __name__ == "__main__":
    to_save_as = sys.argv[1].rsplit(".",1)[0] + ".md"
    to_save_as = to_save_as.replace("RENAMED - ", "")
    to_save_as = to_save_as.replace("PDFs", "Output")
    with open(to_save_as, "w") as f:
        #f.write(get_text_from_pdf(sys.argv[1]))
        f.write(text2mdtxt(get_text_from_pdf(sys.argv[1])))