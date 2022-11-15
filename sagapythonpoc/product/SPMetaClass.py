# SPMetaClass -- the "ClassClass" for the CMI classes written in SagaPython
#
# This is a set of functions written as though they are CMI methods,
# but they are hardcoded in to the SagaPython Application, in the globals
# and passed in to all the execs by the SagaPythonSelf dispatch
# They are passed a SagaPythonSelf object, so they look the same as CMI methods.  
# The methodtable for the CMIMetaClass references these as builtins.


# Called by the DoMethod from CMIClass.ClassTableEntry()'s
# Creates a new object, the self is the class, and the
# type of the class is the metaclass

######################################################
# Creating new objects
# The new method take the class of the object to create as the self object.
# It gets the size of the instance data for the object
# from the linearization table of the class as the Lintab field
# Then creates a new object with a self call
# Then creates a new ClsObjVar() for the object, and does an __init__
# call on it.  This calls the class's __init__ with the new object as the self.
#
# The CMI looks at the Language Runtime field of the CMIMetaClass
# to determine that the new message should be delivered to the
# SagaPython runtime and the CMIMetaClass as the type of the current class.

from dataclasses import dataclass
import pickle
import base64
from sagapythonglobals import *
import CMI
import sagapythonself
import SPClassLinearization
import SPClassRuntime
import SPClass

@dataclass(frozen=True)
class sPMetaClassConst:
    dummy = 0
SPMetaClassConst = sPMetaClassConst()

# SPMetaClass New makes new objects from classes
def New(self, owner, *args):
    # self is the class object
    # *args is the tuple of arguments passed in for the new object
    # these are not looked at by New, only the class'es init method
    # the argument types are checked only on sending the init method
    # Get a new loid first

    # Get a new loid first
    ownerobj = sagapythonself.ClsObjVar(owner)
    if ownerobj == None:
        raise RuntimeError("Owner LOID not an object: All objects must have an account owner")

    newloid = ownerobj.NewLOID()
    if newloid == None:
        raise RuntimeError("Internal Error: failed generating a new LOID for the new object")

    # Get the linearization table
    lintab = self.__member(SPClassLinearization.CMIClassLinearizationConst.Lintabl).fld

    # Get a new object with the new loid
    if self.NewObject(newloid, owner, len(lintab)) == False:
        raise RuntimeError("Object Creation Error: LOID already exists")  # shouldn't happen in general

    # create a clsobjvar for the new object
    objvar = sagapythonself.ClsObjVar(newloid)

    # call __init__ with the arguments. Note this is the class init, not a metaclass method
    try:
        objvar.__init__(args)
    except:
        pass

    sagapythonself.SetModified(newloid)
    sagapythonself.WriteObjectEntry(newloid)
    return [newloid]


# SPMetaClass NewInit is expected to be called from a MetaMetaClass object.
def NewInit(self, newloid, baselist, fieldtable, methodtable, importlist, classfinalflag, pyobjects, lintab):

    # initialize the fields of the new object with self calls for allowing subclass overrides.
    # create a clsobjvar for the new object
    objvar = sagapythonself.ClsObjVar(newloid)

    # set linearization table - no extra call here - only metametaclass subclasses can mess with it,
    # not the metaclass of the new object
    objvar.__member(SPClassLinearization.CMIClassLinearizationConst.Lintabl).fld = lintab

    # set runtime name - handled in ClassRuntime - if metaclass is subclassed, can be modified
    # but ClassRuntime does a GetLanguageRuntimeURL
    objvar.__member(SPClassRuntime.CMIClassRuntimeConst.URL).fld = CMI.GetLanguageRuntime()

    # - importobjects is the list of ClassImport instances that
    # must be loaded before a method can be executed by the class
    # - pyobjects are the CMI class objects that are not CMI methods
    # or CMI fields. They are in a dictionary, and are pickled/base64 encoded
    # when stored.  Currently these are readonly for the object instances,
    # initialized at class creation and stored in the pyobjects dictionary
    # - baselist is the baseclass list for the MRO.  Technically not needed
    # for inheritance operation, but might be something we need to be able
    # to read in the future.

    # setup the class's fields in its instance data
    pb = None
    if pyobjects != None:
        pb = pickle.dumps(pyobjects)
        pb = base64.b64encode(pb).decode()

    objvar.__member(SPClass.SPClassConst.BaseClassList).fld = baselist
    objvar.__member(SPClass.SPClassConst.FieldTable).fld = fieldtable
    objvar.__member(SPClass.SPClassConst.MethodTable).fld = methodtable
    objvar.__member(SPClass.SPClassConst.Pyobjects).fld = pb
    objvar.__member(SPClass.SPClassConst.ImportObjectsList).fld = importlist
    objvar.__member(SPClass.SPClassConst.ClassFinalFlag).fld = classfinalflag

    


    




