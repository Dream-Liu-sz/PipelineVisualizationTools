from PyQt5.QtGui import QColor, QFont


COLORS = {
    "bg": "#111111",
    "panel": "#181818",
    "panel_alt": "#202020",
    "card": "#242424",
    "card_soft": "#2D2D2D",
    "border": "#3A3A3A",
    "border_strong": "#5A5A5A",
    "text": "#F2F2F2",
    "text_muted": "#B8B8B8",
    "accent": "#38BDF8",
    "accent_soft": "#0EA5E9",
    "success": "#34D399",
    "warning": "#F59E0B",
    "danger": "#F87171",
    "grid": "#1E1E1E",
    "grid_major": "#2A2A2A",
    "shadow": "#050505",
}


NODE_COLORS = [
    QColor("#38BDF8"),
    QColor("#34D399"),
    QColor("#F59E0B"),
    QColor("#A78BFA"),
    QColor("#F472B6"),
    QColor("#22D3EE"),
    QColor("#FB7185"),
    QColor("#84CC16"),
    QColor("#60A5FA"),
    QColor("#F97316"),
    QColor("#2DD4BF"),
    QColor("#E879F9"),
]


def font(point_size=10, bold=False, mono=False):
    family = "Cascadia Mono" if mono else "Microsoft YaHei UI"
    qfont = QFont(family)
    qfont.setPointSize(point_size)
    qfont.setBold(bold)
    return qfont


def node_color(index):
    return NODE_COLORS[index % len(NODE_COLORS)]


def tooltip_stylesheet():
    return """
        QLabel {
            color: #F2F2F2;
            background-color: rgba(24, 24, 24, 238);
            border: 1px solid #5A5A5A;
            border-radius: 12px;
            padding: 12px 14px;
            line-height: 145%;
        }
    """


def app_stylesheet():
    return """
        QMainWindow {
            background: #111111;
            color: #F2F2F2;
            font-family: "Microsoft YaHei UI";
        }

        QMenuBar {
            background: #111111;
            color: #D6D6D6;
            padding: 4px 8px;
            border-bottom: 1px solid #2A2A2A;
        }

        QMenuBar::item {
            padding: 7px 12px;
            border-radius: 8px;
        }

        QMenuBar::item:selected {
            background: #242424;
            color: #FFFFFF;
        }

        QMenu {
            background: #181818;
            color: #F2F2F2;
            border: 1px solid #3A3A3A;
            padding: 6px;
        }

        QMenu::item {
            padding: 8px 24px;
            border-radius: 6px;
        }

        QMenu::item:selected {
            background: #3A3A3A;
            color: #FFFFFF;
        }

        QScrollBar:vertical {
            background: transparent;
            width: 10px;
            margin: 10px 0 10px 0;
        }

        QScrollBar::handle:vertical {
            background: #050505;
            border: 1px solid #242424;
            border-radius: 5px;
            min-height: 28px;
        }

        QScrollBar::handle:vertical:hover {
            background: #0A0A0A;
            border-color: #3A3A3A;
        }

        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {
            background: #050505;
            border: 1px solid #242424;
            border-radius: 5px;
            height: 10px;
            subcontrol-origin: margin;
        }

        QScrollBar::add-line:vertical {
            subcontrol-position: bottom;
        }

        QScrollBar::sub-line:vertical {
            subcontrol-position: top;
        }

        QScrollBar::up-arrow:vertical,
        QScrollBar::down-arrow:vertical,
        QScrollBar::add-page:vertical,
        QScrollBar::sub-page:vertical {
            background: transparent;
            border: 0;
        }

        QScrollBar:horizontal {
            background: transparent;
            height: 10px;
            margin: 0 10px 0 10px;
        }

        QScrollBar::handle:horizontal {
            background: #050505;
            border: 1px solid #242424;
            border-radius: 5px;
            min-width: 28px;
        }

        QScrollBar::handle:horizontal:hover {
            background: #0A0A0A;
            border-color: #3A3A3A;
        }

        QScrollBar::add-line:horizontal,
        QScrollBar::sub-line:horizontal {
            background: #050505;
            border: 1px solid #242424;
            border-radius: 5px;
            width: 10px;
            subcontrol-origin: margin;
        }

        QScrollBar::add-line:horizontal {
            subcontrol-position: right;
        }

        QScrollBar::sub-line:horizontal {
            subcontrol-position: left;
        }

        QScrollBar::left-arrow:horizontal,
        QScrollBar::right-arrow:horizontal,
        QScrollBar::add-page:horizontal,
        QScrollBar::sub-page:horizontal {
            background: transparent;
            border: 0;
        }

        QPushButton#menuIconButton {
            background: #111111;
            border: 1px solid #3A3A3A;
            border-radius: 8px;
            padding: 4px;
        }

        QPushButton#menuIconButton:hover {
            background: #202020;
            border-color: #5A5A5A;
        }

        QPushButton#menuIconButton:checked {
            background: #181818;
            border-color: #7A7A7A;
        }

        QWidget#leftPanel,
        QWidget#rightPanel,
        QWidget#canvasViewport {
            background: #111111;
        }

        QLabel#panelTitle {
            color: #FFFFFF;
            font-size: 17px;
            font-weight: 700;
        }

        QLabel#panelHint,
        QLabel#contextSubtle,
        QLabel#emptyHint {
            color: #B8B8B8;
        }

        QLabel#contextTitle {
            color: #FFFFFF;
            font-size: 16px;
            font-weight: 700;
        }

        QLabel#metricPill,
        QPushButton#toolbarButton {
            color: #E8E8E8;
            background: #242424;
            border: 1px solid #3A3A3A;
            border-radius: 13px;
            padding: 5px 10px;
        }

        QPushButton#toolbarButton:hover {
            border-color: #7A7A7A;
            background: #2D2D2D;
        }

        QLineEdit#treeSearch {
            color: #F2F2F2;
            background: #202020;
            border: 1px solid #3A3A3A;
            border-radius: 12px;
            padding: 9px 12px;
            selection-background-color: #5A5A5A;
        }

        QLineEdit#treeSearch:focus {
            border-color: #7A7A7A;
            background: #242424;
        }

        QTreeWidget {
            color: #D6D6D6;
            background: #181818;
            border: 1px solid #2A2A2A;
            border-radius: 14px;
            padding: 8px;
            outline: 0;
        }

        QTreeWidget::item {
            min-height: 30px;
            padding: 5px 8px;
            border-radius: 8px;
        }

        QTreeWidget::item:hover {
            background: #242424;
            color: #FFFFFF;
        }

        QTreeWidget::item:selected {
            background: #3A3A3A;
            color: #FFFFFF;
        }

        QSplitter::handle {
            background: #2A2A2A;
            width: 4px;
        }

        QStatusBar {
            color: #B8B8B8;
            background: #111111;
            border-top: 1px solid #2A2A2A;
        }

        QFrame#inspectorDrawer {
            background: #181818;
            border: 1px solid #3A3A3A;
            border-radius: 14px;
        }

        QLabel#inspectorTitle {
            color: #FFFFFF;
            font-size: 15px;
            font-weight: 700;
        }

        QLabel#inspectorSubtitle {
            color: #B8B8B8;
        }

        QTreeWidget#inspectorBody {
            color: #E8E8E8;
            background: #202020;
            border: 1px solid #3A3A3A;
            border-radius: 10px;
            padding: 8px;
            selection-background-color: #5A5A5A;
        }

        QTreeWidget#inspectorBody::item {
            min-height: 24px;
            padding: 3px 4px;
        }
    """
