import json
import numpy as np

K = np.array([[444.01212317, 0., 317.87966175],
              [0., 442.20562833, 264.72142874],
              [0., 0., 1.]])


with open('./images/chessboard/data.json') as f:
    data = json.load(f)

    for fName in data:
        date = data[fName]

        for point in date:
            res = np.matmul(K, point)
            print(res)
