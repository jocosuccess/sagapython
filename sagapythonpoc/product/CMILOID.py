# CMIOID.py implements the "primitive" type to represent the SHA256 OID in SagaPython.
# 
# the OID is base64 encoded in JSON for the state database, and for sending/receiving as a message.
# included in this file is the code for the JSON encode/decode subclass to do the transation to and from the OID type

from json import JSONDecoder, JSONEncoder
import base64

class LOID:
    def __init__(self, oidstr):
        if isinstance(oidstr, bytes):
            self.oid64 = base64.b64encode(oidstr.hex().encode())
            self.oid = oidstr.hex()
        elif isinstance(oidstr, str):
            if oidstr[:2] == "0x":
                self.oid = oidstr[2:]
                self.oid64 = base64.b64encode(bytes(oidstr.encode())[2:])
            else:
                self.oid = oidstr
                self.oid64 = base64.b64encode(bytes(oidstr.encode()))
        else:
            RuntimeError("LOID must be a string or bytes")

    def OID64(self):
        return self.oid64

    def OID64str(self):
        return (self.oid64).decode()

    def OIDbytes(self):
        return bytes.fromhex(self.oid)

    def OIDstr(self):
        return self.oid

    # return the ascii string of hex as bytes
    def OIDstrbytes(self):
        return self.oid.encode()

    def OIDdecode64(self, oid64):
        self.oid64 = oid64
        self.oid = (base64.b64decode(oid64)).decode()
        return self.oid

    def __hash__(self):
        return(hash(self.oid64))

    def __eq__(self, oid):
        if issubclass(type(oid), LOID) == False:
            return False
        return(hash(self.oid64) == oid.__hash__())

CMILOIDType = '$O'  # type for LOIDs in JSON encode - note that this is
                    # also defined in sagapythonglobals and must match here
                    #             
class cMIJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, LOID) == True:
            s64 = obj.OID64str()
            return {CMILOIDType:s64}
        return JSONEncoder.default(self, obj)
        

class cMIJSONDecoder(JSONDecoder):
    def __init__(self, **kwargs):
        super().__init__(object_hook=self.oidhook, **kwargs)

    @staticmethod
    def oidhook(dt):
        if dt.get(CMILOIDType, None) != None:
            b64bytes = dt[CMILOIDType].encode()
            b32 = base64.b64decode(b64bytes)
            s32 = b32.decode()
            return(LOID(s32))
    
        return dt

CMIJSONEncoder = cMIJSONEncoder()
CMIJSONDecoder = cMIJSONDecoder()


