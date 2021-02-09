from camera import Camera
from image_processor import Processor


if __name__ == "__main__":
    camera_ids = [2]

    cameras = []
    for cam_id in camera_ids:
        cameras.append(Camera(cam_id))
        print('Started Camera {}'.format(cam_id))
    
    processor = Processor(cameras)

    running = True
    while running:
        command = input('Please enter command...\n')

        if command == 'q':
            running = False
            for camera in cameras:
                camera.close()
        if command == 'r':
            for camera in cameras:
                if not camera.running:
                    camera.run()
        elif command == 'c':
            processor.stop()
            for camera in cameras:
                camera.calibrate()
        elif command == 's':
            processor.start()
        elif command == 'm':
            for camera in cameras:
                camera.loadMask()
