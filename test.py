from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import json

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

with open('./images/chessboard/data.json') as f:
    data = json.load(f)
    x = [point[0] for point in data['1.png']]
    y = [point[1] for point in data['1.png']]
    z = [point[1] for point in data['1.png']]
    ax.scatter(x, y, z)

plt.show()
