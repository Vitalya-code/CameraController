import math
import os
import sys
import threading
import time
import pyvirtualcam
import qdarkstyle
from PyQt5 import QtCore
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QApplication, QGridLayout, QHBoxLayout, QScrollArea, QPushButton,QLabel, QFileDialog
import cv2

mainFiles = []
folderDest = ""
iconsizeX = 350
iconsizeY = 200
maxInFieald = 5
oldmaxInFieald = 5

try:
    os.mkdir("img")
    osName = os.uname()
    if str(osName[0]) == "Linux":
        os.system("sudo modprobe -r v4l2loopback")
        os.system("sudo modprobe v4l2loopback")
except:
    pass


class Main(QWidget):
    resized = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.initUI()

    def closeEvent(self, event):
        global run
        run = False
        time.sleep(0.1)
        #event.ignore()


    def resizeEvent(self, event):
        width = scrollArea.frameGeometry().width()
        global maxInFieald
        maxInFieald = (math.floor(width / iconsizeX))

        if maxInFieald != oldmaxInFieald and maxInFieald != 0:
            gui_restart()

    def initUI(self):
        self.setGeometry(1000, 500, 1000, 500)
        self.setWindowTitle('CameraController')
        self.setStyleSheet(qdarkstyle.load_stylesheet())
        self.resized.connect(self.resizeEvent)

        #Main Layout
        global layout
        layout = QGridLayout()
        #Top Buttons Layout
        layoutButtons = QHBoxLayout()
        browseBtn = QPushButton("Browse")
        browseBtn.setFixedSize(60,20)
        browseBtn.clicked.connect(onbrowseBtn)
        global label
        label = QLabel("Please choose your folder with videos")

        layoutButtons.addWidget(browseBtn)
        layoutButtons.addWidget(label)
        layout.addLayout(layoutButtons,2,0)

        #scroll area
        global scrollArea
        scrollArea = QScrollArea()
        scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        content_widget = QWidget()
        scrollArea.setWidget(content_widget)
        scrollArea.setWidgetResizable(True)
        global lay
        lay = QGridLayout(content_widget)
        lay.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)

        gui_restart()


        layout.addWidget(scrollArea,4,0)
        self.setLayout(layout)
        self.show()




def onbrowseBtn():
    global folderDest
    folderDest = QFileDialog.getExistingDirectory()
    if folderDest != "":
        label.setText(folderDest)
        readfiles = os.listdir(folderDest)
        for i in readfiles:
            filename, file_extension = os.path.splitext(i)
            if file_extension == ".mp4":
                mainFiles.append(i)

        for i in mainFiles:
            filename, file_extension = os.path.splitext(i)
            vidcap = cv2.VideoCapture(str(folderDest) + "/" + str(i))
            success, image = vidcap.read()
            cv2.imwrite("img/" + filename + ".jpg", image)
            gui_restart()

def gui_restart():
    for i in reversed(range(lay.count())):
        lay.itemAt(i).widget().setParent(None)

    count = 0
    global buttons
    buttons = []
    for i in mainFiles:
        filename = os.path.splitext(i)[0]
        button = QPushButton()
        button.clicked.connect(lambda ch, text=count: onSelect(text))
        button.setIcon(QIcon("img/" + filename + ".jpg"))
        button.setIconSize(QSize(iconsizeX, iconsizeY))
        button.setMinimumSize(iconsizeX, iconsizeY)
        button.setMaximumSize(iconsizeX, iconsizeY)
        global oldmaxInFieald
        oldmaxInFieald = maxInFieald
        out = count / maxInFieald
        out = (math.floor(out))
        lay.addWidget(button, out, count - out * maxInFieald)
        count = count + 1
        buttons.append(button)


def onSelect(text):
    global but
    global status
    status = text
    but = buttons[text]


    StartVideo(folderDest+"/"+mainFiles[text])


    for i in buttons:
        i.setDisabled(False)
    but.setDisabled(True)


def StartVideo(filename):
    global run
    run = False
    time.sleep(0.1)
    run = True
    x = threading.Thread(target=mainThread, args=(filename,))
    x.start()



def mainThread(filename):

    cap = cv2.VideoCapture(filename)
    frameCount = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frameWidth = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frameHeight = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frameFPS = int(cap.get(cv2.CAP_PROP_FPS))

   # cam = pyvirtualcam.Camera(width=frameWidth, height=frameHeight, fps=frameFPS)
    cam = pyvirtualcam.Camera(frameWidth, frameHeight, frameFPS)

    i = 0
    while i < frameCount and run == True:
        _, frame = cap.read()
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        cam.send(frame)
        cam.sleep_until_next_frame()
        i =+ 1




if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Main()
    sys.exit(app.exec_())
