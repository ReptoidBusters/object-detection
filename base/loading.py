import numpy as np
from base.geometry import Object3D

__author__ = 'Artyom_Lobanov'


class Parser:

    def __init__(self):
        self._points = []
        self._faces = []
        self._object = None
        self._path = None

    def read_file(self, path):
        self._points = []
        self._faces = []
        self._path = path
        with open(path) as file:
            for line in file.readlines():
                self._parse(line)
        self._object = Object3D(self._faces, self._points)

    def _parse(self, line):
        line = line.strip()  # remove spaces from the begin of line
        if line.startswith("v "):  # new point
            self._parse_point(line)
        if line.startswith("f "):  # new polygon
            self._parse_face(line)

    def _parse_point(self, line):
        args = [float(x) for x in line.split()[1:]]
        if len(args) == 3:
            args += [1]
        self._points.append(np.asarray(args))

    def _parse_face(self, line):
        def validate(i):
            i = int(i)
            if i > 0:
                i -= 1
            else:
                i += len(self._points)
            return i
        params = line.split()  # get tokens
        # cut numbers of points from line
        params = [word.split("/")[0] for word in params[1:]]
        # translate numbers to valid index
        params = [validate(num) for num in params]
        self._faces.append(np.asarray(params))

    def get_object(self):
        return self._object

    def get_points(self):
        return self._points

    def get_faces(self):
        return self._faces

    def __repr__(self):
        if not self._object:
            return "Parser is empty"
        return "File " + self._path + " parsed. Object read: \n" \
               + self._object.__repr__()


def load_object(path):
    parser = Parser()
    parser.read_file(path)
    return parser.get_object()
