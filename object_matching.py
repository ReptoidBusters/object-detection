import numpy as np


def match_object(object3d, frames, image):

    def find_edges(frame):
        # i have no Open CV, so i don't really sure in this line
        height, width, trash = frame.image.shape
        # Please, check that image_size = [width, height]
        image_size = np.array([width, height])
        return object3d.get_border(frame.object_position,
                                   frame.camera_position,
                                   frame.internal_camera_parameters,
                                   image_size)

    edges = dict()

    for label, key_frame in frames:
        edges[label] = find_edges(key_frame)

    return do_something(frames, edges, image)


def do_something(frames, edges, image):
    """
    frames - dict: labels->frame
    edges - dict: labels->edges for frame with equal label
    """
    pass




