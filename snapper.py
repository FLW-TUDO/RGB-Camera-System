from camera import Camera
import cv2
from glob import glob
import sys
from vicon_tracker import ObjectTracker
from calculate_chessboard import getChessboardPoints
import json

# simple tool to get single images from the camera feed
# used for debugging purposes

folder = 'snapper'
save_json = False

tracker = ObjectTracker()
tracker.connect()

images = glob('./images/{}/*.png'.format(folder))
numbers = []
for fname in images:
    name = fname.split('/')[-1].split('.')[0]
    try:
        numbers.append(int(name))
    except:
        pass

freenumbers = []
if len(numbers) > 0:
    for number in range(1, numbers[-1] + 1):
        if number not in numbers:
            freenumbers.append(number)

if freenumbers == [] and numbers != []:
    index = numbers[-1]
else:
    index = 0

positions = {}
cam = Camera(3)


while True:
    image = cam.getImage()
    if image is None:
        continue
    image = cv2.flip(image, 0)
    image = cv2.flip(image, 1)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = cv2.resize(image, (int(2592 / 2), int(2048 / 2)))

    cv2.imshow('Camera', image)
    key = cv2.waitKey(5)
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
        # 2 ---- 3
        # | \
        # 1   \
        #       9
        if save_json:
            marker_positions = tracker.aquire_Object_MarkerPositions(
                'chessboard')
            chessboard_positions = getChessboardPoints(
                marker_positions[1], marker_positions[2], marker_positions[0], validation_point=marker_positions[8])
            positions['{}.png'.format(index)] = [list(position)
                                                 for position in chessboard_positions]

if save_json:
    with open('./images/{}/data.json'.format(folder), 'w') as f:
        json.dump(positions, f)

cam.close()
