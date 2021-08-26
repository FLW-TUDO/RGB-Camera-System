// 
// Vicon python bindings
// Written for the EagleEye project at the University of South Australia
// 
// 2015-09-18
// Gwilyn Saunders
//
// Exposes a subset of the C++ Client class as Python functions.
// 

#include <Python.h>
#include <string>
#include "Client.h"

using namespace ViconDataStreamSDK;
using namespace CPP;

static PyObject* ViconError;

static PyObject* pyvicon_newclient(PyObject* self, PyObject* args) {
    //create the client, wrap it, return it
    return PyCapsule_New(new Client(), NULL, NULL);
}

static PyObject* pyvicon_version(PyObject* self, PyObject* args) {
    //inputs
    PyObject* capsule;
    
    //parse
    if (!PyArg_ParseTuple(args, "O", &capsule)) return NULL;
    Client* client = (Client*)PyCapsule_GetPointer(capsule, NULL);
    
    //get, return
    Output_GetVersion out = client->GetVersion();
    return Py_BuildValue("III", out.Major, out.Minor, out.Point);
}

// returns true if there is an exception to raise
static bool handleError(Result::Enum result) {
    switch (result) {
        case Result::Success:
            return false; //keep going!!
        case Result::ClientAlreadyConnected:
            PyErr_SetString(ViconError, "PyVicon: Client already connected");
            return true;
        case Result::NotConnected:
            PyErr_SetString(ViconError, "PyVicon: Client not connected");
            return true;
        case Result::ClientConnectionFailed:
            PyErr_SetString(ViconError, "PyVicon: Client connected failed");
            return true;
        case Result::InvalidHostName:
            PyErr_SetString(ViconError, "PyVicon: Invalid host name");
            return true;
        case Result::InvalidIndex:
            PyErr_SetString(ViconError, "PyVicon: Invalid index");
            return true;
        case Result::InvalidSegmentName:
            PyErr_SetString(ViconError, "PyVicon: Invalid segment name");
            return true;
        case Result::InvalidSubjectName:
            PyErr_SetString(ViconError, "PyVicon: Invalid subject name");
            return true;
        case Result::NoFrame:
            PyErr_SetString(ViconError, "PyVicon No frame - hint: if client.frame(): ... ");
            return true;
        default:
            PyErr_SetString(ViconError, "PyVicon: Unknown error - sorry!");
            return true;
    }
}

//--------------  Connect/disconnect/isConnected functions -------------

static PyObject* pyvicon_connect(PyObject* self, PyObject* args) {
    //inputs
    PyObject* capsule;
    char* address;
    
    //parse
    if (!PyArg_ParseTuple(args, "Os", &capsule, &address)) return NULL;
    Client* client = (Client*)PyCapsule_GetPointer(capsule, NULL);
    
    //thread waits here
    Output_Connect out;
    Py_BEGIN_ALLOW_THREADS
    out = client->Connect(address);
    Py_END_ALLOW_THREADS
    
    //true if connected, false if failed
    switch (out.Result) {
        case Result::Success:
            Py_RETURN_TRUE;
        case Result::ClientAlreadyConnected:
            Py_RETURN_TRUE;
        case Result::ClientConnectionFailed:
            Py_RETURN_FALSE;
        default:
            break;
    }
    
    //raise errors for everything else
    if (handleError(out.Result)) return NULL;
    
    //catch the rest
    Py_RETURN_FALSE;
}

static PyObject* pyvicon_disconnect(PyObject* self, PyObject* args) {
    //inputs
    PyObject* capsule;
    
    //parse
    if (!PyArg_ParseTuple(args, "O", &capsule)) return NULL;
    Client* client = (Client*)PyCapsule_GetPointer(capsule, NULL);
    
    //dumb disconnect, who needs errors for this?
    client->Disconnect();
    Py_RETURN_NONE;
}

static PyObject* pyvicon_isconnected(PyObject* self, PyObject* args) {
    //inputs
    PyObject* capsule;
    
    //parse
    if (!PyArg_ParseTuple(args, "O", &capsule)) return NULL;
    Client* client = (Client*)PyCapsule_GetPointer(capsule, NULL);
    
    //get, return
    if (client->IsConnected().Connected)
        Py_RETURN_TRUE;
    else
        Py_RETURN_FALSE;
}

//------------------------- settings functions ------------------------
//it's all a bit repetitive after here - compressed for convenience

static PyObject* pyvicon_enablesegmentdata(PyObject* self, PyObject* args) {
    PyObject* capsule;
    if (!PyArg_ParseTuple(args, "O", &capsule)) return NULL;
    Client* client = (Client*)PyCapsule_GetPointer(capsule, NULL);
    
    if (client->EnableSegmentData().Result == Result::Success)
        Py_RETURN_TRUE;
    else
        Py_RETURN_FALSE;
}


static PyObject* pyvicon_disablesegmentdata(PyObject* self, PyObject* args) {
    PyObject* capsule;
    if (!PyArg_ParseTuple(args, "O", &capsule)) return NULL;
    Client* client = (Client*)PyCapsule_GetPointer(capsule, NULL);
    
    if (client->DisableSegmentData().Result == Result::Success)
        Py_RETURN_TRUE;
    else
        Py_RETURN_FALSE;
}

static PyObject* pyvicon_issegmentdataenabled(PyObject* self, PyObject* args) {
    PyObject* capsule;
    if (!PyArg_ParseTuple(args, "O", &capsule)) return NULL;
    Client* client = (Client*)PyCapsule_GetPointer(capsule, NULL);
    
    if (client->IsSegmentDataEnabled().Enabled)
        Py_RETURN_TRUE;
    else
        Py_RETURN_FALSE;
}

static PyObject* pyvicon_enablemarkerdata(PyObject* self, PyObject* args) {
    PyObject* capsule;
    if (!PyArg_ParseTuple(args, "O", &capsule)) return NULL;
    Client* client = (Client*)PyCapsule_GetPointer(capsule, NULL);
    
    if (client->EnableMarkerData().Result == Result::Success)
        Py_RETURN_TRUE;
    else
        Py_RETURN_FALSE;
}

static PyObject* pyvicon_disablemarkerdata(PyObject* self, PyObject* args) {
    PyObject* capsule;
    if (!PyArg_ParseTuple(args, "O", &capsule)) return NULL;
    Client* client = (Client*)PyCapsule_GetPointer(capsule, NULL);
    
    if (client->DisableMarkerData().Result == Result::Success)
        Py_RETURN_TRUE;
    else
        Py_RETURN_FALSE;
}

static PyObject* pyvicon_ismarkerdataenabled(PyObject* self, PyObject* args) {
    PyObject* capsule;
    if (!PyArg_ParseTuple(args, "O", &capsule)) return NULL;
    Client* client = (Client*)PyCapsule_GetPointer(capsule, NULL);
    
    if (client->IsMarkerDataEnabled().Enabled)
        Py_RETURN_TRUE;
    else
        Py_RETURN_FALSE;
}

static PyObject* pyvicon_setstreammode(PyObject* self, PyObject* args) {
    //inputs
    PyObject* capsule;
    StreamMode::Enum mode; int input;
    
    //parse
    if (!PyArg_ParseTuple(args, "Oi", &capsule, &input)) return NULL;
    Client* client = (Client*)PyCapsule_GetPointer(capsule, NULL);
    
    //test enum support
    if (input < 0 && input > 2) {
        PyErr_SetString(PyExc_TypeError, "setStreamMode() takes ints (0, 1, 2)");
        return NULL;
    }
    
    //convert to the enum
    switch (input) {
        case 0:
            mode = StreamMode::ClientPull;
            break;
        case 1:
            mode = StreamMode::ClientPullPreFetch;
            break;
        default:
            mode = StreamMode::ServerPush;
    }
    
    //return result
    if (client->SetStreamMode(mode).Result == Result::Success)
        Py_RETURN_TRUE;
    else
        Py_RETURN_FALSE;
}

//------------------------ subject getters ----------------------------

static PyObject* pyvicon_subjectcount(PyObject* self, PyObject* args) {
    PyObject* capsule;
    if (!PyArg_ParseTuple(args, "O", &capsule)) return NULL;
    Client* client = (Client*)PyCapsule_GetPointer(capsule, NULL);
    
    //get
    Output_GetSubjectCount out = client->GetSubjectCount();
    if (handleError(out.Result)) return NULL;
    
    return Py_BuildValue("I", out.SubjectCount);
}

static PyObject* pyvicon_subjectname(PyObject* self, PyObject* args) {
    //inputs
    PyObject* capsule;
    unsigned int index;
    
    //parse
    if (!PyArg_ParseTuple(args, "OI", &capsule, &index)) return NULL;
    Client* client = (Client*)PyCapsule_GetPointer(capsule, NULL);
    
    //get and handle errors
    Output_GetSubjectName out = client->GetSubjectName(index);
    if (handleError(out.Result)) return NULL;
    
    //cast from the silly vicon string type
    std::string sub_name = (std::string)out.SubjectName;
    return Py_BuildValue("s", sub_name.c_str());
}

static PyObject* pyvicon_subjects(PyObject* self, PyObject* args) {
    //inputs
    PyObject* capsule;
    
    //parse
    if (!PyArg_ParseTuple(args, "O", &capsule)) return NULL;
    Client* client = (Client*)PyCapsule_GetPointer(capsule, NULL);
    
    //get number and handle errors
    Output_GetSubjectCount count_out = client->GetSubjectCount();
    if (handleError(count_out.Result)) return NULL;
    
    //get count and create py list
    const unsigned int sub_count = count_out.SubjectCount;
    PyObject* subjects = PyList_New(sub_count);
    
    //collect subject names into the list
    for (unsigned int i=0; i<sub_count; i++) {
        Output_GetSubjectName name_out = client->GetSubjectName(i);
        if (handleError(name_out.Result)) return NULL; //does this mem leak the subjects var?
        
        //cast and insert
        PyList_SetItem(subjects, i, Py_BuildValue("s", ((std::string)name_out.SubjectName).c_str()));
    }
    
    //hope to God the list is full
    return subjects;
}

//--------------------- rotation/translation getters ----------------------

static PyObject* pyvicon_globalrotation(PyObject* self, PyObject* args) {
    //inputs
    PyObject* capsule;
    char* name;
    
    //parse
    if (!PyArg_ParseTuple(args, "Os", &capsule, &name)) return NULL;
    Client* client = (Client*)PyCapsule_GetPointer(capsule, NULL);
    
    //get data, run error checking
    Output_GetSegmentGlobalRotationHelical out = client->GetSegmentGlobalRotationHelical(name, name);
    if (handleError(out.Result)) return NULL;
    
    //let python do the rest, just know it's a set of 3 doubles
    return Py_BuildValue("ddd", out.Rotation[0], out.Rotation[1], out.Rotation[2]);
}

static PyObject* pyvicon_globalrotationquaternion(PyObject* self, PyObject* args) {
    //inputs
    PyObject* capsule;
    char* name;

    //parse
    if (!PyArg_ParseTuple(args, "Os", &capsule, &name)) return NULL;
    Client* client = (Client*)PyCapsule_GetPointer(capsule, NULL);

    //get data, run error checking
    Output_GetSegmentGlobalRotationQuaternion out = client->GetSegmentGlobalRotationQuaternion(name, name);
    if (handleError(out.Result)) return NULL;

    //let python do the rest, just know it's a set of 4 doubles
    return Py_BuildValue("dddd", out.Rotation[0], out.Rotation[1], out.Rotation[2], out.Rotation[3]);
}

static PyObject* pyvicon_globalrotationeuler(PyObject* self, PyObject* args) {
    //inputs
    PyObject* capsule;
    char* name;

    //parse
    if (!PyArg_ParseTuple(args, "Os", &capsule, &name)) return NULL;
    Client* client = (Client*)PyCapsule_GetPointer(capsule, NULL);

    //get data, run error checking
    Output_GetSegmentGlobalRotationEulerXYZ out = client->GetSegmentGlobalRotationEulerXYZ(name, name);
    if (handleError(out.Result)) return NULL;

    //let python do the rest, just know it's a set of 3 doubles
    return Py_BuildValue("ddd", out.Rotation[0], out.Rotation[1], out.Rotation[2]);
}

static PyObject* pyvicon_globaltranslation(PyObject* self, PyObject* args) {
    //inputs
    PyObject* capsule;
    char* name;
    
    //parse
    if (!PyArg_ParseTuple(args, "Os", &capsule, &name)) return NULL;
    Client* client = (Client*)PyCapsule_GetPointer(capsule, NULL);
    
    //get data, run error checking
    Output_GetSegmentGlobalTranslation out = client->GetSegmentGlobalTranslation(name, name);
    if (handleError(out.Result)) return NULL;
    
    //magic, isn't it?
    return Py_BuildValue("ddd", out.Translation[0], out.Translation[1], out.Translation[2]);
}

//------------------------ marker, frame, other --------------------------

static PyObject* pyvicon_frame(PyObject* self, PyObject* args) {
    PyObject* capsule;
    if (!PyArg_ParseTuple(args, "O", &capsule)) return NULL;
    Client* client = (Client*)PyCapsule_GetPointer(capsule, NULL);
    
    if (client->GetFrame().Result == Result::Success)
        Py_RETURN_TRUE;
    else
        Py_RETURN_FALSE;
}

/*
// ONLY SUPPRTED IN VICON 1.3+ (UniSA mechlab is on 1.2?)
static PyObject* pyvicon_framerate(PyObject* self, PyObject* args) {
    PyObject* capsule;
    if (!PyArg_ParseTuple(args, "O", &capsule)) return NULL;
    Client* client = (Client*)PyCapsule_GetPointer(capsule, NULL);
    
    Output_GetFrameRate out = client->GetFrameRate();
    if (handleError(out.Result)) return NULL;
    
    return Py_BuildValue("d", out.FrameRateHz);
}
*/

static PyObject* pyvicon_markercount(PyObject* self, PyObject* args) {
    //inputs
    PyObject* capsule;
    char* name;
    
    //parse
    if (!PyArg_ParseTuple(args, "Os", &capsule, &name)) return NULL;
    Client* client = (Client*)PyCapsule_GetPointer(capsule, NULL);
    
    //get, errors, etc
    Output_GetMarkerCount out = client->GetMarkerCount(name);
    if (handleError(out.Result)) return NULL;
    
    return Py_BuildValue("I", out.MarkerCount);
}

static PyObject* pyvicon_markerstatus(PyObject* self, PyObject* args) {
    //inputs
    PyObject* capsule;
    char* name;
    
    if (!PyArg_ParseTuple(args, "Os", &capsule, &name)) return NULL;
    Client* client = (Client*)PyCapsule_GetPointer(capsule, NULL);
    
    //get, errors, etc
    Output_GetMarkerCount count_out = client->GetMarkerCount(name);
    if (handleError(count_out.Result)) return NULL;
    
    unsigned int total = count_out.MarkerCount;
    unsigned int visible = 0;
    
    for (unsigned int i=0; i<total; i++) {
        Output_GetMarkerName name_out = client->GetMarkerName(name, i);
        if (handleError(name_out.Result)) return NULL;
        
        Output_GetMarkerGlobalTranslation test_out = client->GetMarkerGlobalTranslation(name, name_out.MarkerName);
        if (!test_out.Occluded) 
            visible++;
    }
    
    return Py_BuildValue("II", total, visible);
}

static PyObject* pyvicon_markerpositions(PyObject* self, PyObject* args) {
    //inputs
    PyObject* capsule;
    char* name;
    
    if (!PyArg_ParseTuple(args, "Os", &capsule, &name)) return NULL;
    Client* client = (Client*)PyCapsule_GetPointer(capsule, NULL);
    
    //get, errors, etc
    Output_GetMarkerCount count_out = client->GetMarkerCount(name);
    if (handleError(count_out.Result)) return NULL;
    
    unsigned int total = count_out.MarkerCount;
    PyObject* positions = PyList_New(total);
    
    for (unsigned int i=0; i<total; i++) {
        Output_GetMarkerName name_out = client->GetMarkerName(name, i);
        if (handleError(name_out.Result)) return NULL;
        
        Output_GetMarkerGlobalTranslation out = client->GetMarkerGlobalTranslation(name, name_out.MarkerName);
        PyList_SetItem(positions, i, Py_BuildValue("ddd", out.Translation[0], out.Translation[1], out.Translation[2]));
    }

    return positions; 
}

static PyObject* pyvicon_markernames(PyObject* self, PyObject* args) {
    //inputs
    PyObject* capsule;
    char* name;
    
    if (!PyArg_ParseTuple(args, "Os", &capsule, &name)) return NULL;
    Client* client = (Client*)PyCapsule_GetPointer(capsule, NULL);
    
    //get, errors, etc
    Output_GetMarkerCount count_out = client->GetMarkerCount(name);
    if (handleError(count_out.Result)) return NULL;
    
    unsigned int total = count_out.MarkerCount;
    PyObject* names = PyList_New(total);
    
    for (unsigned int i=0; i<total; i++) {
        Output_GetMarkerName name_out = client->GetMarkerName(name, i);
        if (handleError(name_out.Result)) return NULL;

        PyList_SetItem(names, i, Py_BuildValue("s", ((std::string)name_out.MarkerName).c_str()));
    }

    return names; 
}

//------------------------- aaaaand the rest ----------------------------

//declare the accessible functions
static PyMethodDef ModuleMethods[] = {
     {"new_client", pyvicon_newclient, METH_VARARGS, "Create a client object"},
     {"connect", pyvicon_connect, METH_VARARGS, "Connect to vicon"},
     {"disconnect", pyvicon_disconnect, METH_VARARGS, "Disconnect from vicon"},
     {"isConnected", pyvicon_isconnected, METH_VARARGS, "Connection status"},
     {"subjectCount", pyvicon_subjectcount, METH_VARARGS, "Get a count of subjects"},
     {"subjectName", pyvicon_subjectname, METH_VARARGS, "Get a subject name, given an index"},
     {"subjects", pyvicon_subjects, METH_VARARGS, "Get a list of all subjects"},
     {"globalRotation", pyvicon_globalrotation, METH_VARARGS, "Get global rotation of a subject"},
     {"globalRotationQuaternion", pyvicon_globalrotationquaternion, METH_VARARGS, "Get global rotation of a subject in quaternion coordinates"},
     {"globalRotationEuler", pyvicon_globalrotationeuler, METH_VARARGS, "Get global rotation of a subject in euler coordinates"},
     {"globalTranslation", pyvicon_globaltranslation, METH_VARARGS, "Get global translation of a subject"},
     {"markerCount", pyvicon_markercount, METH_VARARGS, "Get number of markers of a subject"},
     {"markerStatus", pyvicon_markerstatus, METH_VARARGS, "Get total and visible number of markers of a subject"},
     {"frame", pyvicon_frame, METH_VARARGS, "A status thing, call it before retrieving any data"},
     {"setStreamMode", pyvicon_setstreammode, METH_VARARGS, "Stream mode: Pull, PreFetch, Push"},
     {"enableSegmentData", pyvicon_enablesegmentdata, METH_VARARGS, "Enables segment data. Just always use it, I guess."},
     {"disableSegmentData", pyvicon_disablesegmentdata, METH_VARARGS, "Opposite of enableSegmentData, right?"},
     {"hasSegmentData", pyvicon_issegmentdataenabled, METH_VARARGS, "Tests whether SegmentData is enabled."},
     {"enableMarkerData", pyvicon_enablemarkerdata, METH_VARARGS, "Enables marker data. Use this for markerCount."},
     {"disableMarkerData", pyvicon_disablemarkerdata, METH_VARARGS, "Opposite of enableMarkerData"},
     {"hasMarkerData", pyvicon_ismarkerdataenabled, METH_VARARGS, "Tests whether MarkerData is enabled."},
     {"version", pyvicon_version, METH_VARARGS, "Vicon system version"},
     {"markerNames", pyvicon_markernames, METH_VARARGS, "Vicon object marker names"},
     {"markerpositions", pyvicon_markerpositions, METH_VARARGS, "Vicon object marker positions"},
     
     //ONLY SUPPRORTED IN VICON 1.3+
     //{"frameRate", pyvicon_framerate, METH_VARARGS, "Get the current framerate in hertz as a double"},
     
     {NULL, NULL, 0, NULL},
};

static PyModuleDef pyvicon = {
    PyModuleDef_HEAD_INIT,
    "pyvicon",                              // Module name to use with Python import statements
    "Vicon wrapper for python",             // Module description
    0,
    ModuleMethods                           // Structure that defines the methods of the module
};

PyMODINIT_FUNC PyInit_pyvicon(void) {
    //Create the module
    PyObject* m;
    //Python 2
    //m = Py_InitModule("pyvicon", ModuleMethods);
    //Python 3
    m = PyModule_Create(&pyvicon);

    //Create + add ViconError
    ViconError = PyErr_NewException("pyvicon.error", NULL, NULL);
    Py_INCREF(ViconError);
    PyModule_AddObject(m, "error", ViconError);
    return m;
}
