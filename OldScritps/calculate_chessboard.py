import numpy as np
from itertools import product
from matplotlib import pyplot as plt

a = 7
b = 5


def draw(corners):
    plt.scatter([c[0] for c in corners], [c[1] for c in corners])
    for i in range(len(corners) - 1):
        l1 = corners[i][:2]
        l2 = corners[i+1][:2]
        plt.axline(l1, l2)
    plt.show()


def getChessboardPoints(corner, xz_point, xy_point, validation_point=None):
    x_axis = np.array(xz_point) - np.array(corner)
    y_axis = np.array(xy_point) - np.array(corner)

    correction = None
    if validation_point is not None:
        prediction = corner + x_axis * (a + 1) + y_axis * (b + 1)
        offset = prediction - validation_point
        correction = [validation_point - x_axis *
                      j - y_axis * i for i, j in product(range(b, 0, -1), range(a, 0, -1))]

    corners = [corner + x_axis * j + y_axis * i
               for i, j in product(range(1, b+1), range(1, a+1))]
    if correction is not None:
        corners2 = [(corner + corr) / 2 for corner,
                    corr in zip(corners, correction)]
        return corners2
    else:
        return corners


if __name__ == "__main__":
    corner = np.array(
        (-538.0413534556614, -1673.8279964761737, 50.797529165787665))
    xz_point = np.array(
        (-408.37914219245994, -1669.24600619773, 51.238083009259874))
    xy_point = np.array(
        (-532.8184361461675, -1803.1212152781552, 50.508417835382254))
    validation_point = np.array(
        (527.8059747618893, -2412.5474180537926, 49.77562997627586))

    ret = getChessboardPoints(
        corner, xz_point, xy_point, validation_point=validation_point)

    draw(ret)
