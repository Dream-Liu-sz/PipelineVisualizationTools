from PyQt5.Qt import QPoint
from PyQt5.Qt import QMessageBox
from PyQt5.Qt import QMainWindow
from PyQt5.QtCore import Qt, QEvent, QTimer, pyqtSignal
from PyQt5.Qt import QPalette
from PyQt5.Qt import QIcon
from PyQt5.Qt import QAction
from PyQt5.QtGui import QColor, QCursor, QFont, QFontMetrics
from PyQt5.QtWidgets import QTreeWidget, QAbstractItemView, QHeaderView, QFrame, QTreeWidgetItem, QWidget, QFileDialog, \
    QLabel

from CanvasWidget import CanvasImage
from NodePainter import NodePainter
from Utils import Utils
from Utils import ComMsg
from Utils import MsgType
from UseCase import UseCaseDes
import sys

import resource
# import time

class MainWindow(QMainWindow):
    TAG = "MainWindow"
    mSignal = pyqtSignal(ComMsg)
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setWindowTitle("Pipeline Visualization tools")
        self.resize(1280, 720)
        # self.setCentralWidget(self.mCanvas)
        # self.func()
        self.mImageBrowserWidth = 200
        self.mVlayoutInstalMap = dict()
        self.mNodePainterList = []
        self.mDrawLinePainterList = []
        self.mSelectPipeline = None
        self.mEnlargeSum = 0
        self.m_drag = False
        self.mLabel = None
        self.setAttribute(Qt.WidgetAttribute.WA_Hover);
        self.installEventFilter(self)
        self.setPalette(QPalette(Qt.white))
        self.setAutoFillBackground(True)
        self.setWindowIcon(QIcon(":res/logo.ico"))
        # self.setWindowFlag(Qt.FramelessWindowHint)
        # self.setAttribute(Qt.WA_TranslucentBackground)
        self.isTimeEnd = False
        self.mTimerStartFlag = False
        self.mLabelMovePos = None
        self.mlabelStatusChanged = False
        self.mLabelPropMsg = ""
        self.leftPress = False
        self.mKeyShiftStatus = False
        self.mMouseInBrowser = False
        self.mKeyCtrlStatus = False
        self.initUI()


    def initUI(self):
        self.initMenu()
        self.initBrowser()
        self.initImageWindow()
        self.initLable()
        self.initTimer()

    def initLable(self):
        self.mLabel = QLabel(self)
        font = QFont()
        palette = QPalette()
        palette.setColor(QPalette.WindowText, Qt.white)
        font.setPixelSize(18)
        font.setFamily("KaiTi")
        # font.setBold(True)
        font.setItalic(True)
        self.mLabelMetrics = QFontMetrics(font)
        self.mLabel.setFont(font)
        # self.mLabel.setAttribute(Qt.WA_TranslucentBackground, False)
        self.mLabel.setStyleSheet("background:rgb(50,50,50)")
        self.mLabel.setWordWrap(True)
        self.mLabel.setPalette(palette)
        self.mLabel.show()
        self.mLabel.setVisible(False)
        self.mLabelStatus = False

    def initTimer(self):
        self.timer= QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.timeSlot)

    def initMenu(self):
        Utils.LogD(self.TAG, "initMenu+")
        openImageFolderAct = QAction("open", self)
        openImageFolderAct.setStatusTip("Select Xml file")
        openImageFolderAct.setShortcut("Ctrl+O")

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('File')
        fileMenu.addAction(openImageFolderAct)
        fileMenu.triggered[QAction].connect(self.processtrigger)

        aboutAct = QAction("about", self)
        aboutAct.setStatusTip("about")
        helpMenu = menubar.addMenu('Help')
        helpMenu.addAction(aboutAct)
        helpMenu.triggered[QAction].connect(self.processHelp)

        Utils.LogD(self.TAG, ("%s: - " % (sys._getframe().f_code.co_name)))

    def processtrigger(self,q):
        # directory1 = QFileDialog.getExistingDirectory(self,
        #                                               "选取文件夹",
        #                                               "./")  # 起始路径
        # rootdir = r"C:\Users\lx\Documents"
        rootdir = r"D:\workspace\tools\PipelineTools"
        self.mFileName, self.mFiletype = QFileDialog.getOpenFileName(self,
                                                          "选取文件",
                                                          rootdir,
                                                          "Xml Files (*.xml);;All Files (*)")

        # files, ok1 = QFileDialog.getOpenFileNames(self,
        #                                           "多文件选择",
        #                                           "./",
        #                                           "All Files (*);;Text Files (*.txt)")
        #
        # fileName2, ok2 = QFileDialog.getSaveFileName(self,
        #                                              "文件保存",
        #                                              "./",
        #                                              "All Files (*);;Text Files (*.txt)")
        if len(self.mFileName) > 0 and str(self.mFileName).find("xml") > 0:
            self.imageBrowser.clear()
            self.initUseCase()

    def processHelp(self):
        version = "V1.3"
        update = "2021.12.22"
        aboutInfo = '                                                       \n'\
                    '    版本信息：%s                \n'\
                    '    版权所有@Jianlin           \n'\
                    '    问题反馈：a185531353@qq.com \n'\
                    '    最后更新时间：%s \n' % (version, update)
        QMessageBox.about(self, 'About', aboutInfo)

    def initUseCase(self):
        Utils.LogD(self.TAG, ("%s: + " % (sys._getframe().f_code.co_name)))
        Utils.LogI(self.TAG, ("Select file is " + self.mFileName))
        # 创建跟节点
        self.mUseCase = UseCaseDes(str(self.mFileName))
        self.mUseCase.useCaseTranslation()
        self.updateTreeWidget()
        # self.root1 = QTreeWidgetItem(self.imageBrowser)
        # self.root1.setText(0, '2UseCase')
        # 默认展开
        # self.imageBrowser.expandAll()
        Utils.LogD(self.TAG, ("%s: - " % (sys._getframe().f_code.co_name)))

    def initBrowser(self):
        '''
            @Func:左侧树形选择栏
        '''
        Utils.LogD(self.TAG, ("%s: + " % (sys._getframe().f_code.co_name)))
        # self.imageBrowser = QListWidget(self)
        self.mImageBrowserPos = QPoint(0, 26)
        self.imageBrowser = QTreeWidget(self)
        # self.mImageBrowserWidth = 400
        # tree.setFixedSize(self.width(), self.height())  # 设置控件尺寸
        self.imageBrowser.setColumnCount(1)
        self.imageBrowser.setHeaderLabels(['name'])
        # self.imageBrowser.setColumnWidth(0, 120)
        # self.imageBrowser.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.imageBrowser.setMinimumSize(20, 0)
        # self.imageBrowser.resize(self.mImageBrowserWidth, 0)
        self.imageBrowser.move(self.mImageBrowserPos)
        self.imageBrowser.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

        self.imageBrowser.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.imageBrowser.header().setStretchLastSection(False)
        self.imageBrowser.header().setSectionResizeMode(QHeaderView.Stretch)
        self.imageBrowser.setHeaderHidden(True)
        # self.imageBrowser.setMouseTracking(True)
        self.imageBrowser.raise_()
        # self.setCentralWidget(self.imageBrowser)
        # self.centralWidget().setMouseTracking(True)
        # root1.setIcon(0, QIcon('文件夹.png'))
        # self.child1.setIcon(0, QIcon('文件.png'))
        self.imageBrowser.setStyleSheet("background-color: rgb(50, 50, 50);")
        self.imageBrowser.setFrameShape(QFrame.Box)
        self.imageBrowser.setFrameShadow(QFrame.Raised)
        self.imageBrowser.doubleClicked.connect(self.onClicked)

        Utils.LogD(self.TAG, ("%s: - " % (sys._getframe().f_code.co_name)))

    def onClicked(self, modelIndex):
        item = self.imageBrowser.currentItem()
        self.mFontSize = 24
        if item.parent() != None and item.parent().text(0) != "UseCase":
            # QMessageBox.information(self, 'Tips', 'Select useCase %s pipeline is %s' % (item.parent().text(0), item.text(0)))
            self.mSelectPipeline = self.mUseCase.buildPipeline(item.parent().text(0), item.text(0), self.mCanvasCenterPos, self.mFontSize, self)
            self.mSelectPipeline.print()
            self.clearWork()
            self.initCanvas()

    def updateTreeWidget(self):
        '''
            @Func:给左侧树形选择栏添加item
        '''
        for useCase in self.mUseCase.getPipelineMap().keys():
            root = QTreeWidgetItem(self.imageBrowser)
            root.setText(0, useCase)
            root.setForeground(0, QColor(200, 200, 200))
            for pipeline in self.mUseCase.getPipelineMap().get(useCase):
                pipelineItem = QTreeWidgetItem(root)
                pipelineItem.setText(0, pipeline.getPipelineName())
                pipelineItem.setForeground(0, QColor(200, 200, 200))

    def initImageWindow(self):
        '''
            @Func:初始化最下层Qwidget，以及承载NodePainter的Canvas
        '''
        Utils.LogD(self.TAG, ("%s: + " % (sys._getframe().f_code.co_name)))
        self.imageWindow = QWidget(self)
        self.mImageWindowWidth = 4000
        self.mImageWindowHeight = 3000
        self.mImageWindowPos = QPoint(0, 0)
        self.imageWindow.resize(self.mImageWindowWidth, self.mImageWindowHeight)
        self.imageWindow.move(self.mImageWindowPos)
        self.imageWindow.setStyleSheet("background-color: rgb(50, 50, 50);")
        self.imageWindow.lower()

        self.mCanvas = CanvasImage(self.imageWindow, QColor(200, 1, 1))
        self.mCanvasWidth = 8000
        self.mCanvasHeight = 8000
        self.mCanvasCenterPos = QPoint(1000, 2000)
        self.mCanvasWidthBottomPos = QPoint(-(self.mCanvasCenterPos.x()) + 550, -(self.mCanvasCenterPos.y()) + 300)
        self.mCanvas.resize(self.mCanvasWidth, self.mCanvasHeight)
        self.mCanvas.move(self.mCanvasWidthBottomPos)
        self.mCanvas.setPalette(QPalette(Qt.white))
        self.mCanvas.setAutoFillBackground(True)
        self.mCanvas.setStyleSheet("background-color: rgb(50, 50, 50);")
        self.mCanvas.show()
        Utils.LogD(self.TAG, ("%s: - " % (sys._getframe().f_code.co_name)))
        # tempLayout = QHBoxLayout()
        # tempLayout.addWidget(self.mCanvas)
        # self.mBottomCanvas.setLayout(tempLayout)

    # def initLayout(self):
    #     layoutH = QHBoxLayout()
    #     layoutH.addWidget(self.imageBrowser, 1)
    #     layoutH.addWidget(self.imageWindow, 9)
    #     # layoutV = QVBoxLayout()
    #     # layoutV.addWidget(self.)
    #     # layoutH.setSize
    #     self.setLayout(layoutH)

    # def getVLayoutInstance(self, level):
    #     Utils.LogD(self.TAG, ("%s:+ " % (sys._getframe().f_code.co_name)))
    #     if self.mVlayoutInstalMap.get(level) == None:
    #         layout = QVBoxLayout()
    #         # layout.addStretch(50)
    #         # layout.setContentsMargins(20,20,20,20)
    #         temp = {level: layout}
    #         Utils.LogD(self.TAG, ("level is %s, id %d" % (level, id(layout))))
    #         self.mVlayoutInstalMap.update(temp)
    #         Utils.LogD(self.TAG, ("layout ", self.mVlayoutInstalMap.get(level)))
    #     Utils.LogD(self.TAG, ("%s:-" % (sys._getframe().f_code.co_name)))
    #     return self.mVlayoutInstalMap.get(level)

    def initCanvas(self):
        '''
            @Func:在Canvas上绘制NodePainter
        '''
        Utils.LogD(self.TAG, ("%s: +" % (sys._getframe().f_code.co_name)))
        colorList = [QColor(252, 230, 202), QColor(200, 0, 0), QColor(255, 255, 0), QColor(64, 224, 205), QColor(255, 0, 255),
                     QColor(0, 255, 255), QColor(255, 153, 18), QColor(156, 102, 31), QColor(202, 235, 216), QColor(3, 168, 158),
                     QColor(0, 199, 104), QColor(199, 97, 20), QColor(153, 51, 250), QColor(128, 42, 42), QColor(255, 125, 64),
                     QColor(107, 142, 35), QColor(85, 102, 0), QColor(0, 0, 255), QColor(250, 240, 230), QColor(150, 100, 0)]
        i = 0
        for node in self.mSelectPipeline.getNodeList():
            # Utils.LogD(self.TAG,
            #            ("%s: " % (sys._getframe().f_code.co_name), node.getNodeName() + node.getNodeInstanceId(),
            #             "color", colorList[i].getRgb()))
            if node.getNodePos() != None:
                node.setColor(colorList[i])
                fontSize = node.getNodeFontSize() if node.getNodeFontSize() is not None else self.mFontSize
                node.setNodeFont(fontSize)
                nodePainter = NodePainter(self.mCanvas, node, fontSize)
                node.calPortPos()
                nodePainter.move(node.getNodePos())
                nodePainter.lower()
                nodePainter.show()
                nodePainter.update()
                nodePainter.connectParentSlot(self.recieveChildMsgSlot)
                self.mSignal.connect(nodePainter.receviceParentMsg)
                self.mNodePainterList.append(nodePainter)
                i += 1
                if i >= len(colorList) - 1:
                    i = 0
            else:
                Utils.LogE(self.TAG, ("%s: - " % (sys._getframe().f_code.co_name), node.getNodeName() +
                                      node.getNodeInstanceId() + " pos is none!"))
                exit(0)

        self.mCanvas.initPainterInstance(self.mSelectPipeline.getNodeList())
        self.mCanvas.setPortLinkDes(self.mSelectPipeline.getPortLink())
        self.mCanvas.update()
        self.mCanvas.move(self.mCanvasWidthBottomPos)
        Utils.LogD(self.TAG, ("%s: - " % (sys._getframe().f_code.co_name)))

    def clearWork(self):
        for nodePainter in self.mNodePainterList:
            nodePainter.close()
        self.mNodePainterList.clear()

        self.mEnlargeSum = 0

    def isSelectNode(self, node, currentPos):
        nodePos = node.getNodePos()
        nodeSize = node.getNodeSize()
        if nodePos is not None and nodeSize is not None:
            if nodePos.x() < currentPos.x() < nodePos.x() + nodeSize.width() and \
                    nodePos.y() < currentPos.y() < nodePos.y() + nodeSize.height():
                return True
        return False

    def recieveMsg(self, item):
        QMessageBox.information(self, 'QListView', '你选择了：' + self.list[item.row()])

    def recieveChildMsgSlot(self, msg):
        '''
        @Func:注册到nodePainter中的额槽函数，接收nodePainter鼠標press事件
              目前的作用是在mainWindow中用来解决鼠标悬停显示prop与鼠标按压拖拽node功能的
        '''
        msgType, msgValue = msg.getMsg()
        if msgType == MsgType.LeftButton:
            self.leftPress = msgValue
            if self.leftPress == False:
                self.mCanvas.update()
        elif msgType == MsgType.WheelMouse:
            self.mCanvas.update()

    def mousePressEvent(self, event):
        '''
            @Func:重载一下鼠标按下事件(单击)
        '''
        if event.button() == Qt.LeftButton:
            if self.mImageBrowserChange == False:
                Utils.LogI(self.TAG, ("mousePressEvent...", self.m_drag))
                self.m_drag = True
                self.m_DragPosition = event.globalPos() - self.mCanvas.pos()
                self.setCursor(QCursor(Qt.OpenHandCursor))
                event.accept()
                # Utils.LogI(self.TAG, ("recieve mousePressEvent", "event:", event.globalPos(), "canvas:", self.mCanvas.pos()))
            else:
                self.mImageBrowserStart = event.pos()
                # Utils.LogI(self.TAG,
                #            ("recieve mousePressEvent", "self.mImageBrowserStart:", self.mImageBrowserStart))

    def wheelEvent(self, event):
        angle = event.angleDelta() / 8    # 返回QPoint对象，为滚轮转过的数值，单位为1/8度
        angleX = angle.x()                # 水平滚过的距离(此处用不上)
        angleY = angle.y()                # 竖直滚过的距离
        step = angleY * 2.5
        if self.mMouseInBrowser is False and self.mKeyCtrlStatus is False:
            if self.mKeyShiftStatus:
                self.mCanvas.move(self.mCanvas.pos() + QPoint(step, 0))
            else:
                self.mCanvas.move(self.mCanvas.pos() + QPoint(0, step))

        if angleY > 0:
            pass
        else:                                                                  # 滚轮下滚
            pass

    def updateBrowserSize(self):
        self.imageBrowser.resize(self.mImageBrowserWidth, self.height() - 15)
        self.mImageBrowserWidth = self.imageBrowser.geometry().width()

    def mouseMoveEvent(self, event):
        if Qt.LeftButton and self.m_drag:
            pos = event.globalPos()
            self.mCanvas.move(pos - self.m_DragPosition)
            event.accept()
        elif Qt.LeftButton and self.mImageBrowserChange:
            self.mImageBrowserWidth = event.pos().x()
            self.updateBrowserSize()


    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.m_drag = False
            self.mImageBrowserChange = False
            self.setCursor(QCursor(Qt.ArrowCursor))
            # self.updateBrowserSize()
            # Utils.LogD(self.TAG, "mouseReleaseEvent")

    def getmImageBrowserWidth(self):
        return self.mImageBrowserWidth

    def showNodePorp(self, pos):
        num = 0
        propMsg = ""
        enable = False
        if self.mImageBrowserChange is False and self.mSelectPipeline is not None:
            canvasRelativePos = pos - self.mCanvas.pos()
            for node in self.mSelectPipeline.getNodeList():
                # Utils.LogI(self.TAG,
                #            ("pos: ", pos, "canvasRelativePos:", canvasRelativePos, "NodeName:", node.getNodeName(),
                #             "NodePos", node.getNodePos(), "move:", node.getNodePos() + self.mCanvas.pos()))
                if self.isSelectNode(node, canvasRelativePos):
                    nodePropList = node.getNodeProp()
                    for nodeProp in nodePropList:
                        propMsg += "------------------------------\n" + \
                                   "NodePropertyName:" + nodeProp[0] + "\n" + \
                                   "NodePropertyId:" + nodeProp[1] + "\n" + \
                                   "NodePropertyDataType:" + nodeProp[2] + "\n" + \
                                   "NodePropertyValue:" + nodeProp[3] + "\n"

                        num += 6

                    if len(propMsg) > 20:
                        propMsg += "------------------------------\n"
                        self.mLabelPropMsg = propMsg
                        self.mLabelMovePos = node.getNodePos() + self.mCanvas.pos() - QPoint(0, self.mLabelMetrics.height() * num)
                        enable = True
                        if self.mTimerStartFlag is False:
                            # Utils.LogI(self.TAG, ("start time...", time.time()))
                            self.timer.start(800)
                            # self.timer.singleShot(1200, self.timeSlot)
                            self.mTimerStartFlag = True

            if enable is True and self.mLabelStatus is False:
                self.mlabelStatusChanged = True
                self.mLabelStatus = True
            elif enable is False and self.mLabelStatus is True:
                self.mlabelStatusChanged = True
                self.mLabelStatus = False
            elif enable is False:
                self.timer.stop()
                self.mTimerStartFlag = False

        if self.mlabelStatusChanged:
            if self.mLabelStatus is True and self.mLabelMovePos is not None:
                pass
            else:
                self.mLabel.setText("")
                self.mLabel.setVisible(False)

    def timeSlot(self):
        # self.isTimeEnd = True
        self.mTimerStartFlag = False

        if self.mlabelStatusChanged:
            Utils.LogI(self.TAG, ("run time...", self.m_drag))
            if self.mLabelStatus is True and self.mLabelMovePos is not None and self.leftPress is False:
                self.mLabel.setText(self.mLabelPropMsg)
                self.mLabel.adjustSize()
                self.mLabel.move(self.mLabelMovePos)
                self.mLabel.setVisible(True)
                self.mLabel.raise_()
            else:
                self.mLabel.setText("")
                self.mLabel.setVisible(False)

        self.mLabelPropMsg = ""
        self.mLabelMovePos = None
        self.mlabelStatusChanged = False
        # Utils.LogI(self.TAG, ("run time...", time.time()))

    def eventFilter(self, object, event):
        '''
            @Func:处理QEvent.HoverMove事件，鼠标指针处于树形结构的选择框附件时，变为左右箭头
        '''
        if event.type() == QEvent.HoverMove:
            pos = event.pos()
            if pos.x() < self.mImageBrowserWidth:
                self.mMouseInBrowser = True
            else:
                self.mMouseInBrowser = False
            if pos.x() < self.mImageBrowserWidth + 10 and pos.x() > self.mImageBrowserWidth - 10 \
                    and self.leftPress is False:
                self.setCursor(Qt.SizeHorCursor)
                self.mImageBrowserChange = True
                msg = ComMsg(MsgType.HoverMove, True)
                self.mSignal.emit(msg)
            else:
                self.setCursor(Qt.ArrowCursor)
                self.mImageBrowserChange = False
                msg = ComMsg(MsgType.HoverMove, False)
                self.mSignal.emit(msg)
            self.showNodePorp(pos)

        return False

    def keyPressEvent(self, keyEvent):
        if keyEvent.key() == Qt.Key_Shift:
            self.mKeyShiftStatus = True
            # keyEvent.accept()
        elif keyEvent.key() == Qt.Key_Control:
            self.mKeyCtrlStatus = True
            msg = ComMsg(MsgType.KeyCtrl, True)
            self.mSignal.emit(msg)

    def keyReleaseEvent(self, keyEvent):
        if keyEvent.key() == Qt.Key_Shift:
            self.mKeyShiftStatus = False
            # keyEvent.accept()
        elif keyEvent.key() == Qt.Key_Control:
            self.mKeyCtrlStatus = False
            msg = ComMsg(MsgType.KeyCtrl, False)
            self.mSignal.emit(msg)

    def resizeEvent(self, event):
        self.updateBrowserSize()
        # Utils.LogD(self.TAG,
        #            ("%s: - self.mImageBrowserWidth %d" % (sys._getframe().f_code.co_name, self.mImageBrowserWidth)))
