#!/usr/bin/env python3
# coding: utf-8
# -*- coding: utf-8 -*-

from PyQt5 import uic, QtGui, QtCore, Qt, QtWidgets
import sys
import sh
import webbrowser as wb
import gesture_classifier as gc

UI_FILE = 'gesture_recognizer.ui'
HELP_TEXT = 'HELP TEXT'


class DrawWidget(QtWidgets.QWidget):
    recognize_trigger = Qt.pyqtSignal()

    def __init__(self, parent, x, y, width=420, height=400):
        """
        constructor

        :param parent: the widget's parent
        :param x: the widget's x coordinate
        :param y: the widget's y coordinate
        :param width: the widget's width
        :param height: the widget's height

        :return: void
        """

        super().__init__(parent)
        self.setGeometry(x, y, width, height)
        self.resize(width, height)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.drawing = False
        self.points = []
        self.points_for_classifier = []

        self.classifier = gc.DollarOneGestureRecognizer()

        self.setMouseTracking(True)
        self.show()

    def mousePressEvent(self, ev):
        """
        overridden

        callback for mouse press
        activates the drawing and clears the needed datastructures

        :param ev: the fired event
        :return: void
        """

        if ev.button() == QtCore.Qt.LeftButton:
            self.drawing = True
            self.points = []
            self.points_for_classifier = []
            self.update()

    def mouseReleaseEvent(self, ev):
        """
        overridden

        callback fpr mouse release
        saves all gathered points and emits a signal for the processing
        callback function

        :param ev: the fired event

        :return: void
        """

        if ev.button() == QtCore.Qt.LeftButton:
            self.drawing = False

            if not len(self.points) == 0:
                for p in self.points:
                    x, y = p
                    self.points_for_classifier.append(gc.Point(x, y))

                self.recognize_trigger.emit()

            self.update()

    def mouseMoveEvent(self, ev):
        """
        overridden

        callback for mouse move
        saves the points retrieved from the event to a datastructure

        :param ev: the fired event

        :return: void
        """

        if self.drawing:

            x = ev.x()
            y = ev.y()

            self.points.append((x, y))
            self.update()

    def poly(self, pts):
        """
        creates a polygon based on the given points

        :param pts: the points of the polygon

        :return: a polygon object
        """

        return QtGui.QPolygonF(map(lambda p: QtCore.QPointF(*p), pts))

    def paintEvent(self, ev):
        """
        overridden

        callback for paint event
        draws a polygon to the widgetss

        :param ev: the fired event

        :return: void
        """

        qp = QtGui.QPainter()
        qp.begin(self)
        qp.setBrush(QtGui.QColor(0, 0, 0))
        qp.drawRect(ev.rect())
        qp.setBrush(QtGui.QColor(20, 255, 190))
        qp.setPen(QtGui.QColor(0, 155, 0))
        qp.drawPolyline(self.poly(self.points))
        for point in self.points:
            qp.drawEllipse(point[0] - 1, point[1] - 1, 2, 2)


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

        self.draw_widget.recognize_trigger.connect(self.perform_recognition)

        self.gesture_data = []
        self.gesture_actions = ['Macarena', 'GOT_Quote', 'Shutdown']

        self.gesture_list_widget = self.win.listWidget

        self.add_btn = self.win.btn_add
        self.about_btn = self.win.btn_about

        self.add_btn.clicked.connect(self.add)
        self.about_btn.clicked.connect(self.show_readme)

        self.setup_gesture_list_widget()

        self.is_training = False
        self.notification_l = self.win.label_notification

        self.gesture_action_relation = {}

        self.win.show()

        self.gesture_list_widget.setContextMenuPolicy(
            QtCore.Qt.ActionsContextMenu)

    def setup_gesture_list_widget(self):
        """
        adds right click context menu actions to the list widget items

        :return: void
        """
        self.gesture_list_widget.setContextMenuPolicy(
            QtCore.Qt.ActionsContextMenu)

        self.retrain_action = Qt.QAction("Retrain Gesture", None)
        self.retrain_action.triggered.connect(self.retrain)
        self.remove_action = Qt.QAction("Remove Gesture", None)
        self.remove_action.triggered.connect(self.remove)

        self.gesture_list_widget.addAction(self.retrain_action)
        self.gesture_list_widget.addAction(self.remove_action)

    def add(self):
        """
        adds a gesture to the list widget and saves its corresponding action
        in a dictionary

        :return:
        """

        gesture_name, ok = Qt.QInputDialog.getText(self.win, 'Add Gesture',
                                                   'Enter Gesture Name')

        action, ok = Qt.QInputDialog.getItem(self.win, 'Action Chooser',
                                             'Choose an action',
                                             self.gesture_actions)

        self.gesture_action_relation[gesture_name] = action

        self.gesture_list_widget.addItem(Qt.QListWidgetItem(gesture_name))

        self.notification_l.setText('Added Gesture: ' + gesture_name +
                                    ' with Action: ' + action + '. Retrain!')

    def retrain(self):
        """
        sets the the trainings flag to true

        :return: void
        """

        name = self.gesture_list_widget.currentItem().text()

        self.is_training = True
        self.notification_l.setText('Retraining (' + name + ')')

    def remove(self):
        """
        removes a item from the list widget and delete from the trained
        gestures

        :return: void

        """
        index = self.gesture_list_widget.currentRow()
        name = self.gesture_list_widget.currentItem().text()

        self.gesture_list_widget.takeItem(index)
        self.draw_widget.classifier.delete_gesture(index)

        self.notification_l.setText('Deleted Gesture: ' + name)

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

    def perform_recognition(self):
        """
        trains the classifier if the training flags is set or classifies the
        set of drawn points and performs their assigned action

        :return: void
        """

        points = self.draw_widget.points_for_classifier

        if self.is_training:
            self.is_training = False

            name = self.gesture_list_widget.currentItem().text()
            points = self.draw_widget.points_for_classifier

            self.draw_widget.classifier.add_gesture(name, points)
            self.notification_l.setText('Training done! You can use the '
                                        'gesture now!')
        else:
            result = self.draw_widget.classifier.recognize(points)

            self.perform_action(result.name)

    def perform_action(self, gesture):
        """
        performs an action based on the given gesture

        :param gesture: the gesture which assigned action has to be performed

        :return: void
        """

        if gesture not in self.gesture_action_relation:
            return

        if self.gesture_actions[0] == self.gesture_action_relation[gesture]:
            wb.open('https://www.youtube.com/watch?v=XiBYM6g8Tck')
            self.notification_l.setText('Playing Macarena in Browser (' +
                                        gesture + ')')

        elif self.gesture_actions[1] == self.gesture_action_relation[gesture]:
            run_external_application = sh.Command("./dummy.py")
            self.notification_l.setText('Ran dummy.py (' + gesture + ') Look '
                                        'in the terminal')

            print(run_external_application(_bg=False))
        elif self.gesture_actions[2] == self.gesture_action_relation[gesture]:
            self.notification_l.setText('BYE BYE (' + gesture + ')')
            print('Shutdown requested! BYE BYE')
            sys.exit(0)


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
