# SPClassAccount.py
#
# Base class for all accounts.  Should inherit from SPClassAccount - when written
#
from sagapythonglobals import *
from sagapythonself import *
from CMI import *
from CMILOID import *
from CMIObjectData import *
import SPClassObject 
import SPClass
import SPClassLinearization 
import SPClassRuntime 
import SPMetaClass
import SPMetaMetaClass

@dataclass(frozen=True)
class sPClassAccountConst:
    dummy = 0
SPClassAccountConst = sPClassAccountConst()

blankloid = '00000000000000000000000000000000'

# NewLOID returns a new loid based on the loid of the account object
# The account object keeps an incrementing integer to form part of the
# new LOID. The intent is that the base LOID from the account object
# is guaranteed unique with the exception of the last 64 bits.
# Since these are an incrementing number, the total returns LOID is
# always guaranteed unique.
def NewLOID(self):
    baseloidstr  = self.baseLD.OIDstr()
    bl = len(baseloidstr)
    bl = min(bl, 48)
    incr = self.LDincr
    incr += 1
    addbytes = "{0:016x}".format(incr)
    newloidstr = baseloidstr[0:bl] + blankloid[bl:48] + addbytes
    self.LDincr = incr
    return LOID(newloidstr)




