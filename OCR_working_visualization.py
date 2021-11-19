from nltk.util import pr
from numpy.core.fromnumeric import diagonal, resize
from pdf2image import convert_from_path
import cv2
import numpy as np
import pytesseract as tess
from PIL import Image
from textblob import TextBlob
import time




path_pdf = r'sample_pdf\invoice_sample.pdf'


def coordinates(arr):
    # arr = np.array(arrr)
    max_x = int(np.amax(arr, axis=0)[0][0])
    max_y = int(np.amax(arr, axis=0)[0][1])
    min_x = int(np.amin(arr, axis=0)[0][0])
    min_y = int(np.amin(arr, axis=0)[0][1])


    return  min_x, min_y, max_x, max_y


def contour_support(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blurred, 50, 200, 255)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9,9))
    dilate = cv2.dilate(edged, kernel, iterations=4)

    return dilate,gray,blurred,edged,kernel


def Image2Text(image):

    img_txt = ''
    gap = "\n"
    resize_val = 1000 
    (h, w , d) = image.shape


    r = resize_val / w
    dim = (resize_val, int(h * r))
    resized = cv2.resize(image, dim)
    temp = resized
    resized = image
    image = temp 

    cv2.imshow("Aspect Ratio Resize",  image)
    cv2.imshow("orig", resized)

    cv2.waitKey(0)
    cv2.destroyAllWindows()    
    (h, w , d) = image.shape
    blank = np.zeros((h, w, d), dtype='uint8')

    dilate,gray,blurred,edged,kernel = contour_support(image)



    cnts = cv2.findContours(dilate.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)[0]
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)
    len1 = len(cnts)
    # loop over the contours
   
    cv2.drawContours(blank, cnts, -1, (0,0,255), 1)
    cv2.drawContours(image, cnts, -1, (0,0,255), 1)
  
    cv2.imshow("Orignal", image)
    cv2.imshow("contours drawn", blank)


    cv2.waitKey(0)
    cv2.destroyAllWindows()    
      
#---------------------------------DELETE------------------------
    counter1 = 0
    for i in cnts:  
        x1,y1,x2,y2 = coordinates(cnts[counter1])
        cv2.rectangle(image,(x1,y1),(x2,y2),(0,255,0),5)
        counter1 += 1
    cv2.imshow("Orignal", image)
    cv2.waitKey(0)

    cv2.destroyAllWindows()
#---------------------------------------------------------

    i = 0 

    new_gray = gray 

    while i < len1:
        x1,y1,x2,y2 = coordinates(cnts[i])
        cropped = new_gray[y1:y2, x1:x2]
        cv2.imshow("orignal",gray)
        

        bright = cv2.inRange(cropped, 185, 255)

        cv2.imshow("cropped", bright)
        pil_image = Image.fromarray(bright)


        text = tess.image_to_string(bright,lang='eng', config='--psm 1 --oem 1  -c tessedit_char_blacklist=[]|') #-c tessedit_char_whitelist=0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ#<>(){};: ') # text is ex
        img_txt = img_txt + text + gap
        text = "\n".join([ll.rstrip() for ll in img_txt.splitlines() if ll.strip()])


        print(text)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        new_gray[y1:y2, x1:x2] = 255

        i += 1

    return text





#---------------------------------------------------Converting Pdf to Jpg------------------------------------------------------------


pages = convert_from_path(path_pdf)
print(type(pages))
count = 0
corrected_document_text = []
start = time.time()
content = ''
for page in pages:
    count +=1
    pil_image = page 
    open_cv_image = np.array(pil_image) 
    image = cv2.cvtColor(open_cv_image, cv2.COLOR_RGB2BGR)

# --------------------------------------------getting text from image------------------------


    document_text = Image2Text(image)
    corrected_document_text = TextBlob(document_text)
  
    content = content + str(corrected_document_text) 

text_file = open("data.txt", "w")
n = text_file.write(content)
text_file.close()

end = time.time()

print(" ")
print("start time  : "+ str(start))
print("end time    : "+ str(end))
print("time elapsed: "+ str(end - start))
