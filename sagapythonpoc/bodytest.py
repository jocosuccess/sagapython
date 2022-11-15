# test when decorators are executed inside of enclosing functions
# determines if we need to call the enclosing function to get the decorators to fire.

def decfun(f):
    print("got dec func")
    return f

def __body():
    @decfun
    def g():
        print("got g func")

def __tail():
    pass

# we call the body function here -- this can be explicitly added to the 
# transaction source, or we call the body function from an invoke() call.
__body()
