from calibration_all import get_intrinsics
import numpy as np
from icecream import ic


scale = 130
a = 7
b = 5
imgs_path = './images/snapper/*.png'
ret, mtx, dist, newcameramtx, roi, _, _ = get_intrinsics(
    imgs_path, a, b, scale, visulaize=False)
ic(newcameramtx)

intrisics_inv = np.linalg.inv(newcameramtx)
ic(intrisics_inv)

test_imgs = './images/detectron_test_img.png'

upper_left = [533, 477]
upper_right = [617.5, 495]
lower_left = [456.5, 520]
lower_right = [558, 543]

# img_w = int(2592 / 2)
# img_h = int(2048 / 2)
point_2d = np.row_stack(
    (np.array([upper_left[0], upper_left[1]]).reshape(2, 1), [1.0]))
ic(point_2d)

point2cam_transform = intrisics_inv.dot(point_2d)

# point2cam_transform = np.row_stack(
#     (point2cam_transform[0:2], 0.0, point2cam_transform[2]))
ic(point2cam_transform)

# cam2vicon_transform = np.array(([0.555, 0.391, 0.733, 0.0], [-0.564, -0.470, 0.678, 0.0], [
#     0.610, -0.790, -0.040, 1200], [0.0, 0.0, 0.0, 1.0]))  # Z axis zeroed out
# ic(cam2vicon_transform)

# cam2vicon_transform_inv = np.linalg.pinv(cam2vicon_transform)
# point2vicon_transform = cam2vicon_transform_inv.dot(point2cam_transform)
# ic(point2vicon_transform)


cam2vicon_rot = np.array(
    ([0.555, 0.391, 0.733], [-0.564, -0.470, 0.678], [0.610, -0.790, -0.040]))

cam2vicon_trans = np.array(
    ([0.0], [0.0], [1200]))

point_in_vicon = point2cam_transform - cam2vicon_trans
ic(point_in_vicon)

point_in_vicon = (np.linalg.inv(cam2vicon_rot)).dot(point_in_vicon)
ic(point_in_vicon)
