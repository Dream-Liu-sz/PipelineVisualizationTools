from PyQt5.QtCore import QPoint, QPointF
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

        painter.setPen(pen)
        painter.setBrush(QColor(0, 0, 0, 0))
        painter.drawPath(path)

        BezierLineRenderer.draw_port_dot(painter, start_point, pen.color(), radius)
        BezierLineRenderer.draw_port_dot(painter, end_point, pen.color(), radius)

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
    def draw_port_dot(painter, point, color, radius=5):
        painter.setPen(QPen(color))
        painter.setBrush(color)
        painter.drawEllipse(QPointF(point), radius, radius)
