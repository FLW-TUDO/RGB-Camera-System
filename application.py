from camera import Camera
from image_processor import Processor

# This is the main application to start and controll the cameras


if __name__ == "__main__":
    # the selected cameras out of [0,1,2,3,4,5,6,7]
    camera_ids = [0, 1, 2, 3, 4, 5, 6, 7]

    cameras = []
    for cam_id in camera_ids:
        cameras.append(Camera(cam_id))
        print('Started Camera {}'.format(cam_id))

    processor = Processor(cameras)

    running = True
    while running:
        command = input('Please enter command...\n')

        # close the programm
        if command == 'q':
            running = False
            for camera in cameras:
                camera.close()
        # start/restart the cameras
        if command == 'r':
            for camera in cameras:
                if not camera.running:
                    camera.run()
        # calibrate cameras
        elif command == 'c':
            processor.stop()
            for camera in cameras:
                camera.calibrate()
            print(
                'Press q to stop the recording and start processing the calibration data.')
        # display the camera feed
        elif command == 's':
            processor.start()
        # mask cameras
        elif command == 'm':
            for camera in cameras:
                camera.loadMask()
