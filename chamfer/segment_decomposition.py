import collections
import math
import random
import copy
import numpy
import cv2


def get_edge_map(img, threshold1, threshold2):
    return cv2.Canny(img, threshold1, threshold2)


def convert_to_binary(img):
    binary_img = numpy.ndarray(img.shape[0:2], numpy.uint8)
    for i in range(0, len(img)):
        for j in range(0, len(img[i])):
            if img[i][j].any():
                binary_img[i][j] = 255
            else:
                binary_img[i][j] = 0

    return binary_img


def get_orientation_map(img):
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    xder = cv2.Sobel(gray_img, cv2.CV_64F, 1, 0)
    yder = cv2.Sobel(gray_img, cv2.CV_64F, 0, 1)

    orientation_map = cv2.phase(xder, yder)
    for i, row in enumerate(orientation_map):
        for j, _ in enumerate(row):
            orientation_map[i][j] += math.pi / 2
            orientation_map[i][j] %= math.pi

    return orientation_map


def quantized(orientation_map, quantization_channels):
    quantized_map = numpy.ndarray(orientation_map.shape, int)

    for i, row in enumerate(orientation_map):
        for j, angle in enumerate(row):
            units_number = int(round(angle / math.pi * quantization_channels))
            units_number %= quantization_channels
            quantized_map[i][j] = units_number

    return quantized_map


def angle_from_channel(channel, quantization_channels):
    unit_angle = math.pi / quantization_channels
    return channel * unit_angle


class PointSupport:
    def __init__(self, point, orientation_channel, quantization_channels):
        self.point = point
        self.orientation = angle_from_channel(orientation_channel,
                                              quantization_channels)
        self.orientation_channel = orientation_channel
        self.support = 0
        self.list = []

    def angle_deviation(self, point):
        line_vector = numpy.array([math.cos(self.orientation),
                                   math.sin(self.orientation)])
        point_vector = point - self.point

        cross_product = numpy.cross(line_vector, point_vector)
        dot_product = numpy.dot(line_vector, point_vector)
        deviation = math.atan2(cross_product, dot_product) + 2 * math.pi
        return deviation % math.pi

    def residual(self, point):
        distance = numpy.linalg.norm(self.point - point)
        res = distance * math.sin(self.angle_deviation(point))
        return res

    def add_point(self, point, residual):
        if self.residual(point) > residual:
            return False

        self.support += 1
        self.list.append(point)
        return True


class LineSegment:
    # pylint: disable=too-many-instance-attributes
    def __init__(self):
        self.orientation = None
        self.ytype = None
        self.point = None
        self.orientation_channel = None
        self.left_bound = None
        self.right_bound = None
        self.y_angle_coefficient = None
        self.x_angle_coefficient = None

    @staticmethod
    def from_support(support, maxy, maxx):
        # pylint: disable=protected-access
        self = LineSegment()
        self.orientation = support.orientation
        self.ytype = self._determine_type()

        self._calculate_coefficients()

        self.point = self._get_base_point(support.point)
        self.orientation_channel = support.orientation_channel
        self._calculate_bounds(support, maxy, maxx)

        return self

    @staticmethod
    def from_orientation(orientation_channel,
                         quantization_channels,
                         coordinate):
        # pylint: disable=protected-access
        self = LineSegment()
        self.orientation = angle_from_channel(orientation_channel,
                                              quantization_channels)
        self.ytype = self._determine_type()
        self._calculate_coefficients()

        if self.ytype:
            self.point = numpy.array([coordinate, 0])
        else:
            self.point = numpy.array([0, coordinate])

        self.orientation_channel = orientation_channel

        return self

    @staticmethod
    def shifted(line_segment, shift):
        # pylint: disable=protected-access
        self = LineSegment()
        self.orientation = line_segment.orientation
        self.ytype = line_segment.ytype
        self._calculate_coefficients()
        self.point = self._get_base_point(line_segment.point + shift)
        self.orientation_channel = line_segment.orientation_channel

        if self.ytype:
            axis = 1
        else:
            axis = 0

        self.left_bound = line_segment.left_bound + shift[axis]
        self.right_bound = line_segment.right_bound + shift[axis]

        return self

    def _calculate_coefficients(self):
        if not self.ytype:
            self.y_angle_coefficient = math.tan(self.orientation)
        else:
            self.x_angle_coefficient = 1 / math.tan(self.orientation)

    def _determine_type(self):
        return math.pi / 4 <= self.orientation <= 3 * math.pi / 4

    def _get_point_relative(self, index):
        if not self.ytype:
            y_coord = int(round(self.y_angle_coefficient * index))
            point = numpy.array([index, y_coord])
        else:
            x_coord = int(round(self.x_angle_coefficient * index))
            point = numpy.array([x_coord, index])

        return point

    def get_point(self, index):
        return self.point + self._get_point_relative(index)

    def _get_base_point(self, given_point):
        if not self.ytype:
            point = self._get_point_relative(given_point[0])
        else:
            point = self._get_point_relative(given_point[1])

        return given_point - point

    def _calculate_bounds(self, support, maxy, maxx):
        if self.ytype:
            axis = 1
        else:
            axis = 0

        self.left_bound = support.point[axis]
        self.right_bound = support.point[axis]
        for point in support.list:
            candidate = point[axis] - self.point[axis]
            self.left_bound = min(self.left_bound, candidate)
            self.right_bound = max(self.right_bound, candidate)

        while True:
            point = self.get_point(self.left_bound)
            if 0 <= point[1] <= maxy and 0 <= point[0] <= maxx:
                break

            self.left_bound += 1

        while True:
            point = self.get_point(self.right_bound)
            if 0 <= point[1] <= maxy and 0 <= point[0] <= maxx:
                break

            self.right_bound -= 1

    def get_points_list(self):
        result = []
        for index in range(self.left_bound, self.right_bound + 1):
            result.append(self.get_point(index))

        return result

    def get_points_amount(self):
        return self.right_bound - self.left_bound + 1


def find_support(edge_map, point_orientation_channel,
                 quantization_channels, initial_point, residual):
    directions = [numpy.array([0, 1]), numpy.array([1, 0]),
                  numpy.array([0, -1]), numpy.array([-1, 0]),
                  numpy.array([1, 1]), numpy.array([1, -1]),
                  numpy.array([-1, -1]), numpy.array([-1, 1])]

    used_point = numpy.ndarray(edge_map.shape, bool)
    used_point.fill(False)

    support = PointSupport(initial_point,
                           point_orientation_channel,
                           quantization_channels)

    queue = collections.deque()
    queue.append(initial_point)
    used_point[initial_point[1]][initial_point[0]] = True

    while len(queue) > 0:
        point = queue.popleft()
        if not support.add_point(point, residual):
            continue

        for dircn in directions:
            next_point = point + dircn

            if (not (0 <= next_point[1] < len(edge_map) and
                     0 <= next_point[0] < len(edge_map[0])) or
                    edge_map[next_point[1]][next_point[0]] == 0 or
                    used_point[next_point[1]][next_point[0]]):
                continue

            queue.append(next_point)
            used_point[next_point[1]][next_point[0]] = True

    return support


def guess_quantized_orientation_map(edge_map,
                                    quantization_channels, pixel_residual):
    orientation_map = numpy.ndarray(edge_map.shape, int)
    for i in range(0, len(orientation_map)):
        for j in range(0, len(orientation_map[i])):
            if edge_map[i][j] == 0:
                orientation_map[i][j] = 0
                continue

            support = PointSupport(numpy.array([0, 0]),
                                   0.0,
                                   quantization_channels)

            for channel in range(0, quantization_channels):
                newsupport = find_support(edge_map,
                                          channel,
                                          quantization_channels,
                                          numpy.array([j, i]), pixel_residual)

                if newsupport.support >= support.support:
                    support = newsupport

            orientation_map[i][j] = support.orientation_channel

    return orientation_map


def linearize(edge_map, orientation_map,
              quantization_channels, pixel_residual):
    edge_map = copy.deepcopy(edge_map)
    base_points = copy.deepcopy(edge_map)

    pts_list = []
    for i in range(0, len(base_points)):
        for j in range(0, len(base_points[i])):
            if base_points[i][j] == 255:
                pts_list.append(numpy.array([j, i]))

    segments_list = []
    while len(pts_list):
        support = PointSupport(numpy.array([0, 0]), 0.0, quantization_channels)
        candidates = 10

        while len(pts_list) and candidates:
            index = random.randint(0, len(pts_list) - 1)
            point = pts_list[index]
            if base_points[point[1]][point[0]] == 0:
                pts_list[index], pts_list[-1] = pts_list[-1], pts_list[index]
                pts_list.pop()
                continue

            candidates -= 1
            newsupport = find_support(edge_map,
                                      orientation_map[point[1]][point[0]],
                                      quantization_channels,
                                      point, pixel_residual)

            if newsupport.support >= support.support:
                support = newsupport

        if support.support < 5:
            base_points[support.point[1]][support.point[0]] = 0
            continue

        segments_list.append(LineSegment.from_support(support,
                                                      len(base_points) - 1,
                                                      len(base_points[0]) - 1))

        for support_point in support.list:
            base_points[support_point[1]][support_point[0]] = 0
            edge_map[support_point[1]][support_point[0]] = 0

    return segments_list
