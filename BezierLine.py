from PyQt5.QtCore import QPoint, QPointF, Qt
from PyQt5.QtGui import QPainterPath, QPen, QColor


class BezierLineRenderer:
    TAG = "BezierLineRenderer"

    @staticmethod
    def draw_bezier_link(painter, src_port, dst_port, pen, radius=5):
        if src_port is None or dst_port is None:
            return
        if src_port.getPortPos() is None or dst_port.getPortPos() is None:
            return
        if src_port.getParentNodePos() is None or dst_port.getParentNodePos() is None:
            return

        start_point = src_port.getPortPos() + src_port.getParentNodePos() + QPoint(src_port.getWidth(), 0)
        end_point = dst_port.getPortPos() + dst_port.getParentNodePos()

        path = BezierLineRenderer.create_bezier_path(start_point, end_point)

        link_pen = QPen(pen)
        link_color = QColor(pen.color())
        link_color.setAlpha(218)
        link_pen.setColor(link_color)
        link_pen.setWidth(max(2, pen.width()))
        link_pen.setCapStyle(Qt.RoundCap)
        link_pen.setJoinStyle(Qt.RoundJoin)

        painter.setPen(link_pen)
        painter.setBrush(QColor(0, 0, 0, 0))
        painter.drawPath(path)

        BezierLineRenderer.draw_endpoint_marker(painter, start_point, link_color, radius)
        BezierLineRenderer.draw_endpoint_marker(painter, end_point, link_color, radius)

    @staticmethod
    def create_bezier_path(start_point, end_point):
        path = QPainterPath()
        path.moveTo(QPointF(start_point))

        dx = abs(end_point.x() - start_point.x())
        offset = max(50, dx * 0.4)

        control1 = QPointF(start_point.x() + offset, start_point.y())
        control2 = QPointF(end_point.x() - offset, end_point.y())

        path.cubicTo(control1, control2, QPointF(end_point))
        return path

    @staticmethod
    def draw_endpoint_marker(painter, point, color, radius=5):
        marker_color = QColor(color)
        marker_color.setAlpha(170)
        painter.setPen(QPen(marker_color, 1))
        painter.setBrush(QColor(0, 0, 0, 0))
        painter.drawEllipse(QPointF(point), max(3, radius - 2), max(3, radius - 2))
