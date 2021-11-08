import cv2
from vicon_tracker import ObjectTracker
from camera import Camera
import time
import numpy as np

mtx = np.array([[857.77408004,   0.,         660.74539569],
                [0.,         857.76365601, 507.87194174],
                [0.,           0.,           1.]])
dist = np.array([[0.16106916],
                 [0.10749546],
                 [-0.09645183],
                 [0.39021927]])

marker_dict = {
    0: 3,
    6: 1,
    4: 2,
    7: 0,
    2: 2,
    1: 3,
    5: 1,
    3: 2
}
aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_250)


def undistort(img):
    _img_shape = img.shape[:2]
    DIM = _img_shape[::-1]
    map1, map2 = cv2.fisheye.initUndistortRectifyMap(
        mtx, dist, np.eye(3), mtx, DIM, cv2.CV_16SC2)
    undistorted_img = cv2.remap(
        img, map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
    return undistorted_img


def findCenter(corners):
    max_y, min_y, max_x, min_x = [-1] * 4
    for corner in corners:
        if max_x == -1 or max_x < corner[0]:
            max_x = corner[0]
        if max_y == -1 or max_y < corner[1]:
            max_y = corner[1]
        if min_x == -1 or min_x > corner[0]:
            min_x = corner[0]
        if min_y == -1 or min_y > corner[1]:
            min_y = corner[1]

    return [int((max_x + min_x) / 2), int((max_y + min_y) / 2)]


def findCorners(image):
    print("=> Processing image")
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    corners, ids, _ = cv2.aruco.detectMarkers(gray, aruco_dict)
    return corners, ids


if __name__ == "__main__":
    objects = [f'aruco_{x}' for x in range(8)]

    cam = Camera(6)
    tracker = ObjectTracker()
    tracker.connect()

    while cam.getImage() is None:
        time.sleep(0.1)

    patterns = {}

    image = cam.getImage()
    image = undistort(image)
    image = cv2.flip(image, 0)
    image = cv2.flip(image, 1)
    corners, ids = findCorners(image)
    for index in range(len(ids)):
        _id = ids[index][0]
        obj = objects[_id]
        patterns[obj] = {
            'id': _id,
            'v_pos': tracker.aquire_Object_MarkerPositions(obj)[marker_dict[_id]],
            'img_pos': findCenter(corners[index][0])
        }

    for obj in patterns:
        img_pos = patterns[obj]['img_pos']
        cv2.circle(image, tuple(img_pos), 5, (255, 0, 0), 1)

    image = cv2.resize(image, (1400, 1200))
    cv2.imshow('Camera', image)
    cv2.waitKey(0)

    print(patterns)

cam.close()
tracker.disconnect()
