from python_vicon import PyVicon

# Vicon Tracker retrieves objects from the vicon system
# these objects possess detailed information about the location/orientation of the object
# and the different points this object is composed of


class ObjectTracker():

    def connect(self):
        # vicon computer address
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

    # retrieves the marker names of a given obejct
    def aquire_Object_Marker(self, object_name=''):
        self.aquire_Frame()
        try:
            return list(self.client.markerNames(object_name))
        except:
            print("MarkerNames: Name not found in subjects")

    # retrieves the marker positions of a given obejct
    def aquire_Object_MarkerPositions(self, object_name=''):
        self.aquire_Frame()
        try:
            return list(self.client.markerPositions(object_name))
        except:
            print("MarkerPositions: Name not found in subjects")

    # retrieves the translation of a given obejct
    def aquire_Object_Trans(self, object_name=''):
        self.aquire_Frame()
        try:
            return list(self.client.translation(object_name))
        except:
            print("AquireObject: Name not found in subjects")

    # retrieves the rotation (quaternion) of a given obejct in the form X,Y,Z,W
    def aquire_Object_RotQuaternion(self, object_name=''):
        self.aquire_Frame()
        try:
            return list(self.client.rotation_quaternion(object_name))
        except:
            print("AquireObject: Name not found in subjects")

    # retrieves the rotation (Euler) of a given obejct
    def aquire_Object_RotEuler(self, object_name=''):
        self.aquire_Frame()
        try:
            return list(self.client.rotation_euler(object_name))
        except:
            print("AquireObject: Name not found in subjects")

    # retrieves all currently subsribed objects
    def aquire_subjects(self):
        self.aquire_Frame()
        return self.subjects

    # loads the information of a captured frame from the vicon system
    def aquire_Frame(self):
        try:
            self.client.frame()
            self.subjects = self.client.subjects()
            return 0
        except:
            print("Error while getting frame()")


if __name__ == "__main__":
    object_name = 'aruco_4'

    ob = ObjectTracker()

    ob.connect()
    ob.aquire_Frame()
    print(ob.subjects)
    print(ob.aquire_Object_Marker(object_name))
    print(ob.aquire_Object_MarkerPositions(object_name))

    ob.disconnect()
