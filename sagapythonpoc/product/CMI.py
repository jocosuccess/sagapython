# CMI.py
#
# APIs for SagaPython code to access the CMI.
# This layer is intended to be Python code.
# The layers below it are intended to be a GO library for general use in
# the future.  Currently everything is Python.
# Athough could make an extra layer for indirection, for final product
# that is just a waste of a call.
from dataclasses import dataclass
from typing import Final, Union
import sagapythonglobals
import ObjectTable
from CMILOID import *
import ObjectDataBase

@dataclass(frozen=True)
class cMIObjectTableConst:
    CMILOID = 0
    CMIDATA = 1

CMIObjectTableConst = cMIObjectTableConst()

def GetInstanceData(handle: int, idataindex: int) -> Union[str, str]:
    # access the loaded object list by handle, which is the instance data
    # as a list object with strings
    # access the idataindex entry of the list object and return the list object of 2 strings
    if len(ObjectTable.statetable) < handle or 0 > handle:
        raise RuntimeError("CMI object handle out of range")

    return ObjectTable.statetable[handle][CMIObjectTableConst.CMIDATA][idataindex]
    

# reads the object from the database as an unstructured byte array.
# then does a first JSON decode so that it is a list of strings.
# stores the list as an object in a list of objects.
# returns the index as the handle
# Note: need to determine what is intended to be passed as the OID here.
# Should be of type LOID only.
# LoadObject does not check if the object has been loaded previously.
# If an object is loaded multiple times, each load will have a different handle
# This is unlikely to be intended behavior.
def LoadObject(loid : LOID, default):
    if not isinstance(loid, LOID):
        RuntimeError("Internal Error: oid must be of type OID")

    handle = default

    # attempt to read oid from the database
    # tbd - returns a byte array which is actually the JSON instance data list.
    # on failure return default -- which is usually the null object
    objstate = ObjectDataBase.read(loid.OIDbytes())
    if not isinstance(objstate, str):
        objstate = objstate.decode()

    if objstate != None:
        newobj = CMIJSONDecoder.decode(objstate)  # decodes the JSON syntax into python lists
        handle = len(ObjectTable.statetable)
        newstate = [None] * 2
        newstate[CMIObjectTableConst.CMILOID] = loid
        newstate[CMIObjectTableConst.CMIDATA] = newobj
        ObjectTable.statetable.append(newstate)

    return handle

# bootstrap function, only used once. 
# In production code could be used externally and never included.
# part of initial database only.
def ClearObjectTable():
    ObjectTable.statetable = []

def GetObjectTable():
    return ObjectTable.statetable


# Writes the idata object to the database by doing a JSON encode on
# the object, and writing the result to the database.
# The object must be encodable as JSON. It is expected to be 
# a list object containing base64 encoded strings.
def WriteObject(handle, idata):
    jdata = CMIJSONEncoder.encode(idata)

    # might have to encode as bytes before writing
    # write to object database
    ObjectDataBase.write(ObjectTable.statetable[handle][CMIObjectTableConst.CMILOID].OIDbytes(), jdata)

def InstanceDataLen(handle) -> int:
    return len(ObjectTable.statetable[handle][CMIObjectTableConst.CMIDATA])
    
# CreateObject returns a new handle for a new CMI object for passed in OID
# Does not have any instance data.
# Returns False if already exists
def CreateObject(loid: LOID):
    if ObjectDataBase.Exists(loid.OIDbytes()) == True:
        return -1
    
    if ObjectDataBase.NewObject(loid.OIDbytes()) == False:
        raise RuntimeError("ObjectDataBase internal error, can not create new object")

    handle = len(ObjectTable.statetable)
    newstate = [None] * 2
    newstate[CMIObjectTableConst.CMILOID] = loid
    newstate[CMIObjectTableConst.CMIDATA] = None
    ObjectTable.statetable.append(newstate)

    return handle

# Checks if the object exists in the current database
def IsObject(loid: LOID):
    if ObjectDataBase.Exists(loid.OIDbytes()):
        return True
    return False


def Listen():
    pass

    
def SendMessage(callinfo, currclass, cmiobject, readwriteflag, fieldname, arg) -> int:
    pass

def PostMessage(callinfo, currclass, cmiobject, readwriteflag, fieldname, arg) -> int:
    pass

# returns the constant URL for the SagaPython Runtime. 
def GetLanguageRuntime():
    return (sagapythonglobals.CMIConst.CMIRuntimeURL)

# fake CMI self handle stack 
# should be in shared memory
selfstack = [None]

def pushcontext(handle: int, runtime: str):
    selfstack.append([handle, runtime])

def popcontext() -> Union[int, str]:
    un = selfstack.pop()
    return un[0], un[1]



    