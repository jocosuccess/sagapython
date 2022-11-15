# cmidecorators.py
#
# These decorators and associated globals are used to capture the 
# new class information created from the Python decorator/class behavior
# The method decorators are called first, followed by the class decorator for
# each class.
# we are not supporting nested classes.

import inspect
import ast
from dataclasses import dataclass
import pickle
import sagapythonglobals 
from CMILOID import LOID
import sagapythonself
from SPClass import SPClassConst

@dataclass(frozen=True)
class sPDecConst:
    # method flags
    final = 'final'
    public = 'public'
    protected = 'protected'
    private = 'private'

    # compile flags
    optimize = 'coptimize'  # defaults to 2 for max optimization
    dont_inherit = 'cdont_inherit'      # defaults to True
    flags = 'cflags'

    # field name
    sagafieldtable = 'SagaFieldTable'
    spfname = 'spfname'
    spfnshort = 'spfn'
    spftype = 'spftype'
    spftypeshort = 'spft'
    spfflags = 'spfflags'
    spfflagsshort = 'spff'

    # bitflags
    spfread = b'\x01'
    spfwrite = b'\x02'
    spfwriteonce = b'\x04'
    spffinal = b'\0x80'
SPDecConst = sPDecConst()

# each class entry recorded includes the list of baseclasses pass in.
# there are defined in the decorator, not in the class name itself.
# Python expects to be able to compile the classes with inheritance.
# There is probably a way to overide this with metaclass features,
# something for future work. 
#
# The args list and owner must be LOIDs only. default for owner is
# the system account
# Expect to add additional keywords here in the future

# To capture the methods, the method decorator is called for each method
# before the class decorator.  Because of this, the method decorator operators,
# method name are temporarily stored in a global list by the method decorator.
# When the class decorator is called, the current global list created by the
# method decorator is attached to the class entry.
# The class is then created, and the new LOID is stored alongside the 
# class name for use in the body of the transaction.

tempmethodlist = list()
classlist = list()
TestDebug = False

# example entry:
# {'metaclname': "<metaclsLOID>", 'clname': "<classname>", 'bcl': [ancloid1, ancloid2,], 'owner' : ownerloid, 'methods' : [], 'fields': []}

# The decorator function first captures the arguments passed
# then returns a function to capture the class name.
def CMIclassdec(*baselist, owner = sagapythonglobals.CMIConst.SPSystemAccount, metaclass = sagapythonglobals.CMIConst.SPMetaClass, classfinal = False):
    tempclass = dict()

    tempclass['cfinal'] = classfinal

    # check args to be LOIDs
    for x in baselist:
        bclist = []
        if not isinstance(x, LOID):
            raise RuntimeError("CMI Class creation error. Baseclasses must be LOID instances: ", x)

        bclist.append(x)

    tempclass['bcl'] = bclist

    if not isinstance(owner, LOID):
        raise RuntimeError("CMI Class creation error. Owner object must be LOID instance: ", owner)        
    tempclass['owner'] = owner

    if not isinstance(metaclass, LOID):
        raise RuntimeError("CMI Class creation error. Metaclass object must be LOID instance: ", metaclass)
    tempclass['metaclname'] = metaclass
    
    def CMIClassCapture(cls):
        global tempmethodlist
        global classlist
        tempclass['cls'] = cls                    # capture the class object for later interrogation
        tempclass['methods'] = tempmethodlist.copy() # capture the CMI method list that was stored by the method decorators (technically python functions, not bound methods)
        classlist.append(tempclass.copy())
        tempmethodlist = []
        return None

    return CMIClassCapture

# The method decorator function captures the method name and builds the entry
#    SPMethodQualName = 'qmn'
#    SPMethodName = 'mn'
#    SPMethodFlags = "mf"
#    SPCompileFlags = "mcf"   # flags for the exec() Python call
#    SPDontInherit = "mdi"
#    SPMethodSourceName = "msrcn"  # name of function in source to call in exec
#    SPMethodSource = "msrc"
#    SPArgTypes = "atypes"       # list of types, supports varargs as last entry
#    SPReturnTypes = "rtypes"    # list of return types. need to support tuple return

# method flags
# SPMethodFinal = 'f'    # (final)
# SPMethodPublic = 'pb'  # (public) 
# SPMEthodProtected = 'pr' # (protected)
# SPMethodPrivate = 'pv'  # (private)


def CMIMethoddec(*args, **kwargs):
    """arguments to the method decorator:
        'final' or (final = true/false)
        'public' or (public = true/false)
        'protected' or (protected = true/false)
        'private' or (private = true/false)

        flags to the compiler for the method - unlikely to be used
        by default, ast.PyCF_TYPE_COMMENTS is passed in so that all typing features can be used
        ast.PyCF_ONLY_AST is disallowed and will be removed if present
"""

    tempmethoddict = {'fn': None, 'args': args, 'kwargs' : kwargs}
    def CMIMethodCapture(fn):
        global tempmethodlist
        if inspect.isfunction(fn) != True:
            raise RuntimeError("CMI Method creation error. Methods must be valid Python functions: ", fn)
        tempmethoddict['fn'] = fn
        tempmethodlist.append(tempmethoddict)

        if TestDebug == True:
            print("methodname: ", tempmethoddict['fn'].__qualname__)
            print("args: ", tempmethoddict['args'])
            print("kwargs: ", tempmethoddict['kwargs'])
        return fn
    return CMIMethodCapture

# Note: CMIFields is a Python list object with the names of the fields in the class
# These are removed from the class dictionary for local python objects. 
# The rest are pickled as python class objects -- need to review what else needs to be
# removed.  

# after the function containing the classes is called,
# the classlist should be populated.
# the classes should be in a locals dictionary
# The classes are processed by reading the source for
# all of the methods and storing them in the method table entries.
# should also read the signatures for the arguments.
# For the fields, need to read the CMIField list for the names
# of the fields. Then retrieve the attributes and types from
# the class dictionary.
# For the local python objects, remove the entries in the dictionary
# that are Python class related
# This will capture all the local attributes including local methods
# returns a list of pairs of classnames and LOIDs

def BuildCMIClasses() -> list:
    global classlist
    
    classloids = list()

    for cmiclass in classlist:

        cmimtds = cmiclass['methods']
        # create method table entries
        # read source code with inspect
        # note need to capture signature
        mtdentries = list()
        for cmimtd in cmimtds:
            if inspect.isfunction(cmimtd['fn']) != True:
                raise RuntimeError("Found a non-method when expecting a method: ", cmimtd['fn'])
            mtdentry = dict()
            cmimtdsrc = inspect.getsource(cmimtd['fn'])
            mtdstart = cmimtdsrc.find('def')
            cmimtdsrc = cmimtdsrc[mtdstart:]
            mtdentry[SPClassConst.SPMethodQualName] = cmimtd['fn'].__qualname__
            mname = cmimtd['fn'].__qualname__.rpartition('.')
            mtdentry[SPClassConst.SPMethodName] = mname[2]
            mtdentry[SPClassConst.SPMethodSourceName] = mname[2]
            mtdentry[SPClassConst.SPMethodSource] = cmimtdsrc
            mtdentry[SPClassConst.SPArgTypes] = None            # need to read type annotations here in future and translate to JSON schema
            mtdentry[SPClassConst.SPReturnTypes] = None         # need to read type annotations here in future and translate to JSON schema

            mtdargs = cmimtd['args']
            mtdkwargs = cmimtd['kwargs']

            mtdflags = dict()
            mtdflags[SPClassConst.SPMethodFinal] = True
            mtdflags[SPClassConst.SPMethodPublic] = True
            mtdflags[SPClassConst.SPMEthodProtected] = False
            mtdflags[SPClassConst.SPMethodPrivate] = False

            # read the method flags 
            if SPDecConst.final in mtdargs:
                mtdflags[SPClassConst.SPMethodFinal] = True
            else:
                try:
                    mtdflags[SPClassConst.SPMethodFinal] = mtdkwargs[SPDecConst.final]
                except:
                    pass

            if SPDecConst.public in mtdargs:
                mtdflags[SPClassConst.SPMethodPublic] = True
            else:
                try:
                    mtdflags[SPClassConst.SPMethodPublic] = mtdkwargs[SPDecConst.public]
                except:
                    pass

            if SPDecConst.protected in mtdargs:
                mtdflags[SPClassConst.SPMEthodProtected] = True
            else:
                try:
                    mtdflags[SPClassConst.SPMEthodProtected] = mtdkwargs[SPDecConst.protected]
                except:
                    pass

            if SPDecConst.private in mtdargs:
                mtdflags[SPClassConst.SPMethodPrivate] = True
            else:
                try:
                    mtdflags[SPClassConst.SPMethodPrivate] = mtdkwargs[SPDecConst.private]
                except:
                    pass

            mtdentry[SPClassConst.SPMethodFlags] = mtdflags

            # compile flags
            cflags = ast.PyCF_TYPE_COMMENTS
            
            try:
                cflags = mtdkwargs[SPDecConst.flags]
            except:
                pass

            mtdentry[SPClassConst.SPCompileFlags] = cflags

            # optimize flag
            oflag = 2
            try:
                oflag = mtdkwargs[SPDecConst.optimize]
            except:
                pass

            mtdentry[SPClassConst.SPOptimize] = oflag

            # dont inherit flag
            dflag = 1
            try:
                dflag = mtdkwargs[SPDecConst.dont_inherit]
            except:
                pass

            mtdentry[SPClassConst.SPDontInherit] = dflag

            mtdentries.append(mtdentry)
      
        # read field table list here
        # note need to capture signature

        fieldentries = [None]
        try:
            fields = cmiclass['cls'].__dict__[SPDecConst.sagafieldtable]       
        except:
            fields = [] 

        for infield in fields:
            fieldentry = dict()
            newk = list(infield)
            if SPDecConst.spfname in newk:
                fieldentry[SPClassConst.SPFieldName] = infield[SPDecConst.spfname]
            elif SPDecConst.spfnshort in newk:
                fieldentry[SPClassConst.SPFieldName] = infield[SPDecConst.spfnshort]
            else:
                raise RuntimeError("Field entries must specify fieldname in map: ", infield)

            if SPDecConst.spfflags in newk:
                fflags = infield[SPDecConst.spfflags]
            elif SPDecConst.spfflagsshort in newk:
                fflags = infield[SPDecConst.spfflagsshort]
            else:
                fflags = None
                
            fieldentry[SPClassConst.SPFieldReadFlags] = True
            fieldentry[SPClassConst.SPFieldWriteFlags] = True
            fieldentry[SPClassConst.SPFieldWriteOnceFlags] = False
            fieldentry[SPClassConst.SPFieldFinalFlag] = False

            if fflags != None:
                fieldentry[SPClassConst.SPFieldReadFlags] = fflags & SPDecConst.spfread
                fieldentry[SPClassConst.SPFieldWriteFlags] = fflags & SPDecConst.spfwrite
                fieldentry[SPClassConst.SPFieldWriteOnceFlags] = fflags & SPDecConst.spfwriteonce
                fieldentry[SPClassConst.SPFieldFinalFlag] = fflags & SPDecConst.spffinal

            fieldentry[SPClassConst.SPFieldType] = None         # field type should be JSON schema string

            # note: should check field type as valid JSON syntax here, at least must be a string
            if SPDecConst.spftype in newk:
                st = infield[SPDecConst.spftype]
            elif SPDecConst.spftypeshort in newk:
                st = infield[SPDecConst.spftypeshort]
            else:
                st = None

            if st != None:
                if not isinstance(st, str):
                    raise RuntimeError("Field type must be valid JSON schema: ", st)

            fieldentry[SPClassConst.SPFieldReadFlags] = st
                
            fieldentries.append(fieldentry)
            
        # remove field names and method names from
        # class dictionary, remove the python specific
        # names, and pickle the rest.
        clsdict = cmiclass['cls'].__dict__.copy()

        delkeys = ['__module__',
                    '__dict__',
                    '__weakref__',
                    '__doc__',
                    '__init__',
        ]

        # delete the default names
        cdkey = list(clsdict)
        for dk in delkeys:
            if dk in cdkey:
                del clsdict[dk]
        
        # delete all CMI methods
        for mtdentry in mtdentries:
            mtdname = mtdentry[SPClassConst.SPMethodName]
            if mtdname in cdkey:
                try:
                    del clsdict[mtdname]
                except:
                    pass

        # this is intended to pick up any python methods and
        # class static python objects
        pyobjects = clsdict

        # create the CMI class object
        if TestDebug != True:
            metaclass = sagapythonself.ClsObjVar(cmiclass['metaclname'])
            newclassloid = metaclass.new(cmiclass['owner'], 
                                        cmiclass['bcl'],
                                        fieldentries, 
                                        mtdentries,
                                        None, 
                                        cmiclass['cfinal'], 
                                        pyobjects)
        else:
            newclassloid = LOID("DEADBEEF")

        # store the new LOID in a new pair
        classloids.append((cmiclass['cls'].__qualname__, newclassloid[0]))      

    return classloids

# for unit test
if __name__ == '__main__':

    TestDebug = True

    import CMI
    from baseobjects import *

  # test creating the foundation class objects, bootstrap. should not exist in production system with bootstrap database
    CreateTheClassObject()
    CreateTheClass()
    CreateTheClassLinearization()
    CreateTheClassRuntime()
    CreateTheMetaClass()
    CreateTheMetaMetaClass()
    CreateTheClassAccount()
    CreateTheSystemAccount()
    CMI.ClearObjectTable()      # bootstrap function - should not exist in production system, with bootstrapped database

    SagaClass = CMIclassdec
    SagaMethod = CMIMethoddec       

    @SagaClass(sagapythonglobals.CMIConst.SPClassObject)    # no signature required for creating global classes 
    class ClsNewOne:

        @SagaMethod()
        def dummymethod(self):
            pass

    classloids = BuildCMIClasses()

    # dump out tables here
    for x in classloids:
        print("class name: ", x[0])
        print("class LOID: ", x[1])

    TestDebug = False
    classloids = BuildCMIClasses()
    for x in classloids:
        print("class name: ", x[0])
        print("class LOID: ", x[1])
    




