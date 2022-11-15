# SPClass.py
# Defines the fields for all classes.  
# All classes are instances of SPClass
# MetaMetaClass inherit from SPClass which makes it both
# an instance of SPClass and creator of instances of SPClass as class objects.
# MetaClass inherits form SPClass which makes it both
# an instance of SPClass and a creator of objects of type SPClass
# Since classes have at least type MetaClass, they are instances of SPClass
# Since MetaClass has at least type MetaMetaClass, it is an instance of SPClass

from dataclasses import dataclass
from sagapythonself import *

@dataclass(frozen=True)
class sPClassConst:
    # SPClass field table entries
    MethodTable = "mtbl"
    FieldTable = "ftbl"
    ExtendedMethodTable = "emtbl"
    ExtendedFieldTable = "eftbl"
    Classname = "qcln"
    BaseClassList = "bcl"
    ClassFinalFlag = "cf"
    ImportObjectsList = "imps"
    Pyobjects = "py"

    # method table entry dictionary fields
    # Need JSON Schema for this
    SPMethodQualName = 'qmn'
    SPMethodName = 'mn'
    SPMethodFlags = "mf"
    SPCompileFlags = "mcf"   # flags for the exec() Python call
    SPDontInherit = "mdi"
    SPOptimize = 'o'
    SPMethodSourceName = "msrcn"  # name of function in source to call in exec
    SPMethodSource = "msrc"
    SPArgTypes = "atypes"       # list of types, supports varargs as last entry
    SPReturnTypes = "rtypes"    # list of return types. need to support tuple return

    # method flags:
    SPMethodBuiltin = 'bn' # (builtin)
    SPMethodFinal = 'f'    # (final)
    SPMethodPublic = 'pb'  # (public) 
    SPMEthodProtected = 'pr' # (protected)
    SPMethodPrivate = 'pv'  # (private)

    # compile flags
    coptimize = 'coptimize'  # defaults to 2 for max optimization
    cdont_inherit = 'cdont_inherit'      # defaults to True
    cflags = 'cflags'

    # field table entry dictionary fields
    # Need JSON Schema for this
    SPFieldName = 'fn'
    SPFieldReadFlags = "rf"
    SPFieldWriteFlags = "wf"
    SPFieldWriteOnceFlags = "wo"
    SPFieldFinalFlag = "ff"
    SPFieldType = "ft"         # field type must be a json schema where the LOID is a primitive

    # Method Names
    SPClassNew = "new"
    SPClassInit = "init"
SPClassConst = sPClassConst()

