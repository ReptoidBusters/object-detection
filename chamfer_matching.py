import sys
from segment_decomposition import*

class LinearFunction:
    def __init__(self, coefficient, constant):
        self.coefficient = coefficient
        self.constant = constant
    
    def eval(self, point):
        return self.coefficient * point + self.constant
        
    def is_good_replacement(self, lf1, lf2):
        v1 = (self.constant - lf1.constant) * (lf1.coefficient - lf2.coefficient)
        v2 = (lf2.constant - lf1.constant) * (lf1.coefficient - self.coefficient)
        return v1 <= v2
               
    def is_bad_function(self, next_lf, point):
        v1 = point * (self.coefficient - next_lf.coefficient)
        v2 = next_lf.constant - self.constant
        return v1 > v2


def is_in_shape(shape, point):
    return 0 <= point[1] < shape[0] and 0 <= point[0] < shape[1]


class Matcher:
    def __init__(self):
        self.hysteresis_threshold1 = 100
        self.hysteresis_threshold2 = 200
        self.quantization_channels = 16
        self.img_pixel_residual = 1.0
        self.pattern_pixel_residual = 1.0
    
    def _calculate_ydistance(self):
        shape = self.img_edge_map.shape
        max_distance = 2 * max(shape[0], shape[1])
        
        ydst = numpy.ndarray(shape, numpy.int64)
        ydst.fill(max_distance)
        for segment in self.img_segments_list:
            for point in segment.get_points_list():
                ydst[point[1]][point[0]] = 0
                
        for y in range(1, shape[0]):
            for x in range(0, shape[1]):
                ydst[y][x] = min(ydst[y][x], ydst[y - 1][x] + 1)
                
        for y in range(shape[0] - 2, -1, -1):
            for x in range(0, shape[1]):
                ydst[y][x] = min(ydst[y][x], ydst[y + 1][x] + 1)
                
        for y in range(0, shape[0]):
            for x in range(0, shape[1]):
                ydst[y][x] = (ydst[y][x])**2
                
        return ydst
    
    def _calculate_distances(self):
        shape = self.img_edge_map.shape
        ydst = self._calculate_ydistance()
    
        self.distance = numpy.ndarray(shape, numpy.int64)
        for y in range(0, shape[0]):
            stack = []
            for x in range(0, shape[1]):
                lf = LinearFunction(-2 * x, x**2 + ydst[y][x])
                while len(stack) > 1 and lf.is_good_replacement(stack[-2], stack[-1]):
                    stack.pop()
                    
                stack.append(lf)
            
            index = 0    
            for x in range(0, shape[1]):
                while index + 1 != len(stack) and stack[index].is_bad_function(stack[index + 1], x):
                    index += 1
                
                self.distance[y][x] = x**2 + stack[index].eval(x)
    
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
        print("Calculating distances")
        self._calculate_distances()
        
        print("Calculating partial sums")
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
                                               
    def find_occurrence(self):
        img_shape = self.img_edge_map.shape
        max_distance = numpy.dot(img_shape, img_shape)
        
        pattern_shape = self.pattern_edge_map.shape
        diff_shape = (img_shape[0] - pattern_shape[0],
                      img_shape[1] - pattern_shape[1])
        
        points_amount = 0
        for segment in self.pattern_segments_list:
            points_amount += segment.get_points_amount()
        
        cost = (max_distance + 1) * points_amount
        occurrence = numpy.array([0, 0])
        for y in range(0, diff_shape[0]):
            for x in range(0, diff_shape[1]):
                current_cost = 0
                for segment in self.pattern_segments_list:
                    shifted_segment = LineSegment.shifted(segment,
                                                          numpy.array([x, y]))
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
                    occurrence = numpy.array([x, y])
        
        return occurrence
