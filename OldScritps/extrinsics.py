import cv2
import numpy as np
import glob

scale = 130
a = 7
b = 5

# mtx = np.array([[444.01212317, 0., 317.87966175],
#                 [0., 442.20562833, 264.72142874],
#                 [0., 0., 1.]])
# dist = np.array([[0.22847352],
#                  [-0.22746739],
#                  [0.70298454],
#                  [-0.04718649]])

mtx = np.array([[857.77408004,   0.,         660.74539569],
                [0.,         857.76365601, 507.87194174],
                [0.,           0.,           1.]])
dist = np.array([[0.16106916],
                 [0.10749546],
                 [-0.09645183],
                 [0.39021927]])

criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
objp = np.zeros((a*b, 3), np.float32)
objp[:, :2] = np.mgrid[0:a, 0:b].T.reshape(-1, 2)
objp *= scale

axis = np.float32([[3, 0, 0], [0, 3, 0], [0, 0, 3]]).reshape(-1, 3)
axis *= scale


def drawLine(img, corners, imgpts, line_width=3):
    corner = tuple(corners[0].ravel())
    img = cv2.line(img, corner, tuple(
        imgpts[0].ravel()), (255, 0, 0), line_width)
    img = cv2.line(img, corner, tuple(
        imgpts[1].ravel()), (0, 255, 0), line_width)
    img = cv2.line(img, corner, tuple(
        imgpts[2].ravel()), (0, 0, 255), line_width)
    return img


axis_cube = np.float32([[0, 0, 0], [0, 3, 0], [3, 3, 0], [3, 0, 0],
                        [0, 0, -3], [0, 3, -3], [3, 3, -3], [3, 0, -3]])
axis_cube *= scale


def drawCube(img, corners, imgpts, line_width=3):
    imgpts = np.int32(imgpts).reshape(-1, 2)

    # draw ground floor in green
    img = cv2.drawContours(img, [imgpts[:4]], -1, (0, 255, 0), -line_width)

    # draw pillars in blue color
    for i, j in zip(range(4), range(4, 8)):
        img = cv2.line(img, tuple(imgpts[i]), tuple(
            imgpts[j]), (255), line_width)

    # draw top layer in red color
    img = cv2.drawContours(img, [imgpts[4:]], -1, (0, 0, 255), line_width)

    return img


def undistort(img):
    _img_shape = img.shape[:2]
    DIM = _img_shape[::-1]
    map1, map2 = cv2.fisheye.initUndistortRectifyMap(
        mtx, dist, np.eye(3), mtx, DIM, cv2.CV_16SC2)
    undistorted_img = cv2.remap(
        img, map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
    return undistorted_img


def crop(img, center, width, height):
    h = int(height/2)
    w = int(width/2)
    x_left = max(0, int(center[0]-w))
    x_right = min(2592, int(center[0]+w))
    y_upper = max(0, int(center[1]-h))
    y_lower = min(2048, int(center[1]+h))
    return img[y_upper:y_lower, x_left:x_right]


for fname in glob.glob('./images/snapper/*.png'):
    img = cv2.imread(fname)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, corners = cv2.findChessboardCorners(gray, (a, b), None)

    if ret == True:
        corners2 = cv2.cornerSubPix(
            gray, corners, (11, 11), (-1, -1), criteria)
        cv2.drawChessboardCorners(img, (a, b), corners2, ret)
        cv2.imshow('img', img)
        cv2.waitKey(0)

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
        imgpts_line, jac_line = cv2.projectPoints(
            axis, rvecs, tvecs, mtx, dist)
        imgpts_cube, jac_cube = cv2.projectPoints(
            axis_cube, rvecs, tvecs, mtx, dist)

        # img = drawLine(img, corners2, imgpts_line, 10)
        img = drawCube(img, corners2, imgpts_cube, 8)
        img = undistort(img)
        # img = crop(img, corners2[0][0], int(2592/2), int(2048/2))
        img = cv2.resize(img, (int(2592/2), int(2048/2)))
        cv2.imshow(f'{fname}', img)
        key = cv2.waitKey(0) & 0xff
        cv2.destroyWindow(f'{fname}')
        if key == 113:
            cv2.destroyAllWindows()
            break
