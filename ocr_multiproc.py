from pdf2image import convert_from_path
import cv2
import os
import numpy as np
import pytesseract as tess
from PIL import Image
from textblob import TextBlob
import json
import concurrent.futures
import multiprocessing
from multiprocessing import Queue
import time
# from . import parse_regex
# the line below can be commented out if you have tesseract added to your PATH. If not, then include the line below.
#tess.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
start = time.time()



# dpath stores the path of the directory where the uploaded files are stored temporarily


# gives coordinates of text boxes - called in future function
def coordinates(arr):
    max_x = int(np.amax(arr, axis=0)[0][0])
    max_y = int(np.amax(arr, axis=0)[0][1])
    min_x = int(np.amin(arr, axis=0)[0][0])
    min_y = int(np.amin(arr, axis=0)[0][1])

    return min_x, min_y, max_x, max_y


# extracts texts from image
def Image2Text(img):
    img_txt = ''
    gap = "\n"
    #resize_val = 1000
    kernel_size = 9
    #(h, w, d) = img.shape

   
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blurred, 50, 200, 255)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_size, kernel_size))
    dilate = cv2.dilate(edged, kernel, iterations=4)

    # -----------------------Contour detection-----------------------------------------------------
    contours = cv2.findContours(dilate.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)[0]
    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    len1 = len(contours)

    i = 0
    new_gray = gray
    # ------------------------------extraction of contours and then text-----------------------------------
    while i < len1:
        x1, y1, x2, y2 = coordinates(contours[i])
        cropped = new_gray[y1:y2, x1:x2]  # a text concentrated section of the cropped
        bright = cv2.inRange(cropped, 189, 255)

        #pil_image = Image.fromarray(bright)
        text = tess.image_to_string(bright,lang='eng', config='--psm 6 --oem 1  -c tessedit_char_blacklist=[]|') #-c tessedit_char_whitelist=0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ#<>(){};: ') # text is ex
        img_txt = img_txt + text + gap

        new_gray[y1:y2, x1:x2] = 255
        i += 1
    # img_txt = img_txt.replace('-\n', '')
    text = "\n".join([ll.rstrip() for ll in img_txt.splitlines() if ll.strip()])
    return text


def execute(path_pdf, name):
    # ------------------------------------------------pdf to img---------------------------------
    pages = convert_from_path(path_pdf)  # converts pdf into set of images, fmt='png'
    count = 0
    content = ''
    for page in pages:
        count += 1
        pil_image = page
        w, h = pil_image.size
        resize_val = 1000
        r = resize_val / w
        dim = (resize_val, int(h * r))
        pil_image = pil_image.resize(dim)
        open_cv_image = np.array(pil_image)
        image = cv2.cvtColor(open_cv_image, cv2.COLOR_RGB2BGR)

        # -------------------------------------------getting text from image------------------------

        document_text = Image2Text(image)

        content = content + str(document_text)

    # -----------------------------------------------saving it in a text file------------------------------
    name = name.replace('.pdf', '.txt')
    text_file_path = r'extracted' + "\\" + name
    text_file = open(text_file_path, "w")
    text_file.write(content)
    
    text_file.close()

dpath = r"working_folder"

def ocr_fun(id):
    if __name__ == '__main__':
        processes = []

        for filename in os.listdir(dpath):
            filepath = dpath + '/' + filename
            
            p = multiprocessing.Process(target=execute, args=(filepath, filename))#,queue1))
            processes.append(p)



        for process in processes:
            process.start()    

        for process in processes:
            process.join()        

        end = time.time()
        print("time elapsed: " + str(end - start))
        


ocr_fun(1)