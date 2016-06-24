#!/usr/bin/env python3
# coding: utf-8
# -*- coding: utf-8 -*-

from enum import Enum
import wiimote
import time

WM_ADDRESS = "18:2A:7B:F3:F8:F5"  # default address

ACTIVITIES = Enum('ACTIVITIES', 'shake, whip, unlock, lock, slash')


class Activity(Enum):
    shake = 1
    whip = 2
    unlock = 3 # 3 gestures are needed -- most difficult to learn
    lock = 4 # 3 gestures are needed -- most difficult to learn
    slash = 5


def gather_data(activity):
    wm = wiimote.connect(WM_ADDRESS, None)
    min_value = 410  # not always applicable
    level_value = 512
    max_value = 610  # not always applicable

    data = []

    is_pressed = False

    while True:
        if wm.buttons["A"]:
            x, y, z = wm.accelerometer

            data.append([activity, x, y, z, time.time()])
            is_pressed = True
        elif is_pressed:
            break

        time.sleep(0.05)

    return data


def list_to_string_for_csv(l):
    out = ''

    for v in l:
        out += (str(v) + ";")

    return out[0: len(out) - 1]


def main():
    '''
    pipe stdout to csv file!
    :return:void
    '''

    print('a_id;x_accel;y_accel;z_accel;timestamp')

    data = gather_data(Activity.shake.value)

    for l in data:
        out = list_to_string_for_csv(l)
        print(out)


if __name__ == '__main__':
    main()