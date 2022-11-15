# Test creating a list of dictionary objects, JSON encoding
# JSON decoding
# then check with base64

import json
import base64

dict1 = {"var1": 1, "var2": "test"}
dict2 = {"var2": 1, "var3": "test"}
dict3 = {"var3": 1, "var4": "test"}
dict4 = {"var4": 1, "var5": "test"}

objlist = list()
objlist.append(dict1)
objlist.append(dict2)
objlist.append(dict3)
objlist.append(dict4)

print("before:")
print(objlist)

out = json.dumps(objlist)
print("json:")
print(out)

ini = json.loads(out)
print("in:")
print(ini)

print("list entry:")
print(objlist[2])

# now check the base64
# need to take from bytes to base64 and str. 
# That way can read in the methods as bytes not strings.
method = b'def testfunc():'
method1 = b''.join([method, b' \n'])
method1 = b''.join([method1, b'\tprint("hello")', b' \n'])

print(method1.decode())

#exec(method1)
#eval("testfunc()")

# convert method1 to base64
mtdbase64 = base64.b64encode(method1)
print("base64 encode:")
print(mtdbase64)

dict5 = {"mtd": mtdbase64.decode()}
objlist.append(dict5)
print("objlist with method:")
print(objlist)

out = json.dumps(objlist)
print("json out:")
print(out)

ini = json.loads(out)
print(ini[4])

func = base64.b64decode(ini[4]["mtd"])
print(func)

exec(func)
funcname = "testfunc()"
eval(funcname)