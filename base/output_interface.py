import cv2


class Writer:
    """Abstract Write"""
    
    def __init__(self, key_frame):
        self.key_frame = key_frame

    def readArguments():
        raise NotImplementedError

    def save():
        raise NotImplementedError


class TwoFileWriter(Writer):
    """Save image and parameters from two distinct files given by their 
    addresses."""

    def readArguments():
        image_address = input("Image address:")
        parameters_address = input("Parameters address:")
        return (image_address, parameters_address)

    def save(image_address, parameters_address):
        cv2.imwrite(image_address, self.key_frame.image)
        with open(parameters_address, 'w') as fout:
            for field in self.key_frame:
                numpy.savetxt(fout, parameters_address, footer = '\n')


methods = {"two files": TwoFileWriter}