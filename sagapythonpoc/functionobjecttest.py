
# Test to prove that a function can be compiled
# then loaded, and then stored and reused.
# This avoids needing to load it each time it is used.
# Therefore can be stored in a runtime method table for
# each class and called. Further, can be dynamically
# compiled and loaded.


funcstr = """def hello():
    print("this is hello and don't forget it")
    x = 10
    print(x)
"""

def main():

    # first compile the testcode
    try:
        funcobj = compile(funcstr, "spmethod", 'exec')
    except Exception: 
        err = err + "funcstr failed to compile"

    # now have compiled object.  This can be loaded multiple times if needed
    # but would overwrite each other. 

    # next make copy of globals pre-loading it
    globalscopy = globals().copy()
    globalscopy2 = globals().copy()
    globalscopy3 = globals().copy()

    # now do the load
    exec(funcobj, globalscopy)

    # should now have the "hello" function in the globalscopy and not in globals
    print("Globals:")
    print(globals())

    print("GlobalsCopy:")
    print(globalscopy)    

    # should now be able to call the hello function with an exec
    # first try executing in globals directly
    try:
        hello()
    except:
        print("failed to call hello in globals")

    # call with globalscopy
    eval("hello()", globalscopy)

    # now copy out the function object from globalscopy
    funcstore = globalscopy["hello"]
    if funcstore == None:
        raise RuntimeError("failed to find hello")
    else:
        print(funcstore)

    # remove from globalscopy
    del globalscopy["hello"]
    print("calling hello after removing from globalscopy, should fail")
    try:
        eval("hello()", globalscopy)
    except:
        print("failed to call hello - good")

    print("finished hello call without being present")

    # try calling hello() in the second globals copy before adding the function object
    print("trying hello without adding to globalscopy2 dict")
    try:
        eval("hello()", globalscopy2)
    except:
        print("failed good")

    # add function object to globalscopy2
    globalscopy2["hello"] = funcstore
    print("trying hello with adding to globalscopy2 dict")
    try:
        eval("hello()", globalscopy2)
    except:
        print("failed bad")

    # now give it a different name 
    globalscopy3["goodbye"] = funcstore
    print("trying hello as goodbye()")
    try:
        exec("goodbye()", globalscopy3)
    except:
        print("failed to call goodbye - bad")
        
    print("done")
    
if __name__ == '__main__': 
    sys.exit(main())


