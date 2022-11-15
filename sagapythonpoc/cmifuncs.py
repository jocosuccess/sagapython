# cmifuncs - calls to Go library to implement CMI calls

# from ctypes import *

def CMIGetClass(cmioid):
    ...

# need to return the class of the OID or raise an exception
# if an exception, this is an internal error.  Should never have an
# object without a type.