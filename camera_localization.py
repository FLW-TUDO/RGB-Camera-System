import csv
from calibration_all import get_intrinsics, get_extrinsics
from icecream import ic
import numpy as np
import ast
from scipy.spatial.transform import Rotation as R
import cv2
import glob
import os


csv_file = 'vicon_pose_chessboard.csv'
images = './images/snapper/*.png'
scale = 130
a = 7
b = 5

ret, mtx, dist, newcameramtx, roi, _, _ = get_intrinsics(
    images, a, b, scale, visulaize=False)


def get_homogenous_form(rot, trans):
    mat = np.column_stack((rot, trans))
    mat_homog = np.row_stack((mat, [0.0, 0.0, 0.0, 1.0]))
    return mat_homog


def get_chessboard2vicon_transform(csv_file, img_path):
    with open(csv_file) as f:
        reader = csv.reader(f)
        reader_list = list(reader)
        path_mod = os.path.split(img_path)[-1]
        img_num = path_mod.split('.')[-2]
        ic(img_num)

        search_entry = 'img_' + img_num
        ic(search_entry)
        for i, entries in enumerate(reader_list):
            for j in entries:
                if j == search_entry:
                    index = i
                    ic(index)
        row = reader_list[int(index)]

        chessboard2vicon_trans = np.array(ast.literal_eval(row[1]))
        ic(chessboard2vicon_trans)

        chessboard2vicon_rot_quat = ast.literal_eval(row[2])
        ic(chessboard2vicon_rot_quat)
        chessboard2vicon_rot_quat = R.from_quat(chessboard2vicon_rot_quat)
        ic(chessboard2vicon_rot_quat)
        chessboard2vicon_rot = R.as_matrix(
            chessboard2vicon_rot_quat)  # rotation matrix form
        ic(chessboard2vicon_rot)

        chessboard2vicon_transform = get_homogenous_form(
            chessboard2vicon_rot, chessboard2vicon_trans)
        ic(chessboard2vicon_transform)

    # return chessboard2vicon_trans, chessboard2vicon_rot
    return chessboard2vicon_transform


def get_origin_chess2cam_transform(img_path):
    ret, rvecs, tvecs = get_extrinsics(img_path, a, b, scale, mtx, dist)

    origin_chess2cam_trans = np.array(tvecs.reshape(1, 3)[0])
    ic(origin_chess2cam_trans)

    origin_chess2cam_rot_axis_angle = rvecs.reshape(
        1, 3)[0]  # given as a rotation vector (axis-angle)
    ic(origin_chess2cam_rot_axis_angle)
    origin_chess2cam_rot, _ = cv2.Rodrigues(
        origin_chess2cam_rot_axis_angle)  # rotation matrix form
    ic(origin_chess2cam_rot)

    chessboard2vicon_transform = get_homogenous_form(
        origin_chess2cam_rot, origin_chess2cam_trans)
    ic(chessboard2vicon_transform)

    # return origin_chess2cam_trans, origin_chess2cam_rot
    return chessboard2vicon_transform


def get_origin_chess2chessboard_transform(scale):
    origin_chess2chessboard_trans = np.array([scale, scale, 0])
    ic(origin_chess2chessboard_trans)

    origin_chess2chessboard_rot = np.eye(3)
    ic(origin_chess2chessboard_rot)

    origin_chess2chessboard_transform = get_homogenous_form(
        origin_chess2chessboard_rot, origin_chess2chessboard_trans)
    ic(origin_chess2chessboard_transform)

    # return origin_chess2chessboard_trans, origin_chess2chessboard_rot
    return origin_chess2chessboard_transform


if __name__ == '__main__':
    images = glob.glob(images)
    cam2vicon_trans_sum = 0
    for fName in images:
        chessboard2vicon_transform = get_chessboard2vicon_transform(
            csv_file, fName)
        origin_chess2cam_transform = get_origin_chess2cam_transform(
            fName)
        origin_chess2chessboard_transform = get_origin_chess2chessboard_transform(
            scale)

        origin_chess2vicon_transform = chessboard2vicon_transform.dot(
            origin_chess2chessboard_transform)
        cam2vicon_transform = origin_chess2vicon_transform.dot(
            np.linalg.inv(origin_chess2cam_transform))
        ic(cam2vicon_transform)

        cam2vicon_trans_sum += cam2vicon_transform[0:3, 3]

        origin_chess2vicon_rot = R.from_matrix(
            origin_chess2vicon_transform[0:3, 0:3])
        origin_chess2vicon_rot = R.as_quat(origin_chess2vicon_rot)

    ic(cam2vicon_trans_sum)
    cam2vicon_trans_avg = np.divide(cam2vicon_trans_sum, len(images))
    ic(cam2vicon_trans_avg)
