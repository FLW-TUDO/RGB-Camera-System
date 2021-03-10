import numpy as np
from itertools import product

a = 2
b = 2

def getChessboardPoints(corner, xz_point, xy_point):
    x_axis = np.array(xz_point) - np.array(corner)
    y_axis = np.array(xy_point) - np.array(corner)

    points = []
    for i in range(a):
        for j in range(b):
            new_point = corner + x_axis * (i + 1) + y_axis * (j + 1)
            points.append(new_point)

    return points

def getChessboardPoints_short(corner, xz_point, xy_point):
    x_axis = np.array(xz_point) - np.array(corner)
    y_axis = np.array(xy_point) - np.array(corner)

    return [corner + x_axis * (i + 1) + y_axis * (j + 1) for i,j in product(range(a), range(b))]




if __name__ == "__main__":
    corner = np.array([50, 50, 0])
    xz_point = np.array([30, 50, 1])
    xy_point = np.array([50, 30, 1])

    for i,j in product(range(a), range(b)):
        print(j+1, i+1)

    ret1 = getChessboardPoints(corner, xz_point, xy_point)
    ret2 = getChessboardPoints_short(corner, xz_point, xy_point)

    for a,b in zip(ret1, ret2):
        print(a, b)
