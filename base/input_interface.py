import cv2


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

    def readArguments():
        image_address = input("Image address:")
        parameters_address = input("Parameters address:")
        return (image_address, parameters_address)

    def read(self):
        image = cv2.imread(image_address)
        with open(parameters_address).read().split('\n\n\n') as matrices:
            read_matrix = lambda s: numpy.loadtxt(s)
            internal_camera_parameters = read_matrix(matrices[0])
            camera_position = read_matrix(matrices[1])
            camera_orientation = read_matrix(matrices[2])
            object_position = read_matrix(matrices[3])
            object_orientation = read_matrix(matrices[4])
        return KeyFrame(self, image, internal_camera_parameters,
                              camera_position,
                              camera_orientation,
                              object_position,
                              object_orientation)


methods = {"two files": TwoFileLoader}