import cv2
import numpy as np

# static test function for testing the pnp solving of cv2

object_points_extrinsic = np.array([0, 0, 0])
image_points_extrinsic = np.array([0, 0])

image_points = np.load('image_points.npy')
object_points = np.load('object_points.npy')

for point in image_points:
    image_points_extrinsic = np.vstack((image_points_extrinsic, point[0][0]))

for point in object_points:
    object_points_extrinsic = np.vstack((object_points_extrinsic, point[0][0]))


K = np.array([[367.1434646940849, 0.0, 304.250873277727], [
             0.0, 368.8458905420833, 223.58756315623015], [0.0, 0.0, 1.0]])
D = np.array([[0.10666939085590753], [0.432679650635747],
              [-0.9362253755241718], [0.6913429032804886]])
ret, _, tvec = cv2.solvePnP(
    object_points_extrinsic[1:], image_points_extrinsic[1:], K, D)
if ret:
    print("K:")
    print(K)
    print("D:")
    print(D)
    print("Translation:")
    print(tvec)
else:
    print("Calculate extrinsics failed!")
