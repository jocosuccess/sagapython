# body wrapper function 
# should load decorators and classes

# global dictionary of stub proxy classes
import collections
from proxytest import CMIproxyclass
from sagapythontypes import cmoid

class ClsObjVar:
    """ ClsObjVar proxy refere object for CMI  objects
    
    the callable caches the instance of the proxy class for the
     class of the CMI object. The proxy class is dynamically created
     with CMIBuildProxy, and is itself cached in the global
     CMI_proxyclasses dictionary. Any other ClsObjVar objects of the same
     class type will use the cached proxy class and just create a new
     instance. 
       """

    CMI_proxyclasses = collections.UserDict()

    def __call__(self):
        if self.proxyobj is None:
            if IsCMIObject(self.objoid) is None:
                raise RuntimeException("Invalid CMI object")
            CMIobjtype = CMIGetClass(self.objoid)
            if CMI_proxyclasses is None:
                #create CMIproxy class for the objid - then use it
                # proxyclasstr = CMIBuildProxy(self.objid)
                print("calling exec to create proxy class")
                exec(proxyclasstr, globals())
                CMIproxyclasses[] = CMIproxy               
            self.proxyobj = CMIproxyclass(self.objid)
        return self.proxyobj

    # When creating a ClsObjVar, the obj it is a proxy for may not
    # exist yet.  It is not an error to have a reference before 
    # creating the object.
    def __init__(self, objid):
        if isinstance(objid, cmioid):
            self.objid = objid
        else:
            self.objid = cmioid(objid)

        self.proxyobj = None

# call the main body of the transaction here
def bodywrapper():
    return (__body())

