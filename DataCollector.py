import copy
from Camera.CVBCamera import Camera
from PyVicon.vicon_tracker import ObjectTracker
from threading import Thread
import os, csv, cv2
from datetime import datetime
from calibration.obj_gt_pose import get_obj_gt_transform


obj_ids = {"KLT_8_neu": 1,
           "KLT_27_neu": 2,
           "KLT_32_neu": 3
           }
cameras = [0, 1]  # 0,1,2,3,4,5,6,7
path = "recordings"


class Processor(Thread):
    def __init__(self, index):
        Thread.__init__(self)
        self.name = f"camera_{index}"
        self.imageIndex = 0
        self.running = True

        """
        creates a path for each object with the current recording 
        time and the id of the camera itself
        Like:
        ./recordings/11_11_11 08_11_2021/camera_0/images
        """
        now = datetime.now().strftime("%H_%M %d_%m_%Y") #adding seconds results in multiple directories creation
        self.folder_path = os.path.join(path, now)

        self.camera = Camera(index)
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
        while self.running:
            data = {"image": self.camera.getImage()}
            for obj in list(obj_ids.keys()):
                #data['objects']
                obj_trans = get_obj_gt_transform(self.camera, obj)[0]
                obj_rot = get_obj_gt_transform(self.camera, obj)[1]
                pose = {'obj_trans': obj_trans, 'obj_rot': obj_rot}
                pose_copy = copy.deepcopy(pose)
                data[obj] = pose_copy
                #print(data[obj])

            if self.imageIndex == 0:
                self.writeData(data, header=True)
            self.writeData(data, header=False)
            self.imageIndex += 1
            data.clear()

    def stop(self):
        self.running = False

    def writeData(self, data, header):
        """
        Writes as csv line and an image file for each object present in the scene
        """
        cam_path = os.path.join(self.folder_path, self.name)
        images_path = os.path.join(cam_path, 'images')
        if not os.path.exists(images_path):
            os.makedirs(images_path)
        with open(os.path.join(cam_path, "data.csv"), "a", newline="") as csvfile:
            writer = csv.writer(csvfile)
            if header:
                writer.writerow(['ObjectID', 'ImageName', 'camToObjTrans', 'camToObjRot', 'symmetry'])
            else:
                #print(data.keys())
                # obj_keys = []
                # for key in list(data.keys()):
                #     if key is not 'image': # get object IDs
                #         obj_keys.append(key)
                for obj in list(obj_ids.keys()):
                    img_path = os.path.join(images_path, str(self.imageIndex) + '.png')
                    #print(f'Obj ID: {obj}, Img path: {img_path}, Trans: {data[obj]["obj_trans"]}, Rot: {data[obj]["obj_rot"]}')
                    writer.writerow([obj_ids[obj], img_path, data[obj]['obj_trans'], data[obj]['obj_rot']])
                cv2.imwrite(img_path, data["image"])


if __name__ == "__main__":
    processors = [Processor(index)for index in cameras]
    capture_time = 2000 #ms
    #TODO: replace loop with button snapping
    while True:
        for processor in processors:
            #cv2.imshow(f'cam_{processor.name}', processor.camera.getImage())
            key = cv2.waitKey(capture_time)
            if key == 27:
                break

    for processor in processors:
        processor.stop()
