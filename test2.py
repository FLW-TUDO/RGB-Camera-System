import matplotlib as mpl
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
from mpl_toolkits.mplot3d import proj3d


class Arrow3D(FancyArrowPatch):
    def __init__(self, xs, ys, zs, *args, **kwargs):
        FancyArrowPatch.__init__(self, (0, 0), (0, 0), *args, **kwargs)
        self._verts3d = xs, ys, zs

    def draw(self, renderer):
        xs3d, ys3d, zs3d = self._verts3d
        xs, ys, zs = proj3d.proj_transform(xs3d, ys3d, zs3d, renderer.M)
        self.set_positions((xs[0], ys[0]), (xs[1], ys[1]))
        FancyArrowPatch.draw(self, renderer)


if __name__ == '__main__':
    fig = plt.figure()
    ax1 = fig.add_subplot(111, projection='3d')
    ax1.set_xlabel('X')
    ax1.set_xlim(-10, 10)
    ax1.set_ylabel('Y')
    ax1.set_ylim(-10, 10)
    ax1.set_zlabel('Z')
    ax1.set_zlim(-10, 10)

    # Here we create the arrows:
    arrow_prop_dict = dict(
        mutation_scale=20, arrowstyle='->', shrinkA=0, shrinkB=0)

    size = 1
    center = [1, 5, 6]
    base_1 = [center[0]+size, center[1], center[2]]
    base_2 = [center[0], center[1]+size, center[2]]
    base_3 = [center[0], center[1], center[2]+size]
    # rot = np.asarray([[0.4080821, -0.9129453, 0.0000000],
    #                   [0.4795902, 0.2143745, -0.8509035],
    #                   [0.7768283, 0.3472385, 0.5253220]])
    rot = np.array([[1.0, 0.0, 0.0],
                    [0.0, np.cos(np.pi/2), -np.sin(np.pi/2)],
                    [0.0, np.sin(np.pi/2), np.cos(np.pi/2)]])
    # dest_1 = np.matmul(base_1, rot)
    # dest_2 = np.matmul(base_2, rot)
    # dest_3 = np.matmul(base_3, rot)
    dest_1 = rot.dot(base_1)
    dest_2 = rot.dot(base_2)
    dest_3 = rot.dot(base_3)

    # print(base_1)
    # a = Arrow3D([center, dest_], [[0, 0, 0], [0, 0, 0]], [
    #             [0, 0, 0], [0, 0, 0]], **arrow_prop_dict, color='r')
    a = Arrow3D([center[0], dest_1[0]], [center[1], dest_1[1]], [
                center[2], dest_1[2]], **arrow_prop_dict, color='r')
    ax1.add_artist(a)
    a = Arrow3D([center[0], dest_2[0]], [center[1], dest_2[1]], [
                center[2], dest_2[2]], **arrow_prop_dict, color='b')
    ax1.add_artist(a)
    a = Arrow3D([center[0], dest_3[0]], [center[1], dest_3[1]], [
                center[2], dest_3[2]], **arrow_prop_dict, color='g')
    ax1.add_artist(a)

    a = Arrow3D([center[0], base_1[0]], [center[1], base_1[1]], [
                center[2], base_1[2]], **arrow_prop_dict, color='r')
    ax1.add_artist(a)
    a = Arrow3D([center[0], base_2[0]], [center[1], base_2[1]], [
                center[2], base_2[2]], **arrow_prop_dict, color='b')
    ax1.add_artist(a)
    a = Arrow3D([center[0], base_3[0]], [center[1], base_3[1]], [
                center[2], base_3[2]], **arrow_prop_dict, color='g')
    ax1.add_artist(a)

    # Give them a name:
    ax1.text(0.0, 0.0, -0.1, r'$0$')
    ax1.text(1.1, 0, 0, r'$x$')
    ax1.text(0, 1.1, 0, r'$y$')
    ax1.text(0, 0, 1.1, r'$z$')

    plt.show()
