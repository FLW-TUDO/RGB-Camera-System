import csv
from calibration.calibration_all import get_extrinsics, undistort_and_save, get_intrinsics
from icecream import ic
import numpy as np
import ast
from scipy.spatial.transform import Rotation as R
import cv2
import glob
import os
import csv
# ic.disable()


'''
The script finds the location of a given camera in the vicon frame using snapped images of a vicon-tacked checkerboard.
'''

vicon_chessboard_pose_csv_file = '../vicon_pose_chessboard.csv' #intermediary csv file
images_src = '../images/snapper/cam_localization'
images_undist = '../images/snapper/cam_localization/undistorted'
cam_locations_csv_file = '../cam_locations.csv' #final csv file
calib_params_csv_file = '../calib_params_all.csv'

scale = 130
a = 7
b = 5


def get_img_pts(images_src):
    images_paths = sorted(glob.glob(os.path.join(images_src, '*.png')))
    img_pts_all = []
    for img_path in images_paths:
        img = cv2.imread(img_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        ret, corners = cv2.findChessboardCorners(gray, (a, b), None)
        if ret == True:
            corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
            img_pts_all.append(corners2)
        else:
            raise 'Checkerboard intersection points Not found!'
    return img_pts_all


def get_all_chessboard2vicon_pts(csv_file, cam_id):
    chessboard2vicon_rot_list = []
    chessboard2vicon_trans_list = []
    with open(csv_file) as f:
        reader = csv.reader(f)
        reader_list = list(reader)
        cam_search_entry = f'cam_{cam_id}'
        for row in reader_list:
            if row[0] == cam_search_entry:
                chessboard2vicon_trans = np.array(ast.literal_eval(row[2]))  # converts string list
                #ic(chessboard2vicon_trans)

                chessboard2vicon_rot_quat = ast.literal_eval(row[3])
                #ic(chessboard2vicon_rot_quat)
                chessboard2vicon_rot_quat = R.from_quat(chessboard2vicon_rot_quat)
                #ic(chessboard2vicon_rot_quat)
                chessboard2vicon_rot = R.as_matrix(chessboard2vicon_rot_quat)  # rotation matrix form
                #ic(chessboard2vicon_rot)

                chessboard2vicon_trans_list.append(chessboard2vicon_trans)
                chessboard2vicon_rot_list.append(chessboard2vicon_rot)
    return chessboard2vicon_rot_list, chessboard2vicon_trans_list


def get_all_origin_chess2vicon_pts(scale, chessboard2vicon_rot_list, chessboard2vicon_trans_list):
    '''
        Origin_chess is located at the first intersection
    '''
    origin_chess2chessboard_trans = np.array([scale, scale, 0])
    origin_chess2chessboard_rot = np.eye(3)
    origin_chess2chessboard_transform = get_homogenous_form(origin_chess2chessboard_rot, origin_chess2chessboard_trans)
    origin_chess2vicon_trans_list = []
    origin_chess2vicon_rot_list = []
    for rot, trans in zip(chessboard2vicon_rot_list, chessboard2vicon_trans_list):
        chessboard2vicon_transform = get_homogenous_form(rot, trans)
        origin_chess2vicon_transform = chessboard2vicon_transform.dot(origin_chess2chessboard_transform)
        #ic(origin_chess2vicon_transform)
        origin_chess2vicon_trans_list.append(origin_chess2vicon_transform[0:3, 3])
        origin_chess2vicon_rot_list.append(origin_chess2vicon_transform[0:3, 0:3])
    return origin_chess2vicon_rot_list, origin_chess2vicon_trans_list


def make_chessboar_pts():
    pass


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


if __name__ == '__main__':
    img_pts = get_img_pts(images_src)
    ic(img_pts)
    chessboard2vicon_rot_list, chessboard2vicon_trans_list = get_all_chessboard2vicon_pts(cam_id=1, csv_file=vicon_chessboard_pose_csv_file)
    ic(chessboard2vicon_rot_list)
    ic(chessboard2vicon_trans_list)
    origin_chess2vicon_rot_list, origin_chess2vicon_trans_list = get_all_origin_chess2vicon_pts(scale, chessboard2vicon_rot_list, chessboard2vicon_trans_list)
    ic(origin_chess2vicon_rot_list)
    ic(origin_chess2vicon_trans_list)


