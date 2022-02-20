import csv
from calibration.calibration_all import get_extrinsics, undistort_and_save
from icecream import ic
import numpy as np
import ast
from scipy.spatial.transform import Rotation as R
import cv2
import glob
import os
import csv


'''
The script finds the location of a given camera in the vicon frame, assuming a vicon-tracked chessboard is used.
'''

vicon_chessboard_pose_csv_file = '../vicon_pose_chessboard.csv' #intermediary csv file
images = '../images/snapper/cam_localization/*.png'
images_undist = '../images/snapper/cam_localization/undistorted'
cam_locations_csv_file = '../cam_locations.csv' #final csv file

scale = 130
a = 7
b = 5

# ret, mtx, dist, newcameramtx, roi, _, _ = get_intrinsics(
#     images, a, b, scale, visulaize=False)


mtx = np.array([[870.04652949,   0.0, 644.25313422],
                [0.0, 870.04874977, 543.69294777],
                [0.0,   0.0,   1.0]])
newcameramtx = np.array([[808.68377686,   0.0, 643.57414451],
                        [0.0, 810.70056152, 547.12750201],
                        [0.0,   0.0,   1.0]])
dist = np.array([[-0.164559885,  0.108215606,  0.00257066836, -0.000120995529, -0.00928914594]])
roi = (5, 10, 1285, 1003)

def get_homogenous_form(rot, trans):
    '''
    @param rot: rotation matrix
    @type rot: numpy array
    @param trans: translation vector
    @type trans: numpy
    @return: homogenous form
    @rtype: numpy array
    '''
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

        chessboard2vicon_trans = np.array(ast.literal_eval(row[1]))  # converts string list
        ic(chessboard2vicon_trans)

        chessboard2vicon_rot_quat = ast.literal_eval(row[2])
        ic(chessboard2vicon_rot_quat)
        chessboard2vicon_rot_quat = R.from_quat(chessboard2vicon_rot_quat)
        ic(chessboard2vicon_rot_quat)
        chessboard2vicon_rot = R.as_matrix(chessboard2vicon_rot_quat)  # rotation matrix form
        ic(chessboard2vicon_rot)

        chessboard2vicon_transform = get_homogenous_form(chessboard2vicon_rot, chessboard2vicon_trans)
        ic(chessboard2vicon_transform)

    # return chessboard2vicon_trans, chessboard2vicon_rot
    return chessboard2vicon_transform


def get_origin_chess2cam_transform(img_path):
    ret, rvecs, tvecs = get_extrinsics(img_path, a, b, scale, newcameramtx, dist)
    ic(tvecs)
    origin_chess2cam_trans = np.array(tvecs.reshape(1, 3)[0])
    ic(origin_chess2cam_trans)

    origin_chess2cam_rot_axis_angle = rvecs.reshape(1, 3)[0]  # given as a rotation vector (axis-angle)
    ic(origin_chess2cam_rot_axis_angle)
    origin_chess2cam_rot, _ = cv2.Rodrigues(origin_chess2cam_rot_axis_angle)  # rotation matrix form
    ic(origin_chess2cam_rot)

    chessboard2vicon_transform = get_homogenous_form(origin_chess2cam_rot, origin_chess2cam_trans)
    ic(chessboard2vicon_transform)

    # return origin_chess2cam_trans, origin_chess2cam_rot
    return chessboard2vicon_transform


def get_origin_chess2chessboard_transform(scale):
    '''
        Offset correction from location of marker on chessboard to first corner location (used in extrinsic calculation)
        Origin_chess is located at the first intersection
    '''
    origin_chess2chessboard_trans = np.array([scale, scale, 0])
    ic(origin_chess2chessboard_trans)

    origin_chess2chessboard_rot = np.eye(3)
    ic(origin_chess2chessboard_rot)

    origin_chess2chessboard_transform = get_homogenous_form(origin_chess2chessboard_rot, origin_chess2chessboard_trans)
    ic(origin_chess2chessboard_transform)

    # return origin_chess2chessboard_trans, origin_chess2chessboard_rot
    return origin_chess2chessboard_transform

def get_cam2vicon_transform(img_path):
    chessboard2vicon_transform = get_chessboard2vicon_transform(vicon_chessboard_pose_csv_file, img_path)
    origin_chess2cam_transform = get_origin_chess2cam_transform(img_path)
    origin_chess2chessboard_transform = get_origin_chess2chessboard_transform(scale)

    origin_chess2vicon_transform = chessboard2vicon_transform.dot(origin_chess2chessboard_transform)
    cam2vicon_transform = origin_chess2vicon_transform.dot(invert_homog_transfrom(origin_chess2cam_transform))
    ic(cam2vicon_transform)
    cam2vicon_trans = cam2vicon_transform[0:3, 3]
    cam2vicon_rot = cam2vicon_transform[0:3, 0:3]

    # cam2vicon_rot_mat = R.from_matrix(cam2vicon_transform[0:3, 0:3])
    # cam2vicon_rot_euler = np.degrees(cam2vicon_rot_mat.as_euler('xyz', degrees=False))
    return cam2vicon_trans, cam2vicon_rot #as a rotation matrix

#TODO: retrieve intrinsics according to cam id
def get_cam_location(images_path, cam_id, use_undist=True):
    images = glob.glob(images_path)
    cam2vicon_trans_list = np.array([0, 0, 0])
    cam2vicon_rot_list = np.array([0, 0, 0])
    for img_path in images:
        if use_undist:
            img_path = undistort_and_save(img_path, mtx, dist, newcameramtx, roi, visualize=True, save_path=images_undist)
            ic(img_path)
        trans, rot = get_cam2vicon_transform(img_path)
        cam2vicon_trans_list = np.add(cam2vicon_trans_list, trans)
        cam2vicon_rot_mat = R.from_matrix(rot)
        cam2vicon_rot_euler = np.degrees(cam2vicon_rot_mat.as_euler('XYZ', degrees=False))
        cam2vicon_rot_list = np.add(cam2vicon_rot_list, cam2vicon_rot_euler)
        ic(cam2vicon_trans_list)
        ic(cam2vicon_rot_list)
    cam2vicon_trans_avg = np.divide(cam2vicon_trans_list, len(images))
    ic(cam2vicon_trans_avg)
    # TODO: convert to quaternion to get average - slerp
    cam2vicon_rot_avg = np.divide(cam2vicon_rot_list, len(images))
    ic(cam2vicon_rot_avg)
    cam2vicon_rot_avg = R.from_euler('XYZ', cam2vicon_rot_avg, degrees=True)
    cam2vicon_rot_avg_mat = cam2vicon_rot_avg.as_matrix()
    ic(cam2vicon_rot_avg_mat)
    save_cam_location(cam_locations_csv_file, cam_id, cam2vicon_trans_avg.tolist(), cam2vicon_rot_avg_mat.tolist())
    return cam2vicon_trans_avg, cam2vicon_rot_avg_mat

#TODO: add header, check if cam id already exists
def save_cam_location(csv_file, cam_id, cam_trans, cam_rot):
    with open(csv_file, 'a', newline='') as out_file:
        writer = csv.writer(out_file)
        #header = ['cam_id', 'cam_trans', 'cam_rot']
        #writer.writerow(header)
        data = [cam_id, cam_trans, cam_rot]
        writer.writerow(data)

def invert_homog_transfrom(homog_trans):
    trans = homog_trans[0:3, 3]
    rot = homog_trans[0:3, 0:3]
    rot_inv = np.linalg.inv(rot)
    homog_inv = get_homogenous_form(rot_inv, -1*(rot_inv.dot(trans)))
    ic(homog_inv)
    return homog_inv


if __name__ == '__main__':
    trans, rot = get_cam_location(images, use_undist=True)
    # ic(trans)
    # ic(rot)
    # trans, rot = get_chessboard2vicon_transform(vicon_chessboard_pose_csv_file)

