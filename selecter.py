import cv2
from glob import glob
import os
import numpy as np

aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_100)
#columns, rows
board = cv2.aruco.CharucoBoard_create(4, 3, 1, .8, aruco_dict)

# termination criteria
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.00001)

a = 5   # columns
b = 3   # rows
objp = np.zeros((1, a*b, 3), np.float32)
objp[0, :, :2] = np.mgrid[0:a, 0:b].T.reshape(-1, 2)


def chessboard(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Find the chess board corners
    ret, corners = cv2.findChessboardCorners(gray, (a, b), None)

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
            return False
        return True
    else:
        return False


def charuco(gray):
    decimator = 0
    corners, ids, rejectedPoints = cv2.aruco.detectMarkers(gray, aruco_dict)

    # print(corners)
    # print(rejectedPoints)

    if len(corners) > 0:
        # SUB PIXEL DETECTION
        for corner in corners:
            cv2.cornerSubPix(gray, corner,
                             winSize=(3, 3),
                             zeroZone=(-1, -1),
                             criteria=criteria)
        frame_markers = cv2.aruco.drawDetectedMarkers(img.copy(), corners, ids)
        cv2.imshow('Image', frame_markers)
        cv2.waitKey(0)
        res2 = cv2.aruco.interpolateCornersCharuco(corners, ids, gray, board)
        if res2[1] is not None and res2[2] is not None and len(res2[1]) > 3 and decimator % 1 == 0:
            print(res2)


# simple script to delete not usable images
if __name__ == "__main__":
    images = glob('./images/*.jpg')
    # images = glob('./images/charuco/*.jpg')

    for fname in images:
        img = cv2.imread(fname)

        # find chessboard corners
        res = chessboard(img)

        # find charuco corners
        # charuco(gray)
