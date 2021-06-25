import numpy as np
import os
from glob import glob
import cv2


# def sort(element):
#     return int(element.split('.')[0].split('_')[-1])


# camera_ids = [0, 1]

# for camera_id in camera_ids:
#     files = glob(os.path.join(
#         'images', f'camera_{camera_id}', '*'))
#     files.sort(key=sort)
#     for fname in files:
#         image = np.load(fname)
#         cv2.imshow('Camera View', image)

#         if cv2.waitKey(0) == ord('q'):
#             continue
