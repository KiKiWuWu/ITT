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
INITIAL_TRAININGS_DATA_FILE = 'data.csv'
UI_FILE = 'activity_recognizer.ui'

HELP_TEXT = 'Buttons:\n' + \
            'Gesture Mode: Activate the gesture tracking via wiimote.\n' + \
            'No Gesture Mode: Deactivates the Gesture Mode.\n' + \
            'Connect: connects the wiimote with the given address\n' + \
            '+: adds a new gesture to the list if there are less than ' + \
            '3\n' + \
            '\n' + \
            'List Item: right clicking a list item opens a context ' + \
            'menu\n' + \
            'Retrain Gesture: allows the retraining of this gesture\n' + \
            'Remove Gesture: allows the removal of this gesture\n' + \
            '\n' + \
            'Overall Application Usage:\n' + \
            'By activating Gesture Mode the three predefined Gestures' + \
            'are usable when performing their action while pressing ' + \
            'and holding the A button on the wiimote\n\n' + \
            'Shake: Hold the wiimote normally away from you and rotate' + \
            ' it 90 degrees up and 90 degrees left (so the A button' + \
            'faces to the left). Press and hold A and shake the device ' + \
            'away and towards you.\n\n' + \
            'Whip: Hold the wiimote normally away from you and press ' + \
            'and hold A. Then rotate it up 90 degrees and then down 90 ' + \
            'degrees. Repeat this motion for the whipping gesture.\n\n' + \
            'Wiggle: Hold the wiimote normally away from you and press ' + \
            'and hold A. Then move the wiimote from the left to the ' + \
            'right and then right to left without rotating it ' + \
            '(it still faces away from you!) Continue this motion for ' + \
            'the wiggling gesture.\n\n' + \
            'Only three gestures can be stored at the same time. You ' + \
            'can remove one and add a new one. If you do so you have ' + \
            'to select Retrain Gesture from its context menu.'

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

        self.gesture_list_widget = self.win.listWidget

        self.add_btn = self.win.btn_add
        self.action_btn = self.win.btn_action
        self.connect_btn = self.win.btn_connect
        self.about_btn = self.win.btn_about

        self.address_le = self.win.le_address

        self.recognition_l = self.win.l_recognition

        self.gesture_relations = {
            ac.GESTURE_1: 'Shake',
            ac.GESTURE_2: 'Whip',
            ac.GESTURE_3: 'Wiggle'
        }

        self.use_action = None
        self.retrain_action = None
        self.remove_action = None

        self.is_pressed = False
        self.is_classified = False
        self.uses_gestures = False
        self.recognizes_gesture_1 = False
        self.recognizes_gesture_2 = False
        self.recognizes_gesture_3 = False
        self.is_retraining = False

        self.classifier = ac.Classifier(INITIAL_TRAININGS_DATA_FILE)

        self.gesture_data = []

        self.add_btn.clicked.connect(self.add)
        self.action_btn.clicked.connect(self.set_gesture_action)
        self.connect_btn.clicked.connect(self.connect_wiimote)
        self.about_btn.clicked.connect(self.show_readme)

        self.setup_gesture_list_widget()
        self.gesture_list_widget_item_count = self.gesture_list_widget.count()

        self.wm = None

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
        if self.gesture_list_widget_item_count == 3:
            print('Cannot have more gestures than 3. Delete one first!')
        else:
            if self.gesture_list_widget_item_count == 0:
                self.add_gesture(ac.GESTURE_1)
            elif self.gesture_list_widget_item_count == 1:
                self.add_gesture(ac.GESTURE_2)
            elif self.gesture_list_widget_item_count == 2:
                self.add_gesture(ac.GESTURE_3)

    def add_gesture(self, required_gesture):
        gesture_name, ok = \
            Qt.QInputDialog.getText(self.win, 'Input Dialog',
                                    'Enter Gesture Name')

        self.gesture_list_widget_item_count += 1
        self.gesture_list_widget.addItem(Qt.QListWidgetItem(gesture_name))

        if required_gesture == ac.GESTURE_1:
            self.gesture_relations[ac.GESTURE_1] = gesture_name
            self.recognizes_gesture_1 = True
        elif required_gesture == ac.GESTURE_2:
            self.gesture_relations[ac.GESTURE_2] = gesture_name
            self.recognizes_gesture_2 = True
        elif required_gesture == ac.GESTURE_3:
            self.gesture_relations[ac.GESTURE_3] = gesture_name
            self.recognizes_gesture_3 = True

    def self_show(self):
        print(self.list_widget.currentItem().text())

    def setup_gesture_list_widget(self):
        self.gesture_list_widget.setContextMenuPolicy(
            QtCore.Qt.ActionsContextMenu)

        self.gesture_list_widget.addItem(
            Qt.QListWidgetItem(self.gesture_relations[ac.GESTURE_1]))

        self.gesture_list_widget.addItem(
            Qt.QListWidgetItem(self.gesture_relations[ac.GESTURE_2]))

        self.gesture_list_widget.addItem(
            Qt.QListWidgetItem(self.gesture_relations[ac.GESTURE_3]))

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
        self.gesture_list_widget_item_count -= 1
        gesture = self.gesture_list_widget.currentItem().text()

        self.gesture_list_widget.takeItem(
            self.gesture_list_widget.row(
                self.gesture_list_widget.currentItem()))

        if gesture == self.gesture_relations[ac.GESTURE_1]:
            self.recognizes_gesture_1 = False
        if gesture == self.gesture_relations[ac.GESTURE_2]:
            self.recognizes_gesture_2 = False
        if gesture == self.gesture_relations[ac.GESTURE_3]:
            self.recognizes_gesture_3 = False

    def on_gesture_1_activity(self):
        self.recognition_l.setText(self.gesture_relations[ac.GESTURE_1])
        wb.open_new(TAYLOR_SWIFT)

    def on_gesture_2_activity(self):
        self.recognition_l.setText(self.gesture_relations[ac.GESTURE_2])
        run_external_application = sh.Command("./dummy.py")
        print(run_external_application(_bg=False))

    def on_gesture_3_activity(self):
        self.recognition_l.setText(self.gesture_relations[ac.GESTURE_3])
        print("System exit requested")
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

                    activity = self.gesture_list_widget.currentItem().text()

                    self.classifier.train(None, data, activity)

                    self.is_classified = True
                    self.is_retraining = False
                    self.gesture_data.clear()

    def classify(self):
        self.is_classified = True
        gesture = self.classifier.classify(self.gesture_data)

        if ac.GESTURE_1 == gesture and self.recognizes_gesture_1:
            self.on_gesture_1_activity()
        elif ac.GESTURE_2 == gesture and self.recognizes_gesture_2:
            self.on_gesture_2_activity()
        elif ac.GESTURE_3 == gesture and self.recognizes_gesture_3:
            self.on_gesture_3_activity()

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
                if ges == self.gesture_relations[ac.GESTURE_1]:
                    self.recognizes_gesture_1 = True
                if ges == self.gesture_relations[ac.GESTURE_2]:
                    self.recognizes_gesture_2 = True
                if ges == self.gesture_relations[ac.GESTURE_3]:
                    self.recognizes_gesture_3 = True

            self.action_btn.setText('No Gesture Mode')
        else:
            self.uses_gestures = False
            self.action_btn.setText('Gesture Mode')

            self.recognizes_gesture_1 = False
            self.recognizes_gesture_2 = False
            self.recognizes_gesture_3 = False

    def show_readme(self):
        msg = Qt.QMessageBox()
        msg.setIcon(Qt.QMessageBox.Information)

        msg.setText(HELP_TEXT)
        msg.setWindowTitle('About')
        msg.setStandardButtons(Qt.QMessageBox.Ok)
        msg.exec_()


def main():
    app = Qt.QApplication(sys.argv)
    win = Window()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
