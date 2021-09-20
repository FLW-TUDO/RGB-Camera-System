from camera_localization import get_homogenous_form
import cv2
import numpy as np
from icecream import ic


def get_corner2cam_transform(objp, corners2, mtx, dist):
    # rotation given as axis angle
    ret, rvecs, tvecs = cv2.solvePnP(objp, corners2, mtx, dist)
    ic(rvecs)
    if ret:
        rvecs_rot, _ = cv2.Rodrigues(
            rvecs)  # rotation matrix form
        ic(rvecs_rot)
        return rvecs_rot, tvecs
    else:
        print("Calculate extrinsics failed!")


# corner assumed to be upper left (1st point)
def get_relative_pts(points):
    realtive_points = []
    for i, point in enumerate(points[0]):
        if (i == 0):
            if(points.shape[2] == 2):
                realtive_points.append([0.0, 0.0])
            else:
                realtive_points.append([0.0, 0.0, 0.0])
            continue
        else:
            relative_point = abs(point - points[0][0])
            realtive_points.append((np.around(relative_point, 2)).tolist())

    return realtive_points


if __name__ == '__main__':
    img_path = './2d_3d_mapper_test_img.png'
    img = cv2.imread(img_path)

    dist = np.array(
        [[-0.18619846,  0.14989978,  0.00036384,  -0.00132873, -0.04512847]])
    newcameramtx = np.array([[784.04003906,   0.0,         624.41500984],
                             [0.0,         783.08575439,  521.11914666],
                             [0.0,           0.0,            1.0]])

    upper_left_3d = [-6660.1, -290.8, 0.0]
    upper_right_3d = [-5752.4, 2231.1, 0.0]
    lower_left_3d = [-2928.9, 704.4, 0.0]
    lower_right_3d = [-2800, 2821.7, 0.0]

    upper_left_2d = [389, 105]
    upper_right_2d = [710, 107.5]
    lower_left_2d = [496.5, 230]
    lower_right_2d = [946.5, 218.5]

    obj_pts = (np.array((upper_left_3d, upper_right_3d,
                         lower_left_3d, lower_right_3d))).reshape(1, 4, 3)
    ic(obj_pts)

    img_pts = (np.array((upper_left_2d, upper_right_2d,
                         lower_left_2d, lower_right_2d))).reshape(1, 4, 2)
    ic(img_pts)

    relative_img_pts = get_relative_pts(img_pts)
    ic(relative_img_pts)

    relative_obj_pts = get_relative_pts(obj_pts)
    ic(relative_obj_pts)

    rvecs, tvecs = get_corner2cam_transform(
        np.array(relative_obj_pts), np.array(relative_img_pts), newcameramtx, dist)

    corner2cam_transform = get_homogenous_form(rvecs, tvecs)
    ic(corner2cam_transform)

    cam2vicon_transform = np.array([[0.4730510,  0.7677609, -0.4321643, 1010.7],
                                    [-0.8617371, 0.3010987, -0.4083488, 941.5],
                                    [-0.1833901,  0.5655819,  0.8040431, 1251.3],
                                    [0.0, 0.0, 0.0, 1.0]])
    ic(cam2vicon_transform)

    corner2vicon_transform = cam2vicon_transform.dot(corner2cam_transform)
    ic(corner2vicon_transform)
