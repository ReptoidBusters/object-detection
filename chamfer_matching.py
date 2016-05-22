from segment_decomposition import*

class Matcher:
    def __init__(self):
        self.hysteresis_threshold1 = 100;
        self.hysteresis_threshold2 = 200;
        self.quantization_channels = 16
        
    def set_image(self, img):
        self.img_edge_map = get_edge_map(img,
                                         self.hysteresis_threshold1,
                                         self.hysteresis_threshold2)
        
        self.img_orientation_map = get_orientation_map(img)
        self.img_orientation_map = quantized(self.img_orientation_map,
                                             self.quantization_channels)
