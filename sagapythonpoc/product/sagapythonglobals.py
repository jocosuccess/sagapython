# sagapythonglobals.py
#
# These are equivalent to constants.  Python doesn't do constants
from dataclasses import dataclass
import base64
import __future__
from CMILOID import *

# the 3 base classes for instance data are linear in the order:
# object, headclass, sagapythonclass.
# The headclass data is only present in class object.
# the sagapythonclass data is only present in sagapython class objects.
# The headclass only contains the linearization table for class MRO inheritance
# It is kept separate from the sagapython class so that the only dependencies
# on JSON for all objects is the fields of the classobject instance,
# which is the type of the object, and linearization table which is the
# headclass instance data.
@dataclass(frozen=True)
class cMIConst():
    # instance indices for builtin classes, if inheritance ever changes, these need to reflect that
    CMIClassObjectClassIndex = 0
    CMIClassLinearizationIndex = 1
    CMIClassRuntimeIndex = 2
    CMIClassIndex = 3
    CMIMetaClassIndex = 4
    CMIMetaMetaClassIndex = 5

    CMIExtendedMethodTable = False # for future implementation
    CMILOIDType = '$O' # JSON object name for serialized LOID types

    MethodReturnValue = "retvalue"
    MethodArgsList = "argslist"

    # loids for base classes common to all runtimes not just sagapython 
    CMINullObject =   LOID(bytes.fromhex('00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00'))
    CMIClassObject =  LOID(bytes.fromhex('00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 01'))
    CMIClassLinearization = LOID(bytes.fromhex('00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 02'))
    CMIClassRuntime = LOID(bytes.fromhex('00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 03'))

    # loids for base classes specific to sagapython
    SPClassObject = CMIClassObject
    SPClass =         LOID(bytes.fromhex('00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 04'))    
    SPMetaClass =     LOID(bytes.fromhex('00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 05'))
    SPMetaMetaClass = LOID(bytes.fromhex('00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 06'))

    SPClassAccount =  LOID(bytes.fromhex('00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 07'))
    SPSystemAccount = LOID(bytes.fromhex('00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 08'))
    BaseLOID =        LOID(bytes.fromhex('00 BE EF BE EB 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00'))

    CMIRuntimeURL = "file:///SagaPython"

    # global to all CMI objects independent of language
    CMIFieldIndex = 0
    PythonObjectsIndex = 1
    CMIIDataSize = 2
    CMIType = "t"   # global to all CMI objects independent of language runtime.
    CMIOwner = "w"  # global to all CMI objects independent of language runtime

CMIConst = cMIConst()

# global for null to avoid recreating repeatedly
null = object()

# global for all CMI objects -- to be language runtime independent
# On reaching ClassObject methods or fields not present return NYI.
NYI = CMIConst.CMINullObject

# Sent at startup for CMI to use for return messages.
# should be viewed as immutable
CMIRuntimeIndex = None

# Callinfo tbd -- must include the runtime language index from the CMI
# the return message queue
# the message command
# probably other info
# When a message is received, 
class CallInfo:
    def __init__(self, index, mqueue, mcommand):
        self.sourceruntimeindex = index
        self.mqueue = mqueue
        self.mcommand = mcommand

# global prefix for SagaPython builtin functions
SPBuiltin = "SP_"

class cMIData:
    def __init__(self):
        self.ObjectTableOIDMap = dict() # indexed by OID of CMIObjectTableEntry's
        self.ObjectTableHandleMap = dict() # indexed by handle returned from CMI
        self.ObjectTableList = list()  # indexed by integer for fast lookup of CMIObjectTableEntry's

        self.SagaPythonObjectList = list() # used as an index for the CMI context stack

        # The following is more likely to be internal to the CMI, and in shared memory
        # For the moment, since we only have one runtime language, it's in Python
        self.LanguageRuntimeEntry = dict() # has the runtime name, runtime message queue, whatever else is needed
        self.LanguageRuntimeList = list()  # list of runtime entries. The CMI reads the runtime name from the metaclasses

        self.CleanGlobals = dict()
        self.CleanSysModules = dict()

    def setglobals(self, glbls, modules):
    # the following are set one time at transaction app startup
        self.CleanGlobals = glbls
        self.CleanSysModules = modules

    def getglobals(self):
        return self.CleanGlobals, self.CleanSysModules


CMIData = cMIData()

# each entry is a list of dictionary objects for the runtime dynamic transaction data for the SagaPythonSelf objects
# Dict includes the current sys modules, globals, the current locals dictionary if needed. current self object -
DynamicObjectInfo = dict()
DynamicObjectList = list() # list of DynamicObjectInfo as a stack - will be CMI API for shared memory

