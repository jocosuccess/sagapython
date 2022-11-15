# test the getattribute for function, attribute and nested calls
# the intent is that nested calls are for ancestor classes
# alternative approach is that all classes are prepended with C_

class testit:
    def __getattribute__(self, name):
        print("getattribute: ", name)
        return self

    def __setattr__(self, __name, __value) -> None:
        print(__name, ":", __value)


tryit = testit()
x = tryit.aclass.field
tryit.aclass.newfield = None
