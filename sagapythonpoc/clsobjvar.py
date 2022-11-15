# ClsObjVar

# global dictionary of stub proxy classes
# import collections
from typing import *
from sagapythontypes import *
from cmilib import *

class CMIMethodType:
    "Method call proxy to CMI layer"

    # func will be the callable temporary object
    # created in the getattribute call
    # obj is the instance of the owning object instance,
    # in this case, the stub object instance
    # thus when the callable calls the function
    # it will call it with the first parameter as the obj
    # which is the correct self. 
    # We can then insert any additional info desired in the args list
    # expect cmiargs to be an object that is received from the CMI layer
    # from the stub getattribute handling
    def __init__(self, funccallable, stubobj, cmicontext):
        self.__func__ = funccallable
        self.__self__ = stubobj
        self.__cmiargs__ = cmicontext

    def __call__(self, *args, **kwargs ):
        func = self.__func__
        obj = self.__self__
        cmicontext = self.__cmicontext__
        return func(obj, cmicontext, *args, **kwargs)

# CMIFuncCall and CMIFuncSend can probably be functions instead
# of callable objects, but don't think there is much difference here
class CMIFuncCall:
    def __call__(self, cmicontext, *args, **kwargs):
    # verify arguments passed, here. Uses variadic approach
    # CMIArgsValidate(cmi, *args, **kwargs)
    # if valid, make CMI call here
        return CMICall(self.objid, cmicontext, *args, **kwargs)

class CMIFuncSend:
    def __call__(self, cmicontext, *args, **kwargs):
    # verify arguments passed, here. Uses variadic approach
    # CMIArgsValidate(cmi, *args, **kwargs)
    # if valid, make CMI send here
        return CMISend(self.objid, cmicontext, *args, **kwargs)

def CMIFuncGetField(self, cmicontext):
    return CMIGetField(self.objid, cmicontext)

def CMIFuncSetField(self, cmicontext, value):
    # validate type of value against field signature
    return CMISetField(self.objid, cmicontext, value)


class ClsObjVar:
    """ ClsObjVar proxy reference object for CMI  objects

    Dynamically creates a temp object for a method call,
    or a field access based on finding the method or field name
    in the ancestry tree, reading the CMI structures.
    Then verifies the arguments against the signatures
    
       """

    # When creating a ClsObjVar, the obj it is a proxy for may not
    # exist yet.  It is not an error to have a reference before 
    # creating the object.
    def __init__(self, objid):
        object.__setattr__(self, "call", True)
        if isinstance(objid, cmioid):
            object.__setattr__(self, "objid", objid)
        else:
            if len(objid) != SIZE_OID:
                raise RuntimeError("Invalid ObjectID size")
            object.__setattr__(self, "objid", cmioid(objid))

    # every method call or field read will use getattribute - overrides all others
    # passes in the name of the method or field. Use to lookup CMI info
    def __getattribute__(self, name: str):
        oid = object.__getattribute__(self, "objid")
        cmicontext = CMIResolve(oid, name)

        if cmicontext == None:
            raise RuntimeError("NotYetImplemented")

        if cmicontext.mtd == True:
            if(object.__getattribute__(self, "call") == True):  
                obj = CMIFuncCall()    
                return CMIMethodType(obj, self, cmicontext)
            else:
                obj = CMIFuncSend()
                object.__setattr__(self, "call", True)            
                return CMIMethodType(obj, self, cmicontext)
        else:
            # CMI Field read
            return CMIFuncGetField(self, cmicontext)

    def __setattr__(self, field, value):
        oid = object.__getattribute__(self, "objid")
        cmicontext = CMIResolve(oid, field)

        if cmicontext == None:
            raise RuntimeError("NoFieldByThatName")

        if cmicontext.mtd == True:
            raise RuntimeError("IllegalAssignmentToMethodAttempted")

        CMIFuncSetField(self, cmicontext, value)



    # by default, the ClsObjVar stub always does a call in account context
    # However, it can be called as a callable first, and set to send.
    # This is reset on each call, such that it needs to be used everytime explicitly
    # Technically, it could be returned, and used later, but is reset on the
    # getattribute
    def __call__(self, call=True):             
            self.call = call
            return self
