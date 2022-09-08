from PyQt5 import QtCore, QtWidgets, QtGui


class EditorGraphicsView(QtWidgets.QGraphicsView):

    def __init__(self, parent=None):
        QtWidgets.QGraphicsView.__init__(self)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.lastP = None
        self.selected_rect = None   # type: QtCore.QRect
        self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)
        self.rubberBandChanged.connect(lambda rect: self.handle_rubber_band(rect))
        self.current_pixmap_item = None         # type: QtWidgets.QGraphicsPixmapItem
        self.rect_item = None                   # type: QtWidgets.QGraphicsRectItem
        self.dropHandler = None

    def removeRect(self):
        if self.rect_item is not None:
            self.scene().removeItem(self.rect_item)
            self.rect_item = None
            self.selected_rect = None

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
        if self.rect_item is not None:
            self.scene().removeItem(self.rect_item)
            self.rect_item = None
            self.selected_rect = None

    def mouseReleaseEvent(self, e: QtGui.QMouseEvent):
        QtWidgets.QGraphicsView.mouseReleaseEvent(self, e)
        if e.button() == QtCore.Qt.LeftButton:
            scene = self.scene()    # type: QtWidgets.QGraphicsScene
            if self.selected_rect is not None:
                polygon = self.mapToScene(self.selected_rect)  # type: QtCore.QPolygon
                self.rect_item = scene.addRect(polygon.boundingRect())

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
            self.selected_rect = rect

    def rotate_pixmap(self, angle):
        rotation = self.current_pixmap_item.rotation() + angle
        self.current_pixmap_item.setTransformationMode(QtCore.Qt.SmoothTransformation)
        self.current_pixmap_item.setRotation(rotation)
        center = self.current_pixmap_item.boundingRect().width()/2, self.current_pixmap_item.boundingRect().height()/2
        self.current_pixmap_item.setTransformOriginPoint(*center)

    def dropEvent(self, e: QtGui.QDropEvent):
        if e.mimeData().hasUrls() and self.dropHandler is not None:
            self.dropHandler(e)
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
