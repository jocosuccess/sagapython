# simple test code to build towards descriptors

# Using callable for an object instance instead of
# a descriptor. Descriptors aren't called from instance variables
# only class variables. The difference is that we have to use
# object().mtd() syntax instead of object.mtd()

def callfield(oid,fieldname):
    print("callfield, return some value as CMI result")
    print("oid: ", oid, "field :", fieldname)
    return 123445


proxyclasstr = """class CMIproxy:

    def __init__(self, oid):
        self.oid = oid
        self._field1 = "cmifield1"
        self._field2 = "cmifield2"

    @property
    def field1(self):
        print("cmifield1")
        return callfield

    @field1.setter
    def field1(self, value):
        print("set value: ", value, "on cmifield1")

    @property
    def field2(self):
        print("cmifield2")
        return self._field2

    @field2.setter
    def field2(self, value):
        print("set value: ", value, "on cmifield2")

    def method1(self):
        print(self.oid)
        print("method1")

    def method2(self, r: int, t: float):
        # dynamic type verification here
        print(self.oid)
        print("method2")
"""
    
#simulating a global dictionary of proxy classes    
CMIproxyclass = None

class clsobjvar:

    # use class variable here for dictionary of proxy classes already created
    #proxyobj = None

    def __call__(self):
        if self.proxyobj is None:
            global CMIproxyclass
            if CMIproxyclass is None:
                #create CMIproxy class for the objid - then use it
                # proxyclasstr = CMIBuildProxy(self.objid)
                print("calling exec to create proxy class")
                exec(proxyclasstr, globals())
                CMIproxyclass = CMIproxy               
            self.proxyobj = CMIproxyclass(self.objid)
        return self.proxyobj

    def __init__(self, objid):
        self.objid = objid
        self.proxyobj = None
        print(self.objid, objid)


class Container:

    def __init__(self, oid):
        self.objvar = clsobjvar(oid)

   # def __call__(self, oid):
   #     type(self).objvar.__init__(oid)
    #    return self

# Introspection and type hints

def foo():
    pass

import typing

class test1:
   # class test2:
   #     def __init__(self):
   #         print("init self 2")
   #         self.y = 10
#
#        def method1(self):
#            print("test2 method1")

    def __init__(self):
        print ("init test1")
        self.xzzy: int  = 123 
        self.yup: str = "nope"
        self.blah = foo

    def method1(self):
        print("test1 method1")

    nnnn: int = 0

    class test2:
        y: int = 1
        z: str = "sss"

import inspect


def memberfunc(val): 
    #print(val)
    if -1 == str(val).find("{"):
        return False
    return True 

xx = test1()

#x = inspect.getsource(test
#print(x)
x = inspect.getmembers(xx, memberfunc)
print(x)
print(typing.get_type_hints(test1.test2))

def test3(cls):
    print("decorator test3")

@test3 
class test4: 
    pass

class ancestor:
    def __init__(self):
        print("ancestor init called")
        self.__x = 10
        self.x = self.__x + 1

    def ancestorprint(self):
        print (self.x)
        print (self.__x)

class child(ancestor):
    def __init__(self):
        print("child init called")
        self.x = 20
        self.__x = 200
        super().__init__()

    def childprint(self):
        print(self.x)
        print(self.__x)
        print(self.z)





if __name__ == "__main__":
    import sys
    



