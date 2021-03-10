from camera import Camera
import cv2
from glob import glob
import sys

# simple tool to get single images from the camera feed
# used for debugging purposes

folder = 'chessboard'

images = glob('./images/{}/*.jpg'.format(folder))
numbers = []
for fname in images:
    name = fname.split('/')[-1].split('.')[0]
    try:
        numbers.append(int(name))
    except:
        pass

freenumbers = []
if len(numbers) > 0:
    for number in range(numbers[-1]):
        if number not in numbers:
            freenumbers.append(number)

cam = Camera(2)
index = 0

while True:
    image = cam.getImage()
    if image is None:
        continue
    image = cv2.resize(image, (int(2592 / 4), int(2048 / 4)))
    image = cv2.flip(image, 0)
    image = cv2.flip(image, 1)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    cv2.imshow('Camera', image)
    key = cv2.waitKey(10)
    if key == 113:
        cv2.destroyAllWindows()
        break
    if key == 32:
        if len(freenumbers) > 0:
            index = freenumbers.pop(0)
        else:
            index += 1
        sys.stdout.write('\rPicture taken: {}'.format(index))
        sys.stdout.flush()

        filename = './images/{}/{}.png'.format(folder, index)
        cv2.imwrite(filename, image)

cam.close()
