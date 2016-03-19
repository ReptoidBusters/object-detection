import cv2
import numpy


def get_edge_map(img):
    return cv2.Canny(img, 100, 200) # need to choose thresholds properly


def get_orientation_map(img):
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    xder = cv2.Sobel(gray_img, cv2.CV_32F, 1, 0) # need to pay attention to the arguments
    yder = cv2.Sobel(gray_img, cv2.CV_32F, 0, 1) # need to pay attention to the arguments
    
    return cv2.phase(xder, yder, angleInDegrees = True)


def quantized(orientation_map, quantization_channels):
    quantized_map = numpy.ndarray(orientation_map.shape, float)
    unit_angle = 360.0 / quantization_channels
    
    for i, row in enumerate(orientation_map):
        for j, angle in enumerate(row):
            units_number = int(round(angle / 360.0 * quantization_channels)) % quantization_channels
            quantized_map[i][j] = unit_angle * units_number
    
    return quantized_map


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        
    
    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)


class PointSupport:
    def __init__(self, point):
        self.point = point
        self.support = 0


def find_support(edge_map, orientation_map, x, y):
    pass


def linearize(edge_map, orientation_map, quantization_channels):
    orientation_map = quantized(orientation_map, quantization_channels)
    pass


