from threading import Thread
import cv2
import sys
import numpy as np

# simple class to display camera feed of multiple cameras


class Processor(Thread):
    def __init__(self, cameras):
        Thread.__init__(self)
        self.cameras = cameras

        self.lastframe = 0

    # retrieves image from camera and preprocesses image to display it properly
    def getImage(self, camera, resolution=(None, None), rotate=(False, False), mask=False):
        image = camera.getImage()
        if image is None:
            raise Exception('Camera {} is not running'.format(camera.id))
        if mask:
            image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            image = image * camera.mask
        else:
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        if resolution[0] is not None:
            image = cv2.resize(image, resolution)
        if rotate[0]:
            image = cv2.flip(image, 0)
        if rotate[1]:
            image = cv2.flip(image, 1)
        return image

    def dummyImage(self, resolution=(None, None)):
        return np.zeros((resolution[0], resolution[1], 3))

    def stop(self):
        self.running = False
        cv2.destroyAllWindows()

    def run(self):
        self.running = True
        print('Displaying Cameras {}. Press q to exit.'.format(
            [i for i in range(len(self.cameras))]))

        dummyImage = None
        length = len(self.cameras)
        if length % 2 == 1:
            dummyImage = True
            print('Be careful you are using an odd number of cameras.')

        resolution = (int(1920/(int(length/2))), int(1080 / 2))

        while self.running:
            images = []
            for camera in self.cameras:
                images.append(self.getImage(
                    camera, resolution=resolution, rotate=(True, True), mask=False))

            if dummyImage:
                _ = images.pop(-1)

            # concatanate image Horizontally
            Hori1 = np.concatenate(images[:int(length/2)], axis=1)
            Hori2 = np.concatenate(images[int(length/2):], axis=1)

            image = np.vstack((Hori1, Hori2))

            # Displays FPS
            sys.stdout.write('\rFramerates: {}'.format(
                [round(camera.fps, 2) for camera in self.cameras]))
            sys.stdout.flush()

            cv2.imshow('Cameras', image)
            if cv2.waitKey(50) == ord('q'):
                cv2.destroyAllWindows()
                break
