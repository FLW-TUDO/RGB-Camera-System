#!python
# PyVicon class implementation
# Written for the EagleEye project at the University of South Australia
#
# 2015-09-05
# Gwilyn Saunders
# 
# Wraps the static functions made in the .cpp into a Python class object.
# 

import pyvicon


class PyVicon:
    SM_ClientPull = 0
    SM_ClientPullPreFetch = 1
    SM_ServerPush = 2
    
    def __init__(self):
        # create client capsule
        # store version
        self._c = pyvicon.new_client()
        self.__version_tuple__ = pyvicon.version(self._c)
        self.__version__ = "{}.{}.{}".format(
                                self.__version_tuple__[0],
                                self.__version_tuple__[1],
                                self.__version_tuple__[2])
    
    def __del__(self):
        # explicitly deleting probably does nothing
        # I don't know how to clean up a pyCapsule
        # assume it's automatic..?
        del self._c
    
    def connect(self, ip, port=801, defaults=True):
        stat = pyvicon.connect(self._c, "{}:{}".format(ip, port))
        if stat and defaults:
            pyvicon.enableSegmentData(self._c)
            pyvicon.enableMarkerData(self._c)
            pyvicon.setStreamMode(self._c, self.SM_ClientPull)
        return stat
    
    def disconnect(self):
        return pyvicon.disconnect(self._c)
    
    def isConnected(self):
        return pyvicon.isConnected(self._c)
    
    def subjectCount(self):
        return pyvicon.subjectCount(self._c)
    
    def subjectName(self, index):
        return pyvicon.subjectName(self._c, index)
    
    def subjects(self):
        return pyvicon.subjects(self._c)
    
    def rotation(self, name):
        return pyvicon.globalRotation(self._c, name)

    def rotation_quaternion(self, name):
        return pyvicon.globalRotationQuaternion(self._c, name)

    def rotation_euler(self, name):
        return pyvicon.globalRotationEuler(self._c, name)
    
    def translation(self, name):
        return pyvicon.globalTranslation(self._c, name)
    
    def frame(self):
        return pyvicon.frame(self._c)
    
    ## ONLY SUPPRTED IN VICON 1.3+
    #def frameRate(self):
    #    return pyvicon.frameRate(self._c)
    
    def markerStatus(self, name):
        return pyvicon.markerStatus(self._c, name)
    
    def setStreamMode(self, streamMode):
        return pyvicon.setStreamMode(self._c, streamMode)
    
    def enableSegmentData(self, b=True):
        if b: return pyvicon.enableSegmentData(self._c)
        else: return pyvicon.disableSegmentData(self._c)
    
    def hasSegmentData(self):
        return pyvicon.hasSegmentData(self._c)
    
    def enableMarkerData(self, b=True):
        if b: return pyvicon.enableMarkerData(self._c)
        else: return pyvicon.disableMarkerData(self._c)
    
    def hasMarkerData(self):
        return pyvicon.hasMarkerData(self._c)

    def markerNames(self, name):
        return pyvicon.markerNames(self._c, name)

    def markerPositions(self, name):
        return pyvicon.markerpositions(self._c, name)

if __name__ == "__main__":
    client = PyVicon()
    print('Client version: ' + client.__version__)
    print('Is connected: ' + str(client.isConnected()))
    print('Enable segement data: ' + str(client.enableSegmentData()))
    print('Has segment data: ' + str(client.hasSegmentData()))
    print('Client connect to 129.217.152.123:801: ' + str(client.connect('129.217.152.123', 801)))
    #print client.frameRate()
    if client.isConnected():
        print('Enable marker data: ' + str(client.enableMarkerData()))
        print('Has marker data: ' + str(client.hasMarkerData()))
        print('Is connected: ' + str(client.isConnected()))
        client.frame()
        subjects = client.subjects()
        print('Subjects: ' + str(subjects))
        print(client.translation(subjects[1]))
    print('Disconnect: ' + str(client.disconnect()))
    
    exit(0)
