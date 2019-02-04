# -*- coding: utf-8 -*-

import cv2
import numpy as np
import sys
from utils import img_paste
import random
from images_information import data
from operator import itemgetter


def glasses_filter(color, face, eyes, glasses):

    height, width, _ = glasses['img'].shape
    eyes = getCorrectEyes(eyes, face[2])
    if not eyes:
        return

    if eyes[0][0] <= eyes[1][0]:
        x1, y1, w1, h1 = eyes[0]
        x2, y2, w2, h2 = eyes[1]
    else:
        x1, y1, w1, h1 = eyes[1]
        x2, y2, w2, h2 = eyes[0]
    eye_width = w2 + (x2 - x1)
    glasses_width = glasses['width'] * eye_width
    new_height = (height/width) * glasses_width
    new_x = face[0] + x1 - (glasses['width'] - 1) / 2 * eye_width
    new_y = face[1] + y1 - glasses['height_shift'] * new_height


    resize = cv2.resize(glasses['img'], (int(glasses_width), int(new_height)))
    img_paste(resize, color, int(new_x), int(new_y))

def getCorrectEyes(eyes, width):

    if len(eyes) < 2:
        return None

    eyes = sorted(eyes, key=itemgetter(1))
    minDiffX = width // 4

    bestPair = eyes[0], eyes[1]
    bestDiff = abs(eyes[0][1] - eyes[0][1])

    for i in range(1, len(eyes) - 1):
        eye1 = eyes[i]
        for j in range(i + 1, len(eyes)):
            eye2 = eyes[j]
            diff = abs(eye1[1] - eye2[1])
            diffX = abs(eye1[0] - eye2[0])
            if diffX >= minDiffX and diff < bestDiff:
                bestDiff = diff
                bestPair = eye1, eye2
    if abs(bestPair[0][0] - bestPair[1][0]) < minDiffX:
        return None
    return bestPair

def main():

    #load classifier to detect faces
    casc_class = ('haarcascade_frontalface_default.xml')
    face_cascade = cv2.CascadeClassifier(casc_class)

    #check to see the classifier loads properly
    if face_cascade.empty():
        print('WARNING: face cascade did not load')

    #load classifier to detect eyes
    casc_class2 = 'haarcascade_eye.xml'
    eye_cascade = cv2.CascadeClassifier(casc_class2)

    #capture video from the front camera
    my_video = cv2.VideoCapture(0)
    glasses = random.choice(data['glasses'])

    if 'img' not in glasses:
        glasses['img'] = cv2.imread(f'images/glasses/{glasses["id"]}.png', cv2.IMREAD_UNCHANGED)

    while True:
        ret, frame = my_video.read(1)

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = face_cascade.detectMultiScale(frame, 1.3, 5)
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            roi_gray = gray[y:y+h, x:x+w]
            roi_color = frame[y:y+h, x:x+w]

            eyes = eye_cascade.detectMultiScale(roi_gray)
            glasses_filter(frame, (x, y, w), eyes, glasses)
            for (ex, ey, ew, eh) in eyes:
                cv2.rectangle(roi_color, (ex,ey), (ex+ew, ey+eh), (0, 255, 0), 2)


        cv2.imshow('glasses', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    my_video.release()
    cv2.destroyAllWindows()
if __name__ == '__main__':
    main()
