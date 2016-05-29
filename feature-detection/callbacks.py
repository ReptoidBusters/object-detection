import cv2
import matcher
import base.frame as frame


def detect(img):
    '''
    Returns list of tuples (point, descriptor).
    '''
    surf = cv2.xfeatures2d.SURF_create(1000)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    keypoints, descriptors = surf.detectAndCompute(gray, None)

    respoints = []

    for i in range(len(keypoints)):
        respoints.append((keypoints[i].pt, descriptors[i]))

    return keypoints


def processKeyFrame(img, ms, obj):
    '''
    Returns list of tuples (descriptor, 3d point)
    '''
    keypoints = detect(img)
    res = []
    img_size = (len(img), len(img[0]))
    for keyp in keypoints:
        p3d = obj.get_original(ms[0], ms[1], ms[2], img_size[0], img_size[1],
                               (keyp[0][0], img_size[1] - keyp[0][1]))
        res.append((keyp[1], p3d))

    return res


def GLtoCV3d(point):
    return (point[0], -point[1], -point[2])


def GLtoCV2d(point, img_size):
    return (point[0], img_size[0] - point[1])


def processImage(keyframes, obj, img):
    keyframe = next(iter(dict.values))
    keyframepoints = processKeyFrame(keyframe.image, (keyframe.camera_position,
                                     keyframe.internal_camera_parametrs,
                                     keyframe.object_position), obj)
    keypoints = detect(img)

    desc1 = [pnt[0] for pnt in keyframepoints]
    desc2 = [pnt[1] for pnt in keypoints]
    matches = matcher.match_features(desc1, desc2, 'surf')

    obj_points = []
    img_points = []
    img_size = (len(img), len(img[0]))
    for mt in matches:
        obj_points.append(GLtoCV3d(keyframepoints[mt[0]][1]))
        img_points.append(GLtoCV2d(keypoints[mt[1]][0], img_size))

    ms = [[0] * 3] * 3
    for i in range(3):
        for j in range(3):
            ms[i][j] = keyframe.internal_camera_parametrs[i][j]

    found, rvec, tvec = cv2.solvePnP(obj_points, img_points, ms, None)

    object_position = frame.Position(tvec, rvec)

    return frame.KeyFrame(img, keyframe.camera_position,
                          keyframe.internal_camera_parametrs,
                          object_position)
