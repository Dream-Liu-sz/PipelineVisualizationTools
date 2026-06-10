from PyQt5.Qt import QPoint, QSize
from PyQt5.Qt import QMessageBox
from PyQt5.Qt import QMainWindow
from PyQt5.QtCore import Qt, QEvent, QRect, QSettings, QTimer, pyqtSignal
from PyQt5.Qt import QPalette
from PyQt5.Qt import QIcon
from PyQt5.Qt import QAction
from PyQt5.QtGui import QColor, QCursor, QFont, QFontMetrics, QPalette, QPixmap, QPainter, QIcon, QPen
from PyQt5.QtWidgets import QTreeWidget, QAbstractItemView, QHeaderView, QFrame, QTreeWidgetItem, QWidget, QFileDialog, \
    QLabel, QSplitter, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QSizePolicy, QApplication, QDialog, \
    QFormLayout, QDialogButtonBox, QPlainTextEdit, QMenu, QSpinBox, QScrollArea

from CanvasWidget import CanvasImage
from Node import NodeDes
from NodePainter import NodePainter
from PipelineEditor import PipelineEditController
from Utils import Utils
from Utils import ComMsg
from Utils import MsgType
from UseCase import UseCaseDes
from ui_theme import COLORS, app_stylesheet, font, node_color, tooltip_stylesheet
import sys
import ctypes
import os
import json5

import resource

class MainWindow(QMainWindow):
    TAG = "MainWindow"
    DEFAULT_PIPELINE_ZOOM = 0.62
    PORT_LABEL_MIN_ZOOM = 0.78
    CANVAS_MAJOR_GRID = 160
    EXPLORER_MIN_WIDTH = 220
    INSPECTOR_DEFAULT_WIDTH = 294
    SNAPSHOT_BUTTON_SIZE = 54
    FLOAT_BUTTON_GAP = 12
    UNDO_BUTTON_SIZE = 42
    ADD_NODE_BUTTON_SIZE = 48
    SNAPSHOT_MARGIN = 120
    SNAPSHOT_TITLE_HEIGHT = 84
    LAST_OPEN_DIR_KEY = "fileDialog/lastOpenDir"
    DEFAULT_XML_DIR = r"D:\workspace\tools\PipelineTools"
    DEFAULT_JSON_DIR = r"Y:\workspace\code\aero_vendor_do\vendor\noth\hardware\camera\src\extened\config\aero\pipelinedescription"
    mSignal = pyqtSignal(ComMsg)
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setWindowTitle("Pipeline Visualization tools")
        self.resize(1280, 720)
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
        self.mSettings = QSettings("PipelineVisualizationTools", "PipelineVisualizationTools")
        self.mExplorerVisible = True
        self.mLastExplorerWidth = self.mImageBrowserWidth
        self.mLoadedPaths = []
        self.mPipelineJsonPathMap = {}
        self.mUseCase = None
        self.mEditor = PipelineEditController()
        self.mEditMode = False
        self.mLastAddNodePos = QPoint(260, 180)
        self.mInspectorCollapsed = True
        self.mInspectorLastMode = "pipeline"
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
        self.initFloatingControls()
        self.enableFileDropTargets()
        self.updateCanvasContext()

    def enableFileDropTargets(self):
        for widget in (self, getattr(self, "mRootWidget", None), getattr(self, "mLeftPanel", None),
                       getattr(self, "mRightPanel", None), getattr(self, "mCanvasViewport", None),
                       getattr(self, "imageBrowser", None), getattr(self, "imageWindow", None),
                       getattr(self, "mCanvas", None)):
            if widget is not None:
                widget.setAcceptDrops(True)
                if widget is not self:
                    widget.installEventFilter(self)

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
        self.mContextLayout.addWidget(titleColumn, 1)
        self.mContextLayout.addWidget(self.mMetricNodes)
        self.mContextLayout.addWidget(self.mMetricLinks)
        self.mContextLayout.addWidget(self.mMetricZoom)
        self.mRightLayout.addWidget(self.mContextBar)

        self.mCanvasViewport = QWidget(self.mRightPanel)
        self.mCanvasViewport.setObjectName("canvasViewport")
        self.mCanvasViewport.setMinimumSize(480, 360)
        self.mCanvasViewport.setMouseTracking(True)
        self.mCanvasViewport.setAttribute(Qt.WidgetAttribute.WA_Hover)
        self.mCanvasViewport.installEventFilter(self)
        self.mInspectorDefaultWidth = self.INSPECTOR_DEFAULT_WIDTH
        self.initInspectorDrawer()
        self.mInspector.hide()
        self.mRightLayout.addWidget(self.mCanvasViewport, 1)

        self.mSplitter.addWidget(self.mLeftPanel)
        self.mSplitter.addWidget(self.mRightPanel)
        self.mSplitter.addWidget(self.mInspector)
        self.mSplitter.setCollapsible(0, True)
        self.mSplitter.setCollapsible(1, False)
        self.mSplitter.setCollapsible(2, True)
        self.mImageBrowserWidth = self.EXPLORER_MIN_WIDTH
        self.mLastExplorerWidth = self.mImageBrowserWidth
        self.mSplitter.setSizes([self.mImageBrowserWidth, 1060, 0])
        self.mSplitter.splitterMoved.connect(self.onSplitterMoved)

        self.mStatusText = QLabel("Drop XML/JSON to open | Drag canvas to pan | Right-click background: pipeline info | Wheel: vertical | Shift+Wheel: horizontal | Ctrl+Wheel: zoom")
        self.statusBar().addPermanentWidget(self.mStatusText, 1)

    def initInspectorDrawer(self):
        self.mInspector = QFrame(self.mSplitter)
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
        inspectorHeaderLayout.addWidget(self.mInspectorTitle, 1)
        self.mInspectorSubtitle = QLabel("Click a node, link, or background", self.mInspector)
        self.mInspectorSubtitle.setObjectName("inspectorSubtitle")
        self.mInspectorBody = QTreeWidget(self.mInspector)
        self.mInspectorBody.setObjectName("inspectorBody")
        self.mInspectorBody.setColumnCount(2)
        self.mInspectorBody.setHeaderLabels(["Field", "Value"])
        self.mInspectorBody.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.mInspectorBody.header().setSectionResizeMode(1, QHeaderView.Stretch)
        self.mInspectorBody.setFont(font(9, mono=True))
        self.mInspectorEditing = False
        self.mInspectorBody.itemChanged.connect(self.handleInspectorItemChanged)

        self.mInspectorLayout.addWidget(inspectorHeader)
        self.mInspectorLayout.addWidget(self.mInspectorSubtitle)
        self.mInspectorLayout.addWidget(self.mInspectorBody, 1)

    def positionInspectorDrawer(self):
        if not hasattr(self, "mInspector"):
            return
        self.mInspector.raise_()
        self.positionFloatingControls()

    def initLable(self):
        self.mLabel = QLabel(self)
        palette = QPalette()
        palette.setColor(QPalette.WindowText, QColor(COLORS["text"]))
        label_font = font(10, mono=True)
        self.mLabelMetrics = QFontMetrics(label_font)
        self.mLabel.setFont(label_font)
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

    def floatingButtonStyle(self, size, active=False):
        bg = "#F2F2F2"
        fg = "#202020"
        border = "#38BDF8" if active else "#FFFFFF"
        hover = "#FFFFFF"
        return """
            QPushButton {
                background: %s;
                color: %s;
                border: 1px solid %s;
                border-radius: %dpx;
                font-weight: 700;
            }
            QPushButton:hover {
                background: %s;
                border-color: #D8D8D8;
            }
            QPushButton:pressed {
                background: #DADADA;
            }
            QPushButton:disabled {
                background: #DADADA;
                color: #202020;
                border-color: #9A9A9A;
            }
        """ % (bg, fg, border, size // 2, hover)

    def configureFloatingButton(self, button, size, tooltip, text=None, icon=None):
        button.setFixedSize(size, size)
        if text is not None:
            button.setText(text)
        if icon is not None:
            button.setText("")
            button.setIcon(icon)
            button.setIconSize(QSize(28, 28))
        button.setToolTip(tooltip)
        button.setCursor(QCursor(Qt.PointingHandCursor))
        button.setStyleSheet(self.floatingButtonStyle(size))
        button.raise_()

    def initFloatingControls(self):
        self.mEditFloatingButton = QPushButton(self)
        self.configureFloatingButton(self.mEditFloatingButton, self.SNAPSHOT_BUTTON_SIZE,
                                     "Enter or leave JSON edit mode", icon=self.createEditIcon())
        self.mEditFloatingButton.clicked.connect(self.toggleEditMode)

        self.mSaveFloatingButton = QPushButton(self)
        self.configureFloatingButton(self.mSaveFloatingButton, self.SNAPSHOT_BUTTON_SIZE,
                                     "Save edited JSON", icon=self.createSaveIcon())
        self.mSaveFloatingButton.clicked.connect(self.saveEditedJson)
        self.mSaveFloatingButton.hide()

        self.mFitButton = QPushButton(self)
        self.configureFloatingButton(self.mFitButton, self.SNAPSHOT_BUTTON_SIZE,
                                     "Center pipeline view", icon=self.createCenterIcon())
        self.mFitButton.clicked.connect(self.centerCanvas)

        self.mResetViewButton = QPushButton(self)
        self.configureFloatingButton(self.mResetViewButton, self.SNAPSHOT_BUTTON_SIZE,
                                     "Reset pipeline view", icon=self.createResetIcon())
        self.mResetViewButton.clicked.connect(self.resetPipelineView)

        self.mSnapshotButton = QPushButton(self)
        self.configureFloatingButton(self.mSnapshotButton, self.SNAPSHOT_BUTTON_SIZE,
                                     "Save pipeline snapshot as JPEG", icon=self.createSnapshotIcon())
        self.mSnapshotButton.clicked.connect(self.snapshotPipeline)

        self.mAddNodeButton = QPushButton(self)
        self.configureFloatingButton(self.mAddNodeButton, self.ADD_NODE_BUTTON_SIZE,
                                     "Add node from template", icon=self.createPlusIcon())
        self.mAddNodeButton.clicked.connect(self.addNodeFromFloatingButton)
        self.mAddNodeButton.hide()

        self.mUndoFloatingButton = QPushButton(self)
        self.configureFloatingButton(self.mUndoFloatingButton, self.UNDO_BUTTON_SIZE,
                                     "Undo edit", icon=self.createUndoIcon(False))
        self.mUndoFloatingButton.clicked.connect(self.undoEdit)
        self.mUndoFloatingButton.hide()

        self.mRedoFloatingButton = QPushButton(self)
        self.configureFloatingButton(self.mRedoFloatingButton, self.UNDO_BUTTON_SIZE,
                                     "Redo edit", icon=self.createUndoIcon(True))
        self.mRedoFloatingButton.clicked.connect(self.redoEdit)
        self.mRedoFloatingButton.hide()

        self.positionFloatingControls()
        self.updateEditControls()

    def createSnapshotIcon(self):
        pixmap = QPixmap(28, 28)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing, True)
        body = QColor("#202020")
        lens = QColor("#F2F2F2")
        painter.setPen(QPen(body, 2))
        painter.setBrush(body)
        painter.drawRoundedRect(4, 8, 20, 15, 4, 4)
        painter.drawRoundedRect(8, 5, 7, 5, 2, 2)
        painter.setPen(QPen(lens, 2))
        painter.setBrush(QColor("#202020"))
        painter.drawEllipse(10, 11, 8, 8)
        painter.setPen(Qt.NoPen)
        painter.setBrush(lens)
        painter.drawEllipse(20, 10, 2, 2)
        painter.end()
        return QIcon(pixmap)

    def createLineIcon(self, draw_fn):
        pixmap = QPixmap(28, 28)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setPen(QPen(QColor("#202020"), 2.4))
        painter.setBrush(Qt.NoBrush)
        draw_fn(painter)
        painter.end()
        return QIcon(pixmap)

    def createEditIcon(self):
        def draw(painter):
            painter.drawLine(8, 20, 20, 8)
            painter.drawLine(17, 5, 23, 11)
            painter.drawLine(6, 22, 11, 20)
            painter.drawLine(6, 22, 8, 17)
        return self.createLineIcon(draw)

    def createSaveIcon(self):
        def draw(painter):
            painter.drawRoundedRect(6, 5, 16, 18, 2, 2)
            painter.drawLine(10, 5, 10, 11)
            painter.drawLine(10, 11, 18, 11)
            painter.drawRect(10, 16, 8, 6)
        return self.createLineIcon(draw)

    def createCenterIcon(self):
        def draw(painter):
            painter.drawEllipse(7, 7, 14, 14)
            painter.drawLine(14, 3, 14, 9)
            painter.drawLine(14, 19, 14, 25)
            painter.drawLine(3, 14, 9, 14)
            painter.drawLine(19, 14, 25, 14)
        return self.createLineIcon(draw)

    def createResetIcon(self):
        def draw(painter):
            painter.drawArc(6, 6, 16, 16, 35 * 16, 285 * 16)
            painter.drawLine(8, 7, 8, 13)
            painter.drawLine(8, 7, 14, 7)
        return self.createLineIcon(draw)

    def createPlusIcon(self):
        def draw(painter):
            painter.drawLine(14, 7, 14, 21)
            painter.drawLine(7, 14, 21, 14)
        return self.createLineIcon(draw)

    def createUndoIcon(self, redo=False):
        def draw(painter):
            if redo:
                painter.drawArc(6, 7, 16, 14, 210 * 16, 260 * 16)
                painter.drawLine(19, 8, 23, 8)
                painter.drawLine(23, 8, 23, 12)
            else:
                painter.drawArc(6, 7, 16, 14, -110 * 16, 260 * 16)
                painter.drawLine(9, 8, 5, 8)
                painter.drawLine(5, 8, 5, 12)
        return self.createLineIcon(draw)

    def createNodeTemplateIcon(self, blank=False):
        def draw(painter):
            if blank:
                painter.setPen(QPen(QColor("#202020"), 2.4))
                painter.drawRoundedRect(7, 7, 14, 14, 3, 3)
                painter.drawLine(14, 10, 14, 18)
                painter.drawLine(10, 14, 18, 14)
                return
            painter.drawRoundedRect(6, 8, 16, 12, 3, 3)
            painter.drawEllipse(4, 12, 4, 4)
            painter.drawEllipse(20, 12, 4, 4)
        return self.createLineIcon(draw)

    def positionSnapshotButton(self):
        self.positionFloatingControls()

    def positionFloatingControls(self):
        if not hasattr(self, "mSnapshotButton"):
            return
        offset = 0
        if hasattr(self, "mInspector") and self.mInspector.isVisible():
            offset = self.mInspector.width() + 12
        status_height = self.statusBar().height() if self.statusBar() is not None else 0
        size = self.SNAPSHOT_BUTTON_SIZE
        bottom_buttons = [self.mEditFloatingButton]
        if self.mEditMode and self.mEditor.enabled:
            bottom_buttons.append(self.mSaveFloatingButton)
        bottom_buttons.extend([self.mFitButton, self.mResetViewButton, self.mSnapshotButton])
        total_width = len(bottom_buttons) * size + (len(bottom_buttons) - 1) * self.FLOAT_BUTTON_GAP
        x = max(16, self.width() - offset - total_width - 22)
        y = max(16, self.height() - status_height - size - 18)
        for index, button in enumerate(bottom_buttons):
            button.move(x + index * (size + self.FLOAT_BUTTON_GAP), y)
            button.raise_()

        if hasattr(self, "mAddNodeButton"):
            add_size = self.ADD_NODE_BUTTON_SIZE
            add_pos = self.mCanvasViewport.mapTo(self, QPoint(18, max(0, self.mCanvasViewport.height() // 2 - add_size // 2)))
            add_x = add_pos.x()
            add_y = add_pos.y()
            self.mAddNodeButton.move(add_x, add_y)
            self.mAddNodeButton.raise_()

        if hasattr(self, "mUndoFloatingButton"):
            top_left = self.mCanvasViewport.mapTo(self, QPoint(18, 18))
            self.mUndoFloatingButton.move(top_left)
            self.mRedoFloatingButton.move(top_left + QPoint(self.UNDO_BUTTON_SIZE + 8, 0))
            self.mUndoFloatingButton.raise_()
            self.mRedoFloatingButton.raise_()

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
        self.mInspectorToggleButton = QPushButton(menubar)
        self.mInspectorToggleButton.setObjectName("menuIconButton")
        self.mInspectorToggleButton.setCheckable(True)
        self.mInspectorToggleButton.setChecked(False)
        self.mInspectorToggleButton.setIcon(self.createSidebarToggleIcon(False))
        self.mInspectorToggleButton.setIconSize(QSize(18, 18))
        self.mInspectorToggleButton.setFixedSize(32, 28)
        self.mInspectorToggleButton.setToolTip("Show or hide details panel")
        self.mInspectorToggleButton.clicked.connect(self.toggleInspectorFromAction)
        menubar.setCornerWidget(self.mInspectorToggleButton, Qt.TopRightCorner)

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
        stroke = QColor("#F2F2F2" if checked else "#B8B8B8")
        fill = QColor(255, 255, 255, 0)
        painter.setPen(QPen(stroke, 1.4))
        painter.setBrush(fill)
        painter.drawRoundedRect(3, 3, 10, 10, 2, 2)
        painter.drawLine(6, 4, 6, 12)
        painter.end()
        return QIcon(pixmap)

    def triggerOpenFile(self, q):
        rootdir = self.getLastOpenDir(self.DEFAULT_XML_DIR)
        fileName, self.mFiletype = QFileDialog.getOpenFileName(self,
                                                          "Open XML pipeline file",
                                                          rootdir,
                                                          "Xml Files (*.xml);;All Files (*)")

        self.loadPipelineFiles(fileName)

    def triggerOpenFiles(self, q):
        rootdir = self.getLastOpenDir(self.DEFAULT_JSON_DIR)

        fileNames, self.mFiletype = QFileDialog.getOpenFileNames(self,
                                                                      "Open JSON pipeline files",
                                                                      rootdir,
                                                                      "Json Files (*.json);;All Files (*)")
        self.loadPipelineFiles(fileNames)

    def getLastOpenDir(self, fallbackDir):
        lastDir = self.mSettings.value(self.LAST_OPEN_DIR_KEY, "", type=str)
        if lastDir and os.path.isdir(lastDir):
            return lastDir
        if fallbackDir and os.path.isdir(fallbackDir):
            return fallbackDir
        return os.path.dirname(os.path.abspath(__file__))

    def rememberOpenPath(self, paths):
        if isinstance(paths, (list, tuple)):
            if len(paths) == 0:
                return
            path = paths[0]
        else:
            path = paths
        if not path:
            return
        directory = path if os.path.isdir(path) else os.path.dirname(path)
        if directory:
            self.mSettings.setValue(self.LAST_OPEN_DIR_KEY, directory)

    def loadPipelineFiles(self, paths):
        if isinstance(paths, str):
            paths = [paths] if paths else []
        paths = [path for path in paths if path]
        if len(paths) == 0:
            return False
        self.mPipelineJsonPathMap = {}

        xmlFiles = [path for path in paths if path.lower().endswith(".xml")]
        jsonFiles = [path for path in paths if path.lower().endswith(".json")]
        if len(xmlFiles) == 1 and len(jsonFiles) == 0 and len(paths) == 1:
            self.disableEditMode()
            self.mLoadedPaths = list(paths)
            self.imageBrowser.clear()
            self.clearLoadedPipeline()
            self.mFileName = xmlFiles[0]
            self.mCurrentFileSummary = self.mFileName
            self.mJsonOpend = False
            self.rememberOpenPath(self.mFileName)
            self.initUseCase()
            return True
        if len(jsonFiles) > 0 and len(xmlFiles) == 0 and len(jsonFiles) == len(paths):
            self.disableEditMode()
            self.mLoadedPaths = list(jsonFiles)
            self.imageBrowser.clear()
            self.clearLoadedPipeline()
            self.mFileName = jsonFiles
            print(self.mFileName)
            self.mCurrentFileSummary = "%d JSON files loaded" % len(self.mFileName)
            self.mJsonOpend = True
            self.indexJsonPipelinePaths(jsonFiles)
            self.rememberOpenPath(self.mFileName)
            self.initAllJsonPipeline()
            return True

        self.showStyledMessage("Unsupported file",
                               "Please open one XML pipeline file, or one or more JSON pipeline files.")
        return False

    def droppedPipelineFiles(self, event):
        if not event.mimeData().hasUrls():
            return []
        files = []
        for url in event.mimeData().urls():
            if not url.isLocalFile():
                continue
            path = url.toLocalFile()
            if os.path.isfile(path) and path.lower().endswith((".xml", ".json")):
                files.append(path)
        return files

    def dragEnterEvent(self, event):
        if self.droppedPipelineFiles(event):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if self.droppedPipelineFiles(event):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        if self.loadPipelineFiles(self.droppedPipelineFiles(event)):
            event.acceptProposedAction()
        else:
            event.ignore()

    def indexJsonPipelinePaths(self, jsonFiles):
        self.mPipelineJsonPathMap = {}
        for path in jsonFiles:
            try:
                with open(path, "r", encoding="utf-8") as fh:
                    doc = json5.load(fh)
                pipeline_name = str(doc.get("PipelineName", ""))
                if pipeline_name:
                    self.mPipelineJsonPathMap[pipeline_name] = path
            except Exception:
                continue

    def clearLoadedPipeline(self):
        self.clearWork()
        self.mSelectPipeline = None
        self.mCurrentPipelineName = ""
        self.mPipelineBaseLayoutMap.clear()
        self.mPipelineCurrentLayoutMap.clear()
        self.mBaseLayout.clear()
        self.mSelectedNode = None
        self.mSelectedLink = None
        if hasattr(self, "mCanvas"):
            self.mCanvas.mNodeMapPainter.clear()
            self.mCanvas.initPainterInstance([])
            self.mCanvas.setPortLinkDes({})
            self.mCanvas.setSelectedLink(None, None)
            self.mCanvas.setPendingSourcePort(None)
            self.mCanvas.update()

    def processHelp(self):
        version = "V3.1"
        update = "2026.06.01"
        aboutInfo = "\n".join([
            "Version: %s" % version,
            "Owner: Jianlin",
            "Feedback: a185531353@qq.com",
            "Updated: %s" % update,
        ])
        self.showStyledMessage("About", aboutInfo)

    def showTips(self):
        self.showStyledMessage("Tips",
                               "If opening a file shows no result, use the compiled XML file, such as g_xxx_usecase.xml.")


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
        # Create the root use case
        self.mUseCase = UseCaseDes(str(self.mFileName), "")
        self.mUseCase.useCaseTranslation()
        self.updateTreeWidget()
        self.updateCanvasContext()
        Utils.LogD(self.TAG, ("%s: - " % (sys._getframe().f_code.co_name)))

    def initAllJsonPipeline(self):
        Utils.LogD(self.TAG, ("%s: + " % (sys._getframe().f_code.co_name)))

        # Create the root use case
        self.mUseCase = UseCaseDes(self.mFileName, "NCFJsonUses")
        self.mUseCase.useCaseTranslationJson()
        self.updateTreeWidget()
        self.updateCanvasContext()
        Utils.LogD(self.TAG, ("%s: - " % (sys._getframe().f_code.co_name)))

    def initBrowser(self):
        Utils.LogD(self.TAG, ("%s: + " % (sys._getframe().f_code.co_name)))
        self.mImageBrowserPos = QPoint(0, 26)
        self.imageBrowser = QTreeWidget(self.mLeftPanel)
        self.imageBrowser.setColumnCount(1)
        self.imageBrowser.setHeaderLabels(['name'])
        self.imageBrowser.setMinimumSize(0, 0)
        self.imageBrowser.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

        self.imageBrowser.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.imageBrowser.header().setStretchLastSection(False)
        self.imageBrowser.header().setSectionResizeMode(QHeaderView.Stretch)
        self.imageBrowser.setHeaderHidden(True)
        self.imageBrowser.raise_()
        self.imageBrowser.setFrameShape(QFrame.NoFrame)
        self.imageBrowser.setFrameShadow(QFrame.Plain)
        self.imageBrowser.doubleClicked.connect(self.onClicked)
        self.mLeftLayout.addWidget(self.imageBrowser, 1)

        Utils.LogD(self.TAG, ("%s: - " % (sys._getframe().f_code.co_name)))

    def onClicked(self, modelIndex):
        item = self.imageBrowser.currentItem()
        self.mFontSize = 24
        if item.parent() != None and item.parent().text(0) != "UseCase":
            if self.mEditMode and self.mCurrentPipelineName and item.text(0) != self.mCurrentPipelineName:
                self.showStyledMessage("Edit mode", "Finish or leave edit mode before switching to another pipeline.")
                return
            # QMessageBox.information(self, 'Tips', 'Select useCase %s pipeline is %s' % (item.parent().text(0), item.text(0)))
            self.mCurrentPipelineName = item.text(0)
            self.mSelectPipeline = self.mUseCase.buildPipeline(item.parent().text(0), item.text(0), self.mCanvasCenterPos, self.mFontSize, self)
            self.mSelectPipeline.print()
            self.clearWork()
            self.initCanvas()
            self.attachEditorForCurrentPipeline()
            self.updateCanvasContext()

    def attachEditorForCurrentPipeline(self):
        json_path = self.mPipelineJsonPathMap.get(self.mCurrentPipelineName)
        if self.mJsonOpend and json_path is not None and self.mSelectPipeline is not None:
            self.mEditor.attach(self.mSelectPipeline, json_path)
        else:
            self.mEditor.detach()
            self.mEditMode = False
        if hasattr(self, "mCanvas"):
            self.mCanvas.setPendingSourcePort(None)
        self.updateEditControls()

    def disableEditMode(self):
        self.mEditMode = False
        if hasattr(self, "mEditor"):
            self.mEditor.detach()
        if hasattr(self, "mCanvas"):
            self.mCanvas.setPendingSourcePort(None)
        self.updateEditControls()

    def toggleEditMode(self):
        if not self.mEditor.enabled:
            self.mEditMode = False
            self.showStyledMessage("Edit mode", self.editModeUnavailableReason())
        else:
            self.mEditMode = not self.mEditMode
            self.mEditor.set_tool(PipelineEditController.TOOL_SELECT)
            if not self.mEditMode:
                self.mEditor.pending_src_port = None
                if hasattr(self, "mCanvas"):
                    self.mCanvas.setPendingSourcePort(None)
            elif self.mInspectorCollapsed and self.mSelectPipeline is not None:
                self.mInspectorCollapsed = False
                self.showPipelineDetails()
        self.updateEditControls()

    def setEditTool(self, tool):
        return

    def editModeUnavailableReason(self):
        if not self.mJsonOpend:
            return "Please open JSON and double-click one pipeline to render it. XML is read-only."
        if self.mSelectPipeline is None:
            return "Double-click a pipeline in the left panel before entering edit mode."
        if self.mPipelineJsonPathMap.get(self.mCurrentPipelineName) is None:
            return "This pipeline has no matching source JSON path."
        return "This pipeline cannot enter edit mode."

    def updateEditControls(self):
        if not hasattr(self, "mEditFloatingButton"):
            return
        editable = self.mEditor.enabled
        active = editable and self.mEditMode
        self.mEditFloatingButton.setStyleSheet(self.floatingButtonStyle(self.SNAPSHOT_BUTTON_SIZE, active))
        self.mEditFloatingButton.setToolTip("Leave edit mode" if active else "Enter JSON edit mode")
        self.mSaveFloatingButton.setVisible(active)
        self.mSaveFloatingButton.setEnabled(active and self.mEditor.dirty)
        self.mAddNodeButton.setVisible(active)
        self.mUndoFloatingButton.setVisible(active)
        self.mRedoFloatingButton.setVisible(active)
        self.mUndoFloatingButton.setEnabled(active and self.mEditor.can_undo())
        self.mRedoFloatingButton.setEnabled(active and self.mEditor.can_redo())
        if hasattr(self, "mInspectorToggleButton"):
            visible = not self.mInspectorCollapsed
            self.mInspectorToggleButton.blockSignals(True)
            self.mInspectorToggleButton.setChecked(visible)
            self.mInspectorToggleButton.setIcon(self.createSidebarToggleIcon(visible))
            self.mInspectorToggleButton.blockSignals(False)

        if not editable:
            msg = "JSON edit mode is unavailable"
        elif self.mEditMode:
            dirty = "modified" if self.mEditor.dirty else "clean"
            msg = "Editing %s | click output port, then input port to link | %s" % (
                os.path.basename(self.mEditor.json_path), dirty)
        else:
            msg = "Single JSON pipeline ready for edit mode"
        if self.mStatusText is not None:
            self.mStatusText.setText(msg)
        self.positionFloatingControls()

    def refreshEditedCanvas(self):
        if self.mSelectPipeline is None:
            return
        old_zoom = self.mZoomScale
        old_canvas_pos = QPoint(self.mCanvas.pos()) if hasattr(self, "mCanvas") else None
        self.mEditor.pending_src_port = None
        pipeline_key = id(self.mSelectPipeline)
        self.mPipelineBaseLayoutMap.pop(pipeline_key, None)
        self.mPipelineCurrentLayoutMap.pop(pipeline_key, None)
        self.clearWork()
        self.initCanvas()
        self.mZoomScale = old_zoom
        self.refreshZoomedLayout()
        if old_canvas_pos is not None:
            self.mCanvas.move(old_canvas_pos)
        self.updateCanvasContext()
        self.updateEditControls()

    def restorePipelineBaseGeometry(self):
        if self.mSelectPipeline is None:
            return
        for node, base in list(self.mBaseLayout.items()):
            if node is None:
                continue
            node.setNodePos(QPoint(base["pos"]))
            node.setNodeSize(QSize(base["size"]))
            node.setNodeFont(base["font"])
            node.calPortPos()

    def undoEdit(self):
        label = self.mEditor.undo()
        if label is not None:
            self.refreshEditedCanvas()
            self.statusBar().showMessage("Undo: %s" % label, 3000)

    def redoEdit(self):
        label = self.mEditor.redo()
        if label is not None:
            self.refreshEditedCanvas()
            self.statusBar().showMessage("Redo: %s" % label, 3000)

    def relayoutEditedPipeline(self):
        if not self.mEditor.enabled:
            return
        self.mEditor.relayout(self.mCanvasCenterPos, self.mFontSize)
        self.refreshEditedCanvas()
        self.statusBar().showMessage("Pipeline re-layout complete", 3000)

    def saveEditedJson(self):
        if not self.mEditor.enabled:
            self.showStyledMessage("Save JSON", "No editable JSON pipeline is selected.")
            return
        ok, message = self.mEditor.save_json()
        if not ok:
            self.showStyledMessage("Cannot save JSON", message)
            return
        self.updateEditControls()
        self.statusBar().showMessage("Saved JSON: %s" % message, 5000)

    def parsePortText(self, text):
        ports = []
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            if "," in line:
                name, port_id = line.split(",", 1)
            elif ":" in line:
                name, port_id = line.split(":", 1)
            else:
                name, port_id = "port_%s" % line, line
            ports.append((name.strip(), port_id.strip()))
        return ports

    def portText(self, ports):
        return "\n".join("%s,%s" % (port.getPortName(), port.getPortId()) for port in ports)

    def generatedPortText(self, count, prefix):
        return "\n".join("%s_%d,%d" % (prefix, index, index) for index in range(max(0, count)))

    def normalizedPortCount(self, value, fallback):
        try:
            return max(0, int(str(value).strip()))
        except ValueError:
            return fallback

    def editNodeFieldsDialog(self, node, title):
        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        dialog.setMinimumWidth(416 if title == "Add Node From Template" else 520)
        dialog.setStyleSheet("""
            QDialog {
                background: #111111;
                color: #F2F2F2;
                font-family: "Microsoft YaHei UI";
            }
            QLabel {
                color: #D6D6D6;
                background: transparent;
            }
            QLineEdit, QPlainTextEdit, QSpinBox {
                color: #F2F2F2;
                background: #202020;
                border: 1px solid #3A3A3A;
                border-radius: 8px;
                padding: 7px 9px;
                selection-background-color: #5A5A5A;
            }
            QLineEdit:focus, QPlainTextEdit:focus, QSpinBox:focus {
                border-color: #7A7A7A;
                background: #242424;
            }
            QPushButton {
                color: #E8E8E8;
                background: #242424;
                border: 1px solid #3A3A3A;
                border-radius: 8px;
                padding: 7px 16px;
                min-width: 72px;
            }
            QPushButton:hover {
                background: #2D2D2D;
                border-color: #7A7A7A;
            }
        """)
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)
        form = QFormLayout()
        form.setSpacing(10)
        nameEdit = QLineEdit(str(node.getNodeName()), dialog)
        idEdit = QLineEdit(str(node.getNodeId()), dialog)
        instanceEdit = QLineEdit(str(node.getNodeInstance()), dialog)
        instanceIdEdit = QLineEdit(str(node.getNodeInstanceId()), dialog)
        add_mode = title == "Add Node From Template"
        input_count = 0 if add_mode else len(node.getInputPort())
        output_count = 0 if add_mode else len(node.getOutputPort())
        inputCountEdit = QSpinBox(dialog)
        outputCountEdit = QSpinBox(dialog)
        for spin in (inputCountEdit, outputCountEdit):
            spin.setRange(0, 256)
        inputCountEdit.setValue(input_count)
        outputCountEdit.setValue(output_count)
        inputEdit = QPlainTextEdit(self.generatedPortText(input_count, "input") if add_mode else self.portText(node.getInputPort()), dialog)
        outputEdit = QPlainTextEdit(self.generatedPortText(output_count, "output") if add_mode else self.portText(node.getOutputPort()), dialog)
        inputEdit.setPlaceholderText("One input port per line: PortName,PortId")
        outputEdit.setPlaceholderText("One output port per line: PortName,PortId")
        inputEdit.setMinimumHeight(90)
        outputEdit.setMinimumHeight(90)
        inputCountEdit.valueChanged.connect(lambda value: inputEdit.setPlainText(self.generatedPortText(value, "input")))
        outputCountEdit.valueChanged.connect(lambda value: outputEdit.setPlainText(self.generatedPortText(value, "output")))
        form.addRow("NodeName", nameEdit)
        form.addRow("NodeId", idEdit)
        form.addRow("NodeInstance", instanceEdit)
        form.addRow("NodeInstanceId", instanceIdEdit)
        form.addRow("Input port count", inputCountEdit)
        form.addRow("Input ports", inputEdit)
        form.addRow("Output port count", outputCountEdit)
        form.addRow("Output ports", outputEdit)
        layout.addLayout(form)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, dialog)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        if dialog.exec_() != QDialog.Accepted:
            return None
        return {
            "NodeName": nameEdit.text().strip(),
            "NodeId": idEdit.text().strip(),
            "NodeInstance": instanceEdit.text().strip(),
            "NodeInstanceId": instanceIdEdit.text().strip(),
            "InputPorts": self.parsePortText(inputEdit.toPlainText()),
            "OutputPorts": self.parsePortText(outputEdit.toPlainText())
        }

    def addNodeFromTemplate(self, canvas_pos):
        if not self.mEditor.enabled or self.mSelectPipeline is None:
            return
        template = self.chooseNodeTemplate()
        if template is None:
            return
        fields = self.editNodeFieldsDialog(template, "Add Node From Template")
        if fields is None:
            return
        new_key = (fields["NodeName"], fields["NodeId"], fields["NodeInstanceId"])
        for node in self.mSelectPipeline.getNodeList():
            if self.mEditor.node_identity(node) == new_key:
                self.showStyledMessage("Add Node", "A node with this NodeName, NodeId, and NodeInstanceId already exists.")
                return
        self.restorePipelineBaseGeometry()
        new_node = self.mEditor.duplicate_node(template, fields, canvas_pos)
        self.refreshEditedCanvas()
        self.showNodeDetails(new_node)

    def collectNodeTemplates(self):
        templates = {}
        if self.mUseCase is None:
            return []
        for use_case, pipelines in self.mUseCase.getPipelineMap().items():
            for pipeline in pipelines:
                pipeline_name = pipeline.getPipelineName()
                for node in pipeline.getNodeList():
                    key = (str(node.getNodeName()), str(node.getNodeId()), str(node.getNodeInstanceId()))
                    if key not in templates:
                        templates[key] = {
                            "node": node,
                            "source": "%s / %s" % (use_case, pipeline_name)
                        }
        return sorted(templates.values(), key=lambda item: (
            str(item["node"].getNodeName()),
            str(item["node"].getNodeId()),
            str(item["node"].getNodeInstanceId())))

    def blankNodeTemplate(self):
        node = NodeDes("NewNode", "0", "0", "0")
        node.setNodeFont(self.mFontSize)
        node.calNodeSize()
        node.calPortPos()
        return node

    def chooseNodeTemplate(self):
        dialog = QDialog(self, Qt.Popup | Qt.FramelessWindowHint)
        dialog.setObjectName("nodeTemplatePopup")
        dialog.setStyleSheet("""
            QDialog#nodeTemplatePopup {
                background: #181818;
                border: 1px solid #3A3A3A;
                border-radius: 10px;
            }
            QLabel#templatePopupTitle {
                color: #F2F2F2;
                font-weight: 700;
                padding: 2px 2px 6px 2px;
            }
            QScrollArea#nodeTemplateScroll {
                background: #181818;
                border: 0;
            }
            QWidget#nodeTemplateList {
                background: #181818;
            }
            QPushButton#nodeTemplateItem {
                color: #F2F2F2;
                background: #202020;
                border: 1px solid #303030;
                border-radius: 7px;
                padding: 9px 12px;
                text-align: left;
                min-height: 22px;
            }
            QPushButton#nodeTemplateItem:hover {
                background: #2D2D2D;
                border-color: #5A5A5A;
            }
        """)
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        title = QLabel("Add Node", dialog)
        title.setObjectName("templatePopupTitle")
        layout.addWidget(title)

        scroll = QScrollArea(dialog)
        scroll.setObjectName("nodeTemplateScroll")
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        list_widget = QWidget(scroll)
        list_widget.setObjectName("nodeTemplateList")
        list_layout = QVBoxLayout(list_widget)
        list_layout.setContentsMargins(0, 0, 0, 0)
        list_layout.setSpacing(6)

        selected = {"template": None}

        def add_template_button(label, template, tooltip=""):
            button = QPushButton(label, list_widget)
            button.setObjectName("nodeTemplateItem")
            button.setIcon(self.createNodeTemplateIcon(template is None))
            button.setIconSize(QSize(18, 18))
            if tooltip:
                button.setToolTip(tooltip)
            button.clicked.connect(lambda checked=False, value=template: self.acceptNodeTemplate(dialog, selected, value))
            list_layout.addWidget(button)

        add_template_button("Blank node", None)
        for template in self.collectNodeTemplates():
            node = template["node"]
            label = "%s  #%s / inst %s" % (node.getNodeName(), node.getNodeId(), node.getNodeInstanceId())
            add_template_button(label, node, "Source: %s" % template["source"])

        list_layout.addStretch(1)
        scroll.setWidget(list_widget)
        row_count = len(self.collectNodeTemplates()) + 1
        max_height = max(220, min(520, self.mCanvasViewport.height() - 80, row_count * 43 + 16))
        scroll.setFixedHeight(max_height)
        dialog.setFixedWidth(272)
        layout.addWidget(scroll)

        dialog.adjustSize()
        button_center = self.mAddNodeButton.mapToGlobal(
            QPoint(self.mAddNodeButton.width() + 8, self.mAddNodeButton.height() // 2))
        screen_rect = QApplication.desktop().availableGeometry(self)
        popup_x = button_center.x()
        popup_y = button_center.y() - dialog.height() // 2
        popup_y = max(screen_rect.top() + 8, min(popup_y, screen_rect.bottom() - dialog.height() - 8))
        popup_x = max(screen_rect.left() + 8, min(popup_x, screen_rect.right() - dialog.width() - 8))
        dialog.move(QPoint(popup_x, popup_y))
        if dialog.exec_() != QDialog.Accepted:
            return None
        if selected["template"] is None:
            return self.blankNodeTemplate()
        return selected["template"]

    def acceptNodeTemplate(self, dialog, selected, template):
        selected["template"] = template
        dialog.accept()

    def addNodeFromFloatingButton(self):
        if not self.mEditMode or not self.mEditor.enabled:
            return
        viewport_pos = QPoint(180, max(80, self.mCanvasViewport.height() // 2))
        canvas_pos = viewport_pos - self.mCanvas.pos()
        if self.mZoomScale > 0:
            canvas_pos = QPoint(int(canvas_pos.x() / self.mZoomScale), int(canvas_pos.y() / self.mZoomScale))
        self.mLastAddNodePos = QPoint(canvas_pos)
        self.addNodeFromTemplate(canvas_pos)

    def editSelectedNode(self, node):
        if not self.mEditor.enabled or node is None:
            return
        fields = self.editNodeFieldsDialog(node, "Edit Node")
        if fields is None:
            return
        new_key = (fields["NodeName"], fields["NodeId"], fields["NodeInstanceId"])
        for existing in self.mSelectPipeline.getNodeList():
            if existing is not node and self.mEditor.node_identity(existing) == new_key:
                self.showStyledMessage("Edit Node", "A node with this NodeName, NodeId, and NodeInstanceId already exists.")
                return
        self.restorePipelineBaseGeometry()
        self.mEditor.update_node_fields(node, fields)
        self.refreshEditedCanvas()

    def handleLinkToolClick(self, port_hit):
        if port_hit is None:
            self.mEditor.pending_src_port = None
            if hasattr(self, "mCanvas"):
                self.mCanvas.setPendingSourcePort(None)
            self.statusBar().showMessage("Link cancelled", 2500)
            self.updateEditControls()
            return
        node, port, direction = port_hit
        if self.mEditor.pending_src_port is None:
            if direction != "output":
                self.showStyledMessage("Create Link", "Select an output port first.")
                return
            self.mEditor.pending_src_port = port
            if hasattr(self, "mCanvas"):
                self.mCanvas.setPendingSourcePort(port)
            self.statusBar().showMessage("Source selected: %s_%s" % (port.getPortName(), port.getPortId()), 4000)
            return
        if direction == "output":
            self.mEditor.pending_src_port = port
            if hasattr(self, "mCanvas"):
                self.mCanvas.setPendingSourcePort(port)
            self.statusBar().showMessage("Source changed: %s_%s" % (port.getPortName(), port.getPortId()), 4000)
            return
        if direction != "input":
            self.showStyledMessage("Create Link", "Select an input port as the destination.")
            return
        src_port = self.mEditor.pending_src_port
        self.mEditor.pending_src_port = None
        if hasattr(self, "mCanvas"):
            self.mCanvas.setPendingSourcePort(None)
        self.restorePipelineBaseGeometry()
        self.mEditor.add_link(src_port, port)
        self.refreshEditedCanvas()
        self.showLinkDetails(src_port, port)

    def deleteCurrentSelection(self):
        if self.mSelectedLink is not None:
            src, dst = self.mSelectedLink
            self.restorePipelineBaseGeometry()
            self.mEditor.delete_link(src, dst)
            self.mSelectedLink = None
            self.refreshEditedCanvas()
            return
        if self.mSelectedNode is not None:
            self.restorePipelineBaseGeometry()
            self.mEditor.delete_node(self.mSelectedNode)
            self.mSelectedNode = None
            self.refreshEditedCanvas()
            return
        self.showStyledMessage("Delete", "Select a node or link before using Delete.")

    def showDeleteContextMenu(self, global_pos, node=None, link=None):
        if not self.mEditMode or not self.mEditor.enabled:
            return
        menu = QMenu(self)
        action = menu.addAction("Delete Link" if link is not None else "Delete Node")
        chosen = menu.exec_(global_pos)
        if chosen is not action:
            return
        if link is not None:
            self.mSelectedLink = link
            self.mSelectedNode = None
        elif node is not None:
            self.mSelectedNode = node
            self.mSelectedLink = None
        self.deleteCurrentSelection()

    def updateTreeWidget(self):
        # Add items to the left-hand tree selection panel
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
        # Initialize the bottom-most QWidget and the Canvas that hosts the NodePainter
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

    def initCanvas(self):
        # Draw the NodePainter on the Canvas
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
        self.mInspectorCollapsed = False
        self.showPipelineDetails()
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
        inspector_width = self.mInspectorDefaultWidth if not self.mInspectorCollapsed else 0
        if self.mExplorerVisible:
            self.mImageBrowserWidth = self.EXPLORER_MIN_WIDTH
            self.mLastExplorerWidth = self.EXPLORER_MIN_WIDTH
            self.mSplitter.setSizes([self.EXPLORER_MIN_WIDTH,
                                     max(600, self.mSplitter.width() - self.EXPLORER_MIN_WIDTH - inspector_width),
                                     inspector_width])
        self.updateCanvasViewportSize()

    def toggleExplorer(self):
        self.mExplorerVisible = self.mExplorerToggleAction.isChecked()
        self.mExplorerToggleAction.setIcon(self.createSidebarToggleIcon(self.mExplorerVisible))
        if self.mExplorerVisible:
            width = max(self.EXPLORER_MIN_WIDTH, self.mLastExplorerWidth)
            total = max(self.mSplitter.width(), width + 600)
            self.mLeftPanel.show()
            inspector_width = self.mInspector.width() if not self.mInspectorCollapsed else 0
            self.mSplitter.setSizes([width, max(600, total - width - inspector_width), inspector_width])
        else:
            if self.mLeftPanel.width() > 0:
                self.mLastExplorerWidth = self.mLeftPanel.width()
            self.mLeftPanel.hide()
            inspector_width = self.mInspector.width() if not self.mInspectorCollapsed else 0
            self.mSplitter.setSizes([0, max(600, self.mSplitter.width() - inspector_width), inspector_width])
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

    def getSnapshotRect(self):
        bounds = self.getNodeBounds()
        if bounds is None:
            return None
        min_x, min_y, max_x, max_y = bounds
        margin = self.SNAPSHOT_MARGIN
        left = max(0, int(min_x - margin))
        top = max(0, int(min_y - margin))
        right = min(self.mCanvas.width(), int(max_x + margin))
        bottom = min(self.mCanvas.height(), int(max_y + margin))
        if right <= left or bottom <= top:
            return None
        return QRect(left, top, right - left, bottom - top)

    def snapshotFileDefaultPath(self):
        name = self.mCurrentPipelineName if self.mCurrentPipelineName else "pipeline"
        safe_name = "".join(ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in name)
        safe_name = safe_name.strip("_") or "pipeline"
        directory = self.getLastOpenDir(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(directory, "%s_snapshot.jpg" % safe_name)

    def buildSnapshotPixmap(self, contentPixmap):
        if contentPixmap.isNull():
            return contentPixmap

        title_height = self.SNAPSHOT_TITLE_HEIGHT
        title_margin_x = 32
        snapshotPixmap = QPixmap(contentPixmap.width(), contentPixmap.height() + title_height)
        snapshotPixmap.fill(QColor(COLORS["bg"]))

        painter = QPainter(snapshotPixmap)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.TextAntialiasing, True)

        title = self.mCurrentPipelineName if self.mCurrentPipelineName else "Pipeline snapshot"
        title_font = font(20, bold=True)
        metrics = QFontMetrics(title_font)
        available_width = max(80, contentPixmap.width() - title_margin_x * 2)
        while metrics.horizontalAdvance(title) > available_width and title_font.pointSize() > 12:
            title_font.setPointSize(title_font.pointSize() - 1)
            metrics = QFontMetrics(title_font)

        title_text = metrics.elidedText(title, Qt.ElideRight, available_width)
        painter.setFont(title_font)
        painter.setPen(QColor(COLORS["text"]))
        painter.drawText(QRect(title_margin_x, 18, available_width, metrics.height() + 6),
                         Qt.AlignLeft | Qt.AlignVCenter,
                         title_text)

        painter.setPen(QPen(QColor(COLORS["accent"]), 3))
        painter.drawLine(title_margin_x, title_height - 16,
                         min(contentPixmap.width() - title_margin_x, title_margin_x + 220),
                         title_height - 16)
        painter.drawPixmap(0, title_height, contentPixmap)
        painter.end()
        return snapshotPixmap

    def snapshotPipeline(self):
        if self.mSelectPipeline is None or len(self.mNodePainterList) == 0:
            self.showStyledMessage("Snapshot", "Please render a pipeline before saving a snapshot.")
            return

        fileName, _ = QFileDialog.getSaveFileName(self,
                                                  "Save pipeline snapshot",
                                                  self.snapshotFileDefaultPath(),
                                                  "JPEG Images (*.jpg *.jpeg)")
        if not fileName:
            return
        if not fileName.lower().endswith((".jpg", ".jpeg")):
            fileName += ".jpg"

        snapshotRect = self.getSnapshotRect()
        if snapshotRect is None:
            self.showStyledMessage("Snapshot", "No pipeline content is available to save.")
            return

        self.mCanvas.update()
        QApplication.processEvents()
        pixmap = self.mCanvas.grab(snapshotRect)
        snapshotPixmap = self.buildSnapshotPixmap(pixmap)
        if snapshotPixmap.isNull() or not snapshotPixmap.save(fileName, "JPEG", 95):
            self.showStyledMessage("Snapshot", "Failed to save the JPEG snapshot.")
            return

        self.statusBar().showMessage("Saved snapshot: %s" % fileName, 5000)

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

    def ensureInspectorVisible(self, force=False):
        if self.mInspectorCollapsed and not force:
            return False
        if not self.mInspector.isVisible():
            self.mInspectorCollapsed = False
            self.mInspector.show()
            left_width = self.mLeftPanel.width() if self.mLeftPanel.isVisible() else 0
            if left_width > 0:
                self.mImageBrowserWidth = left_width
                self.mLastExplorerWidth = left_width
            total = self.mSplitter.width()
            self.mSplitter.setSizes([left_width,
                                     max(600, total - left_width - self.mInspectorDefaultWidth),
                                     self.mInspectorDefaultWidth])
        self.mInspector.raise_()
        self.positionFloatingControls()
        self.updateEditControls()
        return True

    def hideInspector(self):
        if hasattr(self, "mInspector"):
            left_width = self.mLeftPanel.width() if self.mLeftPanel.isVisible() else 0
            if left_width > 0:
                self.mImageBrowserWidth = left_width
                self.mLastExplorerWidth = left_width
            self.mInspectorCollapsed = True
            self.mSplitter.setSizes([left_width,
                                     max(600, self.mSplitter.width() - left_width),
                                     0])
            self.mInspector.hide()
        self.positionFloatingControls()
        self.updateEditControls()

    def toggleInspectorPanel(self):
        if not hasattr(self, "mInspector"):
            return
        if self.mInspectorCollapsed or not self.mInspector.isVisible():
            self.mInspectorCollapsed = False
            if self.mInspectorMode == "node" and self.mSelectedNode is not None:
                self.showNodeDetails(self.mSelectedNode)
            elif self.mInspectorMode == "link" and self.mSelectedLink is not None:
                self.showLinkDetails(self.mSelectedLink[0], self.mSelectedLink[1])
            else:
                self.showPipelineDetails()
            self.ensureInspectorVisible(force=True)
        else:
            self.hideInspector()

    def toggleInspectorFromAction(self, checked=None):
        if checked:
            self.mInspectorCollapsed = False
            self.toggleInspectorPanel()
        else:
            self.hideInspector()

    def setInspectorTree(self, title, subtitle):
        if not self.ensureInspectorVisible():
            return False
        self.mInspectorTitle.setText(title)
        self.mInspectorSubtitle.setText(subtitle)
        self.mInspectorEditing = True
        self.mInspectorBody.clear()
        self.mInspectorEditing = False
        self.positionInspectorDrawer()
        return True

    def addTreeItem(self, parent, field, value="", editable=False, edit_data=None):
        item = QTreeWidgetItem(parent if parent is not None else self.mInspectorBody)
        item.setText(0, str(field))
        item.setText(1, "" if value is None else str(value))
        item.setForeground(0, QColor(COLORS["text"]))
        item.setForeground(1, QColor(COLORS["text_muted"]))
        if editable:
            item.setFlags(item.flags() | Qt.ItemIsEditable)
            item.setData(1, Qt.UserRole, edit_data)
            item.setForeground(1, QColor(COLORS["text"]))
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

    def addNodeTree(self, parent, node, title=None, editable=False):
        node_item = self.addTreeItem(parent, title or self.formatNodeName(node), "")
        self.addTreeItem(node_item, "NodeName", node.getNodeName(), editable, ("node", node, "NodeName"))
        self.addTreeItem(node_item, "NodeId", node.getNodeId(), editable, ("node", node, "NodeId"))
        self.addTreeItem(node_item, "NodeInstance", node.getNodeInstance(), editable, ("node", node, "NodeInstance"))
        self.addTreeItem(node_item, "NodeInstanceId", node.getNodeInstanceId(), editable, ("node", node, "NodeInstanceId"))
        self.addTreeItem(node_item, "Level", ", ".join(map(str, node.getNodeLevel())))
        self.addTreeItem(node_item, "InputPortCount", len(node.getInputPort()), editable,
                         ("port_count", node, "input"))
        self.addTreeItem(node_item, "OutputPortCount", len(node.getOutputPort()), editable,
                         ("port_count", node, "output"))

        input_item = self.addTreeItem(node_item, "InputPorts", len(node.getInputPort()))
        for index, port in enumerate(node.getInputPort()):
            self.addPortTree(input_item, port, editable=editable, edit_node=node, direction="input", port_index=index)

        output_item = self.addTreeItem(node_item, "OutputPorts", len(node.getOutputPort()))
        for index, port in enumerate(node.getOutputPort()):
            self.addPortTree(output_item, port, editable=editable, edit_node=node, direction="output", port_index=index)

        prop_item = self.addTreeItem(node_item, "Properties", len(node.getNodeProp()))
        for idx, prop in enumerate(node.getNodeProp()):
            one_prop = self.addTreeItem(prop_item, "Property %d" % (idx + 1), "")
            self.addTreeItem(one_prop, "Name", prop[0])
            self.addTreeItem(one_prop, "Id", prop[1])
            self.addTreeItem(one_prop, "Type", prop[2])
            self.addTreeItem(one_prop, "Value", prop[3])
        return node_item

    def addPortTree(self, parent, port, title=None, editable=False, edit_node=None, direction=None, port_index=None):
        port_item = self.addTreeItem(parent, title or "%s_%s" % (port.getPortName(), port.getPortId()), "")
        self.addTreeItem(port_item, "PortName", port.getPortName(), editable,
                         ("port", edit_node, direction, port_index, "PortName") if editable else None)
        self.addTreeItem(port_item, "PortId", port.getPortId(), editable,
                         ("port", edit_node, direction, port_index, "PortId") if editable else None)
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

    def resizedPortFields(self, ports, count, prefix):
        resized = [(port.getPortName(), port.getPortId()) for port in ports[:count]]
        for index in range(len(resized), count):
            resized.append(("%s_%d" % (prefix, index), str(index)))
        return resized

    def handleInspectorItemChanged(self, item, column):
        if self.mInspectorEditing or column != 1 or not self.mEditMode or not self.mEditor.enabled:
            return
        edit_data = item.data(1, Qt.UserRole)
        if edit_data is None:
            return
        kind = edit_data[0]
        node = edit_data[1]
        if node is None:
            return
        fields = {
            "NodeName": node.getNodeName(),
            "NodeId": node.getNodeId(),
            "NodeInstance": node.getNodeInstance(),
            "NodeInstanceId": node.getNodeInstanceId(),
            "InputPorts": [(port.getPortName(), port.getPortId()) for port in node.getInputPort()],
            "OutputPorts": [(port.getPortName(), port.getPortId()) for port in node.getOutputPort()]
        }
        value = item.text(1).strip()
        if kind == "node":
            fields[edit_data[2]] = value
        elif kind == "port_count":
            _, _, direction = edit_data
            current_ports = node.getInputPort() if direction == "input" else node.getOutputPort()
            fallback = len(current_ports)
            count = self.normalizedPortCount(value, fallback)
            if str(count) != value:
                self.mInspectorEditing = True
                item.setText(1, str(count))
                self.mInspectorEditing = False
            if direction == "input":
                fields["InputPorts"] = self.resizedPortFields(current_ports, count, "input")
            else:
                fields["OutputPorts"] = self.resizedPortFields(current_ports, count, "output")
        elif kind == "port":
            _, _, direction, port_index, field_name = edit_data
            port_list_name = "InputPorts" if direction == "input" else "OutputPorts"
            ports = list(fields[port_list_name])
            if port_index is None or port_index >= len(ports):
                return
            name, port_id = ports[port_index]
            ports[port_index] = (value, port_id) if field_name == "PortName" else (name, value)
            fields[port_list_name] = ports
        self.applyInspectorNodeEdit(node, fields)

    def applyInspectorNodeEdit(self, node, fields):
        if not self.mEditor.enabled or node is None:
            return
        new_key = (fields["NodeName"], fields["NodeId"], fields["NodeInstanceId"])
        for existing in self.mSelectPipeline.getNodeList():
            if existing is not node and self.mEditor.node_identity(existing) == new_key:
                self.showStyledMessage("Edit Node", "A node with this NodeName, NodeId, and NodeInstanceId already exists.")
                self.showNodeDetails(node)
                return
        self.restorePipelineBaseGeometry()
        self.mEditor.update_node_fields(node, fields)
        self.refreshEditedCanvas()
        self.showNodeDetails(node)
        self.statusBar().showMessage("Node updated", 3000)

    def showPipelineDetails(self):
        self.mInspectorMode = "pipeline"
        self.mSelectedLink = None
        self.setSelectedNode(None)
        if hasattr(self, "mCanvas"):
            self.mCanvas.setSelectedLink(None, None)
        if not self.setInspectorTree("Pipeline Details", self.mCurrentPipelineName or "Background selection"):
            self.updateEditControls()
            return
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
        self.updateEditControls()

    def showNodeDetails(self, node):
        self.mInspectorMode = "node"
        self.mSelectedLink = None
        self.setSelectedNode(node)
        if hasattr(self, "mCanvas"):
            self.mCanvas.setSelectedLink(None, None)
        if not self.setInspectorTree("Node Details", self.formatNodeName(node)):
            self.updateEditControls()
            return
        self.mInspectorEditing = True
        root = self.addNodeTree(None, node, editable=(self.mEditMode and self.mEditor.enabled))
        self.mInspectorEditing = False
        self.mInspectorBody.collapseAll()
        root.setExpanded(True)
        self.updateEditControls()

    def showLinkDetails(self, src_port, dst_port):
        self.mInspectorMode = "link"
        self.mSelectedLink = (src_port, dst_port)
        self.setSelectedNode(None)
        if hasattr(self, "mCanvas"):
            self.mCanvas.setSelectedLink(src_port, dst_port)
        src_node = self.findNodeForPort(src_port)
        dst_node = self.findNodeForPort(dst_port)
        if not self.setInspectorTree("Link Details",
                                     "%s -> %s" % (self.formatNodeName(src_node), self.formatNodeName(dst_node))):
            self.updateEditControls()
            return
        root = self.addLinkTree(None, src_port, dst_port)
        self.mInspectorBody.expandAll()
        self.updateEditControls()

    def isCanvasSurface(self, obj):
        return obj in (getattr(self, "mCanvasViewport", None),
                       getattr(self, "imageWindow", None),
                       getattr(self, "mCanvas", None))

    def updateHoveredLink(self, obj, event):
        if not hasattr(self, "mCanvas") or not hasattr(event, "pos"):
            return
        if obj == self.mCanvas:
            canvas_pos = event.pos()
        elif self.isCanvasSurface(obj):
            canvas_pos = self.mCanvas.mapFromGlobal(obj.mapToGlobal(event.pos()))
        else:
            self.mCanvas.setHoveredLink(None, None)
            return
        hit = self.mCanvas.hitTestLink(canvas_pos)
        if hit is None:
            self.mCanvas.setHoveredLink(None, None)
        else:
            self.mCanvas.setHoveredLink(hit[0], hit[1])

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
        QMessageBox.information(self, 'QListView', 'You selected: ' + self.list[item.row()])

    def recieveChildMsgSlot(self, msg):
        # Callback registered into nodePainter to receive its mouse-press events
        # Currently used in mainWindow to resolve the conflict between hover-showing-prop and press-dragging-node
        msgType, msgValue = msg.getMsg()
        if msgType == MsgType.LeftButton:
            self.leftPress = msgValue
            if self.leftPress == False:
                self.saveCurrentPipelineLayout()
                self.mCanvas.update()
        elif msgType == MsgType.WheelMouse:
            self.mCanvas.update()

    def mousePressEvent(self, event):
        # Override the mouse press event (single click)
        if event.button() == Qt.LeftButton:
            if self.mImageBrowserChange == False:
                Utils.LogI(self.TAG, ("mousePressEvent...", self.m_drag))
                self.m_drag = True
                self.m_DragPosition = event.globalPos() - self.mCanvas.pos()
                self.setCursor(QCursor(Qt.OpenHandCursor))
                event.accept()
            else:
                self.mImageBrowserStart = event.pos()

    def wheelEvent(self, event):
        angle = event.angleDelta() / 8    # Returns a QPoint with the wheel scroll amount; unit is 1/8 degree
        angleX = angle.x()                # Horizontal scroll distance (not used here)
        angleY = angle.y()                # Vertical scroll distance
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
        else:                                                                  # Wheel scrolled down
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

    def getmImageBrowserWidth(self):
        return self.mImageBrowserWidth

    def showNodePorp(self, pos):
        num = 0
        propMsg = ""
        enable = False
        if self.mImageBrowserChange is False and self.mSelectPipeline is not None:
            canvasRelativePos = self.mCanvas.mapFrom(self, pos)
            for node in self.mSelectPipeline.getNodeList():
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
                            self.timer.start(800)
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

    def eventFilter(self, object, event):
        if event.type() in (QEvent.DragEnter, QEvent.DragMove):
            if self.droppedPipelineFiles(event):
                event.acceptProposedAction()
                return True

        if event.type() == QEvent.Drop:
            files = self.droppedPipelineFiles(event)
            if files:
                self.loadPipelineFiles(files)
                event.acceptProposedAction()
                return True

        # Handle QEvent.HoverMove: when the cursor is near the tree selection panel, change to a left-right resize cursor
        menubar = getattr(self, "mMenuBar", None)
        if object is menubar and event.type() in (QEvent.MouseMove, QEvent.HoverMove) and self.isMenuPopupOpen():
            return True

        if event.type() in (QEvent.HoverMove, QEvent.MouseMove):
            if self.isCanvasSurface(object) or object in self.mNodePainterList:
                self.updateHoveredLink(object, event)
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

        if object in self.mNodePainterList and event.type() == QEvent.MouseButtonPress and event.button() == Qt.RightButton:
            if self.mEditMode and self.mEditor.enabled:
                self.showDeleteContextMenu(event.globalPos(), node=object.mNode)
            else:
                self.showNodeDetails(object.mNode)
            event.accept()
            return True

        if self.isCanvasSurface(object) and event.type() == QEvent.MouseButtonPress and event.button() == Qt.RightButton:
            if object == getattr(self, "mCanvas", None):
                hit = self.mCanvas.hitTestLink(event.pos())
                if self.mEditMode and self.mEditor.enabled and hit is not None:
                    self.showDeleteContextMenu(event.globalPos(), link=hit)
                else:
                    if self.mEditMode and self.mEditor.enabled and self.mEditor.pending_src_port is not None:
                        self.handleLinkToolClick(None)
                    elif hit is None:
                        self.showPipelineDetails()
                    else:
                        self.showLinkDetails(hit[0], hit[1])
            elif object in (getattr(self, "mCanvasViewport", None), getattr(self, "imageWindow", None)):
                if self.mEditMode and self.mEditor.enabled and self.mEditor.pending_src_port is not None:
                    self.handleLinkToolClick(None)
                else:
                    self.showPipelineDetails()
            event.accept()
            return True

        if object in self.mNodePainterList and event.type() == QEvent.MouseButtonPress and event.button() == Qt.LeftButton:
            if self.mEditMode and self.mEditor.enabled:
                canvas_pos = object.pos() + event.pos()
                port_hit = self.mCanvas.hitTestPort(canvas_pos)
                if port_hit is not None:
                    self.handleLinkToolClick(port_hit)
                    event.accept()
                    return True
                else:
                    self.showNodeDetails(object.mNode)
                    return False

        if self.isCanvasSurface(object) and event.type() == QEvent.MouseButtonPress and event.button() == Qt.LeftButton:
            if object == getattr(self, "mCanvas", None):
                if self.mEditMode and self.mEditor.enabled:
                    port_hit = self.mCanvas.hitTestPort(event.pos())
                    if port_hit is not None:
                        self.handleLinkToolClick(port_hit)
                        event.accept()
                        return True
                    if self.mEditor.pending_src_port is not None:
                        self.handleLinkToolClick(None)
                        event.accept()
                        return True
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
        if self.mEditMode and self.mEditor.enabled and keyEvent.modifiers() & Qt.ControlModifier:
            if keyEvent.key() == Qt.Key_Z:
                self.undoEdit()
                keyEvent.accept()
                return
            if keyEvent.key() == Qt.Key_Y:
                self.redoEdit()
                keyEvent.accept()
                return
        if keyEvent.key() == Qt.Key_Delete and self.mEditMode and self.mEditor.enabled:
            if self.mSelectedNode is not None or self.mSelectedLink is not None:
                self.deleteCurrentSelection()
                keyEvent.accept()
                return
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
        elif keyEvent.key() == Qt.Key_Control:
            self.mKeyCtrlStatus = False
            msg = ComMsg(MsgType.KeyCtrl, False)
            self.mSignal.emit(msg)

    def resizeEvent(self, event):
        self.updateBrowserSize()
        self.updateCanvasContext()
        self.positionSnapshotButton()
