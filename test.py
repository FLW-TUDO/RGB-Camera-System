import numpy as np
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy.spatial.transform import Rotation as R


def rotate(vector, degrees=90, axis=np.array([1, 0, 0])):
    angle = np.radians(degrees)
    angel_vector = axis * angle
    r = R.from_rotvec(angel_vector)
    new_vector = r.apply(vector)
    return new_vector


def calculate_position(point, length, camera_angle_hor, camera_angle_ver):
    vector = np.array([-1, 0, 0])
    vector = rotate(vector, camera_angle_ver, axis=np.array([0, 1, 0]))
    vector = rotate(vector, camera_angle_hor, axis=np.array([0, 0, 1]))
    vector *= length

    final_point = point + vector
    print(final_point)
    return final_point


fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

point = np.array([9089, -467, 0])
camera_angle_hor = 90
camera_angle_ver = 45
length = 7136

ax.scatter(*point)
final_point = calculate_position(
    point, length, camera_angle_hor, camera_angle_ver)

ax.scatter(*final_point)
ax.plot(*zip(final_point, point))


plt.show()
