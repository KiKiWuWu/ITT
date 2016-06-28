#!/usr/bin/env python3
# coding: utf-8
# -*- coding: utf-8 -*-

from PyQt5 import uic, QtGui, QtCore, Qt
import sys
import sh
import  webbrowser as wb
import numpy as np
import wiimote
import time
import gesture_classifier as gc

UI_FILE = 'gesture_recognizer.ui'
HELP_TEXT = 'HELP TEXT'


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
        self.win = uic.loadUi(UI_FILE)

        self.gesture_data = []
        self.wm = None

        self.connect_btn = self.win.btn_connect
        self.about_btn = self.win.btn_about
        self.address_le = self.win.le_address

        self.connect_btn.clicked.connect(self.connect_wiimote)
        self.about_btn.clicked.connect(self.show_readme)

        self.wiimote_thread = WiimoteThread()
        self.wiimote_thread.update_trigger.connect(self.get_wiimote_input)
        self.wiimote_thread.start()


        self.win.show()


    def connect_wiimote(self):
        """
        connects to a wiimote if one is found else does nothing

        :return: void
        """

        try:
            self.wm = wiimote.connect(self.address_le.text())
        except Exception:
            pass

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
