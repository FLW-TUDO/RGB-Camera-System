import time

from Camera.Camera import AbstractCamera
import os
import cvb
import cv2
from datetime import datetime
import shutil
from threading import Thread
from calibration.obj_gt_pose import get_obj2vicon_transform, get_obj2vicon_transform_sync, get_new_frame
obj_ids = {
    "rb1_base_c": {'object_id': 2, 'active': True},
}


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
            if obj_ids[obj]["active"]:
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
                if obj_ids[obj]["active"]:
                    obj2vicon_trans, obj2vicon_rot_mat = get_obj2vicon_transform_sync(obj)
                    self.obj_gt_transf[obj]["obj2vicon_trans"] = obj2vicon_trans
                    self.obj_gt_transf[obj]["obj2vicon_rot_mat"] = obj2vicon_rot_mat

    def object_gt_transform(self, objId):
        return self.obj_gt_transf[objId]["obj2vicon_trans"], self.obj_gt_transf[objId]["obj2vicon_rot_mat"]



class Camera(AbstractCamera):
    """
        Camera class for accessing the cvb cameras
    """

    def __init__(self, id, size_factor=2, resolution=None):
        if resolution is not None:
            super().__init__(id=id, size_factor=size_factor, resolution=resolution)
        else:
            super().__init__(id=id, size_factor=size_factor)
        self.device = cvb.DeviceFactory.open(os.path.join(cvb.install_path(), "drivers", "GenICam.vin"), port=self.id)
        self.openStream()
        self.start()

    def retrieveFrame(self):
        image, status = self.stream.wait()
        if status == cvb.WaitStatus.Ok:
            self.image = cvb.as_array(image)

    def openStream(self):
        self.stream = self.device.stream
        self.stream.start()

    def closeStream(self):
        self.running = False
        self.stream.abort()

    def getImage(self, rotate=(True, True)):
        """Retrieves the current image

        Returns:
            numpy.array: current image
        """
        if self.image is None:
            return None
        image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
        image = cv2.resize(image, tuple((int(self.resolution[0]), int(self.resolution[1]))))
        if rotate[0]:
            image = cv2.flip(image, 0)
        if rotate[1]:
            image = cv2.flip(image, 1)
        return image


if __name__ == "__main__":
    if os.path.exists(os.path.join('images', 'timesync')):
        shutil.rmtree(os.path.join('images', 'timesync'))
    os.mkdir(os.path.join('images', 'timesync'))
    cam = Camera(2)
    provider = ViconProvider()
    while True:
        cam.retrieveFrame()
        img = cam.getImage((False, False))
        dt = datetime.now()
        cv2.imwrite(os.path.join('images', 'timesync', f'{dt}.png'), img)
        for obj in obj_ids:
            obj_trans, obj_rot = provider.object_gt_transform(obj)
        time.sleep(.1)

    cam.closeStream()
