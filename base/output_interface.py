import cv2
import numpy
import sys
import io
import os
import base.frame

class Writer:
    """Abstract Writer"""
    
    def __init__(self):
        pass

    def write():
        raise NotImplementedError


class TwoFileWriter(Writer):
    """Save image and parameters to two distinct files given by their 
    addresses."""
    input_list = ["image address", "parameters address"]

    def __init__(self, key_frame, image_address, parameters_address):
        super().__init__()
        self.key_frame = key_frame
        self.image_address = image_address
        self.parameters_address = parameters_address

    def write(self):
        cv2.imwrite(self.image_address, self.key_frame.image)
        open(self.parameters_address, 'w').close()
        with open(self.parameters_address, 'ab') as fout:
            for field in self.key_frame:
                numpy.savetxt(fout, field, header = '', 
                                           footer = '\n',
                                           comments = '')


class FolderWriter(TwoFileWriter):
    """Save image and parameters to two distinct files in a folder given by 
    folder address."""
    input_list = ["folder address"]
    def __init__(self, key_frame, folder_address):
        folder_name = os.path.basename(folder_address)
        if not os.path.isdir(folder_address):
            print("Making folder {}".format(folder_name), file = sys.stderr)
            os.mkdir(folder_address)
        super().__init__(key_frame, os.path.join(folder_address, \
                                                 folder_name + '.png'), \
                                    os.path.join(folder_address, \
                                                 folder_name))


class BulkFolderWriter(Writer):
    """Given the dictionary of KeyFrames save them using FolderWriter in a 
    folder given by folder address."""
    input_list = ["folder address"]

    def __init__(self, key_frames, folder_address):
        super().__init__()
        self.key_frames_dict = key_frames
        if type(self.key_frames_dict) != dict:
            raise ValueError("""The argument passed as KeyFrame dictionary seems 
                to be something else""")
        self.folder_address = folder_address
        if not os.path.isdir(folder_address):
            folder_name = os.path.basename(folder_address)
            print("Making folder {}".format(folder_name), file = sys.stderr)
            os.mkdir(folder_address)

    def write(self):
        for folder_name, key_frame in self.key_frames_dict.items():
            if type(folder_name) != str:
                raise ValueError("The dict key is not a string")
            if type(key_frame) != base.frame.KeyFrame:
                raise ValueError("The dict value is not a KeyFrame")
            FolderWriter(key_frame, os.path.join(self.folder_address, 
                                                 folder_name)).write()


methods = {"two files": TwoFileWriter,      \
           "folder": FolderWriter,          \
           "bulk folder": BulkFolderWriter, \
           }