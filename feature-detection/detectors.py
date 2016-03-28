# Standard imports
import cv2
import numpy as np
import sys

def blobDetector(img):
    # Some information could be found here:
    # http://www.learnopencv.com/blob-detection-using-opencv-python-c/

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Set up the detector with default parameters.
    detectorParams = cv2.SimpleBlobDetector_Params()

    # It's probably broken. But it should look for lighter blobs
    # if value is 255 and for darker blobs if value is 0.
    detectorParams.filterByColor = False
    detectorParams.blobColor = 0

    # Filter by size of area in pixels
    detectorParams.filterByArea = False
    detectorParams.minArea = 100
    detectorParams.maxArea = 1000000

    # Circularity = (4*pi*Area)/(perimeter^2)
    detectorParams.filterByCircularity = False
    detectorParams.minCircularity = 0.3
    detectorParams.maxCircularity = 1

    # Convexity = Area / (Area of convex hull)
    detectorParams.filterByConvexity = False
    detectorParams.minConvexity = 0
    detectorParams.maxConvexity = 200

    # Filter by min inertia to max inertia ratio.
    detectorParams.filterByInertia = False
    detectorParams.minInertiaRatio = 0.01
    detectorParams.maxInertiaRatio = 0.8

    detector = cv2.SimpleBlobDetector_create(detectorParams)

    # Detect blobs.
    keypoints = detector.detect(gray)

    # Draw detected blobs as red circles.
    # cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS ensures
    # the size of the circle corresponds to the size of blob
    im_with_keypoints = cv2.drawKeypoints(
                                   img, keypoints, np.array([]),
                                   (255, 255, 255),
                                   cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    return im_with_keypoints

def siftDetector(img):
    sift = cv2.xfeatures2d.SIFT_create()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    vis = img.copy()

    keypoints = sift.detect(gray, None)
    
    for pnt in keypoints:
        clr = (255,255,255)
        cv2.circle(vis, (int(pnt.pt[0]), int(pnt.pt[1])), 5, clr, 1)
    return vis

def surfDetector(img):
    surf = cv2.xfeatures2d.SURF_create(1000)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    vis = img.copy()
  
    keypoints = surf.detect(gray, None)
    
    for pnt in keypoints:
        clr = (255, 255, 255)
        cv2.circle(vis, (int(pnt.pt[0]), int(pnt.pt[1])), 5, clr, 1)

    return vis 

def gfttDetector(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    vis = img.copy()
   
    keypoints = cv2.goodFeaturesToTrack(gray, 1000, 0.01, 20)
    keypoints = np.int0(keypoints)
    
    for pnt in keypoints:
        x,y = pnt.ravel()
        clr = (255,255,255)
        cv2.circle(vis, (x, y), 5, clr, 1)

    return vis

def orbDetector(img):
    orb = cv2.ORB_create()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    vis = img.copy()

    keypoints = orb.detect(gray, None)
    
    for pnt in keypoints:
        clr = (255,255,255)
        cv2.circle(vis, (int(pnt.pt[0]), int(pnt.pt[1])), 5, clr, 1)
    return vis
       
def mserDetector(img):
    mser = cv2.MSER_create()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    vis = img.copy()
  
    regions = mser.detectRegions(gray, None)
    regBorders = []

    for reg in regions:
        sreg = sorted(reg, key=lambda p: (p[1],p[0]))
        regList = [ (p[0],p[1]) for p in sreg ]

        newRegL = []
        newRegR = []
        ll = len(sreg)
        for i in range(ll):
            if i==0 or sreg[i][1] != sreg[i-1][1]:
                newRegL.append(sreg[i])
            elif i==ll-1 or sreg[i][1] != sreg[i+1][1]:
                newRegR.append(sreg[i])
        newRegL.reverse()
        newRegL.extend(newRegR)
        regBorders.append(np.array(newRegL));

    lenr = len(regBorders)
    for i in range(lenr):
        clr = (np.random.randint(255), np.random.randint(255), np.random.randint(255))
        cv2.polylines(vis, np.array(regBorders[i:i+1]), 1, clr)
    return vis

def fastDetector(img):
    fast = cv2.FastFeatureDetector_create()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    vis = img.copy()

    keypoints = fast.detect(gray, 1000)
    
    for pnt in keypoints:
        clr = (255,255,255)
        cv2.circle(vis, (int(pnt.pt[0]), int(pnt.pt[1])), 5, clr, 1)
    return vis    

def akazeDetector(img):
    akaze = cv2.AKAZE_create()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    vis = img.copy()

    keypoints = akaze.detect(gray)
    
    for pnt in keypoints:
        clr = (255,255,255)
        cv2.circle(vis, (int(pnt.pt[0]), int(pnt.pt[1])), 5, clr, 1)
    return vis    

def starDetector(img):
    star = cv2.xfeatures2d.StarDetector_create()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    vis = img.copy()
  
    keypoints = star.detect(gray, None)
    
    for pnt in keypoints:
        clr = (255, 255, 255)
        cv2.circle(vis, (int(pnt.pt[0]), int(pnt.pt[1])), 5, clr, 1)

    return vis     