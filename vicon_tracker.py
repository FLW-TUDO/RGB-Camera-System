from python_vicon import PyVicon


class ObjectTracker():

    def connect(self):
        self.cfg = {
            "ip_address": '129.217.152.31',
            "port": '801'
        }
        self.client = PyVicon()
        self.subjects = []
        print("Connecting to Vicon: {}:{}".format(
            self.cfg["ip_address"], self.cfg["port"]))
        self.client.connect(self.cfg["ip_address"], self.cfg["port"])
        print('Connected successfully!')

        if not self.client.isConnected():
            print("Failed to connect to Vicon! {}:{}".format(
                self.cfg["ip_address"], self.cfg["port"]))
            return 1

    def disconnect(self):
        self.client.disconnect()
        print("Disconneced successfully")
        return 0

    def aquire_Object_Marker(self, object_name=''):
        self.aquire_Frame()
        try:
            return list(self.client.markerNames(object_name))
        except:
            print("MarkerNames: Name not found in subjects")

    def aquire_Object_MarkerPositions(self, object_name=''):
        self.aquire_Frame()
        try:
            return list(self.client.markerPositions(object_name))
        except:
            print("MarkerPositions: Name not found in subjects")

    def aquire_Object(self, object_name=''):
        self.aquire_Frame()
        try:
            return list(self.client.translation(object_name))
        except:
            print("AquireObject: Name not found in subjects")

    def aquire_subjects(self):
        self.aquire_Frame()
        return self.subjects

    def aquire_Frame(self):
        try:
            self.client.frame()
            self.subjects = self.client.subjects()
            return 0
        except:
            print("Error while getting frame()")


if __name__ == "__main__":
    object_name = 'test_box'

    ob = ObjectTracker()

    ob.connect()
    print(ob.aquire_Object_Marker(object_name))

    ob.disconnect()
