__author__ = 'Artyom'


class Point:

    def __init__(self, x, y, z, w=1):
        self.x = x
        self.y = y
        self.z = z
        self.w = w

    def __repr__(self):
        lst = [self.x, self.y, self.z, self.w]
        lst = [str(i) for i in lst]
        return "(" + ", ".join(lst) + ")"


class Object3D:

    def __init__(self, faces, points):
        self.faces = faces  # list of tuples which define faces
        self.points = points

    def __repr__(self):
        points = [p.__repr__() for p in self.points]
        faces = [f.__repr__() for f in self.faces]
        return "Object3D[points = " + ",\n".join(points) + "]\n[faces = " + ",\n".join(faces) + "]"
