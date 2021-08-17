from camera import Camera
from glob import glob
from itertools import product
from vicon_tracker import ObjectTracker
import numpy as np
import os
import csv
import sys
import cv2
from multiprocessing import Pool
from time import time
from copy import deepcopy


class Processor():
    def __init__(self, camera_ids, objects):
        self.camera_ids = camera_ids
        self.objects = objects

        self.tracker = ObjectTracker()
        self.tracker.connect()

    def getIndex(self, cameras):
        index = 0
        camera = cameras[0]
        if os.path.exists(os.path.join('images', f'camera_{camera.id}')):
            files = glob(os.path.join('images', f'camera_{camera.id}', '*'))
            for fname in files:
                findex = int(fname.split('.')[0].split('_')[-1])
                index = findex + 1 if findex >= index else index
        return index

    def createFolder(self, cameras):
        for camera in cameras:
            if not os.path.exists(os.path.join('images', f'camera_{camera.id}')):
                os.makedirs(os.path.join('images', f'camera_{camera.id}'))

    def aquire_object_positions(self, image_index):
        with open('data.csv', 'a') as f:
            writer = csv.writer(f)
            for object_id in self.objects:
                positions = self.tracker.aquire_Object_Trans(
                    object_id)
                rotation = self.tracker.aquire_Object_RotQuaternion(object_id)
                writer.writerow(
                    [object_id, f'image_{image_index}', positions, rotation])

    # retrieves image from camera and preprocesses image to store it

    def getImage(self, camera, index):
        res = camera.saveImage(index)
        return res

    def stop(self):
        self.running = False

    def record(self):
        self.running = True

        cameras = []
        for cam_id in self.camera_ids:
            cameras.append(Camera(cam_id, size_factor=4))
            print('Started Camera {}'.format(cam_id))

        self.createFolder(cameras)
        image_index = self.getIndex(cameras)

        print('Recording Cameras {}. Press q to exit.'.format(
            [i for i in range(len(cameras))]))

        while self.running:
            time_start = time()
            for camera in cameras:
                _ = self.getImage(camera, image_index)

            self.aquire_object_positions(image_index)
            image_index += 1

            # Displays FPS
            sys.stdout.write('\rFramerates: {}; Recorded fps: {}'.format(
                [round(camera.fps, 2) for camera in cameras], 1/(time()-time_start)))
            sys.stdout.flush()

            if cv2.waitKey(100) == ord('q'):
                break


if __name__ == "__main__":
    # the selected cameras out of [0, 1, 2, 3, 4, 5, 6, 7]
    camera_ids = [0, 1, 2, 3, 4, 5, 6]  # 7
    object_ids = ['KLT_35_neu']

    processor = Processor(camera_ids, object_ids)
    processor.record()
