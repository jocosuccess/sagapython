# Creating a generic asset class
# This will be a foundation class, but this is a rough example of it
# By default, class objects are owned by a global account object 
# Class objects may be created, and owned by other accounts
# usefulness is questionable

def __hdr():
    hdr = { 'acct': 'aaa', 
	    'seq': 1000,        # whatever the next sequence number is 
		'maxGU': 10, 
		'feePerGU': 1,
		'extraPerGU': 2
        }
    return hdr 

def __CMIClasses():

    @SagaClass(CMIConst.SPClassObject)    # no signature required for creating global classes 
    class ClsAsset:

        SagaFieldTable=[]       # no user visible fields

        @SagaMethod()
        def __init__(self, name: str, initcount: int):
            self.assetcount = initcount # internal instance variable
            self.name = name
            self.callcount = 0

        @SagaMethod()
        def Increment(self, inc: int):           
            self.assetcount += inc

        @SagaMethod()
        def Decrement(self, dec: int):
            if self.assetcount - dec > 0 :
                    self.assetcount -= dec
            else:
                raise RuntimeError("negative asset counts are illegal")
            
        # internal method - example simply counts number of calls
        # def callcount(self):
         #   self.callcount +=1 

def __body():

    # The name ClsAsset is only available to the transaction script
    # The objectID must be retrieved if the intent is to use the class
    Log(ClsAsset)    # log it for user to recover it, could also store it in another object

    # An instance of the new class can be instantiated
    classvar = ClsObjVar(ClsAsset)

    objvar = classvar.new(CMIConst.SPSystemAccount, "sparkplugs", 100)    # initialized with 100 count of asset
    objvar = objvar[0]
    
    # make the objvar persistent by inserting it in the account list
    #acctvar.Insert(objvar)    # also sets owner field of objvar
    return True

def __tail():
         return {'hash': 12345,
            'sig': (rvalue, svalue)    # tuple of r and s value for signature
    }                  
    
    