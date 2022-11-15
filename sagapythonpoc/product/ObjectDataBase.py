# ObjectDataBase.py
#
# uses leveldb from pypi. May need the underlying leveldb library.
# Note: for AWS Studio, was unable to use python pip directly with pypi.
# got TLS/SSL errors even after installing ssl libraries, and rebuilding python 3.10.6
# instead use local source file install.
# Also was unable to find wheel in the python 3.10.6 even after the rebuild.

import json
import leveldb

db = None

def opendb(name):
    global db
    try:
        db = leveldb.LevelDB(name)
    except:
        if db == None:
            raise           # reraise if no db

    if db == None:          # sanity check too
        return False
    return True
    
def read(loidbytes: bytes) -> bytes:
    global db
    val = None
    try:
        val = db.Get(loidbytes)
    except:
        pass

    return val

def write(loidbytes: bytes, jdata: str):
    global db
    NewObject(loidbytes)
    if isinstance(jdata, str):
        return (db.Put(loidbytes, jdata.encode()))
    elif isinstance(jdata, bytes) or isinstance(jdata, bytearray):
        return (db.Put(loidbytes, jdata))
    else:
        raise RuntimeError("Error writing to database: Must pass either bytes-like or string objects. Got: ", type(jdata))

def Exists(loidbytes: bytes):
    global db
    try:
        db.Get(loidbytes)
    except:
        return False
    return True

def NewObject(loidbytes: bytes):
    global db
    if Exists(loidbytes) == True:
        return False
    nullobj = json.dumps([[None],[None]])
    db.Put(loidbytes, nullobj.encode())
    return True
