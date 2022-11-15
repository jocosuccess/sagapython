# sagapythonselfstates.py
# Enumeration of states used by the ClsObjVar and the SagaPythonObject class
# to handle the possible syntax for object().__cmi().field/method permutations.
#
from enum import Enum

SPSelfstate = Enum('SPSelfstate', ['ObjectCallingOrDotCMIFieldMethod', 'ObjectCallable',
    'DotCMICallingFieldMethod', 'CMIClass', 'DotFieldMethod'])

#"""ObjectCallingOrDotCMIFieldMethod – next state ObjectCallable, CMICallable, or Do Field/Method
#ObjectCallable – next state DotCMICallingFieldMethod
#DotCMICallingFieldMethod – CMICallable, or (set CMI ancestor flag) Do Field Method
#CMICallable – next state DotFieldMethod
#DotFieldMethod – do method/field (ancestor flag or explicit ancestor"""

#print(SPSelfstate.ObjectCallable)

#v = SPSelfstate.CMICallable

#match(v):
#    case(SPSelfstate.Objectcallable):
#        print("Objectcallable")
#    case(SPSelfstate.CMICallable):
#        print("CMICallable")

