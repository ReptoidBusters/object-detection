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

  
    while True:
        key = cv2.waitKey()
        if 0xFF & key == 27:
            break
