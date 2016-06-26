#!/usr/bin/env python3
# coding: utf-8
# -*- coding: utf-8 -*-

from PyQt5 import uic, QtGui, QtCore, Qt
import sys
import webbrowser as wb
import sh
from sklearn import svm
import numpy as np
import wiimote
import time
import activity_classifier as ac

# FOR THE LULZ
TAYLOR_SWIFT = 'https://www.youtube.com/watch?v=nfWlot6h_JM'


class WiimoteThread(QtCore.QThread):
    """
    simple thread class for concurrent wiimote accelerometer data retrieval
    """

    update_trigger = QtCore.pyqtSignal()

    def __init__(self):
        """
        constructor

        :return: void
        """

        super(WiimoteThread, self).__init__()
        self.is_looping = True

    def run(self):
        """
        looped action of the thread

        :return: void
        """

        while self.is_looping:
            time.sleep(0.02)  # sampling rate of 50 Hz
            self.update_trigger.emit()


class CustomListWidgetItem(Qt.QListWidgetItem):
    """
    class responsible for the custom list widget item
    """

    def __init__(self, name):
        """
        constructor

        :param name: the name of the activity

        :return: void
        """
        super(CustomListWidgetItem, self).__init__(name)
        # add item specific data like gesture, trainings data, etc.


class Window(Qt.QMainWindow):
    """
    class responsible for the UI
    """

    def __init__(self):
        """
        constructor
        UI-elements setup

        :return: void
        """

        super(Window, self).__init__()
        self.win = uic.loadUi("activity_recognizer.ui")

        self.gesture_list_widget = self.win.listWidget

        self.add_btn = self.win.btn_add

        self.use_action = None
        self.retrain_action = None
        self.remove_action = None

        self.is_trained = False
        self.is_pressed = False
        self.is_classified = False

        self.gesture_data = []

        self.add_btn.clicked.connect(self.add)

        self.setup_gesture_list_widget()
        self.wm = wiimote.connect("18:2A:7B:F3:F8:F5")
        self.wiimote_thread = WiimoteThread()
        self.wiimote_thread.update_trigger.connect(self.get_wiimote_input)
        self.wiimote_thread.start()
        self.win.show()

    def add(self):
        gesture_name, is_ok = \
            Qt.QInputDialog.getText(self.win, 'Input Dialog',
                                    'Enter Gesture Name:')

        if not is_ok:
            print('Error: Could not add required gesture (insufficient name!)')
            return

        is_ok = self.train()  # perform required training

        if not is_ok:
            print('Error: Could not add required gesture (training failed!)')
            return

        # add data to CustomListWidget
        self.gesture_list_widget.addItem(CustomListWidgetItem(gesture_name))

    def self_show(self):
        print(self.list_widget.currentItem().text())

    def setup_gesture_list_widget(self):
        self.gesture_list_widget.setContextMenuPolicy(
            QtCore.Qt.ActionsContextMenu)

        self.add_context_menu_actions()

    def add_context_menu_actions(self):
        self.use_action = Qt.QAction("Use Gesture", None)
        self.use_action.triggered.connect(self.use)
        self.retrain_action = Qt.QAction("Retrain Gesture", None)
        self.retrain_action.triggered.connect(self.retrain)
        self.remove_action = Qt.QAction("Remove Gesture", None)
        self.remove_action.triggered.connect(self.remove)

        self.gesture_list_widget.addAction(self.use_action)
        self.gesture_list_widget.addAction(self.retrain_action)
        self.gesture_list_widget.addAction(self.remove_action)

    def train(self):
        print("Training Required")

        return True

    def use(self):
        print("Usage Required")

    def retrain(self):
        print("New Training Required")

    def remove(self):
        self.gesture_list_widget.takeItem(
            self.gesture_list_widget.row(
                self.gesture_list_widget.currentItem()))

    def on_shake(self):
        wb.open_new(TAYLOR_SWIFT)

    def on_whip(self):
        run_external_application = sh.Command("./dummy.py")
        print(run_external_application(_bg=False))

    def on_wiggle(self):
        print("System exit requested (wiggle)")
        # sys.exit(0)
        pass

    def get_wiimote_input(self):
        if self.wm.buttons["A"]:
            x, y, z = self.wm.accelerometer
            self.is_pressed = True
            self.is_classified = False
            self.gesture_data.append([x, y, z])
        elif self.is_pressed and not self.is_classified:
            self.classify()
            self.gesture_data.clear()

    def classify(self):
        self.is_classified = True
        classifier = ac.Classifier('data.csv')
        gesture = classifier.classify(self.gesture_data)

        if ac.SHAKE == gesture:
            self.on_shake()
        elif ac.WHIP == gesture:
            self.on_whip()
        elif ac.WIGGLE == gesture:
            self.on_wiggle()
        elif ac.NOTHING == gesture:
            print("IDLE")


def main():
    app = Qt.QApplication(sys.argv)
    win = Window()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()