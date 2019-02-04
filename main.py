# -*- coding: utf-8 -*-


from PyQt5 import QtCore, QtGui, QtWidgets
import sys
import cv2
from PyQt5.QtCore import QThread
from PyQt5.QtGui import QPixmap, QImage, QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton, QComboBox
from PyQt5 import QtWidgets
import numpy as np
from images_information import data
from glasses import glasses_filter
from hat import hat_paste
import datetime

casc_class = 'haarcascade_frontalface_default.xml'
face_cascade = cv2.CascadeClassifier(casc_class)
eye_casc = 'haarcascade_eye.xml'
eye_cascade = cv2.CascadeClassifier(eye_casc)


class VideoThread(QThread):
    current_pixmap = None


    def __init__(self, label, parent=None):
        QThread.__init__(self, parent=parent)
        self.label = label

    def run(self):
        video = cv2.VideoCapture(0)
        while True:
            ret, frame = video.read()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.equalizeHist(gray)
            frame = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
#Facial rec stuff
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)

            if MainWindow.selected_glasses or MainWindow.selected_hat:
                for (x,y,w,h) in faces:
                    roi_gray = gray[y:y+h, x:x+w]
                    roi_color = frame[y:y+h, x:x+w]

                    if MainWindow.selected_glasses:
                        eyes = eye_cascade.detectMultiScale(roi_gray, 1.3, 5)
                        # for (ex,ey,ew,eh) in eyes:
                            # cv2.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh),(0,255,0),2)
                        glasses_filter(frame, (x, y, w), eyes, MainWindow.selected_glasses)
                if MainWindow.selected_hat:
                    hat_paste(frame, faces, MainWindow.selected_hat)

#Using frame data so it'll read into the GUI rather than just a seperate image
            image = QImage(frame.data, gray.shape[1], gray.shape[0], QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(image)
            VideoThread.current_pixmap = pixmap
            p = pixmap.scaled(640,450, QtCore.Qt.KeepAspectRatio)
            self.label.setPixmap(p)

class MainWindow(QWidget):
    selected_hat = None
    selected_glasses = None

    def __init__(self):
        super().__init__()
        self.setObjectName("Project")
        self.setFixedSize(950, 500)
        self.hatArea = QtWidgets.QScrollArea(self)
        self.hatArea.move(650, 30)
        self.hatArea.resize(250, 200)
        self.hatArea.setWidgetResizable(True)
        self.hatArea.setObjectName("hatArea")
        self.hatAreaWidgetContents = QtWidgets.QWidget(self.hatArea)
        self.hatArea.setWidget(self.hatAreaWidgetContents)
        self.hatLayout = QGridLayout(self.hatAreaWidgetContents)
        self.hatAreaWidgetContents.setLayout(self.hatLayout)
        self.hatAreaWidgetContents.setMinimumSize(198, len(data['hats']) * 20)

        self.video = QtWidgets.QLabel(self)
        self.video.setEnabled(True)
        self.video.move(10, 20)
        self.video.resize(640,450)
        self.video.setObjectName("video")

        self.glassesArea = QtWidgets.QScrollArea(self)
        self.glassesArea.move(650, 250)
        self.glassesArea.resize(250, 200)
        self.glassesArea.setWidgetResizable(True)
        self.glassesArea.setObjectName("glassesArea")
        self.glassesAreaWidgetContents = QtWidgets.QWidget(self.glassesArea)
        self.glassesArea.setWidget(self.glassesAreaWidgetContents)
        self.glassesLayout = QGridLayout(self.glassesAreaWidgetContents)
        self.glassesAreaWidgetContents.setLayout(self.glassesLayout)
        self.glassesAreaWidgetContents.setMinimumSize(198, len(data['glasses']) * 20)

        buttonHat = QtWidgets.QPushButton(self.glassesAreaWidgetContents)
        self.hatLayout.addWidget(buttonHat, 0, 0)
        buttonHat.clicked.connect(lambda state, x=None: self.defineHat(None))

        for i, hat in enumerate(data['hats']):
            i += 1
            hat['img'] = cv2.imread(f'images/hats/{hat["id"]}.png', cv2.IMREAD_UNCHANGED)
            icon = QIcon(f'images/hats/{hat["id"]}.png')
            button = QtWidgets.QPushButton(self.hatAreaWidgetContents)
            self.hatLayout.addWidget(button, i // 2, i % 2)
            button.clicked.connect(lambda state, x=hat: self.defineHat(x))
            button.setIcon(icon)

        buttonGlasses = QtWidgets.QPushButton(self.glassesAreaWidgetContents)
        self.glassesLayout.addWidget(buttonGlasses, 0, 0)
        buttonGlasses.clicked.connect(lambda state, x=None: self.defineGlasses(x))

        for i, glasses in enumerate(data['glasses']):
            i += 1
            glasses['img'] = cv2.imread(f'images/glasses/{glasses["id"]}.png', cv2.IMREAD_UNCHANGED)
            icon = QIcon(f'images/glasses/{glasses["id"]}.png')
            button = QtWidgets.QPushButton(self.glassesAreaWidgetContents)
            self.glassesLayout.addWidget(button, i // 2, i % 2)
            button.clicked.connect(lambda state, x=glasses: self.defineGlasses(x))
            button.setIcon(icon)

        iconCam = QIcon('images/camera-icon.png')
        self.savebutton = QPushButton(self)
        self.savebutton.clicked.connect(self.on_click)
        self.savebutton.setIcon(iconCam)
        self.savebutton.move(655, 455)


        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)
        th = VideoThread(self.video, self)
        th.start()

    def on_click(self):
        now = datetime.datetime.now()
        pixmap = VideoThread.current_pixmap
        if pixmap:
            pixmap.save(f"Screenshots/{now.strftime('%Y-%m-%d_%H-%M-%S')}.jpg")

    def defineGlasses(self, glasses):
        MainWindow.selected_glasses = glasses

    def defineHat(self, hat):
        MainWindow.selected_hat = hat

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Project", "Glasses and Hats simulator"))



if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ui = MainWindow()
    ui.show()
    sys.exit(app.exec_())
