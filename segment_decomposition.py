import cv2
import numpy
import collections


def get_edge_map(img):
    return cv2.Canny(img, 100, 200) # need to choose thresholds properly


def get_orientation_map(img):
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    xder = cv2.Sobel(gray_img, cv2.CV_32F, 1, 0) # need to pay attention to the arguments
    yder = cv2.Sobel(gray_img, cv2.CV_32F, 0, 1) # need to pay attention to the arguments
    
    orientation_map = cv2.phase(xder, yder, angleInDegrees = True)
    for i, row in enumerate(orientation_map):
        for j, angle in enumerate(row):
            orientation_map[i][j] %= 180.0
    
    return orientation_map


def quantized(orientation_map, quantization_channels):
    quantized_map = numpy.ndarray(orientation_map.shape, float)
    unit_angle = 180.0 / quantization_channels
    
    for i, row in enumerate(orientation_map):
        for j, angle in enumerate(row):
            units_number = int(round(angle / 180.0 * quantization_channels)) % quantization_channels
            quantized_map[i][j] = unit_angle * units_number
    
    return quantized_map


class PointSupport:
    def __init__(self, point, orientation):
        self.point = point
        self.orientation = orientation
        self.support = 0
        self.list = []
        
    def add_point(self, point):
        self.support += 1
        self.list.append(point)
        return True


def find_support(edge_map, point_orientation, initial_point):
    directions = [numpy.array([0, 1]), numpy.array([1, 0]), numpy.array([0, -1]), numpy.array([-1, 0]),
    numpy.array([1, 1]), numpy.array([1, -1]), numpy.array([-1, -1]), numpy.array([-1, 1])]
    
    used_point = numpy.ndarray(edge_map.shape, bool)
    used_point.fill(False)
    
    support = PointSupport(initial_point, point_orientation)
    
    queue = collections.deque()
    queue.append(initial_point)
    used_point[initial_point[0]][initial_point[1]] = True
    
    while len(queue) > 0:
        point = queue.popleft()
        if not support.add_point(point):
            continue
            
        for d in directions:
            next_point = point + d
            
            # looks ugly
            if 0 > next_point[0] or next_point[0] >= len(edge_map) or 0 > next_point[1] or next_point[1] >= len(edge_map[0]):
                continue
                
            if edge_map[next_point[0]][next_point[1]] == 0 or used_point[next_point[0]][next_point[1]]:
                continue
            
            queue.append(next_point)
            used_point[next_point[0]][next_point[1]] = True
    
    return support


def linearize(edge_map, orientation_map, quantization_channels):
    orientation_map = quantized(orientation_map, quantization_channels)
    pass


