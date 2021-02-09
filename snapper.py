from camera import Camera
import cv2
from glob import glob

images = glob('./images/chessboard/*.jpg')
starting_number = 0
for fname in images:
    name = fname.split('/')[-1].split('.')[0]
    try:
        print(name)
        starting_number = max(int(name), starting_number) + 1
    except:
        pass


cam = Camera(2)
index = starting_number

while True:
    image = cam.getImage()
    if image is None:
        continue
    image = cv2.resize(image, (int(2592 / 4), int(2048/ 4)))
    image = cv2.flip(image, 0)
    image = cv2.flip(image, 1)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    
    filename = './images/chessboard/{}.jpg'.format(index)
    cv2.imwrite(filename, image)
    index += 1

    input('Enter to continue.....')