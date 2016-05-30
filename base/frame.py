class Position:
    def __init__(self, translation, orientation):
        self.translation = translation
        self.orientation = orientation


class KeyFrame:
    def __init__(self, image, camera_position,
                 internal_camera_parameters,
                 object_position):
        self.image = image
        self.camera_position = camera_position
        self.internal_camera_parameters = internal_camera_parameters
        self.object_position = object_position
