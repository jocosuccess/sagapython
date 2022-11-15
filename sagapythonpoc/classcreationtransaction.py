#!/usr/bin/env python
# must run python3.9 or later


# Prototype of the transaction application
# This reads in the transaction script
# Then executes the sections separately.
# The sections are prepended with decorator functions,
# classes, etc.  These are prepended to the script code
# similarly, code is appended to execute the individual functions:
# __hdr, __body, __tail
# For production, the application would read the script either
# from a temporary file or from a pipe (stdin?)
#
#
# for prototype write a stub of a proxyobject - this would
# normally be created dynamically to be a stub for the
# actual CMI object's class inheritance tree, by CMIBuidProxy
# (which is also stubbed for prototype)
# It would be written as text in a buffer, and then the
# buffer is passed to exec as shown in the ClsObjVar
# The class name would be given a random name as it is
# "invisible" to the rest of the execution.
# included here for test purposes, with a static name
proxyproto = """class CMIproxy:

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



# For prototype -- just including some stub code
# This is the transaction script that would be submitted

stubscript = """
def __hdr():
    gas =  xxx
    maxpay = xxx
    account =<object ID>
    sig = <signature>

    print("called hdr")

def __body():
    print("called body")
    @SagaClass(ClsAsset, ClsFoobar, metaclass = )
    class ClsNFT:
        def method1(self):
            print("NFT method")

        fields = [{'sernum': int}, {'name': str}]
        
        def __init__(self, arg1, arg2):
            self.sernum = arg1
            self.name = arg2

    log(ClsNFT().oid)

    # similarity to standard python:
    # inst = ClsNFT(args)  - creates object instance or
    # inst = ClsNFT().New(args)
    inst = ClsNFT().CMINew(1234, "mynft")
    account().insert(inst)

    inst().method1()

    log(inst().oid)

    # make a method call using the proxy here, which should look like the class
    ClsNFT().method1()

    @SagaClass("another ancesto")
    class fooclass:
        def method1(self):
            print("called foo method1 class, should not happen")

    fooclass().method1()


def __tail():
    hash = xxx
    sig = elliptic curve sig
    print("called tail")        

"""

def __hdr():
    pass

def __body():

    inst = ClsObjVar(<oid>)
    inst().method1()
    
def __tail():

 def __body():
    inst = ClsObjVar(<oid>)
    res = inst().method1()
    if res == xyz:
        obj2 = ClsObjVar(<obj2's oid>)
        obj2().erromethod()
    else:
        <do something else>
        
        

# prepending code for SagaPython functions
# The CMIBuildProxy function will be precompiled and
# added as a compiled module. For prototype it is a stub of
# source code to demonstrate.
funccmiproxystub = """
def CMIBuildProxy(oid):
    return proxyproto

"""


# this is close to the code that would be included
# for ClsObjVar implementation - again would be precompiled - source for prototype
sagapythonclsobjvar = """
#initialize empty proxy dictionary for ClsObjVar objects
proxydict = dict()

class ClsObjVar:

    def __call__(self):
        if self.proxyobj is None:
            if self.objid not in proxydict:
                #create proxy class for the objid
                proxysrc = CMIBuildProxy(self.objid) # call to function that is added by the app
                exec(proxysrc, globals())
                proxydict[self.objid] = CMIproxy               
            self.proxyobj = proxydict[self.objid](self.objid)
        return self.proxyobj

    def __init__(self, objid):
        self.objid = objid
        self.proxyobj = None
        print(self.objid, objid)

"""

sagaclassdecorator = """def SagaClass(kwargs):
    # kwargs is referenced from the closure -- kwargs would be **kwargs
    # this is the means to capture the arguments for base classes and metaclass
    # for the call with the class object

    def classclosure(cls):
        # from kwargs:
        # resolve the base classes - create linearization
        # resolve the metaclass - create a ClsObjVar proxy
        # inspect the class for fields, methods, python code
        # generate the call to the metaclass to create the class with the 
        # results from the introspection.  The metaclass must know how to
        # create the class object data - including ancestor linearization
        # creates and returns a ClsObjVar with the objectID of the new class object
        print("class is: ", cls)
        return ClsObjVar(kwargs)

    return classclosure
"""
def preprocess(script):
    # modify script here
    return script
    
# TransactionApplication code starts here
if __name__ == "__main__":
    # read in the transaction script with either
    # stdin, or a passed in file (sys.argc, sys.argv)
    import sys

    # prototype faked
    txscript = stubscript

    # preprocess stubscript
    stubscript = preprocess(stubscript)

    # build program to execute
    progsrc = proxyproto + funccmiproxystub + sagapythonclsobjvar + sagaclassdecorator + txscript + "__body()"
    exec(progsrc, globals())



