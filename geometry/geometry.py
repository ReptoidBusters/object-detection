__author__ = 'Artyom'


class Point:

    def __init__(self, x, y, z, w=1):
        self.x = x
        self.y = y
        self.z = z
        self.w = w

    def __repr__(self):
        return "(" + str(self.x) + ", " + str(self.y) + ", " + str(self.z) + ", " + str(self.w) + ")"


class Face:

    def __init__(self, points):
        self.points = points

    def __repr__(self):
        points = [p.__repr__() for p in self.points]
        return "Face[points: " + ", ".join(points) + "]"


class Object3D:

    def __init__(self, faces):
        self.faces = faces

    def __repr__(self):
        faces = [f.__repr__() for f in self.faces]
        return "Object3D[faces = " + ",\n".join(faces) + "]"
