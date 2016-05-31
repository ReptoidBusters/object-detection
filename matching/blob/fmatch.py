import numpy as np
import cv2


'''

Usage:

'''

if __name__ == '__main__':
    import sys

    img1 = cv2.imread(sys.argv[1])  # queryImage
    img2 = cv2.imread(sys.argv[2])  # trainImage

    gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

    sift = cv2.xfeatures2d.SIFT_create()

    # find the keypoints and descriptors with SIFT
    kp1, des1 = sift.detectAndCompute(gray1, None)
    kp2, des2 = sift.detectAndCompute(gray2, None)

    # create BFMatcher object
    bf = cv2.BFMatcher()

    # Match descriptors.
    matches = bf.match(des1, des2)

    # Sort them in the order of their distance.
    matches = sorted(matches, key=lambda x: x.distance)

    # Draw first sys.argv[3] matches.
    # img3 = cv2.drawMatches(img1,kp1,img2,kp2,matches[:int(sys.argv[3])],
    #    None, flags=2)
    h1, w1 = img1.shape[:2]
    h2, w2 = img2.shape[:2]
    nWidth = w1 + w2
    nHeight = max(h1, h2)
    hdif = (h1-h2) / 2
    newimg = np.zeros((nHeight, nWidth, 3), np.uint8)
    newimg[:h1, :w1] = img1
    newimg[:h2, w1:w1+w2] = img2

    for i in range(100):
        pt_a = (int(kp1[matches[i].queryIdx].pt[0]), int(kp1[matches[i].queryIdx].pt[1]))
        pt_b = (int(kp2[matches[i].trainIdx].pt[0] + w2), int(kp2[matches[i].trainIdx].pt[1]))
        clr = (255, 255, 255)
        cv2.circle(newimg, (int(pt_a[0]), int(pt_a[1])), 5, clr, 1)        
        clr = (0, 255, 0)
        cv2.circle(newimg, (int(pt_b[0]), int(pt_b[1])), 5, clr, 1)        
        cv2.line(newimg, pt_a, pt_b, (255, 0, 0))

    cv2.namedWindow(sys.argv[1], cv2.WINDOW_NORMAL)
    cv2.imshow(sys.argv[1], newimg)

    '''
    flann.add(sd)
    flann.train()
    idx, dist = cv2.knnMatchImpl(sd, flann_params)
    '''

    #idx, dist = flann.match(sd, td)

    '''
    idx, dist = flann.knnMatch(td, 1)

    dist = dist[:,0]/2500.0
    dist = dist.reshape(-1,).tolist()
    idx = idx.reshape(-1).tolist()
    indices = range(len(dist))
    indices.sort(key=lambda i: dist[i])
    dist = [dist[i] for i in indices]
    idx = [idx[i] for i in indices]

    skp_final = []
    for i, dis in itertools.izip(idx, dist):
        if dis < distance:
            skp_final.append(skp[i])
        else:
            break
    tkp_final = []
    for i, dis in itertools.izip(idx, dist):
        if dis < distance:
            tkp_final.append(tkp[i])
        else:
            break
    '''
    '''
    h1, w1 = img.shape[:2]
    h2, w2 = template.shape[:2]
    nWidth = w1 + w2
    nHeight = max(h1, h2)
    hdif = (h1-h2) / 2
    newimg = np.zeros((nHeight, nWidth, 3), np.uint8)
    newimg[hdif:hdif + h2,  :w2] = template
    newimg[:h1, w2:w1+w2] = img

#    tkp = tkp_final
    #skp = skp_final
    for i in range(min(len(sd), len(matches))):
        pt_a = (int(sd[i][0]), int(sd[i][1]+hdif))
        pt_b = (int(matches[i]+w2), int(matches[i][1]))
        cv2.line(newimg, pt_a, pt_b, (255, 0, 0))

#    for pnt in keypoints:
#        clr = (255,255,255)
#        cv2.circle(vis, (int(pnt.pt[0]), int(pnt.pt[1])), 5, clr, 1)


    cv2.imshow(sys.argv[1], newimg)

    #cv2.createButton(None, kek)
    '''
    while True:
        kek = cv2.waitKey()
        if 0xFF & kek == 27:
            break
