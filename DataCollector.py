import copy
import time

from Camera.CVBCamera import Camera
from PyVicon.vicon_tracker import ObjectTracker
from threading import Thread
import os
import csv
import cv2
from datetime import datetime
from calibration.obj_gt_pose import get_obj_gt_transform, get_obj2vicon_transform, get_obj2vicon_transform_sync, get_new_frame
import numpy as np

obj_ids = {
    "KLT_32_neu": {'object_id': 1, 'active': True},
    "KLT_8_neu": {'object_id': 1, 'active': True},
    "rb1_base_c": {'object_id': 2, 'active': True},
    "AS_1_neu": {'object_id': 3, 'active': True},
    "AS_2_neu": {'object_id': 3, 'active': True},
    "pallet_1": {'object_id': 4, 'active': True},
    "pallet_2": {'object_id': 4, 'active': True},
    "box_1": {'object_id': 5, 'active': True},
    "box_2": {'object_id': 5, 'active': True},
}
cameras = [0, 1, 2, 3, 4, 5, 6, 7]  # 0,1,2,3,4,5,6,7
path = "recordings"


class ViconProvider(Thread):
    """
    Vicon provider will retrieve all objects from the vicon system and store them in memory.
    This helps with quicker access and will reduce the queries to the vicon system over the network.
    """
    def __init__(self):
        Thread.__init__(self)
        self.running = True
        self.obj_gt_transf = {obj: {"obj2vicon_trans": None, "obj2vicon_rot_mat": None} for obj in list(obj_ids.keys())}
        for obj in list(obj_ids.keys()):
            obj2vicon_trans, obj2vicon_rot_mat = get_obj2vicon_transform(obj)
            self.obj_gt_transf[obj]["obj2vicon_trans"] = obj2vicon_trans
            self.obj_gt_transf[obj]["obj2vicon_rot_mat"] = obj2vicon_rot_mat
        self.start()

    def stop(self):
        self.running = False

    def run(self):
        while self.running:
            get_new_frame()
            for obj in list(obj_ids.keys()):
                obj2vicon_trans, obj2vicon_rot_mat = get_obj2vicon_transform_sync(obj)
                self.obj_gt_transf[obj]["obj2vicon_trans"] = obj2vicon_trans
                self.obj_gt_transf[obj]["obj2vicon_rot_mat"] = obj2vicon_rot_mat

    def object_gt_transform(self, objId):
        return self.obj_gt_transf[objId]["obj2vicon_trans"], self.obj_gt_transf[objId]["obj2vicon_rot_mat"]


class Processor(Thread):
    def __init__(self, index, provider=None):
        Thread.__init__(self)
        self.name = index
        self.imageIndex = 0
        self.provider = provider
        self.running = True

        """
        creates a path for each object with the current recording 
        time and the id of the camera itself
        Like:
        ./recordings/11_11_11 08_11_2021/camera_0/images
        """
        now = datetime.now().strftime(
            "%H_%M %d_%m_%Y")  # adding seconds results in multiple directories creation
        self.folder_path = os.path.join(path, now)

        self.camera = Camera(index)
        self.image = None
        self.lock = False
        self.row_data = []
        self.start()

    def run(self):
        """
            Main thread for each camera
            Saves the images to drive
            Finally stores all recorded data in a csv
        """
        while self.running:
            if not self.lock:
                self.lock = True
                self.save()

        self.writeCSV()

        print(f'Camera {self.name} stopped!')

    def save(self):
        """
        Gets poses for all objects of interest that could (possibly) be within the camera view.
        The annotated output would contain as many images with the same ID (and different obj id) as there are objects
        of interest. Images should be filtered at a later stage.

        Writes data to an intermediary dict

        data: {
            "image": numpy.array (RGB image)
            "object_0001": dict | object translation and rotation
            }
        """
        data = {"image": self.camera.getImage(rotate=True)}
        for obj in list(obj_ids.keys()):
            if not obj_ids[obj]['active']:
                continue
            if self.provider is not None:
                obj_trans, obj_rot = self.provider.object_gt_transform(obj)
            else:
                obj_trans, obj_rot = get_obj_gt_transform(self.name, obj)
            pose = {'obj_trans': obj_trans, 'obj_rot': obj_rot}
            pose_copy = copy.deepcopy(pose)
            data[obj] = pose_copy

        self.writeData(data)

        self.imageIndex += 1
        data.clear()

    def release(self):
        self.lock = False

    def stop(self):
        self.running = False

    def writeCSV(self):
        cam_path = os.path.join(self.folder_path, f'camera_{self.name}')
        with open(os.path.join(cam_path, "data.csv"), "a", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['ObjectID', 'ImageName', 'camToObjTrans', 'camToObjRot', 'symmetry'])
            for index, row in enumerate(self.row_data):
                writer.writerow(row)

    def writeData(self, data):
        """
        Writes as csv line and an image file for each object present in the scene
        """
        cam_path = os.path.join(self.folder_path, f'camera_{self.name}')
        images_path = os.path.join(cam_path, 'images')
        if not os.path.exists(images_path):
            os.makedirs(images_path)
        for obj in list(obj_ids.keys()):
            if not obj_ids[obj]['active']:
                continue
            img_path = os.path.join(
                images_path, str(self.imageIndex) + '.png')
            # print(f'Obj ID: {obj}, Img path: {img_path}, Trans: {data[obj]["obj_trans"]}, Rot: {data[obj]["obj_rot"]}')
            self.row_data.append(
                [obj_ids[obj]['object_id'], img_path, data[obj]['obj_trans'], data[obj]['obj_rot']])

        img_path = os.path.join(
            images_path, str(self.imageIndex) + '.png')
        cv2.imwrite(img_path, data["image"])


if __name__ == "__main__":
    image = cv2.imread('recordings/11_28 22_02_2022/camera_2/images/0.png')
    provider = ViconProvider()
    processors = [Processor(index, provider) for index in cameras]
    print(f"Recording started: {datetime.now().strftime('%H_%M')}")
    start_time = time.time()
    while True:
        if np.all([processor.lock for processor in processors]):
            cv2.imshow('Recording', image)
            key = cv2.waitKey(100)
            if key == 32:
                cv2.destroyAllWindows()
                break
            for processor in processors:
                processor.release()

    for processor in processors:
        processor.stop()
        processor.join()
    provider.stop()

    print(f"Recording ended: {datetime.now().strftime('%H_%M')}; Total Images taken: {np.sum([processor.imageIndex for processor in processors])} FPS: {np.sum([processor.imageIndex for processor in processors]) / (time.time() - start_time)}")
