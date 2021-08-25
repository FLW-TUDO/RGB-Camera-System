import numpy as np
import cv2
from numpy.core.fromnumeric import shape
from icecream import ic

# mtx = np.array([[857.77408004,   0.,         660.74539569],
#                 [0.,         857.76365601, 507.87194174],
#                 [0.,           0.,           1.]])
# dist = np.array([[0.16106916],
#                  [0.10749546],
#                  [-0.09645183],
#                  [0.39021927]])

# mtx = np.array([[2.82851400e+03, 0.0, 1.79007186e+03],
#                 [0.0, 2.83037561e+03, 1.32161499e+03],
#                 [0.0, 0.0, 1.0]])  # phone_cam
# # dist = np.array([[0.0785989,
# #                   0.03136068,
# #                   -0.01178551,
# #                   -0.00393113,
# #                   -0.22737146]]) #phone_cam
# dist = np.zeros((4, 1))

# mtx = np.array([[2.82851400e+03, 0.0, 1.79007186e+03],
#                 [0.0, 2.83037561e+03, 1.32161499e+03],
#                 [0.0, 0.0, 1.0]])
# dist = np.array([[0.07859893,  0.03136068, - 0.01178551, - 0.00393113, - 0.22737146]])
# dist = np.array([[0.07859893,  0.03136068, - 0.01178551, - 0.00393113]])

mtx = np.array([[1.83212000e+03, 0.0, 1.30771040e+03],
                [0.0, 1.82888459e+03, 1.03749179e+03],
                [0.0, 0.0, 1.0]])
dist = np.array([[0.00735673],
                 [1.51828844],
                 [-4.9074145],
                 [6.63861832]])

# patterns = {
#     'aruco_4': {'id': 4, 'v_pos': (), 'img_pos': [1415, 1841]},
#     'aruco_6': {'id': 6, 'v_pos': (-1857.8139093831273, 3459.625333057292, -3.07861010142938), 'img_pos': [840, 1735]},
#     'aruco_7': {'id': 7, 'v_pos': (-4268.896867529085, 2173.8924042343388, -12.597325131277131), 'img_pos': [1257, 1623]},
#     'aruco_0': {'id': 0, 'v_pos': (-1582.5014786799493, 105.93455860236305, -10.030135914830108), 'img_pos': [651, 1372]},
#     'aruco_1': {'id': 1, 'v_pos': (-6597.883936645895, -983.9212987623707, -18.5258653515707), 'img_pos': [1831, 1199]},
#     'aruco_5': {'id': 5, 'v_pos': (-3718.829720874985, -1474.972450472043, -6.944720094679851), 'img_pos': [1107, 1111]},
#     'aruco_2': {'id': 2, 'v_pos': (-7800.732450074207, 2606.153289833676, -16.394649616656416), 'img_pos': [1891, 1650]},
#     'aruco_3': {'id': 3, 'v_pos': (-1771.4829075086354, -3616.2612701203743, -19.197175478880006), 'img_pos': [433, 594]}
# }
# patterns = {
#     'aruco_4': {'id': 4, 'v_pos': (-5280.751164704372, 4881.663640019202, -4.059037166426462), 'img_pos': [79, 1195]},
#     'aruco_6': {'id': 6, 'v_pos': (-1857.8139093831273, 3459.625333057292, -3.07861010142938), 'img_pos': [179, 1769]},
#     'aruco_7': {'id': 7, 'v_pos': (-4268.896867529085, 2173.8924042343388, -12.597325131277131), 'img_pos': [309, 757]},
#     'aruco_0': {'id': 0, 'v_pos': (-1582.5014786799493, 105.93455860236305, -10.030135914830108), 'img_pos': [545, 1959]},
#     'aruco_1': {'id': 1, 'v_pos': (-6597.883936645895, -983.9212987623707, -18.5258653515707), 'img_pos': [719, 781]},
#     'aruco_5': {'id': 5, 'v_pos': (-3718.829720874985, -1474.972450472043, -6.944720094679851), 'img_pos': [801, 1503]},
#     'aruco_2': {'id': 2, 'v_pos': (-7800.732450074207, 2606.153289833676, -16.394649616656416), 'img_pos': [397, 703]},
#     'aruco_3': {'id': 3, 'v_pos': (-1771.4829075086354, -3616.2612701203743, -19.197175478880006), 'img_pos': [1317, 2173]}
# }

# patterns = {
#     1: {'id': 1, 'v_pos': (-1344, 720, 5), 'img_pos': [1029, 874.5]},
#     2: {'id': 2, 'v_pos': (-1862, 1340, 405), 'img_pos': [1126, 578]},
#     3: {'id': 3, 'v_pos': (-2943, 1272, 375), 'img_pos': [1023, 456]},
#     4: {'id': 4, 'v_pos': (-3239, 1293, 223), 'img_pos': [992.5, 471.5]},
#     5: {'id': 5, 'v_pos': (-2325, 47, 84), 'img_pos': [679, 609.5]},
#     6: {'id': 6, 'v_pos': (-2988, 314, 161), 'img_pos': [750, 506]},
#     7: {'id': 7, 'v_pos': (-3760, 381, 22), 'img_pos': [747.5, 476]},
#     8: {'id': 8, 'v_pos': (-3817, 261, 603), 'img_pos': [723.5, 344]},
#     9: {'id': 9, 'v_pos': (-4709, 1167, 438), 'img_pos': [878, 349]},
#     10: {'id': 10, 'v_pos': (-4709, 1196, 1007), 'img_pos': [891.5, 241.5]},
#     11: {'id': 11, 'v_pos': (-1434, -587, 4), 'img_pos': [380.5, 835.5]},
#     12: {'id': 12, 'v_pos': (-2630, -555, 316), 'img_pos': [489.5, 498.5]},
#     13: {'id': 13, 'v_pos': (-4674, -177, 404), 'img_pos': [629.5, 353.5]},
#     14: {'id': 14, 'v_pos': (-2698, -1336, 9), 'img_pos': [280.5, 573]},
#     15: {'id': 15, 'v_pos': (-3411, -972, 417), 'img_pos': [422.5, 408.5]},
#     16: {'id': 16, 'v_pos': (-3626, -1075, 428), 'img_pos': [412, 394]},
#     17: {'id': 17, 'v_pos': (-5038, -1548, 386), 'img_pos': [412, 339.5]},
#     18: {'id': 18, 'v_pos': (-5327, -1301, 1005), 'img_pos': [445.5, 235.5]},
#     19: {'id': 19, 'v_pos': (-3391, -1812, 408), 'img_pos': [226.5, 414]},
#     20: {'id': 20, 'v_pos': (-4463, -2082, 313), 'img_pos': [275, 382.5]},
# }

# patterns = {
#     1: {'id': 1, 'v_pos': (1301, -666.7, 6.1), 'img_pos': [3262.5, 2412]},
#     2: {'id': 2, 'v_pos': (1458, 305.2, 4.73), 'img_pos': [1530, 2078.5]},
#     3: {'id': 3, 'v_pos': (2050.9, -907.9, 8), 'img_pos': [3250, 1615]},
#     4: {'id': 4, 'v_pos': (2963.3, -929.9, 313.9), 'img_pos': [3033.5, 818]},
#     5: {'id': 5, 'v_pos': (2019, -249.1, 307.3), 'img_pos': [2405, 1255]},
#     6: {'id': 6, 'v_pos': (2513.6, 709.2, 222.8), 'img_pos': [1287.5, 1039]},
#     7: {'id': 7, 'v_pos': (1627.6, 1145.9, 105.9), 'img_pos': [326, 1713]},
# }

patterns = {
    1: {'id': 1, 'v_pos': (785.7, 383, 91.5), 'img_pos': [2138, 2176]},
    2: {'id': 2, 'v_pos': (1255.1, 774.1, 206.7), 'img_pos': [2060.5, 946.5]},
    3: {'id': 3, 'v_pos': (1073.5, 1376.1, 0), 'img_pos': [930.5, 1045]},
    4: {'id': 4, 'v_pos': (711.4, 1262.6, 0), 'img_pos': [488.5, 1451]}
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
    img = cv2.imread('./images/cam_img_trial_1.png')
    # img = cv2.flip(img, 0)
    # img = cv2.flip(img, 1)
    # img = cv2.imread('./images/intrinsics/2.png')
    img = undistort(img)
    img = cv2.resize(img, (int(2592 / 2), int(2048 / 2)))
    cv2.imshow('Camera', img)
    key = cv2.waitKey(0)
    if key == 113:  # q
        cv2.destroyAllWindows()

    # filename = './images/pictureNEW_undist.png'
    # cv2.imwrite(filename, undist_img)

    for obj in patterns:
        x, y, z = patterns[obj]['v_pos']
        # patterns[obj]['v_pos'] = (x + 6000, y+3000, z)

    img_points = []
    obj_points = []
    for obj in patterns:
        img_points.append(patterns[obj]['img_pos'])
        obj_points.append(patterns[obj]['v_pos'])

    img_points = np.array([img_points], dtype=np.float)
    obj_points = np.array([obj_points], dtype=np.float)

    ret, rvecs, tvecs = cv2.solvePnP(
        obj_points, img_points, mtx, dist, flags=1)  # EPNP

    ret, rvecs, tvecs = cv2.solvePnP(
        obj_points, img_points, mtx, dist, rvec=rvecs, tvec=tvecs, flags=0)  # Iterative

    # rotM = cv2.Rodrigues(rvecs)[0]
    # cameraPosition = -np.matrix(rotM).T * np.matrix(tvecs)
    # ic(cameraPosition)
    # ret = cv2.solvePnPRansac(
    #     obj_points, img_points, mtx, dist)

    ic(rvecs)
    x, y, z = tvecs
    ic(tvecs)
    # print([x - 6000, y-3000, z])

    tot_error = 0
    total_points = 0
    for i in range(len(obj_points[0])):
        objp = np.array([obj_points[0][i]])
        ic(objp)
        reprojected_points, _ = cv2.projectPoints(
            objp, rvecs, tvecs, mtx, dist)
        reprojected_points = reprojected_points.reshape(-1, 2)
        ic(reprojected_points)
        ic(img_points[0][i])
        tot_error += np.sum(np.sqrt((img_points[0][i]-reprojected_points)**2))
        total_points += len(objp)
        ic(tot_error / total_points)

    mean_error = tot_error/total_points
    print("Mean reprojection error: {}".format(mean_error))
