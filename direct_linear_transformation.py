import numpy as N


def DLTcalib(nd, xyz, uv):
    '''
    Camera calibration by DLT using known object points and their image points.

    This code performs 2D or 3D DLT camera calibration with any number of views (cameras).
    For 3D DLT, at least two views (cameras) are necessary.
    Inputs:
     nd is the number of dimensions of the object space: 3 for 3D DLT and 2 for 2D DLT.
     xyz are the coordinates in the object 3D or 2D space of the calibration points.
     uv are the coordinates in the image 2D space of these calibration points.
     The coordinates (x,y,z and u,v) are given as columns and the different points as rows.
     For the 2D DLT (object planar space), only the first 2 columns (x and y) are used.
     There must be at least 6 calibration points for the 3D DLT and 4 for the 2D DLT.
    Outputs:
     L: array of the 8 or 11 parameters of the calibration matrix
     err: error of the DLT (mean residual of the DLT transformation in units of camera coordinates).
    '''

    # Convert all variables to numpy array:
    xyz = N.asarray(xyz)
    uv = N.asarray(uv)
    # number of points:
    np = xyz.shape[0]
    # Check the parameters:
    if uv.shape[0] != np:
        raise ValueError(
            'xyz (%d points) and uv (%d points) have different number of points.' % (np, uv.shape[0]))
    if (nd == 2 and xyz.shape[1] != 2) or (nd == 3 and xyz.shape[1] != 3):
        raise ValueError('Incorrect number of coordinates (%d) for %dD DLT (it should be %d).' % (
            xyz.shape[1], nd, nd))
    if nd == 3 and np < 6 or nd == 2 and np < 4:
        raise ValueError(
            '%dD DLT requires at least %d calibration points. Only %d points were entered.' % (nd, 2*nd, np))

    # Normalize the data to improve the DLT quality (DLT is dependent of the system of coordinates).
    # This is relevant when there is a considerable perspective distortion.
    # Normalization: mean position at origin and mean distance equals to 1 at each direction.
    Txyz, xyzn = Normalization(nd, xyz)
    Tuv, uvn = Normalization(2, uv)

    A = []
    if nd == 2:  # 2D DLT
        for i in range(np):
            x, y = xyzn[i, 0], xyzn[i, 1]
            u, v = uvn[i, 0], uvn[i, 1]
            A.append([x, y, 1, 0, 0, 0, -u*x, -u*y, -u])
            A.append([0, 0, 0, x, y, 1, -v*x, -v*y, -v])
    elif nd == 3:  # 3D DLT
        for i in range(np):
            x, y, z = xyzn[i, 0], xyzn[i, 1], xyzn[i, 2]
            u, v = uvn[i, 0], uvn[i, 1]
            A.append([x, y, z, 1, 0, 0, 0, 0, -u*x, -u*y, -u*z, -u])
            A.append([0, 0, 0, 0, x, y, z, 1, -v*x, -v*y, -v*z, -v])

    # convert A to array
    A = N.asarray(A)
    # Find the 11 (or 8 for 2D DLT) parameters:
    U, S, Vh = N.linalg.svd(A)
    # The parameters are in the last line of Vh and normalize them:
    L = Vh[-1, :] / Vh[-1, -1]
    # Camera projection matrix:
    H = L.reshape(3, nd+1)
    # Denormalization:
    H = N.dot(N.dot(N.linalg.pinv(Tuv), H), Txyz)
    H = H / H[-1, -1]
    L = H.flatten('C')
    # Mean error of the DLT (mean residual of the DLT transformation in units of camera coordinates):
    uv2 = N.dot(H, N.concatenate((xyz.T, N.ones((1, xyz.shape[0])))))
    uv2 = uv2/uv2[2, :]
    # mean distance:
    err = N.sqrt(N.mean(N.sum((uv2[0:2, :].T - uv)**2, 1)))

    return L, err


def DLTrecon(nd, nc, Ls, uvs):
    '''
    Reconstruction of object point from image point(s) based on the DLT parameters.

    This code performs 2D or 3D DLT point reconstruction with any number of views (cameras).
    For 3D DLT, at least two views (cameras) are necessary.
    Inputs:
     nd is the number of dimensions of the object space: 3 for 3D DLT and 2 for 2D DLT.
     nc is the number of cameras (views) used.
     Ls (array type) are the camera calibration parameters of each camera 
      (is the output of DLTcalib function). The Ls parameters are given as columns
      and the Ls for different cameras as rows.
     uvs are the coordinates of the point in the image 2D space of each camera.
      The coordinates of the point are given as columns and the different views as rows.
    Outputs:
     xyz: point coordinates in space
    '''

    # Convert Ls to array:
    Ls = N.asarray(Ls)
    # Check the parameters:
    if Ls.ndim == 1 and nc != 1:
        raise ValueError(
            'Number of views (%d) and number of sets of camera calibration parameters (1) are different.' % (nc))
    if Ls.ndim > 1 and nc != Ls.shape[0]:
        raise ValueError(
            'Number of views (%d) and number of sets of camera calibration parameters (%d) are different.' % (nc, Ls.shape[0]))
    if nd == 3 and Ls.ndim == 1:
        raise ValueError(
            'At least two sets of camera calibration parameters are needed for 3D point reconstruction.')

    if nc == 1:  # 2D and 1 camera (view), the simplest (and fastest) case
        # One could calculate inv(H) and input that to the code to speed up things if needed.
        # (If there is only 1 camera, this transformation is all Floatcanvas2 might need)
        Hinv = N.linalg.inv(Ls.reshape(3, 3))
        # Point coordinates in space:
        xyz = N.dot(Hinv, [uvs[0], uvs[1], 1])
        xyz = xyz[0:2]/xyz[2]
    else:
        M = []
        for i in range(nc):
            L = Ls[i, :]
            # this indexing works for both list and numpy array
            u, v = uvs[i][0], uvs[i][1]
            if nd == 2:
                M.append([L[0]-u*L[6], L[1]-u*L[7], L[2]-u*L[8]])
                M.append([L[3]-v*L[6], L[4]-v*L[7], L[5]-v*L[8]])
            elif nd == 3:
                M.append([L[0]-u*L[8], L[1]-u*L[9],
                          L[2]-u*L[10], L[3]-u*L[11]])
                M.append([L[4]-v*L[8], L[5]-v*L[9],
                          L[6]-v*L[10], L[7]-v*L[11]])

        # Find the xyz coordinates:
        U, S, Vh = N.linalg.svd(N.asarray(M))
        # Point coordinates in space:
        xyz = Vh[-1, 0:-1] / Vh[-1, -1]

    return xyz


def Normalization(nd, x):
    '''
    Normalization of coordinates (centroid to the origin and mean distance of sqrt(2 or 3).

    Inputs:
     nd: number of dimensions (2 for 2D; 3 for 3D)
     x: the data to be normalized (directions at different columns and points at rows)
    Outputs:
     Tr: the transformation matrix (translation plus scaling)
     x: the transformed data
    '''

    x = N.asarray(x)
    m, s = N.mean(x, 0), N.std(x)
    if nd == 2:
        Tr = N.array([[s, 0, m[0]], [0, s, m[1]], [0, 0, 1]])
    else:
        Tr = N.array([[s, 0, 0, m[0]], [0, s, 0, m[1]],
                      [0, 0, s, m[2]], [0, 0, 0, 1]])

    Tr = N.linalg.inv(Tr)
    x = N.dot(Tr, N.concatenate((x.T, N.ones((1, x.shape[0])))))
    x = x[0:nd, :].T

    return Tr, x


def test():
    # Tests of DLTx
    print('')
    print('Test of camera calibration and point reconstruction based on direct linear transformation (DLT).')
    print('3D (x, y, z) coordinates (in cm) of the corner of a cube (the measurement error is at least 0.2 cm):')
    xyz = [[0, 0, 0], [0, 12.3, 0], [14.5, 12.3, 0], [14.5, 0, 0], [
        0, 0, 14.5], [0, 12.3, 14.5], [14.5, 12.3, 14.5], [14.5, 0, 14.5]]
    print(N.asarray(xyz))
    print('2D (u, v) coordinates (in pixels) of 4 different views of the cube:')
    uv1 = [[1302, 1147], [1110, 976], [1411, 863], [1618, 1012],
           [1324, 812], [1127, 658], [1433, 564], [1645, 704]]
    uv2 = [[1094, 1187], [1130, 956], [1514, 968], [1532, 1187],
           [1076, 854], [1109, 647], [1514, 659], [1523, 860]]
    uv3 = [[1073, 866], [1319, 761], [1580, 896], [1352, 1016],
           [1064, 545], [1304, 449], [1568, 557], [1313, 668]]
    uv4 = [[1205, 1511], [1193, 1142], [1601, 1121], [1631, 1487],
           [1157, 1550], [1139, 1124], [1628, 1100], [1661, 1520]]
    print('uv1:')
    print(N.asarray(uv1))
    print('uv2:')
    print(N.asarray(uv2))
    print('uv3:')
    print(N.asarray(uv3))
    print('uv4:')
    print(N.asarray(uv4))

    print('')
    print('Use 4 views to perform a 3D calibration of the camera with 8 points of the cube:')
    nd = 3
    nc = 4
    L1, err1 = DLTcalib(nd, xyz, uv1)
    print('Camera calibration parameters based on view #1:')
    print(L1)
    print('Error of the calibration of view #1 (in pixels):')
    print(err1)
    L2, err2 = DLTcalib(nd, xyz, uv2)
    print('Camera calibration parameters based on view #2:')
    print(L2)
    print('Error of the calibration of view #2 (in pixels):')
    print(err2)
    L3, err3 = DLTcalib(nd, xyz, uv3)
    print('Camera calibration parameters based on view #3:')
    print(L3)
    print('Error of the calibration of view #3 (in pixels):')
    print(err3)
    L4, err4 = DLTcalib(nd, xyz, uv4)
    print('Camera calibration parameters based on view #4:')
    print(L4)
    print('Error of the calibration of view #4 (in pixels):')
    print(err4)
    xyz1234 = N.zeros((len(xyz), 3))
    L1234 = [L1, L2, L3, L4]
    for i in range(len(uv1)):
        xyz1234[i, :] = DLTrecon(
            nd, nc, L1234, [uv1[i], uv2[i], uv3[i], uv4[i]])
    print('Reconstruction of the same 8 points based on 4 views and the camera calibration parameters:')
    print(xyz1234)
    print('Mean error of the point reconstruction using the DLT (error in cm):')
    print(N.mean(N.sqrt(N.sum((N.array(xyz1234)-N.array(xyz))**2, 1))))

    print('')
    print('Test of the 2D DLT')
    print('2D (x, y) coordinates (in cm) of the corner of a square (the measurement error is at least 0.2 cm):')
    xy = [[0, 0], [0, 12.3], [14.5, 12.3], [14.5, 0]]
    print(N.asarray(xy))
    print('2D (u, v) coordinates (in pixels) of 2 different views of the square:')
    uv1 = [[1302, 1147], [1110, 976], [1411, 863], [1618, 1012]]
    uv2 = [[1094, 1187], [1130, 956], [1514, 968], [1532, 1187]]
    print('uv1:')
    print(N.asarray(uv1))
    print('uv2:')
    print(N.asarray(uv2))
    print('')
    print('Use 2 views to perform a 2D calibration of the camera with 4 points of the square:')
    nd = 2
    nc = 2
    L1, err1 = DLTcalib(nd, xy, uv1)
    print('Camera calibration parameters based on view #1:')
    print(L1)
    print('Error of the calibration of view #1 (in pixels):')
    print(err1)
    L2, err2 = DLTcalib(nd, xy, uv2)
    print('Camera calibration parameters based on view #2:')
    print(L2)
    print('Error of the calibration of view #2 (in pixels):')
    print(err2)
    xy12 = N.zeros((len(xy), 2))
    L12 = [L1, L2]
    for i in range(len(uv1)):
        xy12[i, :] = DLTrecon(nd, nc, L12, [uv1[i], uv2[i]])
    print('Reconstruction of the same 4 points based on 2 views and the camera calibration parameters:')
    print(xy12)
    print('Mean error of the point reconstruction using the DLT (error in cm):')
    print(N.mean(N.sqrt(N.sum((N.array(xy12)-N.array(xy))**2, 1))))

    print('')
    print('Use only one view to perform a 2D calibration of the camera with 4 points of the square:')
    nd = 2
    nc = 1
    L1, err1 = DLTcalib(nd, xy, uv1)
    print('Camera calibration parameters based on view #1:')
    print(L1)
    print('Error of the calibration of view #1 (in pixels):')
    print(err1)
    xy1 = N.zeros((len(xy), 2))
    for i in range(len(uv1)):
        xy1[i, :] = DLTrecon(nd, nc, L1, uv1[i])
    print('Reconstruction of the same 4 points based on one view and the camera calibration parameters:')
    print(xy1)
    print('Mean error of the point reconstruction using the DLT (error in cm):')
    print(N.mean(N.sqrt(N.sum((N.array(xy1)-N.array(xy))**2, 1))))


test()
