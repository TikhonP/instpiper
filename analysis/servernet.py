from usefulfunctions import *
#from testnamescpp import names as ansambn
from ParseInsta import extract_information
from PIL import Image
import dlib
from imutils import face_utils
import tensorflow as tf
import imutils
import time
import traceback
import cv2
import multiprocessing as mp
import json
from deepface.basemodels import OpenFace
from threading import Thread
from deepface.extendedmodels import Gender, Race
from deepface.commons import functions
import numpy as np

def ansambn(*args):
    return ["M"]

transgender = {'F':'Female', 'M':'Male'}
sharedmemory = {}
minimgsize = 32 ** 2
MODEL_MEAN_VALUES = (78.4263377603, 87.7689143744, 114.895847746)
age_list = ['0-2 years', '4-6 years', '8-12 years', '15-20 years', '25-32 years', '38-43 years', '48-53 years', '60-100 years']
gender_list = ['Female', 'Male']
race_labels = ['asian', 'indian', 'black', 'white', 'middle eastern', 'latino hispanic']
threshold = functions.findThreshold('OpenFace', 'cosine')
outputfile = ""

class Consumer(mp.Process):
    def __init__(self, q):
        super(Consumer, self).__init__()
        self.q = q
        self.race_model = Race.loadModel()
        print("race_model done")
        self.detector = dlib.get_frontal_face_detector()
        print("detector done")
        self.gender_model = Gender.loadModel()
        print('gender_models done')
        self.OpenFacemodel = OpenFace.loadModel()
        print('OpenFacemodels done')

        for typemodel in [self.OpenFacemodel, self.gender_model, self.race_model]:
            typemodel._make_predict_function()

    def run(self):
        #q = args[0]
        while True:
            acc_json = self.q.get()
            print("got something", acc_json)
            self.acc_analyzer(acc_json)

    def acc_analyzer(self, acc_json):
        try:
            starttime = time.time()
            user = acc_json
            faces, faceweight = self.getfacesfromphotolist(user['all_photos'])
            namegenderpred = ansambn(user['username'], user['full_name'])
            namegenderpred = list(namegenderpred)
            if namegenderpred[0]:
                namegenderpred[0] = namegenderpred[0].upper()
            faceweight += 2 if namegenderpred[0] else -1
            if faceweight < 3:
                if namegenderpred[0]:
                    name_gender = transgender[namegenderpred[0]]
                    print(name_gender, user['username'], time.time() - starttime, 'onlyname')
                    #self.save_output(name_gender, user['username'], user["user_id"])
                return
            namegendvec = np.array([0.6 if namegenderpred[0] and namegenderpred[0].upper() == 'F' else 0.0, 0.6 if namegenderpred[0] and namegenderpred[0].upper() == 'M' else 0.0])
            enc, nfaces = self.get_encodings(faces)
            if enc and 'username' in user:
                center_face = centroid_face(enc)
                facearr = np.array(nfaces[center_face][0])
                img_224 = preprocess_face(facearr, target_size=(224, 224), gray_scale=False)
                gender_prediction = self.get_gender_multiple([img_224], namegendvec)
                race_predictions = self.get_race(img_224)
                print(user['username'], time.time() - starttime, race_predictions, gender_prediction)
                #self.save_output(gender_prediction, user['username'], user["user_id"], race_predictions)

        except Exception:
            traceback.print_exc()

    def get_gender_multiple(self, preprfaces, namevec):
        sumvec = np.array([0.0, 0.0])
        for fc in preprfaces:
            prd = self.gender_model.predict(fc)[0]
            sumvec += prd
        meanvec = sumvec / len(preprfaces)
        meanvec = meanvec + namevec
        return gender_list[np.argmax(meanvec)]

    def save_output(self, *args):
        with open(outputfile, 'a') as f:
            f.write(';'.join(map(str, args)) + '\n')

    def get_race(self, prep_img):
        race_predictions = self.race_model.predict(prep_img)[0, :]
        return race_labels[np.argmax(race_predictions)]

    def getfacesfromphotolist(self, photolist):
        avatartranslate = {True: 3, False: 1}
        faces = []
        faceweight = 0
        for photo in photolist:
            toextend = []
            for face in self.get_dlibfaces(photo[0]):
                faceweight += avatartranslate[photo[1]]
                toextend.append([face, avatartranslate[photo[1]]])
            faces.extend(toextend)
        return faces, faceweight

    def get_dlibfaces(self, img):
        nimage = imutils.resize(np.array(img), width=500)
        gray = cv2.cvtColor(nimage, cv2.COLOR_BGR2GRAY)
        rects = self.detector(gray, 1)
        for rect in rects:
            (x, y, w, h) = face_utils.rect_to_bb(rect)
            face = Image.fromarray(nimage).crop((x, y, x + w, y + h))
            yield face

    def get_encodings(self, faces):
        encodings = []
        normfaces = []
        input_shape = self.OpenFacemodel.layers[0].input_shape[1:3]
        for face in faces:
            try:
                if (face[0].size[0] * face[0].size[1]) > minimgsize:
                    preface = preprocess_face(np.array(face[0]), target_size=input_shape)
                    vec_repres = self.OpenFacemodel.predict(preface)[0, :]
                    encodings.append([vec_repres, face[1]])
                    normfaces.append(face)
            except:
                traceback.print_exc()
        return encodings, normfaces


class Producer():
    def __init__(self, is_parsed, contents_path, is_id=False):
        self.contents_path = contents_path
        self.is_id = is_id
        self.is_parsed = is_parsed
        self.thrs = []

    def process_userjson(self, userdata):
        if not userdata: return None
        user = json.loads(userdata)
        returnuser = userdata
        returnuser['all_photos'] = [get_image(user['avatar']), True] + [[get_image(url), False] for url in user['photo_urls'][:5]]
        return returnuser

    def parse_addtoque(self, userdata, q):
        print("in parse_addtoque")
        thr = Thread(target = self.thr_func, args = (userdata, q, ))
        thr.start()
        #self.thrs.append(thr)

    def thr_func(self, userdata, q):
        print("in thr_func")
        if not self.is_parsed:
            userdata = extract_information(userdata, self.is_id)
            print("extracted info")
        print(userdata)
        got = self.process_userjson(userdata)
        if got:
            q.put(got)

    def start_producing(self, fromind, q):
        print("started producing")
        for ind, line in enumerate(open(self.contents_path)):
            if ind < fromind:
                continue
            if q.qsize() > 100:
                time.sleep(10)
            Thread(target=self.parse_addtoque, args=(line.replace('\n', ''), q,)).start()
            time.sleep(1)

inputpath = "parsedexample.txt"

if __name__ == '__main__':
    mp.set_start_method('spawn')
    q = mp.Queue()
    Consumers = [Consumer(q) for _ in range(1)]
    prod = Producer(is_parsed=False, contents_path=inputpath, is_id=True)
    print('prod created')
    for cns in Consumers:
        cns.start()
        time.sleep(2)
    print('producer started')
    prod.start_producing(0, q)
    for cns in Consumers:
        cns.join()