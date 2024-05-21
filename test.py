#region loading assets
import easyocr
import cv2
import numpy as np
import matplotlib.pyplot as plt
from ultralytics import YOLO

model = YOLO("best.pt")
image = cv2.imread("toyota.png")
results = model.predict(image)
reader = easyocr.Reader(['en'])
#endregion

def getOCR(image,x,y,w,h, reader):
    real_x = x - w/2
    real_y = y - h/2
    cropped = image[int(real_y):int(real_y+h), int(real_x):int(real_x+w)]
    gray = cv2.cvtColor(cropped, cv2.COLOR_RGB2GRAY)
    results = reader.readtext(gray)
    ocr = ""
    for result in results:
        if len(results) == 1:
            ocr = result[1]
        if len(results) >1 and len(results[1])>6 and results[2]> 0.2:
            ocr = result[1]
    return ocr
for r in results:
    if r:
        for box in r.boxes:
            x, y, w, h = box.xywh[0].tolist()
            print(getOCR(image, x, y, w, h, reader))
            
            


