import numpy as np
from geometry.geometry import Object3D

__author__ = 'Artyom_Lobanov'


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
        with open(path) as file:
            for line in file.readlines():
                self.parse(line)
        self.object = Object3D(self.faces, self.points)

    def parse(self, line):
        line = line.strip()  # remove spaces from the begin of line
        if line.startswith("v "):  # new point
            self.parse_point(line)
        if line.startswith("f "):  # new polygon
            self.parse_face(line)

    def parse_point(self, line):
        args = [float(x) for x in line.split()[1:]]
        if len(args) == 3:
            args += [1]
        self.points.append(np.asarray(args))

    def parse_face(self, line):
        def validate(i):
            i = int(i)
            if i > 0:
                i -= 1
            else:
                i += len(self.points)
            return i
        params = line.split()  # get tokens
        # cut numbers of points from line
        params = [word.split("/")[0] for word in params[1:]]
        # translate numbers to valid index
        params = [validate(num) for num in params]
        self.faces.append(np.asarray(params))

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


def load_object(path):
    parser = Parser()
    parser.read_file(path)
    return parser.get_object()
