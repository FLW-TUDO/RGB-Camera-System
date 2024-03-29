import cv2
import numpy as np
from glob import glob

a = 7
b = 5

objp = np.zeros((1, a*b, 3), np.float32)
objp[0, :, :2] = np.mgrid[0:a,
                          0:b].T.reshape(-1, 2)
subpix_criteria = (cv2.TERM_CRITERIA_EPS+cv2.TERM_CRITERIA_MAX_ITER, 100, 1e-6)
axis = np.array([[3, 0, 0], [0, 3, 0], [0, 0, -3]],
                dtype=np.float32).reshape(-1, 3)

K = np.array([[444.01212317, 0., 317.87966175],
              [0., 442.20562833, 264.72142874],
              [0., 0., 1.]])
D = np.array([[0.22847352],
              [-0.22746739],
              [0.70298454],
              [-0.04718649]])


def undistort(img):
    _img_shape = img.shape[:2]
    DIM = _img_shape[::-1]
    map1, map2 = cv2.fisheye.initUndistortRectifyMap(
        K, D, np.eye(3), K, DIM, cv2.CV_16SC2)
    undistorted_img = cv2.remap(
        img, map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
    return undistorted_img


def draw(img, corners, imgpts):
    corner = tuple(corners[0].ravel())
    img = cv2.line(img, corner, tuple(imgpts[0].ravel()), (255, 0, 0), 5)
    img = cv2.line(img, corner, tuple(imgpts[1].ravel()), (0, 255, 0), 5)
    img = cv2.line(img, corner, tuple(imgpts[2].ravel()), (0, 0, 255), 5)
    return img


def calibrate(object_points, image_points):
    ret, rvec, tvec = cv2.solvePnP(
        object_points, image_points, K, D)
    if ret:
        print("Rotation:")
        print(rvec)
        print("Translation:")
        print(tvec)
        return rvec, tvec
    else:
        print("Calculate extrinsics failed!")


def create_points(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Find the chess board corners
    ret, corners = cv2.findChessboardCorners(
        gray, (a, b), cv2.CALIB_CB_ADAPTIVE_THRESH+cv2.CALIB_CB_FAST_CHECK+cv2.CALIB_CB_NORMALIZE_IMAGE)
    # If found, add object points, image points (after refining them)
    if ret == True:
        corners = cv2.cornerSubPix(
            gray, corners, (3, 3), (-1, -1), subpix_criteria)
        img = cv2.drawChessboardCorners(img, (a, b), corners, ret)
        cv2.imshow('img', img)
        cv2.waitKey(0)

        return objp, corners


for fName in glob('./images/chessboard/*.png'):
    image = cv2.imread(fName)
    image = cv2.resize(image, (int(2592/2), int(2048/2)))

    cv2.imshow('Camera', image)
    key = cv2.waitKey(0)
    object_point, image_point = create_points(image)

    rvecs, tvecs = calibrate(object_point, image_point)

    imgpts, jac = cv2.projectPoints(axis, rvecs, tvecs, K, D)
    image = draw(image, image_point, imgpts)
    cv2.imshow('img', image)
    key = cv2.waitKey(0)

    rotM = cv2.Rodrigues(rvecs)[0]
    cameraPosition = -np.matrix(rotM).T * np.matrix(tvecs)

    print('Camera Position')
    print(cameraPosition)

    if key == 113:
        cv2.destroyAllWindows()
        break
