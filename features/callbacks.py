import cv2
from . import matcher
import base.frame as frame
import numpy as np
import random

img_num = 0


def detect(img, nfeatures=500):
    '''
    Returns list of tuples (point, descriptor).
    '''
    sift = cv2.xfeatures2d.SIFT_create(nfeatures)
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    keypoints, descriptors = sift.detectAndCompute(gray, None)

    vis = img.copy()
    for pnt in keypoints:
        clr = (0, 0, 255)
        cv2.circle(vis, (int(pnt.pt[0]), int(pnt.pt[1])), 5, clr, 1)
    print(vis.shape)
    global img_num
    #cv2.imshow("jack", vis)
    img_num = img_num + 1

    respoints = []

    for i in range(len(keypoints)):
        respoints.append((keypoints[i].pt, descriptors[i]))

    return respoints


def processKeyFrame(img, ms, obj):
    '''
    Returns list of tuples (descriptor, 3d point)
    '''
    print("Keyframe image shape: ", img.shape)
    keypoints = detect(img, 500)
    res = []
    img_size = (len(img), len(img[0]))
    print("Keyframe points number: ", len(keypoints))
    keypointss = [(1036, 450),
                  (813, 679),
                  (1087, 727),
                  (994, 843),
                  (832, 406),  # last inlier
                  (100, 100),
                  (1750, 990),
                  (1066, 397)]

    '''
    for keyp in keypoints:
        p3d = obj.get_original(ms[0], ms[1], ms[2], np.array([img_size[1],
                                                              img_size[0]]),
                               np.array([keyp[0][0],
                                         img_size[0] - keyp[0][1]]))
        if p3d is None:
            continue
        res.append((keypoints[0][1], p3d))
    '''

    for keyp in keypointss:
        p3d = obj.get_original(ms[0], ms[1], ms[2], np.array([img_size[1],
                                                              img_size[0]]),
                               np.array([keyp[0],
                                         img_size[0] - keyp[1]]))
        if p3d is None:
            # continue
            print(False)
            continue
        print(True)
        res.append((keypoints[0][1], p3d))

    return res


def GLtoCV3d(point):
    return (point[0], -point[1], -point[2])


def GLtoCV2d(point, img_size):
    return (point[0], img_size[0] - point[1])


def processImage(keyframes, imgAddr, obj):
    imgAddr = imgAddr[0]
    print(imgAddr)
    keyframe = next(iter(keyframes.values()))
    img = cv2.imread(imgAddr)
    
    print("Grinding.")
    keyframepoints = processKeyFrame(keyframe.image, (keyframe.object_position,
                                     keyframe.camera_position,
                                     keyframe.internal_camera_parameters), obj)
    '''
    keypoints = detect(img)

    desc1 = [pnt[0] for pnt in keyframepoints]
    desc2 = [pnt[1] for pnt in keypoints]

    print("Keyframe points length in processImage: ", len(keyframepoints))

    matches = matcher.match_features(desc1, desc2, 'surf')

    obj_points = []
    img_points = []
    img_size = (len(img), len(img[0]))
    sz_key = len(keyframepoints)
    sz_img = len(keypoints)
    for mt in matches:
        print(sz_key, mt[0], sz_img, mt[1])

        clr = (0, 0, 255)
        pt = keypoints[mt[1]][0]
        cv2.circle(img, (int(pt[0]), int(pt[1])), 5, clr, 1)

        obj_points.append(GLtoCV3d(keyframepoints[mt[0]][1]))
        img_points.append(GLtoCV2d(keypoints[mt[1]][0], img_size))

    # BE CAREFUL HERE WITH NUMPY ARRAYS
    ms = [[0] * 3] * 3
    for i in range(3):
        for j in range(3):
            ms[i][j] = keyframe.internal_camera_parameters[i][j]
        ms[i] = np.array(ms[i])
    ms = np.array(ms)

    found, rvec, tvec = cv2.solvePnP(np.array(obj_points),
                                     np.array(img_points), ms, None)

    object_position = frame.Position(tvec, rvec)
    '''

    return frame.KeyFrame(img, keyframe.camera_position,
                          keyframe.internal_camera_parameters,
                          keyframe.object_position)
