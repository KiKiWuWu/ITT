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

Ported to Python.

Original Copyright statement:

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
    SQUARE_SIZE = 250
    ORIGIN = Point(0, 0)

    def __init__(self, name, points):
        self.name = name
        self.points = Functions.resample(points, Unistroke.NUM_POINTS)
        radians = Functions.indicative_angle(self.points)
        self.points = Functions.rotate_by(self.points, -radians)
        self.points = Functions.scale_to(self.points, Unistroke.SQUARE_SIZE)
        self.points = Functions.translate_to(self.points, Unistroke.ORIGIN)


class Result:
    def __init__(self, name, score):
        self.name = name
        self.score = score


class Functions:
    PHI = 0.5 * (-1 + np.sqrt(5))

    @staticmethod
    def resample(points, n):
        interval_length = Functions.path_length(points) / (n - 1)
        D = 0.0

        new_points = [points[0]]

        i = 1

        while i < len(points) - 1:
            d = Functions.distance(points[i - 1], points[i])

            if (D + d) >= interval_length:
                qx = points[i - 1].x + ((interval_length - D) / d) * \
                                       (points[i].x - points[i - 1].x)

                qy = points[i - 1].y + ((interval_length - D) / d) * \
                                       (points[i].y - points[i - 1].y)

                q = Point(qx, qy)

                new_points.append(q)

                points.insert(i, q)

                D = 0.0
            else:
                D += d

            i += 1

        while len(new_points) < n:
            new_points.append(points[-1])

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
    def distance_at_best_angle(points, t, a, b, threshold):
        x1 = Functions.PHI * a + (1.0 - Functions.PHI) * b
        f1 = Functions.distance_at_angle(points, t, x1)
        x2 = (1.0 - Functions.PHI) * a + Functions.PHI * b
        f2 = Functions.distance_at_angle(points, t, x2)

        while np.abs(b - a) > threshold:
            if f1 < f2:
                b = x2
                x2 = x1
                f2 = f1
                x1 = Functions.PHI * a + (1.0 - Functions.PHI) * b
                f1 = Functions.distance_at_angle(points, t, x1)
            else:
                a = x1
                x1 = x2
                f1 = f2
                x2 = (1.0 - Functions.PHI) * a + Functions.PHI * b
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
        min_x = float('+Infinity')
        max_x = float('-Infinity')
        min_y = float('+Infinity')
        max_y = float('-Infinity')

        for p in points:
            min_x = np.minimum(min_x, p.x)
            min_y = np.minimum(min_y, p.y)
            max_x = np.maximum(max_x, p.x)
            max_y = np.maximum(max_y, p.y)

        return Rectangle(min_x, min_y, max_x, max_y)

    @staticmethod
    def path_distance(pts1, pts2):
        d = 0.0

        for i in range(0, len(pts1)):
            d += Functions.distance(pts1[i], pts2[i])

        return d / len(pts1)

    @staticmethod
    def path_length(points):
        d = 0.0

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
    HALF_DIAGONAL = 0.5 * DIAGONAL

    def __init__(self):
        """
        constructor
        :return void
        """
        self.gestures = []

    def recognize(self, points):
        pts = Functions.resample(points, Unistroke.NUM_POINTS)

        radians = Functions.indicative_angle(pts)

        pts = Functions.rotate_by(pts, -radians)
        pts = Functions.scale_to(pts, Unistroke.SQUARE_SIZE)
        pts = Functions.translate_to(pts, Unistroke.ORIGIN)

        b = float('inf')
        u = -1

        for i in range(0, len(self.gestures)):
            d = Functions.distance_at_best_angle(
                pts, self.gestures[i],
                -DollarOneGestureRecognizer.ANGLE_RANGE,
                DollarOneGestureRecognizer.ANGLE_RANGE,
                DollarOneGestureRecognizer.ANGLE_PRECISION)

            if d < b:
                b = d
                u = i

        if u == -1:
            return Result('No Match', 0.0)
        else:
            return Result(self.gestures[u].name, float(1) - b /
                          DollarOneGestureRecognizer.HALF_DIAGONAL)

    def add_gesture(self, name, points):
        # might need conversion of parameter points to Point type points
        self.gestures.append(Unistroke(name, points))

    def delete_gesture(self, index):
        if index < len(self.gestures):
            self.gestures.pop(index)
