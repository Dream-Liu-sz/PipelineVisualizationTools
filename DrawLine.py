
from PyQt5.Qt import QPainter
from PyQt5.Qt import QPen


class DrawLinePainter(QPainter):

    def __init__(self, parent, srcPort, dstPort, color):
        super(DrawLinePainter, self).__init__(parent)
        self.mSrcPort = srcPort
        self.mDstPort = dstPort
        self.mColor = color
        self.mPen = QPen(color)
        self.setPen(self.mPen)

    def drawLink(self):
        if self.mSrcPort != None and self.mDstPort != None and \
                self.mSrcPort.getPortPos() != None and self.mDstPort.getPortPos() != None:
            self.drawLine(self.mSrcPort.getPortPos() + self.mSrcPort.getParentNodePos(),
                          self.mDstPort.getPortPos() + self.mDstPort.getParentNodePos())