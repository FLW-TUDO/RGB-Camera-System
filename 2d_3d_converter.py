from camera import Camera
import numpy as np
import cv2


def undistort(img, mtx, dist):
    _img_shape = img.shape[:2]
    DIM = _img_shape[::-1]
    map1, map2 = cv2.fisheye.initUndistortRectifyMap(
        mtx, dist, np.eye(3), mtx, DIM, cv2.CV_16SC2)
    undistorted_img = cv2.remap(
        img, map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
    return undistorted_img


if __name__ == '__main__':
    test_pts_2d = np.array(
        [[533, 744], [617.5, 495], [456.5, 520], [558, 543]])

    mtx = np.array([[1.83212000e+03, 0.0, 1.30771040e+03],
                    [0.0, 1.82888459e+03, 1.03749179e+03],
                    [0.0, 0.0, 1.0]])
    dist = np.array([[0.00735673],
                     [1.51828844],
                     [-4.9074145],
                     [6.63861832]])
    tvecs =
    rvecs =
    # proj_mat =
    # proj_mat_mod =
    # proj_mat_inv =
    # tvecs_res =
    # rvecs_res =
    img = cv2.imread('./detectron_test_img')
    undistorted_img = undistort(img, mtx, dist)
