import copy
import time

from Camera.CVBCamera import Camera
from threading import Thread
import os
import csv
import cv2
from datetime import datetime
from calibration.obj_gt_pose import get_obj_gt_transform, get_obj2vicon_transform, get_obj2vicon_transform_sync, get_new_frame
import numpy as np

obj_ids = {
    "KLT_1_neu": {'object_id': 1, 'active': True},
    "KLT_2_neu": {'object_id': 1, 'active': True},
    "KLT_4_neu": {'object_id': 1, 'active': True},
    "KLT_7_neu": {'object_id': 1, 'active': True},
    "KLT_8_neu": {'object_id': 1, 'active': False},
    "KLT_9_neu": {'object_id': 1, 'active': True},
    "KLT_13_neu": {'object_id': 1, 'active': True},
    "KLT_15_neu": {'object_id': 1, 'active': True},
    "KLT_17_neu": {'object_id': 1, 'active': True},
    "KLT_18_neu": {'object_id': 1, 'active': True},
    "KLT_19_neu": {'object_id': 1, 'active': True},
    "KLT_20_neu": {'object_id': 1, 'active': True},
    "KLT_21_neu": {'object_id': 1, 'active': True},
    "KLT_22_neu": {'object_id': 1, 'active': True},
    "KLT_24_neu": {'object_id': 1, 'active': True},
    "KLT_25_neu": {'object_id': 1, 'active': True},
    "KLT_26_neu": {'object_id': 1, 'active': True},
    "KLT_27_neu": {'object_id': 1, 'active': True},
    "KLT_29_neu": {'object_id': 1, 'active': True},
    "KLT_30_neu": {'object_id': 1, 'active': True},
    "KLT_31_neu": {'object_id': 1, 'active': True},
    "KLT_32_neu": {'object_id': 1, 'active': False},
    "KLT_35_neu": {'object_id': 1, 'active': True},
    "KLT_37_neu": {'object_id': 1, 'active': True},
    "KLT_38_neu": {'object_id': 1, 'active': True},
    "KLT_39_neu": {'object_id': 1, 'active': True},
    "rb1_base_c": {'object_id': 2, 'active': False},
    "AS_1_neu": {'object_id': 3, 'active': False},
    "AS_2_neu": {'object_id': 3, 'active': False},
    "pallet_1": {'object_id': 4, 'active': False},
    "pallet_2": {'object_id': 4, 'active': False},
    "pallet_3": {'object_id': 4, 'active': True},
    "pallet_4": {'object_id': 4, 'active': True},
    "pallet_5": {'object_id': 4, 'active': True},
    "pallet_6": {'object_id': 4, 'active': True},
    "box_1": {'object_id': 5, 'active': True},
    "box_2": {'object_id': 5, 'active': True},
    "box_3": {'object_id': 5, 'active': True},
    "box_4": {'object_id': 5, 'active': True},
    "box_5": {'object_id': 5, 'active': True},
    "box_6": {'object_id': 5, 'active': True},
    "box_7": {'object_id': 5, 'active': True},
    "box_8": {'object_id': 5, 'active': True},
    "box_9": {'object_id': 5, 'active': True},
    "moroKopf_1": {'object_id': 6, 'active': True},
    "moroKopf_2": {'object_id': 6, 'active': True},
    "forklift": {'object_id': 7, 'active': True},
}
cameras = [2, 3, 4, 5]  # 0,1,2,3,4,5,6,7
path = "recordings"


class ViconProvider(Thread):
    """
    Vicon provider will retrieve all objects from the vicon system and store them in memory.
    This helps with quicker access and will reduce the queries to the vicon system over the network.
    """

    def __init__(self):
        Thread.__init__(self)
        self.running = True
        self.obj_gt_transf = {obj: {"obj2vicon_trans": None,
                                    "obj2vicon_rot_mat": None} for obj in list(obj_ids.keys())}
        for obj in list(obj_ids.keys()):
            if obj_ids[obj]["active"]:
                obj2vicon_trans, obj2vicon_rot_mat = get_obj2vicon_transform(
                    obj)
                self.obj_gt_transf[obj]["obj2vicon_trans"] = obj2vicon_trans
                self.obj_gt_transf[obj]["obj2vicon_rot_mat"] = obj2vicon_rot_mat
        self.start()

    def stop(self):
        self.running = False

    def run(self):
        while self.running:
            get_new_frame()
            for obj in list(obj_ids.keys()):
                if obj_ids[obj]["active"]:
                    obj2vicon_trans, obj2vicon_rot_mat = get_obj2vicon_transform_sync(
                        obj)
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
        self.record_objects = False

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
        Gets poses for all objects of interest that could (possibly) be within the camera view.
        The annotated output would contain as many images with the same ID (and different obj id) as there are objects
        of interest. Images should be filtered at a later stage.

        Writes data to an intermediary dict

        data: {
            "image": numpy.array (RGB image)
            "object_0001": dict | object translation and rotation
            }
        """
        csv_data = []
        while self.running:
            image = self.camera.getImage()

            data = {}
            if not self.record_objects:
                data["timestamp"] = time.time()  # record time in ms
            else:
                for obj in list(obj_ids.keys()):
                    obj_trans = get_obj_gt_transform(self.name, obj)[0]
                    obj_rot = get_obj_gt_transform(self.name, obj)[1]
                    pose = {'obj_trans': obj_trans, 'obj_rot': obj_rot}
                    pose_copy = copy.deepcopy(pose)
                    data[obj] = pose_copy
                    # print(data[obj])

            img_path = self.write_image(image)
            data["img_path"] = img_path
            csv_data.append(data)
            self.imageIndex += 1

        self.writeData(csv_data)
        csv_data.clear()

        print(f'Camera {self.name} stopped!')

    def stop(self):
        self.running = False

    def write_image(self, image):
        cam_path = os.path.join(self.folder_path, f'camera_{self.name}')
        images_path = os.path.join(cam_path, 'images')
        if not os.path.exists(images_path):
            os.makedirs(images_path)
        img_path = os.path.join(images_path, str(self.imageIndex) + '.bmp')
        cv2.imwrite(img_path, image)
        return img_path

    def writeData(self, csv_data):
        """
        Writes as csv line and an image file for each object present in the scene
        """
        cam_path = os.path.join(self.folder_path, f'camera_{self.name}')
        with open(os.path.join(cam_path, "data.csv"), "a", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(
                ['ObjectID', 'ImageName', 'camToObjTrans', 'camToObjRot', 'symmetry'])
            for data in csv_data:
                if not self.record_objects:
                    writer.writerow([data["img_path"], data["timestamp"]])
                else:
                    for obj in list(obj_ids.keys()):
                        # print(f'Obj ID: {obj}, Img path: {img_path}, Trans: {data[obj]["obj_trans"]}, Rot: {data[obj][
                        # "obj_rot"]}')
                        writer.writerow(
                            [obj_ids[obj], data["img_path"], data[obj]['obj_trans'], data[obj]['obj_rot']])

    def release(self):
        self.lock = False


if __name__ == "__main__":
    image = cv2.imread('recordings/11_28 22_02_2022/camera_2/images/0.png')
    provider = ViconProvider()
    processors = [Processor(index, provider) for index in cameras]
    print(f"Recording started: {datetime.now().strftime('%H_%M')}")
    start_time = time.time()
    while True:
        if np.all([processor.lock for processor in processors]):
            cv2.imshow('Recording', image)
            key = cv2.waitKey(1)
            if key == 32:
                cv2.destroyAllWindows()
                break
            for processor in processors:
                processor.release()
            print(processors[0].camera.fps)

    for processor in processors:
        processor.stop()
        processor.join()
    provider.stop()

    print(
        f"Recording ended: {datetime.now().strftime('%H_%M')}; Total Images taken: {np.sum([processor.imageIndex for processor in processors])} FPS: {np.sum([processor.imageIndex for processor in processors]) / (time.time() - start_time)}")
