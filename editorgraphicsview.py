import PyQt5
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtGui import QPen, QBrush


class EditorGraphicsView(QtWidgets.QGraphicsView):

    def __init__(self, parent=None):
        QtWidgets.QGraphicsView.__init__(self)
        self.currentMode = 0
        self.setPositionInput = None
        self.lastP = None
        self.selected_rect = [None, None]  # type: QtCore.QRect
        self.rect_item = [None, None]
        self.current_pixmap_item = [None, None]         # type: QtWidgets.QGraphicsPixmapItem
                       # type: QtWidgets.QGraphicsRectItem
        self.dropHandler = [None, None]

        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)
        self.rubberBandChanged.connect(lambda rect: self.handle_rubber_band(rect))

    def removeRectAll(self):
        self.removeRectByMode(0)
        self.removeRectByMode(1)

    def removeRect(self):
        if self.rect_item[self.currentMode] is not None:
            self.scene().removeItem(self.rect_item[self.currentMode])
            self.rect_item[self.currentMode] = None
            self.selected_rect[self.currentMode] = None
            if self.setPositionInput is not None:
                self.setPositionInput(None)

    def removeRectByMode(self, mode):
        if self.rect_item[mode] is not None:
            self.scene().removeItem(self.rect_item[mode])
            self.rect_item[mode] = None
            self.selected_rect[mode] = None
            if self.setPositionInput is not None:
                self.setPositionInput(None)

    def wheelEvent(self, e: QtGui.QWheelEvent):
        self.setTransformationAnchor(QtWidgets.QGraphicsView.NoAnchor)
        self.setResizeAnchor(QtWidgets.QGraphicsView.NoAnchor)

        if e.angleDelta().y() > 0:
            scale = 1.2
        else:
            scale = 1/1.2
        oldPos = self.mapToScene(e.pos())
        self.scale(scale, scale)
        newPos = self.mapToScene(e.pos())
        delta = newPos - oldPos
        self.translate(delta.x(), delta.y())

    def mousePressEvent(self, e: QtGui.QMouseEvent):
        QtWidgets.QGraphicsView.mousePressEvent(self, e)
        self.lastP = e.pos()
        if self.rect_item[self.currentMode] is not None:
            self.scene().removeItem(self.rect_item[self.currentMode])
            self.rect_item[self.currentMode] = None
            self.selected_rect[self.currentMode] = None

    def mouseReleaseEvent(self, e: QtGui.QMouseEvent):
        QtWidgets.QGraphicsView.mouseReleaseEvent(self, e)
        if e.button() == QtCore.Qt.LeftButton:
            scene = self.scene()    # type: QtWidgets.QGraphicsScene
            if self.selected_rect[self.currentMode] is not None:
                polygon = self.mapToScene(self.selected_rect[self.currentMode])  # type: QtCore.QPolygon
                if self.setPositionInput is not None and not self.setPositionInput(polygon.boundingRect()):
                    return
                q_pen = QPen(PyQt5.QtCore.Qt.red, 2, PyQt5.QtCore.Qt.SolidLine)
                if self.currentMode == 1:
                    q_pen = QPen(PyQt5.QtCore.Qt.blue, 2, PyQt5.QtCore.Qt.DashLine)
                self.rect_item[self.currentMode] = scene.addRect(polygon.boundingRect(), pen=q_pen)


    def keyPressEvent(self, e: QtGui.QKeyEvent):
        QtWidgets.QGraphicsView.keyPressEvent(self, e)
        if e.key() == QtCore.Qt.Key_Control:
            self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)

    def keyReleaseEvent(self, e: QtGui.QKeyEvent):
        QtWidgets.QGraphicsView.keyReleaseEvent(self, e)
        if e.key() == QtCore.Qt.Key_Control:
            self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)

    def mouseMoveEvent(self, e: QtGui.QMouseEvent):
        if e.buttons() & QtCore.Qt.RightButton:
            newP = e.pos()
            delta = newP - self.lastP
            self.lastP = newP
            self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorViewCenter)
            if QtWidgets.QApplication.keyboardModifiers() & QtCore.Qt.ShiftModifier:
                angle = delta.y() / 100.0
            else:
                angle = delta.y()/10
            self.rotate_pixmap(angle)
            self.setTransformationAnchor(QtWidgets.QGraphicsView.NoAnchor)
        else:
            QtWidgets.QGraphicsView.mouseMoveEvent(self, e)

    def handle_rubber_band(self, rect: QtCore.QRect):
        if not rect.isEmpty():
            self.selected_rect[self.currentMode] = rect

    def rotate_pixmap(self, angle):
        rotation = self.current_pixmap_item[self.currentMode].rotation() + angle
        self.current_pixmap_item[self.currentMode].setTransformationMode(QtCore.Qt.SmoothTransformation)
        self.current_pixmap_item[self.currentMode].setRotation(rotation)
        center = self.current_pixmap_item[self.currentMode].boundingRect().width()/2, self.current_pixmap_item[self.currentMode].boundingRect().height()/2
        self.current_pixmap_item[self.currentMode].setTransformOriginPoint(*center)

    def dropEvent(self, e: QtGui.QDropEvent):
        if e.mimeData().hasUrls() and self.dropHandler[self.currentMode] is not None:
            self.dropHandler[self.currentMode](e)
            e.accept()
        else:
            e.ignore()

    def dragEnterEvent(self, e: QtGui.QDragEnterEvent):
        if e.mimeData().hasUrls():
            e.accept()
        else:
            e.ignore()

    def dragMoveEvent(self, e: QtGui.QDragMoveEvent):
        if e.mimeData().hasUrls():
            e.accept()
        else:
            e.ignore()
