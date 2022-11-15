# sagaclasseswrapper.py
# wrapper for the __classes() function to create CMI classes 
from cmidecorators import *

SagaClass = CMIclassdec
SagaMethod = CMIMethoddec       

def cmiclasseswrapper():
    global tempmethodlist
    tempmethodlist = list()
    global classlist
    classlist = list()
    global TestDebug
    TestDebug = False
    __CMIClasses()
    return (BuildCMIClasses())
