class Position:
    def __init__(self, translation, orientation):
        self.translation = translation
        self.orientation = orientation

    def combine(self):
        raise NotImplementedError


class KeyFrame:
    def __init__(self, image, camera_position,
                 internal_camera_parameters,
                 object_position):
        self.image = image
        self.camera_position = camera_position
        self.internal_camera_parameters = internal_camera_parameters
        self.object_position = object_position
        self.iterator = []

    def __iter__(self):
        self.iterator = iter([self.camera_position.orientation,
                              self.camera_position.translation,
                              self.internal_camera_parameters,
                              self.object_position.orientation,
                              self.object_position.translation])
        return self

    def __next__(self):
        return next(self.iterator)
