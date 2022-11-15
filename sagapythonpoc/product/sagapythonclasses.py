# test retrieving transaction script from a temporary file
# The transaction application is sent the name of a file containing the transaction script
# at startup. Alternative is to read from stdin, and have the node application 
# write the transaction script byte by byte.  Since the transaction can't be executed until
# the entire script is transferred, reading from a file makes more sense.
#
# Added code to create CMI classes for testing
# Uses a new function wrapper -- def __CMIClasses()
# compiles and calls the function to execute the classes defined inside the function.
# The decorators capture the methods names and source.
# The field decorators capture the field names and types.  Will need to review how
# to capture signatures and verify them.  At moment, no signature verification is happening.

# from __future__ import annotations
import sys
import re 
import tempfile
from sagapythonglobals import *
import CMI
from CMILOID import *
from baseobjects import *
import ObjectDataBase

# method flags
# final = SPMethodFinal = 'f'    # (final)
# public = SPMethodPublic = 'pb'  # (public) 
# protected = SPMEthodProtected = 'pr' # (protected)
# private = SPMethodPrivate = 'pv'  # (private)
from dataclasses import dataclass
from sagapythonself import *


restart = '(^def|(.*\n+)+def)?[ ]+__'
reend = '[(][^)]*[)]:((.*\n+)+?[A-Za-z_$%&^*!@-]|(.*\n+)+?$)'

# returns script for passed in function name, if any
def readscript(script, funcname) -> Union[str, str]:

    # find beginning of function first
    funcstart = re.search(restart + funcname, script)
    
    if funcstart == None:
        return (funcstart, script)

    # need to backup to the "def" keyword
    # look backwards until hit a \n or beginning of script
    i = funcstart.end()-1
    for i in range(funcstart.end()-1, funcstart.start()-1, -1):
        if script[i] == '\n': break 
    
    defstart = funcstart.start()

    if i > 0:
        defstart = defstart + i

    # now search for complete function    
    fnc = re.search(restart + funcname + reend, script[defstart:])
    if fnc == None:
        return (fnc, script)
    

    #clean up last character - left over, might fix later
    out = fnc.group(0)
    ln = len(out)
    outscript = '\n'
    if defstart > 0:
        outscript = script[:defstart-1] + '\n'
    if fnc.end() + defstart < len(script):
        outscript = outscript + script[fnc.end()+defstart-1:]

    return(out[:ln-1] + "\n", outscript)
    
def main() -> int:

    classes = None
    hdr = None
    body = None
    tail = None
    err = None

    if len(sys.argv) < 6 :
        err = "not enough parameters"
        sys.stderr(err)
        return -1

    # argv[6] is the name of the database if present.  Default is sagapython.db
    dbname = 'sagapython.db'
    if len(sys.argv) == 7:
        dbname = sys.argv[6]

    if ObjectDataBase.opendb(dbname) != True:
        raise RuntimeError("unable to open leveldb database")

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

    with open(sys.argv[1]) as f:
        script = f.read()

    # newline terminate, in case it isn't there
    script = script + "\n"

    # read in each part
    hdr, script = readscript(script, "hdr")
    if hdr == None:
        # no header - set error here
        raise Exception("No hdr")
    tmpf = tempfile.NamedTemporaryFile(delete=False)
    tmpf.write(hdr.encode())
    hdrscript = tmpf.name
    tmpf.close()        # on close, should not cause a delete
    

    classes, script = readscript(script, "CMIClasses")
    # if classes == None:
        # classes are optional no error
    if classes != None:
        tmpf = tempfile.NamedTemporaryFile(delete=False)
        tmpf.write(classes.encode())
        classesscript = tmpf.name
        tmpf.close()        # on close, should not cause a delete

    body, script = readscript(script, "body")
    if body == None:
        raise Exception("No body")
    tmpf = tempfile.NamedTemporaryFile(delete=False)
    tmpf.write(body.encode())
    bodyscript = tmpf.name
    tmpf.close()        # on close, should not cause a delete

    tail, script = readscript(script, "tail")
    if tail == None:
        raise Exception("No tail")
    tmpf = tempfile.NamedTemporaryFile(delete=False)
    tmpf.write(tail.encode())
    tailscript = tmpf.name
    tmpf.close()        # on close, should not cause a delete

    if err != None:
        # need to set sys.stderr here
        sys.stderr(err)
        return -1

    # compile each script
    try:
        hdrobj = compile(hdr, hdrscript, 'exec')
    except Exception as err: 
        err = err + "hdrscript failed to compile"
        raise

    if classes != None:
        try:
            classobj = compile(classes, classesscript, 'exec')
        except Exception as err:
            err = err + "classesscript failed to compile"
            raise

    try:
        bodyobj = compile(body, bodyscript, 'exec')
    except Exception as err: 
        err = err + "bodyscript failed to compile"
        raise

    try:
        tailobj = compile(tail, tailscript, 'exec')
    except Exception as err: 
        err = err + "hdrscript failed to compile"
        raise 

    if err != None:
        # set sys.stderr here
        sys.stderr(err)
        return -1

    # read in and compile the decorators, ClsObjVar definition, and anything else, here

    # make a copy of globals, and remove various names here
    # removal tbd
    sagaglobals = globals().copy()

    # load sagapython hdrwrapper objects here
    if sys.argv[2] == None:
        err = "Need Sagapython hdrwrapper script as 2nd parameter"
        sys.stderr(err)
        return -1

    with open(sys.argv[2]) as sf:
        sagascript = sf.read() 

    if sagascript == None:
        sys.stderr("failed to read in Saga hdr environment")
        return -1

    sagaobjs = compile(sagascript, sys.argv[2], 'exec')

    if sagaobjs == None:
        sys.stderr("Failed to compile Saga hdr environment")
        return -1

    hdrglobals = sagaglobals.copy()

    try:
        exec(sagaobjs, hdrglobals)
    except Exception as err:
        err = err + "saga hdr functions load failed"
        sys.stderr(err)
        return -1

    # now have the hdr wrapper function in hdrglobals 
    # need to load the hdr function - 
    try:
        exec(hdrobj, hdrglobals)
    except Exception:
        sys.stderr("Failed to load __hdr() function")
        return -1

    # call the hdr wrapper function
    hdrinfo = eval("hdrwrapper()", hdrglobals)

    if hdrinfo == None:
        sys.stderr("Failed to run hdr function")
        return -1

    # load sagapython tailwrapper objects here
    if sys.argv[5] == None:
        err = "Need Sagapython tailwrapper script as 4th parameter"
        sys.stderr(err)
        return -1

    with open(sys.argv[5]) as sf:
        sagascript = sf.read() 

    if sagascript == None:
        sys.stderr("failed to read in Sagapython tailwrapper environment")
        return -1

    sagaobjs = compile(sagascript, sys.argv[5], 'exec')

    if sagaobjs == None:
        sys.stderr("Failed to compile Sagapython tailwrapper environment")
        return -1

    tailglobals = sagaglobals.copy()
    tailglobals['rvalue'] = 1
    tailglobals['svalue'] = 2

    try:
        exec(sagaobjs, tailglobals)
    except:
        err = "Sagapython tailwrapper functions load failed"
        sys.stderr(err)
        return -1

    # now have the tailwrapper function in tailglobals 
    # need to load the tail function - 
    try:
        exec(tailobj, tailglobals)
    except:
        sys.stderr("Failed to load __tail() function")
        return -1

    # call the tail wrapper function
    tailinfo = eval("tailwrapper()", tailglobals)

    if tailinfo == None:
        sys.stderr("Failed to run tail function")
        return -1


    if classes != None:
        # ***************** cmi decorator
        # load sagapython body objects here
        if sys.argv[3] == None:
            err = "Need Sagapython decorator script as 3rd parameter"
            sys.stderr(err)
            return -1

        with open(sys.argv[3]) as sf:
            sagascript = sf.read() 

        if sagascript == None:
            sys.stderr("failed to read in Sagapython decorator environment")
            return -1

        sagaobjs = compile(sagascript, sys.argv[3], 'exec')

        if sagaobjs == None:
            sys.stderr("Failed to compile Sagapython decorator environment")
            return -1

        cmiclassesglobals = sagaglobals.copy()

        lcls = dict()

        try:
            exec(sagaobjs, cmiclassesglobals)
        except:
            err = "SagaPython decorator functions load failed"
            sys.stderr(err)
            return -1

        # now have the decorator wrapper function in cmiclassesglobals 
        # need to load the decorator function - 
        try:
            exec(classobj, cmiclassesglobals, lcls)
        except:
            sys.stderr("Failed to load __CMIClasses() function")
            return -1

        # call the body wrapper function
        cmiclassesglobals['__CMIClasses'] = lcls['__CMIClasses']        
        classesinfo = eval("cmiclasseswrapper()", cmiclassesglobals, lcls)

        # *********************************end cmidecorator 

    # load sagapython body objects here
    if sys.argv[4] == None:
        err = "Need Sagapython bodywrapper script as 3rd parameter"
        sys.stderr(err)
        return -1

    with open(sys.argv[4]) as sf:
        sagascript = sf.read() 

    if sagascript == None:
        sys.stderr("failed to read in Sagapython bodywrapper environment")
        return -1

    sagaobjs = compile(sagascript, sys.argv[4], 'exec')

    if sagaobjs == None:
        sys.stderr("Failed to compile Sagapython bodywrapper environment")
        return -1

    bodyglobals = sagaglobals.copy()

    if classes != None:
        for loidentry in classesinfo:
            clname = loidentry[0].rpartition('.')
            bodyglobals[clname[2]] = loidentry[1]

    try:
        exec(sagaobjs, bodyglobals)
    except:
        err = "SagaPython bodywrapper functions load failed"
        sys.stderr(err)
        return -1

    # now have the body wrapper function in bodyglobals 
    # need to load the body function - 
    try:
        exec(bodyobj, bodyglobals)
    except Exception:
        sys.stderr("Failed to load __body() function")
        return -1

    # call the body wrapper function
    bodyinfo = eval("bodywrapper()", bodyglobals)

    if bodyinfo == None:
        sys.stderr("Failed to run body function")
        return -1

    fl = open(hdrscript)
    del fl
    fl = open(classesscript)
    del fl
    fl = open(bodyscript)
    del fl
    fl = open(tailscript)
    del fl

    # write objects out
    WriteObjects()

def Log(*args):
    # do nothing yet
    return

if __name__ == '__main__': 
    sys.exit(main())