import numpy as np
import cv2
import glob
from glob import glob
import os

# termination criteria
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
a = 5  # columns
b = 3  # rows
objp = np.zeros((1, b*a, 3), np.float64)
objp[0, :, :2] = np.mgrid[0:a, 0:b].T.reshape(-1, 2)

# Arrays to store object points and image points from all the images.
objpoints = []  # 3d point in real world space
imgpoints = []  # 2d points in image plane.

images = images = glob('./images/chessboard/*.jpg')

calibration_flags = cv2.fisheye.CALIB_RECOMPUTE_EXTRINSIC + \
    cv2.fisheye.CALIB_CHECK_COND+cv2.fisheye.CALIB_FIX_SKEW

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
        if key == ord('q'):
            objpoints.append(objp)
            imgpoints.append(corners2)
        elif key == ord('r'):
            os.remove(fname)
    else:
        os.remove(fname)
