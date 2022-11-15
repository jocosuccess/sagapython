# SPClassRuntime
#
# Every Class, MetaClass and MetaMetaClass is a SPClassRuntime
# The CMI reads this field directly independent of the language
# it must be a string that locates the language runtime
# The CMI in the future should have a way to register different
# objects for resolving the string field.
from dataclasses import dataclass
import sagapythonglobals

@dataclass(frozen=True)
class cMIClassRuntimeConst:
    URL = str("u")   # global to all CMI objects independent of language runtime.
    # needs more fields to enable a launch script with parameters for the specific runtime

CMIClassRuntimeConst = cMIClassRuntimeConst()

def SetRuntime(self):
    # give subclass a change to override default here
    rn = self.GetRuntime()
    if rn == None:
        rn = sagapythonglobals.CMIConst.CMIRuntimeURL

    self.__field(CMIClassRuntimeConst.URL).fld = rn

    

