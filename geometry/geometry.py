import numpy.linalg as lin
import numpy as np
from geometry.geometry3D import ConvexPolygon
from geometry.geometry3D import Ray
__author__ = 'Artyom_Lobanov'


class Point:
    def __init__(self, x, y, z, w=1):
        self.vector = np.array([x, y, z, w])

    @staticmethod
    def key_code(key):
        return {"x": 0, "y": 1, "z": 2, "w": 3}[key]

    def __setattr__(self, key, value):
        if key == "vector":
            self.__dict__[key] = value
        else:
            self.__dict__["vector"][self.key_code(key)] = value

    def __getattr__(self, key):
        return self.vector[Point.key_code(key)]

    def __repr__(self):
        lst = [self.x, self.y, self.z, self.w]
        lst = [str(i) for i in lst]
        return "(" + ", ".join(lst) + ")"

    def normalize(self):
        if self.vector[3] == 0:
            raise Exception("infinite point")
        self.vector = self.vector / self.vector[3]

    def as_vector(self):
        return self.vector

    def to_cartesian_coordinates(self):
        return self.vector[:3] / self.vector[3]


class Object3D:

    def __init__(self, faces, points):
        self.faces = faces  # list of tuples which define faces
        self.point_store = PointStore(points)

    def __repr__(self):
        points = [p.__repr__() for p in self.point_store.to_points_array()]
        faces = [f.__repr__() for f in self.faces]
        return "Object3D[points = " + ",\n".join(points) + "]\n[faces = " + ",\n".join(faces) + "]"

    def intersect(self, p1, p2):
        p1 = p1.to_cartesian_coordinates()
        p2 = p2.to_cartesian_coordinates()
        ray = Ray(p1, p2)
        res = None
        for face in self.faces:
            points = [self.point_store.get_point(i) for i in face]
            points = [p.to_cartesian_coordinates() for p in points]
            polygon = ConvexPolygon(points)
            point = polygon.intersect(ray)
            if point is None:
                continue
            if res is None:
                res = point
            if lin.norm(res - p1) > lin.norm(point - p1):
                res = point
        return res


class PointStore:
    def __init__(self, points):
        self.array = np.empty((len(points), 4), dtype=np.double)
        self.size = len(points)
        for i in range(len(points)):
            self.array[i, :] = points[i].as_vector()

    def transform(self, index, transformation):
        self.array[index, :] *= transformation.transpose()

    def transform_all(self, transformation):
        self.array = self.array.dot(transformation.transpose())

    def normalize_all(self):
        for i in range(4):
            self.array[:, i] /= self.array[:, 3]

    def get_point(self, i):
        return Point(*self.array[i, :])

    def get_vector(self, i):
        return self.array[i, :]

    def to_points_array(self):
        return [self.get_point(i) for i in range(self.size)]
