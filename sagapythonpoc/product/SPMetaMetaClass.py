# SPMetaMetaClass.py 
#
# The class type for SPMetaClass with methods to create new classes
# SPMetaMetaClass inherits from SPMetaClass and overrides New completely
# to make new classes.  
#  
from dataclasses import dataclass

from sagapythonglobals import *
import CMI
import sagapythonself
import SPClassLinearization

@dataclass(frozen=True)
class sPMetaMetaClassConst:
    dummy = 0
SPMetaMetaClassConst = sPMetaMetaClassConst()

def New(self, owner, baselist, fieldtable, methodtable, importlist, classfinalflag, pyobjects):
    """ self is the ClassMetaClass or subclass
        owner is the account to create the class in
        baselist is the ancestor list
        fieldtable is the fields for the new class instances 
        methodtable is the methods for the class
        pyobjects is the dictionary of python objects 
        local to the class object 
        """

    # Get a new loid first
    ownerobj = sagapythonself.ClsObjVar(owner)
    if ownerobj == None:
        raise RuntimeError("Owner LOID not an object: All objects must have an account owner")

    newloid = ownerobj.NewLOID()
    if newloid == None:
        raise RuntimeError("Internal Error: failed generating a new LOID for the new object")

    # Get the linearization
    lintab = self.GetLinearization(newloid.OIDbytes(), baselist)
    if lintab[0] != CMIConst.CMIClassObject:
        raise RuntimeError("Illegal Inheritance: All classes must inherit from ClassObject as base class")

    classlintab = self.__member(SPClassLinearization.CMIClassLinearizationConst.Lintabl).fld

    # Get a new object with the new loid
    if self.NewObject(newloid, owner, len(classlintab)) == False:
        raise RuntimeError("Object Creation Error: LOID already exists")  # shouldn't happen in general

    # create a clsobjvar for the new object
    objvar = sagapythonself.ClsObjVar(newloid)

    # call the new class to let SPMetaClass initialize it
    objvar.init(newloid, baselist, fieldtable, methodtable, importlist, classfinalflag, pyobjects, lintab)

    # self call for metametaclass subclasses, in case they want to do anything else
    # avoids needing a super call in NewInit
    self.init(newloid, baselist, fieldtable, methodtable, importlist, classfinalflag, pyobjects)

    sagapythonself.SetModified(newloid)
    sagapythonself.WriteObjectEntry(newloid)
    return [newloid]

def NewInit(self, newloid, baselist, fieldtable, methodtable, importlist, classfinalflag, pyobjects):
        return True





    
    
        
    
