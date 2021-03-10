from threading import Thread
import numpy as np
import os
import cv2
import cvb
from time import time

from vicon_tracker import ObjectTracker

# Camera class for accessing the cvb cameras
# Calibration functions are using cv2 function to calibrate the camera
# Vicon Magic Wand v2 is used to capture object points

DEBUG = True


class Camera(Thread):
    def __init__(self, id):
        Thread.__init__(self)
        self.id = id
        self.device = cvb.DeviceFactory.open(os.path.join(
            cvb.install_path(), "drivers", "GenICam.vin"), port=self.id)

        self.tracker = ObjectTracker()

        self.image = None
        self.mask = None

        self.rotate_vertical = True
        self.rotate_horizontal = True
        factor = 4
        self.resolution = (int(2592 / factor), int(2048 / factor))

        self.lastframe = time()
        self.fps = 0

        self.start()

    def run(self):
        self.running = True
        self.openStream()

        while(self.running):
            image, status = self.stream.wait()
            if status == cvb.WaitStatus.Ok:
                self.image = cvb.as_array(image)
                self.fps = 1/(time() - self.lastframe)
                self.lastframe = time()

    def openStream(self):
        self.stream = self.device.stream
        self.stream.start()

    def closeStream(self):
        self.running = False
        self.stream.abort()

    def close(self):
        self.running = False

    def loadMask(self):
        try:
            self.mask = np.load('camera%s_mask.npy' % self.camera.id)
            print("Loaded camera %s mask" % self.camera.id)
        except:
            self.mask = self.calculate_mask()

    # takes a fixed quantity of images and calculates a mask
    # unchanging image points are considered background
    def calculate_mask(self, kernelsize=11, threshold=100):
        print("Started camera %s masking" % self.id)
        kernel = np.ones((kernelsize, kernelsize), np.uint8)
        mask = np.zeros((2048, 2592))
        masking_count = 0
        while masking_count < 200:
            img = self.image
            gray_frame = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            ret, binary_frame = cv2.threshold(
                gray_frame, threshold, 255, cv2.THRESH_BINARY)
            if ret:
                mask = mask + binary_frame
            masking_count += 1

        mask = mask/np.max(mask)
        mask = cv2.dilate(mask, kernel)
        negativ_mask = np.ones_like(mask)
        mask = negativ_mask-mask
        mask = np.uint8(mask)
        np.save('camera%s_mask.npy' % self.id, mask)
        print("Finished camera %s masking with %s iterations" %
              (self.id, masking_count))
        return mask

    # extracts all centriods from an image
    # since the Vicon Magic Wand v2 has 5 bright LEDs the brightest spots of an image are chosen
    def calibration(self, image):
        kernel = np.ones((3, 3), np.uint8)
        centroids_update = np.zeros((5, 2), dtype=np.uint8)
        gray_frame = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # removes noise/background from the image and leaves the LEDs as is
        ret, binary_frame = cv2.threshold(
            gray_frame, 240, 255, cv2.THRESH_BINARY)
        if ret:
            # connect subpoints to one region
            binary_frame = cv2.erode(binary_frame*self.mask, kernel)
            binary_frame = cv2.dilate(binary_frame, kernel)
            _, _, stats, centroids = cv2.connectedComponentsWithStats(
                binary_frame, connectivity=8)
            ret, centroids_update = self.findCalibrationPattern(
                stats, centroids, 5)
            return ret, centroids_update

    # extracts the calibration pattern from a single image
    # Vicon Magic Wand v2 is used as calibration pattern
    # this function connects the centriods of the image to their semantic counter parts of the Magic Wand
    def findCalibrationPattern(self, stats, centroids, number_of_calibrationpoints):
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
                temp_area = self.calcAreaTriangle(marker[0], marker[1], cen)
                if temp_area > area:
                    temp_index = i
                    area = temp_area
                    marker[2] = cen
            temp_centroids = np.delete(temp_centroids, temp_index, 0)

            # find marker in the middle upper side of the wand
            cen0 = temp_centroids[0, :]
            cen1 = temp_centroids[1, :]
            area = self.calcAreaTriangle(marker[0], marker[1], cen0)
            marker_index = np.array([0, 1])
            marker_index_0 = 2
            index_temp_centroids = 0
            if self.calcAreaTriangle(marker[1], marker[2], cen0) < area:
                marker_index = np.array([1, 2])
                marker_index_0 = 0
                area = self.calcAreaTriangle(marker[1], marker[2], cen0)
            if self.calcAreaTriangle(marker[2], marker[0], cen0) < area:
                marker_index = np.array([2, 0])
                marker_index_0 = 1
                area = self.calcAreaTriangle(marker[2], marker[0], cen0)
            if self.calcAreaTriangle(marker[0], marker[1], cen1) < area:
                marker_index = np.array([0, 1])
                marker_index_0 = 2
                area = self.calcAreaTriangle(marker[0], marker[1], cen1)
                index_temp_centroids = 1
            if self.calcAreaTriangle(marker[1], marker[2], cen1) < area:
                marker_index = np.array([1, 2])
                marker_index_0 = 0
                area = self.calcAreaTriangle(marker[1], marker[2], cen1)
                index_temp_centroids = 1
            if self.calcAreaTriangle(marker[2], marker[0], cen1) < area:
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

    def calcAreaTriangle(self, p1, p2, p3):
        return 0.5*abs((p2[0]-p1[0])*(p3[1]-p2[1])-(p3[0]-p2[0])*(p2[1]-p1[1]))

    # retrieves vicon data
    def getViconData(self):
        data = self.tracker.aquire_Object_MarkerPositions('ViconWand')
        x0 = np.asarray(data[4])
        x1 = np.asarray(data[0])
        x2 = np.asarray(data[2])
        x3 = np.asarray(data[3])
        x4 = np.asarray(data[1])
        return np.array([[x0, x1, x2, x3, x4]])

    # determines for each image the object and image points
    def processCalib(self, image, image_points, object_points, image_points_extrinsic, object_points_extrinsic):
        # retrieves the image points
        ret, centroid = self.calibration(image)
        if ret:
            # gets the object points through vicon
            viconpoints = self.getViconData()
            image_points.append(np.array([centroid]))
            object_points.append(np.array(viconpoints))
            image_points_extrinsic = np.vstack(
                (image_points_extrinsic, centroid))
            object_points_extrinsic = np.vstack(
                (object_points_extrinsic, viconpoints.reshape((5, 3))))
            for cen in image_points_extrinsic:
                x = cen.astype(int)[0]
                y = cen.astype(int)[1]
                image = cv2.circle(image, (x, y), 5, (255, 255, 255), -1)
        return image

    def calculateIntrinsics(self, image_points, object_points, image_points_extrinsic, object_points_extrinsic):
        np.set_printoptions(suppress=True, precision=4)

        # moves marker positions into positive values
        smallest = [0., 0., 0.]
        for item in object_points:
            for pos in item[0]:
                smallest[0] = pos[0] if pos[0] < smallest[0] else smallest[0]
                smallest[1] = pos[1] if pos[1] < smallest[1] else smallest[1]
                smallest[2] = pos[2] if pos[2] < smallest[2] else smallest[2]

        for item in object_points:
            for pos in item[0]:
                pos[0] += abs(smallest[0]) + 50
                pos[1] += abs(smallest[1]) + 50
                pos[2] += abs(smallest[2]) + 50

        print("Translation %s" % ([x + 50 for x in smallest]))

        object_points = np.array(object_points)
        image_points = np.array(image_points)

        if DEBUG:
            np.save('object_points.npy', object_points)
            np.save('image_points.npy', image_points)
            np.save('image_points_extrinsic.npy', image_points_extrinsic)
            np.save('object_points_extrinsic.npy', object_points_extrinsic)

            print('Objectpoints: ', object_points.shape)
            print('Imagepoints: ', image_points.shape)
            print('Imagepoints ext: ', image_points_extrinsic.shape)
            print('Objectpoints ext: ', object_points_extrinsic.shape)

        if len(object_points) > 0 and len(object_points) == len(image_points):

            # this is a test part replacing the intrinsic calculations
            K = np.array([[444.01212317, 0., 317.87966175],
                          [0., 442.20562833, 264.72142874],
                          [0., 0., 1.]])
            D = np.array([[0.22847352],
                          [-0.22746739],
                          [0.70298454],
                          [-0.04718649]])
            ret, _, tvec = cv2.solvePnP(
                object_points_extrinsic[1:], image_points_extrinsic[1:], K, D)
            if ret:
                print("Kamera %s:" % self.id)
                print("K:")
                print(K)
                print("D:")
                print(D)
                print("Translation:")
                print(tvec)
                return K, D, tvec
            else:
                print("Calculate extrinsics failed!")
        else:
            print("Camera %s :   " % self.id +
                  str(len(image_points)) + "__" + str(len(object_points)))
            print("List are not the same length or no points found")

    # for calibration purposes the camera switches to internal mode
    # processing the images and calculating intrinsics and extrinsics
    # without delivering a feed
    def calibrate(self):
        self.running = False

        # calibration parameters
        image_points = []
        image_points_extrinsic = np.array([0, 0])
        object_points = []
        object_points_extrinsic = np.array([0, 0, 0])

        self.tracker.connect()

        if self.mask is None:
            self.loadMask()

        print('Started calibration on camera {}.'.format(self.id))

        while True:
            image, status = self.stream.wait()
            if status == cvb.WaitStatus.Ok:
                image = cvb.as_array(image)
                image = self.processCalib(image, image_points, object_points, image_points_extrinsic,
                                          object_points_extrinsic)
                if DEBUG:
                    image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
                    image = image * self.mask
                    image = cv2.resize(image, self.resolution)
                    image = cv2.flip(image, 0)
                    image = cv2.flip(image, 1)

                    cv2.imshow('Calibration', image)
                    # press q to end the calibration recording
                    if cv2.waitKey(5) == ord('q'):
                        cv2.destroyAllWindows()
                        break

        self.closeStream()
        self.tracker.disconnect()

        print('Total number of frames recorded: {}'.format(len(object_points)))

        self.calculateIntrinsics(
            image_points, object_points, image_points_extrinsic, object_points_extrinsic)

    def getImage(self):
        return self.image
