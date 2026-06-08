from PyQt5.QtCore import Qt
from PyQt5.QtCore import QPoint, QSize, QPointF
from PyQt5.QtGui import QPalette, QPen, QBrush, QColor, QPainter, QFont
from PyQt5.QtWidgets import QFrame

from Utils import Utils
from BezierLine import BezierLineRenderer

class CanvasImage(QFrame):
    TAG = "CanvasImage"

    def __init__(self, parent, color):
        super(CanvasImage ,self).__init__(parent)
        self.setPalette(QPalette(Qt.white))
        self.setAutoFillBackground(True)
        self.pen = QPen()
        self.brush = QBrush()
        self.mColor = QColor(200, 0, 0)
        self.Shape = ["Line","Rectangle", 'Rounded Rectangle', "Ellipse", "Pie", 'Chord',
        "Path","Polygon", "Polyline", "Arc", "Points", "Text", "Pixmap"]
        self.mWidth = 400
        self.mHeight = 400
        self.setMinimumSize(8000, 8000)
        self.setFrameShadow(QFrame.Shadow.Raised)
        self.setFrameShape(QFrame.Shape.Box)
        self.move(QPoint(20, 20))
        self.mSize = QSize(8000, 8000)
        self.resize(self.mSize)
        self.mFontSize = 24
        self.mPortLinkDes = {}
        self.mLinkList = []
        self.mNodeList = []
        self.mStartToEndPosMap = dict()
        self.mNodeMapPainter = dict()
        self.mRadius = 5
        # self.setAttribute(Qt.WidgetAttribute.WA_Hover);
        # self.installEventFilter(self)

    def setShape(self, s):
        self.shape = s
        self.update()

    def setPen(self, p):
        self.pen = p
        self.update()

    def setBrush(self, b):
        self.brush = b
        self.update()

    def setPen1(self, p):
        self.mPen = p
        self.update()

    def setRadius(self, radius):
        self.mRadius = radius

    def paintEvent(self, QPaintEvent):
        painter = QPainter(self)
        nodeFront = QFont()
        nodeFront.setPixelSize(self.mFontSize)
        self.pen.setWidth(3)
        # p.setBrush(self.brush)
        painter.setFont(nodeFront)

        i = 0
        for out in self.mPortLinkDes.keys():
            for input in self.mPortLinkDes.get(out):
                # Utils.LogD(self.TAG, ("ready draw  %s --> %s" % (out.getPortName(), input.getPortName())))
                # Utils.LogD(self.TAG, out.getPortPos())
                # Utils.LogD(self.TAG, out.getParentNodePos())
                # Utils.LogD(self.TAG, input.getPortPos())
                # Utils.LogD(self.TAG, input.getParentNodePos())
                for node in self.mNodeList:
                    if node.matchPort(input):
                        painter.setPen(self.mNodeMapPainter.get(node))

                self.drawLink(out, input, painter)
                pass

    def drawLink(self, srcPort, dstPort, painter):
        if srcPort != None and dstPort != None and \
                srcPort.getPortPos() != None and dstPort.getPortPos() != None:
            for node in self.mNodeList:
                if node.matchPort(dstPort):
                    pen = self.mNodeMapPainter.get(node)
                    if pen is not None:
                        BezierLineRenderer.draw_bezier_link(painter, srcPort, dstPort, pen, self.mRadius)
                        return
            startPont = srcPort.getPortPos() + srcPort.getParentNodePos() + QPoint(srcPort.getWidth(), 0)
            endPoint = dstPort.getPortPos() + dstPort.getParentNodePos()
            painter.drawLine(startPont, endPoint)

    def initPainterInstance(self, nodeList):
        for node in nodeList:
            pen = QPen()
            pen.setWidth(2)
            pen.setColor(node.getColor())
            temp = {node: pen}
            self.mNodeMapPainter.update(temp)

        self.mNodeList = nodeList

    def setNodeList(self, list):
        self.mNodeList = list

    def setPortLinkDes(self, link):
        self.mPortLinkDes = link

    def wheelEvent(self, event):
        self.update()
        event.ignore()

    def mouseMoveEvent(self, event):
        '''
        :Func:为了让拖动node painter时能够及时的绘制link
        '''
        if Qt.LeftButton:
            self.update()
            event.ignore()

    # def mouseReleaseEvent(self, event):
    #     if event.button() == Qt.LeftButton:
    #         self.update()
    #         event.ignore()
    #         Utils.LogI(self.TAG, "mouseReleaseEvent")

    # def keyPressEvent(self, keyEvent):
    #     if keyEvent.key() == Qt.Key_Shift:
    #         Utils.LogE(self.TAG, "keyevent")

    def show(self):
        super(CanvasImage, self).show()
    # def calSize(self):
