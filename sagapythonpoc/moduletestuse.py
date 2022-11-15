import sys

def modtest():
    execstring = """import moduletest
    """

    execstring2 = """import moduletest"""

    execstring3 = """
x = 1

def addone():
    global x
    x = x + 1
    print(x)

"""

    gbs1 = globals().copy()
    gbs2 = globals().copy()
    sysmodules = sys.modules.copy()

    exec(execstring, gbs1)
#    print("globals: ", globals().copy())
#    print("gbs1: ", gbs1)
    sysmodules1 = sys.modules.copy()

    #clear the sys.modules and reload sysmodules
    sys.modules.clear() 
    sys.modules |= sysmodules

    exec(execstring2, gbs2)
#    print("gbs2: ", gbs2)
    sysmodules2 = sys.modules.copy()
    sys.modules.clear() 
    sys.modules |= sysmodules

    print("calling addone on gbs1 twice")
    gb = gbs1
    sys.modules.clear() 
    sys.modules |= sysmodules1
    exec("moduletest.addone()", gb)
    exec("moduletest.addone()", gb)

    gb = gbs2
    sys.modules.clear() 
    sys.modules |= sysmodules2
    print("calling addone on gbs2 once")
    exec("moduletest.addone()", gb)

    print("calling addone on gbs1 twice again")
    gb = gbs1
    sys.modules.clear() 
    sys.modules |= sysmodules1
    exec("moduletest.addone()", gb)
    exec("moduletest.addone()", gb)

    gb = gbs2
    sys.modules.clear() 
    sys.modules |= sysmodules2
    print("calling addone on gbs2 once again")
    exec("moduletest.addone()", gb)


def notthis():
    gbs3 = globals().copy()
    gbs4 = globals().copy()
    exec(execstring3, gbs3)
    exec(execstring3, gbs4)

    print("gbs3 and gbs4")
    exec("addone()", gbs3)
    exec("addone()", gbs3)

    exec("addone()", gbs4)

if __name__ == "__main__":
    modtest()