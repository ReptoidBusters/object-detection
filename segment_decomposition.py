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
    quantized_map = numpy.ndarray(orientation_map.shape, int)
    for i, row in enumerate(orientation_map):
        for j, angle in enumerate(row):
            quantized_map[i][j] = angle / 360.0 * quantization_channels
    
    return quantized_map


def linearize(edge_map, orientation_map, quantization_channels):
    pass


