# sagapythontypes
from dataclasses import dataclass 

# number of bytes in a SHA256 hash and in an object ID
SHA256 = int(32)
SIZE_OID = int(32)

class cmioid:
    """ class cmioid
    
    Representation of the SHA256 32 byte array used by all CMI object IDs
    """
    def __init__(self, newoid):
        if isinstance(newoid, bytes):
            if len(newoid) > SIZE_OID:
                raise ValueError("OID size greater than 32 bytes")
            self.__oid = newoid
        else:
            raise TypeError("OID must be bytes")

    @property
    def oid(self):
        return self.__oid

    # should use a static method - for the implementation for init and setter
    # try that later
    @oid.setter
    def oid(self, newoid):
        if isinstance(newoid, bytes):
            if len(newoid) > SIZE_OID:
                raise RuntimeError("OID size greater than 32 bytes")
            self.__oid = newoid
        else:
            raise TypeError("OID must be bytes")

    # no deleter.  Not clear we need to be able to set it after initialized.
