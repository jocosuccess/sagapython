# ObjectDataBase.py
#
# This should be wrapping a LevelDB interface.
# At the moment, for testing, is simply a dictionary on the LOID in bytes
#

# fake object dictionary

database = {}

def opendb(name):
    return True
    
# Note: this is a fake database.
# intentionally trasnlating to strings because 
# python dict does not take byte arrays
def read(loidbytes: bytes):
    strbytes = loidbytes.hex()
    return database[strbytes]

def write(loidbytes: bytes, jdata: str):
    strbytes = loidbytes.hex()
    NewObject(loidbytes)
    database[strbytes] = jdata

def Exists(loidbytes: bytes):
    strbytes = loidbytes.hex()
    bl = strbytes in database
    if bl == True:
        return True
    return False

def NewObject(loidbytes: bytes):
    strbytes = loidbytes.hex()
    bl = strbytes in database
    if bl == True:
        return False
    database[strbytes] = [[None],[None]]
    return True
