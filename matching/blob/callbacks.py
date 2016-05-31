import cv2
from matching.blob.matcher import match_features
import base.frame as frame
import numpy as np
import random
import math
from base.geometry3d import transformation_matrix


def gen_rand_sample(n, count):
    used = [0] * n
    res = []
    while count > 0:
        cand = random.randint(0, n - 1)
        if used[cand] == 1:
            continue
        used[cand] = 1
        res.append(cand)
        count -= 1
    return res


def euclidDist(point):
    return math.sqrt(point[0] * point[0] + point[1] * point[1])


def GLtoCV3d(point):
    return (point[0], point[1], -point[2])


def CVtoGL3d(point):
    return (point[0], point[1], -point[2])


def GLtoCV2d(point, img_size):
    return (point[0], img_size[1] - point[1])


def myRansac(obj_points, img_points, projection, view,
             img_size, projectionError=10, iterations=500):
    ms = projection[:3, :3]
    p_cnt = len(obj_points)
    homo_obj_points = []
    stretched_img_points = []
    for i in range(p_cnt):
        stretched_img_points.append((img_points[i] + 1) * img_size / 2)
        homo_obj_points.append(np.array([obj_points[i][0], obj_points[i][1],
                                         -obj_points[i][2], 1]))

    tvec_ans = np.array([0, 0, 0])
    rvec_ans = np.array([0, 0, 0])
    found = False
    best_inliers = 0
    for iteration_number in range(iterations):
        rand_sample = gen_rand_sample(p_cnt, 5)
        sample_obj = np.array([obj_points[i] for i in rand_sample])
        sample_img = np.array([img_points[i] for i in rand_sample])
        found, rvec, tvec = cv2.solvePnP(sample_obj, sample_img, ms,
                                         None)
        tvec = [float(i) for i in tvec]
        view_transformation = transformation_matrix(view.translation,
                                                    view.orientation)
        transformation = projection.dot(view_transformation).\
            dot(transformation_matrix(tvec, rvec))

        # Projecting points into plane
        proj_obj_points = [transformation.dot(homo_obj_points[i]).A1
                           for i in range(p_cnt)]

        # Transformin coordinates to be image coordinates
        for i in range(p_cnt):
            proj_obj_points[i] = np.array(proj_obj_points[i][:2] /
                                          proj_obj_points[i][3])
            proj_obj_points[i] = (proj_obj_points[i] + 1) * img_size / 2

        inliers = 0
        for i in range(p_cnt):
            if euclidDist(proj_obj_points[i] - stretched_img_points[i]) <\
                    projectionError:
                inliers += 1
        if inliers > best_inliers:
            tvec_ans = tvec
            rvec_ans = rvec
            best_inliers = inliers
    return best_inliers, rvec_ans, tvec_ans


def detect(img, nfeatures=500):
    '''
    Returns list of tuples (point3d, descriptor).
    '''
    sift = cv2.xfeatures2d.SIFT_create(nfeatures)
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    keypoints, descriptors = sift.detectAndCompute(gray, None)

    vis = img.copy()
    for pnt in keypoints:
        clr = (0, 0, 255)
        cv2.circle(vis, (int(pnt.pt[0]), int(pnt.pt[1])), 5, clr, 1)

    respoints = []

    for i in range(len(keypoints)):
        respoints.append((keypoints[i].pt, descriptors[i]))

    return respoints


def processKeyFrame(img, ms, obj):
    '''
    Returns list of tuples (descriptor, 3d point, 2d point)
    '''
    keypoints = detect(img, 100)
    res = []
    img_size = (len(img), len(img[0]))

    for i in range(len(ms[0].orientation)):
        ms[0].orientation[i] = ms[0].orientation[i] * 2 * math.pi / 360
    for keyp in keypoints:
        p3d = obj.get_original(ms[0], ms[1], ms[2], np.array([img_size[1],
                                                              img_size[0]]),
                               np.array([keyp[0][0],
                                         img_size[0] - keyp[0][1]]))

        if p3d is None:
            continue
        res.append((keyp[1], p3d, keyp[0]))

    return res


def blob_matching(keyframes, imgAddr, obj):
    imgAddr = imgAddr[0]
    print(imgAddr)
    keyframe = next(iter(keyframes.values()))
    initial_camera_parameters = (keyframe.camera_position,
                                 keyframe.internal_camera_parameters,
                                 keyframe.object_position)
    initial_position = frame.Position(
        keyframe.object_position.translation.copy(),
        keyframe.object_position.orientation.copy())
    img = cv2.imread(imgAddr)

    keyframepoints = processKeyFrame(keyframe.image, (keyframe.object_position,
                                     keyframe.camera_position,
                                     keyframe.internal_camera_parameters), obj)

    keypoints = detect(img)

    desc1 = [pnt[0] for pnt in keyframepoints]
    desc2 = [pnt[1] for pnt in keypoints]

    print("Keyframe points length in processImage: ", len(keyframepoints))

    matches = match_features(desc1, desc2, 'surf')

    obj_points = []
    img_points = []
    img_size = np.array([len(img[0]), len(img)])

    print("Number of matches: ", len(matches))
    for mt in matches:
        obj_points.append(GLtoCV3d(keyframepoints[mt[0]][1]))
        img_points.append(GLtoCV2d(keypoints[mt[1]][0], img_size))

    ms = keyframe.internal_camera_parameters

    qqq = len(img_points)

    for i in range(qqq):
        img_points[i] = np.array([img_points[i][0], img_points[i][1]])
        img_points[i] = 2 * img_points[i] / img_size - 1

    inliers, rvec, tvec = myRansac(np.array(obj_points),
                                   np.array(img_points), ms,
                                   keyframe.camera_position, img_size)

    print("Best inliers: ", inliers)

    for i in range(len(rvec)):
        rvec[i] = rvec[i] * 360 / (2 * math.pi)

    tvec = CVtoGL3d(tvec)
    tvec = np.array([float(tvec[0]), float(tvec[1]), float(tvec[2])])
    rvec = np.array([float(rvec[0]), float(rvec[1]), float(rvec[2])])

    object_position = frame.Position(tvec + initial_position.translation,
                                     rvec + initial_position.orientation)

    print("Final translation: ", object_position.translation)
    print("Final rotation: ", object_position.orientation)

    keyframe.camera_position = initial_camera_parameters[0]
    keyframe.internal_camera_parameters = initial_camera_parameters[1]
    keyframe.object_position = initial_camera_parameters[2]

    return frame.KeyFrame(img, initial_camera_parameters[0],
                          initial_camera_parameters[1],
                          object_position)
