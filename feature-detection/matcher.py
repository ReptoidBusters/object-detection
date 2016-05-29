import numpy as np
import cv2


norm = cv2.NORM_L2


def init_feature(name):
    if name == 'sift':
        norm = cv2.NORM_L2
    elif name == 'surf':
        norm = cv2.NORM_L2
    elif name == 'orb':
        norm = cv2.NORM_HAMMING
    elif name == 'akaze':
        norm = cv2.NORM_HAMMING
    elif name == 'brisk':
        norm = cv2.NORM_HAMMING
    else:
        return None, None

    matcher = cv2.BFMatcher(norm)
    return matcher


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
    n = len(desc1)
    distances = [[] for i in range(n)]

    for matches in multimatches:
        for m in matches:
            distances[m[0]].append((descriptor_dist(desc1[m[0]], desc2[m[1]])))
    for i in range(n):
        distances[i] = sorted(distances[i])

    matching = [-1 for i in range(len(desc2))]

    # Here it comes
    for i in range(n):
        cur_guy = i
        while len(distances[cur_guy]) > 0:
            cmatch = distances[cur_guy].pop()
            if matching[cmatch[1]] == -1:
                matching[cmatch[1]] = cur_guy
                break
            else:
                if (descriptor_dist(desc1[matching[cmatch[1]]],
                                    desc2[cmatch[1]]) >
                        descriptor_dist(desc1[cur_guy], desc2[cmatch[1]])):
                    cur_guy, matching[cmatch[1]] = matching[cmatch[1]], cur_guy
    res = []
    for i in range(len(desc2)):
        if matching[i] != -1:
            res.append(matching[i], i)
    return res


def match_features(desc1, desc2, feature_name):
    '''
    feature_name \in {'surf', 'sift', 'orb', 'akaze', 'brisk'}
    '''
    detector, matcher = init_feature(feature_name)

    # PLAY WITH VALUE OF K MAYBE
    raw_matches = matcher.knnMatch(desc1, trainDescriptors=desc2, k=10)

    # build stable matching
    matches = build_matching(desc1, desc2, raw_matches)

    return matches
