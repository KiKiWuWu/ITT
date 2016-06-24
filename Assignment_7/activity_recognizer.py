#!/usr/bin/env python3
# coding: utf-8
# -*- coding: utf-8 -*-

from PyQt5 import uic, QtGui, QtCore, Qt
import sys
import webbrowser as wb
import sh

AAAYYYEEE_MACARENA = 'https://www.youtube.com/watch?v=XiBYM6g8Tck'


class CustomListWidgetItem(Qt.QListWidgetItem):
    def __init__(self, name):
        super(CustomListWidgetItem, self).__init__(name)
        # add item specific data like gesture, trainings data, etc.


class Window(Qt.QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        self.win = uic.loadUi("activity_recognizer.ui")

        self.gesture_list_widget = self.win.listWidget

        self.add_btn = self.win.btn_add

        self.use_action = None
        self.retrain_action = None
        self.remove_action = None

        self.is_trained = False

        self.add_btn.clicked.connect(self.add)

        self.setup_gesture_list_widget()
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
        # self.on_shake()
        # self.on_key_unlock()
        self.on_slash()

    def retrain(self):
        print("New Training Required")

    def remove(self):
        self.gesture_list_widget.takeItem(
            self.gesture_list_widget.row(
                self.gesture_list_widget.currentItem()))

    def on_shake(self):
        wb.open_new(AAAYYYEEE_MACARENA)

    def on_whip(self):
        # change ui color based on sensor
        pass

    def on_key_unlock(self):
        # open app
        run_external_application = sh.Command("./dummy.py")
        print(run_external_application(_bg=False))

    def on_key_lock(self):
        # ???
        pass

    def on_slash(self):
        # close this app (not happy with this)
        sys.exit(0)
        pass

def main():
    app = Qt.QApplication(sys.argv)
    win = Window()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()