import math
import numpy.linalg as lin
import numpy as np
from geometry.geometry3d import ConvexPolygon
from geometry.geometry3d import Ray
from geometry.geometry3d import rotation_matrix
from geometry.geometry3d import get_angle

__author__ = 'Artyom_Lobanov'


ACUTE_ANGLE_BOUND = math.pi / 6


def _to_cartesian_coordinates(point):
    return point[:3] / point[3]


class Object3D:

    def __init__(self, faces, points):
        self._faces = faces  # list of numpy.array which define faces
        self._point_store = PointStore(points)
        # maps edges to faces by numbers
        self._neighbors = []
        self._edges = []
        self._interesting_edges = []
        self._normals = [None] * len(faces)
        edges_index = dict()

        def sort(pair):  # to do it faster than sorted
            if pair[0] > pair[1]:
                return pair[::-1]
            return pair

        def find_normal(polygon):
            point_a = _to_cartesian_coordinates(points[polygon[0]])
            point_b = _to_cartesian_coordinates(points[polygon[1]])
            point_c = _to_cartesian_coordinates(points[polygon[2]])
            normal = np.cross(point_b - point_a, point_c - point_a)
            return normal / lin.norm(normal)

        for face_number, face in enumerate(faces):
            for edge in zip(face, np.roll(face, -1, axis=0)):
                edge = sort(edge)
                index = edges_index.get(edge)
                if index is None:
                    index = edges_index[edge] = len(self._edges)
                    self._edges.append(edge)
                    self._neighbors.append([])
                self._neighbors[index].append(face_number)
            self._normals[face_number] = find_normal(face)

        for edge_number, lst in enumerate(self._neighbors):
            if len(lst) != 2:
                continue
            normal_a, normal_b = [self._normals[i] for i in lst]
            angle = get_angle(normal_a, normal_b)
            if math.pi - angle < ACUTE_ANGLE_BOUND:
                self._interesting_edges.append(edge_number)

    def _check_visible(self, camera_position):
        matrix = rotation_matrix(-camera_position.orientation)
        ray = matrix.dot([0, 0, 1]).A1
        return [np.dot(n, ray) < 0 for n in self._normals]

    def _convert_edges(self, lst):
        return [self._point_store.get_points(self._edges[i]) for i in lst]

    def get_interesting_edges(self):
        return self._convert_edges(self._interesting_edges)

    def get_visible_edges(self, camera_position):
        """
        return array of visible edges
        """
        is_visible = self._check_visible(camera_position)

        def check(edge_number):
            lst = self._neighbors[edge_number]
            if len(lst) != 2:
                return False
            face_a, face_b = lst
            return is_visible[face_a] and is_visible[face_b]

        res = [edge for i, edge in enumerate(self._edges) if check(i)]
        return self._convert_edges(res)

    def get_border(self, camera_position):
        is_visible = self._check_visible(camera_position)

        def check(edge_number):
            lst = self._neighbors[edge_number]
            if len(lst) != 2:
                return False
            face_a, face_b = lst
            return is_visible[face_a] ^ is_visible[face_b]

        res = [edge for i, edge in enumerate(self._edges) if check(i)]
        return self._convert_edges(res)

    def _intersect(self, ray):
        begin = ray.begin
        res = None
        for face in self._faces:
            points = self._point_store.get_points(face)
            points = [_to_cartesian_coordinates(p) for p in points]
            polygon = ConvexPolygon(points)
            point = polygon.intersect(ray)
            if point is None:
                continue
            if res is None:
                res = point
            if lin.norm(res - begin) > lin.norm(point - begin):
                res = point
        return res

    def get_original(self, camera_position, camera_params, screen_x, screen_y):
        x_relative_to_centre = screen_x - camera_params[0, 2]
        y_relative_to_centre = screen_y - camera_params[1, 2]
        point = np.ndarray([x_relative_to_centre, y_relative_to_centre, 1])
        point = rotation_matrix(-camera_position.orientation).dot(point)
        point = point + camera_position.translation
        ray = Ray(camera_position.translation, point)
        return self._intersect(ray)


class PointStore:
    def __init__(self, points):
        self._array = np.empty((len(points), 4), dtype=np.float_)
        self.size = len(points)
        for i, point in enumerate(points):
            self._array[i, :] = point

    def transform(self, transformation):
        # matrix.A is an ndarray with equal elements
        self._array = self._array.dot(transformation.transpose()).A

    def get_points(self, i):
        """
        if i is number, return point
        if i is list or tuple, return list of points
        """
        return self._array[i, :]
