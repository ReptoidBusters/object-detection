import numpy as np
import cv2


norm = cv2.NORM_L2


def init_feature(name):
    if name == 'sift':
        detector = cv2.xfeatures2d.SIFT_create()
        norm = cv2.NORM_L2
    elif name == 'surf':
        detector = cv2.xfeatures2d.SURF_create(800)
        norm = cv2.NORM_L2
    elif name == 'orb':
        detector = cv2.ORB_create(400)
        norm = cv2.NORM_HAMMING
    elif name == 'akaze':
        detector = cv2.AKAZE_create()
        norm = cv2.NORM_HAMMING
    elif name == 'brisk':
        detector = cv2.BRISK_create()
        norm = cv2.NORM_HAMMING
    else:
        return None, None

    matcher = cv2.BFMatcher(norm)
    return detector, matcher


def filter_matches(ps1, ps2, multimatches, thresh=100):
    res_matches = []
    for matches in multimatches:
        cur_res = []
        for m in matches:
            if euclid_dist(ps1[m.queryIdx], ps2[m.trainIdx]) < thresh:
                cur_res.append((m.queryIdx, m.trainIdx))
        res_matches.append(cur_res)
    return res_matches


def sqr(a):
    return a * a


def euclid_dist(p1, p2):
    return np.sqrt(sqr(p1[0] - p2[0]) + sqr(p1[1] - p2[1]) +
                   sqr(p1[2] - p2[2]))


def descriptor_dist(desc1, desc2):
    diff = [d1 - d2 for d1, d2 in zip(desc1, desc2)]
    return cv2.norm(diff, norm)


def build_matching(desc1, desc2, multimatches):
    res = []
    for matches in multimatches:
        res.append(matches[0])
    return res


def match_3d_features(kp1, kp2, feature_name):
    '''
    kp1, kp2 - (desc, kp, 3d)
    '''
    detector, matcher = init_feature(feature_name)

    desc1 = [kp[0] for kp in kp1]  # kp[0] is actually a descriptor
    desc2 = [kp[0] for kp in kp2]  # same here
    # PLAY WITH VALUE OF K MAYBE
    raw_matches = matcher.knnMatch(desc1, trainDescriptors=desc2, k=10)

    # filter out matches by 3d distance
    ps1 = [kp[2] for kp in kp1]  # 3d points
    ps2 = [kp[2] for kp in kp2]
    matches = filter_matches(ps1, ps2, raw_matches)

    # build stable matching
    matches = build_matching(desc1, desc2, matches)

    return matches
