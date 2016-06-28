#!/usr/bin/env python3
# coding: utf-8
# -*- coding: utf-8 -*-

from PyQt5 import uic, QtGui, QtCore, Qt
import sys
import sh
import  webbrowser as wb
import numpy as np
import time
import gesture_classifier as gc

UI_FILE = 'gesture_recognizer.ui'
HELP_TEXT = 'HELP TEXT'

# points to classifier need to of Point class type

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

        self.classifier = gc.DollarOneGestureRecognizer()

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

    def get_wiimote_input(self):
        """


        :return: void
        """

        if self.wm is not None:
            if self.wm.buttons["A"]:
                print(self.wm.accelerometer)


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
