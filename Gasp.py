import cv2
import win32gui
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtGui import QImage

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


def front_window_screen(hwnd, isKeepActive):
    """PIL截图方法，不能被遮挡"""
    if isKeepActive:
        shell = win32com.client.Dispatch("WScript.Shell")
        shell.SendKeys('%')
        SetForegroundWindow(hwnd)  # 窗口置顶
    # time.sleep(0.2)  # 置顶后等0.2秒再截图
    x1, y1, x2, y2 = GetWindowRect(hwnd)  # 获取窗口坐标
    grab_image = ImageGrab.grab((x1, y1, x2, y2))  # 用PIL方法截图
    im_cv2 = array(grab_image)  # 转换为cv2的矩阵格式
    # im_opencv = cv2.cvtColor(im_cv2, cv2.COLOR_BGRA2GRAY)
    return im_cv2

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

        self.scene = QtWidgets.QGraphicsScene()
        self.files = []
        self.openShortcut = None
        self.saveEnterShortcut = None
        self.saveShortcut = None
        self.skipShortcut = None
        self.last_rect = None
        self.last_rotation = 0

    def built(self):
        # self.openShortcut = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+O"), self.centralwidget)
        # self.saveShortcut = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+S"), self.centralwidget)
        # self.saveEnterShortcut = QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Space), self.centralwidget)
        # self.skipShortcut = QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Tab), self.centralwidget)

        self.graphicsView.setScene(self.scene)
        self.scene.setBackgroundBrush(QtCore.Qt.white)

        self.openProcess.triggered.connect(self.select_dir) # 打开process按钮
        self.choose_phone.setDisabled(True) # 选择windows窗口
        self.mode.currentIndexChanged.connect(self.chooseMode) # 模式选择事件
        self.choose_phone.currentIndexChanged.connect(self.selectDevice) # 选择abs设备
        self.choose_window.clicked.connect(self.selectWindow) # 选择窗口
        self.screentshot.setDisabled(True)
        self.save_template.setDisabled(True)
        self.width.setDisabled(True)
        self.height.setDisabled(True)
        self.screentshot.clicked.connect(self.catchScreen)

        self.save_template.clicked.connect(self.saveTemplate)

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

    def closing(self):
        pass

    def select_dir(self):
        self.curProcess = QtWidgets.QFileDialog.getExistingDirectory(None, "Select Directory")
        print(f"【debug】 select process path: {self.curProcess}")

    def chooseMode(self, e):
        self.curMode = e
        self.choose_phone.setDisabled(self.curMode == constant.WINDOWSMODE)
        self.choose_window.setDisabled(self.curMode == constant.ABSMODE)
        if self.curMode == constant.ABSMODE:
            status, deviceIds = HandleUtils.adb_device_status()
            self.choose_phone.clear()
            self.deviceIds = deviceIds
            if not status:
                self.choose_phone.addItem("no device detected!")
            else:
                for deviceId in deviceIds:
                    self.choose_phone.addItem(deviceId)
        else:
            self.choose_phone.clear()
            self.choose_phone.addItem("Choose Phone")

    def selectDevice(self, e):
        self.selectedDeviceIndex = e
        print(f"【debug】 select device index: {self.selectedDeviceIndex}, and deviceId is {self.deviceIds[e] if e >= 0 and e < len(self.deviceIds) else 'None'}")

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
        win32gui.MoveWindow(self.windowHandler, 0, 0, width, height, True)

    def catchScreen(self):
        screen = front_window_screen(self.windowHandler, True)
        height, width, depth = screen.shape
        screen = cv2.cvtColor(screen, cv2.COLOR_BGR2RGB)
        screen = cvToQImage(screen)
        self.scene.clear()
        screen = QtGui.QPixmap.fromImage(screen)
        pixmap_item = self.scene.addPixmap(screen)  # type: QtWidgets.QGraphicsPixmapItem
        self.graphicsView.current_pixmap_item = pixmap_item
        self.graphicsView.rotate_pixmap(self.last_rotation)
        if self.last_rect is not None:
            self.graphicsView.rect_item = self.scene.addRect(self.last_rect)
        rect = screen.rect()  # type: # QtCore.QRect
        rect.setWidth(rect.width() * 2)
        rect.setHeight(rect.height() * 2)
        rect.setLeft(rect.x() - rect.width() / 2)
        rect.setTop(rect.y() - rect.height() / 2)
        self.scene.setSceneRect(QtCore.QRectF(rect))
        self.graphicsView.fitInView(pixmap_item.boundingRect(), QtCore.Qt.KeepAspectRatio)

    def saveTemplate(self):
        rect = self.graphicsView.rect_item.boundingRect()  #
        rect.x()
        rect.y()
        print(rect)
        # self.graphicsView.removeRect()
        # self.last_rect = rect
        # self.last_rotation = self.graphicsView.current_pixmap_item.rotation()
        # outImg = QtGui.QPixmap(rect.width(), rect.height())
        # painter = QtGui.QPainter(outImg)
        # self.scene.setSceneRect(rect)
        # self.scene.render(painter)

        # out_dir = os.path.dirname(self.files[0]) + "/cropped/"  # TODO improve output
        # name = os.path.basename(self.files[0])
        # name, _ = os.path.splitext(name)
        # os.makedirs(out_dir, exist_ok=True)
        # path = out_dir + name + ".png"
        # outImg.save(path, "PNG")
        # painter.end()
        # del self.files[0]
        # self.load_next_image()

    def load_next_image(self):
        self.graphicsView.current_pixmap_item = None
        self.graphicsView.rect_item = None
        if len(self.files) > 0:
            self.load_image(self.files[0])
        else:
            self.scene.clear()
            text_item = self.scene.addText("No images left !")
            self.graphicsView.fitInView(text_item.boundingRect(), QtCore.Qt.KeepAspectRatio)

    def save_image(self):
        if self.graphicsView.rect_item is not None and len(self.files) > 0:
            rect = self.graphicsView.rect_item.boundingRect()   # type
            self.graphicsView.removeRect()
            self.last_rect = rect
            self.last_rotation = self.graphicsView.current_pixmap_item.rotation()
            outImg = QtGui.QPixmap(rect.width(), rect.height())
            painter = QtGui.QPainter(outImg)
            self.scene.setSceneRect(rect)
            self.scene.render(painter)
            out_dir = os.path.dirname(self.files[0]) + "/cropped/"      # TODO improve output
            name = os.path.basename(self.files[0])
            name, _ = os.path.splitext(name)
            os.makedirs(out_dir, exist_ok=True)
            path = out_dir + name + ".png"
            outImg.save(path, "PNG")
            painter.end()
            del self.files[0]
            self.load_next_image()

    def drop_handler(self, e: QtGui.QDropEvent):
        urls = e.mimeData().urls()
        self.files = [url.path() for url in urls]
        self.load_next_image()

    def skip_image(self):
        if len(self.files) > 0:
            del self.files[0]
            self.load_next_image()

