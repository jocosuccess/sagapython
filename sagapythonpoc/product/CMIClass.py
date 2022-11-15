# CMIClass
#
# The CMIClass is the code that the dispatch method calls to interface with the
# raw object instance data read from the CMI object database.
# This could be done as all global functions, but putting them in a class
# create a name space, and if needed, can be easily subclassed in the future.
# There is an instance of this created when reading in an object by the GetObjectEntry
# function.  The class is named ClassTableEntry and inherits from ObjectTableEntry.
# Technically the raw CMI object may or may not be a class. However, it's easier
# to not distinguish between them for loading the object.
# 

from dataclasses import dataclass
import sys
from sagapythonglobals import *
import CMI
import CMIObjectData
import sagapythonself 
import SPClass
import SPClassLinearization 

@dataclass(frozen=True)
class cMIClassTableEntryConst:
    # execscript constants must match in execscript src
    SPBuiltin = "SPBuiltin_"
    SPExec = "SPExec_"
    SPExecMethod = SPExec + "Method"
    SPExecArgs = SPExec + "Args"
    SPExecSelf = SPExec + "Self"
    SPExecReturn = SPExec + "Return"
    SPExecError = SPExec + 'Error'

CMIClassTableEntryConst = cMIClassTableEntryConst()

class ClassTableEntry(CMIObjectData.ObjectTableEntry):
    execscript = [None]   # set when the first instance is created. 

    def __init__(self, handle, oid, index, idatalen):
        super().__init__(handle, oid, index, idatalen)
        self.mtdtable = None   # points at method table in object
        self.extendedmtdtable = None
        self.mtdcache = dict()  # indexed by method name, each is a tuple of the compiled object and function object
        self.fields = None    # points to field table in idata, a convenience field
        self.baseclasslist = None  # list of base classes for multiple inheritance
        self.lintab = None
        self.importdict = None # dynamic list of import globals
        self.sysmodules = dict() # dynamic list of sysmodules for imports
        self.globals = dict()
        if ClassTableEntry.execscript[0] == None:
            ClassTableEntry.execscript[0] = self.CompileExecScript()

    # By definition, the field and method tables accessed in ClassTableEntry
    # are always in the SPClass instance data. It is guaranteed that these calls
    # are only applied to class objects not ordinary objects. This is verified
    # by the dispatch code, and the ClsObjVar/SagaPythonSelf code before making the call
    # There is no way to verify from within this call, so screwing it up will crash 
    # the system with random errors.  So don't fuck it up!
    def GetFieldTable(self):
        if self.fields == None:
            self.fields = self.GetCMIInstanceData(CMIConst.CMIClassIndex).get(SPClass.SPClassConst.FieldTable, null)

        if self.fields == null:
            RuntimeError("Internal Class Error: No Field Table")
        return self.fields

    def GetFieldEntry(self, fname):
        tble = self.GetFieldTable()
        for i in range(len(tble)):
            if tble[i] != None:
                if tble[i][SPClass.SPClassConst.SPFieldName] == fname:
                    return tble[i]

        return null

    def GetMethodTable(self):
        if self.mtdtable == None:
            self.mtdtable = self.GetCMIInstanceData(CMIConst.CMIClassIndex).get(SPClass.SPClassConst.MethodTable, null)

        if self.mtdtable == null:
            raise RuntimeError("Current class missing method table")
        return self.mtdtable

    def GetMethod(self, mtd):
        mtdtbl = self.GetMethodTable()
        for i in range(len(mtdtbl)):
            if mtdtbl[i][SPClass.SPClassConst.SPMethodName] == mtd:
                return mtdtbl[i]

        mtdtbl = self.GetExtendedMethodTable()        
        if mtdtbl != None and mtdtbl != null:
            for i in range(len(mtdtbl)):
                if mtdtbl[i][SPClass.SPClassConst.SPMethodName] == mtd:
                    return mtdtbl[i]

        return null

    def GetExtendedMethodTable(self):
        if CMIConst.CMIExtendedMethodTable == False:
            return None
        
        if self.extendedmtdtable != None:
            return self.extendedmtdtable

        classidata = self.GetCMIInstanceData(CMIConst.CMIClassIndex)
        self.extendedmtdtable = classidata.get(SPClass.SPClassConst.ExtendedMethodTable, null)
        return self.extendedmtdtable

    def GetLintab(self):
        if self.lintab != None:
            return self.lintab

        self.lintab = self.GetCMIInstanceData(CMIConst.CMIClassLinearizationIndex).get(SPClassLinearization.CMIClassLinearizationConst.Lintabl, null)
        return self.lintab

    def GetBaseclasslist(self):
        if self.baseclasslist != None:
            return self.baseclasslist

        classidata = self.GetCMIInstanceData(CMIConst.CMIClassIndex)
        self.baseclasslist = classidata.get(SPClass.SPClassConst.BaseClassList, null)
        return self.baseclasslist


        
# DoMethod Now have the 
# callinfo, current class for the ancestor instance data of the object,
# object, method table entry, arguments.

# Now need to do the actual method dispatch

# 1: If the method is not built-in, and not compiled, does the exec compile. – first does the base64 decode to load it.  If we are caching, looks up if there is a compiled cached version.

# 2: If not a built-in, loads the method with an exec (need to review this) – to avoid a global conflict, such as a built-in or something like that, first checks if the object exists.
# Renames it if it does.  Loads the method, postpend the method with the CMI object ID for the class.

# 3: Creates the class environment – which is then cached.  The sysmodules and imports are separated out. During the class environment load

# 4: Creates the SagaPythonSelf object with the object ID info, instance data index, etc.
# Passes in the method name – Not sure if we need that 

# 5: Pushes the self object to the CMI as handle, enabling future stack tracing

# 6: Calls the method as function, with the self object.  Uses the class method signature with the args

# 7: On return from method, have a retvalue assigned – this is in the globals.

# 8: End exec here

# 9: DoMethod reads retvalue since it was an existing global

# 10: returns retvalue to the dispatch call – JSON encode here

# self is the currentclassentry here
# headclassobjentry is the class of the objentry
# objentry is the instance object

    def DoMethod(self, callinfo, headclassobjentry, objentry, mtdentry, args):

        mtd = mtdentry[SPClass.SPClassConst.SPMethodName]
        mcompiled = null
        mfuncobj = null 
        mcacheentry = self.mtdcache.get(mtd, null)
        if mcacheentry != null:
            mcompiled = mcacheentry[0]
            mfuncobj = mcacheentry[1]

        if mfuncobj == null:
            # if a built-in, just assign here, don't compile
            mtdflags = mtdentry.get(SPClass.SPClassConst.SPMethodFlags, null)
            if mtdflags != null and mtdflags.get(SPClass.SPClassConst.SPMethodBuiltin, null) != null:
                mfuncname = mtdentry.get(SPClass.SPClassConst.SPMethodSourceName, null)
                if mfuncname == null:
                    raise RuntimeError("Internal Class Error: Can't find builtin method name")
                mparts = mfuncname.partition('.')
                mfuncmod = sys.modules.get(mparts[0], null)
                if mfuncmod == null:
                    raise RuntimeError("Internal Class Error: Can't find builtin module for: ", mfuncname)
                mfuncobj = mfuncmod.__dict__.get(mparts[2])
                if mfuncobj == null:
                    raise RuntimeError("Internal Error: builtin method missing: ", mfuncname)
            else:
                # compile and build source 
                srcbase64 = mtdentry.get(SPClass.SPClassConst.SPMethodSource, null)    #in base64 as encoded as a string in the JSON object returned as a dict
                if srcbase64 == null:
                    raise RuntimeError("Class error: No source")

                src = base64.b64decode(srcbase64)
                cflags = mtdentry.get(SPClass.SPClassConst.SPCompileFlags, 0)
                cdi = mtdentry.get(SPClass.SPClassConst.SPDontInherit, False)

                try:
                    mcompiled = compile(src, '<sagachain class>', 'exec', flags = cflags, dont_inherit = cdi, optimize = 2)
                except SyntaxError as exc:
                    raise RuntimeError("Method source code invalid: ", mtd)
                except ValueError as exc:
                    raise RuntimeError("Method source is null: ", mtd)
                
                # now load the method
                glbs = globals().copy()
                lcls = dict()
                try:
                    exec(mcompiled, glbs, lcls)
                except:
                    raise RuntimeError("Compiled method failed to load: ", mtd)

                # the function should now have the method name
                mfuncobj = lcls.get(mtd, null)
                if mfuncobj == null:
                    raise RuntimeError("Compiled method incorrect name: ", mtd)

                del glbs
                del lcls

            self.mtdcache[mtd] = [mcompiled, mfuncobj]

        # need to load environment here
        # imports from other classes, and sysmodules
        #
        #  newglobals = self.GetGlobalsEnvironment()
        newglobals = globals().copy()

        # set the method name, the new SagaPythonSelf object, the arguments
        # and the return object as names in the newglobals.
        # the execscript expects these value,

        # create a new SagaPythonSelf object for the method 
        # push onto CMI call context list
        # prepend to argument list
        newself = sagapythonself.SagaPythonSelf(objentry.oid, self.oid, headclassobjentry.oid)
        selfhandle = len(CMIData.SagaPythonObjectList)
        CMIData.SagaPythonObjectList.append(newself)
        #give handle to CMI for tracking
        CMI.pushcontext(selfhandle, CMI.GetLanguageRuntime())

        newglobals[CMIClassTableEntryConst.SPExecSelf] = newself
        newglobals[CMIClassTableEntryConst.SPExecArgs] = args
        newglobals[CMIClassTableEntryConst.SPExecReturn] = None
        newglobals[CMIClassTableEntryConst.SPExecError] = None
        # add the function object with the prepend name
        newglobals[CMIClassTableEntryConst.SPExecMethod] = mfuncobj

        # cmiclass instance should have the sys.modules clean global 
        # added with the CMI class specific import modules.
        sysmodules = self.GetModulesEnvironment()

        locals = dict()
        sysmodulessave = sys.modules.copy()
        sys.modules |= sysmodules
        try:
            exec(self.GetExecScript(), newglobals, locals)
        except BaseException as bexc:
            errval = locals.get(CMIClassTableEntryConst.SPExecError, null)
            errstr = ""
            if errval != null:
                errstr = errval
            raise RuntimeError("Failed execution of method: ", mtd, "base exception: ", errstr) from bexc

        pophandle, poprt = CMI.popcontext()
        if pophandle != selfhandle:
            raise RuntimeError("Internal code error: selfhandle should be top of stack with CMI")

        CMIData.SagaPythonObjectList.pop()

        # newglobals now has the return value in it, Must be a list.
        retval = locals.get(CMIClassTableEntryConst.SPExecReturn, null)

        if retval == null:
            retval = None
        newself = None      # try to give hint to GC that the self object is no longer needed            

        sys.modules = sysmodulessave

        # need to check the return value against method return signature
        # for moment, at least verify the retval is a dict or subclass
        #if isinstance(retval, list) != True:
         #   RuntimeError("Invalid Method return value. Must be a Dict or subclass: ", mtd)

        return retval




    # the sys modules for a class include the imports
    # the import modules should be compiled and cached just
    # like the function objects
    # the sys modules and globals should be cached for the
    # length fo the transaction execution
    def GetModulesEnvironment(self):
        return self.sysmodules

    def GetGlobalsEnvironment(self):
        return self.globals


    # script for executing a CMI function as a pseudo method of SagaPythonSelf
    # execsriptsrc uses statically defined names for the arguments to be passed in,
    # the return arguments, the name of the function to call as a method,
    # and the name of the SagaPythonSelf object
    # these are set as globals before the exec call.
    execscriptsrc = """try:
    SPExec_Return = SPExec_Method(SPExec_Self, *SPExec_Args)
except BaseException as bexc:
    SPExec_Error = str(bexc)
    raise

"""

    def CompileExecScript(self):
        return compile(ClassTableEntry.execscriptsrc, CMIClassTableEntryConst.SPExecMethod, 'exec', optimize = 2)

    def GetExecScript(self):
        if ClassTableEntry.execscript[0] == None:
            ClassTableEntry.execscript[0] = self.CompileExecScript()
        return ClassTableEntry.execscript[0]


    # DoField does the read/write for the Field values -- 
    # Must get the instance data for the object, then get the
    # Field instance dictionary.  Then get the field in the field instance dictionary
    # for the specific class's instance data
    # if a write, need to put it back in the dictionary, but not written to the 
    # CMI yet.  To read the instance data must do the GetInstanceData first
    def DoField(self, callinfo, currclassobjentry, headclassobjentry, classindex, objentry, readwriteflag, fieldentry, arg):

        idata = objentry.GetCMIInstanceData(classindex)
        field = idata.get(fieldentry[SPClass.SPClassConst.SPFieldName], null)

        # read is true, return None if field doesn't exist
        if readwriteflag == True:
            if field == null:
                return None, False
            return field, True
        else:
            # write the arg here - should check arg type against fieldentry
            # would return wrong field type - normally caught by the stub
            # would use field entry here

            idata[fieldentry[SPClass.SPClassConst.SPFieldName]] = arg
            objentry.modified = True
            return None, True


   





         







        
