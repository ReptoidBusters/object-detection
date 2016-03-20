# Standard imports
import cv2
import numpy as np;
import sys
 
# Some information could be found here:
# http://www.learnopencv.com/blob-detection-using-opencv-python-c/

im = cv2.imread(sys.argv[1], cv2.IMREAD_GRAYSCALE)
 
# Set up the detector with default parameters.
detectorParams = cv2.SimpleBlobDetector_Params()

# It's probably broken. But it should look for lighter blobs 
# if value is 255 and for darker blobs if value is 0.
detectorParams.filterByColor = False
detectorParams.blobColor = 0;

# Filter by size of area in pixels
detectorParams.filterByArea = True
detectorParams.minArea = 100
detectorParams.maxArea = 1000000

# Circularity = (4*pi*Area)/(perimeter^2)
detectorParams.filterByCircularity = True
detectorParams.minCircularity = 0.3
detectorParams.maxCircularity = 1


# Convexity = Area / (Area of convex hull)
detectorParams.filterByConvexity = False
detectorParams.minConvexity = 0
detectorParams.maxConvexity= 200

# Filter by min inertia to max inertia ratio.
detectorParams.filterByInertia = False
detectorParams.minInertiaRatio = 0.01
detectorParams.maxInertiaRatio = 0.8

detector = cv2.SimpleBlobDetector_create(detectorParams)
 
# Detect blobs.
keypoints = detector.detect(im)
 
# Draw detected blobs as red circles.
# cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS ensures the size of the circle corresponds to the size of blob
im_with_keypoints = cv2.drawKeypoints(im, keypoints, np.array([]), (0,0,255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
 
# Show keypoints
cv2.imshow("Keypoints", im_with_keypoints)
while True:
	keyPress = cv2.waitKey(0)
	if 0xFF & keyPress == 27:
		break