import cv2
import numpy as np
from glob import glob
import json


objectname = 'checkerboard'
origin_distance = 52.14
scale = 130
a = 7
b = 5
subpix_criteria = (cv2.TERM_CRITERIA_EPS+cv2.TERM_CRITERIA_MAX_ITER, 100, 1e-6)

# K = np.array([[444.01212317, 0., 317.87966175],
#               [0., 442.20562833, 264.72142874],
#               [0., 0., 1.]])
# D = np.array([[0.22847352],
#               [-0.22746739],
#               [0.70298454],
#               [-0.04718649]])

K = np.array([[864.97264262,   0.0,         633.44876394],
              [0.0,         864.93841842, 522.59039761],
              [0.0,          0.0,           1.0, ]])
D = np.array(
    [[-0.17183669,  0.13335938,  0.00132646,  0.00052755]])

objp = np.zeros((a*b, 3), np.float32)
objp[:, :2] = np.mgrid[0:a, 0:b].T.reshape(-1, 2)
objp *= scale


def create_points(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Find the chess board corners
    ret, corners = cv2.findChessboardCorners(
        gray, (a, b), flags=cv2.CALIB_CB_ADAPTIVE_THRESH+cv2.CALIB_CB_FAST_CHECK+cv2.CALIB_CB_NORMALIZE_IMAGE)
    # If found, add object points, image points (after refining them)
    if ret == True:
        corners = cv2.cornerSubPix(
            gray, corners, (11, 11), (-1, -1), subpix_criteria)
        img = cv2.drawChessboardCorners(img, (a, b), corners, ret)

        return corners, objp


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


def draw(img, corners, imgpts):
    corner = tuple(corners[0].ravel())
    img = cv2.line(img, corner, tuple(imgpts[0].ravel()), (255, 0, 0), 5)
    img = cv2.line(img, corner, tuple(imgpts[1].ravel()), (0, 255, 0), 5)
    img = cv2.line(img, corner, tuple(imgpts[2].ravel()), (0, 0, 255), 5)
    return img


def undistort(img):
    _img_shape = img.shape[:2]
    DIM = _img_shape[::-1]
    map1, map2 = cv2.fisheye.initUndistortRectifyMap(
        K, D, np.eye(3), K, DIM, cv2.CV_16SC2)
    undistorted_img = cv2.remap(
        img, map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
    return undistorted_img


def draw_cube(img, corners, imgpts, line_width=3):
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


def axis_select(input, scale):
    if input == 'cube':
        axis = np.float32([[0, 0, 0], [0, scale, 0], [scale, scale, 0], [scale, 0, 0],
                           [0, 0, -scale], [0, scale, -scale], [scale, scale, -scale], [scale, 0, -scale]])
    elif input == 'line':
        axis = np.array([[scale, 0, 0], [0, scale, 0], [0, 0, scale]],
                        dtype=np.float32).reshape(-1, 3)
    return axis


if __name__ == "__main__":
    # with open('./images/chessboard/data.json') as f:
    #     data = json.load(f)

    for i, fName in enumerate(glob('./images/snapper/*.png')):
        image = cv2.imread(fName)
        print(i)
        image_points, object_points = create_points(image)
        # cv2.imshow('Camera', img)
        # key = cv2.waitKey(0)
        # if key == 113:
        #     continue
        # TODO: use obtained tvecs & rvecs from calibrateCamera()
        rvecs, tvecs = calibrate(object_points, image_points)

        scale = 520
        axis = axis_select('cube', scale)
        projected_points, jac = cv2.projectPoints(axis, rvecs, tvecs, K, D)
        # image = draw(image, image_points, projected_points)
        image = draw_cube(image, image_points, projected_points)
        cv2.imshow('img', image)
        key = cv2.waitKey(0)

        if key == 113:  # q
            cv2.destroyAllWindows()
            break
        cv2.destroyAllWindows()
