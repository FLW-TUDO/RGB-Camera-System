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

    def stop(self):
        self.running = False
        cv2.destroyAllWindows()

    def run(self):
        self.running = True
        print('Displaying Cameras {}. Press q to exit.'.format(
            [i for i in range(len(self.cameras))]))
        while self.running:
            images = []
            for camera in self.cameras:
                images.append(self.getImage(
                    camera, resolution=camera.resolution, rotate=(True, True), mask=False))

            # concatanate image Horizontally
            Hori = np.concatenate(images, axis=1)

            # Displays FPS
            sys.stdout.write('\rFramerates: {}'.format(
                [round(camera.fps, 2) for camera in self.cameras]))
            sys.stdout.flush()

            cv2.imshow('HORIZONTAL', Hori)
            if cv2.waitKey(50) == ord('q'):
                cv2.destroyAllWindows()
                break
