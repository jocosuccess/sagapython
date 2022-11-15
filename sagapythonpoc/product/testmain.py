# testmain.py
#
# Evolving unit tests for SagaPython

import base64
import pickle
from sagapythonglobals import *
import CMI
from sagapythonself import *
from baseobjects import *
import SPClassObject
import SPClass
import SPClassLinearization
import SPClassRuntime
import SPMetaClass
import SPMetaMetaClass
import SPClassAccount

# for unit test
if __name__ == '__main__':
    
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

    # create a fake field read message to walk the dispatch code directly
    currobj = CMIConst.SPMetaClass    

    retvalue =  DispatchField(None, currobj, True, SPClassRuntime.CMIClassRuntimeConst.URL, None)

    print (retvalue)

    # DispatchField(None, currobj, False, SPClassRuntime.CMIClassRuntimeConst.URL, "GotIt")

    # creating a new object - to be the system account in the future
    owner = CMIConst.SPSystemAccount
    baselist = [CMIConst.CMIClassObject]
    fieldtable = [None]
    methodtable = [None]
    importlist = [None]
    classfinalflag = False
    pyobjects = {}
    args = [owner, baselist, fieldtable, methodtable, importlist, classfinalflag, pyobjects]
    retvalue =  DispatchMethod(None, currobj, SPClass.SPClassConst.SPClassNew, args)

    print(retvalue)
    
    # create a new account from SPClassAccount
    args = [owner, None]
    currobj = CMIConst.SPClassAccount
    retvalue = DispatchMethod(None, currobj, SPClass.SPClassConst.SPClassNew, args )

    print (retvalue)

    # create a new class with a source method to simulate reading from the database
    # method source is base64 encoded so that it is a string.

    funcode = """def testfunc(self, owner):
        print("got to the testfunc")
        return "got here"
        """

    funcode64 = base64.b64encode(funcode.encode()).decode()

    # Methods Table
    testfunc = {
        SPClass.SPClassConst.SPMethodName: 'testfunc', 
        SPClass.SPClassConst.SPMethodFlags:
            {
                SPClass.SPClassConst.SPMethodPublic: True,
            },
        SPClass.SPClassConst.SPMethodSourceName: 'testfunc',
        SPClass.SPClassConst.SPArgTypes: None,
        SPClass.SPClassConst.SPReturnTypes: None,
        SPClass.SPClassConst.SPMethodSource: funcode64
    }

    mt = [
        testfunc
    ]

    # python class local objects
    pyobjs = dict()
    pyobjpickle = pickle.dumps(pyobjs)
    pyobj64 = base64.b64encode(pyobjpickle).decode()

    owner = CMIConst.SPSystemAccount
    currobj = CMIConst.SPMetaClass
    baselist = [CMIConst.CMIClassObject]
    fieldtable = [None]
    methodtable = mt
    importlist = [None]
    classfinalflag = False
    pyobjects = pyobj64
    args = [owner, baselist, fieldtable, methodtable, importlist, classfinalflag, pyobjects]
    retvalue =  DispatchMethod(None, currobj, SPClass.SPClassConst.SPClassNew, args)

    print ("New class: ")
    print (retvalue[0])

    clsobjvar = ClsObjVar(retvalue[0])
    print ("From ClsObjVar object: ")
    print (ClsObjVar.GetLOID(clsobjvar))
    currobj = retvalue[0]

    # new object
    args = [owner]
    retvalue = DispatchMethod(None, currobj, SPClass.SPClassConst.SPClassNew, args)

    print ("New object: ")
    print (retvalue[0])

    # now send a message to it.
    objvar = ClsObjVar(retvalue[0])
    currobj = retvalue[0]
    retvalue = DispatchMethod(None, currobj, 'testfunc', [owner])
    

    