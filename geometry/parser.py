from geometry import Point
from geometry import Face
from geometry import Object3D

__author__ = 'Artyom'


class Parser:

    def __init__(self):
        self.points = []
        self.faces = []
        self.object = None
        self.path = None

    def read_file(self, path):
        self.points = []
        self.faces = []
        self.path = path
        file = open(path, "r")
        for line in file.readlines():
            self.parse(line)
        self.object = Object3D(self.faces)
        file.close()

    def parse(self, line):
        line = line.strip()  # remove spaces from the begin of line
        if line.startswith("v "):  # new point
            self.parse_point(line)
        if line.startswith("f "):  # new polygon
            self.parse_face(line)

    def parse_point(self, line):
        params = [float(x) for x in line.split()[1:]]
        if len(params) == 3:
            self.points.append(Point(params[0], params[1], params[2]))
        else:
            self.points.append(Point(params[0], params[1], params[2], params[3]))

    def parse_face(self, line):
        params = line.split()
        face_points = []
        for i in [int(ind.split("/")[0]) for ind in params[1:]]:  # parse numbers of points
            if i > 0:
                i -= 1
            face_points.append(self.points[i])
        self.faces.append(Face(face_points))

    def get_object(self):
        return self.object

    def get_points(self):
        return self.points

    def get_faces(self):
        return  self.faces

    def __repr__(self):
        if not self.object:
            return "Parser is empty"
        return "File " + self.path + " parsed. Object read: \n" + self.object.__repr__()

"""
p = Parser()
p.read_file("C:/workspace/test.txt")
print(p)
"""
