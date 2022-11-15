
# Decorators are called once as they are loaded.
# They can be closures.
# In the case of defining a new class, the class can be
# stored in the closure.
# When the class name is referenced, it calls the returned
# closure.  In this case, the class then creates an instance
# of the class, and everything works
# The decorator therefore receives the class object.
# What it returns should act like a class which means it
# should be a callable if we want to maintain the <classname()>
# syntax to create an object.
# Alternatively, we can return a ClsObjVar proxy, after 
# creating the class.

#def test1(cls):
#    print("got cls", cls)
#    def clsfunc(arg):
#        return cls(arg)
#    return clsfunc

#@test1
#class test2:
#    def __init__(self, arg1):
#        self.n = arg1

#pseudo code for CMI class creation
# def SagaClass(cls):
    # create CMI class here
    # ...
    # create proxy object for class
    # as ClsObjVar instance (call it objvar)
    # def classobj():
    #   return objvar   - 
    #   
    # return classobj   return the closure

# @SagaClass
# class CMIclass:
#   def __init__(self, args)
#       self.... = ...

def GIGO():
    class ProxyClass:
     def m1(self):
         print("got m1 in proxy")
     def __newCMI__(self):
         print("make new instance here")

    class ClsObjVar:
        def __init__(self):
            self.proxy = ProxyClass()  

        def __call__(self):             # this would normally create the proxy class and object
            print("got ClsObjVar call")
            return self.proxy
    
    class classclass:
        pass

    def SagaClass(cls):
        # would create CMI class here
        # then create a proxy class and object - optionally, might do lazy here
        # then assign to ClsObjVar
        # then return ClsObjVar instance
        objvar = ClsObjVar()
        return objvar

    @SagaClass
    class foo():
        def m1():
            print("shouldn't be called")

    # can't use metaclass keyword directly with class keyword becuase it forces the python metaclass model.
    # we don't want that. Also, don't want Python MRO on the base classes.  Can we use the arguments and keywords approach?
    def SagaClassTest(f):
    # interrogate f here
    # read arguments - do CMI inheritance - do CMI metaclass
    # pretend to call __init__()
        print("f:", f)
        f()
        return f

    #@SagaClassTest
    def cmiclass(arg1, metaclass="foo"):
        def __init__(self):
            print("test")

    def anothermethod():
        print("not amethod")

    # as though this is a class
    def SagaMethod(f):
        print("this is a sagamethod")
        return anothermethod

    @SagaClassTest
    def aclass():
        @SagaMethod
        def amethod():
            print("this is a method")

        amethod()

    class foobar:
        print("hello from foobar")
    
# approach for SagaPython baseclasses and metaclass
# the decorator function takes the arguments.
# the arguments must be ClsObjVar objects.
# returns a closure that is then called with the
# class.  Closure interrogates the class to make
# a CMI class, and then returns a ClsObjVar object
# as a proxy.  ClsObjVar is not callable to force
# the synax to use the function proxy notation.
# to create a new object, must use the explicit CMINew method
# The CMINew method is in the metaclass, not the class object
# as the class object is the instance in this case.

# code that is included by the Transaction Application transparently
class ClsObjVar:
    # proxy code here
    def __init__(self, oid):
        self.oid = oid
        self.proxy = None
        print("create ClsObjVar. oid:", oid)

    def __call__(self):     # should return proxy object here with descriptors for members, self for testing
        return self

    def method1(self):
        print("called proxy method")
        print("oid: ", self.oid)

def SagaClassWArgs(kwargs):
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
        print("what is kwargs: ", kwargs)
        print("class is: ", cls)
        return ClsObjVar(kwargs)

    return classclosure



#user code here:
def __body():

    @SagaClassWArgs("test kwargs")
    class sagaclass:
        def method1(self):
            print("called class method - should not have")

    # make a method call using the proxy here, which should look like the class
    sagaclass().method1()

    @SagaClassWArgs("another kwargs, newclass")
    class fooclass:
        def method1(self):
            print("called foo method1 class, should not happen")

    fooclass().method1()

# and execute the body here
print("executing body")
__body()




























