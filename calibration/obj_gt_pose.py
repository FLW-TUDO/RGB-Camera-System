import numpy as np
from calibration.camera_localization import get_homogenous_form, invert_homog_transfrom
from icecream import ic
from PyVicon.vicon_tracker import ObjectTracker
import csv
import ast
from scipy.spatial.transform import Rotation as R
import time

ic.disable()

'''
    Script for calculating the location of the object with respect to a camera using camera location and 
    object's vicon location
'''

vicon = ObjectTracker()
vicon.connect()

# cam_locations_csv_file = './cam_locations.csv'
cam_locations_csv_file = '/media/athos/DATA-III/projects/RGB-Camera-System/cam_locations.csv'
camera2vicon = {}
with open(cam_locations_csv_file) as f:
    reader = csv.reader(f)
    reader_list = list(reader)
    for row in reader_list:
        cameraId = row[0]
        translation = np.array(ast.literal_eval(row[1]))
        rotation = np.array(ast.literal_eval(row[2]))  # rotation matrix
        transfrom = get_homogenous_form(rotation, translation)
        camera2vicon[cameraId] = {'transf': transfrom}


def get_obj2vicon_transform(obj_id):
    obj2vicon_trans = vicon.aquire_Object_Trans(object_name=obj_id)
    obj2vicon_rot = vicon.aquire_Object_RotEuler(object_name=obj_id)
    return obj2vicon_trans, obj2vicon_rot


def get_obj2vicon_transform_sync(obj_id):
    obj2vicon_trans = vicon.aquire_Object_Trans_sync(object_name=obj_id)
    obj2vicon_rot = vicon.aquire_Object_RotEuler_sync(object_name=obj_id)
    return obj2vicon_trans, obj2vicon_rot


def get_new_frame():
    vicon.aquire_Frame()

# TODO: check if object and cam exist
def get_obj_gt_transform(cam_id, obj_id):
    cam2vicon_transform = camera2vicon[cam_id]

    obj2vicon_trans, obj2vicon_rot = get_obj2vicon_transform(obj_id)

    # TODO move to scene builder form scene reconstruction
    # obj2vicon_rot = R.from_euler('XYZ', obj2vicon_rot, degrees=False)
    # obj2vicon_rot_mat = obj2vicon_rot.as_matrix()

    # obj2vicon_transform = get_homogenous_form(obj2vicon_rot_mat, obj2vicon_trans)
    # ic(obj2vicon_transform)

    # obj2cam_transform = invert_homog_transfrom(cam2vicon_transform).dot(obj2vicon_transform)
    # ic(obj2cam_transform)
    # obj2cam_trans = obj2cam_transform[0:3, 3].tolist()
    # obj2cam_rot = obj2cam_transform[0:3, 0:3].tolist()

    # return obj2cam_trans, obj2cam_rot
    return obj2vicon_trans, obj2vicon_rot


def invert_homog_transfrom(homog_trans):
    trans = homog_trans[0:3, 3]
    rot = homog_trans[0:3, 0:3]
    rot_inv = np.linalg.inv(rot)
    homog_inv = get_homogenous_form(rot_inv, -1 * (rot_inv.dot(trans)))
    return homog_inv


if __name__ == '__main__':
    get_obj_gt_transform(6, 'KLT_8_neu')
