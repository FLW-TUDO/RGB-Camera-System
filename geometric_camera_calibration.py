import json
import cv2
import numpy as np
from itertools import permutations

a = 7
b = 5
subpix_criteria = (cv2.TERM_CRITERIA_EPS+cv2.TERM_CRITERIA_MAX_ITER, 100, 1e-6)

focal_length = 17.52
image_size = (int(2592/2),int(2048/2))
sensor_size = [12.44, 9.83]

sensor_position = (0,0,0)
focal_position = (sensor_position[0]/2, sensor_position[1]/2, focal_length)

def closestDistanceBetweenLines(a0,a1,b0,b1):
    ''' Given two lines defined by numpy.array pairs (a0,a1,b0,b1)
        Return the closest points on each segment and their distance
    '''
    # Calculate denomitator
    A = a1 - a0
    B = b1 - b0
    magA = np.linalg.norm(A)
    magB = np.linalg.norm(B)
    
    _A = A / magA
    _B = B / magB
    
    cross = np.cross(_A, _B)
    denom = np.linalg.norm(cross)**2
    
    # If lines are parallel (denom=0) test if lines overlap.
    # If they don't overlap then there is a closest point solution.
    # If they do overlap, there are infinite closest positions, but there is a closest distance
    if not denom:
        d0 = np.dot(_A,(b0-a0))   
        # Segments overlap, return distance between parallel segments
        return None,None,np.linalg.norm(((d0*_A)+a0)-b0)
    
    # Lines criss-cross: Calculate the projected closest points
    t = (b0 - a0)
    detA = np.linalg.det([t, _B, cross])
    detB = np.linalg.det([t, _A, cross])

    t0 = detA/denom
    t1 = detB/denom

    pA = a0 + (_A * t0) # Projected closest point on segment A
    pB = b0 + (_B * t1) # Projected closest point on segment B
    
    return pA,pB,np.linalg.norm(pA-pB)

def create_points(img):
    img = cv2.flip(img, 0)
    img = cv2.flip(img, 1)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, corners = cv2.findChessboardCorners(
        gray, (a, b), cv2.CALIB_CB_ADAPTIVE_THRESH+cv2.CALIB_CB_FAST_CHECK+cv2.CALIB_CB_NORMALIZE_IMAGE)
    if ret == True:
        corners = cv2.cornerSubPix(
            gray, corners, (3, 3), (-1, -1), subpix_criteria)
        # img = cv2.drawChessboardCorners(img, (a, b), corners, ret)
        # cv2.imshow('img', img)
        # cv2.waitKey(0)

        return corners

def create_camera_vector(image_point):
    relativ_position = (image_point[0] / image_size[0], image_point[1] / image_size[1])
    sensor_position = (relativ_position[0] * sensor_size[0], relativ_position[1] * sensor_size[1])
    real_point = (sensor_position[0], sensor_position[1], 0)
    return np.array([element - el_focal for element, el_focal in zip(real_point, focal_position)])


with open('./images/chessboard/data.json') as f:
    data = json.load(f)

    for fName in data:
        date = data[fName]
        image_name = './images/chessboard/{}'.format(fName)


        image = cv2.imread(image_name)
        image = cv2.resize(image, image_size)
        image_points = create_points(image)
        image_points = np.flip(image_points, 0)

        idxs = [0,16,32,25,20]

        for idx1, idx2 in permutations(idxs, 2):
            vec_1 = create_camera_vector(image_points[idx1][0])
            vec_2 = create_camera_vector(image_points[idx2][0])

            real_corner_1 = np.array(date[idx1])
            real_corner_2 = np.array(date[idx2])

            real_corner_1_vec = real_corner_1 - vec_1
            real_corner_2_vec = real_corner_2 - vec_2

            res = closestDistanceBetweenLines(real_corner_1, real_corner_1_vec, real_corner_2, real_corner_2_vec)

            print(res)



