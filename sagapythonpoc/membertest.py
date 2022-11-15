from typing import *

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
    def __init__(self, func, obj, cmiargs):
        self.__func__ = func
        self.__self__ = obj
        self.__cmiargs__ = cmiargs

    def __call__(self, *args, **kwargs ):
        func = self.__func__
        obj = self.__self__
        cmiargs = self.__cmiargs__
        return func(obj, cmiargs, *args, **kwargs)

def CMIFunc(self, cmi, *args, **kwargs ):
    print("got to CMIfunc fake method")
    print("cmiargs: ", cmi)

class CMIstub:

    def __init__(self, clsobj, cls2):
        self.CMIanccls = clsobj
        self.CMIanccls2 = cls2
        self.oid = 10
        self.call = "Local"

    def __getattribute__(self, name: str):
        print("stub call: ", name)
        print("oid: ", object.__getattribute__(self, "oid"))
        print("self.call: ", object.__getattribute__(self, "call"))

        # the following would check for all of the CMI variables here - looking for methods, then classnames. There
        # is a conflict between method, fields and ancestor classes. 
        if name == "baseobj":
            val = fake()
        elif name == "fakemtd":
            # create a fake method with the name fakemtd passed in,
            # simulates concept of call CMI 
            return CMIMethodType(CMIFunc, self, "cmiarglist")
        else:
            val = object.__getattribute__(self, name)
        self.call = "Local"
        return val

    def __call__(self, call="Local"):             # this would normally create the proxy class and object
            self.call = call
            print("got ClsObjVar call")
            return self


class fake:
    def notreal(self):
        print("found not real")

    # and the fake object can have another fake attribute
    # if a method, it could return as a closure callable object
    def __getattribute__(self, name: str):
        if name == "notreal":
            return object.__getattribute__(self, "notreal")
        else:
            class tempFunc:
                def __call__(self, mtdname):
                    self.mtd = mtdname      # could be set in an init()
                    return self

                def __getattribute__(self, name: str):
                    print("mtdname: ", object.__getattribute__(self, "mtd"))
                    print("")
            return (tempFunc(name))        

class CMIancestor:
    def mtd(self):
        print("got mtd")

class CMInomtd:
    def __getattribute__(self, __name: str) -> Any:
        print("get attribute name: ", __name)

anc = CMIancestor()
anc2 = CMInomtd()
stub = CMIstub(anc,anc2)

stub(call="Withdef").CMIanccls.mtd()
stub(call="Remote").baseobj.notreal()
stub.baseobj.notreal()
stub.fakemtd("blahblah")