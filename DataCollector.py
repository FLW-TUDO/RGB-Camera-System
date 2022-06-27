import copy
import time

from Camera.CVBCamera import Camera
from PyVicon.ViconProvider import ViconProvider
from calibration.obj_gt_pose import get_obj_gt_transform
from threading import Thread
import os
import csv
import cv2
from datetime import datetime
import numpy as np

RECORD_OBJECTS = False
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
cameras = [0,1,2,3,4,5,6,7] # [1, 2, 5, 6]  # 0,1,2,3,4,5,6,7
path = "recordings"


class Processor(Thread):
    def __init__(self, index, provider=None):
        Thread.__init__(self)
        self.name = index
        self.imageIndex = 0
        self.provider = provider
        self.running = True
        self.record_objects = RECORD_OBJECTS
        self.frequency = 0
        self.lastframe = time.time()

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

    def updateFrequency(self):
        self.frequency = 1 / (time.time() - self.lastframe)
        self.lastframe = time.time()

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
        last_image_id = -1
        while self.running:
            while self.lock:
                time.sleep(0.0001)

            image, image_id = self.camera.getImageSync()
            while image_id == last_image_id or image is None:
                image, image_id = self.camera.getImageSync()

            last_image_id = image_id

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
            self.updateFrequency()
            self.lock = True

        self.writeData(csv_data)
        csv_data.clear()

        print(f'Camera {self.name} stopped!')

    def stop(self):
        self.running = False
        self.lock = False

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
            # writer.writerow(['ObjectID', 'ImageName', 'camToObjTrans', 'camToObjRot', 'symmetry'])
            if not self.record_objects:
                writer.writerow(['img_path', 'timestamp'])
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
    image = None
    provider = ViconProvider(obj_ids) if RECORD_OBJECTS else None
    processors = [Processor(index, provider) for index in cameras]
    print(f"Recording started: {datetime.now().strftime('%H_%M')}")
    start_time = time.time()
    while True:
        if np.all([processor.lock for processor in processors]):
            if image is None:
                image = processors[0].camera.getImage()
            cv2.imshow('Recording', image)
            key = cv2.waitKey(1)
            if key == 32:
                cv2.destroyAllWindows()
                break
            for processor in processors:
                processor.release()

            fps = [processor.frequency for processor in processors]
            print(
                f"Running with {len(processors)} cameras; Max: {round(max(fps))}; Min: {round(min(fps))}"
            )
        else:
            time.sleep(0.0001)

    for processor in processors:
        processor.release()
        processor.stop()
        processor.join()
    if RECORD_OBJECTS:
        provider.stop()

    print(
        f"Recording ended: {datetime.now().strftime('%H_%M')}; Total Time: {round((time.time() - start_time), 2)} Sec; Total Images taken: {np.sum([processor.imageIndex for processor in processors])}; Total FPS: {np.sum([processor.imageIndex for processor in processors]) / (time.time() - start_time) / len(processors)}")
