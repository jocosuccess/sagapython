# SPClassObject
# this is the ClassObject root object for all classes
# 
# The SPClassObject is called with a self object that is any of the following:
# Ordinary object, SPClass object, SPMetaclass object, SPMetaMetaClass object. 
#
# Because SPClassObject has type SPMetaClass, it is callable as an object

from sagapythonglobals import *
from CMILOID import CMIJSONEncoder
import CMI
import sagapythonself

@dataclass(frozen=True)
class cMIClassObjectConst:
    dummy = 0
CMIClassObjectConst = cMIClassObjectConst()

# NewObject creates a new object in the CMI database
# It takes an OID for the new object.
# It checks first if the object exists.
# Returns False if the object already exists.
# Otherwise returns true.
def NewObject(self, loid, owner, idatasize):
    if CMI.IsObject(loid) == True:  return False

    idata = [None] * idatasize

    # set type and owner here  - type is self which is usually SPMetaClass
    # ClassObject fields are always instance 0.  That is, all class and objects
    # must inherit from ClassObject.  GetLinearization can enforce this.
    # The type and owner are set explicitly here. There isn't any methods for this,
    # and the field table flags these as read-only
    # idata[idataindex][CMIConst.CMIFieldIndex]

    objtype = sagapythonself.ClsObjVar.GetLOID(self)
    objcmidata =  {
        CMIConst.CMIType: objtype, 
        CMIConst.CMIOwner: owner
    }
    jobjcmidata = CMIJSONEncoder.encode(objcmidata)

    objdataentry = [None] * CMIConst.CMIIDataSize       # CMI fields and local python objects
    objdataentry[CMIConst.CMIFieldIndex] = base64.b64encode(jobjcmidata.encode()).decode()

    idata[CMIConst.CMIClassObjectClassIndex] = objdataentry
     
    newobjhandle = CMI.CreateObject(loid)
    CMI.WriteObject(newobjhandle, idata)
    objentry = sagapythonself.GetObjectEntry(loid)  
    objentry.modified = True                # forces the new object to be written out to the database with new changes       
    return True

# will add more methods as we go here    




