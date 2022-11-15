# simple module to be imported in separate globals list to prove on exec that the module is scoped for the
# exec separately.

x = 1

def addone():
    global x
    x = x + 1
    print(x)

