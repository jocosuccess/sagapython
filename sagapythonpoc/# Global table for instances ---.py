# Global table for instances --- 


# All current object instances known to SagaPython during a transaction execution are stored here
# in a dictionary.  The dictionary is then added to the globals for all method exec calls
# this is needed because a call back in to the SagaPython CMI needs the object instances.
# Similarly a current context is kept. This is stored in a list.  
#
# Dictionary of instance objects keyed by OID.
# The OID must be a tuple of the SHA256 bytes.
ObjectDict = []

CurrentContext = []


