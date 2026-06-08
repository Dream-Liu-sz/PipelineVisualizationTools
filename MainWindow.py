from PyQt5.Qt import QPoint, QSize
from PyQt5.Qt import QMessageBox
from PyQt5.Qt import QMainWindow
from PyQt5.QtCore import Qt, QEvent, QTimer, pyqtSignal
from PyQt5.Qt import QPalette
from PyQt5.Qt import QIcon
from PyQt5.Qt import QAction
from PyQt5.QtGui import QColor, QCursor, QFont, QFontMetrics, QPalette, QPixmap, QPainter, QIcon, QPen
from PyQt5.QtWidgets import QTreeWidget, QAbstractItemView, QHeaderView, QFrame, QTreeWidgetItem, QWidget, QFileDialog, \
    QLabel, QSplitter, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QSizePolicy

from CanvasWidget import CanvasImage
from NodePainter import NodePainter
from Utils import Utils
from Utils import ComMsg
from Utils import MsgType
from UseCase import UseCaseDes
from ui_theme import COLORS, app_stylesheet, font, node_color, tooltip_stylesheet
import sys
import ctypes

import resource
# import time

class MainWindow(QMainWindow):
    TAG = "MainWindow"
    DEFAULT_PIPELINE_ZOOM = 0.62
    PORT_LABEL_MIN_ZOOM = 0.78
    CANVAS_MAJOR_GRID = 160
    EXPLORER_MIN_WIDTH = 220
    INSPECTOR_DEFAULT_WIDTH = 294
    mSignal = pyqtSignal(ComMsg)
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setWindowTitle("Pipeline Visualization tools")
        self.resize(1280, 720)
        # self.setCentralWidget(self.mCanvas)
        # self.func()
        self.mImageBrowserWidth = self.EXPLORER_MIN_WIDTH
        self.mVlayoutInstalMap = dict()
        self.mNodePainterList = []
        self.mDrawLinePainterList = []
        self.mSelectPipeline = None
        self.mEnlargeSum = 0
        self.m_drag = False
        self.mLabel = None
        self.setAttribute(Qt.WidgetAttribute.WA_Hover);
        self.installEventFilter(self)
        self.setStyleSheet(app_stylesheet())
        self.setPalette(QPalette(QColor(COLORS["bg"])))
        self.setAutoFillBackground(True)
        self.setWindowIcon(QIcon(":res/logo.ico"))
        self.applyNativeDarkTitleBar()
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
        self.mJsonOpend = False;
        self.mImageBrowserChange = False
        self.mZoomScale = 1.0
        self.mStatusText = None
        self.mCurrentPipelineName = ""
        self.mCurrentFileSummary = "No file loaded"
        self.mSelectedNode = None
        self.mSelectedLink = None
        self.mInspectorMode = "pipeline"
        self.mBaseLayout = {}
        self.mPipelineBaseLayoutMap = {}
        self.mPipelineCurrentLayoutMap = {}
        self.mExplorerVisible = True
        self.mLastExplorerWidth = self.mImageBrowserWidth
        self.initUI()
        QTimer.singleShot(0, self.applyDefaultPanelWidths)

    def applyNativeDarkTitleBar(self):
        if sys.platform != "win32":
            return
        try:
            hwnd = int(self.winId())
            value = ctypes.c_int(1)
            # DWMWA_USE_IMMERSIVE_DARK_MODE is 20 on current Windows 10/11,
            # with 19 used by older builds.
            for attr in (20, 19):
                ctypes.windll.dwmapi.DwmSetWindowAttribute(
                    ctypes.c_void_p(hwnd),
                    ctypes.c_int(attr),
                    ctypes.byref(value),
                    ctypes.sizeof(value)
                )
        except Exception:
            pass


    def initUI(self):
        self.initMenu()
        self.initWorkspace()
        self.initBrowser()
        self.initImageWindow()
        self.initLable()
        self.initTimer()
        self.updateCanvasContext()

    def initWorkspace(self):
        self.mRootWidget = QWidget(self)
        self.setCentralWidget(self.mRootWidget)

        rootLayout = QVBoxLayout(self.mRootWidget)
        rootLayout.setContentsMargins(14, 12, 14, 8)
        rootLayout.setSpacing(10)

        self.mSplitter = QSplitter(Qt.Horizontal, self.mRootWidget)
        self.mSplitter.setChildrenCollapsible(False)
        rootLayout.addWidget(self.mSplitter)

        self.mLeftPanel = QWidget(self.mSplitter)
        self.mLeftPanel.setObjectName("leftPanel")
        self.mLeftPanel.setMinimumWidth(self.EXPLORER_MIN_WIDTH)
        self.mLeftPanel.setMaximumWidth(460)
        self.mLeftLayout = QVBoxLayout(self.mLeftPanel)
        self.mLeftLayout.setContentsMargins(0, 0, 0, 0)
        self.mLeftLayout.setSpacing(10)

        navTitle = QLabel("Pipeline Explorer", self.mLeftPanel)
        navTitle.setObjectName("panelTitle")
        navHint = QLabel("Search and double-click a pipeline to render", self.mLeftPanel)
        navHint.setObjectName("panelHint")
        self.mSearchEdit = QLineEdit(self.mLeftPanel)
        self.mSearchEdit.setObjectName("treeSearch")
        self.mSearchEdit.setPlaceholderText("Filter use cases or pipelines")
        self.mSearchEdit.textChanged.connect(self.filterTree)

        self.mLeftLayout.addWidget(navTitle)
        self.mLeftLayout.addWidget(navHint)
        self.mLeftLayout.addWidget(self.mSearchEdit)

        self.mRightPanel = QWidget(self.mSplitter)
        self.mRightPanel.setObjectName("rightPanel")
        self.mRightLayout = QVBoxLayout(self.mRightPanel)
        self.mRightLayout.setContentsMargins(10, 0, 0, 0)
        self.mRightLayout.setSpacing(10)

        self.mContextBar = QWidget(self.mRightPanel)
        self.mContextLayout = QHBoxLayout(self.mContextBar)
        self.mContextLayout.setContentsMargins(0, 0, 0, 0)
        self.mContextLayout.setSpacing(10)

        titleColumn = QWidget(self.mContextBar)
        titleLayout = QVBoxLayout(titleColumn)
        titleLayout.setContentsMargins(0, 0, 0, 0)
        titleLayout.setSpacing(2)
        self.mContextTitle = QLabel("Ready to visualize", titleColumn)
        self.mContextTitle.setObjectName("contextTitle")
        self.mContextSubtitle = QLabel("Open XML or JSON, then choose a pipeline from the explorer.", titleColumn)
        self.mContextSubtitle.setObjectName("contextSubtle")
        titleLayout.addWidget(self.mContextTitle)
        titleLayout.addWidget(self.mContextSubtitle)

        self.mMetricNodes = QLabel("Nodes 0", self.mContextBar)
        self.mMetricNodes.setObjectName("metricPill")
        self.mMetricLinks = QLabel("Links 0", self.mContextBar)
        self.mMetricLinks.setObjectName("metricPill")
        self.mMetricZoom = QLabel("Zoom 100%", self.mContextBar)
        self.mMetricZoom.setObjectName("metricPill")
        self.mFitButton = QPushButton("Center View", self.mContextBar)
        self.mFitButton.setObjectName("toolbarButton")
        self.mFitButton.clicked.connect(self.centerCanvas)
        self.mResetViewButton = QPushButton("Reset View", self.mContextBar)
        self.mResetViewButton.setObjectName("toolbarButton")
        self.mResetViewButton.clicked.connect(self.resetPipelineView)

        self.mContextLayout.addWidget(titleColumn, 1)
        self.mContextLayout.addWidget(self.mMetricNodes)
        self.mContextLayout.addWidget(self.mMetricLinks)
        self.mContextLayout.addWidget(self.mMetricZoom)
        self.mContextLayout.addWidget(self.mFitButton)
        self.mContextLayout.addWidget(self.mResetViewButton)
        self.mRightLayout.addWidget(self.mContextBar)

        self.mContentSplitter = QSplitter(Qt.Horizontal, self.mRightPanel)
        self.mContentSplitter.setChildrenCollapsible(False)

        self.mCanvasViewport = QWidget(self.mContentSplitter)
        self.mCanvasViewport.setObjectName("canvasViewport")
        self.mCanvasViewport.setMinimumSize(480, 360)
        self.mCanvasViewport.setMouseTracking(True)
        self.mCanvasViewport.setAttribute(Qt.WidgetAttribute.WA_Hover)
        self.mCanvasViewport.installEventFilter(self)
        self.mInspectorDefaultWidth = self.INSPECTOR_DEFAULT_WIDTH
        self.initInspectorDrawer()
        self.mContentSplitter.addWidget(self.mCanvasViewport)
        self.mContentSplitter.addWidget(self.mInspector)
        self.mContentSplitter.setSizes([900, self.mInspectorDefaultWidth])
        self.mInspector.hide()
        self.mRightLayout.addWidget(self.mContentSplitter, 1)

        self.mSplitter.addWidget(self.mLeftPanel)
        self.mSplitter.addWidget(self.mRightPanel)
        self.mSplitter.setCollapsible(0, True)
        self.mSplitter.setCollapsible(1, False)
        self.mImageBrowserWidth = self.EXPLORER_MIN_WIDTH
        self.mLastExplorerWidth = self.mImageBrowserWidth
        self.mSplitter.setSizes([self.mImageBrowserWidth, 1060])
        self.mSplitter.splitterMoved.connect(self.onSplitterMoved)

        self.mStatusText = QLabel("Drag canvas to pan | Right-click background: pipeline info | Wheel: vertical | Shift+Wheel: horizontal | Ctrl+Wheel: zoom")
        self.statusBar().addPermanentWidget(self.mStatusText, 1)

    def initInspectorDrawer(self):
        self.mInspector = QFrame(self.mContentSplitter)
        self.mInspector.setObjectName("inspectorDrawer")
        self.mInspector.setMinimumWidth(200)
        self.mInspector.resize(self.mInspectorDefaultWidth, max(240, self.mCanvasViewport.height()))
        self.mInspectorLayout = QVBoxLayout(self.mInspector)
        self.mInspectorLayout.setContentsMargins(14, 14, 14, 14)
        self.mInspectorLayout.setSpacing(8)

        inspectorHeader = QWidget(self.mInspector)
        inspectorHeaderLayout = QHBoxLayout(inspectorHeader)
        inspectorHeaderLayout.setContentsMargins(0, 0, 0, 0)
        inspectorHeaderLayout.setSpacing(8)
        self.mInspectorTitle = QLabel("Pipeline Details", inspectorHeader)
        self.mInspectorTitle.setObjectName("inspectorTitle")
        self.mHideInspectorButton = QPushButton("Hide", inspectorHeader)
        self.mHideInspectorButton.setObjectName("toolbarButton")
        self.mHideInspectorButton.clicked.connect(self.hideInspector)
        inspectorHeaderLayout.addWidget(self.mInspectorTitle, 1)
        inspectorHeaderLayout.addWidget(self.mHideInspectorButton)
        self.mInspectorSubtitle = QLabel("Click a node, link, or background", self.mInspector)
        self.mInspectorSubtitle.setObjectName("inspectorSubtitle")
        self.mInspectorBody = QTreeWidget(self.mInspector)
        self.mInspectorBody.setObjectName("inspectorBody")
        self.mInspectorBody.setColumnCount(2)
        self.mInspectorBody.setHeaderLabels(["Field", "Value"])
        self.mInspectorBody.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.mInspectorBody.header().setSectionResizeMode(1, QHeaderView.Stretch)
        self.mInspectorBody.setFont(font(9, mono=True))

        self.mInspectorLayout.addWidget(inspectorHeader)
        self.mInspectorLayout.addWidget(self.mInspectorSubtitle)
        self.mInspectorLayout.addWidget(self.mInspectorBody, 1)

    def positionInspectorDrawer(self):
        if not hasattr(self, "mInspector"):
            return
        self.mInspector.raise_()

    def initLable(self):
        self.mLabel = QLabel(self)
        palette = QPalette()
        palette.setColor(QPalette.WindowText, QColor(COLORS["text"]))
        label_font = font(10, mono=True)
        self.mLabelMetrics = QFontMetrics(label_font)
        self.mLabel.setFont(label_font)
        # self.mLabel.setAttribute(Qt.WA_TranslucentBackground, False)
        self.mLabel.setStyleSheet(tooltip_stylesheet())
        self.mLabel.setWordWrap(True)
        self.mLabel.setPalette(palette)
        self.mLabel.setMaximumWidth(520)
        self.mLabel.show()
        self.mLabel.setVisible(False)
        self.mLabelStatus = False

    def initTimer(self):
        self.timer= QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.timeSlot)

    def initMenu(self):
        Utils.LogD(self.TAG, "initMenu+")
        openImageFolderAct = QAction("Open XML file", self)
        openImageFolderAct.setStatusTip("Select XML pipeline file")
        openImageFolderAct.setShortcut("Ctrl+O")
        openImageFolderAct.triggered.connect(self.triggerOpenFile)

        openDirImageFolderAct = QAction("Open JSON files", self)
        openDirImageFolderAct.setStatusTip("Select JSON pipeline files")
        openDirImageFolderAct.setShortcut("Ctrl+Alt+O")
        openDirImageFolderAct.triggered.connect(self.triggerOpenFiles)

        menubar = self.menuBar()
        self.mMenuBar = menubar
        menubar.installEventFilter(self)
        self.mExplorerToggleAction = QAction(self.createSidebarToggleIcon(True), "", self)
        self.mExplorerToggleAction.setCheckable(True)
        self.mExplorerToggleAction.setChecked(True)
        self.mExplorerToggleAction.setToolTip("Show or hide pipeline explorer")
        self.mExplorerToggleAction.triggered.connect(self.toggleExplorer)
        menubar.addAction(self.mExplorerToggleAction)

        fileMenu = menubar.addMenu('File')
        fileMenu.addAction(openImageFolderAct)
        fileMenu.addAction(openDirImageFolderAct)

        aboutAct = QAction("About", self)
        aboutAct.setStatusTip("About Pipeline Visualization Tools")
        aboutAct.triggered.connect(self.processHelp)

        tipsAct = QAction("Tips", self)
        tipsAct.setStatusTip("Usage tips")
        tipsAct.triggered.connect(self.showTips)

        helpMenu = menubar.addMenu('Help')
        helpMenu.addAction(aboutAct)

        helpMenu.addAction(tipsAct)

        Utils.LogD(self.TAG, ("%s: - " % (sys._getframe().f_code.co_name)))

    def createSidebarToggleIcon(self, checked):
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing, True)
        stroke = QColor("#B8B8B8" if checked else "#8A8A8A")
        fill = QColor(255, 255, 255, 0)
        painter.setPen(QPen(stroke, 1.4))
        painter.setBrush(fill)
        painter.drawRoundedRect(3, 3, 10, 10, 2, 2)
        painter.drawLine(6, 4, 6, 12)
        painter.end()
        return QIcon(pixmap)

    def triggerOpenFile(self, q):
        # directory1 = QFileDialog.getExistingDirectory(self,
        #                                               "选取文件夹",
        #                                               "./")  # 起始路径
        # rootdir = r"C:\Users\lx\Documents"
        rootdir = r"D:\workspace\tools\PipelineTools"
        self.mFileName, self.mFiletype = QFileDialog.getOpenFileName(self,
                                                          "Open XML pipeline file",
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
            self.mCurrentFileSummary = self.mFileName
            self.initUseCase()

    def triggerOpenFiles(self, q):
        # directory1 = QFileDialog.getExistingDirectory(self,
        #                                               "选取文件夹",
        #                                               "./")  # 起始路径
        # rootdir = r"C:\Users\lx\Documents"
        rootdir = r"Y:\workspace\code\aero_vendor_do\vendor\noth\hardware\camera\src\extened\config\aero\pipelinedescription"
        # folder_path = QFileDialog.getExistingDirectory(self, "选择文件夹", rootdir)

        # self.mFileName, self.mFiletype = QFileDialog.getOpenFileName(self,
        #                                                   "选取文件",
        #                                                   rootdir,
        #                                                   "Xml Files (*.xml);;All Files (*)")

        self.mFileName, self.mFiletype = QFileDialog.getOpenFileNames(self,
                                                                      "Open JSON pipeline files",
                                                                      rootdir,
                                                                      "Json Files (*.json);;All Files (*)")
        #
        # fileName2, ok2 = QFileDialog.getSaveFileName(self,
        #                                              "文件保存",
        #                                              "./",
        #                                              "All Files (*);;Text Files (*.txt)")
        if len(self.mFileName) > 0 and str(self.mFileName).find("json") > 0:
            self.imageBrowser.clear()
            print(self.mFileName)
            self.mCurrentFileSummary = "%d JSON files loaded" % len(self.mFileName)
            self.initAllJsonPipeline()
            self.mJsonOpend = True

    def processHelp(self):
        version = "V3.0"
        update = "2026.5.20"
        aboutInfo = "\n".join([
            "版本信息：%s" % version,
            "版权所有：Jianlin",
            "问题反馈：a185531353@qq.com",
            "最后更新时间：%s" % update,
        ])
        self.showStyledMessage("About", aboutInfo)

    def showTips(self):
        self.showStyledMessage("Tips",
                               "如果遇到导入文件后没有反应\n"
                               "需要导入编译生成的 XML，例如：g_xxx_usecase.xml")

    def showStyledMessage(self, title, message):
        box = QMessageBox(self)
        box.setWindowTitle(title)
        box.setText(message)
        box.setIcon(QMessageBox.Information)
        box.setStandardButtons(QMessageBox.Ok)
        box.setStyleSheet("""
            QMessageBox {
                background-color: #181818;
                color: #F2F2F2;
                font-family: "Microsoft YaHei UI";
            }
            QLabel {
                color: #F2F2F2;
                background: transparent;
            }
            QPushButton {
                color: #E8E8E8;
                background: #242424;
                border: 1px solid #5A5A5A;
                border-radius: 8px;
                padding: 6px 16px;
                min-width: 72px;
            }
            QPushButton:hover {
                background: #2D2D2D;
                border-color: #7A7A7A;
            }
        """)
        box.exec_()

    def initUseCase(self):
        Utils.LogD(self.TAG, ("%s: + " % (sys._getframe().f_code.co_name)))
        Utils.LogI(self.TAG, ("Select file is " + self.mFileName))
        # 创建跟节点
        self.mUseCase = UseCaseDes(str(self.mFileName), "")
        self.mUseCase.useCaseTranslation()
        self.updateTreeWidget()
        self.updateCanvasContext()
        # self.root1 = QTreeWidgetItem(self.imageBrowser)
        # self.root1.setText(0, '2UseCase')
        # 默认展开
        # self.imageBrowser.expandAll()
        Utils.LogD(self.TAG, ("%s: - " % (sys._getframe().f_code.co_name)))

    def initAllJsonPipeline(self):
        Utils.LogD(self.TAG, ("%s: + " % (sys._getframe().f_code.co_name)))

        # 创建跟节点
        self.mUseCase = UseCaseDes(self.mFileName, "NCFJsonUses")
        self.mUseCase.useCaseTranslationJson()
        self.updateTreeWidget()
        self.updateCanvasContext()
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
        self.imageBrowser = QTreeWidget(self.mLeftPanel)
        # self.mImageBrowserWidth = 400
        # tree.setFixedSize(self.width(), self.height())  # 设置控件尺寸
        self.imageBrowser.setColumnCount(1)
        self.imageBrowser.setHeaderLabels(['name'])
        # self.imageBrowser.setColumnWidth(0, 120)
        # self.imageBrowser.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.imageBrowser.setMinimumSize(0, 0)
        # self.imageBrowser.resize(self.mImageBrowserWidth, 0)
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
        self.imageBrowser.setFrameShape(QFrame.NoFrame)
        self.imageBrowser.setFrameShadow(QFrame.Plain)
        self.imageBrowser.doubleClicked.connect(self.onClicked)
        self.mLeftLayout.addWidget(self.imageBrowser, 1)

        Utils.LogD(self.TAG, ("%s: - " % (sys._getframe().f_code.co_name)))

    def onClicked(self, modelIndex):
        item = self.imageBrowser.currentItem()
        self.mFontSize = 24
        if item.parent() != None and item.parent().text(0) != "UseCase":
            # QMessageBox.information(self, 'Tips', 'Select useCase %s pipeline is %s' % (item.parent().text(0), item.text(0)))
            self.mCurrentPipelineName = item.text(0)
            self.mSelectPipeline = self.mUseCase.buildPipeline(item.parent().text(0), item.text(0), self.mCanvasCenterPos, self.mFontSize, self)
            self.mSelectPipeline.print()
            self.clearWork()
            self.initCanvas()
            self.updateCanvasContext()

    def updateTreeWidget(self):
        '''
            @Func:给左侧树形选择栏添加item
        '''
        print(self.mUseCase.getPipelineMap().keys())
        for useCase in self.mUseCase.getPipelineMap().keys():
            root = QTreeWidgetItem(self.imageBrowser)
            root.setText(0, useCase)
            root.setForeground(0, QColor(COLORS["text"]))
            root.setFont(0, font(10, bold=True))
            for pipeline in self.mUseCase.getPipelineMap().get(useCase):
                pipelineItem = QTreeWidgetItem(root)
                pipelineItem.setText(0, pipeline.getPipelineName())
                pipelineItem.setForeground(0, QColor(COLORS["text_muted"]))
                pipelineItem.setFont(0, font(9))
        self.imageBrowser.expandAll()
        self.imageBrowser.collapseAll()
        self.filterTree(self.mSearchEdit.text())

        Utils.LogD(self.TAG, ("%s: - " % (sys._getframe().f_code.co_name)))

    def expandTree(self):
        if self.imageBrowser is not None:
            self.imageBrowser.expandAll()

    def collapseTree(self):
        if self.imageBrowser is not None:
            self.imageBrowser.collapseAll()

    def initImageWindow(self):
        '''
            @Func:初始化最下层Qwidget，以及承载NodePainter的Canvas
        '''
        Utils.LogD(self.TAG, ("%s: + " % (sys._getframe().f_code.co_name)))
        self.imageWindow = QWidget(self.mCanvasViewport)
        self.mImageWindowWidth = max(4000, self.mCanvasViewport.width())
        self.mImageWindowHeight = max(3000, self.mCanvasViewport.height())
        self.mImageWindowPos = QPoint(0, 0)
        self.imageWindow.resize(self.mImageWindowWidth, self.mImageWindowHeight)
        self.imageWindow.move(self.mImageWindowPos)
        self.imageWindow.setStyleSheet("background-color: %s;" % COLORS["bg"])
        self.imageWindow.setMouseTracking(True)
        self.imageWindow.setAttribute(Qt.WidgetAttribute.WA_Hover)
        self.imageWindow.installEventFilter(self)
        self.imageWindow.lower()

        self.mCanvas = CanvasImage(self.imageWindow, QColor(200, 1, 1))
        self.mCanvasWidth = 8000
        self.mCanvasHeight = 8000
        self.mCanvasCenterPos = QPoint(1000, 2000)
        self.mCanvasWidthBottomPos = QPoint(-(self.mCanvasCenterPos.x()) + 550, -(self.mCanvasCenterPos.y()) + 300)
        self.mCanvas.resize(self.mCanvasWidth, self.mCanvasHeight)
        self.mCanvas.move(self.mCanvasWidthBottomPos)
        self.mCanvas.setPalette(QPalette(QColor(COLORS["bg"])))
        self.mCanvas.setAutoFillBackground(True)
        self.mCanvas.setStyleSheet("background-color: %s;" % COLORS["bg"])
        self.mCanvas.setMouseTracking(True)
        self.mCanvas.setAttribute(Qt.WidgetAttribute.WA_Hover)
        self.mCanvas.installEventFilter(self)
        self.mCanvas.linkClicked.connect(self.showLinkDetails)
        self.mCanvas.backgroundClicked.connect(self.showPipelineDetails)
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
        i = 0
        self.mZoomScale = self.DEFAULT_PIPELINE_ZOOM
        self.mBaseLayout.clear()
        self.mSelectedNode = None
        self.mSelectedLink = None
        self.mInspectorMode = "pipeline"
        self.preparePipelineBaseLayout()
        for node in self.mSelectPipeline.getNodeList():
            # Utils.LogD(self.TAG,
            #            ("%s: " % (sys._getframe().f_code.co_name), node.getNodeName() + node.getNodeInstanceId(),
            #             "color", colorList[i].getRgb()))
            if node.getNodePos() != None:
                node.setColor(node_color(i))
                fontSize = node.getNodeFontSize() if node.getNodeFontSize() is not None else self.mFontSize
                node.setNodeFont(fontSize)
                nodePainter = NodePainter(self.mCanvas, node, fontSize, self.mJsonOpend)
                nodePainter.installEventFilter(self)
                node.calPortPos()
                nodePainter.move(node.getNodePos())
                nodePainter.lower()
                nodePainter.show()
                nodePainter.update()
                nodePainter.connectParentSlot(self.recieveChildMsgSlot)
                nodePainter.nodeClicked.connect(self.showNodeDetails)
                self.mSignal.connect(nodePainter.receviceParentMsg)
                self.mNodePainterList.append(nodePainter)
                i += 1
            else:
                Utils.LogE(self.TAG, ("%s: - " % (sys._getframe().f_code.co_name), node.getNodeName() +
                                      node.getNodeInstanceId() + " pos is none!"))
                exit(0)

        self.mCanvas.initPainterInstance(self.mSelectPipeline.getNodeList())
        self.mCanvas.setPortLinkDes(self.mSelectPipeline.getPortLink())
        self.mCanvas.setSelectedLink(None, None)
        self.refreshZoomedLayout()

        max_x = 0
        max_y = 0
        for node in self.mSelectPipeline.getNodeList():
            if node.getNodePos() is not None:
                node_x = node.getNodePos().x() + node.getNodeSize().width() + 200
                node_y = node.getNodePos().y() + node.getNodeSize().height() + 200
                if node_x > max_x:
                    max_x = node_x
                if node_y > max_y:
                    max_y = node_y

        canvas_w = max(self.mCanvasWidth, max_x)
        canvas_h = max(self.mCanvasHeight, max_y)
        self.mCanvas.resize(int(canvas_w), int(canvas_h))

        self.mCanvas.update()
        self.mCanvas.move(self.mCanvasWidthBottomPos)
        self.centerCanvas()
        self.hideInspector()
        Utils.LogD(self.TAG, ("%s: - " % (sys._getframe().f_code.co_name)))

    def preparePipelineBaseLayout(self):
        if self.mSelectPipeline is None:
            return
        pipeline_key = id(self.mSelectPipeline)
        cached_layout = self.mPipelineBaseLayoutMap.get(pipeline_key)
        if cached_layout is None:
            cached_layout = {}
            for node in self.mSelectPipeline.getNodeList():
                if node.getNodePos() is None or node.getNodeSize() is None:
                    continue
                font_size = node.getNodeFontSize() if node.getNodeFontSize() is not None else self.mFontSize
                cached_layout[node] = {
                    "pos": QPoint(node.getNodePos()),
                    "size": QSize(node.getNodeSize()),
                    "font": font_size
                }
            self.mPipelineBaseLayoutMap[pipeline_key] = cached_layout

        restore_layout = self.mPipelineCurrentLayoutMap.get(pipeline_key, cached_layout)
        for node, base in restore_layout.items():
            node.setNodePos(QPoint(base["pos"]))
            node.setNodeSize(QSize(base["size"]))
            node.setNodeFont(base["font"])
            node.calPortPos()
            self.mBaseLayout[node] = {
                "pos": QPoint(base["pos"]),
                "size": QSize(base["size"]),
                "font": base["font"]
            }

    def saveCurrentPipelineLayout(self):
        if self.mSelectPipeline is None or self.mZoomScale <= 0:
            return
        pipeline_key = id(self.mSelectPipeline)
        current_layout = {}
        for node in self.mSelectPipeline.getNodeList():
            pos = node.getNodePos()
            size = node.getNodeSize()
            if pos is None or size is None:
                continue
            current_layout[node] = {
                "pos": QPoint(int(pos.x() / self.mZoomScale), int(pos.y() / self.mZoomScale)),
                "size": QSize(max(1, int(size.width() / self.mZoomScale)),
                              max(1, int(size.height() / self.mZoomScale))),
                "font": max(1, int(node.getNodeFontSize() / self.mZoomScale))
            }
        self.mPipelineCurrentLayoutMap[pipeline_key] = current_layout
        self.mBaseLayout.clear()
        for node, base in current_layout.items():
            self.mBaseLayout[node] = {
                "pos": QPoint(base["pos"]),
                "size": QSize(base["size"]),
                "font": base["font"]
            }

    def resetPipelineView(self):
        if self.mSelectPipeline is None:
            return
        pipeline_key = id(self.mSelectPipeline)
        original_layout = self.mPipelineBaseLayoutMap.get(pipeline_key)
        if original_layout is None:
            return
        self.mPipelineCurrentLayoutMap.pop(pipeline_key, None)
        self.mBaseLayout.clear()
        for node, base in original_layout.items():
            node.setNodePos(QPoint(base["pos"]))
            node.setNodeSize(QSize(base["size"]))
            node.setNodeFont(base["font"])
            node.calPortPos()
            self.mBaseLayout[node] = {
                "pos": QPoint(base["pos"]),
                "size": QSize(base["size"]),
                "font": base["font"]
            }
        self.mZoomScale = self.DEFAULT_PIPELINE_ZOOM
        self.refreshZoomedLayout()
        self.centerCanvas()
        if not self.mInspector.isHidden() and self.mInspectorMode == "pipeline":
            self.showPipelineDetails()

    def clearWork(self):
        for nodePainter in self.mNodePainterList:
            nodePainter.close()
        self.mNodePainterList.clear()

        self.mEnlargeSum = 0

    def filterTree(self, text):
        query = text.strip().lower()
        root_count = self.imageBrowser.topLevelItemCount() if self.imageBrowser is not None else 0
        for root_index in range(root_count):
            root = self.imageBrowser.topLevelItem(root_index)
            root_match = query in root.text(0).lower()
            any_child_visible = False
            for child_index in range(root.childCount()):
                child = root.child(child_index)
                child_match = query in child.text(0).lower()
                visible = not query or root_match or child_match
                child.setHidden(not visible)
                any_child_visible = any_child_visible or visible
            root.setHidden(bool(query) and not root_match and not any_child_visible)

    def onSplitterMoved(self, pos, index):
        self.mImageBrowserWidth = self.mLeftPanel.width()
        if self.mLeftPanel.width() > 0:
            self.mLastExplorerWidth = self.mLeftPanel.width()
            self.mExplorerVisible = True
            self.mExplorerToggleAction.setChecked(True)
            self.mExplorerToggleAction.setIcon(self.createSidebarToggleIcon(True))
        self.updateCanvasViewportSize()

    def applyDefaultPanelWidths(self):
        if self.mExplorerVisible:
            self.mImageBrowserWidth = self.EXPLORER_MIN_WIDTH
            self.mLastExplorerWidth = self.EXPLORER_MIN_WIDTH
            self.mSplitter.setSizes([self.EXPLORER_MIN_WIDTH,
                                     max(600, self.mSplitter.width() - self.EXPLORER_MIN_WIDTH)])
        if self.mInspector.isVisible():
            self.mContentSplitter.setSizes([max(520, self.mContentSplitter.width() - self.mInspectorDefaultWidth),
                                            self.mInspectorDefaultWidth])
        self.updateCanvasViewportSize()

    def toggleExplorer(self):
        self.mExplorerVisible = self.mExplorerToggleAction.isChecked()
        self.mExplorerToggleAction.setIcon(self.createSidebarToggleIcon(self.mExplorerVisible))
        if self.mExplorerVisible:
            width = max(self.EXPLORER_MIN_WIDTH, self.mLastExplorerWidth)
            total = max(self.mSplitter.width(), width + 600)
            self.mLeftPanel.show()
            self.mSplitter.setSizes([width, max(600, total - width)])
        else:
            if self.mLeftPanel.width() > 0:
                self.mLastExplorerWidth = self.mLeftPanel.width()
            self.mLeftPanel.hide()
            self.mSplitter.setSizes([0, max(600, self.mSplitter.width())])
        self.updateCanvasViewportSize()
        self.centerCanvas()

    def updateCanvasViewportSize(self):
        if hasattr(self, "imageWindow"):
            self.imageWindow.resize(max(self.mCanvasViewport.width(), self.mCanvas.width()),
                                    max(self.mCanvasViewport.height(), self.mCanvas.height()))
        self.positionInspectorDrawer()

    def centerCanvas(self):
        if not hasattr(self, "mCanvas"):
            return
        bounds = self.getNodeBounds()
        if bounds is None:
            x = int(self.CANVAS_MAJOR_GRID - self.mCanvasCenterPos.x() * self.mZoomScale)
            y = int(self.mCanvasViewport.height() / 2 - self.mCanvasCenterPos.y() * self.mZoomScale)
        else:
            min_x, min_y, max_x, max_y = bounds
            graph_h = max_y - min_y
            x = int(self.CANVAS_MAJOR_GRID - min_x)
            y = int((self.mCanvasViewport.height() - graph_h) / 2 - min_y)
        self.mCanvas.move(QPoint(x, y))
        self.mCanvas.update()

    def getNodeBounds(self):
        if self.mSelectPipeline is None:
            return None
        min_x = None
        min_y = None
        max_x = None
        max_y = None
        for node in self.mSelectPipeline.getNodeList():
            pos = node.getNodePos()
            size = node.getNodeSize()
            if pos is None or size is None:
                continue
            node_min_x = pos.x()
            node_min_y = pos.y()
            node_max_x = pos.x() + size.width()
            node_max_y = pos.y() + size.height()
            min_x = node_min_x if min_x is None else min(min_x, node_min_x)
            min_y = node_min_y if min_y is None else min(min_y, node_min_y)
            max_x = node_max_x if max_x is None else max(max_x, node_max_x)
            max_y = node_max_y if max_y is None else max(max_y, node_max_y)
        if min_x is None:
            return None
        return min_x, min_y, max_x, max_y

    def updateCanvasContext(self):
        node_count = 0
        link_count = 0
        if self.mSelectPipeline is not None:
            node_count = len(self.mSelectPipeline.getNodeList())
            for outputs in self.mSelectPipeline.getPortLink().values():
                link_count += len(outputs)

        title = self.mCurrentPipelineName if self.mCurrentPipelineName else "Ready to visualize"
        self.mContextTitle.setText(title)
        self.mContextSubtitle.setText(self.mCurrentFileSummary)
        self.mMetricNodes.setText("Nodes %d" % node_count)
        self.mMetricLinks.setText("Links %d" % link_count)
        self.mMetricZoom.setText("Zoom %d%%" % int(self.mZoomScale * 100))

    def refreshZoomedLayout(self):
        if self.mSelectPipeline is None or len(self.mNodePainterList) == 0:
            return
        show_port_labels = self.mZoomScale >= self.PORT_LABEL_MIN_ZOOM
        for nodePainter in self.mNodePainterList:
            node = nodePainter.mNode
            base = self.mBaseLayout.get(node)
            if base is None:
                continue
            pos = base["pos"]
            size = base["size"]
            next_pos = QPoint(int(pos.x() * self.mZoomScale), int(pos.y() * self.mZoomScale))
            next_size = QSize(max(90, int(size.width() * self.mZoomScale)),
                              max(54, int(size.height() * self.mZoomScale)))
            next_font = max(9, int(base["font"] * self.mZoomScale))
            node.setNodePos(next_pos)
            node.setNodeSize(next_size)
            node.setNodeFont(next_font)
            node.calPortPos()
            nodePainter.move(next_pos)
            nodePainter.resize(next_size)
            nodePainter.setFontSize(next_font)
            nodePainter.setShowPortLabels(show_port_labels)
            nodePainter.update()

        max_x = self.mCanvasWidth
        max_y = self.mCanvasHeight
        for node in self.mSelectPipeline.getNodeList():
            if node.getNodePos() is not None and node.getNodeSize() is not None:
                max_x = max(max_x, node.getNodePos().x() + node.getNodeSize().width() + 220)
                max_y = max(max_y, node.getNodePos().y() + node.getNodeSize().height() + 220)
        self.mCanvas.resize(max_x, max_y)
        self.updateCanvasViewportSize()
        self.mCanvas.update()
        self.updateCanvasContext()

    def applyCanvasZoom(self, angle_y, anchor_global_pos=None):
        if self.mSelectPipeline is None or len(self.mNodePainterList) == 0:
            return
        factor = 1.08 if angle_y > 0 else 0.925
        old_zoom = self.mZoomScale
        next_zoom = max(0.55, min(1.9, self.mZoomScale * factor))
        if abs(next_zoom - self.mZoomScale) < 0.001:
            return

        anchor_parent_pos = None
        anchor_canvas_pos = None
        if anchor_global_pos is not None and self.mCanvas.parentWidget() is not None:
            anchor_parent_pos = self.mCanvas.parentWidget().mapFromGlobal(anchor_global_pos)
            anchor_canvas_pos = anchor_parent_pos - self.mCanvas.pos()

        self.mZoomScale = next_zoom
        self.refreshZoomedLayout()
        if anchor_parent_pos is not None and anchor_canvas_pos is not None and old_zoom > 0:
            ratio = self.mZoomScale / old_zoom
            next_canvas_pos = anchor_parent_pos - QPoint(int(anchor_canvas_pos.x() * ratio),
                                                         int(anchor_canvas_pos.y() * ratio))
            self.mCanvas.move(next_canvas_pos)
            self.mCanvas.update()
        if self.mInspector.isHidden():
            return
        if self.mInspectorMode == "node" and self.mSelectedNode is not None:
            self.showNodeDetails(self.mSelectedNode)
        elif self.mInspectorMode == "link" and self.mSelectedLink is not None:
            self.showLinkDetails(self.mSelectedLink[0], self.mSelectedLink[1])

    def findNodeForPort(self, port):
        if self.mSelectPipeline is None or port is None:
            return None
        for node in self.mSelectPipeline.getNodeList():
            if self.mSelectPipeline.matchNodePort(node, port):
                return node
        return None

    def formatNodeName(self, node):
        if node is None:
            return "Unknown"
        return "%s_%s" % (node.getNodeName(), str(node.getNodeInstanceId()))

    def formatPort(self, port):
        if port is None:
            return "Unknown"
        return "%s_%s (nodeId=%s, instanceId=%s)" % (
            str(port.getPortName()), str(port.getPortId()),
            str(port.getNodeId()), str(port.getNodeInstanceId()))

    def setSelectedNode(self, selected_node):
        self.mSelectedNode = selected_node
        for nodePainter in self.mNodePainterList:
            nodePainter.setSelected(nodePainter.mNode is selected_node)

    def ensureInspectorVisible(self):
        if not self.mInspector.isVisible():
            self.mInspector.show()
            self.mContentSplitter.setSizes([max(520, self.mContentSplitter.width() - self.mInspectorDefaultWidth),
                                            self.mInspectorDefaultWidth])
        self.mInspector.raise_()

    def hideInspector(self):
        if hasattr(self, "mInspector"):
            self.mInspector.hide()

    def setInspectorTree(self, title, subtitle):
        self.ensureInspectorVisible()
        self.mInspectorTitle.setText(title)
        self.mInspectorSubtitle.setText(subtitle)
        self.mInspectorBody.clear()
        self.positionInspectorDrawer()

    def addTreeItem(self, parent, field, value=""):
        item = QTreeWidgetItem(parent if parent is not None else self.mInspectorBody)
        item.setText(0, str(field))
        item.setText(1, "" if value is None else str(value))
        item.setForeground(0, QColor(COLORS["text"]))
        item.setForeground(1, QColor(COLORS["text_muted"]))
        return item

    def addValueTree(self, parent, field, value):
        if isinstance(value, dict):
            item = self.addTreeItem(parent, field, "{%d}" % len(value))
            for key in sorted(value.keys(), key=lambda k: str(k)):
                self.addValueTree(item, key, value.get(key))
            return item
        if isinstance(value, (list, tuple)):
            item = self.addTreeItem(parent, field, "[%d]" % len(value))
            for idx, entry in enumerate(value):
                self.addValueTree(item, "[%d]" % idx, entry)
            return item
        return self.addTreeItem(parent, field, value)

    def addNodeTree(self, parent, node, title=None):
        node_item = self.addTreeItem(parent, title or self.formatNodeName(node), "")
        self.addTreeItem(node_item, "NodeName", node.getNodeName())
        self.addTreeItem(node_item, "NodeId", node.getNodeId())
        self.addTreeItem(node_item, "NodeInstance", node.getNodeInstance())
        self.addTreeItem(node_item, "NodeInstanceId", node.getNodeInstanceId())
        self.addTreeItem(node_item, "Level", ", ".join(map(str, node.getNodeLevel())))
        self.addTreeItem(node_item, "InputPortCount", len(node.getInputPort()))
        self.addTreeItem(node_item, "OutputPortCount", len(node.getOutputPort()))

        input_item = self.addTreeItem(node_item, "InputPorts", len(node.getInputPort()))
        for port in node.getInputPort():
            self.addPortTree(input_item, port)

        output_item = self.addTreeItem(node_item, "OutputPorts", len(node.getOutputPort()))
        for port in node.getOutputPort():
            self.addPortTree(output_item, port)

        prop_item = self.addTreeItem(node_item, "Properties", len(node.getNodeProp()))
        for idx, prop in enumerate(node.getNodeProp()):
            one_prop = self.addTreeItem(prop_item, "Property %d" % (idx + 1), "")
            self.addTreeItem(one_prop, "Name", prop[0])
            self.addTreeItem(one_prop, "Id", prop[1])
            self.addTreeItem(one_prop, "Type", prop[2])
            self.addTreeItem(one_prop, "Value", prop[3])
        return node_item

    def addPortTree(self, parent, port, title=None):
        port_item = self.addTreeItem(parent, title or "%s_%s" % (port.getPortName(), port.getPortId()), "")
        self.addTreeItem(port_item, "PortName", port.getPortName())
        self.addTreeItem(port_item, "PortId", port.getPortId())
        self.addTreeItem(port_item, "NodeName", port.getNodeName())
        self.addTreeItem(port_item, "NodeId", port.getNodeId())
        self.addTreeItem(port_item, "NodeInstance", port.getNodeInstance())
        self.addTreeItem(port_item, "NodeInstanceId", port.getNodeInstanceId())
        return port_item

    def addLinkTree(self, parent, src_port, dst_port, title=None):
        src_node = self.findNodeForPort(src_port)
        dst_node = self.findNodeForPort(dst_port)
        link_item = self.addTreeItem(parent, title or "Link", "")
        self.addTreeItem(link_item, "SourceNode", self.formatNodeName(src_node))
        self.addPortTree(link_item, src_port, "OutputPort")
        self.addTreeItem(link_item, "TargetNode", self.formatNodeName(dst_node))
        self.addPortTree(link_item, dst_port, "InputPort")
        return link_item

    def showPipelineDetails(self):
        self.mInspectorMode = "pipeline"
        self.mSelectedLink = None
        self.setSelectedNode(None)
        if hasattr(self, "mCanvas"):
            self.mCanvas.setSelectedLink(None, None)
        self.setInspectorTree("Pipeline Details", self.mCurrentPipelineName or "Background selection")
        node_count = 0
        link_count = 0
        if self.mSelectPipeline is not None:
            node_count = len(self.mSelectPipeline.getNodeList())
            for outputs in self.mSelectPipeline.getPortLink().values():
                link_count += len(outputs)

        summary = self.addTreeItem(None, "Summary", "")
        self.addTreeItem(summary, "Pipeline", self.mCurrentPipelineName or "No pipeline selected")
        self.addTreeItem(summary, "Files", self.mCurrentFileSummary)
        self.addTreeItem(summary, "Format", "JSON" if self.mJsonOpend else "XML")
        self.addTreeItem(summary, "Zoom", "%d%%" % int(self.mZoomScale * 100))
        self.addTreeItem(summary, "NodeCount", node_count)
        self.addTreeItem(summary, "LinkCount", link_count)
        summary.setExpanded(True)

        if self.mSelectPipeline is None:
            return

        nodes_item = self.addTreeItem(None, "Nodes", node_count)
        for idx, node in enumerate(self.mSelectPipeline.getNodeList()):
            self.addNodeTree(nodes_item, node, "Node %d: %s" % (idx + 1, self.formatNodeName(node)))

        keys_item = self.addTreeItem(None, "Keys", "")
        keys = self.mSelectPipeline.getPipelineKeys()
        if keys:
            self.addValueTree(keys_item, "PipelineKeys", keys)
        else:
            src_names = self.mSelectPipeline.getSrcNodeNameList()
            self.addValueTree(keys_item, "SourceOrTargetNames", src_names)

        links_item = self.addTreeItem(None, "Links", link_count)
        link_index = 1
        for src_port, dst_ports in self.mSelectPipeline.getPortLink().items():
            for dst_port in dst_ports:
                self.addLinkTree(links_item, src_port, dst_port, "Link %d" % link_index)
                link_index += 1
        self.mInspectorBody.collapseAll()
        summary.setExpanded(True)

    def showNodeDetails(self, node):
        self.mInspectorMode = "node"
        self.mSelectedLink = None
        self.setSelectedNode(node)
        if hasattr(self, "mCanvas"):
            self.mCanvas.setSelectedLink(None, None)
        self.setInspectorTree("Node Details", self.formatNodeName(node))
        root = self.addNodeTree(None, node)
        self.mInspectorBody.collapseAll()
        root.setExpanded(True)

    def showLinkDetails(self, src_port, dst_port):
        self.mInspectorMode = "link"
        self.mSelectedLink = (src_port, dst_port)
        self.setSelectedNode(None)
        if hasattr(self, "mCanvas"):
            self.mCanvas.setSelectedLink(src_port, dst_port)
        src_node = self.findNodeForPort(src_port)
        dst_node = self.findNodeForPort(dst_port)
        self.setInspectorTree("Link Details",
                              "%s -> %s" % (self.formatNodeName(src_node), self.formatNodeName(dst_node)))
        root = self.addLinkTree(None, src_port, dst_port)
        self.mInspectorBody.expandAll()

    def isCanvasSurface(self, obj):
        return obj in (getattr(self, "mCanvasViewport", None),
                       getattr(self, "imageWindow", None),
                       getattr(self, "mCanvas", None))

    def isMenuPopupOpen(self):
        menubar = getattr(self, "mMenuBar", None)
        if menubar is None:
            return False
        for action in menubar.actions():
            menu = action.menu()
            if menu is not None and menu.isVisible():
                return True
        return False

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
                self.saveCurrentPipelineLayout()
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
        step = int(angleY * 2.5)
        if self.mMouseInBrowser is False:
            if self.mKeyCtrlStatus:
                self.applyCanvasZoom(angleY, event.globalPos())
            elif self.mKeyShiftStatus:
                self.mCanvas.move(self.mCanvas.pos() + QPoint(step, 0))
            else:
                self.mCanvas.move(self.mCanvas.pos() + QPoint(0, step))

        if angleY > 0:
            pass
        else:                                                                  # 滚轮下滚
            pass

    def updateBrowserSize(self):
        self.mImageBrowserWidth = self.mLeftPanel.width()
        self.updateCanvasViewportSize()

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
            canvasRelativePos = self.mCanvas.mapFrom(self, pos)
            for node in self.mSelectPipeline.getNodeList():
                # Utils.LogI(self.TAG,
                #            ("pos: ", pos, "canvasRelativePos:", canvasRelativePos, "NodeName:", node.getNodeName(),
                #             "NodePos", node.getNodePos(), "move:", node.getNodePos() + self.mCanvas.pos()))
                if self.isSelectNode(node, canvasRelativePos):
                    nodePropList = node.getNodeProp()
                    propMsg += "Node: %s_%s\n" % (node.getNodeName(), str(node.getNodeInstanceId()))
                    for nodeProp in nodePropList:
                        propMsg += "\n" + \
                                   "Name: " + str(nodeProp[0]) + "\n" + \
                                   "Id: " + str(nodeProp[1]) + "\n" + \
                                   "Type: " + str(nodeProp[2]) + "\n" + \
                                   "Value: " + str(nodeProp[3]) + "\n"

                        num += 6

                    if len(propMsg) > 20:
                        self.mLabelPropMsg = propMsg
                        nodeTopLeft = self.mCanvas.mapTo(self, node.getNodePos())
                        label_y = max(52, nodeTopLeft.y() - self.mLabelMetrics.height() * min(num, 14))
                        label_x = min(max(self.mImageBrowserWidth + 24, nodeTopLeft.x() + 16), max(self.width() - 560, self.mImageBrowserWidth + 24))
                        self.mLabelMovePos = QPoint(label_x, label_y)
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
        menubar = getattr(self, "mMenuBar", None)
        if object is menubar and event.type() in (QEvent.MouseMove, QEvent.HoverMove) and self.isMenuPopupOpen():
            return True

        if event.type() in (QEvent.HoverMove, QEvent.MouseMove):
            if hasattr(event, "globalPos"):
                pos = self.mapFromGlobal(event.globalPos())
            else:
                pos = self.mapFromGlobal(object.mapToGlobal(event.pos()))

            self.mMouseInBrowser = self.mLeftPanel.rect().contains(self.mLeftPanel.mapFrom(self, pos))
            self.mImageBrowserChange = False
            msg = ComMsg(MsgType.HoverMove, False)
            self.mSignal.emit(msg)
            self.showNodePorp(pos)

            if self.m_drag and hasattr(event, "globalPos"):
                self.mCanvas.move(event.globalPos() - self.m_DragPosition)
                self.mCanvas.update()
                return True

        if self.isCanvasSurface(object) and event.type() == QEvent.MouseButtonPress and event.button() == Qt.RightButton:
            if object == getattr(self, "mCanvas", None):
                if self.mCanvas.hitTestLink(event.pos()) is None:
                    self.showPipelineDetails()
            elif object in (getattr(self, "mCanvasViewport", None), getattr(self, "imageWindow", None)):
                self.showPipelineDetails()
            event.accept()
            return True

        if self.isCanvasSurface(object) and event.type() == QEvent.MouseButtonPress and event.button() == Qt.LeftButton:
            if object == getattr(self, "mCanvas", None):
                hit = self.mCanvas.hitTestLink(event.pos())
                if hit is not None:
                    self.showLinkDetails(hit[0], hit[1])
            self.m_drag = True
            self.m_DragPosition = event.globalPos() - self.mCanvas.pos()
            self.setCursor(QCursor(Qt.ClosedHandCursor))
            event.accept()
            return True

        if self.isCanvasSurface(object) and event.type() == QEvent.MouseButtonRelease and event.button() == Qt.LeftButton:
            self.m_drag = False
            self.setCursor(QCursor(Qt.ArrowCursor))
            event.accept()
            return True

        if event.type() == QEvent.Wheel and (self.isCanvasSurface(object) or object in self.mNodePainterList):
            angle = event.angleDelta() / 8
            angleY = angle.y()
            if self.mKeyCtrlStatus:
                self.applyCanvasZoom(angleY, event.globalPos())
            elif self.mKeyShiftStatus:
                self.mCanvas.move(self.mCanvas.pos() + QPoint(int(angleY * 2.5), 0))
            else:
                self.mCanvas.move(self.mCanvas.pos() + QPoint(0, int(angleY * 2.5)))
            self.mCanvas.update()
            event.accept()
            return True

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
        self.updateCanvasContext()
        # Utils.LogD(self.TAG,
        #            ("%s: - self.mImageBrowserWidth %d" % (sys._getframe().f_code.co_name, self.mImageBrowserWidth)))
