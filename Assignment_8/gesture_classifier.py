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
    """
    this class initializes a point
    """
    def __init__(self, x, y):
        """
        constructor
        
        :param x: x coordinate of the point
        :param y: y coordinate of the point
        
        :return: void
        """
        
        self.x = x
        self.y = y


class Rectangle:
    """
    this class initializes a rectangle
    """
    def __init__(self, x1, y1, x2, y2):
        """
        constructor
        
        :param x1: x coordinate of the first corner point
        :param y1: y coordinate of the first corner point
        :param x2: width of the rectangle
        :param y2: height of the rectangle
        
        :return: void
        """
        
        self.x = x1
        self.y = y1
        self.width = x2
        self.height = y2


class Unistroke:
    """
    this class initialzes a unistroke
    """
    NUM_POINTS = 64
    SQUARE_SIZE = 250
    ORIGIN = Point(0, 0)

    def __init__(self, name, points):
        """
        constructor
        
        :param name: name of the unistroke 
        :param points: array of the points
        
        :return: void
        """
        
        self.name = name
        self.points = Functions.resample(points, Unistroke.NUM_POINTS)

        radians = Functions.indicative_angle(self.points)

        self.points = Functions.rotate_by(self.points, -radians)
        self.points = Functions.scale_to(self.points, Unistroke.SQUARE_SIZE)
        self.points = Functions.translate_to(self.points, Unistroke.ORIGIN)


class Result:
    """
    this class sets the name and the score
    """
    
    def __init__(self, name, score):
        """
        constructor
        
        :param name: the name of the ahpe if recognized correctly
        :param score: float if no match 0.0
        
        :return: void
        """
        
        self.name = name
        self.score = score


class Functions:
    """
    this class statically defines all the helper functions
    
    this class has following methods:
        resample()
        indicative_angle()
        rotate_by()
        scale_to()
        translate_to()
        distance_at_best_angle()
        distance_at_angle()
        centroid()
        bounding_box()
        path_distance()
        path_length()
        distance()
        degrees_to_radians()
    
    """
    
    PHI = 0.5 * (-1.0 + np.sqrt(5))

    @staticmethod
    def resample(points, n):
        """
        this methode resamples the points with new points
        
        :param points: point array
        :param n: fixed number of points from the Unistroke object;
                  Unistroke.NUM_POINTS
        
        :return: new_points array
        """
        
        interval_length = Functions.path_length(points) / (n - 1)
        distance = 0.0

        new_points = [points[0]]

        i = 1

        while i < len(points) - 1:
            temp_distance = Functions.distance(points[i - 1], points[i])

            if (distance + temp_distance) >= interval_length:
                qx = points[i - 1].x + ((interval_length - distance) /
                                        temp_distance) * \
                                       (points[i].x - points[i - 1].x)

                qy = points[i - 1].y + ((interval_length - distance) /
                                        temp_distance) * \
                                       (points[i].y - points[i - 1].y)

                q = Point(qx, qy)

                new_points.append(q)

                points.insert(i, q)

                distance = 0.0
            else:
                distance += temp_distance

            i += 1

        while len(new_points) < n:
            new_points.append(points[-1])

        return new_points

    @staticmethod
    def indicative_angle(points):
        """
        method to indicate the angle of the shape to the centroid
        
        :param points: array of points
        
        :return: an angle in randians
        """
        
        centroid = Functions.centroid(points)
        return np.arctan2(centroid.y - points[0].y, centroid.x - points[0].x)

    @staticmethod
    def rotate_by(points, angle_in_radians):
        """
        method to rotate the points by an angle in radians
        
        :param points: point array
        :param angle_in_radians: rotation angle in radians
        
        :return: the array containing the points after the rotation
        """
        
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
        """
        method that scales the points of a shape
        
        :param points: the array of points
        :param size: the target size to scale to
        
        :return: new_points array
        """
        
        bb = Functions.bounding_box(points)
        new_points = []

        for p in points:
            qx = p.x * (size / bb.width)
            qy = p.y * (size / bb.height)

            new_points.append(Point(qx, qy))

        return new_points

    @staticmethod
    def translate_to(points, pt):
        """

        :param points: the points to be translated
        :param pt: the point to which translate to

        :return: the list of points after they have been translated
        """

        centroid = Functions.centroid(points)

        new_points = []

        for p in points:
            qx = p.x + pt.x - centroid.x
            qy = p.y + pt.y - centroid.y

            new_points.append(Point(qx, qy))

        return new_points

    @staticmethod
    def distance_at_best_angle(points, gesture, neg_angle_range,
                               pos_angle_range, angle_precision):
        """
        this method calculates the distance at the best angle
        
        :param points: array of points 
        :param gesture: a gesture
        :param neg_angle_range: negative angle range 
        :param pos_angle_range: positive angle range
        :param angle_precision: angle precision
        
        :return: returns the scalar of two distances
        """
        
        x1 = Functions.PHI * neg_angle_range + \
            (1.0 - Functions.PHI) * pos_angle_range

        distance1 = Functions.distance_at_angle(points, gesture, x1)
        x2 = (1.0 - Functions.PHI) * neg_angle_range + \
            Functions.PHI * pos_angle_range

        distance2 = Functions.distance_at_angle(points, gesture, x2)

        while np.abs(pos_angle_range - neg_angle_range) > angle_precision:
            if distance1 < distance2:
                pos_angle_range = x2
                x2 = x1
                distance2 = distance1
                x1 = Functions.PHI * neg_angle_range + \
                    (1.0 - Functions.PHI) * pos_angle_range

                distance1 = Functions.distance_at_angle(points, gesture, x1)
            else:
                neg_angle_range = x1
                x1 = x2
                distance1 = distance2
                x2 = (1.0 - Functions.PHI) * neg_angle_range + \
                    Functions.PHI * pos_angle_range

                distance2 = Functions.distance_at_angle(points, gesture, x2)

        return np.minimum(distance1, distance2)

    @staticmethod
    def distance_at_angle(points, unistroke, angle_in_radians):
        """
        this method returns the path distance of the points array to the
        unistroke points
        
        :param points: the point array
        :param unistroke: the target unistroke
        :param angle_in_radians: the angle in radians
        
        :return: the path distance
        """
        new_points = Functions.rotate_by(points, angle_in_radians)

        return Functions.path_distance(new_points, unistroke.points)

    @staticmethod
    def centroid(points):
        """
        calculates the centroid of a point array
        
        :param points: array of points from which the centroid is calculated
        
        :return: the centroid
        """
        
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
        """
        this method computes the bounding box of an array of points
        
        :param points: array of points to receive its bounding box
        
        :return: the bounding box of the given points
        """
        
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
        """
        this method calculates the the path distance between two lists of points
        
        :param pts1: first list of points
        :param pts2: second list of points
        
        :return: the average path distance of the points
        """
        
        d = 0.0

        for i in range(0, len(pts1)):
            d += Functions.distance(pts1[i], pts2[i])

        return d / len(pts1)

    @staticmethod
    def path_length(points):
        """
        this method calculates the path length of point list
        
        :param points: list of points
        
        :return: returns the sum of distances of the points list
        """

        d = 0.0

        for i in range(1, len(points)):
            d += Functions.distance(points[i - 1], points[i])

        return d

    @staticmethod
    def distance(p1, p2):
        """
        this method calcualtes the distance of two points
        
        :param p1: first point
        :param p2: second point
        
        :return: the distance of p1 and p2
        """

        dx = p2.x - p1.x
        dy = p2.y - p1.y

        return np.sqrt(dx * dx + dy * dy)

    @staticmethod
    def degrees_to_radians(angle_in_degrees):
        """
        this method converts an angle from degrees to radians
        
        :param angle_in_degrees: the angle in degrees
        
        :return: the angle in radians
        """

        return angle_in_degrees * np.pi / 180


class DollarOneGestureRecognizer:
    """
    this class sets the dollar one recognizer
    
    this class has following methods
        recognize()
        add_gesture()
        delete_gesture()
    
    """

    ANGLE_RANGE = Functions.degrees_to_radians(45)
    ANGLE_PRECISION = Functions.degrees_to_radians(2)
    DIAGONAL = np.sqrt(Unistroke.SQUARE_SIZE * Unistroke.SQUARE_SIZE +
                       Unistroke.SQUARE_SIZE * Unistroke.SQUARE_SIZE)
    HALF_DIAGONAL = 0.5 * DIAGONAL

    def __init__(self):
        """
        constructor

        :return: void
        """
        self.gestures = []

    def recognize(self, points):
        """
        this methode recognizes a point array as a gesture
        
        :param points: the point array to find the gesture in
        
        :return: result of the dollar one gesture recognizer
        """

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
        """
        this method adds a unistroke gesture to the list of known gestures
        
        :param name: name of the new gesture
        :param points: array of all including points
        
        :return: void
        """

        self.gestures.append(Unistroke(name, points))

    def delete_gesture(self, index):
        """
        this method removes a specific gesture from the list of gestures
        
        :param index: (int) is the position in a list 
                
        :return: void
        """

        if index < len(self.gestures):
            self.gestures.pop(index)
