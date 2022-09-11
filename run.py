#!/usr/bin/python3
import sys
from PyQt5 import QtCore, QtWidgets, QtGui
from Gasp import Gasp
import argparse


def main():
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    gasp = Gasp()
    app.aboutToQuit.connect(gasp.closing)
    gasp.setupUi(MainWindow)
    gasp.built(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Serial Image Editor")
    # parser.add_argument('config_file', help="JSON configuration file")
    # args = parser.parse_args()
    # main(args.config_file)
    main()
