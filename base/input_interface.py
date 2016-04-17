import io
import sys
import os
import cv2
import numpy
import base.frame as frame


class Loader:
    """Abstract Loader"""

    def __init__(self):
        pass

    def load(self):
        raise NotImplementedError


class TwoFileLoader(Loader):
    """Read image and parameters from two distinct files given by their
    addresses."""
    input_list = ["keyframe id", "image address", "parameters address"]

    def __init__(self, keyframe_id, image_address, parameters_address):
        super().__init__()
        self.keyframe_id = keyframe_id
        self.image_address = image_address
        self.parameters_address = parameters_address

    def load(self):
        if not os.path.isfile(self.image_address):
            print(self.image_address, file=sys.stderr)
            raise LookupError("""No image file found at the given address or
                              reading is not permitted""")
        if not os.path.isfile(self.parameters_address):
            print(self.parameters_address, file=sys.stderr)
            raise LookupError("""No parameters file found at the given address
                              or reading is not permitted""")
        image = cv2.imread(self.image_address)
        with open(self.parameters_address) as fin:
            matrices = fin.read().split('\n\n')

            def read_matrix(string):
                return numpy.loadtxt(io.StringIO(string))
            camera_orientation = read_matrix(matrices[0])
            camera_position = read_matrix(matrices[1])
            internal_camera_parameters = read_matrix(matrices[2])
            object_orientation = read_matrix(matrices[3])
            object_position = read_matrix(matrices[4])
        return {self.keyframe_id: frame.KeyFrame(image,
                                                 camera_orientation,
                                                 camera_position,
                                                 internal_camera_parameters,
                                                 object_orientation,
                                                 object_position)}


class FolderLoader(TwoFileLoader):
    r"""Read image and parameters from two distinct files given the folder
    containing them. The directory tree should be like:
    path/folder_name
        folder_name                                         # parameter file
        folder_name.{OpenCV imread()-able extension}        # image file
    The folder should NOT contain any other files."""
    input_list = ["folder address"]

    def __init__(self, folder_address):
        folder_name = os.path.basename(folder_address)
        if not os.path.isdir(folder_address):
            raise LookupError("""The address is invalid or reading is not
                              permitted""")
        params, image, *trash = list(os.walk(folder_address))[0][2] + [''] * 2
        del trash
        if params != os.path.basename(folder_name):
            params, image = image, params
        super().__init__(folder_name, os.path.join(folder_address, image),
                         os.path.join(folder_address, params))


class BulkFolderLoader(Loader):
    r"""Read all files from the given top folder. The directory tree should be
    like:
    path/top_folder
        folder1
        folder2
        ...
    Then folder1, folder2... would be read using FolderLoader and returned as
    a dictionary {"folder1": KeyFrame(), ...}"""
    input_list = ["top folder address"]

    def __init__(self, folder_address):
        self.folder_address = folder_address
        if not os.path.isdir(folder_address):
            raise LookupError("""The address is invalid or reading is not
                permitted""")
        super().__init__()

    def load(self):
        result = {}
        for folder in list(os.walk(self.folder_address))[0][1]:
            loader = FolderLoader(os.path.join(self.folder_address, folder))
            result.update(loader.load())
        return result


METHODS = {
    "two files": TwoFileLoader,
    "folder": FolderLoader,
    "bulk folder": BulkFolderLoader,
}
