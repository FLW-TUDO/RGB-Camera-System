import numpy as np
from camera_localization import get_homogenous_form
from icecream import ic
from PyVicon.vicon_tracker import ObjectTracker
import csv
import ast
from scipy.spatial.transform import Rotation as R


'''
    Script for calculating the location of the object with respect to a camera using camera location and 
    object's vicon location
'''

cam_locations_csv_file = '../cam_locations.csv'


def get_obj2vicon_transform(obj_id):
    vicon = ObjectTracker()
    vicon.connect()
    obj2vicon_trans = vicon.aquire_Object_Trans(object_name=obj_id)
    obj2vicon_rot = vicon.aquire_Object_RotQuaternion(object_name=obj_id)
    return obj2vicon_trans, obj2vicon_rot

def get_obj_gt_transform(cam_id, obj_id):
    # with open(cam_locations_csv_file) as f:
    #     reader = csv.reader(f)
    #     reader_list = list(reader)
    #     #header = reader_list[0]
    #     for row in reader_list[0:]:
    #         if int(row[0]) == cam_id:
    #             cam2vicon_trans = np.array(ast.literal_eval(row[1]))
    #             cam2vicon_rot = np.array(ast.literal_eval(row[2]))
    #             cam2vicon_transform = get_homogenous_form(cam2vicon_rot, cam2vicon_trans)
    #             ic(cam2vicon_transform)
    #
    # obj2vicon_trans, obj2vicon_rot = get_obj2vicon_transform(obj_id)
    # obj2vicon_rot = np.array(convert_to_rotation_matrix(obj2vicon_rot))
    # obj2vicon_trans = np.array(obj2vicon_trans)
    #
    # obj2vicon_transform = get_homogenous_form(obj2vicon_rot, obj2vicon_trans)
    # ic(obj2vicon_transform)


    # klt_trans = np.array([-2590.7, -2225.1, 381.7])
    # klt_rot = np.array(convert_to_rotation_matrix([-0.3, -0.22, 89.7]))
    # obj2vicon_transform = get_homogenous_form(klt_rot, klt_trans)
    # ic(obj2vicon_transform)
    #
    # cam_trans = np.array([-2684.8, -3678.4, 1281.9])
    # cam_rot = np.array(convert_to_rotation_matrix([-125.6, 1.92, 2.72]))
    # cam2vicon_transform = get_homogenous_form(cam_rot, cam_trans)
    # ic(cam2vicon_transform)

    vicon = ObjectTracker()
    vicon.connect()

    klt_trans = vicon.aquire_Object_Trans(object_name='KLT_32_neu')
    klt_rot = vicon.aquire_Object_RotQuaternion(object_name='KLT_32_neu')
    klt_rot = np.array(convert_to_rotation_matrix(klt_rot))
    obj2vicon_transform = get_homogenous_form(klt_rot, klt_trans)
    ic(obj2vicon_transform)

    cam_trans = vicon.aquire_Object_Trans(object_name='camera')
    cam_rot = vicon.aquire_Object_RotQuaternion(object_name='camera')
    cam_rot = np.array(convert_to_rotation_matrix(cam_rot))
    cam2vicon_transform = get_homogenous_form(cam_rot, cam_trans)
    ic(cam2vicon_transform)

    obj2cam_transform = obj2vicon_transform.dot(np.linalg.inv(cam2vicon_transform))
    ic(obj2cam_transform)
    obj2cam_trans = obj2cam_transform[0:3, 3]
    obj2cam_rot = obj2cam_transform[0:3, 0:3]

    return obj2cam_trans, obj2cam_rot

#TODO: verify intrinsic and extrinsic rotations
def convert_to_rotation_matrix(rot):
    '''
    Converts quaterion or euler angles (with XYZ intrisic orientation) to rotation matrix
    '''
    if len(rot) == 3: #euler with XYZ intrinsic rotation
        rot_euler = R.from_euler('XYZ', rot)
        rot_mat = rot_euler.as_matrix()
    elif len(rot) == 4: #quaternion
        rot_quat = R.from_quat(rot)
        rot_mat = rot_quat.as_matrix()
    return rot_mat



if __name__ == '__main__':
    get_obj_gt_transform(0, 'KLT_32_neu')