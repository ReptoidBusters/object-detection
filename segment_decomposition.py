import cv2
import numpy
import collections
import math


def get_edge_map(img):
    return cv2.Canny(img, 100, 200)  # Need to choose thresholds properly


def get_orientation_map(img):
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Need to pay attention to the arguments
    xder = cv2.Sobel(gray_img, cv2.CV_32F, 1, 0)
    yder = cv2.Sobel(gray_img, cv2.CV_32F, 0, 1)
    
    orientation_map = cv2.phase(xder, yder)
    for i, row in enumerate(orientation_map):
        for j, angle in enumerate(row):
            orientation_map[i][j] %= math.pi
    
    return orientation_map


def quantized(orientation_map, quantization_channels):
    quantized_map = numpy.ndarray(orientation_map.shape, float)
    unit_angle = math.pi / quantization_channels
    
    for i, row in enumerate(orientation_map):
        for j, angle in enumerate(row):
            units_number = int(round(angle / math.pi * quantization_channels))
            units_number %= quantization_channels
            
            quantized_map[i][j] = unit_angle * units_number
    
    return quantized_map


class PointSupport:
    def __init__(self, point, orientation):
        self.point = point
        self.orientation = orientation
        self.support = 0
        self.list = []
    
    
    def angle_deviation(self, point):
        cross_product = numpy.cross(self.point, point)
        dot_product = numpy.dot(self.point, point)
        point_orientation = math.atan2(cross_product, dot_product) + math.pi
        point_orientation %= math.pi
        return abs(self.orientation - point_orientation)
    
    
    def residual(self, point):
        distance = numpy.linalg.norm(self.point - point)
        res = distance * math.sin(self.angle_deviation(point))
        print(res)
        return res
    
    def add_point(self, point):
        if self.residual(point) > 10:  # Need to choose thresholds properly
            return
        
        self.support += 1
        self.list.append(point)
        return True


def find_support(edge_map, point_orientation, initial_point):
    directions = [numpy.array([0, 1]), numpy.array([1, 0]),
                  numpy.array([0, -1]), numpy.array([-1, 0]),
                  numpy.array([1, 1]), numpy.array([1, -1]),
                  numpy.array([-1, -1]), numpy.array([-1, 1])]
    
    used_point = numpy.ndarray(edge_map.shape, bool)
    used_point.fill(False)
    
    support = PointSupport(initial_point, point_orientation)
    
    queue = collections.deque()
    queue.append(initial_point)
    used_point[initial_point[1]][initial_point[0]] = True
    
    while len(queue) > 0:
        point = queue.popleft()
        if not support.add_point(point):
            continue
            
        for d in directions:
            next_point = point + d
            
            if (edge_map[next_point[1]][next_point[0]] == 0 or
                used_point[next_point[1]][next_point[0]] or
                not (0 <= next_point[0] < len(edge_map) and
                     0 <= next_point[1] < len(edge_map[0]))):
                continue
            
            queue.append(next_point)
            used_point[next_point[1]][next_point[0]] = True
    
    return support


def linearize(edge_map, orientation_map, quantization_channels):
    orientation_map = quantized(orientation_map, quantization_channels)
    pass


