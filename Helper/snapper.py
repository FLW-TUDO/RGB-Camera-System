from camera import Camera
import cv2
from glob import glob
import sys
from vicon_tracker import ObjectTracker

# simple tool to get single images from the camera feed
# used for debugging purposes

folder = "snapper"

tracker = ObjectTracker()
cam = Camera(6)


def get_index():
    """Retrives next biggest free indeex

    Returns:
        Number: next free index
    """
    images = glob("./images/{}/*.png".format(folder))
    numbers = []
    for fname in images:
        name = fname.split("/")[-1].split(".")[0]
        try:
            numbers.append(int(name))
        except:
            pass

    return numbers[-1] if numbers != [] else 0


def processImage(image):
    """Process the image

    Args:
        image (numpy.array): current image

    Returns:
        numpy.array: processed image
    """
    image = cv2.flip(image, 0)
    image = cv2.flip(image, 1)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = cv2.resize(image, (int(2592 / 2), int(2048 / 2)))
    return image


def main():
    """
    Main function
    Retrieves current image from camera, displays it, captures image and stores it
    """
    tracker.connect()
    index = get_index()

    while True:
        image = cam.getImage()
        if image is None:
            continue

        image = processImage(image)

        cv2.imshow("Camera", image)
        key = cv2.waitKey(5)
        if key == 113:
            cv2.destroyAllWindows()
            break
        if key == 32:
            index += 1
            sys.stdout.write("\rPicture taken: {}".format(index))
            sys.stdout.flush()

            filename = "./images/{}/{}.png".format(folder, index)
            cv2.imwrite(filename, image)

    cam.close()


if __name__ == "__main__":
    main()
