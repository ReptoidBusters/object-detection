import cv2
import numpy
import collections
import math
import random

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
            orientation_map[i][j] += math.pi / 2
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
        self.list = [point]
    
    def angle_deviation(self, point):
        line_vector = numpy.array([math.cos(self.orientation), math.sin(self.orientation)])
        point_vector = point - self.point
        
        cross_product = numpy.cross(line_vector, point_vector)
        dot_product = numpy.dot(line_vector, point_vector)
        deviation = math.atan2(cross_product, dot_product) + 2 * math.pi
        return deviation % math.pi
    
    def residual(self, point):
        distance = numpy.linalg.norm(self.point - point)
        res = distance * math.sin(self.angle_deviation(point))
        return res
    
    def add_point(self, point):
        if self.residual(point) > 2:  # Need to choose thresholds properly
            return False
        
        self.support += 1
        self.list.append(point)
        return True


class LineSegment:
    def __init__(self, support):
        self.point = support.point
        self.orientation = support.orientation
        self.ytype = self._determine_type()
        self._calculate_bounds(support)
    
    def _determine_type(self):
        return math.pi / 4 <= self.orientation <= 3 * math.pi / 4
        
    def _calculate_bounds(self, support):
        if self.ytype:
            axis = 1
        else:
            axis = 0
        
        self.left_bound = 0
        self.right_bound = 0
        for point in support.list:
            self.left_bound = min(self.left_bound, point[axis] - self.point[axis])
            self.right_bound = max(self.right_bound, point[axis] - self.point[axis])
    
    def get_points_list(self):
        result = []
        if not self.ytype:
            for x in range(self.left_bound, self.right_bound):
                result.append(numpy.array([x, math.tan(self.orientation) * x]) + self.point)
        else:
            for y in range(self.left_bound, self.right_bound):
                result.append(numpy.array([1 / math.tan(self.orientation) * y, y]) + self.point)
        
        return result


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
    #orientation_map = quantized(orientation_map, quantization_channels)

    points_list = []
    for i in range(0, len(edge_map)):
        for j in range(0, len(edge_map[i])):
            if edge_map[i][j] == 255:
                points_list.append(numpy.array([j, i]))
    
    segments_list = []
    while len(points_list):
        support = PointSupport(numpy.array([0, 0]), 0.0)
        for i in range(1, 10):
            point = points_list[random.randint(0, len(points_list) - 1)]
            newsupport = find_support(edge_map, orientation_map[point[1]][point[0]], point)
            if newsupport.support >= support.support:
                support = newsupport

        segments_list.append(LineSegment(support))
        for support_point in support.list:
            edge_map[support_point[1]][support_point[0]] = 0
            for i in range(0, len(points_list)):
                if (support_point == points_list[i]).all():
                    points_list.pop(i)
                    break

    return segments_list
    
