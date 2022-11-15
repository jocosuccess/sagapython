# body wrapper function 
# should load decorators and classes

# global dictionary of stub proxy classes
from sagapythonglobals import *
from sagapythonself import *

# call the main body of the transaction here
def bodywrapper():
    return (__body())

