from typing import TYPE_CHECKING
import numpy as np
import cv2 as cv
import glob

a = 7
b = 5
scale = 130

# termination criteria
criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)
# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
objp = np.zeros((a*b, 3), np.float32)
objp[:, :2] = np.mgrid[0:a, 0:b].T.reshape(-1, 2)
# Arrays to store object points and image points from all the images.
objpoints = []  # 3d point in real world space
imgpoints = []  # 2d points in image plane.
images = glob.glob('./images/snapper/*.png')


objp = np.zeros((1, a*b, 3), np.float32)
objp[0, :, :2] = np.mgrid[0:a,
                          0:b].T.reshape(-1, 2)

objp *= scale

print('Calculating...')
for fname in images:
    img = cv.imread(fname)
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    # Find the chess board corners
    ret, corners = cv.findChessboardCorners(gray, (a, b), None)
    # If found, add object points, image points (after refining them)
    if ret == True:
        objpoints.append(objp)
        corners2 = cv.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
        imgpoints.append(corners)
        # Draw and display the corners
        # cv.drawChessboardCorners(img, (a, b), corners2, ret)
        # cv.imshow('img', img)
        # cv.waitKey(250)
# objpoints = np.expand_dims(objpoints, 1)
cv.destroyAllWindows()

ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(
    objpoints, imgpoints, gray.shape[::-1], None, None)
# retval, mtx, dist, rvec, tvecs, stdDevInt, stdDevExt, perViewErrors = cv.calibrateCameraExtended(
#     objpoints, imgpoints, gray.shape[::-1], None, None)


print(mtx)
print(dist)
print(tvecs)


for fname in images:
    img = cv.imread(fname)
    img = cv.resize(img, (int(2592 / 2), int(2048 / 2)))
    h,  w = img.shape[:2]
    newcameramtx, roi = cv.getOptimalNewCameraMatrix(
        mtx, dist, (w, h), 1, (w, h))
    print(newcameramtx)

    # undistort
    dst = cv.undistort(img, mtx, dist, None, newcameramtx)
    # crop the image
    x, y, w, h = roi
    dst = dst[y:y+h, x:x+w]
    cv.imshow('img', dst)
    key = cv.waitKey(0)
    if key == 113:  # q
        cv.destroyAllWindows()
        break
    cv.destroyAllWindows()


# reprojection error
mean_error = 0
for i in range(len(objpoints)):
    imgpoints2, _ = cv.projectPoints(
        objpoints[i], rvecs[i], tvecs[i], mtx, dist)
    error = cv.norm(imgpoints[i], imgpoints2, cv.NORM_L2)/len(imgpoints2)
    mean_error += error
print("total error: {}".format(mean_error/len(objpoints)))
