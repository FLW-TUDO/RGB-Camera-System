import time
from threading import Thread
import cv2
import sys
import numpy as np
from Camera.CVBCamera import Camera
from PyVicon.ViconProvider import ViconProvider



# simple class to display camera feed of multiple cameras

class Processor(Thread):
    def __init__(self, cameras):
        Thread.__init__(self)
        self.cameras = cameras

        self.lastframe = 0

    def dummyImage(self, resolution=(None, None)):
        return np.zeros((resolution[0], resolution[1], 3))

    def stop(self):
        self.running = False
        cv2.destroyAllWindows()

    def run(self):
        self.running = True
        print(
            "Displaying Cameras {}. Press q to exit.".format(
                [i for i in range(len(self.cameras))]
            )
        )

        dummyImage = None
        length = len(self.cameras)
        if length % 2 == 1:
            dummyImage = True
            print("Be careful you are using an odd number of cameras.")

        while self.running:
            images = []
            for camera in self.cameras:
                img = camera.getImage()
                images.append(img)


            if dummyImage:
                _ = images.pop(-1)

            # concatenate image Horizontally
            Hori1 = np.concatenate(images[: int(length / 2)], axis=1)
            Hori2 = np.concatenate(images[int(length / 2):], axis=1)

            image = np.vstack((Hori1, Hori2))

            # Displays FPS
            sys.stdout.write(
                f"\rFramerates: {[round(camera.fps, 2) for camera in self.cameras]};"
            )
            sys.stdout.flush()

            cv2.imshow("Cameras", image)
            if cv2.waitKey(50) == ord("q"):
                cv2.destroyAllWindows()
                break


# This is the main application to start and control the cameras

if __name__ == "__main__":
    # the selected cameras out of [0,1,2,3,4,5,6,7]
    camera_ids = [1,2,5,6]
    resolution = (int((1920 / 2) / (int(len(camera_ids) / 2))), int(1080 / 2)) # for 4 cams

    cameras = []
    for cam_id in camera_ids:
        cameras.append(Camera(cam_id, size_factor=1, resolution=resolution))
        print("Started Camera {}".format(cam_id))

    processor = Processor(cameras)

    running = True
    while running:
        command = input("Please enter command...\n")

        # close the program
        if command == "q":
            running = False
            for camera in cameras:
                camera.close()
        # start/restart the cameras
        if command == "r":
            for camera in cameras:
                if not camera.running:
                    camera.run()
        # display the camera feed
        elif command == "s":
            processor.start()
