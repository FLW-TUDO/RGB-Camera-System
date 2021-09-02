import csv
from calibration_all import axis_select, get_intrinsics, get_extrinsics
from icecream import ic
import numpy as np
import ast
from scipy.spatial.transform import Rotation as R
import cv2
import glob


def get_homogenous_form(rot, trans):
    mat = np.column_stack((rot, trans))
    mat_homog = np.row_stack((mat, [0.0, 0.0, 0.0, 1.0]))
    return mat_homog


def get_chessboard2vicon_transform(csv_file):
    with open(csv_file) as f:
        reader = csv.reader(f)
        reader_list = list(reader)
        for row in reader_list[6:]:
            print(row)
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
            break

    # return chessboard2vicon_trans, chessboard2vicon_rot
    return chessboard2vicon_transform


def get_origin_chess2cam_transform(imgs_path):
    images = glob.glob(imgs_path)
    for fName in images:
        ret, rvecs, tvecs = get_extrinsics(fName, a, b, scale, mtx, dist)

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

        break

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
    csv_file = 'vicon_pose_chessboard.csv'
    imgs_path = './images/snapper/8.png'
    scale = 130
    a = 7
    b = 5
    ret, mtx, dist, newcameramtx, roi, _, _ = get_intrinsics(
        imgs_path, a, b, scale, visulaize=False)

    chessboard2vicon_transfrom = get_chessboard2vicon_transform(
        csv_file)
    origin_chess2cam_transform = get_origin_chess2cam_transform(
        imgs_path)
    origin_chess2chessboard_transfrom = get_origin_chess2chessboard_transform(
        scale)

    origin_chess2vicon_transform = chessboard2vicon_transfrom.dot(
        origin_chess2chessboard_transfrom)
    cam2vicon_transform = origin_chess2vicon_transform.dot(
        np.linalg.inv(origin_chess2cam_transform))
    ic(cam2vicon_transform)
