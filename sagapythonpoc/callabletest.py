# test callable over getattribute
# used to prove that the ClsObjVar and others can take parameters optionally
# before the method/field/ancestor class, so that local parameters can be set first.
# then the self is returned in the __call__.  If we don't want to allow the syntax
# func()(), then we set the callable to disabled for the next call, resetting
# again if a method, and then resetting when completed.  

class calltest:
    def __call__(self):
        print("got call first")
        return (self)

    def __getattribute__(self, __name: str):
        print("get attribute name: ", __name)
