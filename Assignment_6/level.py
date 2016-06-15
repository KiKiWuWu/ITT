#!/usr/bin/env python3
# coding: utf-8

import wiimote
import time
import sys

WM_ADDRESS = "18:2A:7B:F3:F8:F5"  # default address


class BubbleLevel:
    def __init__(self, mac_address=WM_ADDRESS):
        """
        constructor

        :param mac_address: the mac address of the wiimote device
        :param name: the name of the wiimote device
        :return: void
        """

        self.wm = wiimote.connect(mac_address)

        # determined through testing, might need manual adjustment
        self.min_value = 410
        self.level_value = 512
        self.max_value = 610

        interval_step = (self.level_value - self.min_value) / 3

        self.interval = [
            self.min_value + interval_step,
            self.min_value + interval_step * 2,
            self.level_value - 10,
            self.level_value + 10,
            self.max_value - interval_step * 2,
            self.max_value - interval_step
        ]

        self.has_rumbled = False
        self.has_button_press = True
        self.axis_idx = 0  # default x; x = 0; y = 1

    def level_degree(self, value):
        """
        calculates the amount of LEDs to activate and from which side

        :param value: the measured value
        :return: the amount of LEDs to activate,
                a bool depicting from which side
        """

        if value < self.interval[0]:
            return 1, False                                  # *---
        elif self.interval[0] <= value < self.interval[1]:
            return 2, False                                  # **--
        elif self.interval[1] <= value < self.interval[2]:
            return 3, False                                  # ***-
        elif self.interval[2] <= value <= self.interval[3]:
            return 4, False                                  # ****
        elif self.interval[3] < value < self.interval[4]:
            return 3, True                                   # -***
        elif self.interval[4] <= value < self.interval[5]:
            return 2, True                                   # --**
        elif self.interval[5] <= value:
            return 1, True                                   # ---*

    def control(self):
        """
        handles D-Pad input by the user
        :return: void
        """

        if self.wm.buttons["Down"] or self.wm.buttons["Up"] or \
           self.wm.buttons["Left"] or self.wm.buttons["Right"]:
            if not self.has_button_press:
                self.has_button_press = True

                if self.axis_idx == 0:
                    self.axis_idx = 1
                else:
                    self.axis_idx = 0
        else:
            self.has_button_press = False

    def handle_rumble(self, num_leds):
        """
        handle the rumble and set sleep time based on rumble occurrence

        :param num_leds: the amount of LEDs active
        :return: the time the thread has to sleep (0.05 after no rumble;
                 0.15 after a rumble)
        """

        if num_leds == 4 and not self.has_rumbled:
            self.wm.rumble(0.1)
            self.has_rumbled = True
            return 0.15
        if num_leds != 4 and self.has_rumbled:
            self.has_rumbled = False

        return 0.05

    def level(self):
        """
        update loop of leveling operation

        :return: void
        """

        while True:
            print("active axis [" + str(self.axis_idx) + "]; value = " +
                  str(self.wm.accelerometer[self.axis_idx]))

            self.control()

            leds, side = self.level_degree(self.wm.accelerometer[self.axis_idx])

            self.activate_led_row(leds, side)

            time.sleep(self.handle_rumble(leds))

    def activate_led_row(self, num, side):
        """
        activates the given amount of LEDs on the given side

        :param num: the amount of LEDs to be activated
        :param side: the side from which the activation starts
        :return: void
        """

        pattern = []

        if not side:
            for i in range(1, 5):
                if i <= num:
                    pattern.append(1)
                else:
                    pattern.append(0)
        else:
            for i in range(0, 4 - num):
                pattern.append(0)

            for i in range(0, num):
                pattern.append(1)

        self.wm.leds = pattern


def input_from_cmd():
    """
    checks if cmd args are exactly 2 in number

    :return: void
    """

    if len(sys.argv) != 2:
        raise Exception("Insufficient number of CMD Args! Mac Address Required")

    input("Press the 'sync' button on the back of your Wiimote Plus " +
          "or buttons (1) and (2) on your classic Wiimote.\n" +
          "Press <return> once the Wiimote's LEDs start blinking.")


def main():
    """
    application entry point

    :return: void
    """
    input_from_cmd()

    bl = BubbleLevel(sys.argv[1])
    bl.level()


if __name__ == '__main__':
    main()
