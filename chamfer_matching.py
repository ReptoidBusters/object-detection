from segment_decomposition import*

class Matcher:
    def __init__(self):
        self.hysteresis_threshold1 = 100
        self.hysteresis_threshold2 = 200
        self.quantization_channels = 16
        self.img_pixel_residual = 1.0
        self.pattern_pixel_residual = 1.0
        
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
