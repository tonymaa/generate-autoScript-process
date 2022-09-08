# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/GaspUi.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(799, 624)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.openButton = QtWidgets.QToolButton(self.centralwidget)
        self.openButton.setObjectName("openButton")
        self.horizontalLayout.addWidget(self.openButton)
        self.saveButton = QtWidgets.QToolButton(self.centralwidget)
        self.saveButton.setObjectName("saveButton")
        self.horizontalLayout.addWidget(self.saveButton)
        self.cropButton = QtWidgets.QToolButton(self.centralwidget)
        self.cropButton.setObjectName("cropButton")
        self.horizontalLayout.addWidget(self.cropButton)
        self.rotateCwButton = QtWidgets.QToolButton(self.centralwidget)
        self.rotateCwButton.setObjectName("rotateCwButton")
        self.horizontalLayout.addWidget(self.rotateCwButton)
        self.rotateCcwButton = QtWidgets.QToolButton(self.centralwidget)
        self.rotateCcwButton.setObjectName("rotateCcwButton")
        self.horizontalLayout.addWidget(self.rotateCcwButton)
        self.skipButton = QtWidgets.QToolButton(self.centralwidget)
        self.skipButton.setObjectName("skipButton")
        self.horizontalLayout.addWidget(self.skipButton)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.graphicsView = EditorGraphicsView(self.centralwidget)
        self.graphicsView.setObjectName("graphicsView")
        self.verticalLayout.addWidget(self.graphicsView)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 799, 22))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "CX10 commander"))
        self.openButton.setText(_translate("MainWindow", "Open"))
        self.saveButton.setText(_translate("MainWindow", "Save"))
        self.cropButton.setText(_translate("MainWindow", "Crop"))
        self.rotateCwButton.setText(_translate("MainWindow", "Rotate CW"))
        self.rotateCcwButton.setText(_translate("MainWindow", "Rotate CCW"))
        self.skipButton.setText(_translate("MainWindow", "Skip"))

from editorgraphicsview import EditorGraphicsView
