import numpy as np
import cv2 as cv
import glob

a = 7
b = 5
# termination criteria
criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)
# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
objp = np.zeros((a*b, 3), np.float32)
objp[:, :2] = np.mgrid[0:a, 0:b].T.reshape(-1, 2)
# Arrays to store object points and image points from all the images.
objpoints = []  # 3d point in real world space
imgpoints = []  # 2d points in image plane.
images = glob.glob('./images/snapper/*.png')
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
cv.destroyAllWindows()

ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(
    objpoints, imgpoints, gray.shape[::-1], None, None)

print(mtx)
print(dist)


# for fname in images:
#     img = cv.imread(fname)
#     h,  w = img.shape[:2]
#     newcameramtx, roi = cv.getOptimalNewCameraMatrix(
#         mtx, dist, (w, h), 1, (w, h))

#     # undistort
#     dst = cv.undistort(img, mtx, dist, None, newcameramtx)
#     # crop the image
#     x, y, w, h = roi
#     dst = dst[y:y+h, x:x+w]
#     cv.imshow('img', dst)
#     cv.waitKey(0)
# cv.destroyAllWindows()
