# import numpy as np
import cv2
import detectors
import subprocess
import re


'''

Feature detectors tester

Usage:

python3 tester.py ALL|STAR|AKAZE|FAST|ORB|MSER|SURF|SIFT|BLOB|GFTT
        input_image.jpg

'''

if __name__ == '__main__':
    import sys

    detectorsDict = {'ORB': detectors.orbDetector,
                     'MSER': detectors.mserDetector,
                     'SURF': detectors.surfDetector,
                     'SIFT': detectors.siftDetector,
                     'BLOB': detectors.blobDetector,
                     'FAST': detectors.fastDetector,
                     'AKAZE': detectors.akazeDetector,
                     'STAR': detectors.starDetector,
                     'GFTT': detectors.gfttDetector}

    img = cv2.imread(sys.argv[2])

    print(img)

    resString = subprocess.check_output("xrandr | grep '*'", shell=True)
    resString = resString.decode("utf-8")
    tmpNums = [i for i in map(int, re.findall(r'\d+', resString))]
    screenWidth = tmpNums[0]
    screenHeight = tmpNums[1]

    print(screenWidth, screenHeight)

    if sys.argv[1] == 'ALL':
        cnt = 0
        height = min(len(img) + 100, screenHeight // 3)
        width = min(len(img[0]) + 100, screenWidth // 3)
        print(width, height)
        for key, detector in detectorsDict.items():
            x = width * (cnt % 3)
            y = height * (cnt//3)
            cv2.namedWindow(key, cv2.WINDOW_NORMAL)
            img1 = img.copy()
            img1 = detector(img1)
            cv2.imshow(key, img1)
            cv2.moveWindow(key, x, y)
            cv2.resizeWindow(key, width, height)
            cnt += 1
    else:
        img = detectorsDict[sys.argv[1]](img)
        cv2.imshow(sys.argv[1], img)

    # cv2.createButton(None, kek)

    while True:
        kek = cv2.waitKey()
        if 0xFF & kek == 27:
            break
