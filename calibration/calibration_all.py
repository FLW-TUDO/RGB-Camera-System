import os.path

import cv2
import numpy as np
import glob
from icecream import ic


def initialize_obj_points(a, b, scale):
    objp = np.zeros((1, a*b, 3), np.float32)
    objp[0, :, :2] = np.mgrid[0:a, 0:b].T.reshape(-1, 2)
    objp *= scale
    return objp


# TODO: checks returned rvecs & tvecs
def get_intrinsics(imgs_path, a, b, scale, visulaize):
    images = glob.glob(imgs_path)
    objpoints = []
    imgpoints = []
    objp = initialize_obj_points(a, b, scale)
    for fName in images:
        print(fName)
        img = cv2.imread(fName)
        ret, corners2, gray = create_img_points(img, a, b)
        objpoints.append(objp)
        imgpoints.append(corners2)
        if visulaize == True:
            draw_chessboard_pts(img, a, b, corners2, ret, fName)
            key = cv2.waitKey(0)
            if key == 113:  # q
                visulaize = False
            cv2.destroyAllWindows()
    print('Calculating Intrinsics')
    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(
        objpoints, imgpoints, gray.shape[::-1], None, None)
    newcameramtx, roi = cv2.getOptimalNewCameraMatrix(
        mtx, dist, (gray.shape[1], gray.shape[0]), 1, (gray.shape[1], gray.shape[0]))
    return ret, mtx, dist, newcameramtx, roi, rvecs, tvecs


def get_extrinsics(img_path, a, b, scale, mtx, dist):
    # images = glob.glob(imgs_path)
    objp = initialize_obj_points(a, b, scale)
    # for fName in images:
    img = cv2.imread(img_path)
    ret, corners2, gray = create_img_points(img, a, b)
    ret, rvecs, tvecs = cv2.solvePnP(objp, corners2, mtx, dist)
    if ret:
        return ret, rvecs, tvecs
    else:
        print("Calculate extrinsics failed!")


def create_img_points(img, a, b):   # TODO: check flags
    '''returns concatenated image points and object points'''
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    # Find the chess board corners
    ret, corners = cv2.findChessboardCorners(
        gray, (a, b), None)
    # If found, add object points, image points (after refining them)
    if ret == True:
        corners2 = cv2.cornerSubPix(
            gray, corners, (11, 11), (-1, -1), criteria)
        return ret, corners2, gray


def draw_chessboard_pts(img, a, b, corners2, ret, name=''):
    # Draw and display the corners
    cv2.drawChessboardCorners(img, (a, b), corners2, ret)
    cv2.imshow(f'{name}', img)


def draw_lines(img, corners, proj_pts):
    corner = tuple(corners[0].ravel())
    img = cv2.line(img, corner, tuple(proj_pts[0].ravel()), (255, 0, 0), 5)
    img = cv2.line(img, corner, tuple(proj_pts[1].ravel()), (0, 255, 0), 5)
    img = cv2.line(img, corner, tuple(proj_pts[2].ravel()), (0, 0, 255), 5)
    return img


def undistort(imgs_path, mtx, dist, newcameramtx, roi, visualize):
    '''
    @param imgs_path: directory of images to be undistorted
    @type imgs_path: str
    ...
    @return: image matrix
    @rtype: np array
    '''
    images = glob.glob(imgs_path)
    print('Undistorting images')
    for fName in images:
        img = cv2.imread(fName)
        undistorted_img = cv2.undistort(img, mtx, dist, None, newcameramtx)
        # crop the image
        x, y, w, h = roi
        undistorted_img = undistorted_img[y:y+h, x:x+w]
        if visualize == True:
            cv2.imshow('Undistorted', undistorted_img)
            key = cv2.waitKey(0)
            if key == 113:  # q
                cv2.destroyAllWindows()
                break
    return undistorted_img


def undistort_and_save(img_path, mtx, dist, newcameramtx, roi, visualize, save_path=None):
    '''
    @param imgs_path: single image to be undistorted
    @type imgs_path: str
    ...
    @return: undistorted image path
    @rtype: str
    '''
    print('Undistorting images')
    img = cv2.imread(img_path)
    undistorted_img = cv2.undistort(img, mtx, dist, None, newcameramtx)
    # crop the image
    x, y, w, h = roi
    undistorted_img = undistorted_img[y:y+h, x:x+w]
    img_id = os.path.split(img_path)[-1].split('.')[-2]
    final_path = os.path.join(save_path, img_id+'.png')
    cv2.imwrite(final_path, undistorted_img)
    if visualize == True:
        cv2.imshow('Undistorted', undistorted_img)
        key = cv2.waitKey(0)
        if key == 113:  # q
            cv2.destroyAllWindows()
    return final_path

def draw_cube(img, corners, proj_pts, line_width=3):
    proj_pts = np.int32(proj_pts).reshape(-1, 2)
    # draw ground floor in green
    img = cv2.drawContours(img, [proj_pts[:4]], -1, (0, 255, 0), -line_width)
    # draw pillars in blue color
    for i, j in zip(range(4), range(4, 8)):
        img = cv2.line(img, tuple(proj_pts[i]), tuple(
            proj_pts[j]), (255), line_width)
    # draw top layer in red color
    img = cv2.drawContours(img, [proj_pts[4:]], -1, (0, 0, 255), line_width)

    return img


def axis_select(input, scale):
    if input == 'cube':
        axis = np.float32([[0, 0, 0], [0, scale, 0], [scale, scale, 0], [scale, 0, 0],
                           [0, 0, -scale], [0, scale, -scale], [scale, scale, -scale], [scale, 0, -scale]])
    elif input == 'line':
        axis = np.array([[scale, 0, 0], [0, scale, 0], [0, 0, scale]],
                        dtype=np.float32).reshape(-1, 3)
    return axis


# def get_reproj_error(objpoints, imgpoints):
#     mean_error = 0
#     for i in range(len(objpoints)):
#         imgpoints2, _ = cv2.projectPoints(
#             objpoints[i], rvecs[i], tvecs[i], mtx, dist)
#         error = cv2.norm(imgpoints[i], imgpoints2, cv2.NORM_L2)/len(imgpoints2)
#         mean_error += error
#     print("total error: {}".format(mean_error/len(objpoints)))


if __name__ == "__main__":
    scale = 130
    a = 7
    b = 5
    imgs_path = '../images/snapper/*.png'
    ret, mtx, dist, newcameramtx, roi, _, _ = get_intrinsics(
        imgs_path, a, b, scale, visulaize=True)
    ic(mtx)
    ic(newcameramtx)
    ic(dist)
    ic(roi)
    # ret, rvecs, tvecs = get_extrinsics(imgs_path, a, b, scale, mtx, dist)
    # ic(tvecs)
    # ic(rvecs)
    undistorted_img = undistort(
        imgs_path, mtx, dist, newcameramtx, roi, visualize=True)
