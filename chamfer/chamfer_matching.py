import numpy
from . segment_decomposition import LineSegment
from . segment_decomposition import get_edge_map
from . segment_decomposition import get_orientation_map
from . segment_decomposition import quantized
from . segment_decomposition import linearize
from . segment_decomposition import convert_to_binary
from . segment_decomposition import guess_quantized_orientation_map


class LinearFunction:
    def __init__(self, coefficient, constant):
        self.coefficient = coefficient
        self.constant = constant

    def eval(self, point):
        return self.coefficient * point + self.constant

    def is_good_replacement(self, lf1, lf2):
        cnst_diff = self.constant - lf1.constant
        coef_deff = lf1.coefficient - lf2.coefficient
        val1 = cnst_diff * coef_deff

        cnst_diff = lf2.constant - lf1.constant
        coef_diff = lf1.coefficient - self.coefficient
        val2 = cnst_diff * coef_diff
        return val1 <= val2

    def is_bad_function(self, next_lf, point):
        val1 = point * (self.coefficient - next_lf.coefficient)
        val2 = next_lf.constant - self.constant
        return val1 > val2


def is_in_shape(shape, point):
    return 0 <= point[1] < shape[0] and 0 <= point[0] < shape[1]


class Matcher:
    # pylint: disable=too-many-instance-attributes
    def __init__(self):
        self.hysteresis_threshold1 = 100
        self.hysteresis_threshold2 = 200
        self.quantization_channels = 16
        self.img_pixel_residual = 1.0
        self.pattern_pixel_residual = 1.0

        self.img_edge_map = None
        self.img_orientation_map = None
        self.img_orientation_map = None
        self.img_segments_list = None
        self.distance = None
        self.partial_sums_shift = None
        self.partial_sums = None
        self.pattern_edge_map = None
        self.pattern_orientation_map = None
        self.pattern_segments_list = None

    def _calculate_ydistance(self):
        shape = self.img_edge_map.shape
        max_distance = 2 * max(shape[0], shape[1])

        ydst = numpy.ndarray(shape, numpy.int64)
        ydst.fill(max_distance)
        for segment in self.img_segments_list:
            for point in segment.get_points_list():
                ydst[point[1]][point[0]] = 0

        for ycrd in range(1, shape[0]):
            for xcrd in range(0, shape[1]):
                ydst[ycrd][xcrd] = min(ydst[ycrd][xcrd],
                                       ydst[ycrd - 1][xcrd] + 1)

        for ycrd in range(shape[0] - 2, -1, -1):
            for xcrd in range(0, shape[1]):
                ydst[ycrd][xcrd] = min(ydst[ycrd][xcrd],
                                       ydst[ycrd + 1][xcrd] + 1)

        for ycrd in range(0, shape[0]):
            for xcrd in range(0, shape[1]):
                ydst[ycrd][xcrd] = (ydst[ycrd][xcrd])**2

        return ydst

    def _calculate_distances(self):
        shape = self.img_edge_map.shape
        ydst = self._calculate_ydistance()

        self.distance = numpy.ndarray(shape, numpy.int64)
        for ycrd in range(0, shape[0]):
            stack = []
            for xcrd in range(0, shape[1]):
                lfunc = LinearFunction(-2 * xcrd, xcrd**2 + ydst[ycrd][xcrd])
                while len(stack) > 1 and lfunc.is_good_replacement(stack[-2],
                                                                   stack[-1]):
                    stack.pop()

                stack.append(lfunc)

            index = 0
            for xcrd in range(0, shape[1]):
                while (index + 1 != len(stack) and
                       stack[index].is_bad_function(stack[index + 1], xcrd)):
                    index += 1

                self.distance[ycrd][xcrd] = xcrd**2 + stack[index].eval(xcrd)

    def _calculate_partial_sums(self):
        shape = self.img_edge_map.shape
        max_length = max(shape[0], shape[1])
        self.partial_sums_shift = max_length
        partial_sums_range = 3 * self.partial_sums_shift
        self.partial_sums = numpy.ndarray((self.quantization_channels,
                                           partial_sums_range,
                                           self.partial_sums_shift), int)
        self.partial_sums.fill(0)

        for channel in range(0, self.quantization_channels):
            for ind_coord in range(0, partial_sums_range):
                coord = ind_coord - self.partial_sums_shift
                line = LineSegment.from_orientation(channel,
                                                    self.quantization_channels,
                                                    coord)

                array = self.partial_sums[channel][ind_coord]
                for index in range(0, max_length):
                    if index > 0:
                        array[index] = array[index - 1]
                    else:
                        array[index] = 0

                    point = line.get_point(index)
                    if is_in_shape(shape, point):
                        array[index] += self.distance[point[1]][point[0]]

    def set_image(self, img):
        self.img_edge_map = get_edge_map(img,
                                         self.hysteresis_threshold1,
                                         self.hysteresis_threshold2)

        self.img_orientation_map = get_orientation_map(img)

        self.img_orientation_map = quantized(self.img_orientation_map,
                                             self.quantization_channels)

        self.img_segments_list = linearize(self.img_edge_map,
                                           self.img_orientation_map,
                                           self.quantization_channels,
                                           self.img_pixel_residual)
        self._calculate_distances()
        self._calculate_partial_sums()

    def set_pattern(self, pattern):
        self.pattern_edge_map = convert_to_binary(pattern)

        self.pattern_orientation_map = guess_quantized_orientation_map(
            self.pattern_edge_map,
            self.quantization_channels,
            self.pattern_pixel_residual)

        self.pattern_segments_list = linearize(self.pattern_edge_map,
                                               self.pattern_orientation_map,
                                               self.quantization_channels,
                                               self.pattern_pixel_residual)

    def _inf_pattern_cost(self):
        img_shape = self.img_edge_map.shape
        max_distance = numpy.dot(img_shape, img_shape)

        points_amount = 0
        for segment in self.pattern_segments_list:
            points_amount += segment.get_points_amount()

        return (max_distance + 1) * points_amount

    def find_occurrence(self):
        img_shape = self.img_edge_map.shape
        pattern_shape = self.pattern_edge_map.shape
        diff_shape = (img_shape[0] - pattern_shape[0],
                      img_shape[1] - pattern_shape[1])

        cost = self._inf_pattern_cost()
        occurrence = numpy.array([0, 0])
        for ycrd in range(0, diff_shape[0]):
            for xcrd in range(0, diff_shape[1]):
                current_cost = 0
                for segment in self.pattern_segments_list:
                    shifted_segment = LineSegment.shifted(
                        segment,
                        numpy.array([xcrd, ycrd]))
                    ind1 = shifted_segment.orientation_channel
                    ind2 = shifted_segment.point[1] + shifted_segment.point[0]
                    ind2 += self.partial_sums_shift
                    array = self.partial_sums[ind1][ind2]

                    segment_cost = array[shifted_segment.right_bound]
                    if shifted_segment.left_bound > 0:
                        segment_cost -= array[shifted_segment.left_bound - 1]

                    current_cost += segment_cost

                if current_cost < cost:
                    cost = current_cost
                    occurrence = numpy.array([xcrd, ycrd])

        return occurrence
