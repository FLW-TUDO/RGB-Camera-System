from camera import Camera
from record_processor import Processor

if __name__ == "__main__":
    # the selected cameras out of [0,1,2,3,4,5,6,7]
    camera_ids = [0, 2, 3, 4, 5, 6]

    cameras = []
    for cam_id in camera_ids:
        cameras.append(Camera(cam_id))
        print('Started Camera {}'.format(cam_id))

    processor = Processor(cameras)