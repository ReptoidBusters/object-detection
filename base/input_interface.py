import cv2
import numpy
import io
import os
import base.frame

class Loader:
    """Abstract Loader"""

    def __init__(self):
        pass

    def readArguments():
        raise NotImplementedError

    def read():
        raise NotImplementedError


class TwoFileLoader(Loader):
    """Read image and parameters from two distinct files given by their 
    addresses."""

    def __init__(self, image_address, parameters_address):
        super().__init__()
        self.image_address = image_address
        self.parameters_address = parameters_address

    def read(self):
        if not os.path.isfile(image_address):
            raise LookupError("""No image file found at the given address or 
                reading is not permitted""")
        if not os.path.isfile(parameters_address):
            raise LookupError("""No parameters file found at the given address 
                or reading is not permitted""")
        image = cv2.imread(self.image_address)
        with open(self.parameters_address) as fin:
            matrices = fin.read().split('\n\n')
            read_matrix = lambda s: numpy.loadtxt(io.StringIO(s))
            internal_camera_parameters = read_matrix(matrices[0])
            camera_position = read_matrix(matrices[1])
            camera_orientation = read_matrix(matrices[2])
            object_position = read_matrix(matrices[3])
            object_orientation = read_matrix(matrices[4])
        return base.frame.KeyFrame(image, internal_camera_parameters,
                                   camera_position,
                                   camera_orientation,
                                   object_position,
                                   object_orientation)


class FolderLoader(TwoFileLoader):
    """Read image and parameters from two distinct files given the folder 
    containing them. The directory tree should be like:
    path/folder_name
        folder_name                                         # parameter file
        folder_name.\{OpenCV imread()-able extension\}      # image file
    The folder should NOT contain any other files."""

    def __init__(self, folder_address):
        folder_name = os.path.dirname(folder_address)
        if not os.path.isdir(folder_address):
            raise LookupError("""The address is invalid or reading is not 
                permitted""")
        parameters, image, *trash = os.path.walk(folder_address)[2] + [''] * 2
        if parameters != os.path.dirname(folder_name):
            parameters, image = image, parameters
        super().__init__(image, parameters)


class BulkFolderLoader(Loader):
    """Read all files from the given top folder. The directory tree should be 
    like:
    path/top_folder
        folder1
        folder2
        ...
    Then folder1, folder2... would be read using FolderLoader and returned as
    a dictionary \{"folder1": KeyFrame(), ...\}"""

    def __init__(self, folder_address):
        self.folder_address = folder_address
        if not os.path.isdir(folder_address):
            raise LookupError("""The address is invalid or reading is not 
                permitted""")
        super().__init__()

    def read(self):
        return [FolderLoader(folder).read() for folder in \
            os.path.walk(self.folder_address)[1]]
        

methods = {"two files": TwoFileLoader,      \
           "folder": FolderLoader,          \
           "bulk folder":BulkFolderLoader,  \
           }