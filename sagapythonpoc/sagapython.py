# test retrieving transaction script from a temporary file
# The transaction application is sent the name of a file containing the transaction script
# at startup. Alternative is to read from stdin, and have the node application 
# write the transaction script byte by byte.  Since the transaction can't be executed until
# the entire script is transferred, reading from a file makes more sense.

import sys
import re 

restart = '(^def|(.*\n+)+def)?[ ]+__'
reend = '[(][^)]*[)]:((.*\n+)+?[A-Za-z_$%&^*!@-]|(.*\n+)+?$)'

# returns script for passed in function name, if any
def readscript(script, funcname):

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

    hdr = None
    body = None
    tail = None
    err = None

    if len(sys.argv) < 5 :
        err = "not enough parameters"
        sys.stderr(err)
        return -1

    with open(sys.argv[1]) as f:
        script = f.read()

    # newline terminate, in case it isn't there
    script = script + "\n"

    # read in each part
    hdr, script = readscript(script, "hdr")
    if hdr == None:
        # no header - set error here
        err = "No hdr"

    body, script = readscript(script, "body")
    if body == None:
        err = err + "No body"

    tail, script = readscript(script, "tail")
    if tail == None:
        err = err + "No tail"

    if err != None:
        # need to set sys.stderr here
        sys.stderr(err)
        return -1

    # compile each script
    try:
        hdrobj = compile(hdr, "hdrscript", 'exec')
    except Exception: 
        err = err + "hdrscript failed to compile"

    try:
        bodyobj = compile(body, "bodyscript", 'exec')
    except Exception: 
        err = err + "bodyscript failed to compile"

    try:
        tailobj = compile(tail, "tailscript", 'exec')
    except Exception: 
        err = err + "hdrscript failed to compile"

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
    except Exception:
        err = "saga hdr functions load failed"
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
    if sys.argv[4] == None:
        err = "Need Sagapython tailwrapper script as 4th parameter"
        sys.stderr(err)
        return -1

    with open(sys.argv[4]) as sf:
        sagascript = sf.read() 

    if sagascript == None:
        sys.stderr("failed to read in Sagapython tailwrapper environment")
        return -1

    sagaobjs = compile(sagascript, sys.argv[3], 'exec')

    if sagaobjs == None:
        sys.stderr("Failed to compile Sagapython tailwrapper environment")
        return -1

    tailglobals = sagaglobals.copy()

    try:
        exec(sagaobjs, tailglobals)
    except Exception:
        err = "Sagapython tailwrapper functions load failed"
        sys.stderr(err)
        return -1

    # now have the tailwrapper function in tailglobals 
    # need to load the tail function - 
    try:
        exec(tailobj, tailglobals)
    except Exception:
        sys.stderr("Failed to load __tail() function")
        return -1

    # call the hdr wrapper function
    tailinfo = eval("tailwrapper()", tailglobals)

    if tailinfo == None:
        sys.stderr("Failed to run tail function")
        return -1
        
    # load sagapython body objects here
    if sys.argv[3] == None:
        err = "Need Sagapython bodywrapper script as 3rd parameter"
        sys.stderr(err)
        return -1

    with open(sys.argv[3]) as sf:
        sagascript = sf.read() 

    if sagascript == None:
        sys.stderr("failed to read in Sagapython bodywrapper environment")
        return -1

    sagaobjs = compile(sagascript, sys.argv[3], 'exec')

    if sagaobjs == None:
        sys.stderr("Failed to compile Sagapython bodywrapper environment")
        return -1

    bodyglobals = sagaglobals.copy()

    try:
        exec(sagaobjs, bodyglobals)
    except Exception:
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

if __name__ == '__main__': 
    sys.exit(main())