from glob import glob
import itertools
import numpy as np
import copy
import os
import cv2
assert cv2.__version__[
    0] >= '3', 'The fisheye module requires opencv version >= 3.0.0'

subpix_criteria = (cv2.TERM_CRITERIA_EPS+cv2.TERM_CRITERIA_MAX_ITER, 100, 1e-6)
calibration_flags = cv2.fisheye.CALIB_RECOMPUTE_EXTRINSIC + \
    cv2.fisheye.CALIB_CHECK_COND + cv2.fisheye.CALIB_FIX_SKEW
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.00001)


a = 5   # columns
b = 3   # rows
objp = np.zeros((1, a*b, 3), np.float32)
objp[0, :, :2] = np.mgrid[0:a, 0:b].T.reshape(-1, 2)


def create_points(images):
    objp = np.zeros((1, a*b, 3), np.float32)
    objp[0, :, :2] = np.mgrid[0:a,
                              0:b].T.reshape(-1, 2)
    _img_shape = None

    objpoints = []  # 3d point in real world space
    imgpoints = []  # 2d points in image plane.

    for fname in images:
        img = cv2.imread(fname)
        if _img_shape == None:
            _img_shape = img.shape[:2]
        else:
            assert _img_shape == img.shape[:2], "All images must share the same size."
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Find the chess board corners
        ret, corners = cv2.findChessboardCorners(
            gray, (a, b), cv2.CALIB_CB_ADAPTIVE_THRESH+cv2.CALIB_CB_FAST_CHECK+cv2.CALIB_CB_NORMALIZE_IMAGE)
        # If found, add object points, image points (after refining them)
        if ret == True:
            objpoints.append(objp)
            cv2.cornerSubPix(gray, corners, (3, 3), (-1, -1), subpix_criteria)
            imgpoints.append(corners)

    return objpoints, imgpoints, gray.shape[::-1]


def create_permutations(iterable, n=None):
    permutations = list(itertools.permutations(iterable, r=n))
    for perm in permutations:
        possible_perms = list(itertools.permutations(perm))
        for p_perm in possible_perms:
            if p_perm != perm:
                permutations.remove(p_perm)

    return permutations


def calculate_intrinsics(objpoints, imgpoints, _img_shape):
    N_OK = len(objpoints)
    K = np.zeros((3, 3))
    D = np.zeros((4, 1))
    rvecs = [np.zeros((1, 1, 3), dtype=np.float64) for i in range(N_OK)]
    tvecs = [np.zeros((1, 1, 3), dtype=np.float64) for i in range(N_OK)]
    rms, _, _, _, _ = \
        cv2.fisheye.calibrate(
            objpoints,
            imgpoints,
            _img_shape,
            K,
            D,
            rvecs,
            tvecs,
            calibration_flags,
            (cv2.TERM_CRITERIA_EPS+cv2.TERM_CRITERIA_MAX_ITER, 100, 1e-6)
        )

    return K, D, rms


def evaluate_intrinsics(objpoints, imgpoints, _img_shape):
    _, _, rms = calculate_intrinsics(objpoints, imgpoints, _img_shape)
    return rms

# display on image undistorted to check if the calibration worked


def display_undistored(image, K, D):
    img = cv2.imread(image)
    _img_shape = img.shape[:2]
    DIM = _img_shape[::-1]
    map1, map2 = cv2.fisheye.initUndistortRectifyMap(
        K, D, np.eye(3), K, DIM, cv2.CV_16SC2)
    undistorted_img = cv2.remap(
        img, map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
    cv2.imshow("undistorted", undistorted_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def update(top, value, perm, length=10):
    for index, (val, _) in enumerate(top):
        if value < val:
            top.insert(index, (value, perm))
            _ = top.pop(-1) if len(top) > length else None
            return


if __name__ == "__main__":
    initial_perm_length = 3
    max_perm_length = 7
    top_length = 20

    images = glob('./images/*.jpg')
    objpoints, imgpoints, _img_shape = create_points(images)
    perm_range = list(range(len(objpoints)))
    permutations = create_permutations(perm_range, initial_perm_length)

    print('Running tests for {} permutations'.format(len(permutations)))

    top = [(10., [])]

    # create initial results with only initial_perm_length images each time
    for permutation in permutations:
        new_objpoints = [objpoints[index] for index in permutation]
        new_imgpoints = [imgpoints[index] for index in permutation]
        try:
            rms = evaluate_intrinsics(
                new_objpoints, new_imgpoints, _img_shape)

            update(top, rms, permutation, top_length)
        except cv2.error:
            print('Skipped error.')
            continue

    print('Initial permutations passed. Best permutation: {}'.format(top[0]))

    # append one image to the best images and calculate the improvement
    for run_index in range(max_perm_length - initial_perm_length):
        new_top = [(10., [])]
        for i in range(len(objpoints)):
            for val, perm in top:
                if i not in perm:
                    new_perm = perm + (i,)
                    new_objpoints = [objpoints[index] for index in new_perm]
                    new_imgpoints = [imgpoints[index] for index in new_perm]
                    try:
                        rms = evaluate_intrinsics(
                            new_objpoints, new_imgpoints, _img_shape)

                        update(new_top, rms, new_perm, top_length)
                    except cv2.error:
                        print('Skipped error.')
                        continue

        top = copy.copy(new_top)
        print('Run number {} passed. Best permutation: {}'.format(
            run_index, top[0]))

        # originally <= run_index + initial_perm_length
        # but to try out some longer permutations the initial length was removed
        if len(top[0][1]) <= run_index:
            print('No improvement was reached. Final set has been reached in run number {}.'.format(
                run_index))
            break

    print('Resulting image set:')
    for index in top[0][1]:
        print(images[index])

    new_objpoints = [objpoints[index] for index in top[0][1]]
    new_imgpoints = [imgpoints[index] for index in top[0][1]]

    K, D, _ = calculate_intrinsics(new_objpoints, new_imgpoints, _img_shape)
    display_undistored(images[0], K, D)
