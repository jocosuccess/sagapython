# CMIObjectData.py
#
# Definition of what the object data looks like in Python to be read/written in JSON, and written to the object database
#
# Each object consists of instance data for each of the classes in the inheritance tree
# Each instance consists of a list of the CMI instance data, and the local python objects
# The object is then a list of instance data where each instance data is a list entry.
# 
# Before the object can be written out in JSON, any data must be translated to strings
# These are encoded as base64.  The CMI list entry is a dictionary, which is JSON encoded,
# then base64 encoded and then assigned to the list entry.  The Python list entry is a
# python dictionary that is pickled, then base64 encoded, then assigned to the second list entry.
# The entire object instance, when stored to the object database, is JSON encoded of the 
# list of the individual instance lists.  Which looks like a list of lists of 2 entries that
# are both strings. By expecting base64 encoded strings, the CMI makes no further distinctions
# in the object state database.  
#
# When an object is loaded by the CMI, it loads the object in to a list keyed by a returned 
# object handle. The object is loaded in to a global table for future reference during the transaction execution.
# The CMI layer does recognize that the objects are JSON encoded as described.
# The CMI does an initial JSON decode. This is necessary because the CMI must have knowledge of the 
# following:
# object type, object owner, class linearization, runtime URL
# These are found in their respective class instance fields.  Therefore the CMI
# is able to do a base64 decode of the CMI instance fields for those ancestor classes
# and read in the associated JSON syntax.  
# Currently the CMI has no further knowledge of the contents of objects.
# 
#
# ObjectTableEntry and ClassTableEntry are convenience Python classes to manage access
# to the object instance data from the CMI table.  Their main jobs are to cache
# any instance data that has been read in, base64 decoded and JSON decoded for performance,
# and to execute the methods and fields accesses called from the dispatch function.
# 
# ObjectTableEntry = contains a list that is the same size as the object instance list.
# This is used to store the decoded instance data incrementally as needed, from the CMI object
# Note: ideally we should then delete the corresponding data from the CMI instance data list.
# Not clear yet if that is possible. If so, may be a useful memory savings down the road.
# 
# For clearification of instance data structure:
#   instance data list is [entry for each ancestor class in the linearization table]
#   Each classes instance data entry is [CMI fields, Python local objects]
#

from dataclasses import dataclass
from typing import Union
import base64
import io
import pickle
from CMILOID import *
import CMI
from sagapythonglobals import *
#from SPClassObject import *

class ObjectTableEntry:
    def __init__(self, handle, oid, index, idatalen):
        self.idata = [None] * idatalen # decoded list of instance list entries (CMI fields, Python objects)
        self.idatalen = idatalen
        self.handle = handle
        self.oid: LOID = oid
        self.index = index
        self.modified = False
        self.objtype = None
        self.objowner = None

    # returns the entire instance data list.
    # Note: this does not currently unpickle the python objects -- that needs to be added
    def GetAllInstanceData(self):
        for x in range (self.idatalen):
            if self.idata[x] != None:
                continue

            idatalist64 = CMI.GetInstanceData(self.handle, x)
            cmidata = base64.b64decode(idatalist64[CMIConst.CMIFieldIndex])
            cmidata = CMIJSONDecoder.decode(cmidata.decode())
            pydata = base64.b64decode(idatalist64[CMIConst.PythonObjectsIndex])
            self.idata[x] = [cmidata,pydata]

        return self.idata

    def GetCMIInstanceData(self, idataindex):
        if self.idatalen < idataindex:
            raise RuntimeError("Illegal instance data index")  

        pydata = None
        idata = self.idata[idataindex]
        if idata != None: 
            if idata[CMIConst.CMIFieldIndex] != None:
                return idata[CMIConst.CMIFieldIndex]
            
            pydata = idata[CMIConst.PythonObjectsIndex]   # pydata may still be None here

        idatalist64 = CMI.GetInstanceData(self.handle, idataindex)
        if idatalist64 != None:
            cmidata = base64.b64decode(idatalist64[CMIConst.CMIFieldIndex])     # base64.b64decode will take a string
            self.idata[idataindex] = [CMIJSONDecoder.decode(cmidata.decode()), pydata]
        else:
            self.idata[idataindex] = [{}, pydata]
        return self.idata[idataindex][CMIConst.CMIFieldIndex]

    def GetPyInstanceData(self, idataindex):
        if self.idatalen < idataindex:
            raise RuntimeError("Illegal instance data index")  

        cmidata = None
        
        idata = self.idata[idataindex]
        if idata != None: 
            if idata[CMIConst.PythonObjectsIndex] != None:
                return idata[CMIConst.PythonObjectsIndex]

            cmidata = idata[CMIConst.CMIFieldIndex]

        idatalist64 = CMI.GetInstanceData(self.handle, idataindex)
        if idatalist64 != None:
            if idatalist64[CMIConst.PythonObjectsIndex] != None:
                pydata = base64.b64decode(idatalist64[CMIConst.PythonObjectsIndex])
                pydata = pickle.loads(pydata)
                self.idata[idataindex] = [cmidata, pydata]
            else:
                self.idata[idataindex] = [cmidata, null]
        else:
            self.idata[idataindex] = [cmidata, null]
        return self.idata[idataindex][CMIConst.PythonObjectsIndex]

    def WriteCMIInstanceData(self, data, idataindex):
        if self.idatalen < idataindex:
            raise RuntimeError("Illegal instance data index")  

        self.idata[idataindex][CMIConst.CMIFieldIndex] = data
    
    # It is expected that the Python data is a dictionary in general
    def WritePyInstanceData(self, data, idataindex):
        if self.idatalen < idataindex:
            raise RuntimeError("Illegal instance data index")  

        self.idata[idataindex][CMIConst.PythonObjectsIndex] = data

    def GetCMIHandle(self):
        return self.handle
    
    # index in to the ObjectTableList for the SagaPython runtime
    def GetCMIDataIndex(self):
        return self.index  

    def GetCMIClass(self):
        if self.objtype != None:
            return self.objtype
        cmidata = self.GetCMIInstanceData(CMIConst.CMIClassObjectClassIndex)
        self.objtype = cmidata.get(CMIConst.CMIType, null)
        return self.objtype
          









