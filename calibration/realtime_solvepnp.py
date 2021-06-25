from camera import Camera
import cv2
import numpy as np

scale = 130
a = 7
b = 5

# mtx = np.array([[1.75389232e+03, 0.00000000e+00, 1.33467897e+03],
#                 [0.00000000e+00, 1.76310192e+03, 9.90189589e+02],
#                 [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]])
# mtx = np.array([[856.96377093,   0.,         656.22791871],
#                 [0.,         856.9239457,  506.29416576],
#                 [0.,          0.,           1.]])
mtx = np.array([[857.77408004,   0.,         660.74539569],
                [0.,         857.76365601, 507.87194174],
                [0.,           0.,           1.]])
# dist = np.array([[0.1661366],
#                  [-0.11660577],
#                  [0.96362021],
#                  [-0.95954771], ])
# dist = np.array([[-1.75785099e-01],
#                  [1.25234579e-01],
#                  [- 9.30736485e-05],
#                  [- 9.18463510e-04],
#                  [- 2.64115332e-02]])
dist = np.array([[0.16106916],
                 [0.10749546],
                 [-0.09645183],
                 [0.39021927]])

criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

objp = np.zeros((a*b, 3), np.float32)
objp[:, :2] = np.mgrid[0:a, 0:b].T.reshape(-1, 2)
objp *= scale


axis = np.float32([[3, 0, 0], [0, 3, 0], [0, 0, 3]]).reshape(-1, 3)
axis *= scale


def drawLine(img, corners, imgpts, line_width=3):
    corner = tuple(corners[0].ravel())
    img = cv2.line(img, corner, tuple(
        imgpts[0].ravel()), (255, 0, 0), line_width)
    img = cv2.line(img, corner, tuple(
        imgpts[1].ravel()), (0, 255, 0), line_width)
    img = cv2.line(img, corner, tuple(
        imgpts[2].ravel()), (0, 0, 255), line_width)
    return img


axis_cube = np.float32([[0, 0, 0], [0, 3, 0], [3, 3, 0], [3, 0, 0],
                        [0, 0, -3], [0, 3, -3], [3, 3, -3], [3, 0, -3]])
axis_cube *= scale


def drawCube(img, corners, imgpts, line_width=3):
    imgpts = np.int32(imgpts).reshape(-1, 2)

    # draw ground floor in green
    img = cv2.drawContours(img, [imgpts[:4]], -1, (0, 255, 0), -line_width)

    # draw pillars in blue color
    for i, j in zip(range(4), range(4, 8)):
        img = cv2.line(img, tuple(imgpts[i]), tuple(
            imgpts[j]), (255), line_width)

    # draw top layer in red color
    img = cv2.drawContours(img, [imgpts[4:]], -1, (0, 0, 255), line_width)

    return img


def create_points(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Find the chess board corners
    ret, corners = cv2.findChessboardCorners(
        gray, (a, b), flags=cv2.CALIB_CB_ADAPTIVE_THRESH+cv2.CALIB_CB_FAST_CHECK+cv2.CALIB_CB_NORMALIZE_IMAGE)
    # If found, add object points, image points (after refining them)
    if ret == True:
        corners = cv2.cornerSubPix(
            gray, corners, (11, 11), (-1, -1), criteria)
        img = cv2.drawChessboardCorners(img, (a, b), corners, ret)

        return corners, objp


def undistort(img):
    _img_shape = img.shape[:2]
    DIM = _img_shape[::-1]
    map1, map2 = cv2.fisheye.initUndistortRectifyMap(
        mtx, dist, np.eye(3), mtx, DIM, cv2.CV_16SC2)
    undistorted_img = cv2.remap(
        img, map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
    return undistorted_img


def crop(img, center, width, height):
    h = int(height/2)
    w = int(width/2)
    x_left = max(0, int(center[0]-w))
    x_right = min(2592, int(center[0]+w))
    y_upper = max(0, int(center[1]-h))
    y_lower = min(2048, int(center[1]+h))
    return img[y_upper:y_lower, x_left:x_right]


def MSE(a, b):
    return np.sqrt(sum((a-b)**2))


def valid_point(img_points, corners, img_size):
    for point in img_points:
        if point[0][0] < 0 or point[0][0] > img_size[0] or point[0][1] < 0 or point[0][1] > img_size[1]:
            return False

    # x = corners[2]
    # y = corners[70]

    # if MSE(x, img_points[0][0]) > 10 and MSE(y, img_points[0][1]) > 10:
    #     return False

    return True


cam = Camera(2)

while True:
    image = cam.getImage()
    if image is None:
        continue
    image = cv2.flip(image, 0)
    image = cv2.flip(image, 1)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    ret, corners = cv2.findChessboardCorners(gray, (a, b), criteria)

    if ret == True:
        corners2 = cv2.cornerSubPix(
            gray, corners, (11, 11), (-1, -1), criteria)

        # Find the rotation and translation vectors.
        # ret, rvecs, tvecs, inliers = cv2.solvePnPRansac(
        #     objp, corners2, mtx, dist)
        ret, rvecs, tvecs = cv2.solvePnP(
            objp, corners2, mtx, dist)

        # project 3D points to image plane
        imgpts_line, jac_line = cv2.projectPoints(
            axis, rvecs, tvecs, mtx, dist)
        imgpts_cube, jac_cube = cv2.projectPoints(
            axis_cube, rvecs, tvecs, mtx, dist)

        # if not valid_point(imgpts_line, corners2, (2592, 2048)) or not valid_point(imgpts_cube, corners2, (2592, 2048)):
        #     continue
        # else:
        img = drawLine(image, corners2, imgpts_line, 10)
        # img = drawCube(image, corners2, imgpts_cube, 8)
        img = undistort(img)
        img = crop(img, corners2[0][0], int(2592/2), int(2048/2))
        cv2.imshow('Camera', img)
        key = cv2.waitKey(30) & 0xff
        if key == 113:
            cv2.destroyAllWindows()
            break

        print(f'Translation:\n {tvecs}')
    else:
        img = undistort(img)
        img = cv2.resize(img, (int(2592/2), int(2048/2)))
        cv2.imshow('Camera', img)
        key = cv2.waitKey(30) & 0xff
        if key == 113:
            cv2.destroyAllWindows()
            break


cv2.destroyAllWindows()
cam.close()
cam.closeStream()
