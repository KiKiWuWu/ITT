#!/usr/bin/env python3
# coding: utf-8
# -*- coding: utf-8 -*-

import numpy as np

"""
Based on this paper:

Wobbrock, J. O., Wilson, A. D., & Li, Y. (2007, October). Gestures without
libraries, toolkits or training: a $1 recognizer for user interface
prototypes. In Proceedings of the 20th annual ACM symposium on User
interface software and technology (pp. 159-168). ACM.

Implementation looked up here:
https://depts.washington.edu/aimgroup/proj/dollar/dollar.js

This software is distributed under the "New BSD License" agreement:

Copyright (C) 2007-2012, Jacob O. Wobbrock, Andrew D. Wilson and Yang Li.
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
   * Redistributions of source code must retain the above copyright
     notice, this list of conditions and the following disclaimer.
   * Redistributions in binary form must reproduce the above copyright
     notice, this list of conditions and the following disclaimer in the
     documentation and/or other materials provided with the distribution.
   * Neither the names of the University of Washington nor Microsoft,
     nor the names of its contributors may be used to endorse or promote
     products derived from this software without specific prior written
     permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL Jacob O. Wobbrock OR Andrew D. Wilson
OR Yang Li BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
"""


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Rectangle:
    def __init__(self, x1, y1, x2, y2):
        self.x = x1
        self.y = y1
        self.width = x2
        self.height = y2


class Unistroke:
    NUM_POINTS = 64
    SQUARE_SIZE = 250  # draw widget size
    ORIGIN = Point(0, 0)

    def __init__(self, name, points):
        self.name = name
        self.points = Functions.resample(points, Unistroke.NUM_POINTS)
        radians = Functions.indicative_angle(self.points)
        self.points = Functions.rotate_by(self.points, -radians)
        self.points = Functions.scale_to(self.points, Unistroke.SQUARE_SIZE)
        self.points = Functions.translate_to(self.points, Unistroke.ORIGIN)
        self.vector = Functions.vectorize(self.points)


class Result:
    def __init__(self, name, score):
        self.name = name
        self.score = score


class Functions:
    PHI = 0.5 * (-1 + np.sqrt(5))

    @staticmethod
    def resample(points, n):
        interval_length = Functions.path_length(points) / (n - 1)
        D = 0

        new_points = [points[0]]

        for i in range(1, len(points)):
            d = Functions.distance(points[i - 1], points[i])

            if (D + d) >= interval_length:
                qx = points[i - 1].x + ((interval_length - D) / d) * \
                                       (points[i].x - points[i - 1].x)

                qy = points[i - 1].y + ((interval_length - D) / d) * \
                                       (points[i].y - points[i - 1].y)

                q = Point(qx, qy)

                new_points.append(q)

                points.insert(i, q)

                D = 0
            else:
                D += d

        if len(new_points) == (n - 1):
            new_points.append(Point(points[len(points) - 1].x,
                                    points[len(points) - 1].y))

        return new_points

    @staticmethod
    def indicative_angle(points):
        centroid = Functions.centroid(points)
        return np.arctan2(centroid.y - points[0].y, centroid.x - points[0].x)

    @staticmethod
    def rotate_by(points, angle_in_radians):
        centroid = Functions.centroid(points)
        cosine = np.cos(angle_in_radians)
        sine = np.sin(angle_in_radians)
        new_points = []

        for p in points:
            qx = (p.x - centroid.x) * cosine - (p.y - centroid.y) * sine + \
                 centroid.x

            qy = (p.x - centroid.x) * sine + (p.y - centroid.y) * cosine + \
                 centroid.y

            new_points.append(Point(qx, qy))

        return new_points

    @staticmethod
    def scale_to(points, size):
        bb = Functions.bounding_box(points)
        new_points = []

        for p in points:
            qx = p.x * (size / bb.width)
            qy = p.y * (size / bb.height)

            new_points.append(Point(qx, qy))

        return new_points

    @staticmethod
    def translate_to(points, pt):
        centroid = Functions.centroid(points)

        new_points = []

        for p in points:
            qx = p.x + pt.x - centroid.x
            qy = p.y + pt.y - centroid.y

            new_points.append(Point(qx, qy))

        return new_points

    @staticmethod
    def vectorize(points):
        sum_ = 0

        vector = []

        for p in points:
            vector.append(p.x)
            vector.append(p.y)

            sum_ += p.x * p.x + p.y * p.y

        magnitude = np.sqrt(sum_)

        for i in range(0, len(vector)):
            vector[i] /= magnitude

        return vector

    @staticmethod
    def optimal_cosine_distance(v1, v2):
        a = 0
        b = 0

        i = 0

        while i < len(v1):
            a += v1[i] * v2[i] + v1[i + 1] * v2[i + 1]
            b += v1[i] * v2[i + 1] - v1[i + 1] * v2[i]

            i += 2

        angle = np.arctan(b / a)

        return np.arccos(a * np.cos(angle) + b * np.sin(angle))

    @staticmethod
    def distance_at_best_angle(points, t, a, b, threshold):
        x1 = Functions.PHI * a + (1 - Functions.PHI) * b
        f1 = Functions.distance_at_angle(points, t, x1)
        x2 = (1 - Functions.PHI) * a + Functions.PHI * b
        f2 = Functions.distance_at_angle(points, t, x2)

        while np.abs(b - a) > threshold:
            if f1 < f2:
                b = x2
                x2 = x1
                f2 = f1
                x1 = Functions.PHI * a + (1 - Functions.PHI) * b
                f1 = Functions.distance_at_angle(points, t, x1)
            else:
                a = x1
                x1 = x2
                f1 = f2
                x2 = (1 - Functions.PHI) * a + Functions.PHI * b
                f2 = Functions.distance_at_angle(points, t, x2)

        return np.minimum(f1, f2)

    @staticmethod
    def distance_at_angle(points, t, angle_in_radians):
        new_points = Functions.rotate_by(points, angle_in_radians)

        return Functions.path_distance(new_points, t.points)

    @staticmethod
    def centroid(points):
        x = 0
        y = 0

        for p in points:
            x += p.x
            y += p.y

        x /= len(points)
        y /= len(points)

        return Point(x, y)

    @staticmethod
    def bounding_box(points):
        min_x = float('inf')
        max_x = float('-inf')
        min_y = float('inf')
        max_y = float('-inf')

        for p in points:
            min_x = np.minimum(min_x, p.x)
            min_y = np.minimum(min_y, p.y)
            max_x = np.maximum(max_x, p.x)
            max_y = np.maximum(max_y, p.y)

        return Rectangle(min_x, min_y, max_x, max_y)

    @staticmethod
    def path_distance(pts1, pts2):
        d = 0

        for i in range(0, len(pts1)):
            d += Functions.distance(pts1[i], pts2[i])

        return d

    @staticmethod
    def path_length(points):
        d = 0

        for i in range(1, len(points)):
            d += Functions.distance(points[i - 1], points[i])

        return d

    @staticmethod
    def distance(p1, p2):
        dx = p2.x - p1.x
        dy = p2.y - p1.y

        return np.sqrt(dx * dx + dy * dy)

    @staticmethod
    def degrees_to_radians(angle_in_degrees):
        return angle_in_degrees * np.pi / 180


class DollarOneGestureRecognizer:

    ANGLE_RANGE = Functions.degrees_to_radians(45)
    ANGLE_PRECISION = Functions.degrees_to_radians(2)
    DIAGONAL = np.sqrt(Unistroke.SQUARE_SIZE * Unistroke.SQUARE_SIZE +
                       Unistroke.SQUARE_SIZE * Unistroke.SQUARE_SIZE)
    HALF_DIAGONAL = 0.5 / DIAGONAL

    def __init__(self):
        """
        constructor

        :return void
        """
        self.gestures = []

        self.gestures.append(Unistroke('triangle', [
            Point(137,139), Point(135,141), Point(133,144), Point(132,146),
            Point(130,149), Point(128,151), Point(126,155), Point(123,160),
            Point(120,166), Point(116,171), Point(112,177), Point(107,183),
            Point(102,188), Point(100,191), Point(95,195),  Point(90,199),
            Point(86,203),  Point(82,206),  Point(80,209),  Point(75,213),
            Point(73,213),  Point(70,216),  Point(67,219),  Point(64,221),
            Point(61,223),  Point(60,225),  Point(62,226),  Point(65,225),
            Point(67,226),  Point(74,226),  Point(77,227),  Point(85,229),
            Point(91,230),  Point(99,231),  Point(108,232), Point(116,233),
            Point(125,233), Point(134,234), Point(145,233), Point(153,232),
            Point(160,233), Point(170,234), Point(177,235), Point(179,236),
            Point(186,237), Point(193,238), Point(198,239), Point(200,237),
            Point(202,239), Point(204,238), Point(206,234), Point(205,230),
            Point(202,222), Point(197,216), Point(192,207), Point(186,198),
            Point(179,189), Point(174,183), Point(170,178), Point(164,171),
            Point(161,168), Point(154,160), Point(148,155), Point(143,150),
            Point(138,148), Point(136,148)
        ]))

        result = self.recognize([
            Point(137,139), Point(135,141), Point(133,144), Point(132,146),
            Point(130,149), Point(128,151), Point(126,155), Point(123,160),
            Point(120,166), Point(116,171), Point(112,177), Point(107,183),
            Point(102,188), Point(100,191), Point(95,195),  Point(90,199),
            Point(86,203),  Point(82,206),  Point(80,209),  Point(75,213),
            Point(73,213),  Point(70,216),  Point(67,219),  Point(64,221),
            Point(61,223),  Point(60,225),  Point(62,226),  Point(65,225),
            Point(67,226),  Point(74,226),  Point(77,227),  Point(85,229),
            Point(91,230),  Point(99,231),  Point(108,232), Point(116,233),
            Point(125,233), Point(134,234), Point(145,233), Point(153,232),
            Point(160,233), Point(170,234), Point(177,235), Point(179,236),
            Point(186,237), Point(193,238), Point(198,239), Point(200,237),
            Point(202,239), Point(204,238), Point(206,234), Point(205,230),
            Point(202,222), Point(197,216), Point(192,207), Point(186,198),
            Point(179,189), Point(174,183), Point(170,178), Point(164,171),
            Point(161,168), Point(154,160), Point(148,155), Point(143,150),
            Point(138,148), Point(136,148)
        ], True)

        print(result.name)

    def recognize(self, points, use_protractor):
        points = Functions.resample(points, Unistroke.NUM_POINTS)

        radians = Functions.indicative_angle(points)

        points = Functions.rotate_by(points, -radians)
        points = Functions.scale_to(points, Unistroke.SQUARE_SIZE)
        points = Functions.translate_to(points, Unistroke.ORIGIN)

        vector = Functions.vectorize(points)

        b = float('inf')
        u = -1

        for i in range(0, len(self.gestures)):
            if use_protractor:
                d = Functions.optimal_cosine_distance(self.gestures[i].vector,
                                                      vector)
            else:
                d = Functions.distance_at_best_angle(
                    points, gesture, -DollarOneGestureRecognizer.ANGLE_RANGE,
                    DollarOneGestureRecognizer.ANGLE_PRECISION)

            if d < b:
                b = d
                u = i

        return Result('No Match', 0) if u == -1 \
            else Result(self.gestures[u].name, 1 / b if use_protractor
                        else 1 - b / DollarOneGestureRecognizer.HALF_DIAGONAL)

    def add_gesture(self, name, points):
        pass

    def delete_gesture(self, index):
        pass



