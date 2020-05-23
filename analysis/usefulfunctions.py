from PIL import Image
import requests
import cv2
from io import BytesIO
from keras.preprocessing import image
from deepface.commons import distance as dst
import numpy as np
import tensorflow as tf



def preprocess_face(face, target_size=(224, 224), gray_scale=False):
    if gray_scale:
        face = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
    img = cv2.resize(face, target_size)
    img_pixels = image.img_to_array(img)
    img_pixels = np.expand_dims(img_pixels, axis=0)
    img_pixels /= 255
    return img_pixels

def centroid_face(encodings):
    encodings = encodings
    encodings[0][1] -= 1
    centervec = encodings[0][0]
    allcount = 1
    for enc in encodings:
        for c in range(enc[1]):
            allcount += 1
            centervec += enc[0]
    centervec = centervec / allcount
    minndist = float('inf')
    minnind = 0
    for ind in range(len(encodings)):
        dist = dst.findCosineDistance(centervec, encodings[ind][0])
        if dist < minndist:
            minndist = dist
            minnind = ind
    return minnind

def get_image(url):
    try:
        response = requests.get(url)
        return Image.open(BytesIO(response.content)).convert("RGB")
    except:
        pass

