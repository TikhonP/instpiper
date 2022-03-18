from PIL import Image
import requests
import cv2
from io import BytesIO
from keras.preprocessing import image
from deepface.commons import distance as dst
import numpy as np
from parsenames_lib.namesc import names as ansambn
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
from functools import reduce
from arthurmodels import FaceGenderModel


# def ansambn(*args):
#    return ["M"]


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
        return Image.open(BytesIO(response.content)).convert('RGB')
    except:
        pass


transgender = {'F': 'Female', 'M': 'Male'}
sharedmemory = {}
minimgsize = 32 ** 2
MODEL_MEAN_VALUES = (78.4263377603, 87.7689143744, 114.895847746)
age_list = ['0-2 years', '4-6 years', '8-12 years', '15-20 years',
            '25-32 years', '38-43 years', '48-53 years', '60-100 years']
gender_list = ['Female', 'Male']
race_labels = ['asian', 'indian', 'black',
               'white', 'middle eastern', 'latino hispanic']
threshold = functions.findThreshold('OpenFace', 'cosine')
outputfile = ''


class Consumer(mp.Process):
    def __init__(self, q, out_q):
        super(Consumer, self).__init__()
        self.q = q
        self.out_q = out_q
        self.race_model = None
        self.detector = None
        self.gender_model = None
        self.OpenFacemodel = None
        self.last_time = time.time()
        self.cns_done = False

    def run(self):
        print('I am here')
        #q = args[0]
        self.race_model = Race.loadModel()
        print('race_model done')
        self.detector = dlib.get_frontal_face_detector()
        print('detector done')
        self.gender_model = FaceGenderModel()
        print('gender_models done')
        self.OpenFacemodel = OpenFace.loadModel()
        print('OpenFacemodels done')
        self.OpenFacemodel._make_predict_function()
        #self.gender_model._make_predict_function()
        self.race_model._make_predict_function()
        self.last_time = time.time()
        while True:
            try:
                acc_json = self.q.get(block = True, timeout=3)
                self.last_time = time.time()
            except:
                if (time.time() - self.last_time) > 60:
                    break
                continue
            self.acc_analyzer(acc_json)
        self.cns_done = True
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
                if namegenderpred[0] and namegenderpred[0] != 'E':
                    name_gender = transgender[namegenderpred[0]]
                    print(name_gender, user['username'],
                          time.time() - starttime, 'onlyname')
                    self.out_q.put(
                        [name_gender, None, user['username'], user['user_id'], None, 'just_name'])
                else:
                    self.out_q.put(
                        [None, user['username'], user['user_id'], None, 'unknown acc'])
                    #self.save_output(name_gender, user['username'], user["user_id"])
                return
            namegendvec = np.array([0.6 if namegenderpred[0] and namegenderpred[0] != 'E' and namegenderpred[0].upper(
            ) == 'F' else 0.0, 0.6 if namegenderpred[0] and namegenderpred[0] != 'E' and namegenderpred[0].upper() == 'M' else 0.0])
            enc, nfaces = self.get_encodings(faces)
            if enc and 'username' in user:
                center_face = centroid_face(enc)
                facearr = np.array(nfaces[center_face][0])
                img_224 = preprocess_face(
                    facearr, target_size=(224, 224), gray_scale=False)
                gender_prediction = self.get_gender_multiple(
                    [nfaces[center_face][0]], namegendvec)
                race_predictions = self.get_race(img_224)
                print(user['username'], time.time() - starttime,
                      race_predictions, gender_prediction)
                self.out_q.put(
                    [gender_prediction, user['username'], user['user_id'], race_predictions, 'full_analys'])
                return
                #self.save_output(gender_prediction, user['username'], user["user_id"], race_predictions)

        except Exception:
            traceback.print_exc()
        self.out_q.put([None, None, None, None, "just_nones"])

    def get_gender_multiple(self, preprfaces, namevec):
        sumvec = np.array([0.0, 0.0])
        for fc in preprfaces:
            prd = self.gender_model.predict(fc)[0]
            sumvec += prd
        meanvec = sumvec / len(preprfaces)
        print(meanvec, "meanvec do")
        meanvec = meanvec + namevec
        print(meanvec, "meanvec posle")
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
                    preface = preprocess_face(
                        np.array(face[0]), target_size=input_shape)
                    vec_repres = self.OpenFacemodel.predict(preface)
                    vec_repres = self.OpenFacemodel.predict(preface)[0, :]
                    encodings.append([vec_repres, face[1]])
                    normfaces.append(face)
            except:
                traceback.print_exc()
        return encodings, normfaces


class Producer():
    def __init__(self, proxypath, is_parsed, contents_path, is_id=False):
        self.contents_path = contents_path
        self.is_id = is_id
        self.proxies = open(proxypath).read().split('\n')
        self.is_parsed = is_parsed
        self.thrs = []

    def process_userjson(self, userdata):
        if not userdata:
            return None
        #user = json.loads(userdata)
        user = userdata
        returnuser = userdata
        returnuser['all_photos'] = [[get_image(
            user['avatar']), True]] + [[get_image(url), False] for url in user['photo_urls'][:5]]
        return returnuser

    def thr_func(self, userdata, q, shm):
        if not self.is_parsed:
            userdata, stats = extract_information(userdata, self.is_id, self.proxies)
            for i, key in enumerate(stats):
                shm[i] += stats[key]
        if userdata:
            got = self.process_userjson(userdata)
            q.put(got)

    def start_producing(self, fromind, q, shm):
        for ind, line in enumerate(open(self.contents_path)):
            if ind < fromind:
                continue
            if q.qsize() > 100:
                time.sleep(10)
            Thread(target=self.thr_func, args=(
                line.replace('\n', ''), q, shm, )).start()
            time.sleep(1)


class MainClassifier(mp.Process):
    def __init__(self, proxypath, inputpath, process_count, input_desc):
        super(MainClassifier, self).__init__()
        self.proxypath = proxypath
        self.inputpath = inputpath
        self.howmuch = 0
        self.process_count = process_count
        self.input_desc = input_desc
        self.ready_accounts = mp.Queue()
        self.done = False
        self.proxystats = mp.Array('i', [0, 0])

    def run(self):
        q = mp.Queue()
        prod = Producer(proxypath=self.proxypath, is_parsed=self.input_desc['is_parsed'], contents_path=self.inputpath, is_id=self.input_desc['is_id'])
        cnsms = [Consumer(q, self.ready_accounts) for _ in range(self.process_count)]
        for cns in cnsms:
            cns.start()
            time.sleep(2)
        print('producer started')
        prod.start_producing(self.input_desc['from_id'], q, self.proxystats, )


    def get_all_ready_accs(self):
        item_list = []
        while True:
            try:
                item_list.append(
                    self.ready_accounts.get(block=True, timeout=3))
            except:
                if item_list:
                    self.howmuch += len(item_list)
                    return item_list
                return None

    def how_much_done(self):
        return self.ready_accounts.qsize() + self.howmuch



