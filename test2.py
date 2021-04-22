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

    source = [1, 5, 6]
    rot = np.asarray([[0.4080821, -0.9129453, 0.0000000],
                      [0.4795902, 0.2143745, -0.8509035],
                      [0.7768283, 0.3472385, 0.5253220]])
    destination = np.matmul(source, rot)
    print(destination)
    a = Arrow3D([source, destination], [[0, 0, 0], [0, 0, 0]], [
                [0, 0, 0], [0, 0, 0]], **arrow_prop_dict, color='r')
    ax1.add_artist(a)
    a = Arrow3D([0, 0], [0, 1], [0, 0], **arrow_prop_dict, color='b')
    ax1.add_artist(a)
    a = Arrow3D([0, 0], [0, 0], [0, 1], **arrow_prop_dict, color='g')
    ax1.add_artist(a)

    # Give them a name:
    ax1.text(0.0, 0.0, -0.1, r'$0$')
    ax1.text(1.1, 0, 0, r'$x$')
    ax1.text(0, 1.1, 0, r'$y$')
    ax1.text(0, 0, 1.1, r'$z$')

    plt.show()
