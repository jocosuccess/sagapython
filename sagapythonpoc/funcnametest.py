# test the name of the function versus assigning it to different variables
# proves the function name is in the function object, not the name in globals or locals
# means we can name the function anything in the globals, but the function name
# will still be the same -- 
# at runtime should really do a method name binding, but don't have all details for that

def testfunc():
    pass

testfunc()

f = testfunc
print(f.__qualname__)

globalscopy = globals().copy()

globalscopy["newfunc"] = testfunc

eval("print(newfunc.__name__)", globalscopy)