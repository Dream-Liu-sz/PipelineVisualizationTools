from PyQt5.QtCore import Qt, pyqtSignal, QRect, QPoint, QSize, QEvent
from PyQt5.QtGui import QPalette, QPen, QBrush, QFont, QPainter, QCursor, QColor
from PyQt5.QtWidgets import QFrame

from Utils import Utils
from Utils import ComMsg
from Utils import MsgType
from ui_theme import COLORS, font

class NodePainter(QFrame):
    TAG = "NodePainter"

    signal = pyqtSignal(ComMsg)
    nodeClicked = pyqtSignal(object)
    def __init__(self, parent, node, fontSize, jsonOpened):
        super(NodePainter ,self).__init__(parent)
        Utils.LogD(self.TAG, "__init__ +")
        self.setPalette(QPalette(Qt.black))
        self.setAutoFillBackground(True)
        self.mNode = node
        self.setPalette(QPalette(Qt.white))
        self.setAutoFillBackground(True)
        self.pen = QPen()
        self.brush = QBrush()
        self.mColor = node.getColor()
        self.Shape = ["Line","Rectangle", 'Rounded Rectangle', "Ellipse", "Pie", 'Chord',
        "Path","Polygon", "Polyline", "Arc", "Points", "Text", "Pixmap"]
        self.move(node.getNodePos())
        self.mSize = node.getNodeSize()
        self.resize(self.mSize)
        self.mFontSize = fontSize
        self.mNodeFont = QFont()
        self.mEnlargeSum = 0
        self.mScale = float(self.mSize.height()) / float(self.mSize.width())
        self.mMinWidth = 90
        self.mMinHeight = self.mMinWidth * self.mScale
        self.setMinimumSize(self.mMinWidth, self.mMinHeight)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAutoFillBackground(False)
        self.setMouseTracking(True)
        self.installEventFilter(parent)
        # Utils.LogD(self.TAG, ("__init__ - minW %d minH %d" % (self.mMinWidth, self.mMinHeight)))
        self.setStyleSheet("background: transparent;")
        self.setFrameShadow(QFrame.Plain)
        self.setFrameShape(QFrame.NoFrame)
        self.mKeyCtrlStatus = False
        self.mHoverMoveStatus = False
        self.mPressed = False
        self.mHovered = False
        self.mSelected = False
        self.mJsonOpend = jsonOpened
        self.mShowPortLabels = True

    def connectParentSlot(self, slot):
        '''
        @Func:MainWindow注冊進來的槽函數，用來通知mainWindow，nodePainter接收了鼠標press事件
              目前的作用是在mainWindow中用来解决鼠标悬停显示prop与鼠标按压拖拽node功能的
        '''
        self.signal.connect(slot)
        # pass

    def receviceParentMsg(self, msg):
        msgType, msgValue = msg.getMsg()
        if msgType == MsgType.KeyCtrl:
            self.mKeyCtrlStatus = msgValue
        elif msgType == MsgType.HoverMove:
            self.mHoverMoveStatus = msgValue

    def setShape(self, s):
        self.shape = s
        self.update()

    def setPen(self, p):
        self.pen = p
        self.update()

    def setBrush(self, b):
        self.brush = b
        self.update()

    def paintEvent(self, QPaintEvent):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        p.setRenderHint(QPainter.TextAntialiasing, True)

        accent = QColor(self.mColor)
        card = QRect(4, 4, self.geometry().width() - 9, self.geometry().height() - 9)
        shadow = QRect(7, 9, self.geometry().width() - 10, self.geometry().height() - 10)
        border_color = QColor(accent if self.mHovered or self.mPressed or self.mSelected else accent.darker(115))

        p.setPen(Qt.NoPen)
        p.setBrush(QColor(0, 0, 0, 125))
        p.drawRoundedRect(shadow, 10, 10)

        p.setBrush(QColor(COLORS["card"]))
        p.setPen(QPen(border_color, 3 if self.mSelected else (2 if self.mHovered or self.mPressed else 1)))
        p.drawRoundedRect(card, 10, 10)

        header = QRect(card.left() + 14, card.top() + 9, card.width() - 28, 30)
        p.setPen(QColor(COLORS["text"]))
        self.mNodeFont = font(max(9, int(self.mFontSize * 0.58)), bold=True)
        p.setFont(self.mNodeFont)
        node_title = self.mNode.getNodeName() + "_" + str(self.mNode.getNodeInstanceId())
        p.drawText(header, Qt.AlignLeft | Qt.AlignVCenter, node_title)

        self.mNodeFont = font(max(8, int(self.mFontSize * 0.44)), mono=True)
        p.setFont(self.mNodeFont)
        p.setPen(QColor(COLORS["text_muted"]))

        self.mNode.calPortPos()
        for port in self.mNode.getInputPort():
            portName = port.getPortNamePrune() if port.getPortNamePrune() is not None else port.getPortName()
            label = portName if self.mJsonOpend else portName + "_" + port.getPortId()
            port_center = port.getPortPos()
            p.setBrush(QColor(COLORS["card"]))
            p.setPen(QPen(QColor(COLORS["text_muted"]), 1))
            p.drawEllipse(QRect(port_center.x() - 4, port_center.y() - 4, 8, 8))
            p.setPen(QColor(COLORS["text_muted"]))
            if self.mShowPortLabels:
                if self.mJsonOpend:
                    p.drawText(port.getPortPos() + QPoint(10, 4), label)
                else:
                    p.drawText(port.getPortPos() + QPoint(10, 4), label)

        for port in self.mNode.getOutputPort():
            portName = port.getPortNamePrune() if port.getPortNamePrune() is not None else port.getPortName()
            label = portName if self.mJsonOpend else portName + "_" + port.getPortId()
            port_center = port.getPortPos() + QPoint(max(0, port.getWidth()), 0)
            p.setBrush(QColor(COLORS["card"]))
            p.setPen(QPen(accent, 2))
            p.drawEllipse(QRect(port_center.x() - 4, port_center.y() - 4, 8, 8))
            p.setPen(QColor(COLORS["text_muted"]))
            if self.mShowPortLabels:
                if self.mJsonOpend:
                    p.drawText(port.getPortPos() - QPoint(8, -4), label)
                else:
                    p.drawText(port.getPortPos() - QPoint(18, -4), label)
        # if self.shape == "Line":
        #     p.drawLine(rect.topLeft(), rect.bottomRight())
        # elif self.shape == "Rectangle":
        #     p.drawRect(rect)
        # elif self.shape == 'Rounded Rectangle':
        #     p.drawRoundedRect(rect, 25, 25, Qt.RelativeSize)
        # elif self.shape == "Ellipse":
        #     p.drawEllipse(rect)
        # elif self.shape == "Polygon":
        #     p.drawPolygon(QPolygon(points), Qt.WindingFill)
        # elif self.shape == "Polyline":
        #     p.drawPolyline(QPolygon(points))
        # elif self.shape == "Points":
        #     p.drawPoints(QPolygon(points))
        # elif self.shape == "Pie":
        #     p.drawPie(rect, startAngle, spanAngle)
        # elif self.shape == "Arc":
        #     p.drawArc(rect, startAngle, spanAngle)
        # elif self.shape == "Chord":
        #     p.drawChord(rect, startAngle, spanAngle)
        # elif self.shape == "Path":
        #     # p.drawPath(path)
        #     pass
        # elif self.shape == "Text":
        #     p.drawText(rect, Qt.AlignCenter, "Hello Qt!")
        # elif self.shape == "Pixmap":
        #     p.drawPixmap(150, 150, QPixmap("images/qt-logo.png"))

    def setNodeSize(self, size):
        self.mNode.setNodeSize(size)

    def setFontSize(self, fontSize):
        self.mFontSize = fontSize
        self.mNode.setNodeFont(self.mFontSize)

    def getFontSize(self):
        return self.mFontSize

    def getNodePos(self):
        return self.mNode.getNodePos()

    def setSelected(self, selected):
        self.mSelected = selected
        self.update()

    def setShowPortLabels(self, show):
        self.mShowPortLabels = show
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.mHoverMoveStatus is False:
            self.mPressed = True
            self.m_DragPosition = event.globalPos() - self.pos()
            event.accept()
            self.setCursor(QCursor(Qt.OpenHandCursor))
            msg = ComMsg(MsgType.LeftButton, True)
            self.signal.emit(msg)
            self.nodeClicked.emit(self.mNode)
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.mHoverMoveStatus is False:
            self.mPressed = False
            self.setCursor(QCursor(Qt.ArrowCursor))
            event.accept()
            msg = ComMsg(MsgType.LeftButton, False)
            self.signal.emit(msg)
            self.update()

    def mouseMoveEvent(self, event):
        if Qt.LeftButton and self.mPressed:
            pos = event.globalPos()
            nextPos = QPoint(pos - self.m_DragPosition)
            self.move(nextPos)
            self.mNode.setNodePos(nextPos)
            self.mNode.calPortPos()
            # self.mNode.calPortPos(self.mNodeFont)
            event.ignore()

    def wheelEvent(self, event):
        if self.mKeyCtrlStatus:
            angle = event.angleDelta() / 8    # 返回QPoint对象，为滚轮转过的数值，单位为1/8度
            angleX = angle.x()                # 水平滚过的距离(此处用不上)
            angleY = angle.y()                # 竖直滚过的距离
            if angleY > 0:
                # self.mCanvasWidth = self.mCanvasWidth + 50
                # self.mCanvasHeight = self.mCanvasHeight + 50
                # self.mCanvas.resize(self.mCanvasWidth, self.mCanvasHeight)
                increase = 0
                size = self.geometry()
                if size.height() > self.mMinHeight or size.width() > self.mMinWidth:
                    self.mEnlargeSum += 2
                    increase = int(self.mEnlargeSum / 10)
                    # Utils.LogI(self.TAG, ("mEnlargeSum %d increase %d" % (self.mEnlargeSum, increase)))
                    if increase >= 1:
                        self.mEnlargeSum = 0
                self.resize(size.width() + 2, size.height() + int(2 * self.mScale + 0.5))
                self.mNode.setNodeSize(QSize(self.geometry().width(), self.geometry().height()))
                self.setFontSize(self.getFontSize() + increase)
                self.update()
            else:   # 滚轮下滚
                dec = 0
                size = self.geometry()
                if size.height() > self.mMinHeight or size.width() > self.mMinWidth:
                    self.mEnlargeSum -= 2
                    dec = int(self.mEnlargeSum / 10)
                    # Utils.LogI(self.TAG, ("mEnlargeSum %d dec %d" % (self.mEnlargeSum, dec)))
                    if dec <= -1:
                        self.mEnlargeSum = 0
                self.resize(size.width() - 2, size.height() - int(2 * self.mScale + 0.5))
                self.mNode.setNodeSize(QSize(self.geometry().width(), self.geometry().height()))
                self.setFontSize(self.getFontSize() + dec)
                self.update()
            msg = ComMsg(MsgType.WheelMouse, True)
            self.signal.emit(msg)
            event.accept()

    def eventFilter(self, object, event):
        if event.type() == QEvent.HoverMove:
            return True
        return False

    def enterEvent(self, event):
        self.mHovered = True
        self.update()
        super(NodePainter, self).enterEvent(event)

    def leaveEvent(self, event):
        self.mHovered = False
        self.update()
        super(NodePainter, self).leaveEvent(event)

    # def keyPressEvent(self, keyEvent):
    #     pass

    def show(self):
        super(NodePainter, self).show()
