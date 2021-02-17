import cv2
from glob import glob
import os
import numpy as np

# termination criteria
subpix_criteria = (cv2.TERM_CRITERIA_EPS+cv2.TERM_CRITERIA_MAX_ITER, 30, 1e-6)
calibration_flags = cv2.fisheye.CALIB_RECOMPUTE_EXTRINSIC + cv2.fisheye.CALIB_FIX_SKEW
    


objp = np.array([[
    [0,2,0],
    [0,1,0],
    [0,0,0],
    [1,1,0],
    [2,1,0]
]], np.float32)

def calibration(image):
    kernel = np.ones((3, 3), np.uint8)
    centroids_update = np.zeros((5, 2), dtype=np.float32)
    gray_frame = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # removes noise/background from the image and leaves the LEDs as is
    ret, binary_frame = cv2.threshold(
        gray_frame, 240, 255, cv2.THRESH_BINARY)
    if ret:
        # connect subpoints to one region
        binary_frame = cv2.dilate(binary_frame, kernel)
        _, _, stats, centroids = cv2.connectedComponentsWithStats(
            binary_frame, connectivity=8)
        ret, centroids_update = findCalibrationPattern(
            stats, centroids, 5)
        return ret, centroids_update

# extracts the calibration pattern from a single image
# Vicon Magic Wand v2 is used as calibration pattern
# this function connects the centriods of the image to their semantic counter parts of the Magic Wand
def findCalibrationPattern(stats, centroids, number_of_calibrationpoints):
    ret = False
    if np.shape(centroids)[0] > number_of_calibrationpoints:
        ret = True
        stats = stats[1:, :]  # eliminate background (first element)
        centroids = centroids[1:, :]

        # distinguish calibration marker from false detections
        median_area = np.median(stats[:, 4])
        median_x = np.median(stats[:, 0])
        median_y = np.median(stats[:, 1])
        reference_vec = [median_x, median_y, median_area]
        data_points = stats[:, (0, 1, 4)]  # 0=x 1=y 4=Area
        distance = data_points - reference_vec
        distance = distance**2
        # euclidian lenght of each point to the median
        distance = np.sqrt(distance[:, 0] + distance[:, 0]+distance[:, 0])
        distance = distance.T

        new_stats = np.zeros((np.shape(stats)[0], np.shape(stats)[1]+3))
        new_stats[:, 3:] = stats
        new_stats[:, 0] = distance
        new_stats[:, 1:3] = centroids

        # find calibration-marker order
        temp_centroids = centroids.copy()
        marker = np.zeros((5, 2))
        final_marker = np.zeros((5, 2))

        x_min = np.min(temp_centroids[:, 0])
        x_max = np.max(temp_centroids[:, 0])

        # find corners
        index_x_min = np.where(temp_centroids[:, 0] == x_min)
        index_x_min = index_x_min[0]
        marker[0] = np.array(
            [temp_centroids[index_x_min[0], 0], temp_centroids[index_x_min[0], 1]]).ravel()
        temp_centroids = np.delete(temp_centroids, index_x_min[0], 0)
        index_x_max = np.where(temp_centroids[:, 0] == x_max)
        index_x_max = index_x_max[0]
        marker[1] = np.array(
            [temp_centroids[index_x_max[0], 0], temp_centroids[index_x_max[0], 1]]).ravel()
        temp_centroids = np.delete(temp_centroids, index_x_max[0], 0)

        area = 0
        i = -1
        for cen in temp_centroids:
            i += 1
            temp_area = calcAreaTriangle(marker[0], marker[1], cen)
            if temp_area > area:
                temp_index = i
                area = temp_area
                marker[2] = cen
        temp_centroids = np.delete(temp_centroids, temp_index, 0)

        # find marker in the middle upper side of the wand
        cen0 = temp_centroids[0, :]
        cen1 = temp_centroids[1, :]
        area = calcAreaTriangle(marker[0], marker[1], cen0)
        marker_index = np.array([0, 1])
        marker_index_0 = 2
        index_temp_centroids = 0
        if calcAreaTriangle(marker[1], marker[2], cen0) < area:
            marker_index = np.array([1, 2])
            marker_index_0 = 0
            area = calcAreaTriangle(marker[1], marker[2], cen0)
        if calcAreaTriangle(marker[2], marker[0], cen0) < area:
            marker_index = np.array([2, 0])
            marker_index_0 = 1
            area = calcAreaTriangle(marker[2], marker[0], cen0)
        if calcAreaTriangle(marker[0], marker[1], cen1) < area:
            marker_index = np.array([0, 1])
            marker_index_0 = 2
            area = calcAreaTriangle(marker[0], marker[1], cen1)
            index_temp_centroids = 1
        if calcAreaTriangle(marker[1], marker[2], cen1) < area:
            marker_index = np.array([1, 2])
            marker_index_0 = 0
            area = calcAreaTriangle(marker[1], marker[2], cen1)
            index_temp_centroids = 1
        if calcAreaTriangle(marker[2], marker[0], cen1) < area:
            marker_index = np.array([2, 0])
            marker_index_0 = 1
            index_temp_centroids = 1

        final_marker[4] = marker[marker_index_0]
        if index_temp_centroids == 1:
            final_marker[1] = temp_centroids[1]
            final_marker[3] = temp_centroids[0]
        else:
            final_marker[1] = temp_centroids[0]
            final_marker[3] = temp_centroids[1]

        # get marker 0 and 2
        vec1 = final_marker[4]-final_marker[1]
        vec2 = marker[marker_index[0]]-final_marker[1]

        if np.cross(vec1, vec2) < 0:
            final_marker[2] = marker[marker_index[0]]
            final_marker[0] = marker[marker_index[1]]
        else:
            final_marker[0] = marker[marker_index[0]]
            final_marker[2] = marker[marker_index[1]]

        return ret, final_marker
    else:
        return ret, centroids

def calcAreaTriangle(p1, p2, p3):
    return 0.5*abs((p2[0]-p1[0])*(p3[1]-p2[1])-(p3[0]-p2[0])*(p2[1]-p1[1]))

def drawCircle(image, centroids):
    colors = [
        (255, 255, 255),
        (255, 255, 0),
        (255, 0, 255),
        (0, 255, 255),
        (255, 0, 0),
    ]
    for index, centroid in enumerate(centroids):
        centroid = tuple([int(x) for x in centroid])
        radius = 5
        thickness = 2
        image = cv2.circle(image, centroid, radius, colors[index], thickness)
    cv2.imshow('Image', image)
    cv2.waitKey(0)


def create_points(images):
    objpoints = []  # 3d point in real world space
    imgpoints = []  # 2d points in image plane.

    for fname in images:
        img = cv2.imread(fname)
        # img = cv2.flip(img, 1)

        ret, centroids = calibration(img)
        if ret:
            objpoints.append(objp)
            imgpoints.append(np.array([[x] for x in centroids], dtype=np.float64))
        else:
            # drawCircle(img, centroids)
            # os.remove(fname)
            continue
        
    return imgpoints, objpoints

def calculate_intrinsics(objpoints, imgpoints, _img_shape):
    N_OK = len(objpoints)
    K = np.zeros((3, 3))
    D = np.zeros((4, 1))
    rvecs = [np.zeros((1, 1, 3), dtype=np.float64) for i in range(N_OK)]
    tvecs = [np.zeros((1, 1, 3), dtype=np.float64) for i in range(N_OK)]
    rms, _, _, _, _ = \
        cv2.fisheye.calibrate(
            objpoints,
            imgpoints,
            _img_shape,
            K,
            D,
            rvecs,
            tvecs,
            calibration_flags,
            subpix_criteria
        )
    print("Found " + str(N_OK) + " valid images for calibration")
    print("DIM=" + str(_img_shape[::-1]))
    print("RMS: ", rms)
    print("K=np.array(" + str(K.tolist()) + ")")
    print("D=np.array(" + str(D.tolist()) + ")")

    return K, D, rvecs, tvecs

# display on image undistorted to check if the calibration worked
def display_undistored(image, K, D):
    img = cv2.imread(image)
    _img_shape = img.shape[:2]
    DIM = _img_shape[::-1]
    map1, map2 = cv2.fisheye.initUndistortRectifyMap(
        K, D, np.eye(3), K, DIM, cv2.CV_16SC2)
    undistorted_img = cv2.remap(
        img, map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
    cv2.imshow("undistorted", undistorted_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


# calculate calibration error
def calculate_mean_error(objpoints, imgpoints, rvecs, tvecs, K, D):
    mean_error = 0
    for i in range(len(objpoints)):
        imgpoints2, _ = cv2.projectPoints(
            objpoints[i][0], rvecs[i], tvecs[i], K, D)
        imgpoints2 = np.array(imgpoints2, dtype=np.float64)
        error = cv2.norm(imgpoints[i], imgpoints2, cv2.NORM_L2)/len(imgpoints2)
        mean_error += error

    print("total error: ", mean_error/len(objpoints))

# simple script to delete not usable images
if __name__ == "__main__":
    images = glob('./images/magic_wand/*.jpg')[4:20]
    
    imgpoints, objpoints = create_points(images)
    _img_shape = cv2.cvtColor(cv2.imread(images[0]), cv2.COLOR_BGR2GRAY).shape[::-1]
    K, D, rvecs, tvecs = calculate_intrinsics(objpoints, imgpoints, _img_shape)

    image = './images/chessboard/1.jpg'

    display_undistored(image, K, D)
    calculate_mean_error(objpoints, imgpoints, rvecs, tvecs, K, D)

    

    

    
