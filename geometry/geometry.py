import math
import numpy.linalg as lin
import numpy as np
from geometry.geometry3d import ConvexPolygon
from geometry.geometry3d import Ray
from geometry.geometry3d import rotation_matrix
from geometry.geometry3d import get_angle

__author__ = 'Artyom_Lobanov'


ACUTE_ANGLE_BOUND = math.pi / 6


def to_cartesian_coordinates(point):
    return point[:3] / point[3]


class Object3D:

    def __init__(self, faces, points):
        self.faces = faces  # list of numpy.array which define faces
        self.point_store = PointStore(points)
        # maps edges to faces by numbers
        self.neighbors = []
        self.edges = []
        self.interesting_edges = []
        self.normals = [None] * len(faces)
        edges_index = dict()

        def sort(pair):  # to do it faster than sorted
            if pair[0] > pair[1]:
                return pair[::-1]
            return pair

        def find_normal(polygon):
            point_a = to_cartesian_coordinates(points[polygon[0]])
            point_b = to_cartesian_coordinates(points[polygon[1]])
            point_c = to_cartesian_coordinates(points[polygon[2]])
            normal = np.cross(point_b - point_a, point_c - point_a)
            return normal / lin.norm(normal)

        for face_number, face in enumerate(faces):
            for edge in zip(face, np.roll(face, -1, axis=0)):
                edge = sort(edge)
                index = edges_index.get(edge)
                if index is None:
                    index = edges_index[edge] = len(self.edges)
                    self.edges.append(edge)
                    self.neighbors.append([])
                self.neighbors[index].append(face_number)
            self.normals[face_number] = find_normal(face)

        for edge_number, lst in enumerate(self.neighbors):
            if len(lst) != 2:
                continue
            normal_a, normal_b = [self.normals[i] for i in lst]
            angle = get_angle(normal_a, normal_b)
            if math.pi - angle < ACUTE_ANGLE_BOUND:
                self.interesting_edges.append(edge_number)

    def check_visible(self, camera_position):
        """
        return array of bools
        If nth-element in that array is True,
        edge number n is visible
        """
        matrix = rotation_matrix(-camera_position.orientation)
        ray = matrix.dot([0, 0, 1]).A1
        return [np.dot(n, ray) < 0 for n in self.normals]

    def get_visible_edges(self, camera_position):
        """
        return array of visible edges
        """
        is_visible = self.check_visible(camera_position)

        def check(edge_number):
            lst = self.neighbors[edge_number]
            if len(lst) != 2:
                return False
            face_a, face_b = lst
            return is_visible[face_a] and is_visible[face_b]

        res = [edge for i, edge in enumerate(self.edges) if check(i)]
        return [self.point_store.get_points(edge) for edge in res]

    def get_border(self, camera_position):
        is_visible = self.check_visible(camera_position)

        def check(edge_number):
            lst = self.neighbors[edge_number]
            if len(lst) != 2:
                return False
            face_a, face_b = lst
            return is_visible[face_a] ^ is_visible[face_b]

        res = [edge for i, edge in enumerate(self.edges) if check(i)]
        return [self.point_store.get_points(edge) for edge in res]

    def intersect(self, ray):
        begin = ray.begin
        res = None
        for face in self.faces:
            points = self.point_store.array[face]
            points = [to_cartesian_coordinates(p) for p in points]
            polygon = ConvexPolygon(points)
            point = polygon.intersect(ray)
            if point is None:
                continue
            if res is None:
                res = point
            if lin.norm(res - begin) > lin.norm(point - begin):
                res = point
        return res

    def get_original(self, camera_position, camera_params, x, y):
        point = np.array([x - camera_params[0, 2], y - camera_params[1, 2], 1])
        point = rotation_matrix(-camera_position.orientation).dot(point)
        point = point + camera_position.translation
        ray = Ray(camera_position.translation, point)
        return self.intersect(ray)


class PointStore:
    def __init__(self, points):
        self.array = np.empty((len(points), 4), dtype=np.float_)
        self.size = len(points)
        for i, point in enumerate(points):
            self.array[i, :] = point

    def transform(self, transformation):
        # matrix.A is an ndarray with equal elements
        self.array = self.array.dot(transformation.transpose()).A

    def get_points(self, i):
        """
        if i is number, return point
        if i is list or tuple, return list of points
        """
        return self.array[i, :]
