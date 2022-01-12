import math
import os
import sys
import threading
import time
import pyvirtualcam
import qdarkstyle
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QApplication, QGridLayout, QHBoxLayout, QScrollArea, QPushButton, QLabel, \
    QFileDialog, QCheckBox, QSlider
import cv2
import configparser


folderDest = ""
iconsizeX = 350
iconsizeY = 200
maxInFieald = 5
oldmaxInFieald = 5
isSliderConnected = True

#init in system
try:
    #global maindir
    maindir = os.environ.get('temp')+"\img"
    os.mkdir(os.environ.get('temp')+"\img")

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
        stopVideo()
        checkBox.setChecked(False)
        time.sleep(0.5)

    def resizeEvent(self, event):
        width = scrollArea.frameGeometry().width()
        global maxInFieald
        maxInFieald = (math.floor(width / iconsizeX))
        if maxInFieald != oldmaxInFieald and maxInFieald != 0:
            try:
                gui_restart(mainFiles)
            except:
                pass


    def sldReconnect(self):
        global isSliderConnected
        isSliderConnected = True
        stopVideo(0.5)
        currentFrame = math.ceil(self.sender().value() / 100 * frameCount)
        startVideo(config.get("settings", "oldfile"), currentFrame)




    def sldDisconnect(self):
        global isSliderConnected
        isSliderConnected = False




    def initUI(self):
        self.setGeometry(800, 500, 800, 500)
        self.setWindowTitle('CameraController')
        self.setStyleSheet(qdarkstyle.load_stylesheet())
        self.resized.connect(self.resizeEvent)
        self.setWindowIcon(QIcon('ico.ico'))

        # Main Layout
        global layout
        layout = QGridLayout()

        # Top Buttons Layout
        topLayout = QHBoxLayout()

        # Bot status layout
        botLayout = QHBoxLayout()

        # Status bar

        global statusbar
        statusbar = QLabel()
        statusbar.setDisabled(True)
        botLayout.addWidget(statusbar)




        #BrowseButton
        browseBtn = QPushButton("Browse")
        browseBtn.setFixedSize(60, 20)
        browseBtn.clicked.connect(onbrowseBtn)

        #label
        global label
        label = QLabel("Please choose your folder with videos")

        #CheckBox
        global checkBox
        checkBox = QCheckBox("Repeat video")


        global slider
        slider = QSlider(Qt.Horizontal)
        slider.setHidden(True)
        #slider.valueChanged.connect(self.sliderChanged)
        slider.sliderPressed.connect(self.sldDisconnect)
        slider.sliderReleased.connect(self.sldReconnect)


        global timeCount
        timeCount = QLabel()


        # scroll area
        global scrollArea
        scrollArea = QScrollArea()
        scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        content_widget = QWidget()
        scrollArea.setWidget(content_widget)
        scrollArea.setWidgetResizable(True)
        global lay
        lay = QGridLayout(content_widget)
        lay.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)


        #add widgets
        topLayout.addWidget(browseBtn)
        topLayout.addWidget(label)
        topLayout.addWidget(checkBox,Qt.AlignLeft)
        botLayout.addWidget(timeCount)
        botLayout.addWidget(slider)
        layout.addLayout(topLayout, 2, 0)
        layout.addWidget(scrollArea, 4, 0)
        layout.addLayout(botLayout, 6, 0)



        self.setLayout(layout)

        global config
        config = configparser.ConfigParser()
        config.read('config.ini')
        try:
            onbrowseBtn(folder=config['settings']["old_path_to_folder"])
        except:
            pass


        self.show()






def onbrowseBtn(folder=None):
    global folderDest
    if folder != False:
        folderDest = folder
    else:
        folderDest = QFileDialog.getExistingDirectory()

    config = configparser.ConfigParser()
    config['settings'] = {}
    config['settings']['old_path_to_folder'] = folderDest
    with open('config.ini', 'w') as configfile:
        config.write(configfile)

    if folderDest != "":
        label.setText(folderDest)
        readfiles = os.listdir(folderDest)

        global mainFiles
        mainFiles = []
        for i in readfiles:
            filename, file_extension = os.path.splitext(i)
            if file_extension == ".mp4":
                mainFiles.append(i)

        for i in mainFiles:
            filename, file_extension = os.path.splitext(i)
            vidcap = cv2.VideoCapture(str(folderDest) + "/" + str(i))
            success, image = vidcap.read()
            success, im_buf_arr = cv2.imencode(".jpg", image)
            if success:
                im_buf_arr.tofile(maindir + filename + ".jpg")

        gui_restart(mainFiles)


def gui_restart(mainFiles):
    for i in reversed(range(lay.count())):
        lay.itemAt(i).widget().setParent(None)

    count = 0
    global buttons
    buttons = []

    for i in mainFiles:
        filename = os.path.splitext(i)[0]
        button = QPushButton()
        label = QLabel()
        button.setToolTip(filename + ".mp4")
        button.clicked.connect(lambda ch, buttonCount=count: onSelect(buttonCount))
        button.setIcon(QIcon(maindir + filename + ".jpg"))
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



def onSelect(buttonCount):
    global butObj
    butObj = buttons[buttonCount]
    startVideo(folderDest + "/" + mainFiles[buttonCount])


    statusbar.setText(mainFiles[buttonCount])


def startVideo(filename, currentFrame = 0):
    stopVideo(1)
    x = threading.Thread(target=mainThread, args=(filename, currentFrame))
    x.start()



def stopVideo(delay = 0.5):
    try:
        global run
        run = False
        time.sleep(delay)
        run = True
        cam.close()
    except:
        pass



def mainThread(filename, currentFrame):
    global frameCount
    global cam

    cap = cv2.VideoCapture(filename)
    frameCount = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frameWidth = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frameHeight = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frameFPS = int(cap.get(cv2.CAP_PROP_FPS))


    config.set("settings", "oldfile", filename)
    with open('config.ini', 'w') as configfile:
        config.write(configfile)


    cam = pyvirtualcam.Camera(frameWidth, frameHeight, frameFPS)



    cap.set(cv2.CAP_PROP_POS_FRAMES, currentFrame)
    while currentFrame < frameCount and run == True:
        slider.setHidden(False)

        timeCount.setText(str(math.ceil(currentFrame/frameFPS))+"/"+str(math.ceil(frameCount/frameFPS))+" sec")
        if isSliderConnected == True:
            slider.setValue(math.ceil(currentFrame/frameCount*100))

        _, frame = cap.read()
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        cam.send(frame)
        cam.sleep_until_next_frame()
        currentFrame = currentFrame + 1


    stopVideo()
    if checkBox.isChecked():
        #stopVideo(0.5)
        startVideo(config.get("settings", "oldfile"), 0)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Main()
    sys.exit(app.exec_())







