import io
import os
import cv2
import numpy
import base.frame as frame
from base.loading import load_object


SUPPORTED_IMAGE_FORMATS = ['bmp', 'dib', 'jpeg', 'jpg',
                           'jpe', 'jp2', 'png', 'pbm',
                           'pgm', 'ppm', 'sr', 'ras',
                           'tiff', 'tif']


class InvalidAddressError(Exception):
    def __init__(self, string):
        super().__init__()
        self.string = string

    def __repr__(self):
        format_string = "{}\nAddress is invalid or reading was not permitted"
        return format_string.format(self.string)


def load_keyframe(address):
    r"""Read keyframe from a folder. The directory tree should be like:
    path/folder_name
        parameters                                          # parameter file
        image.{OpenCV imread()-able extension}              # image file
    """

    if not os.path.isdir(address):
        raise InvalidAddressError(address)
    label = os.path.basename(address)
    params = os.path.join(address, "params")
    if not os.path.isfile(params):
        raise InvalidAddressError(params)
    image = os.path.join(address, "image.")

    for fmt in SUPPORTED_IMAGE_FORMATS:
        if os.path.isfile(image + fmt):
            image += fmt
            break
    else:
        raise InvalidAddressError("No image")

    image = cv2.imread(image)

    with open(params) as fin:
        matrices = fin.read().split('\n\n')

        def read_matrix(string):
            return numpy.loadtxt(io.StringIO(string))

        camera_orientation = read_matrix(matrices[0])
        camera_translation = read_matrix(matrices[1])
        camera_position = frame.Position(camera_translation,
                                         camera_orientation)
        internal_camera_parameters = read_matrix(matrices[2])
        object_orientation = read_matrix(matrices[3])
        object_translation = read_matrix(matrices[4])
        object_position = frame.Position(object_translation,
                                         object_orientation)
    return {label: frame.KeyFrame(image,
                                  camera_position,
                                  internal_camera_parameters,
                                  object_position)}


def load_work_dir(address):
    r"""Read all keyframes and object file from the given top folder. The
    directory tree should be like:
    path/top_folder
        mesh.obj
        keyframes
            folder1
            folder2
            ...
    Then folder1, folder2... would be read using load_keyframe and returned as
    a dictionary {"folder1": KeyFrame(), ...}"""

    if not os.path.isdir(address):
        raise InvalidAddressError(address)

    object_address = os.path.join(address, "mesh.obj")
    if not os.path.isfile(object_address):
        raise InvalidAddressError(object_address)
    obj = load_object(object_address)

    keyframes = os.path.join(address, "keyframes")
    if not os.path.isdir(keyframes):
        raise InvalidAddressError(keyframes)
    data = {}
    for folder in list(os.walk(keyframes))[0][1]:
        data.update(load_keyframe(os.path.join(keyframes, folder)))
    return (obj, data)
