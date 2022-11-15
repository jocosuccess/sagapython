from CMILOID import *


enc = CMIJSONEncoder()
dec = CMIJSONDecoder()

od = LOID("stuffit&&**")
print(od.oid)

js = enc.encode(od)
print(js)

jd = dec.decode(js)
print(jd.oid)

