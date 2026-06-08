from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtCore import QPoint, QSize, QPointF, QRectF
from PyQt5.QtGui import QPalette, QPen, QBrush, QColor, QPainter, QFont, QPainterPathStroker
from PyQt5.QtWidgets import QFrame

from Utils import Utils
from BezierLine import BezierLineRenderer
from ui_theme import COLORS, font

class CanvasImage(QFrame):
    TAG = "CanvasImage"
    linkClicked = pyqtSignal(object, object)
    backgroundClicked = pyqtSignal()

    def __init__(self, parent, color):
        super(CanvasImage ,self).__init__(parent)
        self.setPalette(QPalette(QColor(COLORS["bg"])))
        self.setAutoFillBackground(True)
        self.pen = QPen()
        self.brush = QBrush()
        self.mColor = QColor(200, 0, 0)
        self.Shape = ["Line","Rectangle", 'Rounded Rectangle', "Ellipse", "Pie", 'Chord',
        "Path","Polygon", "Polyline", "Arc", "Points", "Text", "Pixmap"]
        self.mWidth = 400
        self.mHeight = 400
        self.setMinimumSize(8000, 8000)
        self.setFrameShadow(QFrame.Shadow.Plain)
        self.setFrameShape(QFrame.Shape.NoFrame)
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
        self.mSelectedLink = None
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
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.TextAntialiasing, True)
        self.drawBackground(painter)

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
                link_selected = self.mSelectedLink is not None and self.mSelectedLink[0] is out and self.mSelectedLink[1] is input
                for node in self.mNodeList:
                    if node.matchPort(input):
                        pen = QPen(self.mNodeMapPainter.get(node))
                        if link_selected:
                            pen.setWidth(max(4, pen.width() + 2))
                        painter.setPen(pen)

                self.drawLink(out, input, painter, link_selected)
                pass

        if len(self.mNodeList) == 0:
            self.drawEmptyState(painter)

    def drawBackground(self, painter):
        painter.fillRect(self.rect(), QColor(COLORS["bg"]))
        minor_pen = QPen(QColor(COLORS["grid"]))
        major_pen = QPen(QColor(COLORS["grid_major"]))
        minor_pen.setWidth(1)
        major_pen.setWidth(1)

        grid = 40
        major_grid = grid * 4
        for x in range(0, self.width(), grid):
            painter.setPen(major_pen if x % major_grid == 0 else minor_pen)
            painter.drawLine(x, 0, x, self.height())
        for y in range(0, self.height(), grid):
            painter.setPen(major_pen if y % major_grid == 0 else minor_pen)
            painter.drawLine(0, y, self.width(), y)

    def drawEmptyState(self, painter):
        card = QRectF(420, 360, 430, 190)
        painter.setPen(QPen(QColor(COLORS["border"]), 1))
        painter.setBrush(QColor(COLORS["panel"]))
        painter.drawRoundedRect(card, 18, 18)

        title_font = font(15, bold=True)
        body_font = font(10)
        painter.setFont(title_font)
        painter.setPen(QColor(COLORS["text"]))
        painter.drawText(card.adjusted(28, 28, -28, -120), Qt.AlignLeft | Qt.AlignTop, "Pipeline canvas")

        painter.setFont(body_font)
        painter.setPen(QColor(COLORS["text_muted"]))
        message = "Open an XML or JSON pipeline file, then double-click a pipeline in the left navigation tree to render its topology."
        painter.drawText(card.adjusted(28, 76, -28, -28), Qt.AlignLeft | Qt.TextWordWrap, message)

    def drawLink(self, srcPort, dstPort, painter, selected=False):
        if srcPort != None and dstPort != None and \
                srcPort.getPortPos() != None and dstPort.getPortPos() != None:
            for node in self.mNodeList:
                if node.matchPort(dstPort):
                    pen = self.mNodeMapPainter.get(node)
                    if pen is not None:
                        pen = QPen(pen)
                        if selected:
                            pen.setWidth(max(4, pen.width() + 2))
                        BezierLineRenderer.draw_bezier_link(painter, srcPort, dstPort, pen, self.mRadius)
                        return
            startPont = srcPort.getPortPos() + srcPort.getParentNodePos() + QPoint(srcPort.getWidth(), 0)
            endPoint = dstPort.getPortPos() + dstPort.getParentNodePos()
            painter.drawLine(startPont, endPoint)

    def setSelectedLink(self, src_port, dst_port):
        self.mSelectedLink = (src_port, dst_port) if src_port is not None and dst_port is not None else None
        self.update()

    def hitTestLink(self, point):
        if self.mPortLinkDes is None:
            return None
        stroker = QPainterPathStroker()
        stroker.setWidth(14)
        for src_port, dst_ports in self.mPortLinkDes.items():
            for dst_port in dst_ports:
                if src_port.getPortPos() is None or dst_port.getPortPos() is None:
                    continue
                if src_port.getParentNodePos() is None or dst_port.getParentNodePos() is None:
                    continue
                start_point = src_port.getPortPos() + src_port.getParentNodePos() + QPoint(src_port.getWidth(), 0)
                end_point = dst_port.getPortPos() + dst_port.getParentNodePos()
                path = BezierLineRenderer.create_bezier_path(start_point, end_point)
                if stroker.createStroke(path).contains(QPointF(point)):
                    return src_port, dst_port
        return None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            hit = self.hitTestLink(event.pos())
            if hit is not None:
                self.setSelectedLink(hit[0], hit[1])
                self.linkClicked.emit(hit[0], hit[1])
            else:
                self.setSelectedLink(None, None)
                self.backgroundClicked.emit()
            event.ignore()

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
