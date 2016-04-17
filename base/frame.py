class KeyFrame:
    def __init__(self, image, camera_orientation,
                 camera_position,
                 internal_camera_parameters,
                 object_orientation,
                 object_position):
        self.image = image
        self.camera_orientation = camera_orientation
        self.camera_position = camera_position
        self.internal_camera_parameters = internal_camera_parameters
        self.object_orientation = object_orientation
        self.object_position = object_position
        self.iterator = []

    def __iter__(self):
        self.iterator = (value for key, value in sorted(self.__dict__.items())
                         if key != 'image' and not key.startswith('__'))
        return self

    def __next__(self):
        return next(self.iterator)
