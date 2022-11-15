# cmimasquerade.py
#
# Functions that will be implemented in Go in the CMI library when written.
# Meantime faking them as Python code.
#
# The CMI knows how to do the following functions:
# 1: Read and write an object to the database using the OID as a key.
# Technically the CMI does this by messaging to a database server.
#
# 2: CMI manages shared memory among all the processes, all of which
# access the shared memory through the CMI layer. The sharing is transparent
# to the upper layers.
#
# 3: CMI knows that each object starts with an OID for the type of the object
# This can be interrogated by upper layers.
# 
# 4: CMI knows how to do a method and field dispatch by walking from the object
# to the class object, to the metaclass object, to the dispatch object.
# 4.1: CMI knows how to message the dispatch object with the metaclass, class,
# object, method and arguments (or field and value if a write)
# 4.2: CMI does not know the arguments. They are all passed as opaque byte arrays
#
# 5: CMI knows how to do method or field resolution given the method or field,
# and object instance by asking the class, metaclass and dispatch to do the lookup.
# CMI walks from the object to the dispatch object and then messages the dispatch 
# object with the head class, current class index, metaclass, the method or field.
# 5.1: The dispatch object may return an ancestor class by index to try  
# 5.2: The dispatch object is responsible for managing the linearization of the 
# ancestors and the index into the head class linearization table. The CMI
# does not have knowledge of the linearization directly. 
#
# 6: In general for dispatching of any message, the CMI walks the chain
# object-class-metaclass-metametaclass.  The metametaclass is the dispatch
# that receives the message. It is then its responsibility to perform the
# action.
#
# 7: CMI provides a property layer fo the objects. An object consists
# of a first property for the OID, followed by any number of properties
# indexed incrementally.  The CMI does not know contents of these directly.
#
# 8: CMI has some internal messages it uses to dispatch to objects for
# persistence across transactions: reading from the database, writing back
# to the database.
#
# 9: CMI provides a send/listen interface callable from any language
# The send is non-blocking. All messages go through the send interface
# The return from a listen may either be the result of a send, or another
# message. It is a requirement that results are never returned out of order.
# No multithreading is allowed, only run-to-completion. The CMI does
# not implement callbacks to make integration easier with other languages.
#
# Although not directly necessary, always like objects and methods/fields
# over modules and functions/globals. Personal likes.

from collections import OrderedDict, UserList

# faking the database here mapped by OID. The only global.
# Even though there should only be one CMIMasquerade
# instantiated, still keeping this global 
class CMISharedMemory:

    def __init__(self):
        self.OIDDb = OrderedDict()
    
        # faking the objects read in here - this would be in shared memory
        # as a Go map object
        self.ObjectTableMap = OrderedDict()

        # faking an indexed lookup into the read in objects for performance
        # when walking the object types
        self.ObjectTableIndex = UserList()



class CMIMasquerade:
    """CMIMasquerade pretends to be the CMI layer. In the future there
    will be a Go library linked in to provide the actual functions"""
   
    def __init__(self, sharedmemobj: CMISharedMemory):
        self.sharedmem = sharedmemobj

    def CMISendMessage(self):
        pass

    def CMIListen(self):
        pass
    
    def CMIReadObject(self):
        pass

    def CMIWriteObject(self):
        pass

    def CMIGetClassMetaDispatch(self, obj):
        """returns the list of the obj's class, metaclass and metametaclass
        The metametaclass is known as the dispatch class object"""
        pass

    def CMIGetMetaDispatch(self, cls):
        """Given the class of an object, returns the metaclass and dispatch class"""

    def FindMethodImmediate(self, obj, index, mtd):
        """FindMethodImmediate only looks as the class's method and field table
        with no inheritance or overrides. Used for walking the inheritance tree.
        If the lookup fails, the ancestor class is returned. """
        pass

    def FindMethod(self, obj, mtd):
        """FindMethod expects the object to be the current head class, and looks
        at the method and field table that includes all the overrides and inheritance. Must
        not be used if traversing the ancestors, only on the head class. A failed lookup
        here means the method is not implemented in the head class or any ancestor"""
        pass

    def FindFieldImmediate(self, obj, index, field):
        pass

    def FindField(self, obj, field):
        pass

