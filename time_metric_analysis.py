from matplotlib import pyplot as plt
import csv
import os
import numpy as np
from datetime import datetime
import time

def main():
    data = []
    times = []
    with open(os.path.join('images', 'timesysnc_trials', 'all_cam_low_speed', 'trial_1', 'slow_speed_3_multi.csv')) as f:
        reader = csv.reader(f, delimiter='\t')
        for row in reader:
            position = row[1].replace('[','').replace(']','')
            poses = [float(x) for x in position.split(';')]

            if abs(poses[0]) > 0.1:
                data.append(poses)
                timestamp = row[3].replace("'", '')
                timestamp = datetime.strptime(timestamp, '%d-%m-%Y %H:%M:%S %f')
                unixtime = time.mktime(timestamp.timetuple())
                times.append(unixtime)

    data = np.array(data)

    plt.scatter(range(len(data)), data[:, 1])
    plt.show()


    speed = []
    last_position = np.array([0,0,0])
    last_time = times[0] - 1
    for position, timestep in zip(data, times):
        offset = np.linalg.norm(position - last_position)
        time_diff = timestep - last_time + 1e-10

        speed.append(offset/time_diff)

        last_position = position
        last_time = timestep

    plt.scatter(range(len(speed)), speed)
    plt.show()


if __name__ == "__main__":
    main()