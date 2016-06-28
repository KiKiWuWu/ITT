#!/usr/bin/env python3
# coding: utf-8
# -*- coding: utf-8 -*-

from PyQt5 import Qt, QtGui, QtCore, QtWidgets
import sys
import pylab
import time


class DrawWidget(QtWidgets.QWidget):

    def __init__(self, width=800, height=800):
        super().__init__()
        self.resize(width, height)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.drawing = False
        self.points = []
        self.times = []

        self.g_id = 1
        self.i_id = 0
        # QtGui.QCursor.setPos(self.mapToGlobal(QtCore.QPoint(*self.start_pos)))
        self.setMouseTracking(True)  # only get events when button is pressed
        self.init_ui()
        print('g_id;i_id;x_coord;y_coord;timestamp')

    def init_ui(self):
        self.text = "Please click on the target"
        self.setWindowTitle('Drawable')
        self.show()

    def mousePressEvent(self, ev):
        if ev.button() == QtCore.Qt.LeftButton:
            self.i_id += 1
            self.drawing = True
            self.points = []
            self.data = []
            self.update()

    def mouseReleaseEvent(self, ev):
        if ev.button() == QtCore.Qt.LeftButton:
            self.drawing = False
            self.update()
            self.log_data()

    def mouseMoveEvent(self, ev):
        if self.drawing:

            x = ev.x()
            y = ev.y()

            self.points.append((x, y))
            self.data.append([self.g_id, self.i_id, x, y, time.time()])
            self.update()

    def poly(self, pts):
        return QtGui.QPolygonF(map(lambda p: QtCore.QPointF(*p), pts))

    def paintEvent(self, ev):
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.setBrush(QtGui.QColor(0, 0, 0))
        qp.drawRect(ev.rect())
        qp.setBrush(QtGui.QColor(20, 255, 190))
        qp.setPen(QtGui.QColor(0, 155, 0))
        qp.drawPolyline(self.poly(self.points))
        for point in self.points:
            qp.drawEllipse(point[0]-1, point[1] - 1, 2, 2)
        qp.end()

    def log_data(self):
        if len(self.data) > 5:  # eliminate points
            for l in self.data:
                out = list_to_string_for_csv(l)
                print(out)


def list_to_string_for_csv(l):
    out = ''

    for v in l:
        out += (str(v) + ";")

    return out[0: len(out) - 1]

def main():
    app = Qt.QApplication(sys.argv)
    dw = DrawWidget()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()