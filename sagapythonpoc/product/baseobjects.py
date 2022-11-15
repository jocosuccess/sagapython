# baseobjects.py
#
# The base objects to enable SagaPython for CMI
# all of these have unique OIDs - on startup, check if they are in the database
# if not, add them. In reality this only happens once, but easier to just leave the code in.
# Alternative would be to have a special app that does this initial load.
# SPClassObject
# SPClass
# SPClassLinearization
# SPClassRuntime
# SPClassMetaClass
# SPClassMetaMetaClass
#
# 
# all classes have instance data for the object, linearization and runtime
# Thus technically they all are instances of a class that inherits from these classes.
# 
# The CMI expects the class of the target to specify the language runtime.
# Walking for the object to the class following the type is how the
# CMI determines the runtime to send the message to.  The dispatch listener
# then does the DoMethod - which is part of the objentry, which creates a new Self object
#
import base64
import pickle
from sagapythonglobals import *
from CMI import *
from CMILOID import *
from CMIObjectData import *
import SPClassObject 
import SPClass
import SPClassLinearization 
import SPClassRuntime 
import SPMetaClass
import SPMetaMetaClass
import SPClassAccount

# JSON encode and base64 encode the CMI instance data
# Python pickle and base64 encode the python instance data
# then write to the database
def BuiltinWriteObject(loid: LOID, idata):
    writedata = [None]*len(idata)
    for i in range(len(idata)):
        objentry = [None] * 2
        cmidata = CMIJSONEncoder.encode(idata[i][CMIConst.CMIFieldIndex])
        objentry[CMIConst.CMIFieldIndex] = base64.b64encode(cmidata.encode()).decode()
        if idata[i][CMIConst.PythonObjectsIndex] != None:
            pydata = pickle.dumps(idata[i][CMIConst.PythonObjectsIndex])
            objentry[CMIConst.PythonObjectsIndex] = base64.b64encode(pydata).decode()
        else:
            objentry[CMIConst.PythonObjectsIndex] = None
        writedata[i] = objentry

    newobjhandle = CMI.CreateObject(loid)
    CMI.WriteObject(newobjhandle, writedata)

def CreateTheClassObject():

    if CMI.IsObject(CMIConst.CMIClassObject) == True:
        return

    idata = [None]*5

    objectinstancedata = {CMIConst.CMIType: CMIConst.SPMetaClass, CMIConst.CMIOwner: CMIConst.SPSystemAccount}
    linearizationinstancedata = {SPClassLinearization.CMIClassLinearizationConst.Lintabl: [CMIConst.CMIClassObject]}
    runtimeinstancedata = {SPClassRuntime.CMIClassRuntimeConst.URL: CMIConst.CMIRuntimeURL}

    # Fields Table
    typefld = {
        SPClass.SPClassConst.SPFieldName: SPClassObject.CMIConst.CMIType,
        SPClass.SPClassConst.SPFieldReadFlags: True,
        SPClass.SPClassConst.SPFieldWriteOnceFlags: True,
        SPClass.SPClassConst.SPFieldFinalFlag: True,
        SPClass.SPClassConst.SPFieldType: None  # JSON Schema 
    }

    ownerfld = {
        SPClass.SPClassConst.SPFieldName: SPClassObject.CMIConst.CMIOwner,
        SPClass.SPClassConst.SPFieldReadFlags: True,
        SPClass.SPClassConst.SPFieldWriteOnceFlags: True,
        SPClass.SPClassConst.SPFieldFinalFlag: True,
        SPClass.SPClassConst.SPFieldType: None  # JSON Schema 
    }

    ft = [
        typefld,
        ownerfld
    ]


    # Methods Table
    NewObjectmethod = {
        SPClass.SPClassConst.SPMethodName: 'NewObject', 
        SPClass.SPClassConst.SPMethodFlags:
            {
                SPClass.SPClassConst.SPMethodBuiltin: True,
                SPClass.SPClassConst.SPMethodPublic: True,
            },
        SPClass.SPClassConst.SPMethodSourceName: 'SPClassObject.NewObject',
        SPClass.SPClassConst.SPArgTypes: None,
        SPClass.SPClassConst.SPReturnTypes: None
    }

    mt = [
        NewObjectmethod
    ]

    classinstancedata = {
        SPClass.SPClassConst.BaseClassList: [None],
        SPClass.SPClassConst.FieldTable: ft,
        SPClass.SPClassConst.MethodTable: mt
    }

    metaclassinstancedata = {}

    idata[0] = [objectinstancedata, None]
    idata[1] = [linearizationinstancedata, None]
    idata[2] = [runtimeinstancedata, None]
    idata[3] = [classinstancedata, None]
    idata[4] = [metaclassinstancedata, None]

    BuiltinWriteObject(CMIConst.CMIClassObject, idata)

def CreateTheClass():
    if CMI.IsObject(CMIConst.SPClass) == True:
        return

    idata = [None]*5

    lintab = [
            CMIConst.CMIClassObject,
            CMIConst.CMIClassLinearization, 
            CMIConst.CMIClassRuntime, 
            CMIConst.SPClass
        ]

    objectinstancedata = {CMIConst.CMIType: CMIConst.SPMetaClass, CMIConst.CMIOwner: CMIConst.SPSystemAccount}
    linearizationinstancedata = {SPClassLinearization.CMIClassLinearizationConst.Lintabl: lintab}
    runtimeinstancedata = {SPClassRuntime.CMIClassRuntimeConst.URL: CMIConst.CMIRuntimeURL}

    # Field Table - Field Table Entries
    # Method table field
    mtfld = {
        SPClass.SPClassConst.SPFieldName: SPClass.SPClassConst.MethodTable,
        SPClass.SPClassConst.SPFieldReadFlags: True,
        SPClass.SPClassConst.SPFieldWriteOnceFlags: True,
        SPClass.SPClassConst.SPFieldFinalFlag: True,
        SPClass.SPClassConst.SPFieldType: None  # JSON Schema for a method table of method entries
    }

    # Field Table field
    ftfld = {
        SPClass.SPClassConst.SPFieldName: SPClass.SPClassConst.FieldTable,
        SPClass.SPClassConst.SPFieldReadFlags: True,
        SPClass.SPClassConst.SPFieldWriteOnceFlags: True,
        SPClass.SPClassConst.SPFieldFinalFlag: True,
        SPClass.SPClassConst.SPFieldType: None  # JSON Schema 

    }

    exmtfld = {
        SPClass.SPClassConst.SPFieldName: SPClass.SPClassConst.ExtendedMethodTable,
        SPClass.SPClassConst.SPFieldReadFlags: True,
        SPClass.SPClassConst.SPFieldWriteOnceFlags: True,
        SPClass.SPClassConst.SPFieldFinalFlag: True,
        SPClass.SPClassConst.SPFieldType: None  # JSON Schema 

    }

    exftfld = {
        SPClass.SPClassConst.SPFieldName: SPClass.SPClassConst.ExtendedFieldTable,
        SPClass.SPClassConst.SPFieldReadFlags: True,
        SPClass.SPClassConst.SPFieldWriteOnceFlags: True,
        SPClass.SPClassConst.SPFieldFinalFlag: True,
        SPClass.SPClassConst.SPFieldType: None  # JSON Schema 

    }

    bclfld = {
        SPClass.SPClassConst.SPFieldName: SPClass.SPClassConst.BaseClassList,
        SPClass.SPClassConst.SPFieldReadFlags: True,
        SPClass.SPClassConst.SPFieldWriteOnceFlags: True,
        SPClass.SPClassConst.SPFieldFinalFlag: True,
        SPClass.SPClassConst.SPFieldType: None  # JSON Schema 

    }

    cfffld = {
        SPClass.SPClassConst.SPFieldName: SPClass.SPClassConst.ClassFinalFlag,
        SPClass.SPClassConst.SPFieldReadFlags: True,
        SPClass.SPClassConst.SPFieldWriteOnceFlags: True,
        SPClass.SPClassConst.SPFieldFinalFlag: True,
        SPClass.SPClassConst.SPFieldType: None  # JSON Schema 

    }

    impfld = {
        SPClass.SPClassConst.SPFieldName: SPClass.SPClassConst.ImportObjectsList,
        SPClass.SPClassConst.SPFieldReadFlags: True,
        SPClass.SPClassConst.SPFieldWriteOnceFlags: True,
        SPClass.SPClassConst.SPFieldFinalFlag: True,
        SPClass.SPClassConst.SPFieldType: None  # JSON Schema 

    }

    pyfld = {
        SPClass.SPClassConst.SPFieldName: SPClass.SPClassConst.Pyobjects,
        SPClass.SPClassConst.SPFieldReadFlags: True,
        SPClass.SPClassConst.SPFieldWriteOnceFlags: True,
        SPClass.SPClassConst.SPFieldFinalFlag: True,
        SPClass.SPClassConst.SPFieldType: None  # JSON Schema 
    }

    ft = [
        mtfld,
        ftfld,
        exmtfld,
        exftfld,
        bclfld,
        cfffld,
        impfld,
        pyfld
    ]


    # Methods Table
    # SPClass has no methods. 
    mt = []

    classinstancedata = {
        SPClass.SPClassConst.BaseClassList: [CMIConst.CMIClassRuntime],
        SPClass.SPClassConst.FieldTable: ft,
        SPClass.SPClassConst.MethodTable: mt
    }

    metaclassinstancedata = {}

    idata[0] = [objectinstancedata, None]
    idata[1] = [linearizationinstancedata, None]
    idata[2] = [runtimeinstancedata, None]
    idata[3] = [classinstancedata, None]
    idata[4] = [metaclassinstancedata, None]

    BuiltinWriteObject(CMIConst.SPClass, idata)

def CreateTheClassLinearization():
    if CMI.IsObject(CMIConst.CMIClassLinearization) == True:
        return

    idata = [None]*5

    objectinstancedata = {CMIConst.CMIType: CMIConst.SPMetaClass, CMIConst.CMIOwner: CMIConst.SPSystemAccount}
    lintab = [CMIConst.CMIClassObject, CMIConst.CMIClassLinearization]
    linearizationinstancedata = {SPClassLinearization.CMIClassLinearizationConst.Lintabl: lintab}
    runtimeinstancedata = {SPClassRuntime.CMIClassRuntimeConst.URL: CMIConst.CMIRuntimeURL}

    lintabfld = {
        SPClass.SPClassConst.SPFieldName: SPClassLinearization.CMIClassLinearizationConst.Lintabl,
        SPClass.SPClassConst.SPFieldReadFlags: True,
        SPClass.SPClassConst.SPFieldWriteOnceFlags: True,
        SPClass.SPClassConst.SPFieldFinalFlag: True,
        SPClass.SPClassConst.SPFieldType: None  # JSON Schema 
    }

    # Fields Table
    ft = [
        lintabfld
    ]

    # methods
    GetMROmethod = {
        SPClass.SPClassConst.SPMethodName: SPClassLinearization.CMIClassLinearizationConst.CMIGetMROClass, 
        SPClass.SPClassConst.SPMethodFlags:
                        {
                            SPClass.SPClassConst.SPMethodBuiltin: True,
                            SPClass.SPClassConst.SPMethodPublic: True,
                        },
                    SPClass.SPClassConst.SPMethodSourceName: 'SPClassLinearization.GetMROClass',
                    SPClass.SPClassConst.SPArgTypes: None
    }

    Getlinearization = {
        SPClass.SPClassConst.SPMethodName: SPClassLinearization.CMIClassLinearizationConst.CMIGetLinearization, 
        SPClass.SPClassConst.SPMethodFlags:
                        {
                            SPClass.SPClassConst.SPMethodBuiltin: True,
                            SPClass.SPClassConst.SPMethodPublic: True,
                        },
                    SPClass.SPClassConst.SPMethodSourceName: 'SPClassLinearization.GetLinearization',
                    SPClass.SPClassConst.SPArgTypes: None
    }

    # Methods Table
    mt = [
        GetMROmethod,
        Getlinearization
    ]

    classinstancedata = {
        SPClass.SPClassConst.BaseClassList: [CMIConst.CMIClassObject],
        SPClass.SPClassConst.FieldTable: ft,
        SPClass.SPClassConst.MethodTable: mt,
    }

    metaclassinstancedata = {

    }

    idata[0] = [objectinstancedata, None]
    idata[1] = [linearizationinstancedata, None]
    idata[2] = [runtimeinstancedata, None]
    idata[3] = [classinstancedata, None]
    idata[4] = [metaclassinstancedata, None]

    BuiltinWriteObject(CMIConst.CMIClassLinearization, idata)

def CreateTheClassRuntime():
    if CMI.IsObject(CMIConst.CMIClassRuntime) == True:
        return

    idata = [None]*5

    objectinstancedata = {CMIConst.CMIType: CMIConst.SPMetaClass, CMIConst.CMIOwner: CMIConst.SPSystemAccount}

    lintab = [
            CMIConst.CMIClassObject,
            CMIConst.CMIClassLinearization, 
            CMIConst.CMIClassRuntime, 
        ]
    linearizationinstancedata = {SPClassLinearization.CMIClassLinearizationConst.Lintabl: lintab}    
    runtimeinstancedata = {SPClassRuntime.CMIClassRuntimeConst.URL: CMIConst.CMIRuntimeURL}

    runtimefld = {
        SPClass.SPClassConst.SPFieldName: SPClassRuntime.CMIClassRuntimeConst.URL,
        SPClass.SPClassConst.SPFieldReadFlags: True,
        SPClass.SPClassConst.SPFieldWriteOnceFlags: True,
        SPClass.SPClassConst.SPFieldFinalFlag: True,
        SPClass.SPClassConst.SPFieldType: None  # JSON Schema 
    }

    # Fields Table
    ft = [
        runtimefld
    ]


    # Methods Table
    mt = []

    classinstancedata = {
        SPClass.SPClassConst.BaseClassList: [CMIConst.CMIClassLinearization],
        SPClass.SPClassConst.FieldTable: ft,
        SPClass.SPClassConst.MethodTable: mt
    }

    metaclassinstancedata = {

    }
    idata[0] = [objectinstancedata, None]
    idata[1] = [linearizationinstancedata, None]
    idata[2] = [runtimeinstancedata, None]
    idata[3] = [classinstancedata, None]
    idata[4] = [metaclassinstancedata, None]

    BuiltinWriteObject(CMIConst.CMIClassRuntime, idata)

def CreateTheMetaClass():
    if CMI.IsObject(CMIConst.SPMetaClass) == True:
        return

    idata = [None]*6

    objectinstancedata = {CMIConst.CMIType: CMIConst.SPMetaMetaClass, CMIConst.CMIOwner: CMIConst.SPSystemAccount}
    lintab = [ 
        CMIConst.CMIClassObject,
        CMIConst.CMIClassLinearization,
        CMIConst.CMIClassRuntime, 
        CMIConst.SPClass,
        CMIConst.SPMetaClass, 
        ]
    linearizationinstancedata = {SPClassLinearization.CMIClassLinearizationConst.Lintabl: lintab}    
    runtimeinstancedata = {SPClassRuntime.CMIClassRuntimeConst.URL: CMIConst.CMIRuntimeURL}

    # Fields Table
    ft = []


    # Methods Table
    Newmethod = {
        SPClass.SPClassConst.SPMethodName: SPClass.SPClassConst.SPClassNew, 
        SPClass.SPClassConst.SPMethodFlags:
                        {
                            SPClass.SPClassConst.SPMethodBuiltin: True,
                            SPClass.SPClassConst.SPMethodPublic: True,
                        },
                    SPClass.SPClassConst.SPMethodSourceName: 'SPMetaClass.New',
                    SPClass.SPClassConst.SPArgTypes: None
    }

    Initmethod = {
        SPClass.SPClassConst.SPMethodName: SPClass.SPClassConst.SPClassInit, 
        SPClass.SPClassConst.SPMethodFlags:
                        {
                            SPClass.SPClassConst.SPMethodBuiltin: True,
                            SPClass.SPClassConst.SPMethodPublic: True,
                        },
                    SPClass.SPClassConst.SPMethodSourceName: 'SPMetaClass.NewInit',
                    SPClass.SPClassConst.SPArgTypes: None
    }

    mt = [
        Newmethod,
        Initmethod,
    ]

    classinstancedata = {
        SPClass.SPClassConst.BaseClassList: [CMIConst.SPClass],
        SPClass.SPClassConst.FieldTable: ft,
        SPClass.SPClassConst.MethodTable: mt,
        SPClass.SPClassConst.ExtendedMethodTable: None,
        SPClass.SPClassConst.ImportObjectsList: None
    }

    metaclassinstancedata = {

    }

    metametaclassinstancedata = {

    }

    idata[0] = [objectinstancedata, None]
    idata[1] = [linearizationinstancedata, None]
    idata[2] = [runtimeinstancedata, None]
    idata[3] = [classinstancedata, None]
    idata[4] = [metaclassinstancedata, None]
    idata[5] = [metametaclassinstancedata, None]

    BuiltinWriteObject(CMIConst.SPMetaClass, idata)

# The CMIMetaMetaClass does not have a type. It should never have a message sent directly to it as an object instance
# It is the class type for CMIMetaClass and contains the methods for creating classes
def CreateTheMetaMetaClass():
    if CMI.IsObject(CMIConst.SPMetaMetaClass) == True:
        return

    idata = [None]*5

    objectinstancedata = {CMIConst.CMIType: CMIConst.SPMetaClass, CMIConst.CMIOwner: CMIConst.SPSystemAccount}

    lintab = [ 
        CMIConst.CMIClassObject,
        CMIConst.CMIClassLinearization, 
        CMIConst.CMIClassRuntime, 
        CMIConst.SPClass, 
        CMIConst.SPMetaClass, 
        CMIConst.SPMetaMetaClass,
        ]
    linearizationinstancedata = {SPClassLinearization.CMIClassLinearizationConst.Lintabl: lintab}    
    runtimeinstancedata = {SPClassRuntime.CMIClassRuntimeConst.URL: CMIConst.CMIRuntimeURL}

    # Fields Table
    ft = []


    # Methods Table
    # Note - need to review schema concept late. arg types should be in JSON schema format
    NewInit = {
                    SPClass.SPClassConst.SPMethodName: SPClass.SPClassConst.SPClassInit, 
                    SPClass.SPClassConst.SPMethodFlags:
                        {
                            SPClass.SPClassConst.SPMethodBuiltin: True,
                            SPClass.SPClassConst.SPMethodPublic: True,
                        },
                    SPClass.SPClassConst.SPMethodSourceName: 'SPMetaMetaClass.NewInit',
                    SPClass.SPClassConst.SPArgTypes: None
    }

    NewMethod = {
                    SPClass.SPClassConst.SPMethodName: SPClass.SPClassConst.SPClassNew, 
                    SPClass.SPClassConst.SPMethodFlags:
                        {
                            SPClass.SPClassConst.SPMethodBuiltin: True,
                            SPClass.SPClassConst.SPMethodPublic: True,
                        },
                    SPClass.SPClassConst.SPMethodSourceName: 'SPMetaMetaClass.New',
                    SPClass.SPClassConst.SPArgTypes: None
    }

    mt = [
        NewMethod,
        NewInit
    ]

    classinstancedata = {
        SPClass.SPClassConst.BaseClassList: [CMIConst.SPMetaClass],
        SPClass.SPClassConst.FieldTable: ft,
        SPClass.SPClassConst.MethodTable: mt
    }

    metaclassinstancedata = {

    }

    idata[0] = [objectinstancedata, None]
    idata[1] = [linearizationinstancedata, None]
    idata[2] = [runtimeinstancedata, None]
    idata[3] = [classinstancedata, None]
    idata[4] = [metaclassinstancedata, None]

    BuiltinWriteObject(CMIConst.SPMetaMetaClass, idata)

def CreateTheClassAccount():

    if CMI.IsObject(CMIConst.SPClassAccount) == True:
        return

    idata = [None]*5

    objectinstancedata = {CMIConst.CMIType: CMIConst.SPMetaClass, CMIConst.CMIOwner: CMIConst.SPSystemAccount}
    linearizationinstancedata = {SPClassLinearization.CMIClassLinearizationConst.Lintabl: [CMIConst.CMIClassObject, CMIConst.SPClassAccount]}    # need to fix the inheritance later
    runtimeinstancedata = {SPClassRuntime.CMIClassRuntimeConst.URL: CMIConst.CMIRuntimeURL}

    # Fields Table
    incrfld = {
        SPClass.SPClassConst.SPFieldName: "LDincr",
        SPClass.SPClassConst.SPFieldReadFlags: True,
        SPClass.SPClassConst.SPFieldWriteOnceFlags: False,
        SPClass.SPClassConst.SPFieldFinalFlag: True,
        SPClass.SPClassConst.SPFieldType: None  # JSON Schema 
    }

    baseLDfld = {
        SPClass.SPClassConst.SPFieldName: "baseLD",
        SPClass.SPClassConst.SPFieldReadFlags: True,
        SPClass.SPClassConst.SPFieldWriteOnceFlags: True,
        SPClass.SPClassConst.SPFieldFinalFlag: True,
        SPClass.SPClassConst.SPFieldType: None  # JSON Schema 
    }

    ft = [
        incrfld,
        baseLDfld
    ]


    # Methods Table
    NewLOID = {
        SPClass.SPClassConst.SPMethodName: 'NewLOID', 
        SPClass.SPClassConst.SPMethodFlags:
            {
                SPClass.SPClassConst.SPMethodBuiltin: True,
                SPClass.SPClassConst.SPMethodPublic: True,
            },
        SPClass.SPClassConst.SPMethodSourceName: 'SPClassAccount.NewLOID',
        SPClass.SPClassConst.SPArgTypes: None,
        SPClass.SPClassConst.SPReturnTypes: None
    }

    mt = [
        NewLOID
    ]

    classinstancedata = {
        SPClass.SPClassConst.BaseClassList: [CMIConst.CMIClassObject],
        SPClass.SPClassConst.FieldTable: ft,
        SPClass.SPClassConst.MethodTable: mt
    }

    metaclassinstancedata = {}

    idata[0] = [objectinstancedata, None]
    idata[1] = [linearizationinstancedata, None]
    idata[2] = [runtimeinstancedata, None]
    idata[3] = [classinstancedata, None]
    idata[4] = [metaclassinstancedata, None]

    BuiltinWriteObject(CMIConst.SPClassAccount, idata)

def CreateTheSystemAccount():
    if CMI.IsObject(CMIConst.SPSystemAccount) == True:
        return

    idata = [None]*2

    objectinstancedata = {CMIConst.CMIType: CMIConst.SPClassAccount, CMIConst.CMIOwner: CMIConst.SPSystemAccount}
    systemaccountinstancedata = {'baseLD': CMIConst.BaseLOID, 'LDincr': 1 }
    idata[0] = [objectinstancedata, None]
    idata[1] = [systemaccountinstancedata, None]

    BuiltinWriteObject(CMIConst.SPSystemAccount, idata)

# for unit test
if __name__ == '__main__':
    CreateTheClassObject()
    CreateTheClass()
    CreateTheClassLinearization()
    CreateTheClassRuntime()
    CreateTheMetaClass()
    CreateTheMetaMetaClass()
    CreateTheClassAccount()
    CreateTheSystemAccount()
