#!/usr/bin/env python3
# coding: utf-8
# -*- coding: utf-8 -*-

from PyQt5 import uic, QtGui, QtCore, Qt, QtWidgets
import sys
import sh
import  webbrowser as wb
import numpy as np
import time
import gesture_classifier as gc

UI_FILE = 'gesture_recognizer.ui'
HELP_TEXT = 'HELP TEXT'

# points to classifier need to of Point class type


class DrawWidget(QtWidgets.QWidget):
    def __init__(self, parent, x, y, width=420, height=400):
        super().__init__(parent)
        self.setGeometry(x, y, width, height)
        self.resize(width, height)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.drawing = False
        self.points = []
        self.times = []

        self.classifier = gc.DollarOneGestureRecognizer()

        self.setMouseTracking(True)  # only get events when button is pressed
        self.init_ui()

    def init_ui(self):
        self.show()

    def mousePressEvent(self, ev):
        if ev.button() == QtCore.Qt.LeftButton:
            self.drawing = True
            self.points = []
            self.update()

    def mouseReleaseEvent(self, ev):
        if ev.button() == QtCore.Qt.LeftButton:
            self.drawing = False

            if not len(self.points) == 0:
                pts = []

                for p in self.points:
                    x, y = p
                    pts.append(gc.Point(x, y))

                result = self.classifier.recognize(pts, False)

                print(result.name)
                print(result.score)

            self.update()

    def mouseMoveEvent(self, ev):
        if self.drawing:

            x = ev.x()
            y = ev.y()

            self.points.append((x, y))
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


class Window(Qt.QMainWindow):
    """
    class responsible for the UI
    """

    def __init__(self):
        """
        constructor
        UI-elements setup and variables setup

        :return: void
        """

        super(Window, self).__init__()
        self.win = uic.loadUi(UI_FILE)
        self.draw_widget = DrawWidget(self.win, 240, 30)


        self.gesture_data = []
        self.wm = None

        self.gesture_list_widget = self.win.listWidget

        self.add_btn = self.win.btn_add
        self.about_btn = self.win.btn_about

        self.add_btn.clicked.connect(self.add)
        self.about_btn.clicked.connect(self.show_readme)

        self.setup_gesture_list_widget()

        self.win.show()

        self.gesture_list_widget.setContextMenuPolicy(
            QtCore.Qt.ActionsContextMenu)

    def setup_gesture_list_widget(self):
        self.gesture_list_widget.setContextMenuPolicy(
            QtCore.Qt.ActionsContextMenu)

        self.retrain_action = Qt.QAction("Retrain Gesture", None)
        self.retrain_action.triggered.connect(self.retrain)
        self.remove_action = Qt.QAction("Remove Gesture", None)
        self.remove_action.triggered.connect(self.remove)

        self.gesture_list_widget.addAction(self.retrain_action)
        self.gesture_list_widget.addAction(self.remove_action)

    def add(self):
        gesture_name, ok = Qt.QInputDialog.getText(self.win, 'Input Dialog',
                                    'Enter Gesture Name')

        self.gesture_list_widget.addItem(Qt.QListWidgetItem(gesture_name))

        # train the thing here

    def retrain(self):
        print('retrain')

    def remove(self):
        print('remove')

    def show_readme(self):
        """
        displays the message showing some readme text on how to use this app.
        (it is a prototype and therefore probably not robust)

        :return: void
        """

        msg = Qt.QMessageBox()
        msg.setIcon(Qt.QMessageBox.Information)

        msg.setText(HELP_TEXT)
        msg.setWindowTitle('About')
        msg.setStandardButtons(Qt.QMessageBox.Ok)
        msg.exec_()


def main():
    """
    entry point

    :return: void
    """

    app = Qt.QApplication(sys.argv)
    win = Window()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
