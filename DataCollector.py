from threading import Thread
from Camera.CVBCamera import Camera
from PyVicon.vicon_tracker import ObjectTracker
from threading import Thread
import os, csv, cv2
from datetime import datetime

cameras = [0]  # 0,1,2,3,4,5,6,7
objects = ["klt_01"]
path = "recordings"


class Processor(Thread):
    def __init__(self, index):
        Thread.__init__(self)
        self.name = f"cam_{index}"
        self.imageIndex = 0
        self.running = True

        """
        creates an path for each object with the current recording 
        time and the id of the camera itself
        Like:
        ./recordings/11_11_11 08_11_2021/object_0001/0
        """
        now = datetime.now().strftime("%H_%M_%S %d_%m_%Y")
        self.folder_path = os.path.join(path, now)
        for obj in objects:
            os.makedirs(os.path.join(self.folder_path, obj, "rgb", self.name))

        self.vicon = ObjectTracker()
        self.vicon.connect()
        self.camera = Camera(index)

        self.start()

    def run(self):
        while self.running:
            data = {"image": self.camera.getImage()}
            for obj in objects:
                data[obj] = self.vicon.aquire_Object_MarkerPositions(object_name=obj)

            self.writeData(data)
            self.imageIndex += 1

    def stop(self):
        self.running = False

    """
    data: {
        "image": numpy.array (RGB image)
        "object_0001": list | numpy.array (Marker positions of the object)
    }
    Writes as csv line and an image file for each object present in the scene
    """

    def writeData(self, data):
        for obj in objects:
            path = os.path.join(self.folder_path, obj, "rgb", self.name)
            with open(
                os.path.join(path, "object_data.csv"), "a", newline=""
            ) as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([self.imageIndex, *data[obj]])
            cv2.imwrite(os.path.join(path, f"{self.imageIndex}.png"), data["image"])


if __name__ == "__main__":
    processors = [Processor(index) for index in cameras]
    while True:
        key = cv2.waitKey(1)
        if key == 27:
            break

    for processor in processors:
        processor.stop()
