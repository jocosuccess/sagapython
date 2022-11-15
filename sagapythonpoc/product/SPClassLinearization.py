# SPClassLinearization
#
# Fields - linearization table
# Methods - get linearization table
# The Field is writeonce
#
# 
from dataclasses import dataclass
from sagapythonglobals import *
from CMILOID import *
import sagapythonself 

@dataclass(frozen=True)
class cMIClassLinearizationConst:
    Lintabl = 'ltbl'
    CMIGetMROClass = "CMIGetMROClass"
    CMIGetLinearization = "GetLinearization"
CMIClassLinearizationConst = cMIClassLinearizationConst()

# The linearization table is a list of LOIDs
# The self object here is a metaclass
def GetLinearization(self, headoid, baseclasslist):
    classdict = 0
    classlist = 1
    retval = [{}, list()]
    for noid in baseclasslist:
        noidvar = sagapythonself.ClsObjVar(noid)
        retval = noidvar.__member(CMIClassLinearizationConst.CMIGetMROClass)(retval[classdict], retval[classlist])

    # Now create all the base classes temp objects starting at beginning of list
    classobj = dict()
    cname = 0
    bclist = list()
    for classentry in retval[classlist]:
        bclist.clear()
        tp = tuple()
        if len(classentry) > 1:
            for bc in classentry[1:]:
                bclist.append(classobj[bc])
            tp = tuple(bclist)
        newclass = type(cname.__str__(), tp, dict(oid=LOID(classentry[0])))
        classobj[classentry[0]] = newclass 
        cname += 1

    # Create the final target class with its base classes
    bclist.clear()
    for bc in baseclasslist:
        bclist.append(classobj[bc.OIDbytes()])
    tp = tuple(bclist)
    newclass = type(cname.__str__(), tp, dict(oid=LOID(headoid)))

    # read the MRO - should be a complete list with multiple inheritance
    mrotp = newclass.__mro__

    # translate to list with LOIDs
    mrolist = list()
    for nc in mrotp:
        if nc == object:
            break
        mrolist.append(nc.oid)

    mrolist.reverse()
    # return the new linearized list
    return mrolist

# GetMROClass does a recursive send for all of the class in the baseclass list of the 
# self object (i.e. a SagaPython class).  On return, it
# creates a list consisting of its own LOID (using sagapythonself.SagaPythonSelf.OIDbytes()), and
# the baseclass list of the self class. Then appends these (i.e. pushes) these on 
# to baseclasslist. Then adds its LOID to the classdict with a reference to the list entry
# If the self object is already in the classdict, then it has already been visited
# which means all its baseclasses have been visited, which means just return to stop the recursion.
def GetMROClass(self, cdict, bclist):

    selfbytes = sagapythonself.SagaPythonSelf.LOIDbytes(self)
    if cdict.get(selfbytes, null) != null:
        return [cdict, bclist]

    retval = [cdict, bclist]
    newentry = [selfbytes]

    # get baseclasslist from the self object's instance data
    cmiclassobjentry = sagapythonself.SagaPythonSelf.GetObjectEntry(sagapythonself.SagaPythonSelf.GetLOID(self))
    baseclasslist = cmiclassobjentry.GetBaseclasslist()
    classdict = 0
    classlist = 1

    if baseclasslist != [None] and baseclasslist != None:
        for noid in baseclasslist:
            nbytes = sagapythonself.SagaPythonSelf.LOIDbytes(noid)
            if nbytes in cdict:
                continue
            retval = sagapythonself.DispatchMethod(None, noid, CMIClassLinearizationConst.CMIGetMROClass, retval[classdict], retval[classlist])
            newentry.append(noid.OIDbytes())

    retval[classdict][selfbytes] = len(retval[classlist])
    retval[classlist].append(newentry)
    return retval
    

