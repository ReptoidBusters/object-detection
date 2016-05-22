import numpy as np
import numpy.linalg as lin
from math import cos
from math import sin
from math import acos
__author__ = 'Artyom_Lobanov'

"""
    This package implements some geometric object and algorithms.
    It works in 3D Cartesian coordinate system.
    It's expected that numpy.array will be used as point
"""

# Magic constant. It is used to estimate the error of the calculations.
EPS = 0.0001


class Plane:

    """
        Define plane by normal and distance to origin.
    """
    def __init__(self, normal, d):
        self.normal = normal
        self.d = d

    def contain(self, point):
        return abs(np.dot(self.normal, point) + self.d) < EPS

    def intersect(self, ray):  # (begin + t * d) * k = 0
        """
        Return common point of this plane and the ray.
        If the ray lies in plane or if they are parallel, method return None.
        """
        tmp = self.normal.dot(ray.d)
        if not tmp:
            return None
        distance = -(self.normal.dot(ray.begin) + self.d) / tmp
        return ray.get_point(distance)

    @staticmethod
    def create_plane(point1, point2, point3):
        """
        Return plane, that contain all that points.
        If point isn't different, raise Exception
        """
        normal = np.cross(point2 - point1, point3 - point1)
        length = lin.norm(normal)
        if not length:  # normal = 0
            raise RuntimeError("Can't create plane: points must be different")
        normal /= length  # now normal is normalized
        d = - np.dot(normal, point1)
        return Plane(normal, d)

    def __repr__(self):
        normal_str = "(" + ", ".join([str(x) for x in self.normal]) + ")"
        return "Plane[Normal = " + normal_str + "; D = " + str(self.d) + "]"


class Ray:

    def __init__(self, begin, another):
        self.begin = np.copy(begin)
        self.d = another - begin

    def get_point(self, distance):
        if distance < 0:
            return None
        return self.begin + self.d * distance


def is_collinear(vector_a, vector_b):
    len_a = lin.norm(vector_a)
    len_b = lin.norm(vector_b)
    if not len_a or not len_b:
        return True
    diff = vector_a / len_a - vector_b / len_b
    return lin.norm(diff) < EPS


def get_angle(vector_a, vector_b):
    len_a = lin.norm(vector_a)
    len_b = lin.norm(vector_b)
    if not len_a or not len_b:
        return 0
    scalar_product = np.dot(vector_a, vector_b)
    cos_a = scalar_product / (len_a * len_b)
    return acos(cos_a)


class ConvexPolygon:

    def __init__(self, points):
        self.points = points
        self.plane = Plane.create_plane(points[0], points[1], points[2])
        print(points)

    def intersect(self, ray):
        """
        Return common point of polygon and ray.
        If there is many such point, return None.
        If there is no such point, return None.
        """
        suspect = self.plane.intersect(ray)
        if suspect is None:
            return None
        if self.contain(suspect):
            return suspect
        return None

    def contain(self, point):
        """
        Check if polygon contain that point.
        """
        points = self.points
        orientation = np.cross(points[2] - points[0], points[1] - points[0])
        for p1, p2 in zip(points, np.roll(points, -1, axis=0)):
            res = np.cross(point - p1, p2 - p1)
            if not is_collinear(res, orientation):
                return False
        return True


def rotation_matrix_x(alpha):
    return np.matrix([[1, 0, 0],
                      [0, cos(alpha), -sin(alpha)],
                      [0, sin(alpha),  cos(alpha)]])


def rotation_matrix_y(alpha):
    return np.matrix([[cos(alpha), 0, sin(alpha)],
                      [0, 1, 0],
                      [-sin(alpha), 0,  cos(alpha)]])


def rotation_matrix_z(alpha):
    return np.matrix([[cos(alpha), -sin(alpha), 0],
                      [sin(alpha), cos(alpha), 0],
                      [0, 0, 1]])


def rotation_matrix(angles):
    matrix_x = rotation_matrix_x(angles[0])
    matrix_y = rotation_matrix_y(angles[1])
    matrix_z = rotation_matrix_z(angles[2])
    return matrix_x.dot(matrix_y).dot(matrix_z)
