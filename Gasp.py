import PyQt5.Qt
import cv2
import win32gui
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtGui import QImage, QIcon
from subprocess import Popen, PIPE
from program.GaspUi import Ui_MainWindow
import os
import constant
from numpy import array
from utils.HandleUtils import HandleUtils
from utils.ImageUtils import ImageUtils
from utils.ScreenCaptureUtils import ScreenCaptureUtils
from win32gui import SetForegroundWindow, GetWindowRect
import win32com
from PIL import ImageGrab
import numpy as np

constant.WINDOWSMODE = 0
constant.ABSMODE = 1





def cvToQImage(data):
    # 8-bits unsigned, NO. OF CHANNELS=1
    if data.dtype == np.uint8:
        channels = 1 if len(data.shape) == 2 else data.shape[2]
    if channels == 3: # CV_8UC3
        # Copy input Mat
        # Create QImage with same dimensions as input Mat
        img = QImage(data, data.shape[1], data.shape[0], data.strides[0], QImage.Format_RGB888)
        return img.rgbSwapped()
    elif channels == 1:
        # Copy input Mat
        # Create QImage with same dimensions as input Mat
        img = QImage(data, data.shape[1], data.shape[0], data.strides[0], QImage.Format_Indexed8)
        return img
    else:
        # qDebug("ERROR: numpy.ndarray could not be converted to QImage. Channels = %d" % data.shape[2])
        return QImage()

class Gasp(Ui_MainWindow):

    def __init__(self, parent=None):
        Ui_MainWindow.__init__(self)
        self.curProcess = None
        self.curMode = constant.WINDOWSMODE
        self.deviceIds = None
        self.selectedDeviceIndex = 0
        self.windowHandler = None
        self.windowWidth = 0
        self.windowHeight = 0
        self.phoneWidth = 0
        self.phoneHeight = 0

        self.resizeCaptureRectangle = None

        self.scene = QtWidgets.QGraphicsScene()
        self.files = []
        self.openShortcut = None
        self.saveEnterShortcut = None
        self.saveShortcut = None
        self.skipShortcut = None
        self.last_rect = None
        self.last_rotation = 0


    def built(self, MainWindow):
        # self.openShortcut = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+O"), self.centralwidget)
        # self.saveShortcut = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+S"), self.centralwidget)
        # self.saveEnterShortcut = QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Space), self.centralwidget)
        # self.skipShortcut = QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Tab), self.centralwidget)

        MainWindow.setWindowTitle("Generate Process For Pyauto-Script")
        MainWindow.setWindowIcon(QIcon("./image/favorite.png"))

        self.graphicsView.setScene(self.scene)
        self.scene.setBackgroundBrush(QtCore.Qt.white)
        self.graphicsView.setPositionInput = self.setPositionInput

        self.openProcess.triggered.connect(self.select_dir) # 打开process按钮
        self.choose_phone.setDisabled(True) # 选择windows窗口
        self.mode.currentIndexChanged.connect(self.chooseMode) # 模式选择事件
        self.choose_phone.currentIndexChanged.connect(self.selectDevice) # 选择abs设备
        self.choose_window.clicked.connect(self.selectWindow) # 选择窗口
        self.screentshot.setDisabled(True)
        self.save_template.setDisabled(True)
        self.workingDir.setDisabled(True)
        # self.width.setDisabled(True)
        # self.height.setDisabled(True)
        self.screentshot.clicked.connect(self.catchScreen)

        self.save_template.clicked.connect(self.saveTemplate) # 保存

        self.pos_x.setDisabled(True)
        self.pos_y.setDisabled(True)
        self.randomRightOffset.setDisabled(True)
        self.randomBottomOffset.setDisabled(True)

        selectRectangleRadioGroup = PyQt5.Qt.QButtonGroup(MainWindow)
        selectRectangleRadioGroup.addButton(self.selectCaptreArea, 0)
        selectRectangleRadioGroup.addButton(self.selectClickArea, 1)
        self.selectCaptreArea.setChecked(1)
        self.selectCaptreArea.toggled.connect(self.toggleSelectArea)
        # self.selectFile.
        # self.openButton.clicked.connect(self.select_files)
        # self.rotateCwButton.clicked.connect(lambda: self.graphicsView.rotate_pixmap(45))
        # self.rotateCcwButton.clicked.connect(lambda: self.graphicsView.rotate_pixmap(-45))
        # self.saveButton.clicked.connect(self.save_image)
        # self.skipButton.clicked.connect(self.skip_image)
        # self.openShortcut.activated.connect(self.select_files)
        # self.saveShortcut.activated.connect(self.save_image)
        # self.skipShortcut.activated.connect(self.skip_image)
        # self.saveEnterShortcut.activated.connect(self.save_image)
        self.graphicsView.dropHandler = self.drop_handler
        self.graphicsView.setFocus()

    def toggleSelectArea(self, e):
        self.graphicsView.currentMode = 0 if e else 1

    def closing(self):
        pass

    def select_dir(self):
        curProcess = QtWidgets.QFileDialog.getExistingDirectory(None, "Select Directory")
        if curProcess is None or curProcess == "": return
        self.curProcess = curProcess
        print(f"【debug】 select process path: {self.curProcess}")
        self.workingDir.setTitle(self.curProcess)

    def chooseMode(self, e):
        self.curMode = e
        self.choose_phone.setDisabled(self.curMode == constant.WINDOWSMODE)
        self.choose_window.setDisabled(self.curMode == constant.ABSMODE)
        if self.curMode == constant.ABSMODE:
            self.width.setDisabled(True)
            self.height.setDisabled(True)
            status, deviceIds = HandleUtils.adb_device_status()
            self.choose_phone.clear()
            self.deviceIds = deviceIds
            if not status:
                self.choose_phone.addItem("no device detected!")
                self.runningLog.setText(f'【warning】 没找到任何设备！')
            else:
                self.runningLog.setText(f'【info】 已切换到abs模式，请选择设备。')
                for deviceId in deviceIds:
                    self.choose_phone.addItem(deviceId)
        else:
            self.width.setDisabled(False)
            self.height.setDisabled(False)
            self.choose_phone.clear()
            self.choose_phone.addItem("Choose Phone")
            self.runningLog.setText(f'【info】 已切换到windows模式，点击截图后，选择窗口。')
        # self.save_template.setDisabled(True)
        # self.screentshot.setDisabled(True)

    def selectDevice(self, e):
        self.selectedDeviceIndex = e
        self.screentshot.setDisabled(False)
        self.save_template.setDisabled(False)
        print(f"【debug】 select device index: {self.selectedDeviceIndex}, and deviceId is {self.deviceIds[e] if e >= 0 and e < len(self.deviceIds) else 'None'}")
        if e >= 0 and e < len(self.deviceIds):
            self.runningLog.setText(f'【选中设备】 {self.deviceIds[e]}')

    def selectWindow(self):
        QtWidgets.QMessageBox.information(None, 'Info', f'请在5秒内选择窗口！')
        hand_win_title, hand_num = HandleUtils.get_active_window(5)
        # print(hand_win_title)
        print(f"【debug】 select window title: {hand_win_title}, and handle is {hand_num}")
        # QtWidgets.QMessageBox.information(None, 'Info', f'【选中窗口】 {hand_win_title}')
        self.runningLog.setText(f'【选中窗口】 {hand_win_title}')
        self.windowHandler = hand_num
        self.screentshot.setDisabled(False)
        self.save_template.setDisabled(False)
        self.width.setDisabled(False)
        self.height.setDisabled(False)

        height = int(self.height.text())
        width = int(self.width.text())
        if height <= 0 or width <= 0:
            height = 600
            width = 800
        self.windowWidth = width
        self.windowHeight = height
        win32gui.MoveWindow(self.windowHandler, 0, 0, width, height, True)

    def catchScreen(self):
        # self.graphicsView.removeRect()
        self.graphicsView.removeRectAll()
        screen = None
        # return cv2 image type
        if self.curMode == constant.WINDOWSMODE:
            screen = ScreenCaptureUtils.front_window_screen(self.windowHandler, False, True)
        else:
            screen = ScreenCaptureUtils.adb_screen(self.deviceIds[self.selectedDeviceIndex], False)

        height, width, depth = screen.shape
        if constant.ABSMODE == self.curMode:
            self.phoneWidth = width
            self.phoneHeight = height
        screen = cv2.cvtColor(screen, cv2.COLOR_BGR2RGB)
        screen = cvToQImage(screen)
        self.scene.clear()
        screen = QtGui.QPixmap.fromImage(screen)
        pixmap_item = self.scene.addPixmap(screen)  # type: QtWidgets.QGraphicsPixmapItem
        self.graphicsView.current_pixmap_item[self.graphicsView.currentMode] = pixmap_item
        self.graphicsView.rotate_pixmap(self.last_rotation)
        if self.last_rect is not None:
            self.graphicsView.rect_item[self.graphicsView.currentMode] = self.scene.addRect(self.last_rect)
        rect = screen.rect()  # type: # QtCore.QRect
        rect.setWidth(rect.width() * 2)
        rect.setHeight(rect.height() * 2)
        rect.setLeft(rect.x() - rect.width() / 2)
        rect.setTop(rect.y() - rect.height() / 2)
        self.scene.setSceneRect(QtCore.QRectF(rect))
        self.graphicsView.fitInView(pixmap_item.boundingRect(), QtCore.Qt.KeepAspectRatio)

    def setPositionInput(self, rect):
        res = True
        # 更新input框的x1,y1, x2, y2
        x1, x2, rightOffset, bottomOffset = -1, -1, -1, -1
        if rect is not None:
            x1, x2, rightOffset, bottomOffset = rect.x(), rect.y(), rect.width(), rect.height()
            if self.curMode == constant.WINDOWSMODE and (x1 < 0 or x2 < 0 or x1 + rightOffset > self.windowWidth or x2 + bottomOffset > self.windowHeight): res = False
            if self.curMode == constant.ABSMODE and (x1 < 0 or x2 < 0 or x1 + rightOffset > self.phoneWidth or x2 + bottomOffset > self.phoneHeight): res = False
        if not res:
            x1, x2, rightOffset, bottomOffset = -1, -1, -1, -1
        if self.graphicsView.currentMode == 1:
            self.pos_x.setText(str(round(x1)))
            self.pos_y.setText(str(round(x2)))
            self.randomRightOffset.setText(str(round(rightOffset)))
            self.randomBottomOffset.setText(str(round(bottomOffset)))
        else:
            self.resizeCaptureRectangle = rect
        return res and rect is not None

    def toInt(self, text):
        res = -1
        try:
            res = int(text)
        except ValueError:
            pass
        if res < 0:
            QtWidgets.QMessageBox.information(None, 'warning', f'{text} 输入不合法！')
            return -1
        return res

    def saveTemplate(self):
        if self.curProcess is None: self.select_dir()
        # 获取数据
        delayTime = self.toInt(self.delayTime.text())
        if delayTime < 0: return
        randomDelayTime = self.toInt(self.randomDelayTime.text())
        if randomDelayTime < 0: return
        pos_x = int(self.pos_x.text())
        pos_y = int(self.pos_y.text())
        randomRightOffset = int(self.randomRightOffset.text())
        randomBottomOffset = int(self.randomBottomOffset.text())
        delayUpTime = self.toInt(self.delayUpTime.text())
        if delayUpTime < 0: return
        delayRandomUpTime = self.toInt(self.delayRandomUpTime.text())
        if delayRandomUpTime < 0: return
        randomOffsetWhenUp = self.toInt(self.randomOffsetWhenUp.text())
        if randomOffsetWhenUp < 0: return
        loopLeastCount = self.toInt(self.loopLeastCount.text())
        if loopLeastCount < 0: return
        loopRandomCount = self.toInt(self.loopRandomCount.text())
        if loopRandomCount < 0: return
        loopDelayLeastTime = self.toInt(self.loopDelayLeastTime.text())
        if loopDelayLeastTime < 0: return
        loopDelayRandomTime = self.toInt(self.loopDelayRandomTime.text())
        if loopDelayRandomTime < 0: return
        endDelayLeastTime = self.toInt(self.endDelayLeastTime.text())
        if endDelayLeastTime < 0: return
        endDelayRandomTime = self.toInt(self.endDelayRandomTime.text())
        if endDelayRandomTime < 0: return
        threshold = self.toInt(self.threshold.text())
        if threshold < 0: return
        useMatchingPosition = self.toInt(self.useMatchingPosition.text())
        if useMatchingPosition > 2 or useMatchingPosition < 1:
            QtWidgets.QMessageBox.information(None, 'warning', f'#17 应该输入1或2！')
            return
        matchEvent = self.matchEvent.text().strip().replace(" ", "")
        finishEvent = self.finishEvent.text().strip().replace(" ", "")
        if pos_x == -1 or pos_y == -1 or randomRightOffset == -1 or randomBottomOffset == -1:
            QtWidgets.QMessageBox.information(None, 'warning', f'请截图，再选择区域！')
            self.runningLog.setText("【warning】请截图，再选择区域！")
            return
        process = f"{delayTime}_{randomDelayTime}_{pos_x}x{pos_y}_{randomRightOffset}_{randomBottomOffset}_{delayUpTime}_{delayRandomUpTime}_{randomOffsetWhenUp}_{loopLeastCount}_{loopRandomCount}_{loopDelayLeastTime}_{loopDelayRandomTime}_{endDelayLeastTime}_{endDelayRandomTime}_{threshold}_{useMatchingPosition}_{matchEvent}_{finishEvent}.png"
        print(process)

        # 截取图片，保存
        # rect = self.graphicsView.rect_item.boundingRect()  # type
        rect = self.resizeCaptureRectangle
        self.graphicsView.removeRectAll()
        outImg = QtGui.QPixmap(rect.width(), rect.height())
        painter = QtGui.QPainter(outImg)
        self.scene.setSceneRect(rect)
        self.scene.render(painter)
        savePath = os.path.join(self.curProcess, process)
        outImg.save(savePath, "PNG")
        painter.end()

        # 生成事件脚本文件 xxx.py
        matchEPath = os.path.join(self.curProcess, matchEvent + ".py")
        if len(matchEvent) != 0 and matchEvent != "None" and not os.path.exists(matchEPath):
            self.generatePyFile(matchEPath)
        finishEPath = os.path.join(self.curProcess, finishEvent + ".py")
        if len(finishEvent) != 0 and finishEvent != "None" and not os.path.exists(finishEPath):
            self.generatePyFile(finishEPath)

        self.runningLog.setText(f"【success】已保存到: {savePath}")
        QtWidgets.QMessageBox.information(None, 'success', f'【success】已保存到: {savePath}')

    def generatePyFile(self, path):
        with open(path, mode="w", encoding="utf-8") as w:
            w.write("""'''
    Put your code here.
'''
# For Example
# eventAttribute.terminateProcess()
# print("terminate...")""")

    def load_next_image(self):
        self.graphicsView.current_pixmap_item = None
        self.graphicsView.rect_item = None
        if len(self.files) > 0:
            self.load_image(self.files[0])
        else:
            self.scene.clear()
            text_item = self.scene.addText("No images left !")
            self.graphicsView.fitInView(text_item.boundingRect(), QtCore.Qt.KeepAspectRatio)

    # def save_image(self):
    #     if self.graphicsView.rect_item is not None and len(self.files) > 0:
    #         rect = self.graphicsView.rect_item.boundingRect()   # type
    #         self.graphicsView.removeRect()
    #         self.last_rect = rect
    #         self.last_rotation = self.graphicsView.current_pixmap_item.rotation()
    #         outImg = QtGui.QPixmap(rect.width(), rect.height())
    #         painter = QtGui.QPainter(outImg)
    #         self.scene.setSceneRect(rect)
    #         self.scene.render(painter)
    #         out_dir = os.path.dirname(self.files[0]) + "/cropped/"      # TODO improve output
    #         name = os.path.basename(self.files[0])
    #         name, _ = os.path.splitext(name)
    #         os.makedirs(out_dir, exist_ok=True)
    #         path = out_dir + name + ".png"
    #         outImg.save(path, "PNG")
    #         painter.end()
    #         del self.files[0]
    #         self.load_next_image()

    def drop_handler(self, e: QtGui.QDropEvent):
        urls = e.mimeData().urls()
        self.files = [url.path() for url in urls]
        self.load_next_image()

    def skip_image(self):
        if len(self.files) > 0:
            del self.files[0]
            self.load_next_image()

