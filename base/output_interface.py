import cv2
import numpy
import sys
import io
import os
import base.frame

class Writer:
    """Abstract Write"""
    
    def __init__(self, key_frame):
        self.key_frame = key_frame

    def save():
        raise NotImplementedError


class TwoFileWriter(Writer):
    """Save image and parameters to two distinct files given by their 
    addresses."""
    self.input_list = ["image_address", "parameters_address"]

    def __init__(self, key_frame, image_address, parameters_address):
        super().__init__(key_frame)
        self.image_address = image_address
        self.parameters_address = parameters_address

    def save(self):
        cv2.imwrite(self.image_address, self.key_frame.image)
        with open(self.parameters_address, 'w') as fout:
            for field in self.key_frame:
                print(*"\"" + str(field) + "\"", sep = '')
            for field in self.key_frame:
                numpy.savetxt(fout, field, footer = '\n')


class FolderWriter(TwoFileWriter):
    """Save image and parameters to two distinct files in a folder given by 
    folder address."""
    self.input_list = ["folder_address"]

    def __init__(self, key_frame, folder_address):
        folder_name = os.path.dirname(folder_address)
        if not os.path.isdir(folder_address):
            print("Making folder {}".format(folder_name), file = sys.stderr)
            os.mkdir(folder_address)
        super().__init__(key_frame, os.path.join(folder_address, \
                                                 folder_name + '.png'), \
                                    os.path.join(folder_address, \
                                                 folder_name))


methods = {"two files": TwoFileWriter, "folder": FolderWriter}