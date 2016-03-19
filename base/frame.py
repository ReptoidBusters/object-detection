class KeyFrame:
    def __init__(self, image, internal_camera_parameters,
                              camera_position,
                              camera_orientation,
                              object_position,
                              object_orientation):
        self.image = image
        self.internal_camera_parameters = internal_camera_parameters
        self.camera_position = camera_position
        self.camera_orientation = camera_orientation
        self.object_position = object_position
        self.object_orientation = object_orientation

    def __iter__(self):
        return list(x[1] for x in sorted(self.__dict__.items()) 
                if not x[0].startswith('__'))

    def __next__(self):
        for field in (x[1] for x in sorted(self.__dict__.items()) 
                if not x[0].startswith('__')):
            yield field
        raise StopIteration
