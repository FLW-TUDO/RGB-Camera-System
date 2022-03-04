import os.path

from Camera.CVBCamera import Camera
import cv2
from glob import glob
import sys
from PyVicon.vicon_tracker import ObjectTracker
import csv

# simple tool to get single images from the camera feed
# used for debugging purposes

save_location = './images/snapper'
if not os.path.exists(save_location):
    os.makedirs(save_location)

tracker = ObjectTracker()
object_name = 'chessboard'
cam_id = 1
cam = Camera(cam_id)


def get_index():
    """Retrives next biggest free index

    Returns:
        Number: next free index
    """
    images = glob("{}/*.png".format(save_location))
    numbers = []
    for fname in images:
        name = fname.split("/")[-1].split(".")[0]
        try:
            numbers.append(int(name))
        except:
            pass

    return max(numbers) if numbers != [] else 0

def main(save_vicon=True, append_entries=False):
    """
    Main function
    Retrieves current image from camera, displays it, captures image and stores it
    """
    tracker.connect()
    index = get_index()
    rotate = False

    if save_vicon:
        if append_entries:
            flag = "a"
        else:
            flag = "w"
        with open("vicon_pose_chessboard.csv", flag) as f:
            writer = csv.writer(f)
            #writer.writerow(['cam_id', 'image', 'translation', 'rotation'])

            while True:
                image = cam.getImage(rotate=rotate)
                if image is None:
                    continue

                cv2.imshow("Camera", image)
                key = cv2.waitKey(5)
                if key == 113: #q
                    cv2.destroyAllWindows()
                    break
                if key == 32: #space
                    index += 1
                    sys.stdout.write("\rPicture taken: {}".format(index))
                    sys.stdout.flush()

                    filename = "{}/{}.png".format(save_location, index)
                    cv2.imwrite(filename, image)

                    if object_name in tracker.aquire_subjects():
                        vicon_translation = tracker.aquire_Object_Trans(
                            object_name)
                        vicon_rotation = tracker.aquire_Object_RotQuaternion(
                            object_name)

                        writer.writerow(
                            [f"cam_{cam_id}", f"img_{index}", vicon_translation, vicon_rotation])
                    else:
                        print('Object not detected in vicon!')
    else:
        while True:
            image = cam.getImage(rotate=rotate)
            if image is None:
                continue

            cv2.imshow("Camera", image)
            key = cv2.waitKey(5)
            if key == 113:  # q
                cv2.destroyAllWindows()
                break
            if key == 32:  # space
                index += 1
                sys.stdout.write("\rPicture taken: {}".format(index))
                sys.stdout.flush()

                filename = "{}/{}.png".format(save_location, index)
                cv2.imwrite(filename, image)

    cam.close()


if __name__ == "__main__":
    main(save_vicon=True, append_entries=True)
