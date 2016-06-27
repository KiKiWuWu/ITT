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
WM_ADDRESS = '18:2A:7B:F3:F8:F5'


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
        self.win = uic.loadUi("activity_recognizer.ui")

        self.gesture_list_widget = self.win.listWidget

        self.add_btn = self.win.btn_add
        self.action_btn = self.win.btn_action
        self.connect_btn = self.win.btn_connect

        self.address_le = self.win.le_address

        self.recognition_l = self.win.l_recognition

        self.use_action = None
        self.retrain_action = None
        self.remove_action = None

        self.is_pressed = False
        self.is_classified = False
        self.uses_gestures = False
        self.recognizes_shake = False
        self.recognizes_whip = False
        self.recognizes_wiggle = False
        self.is_retraining = False

        self.classifier = ac.Classifier('data.csv')

        self.gesture_data = []

        self.add_btn.clicked.connect(self.add)
        self.action_btn.clicked.connect(self.set_gesture_action)
        self.connect_btn.clicked.connect(self.connect_wiimote)

        self.setup_gesture_list_widget()
        self.wm = None

        self.connect_wiimote()

        self.wiimote_thread = WiimoteThread()
        self.wiimote_thread.update_trigger.connect(self.get_wiimote_input)
        self.wiimote_thread.start()
        self.win.show()

    def connect_wiimote(self):
            try:
                self.wm = wiimote.connect(self.address_le.text())
            except Exception:
                pass

    def add(self):

        gestures = (ac.SHAKE, ac.WHIP, ac.WIGGLE)

        gesture, ok = Qt.QInputDialog.getItem(self, 'select', 'list',
                                              gestures, 0, False)

        if gesture == ac.SHAKE:
            self.recognizes_shake = True
        if gesture == ac.WHIP:
            self.recognizes_whip = True
        if gesture == ac.WIGGLE:
            self.recognizes_wiggle = True

        if not ok:
            print('Error: Could not add required gesture')
            return

        self.gesture_list_widget.addItem(Qt.QListWidgetItem(gesture))

    def self_show(self):
        print(self.list_widget.currentItem().text())

    def setup_gesture_list_widget(self):
        self.gesture_list_widget.setContextMenuPolicy(
            QtCore.Qt.ActionsContextMenu)

        self.add_context_menu_actions()

    def add_context_menu_actions(self):
        self.retrain_action = Qt.QAction("Retrain Gesture", None)
        self.retrain_action.triggered.connect(self.retrain)
        self.remove_action = Qt.QAction("Remove Gesture", None)
        self.remove_action.triggered.connect(self.remove)

        self.gesture_list_widget.addAction(self.retrain_action)
        self.gesture_list_widget.addAction(self.remove_action)

    def retrain(self):
        self.is_retraining = True

    def remove(self):
        gesture = self.gesture_list_widget.currentItem().text()

        self.gesture_list_widget.takeItem(
            self.gesture_list_widget.row(
                self.gesture_list_widget.currentItem()))

        if gesture == ac.SHAKE:
            self.recognizes_shake = False
        if gesture == ac.WHIP:
            self.recognizes_whip = False
        if gesture == ac.WIGGLE:
            self.recognizes_wiggle = False

    def on_shake(self):
        self.recognition_l.setText(ac.SHAKE)
        wb.open_new(TAYLOR_SWIFT)

    def on_whip(self):
        self.recognition_l = ac.WHIP
        run_external_application = sh.Command("./dummy.py")
        print(run_external_application(_bg=False))

    def on_wiggle(self):
        self.recognition_l = ac.WIGGLE
        print("System exit requested (wiggle)")
        # sys.exit(0)

    def get_wiimote_input(self):
        if self.wm is not None and self.uses_gestures:
            if self.wm.buttons["A"]:
                x, y, z = self.wm.accelerometer
                self.is_pressed = True
                self.is_classified = False
                self.gesture_data.append([float(x), float(y), float(z)])
            elif self.is_pressed and not self.is_classified:
                if not self.is_retraining:
                    self.classify()
                    self.gesture_data.clear()
                else:
                    data = self.gesture_data
                    print(data)

                    activity = self.gesture_list_widget.currentItem().text()

                    self.classifier.train(None, data, activity)

                    self.is_classified = True
                    self.is_retraining = False
                    self.gesture_data.clear()

    def classify(self):
        self.is_classified = True
        gesture = self.classifier.classify(self.gesture_data)

        if ac.SHAKE == gesture and self.recognizes_shake:
            self.on_shake()
        elif ac.WHIP == gesture and self.recognizes_whip:
            self.on_whip()
        elif ac.WIGGLE == gesture and self.recognizes_wiggle:
            self.on_wiggle()

    def set_gesture_action(self):
        if self.wm is None:
            print('connect the wiimote first')
            return

        if self.uses_gestures is False:
            self.uses_gestures = True

            active_gestures = []

            for i in range(0, self.gesture_list_widget.count()):
                active_gestures.append(self.gesture_list_widget.item(i).text())

            for ges in active_gestures:
                if ges == ac.SHAKE:
                    self.recognizes_shake = True
                if ges == ac.WHIP:
                    self.recognizes_whip = True
                if ges == ac.WIGGLE:
                    self.recognizes_wiggle = True

            self.action_btn.setText('No Gesture Mode')
        else:
            self.uses_gestures = False
            self.action_btn.setText('Gesture Mode')

            self.recognizes_shake = False
            self.recognizes_whip = False
            self.recognizes_wiggle = False


def main():
    app = Qt.QApplication(sys.argv)
    win = Window()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()