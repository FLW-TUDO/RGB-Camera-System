
import numpy as np
from vicon_tracker import ObjectTracker
from pyquaternion import Quaternion
import json


tracker = ObjectTracker()
tracker.connect()


def get_obj_to_cam_transform(obj_name, cam_id):
    obj_to_world_trans = tracker.aquire_Object_Trans(obj_name)
    obj_to_world_rot_quat = tracker.aquire_Object_RotQuaternion(
        obj_name)  # x,y,z,w

    obj_to_world_rot_quat_2 = Quaternion(
        obj_to_world_rot_quat[3], obj_to_world_rot_quat[0], obj_to_world_rot_quat[1], obj_to_world_rot_quat[2])  # w,x,y,z
    obj_to_world_rot = obj_to_world_rot_quat_2.rotation_matrix

    with open('cam_poses.json', 'r') as f:
        data = json.load(f)
    cam_to_world_trans = data['cam'+str(cam_id)]['trans']
    cam_to_world_rot = data['cam'+str(cam_id)]['rot']
    obj_to_cam_trans = [(cam_to_world_trans[i] - obj_to_world_trans[i])
                        for i in range(len(obj_to_world_trans))]
    obj_to_cam_rot = obj_to_world_rot * np.transpose(cam_to_world_rot)
    return (obj_to_cam_trans, obj_to_cam_rot)


# cam0_ref_trans = [105, 505, 605]
# cam0_ref_angles = [20, 10, 45]
# def convert_cam_poses(cam_id):


if __name__ == "__main__":
    obj_trans, obj_rot = get_obj_to_cam_transform('KLT_8_neu', 0)
    print(obj_trans)
    print(obj_rot)
