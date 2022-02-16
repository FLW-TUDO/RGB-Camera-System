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
cam = Camera(2)


def get_index():
    """Retrives next biggest free indeex

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


# def processImage(image):
#     """Process the image
#
#     Args:
#         image (numpy.array): current image
#
#     Returns:
#         numpy.array: processed image
#     """
#     # image = cv2.flip(image, 0)
#     # image = cv2.flip(image, 1)
#     # image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
#     # image = cv2.resize(image, (int(2592 / 2), int(2048 / 2)))
#     return image


def main():
    """
    Main function
    Retrieves current image from camera, displays it, captures image and stores it
    """
    tracker.connect()
    index = get_index()

    with open("vicon_pose_chessboard.csv", "a") as f:
        writer = csv.writer(f)
        # writer.writerow(['image', 'translation', 'rotation'])
        while True:
            image = cam.getImage()
            if image is None:
                continue

            # image = processImage(image)

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
                        [f"img_{index}", vicon_translation, vicon_rotation])

    cam.close()


if __name__ == "__main__":
    main()
