from camera import Camera
from glob import glob
from vicon_tracker import ObjectTracker
import numpy as np
import os, csv, cv2

class Processor():
    def __init__(self, cameras, objects):
        Thread.__init__(self)
        self.cameras = cameras
        self.objects = objects
        self.resolution = (int(2592), int(2048))

        self.createFolder()
        self.image_index = self.getIndex()

        self.tracker = ObjectTracker()
        self.tracker.connect()

    def getIndex(self):
        index = 0
        camera = self.cameras[0]
        if os.path.exists(os.path.join('images', f'camera_{camera.id}')):
            images = glob(os.path.join('images', f'camera_{camera.id}'))
            index = int(images[-1].split('.')[0].split('_')[-1])
        return index

    def createFolder(self):
        for camera in self.cameras:
            if not os.path.exists(os.path.join('images', f'camera_{camera.id}')):
                os.makedirs(os.path('images', f'camera_{camera.id}'))

    def aquire_object_positions(self):
        with open('data.csv', 'a') as f:
            writer = csv.writer(f)
            for object_id in self.objects:
                positions = self.tracker.aquire_Object_MarkerPositions(object_id)
                writer.writerow([object_id,f'image_{self.image_index}', positions])


    # retrieves image from camera and preprocesses image to store it
    def getImage(self, camera):
        image = camera.getImage()
        if image is None:
            print('Camera {} is not running'.format(camera.id))
            return False
        
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        image = cv2.resize(image, self.resolution)
        image = cv2.flip(image, 0)
        image = cv2.flip(image, 1)

        np.savez(os.path.join('images', f'camera_{camera.id}', f'image_{self.image_index}.npz'), image)

        return True

    def stop(self):
        self.running = False

    def record(self):
        self.running = True
        print('Recording Cameras {}. Press q to exit.'.format(
            [i for i in range(len(self.cameras))]))

        while self.running:
            with Pool(len(self.cameras)) as p:
                res = p.map(self.getImage, self.cameras)

            self.aquire_object_positions()
            self.image_index += 1

            # Displays FPS
            sys.stdout.write('\rFramerates: {}'.format(
                [round(camera.fps, 2) for camera in self.cameras]))
            sys.stdout.flush()

            if cv2.waitKey(50) == ord('q'):
                break

if __name__ == "__main__":
    # the selected cameras out of [0, 1, 2, 3, 4, 5, 6, 7]
    camera_ids = [0, 1, 2, 3, 4, 5, 6]
    object_ids = ['test_object']

    cameras = []
    for cam_id in camera_ids:
        cameras.append(Camera(cam_id))
        print('Started Camera {}'.format(cam_id))

    processor = Processor(cameras)
    processor.record()
    