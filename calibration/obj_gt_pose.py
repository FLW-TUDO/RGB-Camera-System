import numpy as np
from calibration.camera_localization import get_homogenous_form, invert_homog_transfrom
from icecream import ic
from PyVicon.vicon_tracker import ObjectTracker
import csv
import ast
from scipy.spatial.transform import Rotation as R


'''
    Script for calculating the location of the object with respect to a camera using camera location and 
    object's vicon location
'''

vicon = ObjectTracker()
vicon.connect()

cam_locations_csv_file = './cam_locations.csv'


def get_obj2vicon_transform(obj_id):
    obj2vicon_trans = vicon.aquire_Object_Trans(object_name=obj_id)
    obj2vicon_rot = vicon.aquire_Object_RotEuler(object_name=obj_id)
    return obj2vicon_trans, obj2vicon_rot

# TODO: check if object and cam exist


def get_obj_gt_transform(cam_id, obj_id):
    with open(cam_locations_csv_file) as f:
        reader = csv.reader(f)
        reader_list = list(reader)
        #header = reader_list[0]
        for row in reader_list[0:]:
            if row[0] == cam_id:
                cam2vicon_trans = np.array(ast.literal_eval(row[1]))
                cam2vicon_rot = np.array(
                    ast.literal_eval(row[2]))  # rotation matrix
                cam2vicon_transform = get_homogenous_form(
                    cam2vicon_rot, cam2vicon_trans)
                ic(cam2vicon_transform)

    obj2vicon_trans, obj2vicon_rot = get_obj2vicon_transform(obj_id)
    obj2vicon_rot = R.from_euler('XYZ', obj2vicon_rot, degrees=False)
    obj2vicon_rot_mat = obj2vicon_rot.as_matrix()
    obj2vicon_transform = get_homogenous_form(
        obj2vicon_rot_mat, obj2vicon_trans)
    ic(obj2vicon_transform)

    obj2cam_transform = invert_homog_transfrom(
        cam2vicon_transform).dot(obj2vicon_transform)
    ic(obj2cam_transform)
    obj2cam_trans = obj2cam_transform[0:3, 3]
    obj2cam_rot = obj2cam_transform[0:3, 0:3]

    return obj2cam_trans, obj2cam_rot


def invert_homog_transfrom(homog_trans):
    trans = homog_trans[0:3, 3]
    rot = homog_trans[0:3, 0:3]
    rot_inv = np.linalg.inv(rot)
    homog_inv = get_homogenous_form(rot_inv, -1*(rot_inv.dot(trans)))
    ic(homog_inv)
    return homog_inv


if __name__ == '__main__':
    #get_obj_gt_transform(6, 'KLT_8_neu')
    pass
