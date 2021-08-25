import numpy as np
import cv2

mtx = np.array([[857.77408004,   0.,         660.74539569],
                [0.,         857.76365601, 507.87194174],
                [0.,           0.,           1.]])
dist = np.array([[0.16106916],
                 [0.10749546],
                 [-0.09645183],
                 [0.39021927]])
# patterns = {
#     'aruco_4': {'id': 4, 'v_pos': (-5280.751164704372, 4881.663640019202, -4.059037166426462), 'img_pos': [1415, 1841]},
#     'aruco_6': {'id': 6, 'v_pos': (-1857.8139093831273, 3459.625333057292, -3.07861010142938), 'img_pos': [840, 1735]},
#     'aruco_7': {'id': 7, 'v_pos': (-4268.896867529085, 2173.8924042343388, -12.597325131277131), 'img_pos': [1257, 1623]},
#     'aruco_0': {'id': 0, 'v_pos': (-1582.5014786799493, 105.93455860236305, -10.030135914830108), 'img_pos': [651, 1372]},
#     'aruco_1': {'id': 1, 'v_pos': (-6597.883936645895, -983.9212987623707, -18.5258653515707), 'img_pos': [1831, 1199]},
#     'aruco_5': {'id': 5, 'v_pos': (-3718.829720874985, -1474.972450472043, -6.944720094679851), 'img_pos': [1107, 1111]},
#     'aruco_2': {'id': 2, 'v_pos': (-7800.732450074207, 2606.153289833676, -16.394649616656416), 'img_pos': [1891, 1650]},
#     'aruco_3': {'id': 3, 'v_pos': (-1771.4829075086354, -3616.2612701203743, -19.197175478880006), 'img_pos': [433, 594]}
# }
patterns = {
    'aruco_4': {'id': 4, 'v_pos': (-5280.751164704372, 4881.663640019202, -4.059037166426462), 'img_pos': [79, 1195]},
    'aruco_6': {'id': 6, 'v_pos': (-1857.8139093831273, 3459.625333057292, -3.07861010142938), 'img_pos': [179, 1769]},
    'aruco_7': {'id': 7, 'v_pos': (-4268.896867529085, 2173.8924042343388, -12.597325131277131), 'img_pos': [309, 757]},
    'aruco_0': {'id': 0, 'v_pos': (-1582.5014786799493, 105.93455860236305, -10.030135914830108), 'img_pos': [545, 1959]},
    'aruco_1': {'id': 1, 'v_pos': (-6597.883936645895, -983.9212987623707, -18.5258653515707), 'img_pos': [719, 781]},
    'aruco_5': {'id': 5, 'v_pos': (-3718.829720874985, -1474.972450472043, -6.944720094679851), 'img_pos': [801, 1503]},
    'aruco_2': {'id': 2, 'v_pos': (-7800.732450074207, 2606.153289833676, -16.394649616656416), 'img_pos': [397, 703]},
    'aruco_3': {'id': 3, 'v_pos': (-1771.4829075086354, -3616.2612701203743, -19.197175478880006), 'img_pos': [1317, 2173]}
}


def undistort(img):
    _img_shape = img.shape[:2]
    DIM = _img_shape[::-1]
    map1, map2 = cv2.fisheye.initUndistortRectifyMap(
        mtx, dist, np.eye(3), mtx, DIM, cv2.CV_16SC2)
    undistorted_img = cv2.remap(
        img, map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
    return undistorted_img


if __name__ == "__main__":
    for obj in patterns:
        x, y, z = patterns[obj]['v_pos']
        patterns[obj]['v_pos'] = (x + 8000, y+4000, z+100)

    img_points = []
    obj_points = []
    for obj in patterns:
        img_points.append(patterns[obj]['img_pos'])
        obj_points.append(patterns[obj]['v_pos'])

    img_points = np.array([img_points], dtype=np.float)
    obj_points = np.array([obj_points], dtype=np.float)

    ret, rvecs, tvecs = cv2.solvePnP(
        obj_points, img_points, mtx, dist)

    print(rvecs)
    x, y, z = tvecs
    print([x - 8000, y-4000, z-100])
