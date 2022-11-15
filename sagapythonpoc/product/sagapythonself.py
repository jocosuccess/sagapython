# SagaPythonSelf and ClsObjVar class implementation
#
# The self object represents the instance data for a specific ancestor
# class of a specific CMI object instance. Implements the concept of
# a CMI "head class" and a "current class".  The current class
# by definition is an ancestor of the head class or itself.
# ancestry follows the MRO linearization table.
#
# It supports the following method and field resolution algorithm:
#   1: A direct self dot expression is either a method or field of the
#   current class or inherited by the current class
#   1.1: if not found, then the local python objects is searched
#   2: A virtual member "cmi" such that when present, inheritance
#   starts with the CMI head class, not the current CMI class
#   3: Local python objects are never inherited outside of the current 
#   CMI class.
#

from sagapythonglobals import *
from CMILOID import LOID
import CMIClass
import SPClassObject
import SPClass
import SPClassLinearization
import SPClassRuntime
import SPMetaClass
import SPMetaMetaClass



# ClsObjVar is the base class. 
# Objects of this type will only address CMI fields and methods, not local python objects
#
# SagaPythonSelf is a subclass of ClsObjVar
# Objects of this type will address local python instance and local python class objects
#
# Need to describe valid syntax expressions
#

class ClsObjVar(object):
    def __init__(self, CMIObj) -> None:
        if not isinstance(CMIObj, LOID):
            raise RuntimeError("Illegal object type in new ClsObjVar object: must be type LOID.  Got: ", type(CMIObj))
        super().__setattr__("_ClsObjVar__CMIObj", CMIObj)
        super().__setattr__("_ClsObjVar__ObjEntry", None)
        super().__setattr__("_ClsObjVar__PendingCMIAncestorClass", None)
        super().__setattr__("_ClsObjVar__PendingMethod", None)
        super().__setattr__("_ClsObjVar__PendingMethodClass", None)
        super().__setattr__("_ClsObjVar__SelfArgs", None)
        super().__setattr__("_ClsObjVar__PendingMemberName", None)
        # flags
        super().__setattr__("_ClsObjVar__StartFlag", True)
        super().__setattr__("_ClsObjVar__MethodCallFlag", False)
        super().__setattr__("_ClsObjVar__PendingCMIAncestorFlag", False)
        super().__setattr__("_ClsObjVar__CurrentClassFlag", True)
        super().__setattr__("_ClsObjVar__PendingMemberFlag", False)

    # Syntax handling methods -- __getattribute__, __call__, __setattr__, __delattr__

    def __getattribute__(self, cminame: str):
        """getattribute returns either the value for a field,
        a callable for a method, or a an object with another getattribute
        (the object returned is the same to create a lightweight syntax parser around the dot operator)"""

        if cminame == "__name__":
            return super().__getattribute__(cminame)
            
        # check if expecting a __call__ for the argument to the __member operator
        if super().__getattribute__("_ClsObjVar__PendingMemberFlag") == True:
            type(self).ResetState(self)
            raise RuntimeError("Illegal Syntax: Expecting argument to __member(), not dot operator")

        # check if were expecting a __call__ for a method.
        if super().__getattribute__("_ClsObjVar__MethodCallFlag") == True:
            type(self).ResetState(self)
            raise RuntimeError("Illegal Syntax: Can not use method name in second dot operator")

        # check if were expecting a __call__ for the argument of a __cmi operator
        if super().__getattribute__("_ClsObjVar__PendingCMIAncestorFlag") == True:
            type(self).ResetState(self)
            raise RuntimeError("Illegal Syntax: Expecting argument to __cmi(), not dot operator")

        # if the pendingmembername is set, the __call__ happened for the
        # __member operator. We then got a dot operator. We thus know that this is
        # a field request, not a method call. Do the GetField on the stored name
        # and return

        pendingname = super().__getattribute__("_ClsObjVar__PendingMemberName")
        anccls = super().__getattribute__("_ClsObjVar__PendingCMIAncestorClass")

        if pendingname != None:
            fldval, valid = type(self).GetField(self, anccls, pendingname)
            type(self).ResetState(self)
            if valid == False:
                return None
            return fldval

        if super().__getattribute__("_ClsObjVar__StartFlag") == True:
            if cminame == "__local":
                raise RuntimeError("Illegal Syntax: ClsObjVar does not support the __local operator")


        if super().__getattribute__("_ClsObjVar__StartFlag") == True:
            super().__setattr__("_ClsObjVar__StartFlag", False)

            # check first for __cmi. set flag for 2 pass lockout, return self for next __call__ operator for cmi argument
            if cminame == "__cmi":
                super().__setattr__("_ClsObjVar__PendingCMIAncestorClass", None)
                super().__setattr__("_ClsObjVar__PendingCMIAncestorFlag", True)
                return self

        # check for __member operator -- can be after the __cmi operator 
        # expect __call__ next
        if cminame == "__member":
            super().__setattr__("_ClsObjVar__PendingMemberFlag", True)
            return self

        # now can only be a field or method
        # 
        # check for field starting from pendingCMIAncestorClass if not None
        anccls = super().__getattribute__("_ClsObjVar__PendingCMIAncestorClass")
        fldval, valid = type(self).GetField(self, anccls, cminame)
        if valid == True:
            type(self).ResetState(self)
            return fldval

        # if not a field, check if a method, so set name and set flag for next __call__.
        # Syntax support only self.<optional __cmi()>.method(). 
        anccls = super().__getattribute__("_ClsObjVar__PendingCMIAncestorClass")
        methodclass = type(self).IsMethod(self, anccls, cminame)
        if methodclass != NYI:
            super().__setattr__("_ClsObjVar__PendingMethod", cminame)
            super().__setattr__("_ClsObjVar__PendingMethodClass", methodclass)
            super().__setattr__("_ClsObjVar__MethodCallFlag", True)
            return self 

        type(self).ResetState(self)         
        return NYIObjVar          # note: need to have a special exception raised here so that subclass can capture it if needed.

    # The self object can be a callable because it can take arguments before
    # the method/field/class dot operator. Because we return a new object
    # for the method, the self object callable is only called at the beginning
    # of the syntax. A field does not return an object only the value.
    def __call__(self, *args):

        # if there is a pendingmembername value, then we know that
        # the syntax was a form of <objvar>.__member("name")(args)
        pendingname = super().__getattribute__("_ClsObjVar__PendingMemberName")
        methodcls = super().__getattribute__("_ClsObjVar__PendingMethodClass")
        if pendingname != None:
            retvalue = type(self).CallMethod(self, methodcls, pendingname, args)
            type(self).ResetState(self)
            return retvalue

        # check if this __call__ is for a member operator.
        # if so, store the name and return, the next __call__,
        # getattribute, or setattr will determine if this is a field or method
        # and will execute appropriately
        if super().__getattribute__("_ClsObjVar__PendingMemberFlag") == True:
            # verify that the first argument in *args is of type str
            if not isinstance(args[0], str):
                type(self).ResetState(self)
                raise RuntimeError("Illegal Syntax: __member() expects string as argument")

            super().__setattr__("_ClsObjVar__PendingMemberName", args[0])
            super().__setattr__("_ClsObjVar__PendingMemberFlag", False)
            return self

        # next check if this is arguments to the ClsObjVar instance in call syntax
        # objvar(args).<field/method>...
        if super().__getattribute__("_ClsObjVar__StartFlag") == True:
            if super().__getattribute__("_ClsObjVar__SelfArgs") != None:
                # double call operator on the object instance -- illegal
                type(self).ResetState(self)
                raise RuntimeError("Illegal Syntax: Multiple call operators not allowed")

            # store the argument list
            super().__setattr__("_ClsObjVar__SelfArgs", args)
            return self
        else:
            # check for cmi mode, and read class 
            if super().__getattribute__("_ClsObjVar__PendingCMIAncestorFlag") == True:
                super().__setattr__("_ClsObjVar__PendingCMIAncestorFlag", False)

                try:
                    argname = args[0]
                except:
                    argname = None   # need to fix this so that an empty __cmi()  means super()

                # the argname is string with class name, or a local or global variable                
                if argname in locals():
                    namestr = locals()[argname]
                elif argname in globals():
                    namestr = globals()[argname]
                else:
                    namestr = argname

                if isinstance(namestr, str):
                    super().__setattr__("_ClsObjVar__PendingCMIAncestorClass", namestr)
                    return self
                else:
                    type(self).ResetState(self)
                    raise RuntimeError("Illegal Syntax: Ancestor Class Name must be CN_* of C_* string, or an object of type string")

            # start flag is false, so method call should be true here
            if super().__getattribute__("_ClsObjVar__MethodCallFlag") == True:
                methodname = super().__getattribute__("_ClsObjVar__PendingMethod")
                if methodname == None:
                    type(self).ResetState(self)
                    raise RuntimeError("Illegal Syntax: Method name can not be 'None'")

                methodcls = super().__getattribute__("_ClsObjVar__PendingMethodClass")
                retvalue = type(self).CallMethod(self, methodcls, methodname, args)
                type(self).ResetState(self)
                return retvalue
            else:
                type(self).ResetState(self)
                raise RuntimeError("Illegal Syntax: Method not callable in current state.")


    # __setattr__ can be called directly for a field, can be called after the self object args
    # can be called after the class for the __cmi is determined.  It can not be called while
    # expecting a class for the __cmi.  
    # Note: Python does not allow assignment to a call operator ("()").
    # So can never get here with syntax: objvar.__member() = x
    def __setattr__(self, cminame, __value):

        # verify no __cmi pending 
        if super().__getattribute__("_ClsObjVar__PendingCMIAncestorFlag") == True:
            type(self).ResetState(self) 
            raise RuntimeError("Illegal Syntax: Can not assign to class value")

        fieldname = super().__getattribute__("_ClsObjVar__PendingMemberName")
        if fieldname != None:
            cminame = fieldname

        anccls = super().__getattribute__("_ClsObjVar__PendingCMIAncestorClass")
        fieldclass = type(self).IsField(self, anccls, cminame)
        if fieldclass != NYI:
            type(self).SetField(self, fieldclass, cminame, __value)
            type(self).ResetState(self)
            return 
        else:
            raise RuntimeError("Assignment failed: Field: " + cminame + " not found")


    # Sends a delete message for fields only. A deleted field returns as None.
    # Reading a deleted field does not raise an exception
    def __delattr__(self, cminame):

        # verify no __cmi pending - not clear how we would get here, just a sanity check
        if super().__getattribute__("_ClsObjVar__PendingCMIAncestorFlag") == True:
            type(self).ResetState(self)
            raise RuntimeError("Internal Error: expecting __call__ for __cmi() operator, but got __delattr__")

        fieldname = super().__getattribute__("_ClsObjVar__PendingMemberName")
        if fieldname != None:
            cminame = fieldname

        anccls = super().__getattribute__("_ClsObjVar__PendingCMIAncestorClass")
        fieldclass = type(self).IsField(self, anccls, cminame)
        if fieldclass != NYI:
            type(self).DelField(self, fieldclass, cminame)
            type(self).ResetState(self)
            return True

        type(self).ResetState(self)
        raise RuntimeError("Failed Field Deletion: CMI field not found")
        
    # ClsObjVar class methods. Must pass the self object to them.
    @classmethod 
    def LoadObject(clsself, self, default):
        """make sure object is loaded from database"""
        obj = super(ClsObjVar, self).__getattribute__("_ClsObjVar__ObjEntry")
        if obj == None:
            cmiloid = super(ClsObjVar, self).__getattribute__("_ClsObjVar__CMIObj")
            try:
                obj = GetObjectEntry(cmiloid)
                super(ClsObjVar, self).__setattr__("_ClsObjVar__ObjEntry", obj)
            except:
                obj = default
        return obj

    @classmethod
    def ResetState(clsself, self):
        super(ClsObjVar,self).__setattr__("_ClsObjVar__PendingCMIAncestorClass", None)
        super(ClsObjVar,self).__setattr__("_ClsObjVar__PendingMethod", None)
        super(ClsObjVar,self).__setattr__("_ClsObjVar__PendingMethodClass", None)
        super(ClsObjVar,self).__setattr__("_ClsObjVar__SelfArgs", None)
        super(ClsObjVar,self).__setattr__("_ClsObjVar__PendingMemberName", None)
        # flags
        super(ClsObjVar,self).__setattr__("_ClsObjVar__StartFlag", True)
        super(ClsObjVar,self).__setattr__("_ClsObjVar__MethodCallFlag", False)
        super(ClsObjVar,self).__setattr__("_ClsObjVar__PendingCMIAncestorFlag", False)
        super(ClsObjVar,self).__setattr__("_ClsObjVar__CurrentClassFlag", True)
        super(ClsObjVar,self).__setattr__("_ClsObjVar__PendingMemberFlag", False)

    def __CheckCurrentAccountContext(self):
        """check if caller account and self are owned by same account"""

    def __CheckCurrentObject(self):
        """check if caller object and self are the same. When not
        act like a stub. """

    @classmethod
    def IsMethod(clsself, self, currclass, mtdname):
        if currclass == None:
            objentry = clsself.LoadObject(self, null)
            if objentry == null:
                raise RuntimeError("Illegal Operation: Object Not Found")

            currclass = objentry.GetCMIClass()
            
        cmiloid = ClsObjVar.GetLOID(self)
        return DispatchIsMethod(currclass, cmiloid, mtdname)

    @classmethod
    def CallMethod(clsself, self, currclass, mtdname, args):
        if currclass == None:
            objentry = clsself.LoadObject(self, null)
            if objentry == null:
                raise RuntimeError("Illegal Operation: Object Not Found")

            currclass = objentry.GetCMIClass()

        cmiloid = ClsObjVar.GetLOID(self)
        return DispatchMethod(currclass, cmiloid, mtdname, args)


    @classmethod
    def IsField(clsself, self, currclass, fieldname):
        if currclass == None:
            objentry = clsself.LoadObject(self, null)
            if objentry == null:
                raise RuntimeError("Illegal Operation: Object Not Found")

            currclass = objentry.GetCMIClass()

        cmiloid = ClsObjVar.GetLOID(self)
        return DispatchIsField(currclass, cmiloid, fieldname)

    # GetField checks if currclass == None, and uses the class of the CMIobj
    @classmethod
    def GetField(clsself, self, currclass, fieldname):
        if currclass == None:
            objentry = clsself.LoadObject(self, null)
            if objentry == null:
                raise RuntimeError("Illegal Operation: Object Not Found")

            currclass = objentry.GetCMIClass()

        cmiloid = ClsObjVar.GetLOID(self)
        return DispatchField(currclass, cmiloid, True, fieldname, None)   
        
    @classmethod
    def SetField(clsself, self, currclass, fieldname, value):
        if currclass == None:
            objentry = clsself.LoadObject(self, null)
            if objentry == null:
                raise RuntimeError("Illegal Operation: Object Not Found")

            currclass = objentry.GetCMIClass()

        cmiloid = ClsObjVar.GetLOID(self)
        return DispatchField(currclass, cmiloid, False, fieldname, value)   

    @classmethod
    def DelField(clsself, self, currclass, fieldname):
        if currclass == None:
            objentry = clsself.LoadObject(self, null)
            if objentry == null:
                raise RuntimeError("Illegal Operation: Object Not Found")

            currclass = objentry.GetCMIClass()

        cmiloid = ClsObjVar.GetLOID(self)
        return DispatchField(currclass, cmiloid, False, fieldname, None)   

    def Listen(self):
        # calls CMI Listen eventually

        # on return from CMI Listen, if result, returns result
        # if a new message, does a dispatch

        pass

    @classmethod
    def GetObjectEntry(self, cmiobject: LOID) -> CMIClass.ClassTableEntry:
        return GetObjectEntry(cmiobject)

    @classmethod
    def LOIDbytes (self, obj) -> bytes:
        return super(ClsObjVar, obj).__getattribute__("_ClsObjVar__CMIObj").OIDbytes()

    @classmethod
    def GetLOID(self, obj)-> LOID:
        return super(ClsObjVar, obj).__getattribute__("_ClsObjVar__CMIObj")

    @classmethod
    def IsLinearAncestor(self, headcls, cls1, cls2):
        """verifies that cls1 is the ancestor of cls2 in the lienarization for headclass"""
        if not isinstance(headcls, ClsObjVar):
            if not isinstance(headcls, LOID):
                raise RuntimeError("IsLinearAncestor: class must be of type ClsObjVar or LOID")
            else:
                hobjvar = ClsObjVar(headcls)
                headclassLOID = headcls
        else:
            hobjvar = headcls
            headclassLOID = ClsObjVar.GetLOID(hobjvar)

        if isinstance(cls1, ClsObjVar):
            obj1 = ClsObjVar.GetLOID(cls1).OIDstr()
        elif isinstance(cls1, LOID):
            obj1 = cls1.OIDstr()
        else:
            raise RuntimeError("IsLinearAncestor: class must be of type ClsObjVar or LOID")

        if isinstance(cls2, ClsObjVar):
            obj2 = ClsObjVar.GetLOID(cls2).OIDstr()
        elif isinstance(cls2, LOID):
            obj2 = cls2.OIDstr()
        else:
            raise RuntimeError("IsLinearAncestor: class must be of type ClsObjVar or LOID")

        lintab = hobjvar.__member(SPClassLinearization.CMIClassLinearizationConst.Lintable).fld
        if lintab == NYI:
            raise RuntimeError("IsLinearAncestor: Class error. Linearization table not found!")

        try:    
            obj1index = lintab.index(obj1)
        except ValueError as exception:
            raise RuntimeError("IsLinearAncestor: class not in inheritance linearization for: " + headclassLOID + " class: " + cls1) from exception 

        try:    
            obj2index = lintab.index(obj2)
        except ValueError as exception:
            raise RuntimeError("IsLinearAncestor: class not in inheritance linearization for: " + headclassLOID + " class: " + cls2) from exception 

        if obj2index >= obj1index: 
            return True
        
        return False        

# SagaPythonSelf implements the following:
# __local keyword in getattribute, calling ancestor otherwise
# Overrides dispatch so method and field call
class SagaPythonSelf(ClsObjVar):
    def __init__(self, CMIObj, CMICurrentClass, CMIHeadClass, local=False, oneshot=False) -> None:
        super().__init__(CMIObj)
        super(ClsObjVar, self).__setattr__("_SagaPythonSelf__Local", local)
        super(ClsObjVar, self).__setattr__("_SagaPythonSelf_DotOneshot", oneshot)
        super(ClsObjVar, self).__setattr__("_SagaPythonSelf__CMICurrentClass", CMICurrentClass)
        super(ClsObjVar, self).__setattr__("_SagaPythonSelf__CMIHeadClass", CMIHeadClass)

    def __getattribute__(self, cminame: str):
        """check for the __local keyword if directly after the object.
        if present set flag and return object. Checked later for field and method resolution"""

        if cminame == "__name__":
            return super().__getattribute__(cminame)

        super(ClsObjVar, self).__setattr__("_SagaPythonSelf__DotOneshot", False) 

        # first check if this is already an ancestor class operation
        if super(ClsObjVar, self).__getattribute__("_ClsObjVar__PendingCMIAncestorClass") != None:
            return super().__getattribute__(cminame)

        if super(ClsObjVar, self).__getattribute__("_ClsObjVar__StartFlag") == True:
            if cminame == "__local":
                super(ClsObjVar, self).__setattr__("_ClsObjVar__StartFlag", False)
                super(ClsObjVar, self).__setattr__("_SagaPythonSelf__Local", True)
                super(ClsObjVar, self).__setattr__("_SagaPythonSelf__DotOneshot", True) 
                return self             
    
        # start flag may true or false here.  If __local was not the first
        # operand, then startflag is still True

        # check if we should do local first.  
        lflag = super(ClsObjVar, self).__getattribute__("_SagaPythonSelf__Local")
        if lflag == True:
            # check for member operator, so need callable flag
            # for SagaPythonSelf to override ClsObjVar
            # the actual field/method lookup happens in the SagaPythonSelf
            # __call__ if it is the __member operator, to collect the argument first
            if cminame == "__member":
                super(ClsObjVar, self).__setattr__("_ClsObjVar__StartFlag", False)
                super(ClsObjVar, self).__setattr__("_ClsObjVar__PendingMemberFlag", True)
                return self

            # check local python objects, instance and class first
            # if found, clear the state, and return the new object
            # the rest of the syntax is processed normally by python without
            # reference to the self or objvar object
            fieldname = cminame
            localsdict = type(self).GetInstanceLocals(self)
            if localsdict.get(fieldname, null) != null:
                retvalue = localsdict[fieldname]
                type(self).ResetState(self)
                return retvalue

            # check class locals - these are of the current class, not the head class
            classlocalsdict = type(self).GetClassLocals(self)
            if classlocalsdict.get(fieldname, null) != null:
                retvalue = classlocalsdict[fieldname]
                type(self).ResetState(self)
                return retvalue
            
            # if we got here, both __member and local objects failed, so let ancestor handle it
            # if not a field or a method, it will return an NYI object
            retvalue = super().__getattribute__(cminame)
            if retvalue != NYIObjVar:
                return retvalue
        else:
            # check ancestor first. This checks for field and ismethod.
            # If a field, it is handled by the ancestor.
            # if !NYI, return whatever it is. ClsObjVar will handle it.
            # if NYI, can check local because we know that the __cmi operator 
            # didn't happen.  This code would not be reached if so.
            retvalue = super().__getattribute__(cminame)
            if retvalue != NYIObjVar:
                return retvalue

            fieldname = cminame
            localsdict = type(self).GetInstanceLocals(self)
            if localsdict.get(fieldname, null) != null:
                retvalue = localsdict[fieldname]
                type(self).ResetState(self)
                return retvalue

            # check class locals - these are of the current class, not the head class
            classlocalsdict = type(self).GetClassLocals(self)
            if classlocalsdict.get(fieldname, null) != null:
                retvalue = classlocalsdict[fieldname]
                type(self).ResetState(self)
                return retvalue

        type(self).ResetState(self)
        return NYIObjVar

    def __call__(self, *args):

        if super(ClsObjVar, self).__getattribute__("_SagaPythonSelf__DotOneshot") == True:
            type(self).ResetState(self)
            raise RuntimeError("Illegal Syntax: Expected dot operator, not callable") 

        if super(ClsObjVar, self).__getattribute__("_ClsObjVar__PendingCMIAncestorClass") != None:
            return super().__call__(*args)

        if super(ClsObjVar, self).__getattribute__("_ClsObjVar__PendingMemberFlag") == True:
            return super().__call__(*args)

        # if PendingMemberName is set, we know that the syntax is
        # <object>.__member(name)(args)  or <object>.__local.__member(name)(args)
        # It is therefore a method call. If it is a local object, we have to
        # call it explicitly, we can't just return the object because the
        # the call syntax has already happened. If the local flag is set,
        # we check if first. If the local flag is not set, then call ancestor
        # first. May need to store state first.
        retvalue = NYIObjVar
        pendingname = super(ClsObjVar, self).__getattribute__("_ClsObjVar__PendingMemberName")
        if pendingname != None:
            if super(ClsObjVar, self).__getattribute__("_SagaPythonSelf__Local") == True:
                # check for locals and return
                localsdict = type(self).GetInstanceLocals(self)
                if localsdict.get(pendingname, null) != null:
                    retvalue = localsdict[pendingname](*args)
                    type(self).ResetState(self)
                    return retvalue

                classlocalsdict = type(self).GetClassLocals(self)
                if classlocalsdict.get(pendingname, null) != null:
                    retvalue = classlocalsdict[pendingname](*args)
                    type(self).ResetState(self)
                    return retvalue

                return super().__call__(*args) 
            else:
                # try ancestor first, then check locals
                retvalue = super().__call__(*args)
                if retvalue != NYIObjVar:
                    return retvalue
                
                # check locals
                # check for locals and return
                localsdict = type(self).GetInstanceLocals(self)
                if localsdict.get(pendingname, null) != null:
                    retvalue = localsdict[pendingname](*args)
                    type(self).ResetState(self)
                    return retvalue

                classlocalsdict = type(self).GetClassLocals(self)
                if classlocalsdict.get(pendingname, null) != null:
                    retvalue = classlocalsdict[pendingname](*args)
                    type(self).ResetState(self)
                    return retvalue

                return NYIObjVar

        # If this as syntax: objvar.<method>(args) or objvar.__local.<method>(args)
        # and the method was a local python object (instance or class), then 
        # it was already returned in the getattribute call. 
        # If we get here, we know that this wasn't a pendingmember name callable
        # we know that it can't be a local python method object call
        # therefore we can give it to the ancestor

        return super().__call__(*args)

    def __setattr__(self, cminame: str, arg: any):

        # if there is a __cmi() operator, no locals, become transparent
        if super(ClsObjVar, self).__getattribute__("_ClsObjVar__PendingCMIAncestorClass") != None:
            return super().__setattr__(cminame, arg)

        fieldname = super(ClsObjVar, self).__getattribute__("_ClsObjVar__PendingMethod")
        if fieldname == None:
            fieldname = cminame

        lflag = super(ClsObjVar, self).__getattribute__("_SagaPythonSelf__Local")

        if lflag == True:
            # check instance locals first with fieldname, not cminame
            localsdict = type(self).GetInstanceLocals(self)
            if localsdict.get(fieldname, null) != null:
                localsdict[fieldname] = arg
                type(self).ResetState(self)
                return

            # check class locals - these are of the current class, not the head class
            classlocalsdict = type(self).GetClassLocals(self)
            if classlocalsdict.get(fieldname, null) != null:
                classlocalsdict[fieldname] = arg
                type(self).ResetState(self)
                return

            # if not locals call ancestor. If fails then set new instance local
            try:
                super().__setattr__(cminame, arg)
            except:
                localsdict[fieldname] = arg
            
            type(self).ResetState(self)
            return
        else:
            # try ancestor first, then do locals
            try:
                return super().__setattr__(cminame, arg)
            except:
                pass

            localsdict = type(self).GetInstanceLocals(self)
            if localsdict.get(fieldname, null) != null:
                localsdict[fieldname] = arg
                type(self).ResetState(self)
                return

            # check class locals - these are of the current class, not the head class
            classlocalsdict = type(self).GetClassLocals(self)
            if classlocalsdict.get(fieldname, null) != null:
                classlocalsdict[fieldname] = arg
                type(self).ResetState(self)
                return

            localsdict[fieldname] = arg
            type(self).ResetState(arg)
            return

    @classmethod
    def __detattr__(self, cminame: str):

        # if there is a __cmi() operator, no locals, become transparent
        if super(ClsObjVar, self).__getattribute__("_ClsObjVar__PendingCMIAncestorClass") != None:
            return super().__detattr__(cminame)

        fieldname = super(ClsObjVar, self).__getattribute__("_ClsObjVar__PendingMethod")
        if fieldname != None:
            fieldname = cminame

        lflag = super(ClsObjVar, self).__getattribute__("_SagaPythonSelf__Local")
        if lflag == True:
            # check locals first
            localsdict = type(self).GetInstanceLocals(self)
            if localsdict.get(fieldname, null) != null:
                del localsdict[fieldname]
                type(self).ResetState(self)
                return

            # check class locals - these are of the current class, not the head class
            classlocalsdict = type(self).GetClassLocals(self)
            if classlocalsdict.get(fieldname, null) != null:
                del classlocalsdict[fieldname]
                type(self).ResetState(self)
                return

            return super().__delattr__(cminame)
        else:
            try:
                if super().__delattr__(cminame) == True:
                    return
            except:
                pass

            # check locals first
            localsdict = type(self).GetInstanceLocals(self)
            if localsdict.get(fieldname, null) != null:
                del localsdict[fieldname]
                type(self).ResetState(self)
                return

            # check class locals - these are of the current class, not the head class
            classlocalsdict = type(self).GetClassLocals(self)
            if classlocalsdict.get(fieldname, null) != null:
                del classlocalsdict[fieldname]
                type(self).ResetState(self)
                return

        raise RuntimeError("Failed Field Deletion: Neither CMI field nor Python local object found")
        
    @classmethod
    def IsField(clsself, self, anccls, cminame):
        anccls = SagaPythonSelf.CheckAncestor(self, anccls)
        return super().IsField(self, anccls, cminame)

    @classmethod
    def GetField(clsself, self, anccls, cminame):
        # check that anccls is an ancestor of the current class.
        anccls = SagaPythonSelf.CheckAncestor(self, anccls)
        return super().GetField(self, anccls, cminame)

    @classmethod
    def SetField(clsself, self, anccls, cminame, value):
        # check that anccls is an ancestor of the current class.
        anccls = SagaPythonSelf.CheckAncestor(self, anccls)
        return super().SetField(self, anccls, cminame, value)

    @classmethod
    def IsMethod(clsself, self, anccls, cminame):
        # check that anccls is an ancestor of the current class.
        anccls = SagaPythonSelf.CheckAncestor(self, anccls)
        return super().IsMethod(self, anccls, cminame)

    @classmethod
    def CallMethod(clsself, self, anccls, mtdname, args):
        # check that anccls is an ancestor of the current class.
        # anccls = SagaPythonSelf.CheckAncestor(self, anccls)
        return super().CallMethod(self, anccls, mtdname, args)

    @classmethod
    def CheckAncestor(clsself, self, anccls):
        # check that anccls is an ancestor of the current class.
        currclass = super(ClsObjVar, self).__getattribute__("_SagaPythonSelf__CMICurrentClass")
        if anccls != None:
            if anccls != currclass:
                objentry = SagaPythonSelf.GetObjectEntry(self)
                headclass = objentry.GetCMIClass()              
                if SagaPythonSelf.IsLinearAncestor(headclass, anccls, currclass) != True:
                    raise RuntimeError("Illegal Syntax")
        else:
            anccls = currclass

        return anccls

    @classmethod
    def ResetState(clsself, self):
        super().ResetState(self)
        super(ClsObjVar,self).__setattr__("_SagaPythonSelf__DotOneshot", False)
        super(ClsObjVar, self).__setattr__("_SagaPythonSelf__Local", False)

class nYIObjVar(object):

    def __getattribute__(self, cminame: str):
        raise RuntimeError("Unknown field value: ", cminame)


    # The self object can be a callable because it can take arguments before
    # the method/field/class dot operator. Because we return a new object
    # for the method, the self object callable is only called at the beginning
    # of the syntax. A field does not return an object only the value.
    def __call__(self, *args):
        raise RuntimeError("Unknown method call")


    # __setattr__ can be called directly for a field, can be called after the self object args
    # can be called after the class for the __cmi is determined.  It can not be called while
    # expecting a class for the __cmi.  
    # Note: Python does not allow assignment to a call operator ("()").
    # So can never get here with syntax: objvar.__member() = x
    def __setattr__(self, cminame, __value):
        raise RuntimeError("Unknown field value: ", cminame)

    # Sends a delete message for fields only. A deleted field returns as None.
    # Reading a deleted field does not raise an exception
    def __delattr__(self, cminame):
        raise RuntimeError("Unknown field value: ", cminame)
  
NYIObjVar = nYIObjVar()

  # Dispatch functions called by the Listen() loop
#
# Details of how each is called is still tbd -- protocol between
# processes is likely going to be a combination of shared memory and google protobufs
# actual arguments and instance data are all in JSON
#
# Need to implement support for Account authorizations as part of method dispatches
# in future.
import io
import pickle
import CMI   # The CMI interface layer
from CMIClass import *
from CMIObjectData import *
import SPClassObject
import SPClass
import SPClassLinearization
import SPClassRuntime


# DispatchMethod
# 1: Assume received the class, object, message, arguments

# 2: Asks the CMI to load the object

# 3: Asks the CMI for the type of the object

# 4: Asks the CMI to load the type object (i.e. the head class)

# 5: Asks the CMI for the Class HeadClass instance data from the type object – well known instance index

# 6: Base64 decodes the class instance data. 

# 7: JSON decodes the Class HeadClass instance data – 

# Note: the linearization is common to all language runtimes. 

# 8: Reads the linearization table, finds the index for the passed in class OID

# 9: Asks CMI to load the passed in class

# 10:  Asks the CMI for the type of the loaded class

# 11: Asks the CMI to load the type of the class (metaclass)

# 12: Asks the CMI for the Class HeadClass instance data of the type of the class

# 13: Base64 decodes and JSON decodes – to get linearization

# 14: Walks linearization to find a match for SagaPythonClass

# 15: Have now verified that the current class in the object’s class linearization is a valid SagaPython object safe to read the class info

# 16: Reads the SagaPython Class instance data from well known instance index

# 17: Compares against method or field
# 18: If no match, reads ancestor class field.

# 19: Does a message post to ancestor – this avoids unnecessary unwinding by sending the original return address, not itself.

# 20: On a match – calls DoMethod

def GetObjectEntry(loid: LOID):
    objentry = CMIData.ObjectTableOIDMap.get(loid.OIDstr(), null)
    if objentry != null:
        return objentry
    else:
        objhandle = CMI.LoadObject(loid, null)   # loads the object from database and returns a handle to the instance data JSON list
        if objhandle == null:
            raise RuntimeError("Can't Load CMI object, objectid: " + loid)

        # we force all object entries to have a CMI class component, and use as
        # plain objects where needed. Avoids having extra code to figure out.
        objentry = CMIClass.ClassTableEntry(objhandle, loid, len(CMIData.ObjectTableList), CMI.InstanceDataLen(objhandle))
        CMIData.ObjectTableOIDMap[loid.OIDstr()] = objentry
        CMIData.ObjectTableHandleMap[objhandle] = objentry
        CMIData.ObjectTableList.append(objentry)
        return objentry

def SetModified(loid: LOID):
    objentry = GetObjectEntry(loid)
    objentry.modified = True

def WriteObjects():
    objentry: ObjectTableEntry
    for objentry in CMIData.ObjectTableList:
        WriteObjectEntry(objentry.oid)

def WriteObjectEntry(loid: LOID):

        objentry = CMIData.ObjectTableOIDMap[loid.OIDstr()] 

            # if not modified, don't write to CMI
        if objentry.modified == False: 
            return

        newstatebase64 = [None] * objentry.idatalen
        for idx in range(objentry.idatalen):
            newstatebase64[idx]=[None, None]
            if objentry.idata[idx] != None:
                cmidata = objentry.idata[idx][CMIConst.CMIFieldIndex]
                if cmidata != None:
                    if cmidata != null:
                        idatajson = CMIJSONEncoder.encode(cmidata)
                        newstatebase64[idx][CMIConst.CMIFieldIndex] = base64.b64encode(idatajson.encode()).decode()                
                    else:
                        newstatebase64[idx][CMIConst.CMIFieldIndex] = None
                else:
                    orgcmidata = CMI.GetInstanceData(objentry.handle, idx)
                    if orgcmidata != None and orgcmidata != null:
                        newstatebase64[idx][CMIConst.CMIFieldIndex] = orgcmidata[CMIConst.CMIFieldIndex] 
                    else:
                        newstatebase64[idx][CMIConst.CMIFieldIndex] = None
                        
                pydata = objentry.idata[idx][CMIConst.PythonObjectsIndex]
                if pydata != None:
                    if pydata != null:
                        # pickle python objects here
                        pb = pickle.dumps(pydata)
                        newstatebase64[idx][CMIConst.PythonObjectsIndex] = base64.b64encode(pb).decode()
                    else:
                        newstatebase64[idx][CMIConst.PythonObjectsIndex] = None
                else:
                    orgpydata = CMI.GetInstanceData(objentry.handle, idx)
                    if orgpydata != None and orgpydata != null:
                        newstatebase64[idx][CMIConst.PythonObjectsIndex] = orgpydata[CMIConst.PythonObjectsIndex] 
                    else:
                        newstatebase64[idx][CMIConst.PythonObjectsIndex] = None
            else:
                newstatebase64[idx] = CMI.GetInstanceData(objentry.handle, idx)

        # have a list of JSON encoded, then base64 encoded bytes
        # now give them to the CMI to write out as a JSON list of strings
        CMI.WriteObject(objentry.handle, newstatebase64)            

# ListenDispatchIsMethod is called from the listener inbound code to set the callinfo for message return,
# and to set the local flag to false, postflag to true, is continuing resolution search to another runtime
def ListenDispatchIsMethod(currclass: LOID, cmiobject: LOID, mtd: str, ci = None):

    if ci == None:
        raise RuntimeError("Internal Error: No callinfo")
    
    return DispatchIsMethod(currclass, cmiobject, mtd, callinfo = ci, postflag = True, local = False)

# DispatchMethod is called from a CMI.Listen() on receipt of a message
# for a method call.  The currclass and cmiobject are LOIDs.
def DispatchIsMethod(currclass: LOID, cmiobject: LOID, mtd: str, callinfo = None, postflag = False, local = True):
    
    try:
        objentry = SagaPythonSelf.GetObjectEntry(cmiobject)
    except RuntimeError as exc:
        raise RuntimeError("DispatchMethod invalid OID") from exc        

    headclassLOID = objentry.GetCMIClass()        # returns the LOID for the class of the passed in object handle
                                                    # This may not be the currclass valu
    if headclassLOID == null:
        raise RuntimeError("Object does not have a class")                                                
    
    try:
        headclassobjentry = SagaPythonSelf.GetObjectEntry(headclassLOID)
    except RuntimeError as exc:
        raise RuntimeError("Failed loading class of object") from exc

    # get the class instance data field fron the headclass object
    idata = headclassobjentry.GetCMIInstanceData(CMIConst.CMIClassLinearizationIndex)
    headclasslintab = idata.get(SPClassLinearization.CMIClassLinearizationConst.Lintabl, null)
    if headclasslintab == null:
        raise RuntimeError("Internal Class Error: No linearization table found")
    
    if currclass == None:
        currclass = headclassLOID
        
    try:
        currclasslinearindex = headclasslintab.index(currclass)
    except ValueError as exception:
        raise RuntimeError("Current class not an ancestor. Head class: " + headclassLOID + " current class: " + currclass) from exception 

    while True:

        # check if the current class is a SagaPython class            
        try:
            currclassobjentry = SagaPythonSelf.GetObjectEntry(currclass)
        except RuntimeError as exc:
            raise RuntimeError("Dispatch Method can't find current ancestor class object")

        # check if same runtime, if not call send or post
        rtdata = currclassobjentry.GetCMIInstanceData(CMIConst.CMIClassRuntimeIndex)
        currruntime = rtdata.get(SPClassRuntime.CMIClassRuntimeConst.URL, null)
        if currruntime != CMI.GetLanguageRuntime():
            if postflag == True:
                retvalue = PostIsMethod(callinfo, currruntime, currclass, cmiobject, mtd, None)
                break   # breaks infinite while loop
            else:
                retvalue = SendIsMethod(callinfo, currruntime, currclass, cmiobject, mtd, None)
                break   # breaks infinite while loop            


        # verify that the currclass is an instance of SPMetaClass or subclass (e.g. SPMetaMetaClass)
        currclassclassLOID = currclassobjentry.GetCMIClass()

        try:
            currclassclassobjentry = SagaPythonSelf.GetObjectEntry(currclassclassLOID)
        except RuntimeError as exc:
            raise RuntimeError("Dispatch Method can't find current class's metaclass")

        # verify that the current class's metaclass is a class
        currclassclassidata = currclassclassobjentry.GetCMIInstanceData(CMIConst.CMIClassLinearizationIndex)        
        currclassclasslintab = currclassclassidata.get(SPClassLinearization.CMIClassLinearizationConst.Lintabl, null)
        if currclassclasslintab == null:
            raise RuntimeError("Internal Class Error: No linearization table found")

        try:
            currclassclasslintab.index(CMIConst.SPClass)
        except ValueError as exception:
            raise RuntimeError("Meta class for current class must be a class object itself") from exception
        
        # The object's headclass is a class
        # The current class is in the headclass linearization list
        # The current class is a class SPMetaClass or subclass
        # The current class, class, is verified to be a class

        # Look for the method in the current class method table
        mtdentry = currclassobjentry.GetMethod(mtd) 
        if mtdentry == null:
            # give the ancestor a shot walking the linearization table
            if currclasslinearindex < 1:
                # Reached SPClassObject, Not implemented - return 
                if local == False:
                    if callinfo != None:
                        # Not implemented - return 
                        ReturnValueNYI(callinfo)
                retvalue = NYI
                break

            currclasslinearindex -= 1
            currclass = headclasslintab[currclasslinearindex]
            if currclass == null or currclass == None:
                raise RuntimeError("Internal Class Linearization Table Error: Failed MRO search")

            continue

        else:
            retvalue = currclass
            if local == False:                   # if there is an outstanding send or post, return message. 
                if callinfo != None:
                    ReturnValue(callinfo, retvalue)
            break

    return retvalue

# ListenDispatchMethod is called from the listener inbound code to set the callinfo for message return,
# and to set the local flag to false, postflag to true, is continuing resolution search to another runtime
def ListenDispatchMethod(currclass: LOID, cmiobject: LOID, mtd: str, args, ci = None):

    if ci == None:
        raise RuntimeError("Internal Error: No callinfo")
    
    return DispatchMethod(currclass, cmiobject, mtd, args, callinfo = ci, postflag = True, local = False)

# DispatchMethod is called from a CMI.Listen() on receipt of a message
# for a method call.  The currclass and cmiobject are LOIDs.
# Note: args is a list not individual -- called from the SagaPythonSelf or from the listen function.
def DispatchMethod(currclass: LOID, cmiobject: LOID, mtd: str, args, callinfo = None, postflag = False, local = True):
    
    try:
        objentry = SagaPythonSelf.GetObjectEntry(cmiobject)
    except RuntimeError as exc:
        raise RuntimeError("DispatchMethod invalid OID") from exc        

    headclassLOID = objentry.GetCMIClass()        # returns the LOID for the class of the passed in object handle
                                                    # This may not be the currclass valu
    if headclassLOID == null:
        raise RuntimeError("Object does not have a class")                                                
    
    try:
        headclassobjentry = SagaPythonSelf.GetObjectEntry(headclassLOID)
    except RuntimeError as exc:
        raise RuntimeError("Failed loading class of object") from exc

    # get the class instance data field fron the headclass object
    idata = headclassobjentry.GetCMIInstanceData(CMIConst.CMIClassLinearizationIndex)
    headclasslintab = idata.get(SPClassLinearization.CMIClassLinearizationConst.Lintabl, null)
    if headclasslintab == null:
        raise RuntimeError("Internal Class Error: No linearization table found")

    if currclass == None:
        currclass = headclassLOID
            
    try:
        currclasslinearindex = headclasslintab.index(currclass)
    except ValueError as exception:
        raise RuntimeError("Current class not an ancestor. Head class: " + headclassLOID + " current class: " + currclass) from exception 

    while True:

        # check if the current class is a SagaPython class            
        try:
            currclassobjentry = SagaPythonSelf.GetObjectEntry(currclass)
        except RuntimeError as exc:
            raise RuntimeError("Dispatch Method can't find current ancestor class object")

        # check if same runtime, if not call send or post
        rtdata = currclassobjentry.GetCMIInstanceData(CMIConst.CMIClassRuntimeIndex)
        currruntime = rtdata.get(SPClassRuntime.CMIClassRuntimeConst.URL, null)
        if currruntime != CMI.GetLanguageRuntime():
            if postflag == True:
                retvalue = PostMethod(callinfo, currruntime, currclass, cmiobject, mtd, args)
                break   # breaks infinite while loop
            else:
                retvalue = SendMethod(callinfo, currruntime, currclass, cmiobject, mtd, args)
                break   # breaks infinite while loop            


        # verify that the currclass is an instance of SPMetaClass or subclass (e.g. SPMetaMetaClass)
        currclassclassLOID = currclassobjentry.GetCMIClass()

        try:
            currclassclassobjentry = SagaPythonSelf.GetObjectEntry(currclassclassLOID)
        except RuntimeError as exc:
            raise RuntimeError("Dispatch Method can't find current class's metaclass")

        # verify that the current class's metaclass is a class
        currclassclassidata = currclassclassobjentry.GetCMIInstanceData(CMIConst.CMIClassLinearizationIndex)        
        currclassclasslintab = currclassclassidata.get(SPClassLinearization.CMIClassLinearizationConst.Lintabl, null)
        if currclassclasslintab == null:
            raise RuntimeError("Internal Class Error: No linearization table found")

        try:
            currclassclasslintab.index(CMIConst.SPClass)
        except ValueError as exception:
            raise RuntimeError("Meta class for current class must be a class object itself") from exception
        
        # The object's headclass is a class
        # The current class is in the headclass linearization list
        # The current class is a class SPMetaClass or subclass
        # The current class, class, is verified to be a class

        # Look for the method in the current class method table
        mtdentry = currclassobjentry.GetMethod(mtd) 
        if mtdentry == null:
            # give the ancestor a shot walking the linearization table
            if currclasslinearindex < 1:
                # Reached SPClassObject, Not implemented - return 
                if local == False:
                    if callinfo != None:
                        # Not implemented - return 
                        ReturnValueNYI(callinfo)
                retvalue = NYI
                break

            currclasslinearindex -= 1
            currclass = headclasslintab[currclasslinearindex]
            if currclass == null or currclass == None:
                raise RuntimeError("Internal Class Linearization Table Error: Failed MRO search")

            continue

        else:
            # do the actual method call here
            retvalue = currclassobjentry.DoMethod(callinfo, headclassobjentry, objentry, mtdentry, args)
            if local == False:                   # if there is an outstanding send or post, return message. 
                if callinfo != None:
                    ReturnValue(callinfo, retvalue)
            break

    return retvalue

# DispatchField functions
#
# ListenDispatchIsField is called from the listener inbound code to set the callinfo for message return,
# and to set the local flag to false, postflag to true, is continuing resolution search to another runtime
def ListenDispatchIsField(currclass: LOID, cmiobject: LOID, fieldname: str, ci = None):

    if ci == None:
        raise RuntimeError("Internal Error: No callinfo")
    
    return DispatchIsField(currclass, cmiobject, fieldname, callinfo = ci, postflag = True, local = False)


# does an inheritance resolution on the field
def DispatchIsField(currclass: LOID, cmiobject: LOID, fieldname: str, callinfo = None, postflag = False, local = True):   

    try:
        objentry = SagaPythonSelf.GetObjectEntry(cmiobject)
    except RuntimeError as exc:
        raise RuntimeError("DispatchMethod invalid OID") from exc        

    headclassLOID = objentry.GetCMIClass()     # returns the LOID for the class of the passed in object handle

    try:
        headclassobjentry = SagaPythonSelf.GetObjectEntry(headclassLOID)
    except RuntimeError as exc:
        raise RuntimeError("Failed loading class of object") from exc

    idata = headclassobjentry.GetCMIInstanceData(CMIConst.CMIClassLinearizationIndex)
    headclasslintab = idata.get(SPClassLinearization.CMIClassLinearizationConst.Lintabl, null)
    if headclasslintab == null:
        raise RuntimeError("Internal Class Error: No linearization table found")

    if currclass == None:
        currclass = headclassLOID
        
    try:
        currclasslinearindex = headclasslintab.index(currclass)
    except ValueError as exception:
        raise RuntimeError("Current class not an ancestor. Head class: " + headclassLOID + " current class: " + currclass) from exception 

    while True:

        # check if the current class is a SagaPython class            
        try:
            currclassobjentry = SagaPythonSelf.GetObjectEntry(currclass)
        except RuntimeError as exc:
            raise RuntimeError("Dispatch Method can't find current ancestor class object")

        # check if same runtime, if not call send or post
        rtdata = currclassobjentry.GetCMIInstanceData(CMIConst.CMIClassRuntimeIndex)
        currruntime = rtdata.get(SPClassRuntime.CMIClassRuntimeConst.URL, null)
        if currruntime != CMIConst.CMIRuntimeURL:
            if postflag == True:
                retvalue = PostIsField(callinfo, currruntime, currclass, cmiobject, fieldname)
                break   # breaks infinite while loop
            else:
                retvalue = SendIsField(callinfo, currruntime, currclass, cmiobject, fieldname)
                break   # breaks infinite while loop            

        # verify that the metaclass of the current class is a SagaPython class (i.e. SPClass)
        # (mostly a sanity check, but doesn't hurt)
        currclassclassLOID = currclassobjentry.GetCMIClass()
        try:
            currclassclassobjentry = SagaPythonSelf.GetObjectEntry(currclassclassLOID)
        except RuntimeError as exc:
            raise RuntimeError("Dispatch Method can't find current class's metaclass")

        currclassclassidata = currclassclassobjentry.GetCMIInstanceData(CMIConst.CMIClassLinearizationIndex)        
        currclassclasslintab = currclassclassidata.get(SPClassLinearization.CMIClassLinearizationConst.Lintabl, null)
        if currclassclasslintab == null:
            raise RuntimeError("Internal Class Error: No linearization table found")

        try:
            currclassclasslintab.index(CMIConst.SPClass)
        except ValueError as exception:
            raise RuntimeError("Metaclass of current class is not a class object") from exception

        # check field entry in currclass field table for a match        
        fieldentry = currclassobjentry.GetFieldEntry(fieldname) 
        if fieldentry == null:
            # give the ancestor a shot walking the linearization table
            if currclasslinearindex < 1:
                if local == False:
                    if callinfo != None:
                        # Not implemented - return 
                        ReturnValueNYI(callinfo)
                retvalue = NYI
                break

            currclasslinearindex -= 1
            currclass = headclasslintab[currclasslinearindex]
            if currclass == null or currclass == None:
                raise RuntimeError("Internal Class Linearization Table Error: Failed MRO search")
            continue    # top of while loop checks runtime and does send or post
        else:
            retvalue = currclass
            if local == False:                   # if there is an outstanding send or post, return message. 
                if callinfo != None:
                    ReturnValue(callinfo, retvalue)
            break
    
    return retvalue     # always returns the value locally, even if not used 

# DispatchField functions
#
# ListenDispatchField is called from the listener inbound code to set the callinfo for message return,
# and to set the local flag to false, postflag to true, is continuing resolution search to another runtime
def ListenDispatchField(currclass: LOID, cmiobject: LOID, readwriteflag, fieldname: str, arg, ci = None):

    if ci == None:
        raise RuntimeError("Internal Error: No callinfo")
    
    return DispatchField(currclass, cmiobject, readwriteflag, fieldname, arg, callinfo = ci, postflag = True, local = False)


# does an inheritance resolution on the field
def DispatchField(currclass: LOID, cmiobject: LOID, readwriteflag, fieldname: str, arg, callinfo = None, postflag = False, local = True):   

    try:
        objentry = SagaPythonSelf.GetObjectEntry(cmiobject)
    except RuntimeError as exc:
        raise RuntimeError("DispatchMethod invalid OID") from exc        

    headclassLOID = objentry.GetCMIClass()     # returns the LOID for the class of the passed in object handle

    try:
        headclassobjentry = SagaPythonSelf.GetObjectEntry(headclassLOID)
    except RuntimeError as exc:
        raise RuntimeError("Failed loading class of object") from exc

    idata = headclassobjentry.GetCMIInstanceData(CMIConst.CMIClassLinearizationIndex)
    headclasslintab = idata.get(SPClassLinearization.CMIClassLinearizationConst.Lintabl, null)
    if headclasslintab == null:
        raise RuntimeError("Internal Class Error: No linearization table found")

    if currclass == None:
        currclass = headclassLOID
        
    try:
        currclasslinearindex = headclasslintab.index(currclass)
    except ValueError as exception:
        raise RuntimeError("Current class not an ancestor. Head class: " + headclassLOID + " current class: " + currclass) from exception 

    while True:

        # check if the current class is a SagaPython class            
        try:
            currclassobjentry = SagaPythonSelf.GetObjectEntry(currclass)
        except RuntimeError as exc:
            raise RuntimeError("Dispatch Method can't find current ancestor class object")

        # check if same runtime, if not call send or post
        rtdata = currclassobjentry.GetCMIInstanceData(CMIConst.CMIClassRuntimeIndex)
        currruntime = rtdata.get(SPClassRuntime.CMIClassRuntimeConst.URL, null)
        if currruntime != CMI.GetLanguageRuntime():
            if postflag == True:
                retvalue = PostField(callinfo, currruntime, currclass, cmiobject, readwriteflag, fieldname, arg)
                break   # breaks infinite while loop
            else:
                retvalue = SendField(callinfo, currruntime, currclass, cmiobject, readwriteflag, fieldname, arg)
                break   # breaks infinite while loop            

        # verify that the metaclass of the current class is a SagaPython class (i.e. SPClass)
        # (mostly a sanity check, but doesn't hurt)
        currclassclassLOID = currclassobjentry.GetCMIClass()
        try:
            currclassclassobjentry = SagaPythonSelf.GetObjectEntry(currclassclassLOID)
        except RuntimeError as exc:
            raise RuntimeError("Dispatch Method can't find current class's metaclass")

        currclassclassidata = currclassclassobjentry.GetCMIInstanceData(CMIConst.CMIClassLinearizationIndex)        
        currclassclasslintab = currclassclassidata.get(SPClassLinearization.CMIClassLinearizationConst.Lintabl, null)
        if currclassclasslintab == null:
            raise RuntimeError("Internal Class Error: No linearization table found")

        try:
            currclassclasslintab.index(CMIConst.SPClass)
        except ValueError as exception:
            raise RuntimeError("Metaclass of current class is not a class object") from exception

        # check field entry in currclass field table for a match        
        fieldentry = currclassobjentry.GetFieldEntry(fieldname) 
        if fieldentry == null:
            # give the ancestor a shot walking the linearization table
            if currclasslinearindex < 1:
                # Not implemented - return 
                ReturnValueNYI(callinfo)
                retvalue = None, False
                break

            currclasslinearindex -= 1
            currclass = headclasslintab[currclasslinearindex]
            if currclass == null or currclass == None:
                raise RuntimeError("Internal Class Linearization Table Error: Failed MRO search")
            continue    # top of while loop checks runtime and does send or post
        else:
            # DoField in CMIClass does the actual read/write of the field in the CMI object instance data.
            retvalue = currclassobjentry.DoField(callinfo, currclassobjentry, headclassobjentry, currclasslinearindex, objentry, readwriteflag, fieldentry, arg)
            if local == False:                   # if there is an outstanding send or post, return message. 
                if callinfo != None:
                    ReturnValue(callinfo, retvalue)
            break
    
    return retvalue     # always returns the value locally, even if not used 



# Call CMI to send a message to the runtime of the currclass to search for field
# if we get there, need to find the language runtime implementation for passed in runtime string and send message
def PostField(callinfo, runtime: str, currclass: LOID, cmiobject: LOID, readwriteflag, fieldname: str, arg):
    runtimehandle = CMI.GetLanguageRuntime(runtime)
    if runtimehandle == None:
        raise RuntimeError("Language Runtime Process not found for: ", runtime)

    callinfo.runtime = runtimehandle
    CMI.SendMessage(callinfo, currclass, cmiobject, readwriteflag, fieldname, arg)
    # don't do a listen for a return here, should not receive one.

def SendField(callinfo, runtime: str, currclass: LOID, cmiobject: LOID, readwriteflag, fieldname: str, arg):
    runtimehandle = CMI.GetLanguageRuntime()
    if runtimehandle == None:
        raise RuntimeError("Language Runtime Process not found for: ", runtime)

    callinfo.runtime = runtimehandle
    msgid = CMI.SendMessage(callinfo, currclass, cmiobject, readwriteflag, fieldname, arg)
    
    return ListenFieldReturn(msgid)

def PostIsField(callinfo, runtime: str, currclass: LOID, cmiobject: LOID, fieldname: str):
    pass

def SendIsField(callinfo, runtime: str, currclass: LOID, cmiobject: LOID, fieldname: str):
    pass

def PostIsMethod(callinfo, runtime: str, currclass: LOID, cmiobject: LOID, methodname: str):
    pass

def SendIsMethod(callinfo, runtime: str, currclass: LOID, cmiobject: LOID, methodname: str):
    pass

def PostMethod(callinfo, runtime: str, currclass: LOID, cmiobject: LOID, methodname: str, args):
    pass

def SendMethod(callinfo, runtime: str, currclass: LOID, cmiobject: LOID, methodname: str, args):
    pass


# Listen is called at startup, and after any Send, waiting for an inbound message
def ListenFieldReturn(msgid: int) -> any:

    while True:

        rcvid = CMI.Listen()
        if rcvid != msgid:
            #DoInboundMessage(rcvid)

            retvalue = CMI.GetMessageArgs(rcvid)
        break

    return retvalue 

def ReturnValue(callinfo, retvalue):
    pass

def ReturnValueNYI(callinfo):
    pass









