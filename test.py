from multiprocessing import Pool
import cv2


def test(data):
    cv2.CALIB_FIX_K1 = 1
    print(data)
    return True


with Pool(5) as p:
    res = p.map(test, [1, 2, 3])
