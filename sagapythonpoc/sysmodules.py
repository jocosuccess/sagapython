# Test code to establish creating multiple module objects
# for a common copy of the module code.
# The design is to create a module object for a specific module.
# The module has a global variable in it, and is referenced by 
# a function in the module.
# then save a copy of the module object
# load the module with the module object
# this should initialize the module.  Then record the module object in sys.modules
#
# should now be able to call the function that reads the global variable,
# updates it, and prints it.
#
# Next need to prove that the module can be reinitialized without reloading the code.
# save the current sys.modules module object off, then clear the entry in the dictionary.
#
# As a test, could then try calling the function in the module. It should fail since the
# sys.modules no longer knows the module name.
#
# Next, make a copy of the copy of the module object
# initialize the module again using exec_module() as before.
# record in the sys.modules again
# make the same function call
# the global variable should be the initialized value not the updated value.
#
# Note: it is also assumed that the globals dictionary is copied and used,
# each time.

# Tools:
# FileFinder returns a ModuleSpec with the path to a file.  The file must be
# read in from the object state database, written to a temp file.
# 
# import importlib.util
# import sys

# For illustrative purposes.
# import tokenize
# file_path = tokenize.__file__
# module_name = tokenize.__name__

# spec = importlib.util.spec_from_file_location(module_name, file_path)
# module = importlib.util.module_from_spec(spec)
# sys.modules[module_name] = module
# spec.loader.exec_module(module)


import importlib.util
import sys

filepath = 'moduletest.py'
modulename = 'moduletest'
spec = importlib.util.spec_from_file_location(modulename, filepath)
module = importlib.util.module_from_spec(spec)
# make a copy of the module object - not sure if copy will work
# if not, create multiple module objects
sys.modules[modulename] = module
spec.loader.exec_module(module)
globals()[modulename]=module

print("moduletest")
moduletest.addone()
moduletest.addone()

mod1name = 'moduletest1'
sys.modules[mod1name] = module
spec.loader.exec_module(module)
globals()[mod1name]=module

print("moduletest1")
moduletest1.addone()
moduletest1.addone()

print("moduletest")
moduletest.addone()
moduletest.addone()






