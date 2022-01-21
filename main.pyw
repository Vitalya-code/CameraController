import math
import os
import sys
import threading
import time

import PyQt5
import pyvirtualcam
import qdarkstyle

from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon, QCursor
from PyQt5.QtWidgets import QWidget, QApplication, QGridLayout, QHBoxLayout, QScrollArea, QPushButton, QLabel, \
    QFileDialog, QCheckBox, QSlider, QLineEdit, QMenu

import cv2
import configparser
import shutil


folderDest = ""
iconsizeX = 350
iconsizeY = 200
isSliderConnected = True

appStyle="""
QMainWindow{
background-color: darkgray;
}
"""

# init in system
try:
    maindir = os.environ.get('temp') + "\img"
    os.mkdir(os.environ.get('temp') + "\img")
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
        self.stopVideo()
        self.checkBox.setChecked(False)
        time.sleep(0.5)

    def resizeEvent(self, event):
        #oldwidth = event.oldSize().width()
        #self.oldmaxInField = (math.floor(oldwidth / iconsizeX))

        width = self.scrollArea.frameGeometry().width()
        self.maxInField = (math.floor(width / iconsizeX))


        if self.maxInField != self.oldmaxInField and self.maxInField != 0:
           try:
               self.gui_restart(self.mainFiles)
           except:
               pass


    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        for f in files:
            print(self.folderDest + "/" + os.path.basename(f))

            shutil.copyfile(f, self.folderDest + "/" + os.path.basename(f))
        self.onbrowseBtn(self.folderDest)
        self.gui_restart(self.mainFiles)

    def sldReconnect(self):
        self.isSliderConnected = True
        self.stopVideo(0.1)
        currentFrame = math.ceil(self.sender().value() / 100 * self.frameCount)
        self.startVideo(self.config.get("settings", "oldfile"), currentFrame)

    def sldDisconnect(self):
        self.isSliderConnected = False

    def searchEvent(self, text):
        self.searchFiles = []
        for i in self.mainFiles:
            if i.lower().find(text.lower()) != -1:
                self.searchFiles.append(i)

        self.gui_restart(self.searchFiles)




    def onbrowseBtn(self, folder=None):

        if folder:
            self.folderDest = folder
        else:
            self.folderDest = QFileDialog.getExistingDirectory()

        self.config = configparser.ConfigParser()
        self.config['settings'] = {}
        self.config['settings']['old_path_to_folder'] = self.folderDest
        with open('config.ini', 'w') as configfile:
            self.config.write(configfile)

        if self.folderDest != "":
            self.label.setText(self.folderDest)
            self.readfiles = os.listdir(self.folderDest)
            self.mainFiles = []
            for i in self.readfiles:
                filename, file_extension = os.path.splitext(i)
                if file_extension == ".mp4":
                    self.mainFiles.append(i)

            for i in self.mainFiles:
                filename, file_extension = os.path.splitext(i)
                vidcap = cv2.VideoCapture(str(self.folderDest) + "/" + str(i))
                success, image = vidcap.read()
                success, im_buf_arr = cv2.imencode(".jpg", image)
                if success:
                    im_buf_arr.tofile(maindir + filename + ".jpg")

            self.gui_restart(self.mainFiles)

    def gui_restart(self, mainFiles):
        for i in reversed(range(self.lay.count())):
            self.lay.itemAt(i).widget().setParent(None)

        count = 0

        self.buttons = []

        for i in mainFiles:
            filename = os.path.splitext(i)[0]
            button = QPushButton()



            button.setToolTip(filename + ".mp4")

            button.clicked.connect(lambda ch, buttonCount=count: self.onSelect(buttonCount))
            button.setIcon(QIcon(maindir + filename + ".jpg"))
            button.setIconSize(QSize(iconsizeX, iconsizeY))
            button.setMinimumSize(iconsizeX, iconsizeY)
            button.setMaximumSize(iconsizeX, iconsizeY)


            width = self.scrollArea.frameGeometry().width()
            self.maxInField = (math.floor(width / iconsizeX))

            self.oldmaxInField = self.maxInField


            out = count / self.maxInField
            out = (math.floor(out))
            self.lay.addWidget(button, out, count - out * self.maxInField)



            count = count + 1
            self.buttons.append(button)

    def onSelect(self, buttonCount):
        #butObj = self.buttons[buttonCount]
        #print(self.mainFiles[buttonCount])
        if self.searchFiles != []:
            self.startVideo(self.folderDest + "/" + self.searchFiles[buttonCount])
            self.statusbar.setText(self.searchFiles[buttonCount])
        else:
            self.startVideo(self.folderDest + "/" + self.mainFiles[buttonCount])
            self.statusbar.setText(self.mainFiles[buttonCount])

    def startVideo(self, filename, currentFrame=0):
        self.stopVideo(0.1)
        x = threading.Thread(target=self.mainThread, args=(filename, currentFrame))
        x.start()

    def stopVideo(self, delay=0.5):
        try:
            self.run = False
            time.sleep(delay)
            self.run = True
        except:
            pass

    def mainThread(self, filename, currentFrame):
        cap = cv2.VideoCapture(filename)
        self.frameCount = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.frameWidth = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frameHeight = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.frameFPS = int(cap.get(cv2.CAP_PROP_FPS))

        self.config.set("settings", "oldfile", filename)
        with open('config.ini', 'w') as configfile:
            self.config.write(configfile)

        cam = pyvirtualcam.Camera(self.frameWidth, self.frameHeight, self.frameFPS)
        cap.set(cv2.CAP_PROP_POS_FRAMES, currentFrame)
        while currentFrame < self.frameCount and self.run == True:
            self.slider.setHidden(False)

            self.timeCount.setText(
                str(math.ceil(currentFrame / self.frameFPS)) + "/" + str(
                    math.ceil(self.frameCount / self.frameFPS)) + " sec")
            if isSliderConnected == True:
                self.slider.setValue(math.ceil(currentFrame / self.frameCount * 100))

            _, frame = cap.read()
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            cam.send(frame)
            cam.sleep_until_next_frame()
            currentFrame = currentFrame + 1

        cam.close()
        self.stopVideo(0)
        if self.checkBox.isChecked() and currentFrame == self.frameCount:
            # stopVideo(0.5)
            # startVideo(config.get("settings", "oldfile"), 0)
            self.startVideo(filename, 0)

    def initUI(self):
        self.setGeometry(800, 500, 800, 500)
        self.setWindowTitle('CameraController')
        self.setStyleSheet(qdarkstyle.load_stylesheet())

        self.resized.connect(self.resizeEvent)
        self.setWindowIcon(QIcon('ico.ico'))
        self.setAcceptDrops(True)

        self.maxInField = 5
        self.oldmaxInField = 5
        self.searchFiles = []

        # Main Layout

        self.layout = QGridLayout()

        # Top Buttons Layout
        self.topLayout = QHBoxLayout()

        # Bot status layout
        self.botLayout = QHBoxLayout()

        # Status bar

        self.statusbar = QLabel()
        self.statusbar.setDisabled(True)
        self.botLayout.addWidget(self.statusbar)

        # BrowseButton
        self.browseBtn = QPushButton("Browse")
        self.browseBtn.setFixedSize(60, 20)
        self.browseBtn.clicked.connect(self.onbrowseBtn)
        # self.browseBtn.clicked.connect(lambda checked: self._on_clicked_cell(button, i, j)

        # Search input

        searchInput = QLineEdit()
        searchInput.setPlaceholderText("Search")
        searchInput.textChanged.connect(self.searchEvent)


        self.label = QLabel("Please choose your folder with videos")

        # CheckBox

        self.checkBox = QCheckBox("Repeat video")

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setHidden(True)
        # slider.valueChanged.connect(self.sliderChanged)
        self.slider.sliderPressed.connect(self.sldDisconnect)
        self.slider.sliderReleased.connect(self.sldReconnect)

        self.timeCount = QLabel()

        # scroll area

        self.scrollArea = QScrollArea()
        self.scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        content_widget = QWidget()
        self.scrollArea.setWidget(content_widget)
        self.scrollArea.setWidgetResizable(True)

        self.lay = QGridLayout(content_widget)
        self.lay.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)

        # add widgets
        self.topLayout.addWidget(self.browseBtn)
        self.topLayout.addWidget(self.label)
        self.topLayout.addWidget(self.checkBox, Qt.AlignLeft)
        # topLayout.addWidget(searchLabel,Qt.AlignRight)

        self.topLayout.addWidget(searchInput, Qt.AlignRight)

        self.botLayout.addWidget(self.timeCount)
        self.botLayout.addWidget(self.slider)
        self.layout.addLayout(self.topLayout, 2, 0)
        self.layout.addWidget(self.scrollArea, 4, 0)
        self.layout.addLayout(self.botLayout, 6, 0)

        self.setLayout(self.layout)

        self.config = configparser.ConfigParser()
        self.config.read('config.ini')

        try:
            self.onbrowseBtn(folder=self.config['settings']["old_path_to_folder"])
        except:
            pass

        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Main()
    sys.exit(app.exec_())
