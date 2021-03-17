import cv2
import numpy as np
import glob

a = 7
b = 5

mtx = np.array([[444.01212317, 0., 317.87966175],
                [0., 442.20562833, 264.72142874],
                [0., 0., 1.]])
dist = np.array([[0.22847352],
                 [-0.22746739],
                 [0.70298454],
                 [-0.04718649]])

criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
objp = np.zeros((a*b, 3), np.float32)
objp[:, :2] = np.mgrid[0:a, 0:b].T.reshape(-1, 2)

axis = np.float32([[3, 0, 0], [0, 3, 0], [0, 0, 3]]).reshape(-1, 3)


def draw(img, corners, imgpts):
    corner = tuple(corners[0].ravel())
    img = cv2.line(img, corner, tuple(imgpts[0].ravel()), (255, 0, 0), 3)
    img = cv2.line(img, corner, tuple(imgpts[1].ravel()), (0, 255, 0), 3)
    img = cv2.line(img, corner, tuple(imgpts[2].ravel()), (0, 0, 255), 3)
    return img


for fname in glob.glob('./images/chessboard/*.png'):
    img = cv2.imread(fname)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, corners = cv2.findChessboardCorners(gray, (a, b), None)

    if ret == True:
        corners2 = cv2.cornerSubPix(
            gray, corners, (11, 11), (-1, -1), criteria)

        # Find the rotation and translation vectors.
        # ret, rvecs, tvecs, inliers = cv2.solvePnPRansac(
        #     objp, corners2, mtx, dist)
        ret, rvecs, tvecs = cv2.solvePnP(
            objp, corners2, mtx, dist)

        print('#########################################')
        print(f'Image {fname}')
        print('# Translation')
        print(tvecs)
        print('# Rotation')
        print(rvecs)
        print('#########################################')

        # project 3D points to image plane
        imgpts, jac = cv2.projectPoints(axis, rvecs, tvecs, mtx, dist)

        img = draw(img, corners2, imgpts)
        cv2.imshow(f'{fname}', img)
        cv2.waitKey(0) & 0xff
