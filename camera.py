from threading import Thread
import os
import cvb
from time import time

# Camera class for accessing the cvb cameras


class Camera(Thread):
    def __init__(self, id, size_factor=4):
        Thread.__init__(self)
        self.id = id
        self.device = cvb.DeviceFactory.open(os.path.join(
            cvb.install_path(), "drivers", "GenICam.vin"), port=self.id)

        self.image = None

        self.rotate_vertical = True
        self.rotate_horizontal = True
        self.resolution = (int(2592 / size_factor), int(2048 / size_factor))

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

    def getImage(self):
        return self.image
