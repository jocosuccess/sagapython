# test out source code introspection


import inspect

classmtds = list()

def cmimethod(fmtd):
    classmtds.append(fmtd.__name__)
    print("cmimethod")

def cmiclass(cls):
    print("cmiclass")
    return cls

def __body():
    @cmiclass
    class foobar:

        @cmimethod
        def mtd(self):
            print("here")
            self.y = "there"

        @cmimethod
        def mtd1(self):
            pass

if __name__ == "__main__":
    # read in the transaction script with either
    # stdin, or a passed in file (sys.argc, sys.argv)

    def gigo():
        print("get source of foobar")
        print(inspect.getsource(foobar))
        print(" ")

        for x in foobar.__dict__:
            print(x)

        print(classmtds)
