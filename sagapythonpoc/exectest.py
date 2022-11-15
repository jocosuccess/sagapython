# exectest tests removing the exec()from the builtins for an exec()
# prove that it can't be added back in,
# the prove that the original builtins can be added for a nested exec()


exectest = """

def exectestit():
    print("exec is ")
    print(exec)

print("calling exectestit")
exectestit()    
"""

exectest2 = """
def exectest():
    print(exec)
    exec('print("hello")')

exectest()
"""

import builtins

cpbuiltins = builtins.__dict__.copy()

del(cpbuiltins["exec"])

gbs = globals().copy()

gbs["__builtins__"]=cpbuiltins


print("calling without exec builtin")
try:
    exec(exectest, gbs)
except:
    pass

print("calling while trying to add exec back in")
gbs["exec"] = '<built-in function exec>'
exec(exectest2, gbs)

# Note: pulling exec out doesn't really work since we need
# nested calls to it.
# But maybe can check that the caller is allowed by looking up the stack
# would need to bury the real call in C API, removing the built-in.















