import numpy.linalg as lin
import numpy as np
from geometry.geometry3D import ConvexPolygon
from geometry.geometry3D import Ray
from geometry.geometry3D import rotation_matrix

__author__ = 'Artyom_Lobanov'


def to_cartesian_coordinates(point):
    return point[:3] / point[3]


class Object3D:

    def __init__(self, faces, points):
        self.faces = faces  # list of numpy.array which define faces
        self.point_store = PointStore(points)

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

    def get_original(self, camera_position, camera_parameters, x, y):
        point = np.array([x - camera_parameters[0, 2], y - camera_parameters[1, 2], 1])
        point = rotation_matrix(-camera_position.orientation).dot(point)
        point = point + camera_position.translation
        ray = Ray(camera_position.translation, point)
        return self.intersect(ray)


class PointStore:
    def __init__(self, points):
        self.array = np.empty((len(points), 4), dtype=np.double)
        self.size = len(points)
        for i in range(len(points)):
            self.array[i, :] = points[i]

    def transform(self, transformation):
        self.array = self.array.dot(transformation.transpose())

    def normalize(self):
        for i in range(4):
            self.array[:, i] /= self.array[:, 3]

    def get_point(self, i):
        return self.array[i, :]

    def to_points_array(self):
        return [self.get_point(i) for i in range(self.size)]
