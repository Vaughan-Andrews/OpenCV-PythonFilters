# -*- coding: utf-8 -*-

import numpy as np
import cv2
from images_information import data
import random
from utils import img_paste


def hat_paste(color, faces, hat):
 
    height, width, _  = hat['img'].shape
    for (x,y,w,h) in faces:
        x -= w * (hat['width'] - 1) / 2
        w *= hat['width']

        height *= w / width
        y -= height * hat['height_shift']
        width = w

        img_paste(cv2.resize(hat['img'], (int(width), int(height))), color, int(x), int(y))


def main():

    casc_class = 'haarcascade_frontalface_default.xml'
    face_cascade = cv2.CascadeClassifier(casc_class)

    if face_cascade.empty():
        print('WARNING: Cascade did not load')
    my_video = cv2.VideoCapture(0)
    
    hat = data['hats'][14]
    if 'img' not in hat:
        hat['img'] = cv2.imread(f'images/hats/{hat["id"]}.png', cv2.IMREAD_UNCHANGED) 


    while True:
        ret, frame = my_video.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = face_cascade.detectMultiScale(frame, 1.3, 5)

        for (x,y,w,h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

        hat_paste(frame, faces, hat)

        cv2.imshow("hats", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    my_video.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()