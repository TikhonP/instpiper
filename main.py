from PIL import Image
import requests
import cv2
from io import BytesIO
from keras.preprocessing import image
from deepface.commons import distance as dst
import numpy as np
from testnamescpp import names as ansambn
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

#def ansambn(*args):
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
        return Image.open(BytesIO(response.content)).convert("RGB")
    except:
        pass

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
        self.race_model = None
        #print("race_model done")
        self.detector = None
        #print("detector done")
        self.gender_model = None
        #print('gender_models done')
        self.OpenFacemodel = None
        #print('OpenFacemodels done')
        #self.OpenFacemodel._make_predict_function()
        #self.gender_model._make_predict_function()
        #self.race_model._make_predict_function()
        #for typemodel in [self.OpenFacemodel, self.gender_model, self.race_model]:
        #    typemodel._make_predict_function()

    def run(self):
        print("I am here")
        #q = args[0]
        self.race_model = Race.loadModel()
        print("race_model done")
        self.detector = dlib.get_frontal_face_detector()
        print("detector done")
        self.gender_model = Gender.loadModel()
        print('gender_models done')
        self.OpenFacemodel = OpenFace.loadModel()
        print('OpenFacemodels done')
        self.OpenFacemodel._make_predict_function()
        self.gender_model._make_predict_function()
        self.race_model._make_predict_function()
        while True:
            acc_json = self.q.get()
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
                    vec_repres = self.OpenFacemodel.predict(preface)
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
        #user = json.loads(userdata)
        user = userdata
        returnuser = userdata
        returnuser['all_photos'] = [[get_image(user['avatar']), True]] + [[get_image(url), False] for url in user['photo_urls'][:5]]
        return returnuser

        thr = Thread(target = self.thr_func, args = (userdata, q, ))
        thr.start()
        #self.thrs.append(thr)

    def thr_func(self, userdata, q):
        if not self.is_parsed:
            userdata = extract_information(userdata, self.is_id)
        got = self.process_userjson(userdata)
        if got:
            q.put(got)

    def start_producing(self, fromind, q):
        for ind, line in enumerate(open(self.contents_path)):
            if ind < fromind:
                continue
            if q.qsize() > 100:
                time.sleep(10)
            Thread(target=self.parse_addtoque, args=(line.replace('\n', ''), q,)).start()
            time.sleep(1)

inputpath = "parsedexample.txt"

if __name__ == '__main__':
    #mp.set_start_method('spawn')
    q = mp.Queue()
    prod = Producer(is_parsed=False, contents_path=inputpath, is_id=False)
    Consumers = [Consumer(q) for _ in range(1)]
    print('prod created')
    for cns in Consumers:
        cns.start()
        time.sleep(2)
    print('producer started')
    prod.start_producing(0, q)
    for cns in Consumers:
        cns.join()
localadmin@ubuntu:~/main/InstAccClassify$
localadmin@ubuntu:~/main/InstAccClassify$
localadmin@ubuntu:~/main/InstAccClassify$
localadmin@ubuntu:~/main/InstAccClassify$ wc -l savefiltered.txt
627197 savefiltered.txt
localadmin@ubuntu:~/main/InstAccClassify$ wc -l savefiltered.txt
627215 savefiltered.txt
localadmin@ubuntu:~/main/InstAccClassify$ wc -l savefiltered.txt
627225 savefiltered.txt
localadmin@ubuntu:~/main/InstAccClassify$ wc -l savefiltered.txt
627240 savefiltered.txt
localadmin@ubuntu:~/main/InstAccClassify$ Connection reset by 176.118.213.151 port 22
PS C:\Users\User> ssh localadmin@176.118.213.151
localadmin@176.118.213.151's password:
Welcome to Ubuntu 18.04.4 LTS (GNU/Linux 4.15.0-101-generic x86_64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/advantage

 System information disabled due to load higher than 32.0

 * MicroK8s passes 9 million downloads. Thank you to all our contributors!

     https://microk8s.io/

 * Canonical Livepatch is available for installation.
   - Reduce system reboots and improve kernel security. Activate at:
     https://ubuntu.com/livepatch

0 packages can be updated.
0 updates are security updates.


Last login: Sun May 24 17:54:55 2020 from 46.242.11.200
localadmin@ubuntu:~$ cd main/
localadmin@ubuntu:~/main$ cd InstAccClassify/
localadmin@ubuntu:~/main/InstAccClassify$ touch testtest.py
localadmin@ubuntu:~/main/InstAccClassify$ nano testtest.py
localadmin@ubuntu:~/main/InstAccClassify$ localadmin@ubuntu:~/main/InstAccClassify$ python3 testtest.py
Using TensorFlow backend.
/home/localadmin/.local/lib/python3.6/site-packages/tensorflow/python/framework/dtypes.py:516: FutureWarning: Passing (type, 1) or '1type' as a synonym of type is deprecated; in a future version of numpy, it will be understood as (type, (1,)) / '(1,)type'.
  _np_qint8 = np.dtype([("qint8", np.int8, 1)])
/home/localadmin/.local/lib/python3.6/site-packages/tensorflow/python/framework/dtypes.py:517: FutureWarning: Passing (type, 1) or '1type' as a synonym of type is deprecated; in a future version of numpy, it will be understood as (type, (1,)) / '(1,)type'.
  _np_quint8 = np.dtype([("quint8", np.uint8, 1)])
/home/localadmin/.local/lib/python3.6/site-packages/tensorflow/python/framework/dtypes.py:518: FutureWarning: Passing (type, 1) or '1type' as a synonym of type is deprecated; in a future version of numpy, it will be understood as (type, (1,)) / '(1,)type'.
  _np_qint16 = np.dtype([("qint16", np.int16, 1)])
/home/localadmin/.local/lib/python3.6/site-packages/tensorflow/python/framework/dtypes.py:519: FutureWarning: Passing (type, 1) or '1type' as a synonym of type is deprecated; in a future version of numpy, it will be understood as (type, (1,)) / '(1,)type'.
  _np_quint16 = np.dtype([("quint16", np.uint16, 1)])
/home/localadmin/.local/lib/python3.6/site-packages/tensorflow/python/framework/dtypes.py:520: FutureWarning: Passing (type, 1) or '1type' as a synonym of type is deprecated; in a future version of numpy, it will be understood as (type, (1,)) / '(1,)type'.
  _np_qint32 = np.dtype([("qint32", np.int32, 1)])
/home/localadmin/.local/lib/python3.6/site-packages/tensorflow/python/framework/dtypes.py:525: FutureWarning: Passing (type, 1) or '1type' as a synonym of type is deprecated; in a future version of numpy, it will be understood as (type, (1,)) / '(1,)type'.
  np_resource = np.dtype([("resource", np.ubyte, 1)])
/home/localadmin/.local/lib/python3.6/site-packages/tensorboard/compat/tensorflow_stub/dtypes.py:541: FutureWarning: Passing (type, 1) or '1type' as a synonym of type is deprecated; in a future version of numpy, it will be understood as (type, (1,)) / '(1,)type'.
  _np_qint8 = np.dtype([("qint8", np.int8, 1)])
/home/localadmin/.local/lib/python3.6/site-packages/tensorboard/compat/tensorflow_stub/dtypes.py:542: FutureWarning: Passing (type, 1) or '1type' as a synonym of type is deprecated; in a future version of numpy, it will be understood as (type, (1,)) / '(1,)type'.
  _np_quint8 = np.dtype([("quint8", np.uint8, 1)])
/home/localadmin/.local/lib/python3.6/site-packages/tensorboard/compat/tensorflow_stub/dtypes.py:543: FutureWarning: Passing (type, 1) or '1type' as a synonym of type is deprecated; in a future version of numpy, it will be understood as (type, (1,)) / '(1,)type'.
  _np_qint16 = np.dtype([("qint16", np.int16, 1)])
/home/localadmin/.local/lib/python3.6/site-packages/tensorboard/compat/tensorflow_stub/dtypes.py:544: FutureWarning: Passing (type, 1) or '1type' as a synonym of type is deprecated; in a future version of numpy, it will be understood as (type, (1,)) / '(1,)type'.
  _np_quint16 = np.dtype([("quint16", np.uint16, 1)])
/home/localadmin/.local/lib/python3.6/site-packages/tensorboard/compat/tensorflow_stub/dtypes.py:545: FutureWarning: Passing (type, 1) or '1type' as a synonym of type is deprecated; in a future version of numpy, it will be understood as (type, (1,)) / '(1,)type'.
  _np_qint32 = np.dtype([("qint32", np.int32, 1)])
/home/localadmin/.local/lib/python3.6/site-packages/tensorboard/compat/tensorflow_stub/dtypes.py:550: FutureWarning: Passing (type, 1) or '1type' as a synonym of type is deprecated; in a future version of numpy, it will be understood as (type, (1,)) / '(1,)type'.
  np_resource = np.dtype([("resource", np.ubyte, 1)])
prod created
I am here
WARNING:tensorflow:From /home/localadmin/.local/lib/python3.6/site-packages/keras/backend/tensorflow_backend.py:4070: The name tf.nn.max_pool is deprecated. Please use tf.nn.max_pool2d instead.

producer started
2020-05-24 18:45:46.773365: I tensorflow/core/platform/profile_utils/cpu_utils.cc:94] CPU Frequency: 2199995000 Hz
2020-05-24 18:45:46.782261: I tensorflow/compiler/xla/service/service.cc:168] XLA service 0x5b45660 executing computations on platform Host. Devices:
2020-05-24 18:45:46.782363: I tensorflow/compiler/xla/service/service.cc:175]   StreamExecutor device (0): <undefined>, <undefined>
2020-05-24 18:45:46.893864: W tensorflow/compiler/jit/mark_for_compilation_pass.cc:1412] (One-time warning): Not using XLA:CPU for cluster because envvar TF_XLA_FLAGS=--tf_xla_cpu_global_jit was not set.  If you want XLA:CPU, either set that envvar, or use experimental_jit_scope to enable XLA:CPU.  To confirm that XLA is active, pass --vmodule=xla_compilation_cache=1 (as a proper command-line flag, not via TF_XLA_FLAGS) or set the envvar XLA_FLAGS=--xla_hlo_profile.
2020-05-24 18:45:47.004108: W tensorflow/core/framework/allocator.cc:107] Allocation of 411041792 exceeds 10% of system memory.
2020-05-24 18:45:47.208607: W tensorflow/core/framework/allocator.cc:107] Allocation of 411041792 exceeds 10% of system memory.
dh8rUe:tNRFOe5zzW@45.89.19.11:13926 succ
2020-05-24 18:45:47.847757: W tensorflow/core/framework/allocator.cc:107] Allocation of 411041792 exceeds 10% of system memory.
dh8rUe:tNRFOe5zzW@45.89.19.11:13926 succ
dh8rUe:tNRFOe5zzW@45.89.19.37:4254 succ
dh8rUe:tNRFOe5zzW@45.89.19.30:11824 succ
dh8rUe:tNRFOe5zzW@45.89.19.77:7684 succ
race_model done
dh8rUe:tNRFOe5zzW@45.89.19.43:8352 succ
dh8rUe:tNRFOe5zzW@45.89.19.5:19048 succ
detector done
dh8rUe:tNRFOe5zzW@45.89.19.84:17296 succ
dh8rUe:tNRFOe5zzW@45.89.19.41:4352 succ
dh8rUe:tNRFOe5zzW@45.89.19.9:5886 succ
2020-05-24 18:45:56.597399: W tensorflow/core/framework/allocator.cc:107] Allocation of 411041792 exceeds 10% of system memory.
2020-05-24 18:46:04.946200: W tensorflow/core/framework/allocator.cc:107] Allocation of 411041792 exceeds 10% of system memory.
dh8rUe:tNRFOe5zzW@45.89.19.24:18594 succ
dh8rUe:tNRFOe5zzW@45.89.19.11:13926 succ
dh8rUe:tNRFOe5zzW@45.89.19.9:17692 succ
dh8rUe:tNRFOe5zzW@45.89.19.76:7166 succ
dh8rUe:tNRFOe5zzW@45.89.19.33:18956 succ
dh8rUe:tNRFOe5zzW@45.89.19.8:11016 succ
dh8rUe:tNRFOe5zzW@45.89.18.239:12492 succ
Traceback (most recent call last):
  File "/home/localadmin/main/InstAccClassify/ParseInsta.py", line 64, in extract_information
    profile = dict(get('https://www.instagram.com/{}/?__a=1'.format(username), proxies=uproxy).json())['graphql'][
  File "/home/localadmin/.local/lib/python3.6/site-packages/requests/models.py", line 898, in json
    return complexjson.loads(self.text, **kwargs)
  File "/usr/lib/python3.6/json/__init__.py", line 354, in loads
    return _default_decoder.decode(s)
  File "/usr/lib/python3.6/json/decoder.py", line 339, in decode
    obj, end = self.raw_decode(s, idx=_w(s, 0).end())
  File "/usr/lib/python3.6/json/decoder.py", line 357, in raw_decode
    raise JSONDecodeError("Expecting value", s, err.value) from None
json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
dh8rUe:tNRFOe5zzW@45.89.18.248:10474 succ
dh8rUe:tNRFOe5zzW@45.89.18.239:12492 succ
dh8rUe:tNRFOe5zzW@45.89.19.86:11772 succ
dh8rUe:tNRFOe5zzW@45.89.19.8:11016 succ
dh8rUe:tNRFOe5zzW@45.89.19.107:8672 succ
dh8rUe:tNRFOe5zzW@45.89.19.52:18884 succ
dh8rUe:tNRFOe5zzW@45.89.19.52:18884 succ
dh8rUe:tNRFOe5zzW@45.89.19.41:4352 succ
dh8rUe:tNRFOe5zzW@45.89.19.80:15248 succ
dh8rUe:tNRFOe5zzW@45.89.19.115:6562 succ
dh8rUe:tNRFOe5zzW@45.89.19.8:11016 succ
dh8rUe:tNRFOe5zzW@45.89.18.243:3454 succ
dh8rUe:tNRFOe5zzW@45.89.19.108:5688 succ
dh8rUe:tNRFOe5zzW@45.89.19.103:4482 succ
dh8rUe:tNRFOe5zzW@45.89.19.63:12082 succ
gender_models done
dh8rUe:tNRFOe5zzW@45.89.19.76:18790 succ
Traceback (most recent call last):
  File "/home/localadmin/main/InstAccClassify/ParseInsta.py", line 64, in extract_information
    profile = dict(get('https://www.instagram.com/{}/?__a=1'.format(username), proxies=uproxy).json())['graphql'][
KeyError: 'graphql'
WARNING:tensorflow:From /home/localadmin/.local/lib/python3.6/site-packages/keras/backend/tensorflow_backend.py:4074: The name tf.nn.avg_pool is deprecated. Please use tf.nn.avg_pool2d instead.

dh8rUe:tNRFOe5zzW@45.89.19.45:3996 succ
dh8rUe:tNRFOe5zzW@45.89.19.103:4482 succ
dh8rUe:tNRFOe5zzW@45.89.19.112:6648 succ
dh8rUe:tNRFOe5zzW@45.89.18.243:16216 succ
dh8rUe:tNRFOe5zzW@45.89.19.103:4482 succ
dh8rUe:tNRFOe5zzW@45.89.18.251:5638 succ
OpenFacemodels done
WARNING:tensorflow:From /home/localadmin/.local/lib/python3.6/site-packages/keras/backend/tensorflow_backend.py:422: The name tf.global_variables is deprecated. Please use tf.compat.v1.global_variables instead.

Male gamerbroxhd 0.688288688659668 onlyname
dh8rUe:tNRFOe5zzW@45.89.19.43:8352 succ
dh8rUe:tNRFOe5zzW@45.89.19.74:6510 succ
Female kreativ_mitchel 1.578108787536621 onlyname
dh8rUe:tNRFOe5zzW@45.89.19.27:16884 succ
dh8rUe:tNRFOe5zzW@45.89.19.11:13598 succ
dh8rUe:tNRFOe5zzW@45.89.19.37:4254 succ
dh8rUe:tNRFOe5zzW@45.89.19.66:12464 succ
dh8rUe:tNRFOe5zzW@45.89.19.97:8158 succ
tobi_morbe 4.860924959182739 white Male
dh8rUe:tNRFOe5zzW@45.89.19.40:15200 succ
dh8rUe:tNRFOe5zzW@45.89.19.74:6510 succ
christopherhardtke 2.678617000579834 white Male
dh8rUe:tNRFOe5zzW@45.89.18.234:11714 succ
dh8rUe:tNRFOe5zzW@45.89.19.57:7776 succ
dh8rUe:tNRFOe5zzW@45.89.19.48:11228 succ
busch_sarah 2.2948155403137207 white Female
dh8rUe:tNRFOe5zzW@45.89.19.82:12020 succ
dh8rUe:tNRFOe5zzW@45.89.18.234:11714 succ
lostihusky 2.278212308883667 white Male
Male paul.riess 0.7008533477783203 onlyname
dh8rUe:tNRFOe5zzW@45.89.19.63:12082 succ
dh8rUe:tNRFOe5zzW@45.89.19.96:15400 succ
dh8rUe:tNRFOe5zzW@45.89.19.8:11016 succ
Traceback (most recent call last):
  File "/home/localadmin/main/InstAccClassify/ParseInsta.py", line 64, in extract_information
    profile = dict(get('https://www.instagram.com/{}/?__a=1'.format(username), proxies=uproxy).json())['graphql'][
KeyError: 'graphql'
rustymor.twitch 3.56077241897583 white Male
dh8rUe:tNRFOe5zzW@45.89.19.37:4254 succ
dh8rUe:tNRFOe5zzW@45.89.19.90:7068 succ
Male sergant.ts 1.9221642017364502 onlyname
dh8rUe:tNRFOe5zzW@45.89.19.49:6478 succ
dh8rUe:tNRFOe5zzW@45.89.19.21:16492 succ
Traceback (most recent call last):
  File "/home/localadmin/main/InstAccClassify/ParseInsta.py", line 64, in extract_information
    profile = dict(get('https://www.instagram.com/{}/?__a=1'.format(username), proxies=uproxy).json())['graphql'][
KeyError: 'graphql'
torsten.lucas 2.9373552799224854 white Male
dh8rUe:tNRFOe5zzW@45.89.19.70:14342 succ
dh8rUe:tNRFOe5zzW@45.89.19.40:15200 succ
Male eren_dbz 1.740903377532959 onlyname
dh8rUe:tNRFOe5zzW@45.89.19.74:6510 succ
dh8rUe:tNRFOe5zzW@45.89.19.86:16528 succ
Exception in thread Thread-138:
Traceback (most recent call last):
  File "/usr/lib/python3.6/threading.py", line 916, in _bootstrap_inner
    self.run()
  File "/usr/lib/python3.6/threading.py", line 864, in run
    self._target(*self._args, **self._kwargs)
  File "testtest.py", line 219, in thr_func
    userdata = extract_information(userdata, self.is_id)
  File "/home/localadmin/main/InstAccClassify/ParseInsta.py", line 52, in extract_information
    proxy = proxy.split("@")[1] + "@" + proxy.split("@")[0]
IndexError: list index out of range

m1grain3 2.387164831161499 latino hispanic Male
dh8rUe:tNRFOe5zzW@45.89.19.5:19048 succ
dh8rUe:tNRFOe5zzW@45.89.19.103:13238 succ
daniel_gaming31 2.5557870864868164 white Male
dh8rUe:tNRFOe5zzW@45.89.19.27:13974 succ
elsi_john 0.9869570732116699 white Male
dh8rUe:tNRFOe5zzW@45.89.19.26:3270 succ
Male le.dasc 0.5936195850372314 onlyname
^CError in atexit._run_exitfuncs:
Traceback (most recent call last):
  File "/usr/lib/python3.6/multiprocessing/popen_fork.py", line 28, in poll
    pid, sts = os.waitpid(self.pid, flag)
KeyboardInterrupt
Process Consumer-1:1:
Traceback (most recent call last):
  File "/usr/lib/python3.6/multiprocessing/process.py", line 258, in _bootstrap
    self.run()
  File "testtest.py", line 108, in run
    self.acc_analyzer(acc_json)
  File "testtest.py", line 114, in acc_analyzer
    faces, faceweight = self.getfacesfromphotolist(user['all_photos'])
  File "testtest.py", line 165, in getfacesfromphotolist
    for face in self.get_dlibfaces(photo[0]):
  File "testtest.py", line 174, in get_dlibfaces
    rects = self.detector(gray, 1)
KeyboardInterrupt
^CProcess HitlerClassifier-1:
Traceback (most recent call last):
  File "/usr/lib/python3.6/multiprocessing/process.py", line 258, in _bootstrap
    self.run()
  File "testtest.py", line 250, in run
    prod.start_producing(self.input_desc["from_id"], q)
  File "testtest.py", line 231, in start_producing
    time.sleep(1)
KeyboardInterrupt

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/usr/lib/python3.6/multiprocessing/process.py", line 261, in _bootstrap
    util._exit_function()
  File "/usr/lib/python3.6/multiprocessing/util.py", line 319, in _exit_function
    p.join()
  File "/usr/lib/python3.6/multiprocessing/process.py", line 124, in join
    res = self._popen.wait(timeout)
  File "/usr/lib/python3.6/multiprocessing/popen_fork.py", line 50, in wait
    return self.poll(os.WNOHANG if timeout == 0.0 else 0)
  File "/usr/lib/python3.6/multiprocessing/popen_fork.py", line 28, in poll
    pid, sts = os.waitpid(self.pid, flag)
KeyboardInterrupt

localadmin@ubuntu:~/main/InstAccClassify$ ^C
localadmin@ubuntu:~/main/InstAccClassify$ nano testtest.py
localadmin@ubuntu:~/main/InstAccClassify$ localadmin@ubuntu:~/main/InstAccClassify$ python3 testtest.py
Using TensorFlow backend.
^CTraceback (most recent call last):
  File "testtest.py", line 5, in <module>
    from keras.preprocessing import image
  File "/home/localadmin/.local/lib/python3.6/site-packages/keras/__init__.py", line 3, in <module>
    from . import utils
  File "/home/localadmin/.local/lib/python3.6/site-packages/keras/utils/__init__.py", line 6, in <module>
    from . import conv_utils
  File "/home/localadmin/.local/lib/python3.6/site-packages/keras/utils/conv_utils.py", line 9, in <module>
    from .. import backend as K
  File "/home/localadmin/.local/lib/python3.6/site-packages/keras/backend/__init__.py", line 1, in <module>
    from .load_backend import epsilon
  File "/home/localadmin/.local/lib/python3.6/site-packages/keras/backend/load_backend.py", line 90, in <module>
    from .tensorflow_backend import *
  File "/home/localadmin/.local/lib/python3.6/site-packages/keras/backend/tensorflow_backend.py", line 5, in <module>
    import tensorflow as tf
  File "/home/localadmin/.local/lib/python3.6/site-packages/tensorflow/__init__.py", line 28, in <module>
    from tensorflow.python import pywrap_tensorflow  # pylint: disable=unused-import
  File "/home/localadmin/.local/lib/python3.6/site-packages/tensorflow/python/__init__.py", line 63, in <module>
    from tensorflow.python.framework.framework_lib import *  # pylint: disable=redefined-builtin
  File "/home/localadmin/.local/lib/python3.6/site-packages/tensorflow/python/framework/framework_lib.py", line 25, in <module>
    from tensorflow.python.framework.ops import Graph
  File "<frozen importlib._bootstrap>", line 971, in _find_and_load
  File "<frozen importlib._bootstrap>", line 955, in _find_and_load_unlocked
  File "<frozen importlib._bootstrap>", line 665, in _load_unlocked
  File "<frozen importlib._bootstrap_external>", line 674, in exec_module
  File "<frozen importlib._bootstrap_external>", line 779, in get_code
  File "<frozen importlib._bootstrap_external>", line 487, in _compile_bytecode
KeyboardInterrupt
localadmin@ubuntu:~/main/InstAccClassify$ ^C
localadmin@ubuntu:~/main/InstAccClassify$ ^C
localadmin@ubuntu:~/main/InstAccClassify$ nano testtest.py
localadmin@ubuntu:~/main/InstAccClassify$ localadmin@ubuntu:~/main/InstAccClassify$ nano ParseInsta.py
localadmin@ubuntu:~/main/InstAccClassify$ nano testtest.py
localadmin@ubuntu:~/main/InstAccClassify$ localadmin@ubuntu:~/main/InstAccClassify$ cat testtest.py
from PIL import Image
import requests
import cv2
from io import BytesIO
from keras.preprocessing import image
from deepface.commons import distance as dst
import numpy as np
from testnamescpp import names as ansambn
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

#def ansambn(*args):
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
        return Image.open(BytesIO(response.content)).convert("RGB")
    except:
        pass

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
    def __init__(self, q, out_q):
        super(Consumer, self).__init__()
        self.q = q
        self.out_q = out_q
        self.race_model = None
        #print("race_model done")
        self.detector = None
        #print("detector done")
        self.gender_model = None
        #print('gender_models done')
        self.OpenFacemodel = None
        #print('OpenFacemodels done')
        #self.OpenFacemodel._make_predict_function()
        #self.gender_model._make_predict_function()
        #self.race_model._make_predict_function()
        #for typemodel in [self.OpenFacemodel, self.gender_model, self.race_model]:
        #    typemodel._make_predict_function()

    def run(self):
        print("I am here")
        #q = args[0]
        self.race_model = Race.loadModel()
        print("race_model done")
        self.detector = dlib.get_frontal_face_detector()
        print("detector done")
        self.gender_model = Gender.loadModel()
        print('gender_models done')
        self.OpenFacemodel = OpenFace.loadModel()
        print('OpenFacemodels done')
        self.OpenFacemodel._make_predict_function()
        self.gender_model._make_predict_function()
        self.race_model._make_predict_function()
        while True:
            acc_json = self.q.get()
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
                    self.out_q.put([name_gender, user['username'], user["user_id"]])
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
                self.out_q.put([gender_prediction, user['username'], user["user_id"], race_predictions])
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
        if not userdata: return None
        #user = json.loads(userdata)
        user = userdata
        returnuser = userdata
        returnuser['all_photos'] = [[get_image(user['avatar']), True]] + [[get_image(url), False] for url in user['photo_urls'][:5]]
        return returnuser

    def parse_addtoque(self, userdata, q):
        thr = Thread(target = self.thr_func, args = (userdata, q, ))
        thr.start()
        #self.thrs.append(thr)

    def thr_func(self, userdata, q):
        if not self.is_parsed:
            userdata = extract_information(userdata, self.is_id, self.proxies)
        got = self.process_userjson(userdata)
        if got:
            q.put(got)

    def start_producing(self, fromind, q):
        for ind, line in enumerate(open(self.contents_path)):
            if ind < fromind:
                continue
            if q.qsize() > 100:
                time.sleep(10)
            Thread(target=self.parse_addtoque, args=(line.replace('\n', ''), q,)).start()
            time.sleep(1)

class HitlerClassifier(mp.Process):
    def __init__(self, proxypath, inputpath, process_count, input_desc):
        super(HitlerClassifier, self).__init__()
        self.proxypath = proxypath
        self.inputpath = inputpath
        self.process_count = process_count
        self.input_desc = input_desc
        self.ready_accounts = mp.Queue()
    def run(self):
        q = mp.Queue()
        prod = Producer(proxypath = self.proxypath, is_parsed=self.input_desc['is_parsed'], contents_path=inputpath, is_id=self.input_desc['is_id'])
        Consumers = [Consumer(q, self.ready_accounts) for _ in range(self.process_count)]
        print('prod created')
        for cns in Consumers:
            cns.start()
            time.sleep(2)
        print('producer started')
        prod.start_producing(self.input_desc["from_id"], q)
        for cns in Consumers:
            cns.join()
    def get_all_ready_accs(self):
        item_list = []
        while True:
            try:
                item_list.append(self.ready_accounts.get(block=True))
            except:
                if item_list: return item_list
                return None
    def how_much_done(self):
        return self.ready_accounts.qsize()

inputpath = "parsedexample.txt"

HC = HitlerClassifier("openproxy.txt", "parsedexample.txt", 1, {'is_parsed':False, 'is_id':False, "from_id":0})
HC.start()
