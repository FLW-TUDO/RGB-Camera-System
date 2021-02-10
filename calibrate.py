import cv2
from glob import glob
import os

# simple script to delete not usable images

images = images = glob('./images/chessboard/*.jpg')

# termination criteria
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
a = 5  # columns
b = 3  # rows

for fname in images:
    img = cv2.imread(fname)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Find the chess board corners
    ret, corners = cv2.findChessboardCorners(gray, (a, b), None)
    print(ret)

    # If found, add object points, image points (after refining them)
    if ret == True:
        corners2 = cv2.cornerSubPix(
            gray, corners, (11, 11), (-1, -1), criteria)

        # Draw and display the corners
        img = cv2.drawChessboardCorners(img, (a, b), corners2, ret)
        cv2.imshow('img', img)

        key = cv2.waitKey(0)

        # check the image to display the correct chessboard corners
        if key == ord('r'):
            os.remove(fname)
    else:
        os.remove(fname)
