from geometry.geometry import Point
from geometry.geometry import Face
from geometry.geometry import Object3D

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
        args = [float(x) for x in line.split()[1:]]
        if len(args) == 3:
            self.points.append(Point(args[0], args[1], args[2]))
        else:
            self.points.append(Point(args[0], args[1], args[2], args[3]))

    def parse_face(self, line):
        params = line.split()
        params = [word.split("/")[0] for word in params[1:]]  # cut numbers of points from line
        face_points = []
        for i in [int(j) for j in params]:
            if i > 0:
                i -= 1
            face_points.append(self.points[i])
        self.faces.append(Face(face_points))

    def get_object(self):
        return self.object

    def get_points(self):
        return self.points

    def get_faces(self):
        return self.faces

    def __repr__(self):
        if not self.object:
            return "Parser is empty"
        return "File " + self.path + " parsed. Object read: \n" \
               + self.object.__repr__()
