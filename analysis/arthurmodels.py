from torch import nn
import os
import dlib
from PIL import Image
from torchvision import models
from torchvision import transforms
import torch
class FaceGenderModel():
    def __init__(self):
        self.model = models.resnet50(False)
        self.model.fc = nn.Linear(2048, 2)
        self.model.load_state_dict(torch.load('second_weights'))
        self.model.eval()
        self.transform = transforms.Compose([
    transforms.Resize((250,200)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]), ])
    def cutting_image(self,path):
        detector = dlib.get_frontal_face_detector()
        print("Processing file: {}".format(path))
        img = dlib.load_rgb_image(path)
        dets = detector(img, 1)
        print("Number of faces detected: {}".format(len(dets)))
        for i, d in enumerate(dets):
            img1 = Image.open(path)
            img1 = img1.crop((d.left(), d.top(), d.right(), d.bottom()))
            img1.save(path)
    def predict(self,img):
        #cutted_img = self.cutting_image(path) img = Image.open(path)
        timg = self.transform(img).unsqueeze(0)
        #print(timg.unsqueeze(0).shape)
        pred = torch.softmax(self.model(timg),dim=1)
        return pred.detach().numpy()
