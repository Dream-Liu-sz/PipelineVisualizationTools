from PyQt5.QtCore import Qt, pyqtSignal, QRect, QPoint, QSize, QEvent
from PyQt5.QtGui import QPalette, QPen, QBrush, QFont, QPainter, QCursor, QColor, QFontMetrics
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
        # Slot registered by MainWindow to notify it when nodePainter receives a mouse press event
        # Currently used to resolve the conflict between hover-showing-prop and press-dragging-node
        self.signal.connect(slot)

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
        node_title = self.mNode.getNodeName() + "_" + str(self.mNode.getNodeInstanceId())
        title_size = self.fitTextPointSize(node_title, header.width(), max(8, int(self.mFontSize * 0.58)), 7)
        self.mNodeFont = font(title_size, bold=True)
        p.setFont(self.mNodeFont)
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

    def fitTextPointSize(self, text, max_width, preferred_size, min_size):
        size = max(min_size, preferred_size)
        while size > min_size:
            metrics = QFontMetrics(font(size, bold=True))
            if metrics.horizontalAdvance(text) <= max_width:
                return size
            size -= 1
        return min_size

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
            event.ignore()

    def wheelEvent(self, event):
        if self.mKeyCtrlStatus:
            angle = event.angleDelta() / 8
            angleX = angle.x()
            angleY = angle.y()
            if angleY > 0:
                increase = 0
                size = self.geometry()
                if size.height() > self.mMinHeight or size.width() > self.mMinWidth:
                    self.mEnlargeSum += 2
                    increase = int(self.mEnlargeSum / 10)
                    if increase >= 1:
                        self.mEnlargeSum = 0
                self.resize(size.width() + 2, size.height() + int(2 * self.mScale + 0.5))
                self.mNode.setNodeSize(QSize(self.geometry().width(), self.geometry().height()))
                self.setFontSize(self.getFontSize() + increase)
                self.update()
            else:
                dec = 0
                size = self.geometry()
                if size.height() > self.mMinHeight or size.width() > self.mMinWidth:
                    self.mEnlargeSum -= 2
                    dec = int(self.mEnlargeSum / 10)
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

    def show(self):
        super(NodePainter, self).show()
