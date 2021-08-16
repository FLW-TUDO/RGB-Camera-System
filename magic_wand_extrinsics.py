from _typeshed import NoneType
from camera import Camera
from vicon_tracker import ObjectTracker
import numpy as np
import cv2

cam_id = 2
wand_name = "MagicWand"


def extractCalibrationPattern(image, mask=None):
    kernel = np.ones((3, 3), np.uint8)
    centroids_update = np.zeros((5, 2), dtype=np.uint8)

    gray_frame = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    ret, binary_frame = cv2.threshold(gray_frame, 240, 255, cv2.THRESH_BINARY)
    if ret:
        # connect subpoints to one region
        if mask is not None:
            binary_frame = cv2.erode(binary_frame * mask, kernel)
        else:
            binary_frame = cv2.erode(binary_frame, kernel)
        binary_frame = cv2.dilate(binary_frame, kernel)
        _, _, stats, centroids = cv2.connectedComponentsWithStats(
            binary_frame, connectivity=8
        )
        ret, centroids_update = findCalibrationPattern(stats, centroids, 5)
    return ret, centroids_update


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
        distance = distance ** 2
        distance = np.sqrt(
            distance[:, 0] + distance[:, 0] + distance[:, 0]
        )  # euclidian lenght of each point to the median
        distance = distance.T

        new_stats = np.zeros((np.shape(stats)[0], np.shape(stats)[1] + 3))
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
            [temp_centroids[index_x_min[0], 0], temp_centroids[index_x_min[0], 1]]
        ).ravel()
        temp_centroids = np.delete(temp_centroids, index_x_min[0], 0)
        index_x_max = np.where(temp_centroids[:, 0] == x_max)
        index_x_max = index_x_max[0]
        marker[1] = np.array(
            [temp_centroids[index_x_max[0], 0], temp_centroids[index_x_max[0], 1]]
        ).ravel()
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
        vec1 = final_marker[4] - final_marker[1]
        vec2 = marker[marker_index[0]] - final_marker[1]

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
    return 0.5 * abs(
        (p2[0] - p1[0]) * (p3[1] - p2[1]) - (p3[0] - p2[0]) * (p2[1] - p1[1])
    )


if __name__ == "__main__":
    cam = Camera(cam_id)
    tracker = ObjectTracker()
    tracker.connect()

    object_points = []
    image_points = []

    while True:
        key = cv2.waitKey(5)
        if key == 113:
            break
        if key == 32:
            image = cam.getImage()

            wand_positions = tracker.aquire_Object_MarkerPositions(wand_name)

            image = cv2.flip(image, 0)
            image = cv2.flip(image, 1)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            ret, image_positions = extractCalibrationPattern(image)
            if ret:
                image_points.append(image_positions)
                object_points.append(wand_positions)

    print(f"Image points {image_points}")
    print(f"Object points {object_points}")
