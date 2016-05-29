import cv2
import matcher


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
    for keyp in keypoints:
        p3d = ARTEM_DAVI(obj, ms, keyp[0])
        res.append((keyp[1], p3d))

    return res


def processImage(img, ms, keyframepoints):
    keypoints = detect(img)

    desc1 = [pnt[0] for pnt in keyframepoints]
    desc2 = [pnt[1] for pnt in keypoints]
    matches = matcher.match_features(desc1, desc2, 'surf')

    obj_points = []
    img_points = []
    for mt in matches:
        obj_points.append(keyframepoints[mt[0]][1])
        img_points.append(keypoints[mt[1]][0])

    found, rvec, tvec = cv2.solvePnP(obj_points, img_points, ms, None)
    
