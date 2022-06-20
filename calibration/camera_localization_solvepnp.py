from icecream import ic
import numpy as np
import ast
from scipy.spatial.transform import Rotation as R
import cv2
import glob
import os
import csv
import matplotlib.pyplot as plt
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
    # images_paths = sort_files(os.path.join(images_src, '*.png'))
    img_pts_all = []
    for img_path in images_paths:
        img = cv2.imread(img_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        ret, corners = cv2.findChessboardCorners(gray, (a, b), None)
        if ret == True:
            corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
            corners2 = np.array(corners2)
            corners2 = np.reshape(corners2, (np.shape(corners2)[0], np.shape(corners2)[2])).tolist()
            img_pts_all.append(corners2)
        else:
            raise 'Checkerboard intersection points Not found!'
    return np.array(img_pts_all)


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
    return np.array(chessboard2vicon_rot_list), np.array(chessboard2vicon_trans_list)


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
    return np.array(origin_chess2vicon_rot_list), np.array(origin_chess2vicon_trans_list)


def make_chessboard_pts(origin_chess2vicon_rot_list, origin_chess2vicon_trans_list):
    '''
        creates remaining chessboard intersection points
    '''
    obj_points = initialize_obj_points(a, b, scale)
    chessboard_pts_trans_list = [] # pts on single chessboard instance
    all_chessboard2vicon_trans_list = []
    for rot, trans in zip(origin_chess2vicon_rot_list, origin_chess2vicon_trans_list):
        chessboard2vicon_transform = get_homogenous_form(rot, trans)
        for pt in obj_points[0]:
            pt_homog_form = get_homogenous_form(np.eye(3), pt.T)
            chessboard_pts = chessboard2vicon_transform.dot(pt_homog_form)
            chessboard_pts_trans_list.append(chessboard_pts[0:3, 3]) #only translation needed
        all_chessboard2vicon_trans_list.append(chessboard_pts_trans_list)
        chessboard_pts_trans_list = []
    return np.array(all_chessboard2vicon_trans_list)


def get_cam_location(cam_id, img_pts, vicon_pts):
    _, newcameramtx, dist, _ = get_calib_params(calib_params_csv_file, cam_id)
    ret, rvecs, tvecs = cv2.solvePnP(vicon_pts, img_pts, newcameramtx, dist)
    if ret:
        return rvecs, tvecs
    else:
        print("Calculate extrinsics failed!")


def get_calib_params(csv_file, cam_id):
    with open(csv_file) as f:
        reader = csv.reader(f)
        for row in list(reader):
            if row[0] == str(cam_id):
                mtx = np.array(ast.literal_eval(row[1]))
                newcameramtx = np.array(ast.literal_eval(row[2]))
                dist = np.array(ast.literal_eval(row[3]))
                roi = np.array(ast.literal_eval(row[4]))
                return mtx, newcameramtx, dist, roi


def initialize_obj_points(a, b, scale):
    objp = np.zeros((1, a*b, 3), np.float32)
    objp[0, :, :2] = np.mgrid[0:a, 0:b].T.reshape(-1, 2)
    objp *= scale
    # ic(np.shape(objp))
    return objp


def get_homogenous_form(rot, trans):
    mat = np.column_stack((rot, trans))
    mat_homog = np.row_stack((mat, [0.0, 0.0, 0.0, 1.0]))
    return mat_homog


def draw_chessboard_pts(xs, ys, zs):
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
    ax.scatter(xs, ys, zs)
    ax.set_xlabel('X Label')
    ax.set_ylabel('Y Label')
    ax.set_zlabel('Z Label')
    plt.show()


def check_2d_3d_matching(obj_pts, img_pts, rvecs, tvecs, mtx, dist):
    proj_obj_pts, _ = cv2.projectPoints(obj_pts, rvecs, tvecs, mtx, dist)
    ic(np.shape(proj_obj_pts))
    ic(np.shape(img_pts))
    proj_obj_pts = np.reshape(proj_obj_pts, (np.shape(obj_pts)[0], -1))
    error_x_sum = 0
    error_y_sum = 0
    for i, (img_pt, proj_obj_pt) in enumerate(zip(img_pts, proj_obj_pts)):
        error_x = np.sqrt((img_pt[0] - proj_obj_pt[0])**2)
        error_y = np.sqrt((img_pt[1] - proj_obj_pt[1])**2)
        error_x_sum += error_x
        error_y_sum += error_y
    ic(error_x_sum)
    ic(error_y_sum)




# def sort_files(files_path):
#     img_files = glob.glob(files_path)
#     sorted_files = []
#     i = 0
#     index = 1
#     while len(sorted_files) < len(img_files):
#         img_id = int(os.path.split(img_files[i])[-1].split('.')[-2].split('_')[-1])
#         if(img_id == index):
#             sorted_files.append(img_files[i])
#             index += 1
#             ic(sorted_files)
#         i += 1
#     return sorted_files


if __name__ == '__main__':
    img_pts = get_img_pts(images_src)
    chessboard2vicon_rot_list, chessboard2vicon_trans_list = get_all_chessboard2vicon_pts(cam_id=1, csv_file=vicon_chessboard_pose_csv_file)
    origin_chess2vicon_rot_list, origin_chess2vicon_trans_list = get_all_origin_chess2vicon_pts(scale, chessboard2vicon_rot_list, chessboard2vicon_trans_list)
    chessboard_pts = make_chessboard_pts(origin_chess2vicon_rot_list, origin_chess2vicon_trans_list)

    img_pts_reshaped = np.reshape(img_pts, (np.shape(img_pts)[0]*np.shape(img_pts)[1], np.shape(img_pts)[2]))
    chessboard_pts_reshaped = np.reshape(chessboard_pts, (np.shape(chessboard_pts)[0]*np.shape(chessboard_pts)[1], np.shape(chessboard_pts)[2]))
    ic(np.shape(img_pts_reshaped))
    ic(np.shape(chessboard_pts_reshaped))

    # draw_chessboard_pts(chessboard_pts_reshaped[:, 0], chessboard_pts_reshaped[:, 1], chessboard_pts_reshaped[:, 2])

    rvecs, tvecs = get_cam_location(1, img_pts_reshaped, chessboard_pts_reshaped)
    ic(tvecs)
    ic(rvecs)

    _, newcameramtx, dist, _ = get_calib_params(calib_params_csv_file, 1)
    check_2d_3d_matching(chessboard_pts_reshaped, img_pts_reshaped, rvecs, tvecs, newcameramtx, dist)