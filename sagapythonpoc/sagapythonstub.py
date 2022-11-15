# sagapythonstub implementation.  
#
# Algorithms:
# implements getattribute and setattr, delattr is blocked, and getattr is blocked
# Does set/read the OID locally that it is a stub for
#
# getattribute(self, name):
# the name value is either a field or method name or an ancestor class name
# For the ancestor class it is prepended with "C_" followed by the OID, or
# "CN__" followed by a string classname
# The OID is in base64. Not URL safe since these are OIDs
#
# If the class method and field table have not been loaded for the object yet,
# the stub gets the class type of the object, and then sends a message to the
# class with a request for the method and field table.
# We can include a shortcut where if the metaclass is of the known SagaPython metaclass
# then the tables can be read directly.
# If not, then the message is sent to the class, to get the tables.
# The tables are then stored locally in a class map with an object for each
# 
# Note: The ancestor class syntax can not be used to store the ancestor class reference
# directly.  The stub writes over the previous values.
# To do so, need to do a deep copy of the returns object.  The deepcopy allows
# for adding local attributes to the ClsObjVar instance. If none are used, then
# shallow copy is sufficient -- ClsObjVar does not have any nested objects.
# copy.copy(obj) or copy.deepcopy(obj)

import copy

class ClsObjVar:
    def __init__(self, OID64: str) -> None:
        if not isinstance(OID64, str):
            raise TypeError("OID must be of type or subtypes of str")
        super().__setattr__("_ClsObjVar__oid64", OID64)
        #super().__setattr__("_ClsObjVar__headClass", SPGetCMIType(OID64))
        super().__setattr__("_ClsObjVar__headClass", "10")
        super().__setattr__("_ClsObjVar__CMIparameters", True)
        super().__setattr__("_ClsObjVar__currclass", self.__headClass)

    def __getattribute__(self, __name: str):
        """getattribute in the stub returns either the value for a field,
        a callable for a method, or a an object with another getattribute
        (the object returned is the same stub)"""
        print (__name)
        try:
            val = super().__getattribute__(__name)
            return val
        except:
            pass

        super().__setattr__("_ClsObjVar" + "__CMIparameters", False)

        # check if the name is a C_ or CN__ first, and if 
        # searching the class tree is currently allowed.
        # If a class search has already happened, then 
        # don't search twice on the dot operator until
        # either a field, method or failure is returned
        if __name.startswith("C_"):
            self.__currclass = self.findancestorbyOID(__name)
            return self    

        elif __name.startswith("CN_"):
            self.__currclass = self.findancestorbyName(__name)
            return self

        else:
            val, valid = self.GetField(__name)     # returns with valid = true if this is a field and found, and val is set
            if valid == True:
                self.__currclass = self.__headClass
                self.__CMIparameters = True
                return val
            
            # not a field, check if it is a method
            mtd = self.GetMethod(__name)
            if mtd == None:
                self.__currclass = self.__headClass
                self.__CMIparameters = True
                raise AttributeError

            return(ClsObjVarMethod(self, self.__currclass, mtd))
             
    def __setattr__(self, __name, __value):

        # if name mangled, it is a local variable only, otherwise, CMI Field names take precedence
        print ("set: ", __name, " value: ", __value)
        valid = False
        if  not __name.startswith("_ClsObjVar__"):
            valid = self.__SetField(__name, __value)
        if valid == False:
            super().__setattr__(__name, __value)

        super().__setattr__("_ClsObjVar__currclass", getattr(self, "_ClsObjVar__headClass"))
        super().__setattr__("_ClsObjVar__CMIparameters", True)
        return

    def __call__(self, *args, **kwargs):
        """If this is a direct call on the ClsObjVar instance, then the parameters are
        for the CMI calling parameters.  
        If this is for a method, then the parameters are for the method. """
        if self.__CMIparameters != True:
            raise RuntimeError("Non-callable")            
        else:
            # this is for the CMI parameters
            self.SetCMIParameters(*args, **kwargs)
            self.__CMIparameters = False   # next call is either a method or field   
            return self

    def SetCMIParameters(self, *args, **kwargs):
        pass

    def GetMethod(self, mtdname):
        pass

    def GetField(self, fieldname):
        pass

    def __SetField(self, fieldname, value):
        pass

    def findancestorbyOID(self, __name):
        return ("foundancestorbyoid")

    def findancestorbyName(self, __name):
        return ("foundancestorbyname")


    # CMI stub method type.    
class ClsObjVarMethod:
    """ClsObjVarMethod enables returning a method that can be
    stored and used like any other method. CMI Fields do not support
    storing objects in general. The method object can be stored in internal Python objects"""

    def __init__(self, stubobj, currclass, currmethod) -> None:
        self.__stubobj = stubobj        # used to look up the object instance, and the method table for the class
        self.__currmethodname = currmethod
        self.__currclass = currclass

    def __call__(self, *args, **kwargs):
        
        if self.__currclass == None or self.__currmethodname == None:      # sanity check      
            raise RuntimeError("Got callable method without current class or current method set")
            
        return(self.DoMethod(*args, **kwargs))

    # Does the method stub call
    def DoMethod(self, *args, **kwargs):
        pass
    
