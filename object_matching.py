import numpy as np
import chamfer

def match_object(object3d, frames, image):

    def find_edges(frame):
        # i have no Open CV, so i don't really sure in this line
        height, width, _ = frame.image.shape
        # Please, check that image_size = [width, height]
        image_size = np.array([width, height])
        return object3d.get_border(frame.object_position,
                                   frame.camera_position,
                                   frame.internal_camera_parameters,
                                   image_size)

    edges = dict()

    for label, key_frame in frames:
        edges[label] = find_edges(key_frame)

    return run_matching(edges, image)

def run_matching(edges, image):
    matcher = chamfer.Matcher();
    matcher.set_image(image)
    shape = matcher.set_pattern_via_edge_list(edges[edges.keys()[0]]).shape
    
    occurrence = matcher.find_occurrence()
    cv2.rectangle(image, occurrence, (occurrence[0] + shape[1],
                                      occurrence[1] + shape[0]), (0, 255, 0))
