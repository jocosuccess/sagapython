

# The stub call to the CMI layer - does transition to Go
def CMICall(objid, cmi, *args, **kwargs):
    print("CMI lib layer called")
    print("objid: ", objid)
    print("cmi: ", cmi)

def CMISend(objid, cmi, *args, **kwargs):
    print("CMI lib layer called")
    print("objid: ", objid)
    print("cmi: ", cmi)

# returns the cmiinfo on finding a method or a field
# methods take precedence (Need to check python behavior)
def CMIResolve(objid, name):
    # do resolution using CMI data model
    cmi = CMIinfo(True, "testmtd")

def CMIGetField(self, cmicontext):
    #do CMI Field value here
    return None

def CMISetField(self, cmicontext, value):
    #do CMI Field set value here - no return
    pass

class CMIinfo:
    
    def __init__(self, mtdorfield: bool, name: str):
        self.mtd = mtdorfield
        self.name = name




