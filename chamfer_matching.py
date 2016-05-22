import sys
from segment_decomposition import*

class Matcher:
    def __init__(self):
        self.hysteresis_threshold1 = 100
        self.hysteresis_threshold2 = 200
        self.quantization_channels = 16
        self.img_pixel_residual = 1.0
        self.pattern_pixel_residual = 1.0
    
    def calculate_distances(self):
        shape = self.img_edge_map.shape
        max_distance = numpy.dot(shape, shape)
        
        self.distance = numpy.ndarray(shape, numpy.int64)
        self.distance.fill(max_distance)
        
        print("Calculating distances:", file = sys.stderr)
        cnt = 0
        for segment in self.img_segments_list:
            for point in segment.get_points_list():
                for y in range(0, shape[0]):
                    for x in range(0, shape[1]):
                        diff = point - numpy.array([x, y])
                        dst = numpy.dot(diff, diff)
                        self.distance[y][x] = min(self.distance[y][x], dst)
            cnt += 1
            print(cnt, " of ", len(self.img_segments_list), " segments are processed", file = sys.stderr)
        
        print("Distances are calculated", file = sys.stderr)
        
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
        self.calculate_distances()
                                           
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
                    for point in segment.get_points_list():
                        pos = point + numpy.array([x, y])
                        current_cost += self.distance[pos[1]][pos[0]]
                
                if current_cost < cost:
                    cost = current_cost
                    occurrence = numpy.array([x, y])
                
        return occurrence
